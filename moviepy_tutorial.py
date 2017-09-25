# Import everything needed to edit video clips
from PIL import Image
from moviepy.editor import *

def example1():
    clip1 = VideoFileClip("test1.mp4")
    clip2 = VideoFileClip("test2.mp4").subclip(50,60)
    clip3 = VideoFileClip("test3.mp4")
    final_clip = concatenate_videoclips([clip1,clip2,clip3])
    final_clip.write_videofile("test_output.mp4")

def example2():
    clip1 = VideoFileClip('./test1.mp4')
    i = 1
    for frame in clip1.iter_frames(fps=3, progress_bar=True, dtype='uint8'):
        im = Image.fromarray(frame)
        im.save("frame_image/test_%07d.jpg" % i)
        i += 1

if __name__ == '__main__':
    example2()
