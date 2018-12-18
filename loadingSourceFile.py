#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, csv, sqlite3, pdb, codecs, sys
import iLoad
from utils import iLoadTools

#reload(sys)
#sys.setdefaultencoding("utf8")

class SourceFile:
    def __init__(self, name, conn, log):
        self.conn = conn
        self.name = name
        self.log = log

    def loading(self):
        dt = iLoadTools.DatabaseTool(self.conn)
        csvfile = []
        filename = dt.getSourceFileName()
        filepath = iLoad.workspace + "\\" + self.name + "\\" + filename
        csvfile.append(filepath)

        for cf in csvfile:
            fo = codecs.open(cf,"rb","utf-8")
            reader = csv.reader(fo)
            tablename = os.path.basename(cf)[0:-4]
            nli = []
            insqllist = []
            createsql = ""
            for line in reader:
                line = map(lambda x:x.replace('\xef\xbb\xbf',''), line)
                if reader.line_num == 1:
                    for str in line:
                        str = str.replace(" ","")
                        str = iLoadTools.charReplace(str)
                        restr = str
                        nli.append(restr)
                    collist = ""
                    for l in nli:
                        collist = collist + l +" text, "
                    collist = collist[0:-2]
                    createsql = "create table %s ( %s )" % (tablename, collist)
                elif len(line) == 0:
                    self.log.AppendText("process stop at number %d \n" % (reader.line_num, ))
                    break
                else:
                    insertSql = "insert into %s values(" % tablename
                    for col in line:
                        insertSql = insertSql + "'" + col + "', "
                    insertSql = insertSql[0:-2] + ")"
                    insqllist.append(insertSql)
        
            try:
                self.conn.execute("drop table "+tablename)
            except sqlite3.Error:
                self.log.AppendText("No this table error.\n")
            self.conn.commit()
            self.conn.execute(createsql)
            self.conn.commit()
            for index, il in enumerate(insqllist):
                self.conn.execute(il)
                if index == 100:
                    self.conn.commit()
            self.conn.commit()
            self.log.AppendText("Insert source data successfully\n")
        
if __name__ == '__main__':
    pass
    
