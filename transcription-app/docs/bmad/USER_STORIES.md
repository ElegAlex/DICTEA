# DICTEA - User Stories & Epics

**Version:** 1.0.0
**Date:** 2026-01-14
**Référence PRD:** [PRD.md](./PRD.md)
**Méthodologie:** BMAD (Breakthrough Method for Agile AI-Driven Development)

---

## Table des matières

1. [Introduction](#1-introduction)
2. [Vue d'ensemble des Epics](#2-vue-densemble-des-epics)
3. [Epic 1: Gestion Audio](#3-epic-1-gestion-audio)
4. [Epic 2: Transcription](#4-epic-2-transcription)
5. [Epic 3: Diarisation](#5-epic-3-diarisation)
6. [Epic 4: Export](#6-epic-4-export)
7. [Epic 5: Interface Utilisateur](#7-epic-5-interface-utilisateur)
8. [Epic 6: Configuration](#8-epic-6-configuration)
9. [Epic 7: Gestion des Modèles](#9-epic-7-gestion-des-modèles)
10. [Backlog Priorisé](#10-backlog-priorisé)
11. [Definition of Done](#11-definition-of-done)

---

## 1. Introduction

### 1.1 Objectif du Document

Ce document définit les User Stories organisées par Epics pour le développement de DICTEA. Chaque User Story suit le format standard et inclut les critères d'acceptation détaillés.

### 1.2 Format User Story

```
En tant que [PERSONA],
Je veux [ACTION/FONCTIONNALITÉ],
Afin de [BÉNÉFICE/VALEUR].
```

### 1.3 Estimation - Story Points

| Points | Complexité | Durée estimée |
|--------|------------|---------------|
| **1** | Trivial | < 2h |
| **2** | Simple | 2-4h |
| **3** | Modéré | 4-8h |
| **5** | Complexe | 1-2 jours |
| **8** | Très complexe | 2-3 jours |
| **13** | Épique | 3-5 jours |

### 1.4 Priorité MoSCoW

| Priorité | Description |
|----------|-------------|
| **Must** | Indispensable au MVP |
| **Should** | Important mais non bloquant |
| **Could** | Souhaitable si temps disponible |
| **Won't** | Hors scope MVP |

---

## 2. Vue d'ensemble des Epics

```
┌─────────────────────────────────────────────────────────────────┐
│                    ROADMAP EPICS MVP                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   PHASE 1: Fondations                                          │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│   │   E1        │  │   E7        │  │   E5        │           │
│   │   Gestion   │  │   Gestion   │  │   Interface │           │
│   │   Audio     │  │   Modèles   │  │   Base      │           │
│   │   (21 pts)  │  │   (13 pts)  │  │   (18 pts)  │           │
│   └─────────────┘  └─────────────┘  └─────────────┘           │
│                                                                 │
│   PHASE 2: Core ML                                             │
│   ┌─────────────┐  ┌─────────────┐                            │
│   │   E2        │  │   E3        │                            │
│   │   Trans-    │  │   Diari-    │                            │
│   │   cription  │  │   sation    │                            │
│   │   (26 pts)  │  │   (29 pts)  │                            │
│   └─────────────┘  └─────────────┘                            │
│                                                                 │
│   PHASE 3: Polish                                              │
│   ┌─────────────┐  ┌─────────────┐                            │
│   │   E4        │  │   E6        │                            │
│   │   Export    │  │   Config    │                            │
│   │   (13 pts)  │  │   (11 pts)  │                            │
│   └─────────────┘  └─────────────┘                            │
│                                                                 │
│   TOTAL MVP: ~131 Story Points                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Résumé des Epics

| Epic | Nom | Stories | Points | Priorité |
|------|-----|---------|--------|----------|
| **E1** | Gestion Audio | 7 | 21 | Must |
| **E2** | Transcription | 6 | 26 | Must |
| **E3** | Diarisation | 6 | 29 | Must |
| **E4** | Export | 4 | 13 | Must |
| **E5** | Interface Utilisateur | 5 | 18 | Must |
| **E6** | Configuration | 4 | 11 | Should |
| **E7** | Gestion Modèles | 4 | 13 | Must |
| **TOTAL** | | **36** | **131** | |

---

## 3. Epic 1: Gestion Audio

### E1 - Description

**Objectif:** Permettre l'acquisition et le prétraitement des données audio pour la transcription.

**Valeur métier:** Sans entrée audio, aucune transcription n'est possible. Cet epic est le point d'entrée du workflow.

---

### US-1.1: Import fichier audio

| Attribut | Valeur |
|----------|--------|
| **ID** | US-1.1 |
| **Epic** | E1 - Gestion Audio |
| **Priorité** | Must |
| **Points** | 3 |
| **FR associée** | FR-1.1 |

#### User Story

```
En tant qu'utilisateur,
Je veux importer un fichier audio depuis mon ordinateur,
Afin de le transcrire sans avoir à l'enregistrer moi-même.
```

#### Critères d'acceptation

- [ ] **AC-1:** Un bouton "Ouvrir un fichier" est visible sur l'interface principale
- [ ] **AC-2:** Cliquer ouvre une boîte de dialogue Windows standard
- [ ] **AC-3:** Le filtre affiche uniquement: WAV, MP3, M4A, FLAC, OGG, WMA, AAC
- [ ] **AC-4:** Après sélection, le chemin du fichier s'affiche dans l'interface
- [ ] **AC-5:** Un fichier au format non supporté affiche un message d'erreur explicite

#### Scénarios de test

```gherkin
Scenario: Import d'un fichier MP3 valide
  Given l'application est démarrée
  When je clique sur "Ouvrir un fichier"
  And je sélectionne "interview.mp3"
  Then le chemin "interview.mp3" s'affiche
  And les métadonnées audio sont visibles

Scenario: Import d'un fichier non supporté
  Given l'application est démarrée
  When je tente d'ouvrir "video.avi"
  Then un message d'erreur s'affiche
  And le message indique les formats supportés
```

#### Notes techniques

- Utiliser `QFileDialog.getOpenFileName()` de PySide6
- Valider l'extension avant traitement
- Stocker le chemin dans l'état de l'application

---

### US-1.2: Validation format audio

| Attribut | Valeur |
|----------|--------|
| **ID** | US-1.2 |
| **Epic** | E1 - Gestion Audio |
| **Priorité** | Must |
| **Points** | 2 |
| **FR associée** | FR-1.1 |

#### User Story

```
En tant qu'utilisateur,
Je veux être informé si mon fichier audio n'est pas valide,
Afin de ne pas perdre de temps avec un fichier corrompu.
```

#### Critères d'acceptation

- [ ] **AC-1:** Les fichiers corrompus sont détectés avant traitement
- [ ] **AC-2:** Un message explicite indique le type de problème
- [ ] **AC-3:** L'application ne crash pas sur fichier invalide
- [ ] **AC-4:** L'utilisateur peut sélectionner un autre fichier

#### Notes techniques

- Utiliser `soundfile` pour valider le header
- Catch les exceptions et les transformer en messages utilisateur

---

### US-1.3: Enregistrement microphone

| Attribut | Valeur |
|----------|--------|
| **ID** | US-1.3 |
| **Epic** | E1 - Gestion Audio |
| **Priorité** | Must |
| **Points** | 5 |
| **FR associée** | FR-1.2 |

#### User Story

```
En tant qu'utilisateur,
Je veux enregistrer directement depuis mon microphone,
Afin de transcrire une conversation ou un dictée en direct.
```

#### Critères d'acceptation

- [ ] **AC-1:** Un bouton "Enregistrer" démarre la capture audio
- [ ] **AC-2:** Un indicateur visuel (cercle rouge) montre que l'enregistrement est actif
- [ ] **AC-3:** La durée d'enregistrement s'affiche en temps réel (MM:SS)
- [ ] **AC-4:** Un bouton "Arrêter" stoppe l'enregistrement
- [ ] **AC-5:** Le fichier est automatiquement sauvegardé en WAV
- [ ] **AC-6:** L'enregistrement utilise le micro par défaut du système

#### Scénarios de test

```gherkin
Scenario: Enregistrement de 30 secondes
  Given l'application est démarrée
  And un microphone est connecté
  When je clique sur "Enregistrer"
  Then l'indicateur rouge s'affiche
  And le compteur commence à 00:00
  When j'attends 30 secondes
  And je clique sur "Arrêter"
  Then un fichier WAV est créé
  And sa durée est d'environ 30 secondes

Scenario: Pas de microphone
  Given l'application est démarrée
  And aucun microphone n'est connecté
  When je clique sur "Enregistrer"
  Then un message d'erreur s'affiche
  And le message suggère de vérifier le microphone
```

#### Notes techniques

- Utiliser `sounddevice` pour la capture
- Sample rate: 16000 Hz, mono, 16-bit
- Thread séparé pour ne pas bloquer l'UI

---

### US-1.4: Annulation enregistrement

| Attribut | Valeur |
|----------|--------|
| **ID** | US-1.4 |
| **Epic** | E1 - Gestion Audio |
| **Priorité** | Should |
| **Points** | 2 |
| **FR associée** | FR-1.2 |

#### User Story

```
En tant qu'utilisateur,
Je veux pouvoir annuler un enregistrement en cours,
Afin de recommencer si je me suis trompé.
```

#### Critères d'acceptation

- [ ] **AC-1:** Un bouton "Annuler" est visible pendant l'enregistrement
- [ ] **AC-2:** Cliquer supprime l'enregistrement en cours
- [ ] **AC-3:** L'interface revient à l'état initial
- [ ] **AC-4:** Aucun fichier temporaire ne persiste

---

### US-1.5: Conversion format audio

| Attribut | Valeur |
|----------|--------|
| **ID** | US-1.5 |
| **Epic** | E1 - Gestion Audio |
| **Priorité** | Must |
| **Points** | 3 |
| **FR associée** | FR-1.3 |

#### User Story

```
En tant que système,
Je veux convertir automatiquement l'audio au format optimal,
Afin de garantir la compatibilité avec le moteur de transcription.
```

#### Critères d'acceptation

- [ ] **AC-1:** Tout fichier est converti en 16kHz mono PCM
- [ ] **AC-2:** La conversion est transparente pour l'utilisateur
- [ ] **AC-3:** Le fichier original n'est pas modifié
- [ ] **AC-4:** Les fichiers déjà au bon format ne sont pas reconvertis

#### Notes techniques

- Utiliser `pydub` pour la conversion
- Fichier temporaire dans `temp/`
- Nettoyage après traitement

---

### US-1.6: Affichage métadonnées

| Attribut | Valeur |
|----------|--------|
| **ID** | US-1.6 |
| **Epic** | E1 - Gestion Audio |
| **Priorité** | Should |
| **Points** | 3 |
| **FR associée** | FR-1.4 |

#### User Story

```
En tant qu'utilisateur,
Je veux voir les informations de mon fichier audio,
Afin de vérifier que j'ai sélectionné le bon fichier.
```

#### Critères d'acceptation

- [ ] **AC-1:** La durée est affichée au format HH:MM:SS
- [ ] **AC-2:** Le format du fichier est indiqué (MP3, WAV, etc.)
- [ ] **AC-3:** La taille du fichier est affichée (Mo)
- [ ] **AC-4:** Le sample rate est indiqué
- [ ] **AC-5:** Les informations sont mises à jour à chaque nouveau fichier

---

### US-1.7: Découpage fichiers longs

| Attribut | Valeur |
|----------|--------|
| **ID** | US-1.7 |
| **Epic** | E1 - Gestion Audio |
| **Priorité** | Could |
| **Points** | 3 |
| **FR associée** | FR-1.5 |

#### User Story

```
En tant que système,
Je veux découper automatiquement les fichiers longs,
Afin d'optimiser l'utilisation mémoire pendant le traitement.
```

#### Critères d'acceptation

- [ ] **AC-1:** Les fichiers > 30 min sont découpés en chunks
- [ ] **AC-2:** Le découpage est transparent pour l'utilisateur
- [ ] **AC-3:** Les résultats sont fusionnés automatiquement
- [ ] **AC-4:** Le découpage respecte les silences (pas de coupe mid-phrase)

---

## 4. Epic 2: Transcription

### E2 - Description

**Objectif:** Convertir l'audio en texte avec horodatage précis.

**Valeur métier:** C'est la fonctionnalité centrale de l'application, sans laquelle le produit n'a pas de raison d'être.

---

### US-2.1: Transcription audio

| Attribut | Valeur |
|----------|--------|
| **ID** | US-2.1 |
| **Epic** | E2 - Transcription |
| **Priorité** | Must |
| **Points** | 8 |
| **FR associée** | FR-2.1 |

#### User Story

```
En tant qu'utilisateur,
Je veux transcrire mon audio en texte français,
Afin d'obtenir une version écrite de l'enregistrement.
```

#### Critères d'acceptation

- [ ] **AC-1:** Le bouton "Transcrire" lance le traitement
- [ ] **AC-2:** Le texte français est généré avec ponctuation automatique
- [ ] **AC-3:** La qualité atteint un WER ≤ 10% sur corpus test
- [ ] **AC-4:** Le traitement fonctionne 100% offline
- [ ] **AC-5:** Les chiffres et noms propres courants sont reconnus

#### Scénarios de test

```gherkin
Scenario: Transcription d'un fichier de 5 minutes
  Given un fichier audio de 5 minutes en français
  When je clique sur "Transcrire"
  Then le traitement démarre
  And une barre de progression s'affiche
  And le résultat textuel apparaît après ~5-7 minutes
  And le texte contient la ponctuation

Scenario: Transcription offline
  Given la connexion internet est désactivée
  And les modèles sont en cache
  When je lance une transcription
  Then le traitement se termine avec succès
```

#### Notes techniques

- Utiliser `faster-whisper` avec modèle `medium`
- Compute type: `int8` pour optimisation CPU
- Beam size: 5

---

### US-2.2: Qualité transcription

| Attribut | Valeur |
|----------|--------|
| **ID** | US-2.2 |
| **Epic** | E2 - Transcription |
| **Priorité** | Must |
| **Points** | 3 |
| **FR associée** | FR-2.1 |

#### User Story

```
En tant qu'utilisateur professionnel,
Je veux une transcription de qualité professionnelle,
Afin de l'utiliser dans mes documents officiels.
```

#### Critères d'acceptation

- [ ] **AC-1:** WER ≤ 8% sur le corpus Common Voice français
- [ ] **AC-2:** La ponctuation est générée automatiquement
- [ ] **AC-3:** Les mots techniques courants sont reconnus
- [ ] **AC-4:** Les hésitations et répétitions sont préservées

---

### US-2.3: Timestamps segments

| Attribut | Valeur |
|----------|--------|
| **ID** | US-2.3 |
| **Epic** | E2 - Transcription |
| **Priorité** | Must |
| **Points** | 3 |
| **FR associée** | FR-2.2 |

#### User Story

```
En tant qu'utilisateur,
Je veux voir les timestamps de chaque segment,
Afin de retrouver facilement un passage dans l'audio original.
```

#### Critères d'acceptation

- [ ] **AC-1:** Chaque segment a un timestamp de début et fin
- [ ] **AC-2:** Format d'affichage: [HH:MM:SS - HH:MM:SS]
- [ ] **AC-3:** Précision des timestamps ≤ 200ms
- [ ] **AC-4:** Les timestamps sont inclus dans l'export

---

### US-2.4: Progression temps réel

| Attribut | Valeur |
|----------|--------|
| **ID** | US-2.4 |
| **Epic** | E2 - Transcription |
| **Priorité** | Must |
| **Points** | 5 |
| **FR associée** | FR-2.3 |

#### User Story

```
En tant qu'utilisateur,
Je veux voir la progression de la transcription,
Afin de savoir combien de temps il reste à attendre.
```

#### Critères d'acceptation

- [ ] **AC-1:** Une barre de progression affiche le pourcentage (0-100%)
- [ ] **AC-2:** Le temps écoulé est affiché
- [ ] **AC-3:** Le temps restant estimé est affiché
- [ ] **AC-4:** L'étape courante est décrite (Transcription, Diarisation, etc.)
- [ ] **AC-5:** Les segments transcrits s'affichent progressivement

#### Notes techniques

- Signal Qt `progress(int)` toutes les 2 secondes
- Calcul du temps restant basé sur le RTF observé

---

### US-2.5: Annulation transcription

| Attribut | Valeur |
|----------|--------|
| **ID** | US-2.5 |
| **Epic** | E2 - Transcription |
| **Priorité** | Must |
| **Points** | 3 |
| **FR associée** | FR-2.4 |

#### User Story

```
En tant qu'utilisateur,
Je veux pouvoir annuler une transcription en cours,
Afin de ne pas attendre si j'ai fait une erreur.
```

#### Critères d'acceptation

- [ ] **AC-1:** Un bouton "Annuler" est visible pendant le traitement
- [ ] **AC-2:** L'annulation stoppe le traitement en ≤ 5 secondes
- [ ] **AC-3:** Les ressources (RAM, modèle) sont libérées
- [ ] **AC-4:** Un message confirme l'annulation
- [ ] **AC-5:** L'interface revient à l'état initial

---

### US-2.6: Détection langue

| Attribut | Valeur |
|----------|--------|
| **ID** | US-2.6 |
| **Epic** | E2 - Transcription |
| **Priorité** | Could |
| **Points** | 2 |
| **FR associée** | FR-2.5 |

#### User Story

```
En tant qu'utilisateur,
Je veux que la langue soit détectée automatiquement,
Afin de ne pas avoir à la spécifier manuellement.
```

#### Critères d'acceptation

- [ ] **AC-1:** Si langue = "Auto", détection sur les 30 premières secondes
- [ ] **AC-2:** Le score de confiance est affiché
- [ ] **AC-3:** L'utilisateur peut corriger la détection
- [ ] **AC-4:** Français détecté avec > 95% de précision

---

## 5. Epic 3: Diarisation

### E3 - Description

**Objectif:** Identifier et attribuer les segments de parole aux différents locuteurs.

**Valeur métier:** La diarisation différencie DICTEA des outils de transcription basiques en permettant d'identifier "qui a dit quoi".

---

### US-3.1: Identification locuteurs

| Attribut | Valeur |
|----------|--------|
| **ID** | US-3.1 |
| **Epic** | E3 - Diarisation |
| **Priorité** | Must |
| **Points** | 8 |
| **FR associée** | FR-3.1 |

#### User Story

```
En tant qu'utilisateur,
Je veux que les différents locuteurs soient identifiés,
Afin de savoir qui a dit quoi dans la transcription.
```

#### Critères d'acceptation

- [ ] **AC-1:** Le système détecte automatiquement le nombre de locuteurs (1-10)
- [ ] **AC-2:** Chaque locuteur reçoit un identifiant unique (SPEAKER_00, SPEAKER_01, etc.)
- [ ] **AC-3:** Le DER (Diarization Error Rate) est ≤ 15%
- [ ] **AC-4:** Le nombre de locuteurs détectés est affiché
- [ ] **AC-5:** La même voix est regroupée sous le même identifiant

#### Scénarios de test

```gherkin
Scenario: Diarisation d'une conversation à 2 personnes
  Given un fichier audio avec 2 locuteurs distincts
  When je lance la transcription avec diarisation
  Then 2 locuteurs sont identifiés
  And les segments sont correctement attribués
  And le DER est < 15%

Scenario: Diarisation d'une réunion à 5 personnes
  Given un fichier audio d'une réunion à 5 personnes
  When je lance la transcription avec diarisation
  Then 5 locuteurs sont identifiés
  And le DER est < 20%
```

---

### US-3.2: Attribution segments-locuteurs

| Attribut | Valeur |
|----------|--------|
| **ID** | US-3.2 |
| **Epic** | E3 - Diarisation |
| **Priorité** | Must |
| **Points** | 5 |
| **FR associée** | FR-3.2 |

#### User Story

```
En tant qu'utilisateur,
Je veux que chaque phrase soit attribuée à un locuteur,
Afin de pouvoir suivre la conversation facilement.
```

#### Critères d'acceptation

- [ ] **AC-1:** Chaque segment transcrit est associé à un locuteur
- [ ] **AC-2:** L'attribution se base sur le chevauchement temporel maximal
- [ ] **AC-3:** Les segments sans locuteur clair sont marqués "UNKNOWN"
- [ ] **AC-4:** L'identifiant locuteur est affiché avant chaque segment

---

### US-3.3: Mode qualité

| Attribut | Valeur |
|----------|--------|
| **ID** | US-3.3 |
| **Epic** | E3 - Diarisation |
| **Priorité** | Must |
| **Points** | 5 |
| **FR associée** | FR-3.3 |

#### User Story

```
En tant qu'utilisateur exigeant,
Je veux choisir un mode de diarisation haute qualité,
Afin d'obtenir une attribution précise des locuteurs.
```

#### Critères d'acceptation

- [ ] **AC-1:** Le mode "Qualité" utilise Pyannote 3.1
- [ ] **AC-2:** Le DER en mode qualité est ≤ 12%
- [ ] **AC-3:** Le temps de traitement est affiché (estimé 2-3h/h audio)
- [ ] **AC-4:** Les chevauchements de parole sont gérés

#### Notes techniques

- Modèle: `pyannote/speaker-diarization-3.1`
- Requiert token HuggingFace
- RAM: ~4 Go supplémentaires

---

### US-3.4: Mode rapide

| Attribut | Valeur |
|----------|--------|
| **ID** | US-3.4 |
| **Epic** | E3 - Diarisation |
| **Priorité** | Should |
| **Points** | 5 |
| **FR associée** | FR-3.3 |

#### User Story

```
En tant qu'utilisateur pressé,
Je veux un mode de diarisation rapide,
Afin d'obtenir un résultat plus vite même si moins précis.
```

#### Critères d'acceptation

- [ ] **AC-1:** Le mode "Rapide" utilise SpeechBrain
- [ ] **AC-2:** Le temps de traitement est ~3-4x plus rapide
- [ ] **AC-3:** Le DER en mode rapide est ≤ 20%
- [ ] **AC-4:** Un message indique le compromis qualité/vitesse

#### Notes techniques

- Modèle: `speechbrain/spkrec-ecapa-voxceleb`
- Clustering: AHC ou spectral
- RAM: ~2 Go supplémentaires

---

### US-3.5: Nombre locuteurs

| Attribut | Valeur |
|----------|--------|
| **ID** | US-3.5 |
| **Epic** | E3 - Diarisation |
| **Priorité** | Should |
| **Points** | 3 |
| **FR associée** | FR-3.4 |

#### User Story

```
En tant qu'utilisateur,
Je veux pouvoir indiquer le nombre de locuteurs attendus,
Afin d'améliorer la précision de la diarisation.
```

#### Critères d'acceptation

- [ ] **AC-1:** Un champ permet de saisir le nombre min/max de locuteurs
- [ ] **AC-2:** "Auto" (0) est la valeur par défaut
- [ ] **AC-3:** La plage acceptée est 1-20
- [ ] **AC-4:** Le paramètre est transmis au modèle de diarisation

---

### US-3.6: Gestion chevauchements

| Attribut | Valeur |
|----------|--------|
| **ID** | US-3.6 |
| **Epic** | E3 - Diarisation |
| **Priorité** | Could |
| **Points** | 3 |
| **FR associée** | FR-3.5 |

#### User Story

```
En tant qu'utilisateur,
Je veux être informé quand plusieurs personnes parlent en même temps,
Afin de comprendre les moments de discussion simultanée.
```

#### Critères d'acceptation

- [ ] **AC-1:** Les segments en chevauchement sont détectés
- [ ] **AC-2:** Un indicateur "[OVERLAP]" est affiché
- [ ] **AC-3:** Disponible uniquement en mode Qualité

---

## 6. Epic 4: Export

### E4 - Description

**Objectif:** Permettre l'exploitation des transcriptions dans des formats standards.

**Valeur métier:** Sans export, les transcriptions restent inutilisables. L'export est le point de sortie du workflow.

---

### US-4.1: Export TXT

| Attribut | Valeur |
|----------|--------|
| **ID** | US-4.1 |
| **Epic** | E4 - Export |
| **Priorité** | Must |
| **Points** | 3 |
| **FR associée** | FR-4.1 |

#### User Story

```
En tant qu'utilisateur,
Je veux exporter la transcription en fichier TXT,
Afin de l'utiliser dans Word ou un autre éditeur.
```

#### Critères d'acceptation

- [ ] **AC-1:** Un bouton "Sauver TXT" ouvre une boîte de dialogue
- [ ] **AC-2:** Le format inclut timestamps et locuteurs
- [ ] **AC-3:** L'encodage est UTF-8
- [ ] **AC-4:** Le nom par défaut inclut le nom du fichier source
- [ ] **AC-5:** Le fichier est compatible avec Word, Notepad, etc.

#### Format de sortie

```
[00:00:00 - 00:00:15] SPEAKER_00
Bonjour à tous, bienvenue dans cette réunion.

[00:00:15 - 00:00:45] SPEAKER_01
Merci. Ce mois-ci nous avons atteint 120% des objectifs.
```

---

### US-4.2: Export SRT

| Attribut | Valeur |
|----------|--------|
| **ID** | US-4.2 |
| **Epic** | E4 - Export |
| **Priorité** | Must |
| **Points** | 3 |
| **FR associée** | FR-4.2 |

#### User Story

```
En tant que créateur de contenu,
Je veux exporter en format SRT,
Afin d'ajouter des sous-titres à mes vidéos/podcasts.
```

#### Critères d'acceptation

- [ ] **AC-1:** Un bouton "Sauver SRT" ouvre une boîte de dialogue
- [ ] **AC-2:** Le format respecte la spécification SRT
- [ ] **AC-3:** Les timestamps sont au format HH:MM:SS,mmm
- [ ] **AC-4:** Le locuteur est indiqué au début de chaque sous-titre
- [ ] **AC-5:** Le fichier est compatible VLC, YouTube, etc.

#### Format de sortie

```srt
1
00:00:00,000 --> 00:00:15,340
[SPEAKER_00] Bonjour à tous, bienvenue dans cette réunion.

2
00:00:15,340 --> 00:00:45,120
[SPEAKER_01] Merci. Ce mois-ci nous avons atteint 120% des objectifs.
```

---

### US-4.3: Copie presse-papiers

| Attribut | Valeur |
|----------|--------|
| **ID** | US-4.3 |
| **Epic** | E4 - Export |
| **Priorité** | Must |
| **Points** | 2 |
| **FR associée** | FR-4.3 |

#### User Story

```
En tant qu'utilisateur,
Je veux copier la transcription dans le presse-papiers,
Afin de la coller rapidement dans un autre document.
```

#### Critères d'acceptation

- [ ] **AC-1:** Un bouton "Copier" copie tout le texte
- [ ] **AC-2:** Le format est identique au TXT
- [ ] **AC-3:** Une notification confirme la copie
- [ ] **AC-4:** Le raccourci Ctrl+C fonctionne sur la zone de texte

---

### US-4.4: Options formatage

| Attribut | Valeur |
|----------|--------|
| **ID** | US-4.4 |
| **Epic** | E4 - Export |
| **Priorité** | Could |
| **Points** | 5 |
| **FR associée** | FR-4.4 |

#### User Story

```
En tant qu'utilisateur,
Je veux personnaliser le format d'export,
Afin d'adapter le résultat à mes besoins.
```

#### Critères d'acceptation

- [ ] **AC-1:** Option pour inclure/exclure les timestamps
- [ ] **AC-2:** Option pour inclure/exclure les identifiants locuteurs
- [ ] **AC-3:** Option pour le format timestamps (HH:MM:SS vs secondes)
- [ ] **AC-4:** Les préférences sont sauvegardées

---

## 7. Epic 5: Interface Utilisateur

### E5 - Description

**Objectif:** Fournir une interface intuitive et réactive pour toutes les fonctionnalités.

**Valeur métier:** L'UI est le point de contact entre l'utilisateur et le système. Une UI intuitive réduit la friction et augmente l'adoption.

---

### US-5.1: Fenêtre principale

| Attribut | Valeur |
|----------|--------|
| **ID** | US-5.1 |
| **Epic** | E5 - Interface Utilisateur |
| **Priorité** | Must |
| **Points** | 5 |
| **FR associée** | FR-5.1 |

#### User Story

```
En tant qu'utilisateur,
Je veux une interface claire et organisée,
Afin de trouver facilement les fonctionnalités dont j'ai besoin.
```

#### Critères d'acceptation

- [ ] **AC-1:** La fenêtre utilise les widgets natifs Windows (PySide6)
- [ ] **AC-2:** Le layout s'adapte au redimensionnement
- [ ] **AC-3:** Taille minimale: 800x600 pixels
- [ ] **AC-4:** L'icône est visible dans la barre des tâches
- [ ] **AC-5:** Les sections sont clairement délimitées (Source, Options, Résultat)

#### Wireframe

```
┌─────────────────────────────────────────────────────────────────┐
│  DICTEA - Transcription Audio Offline                      [_][□][X] │
├─────────────────────────────────────────────────────────────────┤
│  ┌─ SOURCE AUDIO ─────────────┐  ┌─ OPTIONS ──────────────────┐ │
│  │                            │  │                             │ │
│  │  [Ouvrir fichier]          │  │  Langue: [Français    ▼]   │ │
│  │  [Enregistrer]  [Stop]     │  │  Mode:   [Qualité     ▼]   │ │
│  │                            │  │  Locuteurs: [Auto     ▼]   │ │
│  │  Fichier: aucun            │  │                             │ │
│  │  Durée: --:--:--           │  │  [    TRANSCRIRE    ]       │ │
│  └────────────────────────────┘  └─────────────────────────────┘ │
│  ┌─ PROGRESSION ─────────────────────────────────────────────────┐ │
│  │  [████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░]  35%             │ │
│  │  Transcription en cours... ~25:00 restantes                  │ │
│  └───────────────────────────────────────────────────────────────┘ │
│  ┌─ RÉSULTAT ────────────────────────────────────────────────────┐ │
│  │                                                               │ │
│  │  [00:00:00 - 00:00:15] SPEAKER_00                            │ │
│  │  Bonjour à tous, bienvenue dans cette réunion...             │ │
│  │                                                               │ │
│  │  [00:00:15 - 00:00:45] SPEAKER_01                            │ │
│  │  Merci. Ce mois-ci nous avons atteint...                     │ │
│  │                                                               │ │
│  └───────────────────────────────────────────────────────────────┘ │
│  [Copier]  [Sauver TXT]  [Sauver SRT]                              │
├─────────────────────────────────────────────────────────────────────┤
│  Prêt                                                               │
└─────────────────────────────────────────────────────────────────────┘
```

---

### US-5.2: Barre de progression

| Attribut | Valeur |
|----------|--------|
| **ID** | US-5.2 |
| **Epic** | E5 - Interface Utilisateur |
| **Priorité** | Must |
| **Points** | 3 |
| **FR associée** | FR-5.2 |

#### User Story

```
En tant qu'utilisateur,
Je veux voir une barre de progression pendant le traitement,
Afin de savoir où en est le processus.
```

#### Critères d'acceptation

- [ ] **AC-1:** Barre de progression avec pourcentage (0-100%)
- [ ] **AC-2:** Mise à jour au moins toutes les 2 secondes
- [ ] **AC-3:** Étape courante affichée (Transcription/Diarisation)
- [ ] **AC-4:** Temps restant estimé
- [ ] **AC-5:** Progression visible dans la taskbar Windows

---

### US-5.3: Interface non-bloquante

| Attribut | Valeur |
|----------|--------|
| **ID** | US-5.3 |
| **Epic** | E5 - Interface Utilisateur |
| **Priorité** | Must |
| **Points** | 5 |
| **FR associée** | FR-5.3 |

#### User Story

```
En tant qu'utilisateur,
Je veux que l'interface reste réactive pendant le traitement,
Afin de pouvoir interagir avec l'application (annuler, etc.).
```

#### Critères d'acceptation

- [ ] **AC-1:** L'UI ne se fige jamais (pas de "Not Responding")
- [ ] **AC-2:** Le bouton Annuler reste cliquable
- [ ] **AC-3:** La fenêtre peut être déplacée et redimensionnée
- [ ] **AC-4:** Latence d'interaction ≤ 100ms

#### Notes techniques

- Traitement ML dans un QThread séparé
- Communication via signaux Qt
- Main thread réservé à l'UI

---

### US-5.4: Affichage résultats

| Attribut | Valeur |
|----------|--------|
| **ID** | US-5.4 |
| **Epic** | E5 - Interface Utilisateur |
| **Priorité** | Must |
| **Points** | 3 |
| **FR associée** | FR-5.4 |

#### User Story

```
En tant qu'utilisateur,
Je veux voir les résultats de manière claire et structurée,
Afin de pouvoir lire et exploiter la transcription facilement.
```

#### Critères d'acceptation

- [ ] **AC-1:** Zone de texte scrollable pour les résultats
- [ ] **AC-2:** Format: [timestamp] SPEAKER_XX + texte
- [ ] **AC-3:** Les locuteurs ont des couleurs différentes (optionnel)
- [ ] **AC-4:** Le texte est sélectionnable et copiable
- [ ] **AC-5:** Police lisible (≥ 12pt)

---

### US-5.5: Messages d'erreur

| Attribut | Valeur |
|----------|--------|
| **ID** | US-5.5 |
| **Epic** | E5 - Interface Utilisateur |
| **Priorité** | Should |
| **Points** | 2 |
| **FR associée** | FR-5.5 |

#### User Story

```
En tant qu'utilisateur non-technique,
Je veux des messages d'erreur compréhensibles,
Afin de savoir quoi faire en cas de problème.
```

#### Critères d'acceptation

- [ ] **AC-1:** Messages en français, sans jargon technique
- [ ] **AC-2:** Suggestions de résolution incluses
- [ ] **AC-3:** Bouton "Détails" pour voir l'erreur technique
- [ ] **AC-4:** Erreurs loggées dans un fichier

---

## 8. Epic 6: Configuration

### E6 - Description

**Objectif:** Permettre la personnalisation du comportement de l'application.

**Valeur métier:** Les options de configuration permettent d'adapter l'outil aux besoins spécifiques de chaque utilisateur.

---

### US-6.1: Choix modèle

| Attribut | Valeur |
|----------|--------|
| **ID** | US-6.1 |
| **Epic** | E6 - Configuration |
| **Priorité** | Should |
| **Points** | 3 |
| **FR associée** | FR-6.1 |

#### User Story

```
En tant qu'utilisateur avancé,
Je veux choisir le modèle de transcription,
Afin d'ajuster le compromis qualité/performance.
```

#### Critères d'acceptation

- [ ] **AC-1:** Liste déroulante avec les modèles disponibles
- [ ] **AC-2:** Chaque modèle affiche sa taille et qualité estimée
- [ ] **AC-3:** Le modèle par défaut est "medium"
- [ ] **AC-4:** Le changement prend effet immédiatement

---

### US-6.2: Choix langue

| Attribut | Valeur |
|----------|--------|
| **ID** | US-6.2 |
| **Epic** | E6 - Configuration |
| **Priorité** | Should |
| **Points** | 2 |
| **FR associée** | FR-6.2 |

#### User Story

```
En tant qu'utilisateur,
Je veux spécifier la langue de mon audio,
Afin d'optimiser la qualité de transcription.
```

#### Critères d'acceptation

- [ ] **AC-1:** Liste déroulante avec les langues supportées
- [ ] **AC-2:** "Français" est la valeur par défaut
- [ ] **AC-3:** Option "Auto-détection" disponible

---

### US-6.3: Choix mode diarisation

| Attribut | Valeur |
|----------|--------|
| **ID** | US-6.3 |
| **Epic** | E6 - Configuration |
| **Priorité** | Should |
| **Points** | 2 |
| **FR associée** | FR-6.3 |

#### User Story

```
En tant qu'utilisateur,
Je veux choisir le mode de diarisation,
Afin d'équilibrer précision et rapidité.
```

#### Critères d'acceptation

- [ ] **AC-1:** Options: "Qualité", "Rapide", "Désactivé"
- [ ] **AC-2:** "Qualité" est la valeur par défaut
- [ ] **AC-3:** Une description explique le compromis

---

### US-6.4: Persistance préférences

| Attribut | Valeur |
|----------|--------|
| **ID** | US-6.4 |
| **Epic** | E6 - Configuration |
| **Priorité** | Could |
| **Points** | 4 |
| **FR associée** | FR-6.4 |

#### User Story

```
En tant qu'utilisateur régulier,
Je veux que mes préférences soient sauvegardées,
Afin de ne pas les reconfigurer à chaque lancement.
```

#### Critères d'acceptation

- [ ] **AC-1:** Les préférences sont sauvegardées à la fermeture
- [ ] **AC-2:** Les préférences sont restaurées au lancement
- [ ] **AC-3:** Fichier de config en YAML lisible
- [ ] **AC-4:** Bouton "Réinitialiser" pour restaurer les défauts

---

## 9. Epic 7: Gestion des Modèles

### E7 - Description

**Objectif:** Gérer le téléchargement, le stockage et le chargement des modèles ML.

**Valeur métier:** Sans les modèles ML, aucune transcription ni diarisation n'est possible. La gestion transparente des modèles est essentielle pour l'expérience utilisateur.

---

### US-7.1: Téléchargement modèles

| Attribut | Valeur |
|----------|--------|
| **ID** | US-7.1 |
| **Epic** | E7 - Gestion Modèles |
| **Priorité** | Must |
| **Points** | 5 |
| **FR associée** | FR-7.1 |

#### User Story

```
En tant que nouvel utilisateur,
Je veux que les modèles soient téléchargés automatiquement,
Afin de ne pas avoir à les installer manuellement.
```

#### Critères d'acceptation

- [ ] **AC-1:** Au premier lancement, détection des modèles manquants
- [ ] **AC-2:** Proposition de téléchargement avec taille estimée
- [ ] **AC-3:** Téléchargement depuis HuggingFace Hub
- [ ] **AC-4:** Barre de progression du téléchargement
- [ ] **AC-5:** Possibilité d'annuler le téléchargement
- [ ] **AC-6:** Gestion des erreurs réseau

---

### US-7.2: Cache local

| Attribut | Valeur |
|----------|--------|
| **ID** | US-7.2 |
| **Epic** | E7 - Gestion Modèles |
| **Priorité** | Must |
| **Points** | 3 |
| **FR associée** | FR-7.2 |

#### User Story

```
En tant que système,
Je veux mettre les modèles en cache localement,
Afin de ne pas les re-télécharger à chaque utilisation.
```

#### Critères d'acceptation

- [ ] **AC-1:** Les modèles sont stockés dans `models/`
- [ ] **AC-2:** Un modèle en cache n'est pas re-téléchargé
- [ ] **AC-3:** L'intégrité du cache peut être vérifiée
- [ ] **AC-4:** Option pour supprimer le cache

---

### US-7.3: Mode offline

| Attribut | Valeur |
|----------|--------|
| **ID** | US-7.3 |
| **Epic** | E7 - Gestion Modèles |
| **Priorité** | Must |
| **Points** | 3 |
| **FR associée** | FR-7.3 |

#### User Story

```
En tant qu'utilisateur sans internet,
Je veux que l'application fonctionne offline,
Afin de transcrire même sans connexion.
```

#### Critères d'acceptation

- [ ] **AC-1:** Si modèles présents, aucune connexion requise
- [ ] **AC-2:** L'application démarre sans internet
- [ ] **AC-3:** Aucun appel réseau pendant la transcription
- [ ] **AC-4:** Message clair si modèles manquants

---

### US-7.4: Progression téléchargement

| Attribut | Valeur |
|----------|--------|
| **ID** | US-7.4 |
| **Epic** | E7 - Gestion Modèles |
| **Priorité** | Should |
| **Points** | 2 |
| **FR associée** | FR-7.4 |

#### User Story

```
En tant qu'utilisateur,
Je veux voir la progression du téléchargement des modèles,
Afin de savoir combien de temps il reste à attendre.
```

#### Critères d'acceptation

- [ ] **AC-1:** Barre de progression avec pourcentage
- [ ] **AC-2:** Taille téléchargée / taille totale
- [ ] **AC-3:** Vitesse de téléchargement
- [ ] **AC-4:** Temps restant estimé

---

## 10. Backlog Priorisé

### 10.1 Sprint 1: Fondations (Must)

| # | Story | Epic | Points | Dépendances |
|---|-------|------|--------|-------------|
| 1 | US-5.1 | E5 | 5 | - |
| 2 | US-1.1 | E1 | 3 | US-5.1 |
| 3 | US-1.2 | E1 | 2 | US-1.1 |
| 4 | US-1.5 | E1 | 3 | US-1.1 |
| 5 | US-7.1 | E7 | 5 | - |
| 6 | US-7.2 | E7 | 3 | US-7.1 |
| | **TOTAL** | | **21** | |

### 10.2 Sprint 2: Core Transcription (Must)

| # | Story | Epic | Points | Dépendances |
|---|-------|------|--------|-------------|
| 7 | US-2.1 | E2 | 8 | US-1.5, US-7.2 |
| 8 | US-2.3 | E2 | 3 | US-2.1 |
| 9 | US-2.4 | E2 | 5 | US-2.1 |
| 10 | US-5.3 | E5 | 5 | US-2.1 |
| | **TOTAL** | | **21** | |

### 10.3 Sprint 3: Diarisation (Must)

| # | Story | Epic | Points | Dépendances |
|---|-------|------|--------|-------------|
| 11 | US-3.1 | E3 | 8 | US-2.1 |
| 12 | US-3.2 | E3 | 5 | US-3.1 |
| 13 | US-3.3 | E3 | 5 | US-3.1 |
| 14 | US-2.5 | E2 | 3 | US-2.1 |
| | **TOTAL** | | **21** | |

### 10.4 Sprint 4: Export & Recording (Must)

| # | Story | Epic | Points | Dépendances |
|---|-------|------|--------|-------------|
| 15 | US-1.3 | E1 | 5 | US-5.1 |
| 16 | US-4.1 | E4 | 3 | US-2.1, US-3.2 |
| 17 | US-4.2 | E4 | 3 | US-2.1, US-3.2 |
| 18 | US-4.3 | E4 | 2 | US-4.1 |
| 19 | US-5.2 | E5 | 3 | US-2.4 |
| 20 | US-5.4 | E5 | 3 | US-2.1 |
| | **TOTAL** | | **19** | |

### 10.5 Sprint 5: Polish (Should/Could)

| # | Story | Epic | Points | Dépendances |
|---|-------|------|--------|-------------|
| 21 | US-1.4 | E1 | 2 | US-1.3 |
| 22 | US-1.6 | E1 | 3 | US-1.1 |
| 23 | US-3.4 | E3 | 5 | US-3.1 |
| 24 | US-3.5 | E3 | 3 | US-3.1 |
| 25 | US-5.5 | E5 | 2 | - |
| 26 | US-6.1 | E6 | 3 | - |
| 27 | US-6.2 | E6 | 2 | - |
| 28 | US-6.3 | E6 | 2 | - |
| 29 | US-7.3 | E7 | 3 | US-7.2 |
| 30 | US-7.4 | E7 | 2 | US-7.1 |
| | **TOTAL** | | **27** | |

### 10.6 Sprint 6: Nice-to-have (Could)

| # | Story | Epic | Points | Dépendances |
|---|-------|------|--------|-------------|
| 31 | US-1.7 | E1 | 3 | US-1.5 |
| 32 | US-2.2 | E2 | 3 | US-2.1 |
| 33 | US-2.6 | E2 | 2 | US-2.1 |
| 34 | US-3.6 | E3 | 3 | US-3.3 |
| 35 | US-4.4 | E4 | 5 | US-4.1 |
| 36 | US-6.4 | E6 | 4 | US-6.1-3 |
| | **TOTAL** | | **20** | |

---

## 11. Definition of Done

### 11.1 Definition of Done - User Story

Une User Story est considérée comme **Done** lorsque tous les critères suivants sont remplis:

| # | Critère | Obligatoire |
|---|---------|-------------|
| 1 | Tous les critères d'acceptation sont validés | ✅ Oui |
| 2 | Le code passe les tests unitaires | ✅ Oui |
| 3 | Le code est reviewé par un pair | ✅ Oui |
| 4 | Le code respecte les standards (PEP 8, type hints) | ✅ Oui |
| 5 | La documentation est mise à jour si nécessaire | ✅ Oui |
| 6 | Aucune régression introduite | ✅ Oui |
| 7 | La fonctionnalité est testable manuellement | ✅ Oui |

### 11.2 Definition of Done - Epic

Un Epic est considéré comme **Done** lorsque:

| # | Critère |
|---|---------|
| 1 | Toutes les User Stories "Must" sont Done |
| 2 | Les User Stories "Should" critiques sont Done |
| 3 | Les tests d'intégration passent |
| 4 | La fonctionnalité est utilisable de bout en bout |
| 5 | La documentation utilisateur est à jour |

### 11.3 Definition of Done - MVP

Le MVP est considéré comme **Done** lorsque:

| # | Critère |
|---|---------|
| 1 | Tous les Epics sont Done |
| 2 | Les NFRs P0 sont respectés |
| 3 | Le build de release est généré |
| 4 | L'installeur fonctionne sur Windows 10/11 |
| 5 | Les tests utilisateurs sont passés |
| 6 | La documentation est complète |

---

## Historique des Révisions

| Version | Date | Auteur | Modifications |
|---------|------|--------|---------------|
| 1.0.0 | 2026-01-14 | PM Agent (BMAD) | Création initiale |

---

**Retour au PRD:** [PRD.md](./PRD.md)
