/****************************************************************************
** ui.h extension file, included from the uic-generated form implementation.
**
** If you wish to add, delete or rename functions or slots use
** Qt Designer which will update this file, preserving your code. Create an
** init() function in place of a constructor, and a destroy() function in
** place of a destructor.
*****************************************************************************/
#include "ordermainadapter.h"
#include "qmessagebox.h"
#include "qptrlist.h"
#include "qvaluelist.h"
#include "qstringlist.h"

void MergeProductDialog::setFirstProductDetails( ulong id, const QString & name )
{
    idEdit->setText(QString("").arg(id));
    nameEdit->setText(name);
}


void MergeProductDialog::loadProducts()
{
    QPtrList<QStringList> list ;
    OrderMainAdapter::instance()->findProductByName( lineEdit3->text() , list);
    QValueList<bool> readOnly;
    QValueList<int> width;
    width << 60 << 80 << 100 << 50;
    readOnly << true << true << true << true;
    OrderMainAdapter::instance()->setTable(list, table1,   width, readOnly); 

    int r = table1->numRows();
    for (int i = 0; i <  r; ++i) {
      QString s = table1->text(i, 3);
      if ( s == "")
        continue;
      if (s == idEdit->text())
        table1->removeRow(i);
    }
}


void MergeProductDialog::confirmMerge()
{
    ulong id2 =0;
    QString name2;
    OrderMainAdapter::instance()->currentProductDetails(table1, id2, name2);
    if (id2 == 0) {
	QMessageBox::information(this, "Invalid details", "No id found for second product.");
	return;
    }
 
     QStringList l;
    
    l << "first product: "<<  "id=" << idEdit->text() << "  " << nameEdit->text();
    l << "\n merging with second product: id="<<QString("").arg(id2) << " "<<name2;
    l <<"\n" << "-> MERGE and keep ";
    if ( radioButton1->isChecked() )  
	l << "First product ?";
    else
	l << "Second product ?";
    if ( QMessageBox::warning( this, "WARNING: PERMANENTLY MERGING PRODUCTS", l.join(""), QMessageBox::Yes, QMessageBox::No) == QMessageBox::Yes) {
	    clog << "Accepted merge" << endl;
      ulong id1 = atol(idEdit->text().ascii());

      if ( radioButton2->isChecked()) {
        ulong tmp = id1;
        id1 = id2;
        id2 = tmp;
      }
      OrderMainAdapter::instance()->mergeProducts(id1, id2); // keep first id
    }
}
