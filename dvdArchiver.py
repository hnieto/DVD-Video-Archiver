#!/usr/bin/python

'''
File dvdArchiver.py
@authors: Heriberto Nieto, TACC Visualization Laboratory, http://www.tacc.utexas.edu/resources/visualization
Note: wxPython requires Python to be run in 32-bit mode. If the computer running this program is a 64-bit machine,
      open a terminal and run "export VERSIONER_PYTHON_PREFER_32_BIT=yes"
'''

import wx

class Archiver(wx.Frame):

    def __init__(self, parent, title):    
        super(Archiver, self).__init__(parent, title=title, size=(450, 400))

        self.InitUI()
        self.Centre()
        self.Show()     

    def InitUI(self):
      
        panel = wx.Panel(self)
        
        sizer = wx.GridBagSizer(5, 5)

        # header
        text1 = wx.StaticText(panel, label="DVD Video Archiver")
        sizer.Add(text1, pos=(0, 0), flag=wx.TOP|wx.LEFT|wx.BOTTOM, border=15)

        icon = wx.StaticBitmap(panel, bitmap=wx.Bitmap('icon.png'))
        sizer.Add(icon, pos=(0, 4), flag=wx.TOP|wx.RIGHT|wx.ALIGN_RIGHT, border=5)

        line = wx.StaticLine(panel)
        sizer.Add(line, pos=(1, 0), span=(1, 5), flag=wx.EXPAND|wx.BOTTOM, border=10)

        # text boxes
        text2 = wx.StaticText(panel, label="Output Directory")
        sizer.Add(text2, pos=(2, 0), flag=wx.LEFT|wx.TOP, border=10)

        tc1 = wx.TextCtrl(panel)
        sizer.Add(tc1, pos=(2, 1), span=(1, 3), flag=wx.TOP|wx.EXPAND, border=5)
        
        button1 = wx.Button(panel, label="Browse...")
        sizer.Add(button1, pos=(2, 4), flag=wx.TOP|wx.RIGHT, border=5)

        text3 = wx.StaticText(panel, label="Output File Name")
        sizer.Add(text3, pos=(3, 0), flag=wx.LEFT|wx.TOP, border=10)

        tc2 = wx.TextCtrl(panel)
        sizer.Add(tc2, pos=(3, 1), span=(1, 3), flag=wx.TOP|wx.EXPAND, border=5)

        text4 = wx.StaticText(panel, label="DVD Directory")
        sizer.Add(text4, pos=(4, 0), flag=wx.TOP|wx.LEFT, border=10)
        
        tc3 = wx.TextCtrl(panel)
        sizer.Add(tc3, pos=(4, 1), span=(1, 3), flag=wx.TOP|wx.EXPAND, border=5)
        
        button2 = wx.Button(panel, label="Browse...")
        sizer.Add(button2, pos=(4, 4), flag=wx.TOP|wx.RIGHT, border=5)

        # check boxes
        sb = wx.StaticBox(panel, label="Optional Attributes")

        boxsizer = wx.StaticBoxSizer(sb, wx.VERTICAL)
        makeISO = wx.CheckBox(panel, label="Create ISO")
        makeISO.SetValue(True)
        makeMKV = wx.CheckBox(panel, label="Create Matroska")
        makeMP4 = wx.CheckBox(panel, label="Create MP4")
        makeMP4.SetValue(True)
        boxsizer.Add(makeISO, flag=wx.LEFT|wx.TOP, border=5)
        boxsizer.Add(makeMKV, flag=wx.LEFT, border=5)
        boxsizer.Add(makeMP4,flag=wx.LEFT, border=5)
        boxsizer.Add((0,10), 0)
        sizer.Add(boxsizer, pos=(6, 0), span=(1, 5), flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)

        # control buttons
        button3 = wx.Button(panel, label='Help')
        sizer.Add(button3, pos=(8, 0), flag=wx.LEFT, border=10)

        button4 = wx.Button(panel, label="Archive")
        sizer.Add(button4, pos=(8, 3))

        button5 = wx.Button(panel, label="Cancel")
        sizer.Add(button5, pos=(8, 4), span=(1, 1), flag=wx.BOTTOM|wx.RIGHT, border=5)

        sizer.AddGrowableCol(2)
        
        panel.SetSizer(sizer)
        
        # event handling
        button1.Bind(wx.EVT_BUTTON, self.openDir)
        button2.Bind(wx.EVT_BUTTON, self.openDir)
        
    def openDir(self, event):
        dlg = wx.DirDialog(self, "", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dlg.ShowModal() == wx.ID_OK:
            self.SetStatusText('You selected: %s\n' % dlg.GetPath())
        dlg.Destroy()


if __name__ == '__main__':
  
    app = wx.App()
    Archiver(None, title="Texas Advanced Computing Center")
    app.MainLoop()