/***************************************************************************
                          ordermainadapter.cpp  -  description
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
#include "discountdialog.h"
#include "ordermainadapter.h"
#include "Customer.h"
#include "Containers.h"
#include <string>
#include <sstream>
#include <qtable.h>
using namespace std;
OrderMainAdapter::OrderMainAdapter(){
}
OrderMainAdapter::~OrderMainAdapter(){
}

OrderMainAdapter * OrderMainAdapter::singleton = 0;

OrderMainAdapter * OrderMainAdapter::instance() {
  if (singleton == 0   )
  {
    singleton = new OrderMainAdapter();
  }
  return singleton;
}

/** finds Customers and returns a string list of customers.
   return value is session id for search phrase.   Needed in getCustomerDetails.
   - not good, this is not a stateless interaction.
   */                                            
 int OrderMainAdapter::findCustomer(
      const QString& first, const QString& last, QStringList& list )
 {
   list.clear();

   vector<Customer*>* pcusts =
	    SQLManager::instance()
      ->findCustomerByNames(
        string(first.ascii()),
        string(last.ascii())
      );
   stringstream ss;
   ss << last.ascii() <<"," << first.ascii();
   string phrase = ss.str();
   loadCustomerList( pcusts, list);
   updateCustomerSearchMaps(phrase, pcusts);
   
   return searchCustIndexes[phrase];
 }

