# DICTEA - Functional Requirements (FRs)

**Version:** 1.0.0
**Date:** 2026-01-14
**Référence PRD:** [PRD.md](./PRD.md)
**Méthodologie:** BMAD (Breakthrough Method for Agile AI-Driven Development)

---

## Table des matières

1. [Introduction](#1-introduction)
2. [Convention de Notation](#2-convention-de-notation)
3. [Epic 1: Gestion Audio (E1)](#3-epic-1-gestion-audio-e1)
4. [Epic 2: Transcription (E2)](#4-epic-2-transcription-e2)
5. [Epic 3: Diarisation (E3)](#5-epic-3-diarisation-e3)
6. [Epic 4: Export (E4)](#6-epic-4-export-e4)
7. [Epic 5: Interface Utilisateur (E5)](#7-epic-5-interface-utilisateur-e5)
8. [Epic 6: Configuration (E6)](#8-epic-6-configuration-e6)
9. [Epic 7: Gestion des Modèles (E7)](#9-epic-7-gestion-des-modèles-e7)
10. [Matrice de Traçabilité](#10-matrice-de-traçabilité)

---

## 1. Introduction

### 1.1 Objectif du Document

Ce document définit l'ensemble des exigences fonctionnelles (Functional Requirements - FRs) de l'application DICTEA. Chaque FR décrit un comportement observable du système du point de vue de l'utilisateur.

### 1.2 Audience

- Équipe de développement
- Product Owner
- QA / Testeurs
- Parties prenantes techniques

### 1.3 Documents Connexes

| Document | Description |
|----------|-------------|
| [PRD.md](./PRD.md) | Product Requirements Document - Vision et contexte |
| [NON_FUNCTIONAL_REQUIREMENTS.md](./NON_FUNCTIONAL_REQUIREMENTS.md) | Exigences non-fonctionnelles |
| [USER_STORIES.md](./USER_STORIES.md) | User Stories détaillées |

---

## 2. Convention de Notation

### 2.1 Format des Requirements

```
FR-[EPIC].[NUMERO]
│    │      │
│    │      └── Numéro séquentiel dans l'epic
│    └── Numéro de l'epic (1-7)
└── Functional Requirement
```

### 2.2 Niveaux de Priorité

| Priorité | Code | Description |
|----------|------|-------------|
| **Critical** | P0 | Indispensable au MVP, bloquant si absent |
| **High** | P1 | Important, dégradation significative si absent |
| **Medium** | P2 | Souhaitable, améliore l'expérience |
| **Low** | P3 | Nice-to-have, peut être reporté |

### 2.3 Mots-clés RFC 2119

| Mot-clé | Signification |
|---------|---------------|
| **DOIT** (MUST) | Exigence absolue, obligatoire |
| **DEVRAIT** (SHOULD) | Recommandé, sauf justification contraire |
| **PEUT** (MAY) | Optionnel, à la discrétion de l'implémentation |
| **NE DOIT PAS** (MUST NOT) | Interdiction absolue |

---

## 3. Epic 1: Gestion Audio (E1)

### 3.1 Vue d'ensemble

L'Epic Gestion Audio couvre toutes les fonctionnalités liées à l'acquisition, l'import et le prétraitement des données audio avant transcription.

```
┌─────────────────────────────────────────────────────────────────┐
│                     FLUX GESTION AUDIO                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐        ┌──────────────┐                     │
│   │  IMPORT      │        │ ENREGISTREMENT│                    │
│   │  FICHIER     │        │  MICROPHONE   │                    │
│   └──────┬───────┘        └──────┬────────┘                    │
│          │                       │                              │
│          └───────────┬───────────┘                              │
│                      ▼                                          │
│              ┌───────────────┐                                  │
│              │  VALIDATION   │                                  │
│              │  FORMAT       │                                  │
│              └───────┬───────┘                                  │
│                      ▼                                          │
│              ┌───────────────┐                                  │
│              │  CONVERSION   │                                  │
│              │  16kHz MONO   │                                  │
│              └───────┬───────┘                                  │
│                      ▼                                          │
│              ┌───────────────┐                                  │
│              │  MÉTADONNÉES  │                                  │
│              │  EXTRACTION   │                                  │
│              └───────────────┘                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### FR-1.1: Import de fichiers audio

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-1.1 |
| **Titre** | Import de fichiers audio multi-formats |
| **Priorité** | P0 - Critical |
| **Epic** | E1 - Gestion Audio |

#### Description

Le système DOIT permettre à l'utilisateur d'importer des fichiers audio depuis le système de fichiers local.

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-1.1.1 | L'utilisateur PEUT sélectionner un fichier via une boîte de dialogue système | ☐ |
| AC-1.1.2 | Les formats supportés DOIVENT inclure: WAV, MP3, M4A, FLAC, OGG, WMA, AAC | ☐ |
| AC-1.1.3 | Le filtre de la boîte de dialogue DOIT afficher uniquement les formats supportés | ☐ |
| AC-1.1.4 | Un fichier non supporté DOIT déclencher un message d'erreur explicite | ☐ |
| AC-1.1.5 | Le chemin du fichier sélectionné DOIT être affiché dans l'interface | ☐ |
| AC-1.1.6 | Les fichiers de taille > 2 Go DOIVENT être acceptés | ☐ |

#### Règles métier

- BR-1.1.1: Un seul fichier peut être chargé à la fois (pas de traitement batch dans MVP)
- BR-1.1.2: Le fichier précédemment chargé est remplacé par le nouveau
- BR-1.1.3: Les fichiers corrompus doivent être détectés avant traitement

#### Dépendances

- Aucune

#### Notes d'implémentation

```python
# Formats supportés avec extensions
SUPPORTED_FORMATS = {
    "WAV": [".wav"],
    "MP3": [".mp3"],
    "M4A": [".m4a"],
    "FLAC": [".flac"],
    "OGG": [".ogg"],
    "WMA": [".wma"],
    "AAC": [".aac"]
}

# Filtre pour QFileDialog
FILTER = "Audio Files (*.wav *.mp3 *.m4a *.flac *.ogg *.wma *.aac)"
```

---

### FR-1.2: Enregistrement microphone

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-1.2 |
| **Titre** | Enregistrement audio depuis le microphone |
| **Priorité** | P0 - Critical |
| **Epic** | E1 - Gestion Audio |

#### Description

Le système DOIT permettre à l'utilisateur d'enregistrer de l'audio directement depuis le microphone du système.

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-1.2.1 | Un bouton "Enregistrer" DOIT démarrer la capture audio | ☐ |
| AC-1.2.2 | Un bouton "Arrêter" DOIT stopper l'enregistrement | ☐ |
| AC-1.2.3 | La durée d'enregistrement DOIT être affichée en temps réel (MM:SS) | ☐ |
| AC-1.2.4 | Un indicateur visuel DOIT signaler que l'enregistrement est actif | ☐ |
| AC-1.2.5 | L'enregistrement DOIT utiliser le périphérique audio par défaut du système | ☐ |
| AC-1.2.6 | L'enregistrement DOIT être sauvegardé automatiquement en WAV | ☐ |
| AC-1.2.7 | L'utilisateur DOIT pouvoir choisir d'annuler après arrêt | ☐ |

#### Règles métier

- BR-1.2.1: L'enregistrement est au format 16 kHz, mono, 16-bit PCM
- BR-1.2.2: Durée maximale d'enregistrement: 4 heures
- BR-1.2.3: Les fichiers sont nommés automatiquement avec timestamp

#### Spécifications techniques

| Paramètre | Valeur |
|-----------|--------|
| Sample Rate | 16000 Hz |
| Channels | 1 (Mono) |
| Bit Depth | 16-bit |
| Format | PCM WAV |
| Buffer Size | 1024 samples |

#### États de l'enregistreur

```
┌─────────────────────────────────────────────────────────────────┐
│                    MACHINE À ÉTATS                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│     ┌───────┐    Start    ┌────────────┐    Stop    ┌───────┐ │
│     │ IDLE  │ ──────────▶ │ RECORDING  │ ─────────▶ │ DONE  │ │
│     └───────┘             └────────────┘            └───────┘ │
│         ▲                                               │      │
│         │                    Cancel                     │      │
│         └───────────────────────────────────────────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### FR-1.3: Conversion format audio

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-1.3 |
| **Titre** | Conversion automatique au format Whisper |
| **Priorité** | P0 - Critical |
| **Epic** | E1 - Gestion Audio |

#### Description

Le système DOIT convertir automatiquement tout fichier audio importé au format optimal pour Whisper (16 kHz, mono, PCM).

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-1.3.1 | Tout audio importé DOIT être converti en 16 kHz | ☐ |
| AC-1.3.2 | Les fichiers stéréo DOIVENT être convertis en mono | ☐ |
| AC-1.3.3 | La conversion DOIT préserver la qualité audio originale | ☐ |
| AC-1.3.4 | Les fichiers compressés (MP3, AAC) DOIVENT être décodés en PCM | ☐ |
| AC-1.3.5 | La conversion NE DOIT PAS modifier le fichier source | ☐ |
| AC-1.3.6 | Un fichier temporaire converti DOIT être créé si nécessaire | ☐ |

#### Règles métier

- BR-1.3.1: Si le fichier est déjà au bon format, aucune conversion n'est effectuée
- BR-1.3.2: Les fichiers temporaires sont supprimés après traitement

---

### FR-1.4: Affichage métadonnées audio

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-1.4 |
| **Titre** | Extraction et affichage des métadonnées |
| **Priorité** | P1 - High |
| **Epic** | E1 - Gestion Audio |

#### Description

Le système DOIT extraire et afficher les métadonnées du fichier audio chargé.

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-1.4.1 | La durée DOIT être affichée au format HH:MM:SS | ☐ |
| AC-1.4.2 | Le format du fichier DOIT être affiché | ☐ |
| AC-1.4.3 | La taille du fichier DOIT être affichée (Mo/Go) | ☐ |
| AC-1.4.4 | Le sample rate original DOIT être affiché | ☐ |
| AC-1.4.5 | Le nombre de canaux DOIT être indiqué (mono/stéréo) | ☐ |

#### Données extraites

```
┌─────────────────────────────────────────────────────────────────┐
│                    MÉTADONNÉES AUDIO                            │
├─────────────────────────────────────────────────────────────────┤
│  Fichier:      interview_2026-01-14.mp3                        │
│  Durée:        01:23:45                                        │
│  Format:       MP3 (320 kbps)                                  │
│  Taille:       187.5 Mo                                        │
│  Sample Rate:  44100 Hz → 16000 Hz (converti)                  │
│  Canaux:       Stéréo → Mono (converti)                        │
└─────────────────────────────────────────────────────────────────┘
```

---

### FR-1.5: Découpage fichiers longs

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-1.5 |
| **Titre** | Segmentation automatique des fichiers volumineux |
| **Priorité** | P2 - Medium |
| **Epic** | E1 - Gestion Audio |

#### Description

Le système DEVRAIT découper automatiquement les fichiers audio longs en segments pour optimiser l'utilisation mémoire.

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-1.5.1 | Les fichiers > 30 minutes DEVRAIENT être découpés | ☐ |
| AC-1.5.2 | La taille des chunks DEVRAIT être configurable | ☐ |
| AC-1.5.3 | Les résultats DOIVENT être fusionnés de manière transparente | ☐ |
| AC-1.5.4 | Le découpage NE DOIT PAS couper au milieu d'une phrase | ☐ |

#### Paramètres

| Paramètre | Valeur par défaut | Configurable |
|-----------|-------------------|--------------|
| chunk_size_minutes | 10 | Oui |
| overlap_seconds | 2 | Oui |

---

## 4. Epic 2: Transcription (E2)

### 4.1 Vue d'ensemble

L'Epic Transcription couvre le processus de conversion de l'audio en texte via le modèle ASR faster-whisper.

```
┌─────────────────────────────────────────────────────────────────┐
│                    PIPELINE TRANSCRIPTION                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐                                             │
│   │ AUDIO INPUT  │                                             │
│   └──────┬───────┘                                             │
│          │                                                      │
│          ▼                                                      │
│   ┌──────────────┐     ┌──────────────┐                        │
│   │ LOAD MODEL   │────▶│  VAD FILTER  │  (optionnel)           │
│   │ (lazy load)  │     │  (silence)   │                        │
│   └──────────────┘     └──────┬───────┘                        │
│                               │                                 │
│                               ▼                                 │
│                        ┌──────────────┐                        │
│                        │  INFERENCE   │                        │
│                        │  (segments)  │                        │
│                        └──────┬───────┘                        │
│                               │                                 │
│                               ▼                                 │
│   ┌──────────────────────────────────────────────────────────┐│
│   │  SEGMENT {                                                ││
│   │    start: float,    // timestamp début (secondes)        ││
│   │    end: float,      // timestamp fin (secondes)          ││
│   │    text: str,       // texte transcrit                   ││
│   │    confidence: float // score confiance [0-1]            ││
│   │  }                                                        ││
│   └──────────────────────────────────────────────────────────┘│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### FR-2.1: Transcription speech-to-text

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-2.1 |
| **Titre** | Transcription audio vers texte |
| **Priorité** | P0 - Critical |
| **Epic** | E2 - Transcription |

#### Description

Le système DOIT transcrire l'audio en texte avec une qualité professionnelle (WER < 10% sur le français).

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-2.1.1 | L'audio chargé DOIT être transcrit en texte français | ☐ |
| AC-2.1.2 | La transcription DOIT atteindre un WER ≤ 10% sur corpus test | ☐ |
| AC-2.1.3 | La ponctuation DOIT être générée automatiquement | ☐ |
| AC-2.1.4 | Les chiffres DOIVENT être transcrits correctement | ☐ |
| AC-2.1.5 | Les noms propres courants DOIVENT être reconnus | ☐ |
| AC-2.1.6 | Le traitement DOIT fonctionner 100% offline | ☐ |

#### Paramètres du modèle

| Paramètre | Valeur | Description |
|-----------|--------|-------------|
| model | "medium" | Modèle faster-whisper |
| compute_type | "int8" | Quantification CPU |
| beam_size | 5 | Largeur de recherche |
| language | "fr" | Langue cible |
| vad_filter | true | Filtrage silence |

#### Benchmarks attendus

| Métrique | Cible | Dataset |
|----------|-------|---------|
| WER (français) | ≤ 8% | Common Voice FR |
| WER (vocabulaire technique) | ≤ 15% | Custom corpus |
| Latence par segment | ≤ 100ms | - |

---

### FR-2.2: Timestamps par segment

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-2.2 |
| **Titre** | Génération des timestamps |
| **Priorité** | P0 - Critical |
| **Epic** | E2 - Transcription |

#### Description

Le système DOIT associer des timestamps précis (début, fin) à chaque segment de transcription.

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-2.2.1 | Chaque segment DOIT avoir un timestamp de début | ☐ |
| AC-2.2.2 | Chaque segment DOIT avoir un timestamp de fin | ☐ |
| AC-2.2.3 | La précision des timestamps DOIT être ≤ 200ms | ☐ |
| AC-2.2.4 | Les timestamps DOIVENT être au format secondes (float) | ☐ |
| AC-2.2.5 | L'affichage DOIT convertir en format HH:MM:SS,mmm | ☐ |

#### Format de sortie

```python
@dataclass
class TranscriptionSegment:
    start: float      # 12.340 (secondes)
    end: float        # 15.670 (secondes)
    text: str         # "Bonjour, comment allez-vous ?"
    confidence: float # 0.95

    def format_timestamp(self, seconds: float) -> str:
        """Convertit secondes en HH:MM:SS,mmm"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
```

---

### FR-2.3: Progression temps réel

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-2.3 |
| **Titre** | Affichage progression transcription |
| **Priorité** | P0 - Critical |
| **Epic** | E2 - Transcription |

#### Description

Le système DOIT afficher la progression de la transcription en temps réel.

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-2.3.1 | Une barre de progression DOIT indiquer l'avancement (0-100%) | ☐ |
| AC-2.3.2 | Le temps écoulé DOIT être affiché | ☐ |
| AC-2.3.3 | Le temps restant estimé DOIT être affiché | ☐ |
| AC-2.3.4 | L'étape courante DOIT être décrite textuellement | ☐ |
| AC-2.3.5 | Les segments transcrits DEVRAIENT s'afficher progressivement | ☐ |

#### Informations affichées

```
┌─────────────────────────────────────────────────────────────────┐
│                    PROGRESSION                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [████████████████████░░░░░░░░░░░░░░░░░░░░]  45%               │
│                                                                 │
│  Étape:           Transcription en cours...                    │
│  Temps écoulé:    00:12:34                                     │
│  Temps restant:   ~00:15:00                                    │
│  Segment actuel:  145 / 320                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### FR-2.4: Annulation transcription

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-2.4 |
| **Titre** | Annulation du traitement |
| **Priorité** | P0 - Critical |
| **Epic** | E2 - Transcription |

#### Description

Le système DOIT permettre à l'utilisateur d'annuler une transcription en cours.

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-2.4.1 | Un bouton "Annuler" DOIT être visible pendant le traitement | ☐ |
| AC-2.4.2 | L'annulation DOIT stopper le traitement en ≤ 5 secondes | ☐ |
| AC-2.4.3 | Les ressources DOIVENT être libérées après annulation | ☐ |
| AC-2.4.4 | L'interface DOIT revenir à l'état initial | ☐ |
| AC-2.4.5 | Un message de confirmation DOIT être affiché | ☐ |

#### Comportement

```
┌─────────────────────────────────────────────────────────────────┐
│                FLUX D'ANNULATION                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   User clicks          Worker receives       UI updates        │
│   [Annuler]    ───────▶  stop signal  ─────▶  "Annulé"        │
│       │                      │                    │            │
│       │                      ▼                    │            │
│       │               Release resources           │            │
│       │               - Unload model              │            │
│       │               - Clear buffers             │            │
│       │               - GC collect                │            │
│       │                      │                    │            │
│       └──────────────────────┴────────────────────┘            │
│                              │                                  │
│                              ▼                                  │
│                      État: IDLE                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### FR-2.5: Détection automatique langue

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-2.5 |
| **Titre** | Détection automatique de la langue |
| **Priorité** | P2 - Medium |
| **Epic** | E2 - Transcription |

#### Description

Le système DEVRAIT détecter automatiquement la langue de l'audio si non spécifiée par l'utilisateur.

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-2.5.1 | La langue DEVRAIT être détectée sur les 30 premières secondes | ☐ |
| AC-2.5.2 | Le score de confiance DEVRAIT être affiché | ☐ |
| AC-2.5.3 | L'utilisateur DEVRAIT pouvoir corriger la détection | ☐ |
| AC-2.5.4 | Le français DOIT être détecté avec > 95% de précision | ☐ |

---

## 5. Epic 3: Diarisation (E3)

### 5.1 Vue d'ensemble

L'Epic Diarisation couvre l'identification et l'attribution des segments de parole aux différents locuteurs.

```
┌─────────────────────────────────────────────────────────────────┐
│                    PIPELINE DIARISATION                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐                                             │
│   │ AUDIO INPUT  │                                             │
│   └──────┬───────┘                                             │
│          │                                                      │
│          ▼                                                      │
│   ┌──────────────┐     ┌──────────────┐                        │
│   │ EMBEDDING    │────▶│  CLUSTERING  │                        │
│   │ EXTRACTION   │     │  SPEAKERS    │                        │
│   └──────────────┘     └──────┬───────┘                        │
│                               │                                 │
│                               ▼                                 │
│                        ┌──────────────┐                        │
│                        │  TIMELINE    │                        │
│                        │  GENERATION  │                        │
│                        └──────┬───────┘                        │
│                               │                                 │
│   ┌──────────────────────────────────────────────────────────┐│
│   │  DIARIZATION_SEGMENT {                                    ││
│   │    start: float,       // début du segment               ││
│   │    end: float,         // fin du segment                 ││
│   │    speaker: str,       // "SPEAKER_00"                   ││
│   │  }                                                        ││
│   └──────────────────────────────────────────────────────────┘│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### FR-3.1: Identification des locuteurs

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-3.1 |
| **Titre** | Détection et différenciation des locuteurs |
| **Priorité** | P0 - Critical |
| **Epic** | E3 - Diarisation |

#### Description

Le système DOIT identifier et différencier les différents locuteurs présents dans l'audio.

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-3.1.1 | Le système DOIT détecter entre 1 et 10 locuteurs | ☐ |
| AC-3.1.2 | Chaque locuteur DOIT recevoir un identifiant unique (SPEAKER_XX) | ☐ |
| AC-3.1.3 | Le DER (Diarization Error Rate) DOIT être ≤ 15% | ☐ |
| AC-3.1.4 | Les mêmes voix DOIVENT être regroupées sous le même ID | ☐ |
| AC-3.1.5 | Le nombre de locuteurs détectés DOIT être affiché | ☐ |

#### Modes de diarisation

| Mode | Modèle | DER attendu | Temps (1h audio) |
|------|--------|-------------|------------------|
| **Quality** | Pyannote 3.1 | ~11% | 2-3h |
| **Fast** | SpeechBrain ECAPA | ~18% | 20-30min |

---

### FR-3.2: Attribution segments-locuteurs

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-3.2 |
| **Titre** | Association transcription et locuteurs |
| **Priorité** | P0 - Critical |
| **Epic** | E3 - Diarisation |

#### Description

Le système DOIT attribuer chaque segment de transcription au locuteur correspondant.

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-3.2.1 | Chaque segment transcrit DOIT être associé à un locuteur | ☐ |
| AC-3.2.2 | L'attribution DOIT se baser sur le chevauchement temporel | ☐ |
| AC-3.2.3 | En cas d'ambiguïté, le locuteur majoritaire DOIT être choisi | ☐ |
| AC-3.2.4 | Les segments sans locuteur identifié DOIVENT être marqués "UNKNOWN" | ☐ |

#### Algorithme d'attribution

```python
def assign_speaker(transcription_segment, diarization_segments):
    """
    Attribue un locuteur à un segment de transcription
    basé sur le chevauchement temporel maximal.
    """
    max_overlap = 0
    assigned_speaker = "UNKNOWN"

    for diar_seg in diarization_segments:
        overlap = calculate_overlap(
            transcription_segment.start, transcription_segment.end,
            diar_seg.start, diar_seg.end
        )
        if overlap > max_overlap:
            max_overlap = overlap
            assigned_speaker = diar_seg.speaker

    return assigned_speaker
```

---

### FR-3.3: Modes qualité/rapide

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-3.3 |
| **Titre** | Sélection du mode de diarisation |
| **Priorité** | P1 - High |
| **Epic** | E3 - Diarisation |

#### Description

Le système DOIT proposer deux modes de diarisation: Qualité (précis) et Rapide.

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-3.3.1 | Un sélecteur DOIT permettre de choisir "Qualité" ou "Rapide" | ☐ |
| AC-3.3.2 | Le mode par défaut DOIT être "Qualité" | ☐ |
| AC-3.3.3 | Une description DOIT expliquer le compromis temps/précision | ☐ |
| AC-3.3.4 | Le temps estimé DOIT être ajusté selon le mode | ☐ |

#### Comparaison des modes

```
┌─────────────────────────────────────────────────────────────────┐
│                 COMPARAISON MODES                               │
├────────────────────┬────────────────────┬───────────────────────┤
│                    │      QUALITÉ       │        RAPIDE         │
├────────────────────┼────────────────────┼───────────────────────┤
│ Modèle             │ Pyannote 3.1       │ SpeechBrain ECAPA     │
│ DER                │ ~11%               │ ~18%                  │
│ Temps (1h audio)   │ 2-3 heures         │ 20-30 minutes         │
│ RAM requise        │ ~4 Go              │ ~2 Go                 │
│ Chevauchements     │ ✓ Gérés            │ ✗ Non gérés           │
│ Recommandé pour    │ Réunions formelles │ Interviews simples    │
└────────────────────┴────────────────────┴───────────────────────┘
```

---

### FR-3.4: Nombre de locuteurs

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-3.4 |
| **Titre** | Spécification du nombre de locuteurs |
| **Priorité** | P1 - High |
| **Epic** | E3 - Diarisation |

#### Description

Le système DEVRAIT permettre à l'utilisateur de spécifier le nombre attendu de locuteurs.

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-3.4.1 | Un champ DEVRAIT permettre de saisir le nombre min de locuteurs | ☐ |
| AC-3.4.2 | Un champ DEVRAIT permettre de saisir le nombre max de locuteurs | ☐ |
| AC-3.4.3 | "Auto" (0) DOIT être la valeur par défaut | ☐ |
| AC-3.4.4 | La plage valide DOIT être 1-20 locuteurs | ☐ |

---

### FR-3.5: Gestion chevauchements

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-3.5 |
| **Titre** | Détection des paroles simultanées |
| **Priorité** | P2 - Medium |
| **Epic** | E3 - Diarisation |

#### Description

Le système DEVRAIT détecter et signaler les moments où plusieurs locuteurs parlent simultanément.

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-3.5.1 | Les chevauchements DEVRAIENT être détectés (mode Qualité) | ☐ |
| AC-3.5.2 | Les segments en chevauchement DEVRAIENT être marqués | ☐ |
| AC-3.5.3 | L'affichage DEVRAIT indiquer "[OVERLAP]" | ☐ |

---

## 6. Epic 4: Export (E4)

### 6.1 Vue d'ensemble

L'Epic Export couvre la génération des fichiers de sortie dans différents formats.

---

### FR-4.1: Export format TXT

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-4.1 |
| **Titre** | Export au format texte structuré |
| **Priorité** | P0 - Critical |
| **Epic** | E4 - Export |

#### Description

Le système DOIT permettre l'export de la transcription au format TXT avec identification des locuteurs.

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-4.1.1 | Un bouton "Sauver TXT" DOIT déclencher l'export | ☐ |
| AC-4.1.2 | Le format DOIT inclure timestamps et locuteurs | ☐ |
| AC-4.1.3 | L'encodage DOIT être UTF-8 | ☐ |
| AC-4.1.4 | Une boîte de dialogue DOIT permettre de choisir l'emplacement | ☐ |
| AC-4.1.5 | Le nom par défaut DOIT inclure le nom du fichier source | ☐ |

#### Format TXT

```
[00:00:00 - 00:00:15] SPEAKER_00
Bonjour à tous, bienvenue dans cette réunion. Nous allons
commencer par faire le point sur les ventes du mois dernier.

[00:00:15 - 00:00:45] SPEAKER_01
Merci. Effectivement, ce mois-ci nous avons atteint 120% de
nos objectifs, ce qui représente une progression significative
par rapport au trimestre précédent.

[00:00:45 - 00:01:02] SPEAKER_00
Excellent. Pouvez-vous nous détailler les secteurs les plus
performants ?
```

---

### FR-4.2: Export format SRT

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-4.2 |
| **Titre** | Export au format sous-titres SRT |
| **Priorité** | P0 - Critical |
| **Epic** | E4 - Export |

#### Description

Le système DOIT permettre l'export de la transcription au format SRT (SubRip Subtitle).

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-4.2.1 | Un bouton "Sauver SRT" DOIT déclencher l'export | ☐ |
| AC-4.2.2 | Le format DOIT respecter la spécification SRT | ☐ |
| AC-4.2.3 | Les timestamps DOIVENT être au format HH:MM:SS,mmm | ☐ |
| AC-4.2.4 | Chaque segment DOIT avoir un numéro séquentiel | ☐ |
| AC-4.2.5 | Le locuteur DOIT être indiqué au début du texte | ☐ |

#### Format SRT

```srt
1
00:00:00,000 --> 00:00:15,340
[SPEAKER_00] Bonjour à tous, bienvenue dans cette réunion.
Nous allons commencer par faire le point sur les ventes.

2
00:00:15,340 --> 00:00:45,120
[SPEAKER_01] Merci. Ce mois-ci nous avons atteint 120%
de nos objectifs.

3
00:00:45,120 --> 00:01:02,450
[SPEAKER_00] Excellent. Pouvez-vous nous détailler les
secteurs les plus performants ?
```

---

### FR-4.3: Copie presse-papiers

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-4.3 |
| **Titre** | Copie vers le presse-papiers |
| **Priorité** | P0 - Critical |
| **Epic** | E4 - Export |

#### Description

Le système DOIT permettre la copie de la transcription vers le presse-papiers système.

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-4.3.1 | Un bouton "Copier" DOIT copier le texte dans le presse-papiers | ☐ |
| AC-4.3.2 | Le format copié DOIT être identique au format TXT | ☐ |
| AC-4.3.3 | Une notification DOIT confirmer la copie | ☐ |
| AC-4.3.4 | Le raccourci Ctrl+C DEVRAIT fonctionner sur la zone de résultat | ☐ |

---

### FR-4.4: Options de formatage

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-4.4 |
| **Titre** | Personnalisation du format d'export |
| **Priorité** | P2 - Medium |
| **Epic** | E4 - Export |

#### Description

Le système DEVRAIT proposer des options de personnalisation pour l'export.

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-4.4.1 | Option: Inclure/exclure les timestamps | ☐ |
| AC-4.4.2 | Option: Inclure/exclure les identifiants locuteurs | ☐ |
| AC-4.4.3 | Option: Format timestamps (HH:MM:SS vs secondes) | ☐ |
| AC-4.4.4 | Les préférences DEVRAIENT être persistées | ☐ |

---

## 7. Epic 5: Interface Utilisateur (E5)

### 7.1 Vue d'ensemble

L'Epic Interface Utilisateur couvre tous les aspects de l'expérience utilisateur graphique.

```
┌─────────────────────────────────────────────────────────────────┐
│                    LAYOUT PRINCIPAL                             │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                      HEADER                                │ │
│  │  Logo DICTEA                              Version 1.0.0   │ │
│  └───────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────┐  ┌─────────────────────────────────┐ │
│  │   SOURCE AUDIO      │  │        OPTIONS                  │ │
│  │                     │  │                                  │ │
│  │  [Ouvrir fichier]   │  │  Langue: [FR ▼]                 │ │
│  │  [Enregistrer]      │  │  Mode:   [Qualité ▼]            │ │
│  │                     │  │  Locuteurs: [Auto ▼]            │ │
│  │  Fichier: xxx.mp3   │  │                                  │ │
│  │  Durée: 01:23:45    │  │  [  TRANSCRIRE  ]               │ │
│  └─────────────────────┘  └─────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    PROGRESSION                             │ │
│  │  [████████████████░░░░░░░░░░░░░░░░]  45%                  │ │
│  │  Transcription en cours... ~15:00 restantes               │ │
│  └───────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    RÉSULTATS                               │ │
│  │                                                            │ │
│  │  [00:00:00] SPEAKER_00                                    │ │
│  │  Bonjour à tous, bienvenue...                             │ │
│  │                                                            │ │
│  │  [00:00:15] SPEAKER_01                                    │ │
│  │  Merci, effectivement ce mois...                          │ │
│  │                                                            │ │
│  └───────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │   [Copier]    [Sauver TXT]    [Sauver SRT]                │ │
│  └───────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Status: Prêt                                              │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

### FR-5.1: Interface graphique native

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-5.1 |
| **Titre** | GUI Windows native PySide6 |
| **Priorité** | P0 - Critical |
| **Epic** | E5 - Interface Utilisateur |

#### Description

Le système DOIT fournir une interface graphique Windows native utilisant PySide6/Qt6.

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-5.1.1 | L'interface DOIT utiliser les widgets natifs Windows | ☐ |
| AC-5.1.2 | L'interface DOIT s'adapter à la résolution d'écran | ☐ |
| AC-5.1.3 | La taille minimale de fenêtre DOIT être 800x600 | ☐ |
| AC-5.1.4 | L'interface DOIT supporter le redimensionnement | ☐ |
| AC-5.1.5 | L'icône application DOIT être visible dans la barre des tâches | ☐ |

---

### FR-5.2: Barre de progression

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-5.2 |
| **Titre** | Indicateur de progression visuel |
| **Priorité** | P0 - Critical |
| **Epic** | E5 - Interface Utilisateur |

#### Description

Le système DOIT afficher une barre de progression visuelle pendant le traitement.

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-5.2.1 | La barre DOIT afficher le pourcentage (0-100%) | ☐ |
| AC-5.2.2 | Le pourcentage DOIT être mis à jour au moins toutes les 2 secondes | ☐ |
| AC-5.2.3 | L'étape courante DOIT être affichée (Transcription/Diarisation) | ☐ |
| AC-5.2.4 | Le temps restant estimé DOIT être affiché | ☐ |
| AC-5.2.5 | La barre DOIT être visible même si fenêtre minimisée (taskbar) | ☐ |

---

### FR-5.3: Interface non-bloquante

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-5.3 |
| **Titre** | Réactivité UI pendant traitement |
| **Priorité** | P0 - Critical |
| **Epic** | E5 - Interface Utilisateur |

#### Description

Le système DOIT maintenir une interface réactive pendant les opérations longues.

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-5.3.1 | L'UI NE DOIT PAS se figer pendant la transcription | ☐ |
| AC-5.3.2 | Le bouton "Annuler" DOIT rester cliquable | ☐ |
| AC-5.3.3 | La fenêtre DOIT pouvoir être déplacée/redimensionnée | ☐ |
| AC-5.3.4 | La latence d'interaction DOIT être ≤ 100ms | ☐ |

#### Architecture Threading

```
┌─────────────────────────────────────────────────────────────────┐
│                    MODÈLE THREADING                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   MAIN THREAD (UI)              WORKER THREAD                   │
│   ┌──────────────┐              ┌──────────────┐               │
│   │  Qt Event    │   signals    │  Transcriber │               │
│   │  Loop        │◀────────────▶│  Diarizer    │               │
│   │              │              │  Processing  │               │
│   │  - Buttons   │              │              │               │
│   │  - Progress  │              │  Heavy       │               │
│   │  - Results   │              │  Computation │               │
│   └──────────────┘              └──────────────┘               │
│                                                                 │
│   COMMUNICATION:                                                │
│   - progress(int)     → Update progress bar                    │
│   - segment(dict)     → Display new segment                    │
│   - finished(result)  → Show final result                      │
│   - error(str)        → Display error message                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### FR-5.4: Affichage résultats

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-5.4 |
| **Titre** | Zone d'affichage des résultats |
| **Priorité** | P0 - Critical |
| **Epic** | E5 - Interface Utilisateur |

#### Description

Le système DOIT afficher les résultats de transcription de manière lisible et structurée.

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-5.4.1 | Les résultats DOIVENT être affichés dans une zone scrollable | ☐ |
| AC-5.4.2 | Chaque segment DOIT montrer timestamp + locuteur + texte | ☐ |
| AC-5.4.3 | Les différents locuteurs DOIVENT être visuellement différenciés | ☐ |
| AC-5.4.4 | Le texte DOIT être sélectionnable | ☐ |
| AC-5.4.5 | La police DOIT être lisible (≥ 12pt) | ☐ |

---

### FR-5.5: Messages d'erreur

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-5.5 |
| **Titre** | Gestion et affichage des erreurs |
| **Priorité** | P1 - High |
| **Epic** | E5 - Interface Utilisateur |

#### Description

Le système DOIT afficher des messages d'erreur compréhensibles pour l'utilisateur.

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-5.5.1 | Les erreurs DOIVENT être affichées dans une boîte de dialogue | ☐ |
| AC-5.5.2 | Le message DOIT être en français, non-technique | ☐ |
| AC-5.5.3 | Une suggestion de résolution DEVRAIT être proposée | ☐ |
| AC-5.5.4 | Le détail technique DEVRAIT être accessible (bouton "Détails") | ☐ |
| AC-5.5.5 | L'erreur DOIT être loggée dans un fichier | ☐ |

#### Catalogue d'erreurs

| Code | Message Utilisateur | Cause |
|------|---------------------|-------|
| E001 | "Format de fichier non supporté" | Extension inconnue |
| E002 | "Fichier audio corrompu ou illisible" | Décodage impossible |
| E003 | "Mémoire insuffisante" | RAM < 8 Go disponible |
| E004 | "Microphone non détecté" | Pas de périphérique audio |
| E005 | "Modèle non trouvé" | Téléchargement requis |

---

## 8. Epic 6: Configuration (E6)

### 8.1 Vue d'ensemble

L'Epic Configuration couvre la gestion des paramètres utilisateur et système.

---

### FR-6.1: Choix modèle transcription

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-6.1 |
| **Titre** | Sélection du modèle Whisper |
| **Priorité** | P1 - High |
| **Epic** | E6 - Configuration |

#### Description

Le système DOIT permettre à l'utilisateur de choisir le modèle de transcription.

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-6.1.1 | Un sélecteur DOIT lister les modèles disponibles | ☐ |
| AC-6.1.2 | Chaque modèle DOIT afficher sa taille et qualité estimée | ☐ |
| AC-6.1.3 | Le modèle par défaut DOIT être "medium" | ☐ |
| AC-6.1.4 | Le changement de modèle DOIT être effectif immédiatement | ☐ |

#### Modèles disponibles

| Modèle | Taille | WER (FR) | RAM | Recommandation |
|--------|--------|----------|-----|----------------|
| tiny | ~75 Mo | ~15% | 2 Go | Tests rapides |
| base | ~150 Mo | ~12% | 3 Go | Qualité basique |
| small | ~500 Mo | ~10% | 4 Go | Bon compromis |
| **medium** | ~1.5 Go | ~8% | 6 Go | **Recommandé** |
| large-v3 | ~3 Go | ~6% | 10 Go | Qualité maximale |

---

### FR-6.2: Choix langue

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-6.2 |
| **Titre** | Sélection de la langue cible |
| **Priorité** | P1 - High |
| **Epic** | E6 - Configuration |

#### Description

Le système DOIT permettre à l'utilisateur de spécifier la langue de l'audio.

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-6.2.1 | Un sélecteur DOIT proposer les langues supportées | ☐ |
| AC-6.2.2 | "Français" DOIT être la valeur par défaut | ☐ |
| AC-6.2.3 | "Auto-détection" DOIT être une option | ☐ |
| AC-6.2.4 | Le code langue DOIT être ISO 639-1 (fr, en, de, etc.) | ☐ |

---

### FR-6.3: Choix mode diarisation

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-6.3 |
| **Titre** | Sélection du mode de diarisation |
| **Priorité** | P1 - High |
| **Epic** | E6 - Configuration |

#### Description

Le système DOIT permettre à l'utilisateur de choisir le mode de diarisation.

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-6.3.1 | Options: "Qualité", "Rapide", "Désactivé" | ☐ |
| AC-6.3.2 | "Qualité" DOIT être la valeur par défaut | ☐ |
| AC-6.3.3 | Le temps estimé DOIT être ajusté selon le choix | ☐ |
| AC-6.3.4 | "Désactivé" DOIT sauter l'étape de diarisation | ☐ |

---

### FR-6.4: Persistance préférences

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-6.4 |
| **Titre** | Sauvegarde des préférences utilisateur |
| **Priorité** | P2 - Medium |
| **Epic** | E6 - Configuration |

#### Description

Le système DEVRAIT sauvegarder et restaurer les préférences utilisateur.

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-6.4.1 | Les préférences DEVRAIENT être sauvegardées à la fermeture | ☐ |
| AC-6.4.2 | Les préférences DEVRAIENT être restaurées au lancement | ☐ |
| AC-6.4.3 | Le fichier de config DOIT être en YAML lisible | ☐ |
| AC-6.4.4 | Un bouton "Réinitialiser" DEVRAIT restaurer les valeurs par défaut | ☐ |

---

## 9. Epic 7: Gestion des Modèles (E7)

### 9.1 Vue d'ensemble

L'Epic Gestion des Modèles couvre le téléchargement, le stockage et le chargement des modèles ML.

---

### FR-7.1: Téléchargement modèles

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-7.1 |
| **Titre** | Téléchargement automatique des modèles |
| **Priorité** | P0 - Critical |
| **Epic** | E7 - Gestion Modèles |

#### Description

Le système DOIT télécharger les modèles ML requis au premier lancement ou sur demande.

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-7.1.1 | Le téléchargement DOIT être déclenché si modèle absent | ☐ |
| AC-7.1.2 | La source DOIT être HuggingFace Hub | ☐ |
| AC-7.1.3 | La progression DOIT être affichée | ☐ |
| AC-7.1.4 | L'utilisateur DOIT pouvoir annuler le téléchargement | ☐ |
| AC-7.1.5 | Une erreur réseau DOIT être gérée gracieusement | ☐ |

---

### FR-7.2: Cache local modèles

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-7.2 |
| **Titre** | Mise en cache locale des modèles |
| **Priorité** | P0 - Critical |
| **Epic** | E7 - Gestion Modèles |

#### Description

Le système DOIT stocker les modèles téléchargés dans un cache local persistant.

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-7.2.1 | Les modèles DOIVENT être stockés dans le dossier `models/` | ☐ |
| AC-7.2.2 | Un modèle en cache NE DOIT PAS être re-téléchargé | ☐ |
| AC-7.2.3 | L'intégrité du cache DOIT être vérifiable | ☐ |
| AC-7.2.4 | L'utilisateur DEVRAIT pouvoir supprimer le cache | ☐ |

---

### FR-7.3: Fonctionnement offline

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-7.3 |
| **Titre** | Mode 100% offline |
| **Priorité** | P0 - Critical |
| **Epic** | E7 - Gestion Modèles |

#### Description

Le système DOIT fonctionner entièrement offline une fois les modèles téléchargés.

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-7.3.1 | Aucune connexion internet NE DOIT être requise après setup | ☐ |
| AC-7.3.2 | L'application DOIT démarrer sans internet si modèles présents | ☐ |
| AC-7.3.3 | Aucun appel réseau NE DOIT être effectué pendant transcription | ☐ |
| AC-7.3.4 | Un message clair DOIT indiquer si modèles manquants | ☐ |

---

### FR-7.4: Progression téléchargement

| Attribut | Valeur |
|----------|--------|
| **ID** | FR-7.4 |
| **Titre** | Affichage progression téléchargement |
| **Priorité** | P1 - High |
| **Epic** | E7 - Gestion Modèles |

#### Description

Le système DEVRAIT afficher la progression du téléchargement des modèles.

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-7.4.1 | Une barre de progression DEVRAIT montrer l'avancement | ☐ |
| AC-7.4.2 | La taille totale et téléchargée DEVRAIENT être affichées | ☐ |
| AC-7.4.3 | La vitesse de téléchargement DEVRAIT être indiquée | ☐ |
| AC-7.4.4 | Le temps restant estimé DEVRAIT être affiché | ☐ |

---

## 10. Matrice de Traçabilité

### 10.1 FRs → User Stories

| FR ID | User Stories | Epic |
|-------|--------------|------|
| FR-1.1 | US-1.1, US-1.2 | E1 |
| FR-1.2 | US-1.3, US-1.4 | E1 |
| FR-1.3 | US-1.5 | E1 |
| FR-1.4 | US-1.6 | E1 |
| FR-1.5 | US-1.7 | E1 |
| FR-2.1 | US-2.1, US-2.2 | E2 |
| FR-2.2 | US-2.3 | E2 |
| FR-2.3 | US-2.4 | E2 |
| FR-2.4 | US-2.5 | E2 |
| FR-2.5 | US-2.6 | E2 |
| FR-3.1 | US-3.1, US-3.2 | E3 |
| FR-3.2 | US-3.3 | E3 |
| FR-3.3 | US-3.4 | E3 |
| FR-3.4 | US-3.5 | E3 |
| FR-3.5 | US-3.6 | E3 |
| FR-4.1 | US-4.1 | E4 |
| FR-4.2 | US-4.2 | E4 |
| FR-4.3 | US-4.3 | E4 |
| FR-4.4 | US-4.4 | E4 |
| FR-5.1 | US-5.1 | E5 |
| FR-5.2 | US-5.2 | E5 |
| FR-5.3 | US-5.3 | E5 |
| FR-5.4 | US-5.4 | E5 |
| FR-5.5 | US-5.5 | E5 |
| FR-6.1 | US-6.1 | E6 |
| FR-6.2 | US-6.2 | E6 |
| FR-6.3 | US-6.3 | E6 |
| FR-6.4 | US-6.4 | E6 |
| FR-7.1 | US-7.1 | E7 |
| FR-7.2 | US-7.2 | E7 |
| FR-7.3 | US-7.3 | E7 |
| FR-7.4 | US-7.4 | E7 |

### 10.2 FRs → Personas

| Persona | FRs Prioritaires |
|---------|------------------|
| **Marie (Avocate)** | FR-1.1, FR-2.1, FR-3.1, FR-3.2, FR-4.1, FR-7.3 |
| **Thomas (Journaliste)** | FR-1.2, FR-2.1, FR-4.2, FR-5.3, FR-7.3 |
| **Sophie (Assistante)** | FR-5.1, FR-5.5, FR-6.4, FR-3.4, FR-4.3 |

### 10.3 Couverture MVP

| Priorité | Total FRs | Dans MVP |
|----------|-----------|----------|
| P0 - Critical | 18 | 18 (100%) |
| P1 - High | 10 | 10 (100%) |
| P2 - Medium | 4 | 2 (50%) |
| P3 - Low | 0 | 0 |
| **TOTAL** | **32** | **30 (94%)** |

---

## Historique des Révisions

| Version | Date | Auteur | Modifications |
|---------|------|--------|---------------|
| 1.0.0 | 2026-01-14 | PM Agent (BMAD) | Création initiale |

---

**Document suivant:** [NON_FUNCTIONAL_REQUIREMENTS.md](./NON_FUNCTIONAL_REQUIREMENTS.md)
