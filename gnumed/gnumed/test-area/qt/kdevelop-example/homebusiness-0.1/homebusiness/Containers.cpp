
// need this for the definition of the string class
#include <string>
#include <vector>
#include <map>
#include <iostream>
#include <sstream>

#include <ctime>
#include "Containers.h"
#include "Customer.h"
#include <pgsql/libpq-fe.h>
// need this to use the string class type as string and not std::string
// this means that a search is done inside the namespace std:: for any
// types.
using namespace std;

//used in PQconnectdb to get a PQconn pointer
string SQLManager::default_connect_str="dbname=homebusiness" ;
string SQLManager::connect_str="" ;

SQLManager * SQLManager::theManager = 0;


const char* SQLManager::selectAllCustomers =
	"select cust_id, firstname, lastname, address, phone from customer";
const char* SQLManager::nextCustomerIdSeq =
	"select nextval('cust_id_seq')";


const char* SQLManager::insertCustomerFormat =
	"insert into customer(firstname, lastname, address, phone,cust_id) values ('%s', '%s', '%s', '%s', %s)";

const char* SQLManager::updateCustomerFormat =
	"update customer set firstname='%s', lastname='%s', address='%s', phone='%s' where cust_id = %s";

const char* SQLManager::findCustomerByIdClause = 
	" where cust_id = %s";

const char* SQLManager::findCustomerByNamesClause = 
	" where lower(firstname) like lower('%%%s%%') and lower(lastname) like lower('%%%s%%')";
	
	
Customer * SQLManager::tupleToCustomer(PGresult* presult, int i) {
	return	new Customer(
		PQgetvalue(presult, i, 0), 
		PQgetvalue(presult, i, 1),
		PQgetvalue(presult, i, 2), 
		PQgetvalue(presult, i, 3),
		PQgetvalue(presult, i, 4)
			    );

}

vector<Customer*>* SQLManager::listAllCustomers() {
	vector<Customer*> * pvec = new vector<Customer*>();
	PGresult* presult = PQexec(connection, selectAllCustomers);
	
	if (PQresultStatus(presult) == PGRES_TUPLES_OK) {
		// a valid, non-empty result
		assertCustomerFields(presult);
		int sz = PQntuples(presult);
		int nfields = PQnfields(presult);

		// add in any tuples as Customers not already in customerMap
		for (int i  = 0 ; i < sz; ++i ) {
			char* id = PQgetvalue( presult, i, 0);
			if (customerMap.find(id) == customerMap.end() )
			{
				
				customerMap[id] = tupleToCustomer(presult,i); 

			}
		}
		  
		
		for ( map<string, Customer*>::const_iterator i =
			       customerMap.begin();
		       i != customerMap.end(); ++i) {
			
			pvec->push_back( i->second);	
		}		
	}	
	PQclear(presult);
	return pvec;
	
}


bool SQLManager::storeCustomer(Customer* c) {
	if (c->id == "" || !atol(c->id.c_str()) ) {
		c->id = nextCustomerId();
		return insertCustomer(c);
	}	
	bool res;

	if (customerMap.find(c->id) == customerMap.end() ) {
		customerMap[c->id] = new Customer();
		res = insertCustomer(c);
	} else {
		res = updateCustomer(c);
	}
	customerMap[c->id]->copy(c);
	return res;
}

bool SQLManager::insertCustomer(Customer* c) {
	char buf[MAXQUERY];
	snprintf(buf, MAXQUERY, insertCustomerFormat, c->firstname.c_str(), c->lastname.c_str(), c->address.c_str(), c->phone.c_str(), c->id.c_str() );
	
	PGresult* presult = PQexec(connection, buf);
	bool result = PQresultStatus(presult) == PGRES_COMMAND_OK;
	PQclear(presult);
	return result;
}

bool SQLManager::updateCustomer(Customer* c) {
	char buf[MAXQUERY];
	snprintf(buf, MAXQUERY, updateCustomerFormat,  c->firstname.c_str(), c->lastname.c_str(), c->address.c_str(), c->phone.c_str(), c->id.c_str() );

	PGresult* presult = PQexec(connection, buf);
	bool result = PQresultStatus(presult) == PGRES_COMMAND_OK;
	PQclear(presult);
	return result;

}

Product* SQLManager::tupleToProduct(PGresult * presult, int tuple) {
	if (tuple < PQntuples(presult) ) {
		Product *p = new Product( 
		string(PQgetvalue(presult, tuple, 1)),
		string(PQgetvalue(presult, tuple, 2)),
		string(PQgetvalue(presult, tuple, 3)) 		);

		p->set_pid ( atol(PQgetvalue(presult, tuple, 0) ) );
		return p;
	}	
	return 0;
};

vector<Product*>*   SQLManager::findAllProducts() {
          return             listAllProducts();
}

vector<Product*>* SQLManager::listAllProducts() {
	return queryToProducts("select  product_id, name, code, description from Product"); 
}
	
/** convert a pqlib query result into a vector of products */
vector<Product*>* SQLManager::queryToProducts(const char* buf) {	
	
	PGresult* presult = PQexec(connection, buf);
	
	vector<Product*>* pvec = new vector<Product*>();
	
	if (PQresultStatus(presult) == PGRES_TUPLES_OK) {
	
		for (int i = 0; i < PQntuples(presult); ++i) {
			Product* p = tupleToProduct(presult, i);
	
			// if already in product map then update the map's
			// product and swap pointer to the product in the map.
//			if (productMap.find(p->get_pid() ) != productMap.end() ) {
//
//				productMap[p->get_pid()]->copy(p);
//				Product* newp = productMap[p->get_pid()];
//				delete p;
//				p = newp;
//
//			} else {
//
//				productMap[p->get_pid()]= new Product();
//
//			}
			
			pvec->push_back(p);
		}
	}
	PQclear(presult);
	return pvec;
	

}


Product* SQLManager::findProduct(unsigned long product_id) {
	char buf[MAXQUERY];
	stringstream ss;
	ss << "select  product_id, name, code, description from Product where product_id="<< product_id ;
	PGresult* presult=PQexec(connection, ss.str().c_str() );
	if (PQresultStatus(presult) != PGRES_TUPLES_OK) {
		cout << PQresultErrorMessage(presult);
		PQclear(presult);
		return 0;
	}
	Product* product = tupleToProduct(presult, 0);
	
	
	PQclear(presult);
	return product;


}

