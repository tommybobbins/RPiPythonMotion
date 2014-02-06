#!/usr/bin/python
import io
import random
import picamera
camera_rotation = 270
from PIL import Image, ImageChops
import io, os, time, datetime, picamera, cv2
import numpy as np
import math, operator
import logging
dt = datetime.datetime.now()
logging.basicConfig(filename='/home/pi/MOTION/securitah_%i_%i_%i.log' %(dt.year, dt.month, dt.day),level=logging.INFO)
camera_resolution = [1280,720]
# Taken from waveform80/Dave Jones' git repository:
# https://github.com/waveform80/picamera/blob/master/docs/recipes2.rst

maximum_rms = 580
prior_image = None

def detect_motion(camera):
    global prior_image
    stream = io.BytesIO()
    camera.rotation = camera_rotation
    camera.capture(stream, format='jpeg', use_video_port=True)
    stream.seek(0)
    if prior_image is None:
        prior_image = Image.open(stream)
        return False
    else:
        current_image = Image.open(stream)
        # Compare current_image to prior_image to detect motion. This is

        diff = ImageChops.difference(current_image, prior_image)
        h = diff.histogram()
        sq = (value*(idx**2) for idx, value in enumerate(h))
        sum_of_squares = sum(sq)
        rms = math.sqrt(sum_of_squares/float(current_image.size[0] * current_image.size[1]))
#        print ("Image size = %i, %i" % (current_image.size[0],current_image.size[1]))
#        rms = math.sqrt(sum_of_squares/float(camera_resolution[0] * camera_resolution[1]))
        dt = datetime.datetime.now()
        if (rms > maximum_rms):
           image_found = 1
           logging.info ("%s Recording. Image variation = %i" % (dt,rms))
#           print ("%s Recording. Image variation = %i" % (dt,rms))
        else:
           image_found = 0
#           logging.info ("%s Not Recording. Image variation = %i" % (dt,rms))
#           print ("%s Not Recording. Image variation = %i" % (dt,rms))
          
#        result = random.randint(0, 10) == 0
        # Once motion detection is done, make the prior image the current
        prior_image = current_image
        return image_found

def write_video(stream):
    # Write the entire content of the circular buffer to disk. No need to
    # lock the stream here as we're definitely not writing to it
    # simultaneously
    filename = time.strftime("/home/pi/MOTION/output%Y%m%d_%H%M%S.h264")
#    print ("Filename = %s" % filename)
    with io.open(filename, 'wb') as output:
        for frame in stream.frames:
            if frame.header:
                stream.seek(frame.position)
                break
        while True:
            buf = stream.read1()
            if not buf:
                break
            output.write(buf)
    # Wipe the circular stream once we're done
    stream.seek(0)
    stream.truncate()

with picamera.PiCamera() as camera:
#    camera.resolution = (camera_resolution[0], camera_resolution[1])
    stream = picamera.PiCameraCircularIO(camera, seconds=10)
    camera.rotation = camera_rotation
    camera.start_recording(stream, format='h264')
    try:
        while True:
            camera.wait_recording(1)
            if detect_motion(camera):
#                print('Motion detected!')
                logging.info ('Motion detected!')
                 # As soon as we detect motion, split the recording to
                 # record the frames "after" motion
                filename = time.strftime("/home/pi/MOTION/outputafter%Y%m%d_%H%M%S.h264")
                camera.split_recording(filename)
                # Write the 10 seconds "before" motion to disk as well
                write_video(stream)
                # Wait until motion is no longer detected, then split
                # recording back to the in-memory circular buffer
                while detect_motion(camera):
                    camera.wait_recording(1)
#                print('Motion stopped!')
                logging.info ("Motion stopped!")
                camera.split_recording(stream)
    finally:
        camera.stop_recording()
