#!/usr/bin/env python
# -*- coding: utf-8 -*-


import datetime, shutil, os

if __name__ == '__main__':
    name = 'iLoad' + datetime.datetime.now().strftime('%Y%m%d')
    shutil.move('dist', name)
    
    lib = os.path.curdir + '/' + name + '/library.zip'
    tar = os.path.curdir + '/makelib/'
    tarFile = os.path.curdir + '/makelib/library.zip'
    
    if os.path.exists(tarFile):
        os.remove(tarFile)
    else:
        print('no such file:%s' % lib)
    
    
    shutil.move(lib, tar)