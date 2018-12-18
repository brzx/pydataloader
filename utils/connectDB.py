#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import os

class CreateDB():
    def __init__(self, dbname, logText):
        self.logText = logText
        self.conn = sqlite3.connect(dbname)
        self.create_tab()
        self.conn.close()
        self.logText.AppendText("Created database successfully\n")

    def create_tab(self):
        try:
            self.conn.execute("drop table configuration")
        except sqlite3.OperationalError as e:
            self.logText.AppendText(e.args[0])
            self.logText.AppendText("\n")
        else:
            self.logText.AppendText("Table configuration deleted successfully\n")
        
        try:
            self.conn.execute("drop table rule_reference")
        except sqlite3.OperationalError as e:
            self.logText.AppendText(e.args[0])
            self.logText.AppendText("\n")
        else:
            self.logText.AppendText("Table rule_reference deleted successfully\n")
        
        try:
            self.conn.execute("drop table mapping")
        except sqlite3.OperationalError as e:
            self.logText.AppendText(e.args[0])
            self.logText.AppendText("\n")
        else:
            self.logText.AppendText("Table mapping deleted successfully\n")
        
        try:
            self.conn.execute('''create table configuration(
                                     cid integer primary key autoincrement,
                                     cname text unique,
                                     load_type text,
                                     url text,
                                     username text,
                                     pwd text,
                                     source_file text,
                                     target_table text,
                                     idate text,
                                     udate text);
                                 ''')
        except sqlite3.OperationalError as e:
            self.logText.AppendText(e.args[0])
            self.logText.AppendText("\n")
        else:
            self.logText.AppendText("Table configuration created successfully\n")
        try:
            self.conn.execute('''create table rule_reference(
                                     rid integer primary key autoincrement,
                                     cid int not null,
                                     rule_name text unique,
                                     rule_type text,
                                     lookup_object text,
                                     condition text,
                                     out_field text,
                                     look_field text,
                                     where_c text,
                                     rindex integer,
                                     idate text,
                                     udate text);
                                 ''')
        except sqlite3.OperationalError as e:
            self.logText.AppendText(e.args[0])
            self.logText.AppendText("\n")
        else:
            self.logText.AppendText("Table rule_reference created successfully\n")
        try:
            self.conn.execute('''create table mapping(
                                     mid integer primary key autoincrement,
                                     cid int not null,
                                     source_field text,
                                     target_field text,
                                     field_type text,
                                     field_length text,
                                     rule text,
                                     reference text,
                                     iskey text,
                                     isvariable text,
                                     mindex integer,
                                     idate text,
                                     udate text);
                                 ''')
        except sqlite3.OperationalError as e:
            self.logText.AppendText(e.args[0])
            self.logText.AppendText("\n")
        else:
            self.logText.AppendText("Table mapping created successfully\n")

class ConnectDB():
    def __init__(self, dbname, logText):
        self.conn = sqlite3.connect(dbname)
        self.logText = logText
        self.logText.AppendText("Open database successfully\n")
    def get_conn(self):
        return self.conn
    def close_conn(self):
        self.conn.close()
        self.logText.AppendText("Close database successfully\n")

