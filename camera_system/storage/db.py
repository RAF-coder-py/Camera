import os
import datetime
from supabase import create_client
from dotenv import load_dotenv


class Storage:
    """
    Fonctions pour récupérer les vidéos : leurs infos en base SQL
    et leur fichier dans le bucket Supabase Storage.
    """

    def __init__(self, bucket_name="camera-videos"):
        load_dotenv()
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")

        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.bucket = self.supabase.storage.from_(bucket_name)

    # ---------- Table "videos" ----------

    def get_video(self, video_id):
        """Récupère une vidéo précise à partir de son identifiant."""
        response = (
            self.supabase
            .table("videos")
            .select("*")
            .eq("id", video_id)
            .maybe_single()
            .execute()
        )
        return response.data if response else None

    def get_all_videos(self):
        """Récupère toutes les vidéos enregistrées."""
        return (
            self.supabase
            .table("videos")
            .select("*")
            .order("id", desc=True)
            .execute()
            .data
        )

    def get_videos_by_human_detection(self, human_detected=True):
        """Récupère les vidéos où une présence humaine a (ou non) été détectée."""
        return (
            self.supabase
            .table("videos")
            .select("*")
            .eq("human_detected", human_detected)
            .order("id", desc=True)
            .execute()
            .data
        )

    # ---------- Bucket (fichiers vidéo) ----------

    # def get_video_url(self, storage_path, expires_in=3600):
    #     """Génère une URL temporaire pour lire/télécharger le fichier vidéo."""
    #     response = self.bucket.create_signed_url(storage_path, expires_in)
    #     return response.get("signedURL") or response.get("signed_url")

    def get_video_file(self, storage_path):
        """Télécharge le contenu brut (bytes) du fichier vidéo."""
        return self.bucket.download(storage_path)

    def list_video_files(self, prefix=""):
        """Liste les fichiers présents dans le bucket (optionnellement dans un sous-dossier)."""
        return self.bucket.list(path=prefix)

    # ---------- Ajout / suppression ----------

    def add_video( self, video_bytes, storage_path, human_detected,
                        duration_seconds=None, recorded_at=None,):
        """
        Upload directement depuis un buffer mémoire (pas de fichier sur disque).
 
        recorded_at : datetime (timezone-aware de préférence) représentant
        l'heure réelle de l'enregistrement. Si non fourni, l'heure actuelle
        est utilisée.
        """
        recorded_at = recorded_at or datetime.now().astimezone()
 
        self.bucket.upload(
            path=storage_path,
            file=video_bytes,
            file_options={"content-type": "video/mp4"}
        )
 
        data = {
            "filename": os.path.basename(storage_path),
            "storage_path": storage_path,
            "human_detected": human_detected,
            "duration_seconds": duration_seconds,
            "recorded_at": recorded_at.isoformat(),
        }
        return self.supabase.table("videos").insert(data).execute().data

    def remove_video(self, video_id):
        """Supprime la vidéo du bucket et de la table SQL."""
        video = self.get_video(video_id)
        if not video:
            return None

        self.bucket.remove([video["storage_path"]])
        return self.supabase.table("videos").delete().eq("id", video_id).execute().data