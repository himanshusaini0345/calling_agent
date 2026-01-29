; Voice Assistant Pipeline - Inno Setup Installer Script
; This creates a professional Windows installer (.exe)
; Requires Inno Setup: https://jrsoftware.org/isinfo.php
; Build with: iscc installer.iss

#define MyAppName "Voice Assistant Pipeline"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Your Name"
#define MyAppURL "https://github.com/yourusername/voice-assistant"
#define MyAppExeName "VoiceAssistantServer.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
AppId={{YOUR-GUID-HERE}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE.txt
; Uncomment the following line to run in non administrative install mode
;PrivilegesRequired=lowest
OutputDir=installer_output
OutputBaseFilename=VoiceAssistantPipeline_Setup
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main executable (if using PyInstaller)
Source: "dist\VoiceAssistantServer.exe"; DestDir: "{app}"; Flags: ignoreversion; Check: FileExists('dist\VoiceAssistantServer.exe')

; Python scripts (alternative to exe)
Source: "server.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "pipeline.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "config_examples.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "test_client.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion

; Provider package
Source: "providers\*"; DestDir: "{app}\providers"; Flags: ignoreversion recursesubdirs createallsubdirs

; Documentation
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "QUICKSTART.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "ARCHITECTURE.md"; DestDir: "{app}"; Flags: ignoreversion

; Configuration files
Source: ".env.example"; DestDir: "{app}"; Flags: ignoreversion
Source: "setup.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "start_server.bat"; DestDir: "{app}"; Flags: ignoreversion

; Models directory (empty, user downloads models)
; NOTE: Uncomment if you want to include pre-downloaded models
; Source: "models\*"; DestDir: "{app}\models"; Flags: ignoreversion recursesubdirs createallsubdirs

[Dirs]
Name: "{app}\models"; Permissions: users-full

[Icons]
Name: "{group}\Voice Assistant Server"; Filename: "{app}\start_server.bat"; WorkingDir: "{app}"
Name: "{group}\Setup Environment"; Filename: "{app}\setup.bat"; WorkingDir: "{app}"
Name: "{group}\Quick Start Guide"; Filename: "{app}\QUICKSTART.md"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\start_server.bat"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\QUICKSTART.md"; Description: "{cm:LaunchProgram,Quick Start Guide}"; Flags: shellexec postinstall skipifsilent

[Code]
var
  PythonPage: TInputOptionWizardPage;
  PythonPath: String;

function IsPythonInstalled: Boolean;
var
  ResultCode: Integer;
begin
  Result := Exec('python', '--version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0);
end;

procedure InitializeWizard;
begin
  PythonPage := CreateInputOptionPage(wpWelcome,
    'Python Installation Check', 
    'This application requires Python 3.8 or later',
    'Please ensure Python is installed and added to PATH before continuing.' + #13#10 + 
    'You can download Python from: https://www.python.org/downloads/' + #13#10#13#10 +
    'Make sure to check "Add Python to PATH" during installation.',
    False, False);
  
  PythonPage.Add('Python is installed and in PATH');
  PythonPage.Add('I will install Python manually later');
  
  if IsPythonInstalled then
    PythonPage.SelectedValueIndex := 0
  else
    PythonPage.SelectedValueIndex := 1;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  if CurPageID = PythonPage.ID then
  begin
    if PythonPage.SelectedValueIndex = 0 then
    begin
      if not IsPythonInstalled then
      begin
        MsgBox('Python is not detected in PATH.' + #13#10 + 
               'Please install Python first and make sure it''s added to PATH.', 
               mbError, MB_OK);
        Result := False;
      end;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    if IsPythonInstalled then
    begin
      // Run setup.bat to install dependencies
      if MsgBox('Would you like to run the setup script now to install dependencies and download models?', 
                mbConfirmation, MB_YESNO) = IDYES then
      begin
        Exec(ExpandConstant('{app}\setup.bat'), '', ExpandConstant('{app}'), SW_SHOW, ewWaitUntilTerminated, ResultCode);
      end;
    end;
  end;
end;
