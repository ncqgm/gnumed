!define MUI_PRODUCT "GNUmedArchive" ;Define your own software name here
!define MUI_VERSION "0.1" ;Define your own software version here

CRCCheck On
; Script create for version 2.0b0 1.24 (06.dec.02) with GUI NSIS (c) by Dirk Paehl. Thank you for use my program

 !include "${NSISDIR}\Contrib\Modern UI\System.nsh"



;--------------------------------
;Configuration
 
 !define MUI_LICENSEPAGE
 !define MUI_COMPONENTSPAGE
 !define MUI_DIRECTORYPAGE
 !define MUI_ABORTWARNING
 !define MUI_UNINSTALLER
 !define MUI_UNCONFIRMPAGE

;---------------------------------
 ;Languages
  !insertmacro MUI_LANGUAGE "German"
  !insertmacro MUI_LANGUAGE "English"
  !insertmacro MUI_LANGUAGE "French"
  !insertmacro MUI_LANGUAGE "Spanish"
  !insertmacro MUI_LANGUAGE "SimpChinese"
  !insertmacro MUI_LANGUAGE "TradChinese"    
  !insertmacro MUI_LANGUAGE "Japanese"    
  !insertmacro MUI_LANGUAGE "Italian"
  !insertmacro MUI_LANGUAGE "Dutch"
  !insertmacro MUI_LANGUAGE "Polish"
  !insertmacro MUI_LANGUAGE "Greek"
  !insertmacro MUI_LANGUAGE "Russian"
  !insertmacro MUI_LANGUAGE "PortugueseBR"
  !insertmacro MUI_LANGUAGE "Ukrainian"
  !insertmacro MUI_LANGUAGE "Czech"
  !insertmacro MUI_LANGUAGE "Bulgarian"

;-----------------------------------

;General
OutFile "setup.exe"

 
  ;License dialog
  LicenseData /LANG=${LANG_GERMAN} "${NSISDIR}\Contrib\License\GPL\gpl_de.txt"
  LicenseData /LANG=${LANG_ENGLISH} "${NSISDIR}\Contrib\License\GPL\gpl.txt"
  LicenseData /LANG=${LANG_FRENCH} "${NSISDIR}\Contrib\Modern UI\License.txt"
  LicenseData /LANG=${LANG_SPANISH} "${NSISDIR}\Contrib\Modern UI\License.txt"
  LicenseData /LANG=${LANG_SIMPCHINESE} "${NSISDIR}\Contrib\Modern UI\License.txt"
  LicenseData /LANG=${LANG_TRADCHINESE} "${NSISDIR}\Contrib\Modern UI\License.txt"
  LicenseData /LANG=${LANG_JAPANESE} "${NSISDIR}\Contrib\Modern UI\License.txt"
  LicenseData /LANG=${LANG_ITALIAN} "${NSISDIR}\Contrib\Modern UI\License.txt"
  LicenseData /LANG=${LANG_DUTCH} "${NSISDIR}\Contrib\Modern UI\License.txt"
  LicenseData /LANG=${LANG_POLISH} "${NSISDIR}\Contrib\Modern UI\License.txt"
  LicenseData /LANG=${LANG_GREEK} "${NSISDIR}\Contrib\Modern UI\License.txt"
  LicenseData /LANG=${LANG_RUSSIAN} "${NSISDIR}\Contrib\Modern UI\License.txt"
  LicenseData /LANG=${LANG_PORTUGUESEBR} "${NSISDIR}\Contrib\Modern UI\License.txt"
  LicenseData /LANG=${LANG_UKRAINIAN} "${NSISDIR}\Contrib\Modern UI\License.txt"
  LicenseData /LANG=${LANG_CZECH} "${NSISDIR}\Contrib\Modern UI\License.txt"
  LicenseData /LANG=${LANG_BULGARIAN} "${NSISDIR}\Contrib\Modern UI\License.txt"


  ;Component-select dialog
    ;Titles
    LangString TITLE_program_files ${LANG_ENGLISH} "program files"
    LangString TITLE_program_modules ${LANG_ENGLISH} "program modules"
    LangString TITLE_config_file ${LANG_ENGLISH} "config-file"
    LangString TITLE_manual ${LANG_ENGLISH} "manual"
    LangString TITLE_program_files ${LANG_GERMAN} "Programmdateien"
    LangString TITLE_program_modules ${LANG_GERMAN} "Programmmodule"
    LangString TITLE_config_file ${LANG_GERMAN} "Konfigurationsdatei"
    LangString TITLE_manual ${LANG_GERMAN} "Handbuch"

