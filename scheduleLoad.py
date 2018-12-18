#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, logging, json, logging.config, pdb
import iLoad, configWizard
from utils import connectDB, iLoadTools

def setup_logging(filepath, default_path="logging.json", default_level=logging.INFO):
    path = default_path
    if os.path.exists(path):
        with open(path, "r") as f:
            config = json.load(f)
            config["handlers"]["info_file_handler"]["filename"] = filepath + "\\" + config["handlers"]["info_file_handler"]["filename"]
            config["handlers"]["error_file_handler"]["filename"] = filepath + "\\" + config["handlers"]["error_file_handler"]["filename"]
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
    
class ScheduleLoad():
    def __init__(self, dbfile, logText):
        self.dbfile = dbfile
        self.logText = logText
        
    def run(self):
        link = connectDB.ConnectDB(self.dbfile, self.logText)
        conn = link.get_conn()
        db_final = iLoadTools.DatabaseTool(conn)
        configName = db_final.getConfigName()
        credential = db_final.getCredential()
        tarList = db_final.getTarFieldList()
        tarTable = db_final.getTargetTable()
        loadType = db_final.getLoadType()
        keys = db_final.getKey()
        
        self.logText.AppendText("execute importing data")
        self.logText.AppendText(tarTable)
        self.logText.AppendText(str(keys))
        data = db_final.getViewData(tarList, configName+"_tar_vw2_tab")
        try:
            tarClass = iLoadTools.getLoadTypeClass(loadType)
            tt = tarClass(credential, self.logText)
        except Exception as e:
            self.logText.AppendText(e.args[0])
        tar_conn = tt.getConnection()
        if tar_conn:
            if keys["haskey"] == "one key":
                self.logText.AppendText("one key")
                tt.upsertData(data, tarTable, tarList, credential, keys)
            elif keys["haskey"] == "no key":
                self.logText.AppendText("no key")
                tt.insertData(data, tarTable, tarList, credential)
            else:
                self.logText.AppendText("You can only set up one primary key.")
        link.close_conn()
        
class VirtualLog:
    def __init__(self):
        pass
    def AppendText(self, str):
        logging.info(str)

if __name__ == "__main__":
    configName = sys.argv[1]
    filepath = iLoad.workspace + "\\" + configName
    setup_logging(filepath)
    logText = VirtualLog()
    dbfile = iLoad.workspace + "\\" + configName + "\\" + configName + ".zdb"
    sl = ScheduleLoad(dbfile, logText)
    sl.run()
    
