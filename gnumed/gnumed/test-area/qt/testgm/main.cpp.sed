#include <qapplication.h>
#include "form1.h"
#include <qsqldatabase.h>
bool createConnections()
{
    // create the default database connection
    QSqlDatabase *defaultDB = QSqlDatabase::addDatabase( "QPSQL7" );
    if ( ! defaultDB ) {
        qWarning( "Failed to connect to driver" );
        return FALSE;
    }
    defaultDB->setDatabaseName( "testgm" );
    defaultDB->setUserName( "stan" );
    defaultDB->setPassword( "pg" );
    defaultDB->setHostName( "localhost" );
    if ( ! defaultDB->open() ) {
        qWarning( "Failed to open books database: " +
                  defaultDB->lastError().driverText() );
        qWarning( defaultDB->lastError().databaseText() );
        return FALSE;
    }

    return TRUE;
}


int main( int argc, char ** argv )
{
    QApplication a( argc, argv );
    if (!createConnections()) {
	    return 1;
    }
    Form1 w;
    w.show();
    a.connect( &a, SIGNAL( lastWindowClosed() ), &a, SLOT( quit() ) );
    return a.exec();
}

