#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, pdb

def countRows(path, exclude=[]):
    rows = 0
    reli = []
    pyfile = []
    li = os.listdir(path)

    for af in li:
        ft = af[-3:]
        if ft == '.py' or ft == '.PY':
            if af not in exclude:
                pyfile.append(path+"\\"+af)
    
    for pf in pyfile:
        with open(pf, "rb") as fo:
            r = fo.readlines()
            reli.append("file %s count is %d" % (os.path.basename(pf), len(r),))
            rows = rows + len(r)
    reli.append("sub total rows is %d" % (rows, ))
    return reli

if __name__ == "__main__":
    cud = os.path.abspath(os.curdir)
    mli = countRows(cud)
    print("===================================================")
    print("main folder python file rows:")
    for i in mli:
        print(i)
    print("===================================================")
    #pdb.set_trace()
    ud = cud + "\\utils"
    uli = countRows(ud, exclude=["myimages.py"])
    print("utils folder python file rows:")
    for j in uli:
        print(j)
    print("===================================================")