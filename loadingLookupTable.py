#!/usr/bin/python
# -*- coding: utf-8 -*-

import base64, pdb, sqlite3
from utils import iLoadTools, connectDB

class LookupTable:
    #this class just for SFDC to get lookup table data
    def __init__(self, dbfile, log):
        self.link = connectDB.ConnectDB(dbfile, log)
        self.conn = self.link.get_conn()
        self.log = log

    def createTab(self, tab, create_sql):
        try:
            self.conn.execute("drop table "+tab)
        except sqlite3.OperationalError as e:
            self.log.AppendText(e.args[0])
            self.log.AppendText("\n")
        else:
            self.log.AppendText("Table %s droped successfully\n" % (tab, ))
        try:
            self.conn.execute(create_sql)
        except sqlite3.OperationalError as e:
            self.log.AppendText(e.args[0])
            self.log.AppendText("\n")
        else:
            self.log.AppendText("Table %s created successfully\n" % (tab, ))

    def loading(self):
        dt = iLoadTools.DatabaseTool(self.conn)
        credential = dt.getCredential()
        sql = "select * from rule_reference where rule_type = 'lookup'"
        cursor = self.conn.execute(sql)
        li = []
        for r in cursor:
            li.append(r)
        if len(li) !=0:
            for row in li:
                if row[8] == '':
                    wherec = ""
                else:
                    wherec = " where %s" % (row[8],)
                soql = "select %s from %s" % (row[6], row[4])
                soql = soql + wherec
                try:
                    tarClass = iLoadTools.getLoadTypeClass(dt.getLoadType())
                    tt = tarClass(dt.getCredential(), self.log)
                except Exception as e:
                    self.log.AppendText(str(e))
                    self.log.AppendText("\n")
                tar_conn = tt.getConnection()
                if tar_conn:
                    try:
                        query_result = tar_conn.query(soql)
                        fields = row[6].split(",")
                        length = len(fields)
                        create_sql = "create table %s (%s)" % \
                                     (row[4]+"_"+row[2], 
                                      reduce(lambda x,y:x+", "+y, map(lambda x:x+" text", fields)), )
                        self.createTab(row[4]+"_"+row[2], create_sql)
                        st = ""
                        for i in fields:
                            st = st + "'%s',"
                        presql = "insert into %s (%s) values(%s)" % \
                                 (row[4]+"_"+row[2], 
                                  reduce(lambda x,y:x+","+y, fields), st[:-1])
                        if query_result["size"] > 0:
                            while True:
                                for row in query_result['records']:
                                    newDict = {}
                                    for k in row.keys():
                                        if k != 'type':
                                            newDict[k.lower()] = row[k].replace("'", "''")
                                    li = []
                                    li = map(lambda x:newDict[x.lower()], fields)
                                    isql = ""
                                    try:
                                        isql = presql % tuple(li)
                                    except UnicodeError as e:
                                        self.log.AppendText(str(e))
                                        self.log.AppendText("\n")
                                    self.conn.execute(isql)
                        
                                if query_result['done'] is True:
                                    break
                                query_result = tar_conn.queryMore(query_result['queryLocator'])
                    
                        else:
                            self.log.AppendText("There is not any data returned from lookup object\n")
                        self.conn.commit()
                        del(tar_conn)
                    except Exception as e:
                        self.log.AppendText("\n")
                        self.log.AppendText(str(e))
                        self.log.AppendText("\n")
                else:
                    self.log.AppendText("cannot get target system connection\n")
        self.link.close_conn()
    
if __name__ == '__main__':
    pass
