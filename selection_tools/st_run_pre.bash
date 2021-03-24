#!/bin/bash
NUM_VIDEOS_TO_COLLECT=15
NUM_VIDEOS_TO_COLLECT=1  # DEBUG
TH_SKIP_FRAMES=120

# Please specify the RAW_DATA_TYPE to process either {Bravecam or Horizon} data
# RAW_DATA_TYPE='BRAVECAM'
RAW_DATA_TYPE='HORIZON'


cd ~/git/labeling_tools/sampling_tools

## get a list of processed videos that have been submitted to aws
# I: /mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d/set* <-- ignoring tmp* dirs
# run it when the aws batch files has been updated

	python3 st_get_processed_video_aws.py > tmp_processed_aws.txt

echo $(cat tmp_processed_aws.txt | wc | awk '{print $1}')' videos have been submitted to AWS'
cp tmp_processed_aws.txt tmp_processed_aws_updated.txt

## incrementally generate hash data for all submitted aws data (if not generated)
# ex: /mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d/set3-2020-02-01-200 has hash files.
# run it when the aws batch files has been updated

	python3 st_aws2hsh.py

## sota detection results --> list of raw frames (while checking the redundant videos)
# I: tmp_processed_aws_updated.txt
echo 'extrating raw frames...'
# define the max video >1
	python3 st_dir2txt.py --num $NUM_VIDEOS_TO_COLLECT --type $RAW_DATA_TYPE > tmp_raw.txt

echo $(cat tmp_raw.txt | wc | awk '{print $1}')' filenames have been extracted'

## filter data
# (TODO) combine multiple filters into 1

        rm tmp_filtered.txt # otherwise the selection code will append data
	python3 st_filter_class.py --in tmp_raw.txt --out tmp_filtered.txt --skip $TH_SKIP_FRAMES

echo 'before : '$(cat tmp_raw.txt | wc | awk '{print $1}')
echo 'after  : '$(cat tmp_filtered.txt | wc | awk '{print $1}')

## create hash database for the filtered data
# I: tmp_filtered.txt
echo 'creating hash database...'

	python3 st_txt2hsh.py

echo 'created hash database'

## filtering duplidated data using the hash
# I: tmp_filtered.txt

	python3 st_hsh2txt.py > tmp_unique_hash.txt 

echo 'before : '$(cat tmp_filtered.txt | wc | awk '{print $1}')
echo 'after  : '$(cat tmp_unique_hash.txt | wc | awk '{print $1}')
# (TODO) copy files to compare before, after

## backup data
# /mnt/nfs_pve/DL_data/tmp/out/

backup_dir=$(date +%Y-%m-%d-%s)
mv /mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d/tmp /mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d/tmp-backup-$backup_dir      
mkdir /mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d/tmp
mkdir /mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d/tmp/img
mkdir /mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d/tmp/imgnbox

	python3 st_txt2img.py --in tmp_unique_hash.txt --out /mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d/tmp

dir_img=/mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d/tmp/img
num_img=$(ls -1 $dir_img | wc | awk '{print $1}')

echo $(date)
echo 'selection pipeline statistics'
echo 'input: '$NUM_VIDEOS_TO_COLLECT' Bravecam videos'
N_raw=$(cat tmp_raw.txt | wc | awk '{print $1}') 
echo 'raw: '$N_raw' frames'
N_selected=$(cat tmp_filtered.txt | wc | awk '{print $1}')
echo 'selection: '$N_selected' frames ('$TH_SKIP_FRAMES'+ sequence)'
N_hashing=$(cat tmp_unique_hash.txt | wc | awk '{print $1}')
F_hashing_rate=$(python3 <<< 'print('$N_hashing'/'$N_selected')')
echo 'hashing: '$N_hashing' (rate:'$F_hashing_rate' )'
F_final_rate=$(python3 <<< 'print('$N_hashing'/'$N_raw')')
echo 'final frames: '$(cat tmp_unique_hash.txt | wc | awk '{print $1}')
echo 'final rate : '$F_final_rate
echo 'done'
