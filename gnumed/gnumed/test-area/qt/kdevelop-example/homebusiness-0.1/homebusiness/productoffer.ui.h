/****************************************************************************
** ui.h extension file, included from the uic-generated form implementation.
**
** If you wish to add, delete or rename functions or slots use
** Qt Designer which will update this file, preserving your code. Create an
** init() function in place of a constructor, and a destroy() function in
** place of a destructor.
*****************************************************************************/
#include <qdatetime.h>
#include "ordermainadapter.h"

void ProductOfferDialog::storeOffer()
{
  
       QString price =  lineEdit1Price->text() ;
      OrderMainAdapter::instance()->createProductOffer(
	   idProductLabel->text(),
	  dateTimeEdit1->dateTime(), 
	  dateTimeEdit2->dateTime() , 
	  price
	  );
}


void ProductOfferDialog::init()
{
    dateTimeEdit1->setDateTime( QDateTime::currentDateTime() );
    dateTimeEdit2->setDateTime(QDateTime(QDate(1970,1,1) , QTime(0,1) ));
}
