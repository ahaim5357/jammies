"""A script containing the methods needed to create and apply patches
between two blocks of text.
"""

# License: Public domain (CC0)
# Isaac Turner 2016/12/05

import re
from difflib import unified_diff
from typing import Iterator, List
from datetime import datetime

_NO_EOL: str = '\\ No newline at end of file'
"""Text indicating there is no newline at the end of the diff file."""

_HUNK_HEADER: re.Pattern = re.compile(r'^@@ -(\d+),?(\d+)? \+(\d+),?(\d+)? @@$')
"""The regex to get the file line information from the hunk header."""

class PatchError(ValueError):
    """The patch file contained invalid information.
    """

def create_patch(from_text: str, to_text: str, filename: str = '',
        time: str = str(datetime.now())) -> str:
    """Creates a patch between two pieces of text. If equivalent, returns
    an empty string.

    Parameters
    ----------
    from_text : str
        The original text to generate the patch from.
    to_text : str
        The new text the patch will transform the original text to.
    filename : str (default '')
        The name of the file the patch is being applied for.
    time : datetime.datetime (default str(datetime.datetime.now))
        The time the patch was generated.

    Returns
    -------
    str
        The generated patch.
    """

    diffs: Iterator[str] = unified_diff(
        from_text.splitlines(keepends = True),
        to_text.splitlines(keepends = True),
        fromfile = filename, tofile = filename,
        tofiledate = time
    )
    # Join diffs together
    # Apply no eol if text line doesn't end with a newline
    return ''.join([diff if diff[-1] == '\n' else f'{diff}\n{_NO_EOL}\n' for diff in diffs])

def apply_patch(text: str, patch: str, revert: bool = False) -> str:
    """Applies a patch to the current text.

    Parameters
    ----------
    text : str
        The text to apply the patch to.
    patch : str
        The patch to apply.
    revert : bool (default False)
        When `True`, will attempt to recover the original file.

    Returns
    -------
    str
        The patched text.
    """

    # Setup basic references and result vars
    text: List[str] = text.splitlines(keepends = True)
    patch: List[str] = patch.splitlines(keepends = True)
    patched_text: str = ''

    pidx: int = 0 # Index line into patch
    tidx: int = 0 # Index line into text

    # Determine whether to apply changes or revert them
    ## midx is the index into the header to determine what to apply
    ## sign is whether to consider the addition or removal as the final transformer
    midx, sign = (1, '+') if not revert else (3, '-') # midx, sign: int, str

    # Skip header lines
    while pidx < len(patch) and patch[pidx].startswith(('---', '+++')):
        pidx += 1

    # Apply patches as long as there are still patch lines left
    while pidx < len(patch):
        # Get header
        header: re.Match[str] | None = _HUNK_HEADER.match(patch[pidx])
        if not header: # If there is no hunk header, throw an exception
            raise PatchError(f'No header found for new hunk on line {pidx}')

        # Get the first line index in the text file to apply/revert the patch for
        shidx = int(header.group(midx)) - 1 + (header.group(midx + 1) == '0')
        # Make sure start hunk index is not after current text index
        ## and that the start hunk index is not after the number of lines in the text file
        if tidx > shidx:
            raise PatchError(f'Hunk start index {shidx} is after the current text index {tidx}')
        if shidx > len(text):
            raise PatchError(f'Hunk start index {shidx} is after the end of the text')

        # Add any lines before the hunk start index to the result
        patched_text += ''.join(text[tidx:shidx])

        # Set the new text start index and move to next patch line
        tidx = shidx
        pidx += 1

        # Loop through patch until eol or next hunk
        while pidx < len(patch) and patch[pidx][0] != '@':
            # If the next patch line is not the end of the text
            ## and the first character isn't a backslash
            ### (indicates either \t, \n, or the _NO_EOL text)
            if pidx + 1 < len(patch) and patch[pidx + 1][0] == '\\':
                # Get the line without the last character
                ## and increase the patch index by 2
                line: str = patch[pidx][:-1]
                pidx += 2
            else:
                # Otherwise, get the current line
                line: str = patch[pidx]
                pidx += 1
            # If the line isn't empty
            if len(line) > 0:
                # If the first character of the line is the sign
                ## or a space
                if line[0] == sign or line[0] == ' ':
                    # Apply the patched text without the first character
                    patched_text += line[1:]
                # Skip the line if it is not the current sign being checked for
                tidx += (line[0] != sign)
    # Apply the rest of the text after all patches were made
    patched_text += ''.join(text[tidx:])
    return patched_text
