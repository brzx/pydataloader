#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx, pdb, sys, os, json, shutil
import mainFrame, titledPage, simpleListCtrl
import newRuleDialog, newMapDialog
import loadingConfigFile, loadingSourceFile, loadingLookupTable
import wx.wizard as wiz
from wx import StaticText
from utils import connectDB, iLoadTools, myimages, validate

wildcard_source = "CSV files (*.csv)|*.csv"
wildcard_exists = "JSON files (*.json)|*.json"

class ConfigWizard(wiz.Wizard):
    def __init__(self, parent, flag):
        wiz.Wizard.__init__(self, parent, -1, "Configuration Wizard", myimages.PyDLWiz.GetBitmap())
        self.SetPageSize((600,800))
        page1 = titledPage.TitledPage(self, "Page 1")
        page2 = titledPage.TitledPage(self, "Page 2")
        page3 = titledPage.TitledPage(self, "Page 3")
        page4 = titledPage.TitledPage(self, "Page 4")
        page5 = titledPage.TitledPage(self, "Page 5")
        self.page1 = page1
        self.page2 = page2
        self.page3 = page3
        self.page4 = page4
        self.page5 = page5
        self.flag = flag

        if flag == "new":
            page1.sizer.Add(wx.StaticText(page1, -1, """This wizard will lead you to set up a configuration for importing data to Salesforce.com."""))
            self.FitToPage(page1)
        elif flag == "exists":
            btn_selectExists = wx.Button(page1, -1, "Browse...", size=(80,23), pos=(515,90))
            page1.Bind(wx.EVT_BUTTON, self.OnSelectExists, btn_selectExists)
            st = StaticText(page1, -1, "Choose JSON file", size=(100, 20), pos=(10,60))
            self.tc_exists = wx.TextCtrl(page1, -1, "", size=(500, -1), pos=(10,90))

        btn_browse = wx.Button(page2, -1, "Browse...", size=(80,23), pos=(515,90))
        page2.Bind(wx.EVT_BUTTON, self.OnBrowseButton, btn_browse)

        st = StaticText(page2, -1, "Choose CSV file", size=(100, 20), pos=(10,60))

        self.t1_source = wx.TextCtrl(page2, -1, "", size=(500, -1), pos=(10,90))

        # below is the information for page3
        st3_cn = StaticText(page3, -1, "ConfigName:", size=(80,20), pos=(10,60))
        self.tc3_cn = wx.TextCtrl(page3, -1, "", size=(200,-1), pos=(90,57))

        st3_lt = StaticText(page3, -1, "LoadType:", size=(80,20), pos=(10,90))
        #self.tc3_lt = wx.TextCtrl(page3, -1, "", size=(200,-1), pos=(90,87))
        self.choice3_lt = wx.Choice(page3, -1, size=(200,-1), pos=(90,87), choices = iLoadTools.LoadTypeList)
        page3.Bind(wx.EVT_CHOICE, self.OnLoadTypeSelected, self.choice3_lt)

        st3_url = StaticText(page3, -1, "URL:", size=(80,20), pos=(10,120))
        self.choice3_url = wx.Choice(page3, -1, size=(200,-1), pos=(90,117), choices = [])

        st3_un = StaticText(page3, -1, "UserName:", size=(80,20), pos=(10,150))
        self.tc3_un = wx.TextCtrl(page3, -1, "", size=(200,-1), pos=(90,147))

        st3_pwd = StaticText(page3, -1, "Password:", size=(80,20), pos=(10,180))
        self.tc3_pwd = wx.TextCtrl(page3, -1, "", size=(200,-1), pos=(90,177), style=wx.TE_PASSWORD)

        st3_tt = StaticText(page3, -1, "TargetTable:", size=(80,20), pos=(10,210))
        self.tc3_tt = wx.TextCtrl(page3, -1, "", size=(200,-1), pos=(90,207))
        # above is the information for page3

        # below is the information for page4
        b_p4_newMap = wx.Button(page4, -1, "New Mapping", size=(100,23), pos=(10,60))
        page4.Bind(wx.EVT_BUTTON, self.OnButtonNewMap, b_p4_newMap)

        tIDmap = wx.NewId()
        self.listmap = simpleListCtrl.SimpleListCtrl(page4, tIDmap,
                                                     style=wx.LC_REPORT
                                                     | wx.BORDER_NONE
                                                     | wx.LC_EDIT_LABELS,
                                                     size=(580,280),
                                                     pos=(10,90)
                                                     )
        self.PopulateHeaderListMap()
        self.listmap.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClickMap)

        line4page4_1 = wx.StaticLine(page4, -1, size=(670,-1), pos=(10,390), style=wx.LI_HORIZONTAL)

        b_p4_newRule = wx.Button(page4, -1, "New Rule", size=(100,23), pos=(10,405))
        page4.Bind(wx.EVT_BUTTON, self.OnButtonNewRule, b_p4_newRule)

        tIDrule = wx.NewId()
        self.listrule = simpleListCtrl.SimpleListCtrl(page4, tIDrule,
                                                      style=wx.LC_REPORT
                                                      | wx.BORDER_NONE
                                                      | wx.LC_EDIT_LABELS,
                                                      size=(580,280),
                                                      pos=(10,435)
                                                      )
        self.PopulateHeaderListRule()
        self.listrule.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClickRule)

        line4page4_2 = wx.StaticLine(page4, -1, size=(670,-1), pos=(10,730), style=wx.LI_HORIZONTAL)
        btn_p4_execute = wx.Button(page4, -1, "Execute", size=(150,40), pos=(10,750))
        btn_p4_execute.SetToolTipString("You can click this button to execute import.")
        page4.Bind(wx.EVT_BUTTON, self.OnClickExecute, btn_p4_execute)
        btn_p4_execute.SetBitmap(myimages.Mondrian.Bitmap, wx.LEFT)
        btn_p4_execute.SetBitmapMargins((2,2))

        btn_p4_schedule = wx.Button(page4, -1, "Schedule", size=(150,40), pos=(180,750))
        btn_p4_schedule.SetToolTipString("You can click this button to set schedule execute import.")
        page4.Bind(wx.EVT_BUTTON, self.OnClickSchedule, btn_p4_schedule)
        btn_p4_schedule.SetBitmap(myimages.Mondrian.Bitmap, wx.LEFT)
        btn_p4_schedule.SetBitmapMargins((2,2))
        # above is the information for page4

        # Use the convenience Chain function to connect the pages
        wiz.WizardPageSimple.Chain(page1, page2)
        wiz.WizardPageSimple.Chain(page2, page3)
        wiz.WizardPageSimple.Chain(page3, page4)
        #wiz.WizardPageSimple.Chain(page4, page5)
        self.GetPageAreaSizer().Add(page1)

        self.Bind(wiz.EVT_WIZARD_PAGE_CHANGED, self.OnWizPageChanged)
        self.Bind(wiz.EVT_WIZARD_PAGE_CHANGING, self.OnWizPageChanging)
        self.Bind(wiz.EVT_WIZARD_CANCEL, self.OnWizCancel)
        self.Bind(wiz.EVT_WIZARD_FINISHED, self.OnWizFinish)

        if self.RunWizard(page1):
            wx.MessageBox("Save configuration successfully")
        else:
            wx.MessageBox("You cancelled this wizard")

    def OnBrowseButton(self, evt):
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard=wildcard_source,
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            li = []
            for path in paths:
                li.append(path)
            if len(li) > 0:
                self.t1_source.Label = li[0]
                pass
        dlg.Destroy()

    def OnSelectExists(self, evt):
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=mainFrame.workspace,
            defaultFile="",
            wildcard=wildcard_exists,
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            li = []
            for path in paths:
                li.append(path)
            if len(li) > 0:
                self.tc_exists.Label = li[0]
                pass
        dlg.Destroy()

    def OnButtonNewMap(self, evt):
        ref_choices = ['', ]
        ruleCount = 0
        ruleCount = self.listrule.GetItemCount()
        if ruleCount > 0:
            for i in range(ruleCount):
                ref_choices.append(self.listrule.GetItemText(i,0))

        dlg = newMapDialog.NewMapDialog(self, -1, "New Mapping", ref_choices, size=(350, 200), style=wx.DEFAULT_DIALOG_STYLE, )
        dlg.CenterOnScreen()

        val = dlg.ShowModal()
        if val == wx.ID_SAVE:
            print("You pressed Save\n")
            newMapLi = []
            newMapLi.append(dlg.newMapping["TargetField"])
            newMapLi.append(dlg.newMapping["SourceField"])
            newMapLi.append(dlg.newMapping["FieldType"])
            newMapLi.append(dlg.newMapping["FieldLength"])
            newMapLi.append(dlg.newMapping["Rule"])
            newMapLi.append(dlg.newMapping["Reference"])
            newMapLi.append(dlg.newMapping["IsKey"])
            newMapLi.append(dlg.newMapping["IsVariable"])
            self.listmap.Append(newMapLi)

        else:
            pass

        dlg.Destroy()

    def OnButtonNewRule(self, evt):
        dlg = newRuleDialog.NewRuleDialog(self, -1, "New Rule", size=(350, 200), style=wx.DEFAULT_DIALOG_STYLE, )
        dlg.CenterOnScreen()
        val = dlg.ShowModal()

        if val == wx.ID_SAVE:
            print("You pressed Save\n")
            newRuleLi = []
            newRuleLi.append(dlg.newRule["RuleName"])
            newRuleLi.append(dlg.newRule["RuleType"])
            newRuleLi.append(dlg.newRule["LookField"])
            newRuleLi.append(dlg.newRule["LookupObject"])
            newRuleLi.append(dlg.newRule["OutField"])
            newRuleLi.append(dlg.newRule["Where"])
            newRuleLi.append(dlg.newRule["Condition"])
            self.listrule.Append(newRuleLi)

        else:
            pass

        dlg.Destroy()

    def OnWizPageChanged(self, evt):
        if evt.GetDirection():
            dir = "forward"
        else:
            dir = "backward"

        page = evt.GetPage()

    def OnWizPageChanging(self, evt):
        if evt.GetDirection():
            dir = "forward"
        else:
            dir = "backward"

        page = evt.GetPage()
        if self.flag == "new":
            if page.pageTitle == "Page 2" and dir == "forward" and (self.t1_source.Label == "" or not self.existsFile(self.t1_source.Label)):
                wx.MessageBox("You should select an exists source file.", "source file")
                evt.Veto()
            elif page.pageTitle == "Page 3" and dir == "forward":
                if self.tc3_cn.GetValue() == "":
                    wx.MessageBox("You should provide config name.", "config name")
                    evt.Veto()
                elif self.choice3_lt.GetString(self.choice3_lt.GetSelection()) == "":
                    wx.MessageBox("You should provide load type.", "load type")
                    evt.Veto()
                elif self.choice3_url.GetString(self.choice3_url.GetSelection()) == "":
                    wx.MessageBox("You should provide URL.", "URL")
                    evt.Veto()
                elif self.tc3_un.GetValue() == "":
                    wx.MessageBox("You should provide user name.", "user name")
                    evt.Veto()
                elif self.tc3_pwd.GetValue() == "":
                    wx.MessageBox("You should provide password.", "password")
                    evt.Veto()
                elif self.tc3_tt.GetValue() == "":
                    wx.MessageBox("You should provide target table.", "target table")
                    evt.Veto()
                elif self.existsConfig(self.tc3_cn.GetValue()):
                    msg = "%s already exists.\nDo you want to replace it?" % (self.tc3_cn.GetValue(), )
                    dlg = wx.MessageDialog(self.page3, msg, "confirm msg box", wx.YES_NO)
                    bno = dlg.ShowModal()
                    if bno == 5104:
                        evt.Veto()
                    dlg.Destroy()

        elif self.flag == "exists":
            if page.pageTitle == "Page 1" and dir == "forward" and self.tc_exists.Label == "":
                wx.MessageBox("You should select a json file.", "json file")
                evt.Veto()
            elif page.pageTitle == "Page 1" and dir == "forward":
                if not self.ValidateJSONFile(self.tc_exists.Label):
                    wx.MessageBox("You should select a valid JSON file.", "valid JSON file")
                    evt.Veto()
                else:
                    existsJSON = iLoadTools.GetConfiguration(self.tc_exists.Label)
                    data = existsJSON.getData()
                    self.t1_source.Label = data["src_full_path"]
                    self.tc3_cn.SetValue(data["cname"])
                    self.choice3_lt.SetSelection(iLoadTools.getLoadTypeIndex(data["load_type"]))
                    iLoadTools.setURLChoice(self.choice3_url, data["load_type"], data["URL"])
                    self.tc3_un.SetValue(data["username"])
                    self.tc3_pwd.SetValue(data["pwd"])
                    self.tc3_tt.SetValue(data["target_table"])
                    #print(data)
                    if len(data["mapping"]) > 0:
                        self.PopulateItemListMap(data["mapping"])
                    if len(data["rule_reference"]) > 0:
                        self.PopulateItemListRule(data["rule_reference"])

            if page.pageTitle == "Page 2" and dir == "forward" and (self.t1_source.Label == "" or not self.existsFile(self.t1_source.Label)):
                wx.MessageBox("You should select an exists source file.", "source file")
                evt.Veto()
            elif page.pageTitle == "Page 3" and dir == "forward":
                if self.tc3_cn.GetValue() == "":
                    wx.MessageBox("You should provide config name.", "config name")
                    evt.Veto()
                elif self.choice3_lt.GetString(self.choice3_lt.GetSelection()) == "":
                    wx.MessageBox("You should provide load type.", "load type")
                    evt.Veto()
                elif self.choice3_url.GetString(self.choice3_url.GetSelection()) == "":
                    wx.MessageBox("You should provide URL.", "URL")
                    evt.Veto()
                elif self.tc3_un.GetValue() == "":
                    wx.MessageBox("You should provide user name.", "user name")
                    evt.Veto()
                elif self.tc3_pwd.GetValue() == "":
                    wx.MessageBox("You should provide password.", "password")
                    evt.Veto()
                elif self.tc3_tt.GetValue() == "":
                    wx.MessageBox("You should provide target table.", "target table")
                    evt.Veto()
                elif self.existsConfig(self.tc3_cn.GetValue()):
                    msg = "%s already exists.\nDo you want to replace it?" % (self.tc3_cn.GetValue(), )
                    dlg = wx.MessageDialog(self.page3, msg, "confirm msg box", wx.YES_NO)
                    bno = dlg.ShowModal()
                    if bno == 5104:
                        evt.Veto()
                    dlg.Destroy()

    def OnWizCancel(self, evt):
        page = evt.GetPage()

    def makeConfigFolder(self, configNM):
        li = os.listdir(mainFrame.workspace)
        if li.count(configNM) > 0:
            pass
        else:
            os.chdir(mainFrame.workspace)
            os.mkdir(configNM)

    def makeConfigDict(self):
        dt = {}
        dt["identifier"] = "iLoadConfiguration"
        dt["mapping"] = []
        dt["rule_reference"] = []
        dt["cname"] = self.tc3_cn.GetValue()
        dt["load_type"] = self.choice3_lt.GetString(self.choice3_lt.GetSelection())
        dt["URL"] = self.choice3_url.GetString(self.choice3_url.GetSelection())
        dt["username"] = self.tc3_un.GetValue()
        dt["pwd"] = self.tc3_pwd.GetValue()
        dt["target_table"] = self.tc3_tt.GetValue()
        dt["source_file"] = os.path.basename(self.t1_source.Label)
        dt["src_full_path"] = self.t1_source.Label

        if self.listmap.GetItemCount() > 0:
            for i in range(self.listmap.GetItemCount()):
                dt["mapping"].append({
                    "target_field" : self.listmap.GetItemText(i, 0),
                    "source_field" : self.listmap.GetItemText(i, 1),
                    "field_type" : self.listmap.GetItemText(i, 2),
                    "field_length" : self.listmap.GetItemText(i, 3),
                    "rule" : self.listmap.GetItemText(i, 4),
                    "reference" : self.listmap.GetItemText(i, 5),
                    "iskey" : self.listmap.GetItemText(i, 6),
                    "isvariable" : self.listmap.GetItemText(i, 7),
                    "index" : i,
                })
        if self.listrule.GetItemCount() > 0:
            for j in range(self.listrule.GetItemCount()):
                dt["rule_reference"].append({
                    "rule_name" : self.listrule.GetItemText(j, 0),
                    "rule_type" : self.listrule.GetItemText(j, 1),
                    "look_field" : self.listrule.GetItemText(j, 2),
                    "lookup_object" : self.listrule.GetItemText(j, 3),
                    "out_field" : self.listrule.GetItemText(j, 4),
                    "where_c" : self.listrule.GetItemText(j, 5),
                    "condition" : self.listrule.GetItemText(j, 6),
                    "index" : j,
                })

        return dt

    def ConfigSave(self, evt):
        reflag = False
        configName = self.tc3_cn.GetValue()
        self.makeConfigFolder(configName)
        configFile = mainFrame.workspace + "\\" + configName + "\\" + configName + ".json"
        data = self.makeConfigDict()

        with open(configFile, "wb") as fs:
            fs.write(json.dumps(data))
        try:
            # delete file first
            shutil.copyfile(self.t1_source.Label, mainFrame.workspace + "\\" + configName + "\\" + os.path.basename(self.t1_source.Label))
        except shutil.Error:
            print(shutil.Error)

        self.dbfile = dbfile = mainFrame.workspace + "\\" + configName + "\\" + configName + ".zdb"

        try:
            if type(self.logText) != wx.TextCtrl:
                self.logText = VirtualLog()
        except Exception as e:
            print(e.args[0])
            self.logText = VirtualLog()


        connectDB.CreateDB(dbfile, self.logText)
        link = connectDB.ConnectDB(dbfile, self.logText)
        conn = link.get_conn()

        # load configuration file to database
        config = loadingConfigFile.ConfigFile(configName, configFile, conn, self.logText)
        config.loading()
        # load source csv file to database
        srcfile = loadingSourceFile.SourceFile(configName, conn, self.logText)
        srcfile.loading()

        link.close_conn()
        os.chdir(mainFrame.homepath)
        reflag = True
        return reflag

    def ValidateData(self, flag):
        reflag = False
        link = connectDB.ConnectDB(self.dbfile, self.logText)
        conn = link.get_conn()
        if flag == "beforeLoadingLookupTab":
            vl = validate.Validation(conn, self.logText)
            if vl.validResult1():
                self.logText.AppendText("agree to continue execute importing steps\n")
                reflag = True
            else:
                self.logText.AppendText("cannot continue\n")
                reflag = False
        if flag == "beforeCreateView":
            pass
        link.close_conn()
        return reflag


    def OnWizFinish(self, evt):
        self.ConfigSave(evt)

    def OnPopupMapDel(self, evt):
        index = self.listmap.GetFirstSelected()
        self.listmap.DeleteItem(index)

    def OnPopupRuleDel(self, evt):
        index = self.listrule.GetFirstSelected()
        self.listrule.DeleteItem(index)

    def OnRightClickMap(self, evt):
        if not hasattr(self, "popupMapDelID"):
            self.popupMapDelID = wx.NewId()
            self.Bind(wx.EVT_MENU, self.OnPopupMapDel, id=self.popupMapDelID)
        menu = wx.Menu()
        menu.Append(self.popupMapDelID, "DeleteThis")
        self.PopupMenu(menu)
        menu.Destroy()

    def OnRightClickRule(self, evt):
        if not hasattr(self, "popupRuleDelID"):
            self.popupRuleDelID = wx.NewId()
            self.Bind(wx.EVT_MENU, self.OnPopupRuleDel, id=self.popupRuleDelID)
        menu = wx.Menu()
        menu.Append(self.popupRuleDelID, "DeleteThis")
        self.PopupMenu(menu)
        menu.Destroy()

    def OnLodDialogInit(self, evt):
        self.ConfigSave(evt)

    def OnExecuteNow(self, evt):
        self.logText.AppendText("executing now\n")
        if self.ValidateData("beforeLoadingLookupTab"):
            self.logText.AppendText("load lookup table to database starting\n")
            link = connectDB.ConnectDB(self.dbfile, self.logText)
            conn = link.get_conn()
            lookTab = loadingLookupTable.LookupTable(conn, self.logText)
            lookTab.loading()
            link.close_conn()
            self.logText.AppendText("load lookup table to database end\n")
            if self.ValidateData("beforeCreateView"):
                self.logText.AppendText("execute importing data\n")
            else:
                pass
        else:
            pass

    def OnLoadTypeSelected(self, evt):
        self.choice3_url.Clear()
        for item in iLoadTools.URLDict[evt.GetString()]:
            self.choice3_url.Append(item)

    def OnClickCloseAll(self, evt):
        self.logDlg.EndModal(-1)

    def OnClickExecute(self, evt):
        self.logDlg = wx.Dialog(self, -1, "Log Information", style=wx.DEFAULT_DIALOG_STYLE)
        #self.logDlg.CenterOnScreen()
        sizerV = wx.BoxSizer(wx.VERTICAL)
        self.logText = wx.TextCtrl(self.logDlg, -1, "", size=(500, 360), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER|wx.TE_READONLY )
        sizerV.Add(self.logText)
        sizerH = wx.BoxSizer(wx.HORIZONTAL)
        btn_execute = wx.Button(self.logDlg, -1, "Execute Now")
        self.logDlg.Bind(wx.EVT_BUTTON, self.OnExecuteNow, btn_execute)
        btn_clearLog = wx.Button(self.logDlg, -1, "Clear All")
        self.logDlg.Bind(wx.EVT_BUTTON, self.OnClickClearAll, btn_clearLog)
        btn_closeLog = wx.Button(self.logDlg, -1, "Close")
        self.logDlg.Bind(wx.EVT_BUTTON, self.OnClickCloseAll, btn_closeLog)
        sizerH.Add(btn_execute)
        sizerH.Add(btn_clearLog)
        sizerH.Add(btn_closeLog)
        sizerV.Add(sizerH)
        self.logDlg.SetSizer(sizerV)
        sizerV.Fit(self.logDlg)
        self.logDlg.Bind(wx.EVT_INIT_DIALOG, self.OnLodDialogInit)
        logDlgCode = self.logDlg.ShowModal()
        self.logDlg.Destroy()

    def OnClickClearAll(self, evt):
        self.logText.Clear()

    def OnClickSchedule(self, evt):
        self.scheDlg = wx.Dialog(self, -1, "Setup schedule", style=wx.DEFAULT_DIALOG_STYLE, size=(500,500))
        #sizerV = wx.BoxSizer(wx.VERTICAL)

        #self.scheDlg.SetSizer(sizerV)
        #sizerV.Fit(self.scheDlg)
        scheDlgCode = self.scheDlg.ShowModal()
        self.scheDlg.Destroy()

    def PopulateHeaderListMap(self):
        self.listmap.InsertColumn(0, "TargetField")
        self.listmap.InsertColumn(1, "SourceField")
        self.listmap.InsertColumn(2, "FieldType")
        self.listmap.InsertColumn(3, "FieldLength")
        self.listmap.InsertColumn(4, "Rule")
        self.listmap.InsertColumn(5, "Reference")
        self.listmap.InsertColumn(6, "IsKey")
        self.listmap.InsertColumn(7, "IsVariable")

    def PopulateItemListMap(self, list):
        self.listmap.DeleteAllItems()
        for i in range(len(list)):
            for j in list:
                if j["index"] == i:
                    newMapLi = []
                    newMapLi.append(j["target_field"])
                    newMapLi.append(j["source_field"])
                    newMapLi.append(j["field_type"])
                    newMapLi.append(j["field_length"])
                    newMapLi.append(j["rule"])
                    newMapLi.append(j["reference"])
                    newMapLi.append(j["iskey"])
                    newMapLi.append(j["isvariable"])
                    self.listmap.Append(newMapLi)

    def PopulateHeaderListRule(self):
        self.listrule.InsertColumn(0, "RuleName")
        self.listrule.InsertColumn(1, "RuleType", wx.LIST_FORMAT_RIGHT)
        self.listrule.InsertColumn(2, "LookField")
        self.listrule.InsertColumn(3, "LookupObject")
        self.listrule.InsertColumn(4, "OutField")
        self.listrule.InsertColumn(5, "Where")
        self.listrule.InsertColumn(6, "Condition")

    def PopulateItemListRule(self, list):
        self.listrule.DeleteAllItems()
        for i in range(len(list)):
            for j in list:
                if j["index"] == i:
                    newRuleLi = []
                    newRuleLi.append(j["rule_name"])
                    newRuleLi.append(j["rule_type"])
                    newRuleLi.append(j["look_field"])
                    newRuleLi.append(j["lookup_object"])
                    newRuleLi.append(j["out_field"])
                    newRuleLi.append(j["where_c"])
                    newRuleLi.append(j["condition"])
                    self.listrule.Append(newRuleLi)

    def existsConfig(self, folderName):
        rebool = False
        li = os.listdir(mainFrame.workspace)
        if li.count(folderName) > 0:
            rebool = True
        return rebool

    def ValidateJSONFile(self, file):
        valid = False
        gc = iLoadTools.GetConfiguration(file)
        data = gc.getData()
        try:
           if data["identifier"] == "iLoadConfiguration":
               valid = True
        except KeyError:
            print("not a valid JSON file")

        return valid

    def existsFile(self, path):
        return os.path.exists(path)


class VirtualLog:
    def __init__(self):
        pass
    def AppendText(self, str):
        print(str)
