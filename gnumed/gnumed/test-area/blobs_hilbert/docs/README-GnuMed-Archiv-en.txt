# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/blobs_hilbert/docs/Attic/README-GnuMed-Archiv-en.txt,v $
# $Revision: 1.1 $
#------------------------------------------------------------------------

What you are about to read is an early version of the GNUmedArchive installation guide
contents :
--------

1.  prerequisites
2.  install it
3.  start it
4.  work it
5.  connecting to commercial software


##############################
1.   installation prerequisites
##############################
You are about to install GNUmedArchive.GNUmedArchive has been implemented in Python.
Therefore you will need Python on your system.Besides Python some more packages are needed.
This document describes the process when using Suse Linux. Your milage may vary. The installation
consists of two parts. Part one involves setting up the server. Second part is to install the
client.

You will need:

on the client
--------------

	Python
	------

	Linux )	When using GNU/Linux you can decide if you wanna compile python from
		source or use precompiled packages that ship with your favorite
		distribution.

		Suse 8.0 )The following packages need to be installed. You may use yast2 to do that.
			python ; python-devel ; python-doc ;

		other ) You may compile from source as well. The can be downloaded here :
			http://www.python.org/ftp/python/2.2.1/Python-2.2.1.tgz

	Windows ) On Windows OS there is a comfortablen installer you can pick up.

		http://www.python.org/ftp/python/2.2.1/Python-2.2.1.exe

	Mac ) 	http://www.python.org/2.2.1/mac.html oder http://www.cwi.nl/~jack/macpython.html


	WxWindows - www.wxwindows.org
	---------
	Linux )	Suse 8.0 ) the following packages may be picked up at www.sourceforge.net
			http://prdownloads.sourceforge.net/wxwindows/wxGTK-2.3.2-1.i386.rpm
			http://prdownloads.sourceforge.net/wxwindows/wxGTK-devel-2.3.2-1.i386.rpm
			http://prdownloads.sourceforge.net/wxwindows/wxGTK-gl-2.3.2-1.i386.rpm

		other ) You may compile from source as well.Pick em up at:
			http://prdownloads.sourceforge.net/wxwindows/wxGTK-2.3.2.tar.gz

	Windows )On Windows OS there is a comfortable installer you might wanna pick up
			http://prdownloads.sourceforge.net/wxwindows/wxMSW-2.2.9.zip

	Wxpython - www.wxpython.org
	--------

	Linux )	Wxpython needs "glib" and "gtk+". In most cases these packages will reside on your system
		already. When using Suse you can use yast2 ans search for "glib" and "gtk".

		Suse 8.0 ) The following packages are installed on my system:
			gtk ; gtk-devel ; gtkmm ; gtkmm-devel ; python-gtk ;
			wxGTK ; wxGTK-devel ; wxGTK-gl

			I downloaded the following packages from Sourceforge:

			http://prdownloads.sourceforge.net/wxpython/wxPython-2.3.2.1-1-Py22.i386.rpm?download
			http://prdownloads.sourceforge.net/wxpython/wxPython-gl-2.3.2.1-1-Py22.i386.rpm?download
			http://prdownloads.sourceforge.net/wxpython/wxPython-tools-2.3.2.tar.gz?download

		other ) You may compile from source as well. Pick em up at:
			http://prdownloads.sourceforge.net/wxpython/wxPython-docs-2.3.2.tar.gz?download
			http://prdownloads.sourceforge.net/wxpython/wxPython-2.3.2.1.tar.gz

	Windows )On Windows there is a comfortable installer.
		http://prdownloads.sourceforge.net/wxpython/wxPython-2.3.2.1-Py22.exe

	Scanning device connection
	-----------------
	Linux   - http://www.mostang.com/sane/        - scanning with Linux

	Windows - http://twainmodule.sourceforge.net/ - for scanning images from within Python(Windows)


	PythonImagingLibrary
	--------------------
	http://www.pythonware.com - PIL 1.1.3

	mx-tools
	-------------------
	http://www.egenix.com/files/python/ - must fit your Python-version



Server
------
	Python
	------

	Linux )	When using GNU/Linux you can decide if you wanna compile python from
		source or use precompiled packages that ship with your favorite
		distribution.

		Suse 8.0 )The following packages need to be installed. You can use yast2 to do that.
			python ; python-devel ; python-doc ;

		other ) You may compile from source as well.Pick em up at:
			http://www.python.org/ftp/python/2.2.1/Python-2.2.1.tgz

	Windows ) On Windows there is a comfortable installer.

		http://www.python.org/ftp/python/2.2.1/Python-2.2.1.exe

	Mac ) 	http://www.python.org/2.2.1/mac.html or http://www.cwi.nl/~jack/macpython.html


	PosgreSQL-database
	---------
	Linux ) Suse 8.0 ) Off your distributions CD or the Internet (http://www.postgresql.org) get and install
			the package 'postgresql'. I have installed the following packages :
			postgresl-devel ; postgresql-libs ; postgresql-server


	PostgreSQL-database adapter for python
	---------

	Linux )   http://prdownloads.sourceforge.net/pypgsql/pypgsql-2.2.tar.gz?download
			The packages contains a file named "readme" which contains installation instructions.
			You might have to adapt the file setup.py to your system before compiling.

	Windows ) There is an installer for this package available as well.
			http://prdownloads.sourceforge.net/pypgsql/pyPgSQL-2.1.win32-py2.2.exe?download

	mx-tools
	-------------------
	http://www.egenix.com/files/python/ - must fit your Python-version

