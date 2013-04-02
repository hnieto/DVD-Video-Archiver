!/bin/bash

#Ask for file name
echo -e "\nPlease, enter a directory name - include complete address for example /Users/vega/Desktop/DIRECTORY"
read FILENAME

echo -e "\nPlease, enter a file name - for example FILENAME"
read NAMEMOVIE
echo -e "\nThe path for your files is $FILENAME/\n"

#Create disk image and checksum
mkdir -p $FILENAME
date "+DATE: %Y-%m-%d%nTIME: %H:%M:%S\n" >> $FILENAME/$NAMEMOVIE.txt

#Create metadata of original COPY
echo -e "\nPlease, enter DVD filename as it appears on the FINDER window"
read DVDNAME
echo -e "\nCreate TXT and XML files of original file's metadata\n"
echo "ORIGINAL METADATA" >> $FILENAME/$NAMEMOVIE.txt
mediainfo -f /Volumes/$DVDNAME >> $FILENAME/$NAMEMOVIE.txt
mediainfo --Output=XML -f /Volumes/$DVDNAME >> $FILENAME/$NAMEMOVIE.xml # needed to extract aspect ratio
wait

#Create disk image and checksum
#echo -e "\nCreate disk image and checksum"
#diskutil unmountDisk /dev/disk1
#dd if=/dev/disk1 of=$FILENAME/$NAMEMOVIE.iso
#echo "CHECKSUM" >> $FILENAME/$NAMEMOVIE.txt
#cksum $FILENAME/$NAMEMOVIE.iso >> $FILENAME/$NAMEMOVIE.txt

#Show streams 
ffmpeg -i $FILENAME/$NAMEMOVIE.iso > $FILENAME/$NAMEMOVIEFormat.txt 2>&1

#select streams
export VWF=~/Desktop/DVD-Video-Archiver
python $VWF/convert.py $FILENAME/$NAMEMOVIEFormat.txt $FILENAME/$NAMEMOVIE.iso $NAMEMOVIE.mkv $NAMEMOVIE.mp4 $FILENAME/$NAMEMOVIE.xml
chmod 755 $FILENAME/convert.sh

#Create Matroska File
export PATH=/usr/local/bin:$PATH
cd $FILENAME/
./convert.sh

echo "Matroska and MP4 created" >> $FILENAME/$NAMEMOVIE.txt
ls -lh $NAMEMOVIE.mkv >> $FILENAME/$NAMEMOVIE.txt
ls -lh $NAMEMOVIE.mp4 >> $FILENAME/$NAMEMOVIE.txt


#Create Quality Index
mkdir $FILENAME/original
mkdir $FILENAME/copy
ffmpeg -i $FILENAME/$NAMEMOVIE.iso -vframes 100 $FILENAME/original/frameoriginal%03d.bmp
ffmpeg -i $FILENAME/$NAMEMOVIE.mkv -vframes 100 $FILENAME/copy/framecopy%03d.bmp
echo "SSIM QUALITY" >> ~ $FILENAME/$NAMEMOVIE.txt
echo "Implementing quality control, please wait"
python $VWF/mainSSIM.py $FILENAME/original/ $FILENAME/copy/ >> $FILENAME/$NAMEMOVIE.txt

echo "final step, almost done"
#Output metadata
echo "METADATA" >> $FILENAME/$NAMEMOVIE.txt
mediainfo -f $FILENAME/$NAMEMOVIE.mkv >> $FILENAME/$NAMEMOVIE.txt
mediainfo --Output=XML $FILENAME/$NAMEMOVIE.mkv >> $FILENAME/$NAMEMOVIE.xml
date "+DATE: %Y-%m-%d%nTIME: %H:%M:%S" >> $FILENAME/$NAMEMOVIE.txt

rm -r $FILENAME/copy
rm -r $FILENAME/original
rm -r $FILENAME/convert.sh

# use for block commenting
#: <<'END'
#END
