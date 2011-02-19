@echo off

SET WORKING_DIR=C:\workplace
SET CLIENT_VER=0.5.1
SET CLIENT_REV=1
SET SERVER_VER=v11.1
SET SERVER_REV=1
SET SOURCEDIR=0-5-1
SET COMPILER=c:\programme\nsis

SET ZIP=C:\Programme\7-zip
SET PREREQUSCLIENT=%WORKING_DIR%\prerequisitesclient
SET PREREQUSSERVER=%WORKING_DIR%\prerequisitesserver

rem del /S /Q user-manual

rem ###################################################
rem #                                                 #
rem # extracting copy of user manual (Wiki)           # 
rem #                                                 #
rem ###################################################

rem c:\tools\wget -v http://publicdb.gnumed.de/gm-manual/Main.TWikiGuest_Gnumed.zip
rem c:\tools\unzip Main.TWikiGuest_Gnumed.zip -d user-manual

rem copy user-manual\Release-01.html user-manual\index.html 

rem del Main.TWikiGuest_Gnumed.zip

echo ###################################################
echo #                                                 #
echo # build mo-files from $LANG.po file               #
echo #                                                 #
echo ###################################################

cd %WORKING_DIR%\gnumed-%SOURCEDIR%\gnumed\client\locale  
call create-gnumed_mo.bat de
call create-gnumed_mo.bat de
call create-gnumed_mo.bat es
call create-gnumed_mo.bat es
call create-gnumed_mo.bat it
call create-gnumed_mo.bat it
call create-gnumed_mo.bat fr
call create-gnumed_mo.bat fr
call create-gnumed_mo.bat fr

echo ###################################################
echo #                                                 #
echo # running makensis to build installation binary   #
echo #                                                 #
echo ###################################################

%COMPILER%\makensis %WORKING_DIR%\gnumed_client-%CLIENT_VER%.nsi
%COMPILER%\makensis %WORKING_DIR%\gnumed_server-%SERVER_VER%.nsi

echo ###################################################
echo #                                                 #
echo # building all-in-one package for the client      #
echo #                                                 #
echo ###################################################

cd %WORKING_DIR%

%ZIP%\7z a -y data.7z GNUmed-client.%CLIENT_VER%-%CLIENT_REV%.exe %PREREQUSCLIENT% -sfx

copy /b %ZIP%\7zS.sfx + %WORKING_DIR%\gnumed-%SOURCEDIR%\gnumed\dists\Windows\7zip_client.conf + %WORKING_DIR%\data.7z %WORKING_DIR\%GNUmed-client.%CLIENT_VER%-full%CLIENT_REV%.exe

del data.7z


echo ###################################################
echo #                                                 #
echo # building all-in-one package for the server      #
echo #                                                 #
echo ###################################################

cd %WORKING_DIR%

%ZIP%\7z a -y data.7z GNUmed-server.%SERVER_VER%-%SERVER_REV%.exe %PREREQUSSERVER% -sfx

copy /b %ZIP%\7zS.sfx + %WORKING_DIR%\gnumed-%SOURCEDIR%\gnumed\dists\Windows\7zip_server.conf + %WORKING_DIR%\data.7z %WORKING_DIR\%GNUmed-server.%SERVER_VER%-full%SERVER_REV%.exe

del data.7z