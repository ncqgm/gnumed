/****************************************************************************
** ui.h extension file, included from the uic-generated form implementation.
**
** If you wish to add, delete or rename functions or slots use
** Qt Designer which will update this file, preserving your code. Create an
** init() function in place of a constructor, and a destroy() function in
** place of a destructor.
*****************************************************************************/
#include "ordermainadapter.h"
#include <qptrlist.h>
#include <qstringlist.h>
#include <qvaluelist.h>

void ProductDialog::updateOffer( int r, int c )
{ 
    
}


void ProductDialog::updateProducts()
{
     QPtrList<QStringList> list;
     QString name = productEdit->text();
     OrderMainAdapter *  ad =  OrderMainAdapter::instance();
     ad->findProductByName(name, list);
     QValueList<bool> readOnly;
     readOnly << true << true << true << true;
     QValueList < int > widths;
     widths << 20 << 40 << 50 << 10;
     ad->setTable(list,  productTable,  widths, readOnly); 
}
