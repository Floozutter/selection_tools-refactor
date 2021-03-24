
"""
filename: st_filter_duplicated.py
2020.12.11
jongmoo.choi@canoo.com

This file filters image-filenames using existing hash data

input: a txt file containing image filenames (full path)
output: print all unique filenames

Usage: python3 st_filter_duplicated.py > newlist.txt

Reference: st_readme.txt
"""
import glob
import imagehash
from PIL import Image
import sqlite3
import pickle
import os

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

def createImgHashFiles():
    print(countAllImages())
    imgList = getAllImages()
    #hashList = getAllHash(imgList)
    img2hash, hash2img = putImgAndHash(imgList)
    print(len(img2hash))
    print(len(hash2img))

    # Store data (serialize)
    with open('img2hash_scale_v1_batch_1_10.pickle', 'wb') as handle:
            pickle.dump(img2hash, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print('saved img2hash')

    with open('hash2img_scale_v1_batch_1_10.pickle', 'wb') as handle:
            pickle.dump(hash2img, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print('saved hash2img')

def getInputFiles(txt):
    files = []
    with open(txt) as f:
        raw = f.readlines()
    files = [x.rstrip() for x in raw]
    return files

def isHashAvailable(INPUT):
    fid = INPUT.split('.txt')[0]
    n1 = fid+'_img2hash.pickle'
    n2 = fid+'_hash2img.pickle'
    if not(os.path.isfile(n1)):
        print('no '+n1)
        return False
    if not(os.path.isfile(n2)):
        print('no '+n2)
        return False
    return True

def getHashPickleFile(hash_file_name):
    if os.path.isfile(hash_file_name):
        with open(hash_file_name, 'rb') as handle:
            hash_database = pickle.load(handle)
    else:
        hash_database = dict([])
    return hash_database

def getReferences():
    img2hash_list = glob.glob('imghash/*_img2hash.pickle')
    hash2img_list = glob.glob('imghash/*_hash2img.pickle')
    return img2hash_list, hash2img_list
    
# main

INPUT='tmp.txt' 

if isHashAvailable(INPUT):
    src_img2hash = getHashPickleFile(INPUT.split('.txt')[0]+'_img2hash.pickle')
    src_hash2img = getHashPickleFile(INPUT.split('.txt')[0]+'_hash2img.pickle')

    img2hash_list, hash2img_list = getReferences()

    goodlist = dict()
    for img in getAllImages(INPUT):
        goodlist[img] = True

    # print('original ', len(goodlist))

    for i in range(len(img2hash_list)):
        img2hash_file = img2hash_list[i]
        hash2img_file = hash2img_list[i]

        hash2img = getHashPickleFile(hash2img_file)

        # print('  hash data:', str(i), len(hash2img)) 

        for src_file in goodlist:
            src_hash = src_img2hash[src_file]
            if src_hash in hash2img:
                # duplicated
                goodlist[src_file] = False
    
    finallist = []
    for img in goodlist:
        if goodlist[img]:
            finallist.append(img)
            print(img)

    # print('remaining ',len(finallist))

