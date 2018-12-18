#!/usr/bin/env python
# -*- coding: utf-8 -*-


import datetime, shutil, os

if __name__ == '__main__':
    name = 'iLoad' + datetime.datetime.now().strftime('%Y%m%d')
    
    srclib = os.path.curdir + '/makelib/output/library.zip'
    tar = os.path.curdir + '/' + name + '/'
    
    shutil.move(srclib, tar)