# License: Public domain (CC0)
# Isaac Turner 2016/12/05

import re
from difflib import unified_diff
from typing import Iterator, List

_NO_EOL: str = '\\ No newline at end of file'
"""Text indicating there is no newline at the end of the diff file."""

_HUNK_HEADER: str = r'^@@ -(\d+),?(\d+)? \+(\d+),?(\d+)? @@$'
"""The regex to get the file line information from the hunk header."""

def create_patch(from_text: str, to_text: str, filename: str = '') -> str:
    """TODO: Document
    """

    diffs: Iterator[str] = unified_diff(
        from_text.splitlines(keepends = True),
        to_text.splitlines(keepends = True),
        fromfile = filename, tofile = filename
    )
    # Join diffs together
    return ''.join([diff if diff[-1] == '\n' else f'{diff}\n{_NO_EOL}\n' for diff in diffs])

def apply_patch(text: str, patch: str, revert: bool = False) -> str:
    """TODO: Document
    """
    text: List[str] = text.splitlines(keepends = True)
    patch: List[str] = patch.splitlines(keepends = True)
    patched_file: str = ''

    # TODO: Rewrite below
    i = sl = 0
    (midx,sign) = (1,'+') if not revert else (3,'-')
    while i < len(patch) and patch[i].startswith(("---","+++")): i += 1 # skip header lines
    while i < len(patch):
        m = re.match(_HUNK_HEADER, patch[i])
        if not m: raise Exception("Bad patch -- regex mismatch [line "+str(i)+"]")
        l = int(m.group(midx))-1 + (m.group(midx+1) == '0')
        if sl > l or l > len(text):
            raise Exception("Bad patch -- bad line num [line "+str(i)+"]")
        patched_file += ''.join(text[sl:l])
        sl = l
        i += 1
        while i < len(patch) and patch[i][0] != '@':
            if i+1 < len(patch) and patch[i+1][0] == '\\': line = patch[i][:-1]; i += 2
            else: line = patch[i]; i += 1
            if len(line) > 0:
                if line[0] == sign or line[0] == ' ': patched_file += line[1:]
                sl += (line[0] != sign)
    patched_file += ''.join(text[sl:])
    return patched_file
