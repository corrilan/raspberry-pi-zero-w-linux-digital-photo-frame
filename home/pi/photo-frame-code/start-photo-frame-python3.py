#!/usr/bin/python3.9

# Fonts used in GIMP created overlays are Chilanka and  Courier 10 Pitch

# apt-get install rpd-plym-splash lightdm libmagickwand-dev python3-pip php7.4-mysql php-bcmath php-gd php7.4-xml x11vnc composer git plymouth apache2 php mariadb-server bc unclutter omxplayer python-rpi-gpio python-imaging python-image-tk imagemagick openssh-server vim autossh screen sshfs xidle xdotool nfs-utils impressive exiftran python3-dev libjpeg-dev zlib1g-dev arp-scan

#pip3 install wand asterisk-ami wikidata

# For setting up Raspberry Pi as an access point to facilitate initial configuration
#https://www.raspberrypi.org/documentation/configuration/wireless/access-point.md
#sudo apt-get install dnsmasq hostapd && sudo systemctl stop dnsmasq && sudo systemctl stop hostapd
#sudo apt-get install lighttpd
#update-rc.d dnsmasq disable
#update-rc.d hostapd disable

# For no mouse edit the /usr/bin/startx file and change the defaultserverargs line to: defaultserverargs="-nocursor"

import subprocess
from subprocess import call
import RPi.GPIO as GPIO  
import time
import pygame, pygame.font, pygame.event, pygame.draw, string
from pygame.locals import *
from pygame import mixer
from numpy import random
import os
from os import scandir, walk
from datetime import datetime, timedelta
from threading import Thread
import threading
from shutil import copyfile
import re
#import PIL
from PIL import ExifTags, ImageOps
from PIL import Image as pilimage
import ctypes
from wand.api import library
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image as wandImage
from asterisk.ami import AMIClient
from asterisk.ami import SimpleAction
from asterisk.ami import AMIClientAdapter
import numpy
import mysql.connector
import glob

# Tell Python about C library
library.MagickPolaroidImage.argtypes = (ctypes.c_void_p,  # MagickWand *
                                        ctypes.c_void_p,  # DrawingWand *
                                        ctypes.c_double)  # Double

library.MagickSetImageBorderColor.argtypes = (ctypes.c_void_p,  # MagickWand *
                                              ctypes.c_void_p)  # PixelWand *

# 4 LINES NOT NEEDED IF USING PIR MONITOR SCRIPT
#call(["/usr/bin/tvservice", "-p"])
#call(["/usr/bin/sudo", "systemctl", "restart", "display-manager"])
#os.environ["DISPLAY"] = ":0.0"
#time.sleep(3)
 
# Graphics initialization
WINDOW_WIDTH = 765
WINDOW_HEIGHT = 985
full_screen = True
window_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
print("Going to init pygame")
os.putenv('SDL_VIDEODRIVER', "x11") # Needed if running using framebuffer instead of X Windows
pygame.init()
print("Done init")
display_modes = pygame.display.list_modes() #find available display modes
RESOLUTION = display_modes[0] #pick the native (largest) resolution
SCREEN_ASPECT = RESOLUTION[0] / RESOLUTION[1] #calculate the aspect ratio of the screen for calculating the image resize

if full_screen:
    surf = pygame.display.set_mode(RESOLUTION, HWSURFACE | FULLSCREEN | DOUBLEBUF | NOFRAME)
    global surf_copy
    surf_copy = pygame.Surface(RESOLUTION, HWSURFACE | FULLSCREEN | DOUBLEBUF | NOFRAME)
else:
    surf = pygame.display.set_mode(window_size)

# Options
CODE_PATH = "/home/pi/photo-frame-code"
TAKE_PHOTO_COUNT = 2 # This choice should eventually be selectable via the web interface and stored in database
PHOTO_ORDERING = "DESC" # ASC DESC RAND() This choice should eventually be selectable via the web interface and stored in database

# Display the generated polaroids which stack up
def show_polaroid(screen, i):
    global id_0
    global id_1
    global rotate_by
    global image_rect
    global surf_copy
    global cb_tilt_switch
    global image_dimensions
    global images
   
    image = pygame.image.load("%(CODE_PATH)s/polaroids/polaroid-%(i)s.png" % {'CODE_PATH': CODE_PATH, 'i': i})
    
    image_dimensions = image.get_size() # Get the dimensions of the image
    image_rect = image.get_rect()
    
    GPIO.remove_event_detect(tilt_switch_a_port)
    GPIO.remove_event_detect(tilt_switch_b_port)
    
    # Work out the required image/screen rotation, if any
    check_tilt_switches()

    if TAKE_PHOTO_COUNT == 1:
        if i+1 == 1:
            image_rect.center = ((0.5 * RESOLUTION[0]) - (0.5 * image_dimensions[id_0]), (0.5 * RESOLUTION[1]) - (0.5 * image_dimensions[id_1]))
    if TAKE_PHOTO_COUNT == 2:
        if i+1 == 1:
            image_rect.center = ((0.5 * RESOLUTION[0]) - (0.5 * image_dimensions[id_0]), 30)
            images['1'] = [image]
        if i+1 == 2:
            image_rect.center = ((0.5 * RESOLUTION[0]) - (0.5 * image_dimensions[id_0]), (RESOLUTION[1] - image_dimensions[id_1] - 30))
            images['2'] = [image]
    if TAKE_PHOTO_COUNT == 3:
        if i+1 == 1:
            image_rect.center = ((0.5 * RESOLUTION[0]) - (0.5 * image_dimensions[id_0]), 30)
            images['1'] = [image]
        if i+1 == 2: 
            image_rect.center = ((0.5 * RESOLUTION[0]) - (0.5 * image_dimensions[id_0]), (0.5 * RESOLUTION[1]) - (0.5 * image_dimensions[id_1]))
            images['2'] = [image]
        if i+1 == 3: 
            image_rect.center = ((0.5 * RESOLUTION[0]) - (0.5 * image_dimensions[id_0]), (RESOLUTION[1] - image_dimensions[id_1] - 30))
            images['3'] = [image]

    screen.blit(pygame.transform.rotate(image, rotate_by), image_rect.center)
    pygame.display.update()
    surf_copy.blit(surf, (0,0))
    GPIO.add_event_detect(tilt_switch_a_port, edge=GPIO.BOTH, callback = cb_tilt_switch_a)
    GPIO.add_event_detect(tilt_switch_b_port, edge=GPIO.BOTH, callback = cb_tilt_switch_b)

