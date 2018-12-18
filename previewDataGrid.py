#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx, pdb
import wx.grid as gridlib

class PreviewDataGrid(gridlib.Grid):
    def __init__(self, parent, data, columnli, rowcount):
        gridlib.Grid.__init__(self, parent, -1)
        self.moveTo = None
        self.Bind(wx.EVT_IDLE, self.OnIdle)
        nli = map(lambda x:x['name'], columnli)
        self.CreateGrid(len(data)+1, len(nli))
        for index, item in enumerate(data):
            for i, jd in enumerate(item):
                if jd is None:
                    jd = ''
                self.SetCellValue(index, i, jd)
                self.SetReadOnly(index, i, True)
        
        for index, item in enumerate(nli):
            self.SetReadOnly(len(data), index, True)
        
        self.SetCellValue(len(data), 0, "total rows: %s" % (rowcount[0][0], ))
        for index, item in enumerate(nli):
            self.SetColLabelValue(index, item)
        self.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_BOTTOM)
        self.Fit()

    def OnIdle(self, evt):
        if self.moveTo != None:
            self.SetGridCursor(self.moveTo[0], self.moveTo[1])
            self.moveTo = None
        evt.Skip()