vector<Product*>* SQLManager::findProductByName(const string& name) {
	char buf[MAXQUERY];
	snprintf(buf, MAXQUERY, "select product_id, name, code, description from product where lower(name) like lower('%%%s%%')", name.c_str() );
	return queryToProducts(buf);
}

vector <Product*>* SQLManager::findProductByCodeOrName(const string& entry) {
	vector<Product* >* vp;
	stringstream ss;
	ss << "select product_id, name, code, description from product where lower(name) like lower('%";
	ss << entry << "%')  or code like '%" << entry << "%'";
	return queryToProducts(ss.str().c_str() );

}

bool SQLManager::storeProduct(Product* p, const Product* oldProduct ) {
	char buf[MAXQUERY];

	stringstream ss;
	if (oldProduct  && oldProduct->get_pid() && oldProduct->get_pid() == p->get_pid() ) {
		ss << "update product set name='";
		ss <<p->get_name(); 
		ss << "', description='";
		ss <<p->get_description() ;
		ss << "', code='";
	       	ss <<p->get_code() ; 
		ss << "'  where product_id=" ;
		ss << p->get_pid() ;

	} else {
		
		PGresult* presult = PQexec(connection, "select nextval('product_id_seq')");
		if (!PQresultStatus(presult) == PGRES_TUPLES_OK) {
			cout << PQresultErrorMessage(presult);
			PQclear(presult);
			return false;
		}
		
		unsigned long id = atol(PQgetvalue(presult, 0, 0));
		p->set_pid( id);

		PQclear(presult);
		ss << "insert into product(product_id, code, name, description) values (";
		ss <<  p->get_pid(); 
		ss << ",'"<< p->get_code()  ;
		ss <<"', '";  
		ss << p->get_name() ; 
		ss<<"'";
	        ss << ", '" << 	 p->get_description() << "' )";
	}

		
	const char * qry = ss.str().c_str();

	PGresult* presult = PQexec(connection, qry);
	bool result = (PQresultStatus(presult) == PGRES_COMMAND_OK);
	
	//productMap[p->get_pid() ]=p;
       	
	PQclear(presult);
	return result;	

}

Product* SQLManager::removeProduct(Product* prod) {
	stringstream ss;
	ss << "delete from product where product_id =" << prod->get_pid();
	const char * qry = ss.str().c_str();
	PGresult* presult = PQexec(connection, qry);	
	bool result = (PQresultStatus(presult) == PGRES_COMMAND_OK);

	if (result == true && atoi(PQcmdTuples(presult)) > 0) {
		//Product *p = productMap[prod->get_pid()];
		//productMap.erase(prod->get_pid() );
		return prod;
	}
	return 0;
}

 bool SQLManager::storeMoney(  Money* m) {
	PGresult* presult;
	clog << "storing " << m->get_string() << " it has id = " << m->get_id() << endl;
	if (m->id != "" ) {
    const char* qry =   m->sql_update().c_str();
		presult = PQexec(connection, qry );	

	} else {
		stringstream ss;
		ss << "select nextval('" << m->sequencer_name() << "')";
		presult = PQexec(connection, ss.str().c_str() );
		if (PQresultStatus(presult) != PGRES_TUPLES_OK)
			return false;
		m->id = string(PQgetvalue(presult, 0, 0));
		PQclear(presult);
    // BUG: forgot to assign presult again after clearing, so it is cleared twice later.
		presult = PQexec( connection, m->sql_insert().c_str() );
	}

	bool ok = PQresultStatus(presult) == PGRES_COMMAND_OK;
	PQclear(presult);
	return ok;		
 }


 Money* SQLManager::findMoney( const string& id) {
	 stringstream ss;
	 // find the type of the money with this id
	 ss << "select "<<Money::SQL_TYPE <<" from money where " << Money::SQL_ID <<"="<<  id;	
	PGresult * presult = PQexec(connection, ss.str().c_str() );
	if (PQresultStatus(presult) != PGRES_TUPLES_OK && PQntuples(presult) != 1) 
		return 0;
	
	// clone the money object registered for the type name found.
	Money * money = MoneyMap::instance()->clone( string(PQgetvalue(presult,0,0)) );
	PQclear(presult);

	// find the money field values
	money->id = string(id);

	presult = PQexec(connection, money->sql_select().c_str());
	
	
	if (PQresultStatus(presult) != PGRES_TUPLES_OK && PQntuples(presult) != 1) {
		return 0;
	}
	vector<string> vals;
	for (int x = 0; x < PQnfields(presult); ++x ) { 
		vals.push_back(string(PQgetvalue(presult, 0, x)));
	}
	
	money->set_state(vals);	
	PQclear(presult);
	return money;
 }