def create_polaroid():
    global full_photo_list
    global mode
    mode = "polaroid"
    for i in range(TAKE_PHOTO_COUNT):
        if (PHOTO_ORDERING == "RAND()"):
            RANDOM_FILE = random.choice(full_photo_list)
        else:
            RANDOM_FILE = full_photo_list_next()

        #RANDOM_FILE = random.choice(full_photo_list).decode("utf-8")
        #RANDOM_FILE = random.choice(full_photo_list)
        print(RANDOM_FILE)
        
        call(["convert",  "%(RANDOM_FILE)s" % {'RANDOM_FILE': RANDOM_FILE}, "-auto-orient", "-thumbnail", "600x600", "-gravity", "center", "-background", "transparent", "-bordercolor", "white", "%(CODE_PATH)s/polaroids/polaroid-%(i)s.png" % {'CODE_PATH': CODE_PATH, 'i': i}])

        with (wandImage(filename="%(CODE_PATH)s/polaroids/polaroid-%(i)s.png" % {'CODE_PATH': CODE_PATH, 'i': i})) as image:
            with Color('white') as white:
                library.MagickSetImageBorderColor(image.wand, white.resource)
            with Drawing() as annotation:
                # ... Optional caption text here ...
                #polaroid(image, annotation, random.choice([-5.00, 5.00 -10.00, 10.00, -15.00, 15.00]))
                polaroid(image, annotation, numpy.random.uniform(-15, 15))
            image.save(filename="%(CODE_PATH)s/polaroids/polaroid-%(i)s.png" % {'CODE_PATH': CODE_PATH, 'i': i})
        show_polaroid(surf, i)

# Define FX method. See MagickPolaroidImage in wand/magick-image.c
def polaroid(wand, context, angle):
    if not isinstance(wand, wandImage):
        raise TypeError('wand must be instance of Image, not ' + repr(wand))
    if not isinstance(context, Drawing):
        raise TypeError('context must be instance of Drawing, not ' + repr(context))
    library.MagickPolaroidImage(wand.wand,
                                context.resource,
                                angle)

def show_full_screen(img, screen, degrees):
    global pause_display

    image = pygame.image.load(img)
    #image = pygame.transform.rotate(image, 90) 
    image = pygame.transform.rotate(image, degrees)
    
    image_dimensions = image.get_size() # Get the dimensions of the image
    image_aspect = image_dimensions[0] / image_dimensions[1] # Calculate the aspect ratio of the image
    print(image_aspect)
     
    GPIO.remove_event_detect(tilt_switch_a_port)
    GPIO.remove_event_detect(tilt_switch_b_port)

    if image_aspect < SCREEN_ASPECT: #if image is taller than the current screen resolution resize to fit (add black bands to sides)
        display_resolution = (int(image_dimensions[0]/(image_dimensions[1]/RESOLUTION[1])), RESOLUTION[1])
        position = (int((RESOLUTION[0] - display_resolution[0]) / 2), 0) #place in middle of screen
    elif image_aspect > SCREEN_ASPECT: #if image is wider than current screen resolution resize to fit (add black bands to top and bottom)
        display_resolution = (RESOLUTION[0], int(image_dimensions[1]/(image_dimensions[0]/RESOLUTION[0])))
        position = (0, int((RESOLUTION[1] - display_resolution[1]) / 2)) #place in middle of screen
    else: #otherwise just resize to screen resolution
        display_resolution = RESOLUTION
        position = (0,0)

    image = pygame.transform.smoothscale(image, display_resolution) #resize to calculated resolution with smoothing (computational - adds delay (about 20secs on B+)

    #image = aspect_scale(image, screen.get_height(), screen.get_width())
    #image = pygame.transform.scale(image, (screen.get_height(), screen.get_width()))
    #image = pygame.transform.rotate(image, degrees)
    surf.fill(pygame.Color("black"))
    screen.blit(image, position)
    pygame.display.flip()

    GPIO.add_event_detect(tilt_switch_a_port, edge=GPIO.BOTH, callback = cb_tilt_switch_a)
    GPIO.add_event_detect(tilt_switch_b_port, edge=GPIO.BOTH, callback = cb_tilt_switch_b)

    time.sleep(60)
    
    while (pause_display == True):
        print("Display paused...")
        time.sleep(30)

    #for x in range(0,100):
    #    image = pygame.transform.smoothscale(image, (image.get_width() + 2, image.get_height() + 2)) 
    #    surf.fill(pygame.Color("black"))
    #    screen.blit(image, position)
    #    pygame.display.flip()

