#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx, pdb
import configWizard, multiTargetsDialog
from wx import StaticBitmap
from utils import myimages

class MainPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.SetBackgroundColour("#ffffff")
        staticBmp = StaticBitmap(self, -1, myimages._logo9.GetBitmap(), pos=(200, 10), size=(400, 120))
        staticBmp.SetBackgroundColour("#a8a8a8")
        
        b_newConfig = wx.Button(self, -1, "New template", pos=(30, 150), size=(180, 30))
        self.Bind(wx.EVT_BUTTON, self.OnOpenNewConfig, b_newConfig)
        
        b_existsConfig = wx.Button(self, -1, "Open template", pos=(240, 150), size=(180, 30))
        self.Bind(wx.EVT_BUTTON, self.OnOpenExistsConfig, b_existsConfig)
        
        b_multiConfig = wx.Button(self, -1, "Multiple targets template", pos=(450, 150), size=(180, 30))
        self.Bind(wx.EVT_BUTTON, self.OnOpenMultiConfig, b_multiConfig)
        
    def OnOpenNewConfig(self, evt):
        new_wizard = configWizard.ConfigWizard(self, "new")
    
    def OnOpenExistsConfig(self, evt):
        exists_wizard = configWizard.ConfigWizard(self, "exists")
    
    def OnOpenMultiConfig(self, evt):
        dlg = multiTargetsDialog.MultiTargetsDialog(self, -1, "Multiple targets template", size=(568,430))
        dlg.ShowModal()
        dlg.Destroy()
