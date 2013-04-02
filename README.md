# DVD Video Archiver

These scripts create an automated workflow that produces a submission information package (SIP) for archiving video art acquired originally in DVD format. For each DVD submitted to the workflow,
the resultant SIP contains an ISO disk image, production quality and access files, and a logs that record the technical metadata about the files and about the conversion processes involved.
The project was elicited by the need of the Blanton Museum of Art at the University of Texas at Austin to find a file-based preservation solution to archive their video art collection 
in a high performance storage (HPC) resource at the [Texas Advanced Computing Center](http://www.tacc.utexas.edu/).

**IMPORTANT**  
This is still a work in progress. Please read this document in its entirety to get a complete understanding of what has and has not been implemented. Thank you.


## High-Level Procedure Description

The process is launched by double-clicking the `blantonWorkFlow.command` shell script. The script will extract the DVD's technical information using [MediaInfo](http://mediainfo.sourceforge.net/en) 
and [ffmpeg](http://ffmpeg.org/ffmpeg.html). The ouput is then logged as XML and TXT, respectively, in a user specified directory. In addition to the shell script, we wrote python
scripts to interface with the [SSIM](http://www.sciencedirect.com/science/article/pii/S0923596503000766) algorithm, to extract the technical characteristics of the work of art to 
provide the correct flags to ffmpeg and [HandBrakeCLI](https://trac.handbrake.fr/wiki/CLIGuide). These tools will produce a [Matroska](http://www.matroska.org/) production quality file
and an MP4 streaming copy.


## SSIM

In order to ensure that the preservation master has been transcoded correctly, a video quality metric is used to compare the original disk image to the preservation files and optionally
to the streaming file. The SSIM implementation compares a single image file and produces a measurement between -1 and 1. If the SSIM Index is 1, the reference file and copy are identical, 
which is what we aim for in this step. For lossy conversion, anything below 1 indicates a loss in quality from the original file. In our workflow, the measurement is averaged between the 
SSIM index of 100 frames.


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
* [MediaInfo](http://mediainfo.sourceforge.net/en)
* [FFMPEG](http://ffmpeg.org/ffmpeg.html)
* [HandBrakeCLI](https://trac.handbrake.fr/wiki/CLIGuide)


## To Do

* Parallelize the workflow to take advantage of HPC system resources for large video collections
* Create single package with Graphical User Interface
* Improve logging to facilitate metadata comparison 


## Outstanding Issues

* large Matroska file (>20GB) generated for some DVD images 
