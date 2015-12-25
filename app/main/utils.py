#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import string
import os
import datetime
from app import logger

def allowed_file(file, allowed_extensions):
    """
    :param file: file name
    :param allowed_extensions: file extension
    :return: bool:
    """
    return '.' in file and file.split('.', 1)[1] in allowed_extensions



def safefilename(filename):
    """
    rename the file, support unicode
    :param filename: filename
    :return: new filename
    """
    try:
        extname = filename.split('.')[1]
    except:
        logger.error('illegal filename')
    random_str = ''.join(random.sample(string.ascii_letters + string.digits, 16))
    return '{}.{}'.format(random_str, extname)


def mkdir(dir):
    """
    create the directory
    :param dir: target directory
    :return: directory path string
    """
    if not os.path.exists(dir):
        os.makedirs(dir)
        logger.info('create dir {}'.format(dir))
    return dir


def mkdirbydate(parent, date=None):
    """
    create directory by datetime
    :param parent: target parent
    :param date: datetime or date type
    :return: target directory path string and date directory name
    """
    date_dir = datetime.datetime.now().strftime('%Y-%m-%d') if not date else date.strftime('%Y-%m-%d')
    dir = os.path.join(parent, date_dir)
    return (mkdir(dir), date_dir)

def mkdirbysize(parent, size=50):
    """
    create directory by size
    :param parent: target parent directory
    :param size: new directory named by size
    :return: target directory path string
    """
    size_dir = os.path.join(parent, str(size))
    return mkdir(size_dir)


def thumbnail(width, height, max_length):

    """
    make the picture size to thumbnail
    :param width: picture width
    :param height: picture height
    :param max_length: expect to thumbnail the max length
    :return: new width and height
    """

    max_width = max_height = float(max_length)
    if width > max_width:
        ratio = max_width / width
        width = max_width
        height = height * ratio
    if height > max_height:
        ratio = max_height / height
        height = max_height
        width = width * ratio
    return (int(width), int(height))