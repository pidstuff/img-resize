#!/usr/bin/env python

# img_resize.py is a small script that will resize a single image or all images
# within a specified path to fit under a given filesize limit. If unspecified,
# img_resize.py will resize the image to fit under 4 megabytes, the default size.

from io import BytesIO
from PIL import Image

import copy
import getopt
import imghdr
import os
import sys

def image_resize_by_filesize(image, maxfilesize):
    img = Image.open(image)
    
    if img.mode is not 'RGB':
        img = Image.open(image).convert('RGB')
        tmpimg = Image.open(image).convert('RGB')
    else:
        tmpimg = Image.open(image)
    
    width, height = tmpimg.size
    membuffer = BytesIO()
    tmpimg.save(membuffer, format='jpeg')
    tmpimg_filesize = sys.getsizeof(membuffer)
    
    while tmpimg_filesize > maxfilesize:
        membuffer = BytesIO()
        width -= int(width * .01)
        height -= int(height * .01)
        tmpimg = tmpimg.resize((width, height))
        tmpimg.save(membuffer, format='jpeg')
        tmpimg_filesize = sys.getsizeof(membuffer)
    
    img = img.resize((width, height), Image.LANCZOS)
    basename = os.path.basename(image)
    filename = '{0}_{1}.jpg'.format('resized', os.path.splitext(basename)[0])
    filepath = '{0}/{1}'.format(os.path.dirname(image), filename)
    img.save(filepath, format='jpeg', optimize=True)

def print_usage_exit(msg='', code=0):
    if msg:
        print('img_resize.py: {0}\n'.format(msg))
    print('''Usage: {0} [OPTION] -i PATH [-s FILESIZE]
        -h: help
        -v: verbose
        -i: path to image or directory of images
        -s: file size in megabytes (4MB default)'''.format(sys.argv[0]))
    sys.exit(code)

def main(argv):
    images = []
    inputpath = ''
    maxfilesize = '4'
    verbose = False
    
    shortopts = 'hvi:s:'
    longopts = [
        'help',
        'verbose',
        'input=',
        'size='
    ]
    
    try:
        opts, args = getopt.getopt(argv, shortopts, longopts)
    except getopt.GetoptError as e:
        print_usage_exit(e, 1)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print_usage_exit()
        elif opt in ('-v', '--verbose'):
            verbose = True
        elif opt in ('-i', '--input'):
            inputpath = arg
        elif opt in ('-s', '--size'):
            maxfilesize = arg
    
    if not maxfilesize.isdigit():
        print_usage_exit('option -s or --size must be a whole number', 1)
    if not inputpath:
        print_usage_exit('option -i or --input is required', 1)
    if not os.path.exists(inputpath):
        print_usage_exit('option -i or --input requires a valid image or directory', 1)
    if not os.path.isdir(inputpath):
        images.append(inputpath)
    else:
        files = os.listdir(inputpath)
        path = os.path.join(os.getcwd(), inputpath)
        for f in files:
            filepath = os.path.join(path, f)
            if imghdr.what(filepath) in ('jpeg', 'png'):
                images.append(filepath)
    
    maxfilesize = int(maxfilesize) * 1024 * 1024
    for i in images:
        if verbose:
            print('Resizing {0}'.format(i))
        image_resize_by_filesize(i, maxfilesize)

if __name__ == "__main__":
    main(sys.argv[1:])

