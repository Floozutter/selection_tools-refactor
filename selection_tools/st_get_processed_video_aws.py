import glob
import os

"""
This script outputs the list of processed video names from the AWS submission directory:

ex: 

(1) reads all subdirectories under the BASE_DIR (ex: /mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d)
(2) checks each aws_filtered*.txt files
(3) outputs only the video names

python3 st_get_processed_video_aws.py > processed.txt

"""

BASE_DIR = '/mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d'
dir_list = glob.glob(os.path.join(BASE_DIR,"set*"))

all_list = set()

for each in dir_list:
    dir_name = each.split('/scale-batch-2d/')[1]

    # check the aws submission file
    aws_file = glob.glob(each + '/aws-filtered*.txt')[0]
    print(aws_file)

    if os.path.isfile(aws_file):
        with open(aws_file) as f:
            filelist = f.readlines()
        for data in filelist:
            all_list.add(data.split('/')[-1].split('+')[0])
    else:
        print(each, 'no files!')

# print(all_list)
# print(len(all_list))
for video in all_list:
    print(video)
