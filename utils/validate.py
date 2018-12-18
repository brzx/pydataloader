#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3, re, pdb
from utils import *

class Validation:

    def __init__(self, conn, log):
        self.conn = conn
        self.log = log
        self.reflag = False
    
    def validResult1(self):
        dt = iLoadTools.DatabaseTool(self.conn)
        try:
            tarClass = iLoadTools.getLoadTypeClass(dt.getLoadType())
            tt = tarClass(dt.getCredential(), self.log)
        except Exception as e:
            self.log.AppendText(str(e))

        tar_conn = tt.getConnection()
        if tar_conn:
            self.log.AppendText(str(tar_conn))
            self.log.AppendText("\n")
            self.reflag = True

            if tt.validTarget(dt.getTargetTable()):
                self.reflag = True
            else:
                self.reflag = False
        else:
            self.reflag = False
        
        if dt.getMappingCount() > 0:
            self.reflag = True
        else:
            self.log.AppendText("no mapping exists\n")
            self.reflag = False
        
        # will do more validation here
        return self.reflag

    def validFinalTable(self):
        vl = False
        count = 0
        dbt = iLoadTools.DatabaseTool(self.conn)
        configName = dbt.getConfigName()
        sql = "select count(1) from %s_tar_vw2_tab" % (configName, )
        try:
            cursor = self.conn.execute(sql)
            for row in cursor:
                count = row[0]
        except sqlite3.OperationalError as ex:
            self.log.AppendText(str(ex))
            self.log.AppendText("\n")
        finally:
            if count == 0:
                self.log.AppendText("No data was generated\n")
            elif count > 0:
                logText = "%d rows was generated\n" % (count, )
                self.log.AppendText(logText)
                vl = True
        return vl
        
    '''
    def validURL(self):
        dt = iLoadTools.DatabaseTool(self.conn)
        url = dt.getURL()
        if re.match(r"^https://.+", url) is not None:
            self.reflag = True
        else:
            self.reflag = False
            self.log.AppendText("URL format is not correct, please use https://...... format\n")
    '''
    
    def genNewlist(self, li, s):
        newli0 = []
        newli1 = []
        for L0 in li:
            if L0.find(s) >= 0:
                for i in L0.split(s):
                    newli0.append(i)
            else:
                newli0.append(L0)
        for l in newli0:
            if newli1.count(l) == 0:
                newli1.append(l)
        return map(lambda x:x.lower(), newli1)
        
    def getFields(self, sql, s=","):
        li = []
        reli = []
        cursor = self.conn.execute(sql)
        for row in cursor:
            li.append(row[0])
        reli = self.genNewlist(li, s)
        return reli
        
    def getLookupRuleList(self):
        reli = []
        sql = "select rule_name \
                 from rule_reference \
                where rule_type = 'lookup'"
        cursor = self.conn.execute(sql)
        for row in cursor:
            reli.append(row[0])
        return reli
    
    def validateLookupfield(self):
        reDict = {}
        logli = []
        srcLi = self.getFields("select source_field \
                                  from mapping")
        tarLi = self.getFields("select target_field \
                                  from mapping")
        for r in self.getLookupRuleList():
            sql1 = "select out_field \
                      from rule_reference \
                     where rule_name = '%s'" % (r, )
            outLi = self.getFields(sql1, ",")
            sql2 = "select condition \
                      from rule_reference \
                     where rule_type = 'lookup' \
                       and rule_name = '%s'" % (r, )
            LkConLi = self.getFields(sql2, "=")
            for lk1 in LkConLi:
                if srcLi.count(lk1)== 0 and tarLi.count(lk1) == 0:
                    logli.append("Rule %s condition field %s does not exists in any table" % (r,lk1, ))
            for lk2 in LkConLi:
                if tarLi.count(lk2) > 0 and outLi.count(lk2) == 0:
                    logli.append("Rule %s condition target field %s does not exists in out fileds" % (r, lk2, ))
        reDict["logli"] = logli
        return reDict
        
    def validateSourcefield(self):
        reDict = {}
        logli = []
        srcLi = self.getFields("select source_field \
                                  from mapping")
        field = reduce(lambda x,y: x+","+y, srcLi)
        sql = "select %s from %s limit 1" % (field, self.getSourceTable(), )
        try:
            self.conn.execute(sql)
        except sqlite3.OperationalError as e:
            logli.append(e.args[0])
        reDict["logli"] = logli
        return reDict
        
    def validateLookupUnique(self):
        reDict = {}
        logli = []
        for r in self.getLookupRuleList():
            sql1 = "select out_field \
                      from rule_reference \
                     where rule_name = '%s'" % (r, )
            outLi = self.getFields(sql1, ",")
            sql2 = "select condition \
                      from rule_reference \
                     where rule_type = 'lookup' \
                       and rule_name = '%s'" % (r, )
            LkConLi = self.getFields(sql2, "=")
            sql3 = "select lookup_object \
                      from rule_reference \
                     where rule_name = '%s'" % (r, )
            LookupObj = self.getFields(sql3)
            for f in LkConLi:
                if outLi.count(f) > 0:
                    sql = "select %s, count(1) from %s group by %s having count(1)>1" % \
                          (f, LookupObj[0]+"_"+r, f )
                    print sql
                    try:
                        cursor = self.conn.execute(sql)
                    except sqlite3.OperationalError as e:
                         logli.append(e.args[0])
                    else:
                        if len(cursor.fetchall()) > 0:
                            logli.append("Rule %s lookup field %s is not unique" % (r, f, ))
        reDict["logli"] = logli
        return reDict
    
