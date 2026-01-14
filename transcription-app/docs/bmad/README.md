# DICTEA - Documentation BMAD

**Projet:** DICTEA - Application de Transcription Audio Offline
**Méthodologie:** BMAD (Breakthrough Method for Agile AI-Driven Development)
**Version:** 1.0.0
**Date:** 2026-01-14

---

## Vue d'ensemble

Cette documentation suit la méthodologie **BMAD** qui structure le développement agile piloté par IA en 4 phases:

```
┌─────────────────────────────────────────────────────────────────┐
│                    BMAD LIFECYCLE                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   PHASE 1              PHASE 2              PHASE 3            │
│   ANALYSIS             PLANNING             SOLUTIONING        │
│   ┌──────────┐        ┌──────────┐        ┌──────────┐        │
│   │ Project  │   ──▶  │   PRD    │   ──▶  │Technical │        │
│   │  Brief   │        │   FRs    │        │Blueprint │        │
│   │          │        │   NFRs   │        │   ADRs   │        │
│   └──────────┘        └──────────┘        └──────────┘        │
│        ✓                   ✓                   ✓               │
│                                                                 │
│   PHASE 4                                                       │
│   IMPLEMENTATION                                                │
│   ┌──────────────────────────────────────────────────────┐     │
│   │ Story-driven development with continuous validation  │     │
│   └──────────────────────────────────────────────────────┘     │
│        → En cours                                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Documents

### Phase 1: Analysis

| Document | Description | Statut |
|----------|-------------|--------|
| *Project Brief* | Idée initiale et contexte | Intégré au PRD |

### Phase 2: Planning

| Document | Description | Statut |
|----------|-------------|--------|
| [PRD.md](./PRD.md) | Product Requirements Document | ✅ Complet |
| [FUNCTIONAL_REQUIREMENTS.md](./FUNCTIONAL_REQUIREMENTS.md) | 32 Functional Requirements | ✅ Complet |
| [NON_FUNCTIONAL_REQUIREMENTS.md](./NON_FUNCTIONAL_REQUIREMENTS.md) | 28 Non-Functional Requirements | ✅ Complet |
| [USER_STORIES.md](./USER_STORIES.md) | 36 User Stories sur 7 Epics | ✅ Complet |

### Phase 3: Solutioning

| Document | Description | Statut |
|----------|-------------|--------|
| [TECHNICAL_ARCHITECTURE.md](./TECHNICAL_ARCHITECTURE.md) | Architecture technique complète | ✅ Complet |

### Phase 4: Implementation

| Document | Description | Statut |
|----------|-------------|--------|
| *Sprint Backlog* | Stories en cours | À créer |
| *Test Plans* | Plans de test | À créer |

---

## Résumé du Projet

### Vision

> *"Démocratiser l'accès à la transcription audio professionnelle en offrant une solution 100% locale, aussi simple qu'un enregistreur vocal, aussi précise qu'un service premium."*

### Caractéristiques Clés

- **100% Offline** - Aucune donnée transmise à l'extérieur
- **Privacy-First** - Conformité RGPD native
- **Qualité Pro** - WER < 8%, DER < 15%
- **Multi-locuteurs** - Diarisation intégrée

### Stack Technique

| Composant | Technologie |
|-----------|-------------|
| Transcription | faster-whisper (CTranslate2) |
| Diarisation | Pyannote 3.1 / SpeechBrain |
| UI | PySide6 (Qt6) |
| Packaging | Nuitka (release) / PyInstaller (dev) |

### Métriques MVP

| Métrique | Cible |
|----------|-------|
| Epics | 7 |
| User Stories | 36 |
| Story Points | 131 |
| FRs | 32 |
| NFRs | 28 |
| ADRs | 6 |

---

## Navigation Rapide

### Par Persona

| Persona | Documents Pertinents |
|---------|---------------------|
| **Marie (Avocate)** | [PRD - Personas](./PRD.md#4-user-personas), [NFR-SEC](./NON_FUNCTIONAL_REQUIREMENTS.md#4-sécurité--privacy-sec) |
| **Thomas (Journaliste)** | [PRD - Personas](./PRD.md#4-user-personas), [FR-E4 Export](./FUNCTIONAL_REQUIREMENTS.md#6-epic-4-export-e4) |
| **Sophie (Assistante)** | [PRD - Personas](./PRD.md#4-user-personas), [NFR-USA](./NON_FUNCTIONAL_REQUIREMENTS.md#6-utilisabilité-usa) |

### Par Epic

| Epic | FRs | User Stories |
|------|-----|--------------|
| E1 - Gestion Audio | [FR-1.x](./FUNCTIONAL_REQUIREMENTS.md#3-epic-1-gestion-audio-e1) | [US-1.x](./USER_STORIES.md#3-epic-1-gestion-audio) |
| E2 - Transcription | [FR-2.x](./FUNCTIONAL_REQUIREMENTS.md#4-epic-2-transcription-e2) | [US-2.x](./USER_STORIES.md#4-epic-2-transcription) |
| E3 - Diarisation | [FR-3.x](./FUNCTIONAL_REQUIREMENTS.md#5-epic-3-diarisation-e3) | [US-3.x](./USER_STORIES.md#5-epic-3-diarisation) |
| E4 - Export | [FR-4.x](./FUNCTIONAL_REQUIREMENTS.md#6-epic-4-export-e4) | [US-4.x](./USER_STORIES.md#6-epic-4-export) |
| E5 - Interface UI | [FR-5.x](./FUNCTIONAL_REQUIREMENTS.md#7-epic-5-interface-utilisateur-e5) | [US-5.x](./USER_STORIES.md#7-epic-5-interface-utilisateur) |
| E6 - Configuration | [FR-6.x](./FUNCTIONAL_REQUIREMENTS.md#8-epic-6-configuration-e6) | [US-6.x](./USER_STORIES.md#8-epic-6-configuration) |
| E7 - Modèles | [FR-7.x](./FUNCTIONAL_REQUIREMENTS.md#9-epic-7-gestion-des-modèles-e7) | [US-7.x](./USER_STORIES.md#9-epic-7-gestion-des-modèles) |

### Par Catégorie NFR

| Catégorie | Lien |
|-----------|------|
| Performance (PERF) | [NFR-PERF](./NON_FUNCTIONAL_REQUIREMENTS.md#3-performance-perf) |
| Sécurité (SEC) | [NFR-SEC](./NON_FUNCTIONAL_REQUIREMENTS.md#4-sécurité--privacy-sec) |
| Fiabilité (REL) | [NFR-REL](./NON_FUNCTIONAL_REQUIREMENTS.md#5-fiabilité-rel) |
| Utilisabilité (USA) | [NFR-USA](./NON_FUNCTIONAL_REQUIREMENTS.md#6-utilisabilité-usa) |
| Maintenabilité (MNT) | [NFR-MNT](./NON_FUNCTIONAL_REQUIREMENTS.md#7-maintenabilité-mnt) |
| Portabilité (PRT) | [NFR-PRT](./NON_FUNCTIONAL_REQUIREMENTS.md#8-portabilité-prt) |
| Scalabilité (SCL) | [NFR-SCL](./NON_FUNCTIONAL_REQUIREMENTS.md#9-scalabilité-scl) |
| Compatibilité (CMP) | [NFR-CMP](./NON_FUNCTIONAL_REQUIREMENTS.md#10-compatibilité-cmp) |

---

## Architecture Decision Records (ADRs)

| ADR | Décision | Statut |
|-----|----------|--------|
| [ADR-001](./TECHNICAL_ARCHITECTURE.md#adr-001-choix-de-faster-whisper-vs-whisper-original) | faster-whisper vs Whisper | Accepté |
| [ADR-002](./TECHNICAL_ARCHITECTURE.md#adr-002-choix-de-pyside6-vs-pyqt6) | PySide6 vs PyQt6 | Accepté |
| [ADR-003](./TECHNICAL_ARCHITECTURE.md#adr-003-architecture-threading-avec-qthread) | QThread pour workers | Accepté |
| [ADR-004](./TECHNICAL_ARCHITECTURE.md#adr-004-dual-mode-diarisation) | Dual-mode diarisation | Accepté |
| [ADR-005](./TECHNICAL_ARCHITECTURE.md#adr-005-configuration-yaml-singleton) | Config YAML singleton | Accepté |
| [ADR-006](./TECHNICAL_ARCHITECTURE.md#adr-006-build-nuitka-pour-release) | Nuitka pour release | Accepté |

---

## Références

- [BMAD Official Documentation](https://docs.bmad-method.org/)
- [BMAD GitHub Repository](https://github.com/bmad-code-org/BMAD-METHOD)
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- [Pyannote Audio](https://github.com/pyannote/pyannote-audio)
- [PySide6](https://doc.qt.io/qtforpython-6/)

---

## Historique

| Version | Date | Modifications |
|---------|------|---------------|
| 1.0.0 | 2026-01-14 | Documentation BMAD initiale complète |

---

*Documentation générée selon la méthodologie BMAD v2.0*
