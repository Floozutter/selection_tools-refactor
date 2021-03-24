import glob
import imagehash
from PIL import Image
import sqlite3
import pickle
import os

"""
createImgHashFiles()
	I: labeling_batch_*
	O: img2hash*.pickle
           hash2img*.pickle

filterRedundantFiles()
	I: in_list.txt (list file containing full pathes)
	O: out_list.txt (list file, removed redundant images

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
            hash2img[str(img_hash)] = [img]
        print(Cnt)
        Cnt += 1
    return img2hash, hash2img

def createImgHashFiles(INPUT):
    BATCH_NAME = INPUT.split('.txt')[0]

    imgList = getAllImages(INPUT)
    img2hash, hash2img = putImgAndHash(imgList)

    # Store data (serialize)
    with open(BATCH_NAME+'_img2hash.pickle', 'wb') as handle:
            pickle.dump(img2hash, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print('saved img2hash')

    with open(BATCH_NAME+'_hash2img.pickle', 'wb') as handle:
            pickle.dump(hash2img, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print('saved hash2img')

    print('hash data created')
    print('No. of images: ', len(img2hash))
    print('No. of hash code: ', len(hash2img))
    print('ratio: ',len(hash2img)/float(len(img2hash)))

INPUT='tmp_filtered.txt'
createImgHashFiles(INPUT)

