import functools

import numpy as np
from PyQt5.QtGui import QImage, QPixmap


def apply_layout_grid(grid, layout):
    for i, row in enumerate(grid):
        for j, widget in enumerate(grid[i]):
            layout.addWidget(widget, i, j)


def np2pixmap(img):
    height, width, channel = img.shape
    bytesPerLine = 3 * width
    q_img = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888)
    pix = QPixmap.fromImage(q_img)
    return pix


def add_bitmask_overlay(img, bitmask, alpha=0.9, color = (255, 0, 0)):
    # effectively for an additive overlay, we just want to "boost" the color channel by a certain amount.
    # mask_image = np.zeros(shape=(*mask.shape, 3), dtype=np.uint8)
    new_img = np.copy(img).astype(np.float)

    new_img[np.where(bitmask>0)] += alpha * np.array(color).astype(np.float)
    new_img[new_img > 255] = 255
    return new_img.astype(np.uint8)


def trace(fn):
    @functools.wraps(fn)
    def wrapped_fn(*args, **kwargs):
        print(fn.__name__)
        return fn(*args, **kwargs)
    return wrapped_fn


def calculate_coverage(bitmask, diff_bitmask):
    # TODO: this needs to be reworked. Decide on what on/off values are, datatype is bool or uint8? value is 127 or 255?
    # Normalize the bitmask so it is actually a bitmask
    bitmask[np.where(bitmask) == 255] = 1
    # Sum the non-zero values of the bitmask, which gives a total area of the mask.
    total_area = int(np.sum(bitmask))

    # Obtain the part of the diff bitmask that overlaps with the main mask. note that this should already
    # Be done but we'll re-do it anyway here for safety. TODO: remove redundancy
    new_difmask = np.copy(diff_bitmask)
    new_difmask[np.where(bitmask != 255)] = 0
    new_difmask[np.where(bitmask == 255)] = 1
    covered_area = np.sum(new_difmask)

    percent_coverage = covered_area / total_area
    return percent_coverage


