#!/usr/bin/python

'''
File dvdArchiver.py
@authors: Heriberto Nieto, TACC Visualization Laboratory, http://www.tacc.utexas.edu/resources/visualization
Note: wxPython requires Python to be run in 32-bit mode. If the computer running this program is a 64-bit machine,
      open a terminal and run "export VERSIONER_PYTHON_PREFER_32_BIT=yes"
'''

import sys
import traceback
from wx.lib.wordwrap import wordwrap
import wx.lib.agw.genericmessagedialog as GMD
from textBoxValidator import textBoxValidator
import wx

class Archiver(wx.Frame):

    def __init__(self, parent, title):    
        super(Archiver, self).__init__(parent, title=title, size=(500, 625))

        self.InitUI()
        self.Centre()
        self.Show()     

    def InitUI(self):
      
        self.panel = wx.Panel(self)
        
        self.gridSizer = wx.GridBagSizer(5, 5)

        # header
        self.label1 = wx.StaticText(self.panel, label="DVD Video Archiver")
        self.gridSizer.Add(self.label1, pos=(0, 0), flag=wx.TOP|wx.LEFT|wx.BOTTOM, border=15)

        self.icon = wx.StaticBitmap(self.panel, bitmap=wx.Bitmap('icon.png'))
        self.gridSizer.Add(self.icon, pos=(0, 4), flag=wx.TOP|wx.RIGHT|wx.ALIGN_RIGHT, border=5)

        self.divider = wx.StaticLine(self.panel)
        self.gridSizer.Add(self.divider, pos=(1, 0), span=(1, 5), flag=wx.EXPAND|wx.BOTTOM, border=10)

        # text boxes
        self.label2 = wx.StaticText(self.panel, label="Output Directory")
        self.gridSizer.Add(self.label2, pos=(2, 0), flag=wx.LEFT|wx.TOP, border=10)

        self.textBox1 = wx.TextCtrl(self.panel, validator=textBoxValidator())
        self.gridSizer.Add(self.textBox1, pos=(2, 1), span=(1, 3), flag=wx.TOP|wx.EXPAND, border=5)
        
        self.button1 = wx.Button(self.panel, label="Browse...")
        self.gridSizer.Add(self.button1, pos=(2, 4), flag=wx.TOP|wx.RIGHT, border=5)

        self.label3 = wx.StaticText(self.panel, label="Output File Name")
        self.gridSizer.Add(self.label3, pos=(3, 0), flag=wx.LEFT|wx.TOP, border=10)

        self.textBox2 = wx.TextCtrl(self.panel, validator=textBoxValidator())
        self.gridSizer.Add(self.textBox2, pos=(3, 1), span=(1, 3), flag=wx.TOP|wx.EXPAND, border=5)

        self.label4 = wx.StaticText(self.panel, label="DVD Directory")
        self.gridSizer.Add(self.label4, pos=(4, 0), flag=wx.TOP|wx.LEFT, border=10)
        
        self.textBox3 = wx.TextCtrl(self.panel, validator=textBoxValidator())
        self.gridSizer.Add(self.textBox3, pos=(4, 1), span=(1, 3), flag=wx.TOP|wx.EXPAND, border=5)
        
        self.button2 = wx.Button(self.panel, label="Browse...")
        self.gridSizer.Add(self.button2, pos=(4, 4), flag=wx.TOP|wx.RIGHT, border=5)

        # check boxes
        self.makeISO = wx.CheckBox(self.panel, label="Create ISO")
        self.makeISO.SetValue(True)
        self.makeMKV = wx.CheckBox(self.panel, label="Create Matroska")
        self.makeMP4 = wx.CheckBox(self.panel, label="Create MP4")
        self.makeMP4.SetValue(True)
        
        self.staticBox = wx.StaticBox(self.panel, label="Optional Attributes")
        self.boxSizer = wx.StaticBoxSizer(self.staticBox, wx.VERTICAL)
        self.boxSizer.Add(self.makeISO, flag=wx.LEFT|wx.TOP, border=5)
        self.boxSizer.Add(self.makeMKV, flag=wx.LEFT, border=5)
        self.boxSizer.Add(self.makeMP4,flag=wx.LEFT, border=5)
        self.boxSizer.Add((0,10), 0)
        self.gridSizer.Add(self.boxSizer, pos=(6, 0), span=(1, 5), flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)
        
        # logging
        self.log = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE)
        self.log.AppendText("Waiting on user ...")
        self.gridSizer.Add(self.log, pos=(8, 0), span=(9, 5), flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)

        # control buttons
        self.about = wx.Button(self.panel, label='About')
        self.gridSizer.Add(self.about, pos=(18, 0), flag=wx.LEFT, border=10)
        
        self.help = wx.Button(self.panel, label='Help')
        self.gridSizer.Add(self.help, pos=(18, 1), flag=wx.LEFT, border=-60)

        self.archive = wx.Button(self.panel, label="Archive")
        self.gridSizer.Add(self.archive, pos=(18, 3))

        self.cancel = wx.Button(self.panel, label="Cancel")
        self.gridSizer.Add(self.cancel, pos=(18, 4), span=(1, 1), flag=wx.BOTTOM|wx.RIGHT, border=5)

        self.gridSizer.AddGrowableCol(2)
        
        self.panel.SetSizer(self.gridSizer)
        
        # event handling
        self.button1.Bind(wx.EVT_BUTTON, self.get_output_dir)
        self.button2.Bind(wx.EVT_BUTTON, self.get_dvd_dir)
        self.about.Bind(wx.EVT_BUTTON, self.open_about)
        self.help.Bind(wx.EVT_BUTTON, self.open_help)
        self.archive.Bind(wx.EVT_BUTTON, self.run_app)
                
    def run_app(self, event):
        self.panel.Validate()
        
    def open_help(self, event):
        msg = wordwrap(
            "Output Directory:\nType or Select the directory in which you wish to store all output files.\n\n"
            "Output File Name:\nProvide a name to be used for all generated files.\n\n"
            "DVD Directory:\nType or Select the directory of the Master DVD or ISO image.\n\n"
            "Optional Attributes:\nSelect the preservation media files that you would like to be generated.\n\n"
            "Logging:\nAll application procedures will be documented in the program log window.\n\n",
            500, wx.ClientDC(self.panel))
        helpWindow = GMD.GenericMessageDialog(self, msg,"Help", wx.OK | wx.ICON_QUESTION)
        helpWindow.ShowModal()
        helpWindow.Destroy()
        
    def open_about(self, event):
        info = wx.AboutDialogInfo()
        info.Name = "DVD Video Archiver"
        info.Version = "(version 1.0.0)"
        info.Description = wordwrap(
            "DVD Video Archiver is an application developed by the Texas Advanced Computing Center "
            "to aid in the the preservation of digital art stored in DVD media.\n\n\n",
            350, wx.ClientDC(self.panel))
        info.WebSite = ("https://github.com/hnieto/DVD-Video-Archiver", "Github Repo")
        info.Developers = ["Heriberto Nieto", "Maria Esteva", "Karla Vega", "Summer Gunnels"]
        info.License = wordwrap(
            "This program is free software: you can redistribute it and/or modify"
            "it under the terms of the GNU General Public License as published by"
            "the Free Software Foundation\n\n"
            "This program is distributed in the hope that it will be useful, "
            "but WITHOUT ANY WARRANTY; without even the implied warranty of "
            "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the "
            "GNU General Public License for more details.\n\n"
            "You should have received a copy of the GNU General Public License "
            "along with this program.  If not, see <http://www.gnu.org/licenses/>.",
            450, wx.ClientDC(self.panel))
        
        # Show the wx.AboutBox
        wx.AboutBox(info)
        
    def get_output_dir(self, event):
        dlg = wx.DirDialog(self, "", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dlg.ShowModal() == wx.ID_OK:
            self.selectedPath = dlg.GetPath()
            self.textBox1.SetValue(self.selectedPath)
        dlg.Destroy()
        
    def get_dvd_dir(self, event):
        dlg = wx.DirDialog(self, "", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dlg.ShowModal() == wx.ID_OK:
            self.selectedPath = dlg.GetPath()
            self.textBox3.SetValue(self.selectedPath)
        dlg.Destroy()

if __name__ == '__main__':

    app = wx.App()
    try:
        Archiver(None, title="Texas Advanced Computing Center")
        app.MainLoop()
    except:
        # show error messages in pop up
        message = ''.join(traceback.format_exception(*sys.exc_info()))
        dialog = wx.MessageDialog(None, message, 'Error!', wx.OK|wx.ICON_ERROR)
        dialog.ShowModal()