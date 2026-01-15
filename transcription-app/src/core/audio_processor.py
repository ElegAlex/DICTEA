"""
Module de traitement audio: enregistrement, conversion, validation.
"""
import logging
import os
import queue
import sys
import threading
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
from pydub.utils import which

from ..utils.config import AudioConfig, get_config
from .exceptions import AudioCorruptedError, AudioDependencyError, AudioFormatError

logger = logging.getLogger(__name__)


@dataclass
class AudioDevice:
    """Périphérique audio."""
    index: int
    name: str
    channels: int
    sample_rate: float
    is_input: bool


class AudioRecorder:
    """
    Enregistreur audio pour capturer les réunions.

    Utilise sounddevice pour l'enregistrement en temps réel.
    """

    def __init__(self, config: AudioConfig | None = None):
        self.config = config or get_config().audio
        self._recording = False
        self._audio_queue: queue.Queue = queue.Queue()
        self._recorded_frames: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None
        self._record_thread: threading.Thread | None = None

    @staticmethod
    def list_input_devices() -> list[AudioDevice]:
        """Liste les périphériques d'entrée audio disponibles."""
        devices = []
        for i, dev in enumerate(sd.query_devices()):
            if dev['max_input_channels'] > 0:
                devices.append(AudioDevice(
                    index=i,
                    name=dev['name'],
                    channels=dev['max_input_channels'],
                    sample_rate=dev['default_samplerate'],
                    is_input=True,
                ))
        return devices

    @staticmethod
    def get_default_input_device() -> AudioDevice | None:
        """Retourne le périphérique d'entrée par défaut."""
        try:
            default_idx = sd.default.device[0]
            if default_idx is not None:
                dev = sd.query_devices(default_idx)
                return AudioDevice(
                    index=default_idx,
                    name=dev['name'],
                    channels=dev['max_input_channels'],
                    sample_rate=dev['default_samplerate'],
                    is_input=True,
                )
        except Exception as e:
            logger.warning(f"Impossible de récupérer le périphérique par défaut: {e}")
        return None

    def start_recording(
        self,
        device_index: int | None = None,
        callback: Callable[[float], None] | None = None,
    ) -> None:
        """
        Démarre l'enregistrement audio.

        Args:
            device_index: Index du périphérique (None = défaut)
            callback: Fonction appelée avec la durée enregistrée (en secondes)
        """
        if self._recording:
            logger.warning("Enregistrement déjà en cours")
            return

        device_index = device_index or self.config.input_device

        self._recorded_frames = []
        self._recording = True

        def audio_callback(indata, frames, time_info, status):
            if status:
                logger.warning(f"Audio status: {status}")
            self._audio_queue.put(indata.copy())

        self._stream = sd.InputStream(
            samplerate=self.config.sample_rate,
            channels=self.config.channels,
            device=device_index,
            callback=audio_callback,
            dtype=np.float32,
        )

        self._stream.start()

        # Thread pour collecter les frames
        def collect_frames():
            total_samples = 0
            while self._recording or not self._audio_queue.empty():
                try:
                    frame = self._audio_queue.get(timeout=0.1)
                    self._recorded_frames.append(frame)
                    total_samples += len(frame)

                    if callback:
                        duration = total_samples / self.config.sample_rate
                        callback(duration)

                except queue.Empty:
                    continue

        self._record_thread = threading.Thread(target=collect_frames, daemon=True)
        self._record_thread.start()

        logger.info(f"Enregistrement démarré (device={device_index}, rate={self.config.sample_rate})")

    def stop_recording(self) -> np.ndarray | None:
        """
        Arrête l'enregistrement et retourne les données audio.

        Returns:
            Array numpy contenant l'audio enregistré
        """
        if not self._recording:
            logger.warning("Aucun enregistrement en cours")
            return None

        self._recording = False

        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        if self._record_thread:
            self._record_thread.join(timeout=2.0)
            self._record_thread = None

        if not self._recorded_frames:
            logger.warning("Aucune donnée audio enregistrée")
            return None

        audio_data = np.concatenate(self._recorded_frames, axis=0)
        duration = len(audio_data) / self.config.sample_rate

        logger.info(f"Enregistrement arrêté: {duration:.1f}s, {len(audio_data)} samples")

        return audio_data

    def save_recording(
        self,
        audio_data: np.ndarray,
        output_path: Path,
        format: str | None = None,
    ) -> Path:
        """
        Sauvegarde l'audio enregistré dans un fichier.

        Args:
            audio_data: Données audio numpy
            output_path: Chemin de sortie
            format: Format de sortie (wav, mp3, etc.)

        Returns:
            Chemin du fichier sauvegardé
        """
        format = format or self.config.export_format

        # Assurer l'extension correcte
        if not output_path.suffix:
            output_path = output_path.with_suffix(f".{format}")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        sf.write(
            str(output_path),
            audio_data,
            self.config.sample_rate,
            format=format.upper() if format != "wav" else None,
        )

        logger.info(f"Audio sauvegardé: {output_path}")
        return output_path

    @property
    def is_recording(self) -> bool:
        return self._recording


