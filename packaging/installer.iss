#define MyAppName "TransVideo"
#define MyAppVersion "1.0"
#define MyAppPublisher "HYowshi"
#define MyAppExeName "TransVideo.exe"

[Setup]
AppId={{7B9B7E0C-7D2D-45DD-93F9-8F4F8F53B7F0}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL=https://github.com/HYowshi/TransVideo
AppSupportURL=https://github.com/HYowshi/TransVideo/issues
AppUpdatesURL=https://github.com/HYowshi/TransVideo/releases
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=..\LICENSE
OutputDir=..\installer-dist
OutputBaseFilename=TransVideo-Setup-{#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} full installer
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
VersionInfoVersion=1.0.0.0
VersionInfoCopyright=Copyright (C) {#MyAppPublisher}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
SetupIconFile=..\videotrans\styles\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName} {#MyAppVersion}
PrivilegesRequired=lowest
CloseApplications=yes
RestartApplications=no
SetupLogging=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Shortcuts:"; Flags: unchecked

[Files]
Source: "..\dist\TransVideo\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[InstallDelete]
Type: filesandordirs; Name: "{app}\tmp"
Type: filesandordirs; Name: "{app}\logs"

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{cmd}"; Parameters: "/c taskkill /IM {#MyAppExeName} /F /T >nul 2>nul"; Flags: runhidden

[UninstallDelete]
Type: filesandordirs; Name: "{app}\tmp"
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\output"
Type: filesandordirs; Name: "{app}\models"
Type: filesandordirs; Name: "{localappdata}\TransVideo"
Type: filesandordirs; Name: "{localappdata}\pyvideotrans"
Type: filesandordirs; Name: "{userappdata}\TransVideo"
Type: filesandordirs; Name: "{userappdata}\pyvideotrans"
Type: filesandordirs; Name: "{tmp}\TransVideo"
Type: filesandordirs; Name: "{tmp}\pyvideotrans"

[Registry]
Root: HKCU; Subkey: "Software\TransVideo"; ValueType: string; ValueName: "InstallDir"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\pyvideotrans"; Flags: uninsdeletekey
