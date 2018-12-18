#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, csv, sqlite3, pdb, codecs
import mainFrame
from utils import iLoadTools

class SourceFile:
    def __init__(self, name, conn, log):
        self.conn = conn
        self.name = name
        self.log = log

    def loading(self):
        SYMBOL = "`~!@#$%^&*()_+-=[]\{}|;':,./<>?"
        pdb.set_trace()
        dt = iLoadTools.DatabaseTool(self.conn)
        csvfile = []
        filepath = os.curdir + "\\keymsgkr.zdb"
        csvfile.append(filepath)

        for cf in csvfile:
            fo = codecs.open(cf,"rb","utf-8")
            reader = csv.reader(fo)
            tablename = os.path.basename(cf)[0:-4]
            nli = []
            insqllist = []
            createsql = ""
            for line in reader:
                if reader.line_num == 1:
                    for str in line:
                        str = str.replace(" ","")
                        for s in SYMBOL:
                            str = str.replace(s,"_")
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
            #print(createsql)
            self.conn.execute(createsql)
            self.conn.commit()
            for index, il in enumerate(insqllist):
                self.conn.execute(il)
                if index == 100:
                    self.conn.commit()
            self.conn.commit()
            self.log.AppendText("Insert source data successfully\n")
            
class LogText:
    def __init__(self):
        pass
    def AppendText(self, str):
        print(str)
        
class ConnectDB():
    def __init__(self, dbname, log):
        self.conn = sqlite3.connect(dbname)
    def get_conn(self):
        return self.conn
    def close_conn(self):
        self.conn.close()
        
if __name__ == '__main__':
    from utils import connectDB
    log = LogText()
    dbfile = os.curdir + "\\keymsgkr.zdb"
    link = ConnectDB(dbfile, log)
    conn = link.get_conn()
    srcfile = SourceFile("keymsgkr", conn, log)
    srcfile.loading()
    
