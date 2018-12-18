#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx, pdb, re

choiceFTList = ['text', 'integer', 'date', 'real']
choiceRuleList = ['direct', 'lookup', 'function']

class NewMapDialog(wx.Dialog):
    def __init__(
            self, parent, ID, title, ref_choices, size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE, data = {"flag" : "new"}
            ):

        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)

        self.PostCreate(pre)
        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self, -1, "Mapping")
        sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        self.ref_choices = ref_choices

        box1 = wx.BoxSizer(wx.HORIZONTAL)
        label1 = wx.StaticText(self, -1, "TargetField:", size=(70,-1))
        label1.SetForegroundColour((255,0,0))
        box1.Add(label1, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.textTF = wx.TextCtrl(self, -1, "", size=(180,-1))
        box1.Add(self.textTF, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box1, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        box2 = wx.BoxSizer(wx.HORIZONTAL)
        self.label2 = wx.StaticText(self, -1, "SourceField:", size=(70,-1))
        box2.Add(self.label2, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.textSF = wx.TextCtrl(self, -1, "", size=(180,-1))
        box2.Add(self.textSF, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box2, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        
        box3 = wx.BoxSizer(wx.HORIZONTAL)
        label3 = wx.StaticText(self, -1, "FieldType:", size=(70,-1))
        label3.SetForegroundColour((255,0,0))
        box3.Add(label3, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.choiceFT = wx.Choice(self, -1, (100, 50), choices = choiceFTList)
        box3.Add(self.choiceFT, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box3, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        
        box4 = wx.BoxSizer(wx.HORIZONTAL)
        label4 = wx.StaticText(self, -1, "FieldLength:", size=(70,-1))
        label4.SetForegroundColour((255,0,0))
        box4.Add(label4, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.textFL = wx.TextCtrl(self, -1, "", size=(180,-1))
        box4.Add(self.textFL, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box4, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        
        box5 = wx.BoxSizer(wx.HORIZONTAL)
        label5 = wx.StaticText(self, -1, "Rule:", size=(70,-1))
        label5.SetForegroundColour((255,0,0))
        box5.Add(label5, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.choiceRule = wx.Choice(self, -1, (100, 50), choices = choiceRuleList)
        self.Bind(wx.EVT_CHOICE, self.OnEvtChoiceRule, self.choiceRule)
        box5.Add(self.choiceRule, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box5, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        box6 = wx.BoxSizer(wx.HORIZONTAL)
        self.label6 = wx.StaticText(self, -1, "Reference:", size=(70,-1))
        box6.Add(self.label6, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.choiceRef = wx.Choice(self, -1, (100, 50), choices = self.ref_choices)
        box6.Add(self.choiceRef, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box6, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        
        box7 = wx.BoxSizer(wx.HORIZONTAL)
        label7 = wx.StaticText(self, -1, "IsKey:", size=(70,-1))
        box7.Add(label7, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.checkboxKey = wx.CheckBox(self, -1, "", style=wx.CHK_3STATE|wx.CHK_ALLOW_3RD_STATE_FOR_USER)
        box7.Add(self.checkboxKey, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box7, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        
        box8 = wx.BoxSizer(wx.HORIZONTAL)
        label8 = wx.StaticText(self, -1, "IsVariable:", size=(70,-1))
        box8.Add(label8, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.checkboxVal = wx.CheckBox(self, -1, "", style=wx.CHK_3STATE|wx.CHK_ALLOW_3RD_STATE_FOR_USER)
        box8.Add(self.checkboxVal, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box8, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        
        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        btnsizer = wx.StdDialogButtonSizer()
        
        if wx.Platform != "__WXMSW__":
            btn = wx.ContextHelpButton(self)
            btnsizer.AddButton(btn)
        
        btnSave = wx.Button(self, wx.ID_SAVE)
        btnSave.SetHelpText("The OK button completes the dialog")
        btnSave.SetDefault()
        self.Bind(wx.EVT_BUTTON, self.OnEvtButtonSave, btnSave)
        btnsizer.AddButton(btnSave)

        btnCancel = wx.Button(self, wx.ID_CANCEL)
        btnCancel.SetHelpText("The Cancel button cancels the dialog. (Cool, huh?)")
        btnsizer.AddButton(btnCancel)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)
        
        if data["flag"] == "edit":
            self.textTF.SetValue(data["target_field"])
            self.textSF.SetValue(data["source_field"])
            self.choiceFT.SetSelection(choiceFTList.index(data["field_type"]))
            self.textFL.SetValue(data["field_length"])
            self.choiceRule.SetSelection(choiceRuleList.index(data["rule"]))
            if data["rule"] == "direct":
                self.label6.SetForegroundColour((0,0,0))
                self.label2.SetForegroundColour((255,0,0))
            else:
                self.label6.SetForegroundColour((255,0,0))
                self.label2.SetForegroundColour((0,0,0))
            self.choiceRef.SetSelection(ref_choices.index(data["reference"]))
            if data["iskey"] == "False":
                isKey = False
            elif data["iskey"] == "True":
                isKey = True
            self.checkboxKey.SetValue(isKey)
            if data["isvariable"] == "False":
                isVal = False
            elif data["isvariable"] == "True":
                isVal = True
            self.checkboxVal.SetValue(isVal)
        
    def OnEvtButtonSave(self, evt):
        self.newMapping = {}
        self.newMapping["TargetField"] = self.textTF.GetValue()
        self.newMapping["SourceField"] = self.textSF.GetValue()
        self.newMapping["FieldType"] = self.choiceFT.GetString(self.choiceFT.GetSelection())
        self.newMapping["FieldLength"] = self.textFL.GetValue()
        self.newMapping["Rule"] = self.choiceRule.GetString(self.choiceRule.GetSelection())
        self.newMapping["Reference"] = self.choiceRef.GetString(self.choiceRef.GetSelection())
        self.newMapping["IsKey"] = self.checkboxKey.GetValue()
        self.newMapping["IsVariable"] = self.checkboxVal.GetValue()

        if self.newMapping["Rule"] == "direct":
            if self.newMapping["TargetField"] == "":
                wx.MessageBox("You should provide TargetField.")
            elif self.newMapping["SourceField"] == "":
                wx.MessageBox("You should provide SourceField.")
            elif self.newMapping["FieldType"] == "":
                wx.MessageBox("You should select a FieldType.")
            elif self.newMapping["FieldLength"] == "":
                wx.MessageBox("You should provide FieldLength.")
            elif re.match(r"^[1-9]", self.newMapping["FieldLength"]) is None:
                wx.MessageBox("You should provide a number for FieldLength.")
            elif self.newMapping["Rule"] == "":
                wx.MessageBox("You should select a Rule.")
            elif self.newMapping["Reference"] != "":
                wx.MessageBox("Direct rule does not need a reference.")
                self.choiceRef.SetSelection(0)
            else:
                self.EndModal(wx.ID_SAVE)
        else:
            if self.newMapping["TargetField"] == "":
                wx.MessageBox("You should provide TargetField.")
            elif self.newMapping["FieldType"] == "":
                wx.MessageBox("You should select a FieldType.")
            elif self.newMapping["FieldLength"] == "":
                wx.MessageBox("You should provide FieldLength.")
            elif re.match(r"^[1-9]", self.newMapping["FieldLength"]) is None:
                wx.MessageBox("You should provide a number for FieldLength.")
            elif self.newMapping["Rule"] == "":
                wx.MessageBox("You should select a Rule.")
            elif self.newMapping["Reference"] == "":
                wx.MessageBox("You should provide Reference.")
            else:
                self.EndModal(wx.ID_SAVE)
        
    def OnEvtChoiceRule(self, evt):
        if evt.GetString() == "direct":
            self.label6.SetForegroundColour((0,0,0))
            self.label6.Refresh()
            self.label2.SetForegroundColour((255,0,0))
            self.label2.Refresh()
            self.choiceRef.SetSelection(0)
        if evt.GetString() == "lookup":
            self.label6.SetForegroundColour((255,0,0))
            self.label6.Refresh()
            self.label2.SetForegroundColour((0,0,0))
            self.label2.Refresh()
        if evt.GetString() == "function":
            self.label6.SetForegroundColour((255,0,0))
            self.label6.Refresh()
            self.label2.SetForegroundColour((0,0,0))
            self.label2.Refresh()
