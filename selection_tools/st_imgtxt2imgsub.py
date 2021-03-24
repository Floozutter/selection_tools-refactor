"""
filename: st_imgtxt2imgsub.py
2021.1.15
jongmoo.choi@canoo.com

Given a list of filtered filenames, copy the original frames into a target directory

input: a txt file containing image filenames
       video name (directory name) "+" frame number ".jpg.png"

output: copied images files to a temp directory (ex: /tmp/out)

     ex: /mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d/1-2020-01-15-50/img/*.jpg

Usage: 

python3 st_imgtxt2imgsub.py --in /mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d/1-2020-01-15-50/filtered-1-50.txt --out /mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d/1-2020-01-15-50/img


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
        dest='dst_dir',
        help='output directory',
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

def getSotaDetectionVideoName(imgFullPath):
    base, img = imgFullPath.split('/video_seq/')
    videoName = base.split('d4t/')[1]
    return videoName

SRC_PATH = '/mnt/nfs_pve/DL_data/canoo-label-pl-bravecam2k/d4t'

def run(src, dst):
    imgList = getAllImages(src)

    N_images = 0
    for img in imgList:
        video_name, frame_number_str = img.split("+")
        frame_number = frame_number_str.split(".jpg.png")[0]

        fullpath = os.path.join(SRC_PATH, video_name + "/video_seq")
        fullpath = os.path.join(fullpath, frame_number + ".jpg")

        src_file = fullpath
        if not(os.path.isfile(src_file)):
            print(src_file, 'not found')
            print('check the SRC_PATH')
            exit()
            continue

        dst_file = os.path.join(dst, img.split(".png")[0])

        print(src_file, '->', dst_file)
        copyfile(src_file, dst_file)
        N_images += 1

    print("No. copied files", N_images)

if __name__ == '__main__':
    args = parse_args()
    run(args.src_file, args.dst_dir)
