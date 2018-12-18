#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, time
import pdb
from utils import connectDB, iLoadTools

class CreateView:

    def __init__(self, conn):
        self.conn = conn
        dbt = iLoadTools.DatabaseTool(conn)
        self.keys = dbt.getKey()
        self.variables = dbt.getVariable()
        self.configName = dbt.getConfigName()
        self.sourceTable = dbt.getSourceTable()
    
    def getViewFieldList(self):
        reDict = {}
        if self.variables["hasvariable"] != "no variable":
            sql = "select source_field, \
                          target_field, \
                          rule, \
                          reference, \
                          mid, \
                          isvariable, \
                          iskey \
                     from mapping \
                    where isvariable = 'True'"
            cursor = self.conn.execute(sql)
            vbli = []
            for row in cursor:
                vbli.append(row[1])
            
            sql = "select mid, \
                          source_field \
                     from mapping \
                    where rule in ('function', 'lookup')"
            cursor = self.conn.execute(sql)
            fli = []
            for row in cursor:
                inLi = row[1].split(",")
                inLi.insert(0, row[0])
                fli.append(inLi)
            useVariableMidLiDUP = []
            for v in vbli:
                for f in fli:
                    if f.count(v) > 0:
                        useVariableMidLiDUP.append(f[0])
            useVariableMidLi = self.removeDuplicateList(useVariableMidLiDUP)
            print useVariableMidLi
            sql = "select source_field, \
                          target_field, \
                          rule, \
                          reference, \
                          mid, \
                          isvariable, \
                          iskey \
                     from mapping"
            cursor = self.conn.execute(sql)
            li = []
            for row in cursor:
                li.append(row)
            directLi = filter(lambda x:x[2]=="direct", li)
            reDict["directLi"] = directLi
            functionLi = filter(lambda x:x[4] not in tuple(useVariableMidLi), filter(lambda x:x[2]=="function", li))
            reDict["functionLi"] = functionLi
            useVariableLookupLi = filter(lambda x:x[4] in tuple(useVariableMidLi), filter(lambda x:x[2]=="lookup", li))
            reDict["useVariableLookupLi"] = useVariableLookupLi
            lookupLi = filter(lambda x:x[4] not in tuple(useVariableMidLi), filter(lambda x:x[2]=="lookup", li))
            reDict["lookupLi"] = lookupLi
            #pdb.set_trace()
            if len(useVariableMidLi) > 1:
                sql = "select source_field, \
                              target_field, \
                              rule, \
                              reference, \
                              mid, \
                              isvariable, \
                              iskey \
                         from mapping \
                        where rule != 'lookup' \
                          and mid in %s" % (str(tuple(useVariableMidLi)), )
            else:
                sql = "select source_field, \
                              target_field, \
                              rule, \
                              reference, \
                              mid, \
                              isvariable, \
                              iskey \
                         from mapping \
                        where rule != 'lookup' \
                          and mid in %s" % ("("+str(useVariableMidLi[0])+")", )
            cursor = self.conn.execute(sql)
            mli = []
            for row in cursor:
                mli.append(row)
            
            reDict["useVariableFunctionLi"] = mli
        else:
            sql = "select source_field, \
                          target_field, \
                          rule, \
                          reference, \
                          mid, \
                          isvariable, \
                          iskey \
                     from mapping"
            cursor = self.conn.execute(sql)
            li = []
            for row in cursor:
                li.append(row)
            directLi = filter(lambda x:x[2]=="direct", li)
            reDict["directLi"] = directLi
            functionLi = filter(lambda x:x[2]=="function", li)
            reDict["functionLi"] = functionLi
            lookupLi = filter(lambda x:x[2]=="lookup", li)
            
            reDict["lookupLi"] = lookupLi
        
        return reDict
    
    def jointFields1(self, fieldDict, prefix="src"):
        allLi = []
        directLi = fieldDict["directLi"]
        functionLi = fieldDict["functionLi"]
        lookupLi = fieldDict["lookupLi"]
        for i in directLi:
            allLi.append(prefix+"."+i[0]+" as "+i[1])
        for j in functionLi:
            sql = "select rule_reference.rule_name, \
                          rule_reference.rule_type, \
                          rule_reference.condition, \
                          mapping.target_field \
                     from rule_reference \
                    inner join mapping on rule_reference.rule_name = mapping.reference \
                    where rule_name = '%s'" % (j[3])
            cursor = self.conn.execute(sql)
            for row in cursor:
                allLi.append(row[2]+" as "+row[3])
        for k in lookupLi:
            sql = "select rule_reference.rule_name, \
                          rule_reference.look_field, \
                          mapping.target_field \
                     from rule_reference \
                    inner join mapping on rule_reference.rule_name = mapping.reference \
                    where rule_name = '%s'" % (k[3])
            cursor = self.conn.execute(sql)
            for row in cursor:
                allLi.append(row[0]+"."+row[1]+" as "+row[2])
        
        return allLi
    
    def jointFields2(self, fieldDict, prefix="src"):
        # for view2 field list
        allLi = []
        directLi = fieldDict["directLi"]
        functionLi = fieldDict["functionLi"]
        lookupLi = filter(lambda x:x[5]!="True", fieldDict["lookupLi"])
        
        for i in directLi:
            allLi.append(prefix+"."+i[1])
        for j in functionLi:
            allLi.append(prefix+"."+j[1])
        for k in lookupLi:
            allLi.append(prefix+"."+k[1])
        
        if fieldDict.has_key("useVariableFunctionLi"):
            useVariableFunctionLi = fieldDict["useVariableFunctionLi"]
            for l in useVariableFunctionLi:
                sql = "select rule_reference.rule_name, \
                              rule_reference.rule_type, \
                              rule_reference.condition, \
                              mapping.target_field \
                         from rule_reference \
                        inner join mapping on rule_reference.rule_name = mapping.reference \
                        where rule_name = '%s'" % (l[3])
                cursor = self.conn.execute(sql)
                for row in cursor:
                    allLi.append(row[2]+" as "+row[3])
        
        if fieldDict.has_key("useVariableLookupLi"):
            useVariableLookupLi = fieldDict["useVariableLookupLi"]
        
            for m in useVariableLookupLi:
                sql = "select rule_reference.rule_name, \
                              rule_reference.rule_type, \
                              rule_reference.look_field, \
                              mapping.target_field \
                         from rule_reference \
                        inner join mapping on rule_reference.rule_name = mapping.reference \
                        where rule_name = '%s'" % (m[3])
                cursor = self.conn.execute(sql)
                for row in cursor:
                    allLi.append(row[0]+"."+row[2]+" as "+row[3])
        
        return allLi
    
    def getLookupRule(self, rule_name):
        sql = "select rule_name, \
                      rule_type, \
                      lookup_object, \
                      condition, \
                      out_field, \
                      look_field, \
                      where_c \
                 from rule_reference \
                where rule_name = '%s'" % (rule_name, )
        cursor = self.conn.execute(sql)
        for row in cursor:
            r = row
        return r
        
    def createViewSQL1(self, fieldDict, allLi, prefix="src"):
        sql = "create view %s_tar_vw1 as select src.*, %s from %s %s " % \
              (self.configName, reduce(lambda x,y:x+","+y, allLi), self.sourceTable, prefix, )
        lookup_str = ""
        if len(fieldDict["lookupLi"]) > 0:
            for i in fieldDict["lookupLi"]:
                rule = self.getLookupRule(i[3])
                lookup_str = lookup_str + " left join %s %s on %s " % \
                (rule[2]+"_"+rule[0], rule[0], rule[3], )
        else:
            lookup_str = ""
        
        sql = sql + lookup_str
        return sql
    
    def createViewSQL2(self, fieldDict, allLi, prefix="src"):
        sql = "create view %s_tar_vw2 as select %s from %s %s " % \
              (self.configName, reduce(lambda x,y:x+","+y, allLi), self.configName+"_tar_vw1", prefix, )
        
        lookup_str = ""
        if fieldDict.has_key("useVariableLookupLi"):
            if len(fieldDict["useVariableLookupLi"]) > 0:
                for i in fieldDict["useVariableLookupLi"]:
                    rule = self.getLookupRule(i[3])
                    lookup_str = lookup_str + " left join %s %s on %s " % \
                    (rule[2]+"_"+rule[0], rule[0], rule[3], )
            else:
                lookup_str = ""
        
        sql = sql + lookup_str
        
        return sql
    
    def removeDuplicateList(self, li):
        newli = []
        for v in li:
            if newli.count(v) == 0:
                newli.append(v)
        return newli
    
    
    
    
    
    
    
    
    
    
