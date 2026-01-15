"""
Fixtures partagées pour les tests DICTEA.
"""
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import numpy as np

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))


# =============================================================================
# Fixtures de configuration
# =============================================================================

@pytest.fixture
def temp_dir():
    """Crée un répertoire temporaire pour les tests."""
    dirpath = tempfile.mkdtemp()
    yield Path(dirpath)
    shutil.rmtree(dirpath, ignore_errors=True)


@pytest.fixture
def temp_config_file(temp_dir):
    """Crée un fichier de configuration temporaire."""
    config_content = """
app:
  name: "TestApp"
  version: "1.0.0"

transcription:
  model: "tiny"
  compute_type: "int8"
  language: "fr"
  cpu_threads: 2
  vad_filter: true
  beam_size: 5

diarization:
  min_speakers: 0
  max_speakers: 0

audio:
  sample_rate: 16000
  channels: 1
  export_format: "wav"
  input_device: null

paths:
  models: "{models}"
  output: "{output}"
  temp: "{temp}"

performance:
  chunk_size_minutes: 10
  aggressive_gc: true
""".format(
        models=str(temp_dir / "models"),
        output=str(temp_dir / "output"),
        temp=str(temp_dir / "temp"),
    )

    config_path = temp_dir / "config.yaml"
    config_path.write_text(config_content, encoding="utf-8")
    return config_path


@pytest.fixture
def mock_config(temp_dir):
    """Retourne une configuration mockée."""
    from src.utils.config import (
        AppConfig, TranscriptionConfig, DiarizationConfig,
        AudioConfig, PathsConfig, PerformanceConfig
    )

    return AppConfig(
        transcription=TranscriptionConfig(
            model="tiny",
            compute_type="int8",
            language="fr",
            cpu_threads=2,
            vad_filter=True,
            beam_size=5,
        ),
        diarization=DiarizationConfig(
            min_speakers=0,
            max_speakers=0,
        ),
        audio=AudioConfig(
            sample_rate=16000,
            channels=1,
            export_format="wav",
            input_device=None,
        ),
        paths=PathsConfig(
            models=temp_dir / "models",
            output=temp_dir / "output",
            temp=temp_dir / "temp",
        ),
        performance=PerformanceConfig(
            chunk_size_minutes=10,
            aggressive_gc=True,
        ),
    )


# =============================================================================
# Fixtures audio
# =============================================================================

@pytest.fixture
def sample_audio_data():
    """Génère des données audio de test (1 seconde de silence + bruit)."""
    sample_rate = 16000
    duration = 1.0  # secondes
    samples = int(sample_rate * duration)

    # Générer un signal simple (bruit blanc faible)
    np.random.seed(42)
    audio = np.random.randn(samples).astype(np.float32) * 0.01

    return audio, sample_rate


@pytest.fixture
def sample_audio_file(temp_dir, sample_audio_data):
    """Crée un fichier audio WAV temporaire."""
    import soundfile as sf

    audio, sample_rate = sample_audio_data
    audio_path = temp_dir / "test_audio.wav"
    sf.write(str(audio_path), audio, sample_rate)

    return audio_path


@pytest.fixture
def longer_audio_file(temp_dir):
    """Crée un fichier audio plus long (5 secondes) pour tests de chunks."""
    import soundfile as sf

    sample_rate = 16000
    duration = 5.0
    samples = int(sample_rate * duration)

    np.random.seed(42)
    audio = np.random.randn(samples).astype(np.float32) * 0.01

    audio_path = temp_dir / "long_audio.wav"
    sf.write(str(audio_path), audio, sample_rate)

    return audio_path


# =============================================================================
# Fixtures Mock ML Models
# =============================================================================

@pytest.fixture
def mock_whisper_model():
    """Mock du modèle Whisper."""
    mock_model = MagicMock()

    # Mock du résultat de transcription
    mock_segment = MagicMock()
    mock_segment.start = 0.0
    mock_segment.end = 1.5
    mock_segment.text = "Bonjour, ceci est un test."
    mock_segment.words = [
        MagicMock(word="Bonjour", start=0.0, end=0.5, probability=0.95),
        MagicMock(word="ceci", start=0.5, end=0.7, probability=0.92),
        MagicMock(word="est", start=0.7, end=0.8, probability=0.98),
        MagicMock(word="un", start=0.8, end=0.9, probability=0.97),
        MagicMock(word="test", start=0.9, end=1.5, probability=0.99),
    ]
    mock_segment.avg_logprob = -0.2

    mock_info = MagicMock()
    mock_info.language = "fr"
    mock_info.language_probability = 0.98
    mock_info.duration = 1.5

    mock_model.transcribe.return_value = (iter([mock_segment]), mock_info)

    return mock_model


@pytest.fixture
def mock_transcription_result():
    """Résultat de transcription mocké."""
    from src.core.transcriber import TranscriptionResult, TranscriptionSegment

    return TranscriptionResult(
        segments=[
            TranscriptionSegment(
                start=0.0,
                end=2.0,
                text="Bonjour, comment allez-vous?",
                words=[],
                speaker=None,
                confidence=0.95,
            ),
            TranscriptionSegment(
                start=2.5,
                end=5.0,
                text="Je vais très bien, merci.",
                words=[],
                speaker=None,
                confidence=0.92,
            ),
        ],
        language="fr",
        language_probability=0.98,
        duration=5.0,
    )


@pytest.fixture
def mock_diarization_result():
    """Résultat de diarisation mocké."""
    from src.core.diarizer import DiarizationResult, SpeakerSegment

    return DiarizationResult(
        segments=[
            SpeakerSegment(start=0.0, end=2.5, speaker="SPEAKER_00"),
            SpeakerSegment(start=2.5, end=5.0, speaker="SPEAKER_01"),
        ],
        num_speakers=2,
    )


# =============================================================================
# Fixtures pour reset du singleton config
# =============================================================================

@pytest.fixture(autouse=True)
def reset_config_singleton():
    """Reset le singleton de configuration entre chaque test."""
    from src.utils import config

    # Sauvegarder l'état original
    original_config = config._config

    yield

    # Restaurer l'état original
    config._config = original_config


# =============================================================================
# Skip markers
# =============================================================================

def pytest_configure(config):
    """Configure les markers personnalisés."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests requiring external resources"
    )
    config.addinivalue_line(
        "markers", "ui: marks tests requiring Qt UI"
    )