;    LangString TITLE_manual ${LANG_FRENCH} "modern.exe"
;    LangString TITLE_SecCopyUI ${LANG_GERMAN} "modern.exe"
;    LangString TITLE_SecCopyUI ${LANG_SPANISH} "modern.exe"
;    LangString TITLE_SecCopyUI ${LANG_SIMPCHINESE} "modern.exe"
;    LangString TITLE_SecCopyUI ${LANG_TRADCHINESE} "modern.exe"
;    LangString TITLE_SecCopyUI ${LANG_JAPANESE} "modern.exe"
;    LangString TITLE_SecCopyUI ${LANG_ITALIAN} "modern.exe"
;    LangString TITLE_SecCopyUI ${LANG_DUTCH} "modern.exe"
;    LangString TITLE_SecCopyUI ${LANG_POLISH} "modern.exe"
;    LangString TITLE_SecCopyUI ${LANG_GREEK} "modern.exe"
;    LangString TITLE_SecCopyUI ${LANG_RUSSIAN} "modern.exe"
;    LangString TITLE_SecCopyUI ${LANG_PORTUGUESEBR} "modern.exe"
;    LangString TITLE_SecCopyUI ${LANG_UKRAINIAN} "modern.exe"
;    LangString TITLE_SecCopyUI ${LANG_CZECH} "modern.exe"
    LangString TITLE_SecCopyUI ${LANG_BULGARIAN} "modern.exe"
    
  ;Descriptions
  ;German
  LangString DESC_program_files ${LANG_German} "Programmdateien - notwendig"
  LangString DESC_client_modules ${LANG_German} "Programmmodule - notwendig"
  LangString DESC_config_file ${LANG_German} "Konfigurationsdatei - Achtung ! überschreibt bereits vorhandene eigene angepasste Konfigurationen"
  LangString DESC_manual ${LANG_German} "Handbuch"
  ;English
  LangString DESC_program_files ${LANG_English} "program files - obligatory"
  LangString DESC_client_modules ${LANG_English} "program mmodules - obligatory"
  LangString DESC_config_file ${LANG_English} "config file - Beware ! overwrites existing files with default values"
  LangString DESC_manual ${LANG_English} "manual"


  ;Folder-select dialog 
  InstallDir "$PROGRAMFILES\${MUI_PRODUCT}"

;--------------------------------
;Modern UI System
!insertmacro MUI_SYSTEM 
;--------------------------------
;Installer Sections
     
Section $(TITLE_program_files)" section_1
SetOutPath "$INSTDIR\client"
FILE "C:\temp\client\gmScanMedDocs.py"
FILE "C:\temp\client\import-med_docs.py"
FILE "C:\temp\client\index-med_docs.py"
FILE "C:\temp\client\run-indexer.bat"
FILE "C:\temp\client\run-scanner.bat"
FILE "C:\temp\client\run-viewer.bat"
FILE "C:\temp\client\gmShowMedDocs.py"
FILE "C:\temp\client\scan.bat"
FILE "C:\temp\client\index.bat"
FILE "C:\temp\client\view.bat"
SectionEnd

Section $(TITLE_program_modules) section_2
SetOutPath "$INSTDIR\client\modules"
FILE "C:\temp\client\modules\docDocument.py"
FILE "C:\temp\client\modules\docMime.py"
FILE "C:\temp\client\modules\docPatient.py"
FILE "C:\temp\client\modules\gmCfg.py"
FILE "C:\temp\client\modules\gmExceptions.py"
FILE "C:\temp\client\modules\gmLoginInfo.py"
FILE "C:\temp\client\modules\gmLog.py"
FILE "C:\temp\client\modules\gmPG.py"
FILE "C:\temp\client\modules\gmCfg.py"
FILE "C:\temp\client\modules\docDatabase.py"
FILE "C:\temp\client\modules\docXML.py"
FILE "C:\temp\client\modules\gmCLI.py"
FILE "C:\temp\client\modules\docMagic.py"
FILE "C:\temp\client\modules\gmBackendListener.py"
FILE "C:\temp\client\modules\gmPhraseWheel.py"
FILE "C:\temp\client\modules\gmI18N.py"
FILE "C:\temp\client\modules\gmDispatcher.py"
SetOutPath "$INSTDIR\client\locale\de_DE@euro\LC_MESSAGES"
FILE "C:\temp\client\locale\de_DE@euro\LC_MESSAGES\gnumed-archive.mo"
SectionEnd

Section $(TITLE_config_file) section_3
SetOutPath "$INSTDIR\client"
FILE "C:\temp\client\gnumed-archive.conf"
SectionEnd

Section $(TITLE_manual) section_4
SetOutPath "$INSTDIR\client\doc"
FILE "C:\temp\client\doc\README-GnuMed-Archiv-de.txt"
SectionEnd


   ;Add Shortcuts
