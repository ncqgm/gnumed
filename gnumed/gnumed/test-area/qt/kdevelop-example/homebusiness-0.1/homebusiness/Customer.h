
#ifndef CUSTOMER_H

// this makes sure the contents of the include file is included once.

// after this, if this file is included in the same scope, the above
// conditional will skip the lines up to #endif
#define CUSTOMER_H


// need this for the definition of the string class
#include <string>
#include <vector>
#include <ctime>
#include <iostream>
#include <map>
// need this to use the string class type as string and not std::string
// this means that a search is done inside the namespace std:: for any
// types.
using namespace std;


class SQLManager;
/** This class stores the data for Customers */
class Customer  {
	friend class SQLManager;
	private:
    string id;

    string firstname;
		string lastname;
		string address;
		string phone;
	
	protected:
		void setId(const string& _id) {
			id = _id;
		}	


	public:
		Customer() {}

		Customer( const string& _id, const string& _f, const string& _l, const string& _a, const string& _p);
		
		
		Customer ( const char* cid, const char * cf, const char *cl, 
				const char *ca, const char * cp) ;

	    const string& get_id() const { return id; }

    const string& get_firstname() const { return firstname; }

   const string& get_lastname() const { return lastname; }
		
		const string& get_address() const { return address; }
		
		const string& get_phone()  const { return phone; }
		
		void set_address(const string & a) { 			address = a; 		}

    void set_lastname(const string& l) {			lastname = l; 		}

		void set_firstname(const string& f) {			firstname = f; 		}

		void set_phone( const string & p) { 			phone = p;  		}

		void copy(const Customer* pcust) {
 			firstname= pcust->firstname;
			lastname = pcust->lastname;
			address= pcust->address;
			phone = pcust->phone;
			id = pcust->id;
		}

    Customer(const Customer& other)  {
      copy(&other);
    }

    friend ostream& operator <<( ostream& os, const Customer& cu);
		static void test1();
		static Customer* testCustomer();
};

class Money;
class Discount {
      unsigned long id;
      public:
          virtual Money& apply(  Money&) const = 0;

          virtual  string  get_string() const = 0;

          virtual void from_string(const string&) = 0;

          virtual const string get_type() const =0;
          
// creates a discount of the same type
          virtual Discount* clone()  const = 0;
 // id getter/setter
          unsigned long get_id() const { return id; }

          void set_id(unsigned long _id) { id = _id; }
          virtual ~Discount() {}
};


class PercentDiscount:public Discount {
    private:
        double percent;
        static const string percentType;
    public:

            PercentDiscount() : percent(0.0) {}

            PercentDiscount( double percentage):
              percent(percentage) {}

            virtual Money& apply(Money& m) const;

            virtual ~PercentDiscount() {}

            string  get_string() const ;

            virtual void from_string(const string & ) ;

            double get_percent() const {
              return percent;
            }
            const string  get_type() const { return "percent"; }

            virtual Discount* clone() const { return new PercentDiscount() ; }
};

class AmountDiscount: public Discount {
      Money* amt;

      static const string amountType;

      public :

          AmountDiscount(); 

          AmountDiscount(Money* _amt) : amt(_amt) {}

          virtual  ~AmountDiscount();

          virtual Money& apply(Money& m) const;

          string  get_string() const ;

          virtual void from_string(const string &) ;

          virtual Discount* clone() const { return new AmountDiscount() ; }

          const string  get_type() const { return "amount"; }

          Money* get_amt() { return amt; }

          void set_amt(Money* m) { amt= m; }
};          


class NullDiscount : public Discount {
    static NullDiscount* singleton;
    protected:
      NullDiscount() {}
    public:
      static NullDiscount* instance() { if (singleton==0)
                                              singleton = new NullDiscount();
                                        return singleton;
                                      }
      static NullDiscount* new_instance() {
                                               return new NullDiscount();
                                          }                                
      Money& apply(  Money& m) const { return m; }
      string  get_string() const ;
      void from_string(const string&) ;
      virtual Discount* clone() const { return new NullDiscount() ; }
      const string   get_type()const{ return "null"; }
};
    
class Discountable {
    private:
      mutable Discount * discount;
    public:
      Discountable() : discount(NullDiscount::new_instance()) {} 
      virtual void set_discount( Discount*d) {discount = d;}
      virtual Discount* get_discount() const  { return discount; }
      virtual ~Discountable() { if (discount != 0) delete discount; }
              
};

class OrderItem;
class Money;
class MoneyMap;
class Product;
/** This class stores the data for orders */
class Order : public Discountable {
	friend class SQLManager;
	private:
		//order has a pointer to it's owning Customer
	  Customer* owner;
		// using a time_t for order_time because will be using the
		// standard c time functions that work on time_t.
 		 unsigned long order_id;
   time_t order_time ;
   
		
		time_t when_completed ;
		time_t paid_date ;
		bool itemize ;

