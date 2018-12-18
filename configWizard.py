#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx, pdb, sys, os, json, shutil, sqlite3, time
import iLoad, titledPage, simpleListCtrl
import newRuleDialog, newMapDialog, createView, previewDataGrid
import loadingConfigFile, loadingSourceFile, loadingLookupTable
import wx.wizard as wiz
import wx.lib.masked as masked
from wx import StaticText
from wx.lib.pubsub import pub
from threading import Thread
from utils import connectDB, iLoadTools, myimages, validate
import wx.lib.rcsizer as rcs

wildcard_source = "CSV files (*.csv)|*.csv"
wildcard_exists = "JSON files (*.json)|*.json"

class ConfigWizard(wiz.Wizard):
    def __init__(self, parent, flag):
        wiz.Wizard.__init__(self, 
                            parent, 
                            -1, 
                            "Configuration Wizard", 
                            myimages.PyDLWiz.GetBitmap())
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
        self.runStep = "step1_start"

        if flag == "new":
            page1.sizer.Add(wx.StaticText(page1, -1, 
            "This wizard will lead you to set up a configuration for importing data to target."))
            self.FitToPage(page1)
        elif flag == "exists":
            btn_selectExists = wx.Button(page1, -1, "Browse...", size=(80,23), pos=(515,90))
            page1.Bind(wx.EVT_BUTTON, self.OnSelectExists, btn_selectExists)
            st = StaticText(page1, -1, "Choose template", size=(100, 20), pos=(10,60))
            self.tc_exists = wx.TextCtrl(page1, -1, "", size=(500, -1), pos=(10,90))

        btn_browse = wx.Button(page2, -1, "Browse...", size=(80,23), pos=(515,90))
        page2.Bind(wx.EVT_BUTTON, self.OnBrowseButton, btn_browse)

        st = StaticText(page2, -1, "Choose source file(csv)", size=(200, 20), pos=(10,60))

        self.t1_source = wx.TextCtrl(page2, -1, "", size=(500, -1), pos=(10,90))

        # below is the information for page3
        st3_cn = StaticText(page3, -1, "TemplateName:", size=(120,20), pos=(10,60))
        st3_cn.SetForegroundColour((255,0,0))
        self.tc3_cn = wx.TextCtrl(page3, -1, "", size=(200,-1), pos=(130,57))

        st3_lt = StaticText(page3, -1, "LoadType:", size=(120,20), pos=(10,90))
        st3_lt.SetForegroundColour((255,0,0))
        self.choice3_lt = wx.Choice(page3, -1, size=(200,-1), pos=(130,87), 
                                    choices = iLoadTools.LoadTypeList)
        page3.Bind(wx.EVT_CHOICE, self.OnLoadTypeSelected, self.choice3_lt)

        st3_url = StaticText(page3, -1, "URL:", size=(120,20), pos=(10,120))
        st3_url.SetForegroundColour((255,0,0))
        self.choice3_url = wx.Choice(page3, -1, size=(200,-1), pos=(130,117), 
                                     choices = [])

        st3_un = StaticText(page3, -1, "UserName:", size=(120,20), pos=(10,150))
        st3_un.SetForegroundColour((255,0,0))
        self.tc3_un = wx.TextCtrl(page3, -1, "", size=(200,-1), pos=(130,147))

        st3_pwd = StaticText(page3, -1, "Password:", size=(120,20), pos=(10,180))
        st3_pwd.SetForegroundColour((255,0,0))
        self.tc3_pwd = wx.TextCtrl(page3, -1, "", size=(200,-1), pos=(130,177), 
                                   style=wx.TE_PASSWORD)

        st3_tt = StaticText(page3, -1, "TargetTable:", size=(120,20), pos=(10,210))
        st3_tt.SetForegroundColour((255,0,0))
        self.tc3_tt = wx.TextCtrl(page3, -1, "", size=(200,-1), pos=(130,207))
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

        line4page4_1 = wx.StaticLine(page4, -1, size=(670,-1), pos=(10,390), 
                                     style=wx.LI_HORIZONTAL)

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

        line4page4_2 = wx.StaticLine(page4, -1, size=(670,-1), pos=(10,730), 
                                     style=wx.LI_HORIZONTAL)
        btn_p4_execute = wx.Button(page4, -1, "Execute", size=(150,40), pos=(10,750))
        btn_p4_execute.SetToolTipString("You can click this button to execute import.")
        page4.Bind(wx.EVT_BUTTON, self.OnClickExecute, btn_p4_execute)
        btn_p4_execute.SetBitmap(myimages.Mondrian.Bitmap, wx.LEFT)
        btn_p4_execute.SetBitmapMargins((2,2))

        btn_p4_validate = wx.Button(page4, -1, "Validate", size=(150,40), pos=(170,750))
        btn_p4_validate.SetToolTipString("You can click this button to validate mapping and rule.")
        page4.Bind(wx.EVT_BUTTON, self.OnClickValidate, btn_p4_validate)
        btn_p4_validate.SetBitmap(myimages.Mondrian.Bitmap, wx.LEFT)
        btn_p4_validate.SetBitmapMargins((2,2))
        
        # Use the convenience Chain function to connect the pages
        wiz.WizardPageSimple.Chain(page1, page2)
        wiz.WizardPageSimple.Chain(page2, page3)
        wiz.WizardPageSimple.Chain(page3, page4)
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
            defaultDir=iLoad.workspace,
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

        dlg = newMapDialog.NewMapDialog(self, -1, "New Mapping", 
              ref_choices, size=(350, 200), style=wx.DEFAULT_DIALOG_STYLE, )
        dlg.CenterOnScreen()

        val = dlg.ShowModal()
        if val == wx.ID_SAVE:
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
        dlg = newRuleDialog.NewRuleDialog(self, -1, "New Rule", 
              size=(350, 200), style=wx.DEFAULT_DIALOG_STYLE, )
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
            if page.pageTitle == "Page 2" and dir == "forward" and \
               (self.t1_source.Label == "" or not self.existsFile(self.t1_source.Label)):
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
                    msg = "%s already exists.\nDo you want to replace it?" % \
                          (self.tc3_cn.GetValue(), )
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
                    if len(data["mapping"]) > 0:
                        self.PopulateItemListMap(data["mapping"])
                    if len(data["rule_reference"]) > 0:
                        self.PopulateItemListRule(data["rule_reference"])

            if page.pageTitle == "Page 2" and dir == "forward" and \
               (self.t1_source.Label == "" or not self.existsFile(self.t1_source.Label)):
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
                    msg = "%s already exists.\nDo you want to replace it?" % \
                          (self.tc3_cn.GetValue(), )
                    dlg = wx.MessageDialog(self.page3, msg, "confirm msg box", wx.YES_NO)
                    bno = dlg.ShowModal()
                    if bno == 5104:
                        evt.Veto()
                    dlg.Destroy()

    def OnWizCancel(self, evt):
        page = evt.GetPage()

    def makeConfigFolder(self, configNM):
        li = os.listdir(iLoad.workspace)
        if li.count(configNM) > 0:
            pass
        else:
            os.chdir(iLoad.workspace)
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
        self.cn = configName = self.tc3_cn.GetValue()
        self.makeConfigFolder(configName)
        configFile = iLoad.workspace + "\\" + configName + "\\" + configName + ".json"
        data = self.makeConfigDict()

        with open(configFile, "wb") as fs:
            fs.write(json.dumps(data))
        try:
            # delete file first
            shutil.copyfile(self.t1_source.Label, iLoad.workspace + "\\" + configName 
                            + "\\" + os.path.basename(self.t1_source.Label))
        except shutil.Error:
            print(shutil.Error)

        self.dbfile = dbfile = iLoad.workspace + "\\" + configName + "\\" + configName + ".zdb"

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
        os.chdir(iLoad.homepath)
        reflag = True
        return reflag

    def ValidateData(self, flag):
        reflag = False
        link = connectDB.ConnectDB(self.dbfile, self.logText)
        conn = link.get_conn()
        if flag == "beforeLoadingLookupTab":
            vl = validate.Validation(conn, self.logText)
            if vl.validResult1():
                self.logText.AppendText("Agree to continue execute importing steps\n")
                reflag = True
            else:
                self.logText.AppendText("Cannot continue\n")
                reflag = False
        if flag == "beforeCreateView":
            reflag = True
        link.close_conn()
        return reflag

    def OnWizFinish(self, evt):
        self.ConfigSave(evt)

    def OnPopupMapDel(self, evt):
        index = self.listmap.GetFirstSelected()
        self.listmap.DeleteItem(index)
        
    def OnPopupMapEdit(self, evt):
        index = self.listmap.GetFirstSelected()
        data = {"flag" : "edit"}
        data["target_field"] = self.listmap.GetItemText(index, 0)
        data["source_field"] = self.listmap.GetItemText(index, 1)
        data["field_type"] = self.listmap.GetItemText(index, 2)
        data["field_length"] = self.listmap.GetItemText(index, 3)
        data["rule"] = self.listmap.GetItemText(index, 4)
        data["reference"] = self.listmap.GetItemText(index, 5)
        data["iskey"] = self.listmap.GetItemText(index, 6)
        data["isvariable"] = self.listmap.GetItemText(index, 7)
        
        ref_choices = ['', ]
        ruleCount = 0
        ruleCount = self.listrule.GetItemCount()
        if ruleCount > 0:
            for i in range(ruleCount):
                ref_choices.append(self.listrule.GetItemText(i,0))
        
        dlg = newMapDialog.NewMapDialog(self, -1, "Edit Mapping", 
              ref_choices, size=(350, 200), style=wx.DEFAULT_DIALOG_STYLE, data=data)
        dlg.CenterOnScreen()
        val = dlg.ShowModal()
        
        if val == wx.ID_SAVE:
            self.listmap.SetStringItem(index, 0, dlg.newMapping["TargetField"])
            self.listmap.SetStringItem(index, 1, dlg.newMapping["SourceField"])
            self.listmap.SetStringItem(index, 2, dlg.newMapping["FieldType"])
            self.listmap.SetStringItem(index, 3, dlg.newMapping["FieldLength"])
            self.listmap.SetStringItem(index, 4, dlg.newMapping["Rule"])
            self.listmap.SetStringItem(index, 5, dlg.newMapping["Reference"])
            self.listmap.SetStringItem(index, 6, str(dlg.newMapping["IsKey"]))
            self.listmap.SetStringItem(index, 7, str(dlg.newMapping["IsVariable"]))
        else:
            pass

        dlg.Destroy()

    def OnPopupRuleDel(self, evt):
        index = self.listrule.GetFirstSelected()
        self.listrule.DeleteItem(index)
        
    def OnPopupRuleEdit(self, evt):
        index = self.listrule.GetFirstSelected()
        data = {"flag" : "edit"}
        data["rule_name"] = self.listrule.GetItemText(index, 0)
        data["rule_type"] = self.listrule.GetItemText(index, 1)
        data["look_field"] = self.listrule.GetItemText(index, 2)
        data["lookup_object"] = self.listrule.GetItemText(index, 3)
        data["out_field"] = self.listrule.GetItemText(index, 4)
        data["where_c"] = self.listrule.GetItemText(index, 5)
        data["condition"] = self.listrule.GetItemText(index, 6)
        
        dlg = newRuleDialog.NewRuleDialog(self, -1, "Edit Rule", 
              size=(350, 200), style=wx.DEFAULT_DIALOG_STYLE, data=data)
        dlg.CenterOnScreen()
        val = dlg.ShowModal()

        if val == wx.ID_SAVE:
            self.listrule.SetStringItem(index, 0, dlg.newRule["RuleName"])
            self.listrule.SetStringItem(index, 1, dlg.newRule["RuleType"])
            self.listrule.SetStringItem(index, 2, dlg.newRule["LookField"])
            self.listrule.SetStringItem(index, 3, dlg.newRule["LookupObject"])
            self.listrule.SetStringItem(index, 4, dlg.newRule["OutField"])
            self.listrule.SetStringItem(index, 5, dlg.newRule["Where"])
            self.listrule.SetStringItem(index, 6, dlg.newRule["Condition"])
        else:
            pass

        dlg.Destroy()

    def OnRightClickMap(self, evt):
        if not hasattr(self, "popupMapDelID"):
            self.popupMapDelID = wx.NewId()
            self.Bind(wx.EVT_MENU, self.OnPopupMapDel, id=self.popupMapDelID)
        if not hasattr(self, "popupMapEditID"):
            self.popupMapEditID = wx.NewId()
            self.Bind(wx.EVT_MENU, self.OnPopupMapEdit, id=self.popupMapEditID)
        menu = wx.Menu()
        menu.Append(self.popupMapEditID, "EditThis")
        menu.Append(self.popupMapDelID, "DeleteThis")
        self.PopupMenu(menu)
        menu.Destroy()

    def OnRightClickRule(self, evt):
        if not hasattr(self, "popupRuleDelID"):
            self.popupRuleDelID = wx.NewId()
            self.Bind(wx.EVT_MENU, self.OnPopupRuleDel, id=self.popupRuleDelID)
        if not hasattr(self, "popupRuleEditID"):
            self.popupRuleEditID = wx.NewId()
            self.Bind(wx.EVT_MENU, self.OnPopupRuleEdit, id=self.popupRuleEditID)
        menu = wx.Menu()
        menu.Append(self.popupRuleEditID, "EditThis")
        menu.Append(self.popupRuleDelID, "DeleteThis")
        self.PopupMenu(menu)
        menu.Destroy()

    def OnLoadDialogInit(self, evt):
        self.ConfigSave(evt)

    def OnLoadTypeSelected(self, evt):
        self.choice3_url.Clear()
        for item in iLoadTools.URLDict[evt.GetString()]:
            self.choice3_url.Append(item)
    
    def OnCopyAllLog(self, evt):
        self.logText.SelectAll()
        self.logText.Copy()
        
    def OnClearAllLog(self, evt):
        self.logText.Clear()
        
    def OnCloseLog(self, evt):
        self.logDlg.EndModal(-1)

    def OnPreviewData(self, evt):
        link = connectDB.ConnectDB(self.dbfile, self.logText)
        conn = link.get_conn()
        dbt = iLoadTools.DatabaseTool(conn)
        configName = dbt.getConfigName()
        tarList = dbt.getTarFieldList()
        tarTable = dbt.getTargetTable()
        vl = validate.Validation(conn, self.logText)
        if vl.validFinalTable():
            data = dbt.getPreviewData(tarList, configName+"_tar_vw2_tab")
            rowcount = dbt.getRowCount(configName+"_tar_vw2_tab")
            self.previewDlg = wx.Dialog(self, -1, "Preview Data", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
            self.datagrid = previewDataGrid.PreviewDataGrid(self.previewDlg, data, tarList, rowcount)
            previewDlgCode = self.previewDlg.ShowModal()
            self.previewDlg.Destroy()

    def OnGenerateData(self, evt):
        self.logText.AppendText("Execute generate data now\n")
        if self.ValidateData("beforeLoadingLookupTab"):
            self.logText.AppendText("Load lookup table to database starting\n")
            LoadLookupThread(self.dbfile, self.logText)
            pub.subscribe(self.updateLookupDisplay, "loadLookup")
            evt.GetEventObject().Disable()
            self.btn_generatedata.SetLabel("Running...")
            self.btn_previewdata.Disable()
            self.btn_loaddatanow.Disable()
            self.btn_loaddataschedule.Disable()
            self.btn_clearLog.Disable()
            self.btn_copyLog.Disable()
            self.btn_closeLog.Disable()
        else:
            pass
    
    def OnLoadDataNow(self, evt):
        link = connectDB.ConnectDB(self.dbfile, self.logText)
        conn = link.get_conn()
        vl = validate.Validation(conn, self.logText)
        if vl.validFinalTable():
            confirmDlg = wx.MessageDialog(self, 'Do you want to load data to target now?',
                                   'Please Confirm', wx.YES_NO | wx.ICON_INFORMATION)
            confirmDlgCode = confirmDlg.ShowModal()
            confirmDlg.Destroy()
            
            if confirmDlgCode == wx.ID_YES:
                self.logText.AppendText("Execute load data now\n")
                if self.ValidateData("beforeLoadingLookupTab"):
                    self.logText.AppendText("Load data to target starting\n")
                    LoadDataToTargetThread(self.dbfile, self.logText)
                    pub.subscribe(self.updateTargetDisplay, "loadTarget")
                    self.btn_generatedata.Disable()
                    self.btn_previewdata.Disable()
                    self.btn_loaddatanow.Disable()
                    self.btn_loaddatanow.SetLabel("Running...")
                    self.btn_loaddataschedule.Disable()
                    self.btn_clearLog.Disable()
                    self.btn_copyLog.Disable()
                    self.btn_closeLog.Disable()
                else:
                    pass
        
    def ScheduleSave(self, evt):
        setDay = str(self.dpc.GetValue().Format("%m/%d/%Y"))
        setTime = str(self.time24.GetValue())
        scheduleFile = iLoad.workspace + "\\" + self.cn + "\\" + "schedule.bat"
        with open(scheduleFile, "wb") as fo:
            fo.write("@echo off\n")
            fo.write("cd " + iLoad.homepath + "\n")
            if iLoad.env == "PROD":
                fo.write("scheduleLoad.exe " + self.cn + "\n")
            elif iLoad.env == "TEST":
                fo.write("python scheduleLoad.py " + self.cn + "\n")
        
        time.sleep(0.1)
        cmd = "schtasks /create /tn \"iLoad_%s\" /tr \"%s\" /sc ONCE /st %s /sd %s /F " \
              % (self.cn, scheduleFile, setTime, setDay, )
        self.logText.AppendText(cmd)
        self.logText.AppendText("\n")
        reCode = os.system(cmd)
        self.logText.AppendText("reCode = %d \n" % (reCode))
        if reCode == 0:
            wx.MessageBox("Save schedule successfully")
            self.scheduleDlg.EndModal(self.scheduleDlg.GetReturnCode())
        else:
            wx.MessageBox("Save schedule failed")
    
    def OnLoadDataSchedule(self, evt):
        link = connectDB.ConnectDB(self.dbfile, self.logText)
        conn = link.get_conn()
        vl = validate.Validation(conn, self.logText)
        if vl.validFinalTable():
            self.scheduleDlg = wx.Dialog(self, -1, "Schedule Setting", 
                               style=wx.DEFAULT_DIALOG_STYLE|wx.SAVE, size=(400, 150))
            textDate = wx.StaticText(self.scheduleDlg, -1, "Date:", size=(30,-1))
            self.dpc = wx.GenericDatePickerCtrl(self.scheduleDlg, #size=(120,-1),
                                           style = wx.TAB_TRAVERSAL
                                           | wx.DP_DROPDOWN
                                           | wx.DP_SHOWCENTURY
                                           | wx.DP_ALLOWNONE )
            
            textTime = wx.StaticText(self.scheduleDlg, -1, "Time:", size=(30,-1))
            spin2 = wx.SpinButton(self.scheduleDlg, -1, wx.DefaultPosition, (-1, 25), wx.SP_VERTICAL)
            self.time24 = masked.TimeCtrl(
                            self.scheduleDlg, -1, name="24 hour control", fmt24hr=True,
                            spinButton = spin2
                            )
            sizer = rcs.RowColSizer()
            box1 = wx.BoxSizer(wx.HORIZONTAL)
            box1.Add(textDate, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
            box1.Add(self.dpc, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
            sizer.Add(box1, row=1, col=1, colspan=2)
            
            box2 = wx.BoxSizer(wx.HORIZONTAL)
            box2.Add(textTime, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
            box2.Add(self.time24, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
            box2.Add(spin2, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
            sizer.Add(box2, row=1, col=4, colspan=2)
            
            btnsizer = wx.StdDialogButtonSizer()
            
            if wx.Platform != "__WXMSW__":
                btn = wx.ContextHelpButton(self)
                btnsizer.AddButton(btn)
            
            btnSave = wx.Button(self.scheduleDlg, wx.ID_SAVE)
            btnSave.SetDefault()
            self.scheduleDlg.Bind(wx.EVT_BUTTON, self.ScheduleSave, btnSave)
            btnsizer.AddButton(btnSave)
            
            btnCancel = wx.Button(self.scheduleDlg, wx.ID_CANCEL)
            btnsizer.AddButton(btnCancel)
            btnsizer.Realize()
            sizer.Add(btnsizer, row=3, col=1, colspan=5)
            self.scheduleDlg.SetSizer(sizer)
            
            scheduleDlgCode = self.scheduleDlg.ShowModal()
            self.scheduleDlg.Destroy()
    
    def OnClickExecute(self, evt):
        self.logDlg = wx.Dialog(self, -1, "Log Information", style=wx.DEFAULT_DIALOG_STYLE)
        sizerV = wx.BoxSizer(wx.VERTICAL)
        self.logText = wx.TextCtrl(self.logDlg, -1, "", size=(560, 360), 
                                   style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER|wx.TE_READONLY )
        sizerV.Add(self.logText)
        sizerH = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_generatedata = wx.Button(self.logDlg, -1, "Generate Data", size=(140,26))
        self.logDlg.Bind(wx.EVT_BUTTON, self.OnGenerateData, self.btn_generatedata)
        self.btn_previewdata = wx.Button(self.logDlg, -1, "Preview Data", size=(140,26))
        self.logDlg.Bind(wx.EVT_BUTTON, self.OnPreviewData, self.btn_previewdata)
        self.btn_loaddatanow = wx.Button(self.logDlg, -1, "Load Data Now", size=(140,26))
        self.logDlg.Bind(wx.EVT_BUTTON, self.OnLoadDataNow, self.btn_loaddatanow)
        self.btn_loaddataschedule = wx.Button(self.logDlg, -1, "Load Data Schedule", size=(140,26))
        self.logDlg.Bind(wx.EVT_BUTTON, self.OnLoadDataSchedule, self.btn_loaddataschedule)
        sizerH.Add(self.btn_generatedata)
        sizerH.Add(self.btn_previewdata)
        sizerH.Add(self.btn_loaddatanow)
        sizerH.Add(self.btn_loaddataschedule)
        sizerV.Add(sizerH)
        
        sizerH1 = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_clearLog = wx.Button(self.logDlg, -1, "Clear All", size=(140,26))
        self.logDlg.Bind(wx.EVT_BUTTON, self.OnClearAllLog, self.btn_clearLog)
        self.btn_copyLog = wx.Button(self.logDlg, -1, "Copy All", size=(140,26))
        self.logDlg.Bind(wx.EVT_BUTTON, self.OnCopyAllLog, self.btn_copyLog)
        self.btn_closeLog = wx.Button(self.logDlg, -1, "Close", size=(140,26))
        self.logDlg.Bind(wx.EVT_BUTTON, self.OnCloseLog, self.btn_closeLog)
        sizerH1.Add(self.btn_clearLog)
        sizerH1.Add(self.btn_copyLog)
        sizerH1.Add(self.btn_closeLog)
        sizerV.Add(sizerH1)
        self.logDlg.SetSizer(sizerV)
        sizerV.Fit(self.logDlg)
        self.logDlg.Bind(wx.EVT_INIT_DIALOG, self.OnLoadDialogInit)
        logDlgCode = self.logDlg.ShowModal()
        self.logDlg.Destroy()

    def OnClickValidate(self, evt):
        self.ConfigSave(evt)
        #self.listmap.SetItemBackgroundColour(0, wx.Colour(255,255,0))
        
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
        li = os.listdir(iLoad.workspace)
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
        
    def updateLookupDisplay(self, msg):
        # execute loading lookup table and update log display
        self.logText.AppendText("\n")
        self.logText.AppendText(msg)
        self.logText.AppendText("\n")
        if msg == "Load lookup table end":
            link = connectDB.ConnectDB(self.dbfile, self.logText)
            conn = link.get_conn()
            self.logText.AppendText("Load lookup table to database end\n")
            if self.ValidateData("beforeCreateView"):
                cv = createView.CreateView(conn)
                dt = cv.getViewFieldList()
                allLi1 = cv.jointFields1(dt)
                sql1 = cv.createViewSQL1(dt, allLi1)
                dbt = iLoadTools.DatabaseTool(conn)
                configName = dbt.getConfigName()
                #pdb.set_trace()
                try:
                    conn.execute("drop view %s" % (configName+"_tar_vw1", ))
                except sqlite3.OperationalError as e:
                    self.logText.AppendText(e.args[0])
                    self.logText.AppendText("\n")
                try:
                    conn.execute(sql1) # create view 1
                    self.logText.AppendText("Create view 1\n")
                except Exception as e:
                    self.logText.AppendText(str(e))
                    self.logText.AppendText("\n")
                
                allLi2 = cv.jointFields2(dt)
                sql2 = cv.createViewSQL2(dt, allLi2)
                
                try:
                    conn.execute("drop view %s" % (configName+"_tar_vw2", ))
                except sqlite3.OperationalError as e:
                    self.logText.AppendText(e.args[0])
                    self.logText.AppendText("\n")
                try:
                    conn.execute(sql2) # create view 2
                    self.logText.AppendText("Create view 2\n")
                except Exception as e:
                    self.logText.AppendText(str(e))
                    self.logText.AppendText("\n")
                conn.commit()
                try:
                    conn.execute("drop table "+configName+"_tar_vw2_tab")
                except sqlite3.OperationalError as e:
                    self.logText.AppendText(e.args[0])
                    self.logText.AppendText("\n")
                else:
                    self.logText.AppendText("Table %s droped successfully\n" % \
                    (configName+"_tar_vw2_tab", ))
                
                GenerateDataToThread(self.dbfile, self.logText)
                pub.subscribe(self.updateGenerateDisplay, "GenerateData")
            else:
                pass
            link.close_conn()
        else:
            pass
            
    def updateGenerateDisplay(self, msg):
        self.logText.AppendText("\n")
        self.logText.AppendText(msg)
        self.logText.AppendText("\n")
        if msg == "Generate data end":
            self.btn_generatedata.SetLabel("Generate Data")
            self.btn_generatedata.Enable()
            self.btn_previewdata.Enable()
            self.btn_loaddatanow.Enable()
            self.btn_loaddataschedule.Enable()
            self.btn_clearLog.Enable()
            self.btn_copyLog.Enable()
            self.btn_closeLog.Enable()
        else:
            pass
    
    def updateTargetDisplay(self, msg):
        self.logText.AppendText("\n")
        self.logText.AppendText(msg)
        self.logText.AppendText("\n")
        if msg == "Load target data end":
            self.btn_generatedata.Enable()
            self.btn_previewdata.Enable()
            self.btn_loaddatanow.SetLabel("Load Data Now")
            self.btn_loaddatanow.Enable()
            self.btn_loaddataschedule.Enable()
            self.btn_clearLog.Enable()
            self.btn_copyLog.Enable()
            self.btn_closeLog.Enable()
        else:
            pass

class LoadLookupThread(Thread):
    def __init__(self, dbfile, logText):
        Thread.__init__(self)
        self.dbfile = dbfile
        self.logText = logText
        self.start()
    def run(self):
        wx.CallAfter(pub.sendMessage, "loadLookup", msg="Load lookup table starting")
        lookTab = loadingLookupTable.LookupTable(self.dbfile, self.logText)
        lookTab.loading()
        wx.CallAfter(pub.sendMessage, "loadLookup", msg="Load lookup table end")

class GenerateDataToThread(Thread):
    def __init__(self, dbfile, logText):
        Thread.__init__(self)
        self.dbfile = dbfile
        self.logText = logText
        self.start()
    def run(self):
        wx.CallAfter(pub.sendMessage, "GenerateData", msg="Generate data starting")
        link = connectDB.ConnectDB(self.dbfile, self.logText)
        conn = link.get_conn()
        db_final = iLoadTools.DatabaseTool(conn)
        configName = db_final.getConfigName()
        finalSQL = "create table %s as select * from %s" % \
                   (configName+"_tar_vw2_tab", configName+"_tar_vw2", )
        try:
            conn.execute(finalSQL)
        except Exception as e:
            self.logText.AppendText(str(e))
            self.logText.AppendText("\n")
        conn.commit()
        self.logText.AppendText("Final table created\n")
        wx.CallAfter(pub.sendMessage, "GenerateData", msg="Generate data end")

class LoadDataToTargetThread(Thread):
    def __init__(self, dbfile, logText):
        Thread.__init__(self)
        self.dbfile = dbfile
        self.logText = logText
        self.start()
    def run(self):
        time.sleep(0.03)
        wx.CallAfter(pub.sendMessage, "loadTarget", msg="Load target data starting")
        link = connectDB.ConnectDB(self.dbfile, self.logText)
        conn = link.get_conn()
        db_final = iLoadTools.DatabaseTool(conn)
        configName = db_final.getConfigName()
        credential = db_final.getCredential()
        tarList = db_final.getTarFieldList()
        tarTable = db_final.getTargetTable()
        loadType = db_final.getLoadType()
        keys = db_final.getKey()
        
        self.logText.AppendText("Execute importing data\n")
        self.logText.AppendText(tarTable)
        self.logText.AppendText("\n")
        self.logText.AppendText(str(keys))
        self.logText.AppendText("\n")
        data = db_final.getViewData(tarList, configName+"_tar_vw2_tab")
        
        try:
            tarClass = iLoadTools.getLoadTypeClass(loadType)
            tt = tarClass(credential, self.logText)
        except Exception as e:
            self.logText.AppendText(e.args[0])
            self.logText.AppendText("\n")
        tar_conn = tt.getConnection()
        if tar_conn:
            if keys["haskey"] == "one key":
                self.logText.AppendText("one key\n")
                tt.upsertData(data, tarTable, tarList, credential, keys)
            elif keys["haskey"] == "no key":
                self.logText.AppendText("no key\n")
                tt.insertData(data, tarTable, tarList, credential)
            else:
                self.logText.AppendText("You can only set up one primary key.\n")
        time.sleep(0.03)
        link.close_conn()
        wx.CallAfter(pub.sendMessage, "loadTarget", msg="Load target data end")

class VirtualLog:
    def __init__(self):
        pass
    def AppendText(self, str):
        print(str)