bool SQLManager::storeProductOffer(ProductOffer* po)
  {
	char buf[MAXQUERY];
	const Product* prod = po->get_product();
	//ProductOffer *po2 = getLatestProductOffer(prod);
/* this ends previous product offers ; disabled to allow for an ongoing
 * product offer as a normal price. 	
	while (po2 != 0 && po2->get_end()  < 1000) {
		po2->set_end(time(NULL) - 10);
		stringstream ss;
		ss << 
		"update product_offer set end_offer = '";
		ss << SQLManager::to_sql_time(po2->get_end(), "%d-%m-%y") ;
		ss << "'";
		ss <<" ";
		ss << " where product_id = ";
	       ss << po2->get_product()->get_pid() ;
	       ss << " and date_trunc('day', end_offer) = '1-1-1970'" ;
		const char* qry = ss.str().c_str();
		PGresult * presult = PQexec( connection ,qry);
#ifdef NDEBUG		
		cout << "executing " << buf << endl;
		if ( PQresultStatus(presult) != PGRES_COMMAND_OK)
				cout << *po2 << "WAS NOT STORED" << endl;
		else	
				cout << *po2 << "STORED" << endl;
#endif
		delete po2;
		PQclear(presult);
		po2 = getLatestProductOffer(prod);
	}	

*/
	if (!storeMoney(  (po->price) )) {
		cout << po->get_price().get_string() << " did not store." << endl;
		return false;
	
	}
  
	string price_id = po->price->get_id();
	stringstream ss;
	
	if (po->get_id()  == 0) {
		PGresult* presult = PQexec(connection, "select nextval('prod_offer_id_seq')");
		if (PQresultStatus(presult) != PGRES_TUPLES_OK || PQntuples(presult) != 1) {
			cout << PQresultErrorMessage(presult) << endl;
			cout << "failed to get product offer sequence nextval" << endl;
			PQclear(presult);
			return false;
		}
		ss << "insert into product_offer(";
		ss <<"prod_offer_id, money_id, product_id, start_offer, end_offer)";
		ss << "values (";
		ss << PQgetvalue(presult,0,0) << ",";
	        ss <<	po->get_price().get_id() << ",";
	        ss <<  po->get_product()->get_pid() <<", ";
		ss << "'" << SQLManager::to_sql_time(po->get_time())  <<"',";
		ss <<"'" << SQLManager::to_sql_time(po->get_end()) << "'";
		ss <<" )";
		PQclear(presult);
	}else {
		ss << "update product_offer set";
		ss << "money_id = " << po->get_price().get_id() << ",";
		ss << "product_id = " << po->get_product()->get_pid() <<", ";
		ss << "start_offer = ";
		ss << "'" << SQLManager::to_sql_time(po->get_time())  <<"',";
		ss << "end_offer = ";
		ss <<"'" << SQLManager::to_sql_time(po->get_end()) << "'";
		ss << " where prod_offer_id = " << po->get_id();
		
	}
	const char * cmd = ss.str().c_str();
	PGresult* presult = PQexec(connection, cmd);	
	bool result = (PQresultStatus(presult) == PGRES_COMMAND_OK);
	PQclear(presult);
	if (!result) {
#ifdef NDEBUG
		cout << "FAILED";
#endif		
	}
	return result;
  }

bool SQLManager::setNormalOffer(ProductOffer *po) {
	if (!storeProductOffer(po)) {
		cout << "SQLManager::setNormalOffer failed. StoreProductOffer failed" << endl;
		return false;
	}
	
	char buf[MAXQUERY];
	stringstream ss;
	ss << "insert into normal_offer(start_offer, product_id) values (";
        ss <<	"'";
	ss << SQLManager::to_sql_time(po->get_time());
	ss << "'";
	ss << ", ";
	ss << po->get_product()->get_pid();
	ss << ")";

	const char* qry = ss.str().c_str();
		

	PGresult* presult = PQexec(connection, qry);	

	bool result = (PQresultStatus(presult) == PGRES_COMMAND_OK);
	PQclear(presult);

  }



ProductOffer * SQLManager::tupleToProductOffer( PGresult* presult, int tuple) {
	  if (PQntuples(presult) == 0) {
		  //cout << "NO TUPLES IN PRODUCT OFFER RESULT" << endl;
	  	  return  0;
  	  }
	  char * c_prod_offer_id = PQgetvalue(presult, tuple, 4);
	  char* c_product_id = PQgetvalue(presult, tuple, 3);
	  char* c_price_id = PQgetvalue( presult, tuple, 2);
	  char* c_end = PQgetvalue(presult, tuple ,1);
	  char * c_time = PQgetvalue(presult, tuple , 0);
    clog << "c_product_id " <<     c_product_id << " " <<endl;
	  Product* product = findProduct(atol(c_product_id) );
	  Money* price = findMoney( string(c_price_id) );
	  
	  
	  ProductOffer* p = new ProductOffer( product, price, sql_to_ctime(c_time), sql_to_ctime(c_end) , atol(c_prod_offer_id));
	  return p;
			  
  }

ProductOffer* SQLManager::getLatestProductOffer(const Product* p, time_t afterTime, bool allLatest) {
      ProductOffer* po = 0;
      vector<ProductOffer*>* poffers = getProductOffers(p, afterTime, allLatest);
      if (!poffers)
        return 0;
      if (!poffers->size()) {
        delete poffers;
        return 0;
      }
      
      po = (*poffers)[0];        //FIXME will leak if more than one offer
      delete poffers;
      return po;
  }
  
