
#include "Customer.h"
#include <vector>
#include <cstdlib>
#include <string>
#include <iostream>
#include <iomanip>
#include <sstream>

using namespace std;
MoneyMap* MoneyMap::singleton = 0;

const string Money::SQL_TYPE=string("type");
const string Money::SQL_ID=string("money_id");


void AUMoney::from_string(const string& str) {
 	string sdollars, scents;
 	string* pcurrent = &sdollars;
 	string::const_iterator i, j ;
 	string numbers = "0123456789";
 	for (i = str.begin(); i != str.end(); ++i) {
 		const char c = *i;
 		uint pos = numbers.find(c,0);
 		if(pos >= 0 && pos < numbers.size() ) {
 			pcurrent->push_back(c);
 			continue;
 		}
 		if (c  == '.')
 			pcurrent = &scents;
 	}
 	dollars = atoi(sdollars.c_str());
 	if (scents.size() == 1)
 		scents.push_back('0');
 	cents = atoi(scents.c_str());
 }
    
const string AUMoney::get_string() const {
	stringstream ss;
	ss << "$" << dollars << '.' << setw(2) << setfill('0') << cents;
	return ss.str();
}

const string AUMoney::sql_insert() const {
		stringstream ss;
		ss << "insert into money( "<<Money::SQL_TYPE<<", dollars, cents, " << Money::SQL_ID << " )";
		ss << " values (  ";
		ss << "'au'" 	<< ", ";
		ss << dollars 	<< ", ";
		ss << cents 	<< ", " ;
		ss << get_id() ;
		ss << ")";
	//	cout << ss.str() << endl;
		string s = ss.str();
		return s;
}

const string AUMoney::sql_select() const {
	stringstream ss;
	ss << "select dollars , cents, "<< Money::SQL_ID << " from money";
	ss << " where "<< Money::SQL_ID<<" = " << get_id();
	return ss.str();
}

const string AUMoney::sql_update() const {
	stringstream ss;
	ss << "update money set dollars = " << dollars;
	ss << " , cents = " << cents;
	ss << " where "<< Money::SQL_ID << "= " << get_id();
	return ss.str();
}


void AUMoney::multiply(const unsigned int multiple) {
int more_cents = cents * multiple;
	int more_dollars = multiple * dollars;    
	int new_cents = more_cents % 100;
	int dollars_from_cents = more_cents / 100;
	more_dollars += dollars_from_cents;
	dollars = more_dollars;
	cents = new_cents;
}

void AUMoney::multiply( const double multiple) {
    double amt = (double)(dollars * 100 + cents);
    amt *= multiple;
    unsigned int new_dollars = (uint) amt/100;
    uint new_cents = ((uint)amt) % 100;
    dollars = new_dollars;
    cents = new_cents;

}

bool AUMoney::subtract( const Money& m) {
    /* this is a hack . change later */
	  AUMoney* pmoney = (AUMoney*) &m;
	  uint amt = dollars* 100 + cents ;
    uint amt2 = pmoney->dollars * 100 + pmoney->cents;
    uint result = amt - amt2 ;
    if (result < 0 )
        return false;

    dollars =   result / 100  ;
    cents =     result % 100;
    return true;
     
}

void  AUMoney::sum(const Money& money) {
	/* this is a hack . change later */
	AUMoney* pmoney = (AUMoney*) &money;
  uint _cents = dollars * 100 + cents;
  uint _ocents = pmoney->dollars * 100 + pmoney->cents;
  _cents += _ocents;
  dollars = _cents / 100;
  cents = _cents %100;
}


void AUMoney::set_state(const vector<string>& vals) {
 		dollars = atoi( vals[0].c_str() );
 		cents = atoi(vals[1].c_str() );
 		set_id(string(vals[2]));
 	}

bool Order::add_item(OrderItem* item) {
	items.push_back(item);
  return true;
}

Order::~Order() {
 vector<OrderItem*>::iterator i;
 for (i = items.begin(); i != items.end() ; ++i) {
	 delete *i;
 }
}



OrderItem* Order::find_item(Product* p)  {
    	return *find_item_impl(p);
}
					    
OrderItem* Order::remove_item(Product* p)  {
    	OrderItem* item = *find_item_impl(p); //save the pointer

    	if (item == NULL)
    		return item;
    	deleted.push_back(item);
    	items.erase(find_item_impl(p)); //erases the pointer from the vector
    	return item; // return the pointer to the OrderItem
}

