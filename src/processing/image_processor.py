import cv2 as cv
import numpy as np
from typing import Tuple, Sequence

class ImageProcessor:
    @staticmethod
    def mask_image(image: np.ndarray, lower: Tuple[int, int, int], upper: Tuple[int, int, int]) -> np.ndarray:
        lower_color, upper_color = np.array(lower), np.array(upper)

        hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
        
        mask = cv.inRange(hsv, lower_color, upper_color)
        
        return mask
    
    @staticmethod
    def find_contours(mask: np.ndarray) -> Sequence:
        contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        return contours