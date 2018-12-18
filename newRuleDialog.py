#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx, pdb

choiceRTList = ['lookup', 'function']

class NewRuleDialog(wx.Dialog):
    def __init__(
            self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE, data = {"flag" : "new"}
            ):

        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)

        self.PostCreate(pre)

        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self, -1, "Rule")
        sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        box1 = wx.BoxSizer(wx.HORIZONTAL)
        label1 = wx.StaticText(self, -1, "RuleName:", size=(80,-1))
        label1.SetForegroundColour((255,0,0))
        box1.Add(label1, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.textRN = wx.TextCtrl(self, -1, "", size=(180,-1))
        box1.Add(self.textRN, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box1, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        box2 = wx.BoxSizer(wx.HORIZONTAL)
        label2 = wx.StaticText(self, -1, "RuleType:", size=(80,-1))
        label2.SetForegroundColour((255,0,0))
        box2.Add(label2, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.choiceRT = wx.Choice(self, -1, (100, 50), choices = choiceRTList)
        self.Bind(wx.EVT_CHOICE, self.OnEvtChoiceRT, self.choiceRT)
        box2.Add(self.choiceRT, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box2, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        box3 = wx.BoxSizer(wx.HORIZONTAL)
        self.label3 = wx.StaticText(self, -1, "LookField:", size=(80,-1))
        box3.Add(self.label3, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.textLF = wx.TextCtrl(self, -1, "", size=(180,-1))
        box3.Add(self.textLF, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box3, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        
        box4 = wx.BoxSizer(wx.HORIZONTAL)
        self.label4 = wx.StaticText(self, -1, "LookupObject:", size=(80,-1))
        box4.Add(self.label4, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.textLO = wx.TextCtrl(self, -1, "", size=(180,-1))
        box4.Add(self.textLO, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box4, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        
        box5 = wx.BoxSizer(wx.HORIZONTAL)
        label5 = wx.StaticText(self, -1, "OutField:", size=(80,-1))
        label5.SetForegroundColour((255,0,0))
        box5.Add(label5, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.textOF = wx.TextCtrl(self, -1, "", size=(180,-1))
        box5.Add(self.textOF, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box5, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        box6 = wx.BoxSizer(wx.HORIZONTAL)
        label6 = wx.StaticText(self, -1, "Where:", size=(80,-1))
        box6.Add(label6, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.textWH = wx.TextCtrl(self, -1, "", size=(180,-1))
        box6.Add(self.textWH, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box6, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        
        box7 = wx.BoxSizer(wx.HORIZONTAL)
        label7 = wx.StaticText(self, -1, "Condition:", size=(80,-1))
        label7.SetForegroundColour((255,0,0))
        box7.Add(label7, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.textCD = wx.TextCtrl(self, -1, "", size=(180,-1))
        box7.Add(self.textCD, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box7, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        
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
            self.textRN.SetValue(data["rule_name"])
            self.choiceRT.SetSelection(choiceRTList.index(data["rule_type"]))
            if data["rule_type"] == "function":
                self.label3.SetForegroundColour((0,0,0))
                self.label4.SetForegroundColour((0,0,0))
                self.textLF.SetEditable(False)
                self.textLO.SetEditable(False)
                self.textWH.SetEditable(False)
            if data["rule_type"] == "lookup":
                self.label3.SetForegroundColour((255,0,0))
                self.label4.SetForegroundColour((255,0,0))
            self.textLF.SetValue(data["look_field"])
            self.textLO.SetValue(data["lookup_object"])
            self.textOF.SetValue(data["out_field"])
            self.textWH.SetValue(data["where_c"])
            self.textCD.SetValue(data["condition"])
        
    def OnEvtButtonSave(self, evt):
        self.newRule = {}
        self.newRule["RuleName"] = self.textRN.GetValue()
        self.newRule["RuleType"] = self.choiceRT.GetString(self.choiceRT.GetSelection())
        self.newRule["LookField"] = self.textLF.GetValue()
        self.newRule["LookupObject"] = self.textLO.GetValue()
        self.newRule["OutField"] = self.textOF.GetValue()
        self.newRule["Where"] = self.textWH.GetValue()
        self.newRule["Condition"] = self.textCD.GetValue()

        if self.newRule["RuleType"] == "lookup":
            if self.newRule["RuleName"] == "":
                wx.MessageBox("You should provide RuleName.")
            elif self.newRule["RuleType"] == "":
                wx.MessageBox("You should provide RuleType.")
            elif self.newRule["LookField"] == "":
                wx.MessageBox("You should provide LookField.")
            elif self.newRule["LookupObject"] == "":
                wx.MessageBox("You should provide LookupObject.")
            elif self.newRule["OutField"] == "":
                wx.MessageBox("You should provide an OutField.")
            elif self.errorOutfieldLook(self.newRule["OutField"]):
                wx.MessageBox("OutField is not correct.")
            elif self.newRule["Condition"] == "":
                wx.MessageBox("You should provide Condition.")
            elif self.errorConditionLookup(self.newRule["Condition"], self.newRule["RuleName"], self.newRule["OutField"]):
                wx.MessageBox("Condition is not correct.")
            else:
                self.EndModal(wx.ID_SAVE)
        else:
            if self.newRule["RuleName"] == "":
                wx.MessageBox("You should provide RuleName.")
            elif self.newRule["RuleType"] == "":
                wx.MessageBox("You should provide RuleType.")
            elif self.newRule["OutField"] == "":
                wx.MessageBox("You should provide an OutField.")
            elif self.newRule["Condition"] == "":
                wx.MessageBox("You should provide Condition.")
            elif self.errorConditionFunction(self.newRule["Condition"], self.newRule["RuleName"]):
                wx.MessageBox("Condition is not correct.")
            else:
                self.EndModal(wx.ID_SAVE)

    def OnEvtChoiceRT(self, evt):
        if evt.GetString() == "function":
            self.label3.SetForegroundColour((0,0,0))
            self.label3.Refresh()
            self.label4.SetForegroundColour((0,0,0))
            self.label4.Refresh()
            self.textLF.Clear()
            self.textLF.SetEditable(False)
            self.textLO.Clear()
            self.textLO.SetEditable(False)
            self.textWH.Clear()
            self.textWH.SetEditable(False)
        if evt.GetString() == "lookup":
            self.label3.SetForegroundColour((255,0,0))
            self.label3.Refresh()
            self.label4.SetForegroundColour((255,0,0))
            self.label4.Refresh()
            self.textLF.SetEditable(True)
            self.textLO.SetEditable(True)
            self.textWH.SetEditable(True)

    def errorConditionLookup(self, con, ruleName, outfield):
        """format: src.column=ruleName.column"""
        rev = False
        preLi = ["src", ruleName]
        outLi = outfield.split(",")
        
        if con.count("=") != 1:
            rev = True
        else:
            li = con.split("=")
            for l in li:
                if l.strip() == "":
                    rev = True
            if rev is False:
                for l in li:
                    if l.count(".") != 1:
                        rev = True
            if rev is False:
                c0 = li[0].split(".")
                if preLi.count(c0[0]) <= 0:
                    rev = True
                else:
                    if c0[0] == ruleName and outLi.count(c0[1]) < 1:
                        rev = True
                    preLi = filter(lambda x:x!=c0[0], preLi)
                if c0[1].strip() == "":
                    rev = True

                c1 = li[1].split(".")
                if preLi.count(c1[0]) <= 0:
                    rev = True
                else:
                    if c1[0] == ruleName and outLi.count(c1[1]) < 1:
                        rev = True
                    preLi = filter(lambda x:x!=c1[0], preLi)
                if c1[1].strip() == "":
                    rev = True
        return rev

    def errorConditionFunction(self, con, ruleName):
        rev = False
        if con.count("=") >= 1:
            rev = True
        return rev

    def errorOutfieldLook(self, outfield):
        rev = False
        if outfield.count(",") < 1:
            rev = True
        else:
            li = outfield.split(",")
            for item in li:
                if item.strip() == "":
                    rev = True
        
        return rev
