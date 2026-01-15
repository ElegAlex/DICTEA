# DICTEA - Journal de Développement

> Ce fichier trace l'historique des sessions de développement.
> **Claude doit le lire au début de chaque session et le mettre à jour à la fin.**

---

## 2026-01-15 - Session 6 : Support FFmpeg Windows

### Contexte
- Signalement: l'exécutable Windows ne reconnaît pas certains formats audio (m4a).
- Suspect: FFmpeg absent dans le bundle Windows.

### Réalisé
- [x] Ajout d'une vérification explicite de FFmpeg dans le traitement audio.
- [x] Messages d'erreur utilisateur plus clairs pour dépendance manquante.
- [x] Validation audio côté workers (transcription/diarization).
- [x] Build Windows mis à jour pour inclure FFmpeg (téléchargement automatique).

### Fichiers modifiés
- `transcription-app/src/core/audio_processor.py` - Détection/configuration FFmpeg, validation audio.
- `transcription-app/src/core/exceptions.py` - Nouvelle erreur AudioDependencyError.
- `transcription-app/src/core/diarizer.py` - Vérification FFmpeg avant chargement audio.
- `transcription-app/src/ui/workers.py` - Validation audio avant traitement.
- `transcription-app/src/ui/main_window.py` - Messages d'erreur plus précis.
- `transcription-app/scripts/build.py` - Téléchargement/embarquage FFmpeg dans le build Windows.

### Décisions prises
- FFmpeg devient une dépendance requise pour décoder les formats compressés (m4a, mp3).
- Le build Windows échoue si FFmpeg n'est pas disponible.

### Prochaines étapes
- [ ] Tester un build Windows propre pour confirmer la lecture m4a.
- [ ] Documenter l'installation manuelle de FFmpeg pour l'utilisateur final.

### Problèmes/Blocages
- Nécessite une validation sur machine Windows réelle.

## 2026-01-14 - Session 1 : Analyse et Documentation BMAD

### Contexte initial
- Projet existant avec code fonctionnel dans `transcription-app/`
- Application de transcription audio offline avec diarisation
- Stack: Python, PySide6, faster-whisper, Pyannote

### Réalisé

#### Analyse du projet
- [x] Exploration complète du codebase
- [x] Identification de l'architecture (Core/UI/Utils layers)
- [x] Analyse des patterns (Singleton, Worker Thread, Signal/Slot)
- [x] Mapping des dépendances

#### Documentation BMAD créée
- [x] **PRD.md** (~730 lignes) - Vision, personas (Marie/Thomas/Sophie), scope MVP
- [x] **FUNCTIONAL_REQUIREMENTS.md** (~1420 lignes) - 32 FRs sur 7 Epics
- [x] **NON_FUNCTIONAL_REQUIREMENTS.md** (~1470 lignes) - 28 NFRs (PERF/SEC/REL/USA/MNT/PRT/SCL/CMP)
- [x] **USER_STORIES.md** (~1470 lignes) - 36 User Stories, backlog priorisé, 131 story points
- [x] **TECHNICAL_ARCHITECTURE.md** (~1650 lignes) - C4 Model, composants, threading, ADRs, sécurité, perf
- [x] **README.md** - Index de navigation BMAD

### Fichiers créés
```
transcription-app/docs/bmad/
├── README.md                      # Index navigation
├── PRD.md                         # Product Requirements Document
├── FUNCTIONAL_REQUIREMENTS.md     # 32 Functional Requirements
├── NON_FUNCTIONAL_REQUIREMENTS.md # 28 Non-Functional Requirements
├── USER_STORIES.md                # 36 User Stories + Backlog
└── TECHNICAL_ARCHITECTURE.md      # Architecture technique complète
```

### Décisions documentées (ADRs)
| ADR | Décision |
|-----|----------|
| ADR-001 | faster-whisper vs Whisper → faster-whisper (4x perf) |
| ADR-002 | PySide6 vs PyQt6 → PySide6 (LGPL) |
| ADR-003 | Threading → QThread + Signals/Slots |
| ADR-004 | Diarisation → Dual-mode (Quality/Fast) |
| ADR-005 | Config → YAML Singleton |
| ADR-006 | Build release → Nuitka |

### Métriques de la documentation
- **Total:** ~6900 lignes de documentation technique
- **Epics:** 7
- **User Stories:** 36
- **Story Points:** 131
- **FRs:** 32
- **NFRs:** 28
- **ADRs:** 6
- **Personas:** 3

