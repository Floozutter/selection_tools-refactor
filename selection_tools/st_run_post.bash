#!/bin/bash

cd /mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d/tmp

## compare/delete img and imgnbox dirs 
# the operator can remove some images in the "imgnbox" directory
# this script compare and deleted files in the "img" directory wrt "imgnbox"

dir_base=/mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d/tmp
dir_img=/mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d/tmp/img
dir_box=/mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d/tmp/imgnbox
dir_scale_upload=/home/adas/git/labeling_tools/scale_submission/code_v2

num_img=$(ls -1 $dir_img | wc | awk '{print $1}')
num_box=$(ls -1 $dir_box | wc | awk '{print $1}')
echo 'img : '$num_img
echo 'box : '$num_box

if [ $num_img == $num_box ]; then
    echo 'same'
else
    echo 'different'
    # list of img files (jpg)
    ls -1 $dir_img | grep jpg > tmp_list_img.txt
    # list of box files (png) - to compare ".png" is deleted
    ls -1 $dir_box | grep png | sed 's#.png##' > tmp_list_box.txt
    # list of the deleted files
    tbd_list=$(diff tmp_list_img.txt tmp_list_box.txt | grep '<' | awk '{print $2}')
    # delete each jpg file
    for each in $tbd_list; do
        echo $each
        rm $dir_img/$each
    done
    ## confirm the numbers
    num_img=$(ls -1 $dir_img | wc | awk '{print $1}')
    num_box=$(ls -1 $dir_box | wc | awk '{print $1}')
    echo 'img : '$num_img
    echo 'box : '$num_box
fi

# (TODO) validate this step
# copy all images to the following directory (for SOTA training)
target_img_dir=/mnt/nfs_pve/DL_data/ml/db/scale/2021q1
cp $dir_img/*.jpg $target_img_dir

## create a list for AWS
# aws_prefix=s3://canoo-adas-label/poc_road_v2/box/setX
ls -1 $dir_img | grep jpg | sed 's#^#s3://canoo-adas-label/poc_road_v2/box/setX/#' > 'aws-filtered-X-'$num_img'.txt'

head $dir_base/aws-filtered-X-$num_img.txt
cp $dir_base/aws-filtered-X-$num_img.txt $dir_scale_upload/
ls -ltr $dir_scale_upload

echo 
echo $dir_base/aws-filtered-X-$num_img.txt' --> /home/adas/git/labeling_tools/scale_submission/code_v2'
echo '(1) use AWS to upload the files'
echo '(2) change the "setX" to the correct set number and upload it' 

cd ~/git/labeling_tools/sampling_tools

echo 'done'
