"""
Workers QThread pour les tâches longues (transcription, diarization).
Permet de maintenir l'UI responsive pendant le traitement.
"""
import logging
import traceback
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, QThread, Signal

from ..core.transcriber import Transcriber, TranscriptionResult
from ..core.diarizer import Diarizer, DiarizationResult, assign_speakers_to_transcription
from ..core.audio_processor import AudioProcessor

logger = logging.getLogger(__name__)


class TranscriptionWorker(QObject):
    """
    Worker pour la transcription en arrière-plan.
    
    Signals:
        started: Émis au démarrage
        progress: (étape: str, pourcentage: float, détail: str)
        segment_ready: Émis pour chaque segment transcrit (index, texte)
        finished: Émis à la fin avec le résultat
        error: Émis en cas d'erreur
    """
    
    started = Signal()
    progress = Signal(str, float, str)  # étape, pourcentage, détail
    segment_ready = Signal(int, str)     # index, texte du segment
    finished = Signal(TranscriptionResult)
    error = Signal(str)
    
    def __init__(
        self,
        audio_path: Path,
        transcriber: Transcriber,
        language: Optional[str] = None,
    ):
        super().__init__()
        self.audio_path = audio_path
        self.transcriber = transcriber
        self.language = language
        self._cancelled = False
    
    def cancel(self) -> None:
        """Demande l'annulation du traitement."""
        self._cancelled = True
    
    def run(self) -> None:
        """Exécute la transcription."""
        try:
            self.started.emit()
            self.progress.emit("Initialisation", 0.0, "Chargement du modèle...")
            
            # Charger le modèle si nécessaire
            if self.transcriber.model is None:
                def model_progress(msg, pct):
                    self.progress.emit("Modèle", pct * 0.2, msg)
                self.transcriber.load_model(progress_callback=model_progress)
            
            if self._cancelled:
                return
            
            self.progress.emit("Transcription", 20.0, "Démarrage...")
            
            # Transcription avec callback de progression
            segment_count = 0
            
            def transcription_progress(idx, text):
                nonlocal segment_count
                segment_count = idx + 1
                # Estimation progression (on ne connait pas le total à l'avance)
                pct = min(20.0 + (idx * 2), 95.0)
                self.progress.emit("Transcription", pct, text[:60] + "..." if len(text) > 60 else text)
                self.segment_ready.emit(idx, text)
            
            result = self.transcriber.transcribe(
                self.audio_path,
                language=self.language,
                progress_callback=transcription_progress,
            )
            
            if self._cancelled:
                return
            
            self.progress.emit("Terminé", 100.0, f"{segment_count} segments transcrits")
            self.finished.emit(result)
            
        except Exception as e:
            logger.error(f"Erreur transcription: {e}\n{traceback.format_exc()}")
            self.error.emit(str(e))


class DiarizationWorker(QObject):
    """
    Worker pour la diarization en arrière-plan.
    """
    
    started = Signal()
    progress = Signal(str, float, str)
    finished = Signal(DiarizationResult)
    error = Signal(str)
    
    def __init__(
        self,
        audio_path: Path,
        diarizer: Diarizer,
        min_speakers: int = 0,
        max_speakers: int = 0,
    ):
        super().__init__()
        self.audio_path = audio_path
        self.diarizer = diarizer
        self.min_speakers = min_speakers
        self.max_speakers = max_speakers
        self._cancelled = False
    
    def cancel(self) -> None:
        self._cancelled = True
    
    def run(self) -> None:
        try:
            self.started.emit()
            self.progress.emit("Initialisation", 0.0, "Chargement modèle diarization...")
            
            def diarization_progress(msg, pct):
                self.progress.emit("Diarization", pct, msg)
            
            result = self.diarizer.diarize(
                self.audio_path,
                min_speakers=self.min_speakers if self.min_speakers > 0 else None,
                max_speakers=self.max_speakers if self.max_speakers > 0 else None,
                progress_callback=diarization_progress,
            )
            
            if self._cancelled:
                return
            
            self.progress.emit("Terminé", 100.0, f"{result.num_speakers} locuteurs identifiés")
            self.finished.emit(result)
            
        except Exception as e:
            logger.error(f"Erreur diarization: {e}\n{traceback.format_exc()}")
            self.error.emit(str(e))


