# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/blobs_hilbert/docs/Attic/README-GnuMed-Archiv-de.txt,v $
# $Revision: 1.4 $
#------------------------------------------------------------------------

Sie lesen gerade eine Vorversion des Installationshandbuchs zu GNUmedArchiv

Inhalt :
--------

1.  Voraussetzung
2.  Installation
3.  Starten
4.  Loslegen
5.  Praxisprogrammanbindung


##############################
1.   Installation Voraussetzung
##############################

Sie sind dabei, GNUmedArchiv zu installieren. GNUmedArchiv ist in der Programmiersprache Python geschrieben.
Daher muss auf dem System Python installiert sein. Zusätzlich müssen noch andere Pakete
installiert sein. Die folgende Anleitung wurde mit Suse 8.0 getestet.Andere Distributionen
sollten auch funktionieren.Die Installation umfasst die Installation auf dem Client bzw. Arbeitsplatz
und die Installation der Datenbank auf dem Server.Damit GNUmed/Archive läuft, müssen von Ihrem System
einige Voraussetzungen erfüllt werden.

Sie brauchen:

auf dem Client
--------------

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

	Scanner-Anbindung
	-----------------
	Linux   - http://www.mostang.com/sane/        - scannen unter Linux

	Windows - http://twainmodule.sourceforge.net/ - damit man von Python aus Scannen kann (Windows)


	PythonImagingLibrary
	--------------------
	http://www.pythonware.com - PIL 1.1.3

	mx-tools
	-------------------
	http://www.egenix.com/files/python/ - muss zur Python-Version passen



Server
------
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


	Posgresql-Datenbank
	---------
	Linux ) Suse 8.0 ) Von der CD oder aus dem Netz (http://www.postgresql.org) muss das Paket postgresql
			installiert werden. Zusätzlich habe ich noch folgende Pakete installliert :
			postgresl-devel ; postgresql-libs ; postgresql-server


	Python-Schnittstelle für PostgreSQL
	---------

	Linux )   http://prdownloads.sourceforge.net/pypgsql/pypgsql-2.2.tar.gz?download
			Die Datei enthält eine Datei namens "readme" in der die Installation beschrieben ist.
			Man muss evtl. die Datei setup.py an das eigene System anpassen bevor es kompiliert wird.
			Wichtig sind dabei die Pfade zu den entsprechenden Bibliotheken.

	Windows ) Auch für dieses Paket gibt es einen Installer
			http://prdownloads.sourceforge.net/pypgsql/pyPgSQL-2.1.win32-py2.2.exe?download

	mx-tools
	-------------------
	http://www.egenix.com/files/python/ - muss zur Python-Version passen


#############################
2.   Installation
#############################
Client
------
	GNU/Linux )
	Entpacken Sie das Archiv 'gnumed-archive-client.tgz' in ein Verzeichnis Ihrer Wahl.
	Führen Sie dann in diesem Verzeichnis das Installationsskript 'install.sh' aus.

	Windows )
	Führen Sie das Installationsprogramm [setup.exe] aus.

	Wenn Sie GNUmedArchive nicht im Standardpfad installieren, müssen Sie die
	Dateien 'run-scanner.bat' , 'run-indexer.bat' und 'run-viewer.bat' entsprechend anpassen.
	Diese Dateien befinden sich im Installationsverzeichnis.

	Der Eintrag zur Sprachwahl befindet sich in den Dateien 'run-scanner.bat', 'run-indexer.bat'
	und 'run-indexer.bat'. Für die deutsche Oberfläche entfernen Sie bitte die Zeichenkette
	'REM' vor dem Eintrag 'set LANG=de_DE@EURO'.

	Sollte 'python.exe' auf Ihrem System nicht im Standardverzeichnis ' c:\python22' installiert
	sein, muss der richtige Pfad in die genannten *.bat-Dateien Eingetragen werden.

	Nicht vergessen, die Datei gnumed-archive.conf auf den Clients anzupassen damit
	die Datenbank auch erreicht wird. Diese Datei kann an verschiedenen Stellen abgelegt werden.

	GNU/Linux )
	Im Idealfall erzeugt man ein Verzeichnis '.gnumed' im Home-Verzeichnis des ausführenden
	Benutzers und kopiert die Datei gnumed-archive.conf in dieses
	Verzeichnis.

	Windows )
	In Windows ist es ratsam die Datei 'gnumed-archive.conf' ins selbe Verzeichnis wie die Programm-Dateien
	zu legen. Das ist automatisch der Fall wenn man GNUmedArchive via 'setup.exe' installiert.

	Eine Beispielkonfiguration (gnumed-archive.conf) findet sich im Archiv 'gnumed-archive-client.tgz' bzw.
	'setup.exe'