	vector<OrderItem*> items;
	vector<OrderItem*> deleted;
	protected:
		vector<OrderItem*>::iterator find_item_impl(Product* p) ;
    
		void set_id(unsigned long _id) { order_id = _id; }

    void set_customer(Customer* c) {  owner = c;  }

  public:
    Order(const Order& other) : Discountable(), order_id(other.order_id),
    order_time(other.order_time), when_completed(other.when_completed),
    paid_date(other.paid_date) , itemize(other.itemize),
    owner(other.owner), items(other.items), deleted(other.deleted) {}

		
		// the constructor requires all the details
		Order () :
			owner(0), order_time(time(NULL)), order_id(0), when_completed(0), paid_date(0) , itemize(false) {}
		Order ( Customer* _owner, time_t t):
			owner(_owner), order_time(t), order_id(0), when_completed(0), paid_date(0) , itemize(false){}
    
		Order ( Customer* _owner, unsigned long id, time_t start, time_t end =0, time_t paid=0) :
			owner(_owner), order_id(id), order_time(start), when_completed(end) , paid_date(paid), itemize(false) {}
		~Order() ;
    Customer* get_customer() const { return owner; }

		const time_t get_time() const{ return order_time; }

		void set_time(time_t t) {	order_time = t; }

		void set_completed(const time_t t) {	when_completed = t;		}

		const time_t get_completed() const {  return when_completed;	}
                                           
		void set_paid(const time_t t) {	paid_date = t; }

		const time_t get_paid() const {	return paid_date;	}

		Money& get_total(Money&) const ;

    Money& get_raw_total(Money&) const ;
    
		unsigned long get_id() const {	return order_id;	}



		bool add_item(OrderItem* item);

		OrderItem* remove_item(Product* p);

		bool remove_item(unsigned int n) ;

		OrderItem* get_item(uint n) ;

		OrderItem* find_item(Product* p) ;

    
    
		unsigned int size() const { return items.size(); }

		vector<OrderItem*>*  get_items() const ;

		void set_itemize(bool _itemize) {	itemize = _itemize;	}


		static Order* testOrder1() ;

		friend ostream& operator <<( ostream& os, const Order& order);
		static string get_formatted_time(const time_t t, const char* format = "%d/%m/%C%y %H:%M");

		static time_t get_time(const string& , const char* format = "%d/%m/%y %H:%M");
		static Money* get_total_of_orders(vector<Order*>* pvo, const string& moneyType) ;
    static Money* get_total_of_orders(vector<Order*>* pvo, Money* m);

    
    
};
// don't forget the ending semi-colon, as this is a class or type
// definition


/** This class stores the data for products*/
class Product {
	friend class SQLManager;
	friend ostream & operator <<( ostream&, const Product&);
	private:
		string name;
		string code;
		string description;
		vector <string> old_codes;
		unsigned long id;
	protected:
	public:

		Product(  const string& _name, const string& _code, const string& _description):
		name(_name), code(_code), description(_description), id(0) {}


		Product(  const char* _name, const char* _code, const char* _description):
		 name(_name), code(_code), description(_description) , id(0) {}

		const string& get_code() const { return code; }

    const string& get_name() const { return name; }

		const string& get_description() const { return description; }

		void set_description(const string& _description) {
			description = _description;
		}

		void set_name(const string& _name) {
			name= _name;
		}

		void set_code(const string& _code) {
			if (code == _code)
				return;
			old_codes.push_back(code);
			code= _code;
		}

		void set_pid( unsigned long _id) {
			id = _id;
		}

		unsigned long get_pid() const {
			return id;
		}

    
		void copy(Product* p) {
			name = p->name;
			code = p->code;
			description=p->description;
		}
		// unit test methods
		//

	       // a test vector of products
		static vector<Product*>* testProducts1();
		static vector<Money*>* testProductPrices1();

};



class Money {
	friend class SQLManager;
	private:
		string id;
	protected:
	static 	const string SQL_TYPE;
	static 	const string SQL_ID;
	public:
		Money() : id ("") {}
		virtual const string get_string() const = 0;
		virtual void  multiply(unsigned int m) = 0;
    virtual void  multiply(double m) = 0;
		virtual bool  subtract(const Money& ) = 0;
    virtual void sum(const Money& m) = 0;
		virtual Money* clone() = 0;
		virtual void from_string(const string& str) = 0;

		virtual const string sql_insert() const = 0;
		virtual const string sql_update() const = 0;
		virtual const string sql_select() const = 0;
    virtual const string sequencer_name() const = 0;

    
    /** loads the money's data from a ordered list of strings */
		virtual void set_state(const vector<string>& vals) = 0;

		
		virtual void set_id(const string& _id) { id = _id ; }
		virtual const string& get_id() const { return id; }