bool Order::remove_item(unsigned int n) {
	if ( n < 0 || n >= items.size() )
		return false;
	deleted.push_back(items[n]);
	items.erase(items.begin() + n);
	return true;
}


OrderItem* Order::get_item(uint n) {
	if (n >= 0 && n < items.size())
		return items[n];
  return 0;  
}

vector<OrderItem*>::iterator Order::find_item_impl(Product *p) {
  if (p == 0) return items.end();	
	vector<OrderItem*>::iterator i;
	OrderItem* item= NULL;
  for (i = items.begin(); i != items.end(); ++i) {
 		item = *i;
 		if ( item->get_product()->get_pid() == p->get_pid() ) {
     		break;
    }
	}	
	return i;

}


vector<OrderItem*>*  Order::get_items( ) const 
{ 
	vector<OrderItem*>* v = new vector<OrderItem*>(items);
	return v;

}


AUMoney operator+(const AUMoney& m1, const AUMoney& m2)  {
	AUMoney m(0,0);
	m.sum(m1);
	m.sum(m2);
	return m;
	
}

AUMoney& AUMoney::operator +=(const AUMoney& m) {
	this->sum(m);	
	return *this;
}

ProductOffer::~ProductOffer()
{
  delete price;
  delete get_product();
}


/** get_total implementation: the money object passed in is used as a prototype
to get more money objects of the same type. These objects are used
in OrderItem.get_subtotal(money) and added to the original money object.
The total is then returned in the original money object.
*/
Money& Order::get_raw_total(Money& m) const {
  
	vector<OrderItem*>* pitems;
	pitems = this->get_items();
	for (vector<OrderItem*>::iterator  p=pitems->begin(); p != pitems->end(); ++p) {
		
		OrderItem* item = *p;
		Money* m2 = m.clone();
		m += item->get_subtotal(*m2); 
		delete m2;
	}

	delete pitems;
  return m;
}

Money& Order::get_total(Money& m) const {
  Discount* d = get_discount();
  clog << "Applying order discount of type " ;
  clog <<  d->get_type() <<":"<<d->get_string() << endl;
	return d->apply(get_raw_total(m) );
                                          
}

 /** subtotal implementation:
    a pre-constructed money object is passed in. It is expected
    to have a zero value. The money object is loaded with this objects'
   unit price, and multiplied by the quantity of units, and then returned.
   The money object should return with the subtotal value.
   */
   
Money& OrderItem::get_raw_subtotal(Money& m) const {
			m.sum( item->get_price());
			m.multiply(qty);
      return m;

}

Money& OrderItem::get_subtotal(Money& m) const {
     return  get_discount()->apply(get_raw_subtotal(m));
} 


OrderItem::~OrderItem() {
  delete item;

}
Customer::Customer(const string& _id,  const string& _f, const string& _l, const string& _a, const string& _p)
:
id(_id), 
firstname(_f), 
lastname(_l), 
address(_a), 
phone(_p) {} 

Customer::Customer (const char* cid,  const char * cf, const char *cl, const char *ca, const char * cp) 
	: 
	id(string(cid)), 
	firstname(string(cf)), 
	lastname(string(cl)), 
	address(string(ca)), phone(string(cp)) {}
									

Customer*  Customer::testCustomer() {
	Customer*  c = new Customer("", "John", "Smith", "22 Test Rd, TestVille", "1111-2222");
	return c;
}


void Customer::test1() {
	Customer* c = testCustomer();
	cout << *c << endl;
	delete c;
	
}
	

vector<Product*>* Product::testProducts1() {
	vector<Product*>* pv = new vector<Product*>();
	pv->push_back(new Product( "oatmeal facewash", "of1", "a pleasant wash"));
			
	pv->push_back(new Product("rainforest lipstick", "rl1", "refreshingly glossy"));
	return pv;
}

vector <Money*>* Product::testProductPrices1() {
	vector<Money*>* pv = new vector<Money*>();
	Money* m = new AUMoney(10, 20);
	pv->push_back( m );
	m = new AUMoney(15, 75);
	pv->push_back( m);
	return pv;
	
}


