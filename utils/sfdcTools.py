#!/usr/bin/python
# -*- coding: utf-8 -*-

import targetTools
import beatbox, pdb
import datetime

class SFDCTools(targetTools.TargetTools):

    def __init__(self, credential, log):
        self.credential = credential
        self.log = log

    def getConnection(self):
        self.sf = beatbox._tPartnerNS
        self.svc = beatbox.PythonClient()
        beatbox.gzipRequest = False
        if self.credential["url"] == "test":
            self.svc.serverUrl = self.svc.serverUrl.replace('login.', 'test.')
        try:
            self.svc.login(self.credential["username"], self.credential["password"])
            return self.svc
        except Exception as e:
            self.log.AppendText(str(e))
            self.log.AppendText("\n")
            return None

    def validTarget(self, target):
        reflag = False
        soql = "select id from %s limit 1" % (target, )
        try:
            self.svc.query(soql)
            reflag = True
        except Exception as e:
            self.log.AppendText("target table does not exists\n")
            self.log.AppendText(str(e))
            self.log.AppendText("\n")
        return reflag

    def upsertData(self, data, tarTable, tarList, credential, keys):
        fieldList = self.svc.describeSObjects(tarTable)[0].fields.keys()
        fieldDict = {}
        for f in fieldList:
            for t in tarList:
                if f.upper() == t.upper():
                    fieldDict[t] = f
        if not any(f == keys["keyinfo"][0].upper() \
                   for f in map(lambda x:x.upper(), fieldList)):
            self.log.AppendText("Skipped 'upsert' because the custom \
                                external Id field doesn't exist")
        self.log.AppendText("upsert\n")
        
        for row in data:
            upsertDict = {}
            upsertDict["type"] = tarTable
            for n, t in enumerate(tarList):
                upsertDict[fieldDict[t]] = row[n]
            self.log.AppendText(str(upsertDict))
            self.log.AppendText("\n")
            try:
                ur = self.svc.upsert(fieldDict[keys["keyinfo"][0]], upsertDict)
                self.log.AppendText(str(ur[0]))
                self.log.AppendText("\n")
            except Exception as e:
                self.log.AppendText("\n")
                self.log.AppendText(str(e))
                self.log.AppendText("\n")
        self.log.AppendText("upsert data finish\n")

    def insertData(self, data, tarTable, tarList, credential):
        self.log.AppendText("insert\n")
        tl = map(lambda x:x['name'], tarList)
        for row in data:
            insertDict = {}
            insertDict["type"] = tarTable
            for index, item in enumerate(tl):
                if tarList[index]['name'] == item and tarList[index]['type'] == 'text':
                    insertDict[item] = row[index]
                elif tarList[index]['name'] == item and tarList[index]['type'] == 'date':
                    insertDict[item] = datetime.datetime(int(row[index].split('-')[0]),
                        int(row[index].split('-')[1]), int(row[index].split('-')[2]))
                else:
                    pass
            self.log.AppendText(str(insertDict))
            #pdb.set_trace()
            try:
                ur = self.svc.create([insertDict])
                self.log.AppendText(str(ur[0]))
                self.log.AppendText("\n")
            except Exception as e:
                self.log.AppendText("\n")
                self.log.AppendText(str(e))
                self.log.AppendText("\n")
        self.log.AppendText("insert data finish\n")

if __name__ == "__main__":
    pass
