/****************************************************************************
** ui.h extension file, included from the uic-generated form implementation.
**
** If you wish to add, delete or rename functions or slots use
** Qt Designer which will update this file, preserving your code. Create an
** init() function in place of a constructor, and a destroy() function in
** place of a destructor.
*****************************************************************************/
#include <string>
#include <vector>
#include "discountdialog.h"
#include "ordermainadapter.h"
#include "orderdetail.h"
#include "mergeproductdialog.h"
#include "mergecustomerdialog.h"

#include "application1.h"
#include "productoffer.h"
#include "productdialog.h"
#include <qcombobox.h>
#include <qdatetime.h>
#include <qdatetimeedit.h>
#include<qprinter.h>
#include <qpainter.h>
#include <qpaintdevicemetrics.h>
#include <qstatusbar.h>

#include <vector>
#include <string>
#include <sstream>
using namespace std;
 
void OrderMain::fileNew()
{

}


void OrderMain::fileOpen()
{

}


void OrderMain::fileSave()
{

}

void OrderMain::fileSaveAs()
{

}

void OrderMain::filePrint()  
{

}


void OrderMain::fileExit()
{

}


void OrderMain::editUndo()
{

}


void OrderMain::editRedo()
{
   
} 
    


void OrderMain::editCut()
{

}


void OrderMain::editCopy()
{

}


void OrderMain::editPaste()
{

}


void OrderMain::editFind()
{

}   


void OrderMain::helpIndex()
{

}


void OrderMain::helpContents()
{

}


void OrderMain::helpAbout()
{

}

int RAW_TOTAL_COLUMN=5;

void OrderMain::findCustomer()
{
    QStringList alist;
     spinBox1->setValue(
     OrderMainAdapter::instance()->
        findCustomer(
          firstNameLineEdit1->text().stripWhiteSpace(),
          lastNameLineEdit2->text().stripWhiteSpace(),
          alist
        )
     );
      customerListBox1->clear();
     customerListBox1->insertStringList(alist); 
    
   
}




void OrderMain::saveCustomer()
{
    QStringList list;
    
    list << custIdLabel->text();
    list << firstNameLineEdit1->text() ;
    list << lastNameLineEdit2->text();
    list << addressLineEdit3->text();
    list << phoneLineEdit4->text();	   
    int id = OrderMainAdapter::instance()->setCustomerDetails(list);
    QString s;
    custIdLabel->setText(s.arg(id,10));
}



void OrderMain::handleFindCustomerSelection( QListBoxItem * item )
{
     QString selection = item->text();
     cout << selection << endl;
     QStringList alist;
      OrderMainAdapter::instance()->getCustomerDetails( spinBox1->value(),		item->text() ,  alist);
//      cout << "List = " ;
//      for ( int i = 0; i < alist.size() ; ++i) {
//        cout << alist[i] << endl;
//        }
     
      custIdLabel->setText( alist[0]);
      firstNameLineEdit1->setText( alist[1]);
      lastNameLineEdit2->setText( alist[2]);
      addressLineEdit3->setText( alist[3]);
      phoneLineEdit4->setText( alist[4]);
     
}


void OrderMain::newProduct()
{
      lineEditProductCode5->setText("");
     lineEditProductName6->setText("");
      lineEditProductDescription7->setText("");
      idProductLabel->setText("0");
}


void OrderMain::saveProduct()
{
    unsigned long id;
    id = atol(idProductLabel->text().stripWhiteSpace().ascii());
    id =  OrderMainAdapter::instance()->changeProduct(
	    id,
          lineEditProductCode5->text(),
           lineEditProductName6->text(),
          lineEditProductDescription7->text()
          );
    QString s;
    idProductLabel->setText(s.arg(id));
    clog << "called changeProduct" << endl;

    
}

void OrderMain::changeProduct( int row, int col )
{
   QString code, name, description;
   unsigned long id;
    id = atol( tableProducts1-> text(row, 3).ascii() );
	 code =tableProducts1-> text(row, 0); 
	 name =tableProducts1-> text(row, 1);
	 description =tableProducts1-> text(row, 2);
   OrderMainAdapter::instance()->changeProduct( id, code, name, description);
}


