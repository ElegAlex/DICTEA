"""
Module de transcription audio avec faster-whisper.
Optimisé pour CPU Intel avec quantification int8.
"""
import gc
import logging
import os
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path

from faster_whisper import WhisperModel

from ..utils.config import TranscriptionConfig, get_config
from ..utils.model_manager import ModelManager

logger = logging.getLogger(__name__)


@dataclass
class TranscriptionSegment:
    """Segment de transcription avec métadonnées."""
    start: float
    end: float
    text: str
    words: list[dict] | None = None
    speaker: str | None = None
    confidence: float = 0.0


@dataclass
class TranscriptionResult:
    """Résultat complet d'une transcription."""
    segments: list[TranscriptionSegment]
    language: str
    language_probability: float
    duration: float
    
    def to_text(self, include_timestamps: bool = False, include_speakers: bool = True) -> str:
        """Convertit en texte formaté."""
        lines = []
        for seg in self.segments:
            prefix = ""
            if include_speakers and seg.speaker:
                prefix += f"[{seg.speaker}] "
            if include_timestamps:
                prefix += f"[{_format_time(seg.start)} - {_format_time(seg.end)}] "
            lines.append(f"{prefix}{seg.text.strip()}")
        return "\n".join(lines)
    
    def to_srt(self) -> str:
        """Export au format SRT (sous-titres)."""
        lines = []
        for i, seg in enumerate(self.segments, 1):
            start_time = _format_srt_time(seg.start)
            end_time = _format_srt_time(seg.end)
            text = seg.text.strip()
            if seg.speaker:
                text = f"[{seg.speaker}] {text}"
            lines.extend([str(i), f"{start_time} --> {end_time}", text, ""])
        return "\n".join(lines)


def _format_time(seconds: float) -> str:
    """Formate un temps en MM:SS."""
    mins, secs = divmod(int(seconds), 60)
    return f"{mins:02d}:{secs:02d}"


def _format_srt_time(seconds: float) -> str:
    """Formate un temps au format SRT (HH:MM:SS,mmm)."""
    hours, remainder = divmod(seconds, 3600)
    mins, secs = divmod(remainder, 60)
    millis = int((secs % 1) * 1000)
    return f"{int(hours):02d}:{int(mins):02d}:{int(secs):02d},{millis:03d}"


class Transcriber:
    """
    Classe de transcription audio avec faster-whisper.
    
    Optimisée pour:
    - CPU Intel i7 avec instructions AVX2
    - 16 Go RAM avec modèle medium int8
    - Traitement par chunks pour fichiers longs
    """
    
    def __init__(
        self,
        model_name: str | None = None,
        config: TranscriptionConfig | None = None,
    ):
        self.config = config or get_config().transcription
        self.model_name = model_name or self.config.model
        self.model: WhisperModel | None = None
        self.model_manager = ModelManager()
        
        # Optimisations CPU Intel
        self._setup_cpu_optimizations()
    
    def _setup_cpu_optimizations(self) -> None:
        """Configure les optimisations CPU."""
        cpu_threads = self.config.cpu_threads
        if cpu_threads == 0:
            # Auto-detect: utiliser les cores physiques (pas hyperthreading)
            cpu_threads = os.cpu_count() // 2 or 4
        
        os.environ["OMP_NUM_THREADS"] = str(cpu_threads)
        os.environ["MKL_NUM_THREADS"] = str(cpu_threads)
        os.environ["OMP_WAIT_POLICY"] = "PASSIVE"
        
        logger.info(f"CPU threads configurés: {cpu_threads}")
    
    def load_model(
        self,
        progress_callback: Callable[[str, float], None] | None = None,
    ) -> None:
        """
        Charge le modèle Whisper en mémoire.
        Télécharge si nécessaire.
        """
        if self.model is not None:
            logger.info("Modèle déjà chargé")
            return
        
        # Télécharger si nécessaire
        model_path = self.model_manager.download_whisper_model(
            self.model_name,
            progress_callback=progress_callback,
        )
        
        if progress_callback:
            progress_callback("Chargement du modèle en mémoire...", 50.0)
        
        logger.info(f"Chargement du modèle {self.model_name} ({self.config.compute_type})...")
        
        self.model = WhisperModel(
            str(model_path),
            device="cpu",
            compute_type=self.config.compute_type,
            cpu_threads=self.config.cpu_threads or (os.cpu_count() // 2),
        )
        
        if progress_callback:
            progress_callback("Modèle prêt", 100.0)
        
        logger.info("Modèle chargé avec succès")
    
    def unload_model(self) -> None:
        """Décharge le modèle pour libérer la mémoire."""
        if self.model is not None:
            del self.model
            self.model = None
            gc.collect()
            logger.info("Modèle déchargé")
    
    def transcribe(
        self,
        audio_path: Path,
        language: str | None = None,
        progress_callback: Callable[[int, str], None] | None = None,
    ) -> TranscriptionResult:
        """
        Transcrit un fichier audio.
        
        Args:
            audio_path: Chemin vers le fichier audio
            language: Code langue (fr, en, auto...) ou None pour config
            progress_callback: Callback (segment_index, texte_segment)
        
        Returns:
            TranscriptionResult avec tous les segments
        """
        if self.model is None:
            self.load_model()
        
        language = language or self.config.language
        if language == "auto":
            language = None
        
        logger.info(f"Transcription de {audio_path} (langue: {language or 'auto'})...")
        
        segments_iter, info = self.model.transcribe(
            str(audio_path),
            language=language,
            beam_size=self.config.beam_size,
            vad_filter=self.config.vad_filter,
            word_timestamps=True,  # Requis pour alignement diarization
        )
        
        segments = []
        for i, segment in enumerate(segments_iter):
            seg = TranscriptionSegment(
                start=segment.start,
                end=segment.end,
                text=segment.text,
                words=[
                    {"word": w.word, "start": w.start, "end": w.end, "probability": w.probability}
                    for w in (segment.words or [])
                ],
                confidence=segment.avg_logprob if hasattr(segment, 'avg_logprob') else 0.0,
            )
            segments.append(seg)
            
            if progress_callback:
                progress_callback(i, segment.text[:80])
        
        result = TranscriptionResult(
            segments=segments,
            language=info.language,
            language_probability=info.language_probability,
            duration=info.duration,
        )
        
        logger.info(
            f"Transcription terminée: {len(segments)} segments, "
            f"durée {result.duration:.1f}s, langue {result.language}"
        )
        
        return result
    
    def transcribe_stream(
        self,
        audio_path: Path,
        language: str | None = None,
    ) -> Iterator[TranscriptionSegment]:
        """
        Transcrit en mode streaming (yield segment par segment).
        Utile pour affichage progressif dans l'UI.
        """
        if self.model is None:
            self.load_model()
        
        language = language or self.config.language
        if language == "auto":
            language = None
        
        segments_iter, info = self.model.transcribe(
            str(audio_path),
            language=language,
            beam_size=self.config.beam_size,
            vad_filter=self.config.vad_filter,
            word_timestamps=True,
        )
        
        for segment in segments_iter:
            yield TranscriptionSegment(
                start=segment.start,
                end=segment.end,
                text=segment.text,
                words=[
                    {"word": w.word, "start": w.start, "end": w.end, "probability": w.probability}
                    for w in (segment.words or [])
                ],
            )
