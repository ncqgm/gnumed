
#include<iostream>
#include <iomanip>
#include<sstream>
#include "Containers.h"
#include "application1.h"

   
int app1::group_total_indent = 85;
bool app1::confirm(const string& msg) {
	os << msg << " (y/n) ? ";
	string sel;
	static const string YES = "yY";
	getline(is, sel);
	return sel.size() > 0 && YES.find(sel[0]) ;
		

}
int app1::main(int argc, char* argv[]) {

	while(1) {
		switch (main_menu()) {
			case 1:
				create_customer();
				break;
			case 2:
				edit_customer();	
				break;
			case 3 :
				list_all_customers();	
				break;

			case 4: 
				find_customer_by_name();	
				break;
			case 11:
				add_product();
				break;
			case 12:
				change_product();	

			case 13:
				list_products_by_name();	
				break;
			case 21:
				create_product_offer();	
				break;
			
				

			case 23:
				list_price_list();		
				break;

			case 24:
				show_price_history();	
				break;
			case 31:
				create_order();
				break;
			case 32:
				change_order();	
			case 33:
				show_unpaid_orders();	
				break;
			case 34:
				show_orders_by_customer();
				break;
					
			default:
				break;

		}
	}
	return 0;

}
	
int app1::main_menu() {	
	os << "Which command:" << endl;
	os << "1. Create new customer." << endl;
	os << "2. Edit customer" << endl;
	os << "3. list all customers " << endl;
	os << "4. find customers by name " << endl;
	os << "11. add product" << endl;
	os << "12. change product" << endl;
	os << "13. list products by name" << endl;
	os << "21. create product offer" << endl;
	os << "22. set normal product price" << endl;
	os << "23. show price list " << endl;
	os << "24. show product price history" << endl;
	os << "31.create order" << endl;
	os << "32.change order" << endl;
	os << "33.show unpaid orders by customer" << endl;
	os << "34.show all orders by customer" << endl;
	string buf;
	getline(is, buf);	
	
	return atoi(buf.c_str());
}

void app1::edit_customer() {
	Customer * cust = find_customer_by_name();
	if (cust == 0)
		return;
	os << "Editing : " << *cust << endl;
	Customer *newCust = create_customer_ptr(cust);
	if (newCust != 0) {
		SQLManager::instance()->storeCustomer(newCust);
		delete newCust;
	}
}
	

Customer * app1::find_customer_by_name() 
{
	os << "FINDING CUSTOMER BY NAME:" << endl;
	string surname_p, firstname_p, answ;
	os << endl << "enter surname part: ";
	getline(is, surname_p);
	os << endl << "enter firstname part: ";
	getline(is, firstname_p);
	vector<Customer*> *v = SQLManager::instance()->findCustomerByNames(firstname_p, surname_p );

	if (v == 0 || v->size() == 0) {

		os << endl << endl << "***************" << endl;
		os << "No customers found " ;
		os << "for surname containing '"<< surname_p << "'" << endl;
		os << " and first name containing '"<< firstname_p << "' .";
		os << endl;
	       	os << "*****************" << endl << endl;
		return 0;
	}

	int j = 0;
	for (int j = 0 ; j < v->size() ; ++j) {
		os << j+1 << ": " << *(*v)[j] << endl;
	}

	int choice;
	
	if (v->size() == 1) {
		choice = 1; 
	}
	else {
		os << endl << "Select customer  (1-" << v->size() << ", or 0 for none) ? " ;
		getline(is, answ);
		choice = atoi(answ.c_str());
	}

	Customer * chosen = 0;
	
	if (choice > 0 && choice <= v->size() ) 
		chosen = (*v)[choice -1];
      	delete v;

	if (chosen != 0) {
		os << "You chose : " << *chosen << endl;
	}

	return chosen;
}

void app1::list_all_customers() {
	vector<Customer*>* v = SQLManager::instance()->listAllCustomers();
	vector<Customer*>::iterator i;
	os << endl <<  endl;
	int N = 5;
	int j =0;
	string dummy;
	bool nonstop = false;
	if (confirm("List all without stopping ")) {
		nonstop = true;
	}
	for (i = v->begin(); i != v->end(); ++i) {
		os << **i << endl << endl;
		if (++j % N == 0 && !nonstop) {
			os << "Hit enter to see next " << N << " : " << endl;
			getline(is, dummy);
		}
	}

	delete v;	
}



