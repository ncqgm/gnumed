# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/blobs_hilbert/docs/Attic/README-GnuMed-Installation-de.txt,v $
# $Revision: 1.1 $
#------------------------------------------------------------------------

Gnumed Installationsanleitung
###############################
0.  Voraussetzungen
###############################

Python
------

Linux )	Bei Linux kann man sich entscheiden ob man Python von den Quellen installiert oder auf
	die Pakete von Distributionen zurückgreift.

	Suse 8.0 ) Folgende Pakete müssen installiert werden. Dazu kann man yast2 benutzen.
		python ; python-devel ; python-doc ;

	Andere ) Man kann auch von den Quellen installieren. Diese können von
		http://www.python.org/ftp/python/2.2.1/Python-2.2.1.tgz heruntergeladen werden.

Windows ) Für Windows gibt es einen komfortablen Installer.

	http://www.python.org/ftp/python/2.2.1/Python-2.2.1.exe

Mac ) 	http://www.python.org/2.2.1/mac.html oder http://www.cwi.nl/~jack/macpython.html


WxWindows - www.wxwindows.org
---------
Linux )	Suse 8.0 ) Folgende Pakete beschafft man sich bei www.sourceforge.net
		http://prdownloads.sourceforge.net/wxwindows/wxGTK-2.3.2-1.i386.rpm
		http://prdownloads.sourceforge.net/wxwindows/wxGTK-devel-2.3.2-1.i386.rpm
		http://prdownloads.sourceforge.net/wxwindows/wxGTK-gl-2.3.2-1.i386.rpm

	Andere )Man kann auch alles von Quellen installieren
		http://prdownloads.sourceforge.net/wxwindows/wxGTK-2.3.2.tar.gz

Windows )Für Windows gibt es einen komfortablen Installer.
		http://prdownloads.sourceforge.net/wxwindows/wxMSW-2.2.9.zip

Wxpython - www.wxpython.org
--------

Linux )	Voraussetzung für wxpython sind "glib" und "gtk+". Die sind oft schon installiert
	Bei Suse kann man yast2 aufrufen und nach "glib" und "gtk" suchen. Wenn links vom Paketnamen
	ein "i" steht, ist es bereits installiert.

	Suse 8.0 ) Bei mir ist installiert : gtk ; gtk-devel ; gtkmm ; gtkmm-devel ; python-gtk ;
		wxGTK ; wxGTK-devel ; wxGTK-gl

		Ich habe folgende Pakete von Sourceforge heruntergeladen :

		http://prdownloads.sourceforge.net/wxpython/wxPython-2.3.2.1-1-Py22.i386.rpm?download
		http://prdownloads.sourceforge.net/wxpython/wxPython-gl-2.3.2.1-1-Py22.i386.rpm?download
		http://prdownloads.sourceforge.net/wxpython/wxPython-tools-2.3.2.tar.gz?download

	Andere )Man kann auch alles von Quellen installieren
		http://prdownloads.sourceforge.net/wxpython/wxPython-docs-2.3.2.tar.gz?download
		http://prdownloads.sourceforge.net/wxpython/wxPython-2.3.2.1.tar.gz

Windows )Für Windows gibt es einen komfortablen Installer.
	http://prdownloads.sourceforge.net/wxpython/wxPython-2.3.2.1-Py22.exe


Posgresql-Datenbank
---------
Linux ) Suse 8.0 ) Von der CD oder aus dem Netz (http://www.postgresql.org) muss das Paket postgresql
		installiert werden. Zusätzlich habe ich noch folgende Pakete installliert :

		postgresl-devel ; postgresql-libs ; postgresql-server

Python-Schnittstelle für PostgreSQL
---------

Linux )   http://prdownloads.sourceforge.net/pypgsql/pypgsql-2.2.tar.gz?download
	Die Datei enthält eine readme in der die Installation beschrieben ist.
	Man muss die Datei setup.py an das eigene system anpassen bevor es kompiliert wird.

Windows ) Auch für dieses Paket gibt es einen Installer
		http://prdownloads.sourceforge.net/pypgsql/pyPgSQL-2.1.win32-py2.2.exe?download


Scanner-Anbindung
-----------------
Linux   - http://www.mostang.com/sane/        - scannen unter Linux

