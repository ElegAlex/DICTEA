; =============================================================================
; Script Inno Setup - Installeur Windows
; =============================================================================
; Prérequis: Inno Setup 6+ (https://jrsoftware.org/isinfo.php)
; Usage: Compiler ce script avec Inno Setup après avoir généré le build
; =============================================================================

#define MyAppName "Transcription Audio"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "TranscriptionApp"
#define MyAppExeName "TranscriptionApp.exe"

[Setup]
; Identifiant unique de l'application (générer un nouveau GUID pour chaque app)
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
; Désactiver la page de sélection du dossier de démarrage
DisableProgramGroupPage=yes
; Fichier licence (optionnel)
; LicenseFile=..\LICENSE.txt
; Dossier de sortie de l'installeur
OutputDir=..\installer
OutputBaseFilename=TranscriptionApp_Setup_{#MyAppVersion}
; Icône de l'installeur
; SetupIconFile=..\resources\icon.ico
; Compression maximale
Compression=lzma2/ultra64
SolidCompression=yes
; Version Windows minimum (Windows 10)
MinVersion=10.0
; Architecture 64-bit uniquement
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
; Nécessite les droits admin pour installer dans Program Files
PrivilegesRequired=admin
; Style moderne
WizardStyle=modern

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Copier tout le dossier de distribution PyInstaller
Source: "..\dist\TranscriptionApp\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Fichier de configuration
Source: "..\config.yaml"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Lancer l'application après installation (optionnel)
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Nettoyer les fichiers créés par l'application
Type: filesandordirs; Name: "{localappdata}\TranscriptionApp"
Type: filesandordirs; Name: "{app}\models"
Type: filesandordirs; Name: "{app}\output"
Type: filesandordirs; Name: "{app}\temp"
Type: files; Name: "{app}\*.log"

[Code]
// Vérifier si l'application est déjà en cours d'exécution
function IsAppRunning(): Boolean;
var
  ResultCode: Integer;
begin
  Exec('tasklist', '/FI "IMAGENAME eq {#MyAppExeName}" /NH', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Result := (ResultCode = 0);
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  // Avertir si l'application est en cours d'exécution
  if IsAppRunning() then
  begin
    MsgBox('Veuillez fermer {#MyAppName} avant de continuer l''installation.', mbError, MB_OK);
    Result := False;
  end;
end;

// Créer les dossiers nécessaires après installation
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    CreateDir(ExpandConstant('{app}\models'));
    CreateDir(ExpandConstant('{app}\output'));
    CreateDir(ExpandConstant('{app}\temp'));
  end;
end;
