#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, logging, json, logging.config, pdb, sqlite3, time
import iLoad, configWizard, loadingLookupTable, createView
from utils import connectDB, iLoadTools

reload(sys)
sys.setdefaultencoding("utf8")

def setup_logging(filepath, scheduleName, default_path="logging.json", default_level=logging.INFO):
    path = default_path
    if os.path.exists(path):
        with open(path, "r") as f:
            config = json.load(f)
            config["handlers"]["info_file_handler"]["filename"] = filepath + "\\schedule_info_" + scheduleName + ".log"
            config["handlers"]["error_file_handler"]["filename"] = filepath + "\\schedule_error_" + scheduleName + ".log"
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


class MultiScheduleLoad():
    def __init__(self, scheduleFile, logger):
        self.scheduleFile = scheduleFile
        self.logger = logger
        
    def run(self):
        with open(self.scheduleFile) as json_file:
            data = json.load(json_file)
        if data["identifier"] == "iLoadMultipleTargetsConfig":
            self.logger.info("Start to schedule loading......")
            jobList = []
            for i in range(1, len(data["list"])+1):
                for li in data["list"]:
                    if int(li[0]) == i:
                        jobList.append(li[1])
            
            for j in jobList:
                self.loadJob(j) #full load job j to target
        else:
            self.logger.info(2)

    def loadJob(self, job):
        dbfile = iLoad.workspace + "\\" + job + "\\" + job + ".zdb"
        vlog = VirtualLog(self.logger)
        lookTab = loadingLookupTable.LookupTable(dbfile, vlog)
        lookTab.loading()
        link = connectDB.ConnectDB(dbfile, vlog)
        conn = link.get_conn()
        cv = createView.CreateView(conn)
        dt = cv.getViewFieldList()
        allLi1 = cv.jointFields1(dt)
        sql1 = cv.createViewSQL1(dt, allLi1)
        dbt = iLoadTools.DatabaseTool(conn)
        configName = dbt.getConfigName()
        try:
            conn.execute("drop view %s" % (configName+"_tar_vw1", ))
        except sqlite3.OperationalError as e:
            self.logger.info(e.args[0])
        conn.execute(sql1) # create view 1
        self.logger.info("create view 1")
        
        allLi2 = cv.jointFields2(dt)
        sql2 = cv.createViewSQL2(dt, allLi2)
        try:
            conn.execute("drop view %s" % (configName+"_tar_vw2", ))
        except sqlite3.OperationalError as e:
            self.logger.info(e.args[0])
        conn.execute(sql2) # create view 2
        conn.commit()
        self.logger.info("create view 2")
        
        try:
            conn.execute("drop table "+configName+"_tar_vw2_tab")
        except sqlite3.OperationalError as e:
            self.logger.info(e.args[0])
        else:
            self.logger.info("Table %s droped successfully" % \
            (configName+"_tar_vw2_tab", ))
        finalSQL = "create table %s as select * from %s" % \
                   (configName+"_tar_vw2_tab", configName+"_tar_vw2", )
        conn.execute(finalSQL)
        conn.commit()
        self.logger.info("final table created")
        time.sleep(0.03)
        
        self.logger.info("load data to target starting")
        credential = dbt.getCredential()
        tarList = dbt.getTarFieldList()
        tarTable = dbt.getTargetTable()
        loadType = dbt.getLoadType()
        keys = dbt.getKey()
        self.logger.info("execute importing data")
        self.logger.info(tarTable)
        self.logger.info(str(keys))
        data = dbt.getViewData(tarList, configName+"_tar_vw2_tab")
        try:
            tarClass = iLoadTools.getLoadTypeClass(loadType)
            tt = tarClass(credential, vlog)
        except Exception as e:
            self.logger.info(e.args[0])
        tar_conn = tt.getConnection()
        if tar_conn:
            if keys["haskey"] == "one key":
                self.logger.info("one key")
                tt.upsertData(data, tarTable, tarList, credential, keys)
            elif keys["haskey"] == "no key":
                self.logger.info("no key")
                tt.insertData(data, tarTable, tarList, credential)
            else:
                self.logger.info("You can only set up one primary key.")
        
        link.close_conn()
        self.logger.info("job "+job+" has been finished")

class VirtualLog:
    def __init__(self, logger):
        self.logger = logger
    def AppendText(self, str):
        self.logger.info(str)

if __name__ == "__main__":
    scheduleName = sys.argv[1]
    filepath = iLoad.schedulespace
    setup_logging(filepath, scheduleName)
    scheduleFile = iLoad.schedulespace + "\\" + scheduleName + ".json"
    logger = logging.getLogger(__name__)
    msl = MultiScheduleLoad(scheduleFile, logger)
    msl.run()
