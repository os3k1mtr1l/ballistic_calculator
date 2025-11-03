from window.main_window import MainWindow, Source

from pathlib import Path

def main() -> None:
    kwargs: list[dict] = [
        { "source": Source.TEST_SAMPLES },
        { "source": Source.OBS, "capture_device_id": 4 },
        { "source": Source.USER_PATH, "image_path": Path("./test_samples/marker_in_middle.png") }
    ]
    
    window: MainWindow = MainWindow(**kwargs[0])

    window.run()
    window.quit()

if __name__ == "__main__":
    main()