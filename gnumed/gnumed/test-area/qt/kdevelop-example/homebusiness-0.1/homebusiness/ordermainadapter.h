/***************************************************************************
                          ordermainadapter.h  -  description
                             -------------------
    begin                : Mon Apr 19 2004
    copyright            : (C) 2004 by s j tan
    email                : 
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

#ifndef ORDERMAINADAPTER_H
#define ORDERMAINADAPTER_H
#include <string>
#include <vector>
#include <qstringlist.h>
#include <qstring.h>
#include <qlistbox.h>
#include <qlineedit.h>
#include <qdatetime.h>
#include <qvaluelist.h>
#include <qtable.h>
#include "Customer.h"
#include <map>
using namespace std;

/**this class provides the data conversion functions for 
  *the kde dialog ordermain
  *
  *@author s j tan
  */


class OrderMainAdapter {
private:
   static OrderMainAdapter* singleton ;
   map < string, int> searchCustIndexes;
   map < int, const vector<Customer*> *> mapCustSearches;
protected:

    OrderMainAdapter();

    void loadCustomerList(const vector<Customer*>* pcusts, QStringList& list);

    void updateCustomerSearchMaps( const string &,const vector<Customer*> * pcusts);


public:
		~OrderMainAdapter();

  static OrderMainAdapter* instance();

  int findCustomer( const QString& first, const QString& last, QStringList& );

  QStringList& getCustomerDetails( int searchSessionId, const QString& custSearchResultItem, QStringList&);

  QStringList& getOrders(int searchSessionId,  const QString& searchResultItem, QStringList&);

  int setCustomerDetails( const QStringList& );

  bool  findProductByName( const QString & name, QPtrList<QStringList> & list);

  unsigned long changeProduct(unsigned long id, const QString& code, const QString& name, const QString& description);

  bool getOrderStrings( unsigned long id, QPtrList<QStringList>& data, bool  onlyUnpaid, QString& grandTotal);

  QPtrList<QStringList> &  getOffers(   QPtrList<QStringList> & list, const QDateTime& date, const QString& filter="", bool allLatest=true);

  void setTable( QPtrList<QStringList> & list, QTable* table, QValueList<int>& width, QValueList<bool>& readOnly) ;

  void updateOrderItems(unsigned long cust_id, unsigned long& order_id, unsigned long offer_id, int qty, QPtrList<QStringList> & , QString&) ;
 
  bool removeOrderWithId(unsigned long order_id);

  void  orderItemToStringList( const OrderItem* item, QStringList* list);


  void  loadOrderItems( unsigned long order_id, QPtrList<QStringList>& data  , QString& totalStr);
  

                                 
 bool removeOrderItemsExceptWithOfferId( unsigned long order_id, const QValueList<unsigned long> & orig_offer_ids) ;


  bool createProductOffer(const QString&, const QDateTime& start, const QDateTime& end,const QString& priceTxt);

  bool removeOrderItemWithId( unsigned long order_id, unsigned long offer_id) ;
  bool removeOrderItem(  unsigned long order_id, unsigned int index);
  bool getOrderDates(unsigned long order_id , QDate& start,QDate& end) ;
  bool storeOrderDates(unsigned long order_id,const QDate& first,const QDate& paid);

  bool rememberOrder( unsigned long order_id);

  bool restoreOrder( unsigned long order_id);

  bool setDiscount( unsigned long order_id, Discount*);

  bool setDiscount (ulong order_id,  int index, Discount*);   

  Discount* createDiscount( bool isAmount, const QString& amt, int percent);

   void inputDiscount(ulong order_id, int row, const QString& rawTotal,
   const QString& description ) ;

   void currentProductDetails(QTable* table, ulong& id, QString& name );

   bool mergeProducts( ulong idkeep, ulong idmerged) ;

   bool mergeCustomers(ulong idkeep, ulong idmerged);
                                                                                                                                                                                                          
};  // end class definition for OrderMainAdapter
    
#endif
