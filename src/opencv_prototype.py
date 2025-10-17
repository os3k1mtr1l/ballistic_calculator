import cv2 as cv
import numpy as np
from pathlib import Path
from enum import Enum, StrEnum
from typing import Optional

import utils
import constants as Constants

class Source(Enum):
    OBS = 0
    TEST_SAMPLES = 1
    USER_PATH = 2

def print_coords(event, x, y, flags, param) -> None:
    if CVProto.img is None:
        return

    if event == cv.EVENT_LBUTTONDOWN:
        b, g, r = CVProto.img[y, x]
        print(f"Real image: {x}, {y} = [ RGB: {r}, {g}, {b} ]")

def calibration_updated(value) -> None:
    if CVProto.img is None:
        return

    CVProto.value_changing = True

class CVProto:
    img = None

    value_changing = True

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

        self._show_image: bool = True
            
    def _initialize_capture(self, capture_device_id: Optional[int]) -> bool:
        if capture_device_id is None:
                print("Bad video device: Invalid ID")
                return False

        self._cap = cv.VideoCapture(capture_device_id)

        if not self._cap.isOpened():
            print("Bad video device: Can\'t open device")
            return False
        
        self._cap.set(cv.CAP_PROP_FRAME_WIDTH, Constants.WINDOW_SIZE.x)
        self._cap.set(cv.CAP_PROP_FRAME_HEIGHT, Constants.WINDOW_SIZE.y)

        _, CVProto.img = self._cap.read()

        return True

    def _initialize_images(self, path: Optional[Path]) -> bool:
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
        CVProto.img = cv.imread(str(img_path))
        print("Image loaded: ", img_path.name)

        return True

    def _make_hsv_trackbar(self, level: str, object: str, window: str, callback) -> None:
        join_list = [level, "Hue", object]
        cv.createTrackbar(' '.join(join_list), window, 0, 180, callback)
        
        join_list[1] = "Saturation"
        cv.createTrackbar(' '.join(join_list), window, 0, 255, callback)

        join_list[1] = "Value"
        cv.createTrackbar(' '.join(join_list), window, 0, 255, callback)

    def _get_hsv(self, level: str, object: str, window: str) -> tuple:
        join_list = [level, "Hue", object]
        h = cv.getTrackbarPos(' '.join(join_list), window)
        
        join_list[1] = "Saturation"
        s = cv.getTrackbarPos(' '.join(join_list), window)
        
        join_list[1] = "Value"
        v = cv.getTrackbarPos(' '.join(join_list), window)

        return h, s, v
    
    def _set_hsv(self, level: str, object: str, window: str, args: tuple) -> None:
        h, s, v = args

        join_list = [level, "Hue", object]
        cv.setTrackbarPos(' '.join(join_list), window, h)

        join_list[1] = "Saturation"
        cv.setTrackbarPos(' '.join(join_list), window, s)

        join_list[1] = "Value"
        cv.setTrackbarPos(' '.join(join_list), window, v)

    def _initialize_trackbar(self) -> None:
        window_name = "Calibration"

        cv.namedWindow(window_name, cv.WINDOW_NORMAL)
        cv.resizeWindow(window_name, 500, 513)

        self._make_hsv_trackbar("Lower", "Marker", window_name, calibration_updated)
        self._make_hsv_trackbar("Upper", "Marker", window_name, calibration_updated)
        self._make_hsv_trackbar("Lower", "Player", window_name, calibration_updated)
        self._make_hsv_trackbar("Upper", "Player", window_name, calibration_updated)

        # cv.createTrackbar("Lower Hue", "Calibration", 0, 180, calibration_updated)
        # cv.createTrackbar("Lower Saturation", "Calibration", 0, 255, calibration_updated)
        # cv.createTrackbar("Lower Value", "Calibration", 0, 255, calibration_updated)

        # cv.createTrackbar("Upper Hue", "Calibration", 0, 180, calibration_updated)
        # cv.createTrackbar("Upper Saturation", "Calibration", 0, 255, calibration_updated)
        # cv.createTrackbar("Upper Value", "Calibration", 0, 255, calibration_updated)

        # lower_h, lower_s, lower_v = 23, 128, 147
        lower_h, lower_s, lower_v = 30, 171, 174
        upper_h, upper_s, upper_v = 40, 255, 255

        self._set_hsv("Lower", "Marker", window_name, (lower_h, lower_s, lower_v))
        self._set_hsv("Upper", "Marker", window_name, (upper_h, upper_s, upper_v))

        lower_h, lower_s, lower_v = utils.normal_hsv_to_cv((60, 11, 100))
        upper_h, upper_s, upper_v = utils.normal_hsv_to_cv((80, 11, 100))

        self._set_hsv("Lower", "Player", window_name, (lower_h, lower_s, lower_v))
        self._set_hsv("Upper", "Player", window_name, (upper_h, upper_s, upper_v))

        # cv.setTrackbarPos("Lower Hue", "Calibration", lower_h)
        # cv.setTrackbarPos("Lower Saturation", "Calibration", lower_s)
        # cv.setTrackbarPos("Lower Value", "Calibration", lower_v)

        # cv.setTrackbarPos("Upper Hue", "Calibration", upper_h)
        # cv.setTrackbarPos("Upper Saturation", "Calibration", upper_s)
        # cv.setTrackbarPos("Upper Value", "Calibration", upper_v)

    def _initialize_window(self) -> None:
        cv.namedWindow("Image", cv.WINDOW_AUTOSIZE)
        cv.setMouseCallback("Image", print_coords)

    def _update(self) -> None:
        if CVProto.img is None or not CVProto.value_changing:
            return

        # h = cv.getTrackbarPos("Lower Hue", "Calibration")
        # s = cv.getTrackbarPos("Lower Saturation", "Calibration")
        # v = cv.getTrackbarPos("Lower Value", "Calibration")

        h, s, v = self._get_hsv("Lower", "Marker", "Calibration")

        lower_color = np.array([h, s, v])

        # h = cv.getTrackbarPos("Upper Hue", "Calibration")
        # s = cv.getTrackbarPos("Upper Saturation", "Calibration")
        # v = cv.getTrackbarPos("Upper Value", "Calibration")

        h, s, v = self._get_hsv("Upper", "Marker", "Calibration")

        upper_color = np.array([h, s, v])

        hsv = cv.cvtColor(CVProto.img, cv.COLOR_BGR2HSV)

        mask_marker = cv.inRange(hsv, lower_color, upper_color)

        h, s, v = self._get_hsv("Lower", "Player", "Calibration")
        lower_color = np.array([h, s, v])

        h, s, v = self._get_hsv("Upper", "Player", "Calibration")
        upper_color = np.array([h, s, v])

        mask_player = cv.inRange(hsv, lower_color, upper_color)

        mask = cv.bitwise_or(mask_marker, mask_player)

        self._masked_img = cv.bitwise_and(CVProto.img, CVProto.img, mask=mask)

        contours, hierarchy = cv.findContours(mask.copy(), cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        i = max = 0
        for contour in contours:
            if contour.size > contours[max].size:
                max = i
            
            i += 1

        try:
            rect = cv.minAreaRect(contours[max])
            box = cv.boxPoints(rect)
            box = box.astype(int)
            self._img = cv.drawContours(CVProto.img.copy(), [box], -1, (0, 0, 255), 2)
        except:
            self._img = CVProto.img.copy()
        
        value_changing = False

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

        if CVProto.value_changing or self._source == Source.OBS:
            self._update()

    def _render(self) -> None:
        if self._source != Source.OBS and self._previous_index != self._image_index:
            img_path = self._images_path[self._image_index].absolute()
            CVProto.img = cv.imread(str(img_path))
            print("Image loaded: ", img_path.name)
            self._previous_index = self._image_index

        if self._source == Source.OBS:
            _, frame = self._cap.read()
            CVProto.img = frame

        if CVProto.img is None:
            print("Null image")
            self._image_index += 1
            return

        if self._show_image:
            cv.imshow("Image", self._img)
        else:
            cv.imshow("Image", self._masked_img)

    def run(self) -> None:
        while self._is_window_running:
            self._handle_events()
            self._render()

    def quit(self) -> None:
        CVProto.img = None

        if hasattr(self, "_cap"):
            self._cap.release()
        cv.destroyAllWindows()