
#ifndef APPLICATION1_H
#define APPLICATION1_H



#include <iostream>
#include <sstream>
#include "Containers.h"

class TypedOrders;     /** used in   app1:show_orders_by_customer_template()    */

class app1 {
	private:
		ostream& os;
		istream& is;
		ostream* reports;
		string moneyType;
	public:
		int main(int, char*[]);

		app1() : os(cout), is(cin), reports(&cout), moneyType(string("au")) {}

		app1( ostream& a_os, istream& _is = cin, ostream * p_reportos = &cout, const string& _moneyType = string("au")):
			os(a_os), is(_is), reports(p_reportos), moneyType(_moneyType) {}
	
		void set_report_stream(ostream& s) {
			reports = &s;
		}
		void create_customer() ;
		void list_all_customers() ;
		void edit_customer();
		int main_menu() ;
		void add_product();
		void change_product();
		void list_products_by_name();
		void create_product_offer();
		void list_price_list() ;
		void display(vector<ProductOffer*>* );	
		void show_price_history() ;
		void create_order( const char* format = "%d/%m/%y %H:%M") ;
		void change_order( ) ;
		void show_unpaid_orders();
		void show_all_unpaid_orders( ); 
		void show_orders_by_customer();
		void show_unpaid_orders_by_customer();
	protected:	
		bool confirm(const string&);
		void show_total(Money*);
		Customer * create_customer_ptr( Customer *old) ;
		Customer * find_customer_by_name() ;
		void add_product_impl(Product* old );
		vector <Product*> * list_products_impl(bool);
		vector <ProductOffer*>* list_price_list_impl() ;
		Product* select_product();
		string input_value( const string& prompt, const string& old_value) ;
		ProductOffer * select_product_offer(); 
		vector<Order*>* show_orders_by_customer_impl();
		vector<Order*>* show_unpaid_orders_by_customer_impl( );
		bool update_order_impl( Order* order) ;
		void add_order_item( Order *order) ;
		void change_order_item(Order* order); 
		void remove_order_item(Order* order) ;
		void change_order_details( Order* ord) ;			
		void show_orders( vector<Order*>* pvo) ;
		unsigned int select_order_item( Order* order);
	private:	
		vector <Order*>* show_orders_by_customer_template( TypedOrders* );
		vector<Order*>* call_get_unpaid_orders(Customer *c);
		vector<Order*>* call_get_orders(Customer *c);
    static int group_total_indent;
};

/** used in   app1:show_orders_by_customer_template() ,
  * to vary which orders by customer.
  */
  
class TypedOrders {
	public:
		virtual vector<Order*>* getOrders(Customer*) = 0;		
};

/** for unpaid orders */
class UnpaidOrders: public TypedOrders {
	public:
		vector<Order*>* getOrders(Customer* cust) {
			return SQLManager::instance()->getUnPaidOrders(cust);
		}
};

/** for paid and unpaid orders */
class AllOrders: public TypedOrders {
	public:
		vector<Order*>* getOrders(Customer* cust) {
			return SQLManager::instance()->getOrders(cust);
		}
};
			
			


#endif
