# This the GNUMed windows installer 
# Copyright (C) 2002 Ian Haywood
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307,

# sections are taken from the Dia for Windows install script:  
# Copyright (C) 2000-2002 Steffen Macke

OutFile gnumed.exe
Name "GNUMed"
BGGradient off
CRCCheck off
InstallDir $PROGRAMFILES\GNUMed
LicenseText "Please read and agree to this license before continuing."
LicenseData COPYING.txt
ComponentText "This will install GNUMed 0.1 on your system. Select which options you want set up."
DirText "Select a directory to install GNUmed in."
UninstallText "This will uninstall GNUMed. Hit Next to uninstall, or Cancel to cancel."
InstallColors /windows
InstProgressFlags smooth
AutoCloseWindow true
SetCompress auto

Section -Main

# main files
SetOutPath - # set to instdir
#just vomit a snapshot of the installation
File /r "C:\Program Files\GNUMed\*.*" 

# auto-generate batch file
SetCompress off
FileOpen $1 "$INSTDIR\GNUMED.BAT" w
FileWrite $1 "@ECHO OFF"
FileWriteByte $1 "13"
FileWriteByte $1 "10"
# include our private DLL collection in the path
FileWrite $1 'set Path="$WINDOWS;$INSTDIR\DLLs"' # this variable must be double-quoted, not sure why!
FileWriteByte $1 "13"
FileWriteByte $1 "10"
FileWrite $1 'set GMED_DIR=$INSTDIR' 
FileWriteByte $1 "13"
FileWriteByte $1 "10"
FileWrite $1 '$INSTDIR\python.exe $INSTDIR\wxpython\gnumed.py'
FileWriteByte $1 "13"
FileWriteByte $1 "10"
FileClose $1

# add link icons on desktop and menu
# for current user
SetOutPath $DESKTOP
CreateShortCut "GNUMed.lnk" "$INSTDIR\GNUMED.BAT" "" "$INSTDIR\gnumed.ico" 0 SW_SHOWMINIMIZED
SetOutPath $SMPROGRAMS
CreateShortCut "GNUMed.lnk" "$INSTDIR\GNUMED.BAT" "" "$INSTDIR\gnumed.ico" 0 SW_SHOWMINIMISED

# for all users. This seems superfluous, but I think it is to guarantee 
# icon placement on older versions
SetShellVarContext all
SetOutPath $DESKTOP
CreateShortCut "GNUMed.lnk" "$INSTDIR\GNUMED.BAT" "" "$INSTDIR\gnumed.ico" 0 SW_SHOWMINIMIZED
SetOutPath $SMPROGRAMS
CreateShortCut "GNUMed.lnk" "$INSTDIR\GNUMED.BAT" "" "$INSTDIR\gnumed.ico" 0 SW_SHOWMINIMISED

# register the uninstaller with the Registry
WriteRegStr HKEY_LOCAL_MACHINE "Software\Microsoft\Windows\CurrentVersion\Uninstall\GNUMed 0.1" "DisplayName" "GNUMed (remove only)"
WriteRegStr HKEY_LOCAL_MACHINE "Software\Microsoft\Windows\CurrentVersion\Uninstall\GNUMed 0.1" "UninstallString" '"$INSTDIR\uninstall-gnumed.exe"'
WriteUninstaller "$INSTDIR\uninstall-gnumed.exe"
SectionEnd

Section "Uninstall"
DeleteRegValue HKEY_LOCAL_MACHINE "Software\Microsoft\Windows\CurrentVersion\Uninstall\GNUMed 0.1" "UninstallString"
DeleteRegValue HKEY_LOCAL_MACHINE "Software\Microsoft\Windows\CurrentVersion\Uninstall\GNUMed 0.1" "DisplayName"
DeleteRegKey HKEY_LOCAL_MACHINE "Software\Microsoft\Windows\CurrentVersion\Uninstall\GNUMed 0.1"
Delete "$INSTDIR\*.*"
RMDir \r "$INSTDIR"
SetShellVarContext current
Delete "$DESKTOP\GNUMed.lnk"
Delete "$SMPROGRAMS\GNUMed.lnk"
SetShellVarContext all
Delete "$DESKTOP\GNUMed.lnk"
Delete "$SMPROGRAMS\GNUMed.lnk"
SectionEnd












