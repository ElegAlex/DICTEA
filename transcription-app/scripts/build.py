#!/usr/bin/env python3
"""
Script de build multi-plateforme pour DICTEA.

Usage:
    python scripts/build.py [platform] [mode]

Platforms:
    windows     Build Windows .exe (utilise Wine sur Linux)
    linux       Build Linux AppImage
    all         Build pour les deux plateformes

Modes:
    --dev       Build rapide avec PyInstaller (défaut)
    --release   Build optimisé avec Nuitka
    --clean     Nettoyer les dossiers de build

Options:
    --setup-wine    Configure Wine avec Python pour les builds Windows

Examples:
    python scripts/build.py                    # Auto-detect platform, dev mode
    python scripts/build.py windows            # Windows .exe (via Wine sur Linux)
    python scripts/build.py linux              # Linux AppImage
    python scripts/build.py all                # Les deux
    python scripts/build.py --setup-wine       # Installer Python dans Wine
"""
import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

# Configuration
APP_NAME = "DICTEA"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Transcription audio offline avec diarisation"
APP_AUTHOR = "DICTEA Team"
FFMPEG_WINDOWS_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

# Chemins
ROOT_DIR = Path(__file__).parent.parent
BUILD_DIR = ROOT_DIR / "build"
DIST_DIR = ROOT_DIR / "dist"
RESOURCES_DIR = ROOT_DIR / "resources"
FFMPEG_DIR = BUILD_DIR / "ffmpeg"

# Configuration Wine
WINE_PYTHON_VERSION = "3.11.9"
WINE_PYTHON_URL = f"https://www.python.org/ftp/python/{WINE_PYTHON_VERSION}/python-{WINE_PYTHON_VERSION}-amd64.exe"


def print_header(title: str) -> None:
    """Affiche un header formaté."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_step(msg: str) -> None:
    """Affiche une étape."""
    print(f"  → {msg}")


def run_cmd(cmd: list, **kwargs) -> subprocess.CompletedProcess:
    """Exécute une commande avec gestion d'erreur."""
    return subprocess.run(cmd, **kwargs)


def _find_ffmpeg_binaries(root: Path) -> tuple[Path | None, Path | None]:
    """Recherche ffmpeg.exe et ffprobe.exe dans un dossier."""
    ffmpeg_exe = next(root.rglob("ffmpeg.exe"), None)
    ffprobe_exe = next(root.rglob("ffprobe.exe"), None)
    return ffmpeg_exe, ffprobe_exe


def ensure_windows_ffmpeg() -> list[tuple[str, str]]:
    """Télécharge et prépare FFmpeg pour les builds Windows."""
    FFMPEG_DIR.mkdir(parents=True, exist_ok=True)

    ffmpeg_exe, ffprobe_exe = _find_ffmpeg_binaries(FFMPEG_DIR)
    if ffmpeg_exe and ffprobe_exe:
        return [(str(ffmpeg_exe), "."), (str(ffprobe_exe), ".")]

    print_step("FFmpeg introuvable, téléchargement...")
    zip_path = BUILD_DIR / "ffmpeg-release-essentials.zip"
    if not zip_path.exists():
        result = run_cmd(["wget", "-q", "--show-progress", "-O", str(zip_path), FFMPEG_WINDOWS_URL])
        if result.returncode != 0:
            raise RuntimeError("Échec du téléchargement de FFmpeg")

    print_step("Extraction de FFmpeg...")
    if FFMPEG_DIR.exists():
        shutil.rmtree(FFMPEG_DIR)
    FFMPEG_DIR.mkdir(parents=True, exist_ok=True)

    import zipfile

    with zipfile.ZipFile(zip_path, "r") as archive:
        archive.extractall(FFMPEG_DIR)

    ffmpeg_exe, ffprobe_exe = _find_ffmpeg_binaries(FFMPEG_DIR)
    if not (ffmpeg_exe and ffprobe_exe):
        raise RuntimeError("FFmpeg téléchargé mais binaires introuvables")

    return [(str(ffmpeg_exe), "."), (str(ffprobe_exe), ".")]


def clean() -> None:
    """Nettoie les dossiers de build."""
    print_header("Nettoyage")
    for folder in [BUILD_DIR, DIST_DIR]:
        if folder.exists():
            shutil.rmtree(folder)
            print(f"  Supprimé: {folder}")
    # Nettoyer aussi les fichiers .spec
    for spec in ROOT_DIR.glob("*.spec"):
        spec.unlink()
        print(f"  Supprimé: {spec}")
    print("  Nettoyage terminé")