def create_full_screen():
    global rotate_by
    global mode
    global random_image_file

    global full_photo_list
    
    mode = "fullscreen"

    for i in range(TAKE_PHOTO_COUNT):
        suitable_file_found = 0;
        while (suitable_file_found == 0):
            if (PHOTO_ORDERING == "RAND()"):
                RANDOM_FILE = random.choice(full_photo_list)
            else:
                RANDOM_FILE = full_photo_list_next()

            print(RANDOM_FILE)
            #orientation = exif_data(RANDOM_FILE)
            
            check_tilt_switches()
            
            image = pygame.image.load(RANDOM_FILE)
            random_image_file = image # stored for later use if the screen is rotated by user in fullscreen mode
            if (rotate_by == 90) or (rotate_by == -90):
                print("1")
                print(image.get_width())
                print(image.get_height())
                if (image.get_width() > image.get_height()):
                    suitable_file_found = 1;
                    print("width > height")
                    print("Rolling with it...")
                else:
                    print("Skipping it.")
                    suitable_file_found = 1; # Force showing anyway
            elif (rotate_by == 0) or (rotate_by == 180):
                print("2")
                if (image.get_width() < image.get_height()):
                    suitable_file_found = 1;
                    print("width < height")
                    print("Rolling with it...")
                else:
                    print("Skipping it.")
                    suitable_file_found = 1; # Force showing anyway
 
        show_full_screen(RANDOM_FILE, surf, rotate_by)
            #suitable_file_found = 1;
            #time.sleep(10)

# Function to iterate through the list of photographs to display
def full_photo_list_next():
    global full_photo_list_pointer
    if (full_photo_list_pointer < len(full_photo_list) - 1):
        full_photo_list_pointer = full_photo_list_pointer + 1
    else:
        full_photo_list_pointer = 0
    return (full_photo_list[full_photo_list_pointer])
  
def list_files(path):
    file_list = []
    for entry in scandir(path):
        if not entry.is_dir() and not entry.is_symlink() and (entry.path.decode("utf-8").endswith(".jpg") or entry.path.decode("utf-8").endswith(".JPG") or entry.path.decode("utf-8").endswith(".png") or entry.path.decode("utf-8").endswith(".PNG")):
            file_list.append(entry.path)
        elif entry.is_dir() and not entry.is_symlink():
            file_list.extend(list_files(entry.path))
    return file_list

def list_directories(path):
    dir_list = []
    for entry in scandir(path):
        if entry.is_dir():
            dir_list.append(entry.path)
            dir_list.extend(list_directories(entry.path))
    return dir_list

def exif_data(photopath):
    try:
        image = pilimage.open(photopath)
        exif = image._getexif()
        # Exif tag 274 is the orientation.  6 and 8 are landscape, 1 and 3 are portrait
        #print("exif_data:")
        #print(exif[274])
        #for orientation in ExifTags.TAGS.keys():
        #    if ExifTags.TAGS[orientation]=='Orientation':
        #        break
        #exif=dict(image._getexif().items())

        for tag, value in exif.items():
            decoded = PIL.ExifTags.TAGS.get(tag, tag)
            if decoded == 'Orientation':
                print(decoded, ":", value)
        print("tried")
        #if exif[orientation] == 3:
        #    rotate = 180
        #elif exif[orientation] == 6:
        #    rotate = 270
        #elif exif[orientation] == 8:
        #    rotate = 90
        #return rotate

        #return exif[274]
    except (AttributeError, KeyError, IndexError, TypeError, IOError):
        # cases: image does not have exif data or is not a valid image file
        print("errored")

# Event listener to listen for incoming Asterisk calls and show photograph of the caller
def event_listener(event,**kwargs):
    global rotate_by
    global pause_display
    global contact_path

    if event.name == 'Pickup':
        print("PICKED UP")

    # Detect Asterisk PBX event of incoming telephone call
    if event.name == 'NewCallerid':

        # Pause the display so that standard photographs stop being shown
        pause_display = True

        # Retrieve the caller telephone number from the Asterisk event details 
        CALLER_ID_NUM = event['CallerIDNum']

        # Backup currently showing screen so we can restore after the Asterisk call alert
        image_to_restore = surf.copy()

        # Set the path to the directory containing the callers portrait images and contact details, if any
        contact_path = "/home/pi/photo-frame-code/asterisk/contacts/%(CALLER_ID_NUM)s" % {'CALLER_ID_NUM': CALLER_ID_NUM}

        # Check if the directory exists
        if os.path.isdir(contact_path):
            # Directory does exist so keep the contact_path as previously set
            pass
        else:
            # Directory does not exist so point the contact_path to the directory containing unknown caller details
            contact_path = "/home/pi/photo-frame-code/asterisk/contacts/unknown"

        # Wipe the screen of any existing content
        surf.fill(pygame.Color("black"))

        # Work out the required image/screen rotation, if any
        check_tilt_switches()

        # Draw 2 rectangles around the caller portrait area
        pygame.draw.rect(surf, (65,255,0), (20,20,466,350), 1)
        pygame.draw.rect(surf, (65,255,0), (18,18,470,354), 1)

        # Start thread to display the sequence of portrait photographs of the caller
        thread_caller_portrait = Thread(target = caller_portrait)
        thread_caller_portrait.start()

        # Update the screen to display the incoming Asterisk call alert
        pygame.display.flip()

        # Retrieve the caller telephone number from the Asterisk event details 
        #caller_number = event['CallerIDNum'] + " "

        # Read the contact details of the caller into an array and append blank line and caller telephone number
        with open("%s/contact-details.txt" % contact_path) as contact_details:
            text = contact_details.read().splitlines()
        text.append("")
        text.append(CALLER_ID_NUM + " ")

        # Start thread to type out the caller details
        thread_caller_details = Thread(target = display_typed_text, args = (surf, text, 50, 2.5, 65, 255, 0, False, False))
        thread_caller_details.start()

        # Display the Asterisk call alert for 45 seconds, possibly make it so stays until call is ended.
        time.sleep(45)

        # Unpause the display so that standard photographs may resume being shown
        pause_display = not pause_display

        # Wipe the screen and then restore the photograph that was showing before incoming call
        surf.fill(pygame.Color("black"))
        surf.blit(image_to_restore, (0,0))
        pygame.display.flip()

