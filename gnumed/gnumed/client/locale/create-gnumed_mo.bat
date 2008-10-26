@echo off
set DRIVE_LTR=%~d0
cd /d %~dp0

echo generate a gnumed.mo file from a translated $LANG.po file
echo first arg has to be ISO language code

rem $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/locale/create-gnumed_mo.bat,v $
rem $Revision: 1.2 $

SET LANGNAME=%1
SET MOFILE=%LANGNAME%-gnumed.mo

IF !==!%1 (
echo You didn't give an ISO language code as the first argument.
)  ELSE (
SET POFILE=%LANGNAME%.po

echo generating gnumed.mo for language %LANGNAME% ...
msgfmt -v -o %MOFILE% %POFILE%

echo You can now copy %MOFILE% into the appropriate language
echo specific directory such as './%LANGNAME%/LC_MESSAGES/'.
)