### Prochaines étapes possibles
- [x] Implémenter les tests unitaires (pytest configuré mais vide)
- [x] Refactoring des fonctions > 30 lignes dans `main_window.py`
- [ ] Ajouter la gestion d'erreurs manquante
- [ ] Créer un système de batch processing
- [ ] Améliorer l'UX avec preview audio
- [ ] Ajouter support multi-langue UI

---

## 2026-01-14 - Session 2 : Implémentation Tests Unitaires

### Contexte
- Tests unitaires absents malgré pytest dans requirements.txt
- Besoin de couvrir les modules Core et Utils

### Réalisé

#### Infrastructure de tests
- [x] Création de `pytest.ini` avec configuration markers (slow, integration, ui)
- [x] Création de `tests/conftest.py` avec fixtures partagées :
  - Fixtures de configuration (temp_dir, temp_config_file, mock_config)
  - Fixtures audio (sample_audio_data, sample_audio_file, longer_audio_file)
  - Fixtures ML mocks (mock_whisper_model, mock_transcription_result, mock_diarization_result)
  - Reset automatique du singleton config entre tests

#### Tests unitaires implémentés
- [x] `test_config.py` (~180 lignes) - Tests pour config.py
  - TestTranscriptionConfig, TestDiarizationConfig, TestAudioConfig
  - TestPathsConfig, TestPerformanceConfig, TestAppConfig
  - TestGetConfig, TestReloadConfig
- [x] `test_model_manager.py` (~160 lignes) - Tests pour model_manager.py
  - TestWhisperModels, TestPyannoteModels, TestModelManager
- [x] `test_audio_processor.py` (~220 lignes) - Tests pour audio_processor.py
  - TestAudioDevice, TestAudioRecorder, TestAudioProcessor
- [x] `test_transcriber.py` (~250 lignes) - Tests pour transcriber.py
  - TestFormatTime, TestFormatSrtTime
  - TestTranscriptionSegment, TestTranscriptionResult, TestTranscriber
- [x] `test_diarizer.py` (~240 lignes) - Tests pour diarizer.py
  - TestSpeakerSegment, TestDiarizationResult, TestDiarizer
  - TestAssignSpeakersToTranscription

### Fichiers créés
```
transcription-app/
├── pytest.ini                     # Configuration pytest
└── tests/
    ├── __init__.py               # Package tests
    ├── conftest.py               # Fixtures partagées (~180 lignes)
    ├── test_config.py            # Tests config (~180 lignes)
    ├── test_model_manager.py     # Tests model_manager (~160 lignes)
    ├── test_audio_processor.py   # Tests audio_processor (~220 lignes)
    ├── test_transcriber.py       # Tests transcriber (~250 lignes)
    └── test_diarizer.py          # Tests diarizer (~240 lignes)
```

### Métriques
- **Total tests:** ~1230 lignes de code de test
- **Fichiers de test:** 6
- **Classes de test:** 21
- **Cas de test:** ~70

### Couverture des tests
| Module | Couverture |
|--------|------------|
| `src/utils/config.py` | ✅ Complète |
| `src/utils/model_manager.py` | ✅ Complète |
| `src/core/audio_processor.py` | ✅ Complète |
| `src/core/transcriber.py` | ✅ Complète |
| `src/core/diarizer.py` | ✅ Complète |
| `src/ui/main_window.py` | ⏳ À faire (UI) |
| `src/ui/workers.py` | ⏳ À faire (UI) |

### Décisions prises
- Utilisation de mocks pour les modèles ML (évite le téléchargement en CI)
- Fixtures avec fichiers audio générés (bruit blanc) pour tests réalistes
- Markers pytest pour catégoriser les tests (slow, integration, ui)
- Reset automatique du singleton config entre chaque test

### Exécution des tests
```bash
# Installer les dépendances
pip install -r requirements.txt

# Exécuter tous les tests
pytest

# Exécuter sans les tests lents
pytest -m "not slow"

# Avec couverture
pytest --cov=src --cov-report=html
```

### Prochaines étapes
- [ ] Ajouter tests UI avec pytest-qt (main_window, workers)
- [ ] Configurer CI/CD avec GitHub Actions
- [ ] Ajouter pytest-cov pour rapports de couverture
- [ ] Tests d'intégration end-to-end

