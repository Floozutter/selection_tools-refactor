"""
implementation of common utils for sampling tools
jongmoo.choi@canoo.com
2020-12-23
"""
import glob
import os

def get_directories(input_path) -> list:
    """Gets all path names given an input data path.

    Args:
        input_path (str): input path

    Returns:
        list: list of path names (str)
    """
    dirs = []
    for path in glob.glob(input_path):
        dirs.append(path)
    return dirs

def get_img_filenames(dir_path) -> list:
    """Gets image filenames given an input directory.

    Args:
        dir_path (str): input path

    Returns:
        list: list of image filenames (str)
    """
    files = []
    for img_path in glob.glob(os.path.join(dir_path, 'video_seq/*.jpg')):
        files.append(img_path)
    return files

def get_img_filenames_sequential(dir_path) -> list:
    """Gets image filenames given an input directory (sequential).

    Args:
        dir_path (str): input path

    Returns:
        list: list of image filenames (str)
    """
    files = []
    for img_path in glob.glob(os.path.join(dir_path, 'video_seq/*.jpg')):
        files.append(img_path)

    # get the min, max frame numbers 
    files.sort()
    min_frame_number = int(files[0].split('/')[-1].split('.jpg')[0])
    max_frame_number = int(files[-1].split('/')[-1].split('.jpg')[0])

    files = []
    for idx in range(min_frame_number, max_frame_number+1):
        filename = os.path.join(dir_path, 'video_seq/'+str(idx)+'.jpg')
        if os.path.isfile(filename):
            files.append(filename)

    return files

def get_img_filenames_sequential_horizon(dir_path) -> list:
    """Gets image filenames given an input directory (sequential).

    Args:
        dir_path (str): input path

    Returns:
        list: list of image filenames (str)
    """
    files = []
    for img_path in glob.glob(os.path.join(dir_path, 'video_seq/*.jpg')):
        files.append(img_path)

    # get the min, max frame numbers 
    files.sort()

    """
    min_frame_number = int(files[0].split('/')[-1].split('.jpg')[0].split('_image_')[0])
    max_frame_number = int(files[-1].split('/')[-1].split('.jpg')[0].split('_image_')[0])

    out_files = []
    for idx in range(min_frame_number, max_frame_number+1):
        filename = os.path.join(dir_path, 'video_seq/'+str(idx)+'.jpg')
        if os.path.isfile(filename):
            out_files.append(filename)
    return out_files
    """
    return files


def get_processed_videonames(filename):
    """Gets all processed video filenames given a txt file.

    Args:
        filename (str): input txt file path

    Returns:
        list: list of video filenames (str)
    """
    with open(filename) as file_id:
        raw = file_id.readlines()
    return [x.rstrip() for x in raw]

def get_sota_detection_videoname(img_full_path):
    """Gets the video filename from an image filepath.

    Args:
        img_full_path (str): input image filepath

    Returns:
        video_name (str): the video filename
    """
    base, _ = img_full_path.split('/video_seq/')
    video_name = base.split('d4t/')[1]
    return video_name

def update_processed_videofile(filename, video_path):
    """Updates the processed videofile (txt file).

    Args:
        filename (str): input txt filepath
        video_path (str): input video filepath

    Returns:
        none
    """
    with open(filename, 'a') as file_id:
        file_id.write('%s\n' % video_path)
