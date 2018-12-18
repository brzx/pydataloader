#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pdb, os, json
import iLoad

class MakeSpace:
    def __init__(self):
        pass
    
    def makeWorkspace(self):
        li = os.listdir(os.curdir)
        existsFolder = False
        for l in li:
            if l == "workspace":
                existsFolder = True
        if not existsFolder:
            os.mkdir("workspace")
        self.workspace = os.path.abspath(os.curdir) + "\\workspace"
    
    def makeSchedulespace(self):
        li = os.listdir(os.curdir)
        existsFolder = False
        for l in li:
            if l == "schedulespace":
                existsFolder = True
        if not existsFolder:
            os.mkdir("schedulespace")
        self.schedulespace = os.path.abspath(os.curdir) + "\\schedulespace"
        
    def getWorkspace(self):
        return self.workspace
        
    def getSchedulespace(self):
        return self.schedulespace
        
    def getHomePath(self):
        return os.path.abspath(os.curdir)
    
class GetConfiguration:
    def __init__(self, config_file):
        with open(config_file) as json_file:
            self.data = json.load(json_file)
    
    def getData(self):
        return self.data
    
class GetValidConfig:
    def __init__(self):
        self.workspace = iLoad.workspace
        self.list = []
        
    def getValidConfig(self):
        li = os.listdir(self.workspace)
        for l in li:
            file = self.workspace + "\\" + l + "\\" + l + ".json"
            gc = GetConfiguration(file)
            try:
                if gc.getData()["identifier"] == "iLoadConfiguration":
                    self.list.append(l)
            except Exception as ex:
                print(ex)
            del gc
        return self.list

class DatabaseTool:
    def __init__(self, conn):
        self.conn = conn
    
    def getSourceFileName(self):
        filename = ""
        sql = "select source_file \
                 from configuration \
                limit 1"
        cursor = self.conn.execute(sql)
        for row in cursor:
            filename = row[0]
        return filename

    def getLoadType(self):
        loadtype = ""
        sql = "select load_type \
                 from configuration \
                limit 1"
        cursor = self.conn.execute(sql)
        for row in cursor:
            loadtype = row[0]
        return loadtype

    def getCredential(self):
        credential = {}
        url = ""
        sql = "select username, \
                      pwd, \
                      url \
                     from configuration \
                    limit 1"
        cursor = self.conn.execute(sql)
        for row in cursor:
            credential["username"] = row[0]
            credential["password"] = row[1]
            credential["url"] = row[2]
        return credential

    def getSourceTable(self):
        src_table = ""
        sql = "select source_file \
                 from configuration \
                limit 1"
        cursor = self.conn.execute(sql)
        for row in cursor:
            src_table = row[0][:-4]
        return src_table

    def getTargetTable(self):
        target_table = ""
        sql = "select target_table \
                 from configuration \
                limit 1"
        cursor = self.conn.execute(sql)
        for row in cursor:
            target_table = row[0]
        return target_table

    def getMappingCount(self):
        count = 0
        sql = "select count(1) \
                 from mapping"
        cursor = self.conn.execute(sql)
        for row in cursor:
            count = row[0]
        return count
        
    def getConfigName(self):
        sql = "select cname \
                 from configuration"
        cursor = self.conn.execute(sql)
        for row in cursor:
            fi = row[0]
        return fi
        
    def getKey(self):
        keys = {}
        li = []
        sql = "select target_field, \
                      rule, \
                      reference, \
                      iskey \
                 from mapping \
                where iskey = 'True'"
        cursor = self.conn.execute(sql)
        for row in cursor:
            li.append(row)
        
        if len(li) == 0:
            keys["haskey"] = "no key"
        elif len(li) > 1:
            keys["haskey"] = "multi keys"
        else:
            keys["haskey"] = "one key"
            keys["keyinfo"] = li[0]
        
        return keys
    
    def getVariable(self):
        variables = {}
        li = []
        sql = "select mid, \
                      source_field, \
                      target_field, \
                      reference, \
                      isvariable \
                 from mapping \
                where isvariable = 'True'"
        cursor = self.conn.execute(sql)
        for row in cursor:
            li.append(row)
        
        if len(li) == 0:
            variables["hasvariable"] = "no variable"
        elif len(li) > 1:
            variables["hasvariable"] = "multi variables"
            for index,i in enumerate(li):
                variables["variable"+str(index+1)] = i
        else:
            variables["hasvariable"] = "one variable"
            variables["variable1"] = li[0]
        
        return variables
        
    def getTarFieldList(self):
        sql = "select target_field, field_type \
                 from mapping \
                where isvariable != 'True'"
        cursor = self.conn.execute(sql)
        li = []
        for row in cursor:
            li.append({'name':row[0], 'type':row[1]})
        return li
    
    def getViewData(self, li, vwnm):
        reLi = []
        nli = map(lambda x:x['name'], li)
        sql = "select distinct %s from %s" % \
              (reduce(lambda x,y:x+","+y, nli), vwnm)
        cursor = self.conn.execute(sql)
        for row in cursor:
            reLi.append(row)
        return reLi

    def getPreviewData(self, li, vwnm):
        reLi = []
        nli = map(lambda x:x['name'], li)
        sql = "select distinct %s from %s limit 10" % \
              (reduce(lambda x,y:x+","+y, nli), vwnm)
        cursor = self.conn.execute(sql)
        for row in cursor:
            reLi.append(row)
        return reLi

    def getRowCount(self, tabnm):
        reLi = []
        sql = "select count(1) from %s limit 10" % (tabnm, )
        cursor = self.conn.execute(sql)
        for row in cursor:
            reLi.append(row)
        return reLi

    
LoadTypeList = ["", "Salesforce.com", "Oracle", "SAP"]
def getLoadTypeIndex(lt):
    ltDict = {}
    for index, item in enumerate(LoadTypeList):
        ltDict[item] = index
    try:
        return ltDict[lt]
    except Exception as e:
        return 0

def getLoadTypeClass(lt):
    if lt == "Salesforce.com":
        from sfdcTools import SFDCTools as tar_class
    elif lt == "Oracle":
        from oracleTools import OracleTools as tar_class
    elif lt == "SAP":
        from sapTools import SAPTools as tar_class
    return tar_class

URLDict = {
    "Salesforce.com" : ["", "test", "production"],
    "Oracle" : ["", "ORAtest", "ORAproduction"],
    "SAP" : ["", "SAPtest", "SAPproduction"],
    "" : [],
}
def setURLChoice(choice, lt, url):
    li = URLDict[lt]
    choice.Clear()
    for item in li:
        choice.Append(item)
    choice.SetSelection(getURLIndex(li, url))

def getURLIndex(list, url):
    renum = 0
    for index, item in enumerate(list):
        if item == url:
            renum = index
    return renum

def charReplace(str):
    SYMBOL = "`~!@#$%^&*()_+-=[]\{}|;':,./<>?"
    restr = str
    for s in SYMBOL:
        restr = restr.replace(s,"_")
    
    return restr