Server
-------

	GNUmed/Archive greift auf einen PostgreSQL-Server zu. Der läuft z.B unter
	Linux. Es ist wohl auch möglich den Server unter Windows laufen zu lassen. Diese
	Methode wird aber von uns nicht unterstützt. Mehr Infos dazu im Netz unter den
	Schlagworten 'running PostgreSQL under Windows' oder im GNUmed Handbuch.
	PostgreSQL ist jetzt auch für das Netzwerkbetriebssystem Novell erschienen und
	kann daher auch auf diesem Betriebssystem eingesetzt werden.

	Entpacken Sie das Archiv 'gnumed-archive-server.tgz' in ein Verzeichnis Ihrer Wahl.
	Für die Installation benötigen Sie root-Zugriff auf Ihr System.

	Passen Sie nun die Datei'german-doc_types.sql' an Ihre individuellen Bedürfnisse an.
	Diese Datei enthält die Einträge für die Befundtypen die später beim Zuordnen der
	eingescannten Befunde benötigt werden.

	Bsp.:

	INSERT INTO doc_type(id, name) values(101,'Befundtyp1');
	INSERT INTO doc_type(id, name) values(102,'Befundtyp2');
	INSERT INTO doc_type(id, name) values(103,'Befundtypx');
	usw.

	Die Zahl vor dem Befundtyp muss einmalig sein. Das bedeutet,
	das keine Zahl doppelt vergeben werden darf. Daher muss auch
	sichergestellt werden, dass die Zahl nicht bereits in der Datei
	'gmBlobs.sql' verwendet wird. Man schaut sich also die Datei 'gmBlobs.sql' an, schaut nach
	der größten Zahl und addiert dazu '1'. Diese Zahl ist dann die Zahl vor dem ersten Eintrag
	in der Datei'german-doc_types.sql'. Bei den folgenden Einträgen wird einfach hochgezählt.


	Jetzt ist es an der Zeit sich zu überlegen welche Benutzer mit welchen Rechten im
	Archiv arbeiten dürfen bzw. schreibend und/oder lesend zugreifen dürfen. Will man
	nur Testbenutzer anlegen muss nichts angepasst werden. Dafür reichen die Voreinstellungen
	in der Datei 'bootstrap-gm_db_system.conf'. Will man eigene Benutzer einrichten, erledigt man
	das am Besten mit einer eigenen Konfigurationsdatei. Man erzeugt beispielsweise eine
	neue Datei 'users.conf'. Dort trägt man dann eigene Gruppen und Benutzer ein. Diese Datei muss
	ein betsimmtes Format haben. Man orientiert sich am Besten am Format der Datei
	'bootstrap-gm_db_system.conf'.

	Ist alles soweit eingestellt, führt man das Installationsskript 'install.sh' aus und
	folgt den Anweisungen.

	Läuft die Installation ohne Fehler durch, erhalten Sie am Ende weitere Anweisungen
	was noch zu tun ist damit beispielsweise automatisch die angelieferten
	Befunde in die Datenbank gespeichert werden.
	
	Falls bei der Installation Fehler auftreten, ist es ratsam, einen Blick in das Fehlerprotokoll
	zu werfen. Für den Fall, dass auch das nicht zum Ziel führt kann eine Nachricht an die Mailing-Liste
	weiterhelfen. Bitte nicht vergessen, das Fehlerprotokoll anzuhängen.

	Passen Sie nun den Abschnitt [import] in der Konfigurationsdatei 'gnumed-archive.conf' an Ihre Bedürfnisse an.
#################
3.Starten
#################
Client
------
	GNU/Linux )

		'run-scanner.sh'
		'run-indexer.sh'
		'run-viewer.sh'

	MS Windows(TM)
		Im Startmenü wurden entsprechende Verknüpfungen angelegt

Server
------
	GNU/Linux )
		'run-importer.sh'

	Idealerweise legt man einen cron-job an der zu festgelegten Zeiten die Befunde
	in die Datenbank schiebt.

###############################
4.  Loslegen
###############################
    Das Dokumentenarchiv besteht aus vier Teilprogrammen.
    1) Scan-Modul
    2) Index-Modul
    3) Datenbank-Importer
    4) Betrachter

    und so ist der Ablauf ...

Teil 1: Erfassung
------------------------
Ein Stapel Befunde wird fortlaufend eingescannt. Mehrseitige
Dokumente behalten ihren inneren Zusammenhang. Das
Scanprogramm folgt dabei einem logischen Ablauf.

