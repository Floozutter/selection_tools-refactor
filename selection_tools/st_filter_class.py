"""
filename: st_filter_class.py
2020.2.21
jongmoo.choi@canoo.com

This file filters image-filenames using the target object classes and the detection confidence values

INPUT: a txt file containing image filenames (full path)
OUTPUT: txt file containing filtered filenames

Usage: python3 st_filter_lowconf.py --in in.txt --out out.txt

Reference: st_readme.txt

"""
import glob
import os
import cv2
import numpy as np
import os
import argparse
import sys

from PIL import Image

def parse_args():
    parser = argparse.ArgumentParser(description='taking low-conf detection only')
    parser.add_argument(
        '--in',
        dest='src_file',
        help='input img-list file',
        default=None,
        type=str
    )
    parser.add_argument(
        '--out',
        dest='dst_file',
        help='output img-list file',
        default=None,
        type=str
    )
    parser.add_argument(
        '--skip',
        dest='skip_frame',
        help='define the frame difference to skip collection',
        default=None,
        type=str
    )
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    return parser.parse_args()

def loadImage(img_path):
    if(os.path.isfile(img_path)):
        raw = Image.open(img_path)
    else:
        print('no image file: '+img_path)
        raw = None
    return raw

def getAllImages(INPUT) -> list:
    imageList = []
    with open(INPUT) as f:
        imageList = f.readlines()
    imageList = [x.rstrip() for x in imageList]
    return imageList

def getInputFiles(txt):
    files = []
    with open(txt) as f:
        raw = f.readlines()
    files = [x.rstrip() for x in raw]
    return files

def getSotaDetectionFileName(imgFullPath):
    base, img = imgFullPath.split('video_seq/')
    detectionDir = os.path.join(base, 'od_videoseq')
    dataFileName = img+'.txt'
    fullPath = os.path.join(detectionDir,dataFileName)
    return fullPath

def getSotaDetectionResultImgFileName(imgFullPath):
    base, img = imgFullPath.split('video_seq/')
    detectionDir = os.path.join(base, 'od_videoseq')
    dataFileName = img+'.png'
    fullPath = os.path.join(detectionDir,dataFileName)
    return fullPath

def getBoxSizeFromLine(line_str):
    # get x1 y1 x2 y2
    coord_str = line_str.split(' ')[2:]
    coord = [int(float(x)) for x in coord_str]

    # traffic light has an extra space
    if len(coord) > 4:
        coord = coord[1:]

    x1 = coord[0]
    y1 = coord[1]
    x2 = coord[2]
    y2 = coord[3]
 
    # use for witdh only for now
    return x2 - x1

"""
    it's a place-holder for a CIPV detection module
"""
def isCIPV(mask, raw, detection_file):
    DATA_TYPE = 'BRAVE'
    isAnyCIPV = False

    with open(detection_file) as f:
        content = f.readlines()

    for e in content:
        # get x1 y1 x2 y2
        coord_str = e.split(' ')[2:]
        coord = [int(float(x)) for x in coord_str]

        # traffic light has an extra space
        if len(coord) > 4:
            coord = coord[1:]

        x1 = coord[0]
        y1 = coord[1]
        x2 = coord[2]
        y2 = coord[3]
        bottom_center_x = (x2 - x1) / 2.0 + x1
        bottom_center_y = y2

        # TBD: consider an adaptive mask for bravecam videos
        #      that have diffrent resolutions
        if DATA_TYPE == 'BRAVE':
            height_threshold = int(raw.size[1] * 0.6)
            if bottom_center_y >= height_threshold:
                isAnyCIPV = True
                break

        if DATA_TYPE == 'R8':
            loc = int(max(0, bottom_center_x-1)), int(max(0, bottom_center_y-1))
            # print(loc, coord, raw.size)
            # print(loc, coord, mask.getpixel(loc))
            assert(bottom_center_x >= 0)
            val = mask.getpixel(loc)[0]

            if val > 0:
                isAnyCIPV = True
                break
    return isAnyCIPV

def appendFilePathToFile(dst, imgPath):
    with open(dst, 'a') as f:
        f.write('%s\n' % imgPath)

#def getMinConf(det_file, objectType):
#    with open(det_file) as f:
#        raw=f.readlines()
     
#    minConf = 999.0
#    boxSize = 0.0

#    for line in raw:
#        if objectType in line:
#            conf = float(line.split(objectType+' ')[1].split(' ')[0])
#            boxSize = getBoxSizeFromLine(line)
#            if conf < minConf:
#                minConf = conf
#    return minConf, boxSize

