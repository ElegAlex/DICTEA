# DICTEA - Technical Architecture Document

**Version:** 1.0.0
**Date:** 2026-01-14
**Référence PRD:** [PRD.md](./PRD.md)
**Méthodologie:** BMAD (Breakthrough Method for Agile AI-Driven Development)
**Phase:** Solutioning - Technical Blueprint

---

## Table des matières

1. [Vue d'ensemble](#1-vue-densemble)
2. [Architecture C4 Model](#2-architecture-c4-model)
3. [Architecture des Composants](#3-architecture-des-composants)
4. [Architecture des Données](#4-architecture-des-données)
5. [Architecture Threading](#5-architecture-threading)
6. [Flux de Données](#6-flux-de-données)
7. [Interfaces et Contrats](#7-interfaces-et-contrats)
8. [Architecture de Déploiement](#8-architecture-de-déploiement)
9. [Sécurité](#9-sécurité)
10. [Performance](#10-performance)
11. [ADRs (Architecture Decision Records)](#11-adrs-architecture-decision-records)
12. [Dépendances Techniques](#12-dépendances-techniques)

---

## 1. Vue d'ensemble

### 1.1 Résumé Architectural

DICTEA est une **application desktop monolithique** Windows conçue pour la transcription audio offline avec identification des locuteurs. L'architecture suit les principes de **séparation des responsabilités** avec une structure en couches.

### 1.2 Principes Architecturaux

| Principe | Application |
|----------|-------------|
| **Offline-First** | Aucune dépendance runtime à internet |
| **CPU-Only** | Optimisé pour processeurs Intel sans GPU |
| **Separation of Concerns** | Core / UI / Utils distincts |
| **Single Responsibility** | 1 module = 1 responsabilité |
| **Dependency Injection** | Configuration injectable |
| **Event-Driven UI** | Signals/Slots Qt |

### 1.3 Stack Technologique

```
┌─────────────────────────────────────────────────────────────────┐
│                      STACK TECHNIQUE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PRÉSENTATION                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  PySide6 (Qt6)                                          │   │
│  │  └─ QMainWindow, QThread, Signals/Slots                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│  LOGIQUE MÉTIER              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Workers (QObject)                                       │   │
│  │  ├─ TranscriptionWorker                                 │   │
│  │  ├─ DiarizationWorker                                   │   │
│  │  └─ FullPipelineWorker                                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│  CORE ML                     ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Transcriber (faster-whisper)                           │   │
│  │  ├─ WhisperModel (CTranslate2)                         │   │
│  │  └─ Compute: int8 quantization                          │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │  Diarizer (dual-mode)                                   │   │
│  │  ├─ Pyannote 3.1 (quality)                             │   │
│  │  └─ SpeechBrain ECAPA-TDNN (fast)                      │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │  AudioProcessor                                         │   │
│  │  ├─ sounddevice (recording)                            │   │
│  │  ├─ soundfile (I/O)                                    │   │
│  │  └─ pydub (conversion)                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│  INFRASTRUCTURE              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Configuration (YAML)                                   │   │
│  │  ModelManager (HuggingFace Hub)                        │   │
│  │  Logging (Python logging)                              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Architecture C4 Model

### 2.1 Level 1: System Context

```
┌─────────────────────────────────────────────────────────────────┐
│                    SYSTEM CONTEXT                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                    ┌──────────────┐                            │
│                    │  Utilisateur │                            │
│                    │  (Persona)   │                            │
│                    └──────┬───────┘                            │
│                           │                                     │
│                           │ Utilise                            │
│                           ▼                                     │
│              ┌────────────────────────┐                        │
│              │                        │                        │
│              │        DICTEA         │                        │
│              │   (Desktop App)       │                        │
│              │                        │                        │
│              │  Transcription Audio  │                        │
│              │  + Diarisation        │                        │
│              │  100% Offline         │                        │
│              │                        │                        │
│              └───────────┬────────────┘                        │
│                          │                                      │
│         ┌────────────────┼────────────────┐                    │
│         │                │                │                    │
│         ▼                ▼                ▼                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ HuggingFace │  │ Système     │  │ Fichiers    │            │
│  │ Hub         │  │ Audio       │  │ Locaux      │            │
│  │             │  │ (Micro)     │  │ (Import/    │            │
│  │ [Download   │  │             │  │  Export)    │            │
│  │  initial]   │  │             │  │             │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Level 2: Container Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONTAINER DIAGRAM                            │
│                    Application DICTEA                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    DESKTOP APPLICATION                   │   │
│  │                    [Python + PySide6]                    │   │
│  │                                                          │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌─────────────┐  │   │
│  │  │   UI Layer    │  │  Core Layer   │  │ Utils Layer │  │   │
│  │  │               │  │               │  │             │  │   │
│  │  │  MainWindow   │─▶│  Transcriber  │  │   Config    │  │   │
│  │  │  Workers      │  │  Diarizer     │◀─│ ModelMgr    │  │   │
│  │  │               │  │  AudioProc    │  │             │  │   │
│  │  └───────────────┘  └───────────────┘  └─────────────┘  │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
│         ┌────────────────┼────────────────┐                    │
│         │                │                │                    │
│         ▼                ▼                ▼                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   models/   │  │   temp/     │  │   output/   │            │
│  │             │  │             │  │             │            │
│  │ ML Models   │  │ Fichiers    │  │ Exports     │            │
│  │ Cache       │  │ Temporaires │  │ (TXT, SRT)  │            │
│  │ (~3 Go)     │  │             │  │             │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 Level 3: Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMPONENT DIAGRAM                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  UI LAYER (src/ui/)                                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  ┌─────────────────┐        ┌─────────────────────────┐ │   │
│  │  │   MainWindow    │        │       Workers           │ │   │
│  │  │                 │        │                         │ │   │
│  │  │  • UI Layout    │◀──────▶│  • TranscriptionWorker │ │   │
│  │  │  • Event Handle │signals │  • DiarizationWorker   │ │   │
│  │  │  • State Mgmt   │        │  • FullPipelineWorker  │ │   │
│  │  │                 │        │  • WorkerThread        │ │   │
│  │  └────────┬────────┘        └───────────┬─────────────┘ │   │
│  │           │                             │               │   │
│  └───────────┼─────────────────────────────┼───────────────┘   │
│              │                             │                    │
│              │ uses                        │ uses               │
│              ▼                             ▼                    │
│  CORE LAYER (src/core/)                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │   │
│  │  │ Transcriber │  │  Diarizer   │  │ AudioProcessor  │  │   │
│  │  │             │  │             │  │                 │  │   │
│  │  │ •load_model │  │ •load()     │  │ •convert_audio  │  │   │
│  │  │ •transcribe │  │ •diarize()  │  │ •record()       │  │   │
│  │  │ •unload     │  │ •unload()   │  │ •get_info()     │  │   │
│  │  │             │  │             │  │                 │  │   │
│  │  │ WhisperModel│  │ Pyannote OR │  │ sounddevice     │  │   │
│  │  │ (faster-w)  │  │ SpeechBrain │  │ pydub           │  │   │
│  │  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘  │   │
│  │         │                │                  │           │   │
│  └─────────┼────────────────┼──────────────────┼───────────┘   │
│            │                │                  │                │
│            │ uses           │ uses             │ uses           │
│            ▼                ▼                  ▼                │
│  UTILS LAYER (src/utils/)                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  ┌─────────────────────┐  ┌─────────────────────────┐   │   │
│  │  │      Config         │  │    ModelManager         │   │   │
│  │  │                     │  │                         │   │   │
│  │  │  • AppConfig        │  │  • download_whisper()   │   │   │
│  │  │  • get_config()     │  │  • is_downloaded()      │   │   │
│  │  │  • reload_config()  │  │  • get_model_path()     │   │   │
│  │  │                     │  │                         │   │   │
│  │  │  [Singleton]        │  │  [HuggingFace Hub]      │   │   │
│  │  └─────────────────────┘  └─────────────────────────┘   │   │
│  │                                                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Architecture des Composants

### 3.1 Structure des Modules

```
transcription-app/
│
├── main.py                          # Entry Point
│   └── Application bootstrap
│
├── config.yaml                      # Configuration
│   └── User settings
│
├── src/
│   │
│   ├── core/                        # CORE LAYER
│   │   ├── __init__.py             # Exports publics
│   │   ├── transcriber.py          # ASR Engine
│   │   ├── diarizer.py             # Speaker ID
│   │   └── audio_processor.py      # Audio I/O
│   │
│   ├── ui/                          # UI LAYER
│   │   ├── __init__.py             # Exports publics
│   │   ├── main_window.py          # GUI principale
│   │   ├── workers.py              # Thread workers
│   │   └── components/             # Widgets réutilisables
│   │
│   └── utils/                       # UTILS LAYER
│       ├── __init__.py             # Exports publics
│       ├── config.py               # Configuration mgmt
│       └── model_manager.py        # Model download
│
├── models/                          # ML Models Cache
├── output/                          # Export directory
├── temp/                            # Temporary files
│
└── scripts/
    ├── build.py                    # Build automation
    └── installer.iss               # Windows installer
```

### 3.2 Responsabilités des Composants

#### 3.2.1 Core Layer

| Composant | Responsabilité | Dépendances |
|-----------|----------------|-------------|
| **Transcriber** | Conversion audio→texte via Whisper | faster-whisper, ModelManager |
| **Diarizer** | Identification locuteurs | Pyannote/SpeechBrain, torch |
| **AudioProcessor** | I/O audio, conversion, recording | sounddevice, pydub, soundfile |

#### 3.2.2 UI Layer

| Composant | Responsabilité | Dépendances |
|-----------|----------------|-------------|
| **MainWindow** | Interface graphique, orchestration | PySide6, Core components |
| **Workers** | Exécution async des traitements ML | QThread, Core components |

#### 3.2.3 Utils Layer

| Composant | Responsabilité | Dépendances |
|-----------|----------------|-------------|
| **Config** | Gestion configuration YAML | PyYAML, dataclasses |
| **ModelManager** | Téléchargement/cache modèles | huggingface_hub |

### 3.3 Diagramme de Classes

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLASS DIAGRAM                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  «dataclass»                     «dataclass»                    │
│  ┌──────────────────┐            ┌──────────────────┐          │
│  │TranscriptionSegment│          │  SpeakerSegment  │          │
│  ├──────────────────┤            ├──────────────────┤          │
│  │ +start: float    │            │ +start: float    │          │
│  │ +end: float      │            │ +end: float      │          │
│  │ +text: str       │            │ +speaker: str    │          │
│  │ +speaker: str?   │            └──────────────────┘          │
│  │ +confidence: float│                   △                     │
│  └──────────────────┘                    │                     │
│          △                               │                     │
│          │                               │                     │
│          │ contains                      │ contains            │
│          │                               │                     │
│  «dataclass»                     «dataclass»                    │
│  ┌──────────────────┐            ┌──────────────────┐          │
│  │TranscriptionResult│           │DiarizationResult │          │
│  ├──────────────────┤            ├──────────────────┤          │
│  │ +segments: List  │            │ +segments: List  │          │
│  │ +language: str   │            │ +num_speakers: int│          │
│  │ +duration: float │            ├──────────────────┤          │
│  ├──────────────────┤            │ +get_speaker_at()│          │
│  │ +to_text()       │            │ +get_speaker_for_│          │
│  │ +to_srt()        │            │  range()         │          │
│  └──────────────────┘            └──────────────────┘          │
│                                                                 │
│  ┌──────────────────┐            ┌──────────────────┐          │
│  │   Transcriber    │            │    Diarizer      │          │
│  ├──────────────────┤            ├──────────────────┤          │
│  │ -model: WhisperModel          │ -pipeline        │          │
│  │ -config: TranscriptionConfig  │ -config: DiarizationConfig  │
│  │ -model_manager   │            │ -mode: str       │          │
│  ├──────────────────┤            ├──────────────────┤          │
│  │ +load_model()    │            │ +load()          │          │
│  │ +transcribe()    │            │ +diarize()       │          │
│  │ +unload_model()  │            │ +unload()        │          │
│  └──────────────────┘            └──────────────────┘          │
│          │                               │                     │
│          │ uses                          │ uses                │
│          ▼                               ▼                     │
│  ┌──────────────────┐            ┌──────────────────┐          │
│  │  ModelManager    │            │   AppConfig      │          │
│  ├──────────────────┤            ├──────────────────┤          │
│  │ +download_model()│            │ +transcription   │          │
│  │ +is_downloaded() │            │ +diarization     │          │
│  │ +get_model_path()│            │ +audio           │          │
│  └──────────────────┘            │ +paths           │          │
│                                  ├──────────────────┤          │
│                                  │ +load()          │          │
│                                  │ +save()          │          │
│                                  └──────────────────┘          │
│                                          △                     │
│                                          │                     │
│                                          │ singleton           │
│                                          │                     │
│                                  ┌──────────────────┐          │
│                                  │  get_config()    │          │
│                                  └──────────────────┘          │
│                                                                 │
│  «QMainWindow»                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    MainWindow                             │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ -transcriber: Transcriber                                │  │
│  │ -diarizer: Diarizer                                      │  │
│  │ -audio_recorder: AudioRecorder                           │  │
│  │ -current_result: TranscriptionResult                     │  │
│  │ -worker_thread: WorkerThread                             │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ +_on_import_clicked()                                    │  │
│  │ +_on_record_clicked()                                    │  │
│  │ +_on_transcribe_clicked()                                │  │
│  │ +_on_progress(step, percent, detail)                     │  │
│  │ +_on_finished(result)                                    │  │
│  │ +_on_error(message)                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│          │                                                      │
│          │ creates/uses                                         │
│          ▼                                                      │
│  «QObject»                                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              FullPipelineWorker                           │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ -transcriber: Transcriber                                │  │
│  │ -diarizer: Diarizer                                      │  │
│  │ -audio_path: Path                                        │  │
│  │ -_cancelled: bool                                        │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ «signal» progress(str, float, str)                       │  │
│  │ «signal» transcription_done(TranscriptionResult)         │  │
│  │ «signal» finished(TranscriptionResult)                   │  │
│  │ «signal» error(str)                                      │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ +run()                                                   │  │
│  │ +cancel()                                                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Architecture des Données

### 4.1 Modèle de Données

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA MODEL                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  INPUT DATA                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  AudioFile                     RecordedAudio            │   │
│  │  ┌──────────────────┐         ┌──────────────────┐      │   │
│  │  │ path: Path       │         │ frames: ndarray  │      │   │
│  │  │ format: str      │         │ sample_rate: int │      │   │
│  │  │ duration: float  │         │ channels: int    │      │   │
│  │  │ sample_rate: int │         │ duration: float  │      │   │
│  │  │ channels: int    │         └──────────────────┘      │   │
│  │  └──────────────────┘                                   │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              │ converted to                     │
│                              ▼                                  │
│  PROCESSING DATA                                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  WhisperAudio (normalized)                              │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │ data: ndarray[float32]                           │   │   │
│  │  │ sample_rate: 16000 Hz                            │   │   │
│  │  │ channels: 1 (mono)                               │   │   │
│  │  │ duration: float                                  │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│         ┌────────────────────┼────────────────────┐            │
│         │                    │                    │            │
│         ▼                    ▼                    ▼            │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐    │
│  │ Transcription│     │ Diarization │      │   Merged    │    │
│  │   Result    │  +   │   Result    │  =   │   Result    │    │
│  └─────────────┘      └─────────────┘      └─────────────┘    │
│                                                                 │
│  OUTPUT DATA                                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  TranscriptionResult (final)                            │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │ segments: List[TranscriptionSegment]             │   │   │
│  │  │   ├─ start: float                                │   │   │
│  │  │   ├─ end: float                                  │   │   │
│  │  │   ├─ text: str                                   │   │   │
│  │  │   ├─ speaker: str (SPEAKER_XX)                   │   │   │
│  │  │   └─ confidence: float                           │   │   │
│  │  │ language: str                                    │   │   │
│  │  │ language_probability: float                      │   │   │
│  │  │ duration: float                                  │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│         ┌────────────────────┼────────────────────┐            │
│         │                    │                    │            │
│         ▼                    ▼                    ▼            │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐    │
│  │  TXT File   │      │  SRT File   │      │  Clipboard  │    │
│  │  (UTF-8)    │      │  (SubRip)   │      │  (system)   │    │
│  └─────────────┘      └─────────────┘      └─────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Schéma de Configuration (YAML)

```yaml
# config.yaml - Schema Definition

app:
  name: string          # Application name
  version: string       # Semantic version
  language: string      # UI language (fr, en)

transcription:
  model: enum           # tiny|base|small|medium|large-v3
  compute_type: enum    # int8|float16|float32
  language: string      # ISO 639-1 code or "auto"
  cpu_threads: integer  # 0 = auto-detect
  vad_filter: boolean   # Voice Activity Detection
  beam_size: integer    # 1-10

diarization:
  mode: enum            # quality|fast|disabled
  min_speakers: integer # 0 = auto
  max_speakers: integer # 0 = auto

audio:
  sample_rate: integer  # Hz (16000 standard)
  channels: integer     # 1 = mono
  export_format: enum   # wav|mp3
  input_device: string? # null = default

paths:
  models: string        # ML models directory
  output: string        # Export directory
  temp: string          # Temporary files

performance:
  chunk_size_minutes: integer  # For long files
  aggressive_gc: boolean       # Memory cleanup
```

### 4.3 Formats d'Export

#### TXT Format
```
[HH:MM:SS - HH:MM:SS] SPEAKER_XX
Texte du segment transcrit avec ponctuation.

[HH:MM:SS - HH:MM:SS] SPEAKER_YY
Texte du segment suivant.
```

#### SRT Format
```srt
1
HH:MM:SS,mmm --> HH:MM:SS,mmm
[SPEAKER_XX] Texte du segment.

2
HH:MM:SS,mmm --> HH:MM:SS,mmm
[SPEAKER_YY] Texte suivant.
```

---

## 5. Architecture Threading

### 5.1 Modèle de Threads

```
┌─────────────────────────────────────────────────────────────────┐
│                    THREADING MODEL                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    MAIN THREAD                           │   │
│  │                    (Qt Event Loop)                       │   │
│  │                                                          │   │
│  │  Responsabilités:                                        │   │
│  │  • Rendu UI (QMainWindow)                               │   │
│  │  • Gestion événements utilisateur                       │   │
│  │  • Réception signaux workers                            │   │
│  │  • Mise à jour affichage                                │   │
│  │                                                          │   │
│  │  Contrainte: JAMAIS de traitement > 100ms              │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
│                          │ signals/slots                        │
│                          │                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    WORKER THREAD                         │   │
│  │                    (QThread)                             │   │
│  │                                                          │   │
│  │  Responsabilités:                                        │   │
│  │  • Chargement modèles ML                                │   │
│  │  • Transcription (Whisper)                              │   │
│  │  • Diarisation (Pyannote/SpeechBrain)                   │   │
│  │  • Fusion résultats                                     │   │
│  │                                                          │   │
│  │  Workers:                                                │   │
│  │  • TranscriptionWorker                                  │   │
│  │  • DiarizationWorker                                    │   │
│  │  • FullPipelineWorker                                   │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
│                          │ threading.Thread                     │
│                          │                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 AUDIO COLLECTION THREAD                  │   │
│  │                 (daemon thread)                          │   │
│  │                                                          │   │
│  │  Responsabilités:                                        │   │
│  │  • Collecte frames audio depuis queue                   │   │
│  │  • Concaténation buffers                                │   │
│  │  • Callback durée enregistrement                        │   │
│  │                                                          │   │
│  │  Communication: queue.Queue (thread-safe)               │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Communication Inter-Threads

```
┌─────────────────────────────────────────────────────────────────┐
│                 SIGNAL/SLOT COMMUNICATION                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  WORKER → MAIN THREAD (Signals)                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  progress(step: str, percent: float, detail: str)       │   │
│  │  └─→ MainWindow._on_progress()                          │   │
│  │      └─→ Update progress bar + status                   │   │
│  │                                                          │   │
│  │  segment_ready(index: int, text: str)                   │   │
│  │  └─→ MainWindow._on_segment_ready()                     │   │
│  │      └─→ Append to results display                      │   │
│  │                                                          │   │
│  │  transcription_done(result: TranscriptionResult)        │   │
│  │  └─→ MainWindow._on_transcription_done()                │   │
│  │      └─→ Display intermediate result                    │   │
│  │                                                          │   │
│  │  finished(result: TranscriptionResult)                  │   │
│  │  └─→ MainWindow._on_finished()                          │   │
│  │      └─→ Display final result, enable export            │   │
│  │                                                          │   │
│  │  error(message: str)                                    │   │
│  │  └─→ MainWindow._on_error()                             │   │
│  │      └─→ Show error dialog, reset UI                    │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  MAIN → WORKER THREAD (Method calls)                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  worker.cancel()                                        │   │
│  │  └─→ Sets _cancelled = True                             │   │
│  │      └─→ Worker checks flag and stops gracefully        │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  THREAD LIFECYCLE                                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  thread.started  ──connect──▶  worker.run()             │   │
│  │  worker.finished ──connect──▶  thread.quit()            │   │
│  │  worker.error    ──connect──▶  thread.quit()            │   │
│  │  thread.finished ──connect──▶  cleanup()                │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 Gestion de l'Annulation

```python
# Pattern d'annulation thread-safe

class FullPipelineWorker(QObject):
    def __init__(self):
        self._cancelled = False

    def cancel(self):
        """Appelé depuis le main thread."""
        self._cancelled = True

    def run(self):
        """Exécuté dans le worker thread."""
        # Check régulier du flag
        if self._cancelled:
            return

        # Transcription
        for segment in transcriber.transcribe_stream(...):
            if self._cancelled:
                self._cleanup()
                return
            self.segment_ready.emit(...)

        # Diarisation
        if self._cancelled:
            return
        result = diarizer.diarize(...)

        # Émission résultat final
        if not self._cancelled:
            self.finished.emit(result)
```

---

## 6. Flux de Données

### 6.1 Pipeline de Transcription Complet

```
┌─────────────────────────────────────────────────────────────────┐
│              COMPLETE TRANSCRIPTION PIPELINE                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ÉTAPE 1: ACQUISITION AUDIO                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  ┌──────────────┐        ┌──────────────┐               │   │
│  │  │ Import File  │   OR   │ Record Micro │               │   │
│  │  │ (.mp3/.wav)  │        │ (sounddevice)│               │   │
│  │  └──────┬───────┘        └──────┬───────┘               │   │
│  │         │                       │                        │   │
│  │         └───────────┬───────────┘                        │   │
│  │                     │                                    │   │
│  │                     ▼                                    │   │
│  │         ┌──────────────────────┐                        │   │
│  │         │   Raw Audio File     │                        │   │
│  │         │   (any format)       │                        │   │
│  │         └──────────────────────┘                        │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│  ÉTAPE 2: PRÉTRAITEMENT                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │         AudioProcessor.convert_for_whisper()            │   │
│  │                     │                                    │   │
│  │                     ▼                                    │   │
│  │         ┌──────────────────────┐                        │   │
│  │         │   Normalized Audio   │                        │   │
│  │         │   16kHz, mono, PCM   │                        │   │
│  │         └──────────────────────┘                        │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
│         ┌────────────────┴────────────────┐                    │
│         │                                 │                    │
│         ▼                                 ▼                    │
│  ÉTAPE 3A: TRANSCRIPTION           ÉTAPE 3B: DIARISATION      │
│  ┌────────────────────────┐       ┌────────────────────────┐  │
│  │                        │       │                        │  │
│  │  Transcriber.load_model()      │  Diarizer.load()       │  │
│  │         │              │       │         │              │  │
│  │         ▼              │       │         ▼              │  │
│  │  ┌──────────────┐      │       │  ┌──────────────┐      │  │
│  │  │ WhisperModel │      │       │  │ Pyannote OR  │      │  │
│  │  │ (faster-w)   │      │       │  │ SpeechBrain  │      │  │
│  │  └──────────────┘      │       │  └──────────────┘      │  │
│  │         │              │       │         │              │  │
│  │         ▼              │       │         ▼              │  │
│  │  Transcriber.transcribe()      │  Diarizer.diarize()    │  │
│  │         │              │       │         │              │  │
│  │         ▼              │       │         ▼              │  │
│  │  ┌──────────────┐      │       │  ┌──────────────┐      │  │
│  │  │Transcription │      │       │  │ Diarization  │      │  │
│  │  │   Result     │      │       │  │    Result    │      │  │
│  │  │              │      │       │  │              │      │  │
│  │  │ • segments[] │      │       │  │ • segments[] │      │  │
│  │  │ • language   │      │       │  │ • num_speakers      │  │
│  │  │ • duration   │      │       │  │              │      │  │
│  │  └──────────────┘      │       │  └──────────────┘      │  │
│  │                        │       │                        │  │
│  └────────────────────────┘       └────────────────────────┘  │
│         │                                 │                    │
│         └────────────────┬────────────────┘                    │
│                          │                                      │
│                          ▼                                      │
│  ÉTAPE 4: FUSION                                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │       assign_speakers_to_transcription()                │   │
│  │                     │                                    │   │
│  │                     ▼                                    │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │              ALGORITHME DE FUSION                 │   │   │
│  │  │                                                   │   │   │
│  │  │  for segment in transcription.segments:          │   │   │
│  │  │      speaker = diarization.get_speaker_for_range(│   │   │
│  │  │          segment.start, segment.end              │   │   │
│  │  │      )                                           │   │   │
│  │  │      segment.speaker = speaker                   │   │   │
│  │  │                                                   │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  │                     │                                    │   │
│  │                     ▼                                    │   │
│  │         ┌──────────────────────┐                        │   │
│  │         │   Final Result       │                        │   │
│  │         │   (with speakers)    │                        │   │
│  │         └──────────────────────┘                        │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│  ÉTAPE 5: EXPORT                                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐          │   │
│  │  │   TXT    │    │   SRT    │    │ Clipboard│          │   │
│  │  │  Export  │    │  Export  │    │   Copy   │          │   │
│  │  │          │    │          │    │          │          │   │
│  │  │ to_text()│    │ to_srt() │    │ to_text()│          │   │
│  │  └──────────┘    └──────────┘    └──────────┘          │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 Séquence d'Événements UI

```
┌─────────────────────────────────────────────────────────────────┐
│                 SEQUENCE DIAGRAM (Simplified)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  User        MainWindow     Worker        Transcriber  Diarizer │
│   │              │            │               │           │     │
│   │──[Transcribe]─▶           │               │           │     │
│   │              │            │               │           │     │
│   │              │─[create]──▶│               │           │     │
│   │              │            │               │           │     │
│   │              │─[start]───▶│               │           │     │
│   │              │            │──[load_model]─▶           │     │
│   │              │            │               │           │     │
│   │              │◀─progress──│               │           │     │
│   │◀─[update UI]─│            │               │           │     │
│   │              │            │               │           │     │
│   │              │            │──[transcribe]─▶           │     │
│   │              │            │               │           │     │
│   │              │◀─segment───│◀──[segments]──│           │     │
│   │◀─[show text]─│            │               │           │     │
│   │              │            │               │           │     │
│   │              │            │───────────────────[diarize]▶    │
│   │              │            │               │           │     │
│   │              │◀─progress──│               │◀─[result]─│     │
│   │◀─[update UI]─│            │               │           │     │
│   │              │            │               │           │     │
│   │              │◀─finished──│               │           │     │
│   │◀─[show final]│            │               │           │     │
│   │              │            │               │           │     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. Interfaces et Contrats

### 7.1 Interface Transcriber

```python
class ITranscriber(Protocol):
    """Interface pour le moteur de transcription."""

    def load_model(self) -> None:
        """Charge le modèle ML en mémoire.

        Raises:
            ModelNotFoundError: Si le modèle n'existe pas
            MemoryError: Si mémoire insuffisante
        """
        ...

    def transcribe(
        self,
        audio_path: Path,
        language: str = "fr",
        progress_callback: Callable[[float], None] | None = None
    ) -> TranscriptionResult:
        """Transcrit un fichier audio.

        Args:
            audio_path: Chemin vers le fichier audio
            language: Code ISO 639-1 ou "auto"
            progress_callback: Callback de progression (0.0-1.0)

        Returns:
            TranscriptionResult avec segments et métadonnées

        Raises:
            AudioProcessingError: Si fichier audio invalide
            TranscriptionError: Si transcription échoue
        """
        ...

    def unload_model(self) -> None:
        """Décharge le modèle et libère la mémoire."""
        ...

    @property
    def is_loaded(self) -> bool:
        """Retourne True si modèle chargé."""
        ...
```

### 7.2 Interface Diarizer

```python
class IDiarizer(Protocol):
    """Interface pour le moteur de diarisation."""

    def load(self, mode: Literal["quality", "fast"]) -> None:
        """Charge le pipeline de diarisation.

        Args:
            mode: "quality" (Pyannote) ou "fast" (SpeechBrain)

        Raises:
            ModelNotFoundError: Si modèle non disponible
            TokenError: Si token HuggingFace invalide (Pyannote)
        """
        ...

    def diarize(
        self,
        audio_path: Path,
        min_speakers: int = 0,
        max_speakers: int = 0,
        progress_callback: Callable[[float], None] | None = None
    ) -> DiarizationResult:
        """Identifie les locuteurs dans l'audio.

        Args:
            audio_path: Chemin vers le fichier audio
            min_speakers: Nombre min de locuteurs (0=auto)
            max_speakers: Nombre max de locuteurs (0=auto)
            progress_callback: Callback de progression

        Returns:
            DiarizationResult avec segments par locuteur

        Raises:
            DiarizationError: Si diarisation échoue
        """
        ...

    def unload(self) -> None:
        """Décharge le pipeline et libère la mémoire."""
        ...
```

### 7.3 Interface Worker

```python
class IWorker(Protocol):
    """Interface pour les workers de traitement."""

    # Signaux Qt
    started: Signal
    progress: Signal  # (step: str, percent: float, detail: str)
    finished: Signal  # (result: TranscriptionResult)
    error: Signal     # (message: str)

    def run(self) -> None:
        """Exécute le traitement (appelé dans le thread worker)."""
        ...

    def cancel(self) -> None:
        """Demande l'annulation du traitement."""
        ...

    @property
    def is_cancelled(self) -> bool:
        """Retourne True si annulation demandée."""
        ...
```

### 7.4 Contrats de Données

```python
@dataclass
class TranscriptionSegment:
    """Segment de transcription avec métadonnées."""
    start: float           # Timestamp début (secondes)
    end: float             # Timestamp fin (secondes)
    text: str              # Texte transcrit
    speaker: str = ""      # ID locuteur (SPEAKER_XX)
    confidence: float = 0.0  # Score de confiance [0-1]

    def __post_init__(self):
        assert self.start >= 0, "start must be non-negative"
        assert self.end > self.start, "end must be > start"
        assert 0 <= self.confidence <= 1, "confidence must be [0-1]"


@dataclass
class TranscriptionResult:
    """Résultat complet de transcription."""
    segments: list[TranscriptionSegment]
    language: str
    language_probability: float
    duration: float

    def to_text(self, include_timestamps: bool = True) -> str:
        """Formate en texte lisible."""
        ...

    def to_srt(self) -> str:
        """Formate en sous-titres SRT."""
        ...


@dataclass
class DiarizationResult:
    """Résultat de diarisation."""
    segments: list[SpeakerSegment]
    num_speakers: int

    def get_speaker_at(self, time: float) -> str:
        """Retourne le locuteur à un instant donné."""
        ...

    def get_speaker_for_range(self, start: float, end: float) -> str:
        """Retourne le locuteur majoritaire sur une plage."""
        ...
```

---

## 8. Architecture de Déploiement

### 8.1 Structure de Distribution

```
┌─────────────────────────────────────────────────────────────────┐
│                 DEPLOYMENT ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  BUILD PIPELINE                                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  Source Code                                            │   │
│  │       │                                                  │   │
│  │       ├─────────────────┬─────────────────┐             │   │
│  │       │                 │                 │             │   │
│  │       ▼                 ▼                 ▼             │   │
│  │  ┌─────────┐      ┌─────────┐      ┌─────────┐         │   │
│  │  │PyInstaller     │  Nuitka │      │  Inno   │         │   │
│  │  │ (--dev) │      │(--release)     │  Setup  │         │   │
│  │  └────┬────┘      └────┬────┘      └────┬────┘         │   │
│  │       │                │                │              │   │
│  │       ▼                ▼                ▼              │   │
│  │  ┌─────────┐      ┌─────────┐      ┌─────────┐         │   │
│  │  │  dist/  │      │  dist/  │      │ Setup.  │         │   │
│  │  │TransApp/│      │TransApp │      │   exe   │         │   │
│  │  │ (folder)│      │  .exe   │      │         │         │   │
│  │  └─────────┘      └─────────┘      └─────────┘         │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  INSTALLED STRUCTURE                                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  C:\Program Files\DICTEA\                               │   │
│  │  ├── TranscriptionApp.exe      # Main executable        │   │
│  │  ├── config.yaml               # User configuration     │   │
│  │  ├── _internal\                # Python runtime (if PI) │   │
│  │  │   ├── PySide6\              # Qt libraries           │   │
│  │  │   ├── faster_whisper\       # ML library             │   │
│  │  │   └── ...                                            │   │
│  │  └── unins000.exe              # Uninstaller            │   │
│  │                                                          │   │
│  │  %APPDATA%\DICTEA\                                      │   │
│  │  ├── models\                   # ML models cache        │   │
│  │  │   ├── faster-whisper-medium\                         │   │
│  │  │   └── pyannote\                                      │   │
│  │  ├── output\                   # Export directory       │   │
│  │  ├── temp\                     # Temporary files        │   │
│  │  └── logs\                     # Application logs       │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 Configuration Build

#### PyInstaller (Développement)

```python
# build.py - PyInstaller configuration
PYINSTALLER_ARGS = [
    'main.py',
    '--name=TranscriptionApp',
    '--onedir',
    '--windowed',
    '--noconfirm',
    '--add-data=config.yaml:.',
    '--hidden-import=tiktoken_ext.openai_public',
    '--hidden-import=ctranslate2',
    '--hidden-import=huggingface_hub',
    '--hidden-import=sounddevice',
    '--hidden-import=soundfile',
    '--hidden-import=sklearn.cluster',
    '--collect-all=faster_whisper',
    '--collect-all=pyannote',
]
```

#### Nuitka (Release)

```python
# build.py - Nuitka configuration
NUITKA_ARGS = [
    'main.py',
    '--standalone',
    '--onefile',
    '--windows-disable-console',
    '--enable-plugin=pyside6',
    '--include-package=faster_whisper',
    '--include-package=pyannote',
    '--include-package=ctranslate2',
    '--include-data-file=config.yaml=config.yaml',
    '--output-filename=TranscriptionApp.exe',
]
```

### 8.3 Prérequis Runtime

```
┌─────────────────────────────────────────────────────────────────┐
│                 RUNTIME REQUIREMENTS                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  SYSTÈME                                                       │
│  ├── Windows 10/11 64-bit                                      │
│  ├── CPU: Intel i5+ avec AVX2 (post-2013)                     │
│  ├── RAM: 16 Go minimum (8 Go utilisés)                        │
│  └── Stockage: 5 Go (3 Go modèles + 2 Go app)                 │
│                                                                 │
│  DÉPENDANCES RUNTIME (bundled)                                 │
│  ├── Visual C++ Redistributable 2019+                         │
│  ├── Qt6 Runtime (via PySide6)                                │
│  └── OpenMP Runtime (pour ML)                                 │
│                                                                 │
│  RÉSEAU (first-run only)                                       │
│  ├── HuggingFace Hub access                                    │
│  ├── ~1.5 Go download (whisper-medium)                        │
│  └── ~500 Mo download (pyannote)                              │
│                                                                 │
│  PERMISSIONS                                                    │
│  ├── Microphone access (for recording)                        │
│  ├── File system (read/write output)                          │
│  └── Network (first-run model download)                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. Sécurité

### 9.1 Modèle de Menaces

```
┌─────────────────────────────────────────────────────────────────┐
│                    THREAT MODEL                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  SURFACE D'ATTAQUE                                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  ┌─────────────┐                                        │   │
│  │  │ Fichiers    │  Risque: Fichiers audio malformés      │   │
│  │  │ Audio       │  Mitigation: Validation format,        │   │
│  │  │ (input)     │              sandboxing pydub          │   │
│  │  └─────────────┘                                        │   │
│  │                                                          │   │
│  │  ┌─────────────┐                                        │   │
│  │  │ Config      │  Risque: YAML injection                │   │
│  │  │ YAML        │  Mitigation: safe_load(), validation   │   │
│  │  │ (input)     │              schema                    │   │
│  │  └─────────────┘                                        │   │
│  │                                                          │   │
│  │  ┌─────────────┐                                        │   │
│  │  │ HuggingFace │  Risque: MITM sur download             │   │
│  │  │ Downloads   │  Mitigation: HTTPS, checksum verify    │   │
│  │  │ (network)   │              (handled by HF Hub)       │   │
│  │  └─────────────┘                                        │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  DONNÉES SENSIBLES                                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  Type              Protection                           │   │
│  │  ─────────────────────────────────────────────────────  │   │
│  │  Audio files       Local only, never transmitted        │   │
│  │  Transcriptions    Local only, user controls export     │   │
│  │  Temp files        Auto-deleted, secure cleanup         │   │
│  │  Config            No secrets, local only               │   │
│  │  HF Token          Stored in env or user input          │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 9.2 Mesures de Sécurité

| Mesure | Implementation |
|--------|----------------|
| **Traitement local** | Aucun appel réseau pendant transcription |
| **Nettoyage temp** | `atexit.register()` + cleanup explicite |
| **Validation input** | soundfile/pydub pour validation audio |
| **YAML safe** | `yaml.safe_load()` uniquement |
| **No telemetry** | Aucun SDK analytics intégré |
| **Code protection** | Nuitka compilation pour release |

### 9.3 RGPD Compliance

```
┌─────────────────────────────────────────────────────────────────┐
│                    RGPD COMPLIANCE                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PRINCIPE                 APPLICATION DICTEA                   │
│  ───────────────────────────────────────────────────────────── │
│                                                                 │
│  Minimisation            • Aucune donnée collectée            │
│                          • Traitement local uniquement         │
│                                                                 │
│  Limitation finalité     • Audio traité uniquement pour        │
│                            transcription                       │
│                                                                 │
│  Limitation conservation • Fichiers temp supprimés après       │
│                            traitement                          │
│                          • Aucun historique conservé           │
│                                                                 │
│  Intégrité/Confid.      • Aucune transmission externe         │
│                          • Traitement 100% local               │
│                                                                 │
│  Privacy by Design       • Architecture offline-first          │
│                          • Pas de dépendance cloud             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10. Performance

### 10.1 Budgets de Performance

```
┌─────────────────────────────────────────────────────────────────┐
│                 PERFORMANCE BUDGETS                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  TEMPS DE TRAITEMENT (budget par phase)                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  Phase              Budget      % Total                  │   │
│  │  ──────────────────────────────────────────────────────  │   │
│  │  Chargement modèle  30s max     N/A (one-time)          │   │
│  │  Transcription      ≤1.0x RTF   40%                     │   │
│  │  Diarisation (Q)    ≤2.5x RTF   55%                     │   │
│  │  Diarisation (F)    ≤0.5x RTF   20%                     │   │
│  │  Fusion             ≤1s         5%                      │   │
│  │  ──────────────────────────────────────────────────────  │   │
│  │  TOTAL (Quality)    ≤4.0x RTF                           │   │
│  │  TOTAL (Fast)       ≤1.5x RTF                           │   │
│  │                                                          │   │
│  │  RTF = Real-Time Factor (durée traitement / durée audio)│   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  MÉMOIRE (budget par composant)                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  Composant          Baseline    Peak                    │   │
│  │  ──────────────────────────────────────────────────────  │   │
│  │  Application        200 Mo      500 Mo                  │   │
│  │  Whisper model      2 Go        4 Go                    │   │
│  │  Pyannote pipeline  1 Go        3 Go                    │   │
│  │  Audio buffers      100 Mo      500 Mo                  │   │
│  │  ──────────────────────────────────────────────────────  │   │
│  │  TOTAL MAX          -           8 Go                    │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  UI RESPONSIVENESS (latency budgets)                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  Interaction        Budget                              │   │
│  │  ──────────────────────────────────────────────────────  │   │
│  │  Click → feedback   ≤100ms                              │   │
│  │  Progress update    ≤500ms                              │   │
│  │  Segment display    ≤200ms                              │   │
│  │  Cancel → stop      ≤5s                                 │   │
│  │  Scroll (60 FPS)    ≤16ms                               │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 10.2 Stratégies d'Optimisation

```
┌─────────────────────────────────────────────────────────────────┐
│              OPTIMIZATION STRATEGIES                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  CPU OPTIMIZATION                                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  # main.py - Environment setup                          │   │
│  │  physical_cores = os.cpu_count() // 2                   │   │
│  │                                                          │   │
│  │  os.environ["OMP_NUM_THREADS"] = str(physical_cores)    │   │
│  │  os.environ["MKL_NUM_THREADS"] = str(physical_cores)    │   │
│  │  os.environ["OMP_WAIT_POLICY"] = "PASSIVE"              │   │
│  │  os.environ["CUDA_VISIBLE_DEVICES"] = ""                │   │
│  │                                                          │   │
│  │  Rationale:                                              │   │
│  │  • Physical cores only (no hyperthreading benefit)      │   │
│  │  • PASSIVE reduces CPU spin-wait                        │   │
│  │  • CUDA disabled = no GPU detection overhead            │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  MODEL QUANTIZATION                                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  # transcriber.py                                       │   │
│  │  model = WhisperModel(                                  │   │
│  │      model_path,                                        │   │
│  │      device="cpu",                                      │   │
│  │      compute_type="int8",  # 4x faster than float32    │   │
│  │      cpu_threads=config.cpu_threads                     │   │
│  │  )                                                       │   │
│  │                                                          │   │
│  │  Benefits:                                               │   │
│  │  • 4x speedup vs float32                                │   │
│  │  • 2x memory reduction                                  │   │
│  │  • Minimal quality loss (<1% WER increase)              │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  VAD FILTERING                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  # transcriber.py                                       │   │
│  │  segments, info = model.transcribe(                     │   │
│  │      audio_path,                                        │   │
│  │      vad_filter=True,  # Skip silence = ~30% speedup   │   │
│  │      vad_parameters={"min_silence_duration_ms": 500}    │   │
│  │  )                                                       │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  MEMORY MANAGEMENT                                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  Strategy              Implementation                   │   │
│  │  ──────────────────────────────────────────────────────  │   │
│  │  Lazy loading          Models loaded on-demand          │   │
│  │  Explicit unload       transcriber.unload_model()       │   │
│  │  Aggressive GC         gc.collect() after processing    │   │
│  │  Chunking              Split audio >30min               │   │
│  │  Temp cleanup          atexit + explicit cleanup        │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 11. ADRs (Architecture Decision Records)

### ADR-001: Choix de faster-whisper vs Whisper original

| Attribut | Valeur |
|----------|--------|
| **Statut** | Accepté |
| **Date** | 2026-01-14 |
| **Décideurs** | Équipe technique |

#### Contexte

Le projet nécessite un moteur ASR performant fonctionnant sur CPU sans GPU.

#### Décision

Utiliser **faster-whisper** (CTranslate2) au lieu de **openai-whisper**.

#### Justification

| Critère | Whisper | faster-whisper |
|---------|---------|----------------|
| Vitesse CPU | 1x (baseline) | **4x plus rapide** |
| Mémoire | ~8 Go | **~4 Go (int8)** |
| Quantification | Non | **int8 natif** |
| Streaming | Non | **Oui** |
| API | Compatible | Compatible |

#### Conséquences

- **Positif:** Performance 4x sur CPU, réduction mémoire 50%
- **Négatif:** Dépendance à CTranslate2, moins de documentation

---

### ADR-002: Choix de PySide6 vs PyQt6

| Attribut | Valeur |
|----------|--------|
| **Statut** | Accepté |
| **Date** | 2026-01-14 |
| **Décideurs** | Équipe technique |

#### Contexte

Le projet nécessite un framework GUI natif Windows avec threading robuste.

#### Décision

Utiliser **PySide6** (Qt6 officiel) au lieu de **PyQt6**.

#### Justification

| Critère | PyQt6 | PySide6 |
|---------|-------|---------|
| Licence | GPL/Commercial | **LGPL** |
| Mainteneur | Riverbank | **Qt Company** |
| API | Identique | Identique |
| Support LTS | Oui | **Oui (officiel)** |
| Distribution | GPL complexe | **LGPL simple** |

#### Conséquences

- **Positif:** Licence LGPL permissive, support officiel Qt
- **Négatif:** Quelques différences mineures de nommage

---

### ADR-003: Architecture threading avec QThread

| Attribut | Valeur |
|----------|--------|
| **Statut** | Accepté |
| **Date** | 2026-01-14 |
| **Décideurs** | Équipe technique |

#### Contexte

Les traitements ML sont longs (minutes à heures) et ne doivent pas bloquer l'UI.

#### Décision

Utiliser **QThread + Signals/Slots** pour les workers asynchrones.

#### Alternatives considérées

| Solution | Avantages | Inconvénients |
|----------|-----------|---------------|
| asyncio | Python natif | Pas thread-safe avec Qt |
| threading.Thread | Simple | Pas de signals Qt |
| multiprocessing | Isolation mémoire | Overhead IPC, pickle |
| **QThread** | **Intégré Qt, signals** | Learning curve |

#### Conséquences

- **Positif:** Communication thread-safe via signals, intégration Qt native
- **Négatif:** Couplage à Qt pour les workers

---

### ADR-004: Dual-mode diarisation

| Attribut | Valeur |
|----------|--------|
| **Statut** | Accepté |
| **Date** | 2026-01-14 |
| **Décideurs** | Équipe technique |

#### Contexte

La diarisation est coûteuse en temps CPU. Différents utilisateurs ont des besoins différents.

#### Décision

Implémenter deux modes de diarisation:
- **Quality:** Pyannote 3.1 (précis mais lent)
- **Fast:** SpeechBrain ECAPA-TDNN (rapide mais moins précis)

#### Justification

| Mode | DER | Temps/h audio | Use case |
|------|-----|---------------|----------|
| Quality | ~11% | 2-3h | Réunions formelles |
| Fast | ~18% | 20-30min | Interviews simples |

#### Conséquences

- **Positif:** Flexibilité utilisateur, meilleur UX
- **Négatif:** Deux pipelines à maintenir, plus de dépendances

---

### ADR-005: Configuration YAML singleton

| Attribut | Valeur |
|----------|--------|
| **Statut** | Accepté |
| **Date** | 2026-01-14 |
| **Décideurs** | Équipe technique |

#### Contexte

La configuration doit être accessible globalement mais chargée une seule fois.

#### Décision

Implémenter un **pattern Singleton** pour `AppConfig` avec `get_config()`.

#### Implémentation

```python
_config: AppConfig | None = None

def get_config() -> AppConfig:
    global _config
    if _config is None:
        _config = AppConfig.load()
    return _config
```

#### Conséquences

- **Positif:** Configuration centralisée, accès simple
- **Négatif:** État global, tests unitaires plus complexes

---

### ADR-006: Build Nuitka pour release

| Attribut | Valeur |
|----------|--------|
| **Statut** | Accepté |
| **Date** | 2026-01-14 |
| **Décideurs** | Équipe technique |

#### Contexte

Le code source doit être protégé contre la rétro-ingénierie en production.

#### Décision

Utiliser **Nuitka** pour les builds de release (compilation C++) et **PyInstaller** pour le développement (rapidité).

#### Comparaison

| Critère | PyInstaller | Nuitka |
|---------|-------------|--------|
| Temps build | 2-5 min | **20-30 min** |
| Taille output | ~300 Mo | ~200 Mo |
| Protection code | Bytecode (décompilable) | **C++ (difficile)** |
| Performance | Baseline | +10-30% |

#### Conséquences

- **Positif:** Protection code source, performance améliorée
- **Négatif:** Build time long, configuration complexe

---

## 12. Dépendances Techniques

### 12.1 Dépendances Python

```
┌─────────────────────────────────────────────────────────────────┐
│                 DEPENDENCY TREE                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  CORE ML                                                       │
│  ├── faster-whisper>=1.0.0                                     │
│  │   └── ctranslate2>=4.0.0                                   │
│  │       └── numpy>=1.20.0                                     │
│  ├── pyannote.audio>=3.1.0                                     │
│  │   ├── torch>=2.0.0                                         │
│  │   ├── torchaudio>=2.0.0                                    │
│  │   └── pyannote.core                                        │
│  └── speechbrain>=1.0.0 (optional, for fast mode)             │
│      └── torch>=2.0.0                                         │
│                                                                 │
│  AUDIO                                                         │
│  ├── sounddevice>=0.4.0                                        │
│  │   └── numpy>=1.20.0                                         │
│  ├── soundfile>=0.12.0                                         │
│  │   └── cffi>=1.0.0                                          │
│  └── pydub>=0.25.0                                             │
│      └── (ffmpeg system dependency)                            │
│                                                                 │
│  UI                                                             │
│  └── PySide6>=6.5.0                                            │
│      └── shiboken6>=6.5.0                                      │
│                                                                 │
│  UTILS                                                         │
│  ├── PyYAML>=6.0.0                                             │
│  ├── huggingface-hub>=0.19.0                                   │
│  └── tqdm>=4.65.0                                              │
│                                                                 │
│  DEV                                                           │
│  ├── pytest>=7.0.0                                             │
│  ├── pytest-qt>=4.2.0                                          │
│  └── black>=23.0.0                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 12.2 Dépendances Système

| Dépendance | Version | Obligatoire | Notes |
|------------|---------|-------------|-------|
| Windows | 10/11 64-bit | Oui | Plateforme cible |
| Visual C++ Runtime | 2019+ | Oui | Pour torch/ctranslate2 |
| FFmpeg | 4.0+ | Non | Pour formats audio étendus |

### 12.3 Modèles ML

| Modèle | Source | Taille | Téléchargement |
|--------|--------|--------|----------------|
| faster-whisper-medium | HuggingFace | ~1.5 Go | Automatique |
| pyannote/speaker-diarization-3.1 | HuggingFace | ~500 Mo | Automatique (token requis) |
| speechbrain/spkrec-ecapa-voxceleb | HuggingFace | ~100 Mo | Automatique |

---

## Historique des Révisions

| Version | Date | Auteur | Modifications |
|---------|------|--------|---------------|
| 1.0.0 | 2026-01-14 | Architect Agent (BMAD) | Création initiale |

---

**Documents connexes:**
- [PRD.md](./PRD.md) - Product Requirements Document
- [FUNCTIONAL_REQUIREMENTS.md](./FUNCTIONAL_REQUIREMENTS.md) - Requirements fonctionnelles
- [NON_FUNCTIONAL_REQUIREMENTS.md](./NON_FUNCTIONAL_REQUIREMENTS.md) - Requirements non-fonctionnelles
- [USER_STORIES.md](./USER_STORIES.md) - User Stories et Epics