#############################
2.   install it
#############################
client
------
	GNU/Linux )
	Uncompress the archive 'gnumed-archive-client.tgz' to a directory of your choice.
	You may then run the install script 'install.sh' aus.

	Windows )
	Just run 'setup.exe'.

	If you decide to install GNUmedArchive in any directory but the default one you will have to adapt
	the files 'run-scanner.bat' , 'run-indexer.bat' and 'run-viewer.bat'.
	These files can be found in the chosen installation directory.

	You need to set your preferred language when using the GUI in any but the default (English) language.
	Set the language inside the files 'run-scanner.bat', 'run-indexer.bat' and 'run-indexer.bat'.
	For a German GUI remove the 'REM' in front of the entry 'set LANG=de_DE@EURO'.

	Just in case 'python.exe' in not installed in the default location 'c:\python22' on your system, you
	must change the path to Python inside the batch-files.

	Do not forget to adapt the configuration file 'gnumed-archive.conf' to reflect your system setup.
	This file may reside in different places inside your system.

	GNU/Linux )
	In most cases you will want to create a directory '.gnumed' in your home-dir and move the file
	'gnumed-archive.conf' to this directory.

	Windows )
	When using MS Windows (TM) it is a good idea to place this file in the same directory as the program-files.
	You need not woory about this when installing GNUmedArchive via 'setup.exe'.

	A sample config-file (gnumed-archive.conf) is provived with 'gnumed-archive-client.tgz' or
	'setup.exe'
server
-------

	GNUmedArchive works with PostgreSQL database as backend. This database may run under any OS that
	is capable of running PostgreSQL such as GNU/Linux. It also seems to be possible to run PostgreSQL with
	MS Windows although this is not supported or even intended by the creators of GNUmedArchive.
	More info on this issue can be found on the net when searching for 'running PostgreSQL under Windows'
	or inside the GNUmed manual. PostgreSQL recently appeared on Novell and might even be used with this
	OS.

	Just uncompress the archive 'gnumed-archive-server.tgz' to a directory of your choice.
	You need to become root to successfuly manage the installation.

	You might want to edit the file 'german-doc_types.sql' in case you want German document types inside your
	database. This file contains entries for the document types which later on will be used for classifying
	documents.

	e.g.:

	INSERT INTO doc_type(id, name) values(101,'document type1');
	INSERT INTO doc_type(id, name) values(102,'document type2');
	INSERT INTO doc_type(id, name) values(103,'document typex');
	and so on.

	The numerical value in front of tge document type must be unique. This mean no value must be there twice.
	Because of that you must also make sure that none of the values has been used before in any other file
	such as 'gmBlobs.sql'. Just take a look at the highest value in 'gmBlobs.sql' and add (+) '1'. The newly
	calcuclated value is the first one to use in 'german-doc_types.sql'. Just increase by '1' for each following
	entry.

	Now it is time to think about who is going to use the document archive and with what privileges.
	You may create user who will have read and write permissions and others who will just have read
	permissions. In case you just want to create test-users everything has been taken care of for you.
	The file 'bootstrap-gm_db_system.conf' will take care of that. If you prefer to set up your own set of users
	you might want to create a seperate config file. Just create some file like 'users.conf' and put your
	configuration in there. This file needs to have a special format so take a look at the default file
	'bootstrap-gm_db_system.conf'.

	Assuming you are done so far you may now run the installation shell script 'install.sh' and follow the
	instructions on your screen

	If the installation succeeds you will get further instruction on what you can do to make your freshly
	installed software run smoothly. This includes instructions on how to automize the process of actually
	filling the database with the data you produced.

	If for some reason the installation fails you may want to take a look at the log-file which kept track
	of your installation effort. If you fail to understand what the file tells you, you may ask for help
	on the mailing list. Do not forget to attach the log-file.

	You should now adapt the section [import] in the config file 'gnumed-archive.conf' to suit your needs.
#################
3.start it
#################
client
------
	GNU/Linux )

		'run-scanner.sh'
		'run-indexer.sh'
		'run-viewer.sh'

	MS Windows(TM)
		Im Startmenü wurden entsprechende Verknüpfungen angelegt

server
------
	GNU/Linux )
		'run-importer.sh'

	You can automize this job by creating a cron-job.