void app1::create_customer() {
	Customer * cust = create_customer_ptr( 0);
	if (cust == 0)
		return ;
	SQLManager::instance()->storeCustomer(cust);
	return;

}

Customer * app1::create_customer_ptr( Customer *oldCustomer) {
	

	string surname(""), firstname(""), address(""), phone(""), id("");
	string new_surname(""), new_firstname(""), new_address(""), new_phone("");
	string answ("n");	
	
	
	if (oldCustomer != 0)  {
		surname = oldCustomer->get_lastname();
		firstname = oldCustomer->get_firstname();
		address = oldCustomer->get_address();
		phone = oldCustomer->get_phone();
		id = oldCustomer->get_id();
	}
	
	while (true) {
	os << endl << "enter surname (current='" << surname <<"' ): ";
	getline(is, new_surname);
	os << endl << "enter firstname (current='"<< firstname <<"'): ";
	getline(is, new_firstname);

	os << endl << "enter address (current='"<<address<<"'): ";
	getline(is, new_address);

	os << endl << "enter phone (current='"<<phone<<"'): ";
	getline(is, new_phone);

 	new_surname = new_surname == ""? surname: new_surname;
 	new_firstname = new_firstname == ""? firstname: new_firstname;
 	new_address = new_address == ""? address: new_address;
 	new_phone = new_phone == ""? phone: new_phone;


	if ( new_surname == "" && new_firstname == "") return 0;

	os << endl<< "You entered " << new_surname << ", " << new_firstname << " at " << new_address << " , tel. " << new_phone << endl;


	os << "Is this correct (Y / N or a to abort) ? ";
	getline(is, answ);
	if (answ.size() > 0 && answ[0] == 'a')
		return 0;

	if (answ.size() > 0 && answ[0] == 'y' || answ[0] == 'Y') {
		Customer * cust = new Customer(id, new_firstname, new_surname, new_address, new_phone) ;
		return cust;
	}

	surname = new_surname;
	firstname = new_firstname;
	address = new_address;
	phone = new_phone;
	}
}

string app1::input_value( const string& prompt, const string& old_value) 
{ 
	string value;
	os << prompt << "(current='" << old_value << "') : ";
	getline(is, value);
	value == "" ? old_value: value;
	return value;
	
}
	

void app1::add_product( ) {
	add_product_impl( 0);
}

void app1::change_product() {
	Product * product = select_product();
	if (product == 0)
		return;
	add_product_impl( product);

}

void app1::add_product_impl( Product* old) {
	
	string old_name, old_description, old_code;
	if (old != 0) {
		old_name = old->get_name();
		old_description = old->get_description();
		old_code = old->get_code();
	}
	
	while(true) {
		string product_name = input_value( "Enter product name", old_name);
		string product_code = input_value( "Enter product code", old_code);
		string product_description = input_value( "Enter product description", old_description);

		os << "Save these values:" ;

		os << endl << "\tname=" << product_name << endl;
		os << endl << "\tcode=" << product_code << endl;
		os << endl << "\tdescription=" << product_description << endl;
		os << "(y/n or a for abort) ? : ";
		string answ;
		getline(is, answ);
		if ( answ.size() > 0 && answ[0] == 'y') {	
			Product * product = 
				new Product( 
					product_name, 
					product_code, 
					product_description
					);
			if (old != 0 && old->get_pid() != 0) {
				product->set_pid(old->get_pid() );
			}
			SQLManager::instance()->storeProduct(product, old);
			return;
		}
		if (answ.size() > 0 && answ[0] == 'a')
			return;
	}

}


void app1::list_products_by_name() {
	delete list_products_impl( true);
}

vector <Product*> * app1::list_products_impl( bool showProducts) {


	string name;
	os << "Enter part of product name: ";
	getline(is, name);
	os << endl << endl;
	
	vector < Product*>*v= SQLManager::instance()->findProductByName( name);
	if (!showProducts)
		return v;

	vector<Product*>::iterator i;
	int j = 1;
	for (i = v->begin(); i != v->end(); ++i, ++j) {
		Product * p = *i;
		os << j << ": " << *p << endl;
	}
	return v;


}