# check if this detection result contain a specific class
def hasItClassX(det_file, objectTypeList):
    with open(det_file) as f:
        raw=f.readlines()
     
    TH_BOX_SIZE = 16
    TH_CONF_MIN = 0.0
    TH_CONF_MAX = 0.99
    boxSize = 0.0

    for line in raw:
        for objectType in objectTypeList:
            if objectType in line:
                conf = float(line.split(objectType+' ')[1].split(' ')[0])
                boxSize = getBoxSizeFromLine(line)
                if boxSize >= TH_BOX_SIZE and conf >= TH_CONF_MIN and conf <= TH_CONF_MAX:
                    return True
    return False

def hasItLowConfLargeObject(det_file, low_conf_class_list):
    def checkObject(low_conf_class_list, line_string):
        if(len(low_conf_class_list)==1):
            if low_conf_class_list in line:
                return True
            else: 
                return False
        elif(len(low_conf_class_list)==0):
            return False
        else:
            for each in low_conf_class_list:
                if each in line:
                    return True
        return False

    with open(det_file) as f:
        raw=f.readlines()
    
    minConf = 999.0
    boxSize = 0.0

    for line in raw:
        if objectType in line:
            conf = float(line.split(objectType+' ')[1].split(' ')[0])
            boxSize = getBoxSizeFromLine(line)
            if conf < minConf:
                minConf = conf

    if (minConf <= 0.80 and boxSize >= 150):
        return True
    else:
        return False


def run(src, dst, THRESHOLD_SKIP_FRAME):
    def getParsedFrame(img_path):
        if '/canoo-label-pl-bravecam2k/d4t/' in img_path: # bravecam
            videoName = img_path.split('/d4t/')[1].split('/video_seq/')[0]
            frameNumber = int(img_path.split('/d4t/')[1].split('/video_seq/')[1].split('.jpg')[0])
            raw_data_type = 'BRAVECAM'
        elif '/horizon_unpacked_sota/' in img_path:
            if not('/6_6/' in img_path):
                print('NOT sota 6.6')
                exit()
            videoName = img_path.split('/6_6/')[1].split('/video_seq/')[0]
            frameNumber = int(img_path.split('/6_6/')[1].split('/video_seq/')[1].split('.jpg')[0].split('_image_')[0])
            raw_data_type = 'HORIZON'
        else:
            print('wrong directory', img_path)
            exit()
        # frameNumber: (int)
        return videoName, frameNumber, raw_data_type

    rare_object_list = ['train', 'boat', 'refrigerator', 'motorbike', 'animal', 'person', 'bicycle']
    low_object_list = ['truck', 'car', 'bus', 'bicycle', 'motorbike', 'person', 'animal']
    # mask image
    mask = Image.open("CIPV_mask1.png")
    imgList = getAllImages(src)

    # skip sequential data
    previousVideoName = ''
    previousFrameNumber = 0

    for img in imgList:
        # check the sequence and skip it with the threshold
        videoName, frameNumber, raw_data_type = getParsedFrame(img)

        # remove sequence data
        if not(videoName == previousVideoName): # new video
            previousVideoName = videoName
            previousFrameNumber = frameNumber
        elif (frameNumber - previousFrameNumber) < int(THRESHOLD_SKIP_FRAME): # sequential data 15, 60, 120
            continue

        det_file = getSotaDetectionFileName(img)

        if not(os.path.isfile(det_file)):
            print(det_file, 'not found')
            continue

        # ------------------------------------------------------------------
        # combine multiple things together
        # check OR conditions 
        isGoodSample = True
        # ------------------------------------------------------------------

        # check the class name
        isGoodSample = isGoodSample or hasItClassX(det_file, rare_object_list)

        # large low-conf truck
        isGoodSample = isGoodSample or hasItLowConfLargeObject(det_file, low_conf_class_list)

        # combined ALL -----------------------------------------------------
        if not(isGoodSample):
            continue

        # get raw image
        if(os.path.isfile(img)):
             raw = Image.open(img)
        else:
             print(img, 'not found')
             continue 

        # CIPV
        # (TODO) fix CIPV for Horizon data
        if not(raw_data_type=='HORIZON'):
            if not(isCIPV(mask, raw, det_file)):
                print(det_file, 'not CIPV')
                continue

        # init the reference         
        previousFrameNumber = frameNumber

        print(img)
        # NOTE: it is appending!!22
        appendFilePathToFile(dst, img)
        #print(getSotaDetectionResultImgFileName(img), boxSize)

if __name__ == '__main__':
    args = parse_args()
    run(args.src_file, args.dst_file, args.skip_frame)
