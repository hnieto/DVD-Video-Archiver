# DVD Video Archiver

![DVD Video Archiver](https://dl.dropboxusercontent.com/u/25652072/DVD-Video-Archiver.jpg)

These scripts automate the process that produces a submission information package (SIP) for archiving video art acquired originally in DVD format. For each DVD submitted to the application,
the resultant SIP can contain an ISO disk image, production quality matroska file, MP4 streaming file, and a log that records the technical metadata about the files and about the conversion processes involved. The project was elicited by the need of the Blanton Museum of Art at the University of Texas at Austin to find a file-based preservation solution to archive their video art collection 
in a high performance storage (HPC) resource at the [Texas Advanced Computing Center](http://www.tacc.utexas.edu/).

**IMPORTANT**  
This is still a work in progress. Please read this document in its entirety to get a complete understanding of what has and has not been implemented. Thank you.


## Setting Up

### Python

The scripts and corresponding python libraries have been packaged into a standalone `.app` Mac OS X application with the help of [py2app](http://wiki.python.org/moin/MacPython/py2app). The user does **not** have to worry about installing any Python modules or modifying their existing Python environment. 

### HandBrakeCLI

[HandbrakeCLI](http://handbrake.fr/downloads2.php) is a general-purpose, free, open-source, cross-platform, multithreaded video transcoder command-line tool. This application requires HandBrakeCLI to convert an ISO to a streaming MP4 file. Once installed, HandBrakeCLI must also be added to your $PATH. To do so, 

* Open a terminal window (Applications > Utilities > Terminal)   
* Edit your `.profile` with your favorite editor (ie. run `vi ~/.profile`)    
* find the line that starts with `export PATH=` and change it to `export PATH=/folder/containing/handbrakecli/:$PATH`  
* close your editor (if using vi, type `:wq!`)   
* reload your `.profile` by running `source ~/.profile`  
* verify your changes by running `echo $PATH`  
* finally, type `HandBrakeCLI --help`. If you see the help options for HandBrakeCLI, then you've successfully setup the tool   

**IMPORTANT**   
If you are using Mac OS X 10.5, download HandBrakeCLI from [here](http://sourceforge.net/projects/handbrake/files/0.9.5/HandBrake-0.9.5-MacOSX.5_CLI_x86_64.dmg/download) instead.

### FFMPEG

[FFMPEG](http://ffmpeg.org/ffmpeg.html) is a cross-platform solution to record, convert and stream audio and video. This application uses FFMPEG to convert an ISO to an MKV high quality container. There are serveral ways you can install FFMPEG. You can either download the source and compile it yourself or use a package manager like [Homebrew](http://mxcl.github.io/homebrew/) to take care of the installation for you. Both of these options are described in [here](http://ffmpeg.org/trac/ffmpeg/wiki/MacOSXCompilationGuide).

### MediaInfo

[MediaInfo](http://mediainfo.sourceforge.net/en/Download/Mac_OS) is a free and open-source program that displays technical information about media files. This application uses MediaInfo to extract information from a DVD into a TXT and XML file. This metadata is later parsed for specific technical information and used to generate the FFMPEG command that will ultimately create an MKV container. MediaInfo can be downloaded as a `.dmg` from the link above and then installed by following the on-screen instructions.


## How To Run

Once `dvdArchiver.zip` has been extracted, you can run the application in one of the following two ways:

### From Terminal 
Open a terminal window (Applications > Utilities > Terminal) and run:   
	`./path/to/extracted/program/dvdArchiver.app/Contents/MacOS/dvdArchiver`

### Double Click
You can also launch the application by double-clicking on it.   

**WARNING**   
This is buggy. The GUI will open but the command line calls for MediaInfo, FFMPEG, and HandBrakeCLI do not get executed. I will work on gettting this fixed ASAP but in the meantime just run the application directly from the terminal.


## Usage   

This appliction allows the user to create up to three different preservation files during one execution cycle. Our program will create a separate folder under the output directory specified by the user for each preservation type it creates and its corresponding metadata files. MediaInfo will extract metadata into TXT and XML for both the original file and the generated preservation file. Timestamps are added to the end of each TXT file for logging purposes. The following sections will describe which files can be created and how.

### Create ISO

Make sure your DVD is mounted. Check the `Create ISO` option and fill in the following text boxes in the GUI:
* Output Directory  
* Output File Name  
* DVD Directory  

The `dd` command line utility is then used to create an ISO disk image from the DVD. An MD5 and SHA-1 checksum are produced once the ISO has been created. The `ISO FIle` text box will be disabled since this information will not be used during the ISO creation process.    

**IMPORTANT**   
If the master DVD is encrypted, `libdvdread` and `libdvdcss` must be installed before attempting to produce a SIP using this application. You can download the `libdvdcss.pkg` from [here](http://download.videolan.org/pub/videolan/libdvdcss/1.2.11/macosx/). This application is only intended to be used with legally purchased DVDs.  

### Create MKV

To convert from an ISO disc image to an MKV container, select `Create Matroska` from the `Preservation Media Types` section and fill in the following text boxes:    
* Output Directory    
* Output File Name   
* ISO File   

Our software will automatically mount the ISO file and then MediaInfo will extract the DVD metadata and create an XML file. FFMPEG will then use this technical data and `ISO File` to generate a Matroska file more accurately. An MD5 and SHA-1 checksum are produced once the MKV has been created. If the "Create ISO" option was selected along with "Create MKV", the ISO generated by our software will then be used to create the MKV.

### Create MP4

To convert from an ISO to a streaming MP4 file, select `Create MP4` from the `Preservation Media Types` section and fill in the following text boxes:   
* Output Directory        
* Output File Name   
* ISO File

If the "Create ISO" option was selected along with "Create MP4", the ISO generated by our software will then be used to create the MP4.


## SSIM

In order to ensure that the preservation master copy has been transcoded correctly, a video quality metric is used to compare the original disk image to the preservation file. The SSIM implementation compares a single image file and produces a measurement between -1 and 1. If the SSIM Index is 1, the reference file and copy are identical, which is what we aim for in this step. For lossy conversion, anything below 1 indicates a loss in quality from the original file. In our workflow, the measurement is averaged between the SSIM index of 100 frames.


## XML File Format

```
<Mediainfo version="0.7.59">
	<File>
		<track type="General">
			...
			file name, file type, etc
			...
		</track>

		<track type="Video">
			...
			aspect ratio, bit rate, frame rate, etc
			...
		</track>

		<track type="Text">
			...
			format, codec, etc
			...
		</track>
	</File>
</Mediainfo>
```


## Requirements

* [MediaInfo](http://mediainfo.sourceforge.net/en)
* [FFMPEG](http://ffmpeg.org/ffmpeg.html)
* [HandBrakeCLI](https://trac.handbrake.fr/wiki/CLIGuide)

**IMPORTANT**   
The installation directory of the these three programs is independent of this application.


## To Do

* Parallelize the workflow to take advantage of HPC system resources for large video collections
* Improve logging to facilitate metadata comparison 