# =============================================================================
# Wine Support (pour build Windows depuis Linux)
# =============================================================================

def check_wine_installed() -> bool:
    """Vérifie si Wine est installé."""
    result = run_cmd(["which", "wine"], capture_output=True)
    return result.returncode == 0


def get_wine_python_path() -> Path | None:
    """Retourne le chemin de Python dans Wine."""
    wine_prefix = Path(os.environ.get("WINEPREFIX", Path.home() / ".wine"))

    # Chercher Python dans les emplacements courants
    possible_paths = [
        wine_prefix / "drive_c" / "Python311" / "python.exe",
        wine_prefix / "drive_c" / "Python310" / "python.exe",
        wine_prefix / "drive_c" / "Python39" / "python.exe",
        wine_prefix / "drive_c" / "Program Files" / "Python311" / "python.exe",
        wine_prefix / "drive_c" / "Program Files" / "Python310" / "python.exe",
        wine_prefix / "drive_c" / "users" / os.environ.get("USER", "user") / "AppData" / "Local" / "Programs" / "Python" / "Python311" / "python.exe",
    ]

    for path in possible_paths:
        if path.exists():
            return path

    return None


def wine_cmd(cmd: list, **kwargs) -> subprocess.CompletedProcess:
    """Exécute une commande via Wine."""
    return run_cmd(["wine"] + cmd, **kwargs)