Product* app1::select_product(){
	vector <Product *> * pproducts = list_products_impl( true);
	if (pproducts == 0 || pproducts->size() == 0)
		return 0;
	string sel;
	os << "Enter index number of selected product : " ;
	getline(is, sel);
	int n = atoi(sel.c_str()) -1;
	if ( n < 0 || n >= pproducts->size() )	 {
		os << "No product selected." << endl;
		return 0;
	}

	Product *product = (*pproducts)[n];
	delete pproducts;
	return product;
}

void app1::create_product_offer() {
	os << "CREATE A PRODUCT OFFER" << endl;
	Product* product = select_product();
	if (product ==  0) {
		return;
	}
	vector<Product*> products;
	products.push_back(product);
	vector<ProductOffer*>* poffs= SQLManager::instance()->listLatestProductOffers( &products, true);
	

	os << "Current product offer for " << product->get_name() << endl;
	if ( poffs != 0 && poffs->size() >0) {
		os << *( (*poffs)[0]) << endl;

	} else {
		os << "No product offer current." << endl;
	};	



	os << "Enter new offer price:" ;
	string price_txt;
	getline(is, price_txt);
	Money* m = MoneyMap::instance()->cloneDefault();
	m->from_string(price_txt);

	os << "Enter start date for offer (enter for current): ";
	string str;
	getline(is, str);
	time_t start = str == "" ? time(NULL) : Order::get_time(str);

	os << endl << "Enter end date of offer : ";
	str = "";
	getline(is, str);
	time_t end = str == "" ? 0 :  Order::get_time(str);

	
	os << endl<< "The product offer is ";
	os << endl <<"\t"<<*product ;
	os << endl << "for " << m->get_string() <<endl;

	os << "Accept product offer ? ";
	string answ;
	getline(is, answ);	

	if (answ.size() > 0 && answ[0] == 'y') {
		ProductOffer * p = new ProductOffer( product, m, start, end);
		SQLManager::instance()->storeProductOffer(p);
	}
	if ( poffs != 0 && poffs->size() >0) {
		os << "Previous offer was : ";
		os << *( (*poffs)[0]) << endl;
		os << "End previous product offer permanently when new offer starts?" << endl;
		answ = "";
		getline(is, answ);
		if (answ.size() > 0 && answ[0] == 'y') {
			ProductOffer * old = (*poffs)[0];
			old->set_end(start-60);	
			if (SQLManager::instance()->storeProductOffer(old))
				os << "Old offer has been ended." << end;
		}

	}
}

void app1::list_price_list() {
	vector <ProductOffer*>*poffers =  list_price_list_impl();
	display(poffers);	
	if (poffers != 0) 
		delete poffers;
}


vector<ProductOffer*>* app1::list_price_list_impl() {
	vector<Product*>* products = list_products_impl( false);
	if (products == 0)
		return 0;
	vector<ProductOffer*>* poffers = SQLManager::instance()->listLatestProductOffers( products, true);
	delete products;
	
	return poffers;
}

void app1::display(vector<ProductOffer*>* poffers) {	
	if (poffers == 0 || poffers->size() == 0) {
		os << "No product offers found. ********" << endl;
		return;
	}
	vector<ProductOffer*>::const_iterator poi;
	os << endl << endl << "CURRENT PRODUCT OFFERS" << endl;
	int j = 0;
	for (poi = poffers->begin(); poi != poffers->end(); ++poi) {
		os << ++j << "\t: " << **poi << endl;
	}
	os << endl;
}



void app1::show_price_history()  {
	os << "Enter product code or product name : ";
	string entry;
	getline(is, entry);	
	
	vector<Product*> * vp = 
		SQLManager::instance()->findProductByCodeOrName(entry);
	map < unsigned long, vector<ProductOffer*>* >* poMap = 
		SQLManager::instance()->getProductOfferHistory(vp);

	map < unsigned long, vector<ProductOffer*>* >::const_iterator mi;

	for (mi = poMap->begin() ; mi != poMap->end(); ++mi) {
		const vector <ProductOffer*>* v =  mi->second;
		os << "price history for " << *SQLManager::instance()->findProduct( mi->first) ;
		os << endl;
		vector<ProductOffer*>::const_iterator j;
		for (j = v->begin(); j != v->end() ; ++j) {
			ProductOffer * po = *j;

			os << "\t" << "From " ;
			os << Order::get_formatted_time(po->get_time()) ;

			if ( po->get_end() >100) {
				os << " to " ;
				os << Order::get_formatted_time(po->get_end()) ;			} else {
				os << "\t\t";
			}
				
			os << "\t price=" << po->get_price().get_string() << endl ;
		}
	}
}

