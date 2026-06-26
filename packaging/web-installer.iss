#define MyAppName "TransVideo"
#define MyAppVersion "1.0"
#define MyAppPublisher "HYowshi"
#define MyAppExeName "TransVideo.exe"

[Setup]
AppId={{7B9B7E0C-7D2D-45DD-93F9-8F4F8F53B7F0}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=..\LICENSE
OutputDir=..\installer-dist
OutputBaseFilename=TransVideo-Web-Setup-{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
SetupIconFile=..\videotrans\styles\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
PrivilegesRequired=lowest

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Tạo lối tắt ngoài Desktop"; GroupDescription: "Lối tắt:"; Flags: unchecked

[Files]
Source: "..\installer-staging\TransVideo\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Hướng dẫn sử dụng"; Filename: "{app}\docs\HUONG_DAN_SU_DUNG.md"
Name: "{group}\Gỡ cài đặt {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Mở {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\.venv"
Type: filesandordirs; Name: "{app}\tmp"
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\output"
Type: filesandordirs; Name: "{app}\models"
Type: files; Name: "{app}\.transvideo-installing"
Type: files; Name: "{app}\.uv-sync.lock"
Type: filesandordirs; Name: "{localappdata}\pyvideotrans"
Type: filesandordirs; Name: "{tmp}\pyvideotrans"

[Registry]
Root: HKCU; Subkey: "Software\pyvideotrans"; Flags: uninsdeletekeyifempty
