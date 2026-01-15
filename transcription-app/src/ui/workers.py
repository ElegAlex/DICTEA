"""
Workers QThread pour les tâches longues (transcription, diarization).
Permet de maintenir l'UI responsive pendant le traitement.
"""
import gc
import logging
import traceback
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal

from ..core.audio_processor import AudioProcessor
from ..core.diarizer import DiarizationResult, Diarizer, assign_speakers_to_transcription
from ..core.exceptions import (
    AudioFileNotFoundError,
    DICTEAError,
    HuggingFaceTokenError,
    ModelLoadError,
    TranscriptionCancelledError,
    get_user_friendly_message,
)
from ..core.transcriber import Transcriber, TranscriptionResult

logger = logging.getLogger(__name__)


class TranscriptionWorker(QObject):
    """
    Worker pour la transcription en arrière-plan.

    Signals:
        started: Émis au démarrage
        progress: (étape: str, pourcentage: float, détail: str)
        segment_ready: Émis pour chaque segment transcrit (index, texte)
        finished: Émis à la fin avec le résultat
        error: Émis en cas d'erreur (message utilisateur)
    """

    started = Signal()
    progress = Signal(str, float, str)
    segment_ready = Signal(int, str)
    finished = Signal(TranscriptionResult)
    error = Signal(str)

    def __init__(
        self,
        audio_path: Path,
        transcriber: Transcriber,
        language: str | None = None,
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
            self._validate_input()
            self.started.emit()
            self._run_transcription()
        except DICTEAError as e:
            logger.error(f"Erreur transcription: {e}\n{traceback.format_exc()}")
            self.error.emit(e.user_message)
        except Exception as e:
            logger.error(f"Erreur transcription: {e}\n{traceback.format_exc()}")
            self.error.emit(get_user_friendly_message(e))

    def _validate_input(self) -> None:
        """Valide le fichier d'entrée."""
        if not self.audio_path.exists():
            raise AudioFileNotFoundError(str(self.audio_path))
        AudioProcessor().validate_audio_file(self.audio_path)

    def _run_transcription(self) -> None:
        """Exécute la transcription proprement dite."""
        self.progress.emit("Initialisation", 0.0, "Chargement du modèle...")

        self._load_model_if_needed()

        if self._cancelled:
            raise TranscriptionCancelledError()

        self.progress.emit("Transcription", 20.0, "Démarrage...")

        result = self._transcribe_with_progress()

        if self._cancelled:
            raise TranscriptionCancelledError()

        segment_count = len(result.segments)
        self.progress.emit("Terminé", 100.0, f"{segment_count} segments transcrits")
        self.finished.emit(result)

    def _load_model_if_needed(self) -> None:
        """Charge le modèle si nécessaire."""
        if self.transcriber.model is not None:
            return

        try:
            def model_progress(msg, pct):
                self.progress.emit("Modèle", pct * 0.2, msg)
            self.transcriber.load_model(progress_callback=model_progress)
        except Exception as e:
            raise ModelLoadError(self.transcriber.model_name, str(e))

    def _transcribe_with_progress(self) -> TranscriptionResult:
        """Transcrit avec callback de progression."""
        def transcription_progress(idx, text):
            pct = min(20.0 + (idx * 2), 95.0)
            display_text = text[:60] + "..." if len(text) > 60 else text
            self.progress.emit("Transcription", pct, display_text)
            self.segment_ready.emit(idx, text)

        return self.transcriber.transcribe(
            self.audio_path,
            language=self.language,
            progress_callback=transcription_progress,
        )


class DiarizationWorker(QObject):
    """Worker pour la diarization en arrière-plan."""

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
            self._validate_input()
            self.started.emit()
            self._run_diarization()
        except DICTEAError as e:
            logger.error(f"Erreur diarization: {e}\n{traceback.format_exc()}")
            self.error.emit(e.user_message)
        except Exception as e:
            logger.error(f"Erreur diarization: {e}\n{traceback.format_exc()}")
            self.error.emit(get_user_friendly_message(e))

    def _validate_input(self) -> None:
        """Valide le fichier d'entrée."""
        if not self.audio_path.exists():
            raise AudioFileNotFoundError(str(self.audio_path))
        AudioProcessor().validate_audio_file(self.audio_path)

    def _run_diarization(self) -> None:
        """Exécute la diarization."""
        self.progress.emit("Initialisation", 0.0, "Chargement modèle diarization...")

        def diarization_progress(msg, pct):
            self.progress.emit("Diarization", pct, msg)

        try:
            result = self.diarizer.diarize(
                self.audio_path,
                min_speakers=self.min_speakers if self.min_speakers > 0 else None,
                max_speakers=self.max_speakers if self.max_speakers > 0 else None,
                progress_callback=diarization_progress,
            )
        except Exception as e:
            error_str = str(e).lower()
            if "token" in error_str or "401" in error_str or "unauthorized" in error_str:
                raise HuggingFaceTokenError()
            raise

        if self._cancelled:
            return

        self.progress.emit("Terminé", 100.0, f"{result.num_speakers} locuteurs identifiés")
        self.finished.emit(result)


class FullPipelineWorker(QObject):
    """Worker pour le pipeline complet: transcription + diarization."""

    started = Signal()
    progress = Signal(str, float, str)
    transcription_done = Signal(TranscriptionResult)
    finished = Signal(TranscriptionResult)
    error = Signal(str)

    def __init__(
        self,
        audio_path: Path,
        transcriber: Transcriber,
        diarizer: Diarizer,
        language: str | None = None,
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
            self._validate_input()
            self.started.emit()
            self._run_pipeline()
        except DICTEAError as e:
            logger.error(f"Erreur pipeline: {e}\n{traceback.format_exc()}")
            self.error.emit(e.user_message)
        except Exception as e:
            logger.error(f"Erreur pipeline: {e}\n{traceback.format_exc()}")
            self.error.emit(get_user_friendly_message(e))
        finally:
            self._cleanup()

    def _validate_input(self) -> None:
        """Valide le fichier d'entrée."""
        if not self.audio_path.exists():
            raise AudioFileNotFoundError(str(self.audio_path))
        if not AudioProcessor.is_supported(self.audio_path):
            raise AudioFormatError(str(self.audio_path), self.audio_path.suffix)

    def _run_pipeline(self) -> None:
        """Exécute le pipeline complet."""
        transcription_result = self._run_transcription()
        if self._cancelled:
            return

        diarization_result = self._run_diarization()
        if self._cancelled:
            return

        final_result = self._merge_results(transcription_result, diarization_result)
        self.finished.emit(final_result)

    def _run_transcription(self) -> TranscriptionResult:
        """Étape 1: Transcription."""
        self.progress.emit("Transcription", 0.0, "Chargement du modèle...")

        if self.transcriber.model is None:
            try:
                def model_progress(msg, pct):
                    self.progress.emit("Transcription", pct * 0.1, msg)
                self.transcriber.load_model(progress_callback=model_progress)
            except Exception as e:
                raise ModelLoadError(self.transcriber.model_name, str(e))

        if self._cancelled:
            raise TranscriptionCancelledError()

        self.progress.emit("Transcription", 10.0, "En cours...")

        result = self.transcriber.transcribe(
            self.audio_path,
            language=self.language,
        )

        self.progress.emit("Transcription", 40.0, "Terminée")
        self.transcription_done.emit(result)

        return result

    def _run_diarization(self) -> DiarizationResult:
        """Étape 2: Diarization."""
        self.progress.emit("Diarization", 45.0, "Identification des locuteurs...")

        def diarization_progress(msg, pct):
            mapped_pct = 45.0 + (pct * 0.5)
            self.progress.emit("Diarization", mapped_pct, msg)

        try:
            result = self.diarizer.diarize(
                self.audio_path,
                min_speakers=self.min_speakers if self.min_speakers > 0 else None,
                max_speakers=self.max_speakers if self.max_speakers > 0 else None,
                progress_callback=diarization_progress,
            )
        except Exception as e:
            error_str = str(e).lower()
            if "token" in error_str or "401" in error_str or "unauthorized" in error_str:
                raise HuggingFaceTokenError()
            raise

        return result

    def _merge_results(
        self,
        transcription: TranscriptionResult,
        diarization: DiarizationResult,
    ) -> TranscriptionResult:
        """Étape 3: Fusion des résultats."""
        self.progress.emit("Fusion", 95.0, "Attribution des locuteurs...")

        final_result = assign_speakers_to_transcription(transcription, diarization)

        self.progress.emit(
            "Terminé", 100.0,
            f"{len(final_result.segments)} segments, {diarization.num_speakers} locuteurs"
        )

        return final_result

    def _cleanup(self) -> None:
        """Libère la mémoire après le traitement."""
        gc.collect()


class BatchWorker(QObject):
    """Worker pour le traitement par lots."""

    started = Signal()
    progress = Signal(int, int, str, float)  # current, total, filename, percent
    item_completed = Signal(int, bool, str)  # index, success, message
    finished = Signal(object)  # BatchResult
    error = Signal(str)

    def __init__(
        self,
        files: list,
        transcriber: Transcriber,
        diarizer: Diarizer | None,
        options: dict,
    ):
        super().__init__()
        self.files = files
        self.transcriber = transcriber
        self.diarizer = diarizer
        self.options = options
        self._cancelled = False
        self._processor = None

    def cancel(self) -> None:
        self._cancelled = True
        if self._processor:
            self._processor.cancel()

    def run(self) -> None:
        try:
            from ..core.batch_processor import BatchOptions, BatchProcessor

            self.started.emit()

            options = BatchOptions(
                language=self.options.get("language"),
                use_diarization=self.options.get("use_diarization", True),
                min_speakers=self.options.get("min_speakers", 0),
                max_speakers=self.options.get("max_speakers", 0),
                output_dir=self.options.get("output_dir"),
                output_format=self.options.get("output_format", "txt"),
                include_timestamps=self.options.get("include_timestamps", True),
                include_speakers=self.options.get("include_speakers", True),
                skip_existing=self.options.get("skip_existing", False),
            )

            self._processor = BatchProcessor(self.transcriber, self.diarizer)

            def progress_callback(current, total, filename, percent):
                self.progress.emit(current, total, filename, percent)

            result = self._processor.process(self.files, options, progress_callback)

            for i, item in enumerate(result.items):
                success = item.status.value == "completed"
                msg = item.error_message or f"Terminé en {item.processing_time:.1f}s"
                self.item_completed.emit(i, success, msg)

            self.finished.emit(result)

        except Exception as e:
            logger.error(f"Erreur batch: {e}\n{traceback.format_exc()}")
            self.error.emit(get_user_friendly_message(e))


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

        self.thread.started.connect(self.worker.run)

        if hasattr(self.worker, 'finished'):
            self.worker.finished.connect(self._on_finished)
        if hasattr(self.worker, 'error'):
            self.worker.error.connect(self._on_finished)

    def _on_finished(self, *args) -> None:
        """Nettoie proprement à la fin du traitement."""
        self.thread.quit()

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