# Display the portrait photographs of the caller - called as a thread
def caller_portrait():
    global rotate_by
    global contact_path
    global pause_display
    while (pause_display == True):
        for i in range(1,5):
            if (pause_display == False):
                break
            caller_portrait = pygame.image.load(contact_path + "/%s.jpg" % i)
            surf.blit(pygame.transform.rotate(caller_portrait, rotate_by), (25, 25))
            pygame.display.update((25,25,540,456))
            time.sleep(1)

# Display contact details of the caller - called as a thread
def display_typed_text(screen, message, size, screen_divide, red, green, blue, bold, italic):
    global rotate_by
    global pause_display
    x = 0
    y = 0
    fontobject=pygame.font.SysFont('monospace', size, bold=bold, italic=italic)
    if len(message) != 0:
        previous_typed_text_screen = pygame.Surface((350,700)) # Backup currently showing screen so we can restore
        previous_typed_text_screen.blit(surf, (0,0), (15,560,350,700))
        for idx,line in enumerate(message):
            label = []
            x = (5 +(idx*size))
            for letter in line:
                label.append(fontobject.render(letter, 1, (red, green, blue)))
            for character in range(len(label)):
                surf.blit(previous_typed_text_screen, (15,560))
                screen.blit(pygame.transform.rotate(label[character], rotate_by), (x, 1225 -(character*size)))
                pygame.display.update((15,560,350,700))
                previous_typed_text_screen.blit(surf, (0,0), (15,560,350,700)) # Backup currently showing screen so we can restore
                pygame.draw.rect(surf, (65,255,0), (x+5,y-50,40,25))
                pygame.display.update((15,560,350,700))
            # If this is the last word, remove the previously plotted cursor
            if (idx == 6):
                pygame.draw.rect(surf, (0,0,0), (x+5,y-50,40,25))

    # Plot the flashing cursor at the end
    y = 1225 -((len(label)-2)*size)
    while (pause_display == True):
        pygame.draw.rect(surf, (65,255,0), (x+5,y-30,40,25)) # Flash on
        pygame.display.update((x+5,y-30,40,25))
        time.sleep(0.5)
        if (pause_display == False):
            break
        pygame.draw.rect(surf, (0,0,0), (x+5,y-30,40,25)) # Flash off
        pygame.display.update((x+5,y-30,40,25))
        time.sleep(0.5)
        
def check_tilt_switches():
    global id_0
    global id_1
    global rotate_by
    global tilt_switch_a_port
    global tilt_switch_b_port
    global tilt_switch_a
    global tilt_switch_b
    global last_plot_orientation
    global last_plot_rotate_by

    tilt_switch_a = GPIO.input(tilt_switch_a_port)
    tilt_switch_b = GPIO.input(tilt_switch_b_port)
    
    if (tilt_switch_a == 0 and tilt_switch_b == 1):
        id_0 = 0
        id_1 = 1
        rotate_by = 0
        last_plot_orientation = "portrait"
        last_plot_rotate_by = 0
    elif (tilt_switch_a == 1 and tilt_switch_b == 1):
        id_0 = 1
        id_1 = 0
        rotate_by = -90
        last_plot_orientation = "landscape"
        last_plot_rotate_by = -90
    elif (tilt_switch_a == 1 and tilt_switch_b == 0):
        id_0 = 0
        id_1 = 1
        rotate_by = 180
        last_plot_orientation = "portrait"
        last_plot_rotate_by = 180
    elif (tilt_switch_a == 0 and tilt_switch_b == 0):
        id_0 = 1
        id_1 = 0
        rotate_by = 90
        last_plot_orientation = "landscape"
        last_plot_rotate_by = 90

    print("A is", tilt_switch_a)
    print("B is", tilt_switch_b)
    print("Rotate is", rotate_by)

