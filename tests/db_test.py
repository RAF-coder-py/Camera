"""
Test simple de la classe Storage.

Ce script teste directement contre le vrai projet Supabase (pas de mock) :
il ajoute une petite fausse vidéo, vérifie qu'on peut la récupérer,
puis la supprime pour ne rien laisser dans la base ou le bucket.

Pré-requis :
- un fichier .env avec SUPABASE_URL et SUPABASE_KEY
- une table "videos" et un bucket "camera-videos" déjà créés

Lancer depuis la racine du projet avec : python -m tests.db_test
"""

from camera_system.storage.db import Storage


TEST_STORAGE_PATH = "test/fake_video.mp4"
FAKE_VIDEO_BYTES = b"ceci n'est pas une vraie video, juste un test"


def test_add_video(storage):
    print("1. Ajout d'une vidéo de test...")

    result = storage.add_video(
        video_bytes=FAKE_VIDEO_BYTES,
        storage_path=TEST_STORAGE_PATH,
        human_detected=True,
        duration_seconds=5.0,
    )
    assert result, "add_video n'a rien retourné"

    video_id = result[0]["id"]
    print(f"   -> OK, vidéo ajoutée avec l'id {video_id}")

    return video_id


def test_get_video(storage, video_id):
    print("2. Récupération de la vidéo par id...")

    video = storage.get_video(video_id)
    assert video is not None, "get_video n'a rien trouvé"
    assert video["storage_path"] == TEST_STORAGE_PATH

    print(f"   -> OK, vidéo retrouvée : {video['filename']}")


def test_get_all_videos(storage, video_id):
    print("3. Vérification qu'elle apparaît dans get_all_videos...")

    all_videos = storage.get_all_videos()
    ids = [v["id"] for v in all_videos]
    assert video_id in ids, "la vidéo n'apparaît pas dans get_all_videos"

    print(f"   -> OK, {len(all_videos)} vidéo(s) au total")


def test_get_videos_by_human_detection(storage, video_id):
    print("4. Vérification via get_videos_by_human_detection...")

    human_videos = storage.get_videos_by_human_detection(human_detected=True)
    ids = [v["id"] for v in human_videos]
    assert video_id in ids, "la vidéo n'apparaît pas dans get_videos_by_human_detection"

    print(f"   -> OK, {len(human_videos)} vidéo(s) avec humain détecté")


def test_get_video_file(storage):
    print("5. Téléchargement du fichier depuis le bucket...")

    downloaded = storage.get_video_file(TEST_STORAGE_PATH)
    assert downloaded == FAKE_VIDEO_BYTES, "le contenu téléchargé ne correspond pas"

    print("   -> OK, contenu du fichier identique à l'original")


def test_list_video_files(storage):
    print("6. Vérification que le fichier apparaît dans list_video_files...")

    files = storage.list_video_files(prefix="test")
    names = [f["name"] for f in files]
    assert "fake_video.mp4" in names, "le fichier n'apparaît pas dans list_video_files"

    print("   -> OK, fichier trouvé dans le bucket")


def test_remove_video(storage, video_id):
    print("7. Suppression de la vidéo de test...")

    storage.remove_video(video_id)
    video_after = storage.get_video(video_id)
    assert video_after is None or video_after == {}, "la vidéo existe encore en base"

    print("   -> OK, vidéo supprimée (bucket + base)")


def run_tests():
    storage = Storage()

    video_id = test_add_video(storage)
    test_get_video(storage, video_id)
    test_get_all_videos(storage, video_id)
    test_get_videos_by_human_detection(storage, video_id)
    test_get_video_file(storage)
    test_list_video_files(storage)
    test_remove_video(storage, video_id)

    print("\nTous les tests sont passés.")


if __name__ == "__main__":
    run_tests()