"""
filename: st_filter_lowconf.py
2020.12.14
jongmoo.choi@canoo.com

This file filters image-filenames using the SOTA detection confidence values

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

def getMinConf(det_file, objectType):
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
    return minConf, boxSize

def run(src, dst):
    # mask image
    mask = Image.open("CIPV_mask1.png")

    imgList = getAllImages(src)

    for img in imgList:
        det_file = getSotaDetectionFileName(img)
        if not(os.path.isfile(det_file)):
            # print(det_file, 'not found')
            continue

        # confidence
        #minConf, boxSize = getMinConf(det_file, 'car')
        #if (minConf > 0.80 or boxSize < 150): # 0.7
        #    continue

        minConf, boxSize = getMinConf(det_file, 'truck')
        if (minConf > 0.80 or boxSize < 150): # 0.7
            continue

        #minConf, boxSize = getMinConf(det_file, 'bus')
        #if (minConf > 0.80 or boxSize < 150): # 0.7
        #    continue

        # get raw image
        if(os.path.isfile(img)):
             raw = Image.open(img)
        else:
             # print(img, 'not found')
             continue 

        # CIPV
        if not(isCIPV(mask, raw, det_file)):
            # print(det_file, 'not CIPV')
            continue
            pass
         
        print(img)
        appendFilePathToFile(dst, img)
        #print(getSotaDetectionResultImgFileName(img), boxSize)

if __name__ == '__main__':
    args = parse_args()
    run(args.src_file, args.dst_file)