def check_tilt_switches_immediate_rotate(channel):
    global id_0
    global id_1
    global rotate_by
    global tilt_switch_a_port
    global tilt_switch_b_port
    global tilt_switch_a
    global tilt_switch_b
    global surf_copy
    global last_plot_orientation
    global last_plot_rotate_by
    global images
    global mode
    blit_surf_copy = False

    if (channel == tilt_switch_a_port):
        GPIO.remove_event_detect(tilt_switch_b_port)
        print("Removing handler for b")
    else:
        GPIO.remove_event_detect(tilt_switch_a_port)
        print("Removing handler for a")

    if (mode == "fullscreen"):
        immediate_rotate_full_screen()
    
    if (mode == "polaroid"):
        image_dimensions = surf_copy.get_size() # Get the dimensions of the image
        image_rect = surf_copy.get_rect()
        
        # images dictionary:
        #   kay (1,2,3)
        #       value [imagefile, dimensions, rect]
        if (TAKE_PHOTO_COUNT > 1):
            for key in images:
                images_array = images[key]
                print(images_array)
                dimensions = images_array[0].get_size() # Get the dimensions of the image
                rect = images_array[0].get_rect()
                
                if len(images_array) < 3:
                    images_array.append(dimensions)
                    images_array.append(rect)
                else:
                    images_array[1] = dimensions
                    images_array[2] = rect
                images[key] = images_array

        #for key in images:
        #    images_array = images[key]
        #    print(images_array)
                
        new_tilt_switch_a = GPIO.input(tilt_switch_a_port)
        new_tilt_switch_b = GPIO.input(tilt_switch_b_port)

        if (new_tilt_switch_a != tilt_switch_a) or (new_tilt_switch_b != tilt_switch_b):
            if (new_tilt_switch_a == 0 and new_tilt_switch_b == 1):
                print("switch 1")
                id_0 = 0
                id_1 = 1
                if last_plot_rotate_by == 0:
                    rotate_by = 0
                    image_rect.center = (0,0)
                if last_plot_rotate_by == 180:
                    rotate_by = 180
                    image_rect.center = (0,0)
                if last_plot_rotate_by == 90:
                    rotate_by = -90
                    if TAKE_PHOTO_COUNT > 1:
                        rotate_by = 0
                    image_rect.center = ((0.5 * RESOLUTION[0]) - (0.5 * image_dimensions[id_1]), (0.5 * RESOLUTION[1]) - (0.5 * image_dimensions[id_0]))
                if last_plot_rotate_by == -90:
                    rotate_by = 90
                    if TAKE_PHOTO_COUNT > 1:
                        rotate_by = 0
                    image_rect.center = ((0.5 * RESOLUTION[0]) - (0.5 * image_dimensions[id_1]), (0.5 * RESOLUTION[1]) - (0.5 * image_dimensions[id_0]))
                if TAKE_PHOTO_COUNT > 1:
                    print("0")
                    if (last_plot_orientation == "portrait"):
                        blit_surf_copy = True
                    else:
                        for key in images:
                            images_array = images[key]
                            dim = images_array[1]
                            print(key)
                            if (key == "1"):
                                y_coord = 30
                            elif (key == str(len(images))):
                                y_coord = (RESOLUTION[1] - dim[id_1] - 30)
                            else:
                                y_coord = (0.5 * RESOLUTION[1]) - (0.5 * dim[id_1])
                            images_array[2].center = ((0.5 * RESOLUTION[0]) - (0.5 * dim[id_0]), y_coord)
            elif (new_tilt_switch_a == 1 and new_tilt_switch_b == 1):
                print("switch 2")
                id_0 = 1
                id_1 = 0
                if last_plot_rotate_by == 0:
                    rotate_by = -90
                    image_rect.center = ((0.5 * RESOLUTION[0]) - (0.5 * image_dimensions[id_0]), (0.5 * RESOLUTION[1]) - (0.5 * image_dimensions[id_1]))
                if last_plot_rotate_by == 180:
                    rotate_by = 90
                    if TAKE_PHOTO_COUNT > 1:
                        rotate_by = -90
                    image_rect.center = ((0.5 * RESOLUTION[0]) - (0.5 * image_dimensions[id_0]), (0.5 * RESOLUTION[1]) - (0.5 * image_dimensions[id_1]))
                if last_plot_rotate_by == 90:
                    rotate_by = 180
                    image_rect.center = ((0.5 * RESOLUTION[0]) - (0.5 * image_dimensions[id_1]), (0.5 * RESOLUTION[1]) - (0.5 * image_dimensions[id_0]))
                if last_plot_rotate_by == -90:
                    rotate_by = 0
                    image_rect.center = (0,0)
                if TAKE_PHOTO_COUNT > 1:
                    print("-90")
                    if (last_plot_orientation == "landscape"):
                        blit_surf_copy = True
                    else:
                        for key in images:
                            images_array = images[key]
                            dim = images_array[1]
                            print(key)
                            if (key == "1"):
                                y_coord = 30
                            elif (key == str(len(images))):
                                y_coord = (RESOLUTION[1] - dim[id_1] - 30)
                            else:
                                y_coord = (0.5 * RESOLUTION[1]) - (0.5 * dim[id_1])
                            images_array[2].center = ((0.5 * RESOLUTION[0]) - (0.5 * dim[id_0]), y_coord)
            elif (new_tilt_switch_a == 1 and new_tilt_switch_b == 0):
                print("switch 3")
                id_0 = 0
                id_1 = 1
                if last_plot_rotate_by == 0:
                    rotate_by = 180
                    image_rect.center = (0,0)
                if last_plot_rotate_by == 180:
                    rotate_by = 0
                    image_rect.center = (0,0)
                if last_plot_rotate_by == 90:
                    rotate_by = 90
                    if TAKE_PHOTO_COUNT > 1:
                        rotate_by = 180
                    image_rect.center = ((0.5 * RESOLUTION[0]) - (0.5 * image_dimensions[id_1]), (0.5 * RESOLUTION[1]) - (0.5 * image_dimensions[id_0]))
                if last_plot_rotate_by == -90:
                    rotate_by = -90
                    if TAKE_PHOTO_COUNT > 1:
                        rotate_by = 180
                    image_rect.center = ((0.5 * RESOLUTION[0]) - (0.5 * image_dimensions[id_1]), (0.5 * RESOLUTION[1]) - (0.5 * image_dimensions[id_0]))
                if TAKE_PHOTO_COUNT > 1:
                    print("180")
                    if (last_plot_orientation == "portrait"):
                        blit_surf_copy = True
                    else:
                        for key in images:
                            images_array = images[key]
                            dim = images_array[1]
                            print(key)
                            if (key == "1"):
                                y_coord = 30
                            elif (key == str(len(images))):
                                y_coord = (RESOLUTION[1] - dim[id_1] - 30)
                            else:
                                y_coord = (0.5 * RESOLUTION[1]) - (0.5 * dim[id_1])
                            images_array[2].center = ((0.5 * RESOLUTION[0]) - (0.5 * dim[id_0]), y_coord)
            elif (new_tilt_switch_a == 0 and new_tilt_switch_b == 0):
                print("switch 4")
                id_0 = 0
                id_1 = 1
                if last_plot_rotate_by == 0:
                    rotate_by = 90
                    image_rect.center = ((0.5 * RESOLUTION[0]) - (0.5 * image_dimensions[id_1]), (0.5 * RESOLUTION[1]) - (0.5 * image_dimensions[id_0]))
                if last_plot_rotate_by == 180:
                    rotate_by = -90
                    if TAKE_PHOTO_COUNT > 1:
                        rotate_by = 90
                    image_rect.center = ((0.5 * RESOLUTION[0]) - (0.5 * image_dimensions[id_1]), (0.5 * RESOLUTION[1]) - (0.5 * image_dimensions[id_0]))
                if last_plot_rotate_by == 90:
                    rotate_by = 0
                    image_rect.center = (0,0)
                if last_plot_rotate_by == -90:
                    rotate_by = 180
                    image_rect.center = (0,0)
                if TAKE_PHOTO_COUNT > 1:
                    print("90")
                    if (last_plot_orientation == "landscape"):
                        blit_surf_copy = True
                    else:
                        for key in images:
                            images_array = images[key]
                            dim = images_array[1]
                            print(key)
                            if (key == "1"):
                                y_coord = 30
                                print("a")
                            elif (key == str(len(images))):
                                y_coord = (RESOLUTION[1] - dim[id_0] - 30)
                                print("b")
                            else:
                                y_coord = (0.5 * RESOLUTION[1]) - (0.5 * dim[id_1])
                                print("c")
                            images_array[2].center = ((0.5 * RESOLUTION[0]) - (0.5 * dim[id_1]), y_coord)
            surf.fill(pygame.Color("black"))

            if ((TAKE_PHOTO_COUNT == 1) or (blit_surf_copy == True)):
                surf.blit(pygame.transform.rotate(surf_copy, rotate_by), image_rect.center)
            
            if ((TAKE_PHOTO_COUNT > 1) and (blit_surf_copy == False)):
                for key in images:
                    images_array = images[key]
                    surf.blit(pygame.transform.rotate(images_array[0], rotate_by), images_array[2].center)

            pygame.display.update()
            print("Immediate Rotate")
            print("A is", tilt_switch_a)
            print("B is", tilt_switch_b)
            print("Rotate is", rotate_by)
            print("Channel is", channel)
            tilt_switch_a = new_tilt_switch_a
            tilt_switch_b = new_tilt_switch_b

    print("Checked immediate rotate")
    if (channel == tilt_switch_a_port):
        GPIO.add_event_detect(tilt_switch_b_port, edge=GPIO.BOTH, callback = cb_tilt_switch_b)
        print("Enabling handler for b")
    else:
        GPIO.add_event_detect(tilt_switch_a_port, edge=GPIO.BOTH, callback = cb_tilt_switch_a)
        print("Enabling handler for a")
 
