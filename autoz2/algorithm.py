from typing import Callable
import numpy as np
import cv2
from skimage import draw

class CVPipelineNode:
    # For now, we assume pipelines are linear DAGs.
    def __init__(self, run_fn: Callable, child: "CVPipelineNode" = None,):
        self.child = child
        self.run_fn = run_fn

    def run(self, args):
        self.run_fn(args)

def apply_blur(frame, k, s):
    return cv2.GaussianBlur(frame, (k, k), s, borderType=cv2.BORDER_DEFAULT)

def calc_bitmask_overlap(bitmask, diff_bitmask):
    # Sum the non-zero values of the bitmask, which gives a total area of the mask.
    total_area = int(np.sum(bitmask))

    # Obtain the part of the diff bitmask that overlaps with the main mask. note that this should already
    # Be done but we'll re-do it anyway here for safety.
    new_difmask = np.copy(diff_bitmask)
    new_difmask[np.where(bitmask != 255)] = 0
    new_difmask[np.where(bitmask == 255)] = 1
    covered_area = np.sum(new_difmask)

    percent_coverage = covered_area / total_area
    return percent_coverage

class Algorithm:
    def __init__(self):
        self.pipeline_resolution = (740, 740)
        # self.pipeline_resolution = (128, 128)
        self.bg_subtractor: cv2.BackgroundSubtractorMOG2 = cv2.createBackgroundSubtractorMOG2()
        self.bg_subtractor.setHistory(1)
        self.k = 21
        self.s = 60
        self.base_frame = None
        self.frame = None
        self.blurred = None
        self.thresholded = None
        self.overlapped = None
        self.difference_threshold = 9
        self.contact_decision_threshold = 12

        w, h = self.pipeline_resolution
        self.mask = np.zeros(shape=self.pipeline_resolution, dtype=np.uint8)
        rr, cc = draw.ellipse(h//2, w//2, h//2.2, w//2.2)
        self.mask[rr, cc] = 127

        axes_length = (int(h/2.2), int(w/2.2))  # nb. explicit int conversion required or openCV fails dispatch.
        self.mask_outline = np.zeros(shape=self.pipeline_resolution, dtype=np.uint8)
        self.mask_outline = cv2.ellipse(self.mask_outline, (h//2, w//2), axes_length, 0, 0, 360, color=(255, 255, 255), thickness=5)
        self.mask_outline[self.mask_outline>0] = 127

    def run(self, frame) -> float:
        """
        Step the algorithm forward. Return true if contact has been detected. Otherwise
        """
        # In very OOP fashion, we have the frame
        self.frame = cv2.resize(frame, self.pipeline_resolution)
        self.blurred = apply_blur(self.frame, self.k, self.s)

        if self.base_frame is None:
            self.base_frame = self.blurred
            return 0

        self.bg_subtractor.apply(self.base_frame)
        self.thresholded = self.bg_subtractor.apply(self.blurred)

        # Normalize
        # self.thresholded = self.thresholded / self.thresholded.max()
        # self.thresholded = self.thresholded.astype(np.bool)

        # Compute overlap between fg mask (detected change) and input mask.
        overlap = cv2.bitwise_and(self.mask, self.thresholded)
        self.overlapped = overlap
        w, h = self.mask.shape

        coverage = np.sum(overlap) / (h*w)

        return float(coverage)










