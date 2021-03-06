; basic script template for NullsoftInstallerPackager
;
; Copyright 2010 Patrick Spendrin <ps_ml@gmx.de>
; Copyright 2016 Kevin Funk <kfunk@kde.org>

; registry stuff
!define regkey "Software\${company}\${productname}"
!define uninstkey "Software\Microsoft\Windows\CurrentVersion\Uninstall\${productname}"

!define startmenu "$SMPROGRAMS\${productname}"
!define uninstaller "uninstall.exe"

;--------------------------------

XPStyle on
ShowInstDetails hide
ShowUninstDetails hide

SetCompressor /SOLID lzma

Name "${productname}"
Caption "${productname} ${version}"

OutFile "${setupname}"
!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "x64.nsh"

;!define MUI_ICON
${icon}
;!define MUI_ICON

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY

;!insertmacro MUI_PAGE_LICENSE
${license}
;!insertmacro MUI_PAGE_LICENSE

!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!define MUI_FINISHPAGE_RUN_TEXT "Run ${productname}"
!define MUI_FINISHPAGE_RUN "$INSTDIR\${executable}"
!define MUI_FINISHPAGE_LINK "Visit project homepage"
!define MUI_FINISHPAGE_LINK_LOCATION "${website}"
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

SetDateSave on
SetDatablockOptimize on
CRCCheck on
SilentInstall normal

InstallDir "${defaultinstdir}\${productname}"
InstallDirRegKey HKLM "${regkey}" "Install_Dir"

Var /global ExistingInstallation

Function .onInit
!if ${architecture} == "x64"
  ${IfNot} ${RunningX64}
  MessageBox MB_OK|MB_ICONEXCLAMATION "This installer can only be run on 64-bit Windows."
  Abort
  ${EndIf}
!endif
ReadRegStr $R0 HKLM "${regkey}" "Install_Dir"
${IfNot} $R0 == ""
  StrCpy $ExistingInstallation $R0
${EndIf}
FunctionEnd


;--------------------------------

AutoCloseWindow false


; beginning (invisible) section
Section
${IfNot} $ExistingInstallation == ""
  ExecWait '"$ExistingInstallation\${uninstaller}" /S _?=$ExistingInstallation'
${EndIf}
  WriteRegStr HKLM "${regkey}" "Install_Dir" "$INSTDIR"
  ; write uninstall strings
  WriteRegStr HKLM "${uninstkey}" "DisplayName" "${productname}"
  WriteRegStr HKLM "${uninstkey}" "UninstallString" '"$INSTDIR\${uninstaller}"'
  WriteRegStr HKLM "${uninstkey}" "DisplayIcon" "$INSTDIR\${executable}"
  WriteRegStr HKLM "${uninstkey}" "URLInfoAbout" "${website}"
  WriteRegStr HKLM "${uninstkey}" "Publisher" "KDE"
  WriteRegStr HKLM "${uninstkey}" "DisplayVersion" "${version}"

  SetOutPath $INSTDIR


; package all files, recursively, preserving attributes
; assume files are in the correct places

File /a /r /x "*.nsi" /x "${setupname}" "${srcdir}\*.*"

WriteUninstaller "${uninstaller}"

SectionEnd

; create shortcuts
Section
SetShellVarContext all
CreateDirectory "${startmenu}"
SetOutPath $INSTDIR ; for working directory
CreateShortCut "${startmenu}\${productname}.lnk" "$INSTDIR\${executable}"
CreateShortCut "${startmenu}\Uninstall.lnk" "$INSTDIR\uninstall.exe"
${extrashortcuts}
SectionEnd

;post install
Section
SetOutPath "$INSTDIR"
!if "${vcredist}" != "none"
    File /a /oname=vcredist.exe "${vcredist}"
    ExecWait '"$INSTDIR\vcredist.exe" /passive /norestart'
!endif
ExecWait '"$INSTDIR\bin\update-mime-database.exe" "$INSTDIR\share\mime"'
ExecWait '"$INSTDIR\bin\kbuildsycoca5.exe" "--noincremental"'
Delete "$INSTDIR\vcredist.exe"
SectionEnd

; Uninstaller
; All section names prefixed by "Un" will be in the uninstaller

UninstallText "This will uninstall ${productname}."

Section "Uninstall"
SetShellVarContext all
ExecWait '"$INSTDIR\bin\kdeinit5.exe" "--shutdown"'
ExecWait '"taskkill" "/F" "/IM" "dbus-daemon.exe"'

DeleteRegKey HKLM "${uninstkey}"
DeleteRegKey HKLM "${regkey}"

Delete "${startmenu}\${productname}.lnk"
Delete "${startmenu}\Uninstall.lnk"

RMDir /r "${startmenu}"
RMDir /r "$INSTDIR"

SectionEnd

