from camera_system.sensors.pir_watcher import PIRWatcher
from camera_system.storage.db import Storage

PIRSENSORPIN = 17

pir = PIRWatcher(PIRSENSORPIN)
DB = Storage()


# while True:
#     pir.wait_for_motion()
#     print("Mouvement détécté !")

#     pir.wait_for_no_motion()
#     print("Plus de mouvement !")

filename = "coucou"
storage_path = "coucu/coucou"
video_url = "https://bite.com"
duration = 3


DB.add_video(filename, storage_path, video_url, duration)