class AudioProcessor:
    """
    Traitement et conversion de fichiers audio.

    Normalise les fichiers audio pour le format optimal Whisper:
    - 16 kHz
    - Mono
    - 16-bit PCM
    """

    SUPPORTED_FORMATS = {'.wav', '.mp3', '.m4a', '.flac', '.ogg', '.wma', '.aac'}
    WHISPER_SAMPLE_RATE = 16000

    def __init__(self, config: AudioConfig | None = None):
        self.config = config or get_config().audio
        self._ffmpeg_checked = False

    def _candidate_ffmpeg_dirs(self) -> list[Path]:
        """Liste les dossiers potentiels contenant FFmpeg."""
        dirs: list[Path] = []

        env_dir = os.getenv("DICTEA_FFMPEG_DIR")
        if env_dir:
            dirs.append(Path(env_dir))

        if getattr(sys, "frozen", False):
            exe_dir = Path(sys.executable).parent
            dirs.extend([exe_dir, exe_dir / "ffmpeg"])

        app_root = Path(__file__).resolve().parents[2]
        dirs.extend([
            app_root,
            app_root / "resources",
            app_root / "resources" / "ffmpeg",
        ])

        return dirs

    def _resolve_ffmpeg_paths(self) -> tuple[str | None, str | None]:
        """Retourne les chemins de ffmpeg/ffprobe si disponibles."""
        converter = which("ffmpeg")
        ffprobe = which("ffprobe")

        if converter and ffprobe:
            return converter, ffprobe

        exe_name = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
        probe_name = "ffprobe.exe" if os.name == "nt" else "ffprobe"

        for directory in self._candidate_ffmpeg_dirs():
            converter_path = directory / exe_name
            ffprobe_path = directory / probe_name
            if converter_path.exists() and ffprobe_path.exists():
                return str(converter_path), str(ffprobe_path)

        return None, None

    def _ensure_ffmpeg(self) -> None:
        """Configure FFmpeg pour pydub ou lève une erreur explicite."""
        if self._ffmpeg_checked:
            return

        converter, ffprobe = self._resolve_ffmpeg_paths()
        if converter and ffprobe:
            AudioSegment.converter = converter
            AudioSegment.ffprobe = ffprobe
            self._ffmpeg_checked = True
            return

        raise AudioDependencyError("FFmpeg introuvable")

    def ensure_ffmpeg(self) -> None:
        """Expose la vérification FFmpeg pour d'autres modules."""
        self._ensure_ffmpeg()

    @classmethod
    def is_supported(cls, file_path: Path) -> bool:
        """Vérifie si le format de fichier est supporté."""
        return file_path.suffix.lower() in cls.SUPPORTED_FORMATS

    def validate_audio_file(self, file_path: Path) -> dict:
        """Valide qu'un fichier audio est lisible et retourne ses infos."""
        if not self.is_supported(file_path):
            raise AudioFormatError(str(file_path), file_path.suffix)

        self._ensure_ffmpeg()

        try:
            return self.get_audio_info(file_path)
        except CouldntDecodeError as exc:
            raise AudioCorruptedError(str(file_path), str(exc)) from exc

    def get_audio_info(self, file_path: Path) -> dict:
        """
        Retourne les informations sur un fichier audio.

        Returns:
            dict avec duration, sample_rate, channels, format
        """
        try:
            self._ensure_ffmpeg()
            audio = AudioSegment.from_file(str(file_path))
            return {
                "duration": len(audio) / 1000.0,  # secondes
                "sample_rate": audio.frame_rate,
                "channels": audio.channels,
                "format": file_path.suffix.lower().strip('.'),
                "size_mb": file_path.stat().st_size / (1024 * 1024),
            }
        except Exception as e:
            logger.error(f"Erreur lecture info audio {file_path}: {e}")
            raise

    def convert_for_whisper(
        self,
        input_path: Path,
        output_path: Path | None = None,
        progress_callback: Callable[[str, float], None] | None = None,
    ) -> Path:
        """
        Convertit un fichier audio au format optimal pour Whisper.

        Args:
            input_path: Fichier audio source
            output_path: Fichier de sortie (None = temp)
            progress_callback: Callback de progression

        Returns:
            Chemin du fichier converti
        """
        if not self.is_supported(input_path):
            raise AudioFormatError(str(input_path), input_path.suffix)

        self._ensure_ffmpeg()

        if output_path is None:
            temp_dir = get_config().paths.temp
            temp_dir.mkdir(parents=True, exist_ok=True)
            output_path = temp_dir / f"{input_path.stem}_converted.wav"

        if progress_callback:
            progress_callback("Chargement audio...", 10.0)

        logger.info(f"Conversion de {input_path} vers format Whisper...")

        # Charger l'audio
        audio = AudioSegment.from_file(str(input_path))

        if progress_callback:
            progress_callback("Conversion en cours...", 50.0)

        # Convertir
        audio = audio.set_frame_rate(self.WHISPER_SAMPLE_RATE)
        audio = audio.set_channels(1)  # Mono

        # Exporter en WAV 16-bit
        output_path.parent.mkdir(parents=True, exist_ok=True)
        audio.export(
            str(output_path),
            format="wav",
            parameters=["-acodec", "pcm_s16le"],
        )

        if progress_callback:
            progress_callback("Conversion terminée", 100.0)

        logger.info(f"Audio converti: {output_path}")
        return output_path

    def split_audio(
        self,
        file_path: Path,
        chunk_minutes: int = 10,
        output_dir: Path | None = None,
    ) -> list[Path]:
        """
        Découpe un fichier audio en chunks pour traitement par morceaux.
        Utile pour les fichiers très longs et la gestion mémoire.

        Args:
            file_path: Fichier audio source
            chunk_minutes: Durée de chaque chunk en minutes
            output_dir: Dossier de sortie

        Returns:
            Liste des chemins vers les chunks
        """
        if output_dir is None:
            output_dir = get_config().paths.temp / "chunks"

        output_dir.mkdir(parents=True, exist_ok=True)

        self._ensure_ffmpeg()
        audio = AudioSegment.from_file(str(file_path))
        chunk_ms = chunk_minutes * 60 * 1000

        chunks = []
        for i, start in enumerate(range(0, len(audio), chunk_ms)):
            chunk = audio[start:start + chunk_ms]
            chunk_path = output_dir / f"{file_path.stem}_chunk_{i:03d}.wav"

            chunk.export(str(chunk_path), format="wav")
            chunks.append(chunk_path)

        logger.info(f"Audio découpé en {len(chunks)} chunks de {chunk_minutes}min")
        return chunks

    def cleanup_temp_files(self, patterns: list[str] | None = None) -> int:
        """
        Nettoie les fichiers temporaires.

        Returns:
            Nombre de fichiers supprimés
        """
        temp_dir = get_config().paths.temp
        if not temp_dir.exists():
            return 0

        patterns = patterns or ["*.wav", "*.tmp"]
        count = 0

        for pattern in patterns:
            for f in temp_dir.glob(pattern):
                try:
                    f.unlink()
                    count += 1
                except Exception as e:
                    logger.warning(f"Impossible de supprimer {f}: {e}")

        logger.info(f"Nettoyage: {count} fichiers temporaires supprimés")
        return count
