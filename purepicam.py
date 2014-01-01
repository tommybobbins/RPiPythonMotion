#!/usr/bin/python

# simple motion-detection using pypi.python.org/pypi/picamera
# runs at up to 10 fps depending on resolution, etc.
# Nov. 30 2013 J.Beale
# Additions by waveform80
# http://www.raspberrypi.org/phpBB3/viewtopic.php?p=470488#p470488


# Some Python 3 compatibility magic...
from __future__ import (
        unicode_literals,
        absolute_import,
        print_function,
        division,
        )
str = type('')

import io, os, time, datetime, picamera, cv2
import numpy as np

#width = 32
#height = 16 # minimum size that works ?
width = 640
height = 480
# Round width and height up to closest multiple of 32 and 16 respectively as
# these are what the camera rounds to internally, and we need these sizes for
# raw-mode captures
fwidth = (width + 31) // 32 * 32
fheight = (height + 15) // 16 * 16
frames = 0
first_frame = True
frac = 0.05       # fraction to update long-term average on each pass
a_thresh = 16.0   # amplitude change detection threshold for any pixel
pc_thresh = 20    # number of pixels required to exceed threshold
avgmax = 3        # long-term average of maximum-pixel-change-value
tfactor = 2       # threshold above max.average diff per frame for motion detect
picHoldoff = 0.2  # minimum interval (seconds) between saving images
fupdate = 100     # report debug data every this many frames
motionpath = "/home/pi/MOTION/"
logfile = motionpath + "cam-log.csv"

np.set_printoptions(precision=2)
with io.open(logfile, 'a') as f:
    f.write("# cam log v0.1 Nov.28 2013 JPB\n")
    f.write("# Start: " +  str(datetime.datetime.now()) + "\n")
    f.flush()

    daytime = datetime.datetime.now().strftime("%y%m%d-%H_%M_%S.%f")
    daytime = daytime[:-3]  # remove last three digits (xxx microseconds)
#    print ("# Start at %s" % str(datetime.datetime.now()))

    stream = io.BytesIO()
    with picamera.PiCamera() as camera:
        camera.resolution = (width, height)
        camera.start_preview()
        time.sleep(2)
        start = time.time()
        # I'd like to use raw_format='RGB' here, but unfortunately that's not
        # currently possible with video-port based captures (the splitter being
        # used to permit simultaneous video and image capture from the
        # video-port doesn't work when the camera's video port is in RGB mode).
        #
        # So, we'll just have to stick to YUV. However, I'm betting that the Y
        # bits alone are probably good enough for motion detection, so instead
        # of bothering with RGB decoding, we'll just grab the first n bytes of
        # the stream (the Y-plane) and discard the rest.
        while True:
            camera.capture(stream, format='raw', use_video_port=True)
            stream.seek(0)
            image = np.fromstring(stream.getvalue(), count=fwidth * fheight, dtype=np.uint8)
            # Now reshape the array into a 2D image, and lop off the unused
            # portions (which resulted from the camera's rounding of the res).
            # There's no longer any need to "decode" the image with OpenCV as
            # an OpenCV image is just a numpy array anyway
            image = image.reshape((fheight, fwidth))[:height, :width].astype(np.float32)
            frames += 1
            if (frames % fupdate) == 0:
                pstr=("%s,  %03d max = %5.3f, avg = %5.3f" % (str(datetime.datetime.now()), frames, max, avgmax))
                f.write(pstr)
                f.flush()
            if first_frame:
                first_frame = False
                # No need to extract green channel anymore as we've only got a
                # grayscale image anyway. Just use the whole image
                avgcol = image
                avgdiff = avgcol / 20.0 # obviously a coarse estimate
            else:
                avgcol = (avgcol * (1.0 - frac)) + (image * frac)
                # Calculate the matrix of difference-from-average pixel values
                # (diff), and the long-term average difference (avgdiff)
                diff = image - avgcol
                diff = abs(diff)
                avgdiff = ((1 - frac) * avgdiff) + (frac * diff)
                # Calculate the adaptive amplitude-of-change threshold (athresh)
                a_thresh = tfactor * avgmax
                condition = diff > a_thresh
                changedPixels = np.extract(condition, diff)
                countPixels = changedPixels.size
                # Find the biggest single-pixel change
                max = np.amax(diff)
                avgmax = ((1 - frac) * avgmax) + (max * frac)
                # A notable change of enough pixels implies motion!
                if countPixels > pc_thresh:
                    now = time.time()
                    interval = now - start
                    start = now
                    daytime = datetime.datetime.now().strftime("%y%m%d-%H_%M_%S.%f")
                    daytime = daytime[:-3]  # remove last three digits (xxx microseconds)
                    daytime = daytime + "_" + str(countPixels)
                    tstr = ("%s,  %04.1f, %6.3f, %03d\n" % (daytime, max, interval, countPixels))
#                    print (tstr, end='')
                    f.write(tstr)
                    f.flush()
                    # Don't write images more quickly than picHoldoff interval
                    if interval > picHoldoff:
                        imgName = motionpath + daytime + ".jpg"
                        cv2.imwrite(imgName, image)  # save as an image
