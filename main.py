# from camera_system.sensors.pir_watcher import PIRWatcher
# from camera_system.storage.db import Storage

# # PIRSENSORPIN = 17

# # pir = PIRWatcher(PIRSENSORPIN)
# # storage = Storage()


from datetime import datetime
import time
import yaml


from camera_system.sensors.pir_watcher import PIRWatcher
from camera_system.recorder.camera_controller import CameraController
from camera_system.storage.db import Storage


def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def main():

    config = load_config()
    pir_pin = config['pir']['gpio_pin']
    resolution = (config['camera']['resolution']['width'], config['camera']['resolution']['height'])
    pir_min_interval_seconds = config['pir']['min_interval_seconds']

    pir = PIRWatcher(pir_pin)
    cam = CameraController(resolution)
    storage = Storage()


    try:
        while True:

            pir.wait_for_motion()
            recorded_at = datetime.now().astimezone()
            cam.start_recording()
            pir.wait_for_no_motion()
            result = cam.stop_recording()
            storage.add_video(
                video_bytes=result['video_bytes'],
                storage_path=storage.build_storage_path(recorded_at),
                human_detected=True,
                duration_seconds=result['duration_seconds'],
                recorded_at=recorded_at
            )
            time.sleep(pir_min_interval_seconds)
    finally:
        cam.close()


if __name__ == "__main__":
    main()