'''
File main_single_image.py
Created on 21 nov. 2011
@author: Antoine Vacavant, ISIT lab, antoine.vacavant_AT_iut.u-clermont1.fr, http://isit.u-clermont1.fr/~anvacava
'''

#Possible use of matplotlib from http://http://matplotlib.sourceforge.net/
from pylab import * 
import matplotlib.pyplot as plt

#More imports
import Image
import numpy
import ImageOps

#ssim.py to compute SSIM
import ssim

#import arguments
import sys
import os
'''
Get 2D matrix from an image file, possibly displayed with matplotlib 
@param path: Image file path on HD
@return A 2D matrix
''' 
def build_mat_from_grayscale_image(path):
    img=Image.open(str(path))
    img=ImageOps.grayscale(img)
    imgData=img.getdata()
    imgTab=numpy.array(imgData)
    w,h=img.size
    imgMat=numpy.reshape(imgTab,(h,w))
    
    return imgMat

'''
Main program
'''
if len(sys.argv) != 3: #the program name and the two arguments
	#stop the program and print and error message
    #These are the folder names created for each sequence
	sys.exit("Must provide two folder names")

folder1 = sys.argv[1]
folder2 = sys.argv[2]

listing1 = os.listdir(folder1)
listing2 = os.listdir(folder2)

cnt = 0
totalSum = 0
ssimArray = []
devSum = 0

for infile in listing1:
    if __name__ == '__main__':

        #First image 
        imgRefMat=build_mat_from_grayscale_image(sys.argv[1]+"/"+infile)
        (w,h) = (imgRefMat.shape[0],imgRefMat.shape[1])
        
        #First subplot
        figure()
        subplot(121)
        plt.imshow(imgRefMat, cmap=cm.gray, hold=True)
        
        #Second image
        imgOutMat=build_mat_from_grayscale_image(sys.argv[2]+"/"+listing2[cnt])
        
        #Second subplot
        subplot(122)
        plt.imshow(imgOutMat, cmap=cm.gray, hold=True)
       # plt.show()
        
        #Compute SSIM
        cSSIM=ssim.compute_ssim(imgRefMat,imgOutMat)
        totalSum= totalSum+ cSSIM
        ssimArray.append(cSSIM)
#        print "SSIM=", cSSIM
#        print cSSIM
# Add counter for next file
        cnt = cnt + 1

averageSSIM = totalSum/cnt

# Determine standard deviation
for item in ssimArray:
    temp = item - averageSSIM
    temp = temp*temp
    devSum = devSum + temp

standardDeviation = devSum/(cnt -1)
print "averageSSIM=", averageSSIM
print "standardDeviation=", standardDeviation
