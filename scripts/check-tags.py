#!/usr/bin/env python3
"""Validate YAML front-matter tags in Hugo content before committing.

Exit 1 if any staged content file has a malformed tag list. Only files in the
index are checked, so a dirty-but-unadded working tree never blocks a commit.

Checks
------
1.  Every content file must have exactly one `tags:` key, in front matter only.
2.  A `tags:` key must never appear in the body (the failure mode this repo hit:
    a `---/tags:/---` block appended at EOF by a re-import).
3.  The value must be a flow list on one line: `tags: [a, b]`.
4.  Each tag: lowercase, hyphenated, no whitespace, no URLs, no trailing
    `.` `:` `,`, at most MAXLEN characters, at least one `/`.
5.  Root must be one of ROOTS.
6.  No joint analyst tags (`analyst/x-and-y`).
7.  No duplicate tags within a file (case-insensitively after normalisation).
"""

import re
import subprocess
import sys

ROOTS = {'analyst', 'sector', 'thesis', 'market', 'potential', 'focus', 'size', 'theme'}
MAXLEN = 45
TAG_RE = re.compile(r'^[a-z0-9][a-z0-9/\-()!]*$')
FM_RE = re.compile(r'^---\r?\n(.*?)\r?\n---\r?\n', re.S)
TAGS_LINE_RE = re.compile(r'^tags\s*:(.*)$', re.M)
FLOW_RE = re.compile(r'^\s*\[(.*)\]\s*$')


def staged_content_files():
    out = subprocess.run(
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACMR', '-z'],
        capture_output=True, text=True, check=True,
    ).stdout
    return [p for p in out.split('\0') if p and p.endswith('.md') and p.startswith('content/')]


def body_tag_blocks(text, fm_end):
    """Line numbers of any `tags:` key occurring after front matter."""
    hits = []
    for m in TAGS_LINE_RE.finditer(text, fm_end):
        line = text.count('\n', 0, m.start()) + 1
        hits.append(line)
    return hits


def check_tag(tag):
    if not tag:
        return 'empty tag'
    if len(tag) > MAXLEN:
        return f'too long ({len(tag)} > {MAXLEN} chars) - probably a sentence blob'
    if ' ' in tag or '\t' in tag:
        return 'contains whitespace'
    if 'http' in tag:
        return 'contains a URL'
    if tag.endswith(('.', ':', ',')):
        return 'trailing punctuation'
    if not TAG_RE.match(tag):
        return 'invalid characters (want lowercase [a-z0-9/-()!])'
    if '/' not in tag:
        return f'rootless (prefix with one of: {", ".join(sorted(ROOTS))})'
    root = tag.split('/')[0]
    if root not in ROOTS:
        return f'bad root "{root}" (allowed: {", ".join(sorted(ROOTS))})'
    if root == 'analyst' and '-and-' in tag:
        return 'joint analyst tag (split into separate tags)'
    return None


def check_file(path, errors):
    try:
        text = open(path, encoding='utf-8').read()
    except (OSError, UnicodeDecodeError) as exc:
        errors.append((path, 0, f'unreadable: {exc}'))
        return

    if not text.startswith('---'):
        return  # no front matter: not our business

    fm = FM_RE.match(text)
    if not fm:
        errors.append((path, 1, 'front matter opened with --- but never closed'))
        return
    frontmatter = fm.group(1)

    keys = [m for m in TAGS_LINE_RE.finditer(frontmatter)]
    if not keys:
        return  # no tags at all is allowed
    if len(keys) > 1:
        errors.append((path, 1, f'{len(keys)} tags: keys in front matter (want 1)'))

    raw = keys[0].group(1)
    flow = FLOW_RE.match(raw)
    if not flow:
        errors.append((path, 1, 'tags value is not a single-line flow list [ ... ]'))
        return

    tags = [t.strip().strip('"\'') for t in flow.group(1).split(',')]
    seen = {}
    for tag in tags:
        if not tag:
            continue
        problem = check_tag(tag)
        if problem:
            errors.append((path, 4, f'tag "{tag[:60]}{"..." if len(tag) > 60 else ""}": {problem}'))
        elif tag in seen:
            errors.append((path, 4, f'duplicate tag "{tag}"'))
        else:
            seen[tag] = True

    for line in body_tag_blocks(text, fm.end()):
        errors.append((path, line, 'tags: key in body - tags belong in front matter only'))


def main():
    files = staged_content_files()
    if not files:
        return 0

    errors = []
    for path in files:
        check_file(path, errors)

    if not errors:
        return 0

    print('front-matter tag check failed\n', file=sys.stderr)
    for path, line, msg in errors:
        print(f'  {path}:{line}: {msg}', file=sys.stderr)
    print(f'\n{len(errors)} problem(s) in {len({e[0] for e in errors})} file(s).', file=sys.stderr)
    print('Fix the tags, or commit with --no-verify to bypass.', file=sys.stderr)
    return 1


if __name__ == '__main__':
    sys.exit(main())