//
// bool findCustomer(int sessionId,   QStringList& list ) {
//    if (mapCustSearches.find(sessionId) != mapCustSearches.end() )
//    {
//        list.clear();
//        loadCustomerList( mapCustSearches[sessionId] , list);
//        return true;
//    }
//    return false;
//
// }
//

 void  OrderMainAdapter::updateCustomerSearchMaps(const string& phrase, const vector<Customer*> * pcusts) {
   if (searchCustIndexes.find(phrase) == searchCustIndexes.end()) {
      searchCustIndexes[phrase] = searchCustIndexes.size() + 1;
   }
   if (mapCustSearches.find(searchCustIndexes[phrase]) != mapCustSearches.end()) {
      delete mapCustSearches[searchCustIndexes[phrase]];
   }
   mapCustSearches[searchCustIndexes[phrase]] = pcusts;

 }

  void OrderMainAdapter::loadCustomerList(const vector<Customer*>* pcusts, QStringList& list) {

    vector<Customer*>::const_iterator i, end;
    end = pcusts->end();
    int j = 0;
    for ( i = pcusts->begin() ; i != end; ++i ) {
  	  stringstream ss;
  	  ss << ++j << ": " << **i;
  	  list.push_back(QString(ss.str().c_str()));
    }
  }

   QStringList& OrderMainAdapter::getCustomerDetails(
    int searchSessionId, const QString& custSearchResultItem,
    QStringList& list)
   {
      list.clear();
      if (mapCustSearches.find(searchSessionId) == mapCustSearches.end() ) {
        return list;
      }

      const vector<Customer*> * pcusts =  mapCustSearches[searchSessionId];
      stringstream buf;
      for (int i = 0; i < custSearchResultItem.length() && custSearchResultItem[i] != ':' ; ++i) {
        buf << custSearchResultItem[i];
      }

      int n ;
      buf >> n;
      cout << "getCustomerDetails with item " << n << endl;

      if (--n >= pcusts->size())
        return list;
      Customer * cust = (*pcusts)[n];
      list.push_back(QString(cust->get_id()));
      list.push_back(QString(cust->get_firstname().c_str()));
      list.push_back(QString(cust->get_lastname().c_str()));
      list.push_back(QString(cust->get_address().c_str()));
      list.push_back(QString(cust->get_phone().c_str()));

      return list;
   }

   int OrderMainAdapter::setCustomerDetails( const QStringList& list) {
      if (list.size() < 5)
        return 0;

      Customer* c = new Customer(list[0].ascii(), list[1].ascii(), list[2].ascii(), list[3].ascii() , list[4].ascii());
      if ( SQLManager::instance()->storeCustomer(c)) {
          return atoi(c->get_id().c_str());
      } else return 0;


   }

   bool OrderMainAdapter::findProductByName( const QString & name,
    QPtrList<QStringList> & list)
    {
      vector<Product*>* vec =
      SQLManager::instance()->findProductByName( string(name.ascii()));
      if (vec == 0 || vec->size() == 0)
        return false;

      vector<Product*>::const_iterator i, end;
      end = vec->end();
      for ( i = vec->begin() ; i != end; ++i) {
        QStringList* sl = new QStringList() ;
        QString s;
        Product * p = *i;
        *sl << p->get_code();
        *sl << p->get_name();
        *sl << p->get_description();
        *sl << s.arg(p->get_pid());

        vector <ProductOffer*> * offers =
            SQLManager::instance() ->getProductOffers(p, time(NULL));
        
        for (int j = 0 ;  j < 2; ++j) {
           if ( offers && j < offers->size() ) {
              ProductOffer * po = (*offers)[j];
              *sl << po->get_price().get_string();
              *sl << Order::get_formatted_time(po->get_time());
              *sl << Order::get_formatted_time(po->get_end());
           }   else {
             * sl << "no offer" << "  -" << "  -";
           }
        }    

        
        if (offers) {
            for ( vector<ProductOffer*>::iterator i = offers->begin();
            i != offers->end(); ++i) {
              delete (*i);
            }
            delete offers;
        }
        list.append(sl);


      }
      
      for (i = vec->begin(); i != end; ++i) {
        delete (*i);
      }
      
      delete vec;

      list.setAutoDelete(true);
      return true;
    }


    unsigned long OrderMainAdapter::changeProduct( unsigned long id, const QString& code, const QString& name, const QString& description)
     {
      Product *p = new Product(name.ascii(), code.ascii(), description.ascii());
      p->set_pid(id);
            SQLManager::instance()->storeProduct(p,p);
      return p->get_pid();
      //delete p;
    }

    bool OrderMainAdapter::getOrderStrings( unsigned long id, QPtrList<QStringList>& data , bool  onlyUnpaid, QString& grandTotalStr) {
      if (id == 0)
        return false;

      data.clear();
      Customer * cust = SQLManager::instance()->findCustomerById(QString().arg(id).stripWhiteSpace().ascii());
      if (cust == 0)
        return false;
      vector<Order*>* porders = 0;
      if (onlyUnpaid)
        porders = SQLManager::instance()->getUnPaidOrders(cust);
      else
        porders = SQLManager::instance()->getOrders(cust);
      if (!porders)
        return false;

      Money* m = Order::get_total_of_orders(porders, MoneyMap::instance()->cloneDefault());
      grandTotalStr = QString(m->get_string().c_str());
      delete m;
      
      for ( int i = 0 ; i < porders->size(); ++i) {
        Order* order = (*porders)[i];

        QString time= QString(order->get_formatted_time(order->get_time()).c_str());

        QString fin= QString(order->get_formatted_time(order->get_paid()).c_str());

        Money * m = MoneyMap::instance()->cloneDefault();
        QString total = QString( order->get_total(*m).get_string().c_str() );
        delete m;

        QString id = QString().arg(order->get_id());

        QString discount = order->get_discount()->get_string();

        Money * m2 = MoneyMap::instance()->cloneDefault();
       
        QString origTotal = order->get_raw_total(*m2).get_string();
        delete m2;
        
        QStringList * pList = new QStringList();
        *pList << time <<  total << fin << id << discount << origTotal;
        
        data.append(pList);
      }
    }



    /** TODO : change listLatestProductOffers to listProductOffersFrom(..date..) */
       /** Bug Note: don't forget qdatetime.h include file, (not qdate.h)*/
     QPtrList<QStringList> & OrderMainAdapter::getOffers(  QPtrList<QStringList> & pStrList, const QDateTime& date, const QString& filter, bool allLatest) {
       pStrList.setAutoDelete(true);
       vector<Product*>* products = SQLManager::instance()->findProductByName(filter);
       if (!products)
          return pStrList;
       
       vector<ProductOffer*>* offers = SQLManager::instance()-> listLatestProductOffers(products,date.toTime_t(),  allLatest);

       if (!offers ) {
        delete products;
        return pStrList;
       }

       for (int i = 0 ; i < offers->size(); ++i) {
          ProductOffer* poffer = (*offers)[i];
          QStringList* sl = new QStringList();
          *sl  <<  poffer->get_product_name() << poffer->get_code()  ;
          *sl << poffer->get_price().get_string() << QString().arg(poffer->get_id());
          pStrList.append(sl);
       }
       delete products;
       delete offers;
       return pStrList;
   }


