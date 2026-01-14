# DICTEA - Product Requirements Document (PRD)

**Version:** 1.0.0
**Date:** 2026-01-14
**Méthodologie:** BMAD (Breakthrough Method for Agile AI-Driven Development)
**Statut:** Draft
**Auteur:** Product Manager Agent

---

## Table des matières

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Vision et Objectifs](#3-vision-et-objectifs)
4. [User Personas](#4-user-personas)
5. [Scope du Produit](#5-scope-du-produit)
6. [Functional Requirements (FRs)](#6-functional-requirements-frs)
7. [Non-Functional Requirements (NFRs)](#7-non-functional-requirements-nfrs)
8. [User Journeys](#8-user-journeys)
9. [Success Metrics](#9-success-metrics)
10. [Risks et Assumptions](#10-risks-et-assumptions)
11. [Dependencies](#11-dependencies)
12. [Glossaire](#12-glossaire)

---

## 1. Executive Summary

### 1.1 Résumé du Produit

**DICTEA** est une application desktop Windows de transcription audio professionnelle fonctionnant **100% hors-ligne**. Elle combine la reconnaissance vocale automatique (ASR) de pointe avec l'identification des locuteurs (diarisation) pour transformer des enregistrements audio en texte structuré, avec attribution des paroles à chaque intervenant.

### 1.2 Proposition de Valeur Unique

| Différenciateur | Description |
|-----------------|-------------|
| **Privacy-First** | Traitement local exclusif, aucune donnée audio transmise |
| **Offline Total** | Fonctionnement sans connexion après installation initiale |
| **Qualité Professionnelle** | WER < 8% sur le français, DER < 12% pour la diarisation |
| **Simplicité d'Usage** | Interface intuitive, workflow en 3 clics |

### 1.3 Marché Cible

- **Marché primaire:** Professionnels francophones (avocats, journalistes, chercheurs, secrétaires)
- **Marché secondaire:** PME françaises avec besoins de transcription réguliers
- **Taille estimée:** ~500 000 professionnels en France avec besoins de transcription

### 1.4 Business Model

Application desktop gratuite/freemium avec potentiel de monétisation via :
- Version Pro avec modèles étendus
- Support entreprise
- Formations et onboarding

---

## 2. Problem Statement

### 2.1 Contexte du Problème

La transcription audio professionnelle représente un défi majeur pour de nombreux professionnels :

#### Problèmes actuels des solutions existantes

| Solution | Problème |
|----------|----------|
| **Services Cloud** (Otter.ai, Rev) | Confidentialité compromise, données sensibles externalisées |
| **Transcription manuelle** | Coût élevé (150-300€/heure audio), délais importants |
| **Outils gratuits** (YouTube, Google) | Qualité insuffisante, pas de diarisation, dépendance internet |
| **Solutions entreprise** (Nuance) | Coût prohibitif, complexité d'installation |

### 2.2 Pain Points Utilisateurs

```
┌─────────────────────────────────────────────────────────────────┐
│  CONFIDENTIALITÉ        │  COÛT           │  QUALITÉ           │
├─────────────────────────┼─────────────────┼────────────────────┤
│  • Données sensibles    │  • 150€+/h      │  • Erreurs fréquentes │
│  • RGPD compliance      │  • Abonnements  │  • Pas de locuteurs   │
│  • Secret professionnel │  • Coûts cachés │  • Formats limités    │
└─────────────────────────┴─────────────────┴────────────────────┘
```

### 2.3 Opportunité de Marché

L'émergence de modèles ASR performants (Whisper) et de diarisation (Pyannote) permet désormais une transcription de qualité professionnelle en local, répondant aux exigences de confidentialité sans compromis sur la qualité.

### 2.4 Énoncé du Problème

> **Les professionnels francophones ont besoin d'une solution de transcription audio qui garantit la confidentialité totale de leurs données sensibles, tout en offrant une qualité de transcription professionnelle avec identification des locuteurs, sans dépendance à une connexion internet ni coûts récurrents.**

---

## 3. Vision et Objectifs

### 3.1 Vision Produit

> *"Démocratiser l'accès à la transcription audio professionnelle en offrant une solution 100% locale, aussi simple qu'un enregistreur vocal, aussi précise qu'un service premium."*

### 3.2 Mission

Permettre à tout professionnel francophone de transcrire ses enregistrements audio en toute confidentialité, avec identification des locuteurs, en moins de temps que la durée de l'enregistrement.

### 3.3 Objectifs Stratégiques

| Objectif | Métrique | Cible |
|----------|----------|-------|
| **O1: Adoption** | Utilisateurs actifs mensuels | 10 000 en Y1 |
| **O2: Qualité** | Taux d'erreur mot (WER) | < 8% |
| **O3: Satisfaction** | NPS (Net Promoter Score) | > 50 |
| **O4: Performance** | Ratio temps réel transcription | < 1.5x |

### 3.4 Principes Directeurs

1. **Privacy by Design** - La confidentialité n'est pas une option mais un fondement
2. **Simplicity First** - Complexité cachée, simplicité exposée
3. **Quality over Speed** - Privilégier la précision à la rapidité
4. **Offline by Default** - Internet = optionnel, jamais requis

---

## 4. User Personas

### 4.1 Persona Primaire: Marie - L'Avocate

```
┌────────────────────────────────────────────────────────────────┐
│  MARIE DUPONT - Avocate en droit des affaires                  │
├────────────────────────────────────────────────────────────────┤
│  Âge: 42 ans          │  Localisation: Paris                   │
│  Expérience tech: Moyenne │  Usage: 5-10 transcriptions/mois   │
├────────────────────────────────────────────────────────────────┤
│  CONTEXTE                                                      │
│  • Cabinet de 15 avocats                                       │
│  • Enregistre ses entretiens clients et audiences             │
│  • Soumise au secret professionnel strict                     │
│  • Secrétariat débordé, délais de transcription longs         │
├────────────────────────────────────────────────────────────────┤
│  OBJECTIFS                                                     │
│  • Transcrire rapidement ses enregistrements                  │
│  • Garantir la confidentialité absolue                        │
│  • Identifier qui parle dans les réunions multi-parties       │
│  • Exporter vers Word pour ses dossiers                       │
├────────────────────────────────────────────────────────────────┤
│  FRUSTRATIONS                                                  │
│  • Services cloud interdits par la déontologie                │
│  • Transcription manuelle trop coûteuse et lente              │
│  • Outils existants ne distinguent pas les locuteurs          │
│  • Qualité insuffisante sur le vocabulaire juridique          │
├────────────────────────────────────────────────────────────────┤
│  CITATION                                                      │
│  "J'ai besoin d'une solution où mes données ne quittent       │
│   jamais mon ordinateur. Le secret professionnel, c'est       │
│   non négociable."                                             │
└────────────────────────────────────────────────────────────────┘
```

**Jobs to be Done:**
- JTBD-1: Transcrire un entretien client de 45min en moins d'1h
- JTBD-2: Retrouver qui a dit quoi dans une négociation
- JTBD-3: Produire un compte-rendu structuré par locuteur

---

### 4.2 Persona Secondaire: Thomas - Le Journaliste

```
┌────────────────────────────────────────────────────────────────┐
│  THOMAS MARTIN - Journaliste d'investigation                   │
├────────────────────────────────────────────────────────────────┤
│  Âge: 35 ans          │  Localisation: Lyon                    │
│  Expérience tech: Élevée │  Usage: 15-20 transcriptions/mois  │
├────────────────────────────────────────────────────────────────┤
│  CONTEXTE                                                      │
│  • Rédaction d'un média régional                              │
│  • Interviews fréquentes avec sources sensibles               │
│  • Travaille souvent en mobilité sans connexion               │
│  • Budget limité pour les outils                              │
├────────────────────────────────────────────────────────────────┤
│  OBJECTIFS                                                     │
│  • Transcrire rapidement ses interviews                       │
│  • Protéger l'identité de ses sources                         │
│  • Travailler offline (train, zones blanches)                 │
│  • Générer des sous-titres pour podcasts                      │
├────────────────────────────────────────────────────────────────┤
│  FRUSTRATIONS                                                  │
│  • Outils cloud = risque pour ses sources                     │
│  • Pas de connexion fiable en déplacement                     │
│  • Abonnements multiples trop coûteux                         │
│  • Export SRT souvent mal formaté                             │
├────────────────────────────────────────────────────────────────┤
│  CITATION                                                      │
│  "Mes sources me font confiance. Je ne peux pas envoyer       │
│   leur voix sur des serveurs américains."                     │
└────────────────────────────────────────────────────────────────┘
```

**Jobs to be Done:**
- JTBD-4: Transcrire une interview de 2h pendant un trajet en train
- JTBD-5: Générer des sous-titres SRT pour un podcast
- JTBD-6: Retrouver une citation précise dans 10h d'archives

---

### 4.3 Persona Tertiaire: Sophie - L'Assistante de Direction

```
┌────────────────────────────────────────────────────────────────┐
│  SOPHIE BERNARD - Assistante de Direction                      │
├────────────────────────────────────────────────────────────────┤
│  Âge: 38 ans          │  Localisation: Bordeaux                │
│  Expérience tech: Faible │  Usage: 3-5 transcriptions/semaine │
├────────────────────────────────────────────────────────────────┤
│  CONTEXTE                                                      │
│  • PME industrielle de 200 employés                           │
│  • Transcrit les réunions de direction (CODIR)                │
│  • Pas de formation technique                                  │
│  • Utilise principalement Word et Outlook                     │
├────────────────────────────────────────────────────────────────┤
│  OBJECTIFS                                                     │
│  • Produire des PV de réunion rapidement                      │
│  • Interface simple sans configuration complexe               │
│  • Identifier les 5-6 directeurs dans les réunions            │
│  • Copier-coller facilement vers Word                         │
├────────────────────────────────────────────────────────────────┤
│  FRUSTRATIONS                                                  │
│  • Outils trop techniques et intimidants                      │
│  • Installation complexe avec prérequis                       │
│  • Pas de temps pour apprendre un nouveau logiciel            │
│  • Erreurs de transcription sur les noms propres              │
├────────────────────────────────────────────────────────────────┤
│  CITATION                                                      │
│  "Je veux juste cliquer sur 'Transcrire' et que ça marche.    │
│   Je n'ai pas le temps d'être informaticienne."               │
└────────────────────────────────────────────────────────────────┘
```

**Jobs to be Done:**
- JTBD-7: Transcrire un CODIR de 2h avec 6 participants
- JTBD-8: Produire un PV structuré par intervenant
- JTBD-9: Former un collègue en 5 minutes

---

## 5. Scope du Produit

### 5.1 Périmètre MVP (Minimum Viable Product)

#### Dans le Scope (In-Scope)

| Catégorie | Fonctionnalités |
|-----------|-----------------|
| **Entrée Audio** | Import fichiers (WAV, MP3, M4A, FLAC, OGG), Enregistrement micro |
| **Transcription** | ASR français haute qualité, timestamps, segments |
| **Diarisation** | Identification 2-10 locuteurs, mode qualité/rapide |
| **Export** | TXT formaté, SRT sous-titres, Presse-papiers |
| **Interface** | GUI Windows native, barre de progression, annulation |
| **Configuration** | Choix modèle, langue, paramètres diarisation |

#### Hors Scope (Out-of-Scope) - MVP

| Catégorie | Fonctionnalités Exclues |
|-----------|------------------------|
| **Plateformes** | macOS, Linux, Web, Mobile |
| **Langues** | Autres que français (configurable mais non optimisé) |
| **Fonctionnalités** | Traitement batch, API/CLI, Édition post-transcription |
| **Intégrations** | Cloud storage, Office 365, Google Workspace |
| **Avancé** | Vocabulaire personnalisé, Modèles fine-tunés |

### 5.2 Roadmap Fonctionnelle

```
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 1 (MVP)          │  PHASE 2              │  PHASE 3      │
│  Q1 2026                │  Q2-Q3 2026           │  Q4 2026+     │
├─────────────────────────┼───────────────────────┼───────────────┤
│  ✓ Transcription FR     │  • Multi-langue       │  • API REST   │
│  ✓ Diarisation          │  • Batch processing   │  • Plugins    │
│  ✓ Export TXT/SRT       │  • Éditeur intégré    │  • Cloud sync │
│  ✓ Enregistrement       │  • Recherche texte    │  • Mobile     │
│  ✓ GUI Windows          │  • Vocabulaire custom │  • macOS      │
└─────────────────────────┴───────────────────────┴───────────────┘
```

### 5.3 Contraintes

| Type | Contrainte |
|------|------------|
| **Technique** | Windows 10/11 uniquement, CPU AVX2 requis, 16 Go RAM minimum |
| **Légale** | RGPD compliance, Licences open-source (MIT, Apache, LGPL) |
| **Business** | Budget développement limité, équipe réduite |
| **Temps** | MVP livrable en 3 mois |

---

## 6. Functional Requirements (FRs)

> Les requirements fonctionnelles détaillées sont disponibles dans le document [FUNCTIONAL_REQUIREMENTS.md](./FUNCTIONAL_REQUIREMENTS.md)

### 6.1 Vue d'ensemble des Epics

| Epic ID | Nom | Description | Priorité |
|---------|-----|-------------|----------|
| **E1** | Gestion Audio | Import, enregistrement et prétraitement audio | P0 - Critical |
| **E2** | Transcription | Conversion speech-to-text avec timestamps | P0 - Critical |
| **E3** | Diarisation | Identification et attribution des locuteurs | P0 - Critical |
| **E4** | Export | Génération des formats de sortie | P0 - Critical |
| **E5** | Interface Utilisateur | GUI et expérience utilisateur | P0 - Critical |
| **E6** | Configuration | Paramétrage et personnalisation | P1 - High |
| **E7** | Gestion Modèles | Téléchargement et cache des modèles ML | P1 - High |

### 6.2 Résumé des FRs par Epic

#### Epic 1: Gestion Audio (E1)

| FR ID | Requirement | Priorité |
|-------|-------------|----------|
| FR-1.1 | Le système DOIT permettre l'import de fichiers audio (WAV, MP3, M4A, FLAC, OGG, WMA, AAC) | P0 |
| FR-1.2 | Le système DOIT permettre l'enregistrement depuis le microphone système | P0 |
| FR-1.3 | Le système DOIT convertir tout audio en format Whisper-compatible (16kHz, mono, PCM) | P0 |
| FR-1.4 | Le système DOIT afficher les métadonnées audio (durée, format, taille) | P1 |
| FR-1.5 | Le système DEVRAIT supporter le découpage automatique des fichiers longs (>30min) | P2 |

#### Epic 2: Transcription (E2)

| FR ID | Requirement | Priorité |
|-------|-------------|----------|
| FR-2.1 | Le système DOIT transcrire l'audio en texte français avec WER < 10% | P0 |
| FR-2.2 | Le système DOIT fournir des timestamps (début, fin) pour chaque segment | P0 |
| FR-2.3 | Le système DOIT afficher la progression en temps réel | P0 |
| FR-2.4 | Le système DOIT permettre l'annulation de la transcription en cours | P0 |
| FR-2.5 | Le système DEVRAIT détecter automatiquement la langue si non spécifiée | P2 |

#### Epic 3: Diarisation (E3)

| FR ID | Requirement | Priorité |
|-------|-------------|----------|
| FR-3.1 | Le système DOIT identifier les différents locuteurs dans l'audio | P0 |
| FR-3.2 | Le système DOIT attribuer chaque segment transcrit à un locuteur | P0 |
| FR-3.3 | Le système DOIT proposer deux modes: Qualité (précis) et Rapide | P1 |
| FR-3.4 | Le système DEVRAIT permettre de spécifier le nombre de locuteurs attendus | P1 |
| FR-3.5 | Le système DEVRAIT gérer les chevauchements de parole | P2 |

#### Epic 4: Export (E4)

| FR ID | Requirement | Priorité |
|-------|-------------|----------|
| FR-4.1 | Le système DOIT exporter en format TXT avec locuteurs et timestamps | P0 |
| FR-4.2 | Le système DOIT exporter en format SRT (sous-titres) | P0 |
| FR-4.3 | Le système DOIT permettre la copie vers le presse-papiers | P0 |
| FR-4.4 | Le système DEVRAIT proposer des options de formatage (avec/sans timestamps) | P2 |

#### Epic 5: Interface Utilisateur (E5)

| FR ID | Requirement | Priorité |
|-------|-------------|----------|
| FR-5.1 | Le système DOIT fournir une interface graphique Windows native | P0 |
| FR-5.2 | Le système DOIT afficher une barre de progression avec estimation | P0 |
| FR-5.3 | Le système DOIT rester réactif pendant le traitement (non-blocking UI) | P0 |
| FR-5.4 | Le système DOIT afficher les résultats de manière lisible et structurée | P0 |
| FR-5.5 | Le système DOIT afficher des messages d'erreur compréhensibles | P1 |

#### Epic 6: Configuration (E6)

| FR ID | Requirement | Priorité |
|-------|-------------|----------|
| FR-6.1 | Le système DOIT permettre le choix du modèle de transcription | P1 |
| FR-6.2 | Le système DOIT permettre le choix de la langue cible | P1 |
| FR-6.3 | Le système DOIT permettre le choix du mode de diarisation | P1 |
| FR-6.4 | Le système DEVRAIT persister les préférences utilisateur | P2 |

#### Epic 7: Gestion Modèles (E7)

| FR ID | Requirement | Priorité |
|-------|-------------|----------|
| FR-7.1 | Le système DOIT télécharger les modèles ML au premier lancement | P0 |
| FR-7.2 | Le système DOIT mettre en cache les modèles localement | P0 |
| FR-7.3 | Le système DOIT fonctionner offline après téléchargement initial | P0 |
| FR-7.4 | Le système DEVRAIT afficher la progression du téléchargement | P1 |

---

## 7. Non-Functional Requirements (NFRs)

> Les requirements non-fonctionnelles détaillées sont disponibles dans le document [NON_FUNCTIONAL_REQUIREMENTS.md](./NON_FUNCTIONAL_REQUIREMENTS.md)

### 7.1 Vue d'ensemble des Catégories NFR

| Catégorie | Code | Description |
|-----------|------|-------------|
| Performance | PERF | Temps de réponse, throughput, utilisation ressources |
| Sécurité | SEC | Protection données, confidentialité, RGPD |
| Fiabilité | REL | Disponibilité, tolérance aux pannes, récupération |
| Utilisabilité | USA | Facilité d'utilisation, accessibilité, apprentissage |
| Maintenabilité | MNT | Modularité, testabilité, évolutivité |
| Portabilité | PRT | Compatibilité, installation, déploiement |
| Scalabilité | SCL | Gestion de charge, limites système |

### 7.2 Résumé des NFRs Critiques

#### Performance (PERF)

| NFR ID | Requirement | Cible | Priorité |
|--------|-------------|-------|----------|
| NFR-PERF-01 | Ratio temps de transcription vs durée audio | ≤ 1.5x temps réel | P0 |
| NFR-PERF-02 | Utilisation mémoire RAM maximale | ≤ 8 Go | P0 |
| NFR-PERF-03 | Temps de démarrage application | ≤ 10 secondes | P1 |
| NFR-PERF-04 | Réactivité UI pendant traitement | ≤ 100ms latence | P0 |

#### Sécurité & Privacy (SEC)

| NFR ID | Requirement | Cible | Priorité |
|--------|-------------|-------|----------|
| NFR-SEC-01 | Traitement des données audio | 100% local, aucune transmission | P0 |
| NFR-SEC-02 | Stockage des fichiers temporaires | Nettoyage automatique | P0 |
| NFR-SEC-03 | Conformité RGPD | Compliance totale | P0 |
| NFR-SEC-04 | Protection du code source | Compilation Nuitka | P1 |

#### Fiabilité (REL)

| NFR ID | Requirement | Cible | Priorité |
|--------|-------------|-------|----------|
| NFR-REL-01 | Taux de succès des transcriptions | ≥ 99% | P0 |
| NFR-REL-02 | Gestion des fichiers corrompus | Échec gracieux avec message | P1 |
| NFR-REL-03 | Récupération après crash | Pas de perte de données | P1 |

#### Utilisabilité (USA)

| NFR ID | Requirement | Cible | Priorité |
|--------|-------------|-------|----------|
| NFR-USA-01 | Temps d'apprentissage utilisateur novice | ≤ 5 minutes | P0 |
| NFR-USA-02 | Nombre de clics pour transcription complète | ≤ 4 clics | P1 |
| NFR-USA-03 | Messages d'erreur compréhensibles | Langage non-technique | P1 |

#### Portabilité (PRT)

| NFR ID | Requirement | Cible | Priorité |
|--------|-------------|-------|----------|
| NFR-PRT-01 | Systèmes d'exploitation supportés | Windows 10/11 64-bit | P0 |
| NFR-PRT-02 | Installation sans droits administrateur | Optionnel | P2 |
| NFR-PRT-03 | Taille de l'installeur | ≤ 500 Mo (sans modèles) | P1 |

---

## 8. User Journeys

### 8.1 Journey 1: Transcription d'un fichier existant

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  MARIE (Avocate) - Transcrire un entretien client enregistré                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. LANCEMENT                    2. IMPORT                                  │
│  ┌──────────────┐               ┌──────────────┐                           │
│  │ Double-clic  │ ──────────▶   │ Clic "Ouvrir │                           │
│  │ DICTEA.exe   │               │ un fichier"  │                           │
│  └──────────────┘               └──────────────┘                           │
│        │                               │                                    │
│        ▼                               ▼                                    │
│  [App démarre en 5s]           [Sélection fichier MP3]                     │
│                                                                             │
│  3. CONFIGURATION                4. TRANSCRIPTION                          │
│  ┌──────────────┐               ┌──────────────┐                           │
│  │ Vérifier:    │ ──────────▶   │ Clic         │                           │
│  │ - Langue: FR │               │ "Transcrire" │                           │
│  │ - Mode: Auto │               └──────────────┘                           │
│  └──────────────┘                      │                                    │
│                                        ▼                                    │
│                                [Progress bar: 45min → 50min]                │
│                                                                             │
│  5. RÉSULTAT                     6. EXPORT                                  │
│  ┌──────────────────────┐       ┌──────────────┐                           │
│  │ [LOCUTEUR_1] Bonjour │       │ Clic "Copier"│ ──▶ Coller dans Word      │
│  │ [LOCUTEUR_2] Bonjour │       │ ou "Sauver"  │                           │
│  │ ...                  │       └──────────────┘                           │
│  └──────────────────────┘                                                   │
│                                                                             │
│  ✓ SUCCÈS: Entretien de 45min transcrit en 50min avec 2 locuteurs          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Journey 2: Enregistrement et transcription directe

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  THOMAS (Journaliste) - Interview en personne                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. PRÉPARATION                  2. ENREGISTREMENT                          │
│  ┌──────────────┐               ┌──────────────┐                           │
│  │ Lancer app   │ ──────────▶   │ Clic         │ ──▶ LED rouge active      │
│  │ avant RDV    │               │ "Enregistrer"│                           │
│  └──────────────┘               └──────────────┘                           │
│                                        │                                    │
│                                        ▼                                    │
│                                 [Interview 30min]                           │
│                                        │                                    │
│  3. ARRÊT                        4. TRANSCRIPTION                          │
│  ┌──────────────┐               ┌──────────────┐                           │
│  │ Clic "Stop"  │ ──────────▶   │ Confirmation │ ──▶ Transcription auto    │
│  │              │               │ "Transcrire?"│                           │
│  └──────────────┘               └──────────────┘                           │
│                                        │                                    │
│                                        ▼                                    │
│                                 [Progress: 30min → 40min]                   │
│                                                                             │
│  5. RÉSULTAT                     6. EXPORT SRT                              │
│  ┌──────────────────────┐       ┌──────────────┐                           │
│  │ [00:00:05] Thomas:   │       │ Clic         │ ──▶ Podcast avec          │
│  │ Bonjour, merci...    │       │ "Export SRT" │     sous-titres           │
│  └──────────────────────┘       └──────────────┘                           │
│                                                                             │
│  ✓ SUCCÈS: Interview transcrite, sous-titres générés pour podcast          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.3 Journey 3: Réunion multi-locuteurs

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  SOPHIE (Assistante) - Transcription CODIR                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. IMPORT                       2. PARAMÉTRAGE                             │
│  ┌──────────────┐               ┌──────────────┐                           │
│  │ Ouvrir       │ ──────────▶   │ Nb locuteurs │                           │
│  │ "CODIR.wav"  │               │ = 6          │                           │
│  │ (2h audio)   │               │ Mode=Qualité │                           │
│  └──────────────┘               └──────────────┘                           │
│                                        │                                    │
│  3. TRANSCRIPTION LONGUE              ▼                                     │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │ [██████████░░░░░░░░░░░░░░░░░] 35% - Transcription...        │          │
│  │ [██████████████████░░░░░░░░░] 65% - Diarisation...          │          │
│  │ Temps estimé: 2h30                                           │          │
│  │ [Bouton Annuler disponible]                                  │          │
│  └──────────────────────────────────────────────────────────────┘          │
│                                        │                                    │
│  4. RÉSULTAT STRUCTURÉ               ▼                                     │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │ [00:00:00 - 00:02:30] LOCUTEUR_1                             │          │
│  │ Bonjour à tous, commençons le point sur les ventes...       │          │
│  │                                                               │          │
│  │ [00:02:30 - 00:05:15] LOCUTEUR_2                             │          │
│  │ Merci. Ce mois-ci, nous avons atteint 120% des objectifs... │          │
│  │ ...                                                           │          │
│  └──────────────────────────────────────────────────────────────┘          │
│                                        │                                    │
│  5. EXPORT                             ▼                                    │
│  ┌──────────────┐                                                          │
│  │ Copier vers  │ ──▶ Coller dans Word ──▶ Renommer locuteurs              │
│  │ Word         │     LOCUTEUR_1 → "DG"   LOCUTEUR_2 → "DAF"              │
│  └──────────────┘                                                          │
│                                                                             │
│  ✓ SUCCÈS: CODIR de 2h transcrit, 6 locuteurs identifiés                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. Success Metrics

### 9.1 KPIs Produit

| Métrique | Définition | Cible MVP | Méthode de Mesure |
|----------|------------|-----------|-------------------|
| **Adoption** | Téléchargements cumulés | 5 000 en 6 mois | Analytics installeur |
| **Activation** | % utilisateurs ayant transcrit ≥1 fichier | ≥ 70% | Logs anonymisés |
| **Rétention** | Utilisateurs actifs mois M2 / M1 | ≥ 40% | Analytics optionnel |
| **NPS** | Net Promoter Score | ≥ 40 | Enquête in-app |

### 9.2 KPIs Qualité

| Métrique | Définition | Cible | Méthode de Mesure |
|----------|------------|-------|-------------------|
| **WER** | Word Error Rate transcription FR | ≤ 8% | Benchmark datasets |
| **DER** | Diarization Error Rate | ≤ 15% | Benchmark AMI corpus |
| **Crash Rate** | % sessions avec crash | ≤ 1% | Logs erreurs |
| **Success Rate** | % transcriptions complétées | ≥ 98% | Logs succès/échecs |

### 9.3 KPIs Performance

| Métrique | Définition | Cible | Méthode de Mesure |
|----------|------------|-------|-------------------|
| **RTF** | Real-Time Factor (durée traitement / durée audio) | ≤ 1.5 | Chrono interne |
| **Memory Peak** | Pic d'utilisation RAM | ≤ 8 Go | Monitoring système |
| **Startup Time** | Temps lancement application | ≤ 10s | Chrono cold start |
| **UI Responsiveness** | Latence interaction UI | ≤ 100ms | Profiling Qt |

### 9.4 Success Criteria MVP

Le MVP sera considéré comme un succès si :

1. **Fonctionnel:** 100% des FRs P0 implémentées et fonctionnelles
2. **Qualité:** WER ≤ 10% sur corpus test français
3. **Performance:** RTF ≤ 2x temps réel avec diarisation
4. **Stabilité:** Crash rate ≤ 2% sur 100 transcriptions test
5. **Utilisabilité:** 5 utilisateurs test complètent le journey sans aide

---

## 10. Risks et Assumptions

### 10.1 Assumptions (Hypothèses)

| ID | Hypothèse | Impact si Faux | Mitigation |
|----|-----------|----------------|------------|
| **A1** | Les utilisateurs cibles ont des PCs avec 16 Go RAM | Exclut une partie du marché | Optimisation mémoire, mode léger |
| **A2** | CPU AVX2 disponible sur machines cibles (post-2013) | App non fonctionnelle | Détection au démarrage, message clair |
| **A3** | Modèle Whisper medium suffisant pour qualité pro | Qualité insuffisante | Option modèle large-v3 |
| **A4** | Utilisateurs acceptent 1-2x temps réel pour transcription | Abandon si trop lent | Optimisations, mode rapide |
| **A5** | Internet disponible pour téléchargement initial modèles | Installation impossible | Package offline, clé USB |

### 10.2 Risks (Risques)

| ID | Risque | Probabilité | Impact | Mitigation |
|----|--------|-------------|--------|------------|
| **R1** | Performances insuffisantes sur CPU moyen | Moyenne | Élevé | Benchmarks précoces, optimisation int8 |
| **R2** | Consommation RAM excessive (>16 Go) | Moyenne | Élevé | Garbage collection agressif, chunking |
| **R3** | Qualité diarisation insuffisante (>20% DER) | Faible | Moyen | Mode quality/fast, ajustement params |
| **R4** | Incompatibilité Windows 10 anciennes versions | Faible | Moyen | Tests multi-versions, requirements clairs |
| **R5** | Licences Pyannote restrictives (acceptation T&C) | Élevée | Élevé | Alternative SpeechBrain, documentation claire |
| **R6** | Taille installeur trop importante (>2 Go) | Moyenne | Faible | Téléchargement modèles séparé |
| **R7** | Complexité installation pour utilisateurs non-tech | Moyenne | Moyen | Installeur one-click, wizard |

### 10.3 Dependencies Externes

| Dépendance | Type | Risque | Alternative |
|------------|------|--------|-------------|
| **faster-whisper** | Librairie ML | Faible (MIT) | Whisper.cpp |
| **Pyannote Audio** | Librairie ML | Moyen (MIT + T&C HuggingFace) | SpeechBrain |
| **PySide6** | Framework UI | Faible (LGPL) | PyQt6 (GPL) |
| **HuggingFace Hub** | Distribution modèles | Moyen (service externe) | Hébergement propre |
| **Nuitka** | Compilateur | Faible (Apache) | PyInstaller |

---

## 11. Dependencies

### 11.1 Dependencies Techniques

```
┌─────────────────────────────────────────────────────────────────┐
│                     STACK TECHNIQUE DICTEA                      │
├─────────────────────────────────────────────────────────────────┤
│  APPLICATION                                                    │
│  ├── PySide6 (UI Framework)                                    │
│  ├── PyYAML (Configuration)                                    │
│  └── tqdm (Progress bars)                                      │
├─────────────────────────────────────────────────────────────────┤
│  CORE ML                                                        │
│  ├── faster-whisper (ASR)                                      │
│  │   └── ctranslate2 (Backend optimisé)                        │
│  ├── pyannote.audio (Diarisation quality)                      │
│  │   └── torch (PyTorch backend)                               │
│  └── speechbrain (Diarisation fast)                            │
├─────────────────────────────────────────────────────────────────┤
│  AUDIO                                                          │
│  ├── sounddevice (Recording)                                   │
│  ├── soundfile (I/O)                                           │
│  └── pydub (Conversion)                                        │
├─────────────────────────────────────────────────────────────────┤
│  DISTRIBUTION                                                   │
│  ├── huggingface-hub (Model download)                          │
│  ├── Nuitka (Compilation release)                              │
│  ├── PyInstaller (Build dev)                                   │
│  └── Inno Setup (Windows installer)                            │
└─────────────────────────────────────────────────────────────────┘
```

### 11.2 Modèles ML Requis

| Modèle | Source | Taille | Usage |
|--------|--------|--------|-------|
| **faster-whisper-medium** | HuggingFace | ~1.5 Go | Transcription |
| **pyannote/speaker-diarization-3.1** | HuggingFace | ~500 Mo | Diarisation quality |
| **speechbrain/spkrec-ecapa-voxceleb** | HuggingFace | ~100 Mo | Diarisation fast |

### 11.3 Infrastructure Requise

| Composant | Requis | Usage |
|-----------|--------|-------|
| **Compte HuggingFace** | Oui (gratuit) | Accepter T&C Pyannote |
| **Token HuggingFace** | Oui | Téléchargement modèles |
| **Serveur de build** | Non | Build local possible |
| **CI/CD** | Optionnel | GitHub Actions recommandé |

---

## 12. Glossaire

| Terme | Définition |
|-------|------------|
| **ASR** | Automatic Speech Recognition - Reconnaissance automatique de la parole |
| **Diarisation** | Processus d'identification et de séparation des locuteurs dans un flux audio |
| **DER** | Diarization Error Rate - Taux d'erreur de diarisation (% temps mal attribué) |
| **WER** | Word Error Rate - Taux d'erreur mot (% mots incorrects dans transcription) |
| **RTF** | Real-Time Factor - Ratio temps de traitement / durée audio |
| **Whisper** | Modèle ASR d'OpenAI, base de faster-whisper |
| **Pyannote** | Framework Python pour analyse audio et diarisation |
| **faster-whisper** | Implémentation optimisée de Whisper via CTranslate2 |
| **CTranslate2** | Moteur d'inférence optimisé pour transformers |
| **SpeechBrain** | Toolkit open-source pour traitement de la parole |
| **VAD** | Voice Activity Detection - Détection d'activité vocale |
| **Segment** | Portion de transcription avec timestamps et texte |
| **MVP** | Minimum Viable Product - Produit minimum viable |
| **P0/P1/P2** | Niveaux de priorité (P0 = critique, P1 = important, P2 = souhaitable) |
| **RGPD** | Règlement Général sur la Protection des Données |

---

## Historique des Révisions

| Version | Date | Auteur | Modifications |
|---------|------|--------|---------------|
| 1.0.0 | 2026-01-14 | PM Agent (BMAD) | Création initiale du PRD |

---

## Références

- [BMAD Methodology](https://docs.bmad-method.org/)
- [faster-whisper Documentation](https://github.com/SYSTRAN/faster-whisper)
- [Pyannote Audio Documentation](https://github.com/pyannote/pyannote-audio)
- [PySide6 Documentation](https://doc.qt.io/qtforpython-6/)

---

**Document suivant:** [FUNCTIONAL_REQUIREMENTS.md](./FUNCTIONAL_REQUIREMENTS.md)
