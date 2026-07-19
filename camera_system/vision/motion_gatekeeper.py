import time


# ─────────────────────────────────────────────────────────────
# 1. Filtrage des faux déclenchements PIR (avant tout appel IA)
# ─────────────────────────────────────────────────────────────

class MotionGatekeeper:
    """
    Reçoit les signaux bruts du PIR et décide si c'est un vrai mouvement
    ou juste du bruit / un faux déclenchement.

    Règle simple : il faut que le PIR envoie plusieurs signaux rapprochés
    dans un court laps de temps pour qu'on considère que c'est un vrai mouvement.
    """

    def __init__(self):
        self.min_signals_required = 3
        self.window_seconds = 4.0
        self.debounce_seconds = 0.3
        self.signal_times = []
        self.last_signal_time = 0

    def on_pir_signal(self):
        """
        À appeler à chaque fois que le capteur PIR détecte quelque chose.
        Retourne True si on considère que c'est un vrai mouvement, False sinon.
        """
        now = time.monotonic()

        # Ignorer les signaux trop rapprochés 
        if now - self.last_signal_time < self.debounce_seconds:
            return False
        self.last_signal_time = now

        # On enregistre ce signal
        self.signal_times.append(now)

        # On garde seulement les signaux récents (dans la fenêtre)
        self.signal_times = [t for t in self.signal_times if now - t <= self.window_seconds]

        # A-t-on assez de signaux récents pour valider le mouvement ?
        if len(self.signal_times) >= self.min_signals_required:
            self.signal_times = []  # on repart de zéro pour la prochaine fois
            return True

        return False


# ─────────────────────────────────────────────────────────────
# 2. Suivi de présence pendant l'enregistrement (vérif périodique)
# ─────────────────────────────────────────────────────────────

class PresenceTracker:
    """
    Une fois qu'un enregistrement est en cours, cette classe permet de savoir
    quand relancer une vérification IA, et quand arrêter l'enregistrement
    si la personne n'est plus détectée plusieurs fois de suite.
    """

    def __init__(self):
        # Toutes les combien de secondes on revérifie la présence
        self.recheck_interval_seconds = 15.0

        # Nombre d'échecs consécutifs avant de considérer que la personne est partie
        self.max_consecutive_failures = 3

        # Compteur d'échecs consécutifs (remis à zéro dès qu'on revoit la personne)
        self.consecutive_failures = 0

        # Horodatage de la dernière vérification
        self.last_check_time = 0

    def should_check_now(self):
        """Retourne True s'il est temps de relancer une vérification IA."""
        now = time.monotonic()
        return now - self.last_check_time >= self.recheck_interval_seconds

    def report_check_result(self, human_was_detected):
        """
        À appeler juste après chaque vérification IA, avec le résultat.
        Retourne True si l'enregistrement doit continuer, False s'il faut arrêter.
        """
        self.last_check_time = time.monotonic()

        if human_was_detected:
            self.consecutive_failures = 0
            return True

        self.consecutive_failures += 1

        if self.consecutive_failures >= self.max_consecutive_failures:
            return False  # trop d'échecs → on arrête l'enregistrement

        return True

    def reset(self):
        """À appeler au début d'un nouvel enregistrement."""
        self.consecutive_failures = 0
        self.last_check_time = 0