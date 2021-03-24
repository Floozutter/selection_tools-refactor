import glob
import imagehash
from PIL import Image
import sqlite3
import pickle
import os

"""
This script generates hash files from the AWS submission directory:

ex: 

.
├── set1-2020-01-15-50
│   ├── aws-filtered-1-50.txt
│   ├── filtered-1-50.txt
│   ├── img
│   ├── imgnbox
│   ├── sample-1-2835.txt
│   ├── set1-2020-01-15-50-hash2img.pickle
│   └── set1-2020-01-15-50-img2hash.pickle


(1) reads all subdirectories under the BASE_DIR (ex: /mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d)
(2) checks each directory if two hash files exist (img2hash, hash2img)
(3) if the hash files are not found, create hash files under the directory

"""

def loadImage(img_path):
    if(os.path.isfile(img_path)):
        raw = Image.open(img_path)
    else:
        print('no image file: '+img_path)
        raw = None
    return raw

def getHash(raw):
    if(raw is not None):
        img_hash = imagehash.average_hash(raw)
    else:
        img_hash = None
    return img_hash

def getAllImages(INPUT) -> list:
    imageList = []
    with open(INPUT) as f:
        imageList = f.readlines()
    imageList = [x.rstrip() for x in imageList]
    return imageList

def getAllHash(imageList) -> list:
    hashList = []
    for img in imageList:
        raw = loadImage(img)
        img_hash = getHash(raw)
        print(img_hash)
        hashList.append(img_hash)
    return hashList

def putImgAndHash(imageList):
    Cnt = 0;
    img2hash = dict()
    hash2img = dict()
    for img in imageList:
        raw = loadImage(img)
        img_hash = getHash(raw)
        #print(img_hash)
        img2hash[img] = str(img_hash)
        if str(img_hash) in hash2img:
            hash2img[str(img_hash)].append(img)
        else:
            parsed_img = img.split('/')[-1]
            print(parsed_img)
            hash2img[str(img_hash)] = [parsed_img]
        print(Cnt)
        Cnt += 1
    return img2hash, hash2img

def createImgHashFilesInAWSDir(fullpath, dirname, img2hash_file, hash2img_file):
    imgList = glob.glob(os.path.join(fullpath,'img/*.jpg'))
    img2hash, hash2img = putImgAndHash(imgList)

    # Store data (serialize)
    with open(img2hash_file, 'wb') as handle:
            pickle.dump(img2hash, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print('saved img2hash')

    with open(hash2img_file, 'wb') as handle:
            pickle.dump(hash2img, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print('saved hash2img')

    print('hash data created')
    print('No. of images: ', len(img2hash))
    print('No. of hash code: ', len(hash2img))
    print('ratio: ',len(hash2img)/float(len(img2hash)))


BASE_DIR = '/mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d'
dir_list = glob.glob(os.path.join(BASE_DIR,"set*"))

for each in dir_list:
    dir_name = each.split('/scale-batch-2d/')[1]
    # check if hask files exist
    hash2img_file = os.path.join(each, dir_name + '-hash2img.pickle')
    img2hash_file = os.path.join(each, dir_name + '-img2hash.pickle')

    if (os.path.isfile(hash2img_file) and os.path.isfile(img2hash_file)):
        print(each, 'has hash files.')
        continue
    else:
        print('no hash files!')

    createImgHashFilesInAWSDir(each, dir_name, img2hash_file, hash2img_file)



