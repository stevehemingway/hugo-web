#!/usr/bin/env python3
"""Remove doubled phrases from post titles and H1 headings.

A messy merge duplicated words in two places:

  title: Bitmine Immersion Technologies Bitmine Immersion Technologies
  # Bitmine Immersion Technologies (stocks/BMNR), Bitmine Immersion Technologies

This script collapses every doubled phrase in the front-matter `title` and in
the leading `#` heading, and removes the repeated name that the merge glued on
after the `(stocks/TICKER),` marker.

Rules
  * The heading is rebuilt as `# <name> (stocks/<TICKER>)` when it carries the
    `(stocks/TICKER), <repeated name>` shape.
  * Any phrase of two or more words that appears twice is collapsed to one.
  * Single doubled words (`Foo Foo`) are collapsed too.
  * Nothing below the first heading is touched.

Usage
  ./dedup_titles.py [--write] [paths...]
Without --write it only reports; nothing is modified.
"""
import glob
import os
import re
import sys

FM = re.compile(r'\A---\n(.*?)\n---\n', re.S)
TITLE = re.compile(r'^title:[ \t]*(.*)$', re.M)
H1 = re.compile(r'^(#[ \t]+)(.*)$', re.M)
STOCKS_MARK = re.compile(r'^(?P<name>.*?)[ \t]*\(stocks/(?P<ticker>[^)]*)\)[ \t]*,?[ \t]*(?P<tail>.*)$')


def collapse(text):
    """Collapse repeated words/phrases in `text`, preserving case and spacing."""
    words = text.split()
    if len(words) < 2:
        return text
    # Longest repeated phrase first: n words appearing twice -> n words.
    for n in range(len(words) // 2, 0, -1):
        i = 0
        while i + 2 * n <= len(words):
            first = words[i:i + n]
            second = words[i + n:i + 2 * n]
            if first == second:
                del words[i + n:i + 2 * n]
                continue
            i += 1
    # A phrase repeated non-adjacently (A B ... A B) collapses on the 2nd copy.
    for n in range(len(words) // 2, 1, -1):
        i = 0
        while i + n <= len(words):
            phrase = words[i:i + n]
            for j in range(i + n, len(words) - n + 1):
                if words[j:j + n] == phrase:
                    del words[j:j + n]
                    return collapse(' '.join(words))
            i += 1
    return ' '.join(words)


def clean_title(value):
    quote = ''
    inner = value.strip()
    if len(inner) >= 2 and inner[0] == inner[-1] and inner[0] in '"\'':
        quote, inner = inner[0], inner[1:-1]
    new = collapse(inner)
    if new == inner:
        return None
    return quote + new + quote


def clean_h1(line):
    """Rebuild a `# Name (stocks/T) , Name` heading. Returns None if unchanged."""
    m = STOCKS_MARK.match(line)
    if m and m.group('tail'):
        name = collapse(m.group('name').strip())
        tail = collapse(m.group('tail').strip()).strip(' ,')
        name_wo_mark = name
        # Drop the tail when it merely repeats the name (any case/punctuation).
        norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())
        if not tail or norm(tail) == norm(name_wo_mark) or norm(name_wo_mark).startswith(norm(tail)):
            return f'{name} (stocks/{m.group("ticker")})'
        return f'{name} (stocks/{m.group("ticker")}), {tail}'
    new = collapse(line)
    return new if new != line else None


def fix_text(text):
    """Return (new_text, [changes]). changes is empty when nothing to do."""
    changes = []
    m = FM.match(text)
    if not m:
        return text, changes
    front = m.group(0)
    rest = text[m.end():]

    def sub_title(tm):
        new = clean_title(tm.group(1))
        if new is None:
            return tm.group(0)
        changes.append(f'title: {tm.group(1).strip()} -> {new}')
        return 'title: ' + new

    new_front = TITLE.sub(sub_title, front, count=1)

    h1 = H1.search(rest)
    new_rest = rest
    if h1:
        new_line = clean_h1(h1.group(2))
        if new_line is not None:
            changes.append(f'h1: {h1.group(2)} -> {new_line}')
            new_rest = rest[:h1.start()] + h1.group(1) + new_line + rest[h1.end():]

    if not changes:
        return text, changes
    return new_front + new_rest, changes


def main(argv):
    write = '--write' in argv
    paths = [a for a in argv if not a.startswith('--')] or sorted(glob.glob('*.md'))

    files = entries = 0
    for path in paths:
        with open(path, encoding='utf-8', errors='replace') as fh:
            text = fh.read()
        new, changes = fix_text(text)
        if not changes:
            continue
        files += 1
        entries += len(changes)
        print(path)
        for c in changes:
            print('   ', c)
        if write:
            tmp = path + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as fh:
                fh.write(new)
            os.replace(tmp, path)

    print(f'\n{files} file(s), {entries} heading(s) '
          f'{"fixed" if write else "would be fixed (dry run)"}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
