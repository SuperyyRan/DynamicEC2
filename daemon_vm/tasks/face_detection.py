import sys,os
import cv
from PIL import Image,ImageDraw
from math import sqrt

from  datetime  import  *  
import  time
import threading

from DynamicEC2.messages.sendMessage import *
from DynamicEC2.common.Task import *
from DynamicEC2.common.Message import *


def detectObjects(image):
    """ Converts an image to grayscale and prints the locations of any faces found"""
    grayscale = cv.CreateImage((image.width,image.height),8,1)
    cv.CvtColor(image,grayscale,cv.CV_BGR2GRAY)
    cascade = cv.Load('./haarcascade_frontalface_default.xml')
    faces = cv.HaarDetectObjects(grayscale,cascade,cv.CreateMemStorage(0),1.1,2,cv.CV_HAAR_DO_CANNY_PRUNING,(20,20))
    result = []
    for (x,y,w,h),n in faces:
        result.append((x,y,x+w,y+h))
    return result

def grayscale(r,g,b):
    return int(r*.3+g*.59+b*.11)

def process(infile,outfile):
    image = cv.LoadImage(infile);
    if image:
        faces = detectObjects(image)
    im = Image.open(infile)
    if faces:
        draw = ImageDraw.Draw(im)
        for f in faces:
            draw.rectangle(f,outline = (255,0,0))
        #im.save(outfile,"JPEG",quality=100)
    else:
        print("Error:cannot detect faces on %s" % infile)

def run(recv_task):
    #inputfile and outputfile name definitaion
    n = recv_task.execParameter
    inputfile = []
    outputfile = []
    for i in range(1,n+1,1):
        inputfile.append('./input.jpg')
        outputfile.append('./output'+str(i)+'.jpg')
    time.time()    
    for i in range(0,n,1):
        process(inputfile[i],outputfile[i])
        #print "process finish" + str(i) + "out of" + str(n)
    time.time()

    response = Message('Task_End', pickle.dumps(recv_task))
    sendMessage(['server'], pickle.dumps(response))
    print "-----task end-------"

