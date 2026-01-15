"""
Module de traitement par lots (batch processing).
Permet de transcrire plusieurs fichiers audio en séquence.
"""
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

from .audio_processor import AudioProcessor
from .diarizer import Diarizer, assign_speakers_to_transcription
from .exceptions import AudioFileNotFoundError, AudioFormatError
from .transcriber import Transcriber, TranscriptionResult

logger = logging.getLogger(__name__)


class BatchItemStatus(Enum):
    """Statut d'un élément du batch."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class BatchItem:
    """Représente un fichier dans le batch."""
    path: Path
    status: BatchItemStatus = BatchItemStatus.PENDING
    result: TranscriptionResult | None = None
    error_message: str | None = None
    processing_time: float = 0.0

    @property
    def filename(self) -> str:
        return self.path.name


@dataclass
class BatchResult:
    """Résultat global du batch processing."""
    items: list[BatchItem]
    total_time: float = 0.0
    started_at: datetime | None = None
    finished_at: datetime | None = None

    @property
    def total_count(self) -> int:
        return len(self.items)

    @property
    def completed_count(self) -> int:
        return sum(1 for item in self.items if item.status == BatchItemStatus.COMPLETED)

    @property
    def failed_count(self) -> int:
        return sum(1 for item in self.items if item.status == BatchItemStatus.FAILED)

    @property
    def success_rate(self) -> float:
        if self.total_count == 0:
            return 0.0
        return self.completed_count / self.total_count * 100


@dataclass
class BatchOptions:
    """Options pour le batch processing."""
    language: str | None = None
    use_diarization: bool = True
    min_speakers: int = 0
    max_speakers: int = 0
    output_dir: Path | None = None
    output_format: str = "txt"  # txt, srt, both
    include_timestamps: bool = True
    include_speakers: bool = True
    skip_existing: bool = False


class BatchProcessor:
    """
    Processeur de batch pour transcrire plusieurs fichiers.

    Usage:
        processor = BatchProcessor(transcriber, diarizer)
        result = processor.process(files, options, progress_callback)
    """

    def __init__(
        self,
        transcriber: Transcriber,
        diarizer: Diarizer | None = None,
    ):
        self.transcriber = transcriber
        self.diarizer = diarizer
        self.audio_processor = AudioProcessor()
        self._cancelled = False

    def cancel(self) -> None:
        """Annule le traitement en cours."""
        self._cancelled = True

    def process(
        self,
        files: list[Path],
        options: BatchOptions,
        progress_callback: Callable[[int, int, str, float], None] | None = None,
    ) -> BatchResult:
        """
        Traite une liste de fichiers audio.

        Args:
            files: Liste des fichiers à traiter
            options: Options de traitement
            progress_callback: Callback (current, total, filename, percent)

        Returns:
            BatchResult avec les résultats de tous les fichiers
        """
        self._cancelled = False
        items = [BatchItem(path=f) for f in files]
        result = BatchResult(items=items, started_at=datetime.now())

        for i, item in enumerate(items):
            if self._cancelled:
                self._mark_remaining_as_skipped(items, i)
                break

            if progress_callback:
                progress_callback(i + 1, len(items), item.filename, 0.0)

            self._process_item(item, options, progress_callback, i, len(items))

        result.finished_at = datetime.now()
        result.total_time = (result.finished_at - result.started_at).total_seconds()

        logger.info(
            f"Batch terminé: {result.completed_count}/{result.total_count} réussis, "
            f"{result.failed_count} échecs, {result.total_time:.1f}s"
        )

        return result

    def _process_item(
        self,
        item: BatchItem,
        options: BatchOptions,
        progress_callback: Callable | None,
        current_index: int,
        total: int,
    ) -> None:
        """Traite un seul fichier du batch."""
        import time
        start_time = time.time()
        item.status = BatchItemStatus.PROCESSING

        try:
            self._validate_file(item.path)

            if options.skip_existing and self._output_exists(item.path, options):
                item.status = BatchItemStatus.SKIPPED
                logger.info(f"Fichier ignoré (existe déjà): {item.filename}")
                return

            result = self._transcribe_file(item.path, options, progress_callback, current_index, total)
            item.result = result
            item.status = BatchItemStatus.COMPLETED

            self._save_result(item, options)

        except Exception as e:
            item.status = BatchItemStatus.FAILED
            item.error_message = str(e)
            logger.error(f"Erreur traitement {item.filename}: {e}")

        finally:
            item.processing_time = time.time() - start_time

    def _validate_file(self, path: Path) -> None:
        """Valide un fichier avant traitement."""
        if not path.exists():
            raise AudioFileNotFoundError(str(path))
        if not AudioProcessor.is_supported(path):
            raise AudioFormatError(str(path), path.suffix)

    def _transcribe_file(
        self,
        path: Path,
        options: BatchOptions,
        progress_callback: Callable | None,
        current_index: int,
        total: int,
    ) -> TranscriptionResult:
        """Transcrit un fichier avec ou sans diarization."""

        def item_progress(pct: float):
            if progress_callback:
                progress_callback(current_index + 1, total, path.name, pct)

        # Transcription
        item_progress(10.0)
        result = self.transcriber.transcribe(path, language=options.language)
        item_progress(50.0)

        # Diarization si demandée
        if options.use_diarization and self.diarizer:
            diarization_result = self.diarizer.diarize(
                path,
                min_speakers=options.min_speakers if options.min_speakers > 0 else None,
                max_speakers=options.max_speakers if options.max_speakers > 0 else None,
            )
            item_progress(90.0)
            result = assign_speakers_to_transcription(result, diarization_result)

        item_progress(100.0)
        return result

    def _output_exists(self, input_path: Path, options: BatchOptions) -> bool:
        """Vérifie si le fichier de sortie existe déjà."""
        output_dir = options.output_dir or input_path.parent
        base_name = input_path.stem

        if options.output_format in ("txt", "both") and (output_dir / f"{base_name}.txt").exists():
            return True
        return options.output_format in ("srt", "both") and (output_dir / f"{base_name}.srt").exists()

    def _save_result(self, item: BatchItem, options: BatchOptions) -> None:
        """Sauvegarde le résultat d'un item."""
        if item.result is None:
            return

        output_dir = options.output_dir or item.path.parent
        output_dir.mkdir(parents=True, exist_ok=True)
        base_name = item.path.stem

        if options.output_format in ("txt", "both"):
            txt_path = output_dir / f"{base_name}.txt"
            content = item.result.to_text(
                include_timestamps=options.include_timestamps,
                include_speakers=options.include_speakers,
            )
            txt_path.write_text(content, encoding="utf-8")
            logger.info(f"Sauvegardé: {txt_path}")

        if options.output_format in ("srt", "both"):
            srt_path = output_dir / f"{base_name}.srt"
            srt_path.write_text(item.result.to_srt(), encoding="utf-8")
            logger.info(f"Sauvegardé: {srt_path}")

    def _mark_remaining_as_skipped(self, items: list[BatchItem], start_index: int) -> None:
        """Marque les éléments restants comme ignorés."""
        for i in range(start_index, len(items)):
            if items[i].status == BatchItemStatus.PENDING:
                items[i].status = BatchItemStatus.SKIPPED


def get_audio_files_from_directory(
    directory: Path,
    recursive: bool = False,
) -> list[Path]:
    """
    Récupère tous les fichiers audio d'un répertoire.

    Args:
        directory: Répertoire à scanner
        recursive: Si True, inclut les sous-répertoires

    Returns:
        Liste des fichiers audio triés par nom
    """
    if not directory.is_dir():
        return []

    pattern = "**/*" if recursive else "*"
    files = []

    for ext in AudioProcessor.SUPPORTED_FORMATS:
        files.extend(directory.glob(f"{pattern}{ext}"))

    return sorted(files, key=lambda p: p.name.lower())