vector<ProductOffer*>* SQLManager::getProductOffers(const Product* p, const time_t currentWhen, bool anyLatest) {
	
      if (p == 0)
    		return 0;
    	char buf[MAXQUERY];
    	stringstream ss;
      string timeStr =to_sql_time(currentWhen);
    	ss <<  "select start_offer, end_offer,  money_id , product_id , prod_offer_id from product_offer po1 where po1.product_id = " << p->get_pid();
    	 if (!anyLatest)
          ss <<  " and po1.start_offer <= '" << timeStr << "' ";
     
      ss << " and (date_trunc('day',po1.end_offer)= '1970-01-01'  or po1.end_offer >= '" << timeStr <<"') ";
      ss << " order by start_offer desc" ;

       
    	const char * qry = ss.str().c_str();
    	//cout << "Latest Offer query: " << qry<< endl;

    	PGresult* presult = PQexec(connection,qry);
    	bool result = (PQresultStatus(presult) == PGRES_TUPLES_OK);
      if ( !result) {
          cout << PQresultErrorMessage(presult) << endl;
          PQclear(presult);
          return 0;
      }
      vector<ProductOffer*> * offers = new vector<ProductOffer*>();
      for ( int i = 0 ; i < PQntuples(presult); ++i ) {
    	  ProductOffer* offer = tupleToProductOffer( presult, i);
        offers->push_back(offer);
      }
    	PQclear(presult);
    	return offers;
    	  

}

  ProductOffer * SQLManager::getProductOffer(const unsigned long id) {
	stringstream ss;
	ss << "select start_offer, end_offer,  money_id , product_id , prod_offer_id from product_offer where prod_offer_id = " << id;
	const char* cc = ss.str().c_str();
	PGresult* presult =PQexec(connection, cc);
	bool result = (PQresultStatus(presult) == PGRES_TUPLES_OK);
  if (!result)
  
    return 0;
	ProductOffer* offer = tupleToProductOffer( presult, 0);
	PQclear(presult);
	return offer;

  }

  vector<ProductOffer*>* SQLManager::listLatestProductOffers(const vector<Product*>* products, const time_t currentWhen, bool allLatest)
  {
	if (products == 0 || products->size() == 0) 
		return 0;
	vector<ProductOffer*>* poffers = new vector<ProductOffer*>();
		
	vector<Product*>::const_iterator p;
	vector<Product*>::const_iterator end = products->end();
	for (p = products->begin(); p != end; ++p) {
		vector<ProductOffer*>* pov = getProductOffers(*p, currentWhen, allLatest);
		
	//	cout << "retrieving for product " << **p;
		
		if (pov == 0) {
			//cout << "none" << endl;
			continue;
		}
    vector<ProductOffer*>::const_iterator i,e;
    i = pov->begin();
    e = pov->end();
    for ( ; i != e; ++i) {
         //	cout << "retrieved " << po << endl;
       		poffers->push_back(*i);
    }
    delete pov;
	
	}
	return poffers;
  
  }

 map< unsigned long, vector<ProductOffer*>* >* SQLManager::getProductOfferHistory( vector<Product*>* products) {
	stringstream ss;
	ss << "select  start_offer, end_offer, money_id , product_id, prod_offer_id  from product_offer where product_id in ( ";
	vector<Product*>::const_iterator p;
	for (p = products->begin(); p != products->end(); ++p) {
		ss <<  (*p)->get_pid() ;
		
		if (  (p+1)!=products->end() ) {
			ss << ", ";
		}
	}
	ss << ") order by product_id, start_offer";
	
	//cout << "SQL for getProductOfferHistory is " << ss.str() << endl;	
	PGresult* presult = PQexec(connection, ss.str().c_str() );	
	bool result = (PQresultStatus(presult) == PGRES_TUPLES_OK);
	map < unsigned long, vector<ProductOffer*>* >* vmap = new map < unsigned long, vector < ProductOffer*>* >();
		
	for (int i = 0 ; i < PQntuples(presult); ++i) {
		ProductOffer* p = tupleToProductOffer(presult, i);
		if (p == 0) 
			continue;
		if (vmap->find( p->get_product()->get_pid() ) == vmap->end()) {
			(*vmap)[p->get_product()->get_pid()] = new vector<ProductOffer*>();
		} 			
		((vector<ProductOffer*>* )(*vmap)[p->get_product()->get_pid()])->push_back(p);
		//cout << "Found product offer" << *p << endl;
	}
	return vmap;	


}


void SQLManager::testCustomers(){
	const char* firstnames[]= {
		"Henry", "William", "Peter", "Ian",
		"Davin", "Yuri", "Tony", "Sally",
		"Heather", "Monica", "Mary", "Sheila",
		"Betty", "Jennifer", "Anne", "Paula",
		"Olga", "Hilda", "Gary", "Vincent",
		"Andrew", "Kevin" , ""};
	const char* lastnames[] = {
	"Jones", "Smith", "Lee", "Yang", "Chan",
	"Beck", "Cameron", "James", "Nam",
	"Nguyen", "Ransome", "Ellard" , ""
	};

	const char* address[] = {
		"White", "Black", "Corowa",
		"Kallista", "Gregoria", 
		"Browns", "Green", "Blueborn", 
		"Lilac", "Perugia" , "Martha", 
		"Wall", "" };

	const char* suffixes[] = {
		"Ave", "St", "Blvd", "Rd", 
		"Pde" , "" };
	const char* suburbs[] = {
		"Blackburn", "Sunbury",
		"Altona", "Essendon", 
		"Boronia", "Hallam", 
		"Westgarth", "Kealba", ""
	};

	

	typedef vector<string> S;
	S fnames, lnames, addrs, sufs, urbs;
	
	const char** srcs[] = { firstnames, lastnames, address, suffixes, suburbs , 0};
	S* pvecs[] = { &fnames, &lnames, &addrs, &sufs, &urbs, 0 };
	typedef const char***  charsarrayT;
	typedef S** SarrayT;
	charsarrayT ppc;
	SarrayT dest;
	for (  ppc = srcs ,  dest = pvecs;
		       	*ppc != 0; 
			++ppc, ++dest )   {
		for (const char** pbuf = *ppc; strlen(*pbuf)!=0; ++pbuf) {
			S* pvec = *dest;
			pvec->push_back(string(*pbuf));
		}
	}

	const char* labels[] = {"firstnames", "lastnames", "addresses", "suffixes", "suburbs" };

	SarrayT ppvec = pvecs;

	// iterate over loaded string vectors and show their contents 
	// show the associated label before each vector contents.
	for (int i = 0  ; ppvec[i] != 0; ++i ) {
		S* pvec = ppvec[i];
		cout << labels[i] << ": ";
		for ( S::const_iterator j = pvec->begin(); 
				j != pvec->end(); ++j) {

			cout << *j << "  ";
		}
		cout << endl;
		
	}

	// NO DEBUGGING ! C++ static type checks and C seamlessness 
	// really worked here.
	srandom( (unsigned int) time(NULL));
	vector <Customer*> customers;
	for (int i= 0; i < TESTCUSTOMERS; ++i) {
		
		// random address
		stringstream ss ;
		ss << random()%100 << ", ";
		ss << addrs[random()%addrs.size()] << " ";
	        ss << sufs[random() % sufs.size()];
		ss << ", " << urbs[random() % urbs.size() ] << ".";
		
		// random phone number
		char buffer[50];
		snprintf(buffer, 50, "%ld", random());
		
		Customer *c = new Customer(
				"",
				fnames[ random() % fnames.size()],
				lnames[ random() % lnames.size()],
				ss.str(), 
				string(buffer)
				);
		
		cout << *c << endl;
		customers.push_back(c);
					
		
	}
	
	SQLManager* mgr = SQLManager::instance();
	
	vector<Customer*>::iterator i;
	
	for ( i =customers.begin(); i != customers.end(); ++i)
	{
		if(!mgr->storeCustomer(*i)) 
		{
			cout << "failure in storing " << **i <<endl;
		}
	}
	
	vector<Customer*>* pcusts = mgr->listAllCustomers();
	
	for (i= pcusts->begin(); i != pcusts->end(); ++i) 
	{
		cout << "In store was : " << **i << endl;
	}

		
	for (i= pcusts->begin(); i != pcusts->end(); ++i)  {
		cout << "changing phone number of " << **i <<endl;
		// random phone number
		char buffer[50];
		snprintf(buffer, 50, "%ld", random());
		Customer* pc = *i;	
		pc->set_phone(string(buffer));
		if (mgr->storeCustomer(*i))
			cout << "phone number is now " << buffer << endl;
		else
			cout << "failure in storing " << **i << endl;
	}
	delete pcusts;

	const char* findLastNames[] = { "Nguy", "Cam", "Jo", "Rans", "" };

	const char** pname;

	for (pname = findLastNames; strlen(*pname) != 0; ++pname) {
	
		vector<Customer*>* vcust = mgr->findCustomerByNames( "", *pname);
		cout << endl << "Customers with surnames like " << *pname << " are " << endl;
		for (vector<Customer*>::const_iterator ci = vcust->begin();
			ci != vcust->end(); ++ci) {
			cout << **ci << endl;

		}
	}

	const char* product[] = {
	"lipstick", "foundation", "face wash", "shampoo", "conditioner",
	"eyeliner", "nail polish", "" };

	const char* style[] =	{
		"moderne", "rainforest", "avant garde", 
		"chic", "70s", "glam" , "" 
	};

	const char* description[] = {
		"lovely", "stunning", "exciting", "cool", "aloof", "spacey",""
	};

	int nproducts = 0, nstyles  =0 , ndescriptions  =0 ;
	
	for( const char** p = product; strlen(p[nproducts]) >0; ++nproducts);
	for( const char** p = style; strlen(p[nstyles]) >0; ++nstyles);
	for( const char** p = description; strlen(p[ndescriptions]) >0; ++ndescriptions);


	int TESTPRODUCTS=4;
	for (int i =0 ; i < TESTPRODUCTS; ++i) {
		char name[200];
		snprintf(name, 200, "%s %s", style[random() % nstyles], 
				product[random() % nproducts] );
		
		char code[20];
		snprintf(code, 20, "%ld", random()); 
		Product * p = new Product( name, code, description[random()%ndescriptions]);
		mgr->storeProduct(p,0);
		
	}	

	vector<Product*> * pprods = mgr->listAllProducts();

	vector< Product* >::const_iterator p;
	for (p = pprods->begin(); p != pprods->end(); ++p) {
		cout << "STORED PRODUCT: " << **p <<endl;
	}

}
		
		