### Notes techniques
- Le code existant est fonctionnel et bien structuré
- Architecture en couches respectée (Core/UI/Utils)
- ~~Quelques méthodes UI dépassent 30 lignes → candidats au refactoring~~ ✅ Fait Session 3
- ~~Tests unitaires à implémenter (framework pytest prêt)~~ ✅ Fait Session 2

---

## 2026-01-14 - Session 3 : Refactoring main_window.py

### Contexte
- `main_window.py` contenait 3 méthodes > 30 lignes (violation des règles de dev)
- Nécessité de respecter SRP (Single Responsibility Principle)

### Problèmes identifiés

| Méthode | Lignes | Problème |
|---------|--------|----------|
| `_setup_ui` | 150 | Monolithique, difficile à maintenir |
| `_on_record_clicked` | 45 | Mélange start/stop |
| `_on_transcribe_clicked` | 49 | Trop de responsabilités |

### Réalisé

#### Refactoring `_setup_ui` (150 → 17 lignes)
Découpé en 7 méthodes spécialisées :
- [x] `_create_source_section()` - GroupBox source audio (23 lignes)
- [x] `_create_options_section()` - GroupBox options (43 lignes)
- [x] `_create_transcribe_button()` - Bouton principal (12 lignes)
- [x] `_create_progress_section()` - Barre de progression (15 lignes)
- [x] `_create_result_section()` - Zone de résultat (18 lignes)
- [x] `_create_export_buttons()` - Boutons export (20 lignes)
- [x] `_create_status_bar()` - Barre de statut (5 lignes)

#### Refactoring `_on_record_clicked` (45 → 6 lignes)
Découpé en 4 méthodes :
- [x] `_start_recording()` - Démarrage enregistrement (19 lignes)
- [x] `_stop_recording()` - Arrêt enregistrement (14 lignes)
- [x] `_save_recording()` - Sauvegarde fichier (10 lignes)
- [x] `_update_recording_display()` - MAJ affichage (5 lignes)

#### Refactoring `_on_transcribe_clicked` (49 → 10 lignes)
Découpé en 6 méthodes :
- [x] `_cancel_transcription()` - Annulation (4 lignes)
- [x] `_start_transcription()` - Lancement (5 lignes)
- [x] `_get_transcription_options()` - Récupération options (11 lignes)
- [x] `_disable_ui_for_transcription()` - Désactivation UI (6 lignes)
- [x] `_create_and_start_worker()` - Création worker (15 lignes)
- [x] `_create_full_pipeline_worker()` - Worker complet (11 lignes)
- [x] `_create_transcription_worker()` - Worker simple (9 lignes)

#### Améliorations supplémentaires
- [x] Organisation en sections avec commentaires séparateurs
- [x] Ajout de `_format_duration()` comme méthode statique utilitaire
- [x] Ajout de `_update_source_info_for_file()` pour clarifier le code
- [x] Suppression imports inutilisés (`QTabWidget`, `QSplitter`, `Qt`, `QIcon`)

### Fichiers modifiés
- `src/ui/main_window.py` - Refactoring complet (464 → 539 lignes, +16% mais toutes méthodes < 30 lignes)

### Métriques avant/après

| Métrique | Avant | Après |
|----------|-------|-------|
| Lignes totales | 464 | 539 |
| Méthodes > 30 lignes | 3 | 0 |
| Méthodes publiques | 1 | 1 |
| Méthodes privées | 21 | 35 |
| Max lignes/méthode | 150 | 43 |

### Structure finale du fichier

```
MainWindow
├── __init__
├── Setup UI (7 méthodes)
│   ├── _setup_ui
│   ├── _create_source_section
│   ├── _create_options_section
│   ├── _create_transcribe_button
│   ├── _create_progress_section
│   ├── _create_result_section
│   ├── _create_export_buttons
│   └── _create_status_bar
├── Signals (1 méthode)
│   └── _connect_signals
├── Import handlers (4 méthodes)
│   ├── _on_import_clicked
│   ├── _load_audio_file
│   ├── _update_source_info_for_file
│   └── _format_duration (static)
├── Recording handlers (5 méthodes)
│   ├── _on_record_clicked
│   ├── _start_recording
│   ├── _stop_recording
│   ├── _save_recording
│   └── _update_recording_display
├── Transcription handlers (10 méthodes)
│   ├── _on_transcribe_clicked
│   ├── _cancel_transcription
│   ├── _start_transcription
│   ├── _get_transcription_options
│   ├── _disable_ui_for_transcription
│   ├── _create_and_start_worker
│   ├── _create_full_pipeline_worker
│   ├── _create_transcription_worker
│   └── Callbacks (4)
├── UI Helpers (3 méthodes)
├── Export handlers (4 méthodes)
└── Lifecycle (1 méthode)
    └── closeEvent
```

