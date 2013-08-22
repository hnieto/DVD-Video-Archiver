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
from datetime import datetime
import xml.etree.ElementTree as ET
from ssim import runSSIM

iso = ""
mount_dir = ""
dd_command = ""
ffmpeg_command = "ffmpeg -i "
handbrake_command = "HandBrakeCLI --main-feature -e x264  -q 20.0 -a -E faac -B 160 -6 dpl2 -R Auto -D 0.0 -f mp4 -O --strict-anamorphic -m -x ref=1:weightp=1:subq=2:rc-lookahead=10:trellis=0:8x8dct=0 -i "

class Archiver(wx.Frame):

    def __init__(self, parent, title):    
        super(Archiver, self).__init__(parent, title=title, size=(500, 660), style=wx.CLOSE_BOX) # close_box prevents resizing

        self.InitUI()
        self.Centre()
        self.Show()     

    def InitUI(self):
      
        self.panel = wx.Panel(self)
        
        self.gridSizer = wx.GridBagSizer(5, 5)

        # header
        self.label1 = wx.StaticText(self.panel, label="DVD Video Archiver")
        self.gridSizer.Add(self.label1, pos=(0, 0), flag=wx.TOP|wx.LEFT|wx.BOTTOM, border=15)

        self.icon = wx.StaticBitmap(self.panel, bitmap=wx.Bitmap(os.path.join(os.path.dirname(__file__), 'icon.png')))
        self.gridSizer.Add(self.icon, pos=(0, 4), flag=wx.TOP|wx.RIGHT|wx.ALIGN_RIGHT, border=5)

        self.divider = wx.StaticLine(self.panel)
        self.gridSizer.Add(self.divider, pos=(1, 0), span=(1, 5), flag=wx.EXPAND|wx.BOTTOM, border=10)

        # text boxes
        self.label2 = wx.StaticText(self.panel, label="Output Directory")
        self.gridSizer.Add(self.label2, pos=(2, 0), flag=wx.LEFT|wx.TOP, border=10)

        self.textBox1 = wx.TextCtrl(self.panel)
        self.gridSizer.Add(self.textBox1, pos=(2, 1), span=(1, 3), flag=wx.TOP|wx.EXPAND, border=5)
        
        self.button1 = wx.Button(self.panel, label="Browse...")
        self.gridSizer.Add(self.button1, pos=(2, 4), flag=wx.TOP|wx.RIGHT, border=5)

        self.label3 = wx.StaticText(self.panel, label="Output File Name")
        self.gridSizer.Add(self.label3, pos=(3, 0), flag=wx.LEFT|wx.TOP, border=10)

        self.textBox2 = wx.TextCtrl(self.panel)
        self.gridSizer.Add(self.textBox2, pos=(3, 1), span=(1, 3), flag=wx.TOP|wx.EXPAND, border=5)

        self.label4 = wx.StaticText(self.panel, label="DVD Directory")
        self.gridSizer.Add(self.label4, pos=(4, 0), flag=wx.TOP|wx.LEFT, border=10)
        
        self.textBox3 = wx.TextCtrl(self.panel)
        self.gridSizer.Add(self.textBox3, pos=(4, 1), span=(1, 3), flag=wx.TOP|wx.EXPAND, border=5)
        
        self.button2 = wx.Button(self.panel, label="Browse...")
        self.gridSizer.Add(self.button2, pos=(4, 4), flag=wx.TOP|wx.RIGHT, border=5)
        
        self.label5 = wx.StaticText(self.panel, label="ISO File")
        self.gridSizer.Add(self.label5, pos=(5, 0), flag=wx.TOP|wx.LEFT, border=10)
        
        self.textBox4 = wx.TextCtrl(self.panel)
        self.gridSizer.Add(self.textBox4, pos=(5, 1), span=(1, 3), flag=wx.TOP|wx.EXPAND, border=5)
        
        self.button3 = wx.Button(self.panel, label="Browse...")
        self.gridSizer.Add(self.button3, pos=(5, 4), flag=wx.TOP|wx.RIGHT, border=5)

        # check boxes
        self.staticBox = wx.StaticBox(self.panel, label="Preservation File Types")
        self.boxSizer = wx.StaticBoxSizer(self.staticBox, wx.VERTICAL)
        self.makeISO = wx.CheckBox(self.panel, label="Create ISO")
        self.makeMKV = wx.CheckBox(self.panel, label="Create Matroska")
        self.makeMP4 = wx.CheckBox(self.panel, label="Create MP4")
        self.boxSizer.Add(self.makeISO, flag=wx.LEFT|wx.TOP, border=5)
        self.boxSizer.Add(self.makeMKV, flag=wx.LEFT, border=5)
        self.boxSizer.Add(self.makeMP4,flag=wx.LEFT, border=5)
        self.boxSizer.Add((0,10), 0)
        self.gridSizer.Add(self.boxSizer, pos=(7, 0), span=(1, 5), flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)
        
        # logging
        self.logBox = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.logBox.AppendText("Waiting on user ...")
        self.gridSizer.Add(self.logBox, pos=(9, 0), span=(9, 5), flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT , border=10)

        # control buttons
        self.about = wx.Button(self.panel, label='About')
        self.gridSizer.Add(self.about, pos=(19, 0), flag=wx.LEFT, border=10)
        
        self.help = wx.Button(self.panel, label='Help')
        self.gridSizer.Add(self.help, pos=(19, 1), flag=wx.LEFT, border=-50)

        self.archive = wx.Button(self.panel, label="Archive")
        self.gridSizer.Add(self.archive, pos=(19, 4), span=(1,1), flag=wx.BOTTOM|wx.RIGHT, border=5)

        self.gridSizer.AddGrowableCol(2)
        
        self.panel.SetSizer(self.gridSizer)
        
        # event handling
        self.button1.Bind(wx.EVT_BUTTON, self.get_output_dir)
        self.button2.Bind(wx.EVT_BUTTON, self.get_dvd_dir)
        self.button3.Bind(wx.EVT_BUTTON, self.get_iso_file)
        self.makeISO.Bind(wx.EVT_CHECKBOX, self.toggle_visibility)
        self.makeMKV.Bind(wx.EVT_CHECKBOX, self.toggle_visibility)
        self.makeMP4.Bind(wx.EVT_CHECKBOX, self.toggle_visibility)
        self.about.Bind(wx.EVT_BUTTON, self.open_about)
        self.help.Bind(wx.EVT_BUTTON, self.open_help)
        self.archive.Bind(wx.EVT_BUTTON, self.run_app)
                
    def run_app(self, event):           
        # validate GUI inputs
        if self.validator():
            self.logBox.AppendText("\nStarting Archive Process\n")

            if self.makeISO.GetValue():
                start_time1 = datetime.now()
                self.logBox.AppendText("\nCREATING ISO\n")
                os.makedirs(self.textBox1.GetValue() + "/iso")
                self.extract_dvd_metadata_xml(self.textBox1.GetValue() + "/iso/dvd.xml", "\"" + self.textBox3.GetValue() + "\"") 
                self.extract_dvd_metadata_txt(self.textBox1.GetValue() + "/iso/dvd.txt", "\"" + self.textBox3.GetValue() + "\"")
                self.generate_dd_command()
                self.create_iso()
                self.extract_iso_metadata_xml(self.textBox1.GetValue() + "/iso/iso.xml") 
                self.extract_iso_metadata_txt(self.textBox1.GetValue() + "/iso/iso.txt")
                self.logBox.AppendText(" Time Elapsed = " + str(datetime.now()-start_time1) + "\n")
                            
            if self.makeMKV.GetValue():
                start_time2 = datetime.now()
                self.logBox.AppendText("\nCREATING MKV\n")
                os.makedirs(self.textBox1.GetValue() + "/mkv")
                dvdPath = self.mount_iso()
                self.extract_dvd_metadata_xml(self.textBox1.GetValue() + "/mkv/dvd.xml", dvdPath)
                self.extract_dvd_metadata_txt(self.textBox1.GetValue() + "/mkv/dvd.txt", dvdPath)
                self.extract_iso_metadata_xml(self.textBox1.GetValue() + "/mkv/iso.xml") 
                self.extract_iso_metadata_txt(self.textBox1.GetValue() + "/mkv/iso.txt") 
                self.generate_ffmpeg_command(self.textBox1.GetValue() + "/mkv/dvd.xml")
                self.create_matroska()
                self.extract_mkv_metadata_xml(self.textBox1.GetValue() + "/mkv/mkv.xml", self.textBox1.GetValue() + "/mkv/" + self.textBox2.GetValue() + ".mkv") 
                self.extract_mkv_metadata_txt(self.textBox1.GetValue() + "/mkv/mkv.txt", self.textBox1.GetValue() + "/mkv/" + self.textBox2.GetValue() + ".mkv")
                self.quality_control()
                self.unmount_iso(dvdPath)
                self.logBox.AppendText(" Time Elapsed = " + str(datetime.now()-start_time2) + "\n")
                
            if self.makeMP4.GetValue():
                start_time3 = datetime.now()
                self.logBox.AppendText("\nCREATING MP4\n")
                os.makedirs(self.textBox1.GetValue() + "/mp4")
                self.extract_iso_metadata_xml(self.textBox1.GetValue() + "/mp4/iso.xml") 
                self.extract_iso_metadata_txt(self.textBox1.GetValue() + "/mp4/iso.txt") 
                self.generate_handbrake_command()
                self.create_mp4()
                self.extract_mp4_metadata_xml(self.textBox1.GetValue() + "/mp4/mp4.xml", self.textBox1.GetValue() + "/mp4/" + self.textBox2.GetValue() + ".mp4") 
                self.extract_mp4_metadata_txt(self.textBox1.GetValue() + "/mp4/mp4.txt", self.textBox1.GetValue() + "/mp4/" + self.textBox2.GetValue() + ".mp4")
                self.logBox.AppendText(" Time Elapsed = " + str(datetime.now()-start_time3) + "\n")
            
            # save GUI log to txt file
            self.logBox.SaveFile(self.textBox1.GetValue() + "/log.txt")
            self.logFile = open(self.textBox1.GetValue() + "/log.txt", 'a')
            self.logFile.write("\n" + strftime("%b %d %Y %H:%M:%S"))  
            self.logFile.close()
            
            self.logBox.AppendText("\nPROGRAM COMPLETE\n")

            
    def extract_dvd_metadata_xml(self, filePath, dvdPath):
        file = open(filePath, "w")
        
        #log to GUI
        self.logBox.AppendText(" Extracting DVD MetaData to XML File\n")
        
        # log to file
        subprocess.call("mediainfo --Output=XML -f %s 2>&1" % dvdPath, shell=True, stdout=file)
        file.close()
        
        # restore stdout to normal
        sys.stdout = sys.__stdout__
        
    def extract_dvd_metadata_txt(self, filePath, dvdPath):
        file = open(filePath, "w")
        
        #log to GUI
        self.logBox.AppendText(" Extracting DVD MetaData to TEXT File\n")
        
        # log to file
        file.write(strftime("%b %d %Y %H:%M:%S"))       
        subprocess.call("mediainfo -f %s 2>&1" % dvdPath, shell=True, stdout=file)
        
        file.close()
        
        # restore stdout to normal
        sys.stdout = sys.__stdout__
        
    ''' used to convert DVD to iso '''
    def generate_dd_command(self):
        global dd_command
        global mount_dir
        
        self.logBox.AppendText(" Generating DD Utility Command\n")
        
        # find mount directory for DVD
        cmd = "mount | grep " + "\"" + self.textBox3.GetValue() + "\"" + " | awk '{print $1}'"
        p1 = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        mount_dir = p1.stdout.read().rstrip('\n')
        
        # construct dd_command using mount point found above
        dd_command = "dd if=" + mount_dir + " of=" + self.textBox1.GetValue() + "/iso/" + self.textBox2.GetValue() + ".iso 2>&1"
        
        self.logBox.AppendText("  DD command complete.\n")
        self.logBox.AppendText("  DD command = " + dd_command + "\n")
        
    def create_iso(self):  
        global iso 
              
        self.logBox.AppendText(" Unmounting DVD.\n")
        unmount = subprocess.Popen("diskutil unmountDisk " + mount_dir + " 2>&1", shell=True, stdout=subprocess.PIPE)
        
        # log to wxTextCtrl
        for line in unmount.stdout:
            wx.Yield()
            self.logBox.AppendText("  " + line)
        unmount.wait()
        
        self.logBox.AppendText(" Launch DD Utility Command\n")
        
        dd = subprocess.Popen(dd_command, shell=True, stdout=subprocess.PIPE)
        
        # log to wxTextCtrl
        for line in dd.stdout:
            wx.Yield()
            self.logBox.AppendText("  " + line)
        dd.wait()
        
        self.logBox.AppendText("  ISO Successfully Created.\n")
        iso = self.textBox1.GetValue() + "/iso/" + self.textBox2.GetValue() + ".iso"
        
        self.logBox.AppendText(" Creating MD5 checksum.\n")
        md5_command = "openssl md5 " + self.textBox1.GetValue() + "/iso/" + self.textBox2.GetValue() + ".iso 2>&1"
        md5 = subprocess.Popen(md5_command, shell=True, stdout=subprocess.PIPE)

        # log to gui and txt file
        for line in md5.stdout:
            wx.Yield()
            self.logBox.AppendText("  " + line)
        md5.wait()
        
        self.logBox.AppendText(" Creating SHA-1 checksum.\n")
        sha1_command = "openssl sha1 " + self.textBox1.GetValue() + "/iso/" + self.textBox2.GetValue() + ".iso 2>&1"
        sha1 = subprocess.Popen(sha1_command, shell=True, stdout=subprocess.PIPE)

        # log to wxTextCtrl
        for line in sha1.stdout:
            wx.Yield()
            self.logBox.AppendText("  " + line)
        sha1.wait()
               
        # restore stdout to normal
        sys.stdout = sys.__stdout__
        
    def extract_iso_metadata_xml(self, filePath):
        file = open(filePath, "w")
        
        #log to GUI
        self.logBox.AppendText(" Extracting ISO MetaData to XML File\n")
        
        # log to file
        file.write(strftime("%b %d %Y %H:%M:%S"))       
        subprocess.call("mediainfo --Output=XML -f %s 2>&1" % iso, shell=True, stdout=file)
        
        file.close()
        
        # restore stdout to normal
        sys.stdout = sys.__stdout__
        
    def extract_iso_metadata_txt(self, filePath):
        file = open(filePath, "w")
        
        #log to GUI
        self.logBox.AppendText(" Extracting ISO MetaData to TEXT File\n")
        
        # log to file
        file.write(strftime("%b %d %Y %H:%M:%S"))     
        subprocess.call("mediainfo -f %s 2>&1" % iso, shell=True, stdout=file)
        
        file.close()
        
        # restore stdout to normal
        sys.stdout = sys.__stdout__
        
    def mount_iso(self):
        cmd = "hdiutil mount " + iso + " | awk '{print $2}'"
        p1 = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        return p1.stdout.read().rstrip('\n')
        
    ''' used to convert iso to mkv '''
    def generate_ffmpeg_command(self, xmlFile):
        global ffmpeg_command
        
        self.streams = []
        self.cntVideo = 0
        self.cntAudio = 0
        self.cntSubtitle = 0
        
        self.logBox.AppendText(" Generating FFMPEG Command\n") 
        self.logBox.AppendText("  Appending ISO to FFMPEG command.\n")
        ffmpeg_command += iso
        
        self.logBox.AppendText("  Parsing XML file for aspect ratio from VIDEO_TS.IFO ... \n")
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
        self.logBox.AppendText("   Aspect Ratio found = " + str(self.aspectRatio) + "\n")
        self.logBox.AppendText("   Appending aspect ratio to FFMPEG command.\n")
        ffmpeg_command += " -aspect " + self.aspectRatio
                
        self.logBox.AppendText("  Checking number of streams ... \n")
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
        
        self.logBox.AppendText("   " + str(self.cntVideo) + " video streams detected.\n")
        self.logBox.AppendText("   " + str(self.cntAudio) + " audio streams detected.\n")
        self.logBox.AppendText("   " + str(self.cntSubtitle) + " subtitle streams detected.\n")
        
        for i in range(0, self.cntVideo):
            ffmpeg_command += " -vcodec ffv1"

        for i in range(0, self.cntAudio):
            ffmpeg_command += " -acodec copy -ac 2"

        for i in range(0, self.cntSubtitle):
            ffmpeg_command += " -scodec copy"
            
        self.logBox.AppendText("  Appending MKV path to FFMPEG Command.\n")
        ffmpeg_command += " -f matroska " + self.textBox1.GetValue() + "/mkv/" + self.textBox2.GetValue() + ".mkv"
        
        if self.cntVideo>1:
            for i in range(1, self.cntVideo):
                ffmpeg_command += " -newvideo"

        elif self.cntAudio > 1:
            for i in range(1, self.cntAudio):
                ffmpeg_command += ""
                
        ffmpeg_command += " 2>&1"
        self.logBox.AppendText("  FFMPEG command complete.\n")
        self.logBox.AppendText("  FFMPEG command = " + ffmpeg_command + "\n")
                
        # restore stdout to normal
        sys.stdout = sys.__stdout__
        
    def create_matroska(self):
        self.logBox.AppendText(" Creating Matroska File\n") 
        
        proc4 = subprocess.Popen(ffmpeg_command, shell=True, stdout=subprocess.PIPE)

        # log to gui and txt file
        for line in proc4.stdout:
            wx.Yield()
            self.logBox.AppendText("  " + line)
        proc4.wait()
                
        self.logBox.AppendText("  Matroska Successfully Created.\n")
        
        self.logBox.AppendText(" Creating MD5 checksum.\n")
        md5_command = "openssl md5 " + self.textBox1.GetValue() + "/" + self.textBox2.GetValue() + ".mkv 2>&1"
        md5 = subprocess.Popen(md5_command, shell=True, stdout=subprocess.PIPE)

        # log to gui and txt file
        for line in md5.stdout:
            wx.Yield()
            self.logBox.AppendText("  " + line)
        md5.wait()
        
        self.logBox.AppendText(" Creating SHA-1 checksum.\n")
        sha1_command = "openssl sha1 " + self.textBox1.GetValue() + "/" + self.textBox2.GetValue() + ".mkv 2>&1"
        sha1 = subprocess.Popen(sha1_command, shell=True, stdout=subprocess.PIPE)

        # log to gui and txt file
        for line in sha1.stdout:
            wx.Yield()
            self.logBox.AppendText("  " + line)
        sha1.wait()        
        
        # restore stdout to normal
        sys.stdout = sys.__stdout__
        
    def extract_mkv_metadata_xml(self, filePath, mkvPath):
        file = open(filePath, "w")
        
        #log to GUI
        self.logBox.AppendText(" Extracting MKV MetaData to XML File\n")
        
        # log to file
        file.write(strftime("%b %d %Y %H:%M:%S"))       
        subprocess.call("mediainfo --Output=XML -f %s 2>&1" % mkvPath, shell=True, stdout=file)
        
        file.close()
        
        # restore stdout to normal
        sys.stdout = sys.__stdout__
        
    def extract_mkv_metadata_txt(self, filePath, mkvPath):
        file = open(filePath, "w")
        
        #log to GUI
        self.logBox.AppendText(" Extracting MKV MetaData to TEXT File\n")
        
        # log to file
        file.write(strftime("%b %d %Y %H:%M:%S"))       
        subprocess.call("mediainfo -f %s 2>&1" % mkvPath, shell=True, stdout=file)
        
        file.close()
        
        # restore stdout to normal
        sys.stdout = sys.__stdout__
        
    def quality_control(self):
        self.logBox.AppendText(" Implementing Quality Control on MKV\n")
        
        os.makedirs(self.textBox1.GetValue() + "/mkv/original")
        os.makedirs(self.textBox1.GetValue() + "/mkv/copy")
        iso_bmp_command = "ffmpeg -i " + iso + " -vframes 100 " + self.textBox1.GetValue() + "/mkv/original/frameoriginal%03d.bmp 2>&1"
        mkv_bmp_command = "ffmpeg -i " + self.textBox1.GetValue() + "/mkv/" + self.textBox2.GetValue() + ".mkv" + " -vframes 100 " + self.textBox1.GetValue() + "/mkv/copy/framecopy%03d.bmp 2>&1"
        
        self.logBox.AppendText("  Running command: " + iso_bmp_command + "\n")
        proc6 = subprocess.Popen(iso_bmp_command, shell=True, stdout=subprocess.PIPE)
        
        # log to gui and txt file
        for line in proc6.stdout:
            wx.Yield()
            self.logBox.AppendText("   " + line)
        proc6.wait()
        
        # restore stdout to normal
        sys.stdout = sys.__stdout__

        self.logBox.AppendText("  Running command: " + mkv_bmp_command + "\n")
        proc7 = subprocess.Popen(mkv_bmp_command, shell=True, stdout=subprocess.PIPE)
        
        # log to gui and txt file
        for line in proc7.stdout:
            wx.Yield()
            self.logBox.AppendText("   " + line)
        proc7.wait()
        
        # restore stdout to normal
        sys.stdout = sys.__stdout__
        
        self.logBox.AppendText("  Using Structure Similarity (SSIM) Index to verify lossless conversion.\n  Please wait.\n")
        
        (averageSSIM, standardDeviation) = runSSIM(self.textBox1.GetValue()+"/mkv/original/", self.textBox1.GetValue()+"/mkv/copy/")
        self.logBox.AppendText("   Average SSIM = " + str(averageSSIM) + "\n")
        self.logBox.AppendText("   Standard Deviation = " + str(standardDeviation) + "\n")

        self.logBox.AppendText("  Removing temporary folders.\n")        
        subprocess.call(['rm','-r',self.textBox1.GetValue() + '/mkv/original'])
        subprocess.call(['rm','-r',self.textBox1.GetValue() + '/mkv/copy'])
        
        self.logBox.AppendText("  Quality Check Complete.\n\n")
        
    def unmount_iso(self, dvdPath):
        # find mount directory for DVD
        cmd = "mount | grep " + dvdPath + " | awk '{print $1}'"
        p1 = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        mounting_point = p1.stdout.read().rstrip('\n')
        
        self.logBox.AppendText(" Unmounting DVD.\n")
        unmount = subprocess.Popen("diskutil unmountDisk " + mounting_point + " 2>&1", shell=True, stdout=subprocess.PIPE)
        
        # log to wxTextCtrl
        for line in unmount.stdout:
            wx.Yield()
            self.logBox.AppendText("  " + line)
        unmount.wait()
                
    ''' used to convert iso to mp4 '''
    def generate_handbrake_command(self):
        global handbrake_command
        
        self.logBox.AppendText(" Generating HandBrake Command\n") 
        handbrake_command += iso + " -o " + self.textBox1.GetValue() + "/mp4/" + self.textBox2.GetValue() + ".mp4 2>&1"

        self.logBox.AppendText("  HandBrake command complete.\n")
        self.logBox.AppendText("  HandBrake command = " + handbrake_command + "\n")
                
    def create_mp4(self):
        self.logBox.AppendText(" Creating MP4 File\n") 
        proc5 = subprocess.Popen(handbrake_command, shell=True, stdout=subprocess.PIPE)

        # log to wxTextCtrl
        for line in proc5.stdout:
            wx.Yield()
            self.logBox.AppendText("  " + line)
        proc5.wait()
                
        self.logBox.AppendText("  MP4 Successfully Created.\n\n")
                
        # restore stdout to normal
        sys.stdout = sys.__stdout__
        
    def extract_mp4_metadata_xml(self, filePath, mp4Path):
        file = open(filePath, "w")
        
        #log to GUI
        self.logBox.AppendText(" Extracting MP4 MetaData to XML File\n")
        
        # log to file
        file.write(strftime("%b %d %Y %H:%M:%S"))       
        subprocess.call("mediainfo --Output=XML -f %s 2>&1" % mp4Path, shell=True, stdout=file)
        
        file.close()
        
        # restore stdout to normal
        sys.stdout = sys.__stdout__
        
    def extract_mp4_metadata_txt(self, filePath, mp4Path):
        file = open(filePath, "w")
        
        #log to GUI
        self.logBox.AppendText(" Extracting MP4 MetaData to TEXT File\n")
        
        # log to file
        file.write(strftime("%b %d %Y %H:%M:%S"))       
        subprocess.call("mediainfo -f %s 2>&1" % mp4Path, shell=True, stdout=file)
        
        file.close()
        
        # restore stdout to normal
        sys.stdout = sys.__stdout__
        
    def validator(self):
        if not self.makeISO.GetValue() and not self.makeMKV.GetValue() and not self.makeMP4.GetValue():
            wx.MessageBox("Nothing left to do.\n\nSelect at least one of the following archive media format:\nISO, MKV, or MP4", "Error")
            self.textBox1.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            self.textBox1.Refresh()
            self.textBox2.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            self.textBox2.Refresh()
            self.textBox3.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            self.textBox3.Refresh()
            self.textBox4.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            self.textBox4.Refresh()
            return False
        else:
            if self.makeISO.GetValue():
                if self.validate_output_dir() and self.validate_output_file_name() and self.validate_dvd_dir():
                    return True
                else:
                    return False
                
            elif not self.makeISO.GetValue() and (self.makeMKV.GetValue() or self.makeMP4.GetValue()):
                if self.validate_output_dir() and self.validate_output_file_name() and self.validate_iso_file():
                    return True
                else:
                    return False
                
    def validate_output_dir(self):
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
            if not os.path.exists("%s" % self.textBox1.GetValue()):
                wx.MessageBox("The directory does not exist.\nVerify your spelling and format or use the directory dialog.", "Error")
                self.textBox1.SetBackgroundColour("pink")
                self.textBox1.SetFocus()
                self.textBox1.Refresh()
                return False
            else:
                return True
            
    def validate_output_file_name(self):
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
            else:
                return True
            
    def validate_dvd_dir(self):
        # check if textbox is empty
        if len(self.textBox3.GetValue()) == 0:
            wx.MessageBox("Please enter a DVD directory. If you're using an ISO instead of a physical DVD, be sure to mount it first.", "Error")
            self.textBox3.SetBackgroundColour("pink")
            self.textBox3.SetFocus()
            self.textBox3.Refresh()
            return False
        else:
            self.textBox3.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            self.textBox3.Refresh()

            # check if directory exists
            if not os.path.exists("%s" % self.textBox3.GetValue()):
                wx.MessageBox("The directory does not exist.\nVerify your spelling and format or use the directory dialog.", "Error")
                self.textBox3.SetBackgroundColour("pink")
                self.textBox3.SetFocus()
                self.textBox3.Refresh()
                return False
            else:
                return True
            
    def validate_iso_file(self):
        global iso # update iso var after validating it's path
  
        # check if textbox is empty
        if len(self.textBox4.GetValue()) == 0:
            wx.MessageBox("Please select a .iso file. It is required to create MKV or MP4.", "Error")
            self.textBox4.SetBackgroundColour("pink")
            self.textBox4.SetFocus()
            self.textBox4.Refresh()
            return False
        else:
            self.textBox4.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
            self.textBox4.Refresh()

            # check if directory exists
            if not os.path.exists(self.textBox4.GetValue()):
                wx.MessageBox("The iso file does not exist.\nVerify your spelling and format or use the directory dialog.", "Error")
                self.textBox4.SetBackgroundColour("pink")
                self.textBox4.SetFocus()
                self.textBox4.Refresh()
                return False
            else:
                iso = self.textBox4.GetValue()
                return True
        
    def open_help(self, event):
        msg = wordwrap(
            "Output Directory\nType or Select the directory in which you wish to store all output files.\nFormat: /path/to/folder/\n\n"
            "Output File Name\nProvide a name to be used for all generated files.\nAllowed characters: letters, numbers, hyphen, underscore\n\n"
            "DVD Directory\nType or Select the directory of the Master DVD.\nFormat: /path/to/dvd/folder/\n\n"
            "ISO File\nType or Select the directory of the ISO file if creating MKV or MP4.\nFormat: /path/to/iso/file/\n\n"
            "Preservation Media Types\nSelect the preservation media files that you would like to be generated.\n\n"
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
        
    def get_iso_file(self, event):
        dlg = wx.FileDialog(self, "", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dlg.ShowModal() == wx.ID_OK:
            self.selectedPath = dlg.GetPath()
            self.textBox4.SetValue(self.selectedPath)
        dlg.Destroy()
        
    def toggle_visibility(self, event):
        if self.makeISO.GetValue() and not self.makeMKV.GetValue() and not self.makeMP4.GetValue():
            # hide iso txt box and browse button
            self.button3.Hide()
            self.textBox4.SetValue("")
            self.textBox4.SetEditable(False)
            self.textBox4.SetBackgroundColour((220,220,220))
            
        elif self.makeISO.GetValue() and (self.makeMKV.GetValue() or self.makeMP4.GetValue()):
            # show dvd txt box and browse button
            self.button2.Show()
            self.textBox3.SetEditable(True)
            self.textBox3.SetBackgroundColour((255,255,255))
            
            # hide iso txt box and browse button
            # will use generated iso for mkv/mp4 conversion
            self.button3.Hide()
            self.textBox4.SetValue("")
            self.textBox4.SetEditable(False)
            self.textBox4.SetBackgroundColour((220,220,220))
            
        elif not self.makeISO.GetValue() and (self.makeMKV.GetValue() or self.makeMP4.GetValue()):
            # show iso txt box and browse button
            self.button3.Show()
            self.textBox4.SetEditable(True)
            self.textBox4.SetBackgroundColour((255,255,255))
            
            # hide dvd txt box and browse button 
            # will mount iso to extract metadata
            self.button2.Hide()
            self.textBox3.SetValue("")
            self.textBox3.SetEditable(False)
            self.textBox3.SetBackgroundColour((220,220,220))
    
        else:
            # show iso txt box and browse button
            self.button3.Show()
            self.textBox4.SetEditable(True)
            self.textBox4.SetBackgroundColour((255,255,255))
            
            # show dvd txt box and browse button
            self.button2.Show()
            self.textBox3.SetEditable(True)
            self.textBox3.SetBackgroundColour((255,255,255))

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