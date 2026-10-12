#!/usr/bin/env python

# dempak.py: Dark Age of Camelot archive (.mpk/.npk) extractor.
# See http://www.randomly.org/projects/mapper/ for updates and sample output.
# This module is both importable and directly runnable.

"""Dark Age of Camelot .npk/.mpk archive extraction module."""

import zlib, struct
from io import BytesIO

class error(IOError): pass

_test = zlib.decompressobj()
if not hasattr(_test, 'unused_data'):
    raise error('Update your Python: this zlib module is too old')
del _test

def _readstream(f):
    """_readstream(f) -> string
Decompress a zlib stream from a file 'f'; ensure 'f' points immediately after
the end of the stream on return. Returns the decompressed stream data.
"""
    do = zlib.decompressobj()

    output = b''
    while not do.eof:
        chunk = f.read(1024)
        if not chunk:
            raise error('unexpected end of stream')
        output += do.decompress(chunk)

    f.seek(0 - len(do.unused_data), 1)
    return output

class MPAKFile:
    """Object wrapping an archive file."""
    
    def __init__(self, path):
        """MPAKFile(path) -> object

Open a new MPAKFile object for the archive located at 'path'.
Throws dempak.error or IOError on errors.
"""
        
        self.path = path
        self.f = open(path, 'rb')

        # check signature
        if self.f.read(4) != b'MPAK':
            raise error('not a MPAK archive')

        self.f.seek(21)

        # discard first stream
        mpk = _readstream(self.f)
        #print "MPK archive name:", mpk

        # read second stream: directory
        dirdata = _readstream(self.f)
        ##print dirdata

        # decode directory.
        baseoffset = self.f.tell()
        self.directory = {}
        offset = 0
        while offset + 0x11b < len(dirdata):
            name = dirdata[offset:offset+0x110].split(b'\0', 1)[0].decode('latin-1')

            (entryoffset,) = struct.unpack('<I', dirdata[offset+0x110:offset+0x114])
            self.directory[name.lower()] = baseoffset + entryoffset
            offset += 0x11c

        self.entries = list(self.directory.keys())
        # done.

    def open(self, entry):
        """open(entry) -> file

Return a file-like object for the archive entry 'entry'.
Throws dempak.error or IOError on errors.
"""
        if not self.f:
            raise error('file is closed')

        entry = entry.lower()
        if entry not in self.directory:
            raise error('unknown entry: ' + entry)

        self.f.seek(self.directory[entry])
        data = _readstream(self.f)
        return BytesIO(data)

    def close(self):
        self.f.close()
        self.f = None

_filecache = {}

def getMPAKEntry(path, entry):
    """getMPAKEntry(path, entry) -> file

Get a file-like object for a particular entry of an archive.
Throws dempak.error or IOError on errors."""
    
    global _filecache

    if path not in _filecache:
        _filecache[path] = MPAKFile(path)

    return _filecache[path].open(entry)

def run():
    import sys, os

    if len(sys.argv) < 2 or len(sys.argv) > 4:
        print("Usage: %s <path to .mpk/.npk> <optional output path> <options: -quiet>" % sys.argv[0], file=sys.stderr)
        sys.exit(1)

    name = sys.argv[1]
    f = MPAKFile(name)

    base = ''
    quiet = 0
    if len(sys.argv) >= 3:
        base = sys.argv[2]
        if base == '-quiet': quiet = 1
        else:
            base = sys.argv[2]
            if not os.path.isdir(base):
                os.mkdir(base)
            if not os.path.isdir(base):
                print("Can't create or find output directory '%s'" % base, file=sys.stderr)
                sys.exit(1)
            
    if len(sys.argv) >= 4:
        option = sys.argv[3]
        if option == '-quiet': quiet = 1

    
    for e in f.entries:
        outpath = e
        if base: outpath = os.path.join(base, e)
        if not quiet: print("Extracting", e, "=>", outpath, end=' ', file=sys.stderr)
        
        infile = f.open(e)
        data = infile.read()
        infile.close()

        outfile = open(outpath, 'wb')
        outfile.write(data)
        outfile.close()

        if not quiet: print("(" + str(len(data)) + " bytes)", file=sys.stderr)

    f.close()
    sys.exit(0)

if __name__ == '__main__': run()

# Changelog:
#   12-Oct-2026: Python 3 compatibility improvements.
#   26-Jan-2002: Initial version. Requires Python 2.1 for
#                the more recent zlib module.
