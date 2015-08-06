#!/usr/bin/python
# Written by Oliver Turnbull for EnviroPi project, part of the AstroPi competition

import time
import picamera
from astro_pi import AstroPi
from PIL import Image
import os

# Picamera object and horizontally flips it
camera = picamera.PiCamera()
camera.hflip = True
# Length of experiment in minutes - 6 days
lengthMins = 8640
# Length in secs between taking pictures, taking into account ~2 secs for loop to run
sleepSecs = 28
# Reference to astropi
ap = AstroPi()

# Function to check if image taken is mostly black, returns true if mostly black
def checkBlack(directory):
    im = Image.open(directory)
    # Splits image into pixels
    pixels = im.getdata()
    # RGB threshold at which pixel is defined as 'black'
    blackThresh = 15
    # Number of black pixels in image
    nblack = 0
    # Cycles through pixels, counting number of 'black' pixels
    for pixel in pixels:
        if sum(pixel) < blackThresh:
            nblack +=1
    n = len(pixels)
    # If more than 40% is black, discard image
    if (nblack / float(n)) > 0.4:
        return True
    else:
        return False


def captureImage(camera):
    # Directory to save image - adds timestamp to end of image name
    timeStamp = time.strftime("%d-%m-%Y_%H:%M:%S")
    # Directory to save image to
    directory = ('raw/img_%s.jpg' % timeStamp)
    # Captures and saves image in raw directory
    camera.capture(directory)
    # Checks whether image is mostly black
    if checkBlack(directory):
        # Delete mostly black photo
        os.remove(directory)
        print('Mostly Black')
    else:
        print('not black')

# Main loop run while experiment is happening, captures images
def mainLoop(lengthMins, sleepSecs, camera, astroPi):
    # Converts lenght of experiment from mins to secs
    lengthSecs = lengthMins * 60
    secondsPassed = 0
    # Variable used to uniquely name the images
    x = 0
    # Captures images until seconds passed exceeds experiment length
    while secondsPassed <= lengthSecs:
        currentTime = time.time()
        captureImage(camera)
        # Amount to wait between capturing images (defined at top) and flash red to show running
        ap.clear()
        time.sleep(sleepSecs)
        ap.set_pixel(3, 4, 255, 0, 0)
        ap.set_pixel(3, 3, 255, 0, 0)
        ap.set_pixel(4, 3, 255, 0, 0)
        ap.set_pixel(4, 4, 255, 0, 0)
        x += 1
        secondsPassed += sleepSecs
        print(time.time() - currentTime)
    # Displays completion message
    astroPi.show_message('Completed!')
    time.sleep(10)
    blue = (0,0,255)
    ap.clear(blue)



# Waits for user input (middle button on joystick) before starting and makes LED green
green = (0,255,0)
ap.clear(green)
# Prevens EOF error
try:
    input()
except EOFError:
    print('eof error')
ap.clear()

# 5 second countdown
ap.show_message('5')
time.sleep(1)
ap.show_message('4')
time.sleep(1)
ap.show_message('3')
time.sleep(1)
ap.show_message('2')
time.sleep(1)
ap.show_message('1')
time.sleep(1)
        

# Runs the experiment
mainLoop(lengthMins, sleepSecs, camera, ap)
print('done')

