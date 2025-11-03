from typing import Tuple
from pathlib import Path
import os

import constants as Constants

def get_images_path(path: Path | str) -> list[Path]:
    if isinstance(path, str):
        path = Path(path)

    if not path.exists():
        raise RuntimeError("Invalid path")

    images: list[Path] = []

    if str(path).endswith(Constants.IMAGE_EXTENSIONS):
        images.append(path)
    elif path.is_dir():
        images.extend(
                [
                    path / Path(file)
                    for file in os.listdir(path)
                    if file.endswith(Constants.IMAGE_EXTENSIONS) and os.path.isfile(path / file)
                ]
            )
    
    return images

def hsv_normal_to_cv(hsv: Tuple[int, int, int]) -> Tuple[int, int, int]:
        h, s, v = hsv

        h = h // 2
        s = s * 255 // 100
        v = v * 255 // 100
        
        return h, s, v

def hsv_cv_to_normal(hsv: Tuple[int, int, int]) -> Tuple[int, int, int]:
    h, s, v = hsv

    h = h * 2
    s = s * 100 // 255
    v = v * 100 // 255
    
    return h, s, v