def immediate_rotate_full_screen():
    global rotate_by
    global random_image_file
    screen = surf
    check_tilt_switches()
    #NEED TO SPEED UP THE FULL SCREEN ROTATION SYSTEM BY MAKING SIMILAR TO THE POLAROID ROTATION SYSTEM IDEALLY 
    image = random_image_file
    image = pygame.transform.rotate(image, rotate_by)
    
    image_dimensions = image.get_size() # Get the dimensions of the image
    image_aspect = image_dimensions[0] / image_dimensions[1] # Calculate the aspect ratio of the image
    print(image_aspect)
     
    if image_aspect < SCREEN_ASPECT: #if image is taller than the current screen resolution resize to fit (add black bands to sides)
        display_resolution = (int(image_dimensions[0]/(image_dimensions[1]/RESOLUTION[1])), RESOLUTION[1])
        position = (int((RESOLUTION[0] - display_resolution[0]) / 2), 0) #place in middle of screen
    elif image_aspect > SCREEN_ASPECT: #if image is wider than current screen resolution resize to fit (add black bands to top and bottom)
        display_resolution = (RESOLUTION[0], int(image_dimensions[1]/(image_dimensions[0]/RESOLUTION[0])))
        position = (0, int((RESOLUTION[1] - display_resolution[1]) / 2)) #place in middle of screen
    else: #otherwise just resize to screen resolution
        display_resolution = RESOLUTION
        position = (0,0)

    image = pygame.transform.smoothscale(image, display_resolution) #resize to calculated resolution with smoothing (computational - adds delay (about 20secs on B+)

    surf.fill(pygame.Color("black"))
    screen.blit(image, position)
    pygame.display.flip()