/** generates test product offers from test products and test product prices*/
vector <ProductOffer*>*  ProductOffer::testProductOffers1(
		const vector<Product*>* products, 
		const vector<Money* >* prices) {
	vector<ProductOffer*>* pv = new vector<ProductOffer*>(); 
	
	vector<Product*>::const_iterator iproduct;
	vector<Money *>::const_iterator iprice;

	for ( iproduct = products->begin(), iprice = prices->begin(); 
		iproduct != products->end() && iprice != prices->end() ;
	       	++iproduct, ++iprice) {
		
		pv->push_back(new ProductOffer(*iproduct, *iprice) );
		
	}
	return pv;	
	
	
}
/** generates test product offers from test products and test product prices.
 * responsible for the parameters to testProductOffers1
 */
vector <ProductOffer*>*  ProductOffer::testProductOffers2() {
	vector<Product*>*  pvp = Product::testProducts1();
	vector<Money*>* pvm = Product::testProductPrices1();
	vector<ProductOffer*>* pvecOffers =  testProductOffers1(pvp, pvm);
	delete pvm;
	delete pvp;
        return pvecOffers;	
}

/** creates test product offers and generates a test order from the order items
 * linking to the product offers. 
 */
Order* Order::testOrder1() {
	Customer* cust = Customer::testCustomer();
	Order* po = new Order(cust, time(NULL));
	vector<ProductOffer*>* poffers = ProductOffer::testProductOffers2();
	for( vector<ProductOffer*>::iterator offerIterator = poffers->begin();
		offerIterator != poffers->end();
		++offerIterator
	   ) {

		OrderItem* item = new OrderItem(po, *offerIterator, random() % 100, time(NULL));  
		po->add_item(item);	
	}

	delete poffers;

	return po;
}

/** default printing output of product offer.
 * shows code , product name, and offer pirce.
 */
ostream& operator <<(ostream& os,const ProductOffer& po) {
	
	os << po.get_code() << "\t" ;
	os << po.get_product_name();
	os << "\tfrom " << Order::get_formatted_time(po.get_time());
	if (po.get_end() > 1000) 
		os << " to " << Order::get_formatted_time(po.get_end());
        os << "\t" << po.get_price().get_string() ;
	return os;

}	
/** default printing output of AUMoney.
 * shows $dollars.cents 
 */
ostream& operator <<( ostream& os, const AUMoney& m) {
	os << "$" << m.get_dollars() << "." <<  setw(2) << setfill('0') << m.get_cents() ;
	return os;
}

/** default printing output of Customer.
 * shows firstname, lastname, address, phone. 
 */
ostream& operator << ( ostream& os, const Customer& cu) {
	os << cu.get_firstname() << " " << cu.get_lastname() << ", " << cu.get_address() << ", tel." << cu.get_phone();
	return os;
}

/** default printing output of OrderItem. 
 * shows qty, product name, price , subtotal .
 */
ostream& operator << ( ostream& os, const OrderItem& orderItem) {
        stringstream ss;
	      ss <<  orderItem.get_qty() << " x ";
        ss << orderItem.get_product()->get_name();
        ss	<< " @ ";
        ss << orderItem.get_price().get_string();
        os <<  setw(40) << setfill(' ') << ss.str();
        string discount = orderItem.get_discount()->get_string();
        discount = discount != "" ? " less " + discount : discount;
        os << setw(10) << setfill('.') << discount;

        AUMoney m(0,0);
	      os << setw(10) << setfill('.') << " =  " << orderItem.get_subtotal(m).get_string();
	return os;
	
}

/** default printing output of Order. shows customer name, init date of order, 
 * total of the order, and each order item.
 */
ostream& operator <<( ostream& os, const Order& order) {
	//char buffer[200];
	time_t  pt =  order.get_time();
	Customer * c = order.get_customer();
	os <<  c->get_firstname() << ' '<< c->get_lastname()  ;
  os << " on " << Order::get_formatted_time(pt) ;
	if (order.get_completed() > 100)
		os << endl << ", completed on " << Order::get_formatted_time(order.get_completed());
	if (order.get_paid() > 100) 
		os << ", paid on " << Order::get_formatted_time(order.get_paid());
	
	
	os << endl;
	
	vector<OrderItem*>::const_iterator oi ;	
	int j = 0;	
	for ( oi = order.items.begin() ; oi != order.items.end(); ++oi) {
		OrderItem* pitem = *oi;
	//	if (order.itemize) {
			os << ++j << " : ";
	//	}
		os << *pitem;
		os << endl;
	}
  
	     Money* pm = MoneyMap::instance()->cloneDefault();
     
        //os << setw(30) << setfill('=') << "";
      os << endl << setw(50) << setfill(' ') << "original total: " ;
      os << order.get_raw_total(*pm).get_string() << endl ;
      os << setw(30) << setfill('.') << " ";
      if (order.get_discount()->get_type() != "null")
        os << " less " << order.get_discount()->get_string() << endl;
      delete pm;
      pm =  MoneyMap::instance()->cloneDefault();
      
      os << endl << setw(50) << setfill(' ') << "    total  " ;
      os << order.get_total(*pm).get_string() << endl;
      os << setw(30) << setfill('=') << "" << endl;
	    delete pm;
	return os;
}

