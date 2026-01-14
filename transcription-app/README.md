# Application de Transcription Audio Offline

Application client lourd Windows pour transcrire des enregistrements audio avec identification des locuteurs (diarization).

## Caractéristiques

- **100% Offline** : Aucune connexion internet requise après téléchargement des modèles
- **Transcription haute qualité** : faster-whisper avec modèle medium (WER 6-8% sur le français)
- **Identification des locuteurs** : Pyannote Audio 3.1 pour distinguer qui parle
- **Enregistrement intégré** : Capture directe depuis le microphone
- **Import de fichiers** : Support WAV, MP3, M4A, FLAC, OGG, WMA, AAC
- **Export multi-formats** : TXT, SRT (sous-titres)

## Configuration requise

- **OS** : Windows 10/11 (64-bit)
- **CPU** : Intel i7 ou équivalent (AVX2 requis)
- **RAM** : 16 Go minimum
- **Stockage** : 5 Go (dont 3 Go pour les modèles)

## Installation

### Développement

```bash
# Cloner le projet
git clone <repo>
cd transcription-app

# Créer l'environnement virtuel
python -m venv venv
venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python main.py
```

### Production

```bash
# Build avec PyInstaller (développement)
python scripts/build.py --dev

# Build avec Nuitka (release, ~30 min)
python scripts/build.py --release

# Créer l'installeur Windows
# Ouvrir scripts/installer.iss avec Inno Setup et compiler
```

## Configuration

Éditer `config.yaml` pour ajuster :

- Modèle de transcription (tiny → large-v3)
- Mode diarization (quality vs fast)
- Langue par défaut
- Chemins des dossiers

## Performances attendues

| Métrique | Valeur |
|----------|--------|
| Transcription seule | ~1x temps réel |
| Avec diarization (quality) | ~3-4x temps réel |
| Avec diarization (fast) | ~1.5x temps réel |
| RAM utilisée | 6-8 Go |

## Structure du projet

```
transcription-app/
├── main.py                 # Point d'entrée
├── config.yaml             # Configuration
├── requirements.txt        # Dépendances Python
├── src/
│   ├── core/
│   │   ├── transcriber.py  # faster-whisper wrapper
│   │   ├── diarizer.py     # Pyannote/SpeechBrain
│   │   └── audio_processor.py
│   ├── ui/
│   │   ├── main_window.py  # Interface PySide6
│   │   └── workers.py      # QThread workers
│   └── utils/
│       ├── config.py       # Gestion configuration
│       └── model_manager.py
├── models/                  # Modèles ML (téléchargés)
├── scripts/
│   ├── build.py            # Script de build
│   └── installer.iss       # Inno Setup
└── tests/
```

## Stack technique

| Composant | Technologie | Justification |
|-----------|-------------|---------------|
| Transcription | faster-whisper | 4x plus rapide que Whisper original, optimisé CPU |
| Diarization | Pyannote 3.1 | Meilleure précision (DER 11%), gère le chevauchement |
| UI | PySide6 | LGPL, threading natif Qt, support LTS |
| Packaging | Nuitka | Protection du code source, performances optimisées |

## Licence

MIT

## Notes RGPD

Cette application fonctionne entièrement en local. Aucune donnée audio n'est transmise à des serveurs externes. Les modèles ML sont exécutés localement sur la machine de l'utilisateur.
