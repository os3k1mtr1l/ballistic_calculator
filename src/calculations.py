import constants as Constants
from math import sqrt, atan2
from typing import NamedTuple, Optional, Union

class Point(NamedTuple):
    x: int
    y: int

def normalize_angle(angle: float) -> float:
    angle = ((360 - angle) % 360)

    return round(angle, 2)

def angle_to_cardinal(angle: float, epsilon: float = 1.0) -> Union[float, str]:    
    if abs(angle - 0) < epsilon:
        return 'N'
    elif abs(angle - 90) < epsilon:
        return  'E'
    elif abs(angle - 180) < epsilon:
        return  'S'
    elif abs(angle - 270) < epsilon:
        return  'W'

    return angle

def calculate_difference(pos1: Point, pos2: Point) -> tuple[float, float]:
    x1, y1 = pos1
    x2, y2 = pos2

    dx = (x1 - x2) / Constants.PIXELS_PER_SQUARE
    dy = (y1 - y2) / Constants.PIXELS_PER_SQUARE

    return dx, dy

def calculate_distance(pos1: Optional[Point], pos2: Optional[Point]) -> Optional[float]:
    if pos1 is None or pos2 is None:
        return None
    
    dx, dy = calculate_difference(pos1, pos2)

    meters: float = sqrt(dx**2 + dy**2)
    meters = meters * Constants.METERS_PER_SQUARE

    return round(meters)

def calculate_angle(pos1: Optional[Point], pos2: Optional[Point]) -> Optional[float]:
    if pos1 is None or pos2 is None:
        return None
    
    dx, dy = calculate_difference(pos1, pos2)

    angle: float = Constants.RAD_TO_DEG * atan2(dx,dy)
    angle = normalize_angle(angle)

    return round(angle, 2)