const string SQLManager::nextCustomerId() {
	PGresult* presult = PQexec(connection, nextCustomerIdSeq);
	if (PQresultStatus(presult) == PGRES_TUPLES_OK) {
		lastCustomerId =  string(PQgetvalue(presult, 0, 0) ); 
		return lastCustomerId;
	}	
	cerr << "UNABLE TO RETRIEVE CUSTOMER SEQUENCE VALUE.";
        cerr <<	"TRYING STORED VALUE." << endl;
	if (lastCustomerId != "") {
		char buf[100];
		unsigned long id = atoi(lastCustomerId.c_str());
		++id;
		snprintf(buf, 100, "%ld", id);
		cerr << "Created next id = " << buf << endl;
		lastCustomerId = string( buf);
		return lastCustomerId;
	}
	

}



Customer * SQLManager::findCustomerById(const string& id)
{

	map< string, Customer*>::iterator icust ;
	if ( (icust = customerMap.find(id)) != customerMap.end() ) {
		Customer* pc = icust->second;
		return pc;
	}
	
	char qbuffer[100];
	char buffer[120];
	snprintf(qbuffer, 200, "%s %s", selectAllCustomers, findCustomerByIdClause);
	snprintf(buffer, 120, qbuffer, id.c_str() );

	vector<Customer*>* pvec = queryToCustomers(buffer);

	if (pvec == 0)
		return 0;

	if ( pvec->size()==1) {
		Customer* pc = (*pvec)[0];
		delete pvec;
		return pc;
	}
	delete pvec;
	return 0;


}

vector<Customer*>* SQLManager::queryToCustomers(const string& query) {
	
	cout << "query = "<< query<< endl;
	
	PGresult* presult = PQexec(connection, query.c_str());
	vector<Customer*>* pvec = 0;
	if( PQresultStatus(presult) == PGRES_TUPLES_OK) {
		pvec = new vector<Customer*>();
		for (int i = 0; i < PQntuples(presult); ++i) {
			Customer *pc = tupleToCustomer(presult, i);
			pvec->push_back(pc);
		}
	}
	PQclear(presult);		

	if (pvec != 0) {  // check if id of customers in vector is already
			// in manager's customer map, and store if not present
			// or substitute manager's version of customer.
			// no check for newer versions made.
		vector<Customer*>::iterator i;
		for (i = pvec->begin(); i!= pvec->end(); ++i) {
			Customer * pc = *i;
			if (customerMap.find(pc->get_id()) != customerMap.end() ) 
			{
				customerMap[pc->get_id()]->copy( pc);
				*i = customerMap[pc->get_id()];
			} else {
				customerMap[pc->get_id()] = pc;
			}	
		}	
		
	}
	return pvec;

}

vector<Customer*>* SQLManager::findCustomerByNames(
		const string& firstnames, const string & lastnames)
{
	int len = strlen(findCustomerByNamesClause) + firstnames.size()+ lastnames.size() ;
	char*  qbuffer = new char[len+1];
	snprintf(qbuffer, len,  findCustomerByNamesClause, firstnames.c_str(), lastnames.c_str() );
	cout << "qbuffer = " << qbuffer << endl;

	stringstream ss ;
	ss << selectAllCustomers << " " << qbuffer;


	vector<Customer*>* v = queryToCustomers(ss.str());
	delete qbuffer;
	return v;

}
	

