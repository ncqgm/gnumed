Time for retro - 90s hacking , delphi style!



1. The Makefile

- See PATCH.txt  , or just run sh patch_makefile.sh before running make,
then ./testgm  to see this prototype.


- it's basically created by /usr/lib/qt3/bin/qmake (on Mandrake)
from form1.ui and main.cpp. Form1.ui was created using qtDesigner, 
and main.cpp was generated using qtDesigner. 

There is no easy qtDesigner way to make the db connection changeable ,
so the easiest thing to  do is to edit main.cpp to accept command line
parameters of username, password.
(not done yet).


Prerequisites -  qtDesigner 3
	      -  qtpsql driver for postgresql access in qt. (included in Mandrake 9.2 cds )
	      - postgresql server running with tcp sockets enabled.

Installing - 

1.The default user and password needs to be changed in main.cpp to a valid
username and password for your local postgresql.
2. run 'make'
 The makefile is modified to 
	a)put a patch in form1.h so it compiles ,
 and also 
	b)to create a postgres db called "testgm"  using the
	current user ( assuming postgresql create database rights) and running 
	the simple.sql script to populate. 

3. run ./testgm

hopefully it works.


the applet - it uses the QDataTable and  QDataBrowser as data aware widgets.
As much as possible, tried to use the available API.


Applet structure
-------------------
QT has a Signals/Slots system, where Widget A's Signal can connect to Widget B's slot ; both are just function names. You can create new slots with Qt Designer.

What happens, is that most of the programmed custom slots end up on Form1 or whatever the
main widget window is , so it becomes like a Single Controller/UI . 
The Model part of MVC is 
 just what's available in QT , i.e. QSqlRecord, QSqlQuery; QSqlCursor inheriting from the previous 2 classes, and QVariant as a universal type adapter. 
Like Delphi, the Signals/Slots lets a programmer provide behaviour, and also
to intercept the flow of select, insert and update to validate data, set up foreign key links , create generated field values.

In this applet, the FindPatientDataTable  has its filter set by the
requested patient surname and firstname.  A Selection event on the findPatient
links to to the patient DataBrowser, which acts to edit demographic data.
Changes in the DataBrowser (such as selecting in the findPatientDataTable,
navigating the dataBrowser)  triggers custom functions that set the filter
on the the clinical dataTables ( id_patient is the main value passed).
Pre-inserts on the clinical dataTables are intercepted, to
add the nextval of the relevant sql sequence as the primary key for inserts.

The more elaborate custom slots are those that handle the progress notes and
customize mouse clicks on the prescription table for print selection.

The progress notes are triggered by the patient data browser current record change signal. It uses a SqlQuery object to create the text for the past progress notes, and also selects for any notes with the same user and day , and places
them in the current progress notes editing area, so that same day notes can
be re-edited. Only insert is called, so the previous version of today's progress notes are still recorded in the old version.




Notes on C++:
--------------
 - C++ has static type checking to aid in finding bugs.
 - it has template strict-typed collections, which is a lot better than
java's need to cast everything to the required type when pulled out of a collection. 
 - it has no garbage collection, and relies on either on scope or proper
pointer deallocation.  Scope is probably the safest. 
    e.g.  suppose a function is needed to return an object , e.g. a list of
of the names. Create  an empty list object in the callers scope, 
and pass it in as an alias parameter e.g. 'List& createFooList( List& l)' is the 
servicing method. The servicing function can even assign to l with another list without calling "new List()" , if a good copy constructor/=operator exists for the List. 

 - it hasn't got interfaces, but does have pure virtual classes. QT shows it
e.g. overuse of inheritance ?  SqlCursor inherits from SqlRecord and SqlQuery.
On the other hand ,unlike python, classes not inheriting the same methods from a parent can't have interchangeable objects e.g. QDataBrowser.setSqlCursor() and
QDataTable.setSqlCursor() aren't callable through a commonly typed pointer
(QDataBrowser* isn't interchangeable with QDataTable *).

 
Notes on QT:
	- the data aware ui components save a bit of work.
	- not a bad ui Framework, but is a bit inflexible in some areas.
 	- don't know how to get a handle of the QPopupMenu of QDataBrowser
and QDataTable.
	
	- the Sql documentation has quite a few classes, and not enough
explanation is given about how they work together. 

	- signal/slot connections are easy to set up with QTDesigner, but they
are also easy to destroy. e.g. it's sometimes more convenient to trash
a DataTable then to modify its displayed columns, but the cost is that
the connections have to be re-entered.

 



Old Notes.
--------------------
1. Compiling

a patch was included in the Makefile.

The Makefile will be regenerated if a qmake is done.

if the following error occurs:

In file included from main.cpp:2:
form1.h:143: error: `QSqlQuery' was not declared in this scope
form1.h:143: error: `query' was not declared in this scope

run 

	make clean
	sh patch_form1.sh


This will add a necessary include in one of the functions of Form1.


