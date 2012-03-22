#!/usr/bin/python
import os, sys
import VOEventLib.VOEvent as voe
import VOEventLib.Vutil as voe_utils

archive_rootdir=os.environ["HOME"]+"/comet/voe_archive"

def main():
    """Example of an external utility that can handle VOEvents piped from Comet.
    Requires VOEventLib (ToDo - fix to use only lxml).

    This bascially duplicates functionality already provided by comet,
    but in an easily user hackable form.

    """
    s = sys.stdin.read()
    v = voe_utils.parseString(s)
    archive_voevent(v, archive_rootdir)
    return 0


def archive_voevent(v, rootdir):
    relpath, filename = v.ivorn.split('//')[1].split('#')
    filename+=".xml"
    fullpath = os.path.sep.join((rootdir, relpath, filename))
    ensure_dir(fullpath)
    with open(fullpath, 'w') as f:
        print "Archiving to",fullpath
        f.write(voe_utils.stringVOEvent(v))

def ensure_dir(filename):
    d = os.path.dirname(filename)
    if not os.path.exists(d):
        os.makedirs(d)
    
    
if __name__=='__main__':
    sys.exit(main())
    
