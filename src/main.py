from pygame_prototype import PGProto
from opencv_prototype import CVProto, Source

from pathlib import Path

def main() -> None:
    # window: PGProto | CVProto = PGProto()
    # window: PGProto | CVProto = CVProto(Source.TEST_SAMPLES)
    window: PGProto | CVProto = CVProto(Source.OBS, capture_device_id=4)
    # window: PGProto | CVProto = CVProto(Source.USER_PATH, image_path=Path("./test_samples/full_map.png"))

    window.run()
    window.quit()

if __name__ == "__main__":
    main()