class ButtonHandler(threading.Thread):
    def __init__(self, pin, func, edge='both', bouncetime=200):
        super().__init__(daemon=True)

        self.edge = edge
        self.func = func
        self.pin = pin
        self.bouncetime = float(bouncetime)/1000

        self.lastpinval = GPIO.input(self.pin)
        self.lock = threading.Lock()

    def __call__(self, *args):
        if not self.lock.acquire(blocking=False):
            return

        t = threading.Timer(self.bouncetime, self.read, args=args)
        t.start()

    def read(self, *args):
        pinval = GPIO.input(self.pin)
        
        if (
            ((pinval == 0 and self.lastpinval == 1) and
            (self.edge in ['falling', 'both'])) or
            ((pinval == 1 and self.lastpinval == 0) and
            (self.edge in ['rising', 'both']))
        ):
            self.func(*args)

        self.lastpinval = pinval
        self.lock.release()

def test_tilt_switches():
    global tilt_switch_a_port
    global tilt_switch_b_port
    
    tilt_switch_a = GPIO.input(tilt_switch_a_port)
    tilt_switch_b = GPIO.input(tilt_switch_b_port)

    print("A is", tilt_switch_a)
    print("B is", tilt_switch_b)
    time.sleep(1)

#def factory_reset_system(self):
#    print("Would factory reset here.")

    # Reset screen off timeout to 15 minutes
    # CODE NOT YET WRITTEN
   
    # Reset any other user configured settings
    # CODE NOT YET WRITTEN
 
    # Replace existing /etc/hosts and /etc/hostname with default factory versions
    #call(["/usr/bin/sudo", "/bin/cp", "/etc/hosts.FACTORY", "/etc/hosts"])
    #call(["/usr/bin/sudo", "/bin/cp", "/etc/hostname.FACTORY", "/etc/hostname"])
    
    # Enable both dnsmasq and hostapd to facilitate initial setup
    #call(["/usr/bin/sudo", "/usr/sbin/update-rc.d", "dnsmasq", "enable"])
    #call(["/usr/bin/sudo", "/usr/sbin/update-rc.d", "hostapd", "enable"])
    
    # Finally, reboot the Raspberry Pi with the restored factory configuration
    #call(["/usr/bin/sudo", "/sbin/reboot"])

#def halt_system(self):
#    call(["/usr/bin/sudo", "/sbin/halt"])

def populate_photo_list():
    global full_photo_list
    #global generated_full_photo_list

    # Iterate through photos directory and create a list of all available photographs
    # List generation currently takes around 3.5 minutes as there is a ton of photos
    
    dirName = "%(CODE_PATH)s/photos" % {'CODE_PATH': CODE_PATH}
    
    full_directory_list = list_directories(dirName)
    RANDOM_DIRECTORY = random.choice(full_directory_list)
    
    # Log the current random directory to an external file for debugging purposes
    with open("/home/pi/photo-frame-code/path-log.txt", "a") as myfile:
        myfile.write(RANDOM_DIRECTORY+"\n")
        myfile.close()
    
    print(RANDOM_DIRECTORY)
    full_photo_list = list_files(RANDOM_DIRECTORY)
    #generated_full_photo_list = True
    #full_photo_list = list_files(dirName)

def populate_photo_list_from_lychee():
    global full_photo_list
    mydb = mysql.connector.connect(
            host="localhost",
            user="lycheedbuser",
            password="lycheedbpassword",
            database="lychee"
    )

    myalbumscursor = mydb.cursor()

    # Select all photos from the random album and order randomly
    #myphotoscursor.execute("SELECT CONCAT('/var/www/Lychee/public/uploads/big/', url) FROM photos WHERE album_id=%s ORDER BY RAND()" % album)
    myphotoscursor.execute("SELECT url FROM photos WHERE album_id=%s ORDER BY RAND()" % album)

    myphotosresult = myphotoscursor.fetchall()
    
    # Check if an album has been returned as 0 may exist
    if myalbumsresult:
        myphotoscursor = mydb.cursor()

        for x in myalbumsresult:
            album=(x[0])

        # Select all photos from the random album and order randomly
        #myphotoscursor.execute("SELECT CONCAT('/var/www/Lychee/public/uploads/big/', url) FROM photos WHERE album_id=%s ORDER BY RAND()" % album)
        #myphotoscursor.execute("SELECT url FROM photos WHERE album_id=%s ORDER BY RAND()" % album) # Order by random
        myphotoscursor.execute("SELECT url, taken_at FROM photos WHERE album_id=%s ORDER BY taken_at DESC" % album) # Order by taken date/time in descending 

        myphotosresult = myphotoscursor.fetchall()

        # Delete the hardlinks to all photos from the previous run
        files = glob.glob('%(CODE_PATH)s/live-hardlinked-lychee-photos/*' % {'CODE_PATH': CODE_PATH})
        for f in files:
            os.remove(f)

        for x in myphotosresult:
            # Create hardlink to the original Lychee photograph so if anyone deletes it from Lychee, the frame will not crash
            os.link('/var/www/Lychee/public/uploads/big/%s' % x[0], '%(CODE_PATH)s/live-hardlinked-lychee-photos/%(FILE)s' % {'CODE_PATH': CODE_PATH, 'FILE': x[0]})
            #full_photo_list.append(x[0])
            full_photo_list.append('%(CODE_PATH)s/live-hardlinked-lychee-photos/%(FILE)s' % {'CODE_PATH': CODE_PATH, 'FILE': x[0]})
            
def check_existence_of_lychee_album_and_photo():
    mydb = mysql.connector.connect(
            host="localhost",
            user="lychee",
            password="lychee2021!",
            database="lychee"
    )

    myalbumscursor = mydb.cursor()

    # Select a random album from the Lychee database
    myalbumscursor.execute("SELECT id FROM albums LIMIT 1")

    myalbumsresult = myalbumscursor.fetchall()

    # Check if an album has been returned as 0 may exist
    if myalbumsresult:
        return (True)
    else:
        return (False)
      
