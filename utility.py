'''
## Acknowledgements

Some sections of this code are adapted from the work of others. Notably,
LocateIPG by chromium (https://chromium.googlesource.com/chromium/src/+/refs/heads/main/content/test/gpu/gpu_tests/ipg_utils.py)
Reverse_readLine by smichr (https://stackoverflow.com/questions/2301789/how-to-read-a-file-in-reverse-order)
Split by Joschua (https://stackoverflow.com/questions/4697006/python-split-string-by-list-of-separators)
DiffBetweenArray by Glorfindel (https://stackoverflow.com/questions/534855/subtracting-2-lists-in-python)
The code has been modified to fit the requirements of this project and has been integrated into the overall implementation.

'''
import os
import sys
def LocateIPG():
    if sys.platform == 'win32':
        ipg_dir = os.getenv('IPG_Dir')
        if not ipg_dir:
            raise Exception('No env IPG_Dir')
        gadget_path = os.path.join(ipg_dir, 'PowerLog3.0.exe')
        if not os.path.isfile(gadget_path):
            raise Exception("Can't locate Intel Power Gadget at " + gadget_path)
        return gadget_path
    if sys.platform == 'darwin':
        return '/Applications/Intel Power Gadget/PowerLog'
    raise Exception('Only supported on Windows/Mac')
def reverse_readline(filename, buf_size=8192):
    """A generator that returns the lines of a file in reverse order"""
    with open(filename, 'rb') as fh:
        segment = None
        offset = 0
        fh.seek(0, os.SEEK_END)
        file_size = remaining_size = fh.tell()
        while remaining_size > 0:
            offset = min(file_size, offset + buf_size)
            fh.seek(file_size - offset)
            buffer = fh.read(min(remaining_size, buf_size)).decode(encoding='utf-8')
            remaining_size -= buf_size
            lines = buffer.split('\n')
            # The first line of the buffer is probably not a complete line so
            # we'll save it and append it to the last line of the next buffer
            # we read
            if segment is not None:
                # If the previous chunk starts right from the beginning of line
                # do not concat the segment to the last line of new chunk.
                # Instead, yield the segment first
                if buffer[-1] != '\n':
                    lines[-1] += segment
                else:
                    yield segment
            segment = lines[0]
            for index in range(len(lines) - 1, 0, -1):
                if lines[index]:
                    yield lines[index]
        # Don't yield None if the file was empty
        if segment is not None:
            yield segment

def split(txt, seps):
    default_sep = seps[0]

    # we skip seps[0] because that's the default separator
    for sep in seps[1:]:
        txt = txt.replace(sep, default_sep)
    return [i.strip() for i in txt.split(default_sep)]

def diffBetweenArr(a,b):
    return [float(a_i) - float(b_i) for a_i, b_i in zip(a, b)]