"""
Gestion de la configuration de l'application.
"""
import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TranscriptionConfig:
    model: str = "medium"
    compute_type: str = "int8"
    language: str = "fr"
    cpu_threads: int = 0
    vad_filter: bool = True
    beam_size: int = 5


@dataclass
class DiarizationConfig:
    mode: str = "quality"  # "quality" (Pyannote) ou "fast" (SpeechBrain)
    min_speakers: int = 0
    max_speakers: int = 0


@dataclass
class AudioConfig:
    sample_rate: int = 16000
    channels: int = 1
    export_format: str = "wav"
    input_device: Optional[int] = None


@dataclass
class PathsConfig:
    models: Path = field(default_factory=lambda: Path("models"))
    output: Path = field(default_factory=lambda: Path("output"))
    temp: Path = field(default_factory=lambda: Path("temp"))


@dataclass
class PerformanceConfig:
    chunk_size_minutes: int = 10
    aggressive_gc: bool = True


@dataclass
class AppConfig:
    transcription: TranscriptionConfig = field(default_factory=TranscriptionConfig)
    diarization: DiarizationConfig = field(default_factory=DiarizationConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    
    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "AppConfig":
        """Charge la configuration depuis un fichier YAML."""
        if config_path is None:
            # Chercher config.yaml à côté de l'exécutable ou dans le dossier courant
            possible_paths = [
                Path(__file__).parent.parent.parent / "config.yaml",
                Path.cwd() / "config.yaml",
                Path(os.environ.get("APPDATA", "")) / "TranscriptionApp" / "config.yaml",
            ]
            for p in possible_paths:
                if p.exists():
                    config_path = p
                    break
        
        config = cls()
        
        if config_path and config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            
            if "transcription" in data:
                config.transcription = TranscriptionConfig(**data["transcription"])
            if "diarization" in data:
                config.diarization = DiarizationConfig(**data["diarization"])
            if "audio" in data:
                config.audio = AudioConfig(**data["audio"])
            if "paths" in data:
                paths_data = data["paths"]
                config.paths = PathsConfig(
                    models=Path(paths_data.get("models", "models")),
                    output=Path(paths_data.get("output", "output")),
                    temp=Path(paths_data.get("temp", "temp")),
                )
            if "performance" in data:
                config.performance = PerformanceConfig(**data["performance"])
        
        # Créer les dossiers nécessaires
        config.paths.models.mkdir(parents=True, exist_ok=True)
        config.paths.output.mkdir(parents=True, exist_ok=True)
        config.paths.temp.mkdir(parents=True, exist_ok=True)
        
        return config
    
    def save(self, config_path: Path) -> None:
        """Sauvegarde la configuration dans un fichier YAML."""
        data = {
            "transcription": {
                "model": self.transcription.model,
                "compute_type": self.transcription.compute_type,
                "language": self.transcription.language,
                "cpu_threads": self.transcription.cpu_threads,
                "vad_filter": self.transcription.vad_filter,
                "beam_size": self.transcription.beam_size,
            },
            "diarization": {
                "mode": self.diarization.mode,
                "min_speakers": self.diarization.min_speakers,
                "max_speakers": self.diarization.max_speakers,
            },
            "audio": {
                "sample_rate": self.audio.sample_rate,
                "channels": self.audio.channels,
                "export_format": self.audio.export_format,
                "input_device": self.audio.input_device,
            },
            "paths": {
                "models": str(self.paths.models),
                "output": str(self.paths.output),
                "temp": str(self.paths.temp),
            },
            "performance": {
                "chunk_size_minutes": self.performance.chunk_size_minutes,
                "aggressive_gc": self.performance.aggressive_gc,
            },
        }
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)


# Singleton global
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Retourne la configuration globale (singleton)."""
    global _config
    if _config is None:
        _config = AppConfig.load()
    return _config


def reload_config(config_path: Optional[Path] = None) -> AppConfig:
    """Recharge la configuration depuis le fichier."""
    global _config
    _config = AppConfig.load(config_path)
    return _config
