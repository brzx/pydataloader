#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, time, sqlite3, json, pdb
from utils import connectDB

class ConfigFile:
    def __init__(self, name, file, conn, log):
        self.file = file
        self.conn = conn
        self.name = name
        self.log = log
        self.log.AppendText("File is %s \n" % (file, ))
    
    def getJsonData(self):
        gc = GetConfiguration()
        gc.load(self.file)
        return gc.getData()
    
    def insertData(self, configName, data, localtime):
        sql = "insert into configuration(cname, load_type, url, username, pwd, source_file, \
               target_table, idate, udate) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
              (data['cname'], data['load_type'], data['URL'], data['username'], data['pwd'], data['source_file'],
               data['target_table'], localtime, localtime)
        try:
            self.conn.execute(sql)
        except sqlite3.Error as e:
            self.log.AppendText(e.args[0])
            self.log.AppendText("\n")
        self.conn.commit()
    
        sql = "select cid from configuration where cname = '%s'" % (data['cname'], )
        cursor = self.conn.execute(sql)
        for row in cursor:
            cid = row[0]
        
        for rr in data['rule_reference']:
            con = rr['condition'].replace("'", "''")
            if rr['rule_type'] == 'lookup':
                sql = "insert into rule_reference(cid, rule_name, rule_type, lookup_object, condition, out_field, \
                       where_c, idate, udate, look_field, rindex) values (%d, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %d)" % \
                      (cid, rr['rule_name'], rr['rule_type'], rr['lookup_object'], con, rr['out_field'],
                       rr['where_c'], localtime, localtime, rr['look_field'], rr['index'])
                try:
                    self.conn.execute(sql)
                except sqlite3.Error as e:
                    self.log.AppendText(e.args[0])
                    self.log.AppendText("\n")
            elif rr['rule_type'] == 'function':
                sql = "insert into rule_reference(cid, rule_name, rule_type, condition, out_field, idate, udate, rindex) \
                       values (%d, '%s', '%s', '%s', '%s', '%s', '%s', %d)" % \
                      (cid, rr['rule_name'], rr['rule_type'], con, rr['out_field'], localtime, localtime, rr['index'])
                try:
                    self.conn.execute(sql)
                except sqlite3.Error as e:
                    self.log.AppendText(e.args[0])
                    self.log.AppendText("\n")
        self.conn.commit()
    
        for m in data['mapping']:
            sql = "insert into mapping(cid, source_field, target_field, field_type, field_length, rule, reference, idate, \
                   udate, iskey, isvariable, mindex) values (%d, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %d)" % \
                  (cid, m['source_field'], m['target_field'], m['field_type'], m['field_length'], m['rule'], m['reference'],
                   localtime, localtime, m['iskey'], m['isvariable'], m['index'])
            try:
                self.conn.execute(sql)
            except sqlite3.Error as e:
                self.log.AppendText(e.args[0])
                self.log.AppendText("\n")
        self.conn.commit()
    
    def loading(self):
        data = self.getJsonData()
        self.insertData(self.name, data, time.asctime(time.localtime(time.time())))
        self.log.AppendText("Insert configuration data successfully\n")
        
class GetConfiguration:
    def __init__(self):
        pass
    def load(self, config_file):
        with open(config_file) as json_file:
            self.data = json.load(json_file)
    def getData(self):
        return self.data
