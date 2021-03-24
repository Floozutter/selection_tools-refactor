"""
jongmoo.choi@canoo.com
2020-2-21

filename: st_dir2txt.py

* Extracts the image filenames from the SOTA detection results.
* (new: It extracts sequentially due to the limitation of the hashing)
* Maintains the processed video names (develop version before 1 batch submission)
* Extracts N videos only at a time

Useage:
   python scale_dir2txt.py >> list.txt
"""
import st_utils as st
import os
import sys
import argparse

INPUT_BRAVECAM = '/mnt/nfs_pve/DL_data/canoo-label-pl-bravecam2k/d4t/*'
INPUT_HORIZON = '/mnt/nfs_pve/canooDev/horizon_unpacked_sota/6_6/ADAS_*'
PROCESSED = 'tmp_processed_aws_updated.txt'
# max_videos = 5

def parse_args():
    parser = argparse.ArgumentParser(description='number of videos to be processed')
    parser.add_argument(
        '--num',
        dest='max_number_of_videos',
        help='number of videos (int)',
        default=None,
        type=str
    )
    #parser.add_argument(
    #    '--in',
    #    dest='in_dir',
    #    help='input img directory (directory path)',
    #    default=None,
    #    type=str
    #)
    #parser.add_argument(
    #    '--out',
    #    dest='dst_file',
    #    help='output img-list file (single file)',
    #    default=None,
    #    type=str
    #)
    parser.add_argument(
        '--type',
        dest='raw_type',
        help='input raw data type (BRAVECAM or HORIZON)',
        default=None,
        type=str
    )
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    return parser.parse_args()

def update_processed_videofile(filename, videopath):
    """Updates processed videofile

    Args:
        filename (str): processed videofile
        videopath (str): input video filepath

    Returns:
        none
    """
    with open(filename, 'a') as file_id:
        file_id.write('%s\n' % videopath)

def run_bravecam(max_videos):
    """Provides image filenames given (1) SOTA directory and (2) processed data.

    Args:
        INPUT: SOTA detection results (see st_readme.txt)
        PROCESSED: txt file containing processed video filenames

    Returns:
        print out the image filenames (full path)
        Ture
    """
    dirs = st.get_directories(INPUT_BRAVECAM)
    imgs = []

    processed = st.get_processed_videonames(PROCESSED)

    cnt_video = 0
    for videopath in dirs:
        # check if it's a valid directory
        if not(os.path.isfile(os.path.join(videopath,'out.avi'))):
            continue

        if cnt_video >= max_videos:
            break
        
        # we are NOT using the full path (using videoName only)
        videoname = videopath.split('/')[-1]
        if not videoname in processed:
            imgs += st.get_img_filenames_sequential(videopath)

            update_processed_videofile(PROCESSED, videoname)
            cnt_video += 1

    for img in imgs:
        print(img)
    return True

def run_horizon(max_videos):
    """Provides image filenames given (1) SOTA results from Horizon unpacked files and (2) processed data.

    Args:
        INPUT: SOTA detection results (see st_readme.txt)
        PROCESSED: txt file containing processed video filenames

    Returns:
        print out the image filenames (full path)
        Ture
    """
    dirs = st.get_directories(INPUT_HORIZON)
    imgs = []

    processed = st.get_processed_videonames(PROCESSED)

    cnt_video = 0
    for videopath in dirs:
        # check if it's a valid directory
        # ASSUME all directories for the Horizon raw data are valid
        if cnt_video >= max_videos:
            break
        
        # we are NOT using the full path (using videoName only)
        videoname = videopath.split('/')[-1]

        if not videoname in processed:
            imgs += st.get_img_filenames_sequential_horizon(videopath)

            update_processed_videofile(PROCESSED, videoname)
            cnt_video += 1

    for img in imgs:
        print(img)
    return True

if __name__ == '__main__':
    args = parse_args()
    max_num_videos = int(args.max_number_of_videos)
    if args.raw_type=='BRAVECAM':
        run_bravecam(max_num_videos)
    elif args.raw_type=='HORIZON':
        run_horizon(max_num_videos)
    else:
        print('wrong raw type', args.raw_type)
    