Windows - http://twainmodule.sourceforge.net/ - damit man von Python aus Scannen kann (Windows)


PythonImagingLibrary
--------------------
    http://www.pythonware.com

mx-tools
-------------------
    http://www.egenix.com/files/python/ - muss zur Python-Version passen


GNUmed - entweder komplett oder Teile
---------------------------------------
    http://savannah.gnu.org/projects/gnumed/


################
1. Installation
################
Gnumed

Sie sind dabei, Gnumed zu installieren. Gnumed ist in der Programmiersprache Python geschrieben.
Daher muss auf dem System Python installiert sein. Zusätzlich müssen noch andere Pakete
installiert sein. Die folgende Anleitung wurde mit Suse 8.0 getestet.Andere Distributionen
sollten auch funktionieren.

Nachdem alle oben genannten Pakete installiert worden sind , besorgt man sich den aktuellen
CVS-Baum. Dieser enthält die Quellen von Gnumed und GnumedArchiv

Vorausgesetzt man ist mit dem Internet verbunden, gibt man auf der Konsole folgendes
ein :
Wenn nach einem Passwort gefragt wird, einfach mit Enter-Taste bestätigen.

cvs -d:pserver:anoncvs@subversions.gnu.org:/cvsroot/gnumed login

cvs -z3 -d:pserver:anoncvs@subversions.gnu.org:/cvsroot/gnumed co gnumed

Damit werden die Quellen aus dem Internet geladen und im aktuellen Verzeihnis ein Unterverzeichnis
gnumed erstellt.

############
PostgreSQL

Vorrausgesetzt alle Pakete sind wie oben beschrieben installiert, erzeugt man
nun die Datenank für Gnumed. Bei der Installation von PostgreSQL wird ein
Benutzer namens "postgres" erzeugt. Dieser Benutzer "postgres" kann
Benutzer für die Gnumed-Datenbank anlegen.

Voraussetzung ist, dass PostgreSQL gestartet ist. Das funktioniert bei
jeder Linux-Distribution anders.
Bei Suse 8.0 lautet der Befehl : "rcpostgresql restart"

auf der Konsole:

1.) su root              # wechselt den aktive Benutzer zu root
2.) su postgres          # wechselt den aktive Benutzer zu postgres
3.) createuser $Arzt1    # erzeugt einen Datenbanknutzer "Arzt1"
4.) createdb gnumed      # erzeugt eine Datenbank mit dem Namen "gnumed"

Jetzt muss die Datenbank noch mit Inhalten gefüllt werden.
Dazu wechselt man in das Verzeichnis gnumed/gnumed/gnumed/server/sql

5.) psql gnumed
6.) \i gmconfiguration.sql
7.) \i gnumed.sql        # usw. mit allen *.sql-Dateien die dort liegen außer gmBlobs.sql

für GnumedArchiv muss die Datei gmBlobs.sql an die individuellen
Bedürfnisse angepasst werden.
Eigene Typen werden werden einfach ab 100 hinzugefügt.

Bsp.:

INSERT INTO doc_type(id, name) values(100,'Befundtyp1');
INSERT INTO doc_type(id, name) values(102,'Entlassung Chirurgie');
usw.

8.) \i gmBlobs.sql
9.) exit          # dadurch wird wieder zu root-Benutzer gewechselt
10.) rcpostgresql restart

#################
2.Starten
#################
man wechselt jetzt in das Unterverzeichnis /gnumed/gnumed/gnumed/client/wxpython/
und gibt auf der Kommandozeile ein:

python gumed.py --talkback

Jetzt sollte ein graphischer Anmeldedialog erscheinen. Wenn nicht, fragt man auf der Mailing-Liste
um Rat. Im Idealfall schickt man die Datei gnumed.log zusammen mit einer Fehlerbeschreibung an
fixme@gnumed.net

#################
3.Helfen
#################
wenn man Gnumed gut findet und mithelfen will, geht man im Netz zu www.gnumed.de/whatucando.htm
und meldet sich freiwillig für dort hinterlegte Aufgaben.

#------------------------------------------------------------------------
$Log: README-GnuMed-Installation-de.txt,v $
Revision 1.1  2002-09-17 09:16:57  ncq
- added those files