void app1::create_order( const char* format) {
	Customer *cust = find_customer_by_name();
	if (cust == 0)
		return;

	Order * order = new Order(cust, time(NULL));
	change_order_details(order);
	while(update_order_impl( order));
}

bool app1::update_order_impl( Order* order) {
	
	os << endl;	
	os << endl;	
	os << "Order is " << *order;
	os << endl;	
	os << "1.Add order item ";
	os << "2.remove order item ";
	os << "3.change order item qty ";
	os << "4.complete order";
	os << endl;
	os << "Select choice (1 - 4):";
	string sel;
	getline(is, sel);

	bool ret = true;
	switch(atoi(sel.c_str())) {
		case 1:
			add_order_item( order);
			break;
		case 2:
			remove_order_item( order);
			break;
		case 3:
			change_order_item( order);
			break;
		case 4:
			if (order->size() ==0 && confirm("Order is empty. Remove empty order?")) {
				SQLManager::instance()->removeOrder(order);				
			}
			
		default:
		       	break;
				
	}
	SQLManager::instance() -> storeOrder(order);
	return ret;
}
	
void app1::add_order_item(  Order *order) {
	ProductOffer * poffer = select_product_offer();
	if (poffer == 0)
		return;
	string sel = "";
	os << "How many items at the above price to order?";
	getline(is, sel);
	int n = atoi(sel.c_str());
	if (n <= 0) {
		os << " ** Invalid quantity selected" << endl;
		return;
	}
	OrderItem* item = new OrderItem(order, poffer, n, time(NULL));
	order->add_item(item);
	os << "Order item added." << endl;
}

unsigned int app1::select_order_item( Order* order) {
	if (order->size() == 0)  {
		os << "No items in order";
		return 0;
	}
	os << endl << endl;
	os << *order << endl;
	os << "Select item number :";
	string sel;
	getline(is, sel);
	int n = atoi(sel.c_str());
	if ( n < 1 || n > order->size())
		return 0;
	return n;
}

void app1::remove_order_item( Order* order) {
	if (order->size() == 0)
		return;
	int n = select_order_item( order);
	order->remove_item(n-1);
}

void app1::change_order_item(Order* order) {
	if (order->size() == 0)
		return;

	int n = select_order_item( order);
	OrderItem* item = order->get_item(n-1);
	if (item == 0)
		return;
	os << "For " << *item << endl;
	os << "Enter New quantity : " ;
	string sel;	
	getline(is, sel);
	int q = atoi(sel.c_str());
	if (q <= 0) 
		return;
	item->set_qty(q);
}


ProductOffer * app1::select_product_offer() {

	vector<ProductOffer*>* vp = list_price_list_impl();
	if (vp == 0 || vp->size() == 0)
		return 0;
	display(vp);
	
	int n = 1;
	while (vp->size() > 1) {
		os << "Enter selection ";
		os << " ( 1 - ";
		os << vp->size() << " : ";
		string sel;
		getline(is, sel);
		n = atoi(sel.c_str());
		if ( n >= 1 && n <= vp->size() ) 
			break;

		os << endl << n << " is a invalid selection." << endl;
		os << "Abort selection (y/n) ? " ;
		getline(is, sel);
		if ( sel.size() > 0 && sel[0] == 'y')
			return 0;

	}
	return (*vp)[n-1];
		
}


void app1::show_unpaid_orders_by_customer() {
	delete show_unpaid_orders_by_customer_impl();
}
void app1::show_orders_by_customer() {
	delete show_orders_by_customer_impl( );
}

void app1::show_total(Money* m) {
	if (m!=0) {
		os << endl;
		os << "*** Total of orders' amount = " ;
		os << m->get_string() << endl;
	}
}


vector<Order*>* app1::show_unpaid_orders_by_customer_impl() {
	return show_orders_by_customer_template( new UnpaidOrders() );
}


vector<Order*>* app1::show_orders_by_customer_impl() {
	return show_orders_by_customer_template(  new AllOrders() );

}

