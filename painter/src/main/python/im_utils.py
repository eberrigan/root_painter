"""
Copyright (C) 2020 Abraham George Smith

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

# pylint: disable=C0111, W0511
import os
import warnings
import glob
import sys

import numpy as np
from PyQt5 import QtGui
from skimage import color
from skimage.io import imread, imsave
from skimage import img_as_ubyte
from skimage import img_as_float
from skimage.transform import resize
from skimage.color import rgb2gray
import qimage2ndarray
from PIL import Image, ImageOps

def is_image(fname):
    extensions = {".jpg", ".png", ".jpeg", '.tif', '.tiff'}
    return any(fname.lower().endswith(ext) for ext in extensions)


def all_image_paths_in_dir(dir_path):
    root_dir = os.path.abspath(dir_path)
    all_paths = glob.iglob(root_dir + '/**/*', recursive=True)
    image_paths = []
    for p in all_paths:
        name = os.path.basename(p)
        if name[0] != '.':
            ext = os.path.splitext(name)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.tif', '.tiff']:
                image_paths.append(p)
    return image_paths




def fpath_to_pixmap(fpath):
    """ Load image from fpath and convert to a PyQt5 pixmap object """
    np_im = load_image(fpath)
    # some (png) images were float64 and appeared very 
    # dark after conversion to pixmap.
    # convert to int8 to fix.
    np_im = img_as_ubyte(np_im) 
    q_image = qimage2ndarray.array2qimage(np_im)
    return QtGui.QPixmap.fromImage(q_image)

def load_image(photo_path):
    #photo = imread(photo_path)
    photo = Image.open(photo_path)
    photo = ImageOps.exif_transpose(photo)
    photo = np.array(photo)
    # sometimes photo is a list where first element is the photo
    if len(photo.shape) == 1:
        photo = photo[0]

    # JFIF files have an extra dimension at the start containing two elements
    # The first element is the image.
    if len(photo.shape) == 4 and photo.shape[0] == 2:
        photo = photo[0]

    # if 4 channels then convert to rgb
    # (presuming 4th channel is alpha channel)
    if len(photo.shape) > 2 and photo.shape[2] == 4:
        photo = color.rgba2rgb(photo)

    # if image is black and white then change it to rgb
    # TODO: train directly on B/W instead of doing this conversion.
    if len(photo.shape) == 2:
        photo = color.gray2rgb(photo)
    return photo


def save_masked_image(seg_dir, image_dir, output_dir, fname):
    """ useful for using segmentations to remove irrelvant information in an image
        as part of a pre-processing stage """
    seg = imread(os.path.join(seg_dir, fname))
    # use alpha channel if rgba
    if len(seg.shape) > 2:
        seg = seg[:, :, 2]
    im_path = os.path.join(image_dir, os.path.splitext(fname)[0]) + '.*'
    glob_results = glob.glob(im_path)
    if glob_results:
        im = imread(glob_results[0])
        im[seg==0] = 0 # make background black.
        imsave(os.path.join(output_dir, os.path.splitext(fname)[0] + '.jpg'), im, quality=95)

def save_corrected_segmentation(annot_fpath, seg_dir, output_dir):
    """assign the annotations (corrections) to the segmentations. This is useful
       to obtain more accurate (corrected) segmentations."""
    fname = os.path.basename(annot_fpath)
    seg = img_as_float(imread(os.path.join(seg_dir, fname)))
    annot = img_as_float(imread(annot_fpath))
    fg = annot[:, :, 0]
    bg = annot[:, :, 1]
    seg[bg > 0] = [0,0,0,0]
    seg[fg > 0] = [0, 1.0, 1.0, 0.7]
    imsave(os.path.join(output_dir, fname), seg)


def gen_composite(annot_dir, photo_dir, comp_dir, fname, ext='.jpg'):
    """ for review.
    Output the pngs with the annotation overlaid next to it.
    should make it possible to identify errors. """
    out_path = os.path.join(comp_dir, fname.replace('.png', ext))
    if not os.path.isfile(out_path):
        name_no_ext = os.path.splitext(fname)[0]
        # doesn't matter what the extension is
        glob_str = os.path.join(photo_dir, name_no_ext) + '.*'
        bg_fpath = list(glob.iglob(glob_str))[0]
        background = load_image(bg_fpath)
        annot = imread(os.path.join(annot_dir, os.path.splitext(fname)[0] + '.png'))
        if sys.platform == 'darwin':
            # resize uses np.linalg.inv and causes a segmentation fault
            # for very large images on osx
            # See https://github.com/bcdev/jpy/issues/139
            # Maybe switch to ATLAS to help (for BLAS)
            # until fixed, use simpler resize method.
            # take every second pixel
            background = background[::2, ::2]
            annot = annot[::2, ::2]
        else:
            background = resize(background,
                                (background.shape[0]//2,
                                 background.shape[1]//2, 3))
            annot = resize(annot, (annot.shape[0]//2, annot.shape[1]//2, 3))
        # if the annotation has 4 channels (that means alpha included)
        if len(annot.shape) and annot.shape[2] == 4:
            # then save alpha channel
            alpha_channel = annot[:, :, 3]
            # convert the annot to just the rgb
            annot = annot[:, :, :3]
            # and set to 0 if the alpha was 0
            annot[alpha_channel == 0] = [0, 0, 0]

        annot = rgb2gray(annot)
        annot = img_as_ubyte(annot)
        background = img_as_ubyte(background)
        comp_right = np.copy(background)
        comp_right[annot > 0] = [255, 0, 0]
        # if width is more than 20% bigger than height then vstack
        if background.shape[1] > background.shape[0] * 1.2:
            comp = np.vstack((background, comp_right))
        else:
            comp = np.hstack((background, comp_right))
        assert comp.dtype == np.uint8
        with warnings.catch_warnings():
            # avoid low constrast warning.
            warnings.simplefilter("ignore")
            imsave(out_path, comp, quality=95)