void OrderMain::editSelectedProductRow()
{
    QTableSelection selection = tableProducts1->selection(0);
    if ( selection.isActive()) {
	int row = selection.topRow();
	QString code, name, description;
	unsigned long id;
	 QString idStr =  tableProducts1-> text(row, 3);
	 if (idStr == "")
	     return;
	 id = atol(idStr.ascii() );
	 code =tableProducts1-> text(row, 0); 
	 name =tableProducts1-> text(row, 1);
	 description =tableProducts1-> text(row, 2);
  
	idProductLabel->setText(QString().arg(id));
	  lineEditProductCode5->setText(code);
	  lineEditProductName6->setText(name);
	  lineEditProductDescription7->setText(description);

     }
}






void OrderMain::updateOrderView()
{
    QPtrList<QStringList> data;
    data.setAutoDelete(true);
    QString custIdStr =   custIdLabel->text().stripWhiteSpace();
    unsigned long id = 0;

    if (custIdStr != "")
          id = atol(custIdStr.ascii() );

    if (id == 0)  {
	     while (orderTable2->numRows() > 0) {
	          orderTable2->removeRow(0);
	     }
	     return;
    }
    QString grandTotalStr;
    OrderMainAdapter::instance()->getOrderStrings( id, data, radioButtonUnpaidOrders1->isOn() , grandTotalStr);
    grandTotalLabel->setText(grandTotalStr);
    QValueList<int> width ;
    width << 70 << 50 << 70 << 20 << 45 << 50 ;
    QValueList<bool> readonly;
    readonly <<  true << true << true << true << true;
    
    while(orderTable2->numRows()) {
	orderTable2->removeRow(0);
    }
    OrderMainAdapter::instance()-> setTable( data, orderTable2, width, readonly);
    clearItemRows();
}
 


void OrderMain::showContextOrderMenu( int row , int col , const QPoint &p )
{
  QPopupMenu* menu = new QPopupMenu( orderTable2, "Order Update");
  menu->insertItem("New Order",  this , SLOT(newOrder()), CTRL+Key_N );
  menu->insertItem("Delete Order",  this , SLOT(deleteOrder()), CTRL+Key_D );
  menu->insertItem("edit Order",  this , SLOT(editOrder()), CTRL+Key_E );
  menu->insertItem("set Order Discount",  this , SLOT(setOrderDiscount()), CTRL+Key_S );
  menu->exec(p);
 delete menu;
}


void OrderMain::newOrder()
{
    
    OrderDialog* dialog = new OrderDialog( this, "Order Detail", true);
    dialog->custIdLabel->setText(custIdLabel->text());
    dialog->dateEdit1->setDate(QDate::currentDate());
    dialog->dateEdit2->setDate(QDate(1970,1,1));
    int result = dialog ->exec();
    if (result == QDialog::Rejected) {
	
	if (dialog->getOrderId()) {
	    OrderMainAdapter::instance()->removeOrderWithId(dialog->getOrderId());
	}
    }
    
    delete dialog;
    updateOrderView();
}


void OrderMain::findProduct()
{
    QPtrList<QStringList> list;
    list.setAutoDelete(true);
    QString name = lineEditProductName6->text();
     OrderMainAdapter::instance()->findProductByName(name,
    list);
    QValueList<int> width ;
    width << 80 << 150 << 200 << 20 << 80 <<80 <<80 << 80;
    QValueList<bool> readonly;
     readonly <<  true << true << true << true << true << true << true << true ;
     OrderMainAdapter::instance()-> setTable(list, tableProducts1 , width, readonly); 
   
}


void OrderMain::updateOrderItemsView()
{
   
    if (getOrderId() == 0)
	return;
    QPtrList<QStringList> data;
    QString totalStr;
    OrderMainAdapter::instance()->loadOrderItems( getOrderId(), data, totalStr);
    totalLabel->setText(totalStr);
    QValueList<int> width ;
    width <<150 <<60 <<30 << 60<< 40;
    QValueList<bool> readonly;
     readonly <<  false << true  << false << true << true;
     OrderMainAdapter::instance()-> setTable(data, tableOrderItems3 , width, readonly); 
     
}


