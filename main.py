from camera_system.sensors.pir_watcher import PIRWatcher
from camera_system.storage.db import DBmanager

PIRSENSORPIN = 17

pir = PIRWatcher(PIRSENSORPIN)
DB = DBmanager()


# while True:
#     pir.wait_for_motion()
#     print("Mouvement détécté !")

#     pir.wait_for_no_motion()
#     print("Plus de mouvement !")
DB.delete_video(1)