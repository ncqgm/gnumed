/****************************************************************************
** ui.h extension file, included from the uic-generated form implementation.
**
** If you wish to add, delete or rename functions or slots use
** Qt Designer which will update this file, preserving your code. Create an
** init() function in place of a constructor, and a destroy() function in
** place of a destructor.
*****************************************************************************/
#include "Customer.h"
#include <string>
using namespace std;

void DiscountDialog::showValueDiscount(const QString&)
{
    
	
	
}


void DiscountDialog::showPercentDiscount( int p )
{     
	  double discounted = ((double)p) / 100.;
	  Money * m = MoneyMap::instance()->cloneDefault();
	  m->from_string(string(totalLineEdit->text().ascii()));
	  m->multiply(discounted);
	  amountLineEdit->setText(QString(m->get_string().c_str() ) );
	  delete m;
    
}


void DiscountDialog::setRawTotal( const QString & total )
{
    totalLineEdit->setText(total);
}


void DiscountDialog::setDescription( const QString & d )
{
    descriptionLineEdit->setText(d);
}


void DiscountDialog::showDiscountFromAmount()
{
    
    Money * m = MoneyMap::instance()->cloneDefault();
	  m->from_string(string(amountLineEdit->text().ascii()));
    Money * m2 =  MoneyMap::instance()->cloneDefault();
    m2->from_string(string(totalLineEdit->text().ascii()));
    m2->subtract(*m);
    discountLineEdit->setText(QString(m2->get_string().c_str() ));
    delete m;
    delete m2;
}


void DiscountDialog::percentChosen( bool yes )
{
    spinBox1->setEnabled(yes);
    amountLineEdit->setEnabled(!yes);
}


void DiscountDialog::valueChosen( bool yes )
{
    spinBox1->setEnabled(!yes);
    amountLineEdit->setEnabled(yes);

}


QString DiscountDialog::getDiscounted()
{
    return  discountLineEdit->text();
}


void DiscountDialog::getDiscountDetails(bool& isAmount, QString& amt, int& percent)
{
    Discount * discount;
    isAmount =  amountLineEdit->isEnabled() ;
    amt = amountLineEdit->text();
    percent = spinBox1->value();
}
