# DICTEA - Non-Functional Requirements (NFRs)

**Version:** 1.0.0
**Date:** 2026-01-14
**Référence PRD:** [PRD.md](./PRD.md)
**Méthodologie:** BMAD (Breakthrough Method for Agile AI-Driven Development)

---

## Table des matières

1. [Introduction](#1-introduction)
2. [Convention de Notation](#2-convention-de-notation)
3. [Performance (PERF)](#3-performance-perf)
4. [Sécurité & Privacy (SEC)](#4-sécurité--privacy-sec)
5. [Fiabilité (REL)](#5-fiabilité-rel)
6. [Utilisabilité (USA)](#6-utilisabilité-usa)
7. [Maintenabilité (MNT)](#7-maintenabilité-mnt)
8. [Portabilité (PRT)](#8-portabilité-prt)
9. [Scalabilité (SCL)](#9-scalabilité-scl)
10. [Compatibilité (CMP)](#10-compatibilité-cmp)
11. [Matrice de Traçabilité](#11-matrice-de-traçabilité)

---

## 1. Introduction

### 1.1 Objectif du Document

Ce document définit l'ensemble des exigences non-fonctionnelles (Non-Functional Requirements - NFRs) de l'application DICTEA. Les NFRs décrivent **comment** le système doit se comporter, par opposition aux FRs qui décrivent **ce que** le système doit faire.

### 1.2 Importance des NFRs

Les NFRs sont critiques car elles définissent :
- **Qualité perçue** par l'utilisateur (performance, UX)
- **Viabilité technique** (maintenabilité, scalabilité)
- **Conformité réglementaire** (sécurité, privacy)
- **Exploitabilité** (déploiement, monitoring)

### 1.3 Documents Connexes

| Document | Description |
|----------|-------------|
| [PRD.md](./PRD.md) | Product Requirements Document |
| [FUNCTIONAL_REQUIREMENTS.md](./FUNCTIONAL_REQUIREMENTS.md) | Exigences fonctionnelles |
| [USER_STORIES.md](./USER_STORIES.md) | User Stories détaillées |

---

## 2. Convention de Notation

### 2.1 Format des Requirements

```
NFR-[CATEGORY]-[NUMBER]
│      │         │
│      │         └── Numéro séquentiel (01-99)
│      └── Code catégorie (PERF, SEC, REL, etc.)
└── Non-Functional Requirement
```

### 2.2 Catégories NFR

| Code | Catégorie | Description |
|------|-----------|-------------|
| **PERF** | Performance | Temps de réponse, throughput, ressources |
| **SEC** | Sécurité | Protection données, confidentialité, RGPD |
| **REL** | Fiabilité | Disponibilité, récupération, tolérance pannes |
| **USA** | Utilisabilité | Facilité d'usage, accessibilité, apprentissage |
| **MNT** | Maintenabilité | Modularité, testabilité, évolutivité |
| **PRT** | Portabilité | Compatibilité, installation, migration |
| **SCL** | Scalabilité | Limites, croissance, extensibilité |
| **CMP** | Compatibilité | Intégrations, formats, standards |

### 2.3 Niveaux de Priorité

| Priorité | Code | Description |
|----------|------|-------------|
| **Critical** | P0 | Bloquant pour release, indispensable |
| **High** | P1 | Dégradation majeure si absent |
| **Medium** | P2 | Améliore significativement l'expérience |
| **Low** | P3 | Nice-to-have, peut être différé |

### 2.4 Niveaux de Conformité

| Niveau | Description |
|--------|-------------|
| **MUST** | Obligation absolue, échec si non respecté |
| **SHOULD** | Fortement recommandé, exception justifiable |
| **MAY** | Optionnel, à la discrétion de l'implémentation |

---

## 3. Performance (PERF)

### 3.1 Vue d'ensemble

Les exigences de performance définissent les attentes en termes de temps de traitement, utilisation des ressources et réactivité du système.

```
┌─────────────────────────────────────────────────────────────────┐
│                    BUDGET PERFORMANCE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   TEMPS DE TRAITEMENT (1h audio)                               │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │ Transcription seule    │████████████│        ~1h        │  │
│   │ + Diarisation rapide   │████████████████│    ~1.5h      │  │
│   │ + Diarisation qualité  │████████████████████████│ ~3-4h │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│   UTILISATION MÉMOIRE                                          │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │ Baseline (idle)        │██│             ~500 Mo         │  │
│   │ Transcription active   │████████████│   ~4 Go           │  │
│   │ Pic (trans + diar)     │████████████████│ ~8 Go MAX     │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│   RÉACTIVITÉ UI                                                │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │ Clic → Feedback        │█│              <100ms          │  │
│   │ Update progression     │██│             <500ms          │  │
│   │ Affichage segment      │███│            <1s             │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### NFR-PERF-01: Ratio temps de traitement

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-PERF-01 |
| **Titre** | Real-Time Factor (RTF) de transcription |
| **Catégorie** | Performance |
| **Priorité** | P0 - Critical |

#### Description

Le système MUST atteindre un ratio temps de traitement / durée audio inférieur ou égal à 1.5x pour la transcription seule.

#### Spécifications

| Scénario | RTF Cible | RTF Maximum |
|----------|-----------|-------------|
| Transcription seule | ≤ 1.0x | 1.5x |
| Transcription + Diarisation rapide | ≤ 1.5x | 2.0x |
| Transcription + Diarisation qualité | ≤ 3.0x | 4.0x |

#### Conditions de mesure

- **CPU:** Intel i7-8700 ou équivalent
- **RAM:** 16 Go DDR4
- **Audio:** Fichier WAV 16kHz mono
- **Modèle:** faster-whisper medium
- **Durée test:** 30 minutes d'audio

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-PERF-01.1 | RTF transcription ≤ 1.5x sur CPU cible | ☐ |
| AC-PERF-01.2 | RTF total (trans+diar) ≤ 4x en mode qualité | ☐ |
| AC-PERF-01.3 | Benchmark reproductible sur 3 exécutions | ☐ |

#### Méthode de test

```python
def test_rtf_transcription():
    audio_duration = 1800  # 30 minutes en secondes
    start = time.time()
    transcribe(audio_file)
    elapsed = time.time() - start
    rtf = elapsed / audio_duration
    assert rtf <= 1.5, f"RTF {rtf:.2f}x exceeds limit"
```

---

### NFR-PERF-02: Utilisation mémoire RAM

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-PERF-02 |
| **Titre** | Pic d'utilisation mémoire |
| **Catégorie** | Performance |
| **Priorité** | P0 - Critical |

#### Description

Le système MUST limiter son utilisation mémoire RAM à un maximum de 8 Go pendant le traitement.

#### Spécifications

| Phase | RAM Min | RAM Max |
|-------|---------|---------|
| Idle (application démarrée) | 200 Mo | 500 Mo |
| Chargement modèle transcription | 2 Go | 4 Go |
| Transcription active | 3 Go | 5 Go |
| Diarisation active | 2 Go | 4 Go |
| **Pic (transcription + diarisation)** | 5 Go | **8 Go** |

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-PERF-02.1 | RAM pic ≤ 8 Go sur fichier 2h | ☐ |
| AC-PERF-02.2 | Pas de memory leak sur 10 transcriptions consécutives | ☐ |
| AC-PERF-02.3 | Garbage collection efficace après traitement | ☐ |

#### Stratégies d'optimisation

1. **Chargement lazy** des modèles
2. **Déchargement** après utilisation
3. **Garbage collection** agressif
4. **Chunking** des fichiers longs
5. **Quantification int8** des modèles

---

### NFR-PERF-03: Temps de démarrage

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-PERF-03 |
| **Titre** | Temps de lancement application |
| **Catégorie** | Performance |
| **Priorité** | P1 - High |

#### Description

Le système SHOULD démarrer et afficher l'interface utilisateur en moins de 10 secondes.

#### Spécifications

| Métrique | Cible | Maximum |
|----------|-------|---------|
| Cold start (premier lancement) | ≤ 8s | 15s |
| Warm start (relancement) | ≤ 5s | 10s |
| Affichage fenêtre | ≤ 3s | 5s |
| Application interactive | ≤ 10s | 15s |

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-PERF-03.1 | Fenêtre visible en ≤ 5s | ☐ |
| AC-PERF-03.2 | Application interactive en ≤ 10s | ☐ |
| AC-PERF-03.3 | Pas de chargement de modèle au démarrage | ☐ |

---

### NFR-PERF-04: Réactivité interface

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-PERF-04 |
| **Titre** | Latence d'interaction UI |
| **Catégorie** | Performance |
| **Priorité** | P0 - Critical |

#### Description

Le système MUST maintenir une latence d'interaction UI inférieure à 100ms pendant le traitement.

#### Spécifications

| Interaction | Latence Cible | Latence Max |
|-------------|---------------|-------------|
| Clic bouton → feedback visuel | ≤ 50ms | 100ms |
| Mise à jour barre progression | ≤ 500ms | 1000ms |
| Affichage nouveau segment | ≤ 200ms | 500ms |
| Scroll zone résultat | ≤ 16ms | 33ms (30 FPS) |
| Annulation → arrêt effectif | ≤ 2s | 5s |

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-PERF-04.1 | UI non bloquée pendant transcription | ☐ |
| AC-PERF-04.2 | Bouton Annuler toujours réactif | ☐ |
| AC-PERF-04.3 | Fenêtre déplaçable pendant traitement | ☐ |
| AC-PERF-04.4 | Pas de "Not Responding" Windows | ☐ |

---

### NFR-PERF-05: Utilisation CPU

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-PERF-05 |
| **Titre** | Optimisation de l'utilisation CPU |
| **Catégorie** | Performance |
| **Priorité** | P1 - High |

#### Description

Le système SHOULD utiliser efficacement les ressources CPU multi-cœur tout en laissant le système réactif.

#### Spécifications

| Métrique | Cible |
|----------|-------|
| Utilisation CPU pendant traitement | 70-90% |
| Threads alloués au ML | N-2 (N = cœurs logiques) |
| Thread UI réservé | 1 dédié |
| CPU idle max (sans traitement) | ≤ 5% |

#### Configuration recommandée

```yaml
performance:
  cpu_threads: 0        # Auto-détection (N-2)
  batch_size: 16        # Optimal pour CPU
  compute_type: "int8"  # Quantification CPU
```

---

## 4. Sécurité & Privacy (SEC)

### 4.1 Vue d'ensemble

Les exigences de sécurité et de confidentialité sont **fondamentales** pour DICTEA, dont la proposition de valeur principale est le traitement 100% local.

```
┌─────────────────────────────────────────────────────────────────┐
│                    MODÈLE DE SÉCURITÉ                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                    PÉRIMÈTRE LOCAL                       │  │
│   │                                                          │  │
│   │   ┌──────────┐    ┌──────────┐    ┌──────────┐         │  │
│   │   │  Audio   │───▶│  ML      │───▶│  Export  │         │  │
│   │   │  Input   │    │  Models  │    │  Files   │         │  │
│   │   └──────────┘    └──────────┘    └──────────┘         │  │
│   │                                                          │  │
│   │   ┌──────────┐    ┌──────────┐    ┌──────────┐         │  │
│   │   │  Temp    │    │  Config  │    │  Logs    │         │  │
│   │   │  Files   │    │  YAML    │    │  (local) │         │  │
│   │   └──────────┘    └──────────┘    └──────────┘         │  │
│   │                                                          │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              ║                                  │
│                              ║ AUCUNE DONNÉE                   │
│                              ║ NE TRAVERSE                     │
│                              ▼                                  │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                    INTERNET                              │  │
│   │                                                          │  │
│   │   Uniquement pour:                                       │  │
│   │   - Téléchargement initial des modèles (opt-in)         │  │
│   │   - Mise à jour application (opt-in)                    │  │
│   │                                                          │  │
│   │   JAMAIS pour:                                           │  │
│   │   - Audio                                                │  │
│   │   - Transcriptions                                       │  │
│   │   - Données utilisateur                                  │  │
│   │   - Télémétrie                                          │  │
│   │                                                          │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### NFR-SEC-01: Traitement local exclusif

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-SEC-01 |
| **Titre** | Aucune transmission de données audio |
| **Catégorie** | Sécurité |
| **Priorité** | P0 - Critical |

#### Description

Le système MUST traiter 100% des données audio localement, sans aucune transmission vers des serveurs externes.

#### Spécifications

| Donnée | Transmission autorisée |
|--------|------------------------|
| Fichiers audio | **NON** |
| Enregistrements microphone | **NON** |
| Transcriptions | **NON** |
| Segments diarisation | **NON** |
| Métadonnées fichiers | **NON** |
| Configuration utilisateur | **NON** |

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-SEC-01.1 | Aucun appel réseau pendant transcription | ☐ |
| AC-SEC-01.2 | Application fonctionnelle sans internet | ☐ |
| AC-SEC-01.3 | Audit réseau négatif (Wireshark/Fiddler) | ☐ |
| AC-SEC-01.4 | Pas de dépendance à des API cloud | ☐ |

#### Méthode de vérification

```bash
# Test d'isolation réseau
# 1. Désactiver la connexion réseau
# 2. Lancer l'application
# 3. Importer un fichier audio
# 4. Lancer la transcription
# 5. Vérifier le succès complet
# RÉSULTAT ATTENDU: Succès sans erreur réseau
```

---

### NFR-SEC-02: Nettoyage fichiers temporaires

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-SEC-02 |
| **Titre** | Suppression automatique des fichiers temporaires |
| **Catégorie** | Sécurité |
| **Priorité** | P0 - Critical |

#### Description

Le système MUST supprimer automatiquement tous les fichiers temporaires après traitement ou à la fermeture de l'application.

#### Spécifications

| Type de fichier | Durée de vie | Suppression |
|-----------------|--------------|-------------|
| Audio converti (temp) | Fin du traitement | Automatique |
| Chunks audio | Fin du traitement | Automatique |
| Résultats intermédiaires | Fin du traitement | Automatique |
| Cache de session | Fermeture app | Automatique |
| Logs (si sensibles) | 7 jours | Automatique |

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-SEC-02.1 | Dossier temp/ vide après fermeture normale | ☐ |
| AC-SEC-02.2 | Nettoyage même après crash (au redémarrage) | ☐ |
| AC-SEC-02.3 | Pas de fichiers audio résiduels | ☐ |

#### Implémentation

```python
import atexit
import shutil
from pathlib import Path

def cleanup_temp_files():
    temp_dir = Path("temp")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        temp_dir.mkdir()

# Nettoyage à la fermeture
atexit.register(cleanup_temp_files)
```

---

### NFR-SEC-03: Conformité RGPD

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-SEC-03 |
| **Titre** | Conformité au Règlement Général sur la Protection des Données |
| **Catégorie** | Sécurité |
| **Priorité** | P0 - Critical |

#### Description

Le système MUST être conforme au RGPD (Règlement UE 2016/679) pour le traitement des données personnelles.

#### Principes RGPD appliqués

| Principe | Application DICTEA |
|----------|-------------------|
| **Minimisation** | Aucune donnée collectée au-delà du traitement |
| **Limitation finalité** | Audio traité uniquement pour transcription |
| **Limitation conservation** | Fichiers temp supprimés immédiatement |
| **Intégrité & confidentialité** | Traitement 100% local |
| **Privacy by design** | Conception orientée confidentialité |

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-SEC-03.1 | Aucune collecte de données personnelles | ☐ |
| AC-SEC-03.2 | Aucune transmission vers pays tiers | ☐ |
| AC-SEC-03.3 | Pas de profiling utilisateur | ☐ |
| AC-SEC-03.4 | Documentation RGPD disponible | ☐ |

---

### NFR-SEC-04: Protection du code source

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-SEC-04 |
| **Titre** | Obfuscation et protection du code |
| **Catégorie** | Sécurité |
| **Priorité** | P1 - High |

#### Description

Le système SHOULD protéger le code source contre la rétro-ingénierie dans les builds de release.

#### Méthodes de protection

| Niveau | Méthode | Build |
|--------|---------|-------|
| **Basique** | PyInstaller bytecode | Développement |
| **Standard** | Nuitka compilation | Release |
| **Avancé** | Nuitka + commercial obfuscator | Enterprise |

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-SEC-04.1 | Build release compilé avec Nuitka | ☐ |
| AC-SEC-04.2 | Pas de fichiers .py lisibles dans dist/ | ☐ |
| AC-SEC-04.3 | Décompilation non triviale | ☐ |

---

### NFR-SEC-05: Absence de télémétrie

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-SEC-05 |
| **Titre** | Aucune télémétrie ni analytics |
| **Catégorie** | Sécurité |
| **Priorité** | P0 - Critical |

#### Description

Le système MUST NOT collecter ni transmettre de données de télémétrie, analytics ou statistiques d'usage.

#### Données interdites

| Type | Collecte | Transmission |
|------|----------|--------------|
| Statistiques d'usage | ❌ | ❌ |
| Rapports de crash | ❌ | ❌ |
| Métriques performance | ❌ | ❌ |
| Identifiants machine | ❌ | ❌ |
| Comportement utilisateur | ❌ | ❌ |

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-SEC-05.1 | Aucun SDK analytics intégré | ☐ |
| AC-SEC-05.2 | Aucun identifiant unique généré | ☐ |
| AC-SEC-05.3 | Audit code négatif pour télémétrie | ☐ |

---

## 5. Fiabilité (REL)

### 5.1 Vue d'ensemble

Les exigences de fiabilité définissent la robustesse et la tolérance aux pannes du système.

---

### NFR-REL-01: Taux de succès transcription

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-REL-01 |
| **Titre** | Taux de succès des transcriptions |
| **Catégorie** | Fiabilité |
| **Priorité** | P0 - Critical |

#### Description

Le système MUST atteindre un taux de succès des transcriptions supérieur ou égal à 98%.

#### Spécifications

| Métrique | Cible | Minimum |
|----------|-------|---------|
| Taux de succès global | ≥ 99% | 98% |
| Taux de succès (fichiers valides) | ≥ 99.5% | 99% |
| Taux de succès (enregistrements) | ≥ 99% | 98% |

#### Définition du succès

Une transcription est considérée **réussie** si :
1. Le traitement se termine sans crash
2. Un résultat textuel est produit
3. Les timestamps sont générés
4. Le fichier d'export est créé (si demandé)

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-REL-01.1 | ≥98% succès sur 100 fichiers test | ☐ |
| AC-REL-01.2 | Échec gracieux avec message explicite | ☐ |
| AC-REL-01.3 | Pas de corruption de données sur échec | ☐ |

---

### NFR-REL-02: Gestion fichiers corrompus

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-REL-02 |
| **Titre** | Tolérance aux fichiers audio invalides |
| **Catégorie** | Fiabilité |
| **Priorité** | P1 - High |

#### Description

Le système SHOULD détecter et gérer gracieusement les fichiers audio corrompus ou invalides.

#### Scénarios de corruption

| Scénario | Comportement attendu |
|----------|---------------------|
| Fichier tronqué | Message d'erreur, pas de crash |
| Headers invalides | Détection, message explicite |
| Codec non supporté | Suggestion format alternatif |
| Fichier vide (0 octets) | Rejet immédiat avec message |
| Fichier renommé (faux format) | Détection du vrai format |

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-REL-02.1 | Pas de crash sur fichier corrompu | ☐ |
| AC-REL-02.2 | Message d'erreur en français | ☐ |
| AC-REL-02.3 | Retour à l'état stable après erreur | ☐ |

---

### NFR-REL-03: Récupération après crash

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-REL-03 |
| **Titre** | Récupération après interruption |
| **Catégorie** | Fiabilité |
| **Priorité** | P1 - High |

#### Description

Le système SHOULD permettre une récupération propre après un crash ou une interruption.

#### Spécifications

| Événement | Comportement |
|-----------|--------------|
| Crash pendant transcription | Nettoyage temp au redémarrage |
| Fermeture forcée (Task Manager) | État propre au redémarrage |
| Coupure de courant | Pas de corruption config |
| Out of Memory | Tentative de récupération gracieuse |

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-REL-03.1 | Redémarrage propre après crash | ☐ |
| AC-REL-03.2 | Configuration préservée | ☐ |
| AC-REL-03.3 | Nettoyage automatique des temp orphelins | ☐ |

---

### NFR-REL-04: Stabilité mémoire

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-REL-04 |
| **Titre** | Absence de memory leaks |
| **Catégorie** | Fiabilité |
| **Priorité** | P0 - Critical |

#### Description

Le système MUST ne pas présenter de fuites mémoire sur des sessions prolongées.

#### Spécifications

| Test | Critère de succès |
|------|-------------------|
| 10 transcriptions consécutives | RAM finale ≤ RAM initiale + 200 Mo |
| Session de 8 heures | Pas d'augmentation progressive |
| Cycles charge/décharge modèle | Retour au baseline |

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-REL-04.1 | Pas de leak sur 10 transcriptions | ☐ |
| AC-REL-04.2 | GC efficace après déchargement modèle | ☐ |
| AC-REL-04.3 | Monitoring mémoire sans drift | ☐ |

---

## 6. Utilisabilité (USA)

### 6.1 Vue d'ensemble

Les exigences d'utilisabilité définissent la facilité d'apprentissage et d'utilisation du système.

---

### NFR-USA-01: Temps d'apprentissage

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-USA-01 |
| **Titre** | Courbe d'apprentissage utilisateur novice |
| **Catégorie** | Utilisabilité |
| **Priorité** | P0 - Critical |

#### Description

Le système MUST permettre à un utilisateur novice de réaliser sa première transcription en moins de 5 minutes, sans formation préalable.

#### Spécifications

| Tâche | Temps cible | Temps max |
|-------|-------------|-----------|
| Première transcription (fichier) | ≤ 3 min | 5 min |
| Premier enregistrement | ≤ 2 min | 4 min |
| Premier export | ≤ 1 min | 2 min |
| Compréhension des options | ≤ 5 min | 10 min |

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-USA-01.1 | 5 testeurs complètent sans aide en <5min | ☐ |
| AC-USA-01.2 | Labels et boutons auto-explicatifs | ☐ |
| AC-USA-01.3 | Workflow principal en ≤4 clics | ☐ |

---

### NFR-USA-02: Simplicité du workflow

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-USA-02 |
| **Titre** | Nombre minimal d'interactions |
| **Catégorie** | Utilisabilité |
| **Priorité** | P1 - High |

#### Description

Le système SHOULD minimiser le nombre d'interactions requises pour accomplir les tâches principales.

#### Spécifications - Nombre de clics

| Tâche | Clics cible | Clics max |
|-------|-------------|-----------|
| Importer + Transcrire | 3 | 4 |
| Enregistrer + Transcrire | 4 | 5 |
| Exporter résultat (TXT) | 2 | 3 |
| Copier vers presse-papiers | 1 | 2 |

#### Workflow optimal

```
IMPORT + TRANSCRIPTION (3 clics)
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│  [1] Clic "Ouvrir" → Boîte dialogue                           │
│  [2] Sélection fichier + OK                                   │
│  [3] Clic "Transcrire"                                        │
│                                                                │
│  → Attente (progress bar)                                     │
│  → Résultat affiché automatiquement                           │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

### NFR-USA-03: Messages utilisateur

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-USA-03 |
| **Titre** | Clarté des messages d'interface |
| **Catégorie** | Utilisabilité |
| **Priorité** | P1 - High |

#### Description

Le système SHOULD utiliser des messages clairs, en français, sans jargon technique.

#### Exemples de formulation

| ❌ Mauvais | ✅ Bon |
|-----------|--------|
| "FileNotFoundError: audio.wav" | "Le fichier audio n'a pas été trouvé. Vérifiez qu'il existe toujours à cet emplacement." |
| "OOM Error during inference" | "Mémoire insuffisante. Fermez d'autres applications et réessayez." |
| "Model not in cache" | "Le modèle de transcription doit être téléchargé (1.5 Go). Voulez-vous continuer ?" |
| "RTF: 1.23x" | "Transcription terminée en 1h23 pour 1h d'audio" |

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-USA-03.1 | Tous les messages en français | ☐ |
| AC-USA-03.2 | Pas de codes d'erreur techniques exposés | ☐ |
| AC-USA-03.3 | Suggestions d'action incluses | ☐ |

---

### NFR-USA-04: Accessibilité

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-USA-04 |
| **Titre** | Accessibilité de base |
| **Catégorie** | Utilisabilité |
| **Priorité** | P2 - Medium |

#### Description

Le système SHOULD respecter les principes d'accessibilité de base.

#### Spécifications

| Critère | Cible |
|---------|-------|
| Taille police minimale | 12pt |
| Contraste texte/fond | Ratio ≥ 4.5:1 |
| Navigation clavier | Tab order logique |
| Raccourcis clavier | Actions principales |

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-USA-04.1 | Police lisible (≥12pt) | ☐ |
| AC-USA-04.2 | Contraste suffisant | ☐ |
| AC-USA-04.3 | Navigation Tab fonctionnelle | ☐ |

---

## 7. Maintenabilité (MNT)

### 7.1 Vue d'ensemble

Les exigences de maintenabilité définissent la facilité de maintenance, d'évolution et de test du code.

---

### NFR-MNT-01: Architecture modulaire

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-MNT-01 |
| **Titre** | Séparation des responsabilités |
| **Catégorie** | Maintenabilité |
| **Priorité** | P1 - High |

#### Description

Le système SHOULD suivre une architecture modulaire avec séparation claire des responsabilités.

#### Structure cible

```
src/
├── core/           # Logique métier ML (indépendant UI)
│   ├── transcriber.py    # ASR uniquement
│   ├── diarizer.py       # Diarisation uniquement
│   └── audio_processor.py # I/O audio uniquement
├── ui/             # Présentation (indépendant core)
│   ├── main_window.py    # Layout et widgets
│   └── workers.py        # Threading Qt
└── utils/          # Utilitaires transverses
    ├── config.py         # Configuration
    └── model_manager.py  # Gestion modèles
```

#### Principes appliqués

| Principe | Application |
|----------|-------------|
| **SRP** | 1 classe = 1 responsabilité |
| **DIP** | Dépendances via interfaces |
| **OCP** | Extensible sans modification |
| **Couplage faible** | Modules indépendants |

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-MNT-01.1 | Core testable sans UI | ☐ |
| AC-MNT-01.2 | Pas de dépendance circulaire | ☐ |
| AC-MNT-01.3 | Fonctions < 30 lignes | ☐ |

---

### NFR-MNT-02: Qualité du code

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-MNT-02 |
| **Titre** | Standards de qualité code |
| **Catégorie** | Maintenabilité |
| **Priorité** | P1 - High |

#### Description

Le système SHOULD respecter les standards de qualité de code Python.

#### Standards

| Outil | Cible |
|-------|-------|
| **PEP 8** | Conformité 100% |
| **Type hints** | Couverture ≥ 80% |
| **Docstrings** | Toutes les fonctions publiques |
| **Complexité cyclomatique** | ≤ 10 par fonction |
| **Nesting** | ≤ 3 niveaux |

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-MNT-02.1 | Pas d'erreur flake8 | ☐ |
| AC-MNT-02.2 | Type hints sur API publique | ☐ |
| AC-MNT-02.3 | Docstrings Google style | ☐ |

---

### NFR-MNT-03: Testabilité

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-MNT-03 |
| **Titre** | Conception pour la testabilité |
| **Catégorie** | Maintenabilité |
| **Priorité** | P1 - High |

#### Description

Le système SHOULD être conçu pour faciliter les tests unitaires et d'intégration.

#### Spécifications

| Type de test | Couverture cible |
|--------------|------------------|
| Tests unitaires (core) | ≥ 80% |
| Tests d'intégration | Scénarios critiques |
| Tests UI (pytest-qt) | Workflows principaux |

#### Principes

1. **Injection de dépendances** pour les mocks
2. **Interfaces abstraites** pour découplage
3. **Fonctions pures** quand possible
4. **Pas d'état global** (sauf config singleton)

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-MNT-03.1 | Core testable avec mocks | ☐ |
| AC-MNT-03.2 | pytest exécutable en CI | ☐ |
| AC-MNT-03.3 | Couverture mesurable | ☐ |

---

### NFR-MNT-04: Logging et diagnostics

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-MNT-04 |
| **Titre** | Système de logging structuré |
| **Catégorie** | Maintenabilité |
| **Priorité** | P1 - High |

#### Description

Le système SHOULD fournir un logging structuré pour le diagnostic des problèmes.

#### Niveaux de log

| Niveau | Usage |
|--------|-------|
| **DEBUG** | Détails techniques, développement |
| **INFO** | Événements normaux (démarrage, fin traitement) |
| **WARNING** | Situations anormales mais gérées |
| **ERROR** | Erreurs nécessitant attention |
| **CRITICAL** | Erreurs bloquantes |

#### Configuration

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-MNT-04.1 | Logs structurés dans fichier | ☐ |
| AC-MNT-04.2 | Rotation des logs (max 10 Mo) | ☐ |
| AC-MNT-04.3 | Pas de données sensibles loggées | ☐ |

---

## 8. Portabilité (PRT)

### 8.1 Vue d'ensemble

Les exigences de portabilité définissent la compatibilité et la facilité de déploiement.

---

### NFR-PRT-01: Compatibilité Windows

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-PRT-01 |
| **Titre** | Support des versions Windows |
| **Catégorie** | Portabilité |
| **Priorité** | P0 - Critical |

#### Description

Le système MUST fonctionner sur Windows 10 et Windows 11 en version 64-bit.

#### Versions supportées

| Version | Support | Notes |
|---------|---------|-------|
| Windows 11 (23H2+) | ✅ Complet | Version recommandée |
| Windows 11 (21H2-22H2) | ✅ Complet | |
| Windows 10 (22H2) | ✅ Complet | Version minimale recommandée |
| Windows 10 (21H2) | ✅ Complet | |
| Windows 10 (< 21H2) | ⚠️ Partiel | Non garanti |
| Windows 8.1 | ❌ Non supporté | |
| Windows 32-bit | ❌ Non supporté | AVX2 requis |

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-PRT-01.1 | Fonctionne sur Windows 10 22H2 | ☐ |
| AC-PRT-01.2 | Fonctionne sur Windows 11 23H2 | ☐ |
| AC-PRT-01.3 | Erreur claire si Windows 32-bit | ☐ |

---

### NFR-PRT-02: Installation simplifiée

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-PRT-02 |
| **Titre** | Processus d'installation one-click |
| **Catégorie** | Portabilité |
| **Priorité** | P1 - High |

#### Description

Le système SHOULD s'installer via un installeur unique sans prérequis manuels.

#### Spécifications

| Caractéristique | Cible |
|-----------------|-------|
| Nombre de clics installation | ≤ 5 |
| Prérequis manuels | Aucun |
| Droits admin requis | Non (recommandé) |
| Durée installation | ≤ 2 minutes |

#### Contenu installeur

```
TranscriptionApp-Setup.exe
├── Application (exe + libs)
├── Runtimes (VC++ si nécessaire)
├── Configuration par défaut
├── Raccourcis (Bureau, Menu)
└── Désinstalleur
```

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-PRT-02.1 | Installation sans erreur en ≤5 clics | ☐ |
| AC-PRT-02.2 | Pas de prérequis à installer séparément | ☐ |
| AC-PRT-02.3 | Désinstallation propre | ☐ |

---

### NFR-PRT-03: Taille installeur

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-PRT-03 |
| **Titre** | Taille du package d'installation |
| **Catégorie** | Portabilité |
| **Priorité** | P1 - High |

#### Description

Le système SHOULD avoir un installeur de taille raisonnable (< 500 Mo sans modèles).

#### Spécifications

| Composant | Taille cible | Taille max |
|-----------|--------------|------------|
| Installeur (sans modèles) | ≤ 300 Mo | 500 Mo |
| Application installée | ≤ 400 Mo | 600 Mo |
| Modèle medium (téléchargé) | ~1.5 Go | - |
| Total avec modèles | ~2 Go | 3 Go |

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-PRT-03.1 | Installeur < 500 Mo | ☐ |
| AC-PRT-03.2 | Téléchargement modèles séparé | ☐ |
| AC-PRT-03.3 | Estimation espace disque affichée | ☐ |

---

### NFR-PRT-04: Configuration matérielle

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-PRT-04 |
| **Titre** | Exigences matérielles minimales |
| **Catégorie** | Portabilité |
| **Priorité** | P0 - Critical |

#### Description

Le système MUST fonctionner sur la configuration matérielle minimale spécifiée.

#### Spécifications

| Composant | Minimum | Recommandé |
|-----------|---------|------------|
| **CPU** | Intel i5-6xxx / AMD Ryzen 3 | Intel i7-8xxx / AMD Ryzen 5 |
| **Instruction set** | AVX2 obligatoire | AVX2 |
| **RAM** | 12 Go | 16 Go |
| **Stockage libre** | 5 Go | 10 Go |
| **OS** | Windows 10 64-bit | Windows 11 64-bit |

#### Détection des capacités

```python
def check_system_requirements():
    """Vérifie les prérequis système au démarrage."""
    issues = []

    # Vérifier AVX2
    if not cpu_supports_avx2():
        issues.append("Votre processeur ne supporte pas AVX2")

    # Vérifier RAM
    total_ram_gb = psutil.virtual_memory().total / (1024**3)
    if total_ram_gb < 12:
        issues.append(f"RAM insuffisante: {total_ram_gb:.1f} Go (12 Go requis)")

    # Vérifier espace disque
    free_space_gb = psutil.disk_usage('.').free / (1024**3)
    if free_space_gb < 5:
        issues.append(f"Espace disque insuffisant: {free_space_gb:.1f} Go")

    return issues
```

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-PRT-04.1 | Détection AVX2 au démarrage | ☐ |
| AC-PRT-04.2 | Message clair si prérequis non remplis | ☐ |
| AC-PRT-04.3 | Fonctionne avec 12 Go RAM | ☐ |

---

## 9. Scalabilité (SCL)

### 9.1 Vue d'ensemble

Les exigences de scalabilité définissent les limites du système et sa capacité à gérer des charges importantes.

---

### NFR-SCL-01: Durée audio maximale

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-SCL-01 |
| **Titre** | Support des fichiers audio longs |
| **Catégorie** | Scalabilité |
| **Priorité** | P1 - High |

#### Description

Le système SHOULD supporter des fichiers audio d'une durée maximale de 4 heures.

#### Spécifications

| Durée | Support | Stratégie |
|-------|---------|-----------|
| < 30 min | ✅ Direct | Traitement en une passe |
| 30 min - 2h | ✅ Chunked | Découpage en segments |
| 2h - 4h | ✅ Chunked | Découpage + GC agressif |
| > 4h | ⚠️ Expérimental | Risque OOM |

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-SCL-01.1 | Transcription fichier 2h sans OOM | ☐ |
| AC-SCL-01.2 | Transcription fichier 4h avec chunking | ☐ |
| AC-SCL-01.3 | Message si durée > 4h | ☐ |

---

### NFR-SCL-02: Taille fichier maximale

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-SCL-02 |
| **Titre** | Support des fichiers volumineux |
| **Catégorie** | Scalabilité |
| **Priorité** | P1 - High |

#### Description

Le système SHOULD supporter des fichiers audio jusqu'à 2 Go.

#### Spécifications

| Taille | Support | Notes |
|--------|---------|-------|
| < 500 Mo | ✅ Complet | Cas nominal |
| 500 Mo - 1 Go | ✅ Complet | Formats compressés |
| 1 Go - 2 Go | ✅ Complet | Formats non compressés |
| > 2 Go | ⚠️ Partiel | Dépend du format |

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-SCL-02.1 | Import fichier 1 Go sans erreur | ☐ |
| AC-SCL-02.2 | Import fichier 2 Go WAV | ☐ |
| AC-SCL-02.3 | Message si fichier > 2 Go | ☐ |

---

### NFR-SCL-03: Nombre de locuteurs

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-SCL-03 |
| **Titre** | Support multi-locuteurs |
| **Catégorie** | Scalabilité |
| **Priorité** | P1 - High |

#### Description

Le système SHOULD identifier correctement jusqu'à 10 locuteurs distincts.

#### Spécifications

| Nb locuteurs | Support | Précision attendue |
|--------------|---------|-------------------|
| 1-2 | ✅ Excellent | DER < 10% |
| 3-5 | ✅ Bon | DER < 15% |
| 6-10 | ✅ Acceptable | DER < 20% |
| > 10 | ⚠️ Dégradé | DER > 25% |

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-SCL-03.1 | Diarisation 2 locuteurs DER < 12% | ☐ |
| AC-SCL-03.2 | Diarisation 5 locuteurs DER < 18% | ☐ |
| AC-SCL-03.3 | Warning si > 10 locuteurs détectés | ☐ |

---

## 10. Compatibilité (CMP)

### 10.1 Vue d'ensemble

Les exigences de compatibilité définissent l'interopérabilité avec les formats et systèmes externes.

---

### NFR-CMP-01: Formats audio supportés

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-CMP-01 |
| **Titre** | Compatibilité formats audio |
| **Catégorie** | Compatibilité |
| **Priorité** | P0 - Critical |

#### Description

Le système MUST supporter les formats audio courants.

#### Formats supportés

| Format | Extension | Codec | Support |
|--------|-----------|-------|---------|
| WAV | .wav | PCM | ✅ Natif |
| MP3 | .mp3 | MPEG Layer 3 | ✅ Via pydub |
| M4A | .m4a | AAC | ✅ Via pydub |
| FLAC | .flac | FLAC | ✅ Via soundfile |
| OGG | .ogg | Vorbis | ✅ Via soundfile |
| WMA | .wma | WMA | ✅ Via pydub |
| AAC | .aac | AAC | ✅ Via pydub |

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-CMP-01.1 | Import WAV 16/24/32 bit | ☐ |
| AC-CMP-01.2 | Import MP3 128-320 kbps | ☐ |
| AC-CMP-01.3 | Import tous formats listés | ☐ |

---

### NFR-CMP-02: Formats export supportés

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-CMP-02 |
| **Titre** | Compatibilité formats export |
| **Catégorie** | Compatibilité |
| **Priorité** | P0 - Critical |

#### Description

Le système MUST exporter dans les formats TXT et SRT standards.

#### Spécifications

| Format | Standard | Encodage | Usage |
|--------|----------|----------|-------|
| TXT | Plain text | UTF-8 | Documents, Word |
| SRT | SubRip | UTF-8 | Sous-titres vidéo |

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-CMP-02.1 | TXT ouvrable dans Notepad/Word | ☐ |
| AC-CMP-02.2 | SRT compatible VLC/YouTube | ☐ |
| AC-CMP-02.3 | Encodage UTF-8 validé | ☐ |

---

### NFR-CMP-03: Compatibilité HuggingFace

| Attribut | Valeur |
|----------|--------|
| **ID** | NFR-CMP-03 |
| **Titre** | Intégration HuggingFace Hub |
| **Catégorie** | Compatibilité |
| **Priorité** | P0 - Critical |

#### Description

Le système MUST être compatible avec HuggingFace Hub pour le téléchargement des modèles.

#### Spécifications

| Aspect | Requirement |
|--------|-------------|
| API version | HuggingFace Hub >= 0.19 |
| Authentication | Token optionnel (requis pour Pyannote) |
| Cache | Répertoire local configurable |
| Offline | Mode offline après premier téléchargement |

#### Critères d'acceptation

| # | Critère | Vérifié |
|---|---------|---------|
| AC-CMP-03.1 | Téléchargement faster-whisper | ☐ |
| AC-CMP-03.2 | Téléchargement Pyannote avec token | ☐ |
| AC-CMP-03.3 | Cache local fonctionnel | ☐ |

---

## 11. Matrice de Traçabilité

### 11.1 NFRs → Catégories

| Catégorie | NFRs | Priorité dominante |
|-----------|------|-------------------|
| **Performance** | NFR-PERF-01 à 05 | P0/P1 |
| **Sécurité** | NFR-SEC-01 à 05 | P0 |
| **Fiabilité** | NFR-REL-01 à 04 | P0/P1 |
| **Utilisabilité** | NFR-USA-01 à 04 | P0/P1 |
| **Maintenabilité** | NFR-MNT-01 à 04 | P1 |
| **Portabilité** | NFR-PRT-01 à 04 | P0/P1 |
| **Scalabilité** | NFR-SCL-01 à 03 | P1 |
| **Compatibilité** | NFR-CMP-01 à 03 | P0 |

### 11.2 NFRs → Personas

| Persona | NFRs Prioritaires |
|---------|-------------------|
| **Marie (Avocate)** | NFR-SEC-01, NFR-SEC-03, NFR-REL-01 |
| **Thomas (Journaliste)** | NFR-PERF-01, NFR-PRT-04, NFR-SCL-01 |
| **Sophie (Assistante)** | NFR-USA-01, NFR-USA-02, NFR-USA-03 |

### 11.3 Couverture MVP

| Priorité | Total NFRs | Dans MVP |
|----------|------------|----------|
| P0 - Critical | 12 | 12 (100%) |
| P1 - High | 14 | 14 (100%) |
| P2 - Medium | 2 | 1 (50%) |
| **TOTAL** | **28** | **27 (96%)** |

### 11.4 NFRs → Tests

| NFR ID | Type de test | Automatisable |
|--------|--------------|---------------|
| NFR-PERF-01 | Benchmark | Oui |
| NFR-PERF-02 | Profiling mémoire | Oui |
| NFR-PERF-03 | Chrono démarrage | Oui |
| NFR-PERF-04 | Test UI réactivité | Partiellement |
| NFR-SEC-01 | Audit réseau | Oui (Wireshark) |
| NFR-SEC-02 | Vérification fichiers | Oui |
| NFR-REL-01 | Test de masse | Oui |
| NFR-USA-01 | Test utilisateur | Non |
| NFR-PRT-01 | Test multi-OS | Oui (CI) |

---

## Historique des Révisions

| Version | Date | Auteur | Modifications |
|---------|------|--------|---------------|
| 1.0.0 | 2026-01-14 | PM Agent (BMAD) | Création initiale |

---

**Document suivant:** [USER_STORIES.md](./USER_STORIES.md)
