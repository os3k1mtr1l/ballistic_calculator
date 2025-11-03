import cv2 as cv
import numpy as np
from pathlib import Path
from enum import Enum
from typing import Optional
from functools import partial

from utilities import get_images_path
from processing import ImageProcessor
from constants import Keys, MAIN_WINDOW_NAME, WINDOW_SIZE, TEST_SAMPLES_PATH
from .calibration_window import CalibrationWindow

class Source(Enum):
    OBS = 0
    TEST_SAMPLES = 1
    USER_PATH = 2

class RenderType(Enum):
    IMAGE = 0
    MASK = 1
    CONTOURS = 2
    # ALL = 3

class MainWindow:
    def print_coords(self, event, x, y, flags, param) -> None:
        if self._image is None:
            return

        if event == cv.EVENT_LBUTTONDOWN:
            b, g, r = self._image[y, x]
            print(f"Real image: {x}, {y} = [ RGB: {r}, {g}, {b} ]")

    def calibration_updated(self, value) -> None:
        if self._image is None:
            return

        self._needs_update = True

    def __init__(self, source: Source, image_path: Optional[Path] = None, capture_device_id: Optional[int] = None):
        self._is_window_running: bool = True
        self.window_name = MAIN_WINDOW_NAME
        
        self._source = source
        self._render_type = RenderType.IMAGE

        self._next_image = False
        self._no_more_images = True
        self._needs_update = True
        self._render_change = True

        self._image: Optional[np.ndarray] = None
        self._render_target: Optional[np.ndarray] = None
        self._cap: Optional[cv.VideoCapture] = None
        self._images_path: Optional[list[Path]] = None

        if source == Source.OBS:
            self._is_window_running = self._initialize_capture(capture_device_id)
        elif source == Source.TEST_SAMPLES or source == Source.USER_PATH:
            self._is_window_running = self._initialize_images(image_path)
        else:
            self._is_window_running: bool = False
            print("Source is not defined")
            return

        self.calibration = CalibrationWindow(partial(MainWindow.calibration_updated, self))
        self._initialize_window()

    def _initialize_capture(self, capture_device_id: Optional[int]) -> bool:
        if capture_device_id is None:
                print("Bad video device: Invalid ID")
                return False

        self._cap = cv.VideoCapture(capture_device_id)

        if not self._cap.isOpened():
            print("Bad video device: Can\'t open device")
            return False
        
        self._cap.set(cv.CAP_PROP_FRAME_WIDTH, WINDOW_SIZE.x)
        self._cap.set(cv.CAP_PROP_FRAME_HEIGHT, WINDOW_SIZE.y)

        _, self._image = self._cap.read()

        return True
    
    def _initialize_images(self, path: Optional[Path]) -> bool:
        if path is None and self._source == Source.TEST_SAMPLES:
            path = TEST_SAMPLES_PATH

        if path is None or not path.exists():
            print("Bad path: Path is none")
            return False

        self._images_path = get_images_path(path)

        if len(self._images_path) == 0:
            print("Bad path: Image files empty")
            return False

        self.generator = (image_path.absolute() for image_path in self._images_path)
        self._no_more_images = not len(self._images_path) > 1
        self._next_image = True

        self._next_frame()

        return True

    def _initialize_window(self) -> None:
        cv.namedWindow(self.window_name, cv.WINDOW_AUTOSIZE)
        cv.setMouseCallback(self.window_name, partial(MainWindow.print_coords, self))

    def _next_frame(self) -> None:
        if self._next_image:
            try:
                img_path = next(self.generator)
                self._image = cv.imread(str(img_path))
                print("Image loaded: ", img_path.name)
            except:
                print("Image sequence: Stop")
                self._no_more_images = True
            
            self._next_image = False

        if self._source == Source.OBS and self._cap:
            _, self._image = self._cap.read()

    def _process_image(self) -> None:
        if self._image is None or (not self._needs_update and self._source != Source.OBS):
            return
        
        w, h = self._image.shape[:-1]

        cx, cy = w // 2, h // 2

        self._image = self._image[cx:w, cy:h] # Approximate region of interest

        lower, upper = self.calibration.get_hsv_trackbar("Lower", "Marker"), self.calibration.get_hsv_trackbar("Upper", "Marker")
        marker_mask = ImageProcessor.mask_image(self._image, lower, upper)

        lower, upper = self.calibration.get_hsv_trackbar("Lower", "Player"), self.calibration.get_hsv_trackbar("Upper", "Player")
        player_mask = ImageProcessor.mask_image(self._image, lower, upper)

        self._mask = cv.bitwise_or(marker_mask, player_mask)

        contours = ImageProcessor.find_contours(self._mask)
        self._contoured = cv.drawContours(self._image.copy(), contours, -1, (0, 0, 255), 2)

        self._needs_update = False

    def _set_render_target(self) -> None:
        if not self._render_change:
            return

        match self._render_type:
            case RenderType.MASK:
                self._render_target = self._mask

            case RenderType.CONTOURS:
                self._render_target = self._contoured
            
            # case RenderType.ALL:
            #     pass

            case _:
                self._render_target = self._image

        self._render_change = False

    def _update(self) -> None:
        self._next_frame()
        self._process_image()
        self._set_render_target()

    def _handle_events(self) -> None:
        k = cv.waitKey(1) & 0xFF

        if self._source != Source.OBS and k == Keys.NEXT.value:
            if self._no_more_images:
                self._is_window_running = False
                return

            self._next_image = True
            self._needs_update = True
            self._render_change = True

        if k == Keys.SWITCH_RENDER_TYPE.value:
            render_type_last_name = self._render_type.name
            self._render_type = RenderType((self._render_type.value + 1) % len(RenderType))
            self._render_change = True
            print(f"Render type switched: {render_type_last_name} -> {self._render_type.name}")

        if k == Keys.EXIT.value:
            self._is_window_running = False
            print("Exiting window")

    def _render(self) -> None:
        if self._render_target is None:
            return

        cv.imshow(self.window_name, self._render_target)

    def run(self) -> None:
        while self._is_window_running:
            self._handle_events()
            self._update()
            self._render()

    def quit(self) -> None:
        del(self._image)

        if self._cap:
            self._cap.release()

        cv.destroyAllWindows()