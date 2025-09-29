import cv2 as cv
import numpy as np
from pathlib import Path
from enum import Enum
from typing import Optional

import utils
import constants as Constants

# Think, if it can be not global
img = None

value_changing = True
#

class Source(Enum):
    OBS = 0
    TEST_SAMPLES = 1
    USER_PATH = 2

def print_coords(event, x, y, flags, param) -> None:
    global img

    if img is None:
        return

    if event == cv.EVENT_LBUTTONDOWN:
        b, g, r = img[y, x]
        print(f"Real image: {x}, {y} = [ RGB: {r}, {g}, {b} ]")


def calibration_updated(event, x, y, flags, param) -> None:
    global img, value_changing

    if img is None:
        return

    if event == cv.EVENT_LBUTTONDOWN:
        value_changing = True
    
    if event == cv.EVENT_LBUTTONUP:
        value_changing = False

class CVProto:
    def __init__(self, source: Source, image_path: Optional[Path] = None, capture_device_id: Optional[int] = None):
        self._is_window_running: bool = True
        self._source = source
        
        if source == Source.OBS:
            self._is_window_running = self._initialize_capture(capture_device_id)
        elif source == Source.TEST_SAMPLES or source == Source.USER_PATH:
            self._is_window_running = self._initialize_images(image_path)
        else:
            self._is_window_running: bool = False
            print("Source is not defined")

        self._initialize_trackbar()
        self._initialize_window()

        self._show_image: bool = False
            
    def _initialize_capture(self, capture_device_id: Optional[int]) -> bool:
        global img

        if capture_device_id is None:
                print("Bad video device: Invalid ID")
                return False

        self._cap = cv.VideoCapture(capture_device_id)

        if not self._cap.isOpened():
            print("Bad video device: Can\'t open device")
            return False
        
        self._cap.set(cv.CAP_PROP_FRAME_WIDTH, Constants.WINDOW_SIZE.x)
        self._cap.set(cv.CAP_PROP_FRAME_HEIGHT, Constants.WINDOW_SIZE.y)

        _, img = self._cap.read()

        return True

    def _initialize_images(self, path: Optional[Path]) -> bool:
        global img
        
        if path is None and self._source == Source.TEST_SAMPLES:
            path = Constants.TEST_SAMPLES_PATH

        if path is None or not path.exists():
            print("Bad path: Path is none")
            return False

        self._images_path = utils.get_images_path(path)

        if len(self._images_path) == 0:
            print("Bad path: Image files empty")
            return False
        
        self._image_index = 0
        self._previous_index = 0
        img_path = self._images_path[self._image_index].absolute()
        img = cv.imread(str(img_path))
        print("Image loaded: ", img_path.name)

        return True

    def _initialize_trackbar(self) -> None:
        nothing = lambda x: None

        cv.namedWindow("Calibration", cv.WINDOW_NORMAL)
        cv.resizeWindow("Calibration", 530, 230)
        cv.createTrackbar("Lower Hue", "Calibration", 0, 180, nothing)
        cv.createTrackbar("Lower Saturation", "Calibration", 0, 255, nothing)
        cv.createTrackbar("Lower Value", "Calibration", 0, 255, nothing)

        cv.createTrackbar("Upper Hue", "Calibration", 0, 180, nothing)
        cv.createTrackbar("Upper Saturation", "Calibration", 0, 255, nothing)
        cv.createTrackbar("Upper Value", "Calibration", 0, 255, nothing)

        lower_h, lower_s, lower_v = 23, 128, 147
        upper_h, upper_s, upper_v = 40, 255, 255

        cv.setTrackbarPos("Lower Hue", "Calibration", lower_h)
        cv.setTrackbarPos("Lower Saturation", "Calibration", lower_s)
        cv.setTrackbarPos("Lower Value", "Calibration", lower_v)

        cv.setTrackbarPos("Upper Hue", "Calibration", upper_h)
        cv.setTrackbarPos("Upper Saturation", "Calibration", upper_s)
        cv.setTrackbarPos("Upper Value", "Calibration", upper_v)

        cv.setMouseCallback("Calibration", calibration_updated)

    def _initialize_window(self) -> None:
        cv.namedWindow("Image", cv.WINDOW_AUTOSIZE)
        cv.setMouseCallback("Image", print_coords)

    def _update(self) -> None:
        global img, value_changing
        
        if img is None or not value_changing:
            return

        h = cv.getTrackbarPos("Lower Hue", "Calibration")
        s = cv.getTrackbarPos("Lower Saturation", "Calibration")
        v = cv.getTrackbarPos("Lower Value", "Calibration")

        lower_color = np.array([h, s, v])

        h = cv.getTrackbarPos("Upper Hue", "Calibration")
        s = cv.getTrackbarPos("Upper Saturation", "Calibration")
        v = cv.getTrackbarPos("Upper Value", "Calibration")

        upper_color = np.array([h, s, v])

        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

        mask = cv.inRange(hsv, lower_color, upper_color)
        self._masked_img = cv.bitwise_and(img, img, mask=mask)

    def _handle_events(self) -> None:
        global value_changing
        
        k = cv.waitKey(1) & 0xFF

        if self._source != Source.OBS and k == Constants.KEY_NEXT:
            if self._image_index == len(self._images_path) - 1:
                self._is_window_running = False
                return
            
            self._image_index += 1
            
            value_changing = True

        if k == Constants.KEY_SWITCH_MASK:
            self._show_image = not self._show_image
            print("Showing image" if self._show_image else "Showing mask")

        if k == Constants.KEY_EXIT:
            self._is_window_running = False
            print("Exiting window")

        if value_changing or self._source == Source.OBS:
            self._update()

    def _render(self) -> None:
        global img

        if self._source != Source.OBS and self._previous_index != self._image_index:
            img_path = self._images_path[self._image_index].absolute()
            img = cv.imread(str(img_path))
            print("Image loaded: ", img_path.name)
            self._previous_index = self._image_index

        if self._source == Source.OBS:
            _, frame = self._cap.read()
            img = frame

        if img is None:
            print("Null image")
            self._image_index += 1
            return

        if self._show_image:
            cv.imshow("Image", img)
        else:
            cv.imshow("Image", self._masked_img)

    def run(self) -> None:
        while self._is_window_running:
            self._handle_events()
            self._render()

    def quit(self) -> None:
        global img
        img = None

        if hasattr(self, "_cap"):
            self._cap.release()
        cv.destroyAllWindows()