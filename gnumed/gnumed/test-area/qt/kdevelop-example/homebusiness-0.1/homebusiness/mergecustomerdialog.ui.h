/****************************************************************************
** ui.h extension file, included from the uic-generated form implementation.
**
** If you wish to add, delete or rename functions or slots use
** Qt Designer which will update this file, preserving your code. Create an
** init() function in place of a constructor, and a destroy() function in
** place of a destructor.
*****************************************************************************/
#include "ordermainadapter.h"
#include <qstringlist.h>
#include <qlistbox.h>
#include <qmessagebox.h>

static int sessionId = 0;

void MergeCustomerDialog::setFirstCustomerDetails( ulong id, const QString & name )
{
    idEdit1->setText(QString("").arg(id).stripWhiteSpace());
    nameEdit1->setText(name);

}


void MergeCustomerDialog::setSecondCustomerDetails( ulong id, const QString & name )
{
  idEdit2->setText(QString("").arg(id));
    nameEdit2->setText(name);
}


void MergeCustomerDialog::findSecondCustomer()
{
     QStringList list;
     sessionId = OrderMainAdapter::instance()->findCustomer (
        findFirstNameEdit->text().stripWhiteSpace() ,
        findLastNameEdit->text().stripWhiteSpace(), list);

     customerListBox->clear();
     customerListBox->insertStringList(list);
}




void MergeCustomerDialog::handleCustomerSelection( QListBoxItem * item )
{
    QStringList list;
    OrderMainAdapter::instance()->getCustomerDetails( sessionId, item->text(), list);
    if (list[0] == idEdit1->text() ) {
        QMessageBox::information(this, "Same Customer", "Cannot merge the same customer");
        
        return;
    }
    idEdit2->setText( list[0]);
    nameEdit2->setText(list[1] +" "+ list[2]);   
}


void MergeCustomerDialog::confirmMerge()
{
    ulong id1, id2;
    if (idEdit2->text() == "") 
	return;
    id2 = atol(idEdit2->text().ascii());
    id1 = atol(idEdit1->text().ascii());
    QStringList l;
    l << "Merge customers id=" << idEdit1->text() ;
    l << " : " << nameEdit1->text() << " with customer id=";
    l << idEdit2->text() << ": " << nameEdit2->text() ;
    l << ". Are you sure?";
    if(QMessageBox::warning(this, "ABOUT TO MERGE:", l.join(""),
			    QMessageBox::Yes, QMessageBox::No ) 
	== QMessageBox::Yes ) {
	
	if ( radioButton2->isChecked()) {
	    ulong tmp = id1;
	    id1 = id2;
	    id2 = tmp;
	}
	OrderMainAdapter::instance()->mergeCustomers(id1, id2);
	accept();
    }
}
