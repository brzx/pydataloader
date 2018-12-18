#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import mainFrame

class LogThis(object):
 
    def __init__(self):
        pass
 
    def __call__(self, fn):
        def wrapped(*args, **kwargs):
            def nfn(*args, **kwargs):
                r = fn(*args, **kwargs)
                logFileName = mainFrame.workspace + "\\" + args[1] + "\\report_" + str(time.time()) + ".log"
                self.writeLog(r["logli"], fn.__name__, logFileName)
                return r
            return nfn(*args, **kwargs)
        return wrapped
        
    def writeLog(self, li, fname, logFileName):
        with open(logFileName, "ab") as fo:
            fo.write("-------------------------------------------------------------------\n")
            fo.write(time.asctime(time.localtime(time.time())))
            fo.write("    ")
            fo.write("function name is %s" % (fname, ))
            fo.write("\n")
            for l in li:
                fo.write(l)
                fo.write("\n")
            fo.write(time.asctime(time.localtime(time.time())))
            fo.write("\n")
            fo.write("-------------------------------------------------------------------\n")