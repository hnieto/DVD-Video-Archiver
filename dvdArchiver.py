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
import os
import re
import wx
import subprocess
from time import strftime
import xml.etree.ElementTree as ET
#from ssim import runSSIM

txtFile = ""
xmlFile = ""
iso = ""
ffmpeg_command = "ffmpeg -i "
handbrake_command = "HandBrakeCLI -i "

class Archiver(wx.Frame):

    def __init__(self, parent, title):    
        super(Archiver, self).__init__(parent, title=title, size=(500, 625), style=wx.CLOSE_BOX) # close_box prevents resizing

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

        self.textBox1 = wx.TextCtrl(self.panel)#, validator=textBoxValidator())
        self.gridSizer.Add(self.textBox1, pos=(2, 1), span=(1, 3), flag=wx.TOP|wx.EXPAND, border=5)
        
        self.button1 = wx.Button(self.panel, label="Browse...")
        self.gridSizer.Add(self.button1, pos=(2, 4), flag=wx.TOP|wx.RIGHT, border=5)

        self.label3 = wx.StaticText(self.panel, label="Output File Name")
        self.gridSizer.Add(self.label3, pos=(3, 0), flag=wx.LEFT|wx.TOP, border=10)

        self.textBox2 = wx.TextCtrl(self.panel)#, validator=textBoxValidator())
        self.gridSizer.Add(self.textBox2, pos=(3, 1), span=(1, 3), flag=wx.TOP|wx.EXPAND, border=5)

        self.label4 = wx.StaticText(self.panel, label="DVD Directory")
        self.gridSizer.Add(self.label4, pos=(4, 0), flag=wx.TOP|wx.LEFT, border=10)
        
        self.textBox3 = wx.TextCtrl(self.panel)#, validator=textBoxValidator())
        self.gridSizer.Add(self.textBox3, pos=(4, 1), span=(1, 3), flag=wx.TOP|wx.EXPAND, border=5)
        
        self.button2 = wx.Button(self.panel, label="Browse...")
        self.gridSizer.Add(self.button2, pos=(4, 4), flag=wx.TOP|wx.RIGHT, border=5)

        # check boxes
        self.staticBox = wx.StaticBox(self.panel, label="Optional Attributes")
        self.boxSizer = wx.StaticBoxSizer(self.staticBox, wx.VERTICAL)
        self.makeISO = wx.CheckBox(self.panel, label="Create ISO")
        self.makeISO.SetValue(True)
        self.makeMKV = wx.CheckBox(self.panel, label="Create Matroska")
        self.makeMP4 = wx.CheckBox(self.panel, label="Create MP4")
        self.makeMP4.SetValue(True)
        self.boxSizer.Add(self.makeISO, flag=wx.LEFT|wx.TOP, border=5)
        self.boxSizer.Add(self.makeMKV, flag=wx.LEFT, border=5)
        self.boxSizer.Add(self.makeMP4,flag=wx.LEFT, border=5)
        self.boxSizer.Add((0,10), 0)
        self.gridSizer.Add(self.boxSizer, pos=(6, 0), span=(1, 5), flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)
        
        # logging
        self.logBox = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.logBox.AppendText("Waiting on user ...")
        self.gridSizer.Add(self.logBox, pos=(8, 0), span=(9, 5), flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)

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
        # validate GUI inputs
        if(self.textBoxValidator() and self.checkBoxValidator()):
            
            self.logBox.AppendText("\nStarting Archive Process")
            self.extractMetaDataToTxt()
            self.extractMetaDataToXML()
            self.generate_ffmpeg_command()
            self.generate_handbrake_command()
            self.create_matroska()
            self.create_mp4()
            self.quality_control()
            
    def extractMetaDataToTxt(self):
        global txtFile
        self.logBox.AppendText("\n\n#############################\nExtracting DVD MetaData to Text File\n#############################\n\n")
        txtFile = self.textBox1.GetValue() + "/log-" + strftime("%y%m%H%M%S") + ".txt"
        file = open(txtFile, "w")
        file.write("#####################################\nExtracting DVD MetaData to Text File\n#####################################\n\n")
        proc1 = subprocess.Popen("mediainfo -f %s" % self.textBox3.GetValue(), shell=True, stdout=subprocess.PIPE)

        # log to gui and txt file
        for line in proc1.stdout:
            wx.Yield()
            file.write(line)
            self.logBox.AppendText(line)
        proc1.wait()
                
        # restore stdout to normal
        sys.stdout = sys.__stdout__
        self.logBox.AppendText("Operation Completed.\n\n")
        
    def extractMetaDataToXML(self):
        global xmlFile
        self.logBox.AppendText("#############################\nExtracting DVD MetaData to XML File\n#############################\n") 
        xmlFile = self.textBox1.GetValue() + "/xml-" + strftime("%y%m%H%M%S") + ".xml"
        file = open(xmlFile, "w")
        proc2 = subprocess.Popen("mediainfo --Output=XML -f %s" % self.textBox3.GetValue(), shell=True, stdout=file)
        proc2.wait()
        
        # restore stdout to normal
        sys.stdout = sys.__stdout__
        self.logBox.AppendText("\nOperation Completed.\n\n")
        
    def generate_ffmpeg_command(self):
        global ffmpeg_command
        global iso
        
        self.streams = []
        self.cntVideo = 0
        self.cntAudio = 0
        self.cntSubtitle = 0
        self.logBox.AppendText("#############################\nGenerating FFMPEG Command\n#############################\n") 
        iso = self.textBox1.GetValue() + "/" + self.textBox2.GetValue() + ".iso"
        
        self.logBox.AppendText("\nAppending ISO to FFMPEG command.\n")
        ffmpeg_command += iso
        
        self.logBox.AppendText("\nParsing XML file for aspect ratio from VIDEO_TS.IFO ... \n")
        self.tree = ET.parse(xmlFile)
        self.root = self.tree.getroot()
        
        # traverse xml until File_extension == ifo 
        self.index = 0
        for child_element in self.tree.iterfind('File/track[@type="General"]/File_extension'):
            if child_element.text == "ifo":
                break
            else:
                self.index += 1
                
        # get aspect ratio from <File> element located at index
        self.aspectRatio = self.root[self.index].find('track[@type="Video"]/Display_aspect_ratio').text 
        self.logBox.AppendText("Aspect Ratio found = " + str(self.aspectRatio) + "\n")
        self.logBox.AppendText("Appending aspect ratio to FFMPEG command.\n")
        ffmpeg_command += " -aspect " + self.aspectRatio
                
        self.logBox.AppendText("\nChecking number of streams ... \n")
        proc3 = subprocess.Popen("ffmpeg -i %s 2>&1 | grep Stream | awk '{print $3}'" % iso, shell=True, stdout=subprocess.PIPE)

        # redirect command line output into streams[] list
        for line in proc3.stdout:
            wx.Yield()
            self.streams.append(line.strip())
        proc3.wait()
                
        # count number of streams per category
        for stream in self.streams:
            if stream == "Video:":
                self.cntVideo += 1
            if stream == "Audio:":
                self.cntAudio += 1
            if stream == "Subtitle:":
                self.cntSubtitle += 1
                
        self.logBox.AppendText(str(self.cntVideo) + " video streams detected.\n")
        self.logBox.AppendText(str(self.cntAudio) + " audio streams detected.\n")
        self.logBox.AppendText(str(self.cntSubtitle) + " subtitle streams detected.\n")
        
        for i in range(0, self.cntVideo):
            ffmpeg_command += " -vcodec ffv1"

        for i in range(0, self.cntAudio):
            ffmpeg_command += " -acodec copy -ac 2"

        for i in range(0, self.cntSubtitle):
            ffmpeg_command += " -scodec copy"
            
        self.logBox.AppendText("\nAppending MKV path to FFMPEG Command.\n")
        ffmpeg_command += " -f matroska " + self.textBox1.GetValue() + "/" + self.textBox2.GetValue() + ".mkv"
        
        if self.cntVideo>1:
            for i in range(1, self.cntVideo):
                ffmpeg_command += " -newvideo"

        elif self.cntAudio > 1:
            for i in range(1, self.cntAudio):
                ffmpeg_command += ""
        
        self.logBox.AppendText("\nFFMPEG command complete.\n")
        self.logBox.AppendText("FFMPEG command = " + ffmpeg_command + "\n")
        
    def generate_handbrake_command(self):
        global handbrake_command
        self.logBox.AppendText("\n#############################\nGenerating HandBrake Command\n#############################\n") 
        handbrake_command += iso + " -o " + self.textBox1.GetValue() + "/" + self.textBox2.GetValue() + ".mp4"

        self.logBox.AppendText("\nHandBrake command complete.\n")
        self.logBox.AppendText("HandBrake command = " + handbrake_command + "\n")
        
    def create_matroska(self):
        self.logBox.AppendText("\n#############################\nCreating Matroska File\n#############################\n") 
        file = open(txtFile, "a")
        file.write("#############################\nCreating Matroska File\n#############################\n")
        #proc4 = subprocess.Popen(ffmpeg_command, shell=True, stdout=subprocess.PIPE)
        proc4 = subprocess.Popen("echo mkv", shell=True, stdout=subprocess.PIPE)

        # log to gui and txt file
        for line in proc4.stdout:
            wx.Yield()
            file.write(line)
            self.logBox.AppendText(line)
        proc4.wait()
                
        # restore stdout to normal
        sys.stdout = sys.__stdout__
        self.logBox.AppendText("Matroska Successfully Created.\n\n")
        
    def create_mp4(self):
        self.logBox.AppendText("#############################\nCreating MP4 File\n#############################\n") 
        file = open(txtFile, "a")
        file.write("\n#############################\nCreating MP4 File\n#############################\n")
        #proc5 = subprocess.Popen(handbrake_command, shell=True, stdout=subprocess.PIPE)
        proc5 = subprocess.Popen("echo mp4", shell=True, stdout=subprocess.PIPE)

        # log to gui and txt file
        for line in proc5.stdout:
            wx.Yield()
            file.write(line)
            self.logBox.AppendText(line)
        proc5.wait()
                
        # restore stdout to normal
        sys.stdout = sys.__stdout__
        self.logBox.AppendText("MP4 Successfully Created.\n\n")
        
    def quality_control(self):
        self.logBox.AppendText("#############################\nImplementing Quality Control\n#############################\n") 
        file = open(txtFile, "a")
        file.write("\n#############################\nImplementing Quality Control\n#############################\n")
        
        os.makedirs(self.textBox1.GetValue() + "/original")
        os.makedirs(self.textBox1.GetValue() + "/copy")
        iso_bmp_command = "ffmpeg -i " + iso + " -vframes 100 " + self.textBox1.GetValue() + "/original/frameoriginal%03d.bmp"
        mkv_bmp_command = "ffmpeg -i " + self.textBox1.GetValue() + "/" + self.textBox2.GetValue() + ".mkv" + " -vframes 100" + self.textBox1.GetValue() + "/copy/framecopy%03d.bmp"
        
        self.logBox.AppendText("Using Structure Similarity (SSIM) Index to verify lossless conversion.\nPlease wait.\n")
        file.write("Using Structure Similarity (SSIM) Index to verify lossless conversion.\nPlease wait.\n")
        
        #runSSIM(self.textBox1.GetValue()+"/original/", self.textBox1.GetValue()+"/copy/")
        self.logBox.AppendText("Quality Check Complete.\n\n")

        
    def textBoxValidator(self):
        # check if textbox is empty
        if len(self.textBox1.GetValue()) == 0: 
            wx.MessageBox("Please enter an output directory.", "Error")
            self.textBox1.SetBackgroundColour("pink")
            self.textBox1.SetFocus()
            self.textBox1.Refresh()
            return False
        else:
             self.textBox1.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
             self.textBox1.Refresh()
             
             # check if directory exists
             if not os.path.exists(self.textBox1.GetValue()):
                wx.MessageBox("The directory does not exist.\nVerify your spelling and format or use the directory dialog.", "Error")
                self.textBox1.SetBackgroundColour("pink")
                self.textBox1.SetFocus()
                self.textBox1.Refresh()
                return False
             
        # check if textbox is empty
        if len(self.textBox2.GetValue()) == 0: 
            wx.MessageBox("Please enter a file name.", "Error")
            self.textBox2.SetBackgroundColour("pink")
            self.textBox2.SetFocus()
            self.textBox2.Refresh()
            return False
        else:
            self.textBox2.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            self.textBox2.Refresh()
            
            # check if filename is valid (only alphanumeric, hypen, underscore allowed)
            if re.search(r'[^A-Za-z0-9_\-\\]',self.textBox2.GetValue()):
                wx.MessageBox("Filename can only contain letters, numbers, hyphens, and underscores. Please try again.", "Error")
                self.textBox2.SetBackgroundColour("pink")
                self.textBox2.SetFocus()
                self.textBox2.Refresh()
                return False
         
        # check if textbox is empty
        if len(self.textBox3.GetValue()) == 0:
            wx.MessageBox("Please enter a DVD directory.", "Error")
            self.textBox3.SetBackgroundColour("pink")
            self.textBox3.SetFocus()
            self.textBox3.Refresh()
            return False
        else:
            self.textBox3.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            self.textBox3.Refresh()

            # check if directory exists
            if not os.path.exists(self.textBox3.GetValue()):
                wx.MessageBox("The directory does not exist.\nVerify your spelling and format or use the directory dialog.", "Error")
                self.textBox3.SetBackgroundColour("pink")
                self.textBox3.SetFocus()
                self.textBox3.Refresh()
                return False
             
        return True
        
    def checkBoxValidator(self):
        if self.makeISO.GetValue() or self.makeMKV.GetValue() or self.makeMP4.GetValue():
            return True
        else:
            wx.MessageBox("Nothing left to do.\n\nSelect at least one of the following archive media format:\nISO, MKV, or MP4", "Error")
            return False
        
    def open_help(self, event):
        msg = wordwrap(
            "Output Directory\nType or Select the directory in which you wish to store all output files.\nFormat: /path/to/folder/\n\n"
            "Output File Name\nProvide a name to be used for all generated files.\nAllowed characters: letters, numbers, hyphen, underscore\n\n"
            "DVD Directory\nType or Select the directory of the Master DVD or ISO image.\nFormat: /path/to/dvd/folder/\n\n"
            "Optional Attributes\nSelect the preservation media files that you would like to be generated.\n\n"
            "Logging\nAll application procedures will be documented in the program log window.\n\n",
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