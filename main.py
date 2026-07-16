# from camera_system.sensors.pir_watcher import PIRWatcher
# from camera_system.storage.db import Storage

# # PIRSENSORPIN = 17

# # pir = PIRWatcher(PIRSENSORPIN)
# # storage = Storage()


from datetime import datetime

from camera_system.recorder.camera_controller import CameraController
from camera_system.storage.db import Storage


def main():
    cam = CameraController()
    storage = Storage()

    try:
        print("Enregistrement en cours (5 secondes)...")
        result = cam.record_for(5)

        recorded_at = datetime.now().astimezone()
        storage_path = f"video_{recorded_at.strftime('%Y%m%d_%H%M%S')}.h264"

        storage.add_video(
            video_bytes=result["video_bytes"],
            storage_path=storage_path,
            duration_seconds=result["duration_seconds"],
            recorded_at=recorded_at,
        )

        print(f"Vidéo enregistrée : {storage_path} ({result['duration_seconds']}s)")

    finally:
        cam.close()


if __name__ == "__main__":
    main()