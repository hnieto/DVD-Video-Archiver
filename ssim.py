'''
File main_single_image.py
Created on 21 nov. 2011
@author: Antoine Vacavant, ISIT lab, antoine.vacavant_AT_iut.u-clermont1.fr, http://isit.u-clermont1.fr/~anvacava
'''

#Possible use of matplotlib from http://http://matplotlib.sourceforge.net/
from pylab import *
import matplotlib.pyplot as plt

#More imports
from PIL import Image
from PIL import ImageOps
import numpy

import scipy.ndimage
from numpy.ma.core import exp
from scipy.constants.constants import pi
import os
import sys

def runSSIM(folder1, folder2):
    listing1 = os.listdir(folder1)
    listing2 = os.listdir(folder2)

    cnt = 0
    totalSum = 0
    ssimArray = []
    devSum = 0

    for infile in listing1:

        #First image 
        imgRefMat=build_mat_from_grayscale_image(folder1+"/"+infile)
        (w,h) = (imgRefMat.shape[0],imgRefMat.shape[1])
        
        #First subplot
        plt.figure()
        plt.subplot(121)
        plt.imshow(imgRefMat, cmap=cm.gray, hold=True)
        
        #Second image
        imgOutMat=build_mat_from_grayscale_image(folder2+"/"+listing2[cnt])
        
        #Second subplot
        plt.subplot(122)
        plt.imshow(imgOutMat, cmap=cm.gray, hold=True)
       # plt.show()
        
        #Compute SSIM
        cSSIM=compute_ssim(imgRefMat,imgOutMat)
        totalSum= totalSum+ cSSIM
        ssimArray.append(cSSIM)

        # Add counter for next file
        cnt = cnt + 1

    averageSSIM = totalSum/cnt

    # Determine standard deviation
    for item in ssimArray:
        temp = item - averageSSIM
        temp = temp*temp
        devSum = devSum + temp

    standardDeviation = devSum/(cnt -1)
    return (averageSSIM, standardDeviation)

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
The function to compute SSIM
@param param: img_mat_1 1st 2D matrix
@param param: img_mat_2 2nd 2D matrix
'''
def compute_ssim(img_mat_1, img_mat_2):
    #Variables for Gaussian kernel definition
    gaussian_kernel_sigma=1.5
    gaussian_kernel_width=11
    gaussian_kernel=numpy.zeros((gaussian_kernel_width,gaussian_kernel_width))
    
    #Fill Gaussian kernel
    for i in range(gaussian_kernel_width):
        for j in range(gaussian_kernel_width):
            gaussian_kernel[i,j]=\
            (1/(2*pi*(gaussian_kernel_sigma**2)))*\
            exp(-(((i-5)**2)+((j-5)**2))/(2*(gaussian_kernel_sigma**2)))

    #Convert image matrices to double precision (like in the Matlab version)
    img_mat_1=img_mat_1.astype(numpy.float)
    img_mat_2=img_mat_2.astype(numpy.float)
    
    #Squares of input matrices
    img_mat_1_sq=img_mat_1**2
    img_mat_2_sq=img_mat_2**2
    img_mat_12=img_mat_1*img_mat_2
    
    #Means obtained by Gaussian filtering of inputs
    img_mat_mu_1=scipy.ndimage.filters.convolve(img_mat_1,gaussian_kernel)
    img_mat_mu_2=scipy.ndimage.filters.convolve(img_mat_2,gaussian_kernel)
        
    #Squares of means
    img_mat_mu_1_sq=img_mat_mu_1**2
    img_mat_mu_2_sq=img_mat_mu_2**2
    img_mat_mu_12=img_mat_mu_1*img_mat_mu_2
    
    #Variances obtained by Gaussian filtering of inputs' squares
    img_mat_sigma_1_sq=scipy.ndimage.filters.convolve(img_mat_1_sq,gaussian_kernel)
    img_mat_sigma_2_sq=scipy.ndimage.filters.convolve(img_mat_2_sq,gaussian_kernel)
    
    #Covariance
    img_mat_sigma_12=scipy.ndimage.filters.convolve(img_mat_12,gaussian_kernel)
    
    #Centered squares of variances
    img_mat_sigma_1_sq=img_mat_sigma_1_sq-img_mat_mu_1_sq
    img_mat_sigma_2_sq=img_mat_sigma_2_sq-img_mat_mu_2_sq
    img_mat_sigma_12=img_mat_sigma_12-img_mat_mu_12;
    
    #c1/c2 constants
    #First use: manual fitting
    c_1=6.5025
    c_2=58.5225
    
    #Second use: change k1,k2 & c1,c2 depend on L (width of color map)
    l=255
    k_1=0.01
    c_1=(k_1*l)**2
    k_2=0.03
    c_2=(k_2*l)**2
    
    #Numerator of SSIM
    num_ssim=(2*img_mat_mu_12+c_1)*(2*img_mat_sigma_12+c_2)
    #Denominator of SSIM
    den_ssim=(img_mat_mu_1_sq+img_mat_mu_2_sq+c_1)*\
    (img_mat_sigma_1_sq+img_mat_sigma_2_sq+c_2)
    #SSIM
    ssim_map=num_ssim/den_ssim
    index=numpy.average(ssim_map)

    return index

