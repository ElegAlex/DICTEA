"""
Tests unitaires pour le module src/core/diarizer.py
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.core.diarizer import (
    SpeakerSegment,
    DiarizationResult,
    Diarizer,
    assign_speakers_to_transcription,
)
from src.core.transcriber import TranscriptionResult, TranscriptionSegment


class TestSpeakerSegment:
    """Tests pour la dataclass SpeakerSegment."""

    def test_creation(self):
        """Vérifie la création d'un segment."""
        segment = SpeakerSegment(
            start=0.0,
            end=2.5,
            speaker="SPEAKER_00",
        )

        assert segment.start == 0.0
        assert segment.end == 2.5
        assert segment.speaker == "SPEAKER_00"


class TestDiarizationResult:
    """Tests pour la classe DiarizationResult."""

    @pytest.fixture
    def sample_diarization(self):
        """Crée un résultat de diarization de test."""
        return DiarizationResult(
            segments=[
                SpeakerSegment(start=0.0, end=3.0, speaker="SPEAKER_00"),
                SpeakerSegment(start=3.0, end=5.0, speaker="SPEAKER_01"),
                SpeakerSegment(start=5.0, end=8.0, speaker="SPEAKER_00"),
            ],
            num_speakers=2,
        )

    def test_get_speaker_at_beginning(self, sample_diarization):
        """Vérifie la récupération du locuteur au début."""
        speaker = sample_diarization.get_speaker_at(0.5)
        assert speaker == "SPEAKER_00"

    def test_get_speaker_at_middle(self, sample_diarization):
        """Vérifie la récupération du locuteur au milieu."""
        speaker = sample_diarization.get_speaker_at(4.0)
        assert speaker == "SPEAKER_01"

    def test_get_speaker_at_boundary(self, sample_diarization):
        """Vérifie la récupération du locuteur à une frontière."""
        speaker = sample_diarization.get_speaker_at(3.0)
        # 3.0 est inclus dans le segment de SPEAKER_00 (0-3)
        assert speaker == "SPEAKER_00"

    def test_get_speaker_at_no_speaker(self, sample_diarization):
        """Vérifie le comportement hors segments."""
        speaker = sample_diarization.get_speaker_at(10.0)
        assert speaker is None

    def test_get_speaker_for_range_single(self, sample_diarization):
        """Vérifie la récupération du locuteur pour une plage simple."""
        speaker = sample_diarization.get_speaker_for_range(0.5, 2.5)
        assert speaker == "SPEAKER_00"

    def test_get_speaker_for_range_overlap(self, sample_diarization):
        """Vérifie avec chevauchement de plusieurs locuteurs."""
        # Plage 2.5 - 4.0 chevauche SPEAKER_00 (2.5-3.0) et SPEAKER_01 (3.0-4.0)
        speaker = sample_diarization.get_speaker_for_range(2.5, 4.0)
        # SPEAKER_01 a plus de temps dans cette plage (1.0s vs 0.5s)
        assert speaker == "SPEAKER_01"

    def test_get_speaker_for_range_no_overlap(self, sample_diarization):
        """Vérifie le comportement sans chevauchement."""
        speaker = sample_diarization.get_speaker_for_range(10.0, 12.0)
        assert speaker is None

    def test_get_speaker_for_range_exact_match(self, sample_diarization):
        """Vérifie avec correspondance exacte."""
        speaker = sample_diarization.get_speaker_for_range(0.0, 3.0)
        assert speaker == "SPEAKER_00"