def setup():
    global full_photo_list
    global endtime
    global id_0
    global id_1
    global rotate_by
    global tilt_switch_a_port
    global tilt_switch_b_port
    global tilt_switch_a
    global tilt_switch_b
    global image_rect
    global cb_tilt_switch_a
    global cb_tilt_switch_b
    global image_dimensions
    global images
    #global halt_switch_port
    #global factory_reset_switch_port
    global generated_full_photo_list
    global pause_display
    global mode
    global contact_path
    global full_photo_list_pointer
    
    images = {}

    # Hide the mouse pointer in PyGame
    pygame.mouse.set_visible(0)

    # Iterate through photos directory and create a list of all available photographs
    # List generation currently takes around 3.5 minutes as there is a ton of photos
    #dirName = "%(CODE_PATH)s/photos" % {'CODE_PATH': CODE_PATH}
    #full_photo_list = list_files(dirName)
    #full_photo_list = ""
    full_photo_list = []
    full_photo_list_pointer = -1
    
    pause_display = False

    client = AMIClient(address='192.168.2.1',port=5038)
    client.login(username='YourAMIUserHere',secret='YourAMIPasswordHere')
  
    client.add_event_listener(event_listener)
    
    tilt_switch_a_port = 7
    tilt_switch_b_port = 8
    #halt_switch_port = 2
    #factory_reset_switch_port = 26
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(tilt_switch_a_port, GPIO.IN, pull_up_down = GPIO.PUD_UP) # Read output from tilt switch
    GPIO.setup(tilt_switch_b_port, GPIO.IN, pull_up_down = GPIO.PUD_UP) # Read output from tilt switch
    #GPIO.setup(halt_switch_port, GPIO.IN) # Read output from halt switch
    #GPIO.setup(factory_reset_switch_port, GPIO.IN, pull_up_down = GPIO.PUD_UP) # Read output from factory reset switch
    
    cb_tilt_switch_a = ButtonHandler(tilt_switch_a_port, check_tilt_switches_immediate_rotate, edge='both', bouncetime=300)
    cb_tilt_switch_a.start()
    cb_tilt_switch_b = ButtonHandler(tilt_switch_b_port, check_tilt_switches_immediate_rotate, edge='both', bouncetime=300)    # Select all photos from the random album and order randomly
    #myphotoscursor.execute("SELECT CONCAT('/var/www/Lychee/public/uploads/big/', url) FROM photos WHERE album_id=%s ORDER BY RAND()" % album)
    myphotoscursor.execute("SELECT url FROM photos WHERE album_id=%s ORDER BY RAND()" % album)

    myphotosresult = myphotoscursor.fetchall()
    
    # Delete the hardlinks to all photos from the previous run
    files = glob.glob('%(CODE_PATH)s/live-hardlinked-lychee-photos/*' % {'CODE_PATH': CODE_PATH})
    for f in files:
        os.remove(f)

    for x in myphotosresult:
        # Create hardlink to the original Lychee photograph so if anyone deletes it from Lychee, the frame will not crash
        os.link('/var/www/Lychee/public/uploads/big/%s' % x[0], '%(CODE_PATH)s/live-hardlinked-lychee-photos/%(FILE)s' % {'CODE_PATH': CODE_PATH, 'FILE': x[0]})
        #full_photo_list.append(x[0])
        full_photo_list.append('%(CODE_PATH)s/live-hardlinked-lychee-photos/%(FILE)s' % {'CODE_PATH': CODE_PATH, 'FILE': x[0]})

    cb_tilt_switch_b.start()
    #cb_halt_switch = ButtonHandler(halt_switch_port, halt_system, edge='falling', bouncetime=50)
    #cb_halt_switch.start()
    #cb_factory_reset_switch = ButtonHandler(factory_reset_switch_port, factory_reset_system, edge='falling', bouncetime=50)
    #cb_factory_reset_switch.start() 
    #GPIO.add_event_detect(halt_switch_port, edge=GPIO.FALLING, callback = cb_halt_switch)
    #GPIO.add_event_detect(factory_reset_switch_port, edge=GPIO.FALLING, callback = cb_factory_reset_switch)
    
    #generated_full_photo_list = False
    
    print("Ready.")

    while True:

        # If we are in access point host mode and also no albums exist, display graphic instructing owner to either connect to own wifi or upload photographs and use offline   
        if (os.path.isfile("/etc/raspiwifi/host_mode") and not check_existence_of_lychee_album_and_photo()):
            image = pygame.image.load("/home/pi/photo-frame-code/instructions/digital-photo-frame-host-mode-instructions.png")
            image = pygame.transform.rotate(image, 90)
            image_dimensions = image.get_size() # Get the dimensions of the image
            image_aspect = image_dimensions[0] / image_dimensions[1] # Calculate the aspect ratio of the image
            surf.fill(pygame.Color("black"))
            surf.blit(image, (0, 0))
            pygame.display.flip()
            time.sleep(30)

        else:
            while len(full_photo_list) == 0: # Keep checking file location until we have some photos to show
                print("No photos found, scanning...")
                #populate_photo_list()
                populate_photo_list_from_lychee()
                print("Full photo list now populated...")
                time.sleep(30)
            #create_polaroid() # Once we have photos to show, start displaying them
            create_full_screen()
            #test_tilt_switches()

setup()
