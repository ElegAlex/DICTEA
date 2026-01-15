"""
Tests unitaires pour le module src/utils/config.py
"""
import pytest
from pathlib import Path

from src.utils.config import (
    AppConfig,
    TranscriptionConfig,
    DiarizationConfig,
    AudioConfig,
    PathsConfig,
    PerformanceConfig,
    get_config,
    reload_config,
)


class TestTranscriptionConfig:
    """Tests pour TranscriptionConfig dataclass."""

    def test_default_values(self):
        """Vérifie les valeurs par défaut."""
        config = TranscriptionConfig()

        assert config.model == "medium"
        assert config.compute_type == "int8"
        assert config.language == "fr"
        assert config.cpu_threads == 0
        assert config.vad_filter is True
        assert config.beam_size == 5

    def test_custom_values(self):
        """Vérifie l'initialisation avec valeurs personnalisées."""
        config = TranscriptionConfig(
            model="large-v3",
            compute_type="float16",
            language="en",
            cpu_threads=8,
            vad_filter=False,
            beam_size=10,
        )

        assert config.model == "large-v3"
        assert config.compute_type == "float16"
        assert config.language == "en"
        assert config.cpu_threads == 8
        assert config.vad_filter is False
        assert config.beam_size == 10


class TestDiarizationConfig:
    """Tests pour DiarizationConfig dataclass."""

    def test_default_values(self):
        """Vérifie les valeurs par défaut."""
        config = DiarizationConfig()

        assert config.min_speakers == 0
        assert config.max_speakers == 0

    def test_custom_speakers(self):
        """Vérifie la configuration avec nombre de locuteurs personnalisé."""
        config = DiarizationConfig(min_speakers=2, max_speakers=5)

        assert config.min_speakers == 2
        assert config.max_speakers == 5


class TestAudioConfig:
    """Tests pour AudioConfig dataclass."""

    def test_default_values(self):
        """Vérifie les valeurs par défaut."""
        config = AudioConfig()

        assert config.sample_rate == 16000
        assert config.channels == 1
        assert config.export_format == "wav"
        assert config.input_device is None

    def test_custom_device(self):
        """Vérifie la configuration avec périphérique personnalisé."""
        config = AudioConfig(input_device=2)
        assert config.input_device == 2


class TestPathsConfig:
    """Tests pour PathsConfig dataclass."""

    def test_default_values(self):
        """Vérifie les chemins par défaut."""
        config = PathsConfig()

        assert config.models == Path("models")
        assert config.output == Path("output")
        assert config.temp == Path("temp")

    def test_custom_paths(self, temp_dir):
        """Vérifie les chemins personnalisés."""
        config = PathsConfig(
            models=temp_dir / "custom_models",
            output=temp_dir / "custom_output",
            temp=temp_dir / "custom_temp",
        )

        assert config.models == temp_dir / "custom_models"
        assert config.output == temp_dir / "custom_output"
        assert config.temp == temp_dir / "custom_temp"


class TestPerformanceConfig:
    """Tests pour PerformanceConfig dataclass."""

    def test_default_values(self):
        """Vérifie les valeurs par défaut."""
        config = PerformanceConfig()

        assert config.chunk_size_minutes == 10
        assert config.aggressive_gc is True


class TestAppConfig:
    """Tests pour la configuration globale AppConfig."""

    def test_default_config(self):
        """Vérifie la configuration par défaut."""
        config = AppConfig()

        assert isinstance(config.transcription, TranscriptionConfig)
        assert isinstance(config.diarization, DiarizationConfig)
        assert isinstance(config.audio, AudioConfig)
        assert isinstance(config.paths, PathsConfig)
        assert isinstance(config.performance, PerformanceConfig)

    def test_load_from_yaml(self, temp_config_file, temp_dir):
        """Vérifie le chargement depuis un fichier YAML."""
        config = AppConfig.load(temp_config_file)

        assert config.transcription.model == "tiny"
        assert config.transcription.cpu_threads == 2
        assert config.diarization.min_speakers == 0
        assert config.audio.sample_rate == 16000

    def test_load_creates_directories(self, temp_config_file, temp_dir):
        """Vérifie que les répertoires sont créés au chargement."""
        config = AppConfig.load(temp_config_file)

        assert config.paths.models.exists()
        assert config.paths.output.exists()
        assert config.paths.temp.exists()

    def test_load_nonexistent_file(self, temp_dir):
        """Vérifie le comportement avec un fichier inexistant."""
        nonexistent = temp_dir / "nonexistent.yaml"
        config = AppConfig.load(nonexistent)

        # Doit retourner la configuration par défaut
        assert config.transcription.model == "medium"

    def test_save_config(self, temp_dir):
        """Vérifie la sauvegarde de la configuration."""
        config = AppConfig(
            transcription=TranscriptionConfig(model="small"),
            paths=PathsConfig(
                models=temp_dir / "models",
                output=temp_dir / "output",
                temp=temp_dir / "temp",
            ),
        )

        save_path = temp_dir / "saved_config.yaml"
        config.save(save_path)

        assert save_path.exists()

        # Recharger et vérifier
        loaded = AppConfig.load(save_path)
        assert loaded.transcription.model == "small"

    def test_save_creates_parent_directory(self, temp_dir):
        """Vérifie que save crée les répertoires parents."""
        config = AppConfig()
        save_path = temp_dir / "subdir" / "config.yaml"

        config.save(save_path)

        assert save_path.exists()
        assert save_path.parent.exists()


class TestGetConfig:
    """Tests pour le singleton get_config."""

    def test_returns_config(self, temp_config_file, temp_dir):
        """Vérifie que get_config retourne une configuration."""
        from src.utils import config as config_module

        # Reset le singleton
        config_module._config = None

        # Patcher le chemin de recherche du config
        import os
        original_cwd = os.getcwd()
        os.chdir(temp_config_file.parent)

        try:
            result = get_config()
            assert isinstance(result, AppConfig)
        finally:
            os.chdir(original_cwd)

    def test_singleton_returns_same_instance(self):
        """Vérifie le pattern singleton."""
        from src.utils import config as config_module

        config_module._config = AppConfig()

        config1 = get_config()
        config2 = get_config()

        assert config1 is config2


class TestReloadConfig:
    """Tests pour reload_config."""

    def test_reload_replaces_singleton(self, temp_config_file):
        """Vérifie que reload remplace le singleton."""
        from src.utils import config as config_module

        # Créer une config initiale
        config_module._config = AppConfig(
            transcription=TranscriptionConfig(model="large-v3")
        )

        # Recharger depuis le fichier
        new_config = reload_config(temp_config_file)

        assert new_config.transcription.model == "tiny"
        assert get_config().transcription.model == "tiny"