class TestDiarizer:
    """Tests pour la classe Diarizer (NeMo Sortformer)."""

    @pytest.fixture
    def mock_diarizer_deps(self, mock_config):
        """Configure les mocks pour Diarizer."""
        with patch("src.core.diarizer.get_config", return_value=mock_config):
            yield mock_config

    def test_init_default(self, mock_diarizer_deps):
        """Vérifie l'initialisation par défaut."""
        diarizer = Diarizer()

        assert diarizer.model is None
        assert diarizer.mode == "nemo"

    def test_mode_property(self, mock_diarizer_deps):
        """Vérifie la propriété mode - toujours nemo."""
        diarizer = Diarizer()

        assert diarizer.mode == "nemo"

    def test_mode_setter_ignored(self, mock_diarizer_deps):
        """Vérifie que le setter mode est ignoré (NeMo uniquement)."""
        diarizer = Diarizer()
        diarizer.mode = "quality"

        # Le setter ignore la valeur, mode reste "nemo"
        assert diarizer.mode == "nemo"

    def test_unload(self, mock_diarizer_deps):
        """Vérifie le déchargement du modèle."""
        diarizer = Diarizer()
        diarizer.model = MagicMock()

        diarizer.unload()

        assert diarizer.model is None

    def test_load_calls_load_nemo(self, mock_diarizer_deps):
        """Vérifie que load appelle _load_nemo."""
        diarizer = Diarizer()

        with patch.object(diarizer, "_load_nemo") as mock_load_nemo:
            diarizer.load()
            mock_load_nemo.assert_called_once()

    def test_load_skips_if_already_loaded(self, mock_diarizer_deps):
        """Vérifie que load ne recharge pas si déjà chargé."""
        diarizer = Diarizer()
        diarizer.model = MagicMock()

        with patch.object(diarizer, "_load_nemo") as mock_load_nemo:
            diarizer.load()
            mock_load_nemo.assert_not_called()

    def test_diarize_loads_if_needed(self, mock_diarizer_deps, sample_audio_file):
        """Vérifie que diarize charge le modèle si nécessaire."""
        diarizer = Diarizer()

        with patch.object(diarizer, "load") as mock_load:
            with patch.object(diarizer, "_diarize_nemo") as mock_diarize:
                mock_diarize.return_value = DiarizationResult(segments=[], num_speakers=0)

                diarizer.diarize(sample_audio_file)

                mock_load.assert_called_once()

    def test_diarize_skips_load_if_loaded(self, mock_diarizer_deps, sample_audio_file):
        """Vérifie que diarize ne recharge pas si déjà chargé."""
        diarizer = Diarizer()
        diarizer.model = MagicMock()

        with patch.object(diarizer, "load") as mock_load:
            with patch.object(diarizer, "_diarize_nemo") as mock_diarize:
                mock_diarize.return_value = DiarizationResult(segments=[], num_speakers=0)

                diarizer.diarize(sample_audio_file)

                mock_load.assert_not_called()

    def test_diarize_calls_diarize_nemo(self, mock_diarizer_deps, sample_audio_file):
        """Vérifie que diarize appelle _diarize_nemo."""
        diarizer = Diarizer()
        diarizer.model = MagicMock()

        with patch.object(diarizer, "_diarize_nemo") as mock_diarize:
            mock_diarize.return_value = DiarizationResult(segments=[], num_speakers=0)

            result = diarizer.diarize(sample_audio_file)

            mock_diarize.assert_called_once()
            assert isinstance(result, DiarizationResult)


class TestAssignSpeakersToTranscription:
    """Tests pour la fonction assign_speakers_to_transcription."""

    def test_assign_basic(self, mock_transcription_result, mock_diarization_result):
        """Vérifie l'assignation basique des locuteurs."""
        result = assign_speakers_to_transcription(
            mock_transcription_result, mock_diarization_result
        )

        assert result.segments[0].speaker == "SPEAKER_00"
        assert result.segments[1].speaker == "SPEAKER_01"

    def test_assign_no_modification_original(self):
        """Vérifie que les originaux sont modifiés (par référence)."""
        transcription = TranscriptionResult(
            segments=[
                TranscriptionSegment(start=0.0, end=1.0, text="Test"),
            ],
            language="fr",
            language_probability=0.9,
            duration=1.0,
        )

        diarization = DiarizationResult(
            segments=[
                SpeakerSegment(start=0.0, end=2.0, speaker="SPEAKER_00"),
            ],
            num_speakers=1,
        )

        result = assign_speakers_to_transcription(transcription, diarization)

        # Le résultat retourné est la même instance (modifiée)
        assert result is transcription
        assert result.segments[0].speaker == "SPEAKER_00"

    def test_assign_uses_range_first(self):
        """Vérifie que get_speaker_for_range est utilisé en priorité."""
        transcription = TranscriptionResult(
            segments=[
                TranscriptionSegment(start=0.0, end=3.0, text="Test"),
            ],
            language="fr",
            language_probability=0.9,
            duration=3.0,
        )

        diarization = DiarizationResult(
            segments=[
                SpeakerSegment(start=0.0, end=1.0, speaker="SPEAKER_00"),
                SpeakerSegment(start=1.0, end=3.0, speaker="SPEAKER_01"),
            ],
            num_speakers=2,
        )

        result = assign_speakers_to_transcription(transcription, diarization)

        # SPEAKER_01 a plus de temps (2s vs 1s)
        assert result.segments[0].speaker == "SPEAKER_01"

    def test_assign_falls_back_to_midpoint(self):
        """Vérifie le fallback sur le point médian."""
        transcription = TranscriptionResult(
            segments=[
                TranscriptionSegment(start=5.0, end=6.0, text="Test"),
            ],
            language="fr",
            language_probability=0.9,
            duration=6.0,
        )

        diarization = DiarizationResult(
            segments=[
                # Segment ne chevauche pas directement mais contient le midpoint
                SpeakerSegment(start=5.0, end=6.0, speaker="SPEAKER_00"),
            ],
            num_speakers=1,
        )

        result = assign_speakers_to_transcription(transcription, diarization)

        assert result.segments[0].speaker == "SPEAKER_00"

    def test_assign_no_speaker_found(self):
        """Vérifie le comportement quand aucun locuteur n'est trouvé."""
        transcription = TranscriptionResult(
            segments=[
                TranscriptionSegment(start=10.0, end=11.0, text="Test"),
            ],
            language="fr",
            language_probability=0.9,
            duration=11.0,
        )

        diarization = DiarizationResult(
            segments=[
                SpeakerSegment(start=0.0, end=2.0, speaker="SPEAKER_00"),
            ],
            num_speakers=1,
        )

        result = assign_speakers_to_transcription(transcription, diarization)

        # Pas de locuteur trouvé
        assert result.segments[0].speaker is None
