/* CONTAINERS.H : this file contains the declaration for
SQLManager - manages database access, and
*/
// need this for the definition of the string class
#include <string>
#include <vector>
#include <map>
#include <ctime>
#include <pgsql/libpq-fe.h>
#include <assert.h>
#include <iostream>
// need this to use the string class type as string and not std::string
// this means that a search is done inside the namespace std:: for any
// types.
using namespace std;
#ifndef CONTAINERS_H


// after this, if this file is included in the same scope, the above
// conditional will skip the lines up to #endif
#define CONTAINERS_H

#include "Customer.h"
// this makes sure the contents of the include file is included once.

/*

*/
class SQLManager {
	
private:
	static const int MAXQUERY = 1000;
	
  static string default_connect_str; //="dbname=nutrimetics2" ;
  static string connect_str;
  PGconn* connection;
	static SQLManager * theManager;

	map <string , Customer*> customerMap;

  map <unsigned long, Product*> productMap;
  
  map <unsigned long, Order*> orderMap;

	string lastCustomerId;

	static const char* selectAllCustomers;
	static const char* nextCustomerIdSeq ;


	static const char* insertCustomerFormat ;

	static const char* updateCustomerFormat ;


	static const char* findCustomerByIdClause ;

	static const char* findCustomerByNamesClause;


	void assertCustomerFields(PGresult* presult) {
		assert( strcasecmp(PQfname(presult, 0), "cust_id")==0);
		assert( strcasecmp(PQfname(presult, 1), "firstname")==0);
		assert( strcasecmp(PQfname(presult, 2), "lastname")==0);
		assert( strcasecmp(PQfname(presult, 3), "address")==0);
		assert( strcasecmp(PQfname(presult, 4), "phone")==0);
	}
	
	Customer* tupleToCustomer(PGresult* presult, int i);
	
	vector<Customer*>* queryToCustomers(const string& buffer);
	
	Product* tupleToProduct(PGresult * presult, int tuple);

	vector<Product*>* queryToProducts(const char* qry);
	
	ProductOffer * tupleToProductOffer( PGresult* presult, int tuple);

  Order * tupleToOrder( PGresult* presult, int tuple);
  Discount * tupleToDiscount(PGresult* presult, int tuple);
protected:
	SQLManager() {
    if (connect_str == "")
      connect_str = default_connect_str;
		connection = PQconnectdb(connect_str.c_str());
		if ( PQstatus(connection) != CONNECTION_OK) {						cerr << "CONNECTION TO ";
			cerr<< default_connect_str;
			cerr	<< "failed. Exiting" << endl;
			exit(-1);
		}       											
	}
	
	bool insertCustomer(Customer*);
	bool updateCustomer(Customer*);

	bool storeOrderItem(OrderItem*);
	bool deleteOrderItem(OrderItem*);
	bool loadOrderItems(Order*);

  

  bool loadDiscount(OrderItem*);
  bool loadDiscount( Order*);
  bool loadAllDiscounts(Order * order);

  bool executeCommand(stringstream& ss);
public:
	
	static SQLManager* instance() {
		if (theManager == 0) {
			theManager = new SQLManager();
		}
		return theManager;
	}
  static bool reconnect(const string& connectStr) {
    connect_str = connectStr;
    if (theManager)
      delete theManager;
    theManager = new SQLManager();
    return true;
  }
  
	vector<Customer*>* listAllCustomers();
  
	vector<Product*>* listAllProducts();
	
	bool storeCustomer(Customer* c);
	
	Customer * findCustomerById(const string& id);

	vector<Customer*>* findCustomerByNames(const string& firstnames, const string & lastnames);
	
	



	const string nextCustomerId();

	static void testCustomers();	
	
	static const int TESTCUSTOMERS = 10;

	bool storeProduct(Product* p, const Product* oldProduct =0);

	Product* removeProduct(Product* );

	Product* findProduct(unsigned long product_id);
	vector<Product*>* findProductByName(const string& name);
	vector<Product*>* findAllProducts();
	vector <Product*>* findProductByCodeOrName(const string& entry) ;


	bool storeProductOffer(ProductOffer* po);
	
	vector<ProductOffer*>* listLatestProductOffers(const vector<Product*>* products, const time_t currentWhen, bool allLatest = true);
	
 	ProductOffer* getLatestProductOffer(const  Product* p, const time_t currentWhen, bool allLatest );
  vector<ProductOffer*>* getProductOffers(const Product* p, const time_t currentWhen, bool anyLatest = false);
	map<unsigned long, vector<ProductOffer*>* >* getProductOfferHistory( vector<Product*>* );

	ProductOffer* getProductOffer(const unsigned long id);
 	 
	bool storeMoney( Money* m);

	Money* findMoney( const string& id);
  
  static const string to_sql_time(const time_t t, const char* format = "%C%y-%m-%d %H:%M:%S");
    
	static time_t sql_to_ctime(const char* c_time) ;
	
  Order* findOrder(unsigned long);
	Order* removeOrder(Order*);
	vector<Order*>* getOrders(Customer*);

  vector<Order*>* getPaidOrders(Customer*, bool paid = true);
	vector<Order*>* getUnPaidOrders(Customer*);

  vector<Order*> getOrdersWithin(Customer* , time_t start, time_t end);
	vector<Order*>* getAllPaidOrders(bool paid);

  bool storeOrder(Order*);
  bool rememberOrder(Order*);
  bool restoreOrder(unsigned long order_id);
	bool setNormalOffer(ProductOffer *po);	

  Discount*  SQLManager::load_discount(unsigned long order_id, unsigned long offer_id);

	bool storeDiscount(OrderItem* item);

  bool storeDiscount(Order* order);


  
  bool storeDiscountImpl(Discountable* item, const string& typeClause) ;

  bool mergeProducts( ulong idkeep, ulong idmerged) ;
                                                                        
  bool mergeCustomers( ulong idkeep, ulong idmerged);

  
};


class DiscountFactory {
protected :
    virtual bool set_value( PGresult*, Discount *)   = 0;
    virtual Discount* create_discount() = 0;
public:
    Discount* create_discount(PGresult*)  ;

};

class AmountDiscountFactory: public DiscountFactory {
protected:
    virtual bool set_value( PGresult*, Discount *)  ; 
    Discount* create_discount()    { return new AmountDiscount() ; }
};

class PercentDiscountFactory: public DiscountFactory {
protected:
     
     virtual bool set_value( PGresult*, Discount *)   ;
     Discount* create_discount()   {
                                      return new PercentDiscount() ;
                                }
};

class DiscountMap {

  
    private:
       map<const string,   DiscountFactory*> theMap;
       static DiscountMap* singleton ;
    protected:
      DiscountMap() : theMap( map<const string,  DiscountFactory*>() ) {}
    public:
      static   DiscountMap* instance() ;
      Discount* create_discount(const string& the_type, PGresult* values );
      void  register_discount(const string& , DiscountFactory*) ;
};


class Del {
  private:
    static Del * singleton;
  protected:
    Del() {}
  public:
    Del* instance() { if (singleton == 0) singleton = new Del();
                      return singleton;
                    }
  void clear(vector<Customer*>*);

  void clear(Customer*);

  void clear(vector<Product*>*);

  void clear(Product*);

  void clear(vector<ProductOffer*>*);

  void clear(ProductOffer*);
  void clear(Order*);
  void clear(vector<Order*>*);
};
       
#endif
