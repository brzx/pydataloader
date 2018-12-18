#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx, os, json, time, pdb
import wx.lib.rcsizer as rcs
import wx.lib.masked as masked
import iLoad
from utils import iLoadTools

wildcard = "Json source (*.json)|*.json"
           
class MultiTargetsDialog(wx.Dialog):
    def __init__(
            self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE,
            ):
        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)
        self.PostCreate(pre)
        
        sizer = rcs.RowColSizer()
        
        self.lc_result = wx.ListCtrl(self, -1, size=(200,300), style=wx.LC_REPORT)
        self.lc_result.InsertColumn(0, "Index", width=41, format=wx.LIST_FORMAT_CENTER)
        self.lc_result.InsertColumn(1, "Configuration Name", width=160)
        sizer.Add(self.lc_result, row=1, col=1, colspan=6, rowspan=10)
        
        btn_add = wx.Button(self, -1, "<- ADD") 
        self.Bind(wx.EVT_BUTTON, self.OnAddClick, btn_add)
        sizer.Add(btn_add, row=2, col=8, colspan=2)
        
        btn_up = wx.Button(self, -1, "UP")
        self.Bind(wx.EVT_BUTTON, self.OnUpClick, btn_up)
        sizer.Add(btn_up, row=4, col=8, colspan=2)
        
        btn_down = wx.Button(self, -1, "DOWN")
        self.Bind(wx.EVT_BUTTON, self.OnDownClick, btn_down)
        sizer.Add(btn_down, row=6, col=8, colspan=2)
        
        btn_remove = wx.Button(self, -1, "REMOVE ->") 
        self.Bind(wx.EVT_BUTTON, self.OnRemoveClick, btn_remove)
        sizer.Add(btn_remove, row=8, col=8, colspan=2)

        self.lc_config = wx.ListCtrl(self, -1, size=(200,300), style=wx.LC_REPORT|wx.LC_SINGLE_SEL)
        
        info = wx.ListItem()
        info.m_mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
        info.m_image = -1
        info.m_format = 0
        info.m_text = "Configuration Name"
        info.SetWidth(200)
        info.SetTextColour(wx.BLUE)
        info.SetAlign(wx.LIST_FORMAT_CENTER)
        self.lc_config.InsertColumnInfo(0, info)
        
        gvc = iLoadTools.GetValidConfig()
        self.configuration = gvc.getValidConfig()
        for i in self.configuration:
            self.lc_config.Append([i])
        sizer.Add(self.lc_config, row=1, col=11, colspan=6, rowspan=10)
        
        line = wx.StaticLine(self, -1, size=(544,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, row=12, col=1, colspan=19)

        btnOpen = wx.Button(self, wx.ID_OPEN)
        self.Bind(wx.EVT_BUTTON, self.OnOpenExists, btnOpen)
        sizer.Add(btnOpen, row=13, col=1, colspan=3)
        
        btnSave = wx.Button(self, wx.ID_SAVE)
        self.Bind(wx.EVT_BUTTON, self.OnSaveFile, btnSave)
        sizer.Add(btnSave, row=13, col=4, colspan=3)
        
        btnClose = wx.Button(self, wx.ID_CLOSE)
        self.Bind(wx.EVT_BUTTON, self.OnCloseClick, btnClose)
        sizer.Add(btnClose, row=13, col=7, colspan=3)
        
        btnsScheduleSetup = wx.Button(self, -1, "Schedule Setup", size=(200,-1))
        self.Bind(wx.EVT_BUTTON, self.OnScheduleSetup, btnsScheduleSetup)
        sizer.Add(btnsScheduleSetup, row=13, col=10, colspan=5)
        
        self.SetSizer(sizer)
        #sizer.Fit(self)
    
    def OnAddClick(self, evt):
        index = self.lc_config.GetFirstSelected()
        if index == -1:
            wx.MessageBox("Please select an item on the right.")
            return
        else:
            count = self.lc_result.GetItemCount()
            resultLi = []
            newItemLi = []
            if count > 0:
                for i in range(count):
                    resultLi.append(self.lc_result.GetItemText(i, 1))
            newItemLi.append(count+1)
            newItemLi.append(self.lc_config.GetItemText(index))
            self.lc_result.Append(newItemLi)
            self.lc_config.DeleteItem(index)
        
    def OnRemoveClick(self, evt):
        index = self.lc_result.GetFirstSelected()
        if index == -1:
            wx.MessageBox("Please select an item on the left.")
            return
        else:
            count = self.lc_result.GetItemCount()
            countConfig = self.lc_config.GetItemCount()
            configLi = []
            for i in range(countConfig):
                configLi.append(self.lc_config.GetItemText(i, 0))
            item = self.lc_result.GetItemText(index, 1)
            if self.configuration.count(item) > 0 and configLi.count(item) == 0:
                self.lc_config.Append([item])
            self.lc_result.DeleteItem(index)
            flag = index
            li = []
            while flag < count-1:
                li.append([flag+1, self.lc_result.GetItemText(flag, 1)])
                flag = flag + 1
            while self.lc_result.GetItemCount() > index:
                self.lc_result.DeleteItem(index)
            for i in li:
                self.lc_result.Append(i)
    
    def OnUpClick(self, evt):
        index = self.lc_result.GetFirstSelected()
        count = self.lc_result.GetItemCount()
        if index == -1:
            wx.MessageBox("Please select an item on the left.")
            return
        elif index == 0:
            #wx.MessageBox("This is the first one.")
            return
        else:
            flag = index - 1
            li = []
            showli = []
            li.append(self.lc_result.GetItemText(index, 1))
            for i in range(flag, count):
                if i != index:
                    li.append(self.lc_result.GetItemText(i, 1))
            show_index = index
            for j in li:
                showli.append([show_index, j])
                show_index = show_index + 1
            while self.lc_result.GetItemCount() > index:
                self.lc_result.DeleteItem(index)
            self.lc_result.DeleteItem(flag)
            for l in showli:
                self.lc_result.Append(l)
            self.lc_result.Select(index-1)
        
    def OnDownClick(self, evt):
        index = self.lc_result.GetFirstSelected()
        count = self.lc_result.GetItemCount()
        index = self.lc_result.GetFirstSelected()
        if index == -1:
            wx.MessageBox("Please select an item on the left.")
            return
        elif index == count-1:
            return
        else:
            flag = index
            li = []
            showli = []
            li.append(self.lc_result.GetItemText(index+1, 1))
            for i in range(index, count):
                if i != index+1:
                    li.append(self.lc_result.GetItemText(i, 1))
            show_index = index + 1
            for j in li:
                showli.append([show_index, j])
                show_index = show_index + 1
            while self.lc_result.GetItemCount() > index:
                self.lc_result.DeleteItem(index)
            for l in showli:
                self.lc_result.Append(l)
            self.lc_result.Select(index+1)
    
    def OnOpenExists(self, evt):
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=iLoad.schedulespace, 
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            self.lc_config.DeleteAllItems()
            for i in self.configuration:
                self.lc_config.Append([i])
            self.lc_result.DeleteAllItems()
            filepath = dlg.GetPaths()[0]
            with open(filepath) as json_file:
                data = json.load(json_file)
            if data["identifier"] == "iLoadMultipleTargetsConfig":
                for i in range(1, len(data["list"])+1):
                    for li in data["list"]:
                        if int(li[0]) == i:
                            self.lc_result.Append(li)
            else:
                wx.MessageBox("Not a valid schedule file!")
        dlg.Destroy()
    
    def OnSaveFile(self, evt):
        count = self.lc_result.GetItemCount()
        print("count=%d" % (count))
        if count <= 0:
            wx.MessageBox("Please add item to the left.")
            return
        else:
            dlg = wx.FileDialog(
                self, message="Save file as ...", defaultDir=iLoad.schedulespace, 
                defaultFile="", wildcard=wildcard, style=wx.SAVE
                )
            dlg.SetFilterIndex(2)
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                li = []
                filedata = {}
                filedata["identifier"] = "iLoadMultipleTargetsConfig"
                for i in range(count):
                    li.append([self.lc_result.GetItemText(i), self.lc_result.GetItemText(i, 1)])
                filedata["list"] = li
                with open(path, "wb") as f:
                    f.write(json.dumps(filedata))
            
            dlg.Destroy()

    def OnScheduleSetup(self, evt):
        if True:
            self.scheduleDlg = wx.Dialog(self, -1, "Schedule Setup", 
                               style=wx.DEFAULT_DIALOG_STYLE|wx.SAVE, size=(400, 180))
            textDate = wx.StaticText(self.scheduleDlg, -1, "Date:", size=(30,-1))
            self.dpc = wx.GenericDatePickerCtrl(self.scheduleDlg, #size=(120,-1),
                                           style = wx.TAB_TRAVERSAL
                                           | wx.DP_DROPDOWN
                                           | wx.DP_SHOWCENTURY
                                           | wx.DP_ALLOWNONE )

            btn_selectSaved = wx.Button(self.scheduleDlg, -1, "Browse...")
            self.scheduleDlg.Bind(wx.EVT_BUTTON, self.OnSelectSaved, btn_selectSaved)
            st = wx.StaticText(self.scheduleDlg, -1, "Choose:")
            self.tc_saved = wx.TextCtrl(self.scheduleDlg, -1, "", size=(200, -1))
            
            textTime = wx.StaticText(self.scheduleDlg, -1, "Time:", size=(30,-1))
            spin2 = wx.SpinButton(self.scheduleDlg, -1, wx.DefaultPosition, (-1, 25), wx.SP_VERTICAL)
            self.time24 = masked.TimeCtrl(
                            self.scheduleDlg, -1, name="24 hour control", fmt24hr=True,
                            spinButton = spin2
                            )
            sizer = rcs.RowColSizer()

            box0 = wx.BoxSizer(wx.HORIZONTAL)
            box0.Add(st, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
            box0.Add(self.tc_saved, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
            box0.Add(btn_selectSaved, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
            sizer.Add(box0, row=1, col=1, colspan=8)
            
            box1 = wx.BoxSizer(wx.HORIZONTAL)
            box1.Add(textDate, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
            box1.Add(self.dpc, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
            sizer.Add(box1, row=2, col=1, colspan=2)
            
            box2 = wx.BoxSizer(wx.HORIZONTAL)
            box2.Add(textTime, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
            box2.Add(self.time24, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
            box2.Add(spin2, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
            sizer.Add(box2, row=2, col=4, colspan=2)
            
            btnsizer = wx.StdDialogButtonSizer()
            
            if wx.Platform != "__WXMSW__":
                btn = wx.ContextHelpButton(self)
                btnsizer.AddButton(btn)
            
            btnSave = wx.Button(self.scheduleDlg, wx.ID_SAVE)
            btnSave.SetDefault()
            self.scheduleDlg.Bind(wx.EVT_BUTTON, self.OnScheduleSave, btnSave)
            btnsizer.AddButton(btnSave)
            
            btnCancel = wx.Button(self.scheduleDlg, wx.ID_CANCEL)
            btnsizer.AddButton(btnCancel)
            btnsizer.Realize()
            sizer.Add(btnsizer, row=4, col=1, colspan=5)
            self.scheduleDlg.SetSizer(sizer)
            
            scheduleDlgCode = self.scheduleDlg.ShowModal()
            self.scheduleDlg.Destroy()

    def OnScheduleSave(self, evt):
        if self.tc_saved.Label != "":
            setDay = str(self.dpc.GetValue().Format("%m/%d/%Y"))
            setTime = str(self.time24.GetValue())
            taskNM = os.path.basename(self.tc_saved.Label)[:-5]
            scheduleMultiFile = iLoad.schedulespace + "\\" + taskNM + "_schedule.bat"
            with open(scheduleMultiFile, "wb") as fo:
                fo.write("@echo off\n")
                fo.write("cd " + iLoad.homepath + "\n")
                if iLoad.env == "PROD":
                    fo.write("multiScheduleLoad.exe " + taskNM + "\n")
                elif iLoad.env == "TEST":
                    fo.write("python multiScheduleLoad.py " + taskNM + "\n")
            
            time.sleep(0.1)
            cmd = "schtasks /create /tn \"iLoad_M_%s\" /tr \"%s\" /sc ONCE /st %s /sd %s /F " \
                  % (taskNM, scheduleMultiFile, setTime, setDay, )
            print(cmd)
            print("\n")
            reCode = os.system(cmd)
            print("reCode = %d \n" % (reCode))
            if reCode == 0:
                wx.MessageBox("Save multiple schedule successfully")
                self.scheduleDlg.EndModal(self.scheduleDlg.GetReturnCode())
            else:
                wx.MessageBox("Save schedule failed!")
        else:
            wx.MessageBox("Please select a saved schedule file!")

    def OnSelectSaved(self, evt):
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=iLoad.schedulespace,
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            filepath = dlg.GetPaths()[0]
            with open(filepath) as json_file:
                data = json.load(json_file)
            if data["identifier"] == "iLoadMultipleTargetsConfig":
                self.tc_saved.Label = filepath
            else:
                wx.MessageBox("Not a valid schedule file!")
        dlg.Destroy()
    
    def OnCloseClick(self, evt):
        self.EndModal(wx.ID_CLOSE)
