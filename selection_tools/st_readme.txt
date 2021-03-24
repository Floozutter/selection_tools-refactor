[ Overview of filtering process ] 


                                                 (5) hsh2txt ---> $3.txt
                                                         ^
                                                         |
sota  --> (1) dir2txt --> $1.txt ---> (2) txt2hsh --> $2.pickle
                            |                            |
                            |                            V 
                            +------------------> (3) filters ----> $4.txt ---> (4) txt2hsh ---> $5.pickle
                                                         ^    
                                                         |
                                            imghash/*.pickle (existing data)        

sota: image data with sota detection results

[ Processing steps ] 

(0) creating a baseline hash database

st_v1_batch_1_10_create_hash.py

I: /mnt/nfs_pve/Raw_data/data-sampling/data-sampling/brave_cam_sample/labeling_batch_*
O: imghash/st_v1_batch_1_10_hash2img.pickle
   imghash/st_v1_batch_1_10_img2hash.pickle


(1a) st_get_processed_video_aws.py: generating the list of processed videos from the AWS submission directory:

        I: BASE_DIR: /mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d
                     (you don't need to change it)
        O: stdout

+ python3 st_get_processed_video_aws.py > processed.txt

(1) reads all subdirectories under the BASE_DIR (ex: /mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d)
(2) checks each aws_filtered*.txt files
(3) outputs only the video names

(1b) dir2txt: creating a list of source data 

+ python3 st_dir2txt.py > tmp.txt

	I: /mnt/nfs_pve/DL_data/canoo-label-pl-bravecam2k/d4t/*
           data_sampling_processed_videos.txt

        O: tmp.txt
           (appended) data_sampling_processed_videos.txt

(2) txt2hsh: creating hash database from a list of data 

+ python3 st_txt2hsh.py 

	I: tmp.txt (CONST)

	O: tmp_img2hash.pickle
           tmp_hash2img.pickle

(2a) st_aws2hsh.py: creating hash database from the AWS submission directory

        I: BASE_DIR: /mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d
                     (you don't need to change it)

        O: /mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d/set#-#-#-#-#/*.pickle

(3-1) duplicated: filtering similar images using existing reference data (OPTIONAL)

+ python3 st_filter_duplicated.py > dup.txt

	I: tmp.txt (CONST)
           tmp_*.pickle (hash of tmp.txt)
	   imghash/*.pickle (reference data)

	O: dup.txt

(3-2) lowconf: filtering images using low-confidence, ROI, object size

+ python3 st_filter_lowconf.py --in dup.txt --out new.txt

	I: old.txt 
	O: new.txt 

(4) txt2hsh (same as (2))

(5) hsh2txt: filtering similar images inside dataset (not using reference data)

+ python3 st_hsh2txt.py

        I: tmp.txt (CONST)
           tmp_img2hash.pickle
           tmp_hash2img.pickle

        O: print out unique image filenames

(6) txt2img: copy images to a directory

+ python3 st_txt2img.py --in data.txt

	I: data.txt
	O: /tmp/out/*.jpg *.jpg.png (data filenames with videoNames)

           ex: 2000_0101_045930_008.MP4+3276.jpg.png
               (video name)           "+" (frame no)

(7) copy all *.png data into a working directory with GUI

    mkdir sample-1
    cd sample-1
    scp -r adas@192.168.27.6:/tmp/out/*.png .

    make subdirectories if needed (ex: filtered-2-300)

(8) filter only important frames 

    ex: filtered-2-300/*.png contains only the required files for the labeling task

(9) create a list file 
    a: positive set - (ex: filtered-set-300.txt) containting the list of filenames
    
    ex (Windows):
        dir /B > filtered-2-300.txt

/*
    b: negative set for the unseleted filenames (data.txt - filtered-set-1.txt)
       will be using it to check the redundant files later
*/

(10) create a repo for the submission data

    mkdir /mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d/2-2020-01-27-300/
    mkdir /mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d/2-2020-01-27-300/img
    mkdir /mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d/2-2020-01-27-300/imgnbox

(11) copy the list file to the labeling tool directory

    ex: scp filtered-2-300.txt adas@192.168.27.6:/mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d/2-2020-01-27-300
    ex: scp filtered-3-200.txt adas@192.168.27.6:/tmp

(12) copy original frames into a director to submit the Batch data

    cd ~/git/labeling_tools/sampling_tools

    python3 st_imgtxt2imgsub.py --in /mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d/1-2020-01-15-50/filtered-1-50.txt --out /mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d/1-2020-01-15-50/img
    
    reference: directory structure

        ls /mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d/1-2020-01-15-50/
        filtered-1-50.txt  img  imgnbox  poc_v2_s3_list_box_1.txt  sample-1-2835.txt
        /* filtered*.txt and img are mandatory */

    reference: data files
        /mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d/1-2020-01-15-50/img/*.jpg 

(13) copy files to a local directory to use the Web interface

    mkdir set2-300; cd set2-300
    scp -r adas@192.168.27.6:/mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d/2-2020-01-27-300/img/*.jpg .

(14) copy images to AWS

    ex: canoo.okta.com --> AWS --> s3 --> canoo-adas-label --> poc_v2 --> box --> (upload directory)

(15) create the submission text file with the AWS pointers

    ex:
    
    cd /mnt/nfs_pve/DL_data/canoo-filtered/scale-batch-2d/2-2020-01-27-300
    cp filtered-2-300.txt aws-filtered-2-300.txt
    
    target URL: s3://canoo-adas-label/poc_road_v2/box/set2-300/2000_0101_045930_008.MP4+3240.jpg

    (vim) :%s#2000_0108#s3://canoo-adas-label/poc_road_v2/box/set2-300/2000_0108#g

    cp aws-filtered-2-300.txt ~/git/labeling_tools/scale_submission/code_v2/
    cd ~/git/labeling_tools/scale_submission/code_v2/

(16) TBD --------HERE

    python3 submit_two_dim.py aws-filtered-2-300.txt 

(17) update the hash database

    cd ~/git/labeling_tools/sampling_tools
    python3 st_aws2hsh.py


Note 1: dir2txt

        This filtering script has to work with the SOTA detection results
        So, video_seq/*.jpg data should have the sibling directory od_videoseq (*.txt)
	containing the SOTA detection results

	d4t/data directory contains
		bb_videoseq	-- visualization of target objects
		od_videoseq	-- detection results (1) *.jpg.png (2) *.jpg.txt
		video_seq	-- extracted frames (1.jpg ~ N.jpg)

	SOURCE: unprocessed bravecam data (2237 videos)
	/mnt/nfs_pve/Raw_data/data-sampling/data-sampling/brave_cam

	OUTPUT1: processed bravecam data (216 videos)
	/mnt/nfs2/jc/exp/d4t 

	OUTPUT2: new bravecam data processing (80+ videos)
	/mnt/nfs_pve/DL_data/canoo-label-pl-bravecam2k/d4t/

	input txt file can be generated by multiple ways:
	
	e.g., ls -1 /mnt/nfs_pve/DL_data/canoo-label-pl-bravecam2k/d4t/2000_0101_045930_008.MP4/video_seq/5???.jpg > tmp.txt

        e.g., python3 st_dir2txt.py
 

