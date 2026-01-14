"""
Module de diarization (identification des locuteurs).
Supporte deux modes:
- "quality": Pyannote 3.1 (précis mais lent sur CPU)
- "fast": SpeechBrain ECAPA-TDNN (plus rapide, moins précis)
"""
import gc
import logging
from pathlib import Path
from typing import Optional, List, Callable, Dict, Tuple
from dataclasses import dataclass

from ..utils.config import get_config, DiarizationConfig
from .transcriber import TranscriptionResult, TranscriptionSegment

logger = logging.getLogger(__name__)


@dataclass
class SpeakerSegment:
    """Segment avec identification du locuteur."""
    start: float
    end: float
    speaker: str


@dataclass
class DiarizationResult:
    """Résultat de la diarization."""
    segments: List[SpeakerSegment]
    num_speakers: int
    
    def get_speaker_at(self, time: float) -> Optional[str]:
        """Retourne le locuteur à un instant donné."""
        for seg in self.segments:
            if seg.start <= time <= seg.end:
                return seg.speaker
        return None
    
    def get_speaker_for_range(self, start: float, end: float) -> Optional[str]:
        """Retourne le locuteur majoritaire sur une plage de temps."""
        overlaps: Dict[str, float] = {}
        
        for seg in self.segments:
            # Calculer le chevauchement
            overlap_start = max(start, seg.start)
            overlap_end = min(end, seg.end)
            
            if overlap_start < overlap_end:
                overlap_duration = overlap_end - overlap_start
                overlaps[seg.speaker] = overlaps.get(seg.speaker, 0) + overlap_duration
        
        if not overlaps:
            return None
        
        # Retourner le locuteur avec le plus de chevauchement
        return max(overlaps.items(), key=lambda x: x[1])[0]