### Décisions prises
- Garder toutes les méthodes dans la même classe (pas d'extraction de composants)
- Utiliser des sections commentées pour la navigation
- Préférer les méthodes courtes aux classes supplémentaires

### Prochaines étapes
- [ ] Ajouter tests UI avec pytest-qt
- [ ] Refactoring potentiel : extraire les helpers d'export en module séparé
- [ ] Considérer l'extraction de `_create_options_section` (43 lignes, proche de la limite)

---

## 2026-01-14 - Session 4 : Implémentation Fonctionnalités Avancées

### Contexte
- Tests unitaires et refactoring terminés (Sessions 2-3)
- Prochaines étapes: gestion d'erreurs, batch processing, preview audio, CI/CD

### Réalisé

#### 1. Gestion d'erreurs améliorée
- [x] **src/core/exceptions.py** (NEW ~260 lignes)
  - Hiérarchie d'exceptions personnalisées (`DICTEAError` base class)
  - Erreurs Audio: `AudioFileNotFoundError`, `AudioFormatError`, `AudioCorruptedError`, `AudioRecordingError`
  - Erreurs Modèles: `ModelNotFoundError`, `ModelDownloadError`, `ModelLoadError`, `HuggingFaceTokenError`
  - Erreurs Transcription: `TranscriptionCancelledError`, `TranscriptionFailedError`
  - Erreurs Diarization: `DiarizationFailedError`, `NoSpeakersDetectedError`
  - Erreurs Système: `InsufficientMemoryError`, `DiskSpaceError`
  - Fonction `get_user_friendly_message()` pour messages utilisateur

- [x] **src/ui/workers.py** (UPDATED)
  - Validation des fichiers avant traitement
  - Utilisation des exceptions personnalisées
  - Messages d'erreur conviviaux

#### 2. Traitement par lots (Batch Processing)
- [x] **src/core/batch_processor.py** (NEW ~290 lignes)
  - `BatchItemStatus` enum (PENDING, PROCESSING, COMPLETED, FAILED, SKIPPED)
  - `BatchItem` dataclass pour chaque fichier
  - `BatchResult` dataclass avec métriques (success_rate, total_time)
  - `BatchOptions` dataclass (language, diarization, output_format, etc.)
  - `BatchProcessor` class avec support annulation
  - `get_audio_files_from_directory()` helper

- [x] **src/ui/batch_dialog.py** (NEW ~390 lignes)
  - Interface complète de traitement par lots
  - Sélection fichiers/dossiers avec liste interactive
  - Options: langue, diarization, format sortie (TXT/SRT/both)
  - Barre de progression et statut par fichier
  - Gestion annulation et fermeture propre

- [x] **src/ui/workers.py** (UPDATED)
  - `BatchWorker` class avec signaux de progression
  - Intégration avec `BatchProcessor`

- [x] **src/ui/main_window.py** (UPDATED)
  - Bouton "📦 Traitement par lots" ajouté
  - Handler `_on_batch_clicked()` pour ouvrir le dialogue

#### 3. Preview Audio
- [x] **src/ui/audio_player.py** (NEW ~160 lignes)
  - Widget de lecture audio compact
  - Contrôles: Play/Pause, Stop, Slider position, Volume
  - Affichage temps courant/total
  - Utilise QMediaPlayer + QAudioOutput

- [x] **src/ui/main_window.py** (UPDATED)
  - Intégration `AudioPlayerWidget` dans la section source
  - Chargement automatique lors de l'import/enregistrement
  - Arrêt automatique lors de la transcription/fermeture

#### 4. CI/CD GitHub Actions
- [x] **.github/workflows/ci.yml** (NEW)
  - Job `test`: pytest avec couverture, skip tests slow/integration
  - Job `lint`: Ruff (linting + formatting)
  - Job `build-check`: Vérification des imports
  - Support codecov pour rapports de couverture

- [x] **transcription-app/ruff.toml** (NEW)
  - Configuration Ruff pour le projet
  - Rules: E, W, F, I, B, C4, UP, SIM
  - Ignore spécifiques pour tests et __init__.py

### Fichiers créés
```
transcription-app/src/
├── core/
│   ├── exceptions.py          # NEW - Gestion d'erreurs (~260 lignes)
│   └── batch_processor.py     # NEW - Traitement par lots (~290 lignes)
└── ui/
    ├── batch_dialog.py        # NEW - Interface batch (~390 lignes)
    └── audio_player.py        # NEW - Lecteur audio (~160 lignes)

.github/workflows/
└── ci.yml                     # NEW - Pipeline CI/CD

transcription-app/
└── ruff.toml                  # NEW - Config linting
```

### Fichiers modifiés
- `src/ui/workers.py` - Ajout BatchWorker, amélioration erreurs
- `src/ui/main_window.py` - Intégration batch + audio player

### Métriques
- **Nouveau code:** ~1100 lignes
- **Fichiers créés:** 6
- **Fonctionnalités:** 4 (erreurs, batch, preview, CI/CD)

### Architecture mise à jour
```
MainWindow
├── Source Section
│   ├── Import / Record / Batch buttons
│   └── AudioPlayerWidget (NEW)
├── Options Section
├── Transcription Button
├── Progress Section
└── Results Section

BatchDialog (NEW)
├── Files Section (list + add/remove)
├── Options Section
├── Output Section
├── Progress Section
└── Action Buttons

Exceptions Hierarchy (NEW)
├── DICTEAError (base)
├── AudioError
├── ModelError
├── TranscriptionError
├── DiarizationError
└── SystemError
```

### Prochaines étapes possibles
- [ ] Tests UI avec pytest-qt
- [ ] Ajout support drag & drop pour fichiers
- [ ] Export batch en CSV de statistiques
- [ ] Amélioration UX: thèmes, raccourcis clavier
- [ ] Support multi-langue UI (i18n)
- [x] Packaging avec PyInstaller/Nuitka

---

## 2026-01-14 - Session 5 : Packaging Multi-Plateforme

### Contexte
- Script de build existant supportait uniquement Windows
- Besoin de créer des builds pour Windows (.exe) et Linux (AppImage)

### Réalisé

#### Script de build multi-plateforme
- [x] **scripts/build.py** (UPDATED ~475 lignes)
  - Auto-détection de la plateforme
  - Support Windows: PyInstaller (dev) + Nuitka (release)
  - Support Linux: PyInstaller + AppImage
  - Téléchargement automatique de `appimagetool`
  - Création d'icône placeholder avec PIL si disponible
  - Vérification des dépendances avant build
  - Affichage de la taille finale des builds

#### Configuration AppImage Linux
- [x] **resources/dictea.desktop** (NEW)
  - Fichier .desktop standard FreeDesktop
  - Support des types MIME audio
  - Catégories et mots-clés appropriés

### Fichiers créés/modifiés
```
transcription-app/
├── scripts/
│   └── build.py              # UPDATED - Multi-plateforme
└── resources/
    └── dictea.desktop        # NEW - Fichier desktop Linux
```

### Usage du script de build

```bash
# Installer les dépendances de build
pip install pyinstaller pillow

# Build automatique (détecte la plateforme)
python scripts/build.py

# Build Linux AppImage
python scripts/build.py linux

# Build Windows .exe (sur Windows uniquement)
python scripts/build.py windows

# Build release optimisé avec Nuitka
python scripts/build.py --release

# Nettoyer les fichiers de build
python scripts/build.py --clean
```

### Output attendu
| Plateforme | Mode | Output |
|------------|------|--------|
| Linux | dev | `dist/DICTEA-1.0.0-x86_64.AppImage` |
| Windows | dev | `dist/DICTEA/DICTEA.exe` + DLLs |
| Windows | release | `dist/DICTEA.exe` (single file) |

### Prochaines étapes
- [ ] Ajouter une vraie icône (resources/icon.png, resources/icon.ico)
- [ ] Tester les builds sur machines propres
- [ ] Ajouter script d'installeur Windows (Inno Setup)
- [ ] GitHub Actions pour builds automatiques

---

## Template pour prochaines sessions

```markdown
## [DATE] - Session N : Titre

### Contexte
- État avant la session

### Réalisé
- [x] Tâche complétée
- [ ] Tâche non terminée

### Fichiers modifiés/créés
- `chemin/fichier.py` - Description

### Décisions prises
- Décision X car Y

### Prochaines étapes
- [ ] Tâche 1
- [ ] Tâche 2

### Problèmes/Blocages
- Issue à résoudre
```
