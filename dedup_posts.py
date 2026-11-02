#!/usr/bin/env python3
"""Remove duplicated blocks from Hugo post files.

Notes were repeatedly appended to themselves, so a file holds several copies
of the same block, each with its own '---' / tags: wrapper. This collapses
each duplicate to one copy.

Rules
  * A block is the text between '---' lines, after the leading front matter.
  * Blocks starting with 'tags:' or '*Last updated' are wrappers, not content.
  * Two blocks are duplicates when >90% similar after masking the H1, the
    'latest change: <date>' line and 'YYYY-MM-DD CUR 123.4' price lines.
  * A block that is an exact prefix of another is a truncated copy: dropped.
  * Of the duplicates kept, the longest wins (least truncated, most links).
  * Different content is never merged; the file may keep several blocks.

Usage
  ./dedup_posts.py [--write] [--threshold 0.8] [paths...]
Without --write nothing is touched; it only reports.
"""
import glob
import os
import re
import sys
from difflib import SequenceMatcher

FM = re.compile(r'\A---\n.*?\n---\n', re.S)
DATE = re.compile(r'latest change:\s*\d{4}-\d{2}-\d{2}')
LASTUPD = re.compile(r'^\*Last updated:.*$', re.M)
PRICE = re.compile(r'^\d{4}-\d{2}-\d{2}\s+[A-Z]{3}\s+[\d.,]+', re.M)


def split_blocks(text):
    body = FM.sub('', text, count=1) if FM.match(text) else text
    return [b.strip() for b in re.split(r'^---\s*$', body, flags=re.M) if b.strip()]


def is_wrapper(block):
    return block.startswith('tags:') or block.startswith('*Last updated')


def key(block):
    s = re.sub(r'^#\s.*$', '#H', block, count=1, flags=re.M)
    s = DATE.sub('LC', s)
    s = LASTUPD.sub('', s)
    s = PRICE.sub('', s)
    return re.sub(r'\s+', ' ', s).strip()


def similar(a, b, threshold):
    if a == b:
        return True
    short, long_ = sorted((len(a), len(b)))
    if short / long_ < threshold:          # cheap reject before diffing
        return False
    return SequenceMatcher(None, a, b).ratio() >= threshold


def dedup_text(text, threshold=0.8):
    """Return (new_text, removed_count). removed_count == 0 means unchanged."""
    m = FM.match(text)
    front = m.group(0) if m else ''
    blocks = split_blocks(text)
    bodies = [b for b in blocks if not is_wrapper(b)]
    if len(bodies) < 2:
        return text, 0

    # Longest first, so a full copy claims its fingerprint before a short one.
    groups = []                            # list of [key, best_block]
    for b in sorted(bodies, key=len, reverse=True):
        k = key(b)
        for g in groups:
            if similar(k, g[0], threshold):
                break
        else:
            groups.append([k, b])

    # Drop any block that is an exact prefix of another surviving block.
    survivors = [
        b for _, b in groups
        if not any(key(o).startswith(key(b)) and key(o) != key(b) for _, o in groups)
    ]
    removed = len(bodies) - len(survivors)
    if removed <= 0:
        return text, 0

    # Emit in original document order.
    order = {id(b): i for i, b in enumerate(bodies)}
    survivors.sort(key=lambda b: order[id(b)] if id(b) in order else 1 << 30)
    tags = next((b for b in blocks if b.startswith('tags:')), None)

    out = (front.rstrip('\n') + '\n') if front else ''
    out += '\n\n'.join(survivors)
    out += ('\n\n---\n' + tags + '\n---\n') if tags else '\n'
    return out, removed


def main(argv):
    write = '--write' in argv
    threshold = 0.8
    if '--threshold' in argv:
        i = argv.index('--threshold')
        threshold = float(argv[i + 1])
    paths = [a for a in argv if not a.startswith('--') and a != str(threshold)]
    if not paths:
        paths = sorted(glob.glob('*.md'))

    files_changed = blocks_removed = 0
    for path in paths:
        with open(path, encoding='utf-8', errors='replace') as fh:
            text = fh.read()
        new, removed = dedup_text(text, threshold)
        if not removed:
            continue
        files_changed += 1
        blocks_removed += removed
        print(f'{path}: -{removed} block(s), '
              f'{text.count(chr(10))} -> {new.count(chr(10))} lines')
        if write:
            tmp = path + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as fh:
                fh.write(new)
            os.replace(tmp, path)

    print(f'\n{files_changed} file(s), {blocks_removed} block(s) '
          f'{"removed" if write else "would be removed (dry run)"}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
