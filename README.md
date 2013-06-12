# DVD Video Archiver

![DVD Video Archiver](https://dl.dropboxusercontent.com/u/25652072/DVD-Video-Archiver.jpg)

These scripts automate the process that produces a submission information package (SIP) for archiving video art acquired originally in DVD format. For each DVD submitted to the application,
the resultant SIP can contain an ISO disk image, production quality matroska file, MP4 streaming file, and a log that records the technical metadata about the files and about the conversion processes involved. The project was elicited by the need of the Blanton Museum of Art at the University of Texas at Austin to find a file-based preservation solution to archive their video art collection 
in a high performance storage (HPC) resource at the [Texas Advanced Computing Center](http://www.tacc.utexas.edu/).

**IMPORTANT**  
This is still a work in progress. Please read this document in its entirety to get a complete understanding of what has and has not been implemented. Thank you.


## High-Level Procedure Description

The process is launched by opening a terminal (Applications > Utilities > Terminal) and running the following command:
	`cd /Path/To/DVD/Archiver/ && python dvdArchiver.py`


The script will extract the DVD's technical information using [MediaInfo](http://mediainfo.sourceforge.net/en). The ouput is then logged as XML and TXT in a user specified directory. The application parses the technical characteristics of the work of art from the XML to provide the correct flags to ffmpeg and [HandBrakeCLI](https://trac.handbrake.fr/wiki/CLIGuide). These tools will produce a [Matroska](http://www.matroska.org/) production quality file and an MP4 streaming copy, respectively. The `dd` command line utility is used to create an ISO disk image from the DVD. The application allows the user to choose one or all of the preservation files (ISO, MKV, MP4) to be created during one execution cycle. An ISO file **must** be provided if the user wishes to generate an MKV or MP4, otherwise this text box can be left blank.    

**IMPORTANT**   
* After downloading HandBrakeCLI from http://handbrake.fr/downloads2.php, make sure you add the application to your PATH.   
* If the master DVD is encrypted, `libdvdread` and `libdvdcss` must be installed before attempting to produce a SIP using this application. 


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

* [Python](http://www.python.org/) 
* [NumPy](http://www.numpy.org/)
* [SciPy](http://www.scipy.org/)
* [Matplotlib](http://matplotlib.org/)
* [MediaInfo](http://mediainfo.sourceforge.net/en)
* [FFMPEG](http://ffmpeg.org/ffmpeg.html)
* [HandBrakeCLI](https://trac.handbrake.fr/wiki/CLIGuide)


## To Do

* Parallelize the workflow to take advantage of HPC system resources for large video collections
* Create single package with Graphical User Interface
* Improve logging to facilitate metadata comparison 