vector<Order*>* app1::show_orders_by_customer_template(  TypedOrders* orderGetter ){
	
	Customer *cust = find_customer_by_name();
	if (cust == 0)
		return 0;
	vector<Order*>* pvo;
        pvo= orderGetter->getOrders(cust);
	delete orderGetter;

	os << endl << endl << endl;
	os << "Number of orders = " ;
	os << pvo->size() ;
	os << " for ";
	os << endl << *cust << endl;
	os << endl;
	show_orders( pvo);
	Money *m = Order::get_total_of_orders(pvo, moneyType);
	show_total( m);
	os << endl << endl;
	os << "Press enter to continue:";
	string sel;
	getline(is, sel);
	os << endl;
	return pvo;

}

void app1::show_orders(  vector<Order*>* pvo) {
	vector<Order*>::const_iterator i;
	for (i = pvo->begin(); i != pvo->end(); ++i) {
		os << **i<< endl;
	}
}

void app1::change_order( ) {

	vector<Order*>* porders =  show_orders_by_customer_impl();
	os << "Select order to edit: " << endl;
	int j = 0;
	if (porders == 0 )
		return;
	for ( j = 0; j < porders->size() ; ++j) {
		os << '\t' <<j+1 << ": " << Order::get_formatted_time((*porders)[j]->get_time()) << endl;
		
	}
	os << " Enter index number ? ";
	string sel;
	getline(is, sel);
	int n = atoi(sel.c_str()) -1;
	if (n >= 0 && n < porders->size() ) {
		Order* order = (*porders)[n];
		os << "1. Change order items" << endl;
		os << "2. Change order dates" << endl;
		sel = "";
		getline(is, sel);
		switch ( atoi(sel.c_str())) {
			case 1:
			while(update_order_impl( order ));
			break;

			case 2:
				change_order_details( order);
				SQLManager::instance()->storeOrder(order);
				break;

			default:
				break;
			
		}
	}

	delete porders;

}

void app1::change_order_details(Order* ord) {			
	string ordered,completed, paid;
	ordered = ord->get_time() > 100 ? Order::get_formatted_time(ord->get_time()) : "";
	completed = ord->get_completed() > 100 ? Order::get_formatted_time(ord->get_completed()) : "";
	paid = ord->get_paid() > 100 ? Order::get_formatted_time(ord->get_paid()) : "";

	os << "Order date (current= "<< ordered <<") : ";
	string sel;
	getline(is, sel);
	time_t new_ordered = Order::get_time(sel);
	
	os << "Completed date (current= " << completed << ") : ";
	sel = "";
	getline(is, sel);
	time_t new_completed= Order::get_time(sel);
	os << "Paid date (current= " << paid << ") : ";
	sel = "";
	getline(is, sel);
	time_t new_paid = Order::get_time(sel);
	os << "New times are " ;
	os << "Order date "<< Order::get_formatted_time(new_ordered) << endl;
	os << "Completion date "<< Order::get_formatted_time(new_completed) << endl;
	os << "Order date "<< Order::get_formatted_time(new_paid) << endl;
	if (new_ordered > 100)
		ord->set_time(new_ordered);
	if( new_completed > 100)
		ord->set_completed(new_completed);
	if( new_paid > 100)
		ord->set_paid( new_paid);

	
}
	
void app1::show_unpaid_orders() {
	os << "Show unpaid orders:";
	os << endl;
        os << "1.of all customers" << endl;
        os << "2.of one customer" << endl;

	string sel;
	getline(is, sel);
	int n = atoi(sel.c_str());
	switch ( n ) {
		case 1:
			show_all_unpaid_orders( );
			break;

		case 2:
			show_unpaid_orders_by_customer();
			break;

		default:
			break;	

	}

}


void app1::show_all_unpaid_orders( ) {
	vector<Customer*> * pcusts = SQLManager::instance()->listAllCustomers();
	vector<Customer*>::const_iterator i;
	for (i = pcusts->begin(); i != pcusts->end(); ++i) {
		vector<Order*> * porders = SQLManager::instance()->getUnPaidOrders(*i);
		os <<endl << "-----------------" << endl;
		os << "Unpaid orders for " << **i << endl;
		os << "-------------------" << endl;
		vector<Order*>::const_iterator j;
		for (j = porders->begin() ; j!= porders->end() ; ++j) {
			os << **j << endl;
		}
		
		Money *m = Order::get_total_of_orders(porders, moneyType);
    os << endl;
		os << setw(app1::group_total_indent) << setfill(' ') << "" ;
    os <<" total of order totals = " << m->get_string() << endl << endl;
		delete m;
		delete porders;
	}
	delete pcusts;
}