class FullPipelineWorker(QObject):
    """
    Worker pour le pipeline complet: transcription + diarization.
    """
    
    started = Signal()
    progress = Signal(str, float, str)
    transcription_done = Signal(TranscriptionResult)
    finished = Signal(TranscriptionResult)  # Résultat final avec speakers
    error = Signal(str)
    
    def __init__(
        self,
        audio_path: Path,
        transcriber: Transcriber,
        diarizer: Diarizer,
        language: Optional[str] = None,
        min_speakers: int = 0,
        max_speakers: int = 0,
    ):
        super().__init__()
        self.audio_path = audio_path
        self.transcriber = transcriber
        self.diarizer = diarizer
        self.language = language
        self.min_speakers = min_speakers
        self.max_speakers = max_speakers
        self._cancelled = False
    
    def cancel(self) -> None:
        self._cancelled = True
    
    def run(self) -> None:
        try:
            self.started.emit()
            
            # === ÉTAPE 1: Transcription ===
            self.progress.emit("Transcription", 0.0, "Chargement du modèle...")
            
            if self.transcriber.model is None:
                def model_progress(msg, pct):
                    self.progress.emit("Transcription", pct * 0.1, msg)
                self.transcriber.load_model(progress_callback=model_progress)
            
            if self._cancelled:
                return
            
            self.progress.emit("Transcription", 10.0, "En cours...")
            
            transcription_result = self.transcriber.transcribe(
                self.audio_path,
                language=self.language,
            )
            
            if self._cancelled:
                return
            
            self.progress.emit("Transcription", 40.0, "Terminée")
            self.transcription_done.emit(transcription_result)
            
            # === ÉTAPE 2: Diarization ===
            self.progress.emit("Diarization", 45.0, "Identification des locuteurs...")
            
            def diarization_progress(msg, pct):
                # Mapper 0-100% vers 45-95%
                mapped_pct = 45.0 + (pct * 0.5)
                self.progress.emit("Diarization", mapped_pct, msg)
            
            diarization_result = self.diarizer.diarize(
                self.audio_path,
                min_speakers=self.min_speakers if self.min_speakers > 0 else None,
                max_speakers=self.max_speakers if self.max_speakers > 0 else None,
                progress_callback=diarization_progress,
            )
            
            if self._cancelled:
                return
            
            # === ÉTAPE 3: Fusion ===
            self.progress.emit("Fusion", 95.0, "Attribution des locuteurs...")
            
            final_result = assign_speakers_to_transcription(
                transcription_result,
                diarization_result,
            )
            
            self.progress.emit("Terminé", 100.0, 
                f"{len(final_result.segments)} segments, {diarization_result.num_speakers} locuteurs")
            self.finished.emit(final_result)
            
        except Exception as e:
            logger.error(f"Erreur pipeline: {e}\n{traceback.format_exc()}")
            self.error.emit(str(e))


class WorkerThread:
    """
    Utilitaire pour lancer un worker dans un QThread.
    
    Usage:
        worker = TranscriptionWorker(...)
        thread = WorkerThread(worker)
        thread.start()
    """
    
    def __init__(self, worker: QObject):
        self.worker = worker
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        
        # Connecter le démarrage du thread à la méthode run du worker
        self.thread.started.connect(self.worker.run)
        
        # Nettoyer à la fin
        if hasattr(self.worker, 'finished'):
            self.worker.finished.connect(self.thread.quit)
        if hasattr(self.worker, 'error'):
            self.worker.error.connect(self.thread.quit)
    
    def start(self) -> None:
        """Démarre le thread."""
        self.thread.start()
    
    def stop(self) -> None:
        """Arrête le thread."""
        if hasattr(self.worker, 'cancel'):
            self.worker.cancel()
        self.thread.quit()
        self.thread.wait(5000)
    
    def is_running(self) -> bool:
        return self.thread.isRunning()
