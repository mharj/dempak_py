#!/usr/bin/env python
import os, stat, re, shutil, dempak

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
        dest = top[len(nif_folder)+1:] or '.' # strip root folder
        if (re_nif.match(name)):
            print("copying " + dest + os.sep + name)
            os.makedirs(dest, exist_ok=True)
            shutil.copy2(f, dest)
        if (re_nmpk.match(name)):
            print("processing archive " + dest + os.sep + name)
            mpak = dempak.MPAKFile(f)
            try:
                for e in mpak.entries:
                    if re_nif.match(e):
                        print("extracting " + dest + os.sep + e)
                        with mpak.open(e) as infile:
                            data = infile.read()
                        os.makedirs(dest, exist_ok=True)
                        with open(dest + os.sep + e, 'wb') as outfile:
                            outfile.write(data)
            finally:
                mpak.close()
