"""
filename: st_txt2img.py
2020.12.21
jongmoo.choi@canoo.com

copy detection results (*.png) and extracted frames (*.jpg) from the output.txt file 

input: a txt file containing image filenames (full path)
output: copied images files to a temp directory (ex: /tmp/out)
    1) *.jpg (we are not using these images for review) -- to be removed
    2) *.jpg.png (using it for filtering review)
       ex: 2000_0101_045930_008.MP4+3276.jpg.png
           (video name)           "+" (frame no)

Usage: python3 st_txt2img.py --in data.txt

Reference: st_readme.txt
"""
import glob
import os
import sys
import argparse
from shutil import copyfile

def parse_args():
    parser = argparse.ArgumentParser(description='taking low-conf detection only')
    parser.add_argument(
        '--in',
        dest='src_file',
        help='input img-list fiile',
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

def getRawDataType(img_path):
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

def getSotaDetectionVideoName(imgFullPath):
    """
    base, img = imgFullPath.split('/video_seq/')
    videoName = base.split('d4t/')[1]
    return videoName
    """
    videoName, frameNumber, raw_data_type = getRawDataType(imgFullPath)
    return videoName

def run(src, dst):
    if not(os.path.isdir(os.path.join(dst, 'img'))):
        print('the destication dir should have img and imgnbox sub-dirs')
        exit()   
    if not(os.path.isdir(os.path.join(dst, 'imgnbox'))):
        print('the destication dir should have img and imgnbox sub-dirs')
        exit()    

    imgList = getAllImages(src)

    for img in imgList:
        det_file = getSotaDetectionFileName(img)
        if not(os.path.isfile(det_file)):
            # print(det_file, 'not found')
            continue

        # bb image
        src_bbimg = getSotaDetectionResultImgFileName(img)
        videoname = getSotaDetectionVideoName(img)
        outFileName = videoname + '+' + src_bbimg.split('od_videoseq/')[-1]
        dst_outimg = os.path.join(os.path.join(dst, 'imgnbox'), outFileName)

        print(src_bbimg, '->', dst_outimg)
        copyfile(src_bbimg, dst_outimg)

        # source image
        src_frame = img
        src_outFileName = outFileName.split('.png')[0]
        dst_frame = os.path.join(os.path.join(dst, 'img'), src_outFileName)

        print(src_frame, '->', dst_frame)
        copyfile(src_frame, dst_frame)

if __name__ == '__main__':
    args = parse_args()
    run(args.src_file, args.dst_file)
