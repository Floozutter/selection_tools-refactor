
"""
filename: scale_hsh2txt.py
2020.12.22
jongmoo.choi@canoo.com

Description:

* Filters a list of image-filenames using created hash (NOT imghash/*.pickle)

input: a txt file containing image-filenames (full path)
output: print all unique image-filenames

Usage: python3 scale_hsh2txt.py > tmp_unique_hash.txt

Reference: st_readme.txt
"""
import glob
import imagehash
from PIL import Image
import sqlite3
import pickle
import os

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

# main
# given the input tmp.txt file, load the generated hash file, 
# and print ONLY the fist image per hash code

INPUT='tmp_filtered.txt' 

if isHashAvailable(INPUT):
    # src_img2hash = getHashPickleFile(INPUT.split('.txt')[0]+'_img2hash.pickle')
    src_hash2img = getHashPickleFile(INPUT.split('.txt')[0]+'_hash2img.pickle')
    for h in src_hash2img:
        print(src_hash2img[h][0])
else:
    print("no hash data available for", INPUT)