void OrderMain::clearCustomerFields()
{    
      QStringList alist;
      alist << "" << "" << "" << "" << "";
      custIdLabel->setText( alist[0]);
      firstNameLineEdit1->setText( alist[1]);
      lastNameLineEdit2->setText( alist[2]);
      addressLineEdit3->setText( alist[3]);
      phoneLineEdit4->setText( alist[4]);
     

}


void OrderMain::deleteOrder()
{
    if (checkBoxConfirmOrderDeletion1->isChecked()) {
	if (QMessageBox::warning (orderTable2,"Delete Order", "delete selected Order (its order items will also be deleted) ?" , QMessageBox::Yes, QMessageBox::No ) != QMessageBox::Yes)
	    return;
    }
    if (getOrderId() == 0)
	return;
    OrderMainAdapter::instance()->removeOrderWithId(getOrderId());
    updateOrderView();
    orderTable2->clearSelection(true);
}


void OrderMain::clearItemRows()
{
    int rows = tableOrderItems3->numRows();
    if (rows == 0)
	return;
    QMemArray<int> r(rows);
    for (int i = 0; i < rows; ++i ) {
	r[i] = i;
    }
    tableOrderItems3->removeRows(r);
    totalLabel->setText("");
}


void OrderMain::editOrder()
{
     OrderDialog* dialog = new OrderDialog( this, "Order Detail", true);
    dialog->custIdLabel->setText(custIdLabel->text());
    
    
    if (getOrderId() == 0)
	return;
    dialog->setOrderId(getOrderId() );
    QDate start, end;
    OrderMainAdapter::instance()->getOrderDates(getOrderId() , start, end);
    dialog->dateEdit1->setDate( start);
    dialog->dateEdit2->setDate(end);
    int result = dialog ->exec();
    if (result == QDialog::Rejected) {
	ulong orderId = dialog->getOrderId();
	if (orderId) {
	    QStringList l = QStringList::split( ",", dialog->originalItemsIdLabel->text() );
	    QValueList<unsigned long> origIds;
	    for ( QStringList::const_iterator  i = l.begin() ; i != l.end() ; ++i ) {
		if ((*i).stripWhiteSpace() == "")
		    continue;
		origIds.append( atol( (*i).stripWhiteSpace()) );
	    }
	    OrderMainAdapter::instance()->removeOrderItemsExceptWithOfferId(
		orderId,
		origIds
		);
	}
    }
    
    delete dialog;
    updateOrderView();
}


void OrderMain::getSelectedOrderId( QString & orderIdStr )
{
    if (getOrderRow() >= 0)
	orderIdStr = orderTable2->text(getOrderRow(), 3).stripWhiteSpace();
}


void OrderMain::handleContextMenuProducts( int, int, const QPoint & p)
{
    
    QPopupMenu* menu = new QPopupMenu(  tableProducts1, "Product Manage");
  menu->insertItem("New Product Offer",  this , SLOT(newProductOffer()), CTRL+Key_P );
  menu->insertItem("merge products",  this , SLOT(mergeProducts()), CTRL+Key_M );
   // menu->insertItem("Delete Order",  this , SLOT(deleteOrder()), CTRL+Key_D );
  //  menu->insertItem("edit Order",  this , SLOT(editOrder()), CTRL+Key_E );
  menu->exec(p);
 delete menu;
}


void OrderMain::newProductOffer()
{
  QTableSelection sel =tableProducts1->selection(0);
    if (!sel.isActive())
	return;
    int row = sel.topRow();
    QString productIdStr = tableProducts1->text(row, 3).stripWhiteSpace();
    QString productName = tableProducts1->text(row, 1).stripWhiteSpace();
    ProductOfferDialog* dialog = new ProductOfferDialog(this, "Product Offer", true);
    dialog->productLabel->setText( productName);
    dialog->idProductLabel->setText(productIdStr);
//    dialog->dateTimeEdit1 ->setDate( QDate::currentDate());
//    dialog->dateTimeEdit2End->setDate( QDate(1970, 1, 1) );
    int result = dialog->exec();
    if (result == QDialog::Accepted) {
    
      
    }
   delete dialog;
    findProduct();
}


