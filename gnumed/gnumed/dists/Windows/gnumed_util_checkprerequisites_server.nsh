;Title          GNUmed for Windows, NSIS v2 series installer script

;Check for Python and show splash screen
Function CheckDependencies
  Banner::show /NOUNLOAD "Checking for Depedencies ..."

  ReadRegStr $0 HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\Python.exe" ""
  StrCmp $5 "" 0 +2
    StrCpy $5 $0 ; complete path to python.exe from registry
  nsExec::Exec '"$5" -v'
  Pop $0
  StrCmp $0 0 checkwxPython
    MessageBox MB_YESNOCANCEL|MB_ICONEXCLAMATION "The installer can not find Python and \
	wxPython on this computer!$\r$\nPlease install Python and wxPython and run this \
	installer again.$\r$\nPress cancel if you are sure you have Python and wxPython \
	installed.$\r$\n$\r$\nWould you like the installer to open Python's download page \
	for you?" IDNO abort IDCANCEL splash
      ExecShell open \
	    http://www.python.org/download/releases/2.3.5/
      MessageBox MB_OK|MB_ICONINFORMATION "Please make sure you download Python 2.3.5. \
	    The current version of Python has not yet been tested" IDOK abort

  checkwxPython:
      ReadRegStr $0 HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\Python.exe" ""
        StrCpy $3 $0 -10 ; directory part of complete path to python.exe
        StrCpy $3 "$3Lib\site-packages\wx.pth"
      Pop $0
      IfFileExists $3 splash install_wxPython
      
     install_wxPython:
        MessageBox MB_YESNO|MB_ICONEXCLAMATION "The installer can not find wxPython \
		on this computer!$\r$\nPlease install wxPython and run this installer \
		again.$\r$\n$\r$\nWould you like the installer to open wxPython's download \
		page for you?" IDNO abort
        ExecShell open http://www.wxpython.org/download.php#binaries
        Goto abort

  splash:
    Banner::destroy
    ;File /oname=$PLUGINSDIR\splash.bmp splash.bmp
    ;File /oname=$PLUGINSDIR\splash.wav ..\snd\malus.wav

    advsplash::show 1800 350 187 -1 $PLUGINSDIR\splash

    Pop $0 ; $0 has '1' if the user closed the splash screen early,
        ; '0' if everything closed normal, and '-1' if some error occurred.
    Return

  abort:
    Banner::destroy
    Abort
FunctionEnd
