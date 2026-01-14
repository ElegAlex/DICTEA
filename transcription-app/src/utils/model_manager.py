"""
Gestion du téléchargement et du chargement des modèles ML.
"""
import os
import logging
from pathlib import Path
from typing import Optional, Callable
from huggingface_hub import snapshot_download, hf_hub_download

from .config import get_config

logger = logging.getLogger(__name__)

# Mapping des modèles Whisper vers leurs identifiants HuggingFace (format CTranslate2)
WHISPER_MODELS = {
    "tiny": "Systran/faster-whisper-tiny",
    "base": "Systran/faster-whisper-base",
    "small": "Systran/faster-whisper-small",
    "medium": "Systran/faster-whisper-medium",
    "large-v2": "Systran/faster-whisper-large-v2",
    "large-v3": "Systran/faster-whisper-large-v3",
    # Modèle optimisé français
    "large-v3-french": "bofenghuang/whisper-large-v3-french-distil-dec16",
}

# Modèles Pyannote pour diarization
PYANNOTE_MODELS = {
    "segmentation": "pyannote/segmentation-3.0",
    "embedding": "pyannote/embedding",
    "diarization": "pyannote/speaker-diarization-3.1",
}


class ModelManager:
    """Gestionnaire de téléchargement et chargement des modèles."""
    
    def __init__(self, models_dir: Optional[Path] = None):
        self.models_dir = models_dir or get_config().paths.models
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurer HuggingFace pour utiliser notre dossier
        os.environ["HF_HOME"] = str(self.models_dir / "huggingface")
        os.environ["TRANSFORMERS_CACHE"] = str(self.models_dir / "transformers")
    
    def get_whisper_model_path(self, model_name: str = "medium") -> Path:
        """Retourne le chemin local du modèle Whisper."""
        if model_name not in WHISPER_MODELS:
            raise ValueError(f"Modèle inconnu: {model_name}. Disponibles: {list(WHISPER_MODELS.keys())}")
        
        model_path = self.models_dir / "whisper" / model_name
        return model_path
    
    def is_whisper_downloaded(self, model_name: str = "medium") -> bool:
        """Vérifie si le modèle Whisper est déjà téléchargé."""
        model_path = self.get_whisper_model_path(model_name)
        # Vérifier la présence du fichier model.bin
        return (model_path / "model.bin").exists()
    
    def download_whisper_model(
        self,
        model_name: str = "medium",
        progress_callback: Optional[Callable[[str, float], None]] = None,
    ) -> Path:
        """
        Télécharge le modèle Whisper si nécessaire.
        
        Args:
            model_name: Nom du modèle (tiny, base, small, medium, large-v3)
            progress_callback: Fonction de callback (message, pourcentage)
        
        Returns:
            Chemin vers le dossier du modèle
        """
        if model_name not in WHISPER_MODELS:
            raise ValueError(f"Modèle inconnu: {model_name}")
        
        model_path = self.get_whisper_model_path(model_name)
        
        if self.is_whisper_downloaded(model_name):
            logger.info(f"Modèle {model_name} déjà présent: {model_path}")
            if progress_callback:
                progress_callback(f"Modèle {model_name} prêt", 100.0)
            return model_path
        
        repo_id = WHISPER_MODELS[model_name]
        logger.info(f"Téléchargement du modèle {model_name} depuis {repo_id}...")
        
        if progress_callback:
            progress_callback(f"Téléchargement de {model_name}...", 0.0)
        
        try:
            # Télécharger le modèle complet
            snapshot_download(
                repo_id=repo_id,
                local_dir=model_path,
                local_dir_use_symlinks=False,
            )
            
            logger.info(f"Modèle {model_name} téléchargé: {model_path}")
            if progress_callback:
                progress_callback(f"Modèle {model_name} prêt", 100.0)
            
            return model_path
            
        except Exception as e:
            logger.error(f"Erreur téléchargement modèle {model_name}: {e}")
            raise
    
    def is_pyannote_ready(self) -> bool:
        """Vérifie si les modèles Pyannote sont configurés."""
        # Pyannote nécessite un token HuggingFace et acceptation des conditions
        token_path = Path.home() / ".huggingface" / "token"
        return token_path.exists()
    
    def get_model_sizes(self) -> dict:
        """Retourne les tailles approximatives des modèles."""
        return {
            "tiny": "75 Mo",
            "base": "150 Mo",
            "small": "500 Mo",
            "medium": "1.5 Go",
            "large-v3": "3 Go",
            "pyannote": "~500 Mo",
        }
    
    def cleanup_temp_files(self) -> None:
        """Nettoie les fichiers temporaires de téléchargement."""
        temp_dir = self.models_dir / "temp"
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir)
            logger.info("Fichiers temporaires nettoyés")