Schritt 1: Einscannen der Blätter. Hierbei wird jeder Scanner
mit TWAIN-Schnittstelle unter Microsoft Windows sowie jeder
mit SANE-Schnittstelle unter GNU/Linux unterstützt.

Schritt 2: Optional Ändern der Reihenfolge der Seiten. Dieser
Schritt ist nur notwendig wenn die Seiten nicht in der
natürlichen Reihenfolge eingescannt wurden.

Schritt 3: Ist ein Befund vollständig erfasst, wird dieser
gespeichert. Dadurch wird auf dem Bildschirm ein eindeutiges
Identifikationskürzel (Paginiernummer) angezeigt. Diese Kennung
muss auf dem Befund vermerkt werden. Sie stellt den
einfachsten Zusammenhang zwischen Papierbefund und
digitalisierter Version her.

Dann kann der nächste Befund erfasst werden.

Die Oberfläche des Programms ist speziell für diesen
Arbeitsablauf optimiert und enthält nur die die wichtigsten
Bedienelemente. Auf den Einsatz einer Maus kann verzichtet
werden. Für eine spätere Version ist geplant, die Kennung als
Barcode und im Klartext auf den Originalbefund zu drucken.
Dafür kann die freie Software GNUBarcode verwendet werden.

Teil 2: Zuordnung
------------------------
Dieses Programm dient der Zuordnung der gescannten Dokumente zu
einem Patienten. Die meisten kommerziellen Praxisprogramme
lassen für Fremdprogramme keinen direkten Zugriff auf die
elektronische Karteikarte zu. Man kann aber die
GDT/BDT-Schnittstelle nutzen, sofern das Praxisprogramm dies
unterstützt. Beispielsweise kann das Zuordnungsprogramm an
TurboMed als externes Programm angebunden werden. Bei Aufruf
werden die Stammdaten des aktuellen Patienten als BDT-Datei
übergeben und vom Zuordnungsprogramm gelesen. Dieser Umweg
entfällt beim Einsatz des Praxisprogramms GNUmed. Hier könnte
der zugeordnete Befund direkt in der elektronischen Kartei
vermerkt werden.

Auch die Zuordnungssoftware folgt wieder einem logischen
Ablauf.

Schritt 1: Laden des Befunds via Identifikationskürzel
(Paginiernummer) auf dem Befund. Diese muss in das
entsprechende Feld eingetippt werden. Zukünftig ist hier das
Einlesen via Barcode-Scanner vorgesehen. Doch auch ohne
Barcode-Scanner ist das Eintippen der Dokumentenkennung durch
ein intelligentes Eingabefeld sehr komfortabel. Bei Eingabe
einiger Zeichen werden automatisch alle noch nicht
zugeordneten Dokumente angeboten, deren Paginiernummer mit
diesen Zeichen beginnt. Weiteres Tippen grenzt die
Dokumentenauswahl immer mehr ein. Jederzeit kann das
gewünschte Dokument aus der Liste gewählt werden. So reichen
oft drei oder vier Zeichen aus, bis die Kennung eindeutig ist.

Schritt 2: Nach dem Laden der Befundseiten sind beschreibende
Felder auszufüllen. Dazu zählen Erstellungsdatum des Dokuments,
ein kurzer Kommentar, die Angabe des Befundtyps und ein Feld
für beliebig lange Anmerkungen. Von übergeordneter Bedeutung
ist die Angabe des Befundtyps. Dieser muß aus einer vorher
festzulegenden Liste ausgewählt werden. Dieser Liste können
jederzeit weitere Typen hinzugefügt werden. Diese relativ
starre Vorgabe bietet später deutlich höheren Nutzwert bei der
Auswahl von Dokumenten zur Ansicht.

Schritt 3: Sind alle Felder erfaßt, werden diese gespeichert.
Ein Skript überträgt nun im Hintergrund vollautomatisch die
indizierten Dokumente in die Datenbank. Dies kann bei großen
Datenmengen auch erst Nachts geschehen. Somit kann eine
zusätzliche Belastung des Netzwerkes während des Praxisbetriebs
vermieden werden. Auf Wunsch wird es möglich sein, die
Beweiskraft der eingescannten Dokumente mittels eines digitalen
Notarservice (z.B. GNotary) zu erhöhen.

Teil 3: Nutzung