###############################
4.  work it
###############################
    The document archive consists of four parts.
    1) document scanning module
    2) document indexing module
    3) database import module
    4) document viewer

    and here is how it works ...

part 1: aquire documents
------------------------
A pile of documents is aquired via a scanning device. Documents
which consist of multiple pages keep their inherent structure.

step 1: aquire one ore more pages. You can use any scanning device
which is supported by either TWAIN under Microsoft Windows or SANE
under GNU/Linux.

step 2: you could now chnage the order of the aquired pages.
This is optional and only necessary if you aquired the pages in a
different order than you would like them.

step 3: When all pages of a document have been aquired it
is a good idea to save it. This creates a unique identifier for
the document and shows it on your screen. You need to put this
identifier on the physical document for indexing later on.This
idientifier is the only connection between your physical and digital
document
.
In case you do not care about identifiers because you throw
away paper documents you can turn off the display of the identifier
in the config file.

Having done that you can now digitalize the next paper document.

GNUmedArchive's graphical user interface has been optimized for
this workflow and therefore only contains essential controls.
The use of a pointing device has been reduced to a minimum. Future
versions will feature printing the identifier as barcode.
OpenSource Software GNUBarcode will take care of that.

part 2: indexing
-------------------------
This module is used to connect the digital documents to
the patient. Most commercial practice software products
do not allow external software to access their electronic patient
record. In Germany there is a somewhat limited standardized
interface to accomplish that. This interface is called GDT/BDT-
interface. GnumedArchive is capable of communicating with the German
commercial software package 'Turbomed' by using the BDT/GDT-interface
When calling GNUmedArchive from within Turbomed it creates a BDT-file
which contains information about the currently active patient.
GNUmedArchive reads this file and automatically fills in all the
demographic infos. Once GNUmed is ready this won't be necessary.
GNUmedArchive will directly communicate with GNUmed's patient object
and electronic record because of GNUmed is Open Source.

The indexing module follows a logical workflow as well.

step 1: document loading via document identifier on the physical
document. This identifier needs to be typed into the designated
control in the left upper corner. Future versions will have the
option of reading in the barcode by the means of a barcode reader.
Typing the documnet identifier is very quick and comfortable even
without a barcode reader. This is accomplished by the use of a smart
control called 'phrase wheel'. When typing the first character this
control automatically display all document idenfiers of documents
thathave not yet been connected to a patient. Each following 
characterreduces the number of items displayed. Any time you like
you can pick the desired docoment from the displayed list. In most
casesyou will only have to type two or three character to be able
to select your desired identifier/document.

step 2: After loading the document pages into the module you will
have to supply some more info on the document. This includes the 
document creation date, a short comment, the document type and an
optional longer comment. The supply of the document type is of
great importance. This type can be picked from a previously defined
list. Any number of types can be added through the config file.
This relatively unpleasant, time consuming specification will
benefit you later on when viewing large sets of documents for
one patient.

step 3: When all required information as been supplied the document
is saved once again and now connected to the patient. A script
running on the server will then shovel these documents into the
database. This is a background process and therefore does not
require your presence. This has been the last step that requires
human input. When indexing large numbers of documents
one should consider scheduling the database import process at night
when one is using the network and/or server. This way network
load during office hours can be avoided and does not slow down
your core work. There will be an option to digitally sign the
newly indexed documenty by the use a digital notary service. You
might be interested in a project called 'GNotary' when
implementing this.

Because GNUmedArchive is devided into 4 modules you can
perform the digitalizing work asychronously and even on
seperate computers. Only the second step requires some medical
knowledge.

part 3: daily use

The document viewer (either called directly from GNUmed or
any other commercial software ) shows all patient's documents
in a tree structureabove. The actual display of an individual
document page is handled by the OS itself. The viewer only sends
the diplay command to the OS which in turn pick the applicable
viewer and renders the image. This way GNUmedArchive is in no
way limited to whatsoever document types.It only depends on the
OS and its installed viewers if one actually gets tosee the
content. Because of that the Archive can handle graphics file,
video files, audio files, text and even extraterrestrial content
as long it can be stored in bits and bytes. The metadata supplied
during the indexing process benefit you now. Documents can be grouped
by type, creation date or date ranges or event searched for
by the use of the supplied comments. It is easiely possible to find
all ultrasound documents within a given range. This functionality
is still under development. It certainly will be possible to
export documents for the use in letters of referral and so on.

################################################
5. connecting to third-party/commercial software
################################################

GNU/Linux
	GNUmed - GNUmedArchive is part of GNUmed and will be integrated as a plugin.
DOS
	Users of German Turbomed should read the German version of this document.
Windows
	Who cares :) actually I know none.

#------------------------------------------------------------------------
# $Log: README-GnuMed-Archiv-en.txt,v $
# Revision 1.1  2003-01-19 13:44:09  ncq
# - new Englisch installation manual
# - fixes for German
#
