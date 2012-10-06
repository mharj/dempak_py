#!/usr/bin/env python
from __future__ import generators
from distutils.dir_util import mkpath
from distutils.file_util import copy_file
import os, stat, types, re, string, dempak

nif_folder = '/mnt/windows/Program Files/Games/Mythic' # replace with your path

# the walktree function is from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/200131
def walktree(top = ".", depthfirst = True):
    """Walk the directory tree, starting from top. Credit to Noah Spurrier and Doug Fort."""
    names = os.listdir(top)
    if not depthfirst:
        yield top, names
    for name in names:
        try:
            st = os.lstat(os.path.join(top, name))
        except os.error:
            continue
        if stat.S_ISDIR(st.st_mode):
            for (newtop, children) in walktree (os.path.join(top, name), depthfirst):
                yield newtop, children
    if depthfirst:
        yield top, names

re_nif = re.compile(r'^.*\.(nif|kf|kfa)$', re.IGNORECASE)
re_nmpk = re.compile(r'^.*\.(n|m)pk$', re.IGNORECASE)
for top, names in walktree(nif_folder):
    for name in names:
        f = top + os.sep + name
        dest = top[len(nif_folder)+1:] # strip root folder
        if (re_nif.match(name)):
            print "copying " + dest + os.sep + name
            mkpath(dest)
            copy_file(f, dest)
        if (re_nmpk.match(name)):
            print "processing archive " + dest + os.sep + name
            mpak = dempak.MPAKFile(f)
            for e in mpak.entries:
                if re_nif.match(e):
                    print "extracting " + dest + os.sep + e
                    infile = mpak.open(e)
                    data = infile.read()
                    infile.close()
                    
                    mkpath(dest)
                    outfile = open(dest + os.sep + e, 'wb')
                    outfile.write(data)
                    outfile.close()