/** default printing of product. name, code, description.
 */
ostream & operator <<( ostream & os, const Product& p) {
	os << p.name << "\t" << "code:" << p.code << "\t" << p.description ;
	return os;
}


string Order::get_formatted_time(const time_t t, const char* format ) {
	static struct tm timetm;
  if (t < 100)
    return string("");
	localtime_r(&t, &timetm);
	char buf[100];
	strftime(buf, 100,  format , &timetm);
	return string(buf);
}

time_t Order::get_time(const string& s, const char* format ) {

	struct tm timetm;
	bzero( &timetm, sizeof(timetm)); 


	string s2 = s;
	for (unsigned int i = 0; i < s2.size() ; ++i) {
		if (s2[i] == '-') s2[i] = '/';
	}

	strptime( s2.c_str(), format, &timetm);
	

       	static const char * formats[] = { "%d/%m/%y %H:%M", "%d/%m/%y", "%d/%m/%Y", "" };
	for ( const char ** form = formats; strlen(*form) > 0; ++form) {

	}
		
	cout << "strptime did " << timetm.tm_year << " "<< timetm.tm_mon << " " << timetm.tm_mday <<   "hour " << timetm.tm_hour << ":" << timetm.tm_min << endl;
	time_t t= mktime(&timetm);	
	cout << "The integer time is " << t;
	cout << endl;
	return t;
}

  
Money* Order::get_total_of_orders(vector<Order*>* pvo, const string& moneyType) {
	Money* m = MoneyMap::instance()->clone(moneyType);
  if (m == 0 ) {
		cout << "UNABLE TO FIND MONEY CLASS FOR " << moneyType << endl;
  }
  
  return   Order::get_total_of_orders(pvo, m);
}

Money* Order::get_total_of_orders(vector<Order*>* pvo, Money* m) {
  if (m == 0) {
    m = MoneyMap::instance()->cloneDefault();
		if (m == 0) {
			cout << endl << "UNABLE TO GET DEFAULT MONEY TYPE" << endl;
			cout << endl << "TOTAL will not be shown." << endl;
      return 0;
    }
	}
  
  vector<Order*>::const_iterator i, end;
  i = pvo->begin();
  end = pvo->end();
  for ( ;i != end; ++i) {
		Order* order = *i;
		if (m!= 0) {
			Money * prototype = m->clone();
			m->sum(order->get_total(*prototype));
			delete prototype;
		}
	}
	return m;
}

NullDiscount* NullDiscount::singleton  = 0;

string   NullDiscount::get_string() const {
  return "";
}
string   AmountDiscount::get_string() const {
  stringstream ss;
  ss <<  amt->get_string();
  return ss.str();
}
 string   PercentDiscount::get_string() const {
  stringstream ss;
  ss << percent << "%";
  return ss.str();
}

Money& AmountDiscount::apply(Money& m) const {
            m.subtract(*amt);
            return m;
}

AmountDiscount::~AmountDiscount() { delete amt ; }

Money& PercentDiscount::apply(Money& m) const
{
    m.multiply((double)(100-percent)/100.);
    return m;

}

//const string AmountDiscount::the_type = "amount";
//const string PercentageDiscount::the_type = "percentage";
//const string NullDiscount::the_type = "null";
AmountDiscount::AmountDiscount(): amt(MoneyMap::instance()->cloneDefault()) {}  
void AmountDiscount::from_string(const string & str ) {
    amt = MoneyMap::instance()->cloneDefault();
    amt->from_string(str);
    
 }

void PercentDiscount::from_string(const string & str ) {
    stringstream ss(str);
    ss >> percent;
}




void NullDiscount::from_string(const string & s) {}