Order* SQLManager::removeOrder(Order* order) {
  stringstream ss;
  ss << "delete from order_item where order_id = " << order->get_id() ;
  vector<string> sl;
  sl.push_back(ss.str());

  stringstream ss2;
  ss2 << "delete from orders where order_id = " << order->get_id();
  sl.push_back(ss2.str());

  for (int i = 0 ; i < sl.size() ; ++i) {
      const char* cmd = sl[i].c_str();
    
      PGresult* result = PQexec(connection, cmd );
      if ( PQresultStatus(result) != PGRES_COMMAND_OK) {
          clog << PQresultErrorMessage(result) << endl;
          PQclear(result);
          break;

      }
      PQclear(result);
  }

 
  
	return order;
}
bool SQLManager::storeOrder(Order* order) {
	string qry;
	bool retValue ;
	PGresult* result; 
	stringstream ss;
	
	if (order->get_id() == 0) {
		result = PQexec( connection, "select nextval('order_id_seq')");
		if (PQresultStatus(result) == PGRES_TUPLES_OK && PQntuples(result)  == 1) {
			unsigned long id = atol( PQgetvalue(result, 0, 0) );
			order->set_id(id);
			PQclear(result);		
			ss << "insert into orders( order_id, order_date, cust_id, paid_date) values ( ";
			ss << id << "," << "'"<< to_sql_time(order->get_time()) <<"'";
			ss << "," ;
			ss<< order->get_customer()->get_id() ;
			ss << "," ;
			ss << "'";
			ss << to_sql_time(order->get_paid());
			ss << "'";
			ss << ")";
		} else {
			clog << PQresultErrorMessage(result) << endl;
      PQclear(result);
			
      return false;
		}
		
	} else {
		ss << "update orders set cust_id =";
		ss << order->get_customer()->get_id();
		ss << ",";
	        ss <<	" order_date = '" ;
		ss << to_sql_time(order->get_time()) <<"'";
		ss << ", ";
		ss << "end_date = ";
		ss << "'"<< to_sql_time(order->get_completed()) <<"'";
		ss << ", ";
		ss <<" paid_date = ";
		ss << "'" << to_sql_time(order->get_paid()) << "'";
		ss << " where order_id = " << order->get_id();
	}
	
	const char* cquery = ss.str().c_str();
	result = PQexec(connection, cquery);
	retValue = PQresultStatus(result );
	if (!retValue) {
		clog << PQresultErrorMessage(result) << endl;
		PQclear(result);		
		return false;
	}
	PQclear(result);		
	storeDiscount(order);
	vector<OrderItem*>* items = order->get_items();
	vector<OrderItem*>::const_iterator i;
	for (i = items->begin(); i != items->end(); ++i) {
		storeOrderItem(*i);
    
	}

	for (i = order->deleted.begin() ; i != order->deleted.end(); ++i) {
		deleteOrderItem(*i);
		delete(*i);
	}

	order->deleted.clear();
	
	delete items;
}

bool SQLManager::deleteOrderItem(OrderItem* item) {
	stringstream ss , ssCondition;
	ss << "delete from order_item where order_id = ";
	ss << item->get_order_id();
	ss << " and ";
	ss << " prod_offer_id = ";
	ss << item->get_offer_id();
	const char* qry = ss.str().c_str();	
	PGresult* result = PQexec( connection, qry);
	if ( ! PQresultStatus(result) == PGRES_COMMAND_OK) {
		cout << "ERROR in deleteOrderItem:" ;
		cout << PQresultErrorMessage(result);
		PQclear(result);
		return false;
	}
	PQclear(result);
	return true;
}	
		

bool SQLManager::storeOrderItem(OrderItem* item) {
	stringstream ss , ssCondition;
	ss << "select order_id from order_item ";
	ss << "where ";
	ssCondition << "order_id = " << item->get_order_id();
	ssCondition << " and prod_offer_id = " << item->get_offer_id() ;

	ss << ssCondition.str();
	const char* qry = ss.str().c_str();	
	PGresult* result = PQexec( connection, qry);
	if ( ! PQresultStatus(result) == PGRES_TUPLES_OK) {
		cout << "ERROR in storeOrderItem:" ;
		cout << PQresultErrorMessage(result);
		PQclear(result);
		return false;
	}
	
	stringstream ss2;
	
	if ( PQntuples(result) == 0) {
		ss2 << "insert into order_item ( order_id,  prod_offer_id, qty ) values (";
		ss2 << item->get_order_id() ;
		ss2 << ", " << item->get_offer_id()  ;
		ss2 << ", " << item->get_qty() << ")";
	
	} else {
		ss2 << "update order_item ";
		ss2 << "set ";
		ss2 << "qty = " << item->get_qty() ;
		ss2 << " where ";
		ss2 << ssCondition.str();
	}

	const char* qry2 = ss2.str().c_str();
	cout << "executing " << qry2 << endl;
	result = PQexec( connection, qry2);
	if ( ! PQresultStatus(result) == PGRES_COMMAND_OK) {
			cout << "ERROR in storeOrderItem:" ;
			cout << PQresultErrorMessage(result);
		       PQclear(result);
		       return false;
	}
	PQclear(result);
  
  storeDiscount(item);

  return true;
}