void OrderMain::checkReportTabSelected(const QString& title)
{
    cout << title.ascii() << " was selected " << endl;
    if (title=="reports") {
	stringstream ss;
  ss << endl << endl ;
  ss << "UNPAID ORDERS REPORT RUN ON ";
  QString timeStr =  QDateTime::currentDateTime().toString("dd/MM/yyyy hh:mm:ss") ;

  ss <<  timeStr.ascii();
  ss << endl << endl;
  
	app1 app(ss);
	app.show_all_unpaid_orders();
	textEdit1->setText(QString(ss.str().c_str()));
    }
}


void OrderMain::printReport()
{
    QPrinter * printer = new QPrinter();
    const int Margin = 10;
    int pageNo = 1;
    QTextEdit* e = textEdit1;
    
    if ( printer->setup(this) ) {               // printer dialog
        statusBar()->message( "Printing..." );
        QPainter p;
        if( !p.begin( printer ) )              // paint on printer
            return;

        p.setFont( e->font() );
        int yPos        = 0;                    // y-position for each line
        QFontMetrics fm = p.fontMetrics();
        QPaintDeviceMetrics metrics( printer ); // need width/height
                                                // of printer surface
        for( int i = 0 ; i < e->lines() ; i++ ) {
            if ( Margin + yPos > metrics.height() - Margin ) {
                QString msg( "Printing (page " );
                msg += QString::number( ++pageNo );
                msg += ")...";
                statusBar()->message( msg );
                printer->newPage();             // no more room on this page
                yPos = 0;                       // back to top of page
            }
            p.drawText( Margin, Margin + yPos,
                        metrics.width(), fm.lineSpacing(),
                        ExpandTabs | DontClip,
                        e->text( i ) );
            yPos = yPos + fm.lineSpacing();
        }
        p.end();                                // send job to printer
        statusBar()->message( "Printing completed", 2000 );
    } else {
        statusBar()->message( "Printing aborted", 2000 );
    }
    delete printer;
}


void OrderMain::setOrderDiscount()
{
  
    ulong orderId = getOrderId();
    if (orderId == 0) 
	return;
    OrderMainAdapter::instance()->inputDiscount(orderId,-1, 
					       orderTable2->text(getOrderRow(), RAW_TOTAL_COLUMN),  
					       orderTable2->text( getOrderRow(), 0));
    updateOrderView();
}


ulong OrderMain::getOrderId()
{
    QString idStr;
    getSelectedOrderId( idStr);
    if (idStr != "")
	return atol(idStr.ascii());
    return 0;
}


int OrderMain::getOrderRow()
{
    QTableSelection sel = orderTable2->selection(0);
    if (!sel.isActive())
	return -1;
    return sel.topRow();
}


void OrderMain::editProductOffers()
{
    ProductDialog* dialog = new ProductDialog(this);
    dialog->updateProducts();
    dialog->exec();
    delete dialog;
}


void OrderMain::mergeProducts()
{
    QString name("");
    ulong id = 0;
    OrderMainAdapter::instance()->currentProductDetails(tableProducts1,  id, name);
    if (!id)
	return;
    MergeProductDialog * dialog = new MergeProductDialog();
   dialog->setFirstProductDetails(id, name);
   dialog->exec();
   delete dialog;
    
}


void OrderMain::currentProductDetails( ulong& id, QString& name )
{
  QTableSelection sel =tableProducts1->selection(0);
    if (!sel.isActive())
	return;
    int row = sel.topRow();
    QString idStr = tableProducts1->text(row, 3).stripWhiteSpace();
    
    if (idStr == "")
	id = 0;
    else 
	id = atol(idStr.ascii());
    
    name = tableProducts1->text(row, 1).stripWhiteSpace();
    
}


void OrderMain::mergeCustomer()
{
    
    ulong id = 0;
    if ( custIdLabel->text() != "")
      id = atol(custIdLabel->text().ascii());
    QString name = lastNameLineEdit2->text() + " " + firstNameLineEdit1->text();
    
    if (!id)
	    return;
    MergeCustomerDialog * dialog = new MergeCustomerDialog();
   dialog->setFirstCustomerDetails(id, name);
   dialog->exec();
   delete dialog;
}