void OrderMainAdapter::setTable( QPtrList<QStringList> & list, QTable* table, QValueList<int>& width, QValueList<bool>& readOnly) {

    for (int j = 0; j < table->numRows(); ++j) {
      for (int i = 0; i < table->numCols(); ++i) {
        table->setText(j,i, "");
      }
    }
  if (list.count() == 0)
    return;
	table->setNumRows(list.count());
  int cols = ((QStringList*)list.at(0))->size();
	table->setNumCols( cols);

	for (int i = 0 ; i < list.count(); ++i) {
	    QStringList* pl = list.at(i);
	    for (int j = 0; j < pl->size(); ++j) {
		table-> setText(i,j , (*pl)[j]) ;
	    }
	}
	//QHeader * header = tableProducts1->horizontalHeader();
	for(int i = 0; i < cols ; ++i) {
	    //header->setLabel( i, header->label(i), width[i]);
	    if (width.size() <=i || readOnly.size() <= i)
		    break;
	    table->setColumnWidth(i, width[i]);
	    table->setColumnReadOnly(i,readOnly[i]);
	}
 }

  void  OrderMainAdapter::loadOrderItems( unsigned long order_id, QPtrList<QStringList>& data  , QString& totalStr){
    if (order_id == 0)
       return;
    Order * order =    SQLManager::instance()->findOrder(order_id);
     Money * m = MoneyMap::instance()->cloneDefault();
     vector<OrderItem*>* items = order->get_items();
     for ( int i = 0 ; i < items->size() ; ++i) {
       OrderItem* item = (*items)[i];
       QStringList * list = new QStringList();
       orderItemToStringList(item,  list);
       data.append(list);
     }
     data.setAutoDelete(true);

     totalStr = QString("").arg(order->get_total(*m).get_string());

  }

  void OrderMainAdapter::updateOrderItems(unsigned long cust_id,
  unsigned long& order_id,
   unsigned long offer_id, int qty, QPtrList<QStringList>& data ,
   QString& totalStr)
  {
     Customer * cust = SQLManager::instance()->findCustomerById(QString().arg(cust_id));
     Order * order = 0;
     if (order_id != 0) {
           vector<Order*>* porders =  SQLManager::instance()->getOrders(cust);
           if (porders == 0) {
              clog << "constraint violation. Order_id not found for customer_id ";
              clog << cust_id << endl;
              return;
           }
           for (unsigned int i = 0; i < porders->size(); ++i) {
             if (order_id == (*porders)[i]->get_id() ) {
                order = (*porders)[i];
                break;
             }
           }
     }  else {
         order = new Order(cust, time(NULL));
     }

     ProductOffer * offer =SQLManager::instance()->getProductOffer( offer_id);
     OrderItem *item = new OrderItem(order, offer, qty);
     order->add_item(item);
     SQLManager::instance()->storeOrder(order);
     order_id = order->get_id();

     QStringList* list = new QStringList();
     orderItemToStringList(item,  list);
     data.append(list);
     Money* m = MoneyMap::instance()->cloneDefault();

     totalStr = QString("").arg(order->get_total(*m).get_string());
     delete m;

  }

  void   OrderMainAdapter::orderItemToStringList( const OrderItem* item, QStringList* list)
  {
      list->append( item->get_product()->get_name());
     list->append( item->get_price().get_string());
     list->append( QString().arg(item->get_qty()));
     Money * m = MoneyMap::instance()->cloneDefault();
     list->append( item->get_subtotal(*m).get_string() );
     list->append( item->get_discount()->get_string());
     Money * m2 = MoneyMap::instance()->cloneDefault();
     list->append( item->get_raw_subtotal(*m2).get_string()); 
     list->append( QString().arg(item->get_offer_id() ) );
     delete m;
     delete m2;
  }

  bool OrderMainAdapter::removeOrderWithId(unsigned long order_id) {
     Order * order = SQLManager::instance()->findOrder(order_id);
     if (order == 0)
        return false;
     SQLManager::instance()->removeOrder(order);
     return true;
  }

                                          
  bool OrderMainAdapter::removeOrderItemWithId( unsigned long order_id, unsigned long offer_id)
  {
        if (order_id == 0 || offer_id == 0) return false;
        
        Order * order = SQLManager::instance()->findOrder(order_id);
        ProductOffer * offer = SQLManager::instance()-> getProductOffer(offer_id);

        OrderItem* item = order->remove_item((Product*)offer->get_product());
        bool result = item != 0;
        SQLManager::instance()->storeOrder(order);
        delete item;
        delete offer;
        delete order;
        
        return result;
    
  }

  bool OrderMainAdapter::removeOrderItem(  unsigned long order_id, unsigned int index) {
         Order * order = SQLManager::instance()->findOrder(order_id);
         order->remove_item(index);
         bool result = SQLManager::instance()->storeOrder(order);
         return result;

  }
  bool OrderMainAdapter::removeOrderItemsExceptWithOfferId( unsigned long order_id, const QValueList<unsigned long> & orig_offer_ids) {
            Order * order = SQLManager::instance()->findOrder(order_id);
            vector<OrderItem*>* items = order->get_items();
            if (items == 0) {
               //delete order;
               return false;
            }
             bool changed = false;
            for (int i = 0 ; i < items->size(); ++i) {
              OrderItem * item =   (*items)[i];
              if ( orig_offer_ids.find( item->get_offer_id()) == orig_offer_ids.end() ) {
                order->remove_item((Product*)item->get_product());
                changed = true;
              }

            }

            if (changed)
            {
                SQLManager::instance()->storeOrder(order);
            }

            delete items;
            //delete order;
            return changed;
   }
       /** BUGNOTE: QString& priceTxt is modifiable , so can't pass const QString references here. */
    bool OrderMainAdapter::createProductOffer(const QString& idStr, const QDateTime& start, const QDateTime& end,const QString& priceTxt)
    {
         if (idStr == "")
            return false;
         unsigned long prod_id = atol(idStr.stripWhiteSpace());
         if (prod_id == 0) {
            clog << "product id zero from " << idStr << endl;
            return false;
         }
               
         Money* m = MoneyMap::instance()->cloneDefault();
	       m->from_string(priceTxt);
         Product * p = SQLManager::instance()->findProduct(prod_id);
         ProductOffer * po = new ProductOffer(
              p,  m,
              QDateTime(start).toTime_t(),
              QDateTime(end).toTime_t() , 0
          );

         bool res = SQLManager::instance()->storeProductOffer(po);
         delete po;
        // delete m;   ProductOffer deletes it's own money.
         return res;
    }

    
    bool OrderMainAdapter::getOrderDates(unsigned long order_id , QDate& start,QDate& end)
   {
      Order* order = SQLManager::instance()->findOrder(order_id);
      if (order == 0)
         return false;

      QDateTime st, en;
      st.setTime_t(order->get_time());
      en.setTime_t(order->get_paid());

      start = st.date();
      end = en.date();
      delete order;
      return true;
   }   
      
      
      

   bool OrderMainAdapter::storeOrderDates(unsigned long order_id,const QDate& first,const QDate& paid)
   {
     Order* order = SQLManager::instance()->findOrder(order_id);
      if (order == 0)
         return false;
     QDateTime d ;
     d.setDate(first);
     order->set_time(d.toTime_t());
     d.setDate(paid);
     order->set_paid(d.toTime_t());
     int result = SQLManager::instance()->storeOrder(order);
     delete order;
     return result;


     
   }

   bool OrderMainAdapter::rememberOrder( unsigned long order_id)
   {
     Order* order = SQLManager::instance()->findOrder(order_id);
     return SQLManager::instance()->rememberOrder(order);

   } 
   
  bool OrderMainAdapter::restoreOrder( unsigned long order_id)
  {
      return SQLManager::instance()->restoreOrder(order_id);
  }

   bool OrderMainAdapter::setDiscount( unsigned long order_id, Discount* d)
   {
     Order* order = SQLManager::instance()->findOrder(order_id);
     order->set_discount(d);
     return SQLManager::instance()->storeDiscount(order);
   }

   bool OrderMainAdapter::setDiscount (ulong order_id, int index, Discount* d)
   {
      SQLManager* mgr = SQLManager::instance();
      Order* order = mgr->findOrder(order_id);
      if (index >= 0) {
        OrderItem* item = order->get_item(index);
        item->set_discount(d);
        return mgr->storeDiscount(item);
      }
      order->set_discount(d);
      return mgr->storeDiscount(order);
                                                                                 
   }

   Discount* OrderMainAdapter::createDiscount( bool isAmount, const QString& amt, int percent)
   {
      if (isAmount) {
        Money* money = MoneyMap::instance()->cloneDefault();
        money->from_string(string(amt.ascii()));
        
        return new AmountDiscount(money);

      }
      return new PercentDiscount(percent);

   }

   void OrderMainAdapter::inputDiscount(ulong order_id, int row, const QString& rawTotal,
   const QString& description ) {

    if (order_id <= 0 )
       return;
       
    DiscountDialog* dialog = new DiscountDialog();

    dialog->setRawTotal(rawTotal);
    dialog->setDescription(description);
    int result = dialog->exec();
    if ( result == QDialog::Accepted) {
       	int percent;
       	QString amt;
       	bool isAmount;

       	dialog->getDiscountDetails(isAmount, amt, percent);
         Discount* discount =
         OrderMainAdapter::instance()->createDiscount(isAmount, amt, percent);

         OrderMainAdapter::instance()->setDiscount(order_id,
          row,  discount
         );
    }
    delete dialog ;

   }


   

void OrderMainAdapter::currentProductDetails(QTable* table, ulong& id, QString& name )
{
  QTableSelection sel =table->selection(0);
    if (!sel.isActive())
	return;
    int row = sel.topRow();
    QString idStr = table->text(row, 3).stripWhiteSpace();

    if (idStr == "")
	id = 0;
    else
	id = atol(idStr.ascii());

    name = table->text(row, 1).stripWhiteSpace();

}

 bool OrderMainAdapter::mergeProducts( ulong idkeep, ulong idmerged)
 {

  return SQLManager::instance()->mergeProducts( idkeep, idmerged);
 }

 bool OrderMainAdapter::mergeCustomers( ulong idkeep, ulong idmerged)
 {

  return SQLManager::instance()->mergeCustomers( idkeep, idmerged);
 }