from math import pi
from pathlib import Path
from calculations import Point

WINDOW_SIZE: Point = Point(x = 600, y = 600)

PIXELS_PER_SQUARE = 600 / 7 # Map dependent
METERS_PER_SQUARE = 170 # Map dependent
RAD_TO_DEG = 180 / pi

TEXT_RANGE = "Range: {meters}"
TEXT_AZIMUTH = "Azimuth: {angle}"

TEST_SAMPLES_PATH = Path(__file__).parent / ".." / "test_samples"
IMAGE_EXTENSIONS = ".png", ".jpg"

KEY_EXIT = 27 # esc
KEY_NEXT = 13 # enter
KEY_SWITCH_MASK = 32 # space