Section ""
CreateDirectory "$SMPROGRAMS\GNUmedArchive"
  CreateShortCut "$SMPROGRAMS\GNUmedArchive\Uninstall.lnk" "$INSTDIR\uninst.exe" "" "$INSTDIR\uninst.exe" 0
  CreateShortCut "$SMPROGRAMS\GNUmedArchive\run-scanner" "$INSTDIR\client\scan.bat" "" "$INSTDIR\client\scan.bat" 0
  CreateShortCut "$SMPROGRAMS\GNUmedArchive\run-indexer" "$INSTDIR\client\index.bat" "" "$INSTDIR\client\index.bat" 0
  CreateShortCut "$SMPROGRAMS\GNUmedArchive\run-viewer" "$INSTDIR\client\view.bat" "" "$INSTDIR\client\view.bat" 0
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GNUmedArchive" "DisplayName" "GNUmedArchive (remove only)"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GNUmedArchive" "UninstallString" "$INSTDIR\Uninst.exe"
  WriteUninstaller "$INSTDIR\Uninst.exe"
 
 ;Display the Finish header
 ;Insert this macro after the sections if you are not using a finish page
 
SectionEnd
 
    !insertmacro MUI_SECTIONS_FINISHHEADER

;--------------------------------
;Installer Functions

Function .onInit

  ;Language selection

  ;Font
  Push Tahoma
  Push 8

  ;Languages
  !insertmacro MUI_LANGDLL_PUSH "English"
  !insertmacro MUI_LANGDLL_PUSH "French"
  !insertmacro MUI_LANGDLL_PUSH "German"
  !insertmacro MUI_LANGDLL_PUSH "Spanish"
  !insertmacro MUI_LANGDLL_PUSH "SimpChinese"
  !insertmacro MUI_LANGDLL_PUSH "TradChinese"    
  !insertmacro MUI_LANGDLL_PUSH "Japanese"    
  !insertmacro MUI_LANGDLL_PUSH "Italian"
  !insertmacro MUI_LANGDLL_PUSH "Dutch"
  !insertmacro MUI_LANGDLL_PUSH "Polish"
  !insertmacro MUI_LANGDLL_PUSH "Greek"
  !insertmacro MUI_LANGDLL_PUSH "Russian"
  !insertmacro MUI_LANGDLL_PUSH "PortugueseBR"
  !insertmacro MUI_LANGDLL_PUSH "Ukrainian"
  !insertmacro MUI_LANGDLL_PUSH "Czech"
  !insertmacro MUI_LANGDLL_PUSH "Bulgarian"
  
  Push 16F ;16 = number of languages, F = change font

  LangDLL::LangDialog "Installer Language" "Please select a language."

  Pop $LANGUAGE
  StrCmp $LANGUAGE "cancel" 0 +2
    Abort

FunctionEnd
 
;--------------------------------  
;Descriptions 
                                    
!insertmacro MUI_FUNCTIONS_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${section_1} $(DESC_program_files)
    !insertmacro MUI_DESCRIPTION_TEXT ${section_2} $(DESC_client_modules)
    !insertmacro MUI_DESCRIPTION_TEXT ${section_3} $(DESC_config_file)
    !insertmacro MUI_DESCRIPTION_TEXT ${section_4} $(DESC_manual)
!insertmacro MUI_FUNCTIONS_DESCRIPTION_END
 
 
;--------------------------------
    
;Uninstaller Section
   
Section "Uninstall" 
 
  ;Add your stuff here  
   
  ;Delete Files 
  Delete "$INSTDIR\client\doc\*.*"
  RmDir "$INSTDIR\client\doc\"
  Delete "$INSTDIR\client\modules\*.*"
  RmDir "$INSTDIR\client\modules\"
  Delete "$INSTDIR\client\locale\de_DE@euro\LC_MESSAGES\*.*"
  RmDir "$INSTDIR\client\locale\de_DE@euro\LC_MESSAGES\"
  RmDir "$INSTDIR\client\locale\de_DE@euro\"
  RmDir "$INSTDIR\client\locale\"
  Delete "$INSTDIR\client\*.*"
  RmDir "$INSTDIR\client\"
  Delete "$INSTDIR\*.*"
  RmDir "$INSTDIR\"
   
  ;Delete Start Menu Shortcuts
  Delete "$SMPROGRAMS\GNUmedArchive\*.*"
  RmDir "$SMPROGRAMS\GNUmedArchive\"
  ;Delete Uninstaller And Unistall Registry Entries
  DeleteRegKey HKEY_LOCAL_MACHINE "SOFTWARE\GNUmedArchive"
  DeleteRegKey HKEY_LOCAL_MACHINE "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\GNUmedArchive"
  RMDir "$INSTDIR"
  !insertmacro MUI_UNFINISHHEADER 
            
SectionEnd
   
;eof
