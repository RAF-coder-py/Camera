from supabase import Client, create_client
import os
from dotenv import load_dotenv


class VideoRepository:
    """
    Gère les informations des vidéos dans la base de données SQL.
    """

    def __init__(self):
        """
        Initialise l'accès à la base de données.

        Args:
            supabase_client: Client Supabase déjà configuré.
        """

        load_dotenv()

        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")

        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    def add_video(
        self,
        filename,
        storage_path,
        video_url=None,
        duration_seconds=None,
        human_detected=True
    ):
        """
        Ajoute les informations d'une vidéo dans la table SQL.

        Args:
            filename (str): Nom du fichier vidéo.
            storage_path (str): Emplacement du fichier dans Supabase Storage.
            video_url (str | None): URL permettant d'accéder à la vidéo.
            duration_seconds (float | None): Durée de la vidéo.
            human_detected (bool): Indique si un humain a été détecté.

        Returns:
            Réponse retournée par Supabase.
        """
        video_data = {
            "filename": filename,
            "storage_path": storage_path,
            "video_url": video_url,
            "duration_seconds": duration_seconds,
            "human_detected": human_detected
        }

        return (
            self.supabase
            .table("videos")
            .insert(video_data)
            .execute()
        )

    def delete_video(self, video_id):
        """
        Supprime une vidéo de la base de données.

        Args:
            video_id (int): Identifiant de la vidéo à supprimer.

        Returns:
            Réponse retournée par Supabase.
        """
        return (
            self.supabase
            .table("videos")
            .delete()
            .eq("id", video_id)
            .execute()
        )

    def get_video(self, video_id):
        """
        Récupère une vidéo précise à partir de son identifiant.

        Args:
            video_id (int): Identifiant de la vidéo à récupérer.

        Returns:
            Réponse retournée par Supabase.
        """
        return (
            self.supabase
            .table("videos")
            .select("*")
            .eq("id", video_id)
            .single()
            .execute()
        )

    def get_all_videos(self):
        """
        Récupère toutes les vidéos enregistrées dans la base de données.

        Returns:
            Réponse retournée par Supabase.
        """
        return (
            self.supabase
            .table("videos")
            .select("*")
            .order("id", desc=True)
            .execute()
        )

    def get_videos_by_human_detection(self, human_detected=True):
        """
        Récupère les vidéos filtrées selon la détection d'un humain.

        Args:
            human_detected (bool): Filtre sur la présence ou non d'un humain détecté.

        Returns:
            Réponse retournée par Supabase.
        """
        return (
            self.supabase
            .table("videos")
            .select("*")
            .eq("human_detected", human_detected)
            .execute()
        )

    def update_video(self, video_id, **fields):
        """
        Met à jour les informations d'une vidéo existante.

        Args:
            video_id (int): Identifiant de la vidéo à mettre à jour.
            **fields: Champs à mettre à jour (ex: video_url="...", duration_seconds=12.5).

        Returns:
            Réponse retournée par Supabase.
        """
        return (
            self.supabase
            .table("videos")
            .update(fields)
            .eq("id", video_id)
            .execute()
        )

    def count_videos(self):
        """
        Compte le nombre total de vidéos enregistrées.

        Returns:
            int: Nombre de vidéos dans la table.
        """
        response = (
            self.supabase
            .table("videos")
            .select("id", count="exact")
            .execute()
        )
        return response.count