Das Befundanzeigeprogramm wird entweder direkt aus GNUmed oder
aus einem herkömmlichen Praxisprogramm aufgerufen und zeigt
alle Befunde des aktuellen Patienten als Baumstruktur an. Die
eigentliche Darstellung der Befundseiten wird an Programme des
jeweiligen Betriebssystems delegiert. Dadurch ist das
Anzeigeprogramm nicht auf bestimmmte Dateitypen beschränkt. Es
können alle Dateitypen angezeigt werden, für die das
installierte Betriebssystem Anzeigeprogramme anbietet. Somit
können Grafik- ebenso wie Videodateien, Texte oder Audiodaten
zur Anzeige bzw. zu Gehör gebracht werden. Die beim Indizieren
erhobenen Metadaten erlauben einen effektiven Umgang mit den
Befunden. Befunde können nach Typen, Erstellungsdatum bzw.
-zeiträumen sowie nach Kommentaren gefiltert werden. Damit ist
es z.B. möglich, alle Sonographiebefunde eines Patienten für
einen bestimmten Zeitraum zu selektieren. Diese Funktionalität
ist noch in der Entwicklung. Es ist natürlich möglich,
ausgewählte Dokumente zurück an das Praxisprogramm zu
übergeben, beispielsweise zum Erstellen eines Arztbriefes.


#########################################
5. Praxisprogrammanbindung
#########################################

GNU/Linux
	GNUmed - GNUmedArchive ist Bestandteil von GNUmed und wird direkt als Plugin in das Programm integriert.

DOS
	Turbomed - Das Programm GNUmed/Archive soll direkt aus Turbomed heraus gestartet werden.
	Also müssen 'run-scanner.bat','run-indexer.bat','run-viewer.bat gestartet werden. Die Erfahrung
	zeigt, dass die DOS-Box von Turbomed keine Verzeichnisangaben honoriert. Also müssen wir eine Batch-
	Datei erzeugen die wiederum die gewünsche Batchdatei aufruft. Diese wird als externes Programm in der
	Turbomeddatei '289.gdt' eingetragen. Was man wie einzutragen hat, findet man im Turbomed-Handbuch im
	Kapitel 'GDT'

	Bei mir sieht die Datei so aus :

	[289.gdt]

	1
	2
	Befunde zuordnen #c:\gmtmp\pat_idx.dat#c:\Progra~1\gnumed~1\client\index.bat###
	3
	Befunde scannen #c:\gmtmp\pat_idx.dat#c:\Progra~1\gnumed~1\client\scan.bat###
	Befunde zuordnen #c:\gmtmp\pat_idx.dat#c:\Progra~1\gnumed~1\client\index.bat###
	4
	Befunde zuordnen #d:\gmtmp\pat_idx.dat#d:\Progra~1\gnumed~1\client\index.bat###
	Befunde anschauen #c:\gmtmp\pat_idx.dat#c:\Progra~1\gnumed~1\client\view.bat###

	Dadurch können die Arbeitsstationen 2,3 und 4 das Zuordnungsprogramm aus der Karteikarte heraus aufrufen.
	An Station 3 kann zusätzlich das Scanprogramm aufgerufen werden. Der Scan-Eintrag ist nur da sinnvoll wo
	auch ein Scanner oder eine Kamera angeschlossen ist.
	An Station 4 können dann die Befunde auch wieder angeschaut werden.

	Der Anteil "c:\gmtmp\pat_idx.dat" ist variabel. Der Eintrag "patient file" im Abschnitt [index] und [viewer]
	der Konfigurationsdatei gnumed-archive.conf muss auf diese Stelle zeigen. Unter MSDOS (auch im DOS-Fenster) darf
	diese Zeichenkette maximal 8+3 Zeichen lang sein. Sonst müssen die entsprechend verkürzten Namen
	angegebenen werden. Das funktioniert aber nicht immer und sollte vermieden werden.

	Bsp.
	c:\program files\gnumedarchiv\archivgnumed.bat  -> c:\progra~2\gnumed~1\archiv~1.bat

	Das Scan-Teilprogramm ist ja unabhängig vom Patienten und kann daher einfach als
	externes Programm angelegt werden. Es kann dann mit Strg-P aufgerufen werden. Man
	schaue sich den Abschnitt Fremdprogramme im Turbomed-Handbuch an.

	Die Programme werden in der Datei '289.BMN' definiert.


#------------------------------------------------------------------------
$Log: README-GnuMed-Archiv-de.txt,v $
Revision 1.4  2003-01-19 13:44:09  ncq
- new Englisch installation manual
- fixes for German

Revision 1.3  2002/12/22 22:25:04  ncq
- Windows install: setup.exe

Revision 1.2  2002/12/03 10:16:59  ncq
- lots of changes by Basti according to current state of affairs

Revision 1.1  2002/09/17 09:16:57  ncq
- added those files

