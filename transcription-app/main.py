#!/usr/bin/env python3
"""
Application de Transcription Audio Offline
==========================================

Application client lourd pour transcrire des enregistrements audio
avec identification des locuteurs (diarization).

Stack technique:
- Transcription: faster-whisper (CTranslate2)
- Diarization: Pyannote Audio 3.1 / SpeechBrain
- UI: PySide6 (Qt6)

Configuration cible: Intel i7 / 16 Go RAM / CPU-only
"""
import sys
import os
import logging
import multiprocessing
from pathlib import Path

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("transcription_app.log", encoding="utf-8"),
    ]
)
logger = logging.getLogger(__name__)


def setup_environment():
    """Configure l'environnement d'exécution."""
    # Optimisations CPU Intel
    cpu_count = os.cpu_count() or 4
    physical_cores = cpu_count // 2  # Exclure hyperthreading
    
    os.environ.setdefault("OMP_NUM_THREADS", str(physical_cores))
    os.environ.setdefault("MKL_NUM_THREADS", str(physical_cores))
    os.environ.setdefault("OMP_WAIT_POLICY", "PASSIVE")
    
    # Désactiver les warnings GPU si pas de CUDA
    os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
    
    # HuggingFace offline si modèles locaux disponibles
    # os.environ.setdefault("HF_HUB_OFFLINE", "1")
    
    logger.info(f"Environnement configuré: {physical_cores} cores CPU")


def main():
    """Point d'entrée principal."""
    # Nécessaire pour PyInstaller sur Windows
    multiprocessing.freeze_support()
    
    setup_environment()
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        from src.ui.main_window import MainWindow
        
        # Créer l'application Qt
        app = QApplication(sys.argv)
        app.setApplicationName("Transcription Audio")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("TranscriptionApp")
        
        # Style moderne
        app.setStyle("Fusion")
        
        # Fenêtre principale
        window = MainWindow()
        window.show()
        
        logger.info("Application démarrée")
        
        # Boucle d'événements
        sys.exit(app.exec())
        
    except ImportError as e:
        logger.error(f"Dépendance manquante: {e}")
        print(f"\nErreur: Dépendance manquante: {e}")
        print("Installez les dépendances avec: pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        logger.exception(f"Erreur fatale: {e}")
        print(f"\nErreur fatale: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