		Money& operator += ( const Money& m) {
			sum(m);
			return *this;
		}

  /** No descriptions */
  virtual  ~Money() {}
};


class AUMoney :public Money {


	private:
		unsigned int dollars, cents;

	public:
		Money* clone() { return new AUMoney(0,0); }

		AUMoney& operator +=( const AUMoney& m);
		friend AUMoney operator +(const AUMoney&, const AUMoney&);
		friend ostream& operator <<( ostream& os, const AUMoney&);
		AUMoney(unsigned int _dollar, unsigned int _cents) : Money(),
				dollars(_dollar), cents(_cents) {}

		unsigned int get_dollars() const { return dollars; }
		unsigned int get_cents() const { return cents; }

		void from_string(const string& str) ;

		const string get_string() const ;
    
		void  multiply(unsigned int m) ;
    void  multiply( double m);
		void sum(const Money& m) ;
    bool  subtract(const Money& ) ;
		void set_state(const vector<string>& vals);
		
		const string sql_insert() const;
		const string sql_select() const ;
		const string sql_update() const ;


		const string sequencer_name() const { return string("au_money_seq");  }

    virtual ~AUMoney() {}

};


class MoneyMap {
	private:
		map<string, Money*> moneyNames;
		static MoneyMap* singleton;
		string defaultType;
	protected:
		MoneyMap() :defaultType("au") {
			moneyNames["au"] = new AUMoney(0,0);
		}

	public:
		static MoneyMap* instance() {
			if (singleton ==0) singleton = new MoneyMap();
			return singleton;
		}


		Money* clone(const string& atype) {
			if ( moneyNames.find(atype) != moneyNames.end() ) {
				Money * prototype = moneyNames[atype];
				return prototype->clone();
			}
			return 0;
		}

		bool setDefaultType(const string& atype) {
			if ( moneyNames.find(atype) != moneyNames.end() ) {
				defaultType = atype;
				return true;
			}
			return false;
		}

		const string& getDefaultType() const {
			return defaultType;
		}

		Money* cloneDefault() {
			return clone(defaultType);
		}



};
 /**
 * productOffer will delete it's own price.
 */
class ProductOffer {
	friend class SQLManager;
	friend ostream&  operator <<(ostream& os, const ProductOffer&);
	private:
		Product* product;
		Money* price; // do note delete the passed in money pointer.
		time_t the_time, end_time;
		unsigned long id;

	protected:
	public :

		ProductOffer( Product* _p,  Money* unit_price, time_t t, time_t end_t = 0, unsigned long offer_id =0 ):
			product(_p), price(unit_price), the_time(t), end_time(end_t)  , id(offer_id) {}
		ProductOffer( Product* _p,  Money* unit_price ):
			product(_p), price(unit_price), the_time(time(NULL) ) , end_time(0) , id(0) {}
		~ProductOffer() ;  

		const Money&  get_price() const { return *price; }
		const Product* get_product() const { return product; }

		const string& get_code() const {
			return product->get_code();
		}

		const string& get_product_name() const {
			return product->get_name();
		}

		unsigned long get_id() const {
			return id;
		}

		void set_end(const time_t ti) {
			end_time = ti;
		}

		time_t get_time() const { return the_time; }
		time_t get_end() const { return end_time; }


		static vector <ProductOffer*>* testProductOffers1(
				const vector<Product*>* products,
				const vector<Money*>* prices
				);
		static vector <ProductOffer*>* testProductOffers2();



};



class OrderItem : public Discountable {

	private:
		Order* order;
		ProductOffer* item;
		unsigned int qty;
		time_t when_added;

	public:
		friend ostream& operator <<( ostream&, const OrderItem& ) ;

		OrderItem( Order* _o, ProductOffer* _po,
				unsigned int _qty, time_t _tm = time(NULL)) :Discountable(),
				order(_o), item(_po),
					qty(_qty), when_added(_tm)	{}
    ~OrderItem() ;
		const time_t get_offer_time() const {
			return item->get_time();
		}

		const time_t get_ordered_time() const { 
			return when_added;
		}

    
		 Money& get_subtotal(Money& m) const ;
    
     Money& get_raw_subtotal(Money& m) const ;
    
		const Product* get_product() const {
				return item->get_product();
			}

		const unsigned long get_offer_id() const {
      /** CHANGE */
        if (item == 0)  {
          cout<< "product offer was 0 " << endl;
          return 0;
        }
				return item->get_id();
		}

		const unsigned long get_order_id() const {
				return order->get_id();
		}

		const Money& get_price() const {
				return item->get_price();
			}

		unsigned int get_qty() const {
				return qty;
		}
		void set_qty(unsigned int n) {
			qty = n;
		}

};








#endif

