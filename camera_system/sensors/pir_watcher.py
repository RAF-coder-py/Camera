from gpiozero import MotionSensor


class PIRWatcher:
    def __init__(self, pin):
        """
        Initialise le capteur PIR.

        Args:
            pin (int): numéro du GPIO (BCM)
        """
        self.pir = MotionSensor(pin)

    def motion_detected(self):
        """
        Retourne True si un mouvement est détecté.
        """
        return self.pir.motion_detected

    def wait_for_motion(self):
        """
        Bloque le programme jusqu'à ce qu'un mouvement soit détecté.
        """
        self.pir.wait_for_motion()
        print("Ralph detected")

    def wait_for_no_motion(self):
        """
        Bloque le programme jusqu'à ce qu'il n'y ait plus de mouvement.
        """
        self.pir.wait_for_no_motion()