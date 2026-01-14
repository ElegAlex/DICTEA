"""
Exceptions personnalisées pour l'application DICTEA.
Permet une meilleure catégorisation et des messages d'erreur clairs pour l'utilisateur.
"""


class DICTEAError(Exception):
    """Exception de base pour toutes les erreurs DICTEA."""

    def __init__(self, message: str, user_message: str = None):
        super().__init__(message)
        self.user_message = user_message or message


# =============================================================================
# Erreurs Audio
# =============================================================================

class AudioError(DICTEAError):
    """Erreur liée au traitement audio."""
    pass


class AudioFileNotFoundError(AudioError):
    """Fichier audio introuvable."""

    def __init__(self, path: str):
        super().__init__(
            f"Fichier audio introuvable: {path}",
            f"Le fichier audio '{path}' n'existe pas ou n'est pas accessible."
        )
        self.path = path


class AudioFormatError(AudioError):
    """Format audio non supporté."""

    def __init__(self, path: str, format: str):
        supported = "wav, mp3, m4a, flac, ogg, wma, aac"
        super().__init__(
            f"Format audio non supporté: {format}",
            f"Le format '{format}' n'est pas supporté.\nFormats acceptés: {supported}"
        )
        self.path = path
        self.format = format


class AudioCorruptedError(AudioError):
    """Fichier audio corrompu ou illisible."""

    def __init__(self, path: str, details: str = ""):
        super().__init__(
            f"Fichier audio corrompu: {path}",
            f"Le fichier audio '{path}' est corrompu ou illisible.\n{details}"
        )
        self.path = path


class AudioRecordingError(AudioError):
    """Erreur lors de l'enregistrement audio."""

    def __init__(self, details: str):
        super().__init__(
            f"Erreur d'enregistrement: {details}",
            f"Impossible d'enregistrer l'audio.\n{details}\n\n"
            "Vérifiez que votre microphone est connecté et autorisé."
        )


# =============================================================================
# Erreurs Modèles ML
# =============================================================================

class ModelError(DICTEAError):
    """Erreur liée aux modèles ML."""
    pass


class ModelNotFoundError(ModelError):
    """Modèle non trouvé localement."""

    def __init__(self, model_name: str):
        super().__init__(
            f"Modèle non trouvé: {model_name}",
            f"Le modèle '{model_name}' n'est pas téléchargé.\n\n"
            "Il sera téléchargé automatiquement lors de la première utilisation "
            "(connexion internet requise)."
        )
        self.model_name = model_name


class ModelDownloadError(ModelError):
    """Erreur lors du téléchargement d'un modèle."""

    def __init__(self, model_name: str, details: str = ""):
        super().__init__(
            f"Erreur téléchargement modèle: {model_name}",
            f"Impossible de télécharger le modèle '{model_name}'.\n\n"
            f"{details}\n\n"
            "Vérifiez votre connexion internet et réessayez."
        )
        self.model_name = model_name


class ModelLoadError(ModelError):
    """Erreur lors du chargement d'un modèle en mémoire."""

    def __init__(self, model_name: str, details: str = ""):
        super().__init__(
            f"Erreur chargement modèle: {model_name}",
            f"Impossible de charger le modèle '{model_name}' en mémoire.\n\n"
            f"{details}\n\n"
            "Vérifiez que vous avez suffisamment de RAM disponible."
        )
        self.model_name = model_name


class HuggingFaceTokenError(ModelError):
    """Token HuggingFace manquant ou invalide."""

    def __init__(self):
        super().__init__(
            "Token HuggingFace manquant",
            "Le modèle Pyannote nécessite un token HuggingFace.\n\n"
            "1. Créez un compte sur huggingface.co\n"
            "2. Acceptez les conditions du modèle pyannote/speaker-diarization-3.1\n"
            "3. Créez un token d'accès (Settings > Access Tokens)\n"
            "4. Exécutez: huggingface-cli login"
        )


# =============================================================================
# Erreurs Transcription
# =============================================================================

class TranscriptionError(DICTEAError):
    """Erreur lors de la transcription."""
    pass


class TranscriptionCancelledError(TranscriptionError):
    """Transcription annulée par l'utilisateur."""

    def __init__(self):
        super().__init__(
            "Transcription annulée",
            "La transcription a été annulée."
        )


class TranscriptionFailedError(TranscriptionError):
    """Échec de la transcription."""

    def __init__(self, details: str = ""):
        super().__init__(
            f"Échec de la transcription: {details}",
            f"La transcription a échoué.\n\n{details}"
        )


# =============================================================================
# Erreurs Diarization
# =============================================================================

class DiarizationError(DICTEAError):
    """Erreur lors de la diarization."""
    pass


class DiarizationFailedError(DiarizationError):
    """Échec de la diarization."""

    def __init__(self, details: str = ""):
        super().__init__(
            f"Échec de la diarization: {details}",
            f"L'identification des locuteurs a échoué.\n\n{details}"
        )


class NoSpeakersDetectedError(DiarizationError):
    """Aucun locuteur détecté."""

    def __init__(self):
        super().__init__(
            "Aucun locuteur détecté",
            "Aucun locuteur n'a été détecté dans l'audio.\n\n"
            "Vérifiez que le fichier contient de la parole."
        )


# =============================================================================
# Erreurs Système
# =============================================================================

class SystemError(DICTEAError):
    """Erreur système."""
    pass


class InsufficientMemoryError(SystemError):
    """Mémoire insuffisante."""

    def __init__(self, required_gb: float = 0, available_gb: float = 0):
        msg = "Mémoire RAM insuffisante pour cette opération."
        if required_gb and available_gb:
            msg += f"\n\nRequis: {required_gb:.1f} Go\nDisponible: {available_gb:.1f} Go"
        msg += "\n\nFermez d'autres applications ou utilisez un modèle plus petit."
        super().__init__(
            "Mémoire insuffisante",
            msg
        )


class DiskSpaceError(SystemError):
    """Espace disque insuffisant."""

    def __init__(self, required_gb: float = 0):
        msg = "Espace disque insuffisant."
        if required_gb:
            msg += f"\n\nEspace requis: {required_gb:.1f} Go"
        msg += "\n\nLibérez de l'espace disque et réessayez."
        super().__init__(
            "Espace disque insuffisant",
            msg
        )


def get_user_friendly_message(error: Exception) -> str:
    """Retourne un message d'erreur convivial pour l'utilisateur."""
    if isinstance(error, DICTEAError):
        return error.user_message

    # Erreurs Python standard
    error_str = str(error).lower()

    if "no space left" in error_str:
        return DiskSpaceError().user_message

    if "out of memory" in error_str or "memory" in error_str:
        return InsufficientMemoryError().user_message

    if "connection" in error_str or "network" in error_str:
        return (
            "Erreur de connexion réseau.\n\n"
            "Vérifiez votre connexion internet et réessayez."
        )

    if "permission" in error_str:
        return (
            "Erreur de permission.\n\n"
            "Vérifiez que vous avez les droits d'accès au fichier ou dossier."
        )

    # Message générique
    return f"Une erreur s'est produite:\n\n{str(error)}"
