import io
import time
import subprocess
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput


class CameraController:
    """
    Fonctions pour enregistrer une vidéo directement en mémoire (buffer).
    Aucun fichier n'est jamais écrit sur le disque : le buffer est ensuite
    transmis à Storage.add_video() pour être uploadé sur Supabase.
    """

    def __init__(self, resolution=(1280, 720)):
        self.camera = Picamera2()
        self.camera.configure(
            self.camera.create_video_configuration(main={"size": resolution})
        )
        self.encoder = H264Encoder()

        self.is_recording = False
        self.buffer = None
        self.start_time = None

    # ---------- Enregistrement ----------

    def start_recording(self):
        """Démarre l'enregistrement dans un buffer mémoire."""
        if self.is_recording:
            return

        self.buffer = io.BytesIO()
        output = FileOutput(self.buffer)

        self.camera.start()
        self.camera.start_encoder(self.encoder, output)

        self.is_recording = True
        self.start_time = time.time()

    def stop_recording(self):
        """Arrête l'enregistrement et retourne le buffer vidéo (bytes) + sa durée."""
        if not self.is_recording:
            return None

        self.camera.stop_encoder()
        self.camera.stop()

        duration = round(time.time() - self.start_time, 1)
        raw_h264 = self.buffer.getvalue()

        self.buffer.close()
        self.buffer = None
        self.is_recording = False
        self.start_time = None

        # On remet la vidéo dans un vrai conteneur MP4
        video_bytes = subprocess.run(
            ["ffmpeg", "-y", "-r", "30", "-i", "pipe:0",
            "-c:v", "copy", "-f", "mp4",
            "-movflags", "frag_keyframe+empty_moov", "pipe:1"],
            input=raw_h264,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        ).stdout

        return {
            "video_bytes": video_bytes,
            "duration_seconds": duration,
        }

    def record_for(self, seconds):
        """Enregistre pendant une durée fixe (bloquant) et retourne le buffer."""
        self.start_recording()
        time.sleep(seconds)
        return self.stop_recording()

    # ---------- Divers ----------

    def capture_snapshot(self):
        """Capture une image fixe en mémoire."""
        buffer = io.BytesIO()

        was_off = not self.camera.started
        if was_off:
            self.camera.start()

        self.camera.capture_file(buffer, format="jpeg")

        if was_off:
            self.camera.stop()

        return buffer.getvalue()

    def close(self):
        """Libère proprement la caméra."""
        if self.is_recording:
            self.stop_recording()
        self.camera.close()