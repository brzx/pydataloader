#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx, pdb, os, datetime, sys, re
import mainPanel
from utils import iLoadTools
import wx.lib.agw.hyperlink as hl

# when golive to production, use env = PROD
# when test, use env = TEST
env = "PROD"

global workspace, schedulespace
ms = iLoadTools.MakeSpace()
ms.makeWorkspace()
ms.makeSchedulespace()
workspace = ms.getWorkspace()
schedulespace = ms.getSchedulespace()
homepath = ms.getHomePath()
reload(sys)
sys.setdefaultencoding("utf8")

class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800, 310))
        self.panel = mainPanel.MainPanel(self)
        self.setupMenuBar()
        self.Show(True)
    
    def setupMenuBar(self):
        self.CreateStatusBar()
        
        menu_file = wx.Menu()
        mnu_new = menu_file.Append(wx.ID_NEW, "N&ew", "New template")
        mnu_open = menu_file.Append(wx.ID_OPEN, "O&pen", "Open template")
        self.multiID = wx.NewId()
        mnu_multi = menu_file.Append(self.multiID, "M&ulti", "Multiple targets configuration")
        
        mnu_exit = menu_file.Append(wx.ID_EXIT, "E&xit",  "Exit program")
        
        menu_settings = wx.Menu()
        
        menu_view = wx.Menu()
        #self.viewSingleScheduleID = wx.NewId()
        #mnu_view = menu_view.Append(self.viewSingleScheduleID, "&Single Schedule List", "Single Schedule List")
        #self.viewMultipleScheduleID = wx.NewId()
        #mnu_view = menu_view.Append(self.viewMultipleScheduleID, "&Multiple Schedule List", "Multiple Schedule List")
        self.viewScheduleID = wx.NewId()
        mnu_scheduleList = menu_view.Append(self.viewScheduleID, "&Schedule List", "Schedule List")
        
        menu_help = wx.Menu()
        mnu_help = menu_help.Append(wx.ID_HELP, "&Help", "Help")

        self._hyper3 = hl.HyperLinkCtrl(self, wx.ID_ANY, "", URL="")
        self._hyper4 = hl.HyperLinkCtrl(self, wx.ID_ANY, "", URL="")
        hideBox = wx.BoxSizer(wx.VERTICAL)
        hideBox.Add(self._hyper3)
        hideBox.Add(self._hyper4)
        outBox = wx.BoxSizer(wx.VERTICAL)
        outBox.Add(hideBox)
        outBox.Hide(hideBox)
        self.SetSizer(outBox)
        
        mnu_issueList = menu_help.Append(-1, "&Issue List", "Issue List")
        mnu_about = menu_help.Append(wx.ID_ABOUT, "&About", "About")
        
        menubar = wx.MenuBar()
        menubar.Append(menu_file, "&File")
        #menubar.Append(menu_settings, "&Settings")
        menubar.Append(menu_view, "&View")
        menubar.Append(menu_help, "&Help")

        self.Bind(wx.EVT_MENU, self.OnLink, mnu_help)
        self.Bind(wx.EVT_MENU, self.onIssueList, mnu_issueList)
        self.Bind(wx.EVT_MENU, self.onScheduleList, mnu_scheduleList)
        self.Bind(wx.EVT_MENU, self.onAbout, mnu_about)
        self.Bind(wx.EVT_MENU, self.onExit, mnu_exit)
        self.Bind(wx.EVT_MENU, self.onNew, mnu_new)
        self.Bind(wx.EVT_MENU, self.onOpen, mnu_open)
        self.Bind(wx.EVT_MENU, self.onMulti, mnu_multi)
        
        self.SetMenuBar(menubar)
    
    def onNew(self, evt):
        self.panel.OnOpenNewConfig(evt)

    def onOpen(self, evt):
        self.panel.OnOpenExistsConfig(evt)

    def onMulti(self, evt):
        self.panel.OnOpenMultiConfig(evt)

    def OnLink(self, event):
        self._hyper4.GotoURL("html\index.html", True, True)


    def onIssueList(self, evt):
        self._hyper3.GotoURL("Issue List.txt", True, True)

    def onScheduleList(self, evt):
        command = os.popen('schtasks /query /FO CSV')
        schList = command.readlines()
        strList = []
        #for i,s in enumerate(schList):
        for s in schList:
            if re.match(r'^"\\iLoad.', s) is not None:
                str = "%s" % (s[2:s.find(',')-1], )
                strList.append(str)
                del str
        
        sList = []
        mList = []
        for it in strList:
            if re.match(r'^iLoad_M_.', it) is not None:
                mList.append(it)
            else:
                sList.append(it)
        showString = "----------------------------------------\n"
        showString = showString + "          Single Schedule List\n\n"
        for i,s in enumerate(sList):
            str = "%d: %s\n" % (i+1, s, )
            showString = showString + str
            del str
        showString = showString + "----------------------------------------\n"
        showString = showString + "          Multiple Schedule List\n\n"
        for i,m in enumerate(mList):
            str = "%d: %s\n" % (i+1, m, )
            showString = showString + str
            del str
        
        dlg = wx.MessageDialog(self, 
                               showString, 
                               "Schedule List", 
                               wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
    
    def onAbout(self, evt):
        dlg = wx.MessageDialog(self, 
                               "This app is a tool to import data to target", 
                               "About my app", 
                               wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
    
    def onExit(self, evt):
        self.Close(True)
    
def getVersionString():
    now = datetime.datetime.now()
    start = datetime.datetime.strptime('2017-11-10 18:00:00', '%Y-%m-%d %H:%M:%S')
    delta = now - start
    num = float(delta.days) / float(1000)
    return "iLoad %2.3f" % (num, )
    
if __name__ == "__main__":
    app = wx.App(False)
    frame = MainWindow(None, getVersionString())
    frame.Show()
    app.MainLoop()
