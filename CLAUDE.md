# Instructions Claude Code - Projet DICTEA

## Contexte du Projet

**DICTEA** est une application desktop Windows de transcription audio 100% offline avec identification des locuteurs (diarisation).

- **Stack:** Python, PySide6, faster-whisper, Pyannote/SpeechBrain
- **Méthodologie:** BMAD (Breakthrough Method for Agile AI-Driven Development)
- **Cible:** Windows 10/11, CPU uniquement (Intel i7, 16 Go RAM)

## Instructions Obligatoires

### 1. Avant toute action, lis le journal de bord

```
Lis le fichier DEVLOG.md à la racine du projet pour connaître :
- L'état actuel du projet
- Les dernières modifications
- Les tâches en cours et à faire
```

### 2. Documente TOUTES tes avancées

Après chaque session de travail significative, mets à jour `DEVLOG.md` avec :

```markdown
## [DATE] - Titre de la session

### Réalisé
- [ ] Tâche 1 complétée
- [ ] Tâche 2 complétée

### Fichiers modifiés
- `chemin/fichier.py` - Description des changements

### Décisions prises
- Décision X pour raison Y

### Prochaines étapes
- [ ] Tâche suivante 1
- [ ] Tâche suivante 2

### Problèmes/Blocages
- Issue X à résoudre
```

### 3. Structure du projet

```
DICTEA/
├── CLAUDE.md                    # CE FICHIER - Instructions permanentes
├── DEVLOG.md                    # Journal de bord (à maintenir)
└── transcription-app/
    ├── main.py                  # Point d'entrée
    ├── config.yaml              # Configuration
    ├── src/
    │   ├── core/                # Logique ML (transcriber, diarizer, audio)
    │   ├── ui/                  # Interface PySide6
    │   └── utils/               # Config, model manager
    ├── docs/
    │   └── bmad/                # Documentation BMAD complète
    │       ├── README.md        # Index documentation
    │       ├── PRD.md           # Product Requirements
    │       ├── FUNCTIONAL_REQUIREMENTS.md
    │       ├── NON_FUNCTIONAL_REQUIREMENTS.md
    │       ├── USER_STORIES.md
    │       └── TECHNICAL_ARCHITECTURE.md
    └── scripts/
        └── build.py             # Build PyInstaller/Nuitka
```

### 4. Documentation BMAD à jour

La documentation complète existe dans `transcription-app/docs/bmad/` :

| Document | Contenu |
|----------|---------|
| PRD.md | Vision, personas, scope, métriques |
| FUNCTIONAL_REQUIREMENTS.md | 32 FRs sur 7 Epics |
| NON_FUNCTIONAL_REQUIREMENTS.md | 28 NFRs (PERF, SEC, REL, USA, MNT, PRT, SCL, CMP) |
| USER_STORIES.md | 36 User Stories, backlog priorisé, DoD |
| TECHNICAL_ARCHITECTURE.md | C4, composants, threading, ADRs, sécurité, perf |

### 5. Règles de développement

- **SRP:** Une fonction = une responsabilité
- **Max 30 lignes** par fonction
- **Max 3 niveaux** d'imbrication
- **Type hints** obligatoires sur API publique
- **Pas de code spaghetti**
- **Tests** pour toute nouvelle fonctionnalité

### 6. Commande de démarrage de session

Au début de chaque session, exécute mentalement :

```
1. Lire DEVLOG.md → Comprendre l'état actuel
2. Identifier la tâche prioritaire
3. Créer un plan si tâche complexe
4. Exécuter
5. Mettre à jour DEVLOG.md avec les avancées
```

---

## État Actuel du Projet

**Phase:** Documentation BMAD complète ✅ → Prêt pour implémentation/amélioration

**Dernière mise à jour:** 2026-01-14

Consulte `DEVLOG.md` pour le détail des sessions.
