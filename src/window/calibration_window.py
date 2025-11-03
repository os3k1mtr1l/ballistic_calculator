import cv2 as cv
from typing import Tuple, Callable

import constants

class CalibrationWindow:
    def __init__(self, update_callback: Callable[[int], None]):
        self.window_name = constants.CALIBRATION_WINDOW_NAME

        cv.namedWindow(self.window_name, cv.WINDOW_NORMAL)
        cv.resizeWindow(self.window_name, 500, 513)

        # Default HSV for Marker
        lower_hsv = (30, 171, 174)
        upper_hsv = (40, 255, 255)

        self.make_hsv_trackbar("Lower", "Marker", update_callback, lower_hsv)
        self.make_hsv_trackbar("Upper", "Marker", update_callback, upper_hsv)

        # Default HSV for Player
        lower_hsv = (20, 16, 193)
        upper_hsv = (33, 255, 255)

        self.make_hsv_trackbar("Lower", "Player", update_callback, lower_hsv)
        self.make_hsv_trackbar("Upper", "Player", update_callback, upper_hsv)

    def make_hsv_trackbar(self, level: str, label: str, callback: Callable[[int], None], default: Tuple[int, int, int] = (0, 0, 0)) -> None:
        h, s, v = default
        argument_map = { "Hue": (h, 180), "Saturation": (s, 255), "Value": (v, 255) }

        for channel_name, (default_value, max_value) in argument_map.items():
            cv.createTrackbar(f"{level} {channel_name} {label}", self.window_name, default_value, max_value, callback)

    def get_hsv_trackbar(self, level: str, label: str) -> Tuple[int, int, int]:
        h, s, v = tuple(cv.getTrackbarPos(f"{level} {channel_name} {label}", self.window_name) for channel_name in ("Hue", "Saturation", "Value"))

        return h, s, v
    
    def set_hsv_trackbar(self, level: str, label: str, values: Tuple[int, int, int]) -> None:
        h, s, v = values
        argument_map = { "Hue": h, "Saturation": s, "Value": v }

        for channel_name, value in argument_map.items():
            cv.setTrackbarPos(f"{level} {channel_name} {label}", self.window_name, value)