class Diarizer:
    """
    Classe de diarization pour identifier les locuteurs.
    
    Deux modes disponibles:
    - "quality": Pyannote 3.1 (~2-3h/h audio sur CPU, DER ~11%)
    - "fast": SpeechBrain (~20-30min/h audio sur CPU, DER ~18%)
    """
    
    def __init__(self, config: Optional[DiarizationConfig] = None):
        self.config = config or get_config().diarization
        self.pipeline = None
        self._mode = self.config.mode
    
    @property
    def mode(self) -> str:
        return self._mode
    
    @mode.setter
    def mode(self, value: str) -> None:
        if value not in ("quality", "fast"):
            raise ValueError("Mode doit être 'quality' ou 'fast'")
        if value != self._mode:
            self.unload()
            self._mode = value
    
    def load(
        self,
        progress_callback: Optional[Callable[[str, float], None]] = None,
    ) -> None:
        """Charge le pipeline de diarization."""
        if self.pipeline is not None:
            return
        
        if progress_callback:
            progress_callback(f"Chargement diarization ({self._mode})...", 0.0)
        
        if self._mode == "quality":
            self._load_pyannote(progress_callback)
        else:
            self._load_speechbrain(progress_callback)
        
        if progress_callback:
            progress_callback("Diarization prête", 100.0)
    
    def _load_pyannote(
        self,
        progress_callback: Optional[Callable[[str, float], None]] = None,
    ) -> None:
        """Charge le pipeline Pyannote."""
        try:
            from pyannote.audio import Pipeline
            import torch
            
            if progress_callback:
                progress_callback("Chargement Pyannote 3.1...", 30.0)
            
            # Pyannote nécessite un token HuggingFace
            # L'utilisateur doit avoir accepté les conditions sur HuggingFace
            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=True,
            )
            
            # Forcer CPU
            self.pipeline.to(torch.device("cpu"))
            
            logger.info("Pipeline Pyannote chargé (mode quality)")
            
        except Exception as e:
            logger.error(f"Erreur chargement Pyannote: {e}")
            logger.info("Conseil: vérifiez votre token HuggingFace et les conditions d'utilisation")
            raise
    
    def _load_speechbrain(
        self,
        progress_callback: Optional[Callable[[str, float], None]] = None,
    ) -> None:
        """Charge le pipeline SpeechBrain (mode rapide)."""
        try:
            from speechbrain.inference import SpeakerRecognition
            from speechbrain.inference import VAD
            
            if progress_callback:
                progress_callback("Chargement SpeechBrain...", 30.0)
            
            # Embedding model pour reconnaissance locuteurs
            self._embedder = SpeakerRecognition.from_hparams(
                source="speechbrain/spkrec-ecapa-voxceleb",
                savedir="models/speechbrain/spkrec",
            )
            
            # VAD pour segmentation
            self._vad = VAD.from_hparams(
                source="speechbrain/vad-crdnn-libriparty",
                savedir="models/speechbrain/vad",
            )
            
            logger.info("Pipeline SpeechBrain chargé (mode fast)")
            
            # Marquer le pipeline comme chargé (on utilise _embedder et _vad)
            self.pipeline = "speechbrain"
            
        except Exception as e:
            logger.error(f"Erreur chargement SpeechBrain: {e}")
            raise
    
    def unload(self) -> None:
        """Décharge les modèles pour libérer la mémoire."""
        self.pipeline = None
        if hasattr(self, '_embedder'):
            del self._embedder
        if hasattr(self, '_vad'):
            del self._vad
        gc.collect()
        logger.info("Modèles diarization déchargés")
    
    def diarize(
        self,
        audio_path: Path,
        min_speakers: Optional[int] = None,
        max_speakers: Optional[int] = None,
        progress_callback: Optional[Callable[[str, float], None]] = None,
    ) -> DiarizationResult:
        """
        Effectue la diarization d'un fichier audio.
        
        Args:
            audio_path: Chemin vers le fichier audio
            min_speakers: Nombre minimum de locuteurs attendus (0=auto)
            max_speakers: Nombre maximum de locuteurs attendus (0=auto)
            progress_callback: Callback de progression
        
        Returns:
            DiarizationResult avec segments et locuteurs identifiés
        """
        if self.pipeline is None:
            self.load(progress_callback)
        
        min_speakers = min_speakers or self.config.min_speakers or None
        max_speakers = max_speakers or self.config.max_speakers or None
        
        # Convertir 0 en None pour auto-detection
        if min_speakers == 0:
            min_speakers = None
        if max_speakers == 0:
            max_speakers = None
        
        if progress_callback:
            progress_callback("Analyse des locuteurs...", 10.0)
        
        logger.info(f"Diarization de {audio_path} (min={min_speakers}, max={max_speakers})...")
        
        if self._mode == "quality":
            return self._diarize_pyannote(
                audio_path, min_speakers, max_speakers, progress_callback
            )
        else:
            return self._diarize_speechbrain(
                audio_path, min_speakers, max_speakers, progress_callback
            )
    
    def _diarize_pyannote(
        self,
        audio_path: Path,
        min_speakers: Optional[int],
        max_speakers: Optional[int],
        progress_callback: Optional[Callable[[str, float], None]],
    ) -> DiarizationResult:
        """Diarization avec Pyannote."""
        diarization = self.pipeline(
            str(audio_path),
            min_speakers=min_speakers,
            max_speakers=max_speakers,
        )
        
        segments = []
        speakers_set = set()
        
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append(SpeakerSegment(
                start=turn.start,
                end=turn.end,
                speaker=speaker,
            ))
            speakers_set.add(speaker)
        
        if progress_callback:
            progress_callback("Diarization terminée", 100.0)
        
        result = DiarizationResult(
            segments=segments,
            num_speakers=len(speakers_set),
        )
        
        logger.info(f"Diarization terminée: {len(segments)} segments, {result.num_speakers} locuteurs")
        return result
    
    def _diarize_speechbrain(
        self,
        audio_path: Path,
        min_speakers: Optional[int],
        max_speakers: Optional[int],
        progress_callback: Optional[Callable[[str, float], None]],
    ) -> DiarizationResult:
        """
        Diarization avec SpeechBrain (méthode simplifiée).
        Utilise VAD + embeddings + clustering.
        """
        import torch
        import numpy as np
        from sklearn.cluster import AgglomerativeClustering
        import torchaudio
        
        # Charger l'audio
        waveform, sample_rate = torchaudio.load(str(audio_path))
        
        if progress_callback:
            progress_callback("Détection des segments vocaux...", 20.0)
        
        # VAD pour trouver les segments de parole
        # Note: implémentation simplifiée, à adapter selon API SpeechBrain
        boundaries = self._vad.get_speech_segments(str(audio_path))
        
        if progress_callback:
            progress_callback("Extraction des embeddings...", 40.0)
        
        # Extraire les embeddings pour chaque segment
        embeddings = []
        segment_times = []
        
        for start, end in boundaries:
            start_sample = int(start * sample_rate)
            end_sample = int(end * sample_rate)
            segment_audio = waveform[:, start_sample:end_sample]
            
            if segment_audio.shape[1] > 0:
                emb = self._embedder.encode_batch(segment_audio)
                embeddings.append(emb.squeeze().numpy())
                segment_times.append((start, end))
        
        if not embeddings:
            return DiarizationResult(segments=[], num_speakers=0)
        
        if progress_callback:
            progress_callback("Clustering des locuteurs...", 70.0)
        
        # Clustering pour identifier les locuteurs
        embeddings_matrix = np.vstack(embeddings)
        
        n_clusters = max_speakers if max_speakers else min(len(embeddings), 10)
        if min_speakers and n_clusters < min_speakers:
            n_clusters = min_speakers
        
        clustering = AgglomerativeClustering(
            n_clusters=n_clusters,
            metric='cosine',
            linkage='average',
        )
        labels = clustering.fit_predict(embeddings_matrix)
        
        # Construire les segments
        segments = []
        for (start, end), label in zip(segment_times, labels):
            segments.append(SpeakerSegment(
                start=start,
                end=end,
                speaker=f"SPEAKER_{label:02d}",
            ))
        
        if progress_callback:
            progress_callback("Diarization terminée", 100.0)
        
        result = DiarizationResult(
            segments=segments,
            num_speakers=len(set(labels)),
        )
        
        logger.info(f"Diarization SpeechBrain: {len(segments)} segments, {result.num_speakers} locuteurs")
        return result


def assign_speakers_to_transcription(
    transcription: TranscriptionResult,
    diarization: DiarizationResult,
) -> TranscriptionResult:
    """
    Assigne les locuteurs identifiés aux segments de transcription.
    
    Args:
        transcription: Résultat de la transcription
        diarization: Résultat de la diarization
    
    Returns:
        TranscriptionResult avec les speakers assignés
    """
    for segment in transcription.segments:
        # Trouver le locuteur pour ce segment
        mid_time = (segment.start + segment.end) / 2
        speaker = diarization.get_speaker_for_range(segment.start, segment.end)
        
        if speaker is None:
            speaker = diarization.get_speaker_at(mid_time)
        
        segment.speaker = speaker
    
    return transcription
