# module containing utilities to handle videos and images, in order to create new thumbnail files and save them in the filesystem

from moviepy.editor import *
from PIL import Image


# function useful to generate a thumbnail starting from the filename of the video and the size of the requested thumbnail. Then, the image is saved into dest_path
# the thumbnail is extracted at the first frame of the video
def generate_thumbnail_file_from_video(video_filename, width, height, dest_path):
    clip = VideoFileClip(video_filename)
    frame = clip.get_frame(0)   # first frame
    thumbnail = Image.fromarray(frame).resize((width, height))
    thumbnail.save(dest_path)


# function useful to generate a thumbnail by resizing another thumbnail of the same video. Then, the image is saved into dest_path
def generate_thumbnail_file_from_old(old_thumbnail_path, width, height, dest_path):
    old_image = Image.open(old_thumbnail_path)
    thumbnail = old_image.resize((width, height))
    thumbnail.save(dest_path)