bool SQLManager::loadOrderItems(Order* order) {
	stringstream ss;
	
	ss << "select  prod_offer_id, qty, ordered_time from order_item where order_id = " << order->get_id();
        
	const char* qry = ss.str().c_str();
	
	PGresult* result = PQexec(connection, qry);
	bool retval = ( PQresultStatus(result) == PGRES_TUPLES_OK );
	if (!retval) {
		cout << "loadOrderItems:" << PQresultErrorMessage(result) << endl;
		return false;
	}
	
	for (int j = 0 ; j < PQntuples(result); ++j) {  
		char * c_offer_id = PQgetvalue(result, j, 0);
		char * c_qty = PQgetvalue(result, j , 1);
		char * c_ordered_time = PQgetvalue(result, j, 2);
		
		OrderItem* item = new OrderItem( order, getProductOffer(atol(c_offer_id)), atoi(c_qty), sql_to_ctime(c_ordered_time)) ;
		order->add_item(item);
	}
	PQclear(result);
	return true;

}
                 
 Order *  SQLManager::findOrder(unsigned long order_id) {
      stringstream ss;
	    ss << "select order_id, order_date,   end_date , paid_date, cust_id from orders ";
      ss << "where order_id = " << order_id;
      PGresult* result = PQexec(connection, ss.str().c_str());
    	if ( PQresultStatus(result) != PGRES_TUPLES_OK) {
    		cout << "SQLManager::findOrder, " << PQresultErrorMessage(result) << endl;
    		return 0;
    	}
      Order* order = 0;
      if(PQntuples(result)!=0 ) {
         order =  tupleToOrder(result,0);
         
         string cust_id_str = string(PQgetvalue(result, 0,4));

         Customer * cust = findCustomerById(cust_id_str);
         order->set_customer(cust);
      }
      PQclear(result);
      return order;
 }

 vector<Order*>* SQLManager::getOrders(Customer* cust) {
	stringstream ss;
	ss << "select order_id, order_date,   end_date , paid_date from orders ";
	ss << " where cust_id = " << cust->get_id() ;
	PGresult* result = PQexec(connection, ss.str().c_str());
	if ( PQresultStatus(result) != PGRES_TUPLES_OK) {
		cout << "SQLManager::getOrders, " << PQresultErrorMessage(result) << endl;
		return 0;
	}
	vector <Order*> * v = new vector <Order*>();	
	for (int i = 0 ; i < PQntuples(result) ; ++i) {
    Order * o = tupleToOrder(result, i);
    o->set_customer(cust);
   	v->push_back(o);
		
	}

  PQclear(result);

	return v;
}


Order* SQLManager::tupleToOrder( PGresult* result, int i) {

    if (PQntuples(result) <= i) {
       return 0;
    }
    
		Order *order = new Order(
				0,
				atol(PQgetvalue(result, i,0)),
				sql_to_ctime(PQgetvalue(result, i, 1)),
				sql_to_ctime(PQgetvalue(result, i, 2)), // bug here , index should be 2 not 1, else end time will = start time
				sql_to_ctime(PQgetvalue(result, i, 3))
				);

        
        
    if(!loadOrderItems(order) ) {
			cout << "Failed to load items for order "<< *order;
			cout << endl;

		}
    
    loadAllDiscounts(order);
         
    return order;
}


vector<Order*>* SQLManager::getUnPaidOrders(Customer* cust) {
	return getPaidOrders(cust, false);
}

vector<Order*>* SQLManager::getPaidOrders(Customer* cust, bool paid) {
	vector<Order*>* po = getOrders(cust);	
	vector<Order*>* po2 = new vector<Order*>();
	vector<Order*>::iterator i ;
        for ( i = po->begin(); i != po->end(); ++i) {	
		Order *o = *i;
		if (paid == (o->get_paid() > 100) ) {
			po2->push_back(	o);
				
		} else {
			//po->erase(i);
			delete o;
		}
	}
	delete po;
	return po2;
}


vector<Order*> SQLManager::getOrdersWithin(Customer* , time_t start, time_t end) {


}

vector<Order*>* SQLManager::getAllPaidOrders(bool paid) {


}

 const string SQLManager::to_sql_time(const time_t t, const char* format ) {
		struct tm st;
		localtime_r( &t, &st);
		char buf[40];
		strftime( buf, 40, format, &st);
		return string(buf);
	}

   time_t SQLManager::sql_to_ctime(const char* c_time) {
		struct tm st;
		//cout << "TIME CONVERSION " << c_time ;
		strptime( c_time, "%C%y-%m-%d %H:%M:%S", &st);
		//cout << " mktime = "<< mktime(&st);
		return mktime(&st);
	}

  bool SQLManager::rememberOrder(Order* order)
  {
    if (order == 0) return false;
    Order* copy = new Order(*order);
    if (this->orderMap.find(copy->get_id()) != orderMap.end() ) {
      Order* old = orderMap[copy->get_id()];
      orderMap.erase(orderMap.find(copy->get_id()));
      delete old;
    }
      
    orderMap[copy->get_id()]= copy;
    return true;
  }
  
  bool SQLManager::restoreOrder(unsigned long order_id)
	{
    if (orderMap.find(order_id) != orderMap.end() ) {
      storeOrder( orderMap[order_id]);
    }
    return true;                      
  }
  
Discount*  SQLManager::load_discount(unsigned long order_id, unsigned long offer_id)
{
    stringstream ss0;
    ss0 << "order_id =" << order_id ;
    if (offer_id == 0)
        ss0 << " and prod_offer_id is NULL ";
       else
        ss0 << " and prod_offer_id= " <<  offer_id;
    string typeClause = ss0.str();
    stringstream ss;
    ss << "select discount_id, percent, amount, discount_type from discount where " << typeClause;
    ss << " and discount_id = ( select max(discount_id) from discount where " << typeClause;
    ss << " )";
    const char* cs = ss.str().c_str();

    PGresult*  result = PQexec( connection, cs);
    Discount * discount = 0;
    do {
       if ( PQresultStatus(result) != PGRES_TUPLES_OK) {
         clog << PQresultErrorMessage(result) << endl;
         discount = NullDiscount::new_instance();
         break;
       }

       if (PQntuples(result) != 1) {
        // clog << "ERROR: Got back " << PQntuples(result) << " for " << cs << endl;
        // clog << "expected 1 result " << endl;
         discount = NullDiscount::new_instance();
         break;
       }

       unsigned long id = atol(PQgetvalue(result, 0, 0));
       string disc_type( PQgetvalue(result, 0, 3));

       discount =  DiscountMap::instance()->create_discount(disc_type, result);
       if (discount == 0) {
         discount = NullDiscount::new_instance();
         break;
       }
       discount->set_id(id);

    } while (0);
    
    PQclear(result);
    return discount;   
}    

Discount* DiscountMap::create_discount(const string& the_type, PGresult* values ) 
{
  if (theMap.find(the_type) == theMap.end()) {
      clog << "discountMap does not have type " << the_type << endl;
      return 0;
  }
  DiscountFactory* factory =  theMap[the_type];
  return factory->create_discount(values);
  
}

