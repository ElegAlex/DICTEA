"""
Module de diarization (identification des locuteurs).
Utilise NVIDIA NeMo Sortformer - 100% offline, sans authentification.
"""
import gc
import logging
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from .audio_processor import AudioProcessor
from ..utils.config import DiarizationConfig, get_config
from .transcriber import TranscriptionResult

logger = logging.getLogger(__name__)

# Chemin vers les modèles NeMo locaux
MODELS_DIR = Path(__file__).parent.parent.parent / "models" / "nemo"


@dataclass
class SpeakerSegment:
    """Segment avec identification du locuteur."""
    start: float
    end: float
    speaker: str


@dataclass
class DiarizationResult:
    """Résultat de la diarization."""
    segments: list[SpeakerSegment]
    num_speakers: int

    def get_speaker_at(self, time: float) -> str | None:
        """Retourne le locuteur à un instant donné."""
        for seg in self.segments:
            if seg.start <= time <= seg.end:
                return seg.speaker
        return None

    def get_speaker_for_range(self, start: float, end: float) -> str | None:
        """Retourne le locuteur majoritaire sur une plage de temps."""
        overlaps: dict[str, float] = {}

        for seg in self.segments:
            overlap_start = max(start, seg.start)
            overlap_end = min(end, seg.end)

            if overlap_start < overlap_end:
                overlap_duration = overlap_end - overlap_start
                overlaps[seg.speaker] = overlaps.get(seg.speaker, 0) + overlap_duration

        if not overlaps:
            return None

        return max(overlaps.items(), key=lambda x: x[1])[0]


class Diarizer:
    """
    Classe de diarization pour identifier les locuteurs.

    Utilise NVIDIA NeMo Sortformer (100% offline, CC-BY-NC-4.0).
    Supporte jusqu'à 4 locuteurs.
    """

    def __init__(self, config: DiarizationConfig | None = None):
        self.config = config or get_config().diarization
        self.model = None
        self._mode = "nemo"  # Mode unique: NeMo

    @property
    def mode(self) -> str:
        return self._mode

    @mode.setter
    def mode(self, value: str) -> None:
        # Setter conservé pour compatibilité future; mode fixe sur NeMo Sortformer.
        # La valeur est ignorée tant que l'application reste 100% offline avec NeMo.
        pass

    def load(
        self,
        progress_callback: Callable[[str, float], None] | None = None,
    ) -> None:
        """Charge le modèle NeMo Sortformer."""
        if self.model is not None:
            return

        if progress_callback:
            progress_callback("Chargement NeMo Sortformer...", 0.0)

        self._load_nemo(progress_callback)

        if progress_callback:
            progress_callback("Diarization prête", 100.0)

    def _load_nemo(
        self,
        progress_callback: Callable[[str, float], None] | None = None,
    ) -> None:
        """Charge le modèle NeMo depuis les fichiers locaux."""
        try:
            import torch
            from nemo.collections.asr.models import SortformerEncLabelModel

            if progress_callback:
                progress_callback("Chargement Sortformer...", 30.0)

            # Chemin vers le modèle local
            model_path = MODELS_DIR / "sortformer" / "diar_sortformer_4spk-v1.nemo"

            if not model_path.exists():
                raise FileNotFoundError(
                    f"Modèle NeMo non trouvé: {model_path}\n"
                    "Exécutez le script de téléchargement des modèles."
                )

            # Charger depuis le fichier local
            self.model = SortformerEncLabelModel.restore_from(
                restore_path=str(model_path),
                map_location=torch.device("cpu"),
                strict=False,
            )
            self.model.eval()

            logger.info("Modèle NeMo Sortformer chargé (100% offline)")

        except Exception as e:
            logger.error(f"Erreur chargement NeMo: {e}")
            raise

    def unload(self) -> None:
        """Décharge les modèles pour libérer la mémoire."""
        self.model = None
        gc.collect()
        logger.info("Modèles diarization déchargés")

    def diarize(
        self,
        audio_path: Path,
        min_speakers: int | None = None,
        max_speakers: int | None = None,
        progress_callback: Callable[[str, float], None] | None = None,
    ) -> DiarizationResult:
        """
        Effectue la diarization d'un fichier audio.

        Args:
            audio_path: Chemin vers le fichier audio
            min_speakers: (ignoré - Sortformer détecte auto jusqu'à 4)
            max_speakers: (ignoré - Sortformer détecte auto jusqu'à 4)
            progress_callback: Callback de progression

        Returns:
            DiarizationResult avec segments et locuteurs identifiés
        """
        if self.model is None:
            self.load(progress_callback)

        if progress_callback:
            progress_callback("Analyse des locuteurs...", 10.0)

        logger.info(f"Diarization de {audio_path}...")

        return self._diarize_nemo(audio_path, progress_callback)

    def _diarize_nemo(
        self,
        audio_path: Path,
        progress_callback: Callable[[str, float], None] | None,
    ) -> DiarizationResult:
        """Diarization avec NeMo Sortformer."""
        import tempfile

        from pydub import AudioSegment

        if progress_callback:
            progress_callback("Préparation audio...", 20.0)

        AudioProcessor().ensure_ffmpeg()

        # Charger l'audio avec pydub (supporte tous les formats via ffmpeg)
        audio = AudioSegment.from_file(str(audio_path))

        # Convertir en mono 16kHz
        audio = audio.set_channels(1).set_frame_rate(16000)

        if progress_callback:
            progress_callback("Sortformer en cours...", 30.0)

        # Sauvegarder dans un fichier temporaire WAV mono
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name
            audio.export(tmp_path, format="wav")

        try:
            # Lancer la diarization sur l'audio mono
            predicted_segments = self.model.diarize(
                audio=tmp_path,
                batch_size=1,
            )
        finally:
            # Nettoyer le fichier temporaire
            Path(tmp_path).unlink(missing_ok=True)

        if progress_callback:
            progress_callback("Traitement des résultats...", 80.0)

        # Convertir les résultats
        segments = []
        speakers_set = set()

        # predicted_segments est une liste de listes de strings "start end speaker"
        if predicted_segments and len(predicted_segments) > 0:
            for seg_str in predicted_segments[0]:  # Premier fichier
                # Format: "0.000 2.550 speaker_0"
                parts = seg_str.strip().split()
                if len(parts) >= 3:
                    start = float(parts[0])
                    end = float(parts[1])
                    speaker = parts[2].upper().replace("SPEAKER_", "SPEAKER_")
                    # Normaliser le nom du speaker
                    if speaker.startswith("SPEAKER_"):
                        speaker = speaker
                    else:
                        speaker = f"SPEAKER_{speaker}"
                    segments.append(SpeakerSegment(
                        start=start,
                        end=end,
                        speaker=speaker,
                    ))
                    speakers_set.add(speaker)

        if progress_callback:
            progress_callback("Diarization terminée", 100.0)

        result = DiarizationResult(
            segments=segments,
            num_speakers=len(speakers_set),
        )

        logger.info(f"Diarization NeMo: {len(segments)} segments, {result.num_speakers} locuteurs")
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
        speaker = diarization.get_speaker_for_range(segment.start, segment.end)

        if speaker is None:
            mid_time = (segment.start + segment.end) / 2
            speaker = diarization.get_speaker_at(mid_time)

        segment.speaker = speaker

    return transcription
