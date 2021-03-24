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

INPUT='/mnt/nfs_pve/Raw_data/data-sampling/data-sampling/brave_cam_sample/labeling_batch_'

def getBatch(batch_no) -> list:
    files = []
    # note that labeling_batch_01 has *.jpg images but
    # the sibling directories have sub-directories
    if batch_no == 1:
        img_str = INPUT+str(batch_no).zfill(2)+'/*.jpg'
    else:
        img_str = INPUT+str(batch_no).zfill(2)+'/road/*.jpg'
   
    print(img_str)
    for f in glob.glob(img_str):
        files.append(f)
    return files

def countAllImages() -> None:
    N = 0
    for batch_no in range(10):
        # print('batch: ' + str(batch_no))
        files = getBatch(batch_no+1)
        # print(files[:10])
        N+=len(files)
    return N

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

def getAllImages() -> list:
    imageList = []
    for batch_no in range(10):
        files = getBatch(batch_no+1)
        if len(files)>0:
            imageList += files
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
    with open('scale_v1_batch_1_10_img2hash.pickle', 'wb') as handle:
            pickle.dump(img2hash, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print('saved img2hash')

    with open('scale_v1_batch_1_10_hash2img.pickle', 'wb') as handle:
            pickle.dump(hash2img, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print('saved hash2img')

def getHashPickleFile(hash_file_name):
    if os.path.isfile(hash_file_name):
        with open(hash_file_name, 'rb') as handle: 
            hash_database = pickle.load(handle)
    else:
        hash_database = dict([])
    return hash_database

# main
# run this function to create img2hash, hash2img pickle files
#createImgHashFiles()

filename1 = 'img2hash_scale_v1_batch_1_10.pickle'
img2hash = getHashPickleFile(filename1)

filename2 = 'hash2img_scale_v1_batch_1_10.pickle'
hash2img = getHashPickleFile(filename2)

print('No. of images: ', len(img2hash))
print('No. of hash code: ', len(hash2img))
print('ratio: ',len(hash2img)/float(len(img2hash)))
