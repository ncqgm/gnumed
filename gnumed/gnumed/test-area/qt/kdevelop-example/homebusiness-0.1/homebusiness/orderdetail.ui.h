/****************************************************************************
** ui.h extension file, included from the uic-generated form implementation.
**
** If you wish to add, delete or rename functions or slots use
** Qt Designer which will update this file, preserving your code. Create an
** init() function in place of a constructor, and a destroy() function in
** place of a destructor.
*****************************************************************************/
#include "ordermainadapter.h"
#include "discountdialog.h"
#include "Customer.h"
#include <qpopupmenu.h>
const int OFFER_ID_COLUMN = 6;
const int  RAW_TOTAL_COLUMN = 5;
const int DESCRIPTION_COLUMN = 0;
const int  SUB_TOTAL_COLUMN=3;
const int DISCOUNT_COLUMN=4;

void OrderDialog::loadOrderOffers()
{
    QPtrList<QStringList> list;
    QDateTime dateTime (dateEdit1->date(), QTime(0,0,0));
    QString nameFilter = lineEdit2->text().stripWhiteSpace();
    bool allLatest = latestOffersCheckbox->isChecked();
    OrderMainAdapter::instance()->getOffers(list, dateTime, nameFilter, allLatest);
    QValueList<int> width ;
    width << 150 << 50 << 50 << 50 ;
    QValueList<bool> readonly;
     readonly <<  true << true << true << true;
     OrderMainAdapter::instance()-> setTable( list, productTable2, width, readonly);
    
}


void OrderDialog::addOfferAndQtyAsOrderItem()
{  
    QTableSelection sel = productTable2->selection(0);
    
    int row =sel.topRow();
    if (row < 0)
	    return;
    
     int qty = spinBox2->value();
     if (qty <= 0)
	 return;
     
    unsigned long offer_id = atol( productTable2->text( row, 3).ascii());
    unsigned long order_id =getOrderId();
   
    QPtrList <QStringList> data;
    QString total = "";
    OrderMainAdapter::instance()->updateOrderItems( atol(custIdLabel->text()), order_id, offer_id, qty, data , total);
    totalLabel->setText(total);
    setOrderId(order_id);
    for (int i = 0 ; i < data.count() ; ++i) {
      	QStringList * psl = data.at(i);
      	int lastRow = tableItems3->numRows() ;
      	tableItems3->insertRows(lastRow);
	
      	for (int j = 0 ; j < psl->count() ; ++ j) {
      	    tableItems3->setText( lastRow, j, (*psl)[j] );
      	}
	
    }
}



void OrderDialog::loadExistingOrderItems()
{
    unsigned long order_id =getOrderId();
    QPtrList<QStringList>data;
    QString totalStr;
    OrderMainAdapter::instance()-> loadOrderItems(order_id, data  , totalStr) ;
    if (data.count() > 0) {
	 totalLabel->setText(totalStr);
	 QValueList<int> width ;
	 width <<200 <<80 <<40 << 80<< 80;
	 QValueList<bool> readonly;
	 readonly <<  false << true  << false << true << true;
	 OrderMainAdapter::instance()-> setTable(data, tableItems3 , width, readonly); 		 if (originalItemsIdLabel->text() == "") {
	     QStringList list;
	     for (int i = 0; i < data.count() ; ++i) {
		 list.append( (*data.at(i))[OFFER_ID_COLUMN]);
	     }
	     originalItemsIdLabel->setText( list.join(","));
	 }
     
    }
   
}


void OrderDialog::popupOrderItemsMenu( int row, int col, const QPoint & p )
{
      QPopupMenu* menu = new QPopupMenu( this, "Order Items");
      
       menu->insertItem( "Delete order item",  this, SLOT(deleteOrderItem()), CTRL+Key_D );
       menu->insertItem( "set item discount", this, SLOT(setItemDiscount()) , CTRL+Key_S);
      menu->exec(p);
      delete menu; 
}


void OrderDialog::deleteOrderItem()
{
    int r = getSelectedOrderItemRow();
    if ( r < 0)
	return;
    QString idOfferStr = tableItems3->text( r, OFFER_ID_COLUMN).stripWhiteSpace();
    
    if (OrderMainAdapter::instance()->removeOrderItem(getOrderId(),(int) r)) {
	
    }
    tableItems3->removeRow(r);
}


void OrderDialog::init()
{
    loadOrderOffers();
    
}


void OrderDialog::removeNewItems()
{
                 if (getOrderId() != 0) {
	    QStringList l = QStringList::split( ",",  originalItemsIdLabel->text() );
	    QValueList<unsigned long> origIds;
	    for ( QStringList::const_iterator  i = l.begin() ; i != l.end() ; ++i ) {
		if ((*i).stripWhiteSpace() == "")
		    continue;
		origIds.append( atol( (*i).stripWhiteSpace()) );
	    }
	    
	    OrderMainAdapter::instance()->removeOrderItemsExceptWithOfferId(
		getOrderId(),
		origIds
		);
	    OrderMainAdapter::instance()->restoreOrder(getOrderId());
	}
	
}


void OrderDialog::storeDates()
{
    QDate first = dateEdit1->date();
    QDate paid = dateEdit2->date();
     
     if (getOrderId() == 0)
	      return;
     OrderMainAdapter::instance()->storeOrderDates( getOrderId(), first, paid);
}


ulong OrderDialog::getOrderId()
{
    return orderIdEdit->text().stripWhiteSpace() =="" ? 0: atol( orderIdEdit->text().ascii() );
}


void OrderDialog::setOrderId( ulong order_id )
{
    orderIdEdit->setText(QString().arg(order_id));
}




void OrderDialog::loadAndRememberOrders()
{
       loadExistingOrderItems();
       OrderMainAdapter::instance()->rememberOrder(getOrderId());

}


void OrderDialog::setItemDiscount()
{
    
    if (getSelectedOrderItemRow() < 0)
	return;
    OrderMainAdapter::instance()->inputDiscount( getOrderId(), getSelectedOrderItemRow(),
tableItems3->text(getSelectedOrderItemRow(),  RAW_TOTAL_COLUMN),
tableItems3->text(getSelectedOrderItemRow(), DESCRIPTION_COLUMN)
);
   loadExistingOrderItems(); 
    /*
    DiscountDialog* dialog = new DiscountDialog();
    
    dialog->setRawTotal( tableItems3->text(getSelectedOrderItemRow(),
					   RAW_TOTAL_COLUMN));
    dialog->setDescription(tableItems3->text(getSelectedOrderItemRow(),
					     DESCRIPTION_COLUMN));
    int result = dialog->exec();
    if ( result == Accepted) {
	int percent;
	QString amt;
	bool isAmount;
  
	dialog->getDiscountDetails(isAmount, amt, percent);
  Discount* discount =
  OrderMainAdapter::instance()->createDiscount(isAmount, amt, percent);

  OrderMainAdapter::instance()->setDiscount(getOrderId(),
   getSelectedOrderItemRow(),  discount
    );
    }
    delete dialog ;
    
    */
}


int OrderDialog::getSelectedOrderItemRow()
{
   QTableSelection sel = tableItems3->selection(0);
    if (!sel.isActive())
	        return -1;
    unsigned int r = sel.topRow();
    if (tableItems3->numRows() <= r)
	        return -1;
    return r;
    
}