void  DiscountMap::register_discount(const string& the_type , DiscountFactory* factory)
{
   theMap[the_type] = factory;
}

  
Discount*  DiscountFactory::create_discount( PGresult* result) 
{
    Discount* discount = create_discount();
    if (!set_value(result, discount)) {
      return 0;
    }
    return discount;
}
  
bool  AmountDiscountFactory::set_value(PGresult* result, Discount* d) 
 {
   string id( PQgetvalue(result, 0, 2) );
  
  Money * money = SQLManager::instance()->findMoney(id);
  AmountDiscount * amtDiscount = (AmountDiscount*) d;
  amtDiscount->set_amt(money);
  return money != 0;  

}

bool PercentDiscountFactory:: set_value(PGresult* result, Discount* discount) 
{

    string dstr(PQgetvalue(result, 0, 1));

    discount->from_string(dstr);
    return dstr!="";
}

DiscountMap* DiscountMap::instance() {
  if (singleton == 0) {
    singleton = new DiscountMap();
    AmountDiscount ad;
    PercentDiscount cd;
    singleton->register_discount(string(ad.get_type()), new AmountDiscountFactory() );
     singleton->register_discount(string(cd.get_type()), new PercentDiscountFactory() );
   
  }
  return singleton;
}


bool SQLManager::storeDiscount(OrderItem* item ) {
    stringstream ss;
    ss         << item->get_order_id() ;
    ss << ", " << item->get_offer_id() ;
    //const char *cs = ss.str().c_str();
     return storeDiscountImpl(item, ss.str());

  }             

  bool SQLManager::storeDiscount(Order* order) {
    stringstream ss;
    ss         << order->get_id() ;
    ss << ", " << "NULL" ;
   return storeDiscountImpl(order, ss.str());


  }
bool SQLManager::storeDiscountImpl(Discountable* item, const string& typeClause) {
    Discount * d = item->get_discount();
    string type = d->get_type();
    bool is_amount  =   type == "amount";
    bool is_percent  =   type == "percent";
    bool is_null = type == "null";
    if (is_null)
      return true;
    
    PGresult* result = PQexec( connection, "select nextval('discount_id_seq')");
		bool ok = PQresultStatus(result) == PGRES_TUPLES_OK && PQntuples(result);
    if (!ok) {
      PQclear(result);
      clog << "failed to get nextval discount_id " << endl;
      return ok;
    }
    
    unsigned long id = atol( PQgetvalue(result, 0, 0) );
		PQclear(result);

    stringstream ss;
    ss << "insert into discount(discount_id, order_id, prod_offer_id, ";
    ss << " discount_type , percent,  amount";
    ss << " ) values ( ";
    ss << id ;
    ss << ", " << typeClause;
    
    ss << ", '" << type << "'";
    double percent = 0;
    if (is_percent) {
        PercentDiscount* pd = (PercentDiscount*) d;
        percent = pd->get_percent();
    }
    ss << ", " << percent;
    if (is_amount) {
        AmountDiscount * amtDiscount = (AmountDiscount*) item->get_discount();
        if(!this->storeMoney( amtDiscount->get_amt() ) ) {
          clog << "FAILED to store money for AmountDiscount in storeDiscount(OrderItem*)";
          clog << endl;
          return false;
        }
        
        ss << ", " <<   amtDiscount->get_amt()->get_id();
    }  else {
        ss << ", NULL";
    }
    ss << ")";
    
    if (!executeCommand(ss))
        return false;
    item->get_discount()->set_id(id);
    return true;  
  }          

  
  
  bool SQLManager::loadDiscount(OrderItem* item) {
    Discount * disc = load_discount(item->get_order_id(), item->get_offer_id());
    item->set_discount(disc);
    return disc != 0;
  }

  bool SQLManager::loadDiscount(Order* item) {
    Discount * disc =  load_discount(item->get_id(), 0);
    item->set_discount(disc);
    return disc != 0;
  }
  
   bool SQLManager::loadAllDiscounts(Order * order) {
      bool ok = true;
      if(!loadDiscount(order))
          ok = false;
      vector<OrderItem*>* items =  order->get_items();
      //  order->get_items() : this is a copy everytime it is called
      // so don't use it in the loop as i != order->get_items()->end()
      // otherwise the loop will seg fault because the items->end() belongs
      // to a different items at each call.
      vector<OrderItem*>::const_iterator i = items->begin();
      vector<OrderItem*>::const_iterator end = items->end();
      for (; i != end; ++i) {

            OrderItem* item = *i;
            bool okItem = loadDiscount(item);
            if (!okItem)
              ok = false;    

      }
      return ok;
   }   
DiscountMap*  DiscountMap::singleton= 0;


bool SQLManager::mergeProducts( ulong idkeep, ulong idmerged) {

  // first step, switch all product offers pointing to product2.
  // then delete product2.

  stringstream ss;
  ss << "update product_offer set product_id = " << idkeep ;
  ss << " where product_id=" << idmerged;
  if (!executeCommand(ss))
     return false;
     
  stringstream ss2;

  ss2 << "delete from product where product_id = " << idmerged;
  return executeCommand(ss2);
  
}


bool SQLManager::mergeCustomers( ulong idkeep, ulong idmerged)   {
  stringstream ss;
  ss << "update orders set cust_id = " << idkeep << " where cust_id = "<<idmerged;
 if (!executeCommand(ss))
  return false;
  
  stringstream ss2;
  ss2 << "delete from customer where cust_id = " << idmerged;
  return executeCommand(ss2);


}

bool SQLManager::executeCommand(stringstream& ss) {
     const char* cmd1 = ss.str().c_str();

  PGresult* result = PQexec( connection, cmd1);
  if (PQresultStatus(result) != PGRES_COMMAND_OK) {
    clog << PQresultErrorMessage(result);
    PQclear(result);
    return false;
  }
  PQclear(result);
  return true;

}

Del* Del::singleton = 0;



  void Del::clear(vector<Customer*>*) {}

  void Del::clear(Customer*) {}

  void Del::clear(vector<Product*>*) {}

  void Del::clear(Product*){}

  void Del::clear(vector<ProductOffer*>*) {}

  void Del::clear(ProductOffer*){}
   void Del::clear(Order*){}
  void Del::clear(vector<Order*>*){}
  void clear(Discount*);
  