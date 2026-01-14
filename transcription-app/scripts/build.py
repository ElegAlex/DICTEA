#!/usr/bin/env python3
"""
Script de build pour créer l'exécutable Windows.

Usage:
    python scripts/build.py [--dev|--release]
    
Options:
    --dev       Build rapide avec PyInstaller (défaut)
    --release   Build optimisé avec Nuitka
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

# Dossier racine du projet
ROOT_DIR = Path(__file__).parent.parent
BUILD_DIR = ROOT_DIR / "build"
DIST_DIR = ROOT_DIR / "dist"


def clean():
    """Nettoie les dossiers de build."""
    for folder in [BUILD_DIR, DIST_DIR]:
        if folder.exists():
            shutil.rmtree(folder)
            print(f"Nettoyé: {folder}")


def build_pyinstaller():
    """Build avec PyInstaller (rapide, pour développement)."""
    print("\n=== Build PyInstaller ===\n")
    
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collecter les données des packages
datas = []
datas += collect_data_files('faster_whisper')
datas += collect_data_files('pyannote')

# Hidden imports nécessaires
hiddenimports = [
    'tiktoken_ext.openai_public',
    'tiktoken_ext',
    'ctranslate2',
    'huggingface_hub',
    'sounddevice',
    'soundfile',
    'sklearn.cluster',
    'sklearn.neighbors',
]
hiddenimports += collect_submodules('pyannote')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TranscriptionApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI mode
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
    name='TranscriptionApp',
)
'''
    
    spec_path = ROOT_DIR / "TranscriptionApp.spec"
    spec_path.write_text(spec_content)
    
    # Exécuter PyInstaller
    cmd = [sys.executable, "-m", "PyInstaller", "--clean", str(spec_path)]
    subprocess.run(cmd, cwd=ROOT_DIR, check=True)
    
    print(f"\n✅ Build terminé: {DIST_DIR / 'TranscriptionApp'}")


def build_nuitka():
    """Build avec Nuitka (lent, pour release)."""
    print("\n=== Build Nuitka ===\n")
    print("⚠️  Ce build peut prendre 20-30 minutes...\n")
    
    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--onefile",
        "--windows-disable-console",
        "--enable-plugin=pyside6",
        "--include-data-files=config.yaml=config.yaml",
        "--include-package=faster_whisper",
        "--include-package=pyannote",
        "--include-package=ctranslate2",
        f"--output-dir={DIST_DIR}",
        "--output-filename=TranscriptionApp.exe",
        "main.py",
    ]
    
    subprocess.run(cmd, cwd=ROOT_DIR, check=True)
    
    print(f"\n✅ Build Nuitka terminé: {DIST_DIR / 'TranscriptionApp.exe'}")


def main():
    os.chdir(ROOT_DIR)
    
    mode = "dev"
    if len(sys.argv) > 1:
        if sys.argv[1] == "--release":
            mode = "release"
        elif sys.argv[1] == "--clean":
            clean()
            return
    
    clean()
    
    if mode == "release":
        build_nuitka()
    else:
        build_pyinstaller()
    
    print("\n📦 Pour créer l'installeur Windows, utilisez scripts/installer.iss avec Inno Setup")


if __name__ == "__main__":
    main()