def check_wine_python() -> tuple[bool, Path | None]:
    """Vérifie si Python est installé dans Wine."""
    python_path = get_wine_python_path()
    if python_path:
        # Vérifier que ça fonctionne
        result = wine_cmd([str(python_path), "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            return True, python_path
    return False, None


def check_wine_pyinstaller(python_path: Path) -> bool:
    """Vérifie si PyInstaller est installé dans Wine Python."""
    result = wine_cmd(
        [str(python_path), "-m", "PyInstaller", "--version"],
        capture_output=True, text=True
    )
    return result.returncode == 0


def setup_wine_python() -> bool:
    """Configure Wine avec Python pour les builds Windows."""
    print_header("Configuration Wine pour builds Windows")

    if not check_wine_installed():
        print("  ERREUR: Wine n'est pas installé.")
        print("  Installer avec: sudo apt install wine64 wine32")
        return False

    print_step("Wine détecté")

    # Vérifier si Python est déjà installé
    has_python, python_path = check_wine_python()
    if has_python:
        print_step(f"Python Wine déjà installé: {python_path}")
    else:
        print_step("Installation de Python dans Wine...")

        # Télécharger l'installeur Python
        installer_path = BUILD_DIR / f"python-{WINE_PYTHON_VERSION}-amd64.exe"
        BUILD_DIR.mkdir(exist_ok=True)

        if not installer_path.exists():
            print_step(f"Téléchargement de Python {WINE_PYTHON_VERSION}...")
            result = run_cmd(
                ["wget", "-q", "--show-progress", "-O", str(installer_path), WINE_PYTHON_URL]
            )
            if result.returncode != 0:
                print("  ERREUR: Échec du téléchargement")
                return False

        # Installer Python via Wine (mode silencieux)
        print_step("Installation de Python (peut prendre quelques minutes)...")
        result = wine_cmd([
            str(installer_path),
            "/quiet",
            "InstallAllUsers=0",
            "PrependPath=1",
            "Include_test=0"
        ])

        if result.returncode != 0:
            print("  ERREUR: Échec de l'installation de Python")
            print("  Essayez manuellement: wine", str(installer_path))
            return False

        # Revérifier
        has_python, python_path = check_wine_python()
        if not has_python:
            print("  ERREUR: Python installé mais non trouvé")
            return False

        print_step(f"Python installé: {python_path}")

    # Installer PyInstaller
    if not check_wine_pyinstaller(python_path):
        print_step("Installation de PyInstaller dans Wine...")
        result = wine_cmd(
            [str(python_path), "-m", "pip", "install", "--upgrade", "pip"],
            capture_output=True
        )
        result = wine_cmd(
            [str(python_path), "-m", "pip", "install", "pyinstaller"],
            capture_output=True
        )
        if not check_wine_pyinstaller(python_path):
            print("  ERREUR: Échec de l'installation de PyInstaller")
            return False
        print_step("PyInstaller installé")
    else:
        print_step("PyInstaller déjà installé")

    # Installer les dépendances du projet
    print_step("Installation des dépendances du projet...")
    requirements_file = ROOT_DIR / "requirements.txt"
    if requirements_file.exists():
        # Installer les dépendances principales (sans les gros packages ML pour l'instant)
        deps = ["PySide6", "pyyaml", "faster-whisper", "soundfile", "numpy"]
        for dep in deps:
            print_step(f"  Installation de {dep}...")
            wine_cmd(
                [str(python_path), "-m", "pip", "install", dep],
                capture_output=True
            )

    print_header("Configuration Wine terminée")
    print(f"  Python Wine: {python_path}")
    print("  Vous pouvez maintenant lancer: python scripts/build.py windows")
    return True


def build_windows_wine() -> Path:
    """Build Windows .exe via Wine depuis Linux."""
    print_header("Build Windows via Wine")

    # Vérifier Wine
    if not check_wine_installed():
        print("  ERREUR: Wine n'est pas installé")
        print("  Installer: sudo apt install wine64")
        print("  Puis: python scripts/build.py --setup-wine")
        sys.exit(1)

    has_python, python_path = check_wine_python()
    if not has_python:
        print("  ERREUR: Python non installé dans Wine")
        print("  Lancer: python scripts/build.py --setup-wine")
        sys.exit(1)

    print_step(f"Utilisation de: {python_path}")

    # Vérifier PyInstaller
    if not check_wine_pyinstaller(python_path):
        print("  ERREUR: PyInstaller non installé dans Wine")
        print("  Lancer: python scripts/build.py --setup-wine")
        sys.exit(1)

    ffmpeg_binaries = ensure_windows_ffmpeg()

    # Créer le fichier .spec pour Windows avec dépendances ML (liste manuelle)
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

datas = [('config.yaml', '.')]
binaries = {ffmpeg_binaries!r}

# Hidden imports listés manuellement (évite collect_submodules qui crash avec Wine)
hiddenimports = [
    # UI
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.QtMultimedia',
    # Audio
    'yaml',
    'numpy',
    'soundfile',
    'sounddevice',
    'pydub',
    # Whisper
    'faster_whisper',
    'ctranslate2',
    'huggingface_hub',
    'tiktoken_ext.openai_public',
    'tiktoken_ext',
    # ML
    'torch',
    'torchaudio',
    'sklearn.cluster',
    'sklearn.neighbors',
    'scipy.signal',
    'scipy.fft',
    # Pyannote core
    'pyannote.core',
    'pyannote.audio',
    'pyannote.audio.pipelines',
    'pyannote.pipeline',
    'pytorch_lightning',
    'lightning',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['matplotlib', 'tkinter', 'triton', 'nemo'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icon.ico' if Path('resources/icon.ico').exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{APP_NAME}',
)
'''

    spec_path = ROOT_DIR / f"{APP_NAME}.spec"
    spec_path.write_text(spec_content)

    # Convertir les chemins en format Windows pour Wine
    wine_root = "Z:" + str(ROOT_DIR).replace("/", "\\\\")
    wine_spec = "Z:" + str(spec_path).replace("/", "\\\\")

    print_step("Lancement de PyInstaller via Wine...")
    print_step("(Cette opération peut prendre plusieurs minutes)")

    # Exécuter PyInstaller via Wine
    result = wine_cmd(
        [str(python_path), "-m", "PyInstaller", "--clean", "--noconfirm", wine_spec],
        cwd=ROOT_DIR
    )

    if result.returncode != 0:
        print("  ERREUR: Le build a échoué")
        sys.exit(1)

    output_dir = DIST_DIR / APP_NAME
    print(f"\n  Build terminé: {output_dir}")

    # Vérifier qu'on a bien un .exe
    exe_path = output_dir / f"{APP_NAME}.exe"
    if exe_path.exists():
        print_step(f"Exécutable Windows créé: {exe_path}")

    return output_dir


# =============================================================================
# Build natif
# =============================================================================

def check_dependencies(mode: str) -> bool:
    """Vérifie les dépendances requises."""
    print_header("Vérification des dépendances")

    missing = []

    # PyInstaller (toujours requis)
    try:
        import PyInstaller
        print(f"  PyInstaller: {PyInstaller.__version__}")
    except ImportError:
        missing.append("pyinstaller")

    # Nuitka (pour release)
    if mode == "release":
        try:
            result = run_cmd(
                [sys.executable, "-m", "nuitka", "--version"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                print("  Nuitka: OK")
            else:
                missing.append("nuitka")
        except Exception:
            missing.append("nuitka")

    if missing:
        print(f"\n  Dépendances manquantes: {', '.join(missing)}")
        print(f"  Installer avec: pip install {' '.join(missing)}")
        return False

    return True


def create_icon_if_missing() -> None:
    """Crée une icône placeholder si elle n'existe pas."""
    RESOURCES_DIR.mkdir(exist_ok=True)

    # Icône PNG pour Linux
    png_path = RESOURCES_DIR / "icon.png"
    if not png_path.exists():
        print_step("Création d'une icône placeholder...")
        try:
            from PIL import Image, ImageDraw
            img = Image.new('RGBA', (256, 256), (52, 73, 94, 255))
            draw = ImageDraw.Draw(img)
            # Dessiner un microphone stylisé
            draw.ellipse([88, 40, 168, 140], fill=(236, 240, 241, 255))
            draw.rectangle([108, 130, 148, 180], fill=(236, 240, 241, 255))
            draw.arc([78, 120, 178, 220], 0, 180, fill=(236, 240, 241, 255), width=8)
            draw.line([128, 200, 128, 230], fill=(236, 240, 241, 255), width=8)
            draw.line([98, 230, 158, 230], fill=(236, 240, 241, 255), width=8)
            img.save(png_path)
            print_step(f"Créé: {png_path}")

            # Créer aussi .ico pour Windows si possible
            ico_path = RESOURCES_DIR / "icon.ico"
            if not ico_path.exists():
                img.save(ico_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
                print_step(f"Créé: {ico_path}")
        except ImportError:
            print_step("PIL non disponible, création d'icône ignorée")


def build_linux_pyinstaller() -> Path:
    """Build Linux avec PyInstaller."""
    print_header("Build Linux (PyInstaller)")

    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = [('config.yaml', '.')]
datas += collect_data_files('faster_whisper')

hiddenimports = [
    'tiktoken_ext.openai_public',
    'tiktoken_ext',
    'ctranslate2',
    'huggingface_hub',
    'sounddevice',
    'soundfile',
    'sklearn.cluster',
    'sklearn.neighbors',
    'scipy.signal',
    'scipy.fft',
]
hiddenimports += collect_submodules('pyannote')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['matplotlib', 'tkinter'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name='{APP_NAME}',
)
'''

    spec_path = ROOT_DIR / f"{APP_NAME}.spec"
    spec_path.write_text(spec_content)

    cmd = [sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm", str(spec_path)]
    run_cmd(cmd, cwd=ROOT_DIR, check=True)

    output_dir = DIST_DIR / APP_NAME
    print(f"\n  Build PyInstaller terminé: {output_dir}")
    return output_dir


def create_appimage(pyinstaller_dir: Path) -> Path:
    """Crée une AppImage à partir du build PyInstaller."""
    print_header("Création AppImage")

    appdir = BUILD_DIR / f"{APP_NAME}.AppDir"

    # Structure AppDir
    appdir.mkdir(parents=True, exist_ok=True)
    (appdir / "usr" / "bin").mkdir(parents=True, exist_ok=True)
    (appdir / "usr" / "share" / "applications").mkdir(parents=True, exist_ok=True)
    (appdir / "usr" / "share" / "icons" / "hicolor" / "256x256" / "apps").mkdir(parents=True, exist_ok=True)

    # Copier les fichiers du build PyInstaller
    print_step("Copie des fichiers...")
    for item in pyinstaller_dir.iterdir():
        dest = appdir / "usr" / "bin" / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest)

    # Créer le fichier .desktop
    desktop_content = f"""[Desktop Entry]
Type=Application
Name={APP_NAME}
Comment={APP_DESCRIPTION}
Exec={APP_NAME}
Icon={APP_NAME.lower()}
Categories=AudioVideo;Audio;Utility;
Terminal=false
StartupNotify=true
"""

    desktop_path = appdir / f"{APP_NAME.lower()}.desktop"
    desktop_path.write_text(desktop_content)

    # Copier aussi dans usr/share/applications
    shutil.copy2(desktop_path, appdir / "usr" / "share" / "applications" / f"{APP_NAME.lower()}.desktop")

    # Copier l'icône
    icon_src = RESOURCES_DIR / "icon.png"
    if icon_src.exists():
        icon_dest = appdir / f"{APP_NAME.lower()}.png"
        shutil.copy2(icon_src, icon_dest)
        shutil.copy2(icon_src, appdir / "usr" / "share" / "icons" / "hicolor" / "256x256" / "apps" / f"{APP_NAME.lower()}.png")

    # Créer AppRun
    apprun_content = f"""#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${{SELF%/*}}
export PATH="${{HERE}}/usr/bin:${{PATH}}"
export LD_LIBRARY_PATH="${{HERE}}/usr/bin:${{LD_LIBRARY_PATH}}"
exec "${{HERE}}/usr/bin/{APP_NAME}" "$@"
"""

    apprun_path = appdir / "AppRun"
    apprun_path.write_text(apprun_content)
    apprun_path.chmod(0o755)

    # Télécharger appimagetool si nécessaire
    appimagetool = BUILD_DIR / "appimagetool-x86_64.AppImage"
    if not appimagetool.exists():
        print_step("Téléchargement de appimagetool...")
        url = "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
        run_cmd(["wget", "-q", "-O", str(appimagetool), url], check=True)
        appimagetool.chmod(0o755)

    # Créer l'AppImage
    print_step("Création de l'AppImage...")
    DIST_DIR.mkdir(exist_ok=True)
    output_file = DIST_DIR / f"{APP_NAME}-{APP_VERSION}-x86_64.AppImage"

    env = os.environ.copy()
    env["ARCH"] = "x86_64"

    run_cmd(
        [str(appimagetool), str(appdir), str(output_file)],
        env=env,
        check=True
    )

    print(f"\n  AppImage créée: {output_file}")
    return output_file


def build_linux_appimage() -> Path:
    """Build complet Linux AppImage."""
    pyinstaller_dir = build_linux_pyinstaller()
    return create_appimage(pyinstaller_dir)


def build_windows_native() -> Path:
    """Build Windows natif (quand on est sur Windows)."""
    print_header("Build Windows (PyInstaller)")

    ffmpeg_binaries = ensure_windows_ffmpeg()

    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = [('config.yaml', '.')]
datas += collect_data_files('faster_whisper')
binaries = {ffmpeg_binaries!r}

hiddenimports = [
    'tiktoken_ext.openai_public',
    'tiktoken_ext',
    'ctranslate2',
    'huggingface_hub',
    'sounddevice',
    'soundfile',
    'sklearn.cluster',
    'sklearn.neighbors',
    'scipy.signal',
    'scipy.fft',
]
hiddenimports += collect_submodules('pyannote')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['matplotlib', 'tkinter'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icon.ico' if Path('resources/icon.ico').exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{APP_NAME}',
)
'''

    spec_path = ROOT_DIR / f"{APP_NAME}.spec"
    spec_path.write_text(spec_content)

    cmd = [sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm", str(spec_path)]
    run_cmd(cmd, cwd=ROOT_DIR, check=True)

    output_dir = DIST_DIR / APP_NAME
    print(f"\n  Build terminé: {output_dir}")
    return output_dir


# =============================================================================
# Main
# =============================================================================

def main():
    os.chdir(ROOT_DIR)

    # Parser les arguments
    args = sys.argv[1:]
    target_platform = None
    mode = "dev"

    for arg in args:
        if arg == "--release":
            mode = "release"
        elif arg == "--dev":
            mode = "dev"
        elif arg == "--clean":
            clean()
            return
        elif arg == "--setup-wine":
            setup_wine_python()
            return
        elif arg in ("windows", "linux", "all"):
            target_platform = arg

    # Auto-detect platform si non spécifié
    current_os = platform.system().lower()
    if target_platform is None:
        target_platform = "windows" if current_os == "windows" else "linux"

    print_header("DICTEA Build System")
    print(f"  Plateforme cible: {target_platform}")
    print(f"  Mode: {mode}")
    print(f"  OS actuel: {current_os}")

    # Créer l'icône si manquante
    create_icon_if_missing()

    # Build selon la plateforme
    outputs = []

    if target_platform in ("windows", "all"):
        if current_os == "windows":
            # Build natif Windows
            if not check_dependencies(mode):
                sys.exit(1)
            clean()
            outputs.append(("Windows .exe", build_windows_native()))
        else:
            # Build Windows via Wine depuis Linux
            clean()
            outputs.append(("Windows .exe (Wine)", build_windows_wine()))

    if target_platform in ("linux", "all"):
        if current_os == "linux":
            if not check_dependencies(mode):
                sys.exit(1)
            if target_platform != "all":  # Éviter double clean
                clean()
            outputs.append(("Linux AppImage", build_linux_appimage()))
        else:
            print("\n  ATTENTION: Build Linux depuis Windows non supporté.")
            print("  Utilisez WSL pour créer l'AppImage")

    # Résumé
    if outputs:
        print_header("Build terminé")
        for name, path in outputs:
            if path.exists():
                size = path.stat().st_size if path.is_file() else sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
                size_mb = size / (1024 * 1024)
                print(f"  {name}: {path}")
                print(f"    Taille: {size_mb:.1f} MB")
            else:
                print(f"  {name}: {path} (non trouvé)")
    else:
        print("\n  Aucun build effectué.")


if __name__ == "__main__":
    main()
