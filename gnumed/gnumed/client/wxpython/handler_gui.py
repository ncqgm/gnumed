# ['gmContacts.py', 'gmDrugDisplay.py', 'gmGuidelines.py', 'gmLock.py', 'gmManual.py', 'gmOffice.py', 'gmPatientWindowManager.py', 'gmPython.py', 'gmSQL.py', 'gmSnellen.py', 'gmStikoBrowser.py', 'gmplNbPatientSelector.py', 'gmplNbSchedule.py']

from wxPython.wx import * 
#creating a handler as gmContacts_handler from gui/gmContacts.py
# type_search_str =  class\s+(?P<new_type>\w+)\s*\(.*(?P<base_type>wxTextCtrl|wxComboBox|wxButton|wxRadioButton|wxCheckBox|wxListBox)
# found new type = TextBox_RedBold which is base_type wxTextCtrl

# found new type = TextBox_BlackNormal which is base_type wxTextCtrl

# [('txt_org_name', 'TextBox_RedBold'), ('txt_org_type', 'TextBox_RedBold'), ('txt_org_street', 'wxTextCtrl'), ('txt_org_suburb', 'TextBox_RedBold'), ('txt_org_zip', 'TextBox_RedBold'), ('txt_org_state', 'TextBox_RedBold'), ('txt_org_user1', 'TextBox_BlackNormal'), ('txt_org_user2', 'TextBox_BlackNormal'), ('txt_org_user3', 'TextBox_BlackNormal'), ('txt_org_category', 'TextBox_BlackNormal'), ('txt_org_phone', 'TextBox_BlackNormal'), ('txt_org_fax', 'TextBox_BlackNormal'), ('txt_org_mobile', 'TextBox_BlackNormal'), ('txt_org_email', 'TextBox_BlackNormal'), ('txt_org_internet', 'TextBox_BlackNormal'), ('txt_org_memo', 'wxTextCtrl'), ('combo_type', 'wxComboBox'), ('chbx_postaladdress', 'wxCheckBox')]


class gmContacts_handler:

	def create_handler(self, panel, model = None):
		if model == None and self.model <> None:
			model = self.model
			
		return self.__init__(panel, model)

	def __init__(self, panel, model = None):
		self.panel = panel
		self.model = model
		if panel <> None:
			self.__set_id()
			self.__set_evt()
			self.impl = None
			if model == None:
				self.model = {}  # change this to a persistence/business object later

	def set_model(self,  model):
		self.model = model
		
	def set_impl(self, impl):
		self.impl = impl

	def __set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('txt_org_name'):
			id = self.panel.txt_org_name.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_org_name.SetId(id)
			self.id_map['txt_org_name'] = id
			

		if self.panel.__dict__.has_key('txt_org_type'):
			id = self.panel.txt_org_type.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_org_type.SetId(id)
			self.id_map['txt_org_type'] = id
			

		if self.panel.__dict__.has_key('txt_org_street'):
			id = self.panel.txt_org_street.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_org_street.SetId(id)
			self.id_map['txt_org_street'] = id
			

		if self.panel.__dict__.has_key('txt_org_suburb'):
			id = self.panel.txt_org_suburb.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_org_suburb.SetId(id)
			self.id_map['txt_org_suburb'] = id
			

		if self.panel.__dict__.has_key('txt_org_zip'):
			id = self.panel.txt_org_zip.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_org_zip.SetId(id)
			self.id_map['txt_org_zip'] = id
			

		if self.panel.__dict__.has_key('txt_org_state'):
			id = self.panel.txt_org_state.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_org_state.SetId(id)
			self.id_map['txt_org_state'] = id
			

		if self.panel.__dict__.has_key('txt_org_user1'):
			id = self.panel.txt_org_user1.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_org_user1.SetId(id)
			self.id_map['txt_org_user1'] = id
			

		if self.panel.__dict__.has_key('txt_org_user2'):
			id = self.panel.txt_org_user2.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_org_user2.SetId(id)
			self.id_map['txt_org_user2'] = id
			

		if self.panel.__dict__.has_key('txt_org_user3'):
			id = self.panel.txt_org_user3.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_org_user3.SetId(id)
			self.id_map['txt_org_user3'] = id
			

		if self.panel.__dict__.has_key('txt_org_category'):
			id = self.panel.txt_org_category.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_org_category.SetId(id)
			self.id_map['txt_org_category'] = id
			

		if self.panel.__dict__.has_key('txt_org_phone'):
			id = self.panel.txt_org_phone.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_org_phone.SetId(id)
			self.id_map['txt_org_phone'] = id
			

		if self.panel.__dict__.has_key('txt_org_fax'):
			id = self.panel.txt_org_fax.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_org_fax.SetId(id)
			self.id_map['txt_org_fax'] = id
			

		if self.panel.__dict__.has_key('txt_org_mobile'):
			id = self.panel.txt_org_mobile.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_org_mobile.SetId(id)
			self.id_map['txt_org_mobile'] = id
			

		if self.panel.__dict__.has_key('txt_org_email'):
			id = self.panel.txt_org_email.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_org_email.SetId(id)
			self.id_map['txt_org_email'] = id
			

		if self.panel.__dict__.has_key('txt_org_internet'):
			id = self.panel.txt_org_internet.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_org_internet.SetId(id)
			self.id_map['txt_org_internet'] = id
			

		if self.panel.__dict__.has_key('txt_org_memo'):
			id = self.panel.txt_org_memo.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_org_memo.SetId(id)
			self.id_map['txt_org_memo'] = id
			

		if self.panel.__dict__.has_key('combo_type'):
			id = self.panel.combo_type.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.combo_type.SetId(id)
			self.id_map['combo_type'] = id
			

		if self.panel.__dict__.has_key('chbx_postaladdress'):
			id = self.panel.chbx_postaladdress.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.chbx_postaladdress.SetId(id)
			self.id_map['chbx_postaladdress'] = id
			

	def __set_evt(self):
		pass
		

		if self.panel.__dict__.has_key('txt_org_name'):
			EVT_TEXT(self.panel.txt_org_name,\
			self.id_map['txt_org_name'],\
			self.txt_org_name_text_entered)

		if self.panel.__dict__.has_key('txt_org_type'):
			EVT_TEXT(self.panel.txt_org_type,\
			self.id_map['txt_org_type'],\
			self.txt_org_type_text_entered)

		if self.panel.__dict__.has_key('txt_org_street'):
			EVT_TEXT(self.panel.txt_org_street,\
			self.id_map['txt_org_street'],\
			self.txt_org_street_text_entered)

		if self.panel.__dict__.has_key('txt_org_suburb'):
			EVT_TEXT(self.panel.txt_org_suburb,\
			self.id_map['txt_org_suburb'],\
			self.txt_org_suburb_text_entered)

		if self.panel.__dict__.has_key('txt_org_zip'):
			EVT_TEXT(self.panel.txt_org_zip,\
			self.id_map['txt_org_zip'],\
			self.txt_org_zip_text_entered)

		if self.panel.__dict__.has_key('txt_org_state'):
			EVT_TEXT(self.panel.txt_org_state,\
			self.id_map['txt_org_state'],\
			self.txt_org_state_text_entered)

		if self.panel.__dict__.has_key('txt_org_user1'):
			EVT_TEXT(self.panel.txt_org_user1,\
			self.id_map['txt_org_user1'],\
			self.txt_org_user1_text_entered)

		if self.panel.__dict__.has_key('txt_org_user2'):
			EVT_TEXT(self.panel.txt_org_user2,\
			self.id_map['txt_org_user2'],\
			self.txt_org_user2_text_entered)

		if self.panel.__dict__.has_key('txt_org_user3'):
			EVT_TEXT(self.panel.txt_org_user3,\
			self.id_map['txt_org_user3'],\
			self.txt_org_user3_text_entered)

		if self.panel.__dict__.has_key('txt_org_category'):
			EVT_TEXT(self.panel.txt_org_category,\
			self.id_map['txt_org_category'],\
			self.txt_org_category_text_entered)

		if self.panel.__dict__.has_key('txt_org_phone'):
			EVT_TEXT(self.panel.txt_org_phone,\
			self.id_map['txt_org_phone'],\
			self.txt_org_phone_text_entered)

		if self.panel.__dict__.has_key('txt_org_fax'):
			EVT_TEXT(self.panel.txt_org_fax,\
			self.id_map['txt_org_fax'],\
			self.txt_org_fax_text_entered)

		if self.panel.__dict__.has_key('txt_org_mobile'):
			EVT_TEXT(self.panel.txt_org_mobile,\
			self.id_map['txt_org_mobile'],\
			self.txt_org_mobile_text_entered)

		if self.panel.__dict__.has_key('txt_org_email'):
			EVT_TEXT(self.panel.txt_org_email,\
			self.id_map['txt_org_email'],\
			self.txt_org_email_text_entered)

		if self.panel.__dict__.has_key('txt_org_internet'):
			EVT_TEXT(self.panel.txt_org_internet,\
			self.id_map['txt_org_internet'],\
			self.txt_org_internet_text_entered)

		if self.panel.__dict__.has_key('txt_org_memo'):
			EVT_TEXT(self.panel.txt_org_memo,\
			self.id_map['txt_org_memo'],\
			self.txt_org_memo_text_entered)

		if self.panel.__dict__.has_key('combo_type'):
			EVT_TEXT(self.panel.combo_type,\
			self.id_map['combo_type'],\
			self.combo_type_text_entered)

		if self.panel.__dict__.has_key('chbx_postaladdress'):
			EVT_CHECKBOX(self.panel.chbx_postaladdress,\
			self.id_map['chbx_postaladdress'],\
			self.chbx_postaladdress_checkbox_clicked)

	def txt_org_name_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_org_name_text_entered(self, event) 
			

		print "txt_org_name_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['org_name']= obj.GetValue()
			print self.model['org_name']
		

	def txt_org_type_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_org_type_text_entered(self, event) 
			

		print "txt_org_type_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['org_type']= obj.GetValue()
			print self.model['org_type']
		

	def txt_org_street_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_org_street_text_entered(self, event) 
			

		print "txt_org_street_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['org_street']= obj.GetValue()
			print self.model['org_street']
		

	def txt_org_suburb_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_org_suburb_text_entered(self, event) 
			

		print "txt_org_suburb_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['org_suburb']= obj.GetValue()
			print self.model['org_suburb']
		

	def txt_org_zip_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_org_zip_text_entered(self, event) 
			

		print "txt_org_zip_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['org_zip']= obj.GetValue()
			print self.model['org_zip']
		

	def txt_org_state_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_org_state_text_entered(self, event) 
			

		print "txt_org_state_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['org_state']= obj.GetValue()
			print self.model['org_state']
		

	def txt_org_user1_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_org_user1_text_entered(self, event) 
			

		print "txt_org_user1_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['org_user1']= obj.GetValue()
			print self.model['org_user1']
		

	def txt_org_user2_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_org_user2_text_entered(self, event) 
			

		print "txt_org_user2_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['org_user2']= obj.GetValue()
			print self.model['org_user2']
		

	def txt_org_user3_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_org_user3_text_entered(self, event) 
			

		print "txt_org_user3_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['org_user3']= obj.GetValue()
			print self.model['org_user3']
		

	def txt_org_category_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_org_category_text_entered(self, event) 
			

		print "txt_org_category_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['org_category']= obj.GetValue()
			print self.model['org_category']
		

	def txt_org_phone_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_org_phone_text_entered(self, event) 
			

		print "txt_org_phone_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['org_phone']= obj.GetValue()
			print self.model['org_phone']
		

	def txt_org_fax_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_org_fax_text_entered(self, event) 
			

		print "txt_org_fax_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['org_fax']= obj.GetValue()
			print self.model['org_fax']
		

	def txt_org_mobile_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_org_mobile_text_entered(self, event) 
			

		print "txt_org_mobile_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['org_mobile']= obj.GetValue()
			print self.model['org_mobile']
		

	def txt_org_email_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_org_email_text_entered(self, event) 
			

		print "txt_org_email_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['org_email']= obj.GetValue()
			print self.model['org_email']
		

	def txt_org_internet_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_org_internet_text_entered(self, event) 
			

		print "txt_org_internet_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['org_internet']= obj.GetValue()
			print self.model['org_internet']
		

	def txt_org_memo_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_org_memo_text_entered(self, event) 
			

		print "txt_org_memo_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['org_memo']= obj.GetValue()
			print self.model['org_memo']
		

	def combo_type_text_entered( self, event): 
		if self.impl <> None:
			self.impl.combo_type_text_entered(self, event) 
			

		print "combo_type_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['type']= obj.GetValue()
			print self.model['type']
		

	def chbx_postaladdress_checkbox_clicked( self, event): 
		if self.impl <> None:
			self.impl.chbx_postaladdress_checkbox_clicked(self, event) 
			

		print "chbx_postaladdress_checkbox_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['postaladdress']= obj.GetValue()
			print self.model['postaladdress']
		
#creating a handler as gmDrugDisplay_handler from gui/gmDrugDisplay.py
# [('comboProduct', 'wxComboBox'), ('btnBookmark', 'wxButton'), ('rbtnSearchAny', 'wxRadioButton'), ('rbtnSearchBrand', 'wxRadioButton'), ('rbtnSearchGeneric', 'wxRadioButton'), ('rbtnSearchIndication', 'wxRadioButton'), ('listbox_jumpto', 'wxListBox'), ('btnPrescribe', 'wxButton'), ('btnDisplay', 'wxButton'), ('btnPrint', 'wxButton'), ('listbox_drugchoice', 'wxListBox')]


class gmDrugDisplay_handler:

	def create_handler(self, panel, model = None):
		if model == None and self.model <> None:
			model = self.model
			
		return self.__init__(panel, model)

	def __init__(self, panel, model = None):
		self.panel = panel
		self.model = model
		if panel <> None:
			self.__set_id()
			self.__set_evt()
			self.impl = None
			if model == None:
				self.model = {}  # change this to a persistence/business object later

	def set_model(self,  model):
		self.model = model
		
	def set_impl(self, impl):
		self.impl = impl

	def __set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('comboProduct'):
			id = self.panel.comboProduct.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.comboProduct.SetId(id)
			self.id_map['comboProduct'] = id
			

		if self.panel.__dict__.has_key('btnBookmark'):
			id = self.panel.btnBookmark.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.btnBookmark.SetId(id)
			self.id_map['btnBookmark'] = id
			

		if self.panel.__dict__.has_key('rbtnSearchAny'):
			id = self.panel.rbtnSearchAny.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.rbtnSearchAny.SetId(id)
			self.id_map['rbtnSearchAny'] = id
			

		if self.panel.__dict__.has_key('rbtnSearchBrand'):
			id = self.panel.rbtnSearchBrand.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.rbtnSearchBrand.SetId(id)
			self.id_map['rbtnSearchBrand'] = id
			

		if self.panel.__dict__.has_key('rbtnSearchGeneric'):
			id = self.panel.rbtnSearchGeneric.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.rbtnSearchGeneric.SetId(id)
			self.id_map['rbtnSearchGeneric'] = id
			

		if self.panel.__dict__.has_key('rbtnSearchIndication'):
			id = self.panel.rbtnSearchIndication.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.rbtnSearchIndication.SetId(id)
			self.id_map['rbtnSearchIndication'] = id
			

		if self.panel.__dict__.has_key('listbox_jumpto'):
			id = self.panel.listbox_jumpto.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.listbox_jumpto.SetId(id)
			self.id_map['listbox_jumpto'] = id
			

		if self.panel.__dict__.has_key('btnPrescribe'):
			id = self.panel.btnPrescribe.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.btnPrescribe.SetId(id)
			self.id_map['btnPrescribe'] = id
			

		if self.panel.__dict__.has_key('btnDisplay'):
			id = self.panel.btnDisplay.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.btnDisplay.SetId(id)
			self.id_map['btnDisplay'] = id
			

		if self.panel.__dict__.has_key('btnPrint'):
			id = self.panel.btnPrint.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.btnPrint.SetId(id)
			self.id_map['btnPrint'] = id
			

		if self.panel.__dict__.has_key('listbox_drugchoice'):
			id = self.panel.listbox_drugchoice.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.listbox_drugchoice.SetId(id)
			self.id_map['listbox_drugchoice'] = id
			

	def __set_evt(self):
		pass
		

		if self.panel.__dict__.has_key('comboProduct'):
			EVT_TEXT(self.panel.comboProduct,\
			self.id_map['comboProduct'],\
			self.comboProduct_text_entered)

		if self.panel.__dict__.has_key('btnBookmark'):
			EVT_BUTTON(self.panel.btnBookmark,\
			self.id_map['btnBookmark'],\
			self.btnBookmark_button_clicked)

		if self.panel.__dict__.has_key('rbtnSearchAny'):
			EVT_RADIOBUTTON(self.panel.rbtnSearchAny,\
			self.id_map['rbtnSearchAny'],\
			self.rbtnSearchAny_radiobutton_clicked)

		if self.panel.__dict__.has_key('rbtnSearchBrand'):
			EVT_RADIOBUTTON(self.panel.rbtnSearchBrand,\
			self.id_map['rbtnSearchBrand'],\
			self.rbtnSearchBrand_radiobutton_clicked)

		if self.panel.__dict__.has_key('rbtnSearchGeneric'):
			EVT_RADIOBUTTON(self.panel.rbtnSearchGeneric,\
			self.id_map['rbtnSearchGeneric'],\
			self.rbtnSearchGeneric_radiobutton_clicked)

		if self.panel.__dict__.has_key('rbtnSearchIndication'):
			EVT_RADIOBUTTON(self.panel.rbtnSearchIndication,\
			self.id_map['rbtnSearchIndication'],\
			self.rbtnSearchIndication_radiobutton_clicked)

		if self.panel.__dict__.has_key('listbox_jumpto'):
			EVT_LISTBOX(self.panel.listbox_jumpto,\
			self.id_map['listbox_jumpto'],\
			self.listbox_jumpto_list_box_single_clicked)

		if self.panel.__dict__.has_key('listbox_jumpto'):
			EVT_LISTBOX_DCLICK(self.panel.listbox_jumpto,\
			self.id_map['listbox_jumpto'],\
			self.listbox_jumpto_list_box_double_clicked)

		if self.panel.__dict__.has_key('btnPrescribe'):
			EVT_BUTTON(self.panel.btnPrescribe,\
			self.id_map['btnPrescribe'],\
			self.btnPrescribe_button_clicked)

		if self.panel.__dict__.has_key('btnDisplay'):
			EVT_BUTTON(self.panel.btnDisplay,\
			self.id_map['btnDisplay'],\
			self.btnDisplay_button_clicked)

		if self.panel.__dict__.has_key('btnPrint'):
			EVT_BUTTON(self.panel.btnPrint,\
			self.id_map['btnPrint'],\
			self.btnPrint_button_clicked)

		if self.panel.__dict__.has_key('listbox_drugchoice'):
			EVT_LISTBOX(self.panel.listbox_drugchoice,\
			self.id_map['listbox_drugchoice'],\
			self.listbox_drugchoice_list_box_single_clicked)

		if self.panel.__dict__.has_key('listbox_drugchoice'):
			EVT_LISTBOX_DCLICK(self.panel.listbox_drugchoice,\
			self.id_map['listbox_drugchoice'],\
			self.listbox_drugchoice_list_box_double_clicked)

	def comboProduct_text_entered( self, event): 
		if self.impl <> None:
			self.impl.comboProduct_text_entered(self, event) 
			

		print "comboProduct_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['comboProduct']= obj.GetValue()
			print self.model['comboProduct']
		

	def btnBookmark_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btnBookmark_button_clicked(self, event) 
			

		print "btnBookmark_button_clicked received ", event
			

	def rbtnSearchAny_radiobutton_clicked( self, event): 
		if self.impl <> None:
			self.impl.rbtnSearchAny_radiobutton_clicked(self, event) 
			

		print "rbtnSearchAny_radiobutton_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['rbtnSearchAny']= obj.GetValue()
			print self.model['rbtnSearchAny']
		

	def rbtnSearchBrand_radiobutton_clicked( self, event): 
		if self.impl <> None:
			self.impl.rbtnSearchBrand_radiobutton_clicked(self, event) 
			

		print "rbtnSearchBrand_radiobutton_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['rbtnSearchBrand']= obj.GetValue()
			print self.model['rbtnSearchBrand']
		

	def rbtnSearchGeneric_radiobutton_clicked( self, event): 
		if self.impl <> None:
			self.impl.rbtnSearchGeneric_radiobutton_clicked(self, event) 
			

		print "rbtnSearchGeneric_radiobutton_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['rbtnSearchGeneric']= obj.GetValue()
			print self.model['rbtnSearchGeneric']
		

	def rbtnSearchIndication_radiobutton_clicked( self, event): 
		if self.impl <> None:
			self.impl.rbtnSearchIndication_radiobutton_clicked(self, event) 
			

		print "rbtnSearchIndication_radiobutton_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['rbtnSearchIndication']= obj.GetValue()
			print self.model['rbtnSearchIndication']
		

	def listbox_jumpto_list_box_single_clicked( self, event): 
		if self.impl <> None:
			self.impl.listbox_jumpto_list_box_single_clicked(self, event) 
			

		print "listbox_jumpto_list_box_single_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['jumpto']= obj.GetStringSelection()
			print self.model['jumpto']
		

	def listbox_jumpto_list_box_double_clicked( self, event): 
		if self.impl <> None:
			self.impl.listbox_jumpto_list_box_double_clicked(self, event) 
			

		print "listbox_jumpto_list_box_double_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['jumpto']= obj.GetStringSelection()
			print self.model['jumpto']
		

	def btnPrescribe_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btnPrescribe_button_clicked(self, event) 
			

		print "btnPrescribe_button_clicked received ", event
			

	def btnDisplay_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btnDisplay_button_clicked(self, event) 
			

		print "btnDisplay_button_clicked received ", event
			

	def btnPrint_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btnPrint_button_clicked(self, event) 
			

		print "btnPrint_button_clicked received ", event
			

	def listbox_drugchoice_list_box_single_clicked( self, event): 
		if self.impl <> None:
			self.impl.listbox_drugchoice_list_box_single_clicked(self, event) 
			

		print "listbox_drugchoice_list_box_single_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['drugchoice']= obj.GetStringSelection()
			print self.model['drugchoice']
		

	def listbox_drugchoice_list_box_double_clicked( self, event): 
		if self.impl <> None:
			self.impl.listbox_drugchoice_list_box_double_clicked(self, event) 
			

		print "listbox_drugchoice_list_box_double_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['drugchoice']= obj.GetStringSelection()
			print self.model['drugchoice']
		
#creating a handler as gmGuidelines_handler from gui/gmGuidelines.py
# [('infoline', 'wxTextCtrl')]


class gmGuidelines_handler:

	def create_handler(self, panel, model = None):
		if model == None and self.model <> None:
			model = self.model
			
		return self.__init__(panel, model)

	def __init__(self, panel, model = None):
		self.panel = panel
		self.model = model
		if panel <> None:
			self.__set_id()
			self.__set_evt()
			self.impl = None
			if model == None:
				self.model = {}  # change this to a persistence/business object later

	def set_model(self,  model):
		self.model = model
		
	def set_impl(self, impl):
		self.impl = impl

	def __set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('infoline'):
			id = self.panel.infoline.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.infoline.SetId(id)
			self.id_map['infoline'] = id
			

	def __set_evt(self):
		pass
		

		if self.panel.__dict__.has_key('infoline'):
			EVT_TEXT(self.panel.infoline,\
			self.id_map['infoline'],\
			self.infoline_text_entered)

	def infoline_text_entered( self, event): 
		if self.impl <> None:
			self.impl.infoline_text_entered(self, event) 
			

		print "infoline_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['infoline']= obj.GetValue()
			print self.model['infoline']
		
#creating a handler as gmLock_handler from gui/gmLock.py
# []
#creating a handler as gmManual_handler from gui/gmManual.py
# [('infoline', 'wxTextCtrl')]


class gmManual_handler:

	def create_handler(self, panel, model = None):
		if model == None and self.model <> None:
			model = self.model
			
		return self.__init__(panel, model)

	def __init__(self, panel, model = None):
		self.panel = panel
		self.model = model
		if panel <> None:
			self.__set_id()
			self.__set_evt()
			self.impl = None
			if model == None:
				self.model = {}  # change this to a persistence/business object later

	def set_model(self,  model):
		self.model = model
		
	def set_impl(self, impl):
		self.impl = impl

	def __set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('infoline'):
			id = self.panel.infoline.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.infoline.SetId(id)
			self.id_map['infoline'] = id
			

	def __set_evt(self):
		pass
		

		if self.panel.__dict__.has_key('infoline'):
			EVT_TEXT(self.panel.infoline,\
			self.id_map['infoline'],\
			self.infoline_text_entered)

	def infoline_text_entered( self, event): 
		if self.impl <> None:
			self.impl.infoline_text_entered(self, event) 
			

		print "infoline_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['infoline']= obj.GetValue()
			print self.model['infoline']
		
#creating a handler as gmOffice_handler from gui/gmOffice.py
# []
#creating a handler as gmPatientWindowManager_handler from gui/gmPatientWindowManager.py
# []
#creating a handler as gmPython_handler from gui/gmPython.py
# []
#creating a handler as gmSQL_handler from gui/gmSQL.py
# [('comboQueryInput', 'wxComboBox'), ('buttonRunQuery', 'wxButton'), ('buttonClearQuery', 'wxButton'), ('textQueryResults', 'wxTextCtrl')]


class gmSQL_handler:

	def create_handler(self, panel, model = None):
		if model == None and self.model <> None:
			model = self.model
			
		return self.__init__(panel, model)

	def __init__(self, panel, model = None):
		self.panel = panel
		self.model = model
		if panel <> None:
			self.__set_id()
			self.__set_evt()
			self.impl = None
			if model == None:
				self.model = {}  # change this to a persistence/business object later

	def set_model(self,  model):
		self.model = model
		
	def set_impl(self, impl):
		self.impl = impl

	def __set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('comboQueryInput'):
			id = self.panel.comboQueryInput.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.comboQueryInput.SetId(id)
			self.id_map['comboQueryInput'] = id
			

		if self.panel.__dict__.has_key('buttonRunQuery'):
			id = self.panel.buttonRunQuery.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.buttonRunQuery.SetId(id)
			self.id_map['buttonRunQuery'] = id
			

		if self.panel.__dict__.has_key('buttonClearQuery'):
			id = self.panel.buttonClearQuery.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.buttonClearQuery.SetId(id)
			self.id_map['buttonClearQuery'] = id
			

		if self.panel.__dict__.has_key('textQueryResults'):
			id = self.panel.textQueryResults.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.textQueryResults.SetId(id)
			self.id_map['textQueryResults'] = id
			

	def __set_evt(self):
		pass
		

		if self.panel.__dict__.has_key('comboQueryInput'):
			EVT_TEXT(self.panel.comboQueryInput,\
			self.id_map['comboQueryInput'],\
			self.comboQueryInput_text_entered)

		if self.panel.__dict__.has_key('buttonRunQuery'):
			EVT_BUTTON(self.panel.buttonRunQuery,\
			self.id_map['buttonRunQuery'],\
			self.buttonRunQuery_button_clicked)

		if self.panel.__dict__.has_key('buttonClearQuery'):
			EVT_BUTTON(self.panel.buttonClearQuery,\
			self.id_map['buttonClearQuery'],\
			self.buttonClearQuery_button_clicked)

		if self.panel.__dict__.has_key('textQueryResults'):
			EVT_TEXT(self.panel.textQueryResults,\
			self.id_map['textQueryResults'],\
			self.textQueryResults_text_entered)

	def comboQueryInput_text_entered( self, event): 
		if self.impl <> None:
			self.impl.comboQueryInput_text_entered(self, event) 
			

		print "comboQueryInput_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['comboQueryInput']= obj.GetValue()
			print self.model['comboQueryInput']
		

	def buttonRunQuery_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.buttonRunQuery_button_clicked(self, event) 
			

		print "buttonRunQuery_button_clicked received ", event
			

	def buttonClearQuery_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.buttonClearQuery_button_clicked(self, event) 
			

		print "buttonClearQuery_button_clicked received ", event
			

	def textQueryResults_text_entered( self, event): 
		if self.impl <> None:
			self.impl.textQueryResults_text_entered(self, event) 
			

		print "textQueryResults_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['textQueryResults']= obj.GetValue()
			print self.model['textQueryResults']
		
#creating a handler as gmSnellen_handler from gui/gmSnellen.py
# [('mirror_ctrl', 'wxCheckBox')]


class gmSnellen_handler:

	def create_handler(self, panel, model = None):
		if model == None and self.model <> None:
			model = self.model
			
		return self.__init__(panel, model)

	def __init__(self, panel, model = None):
		self.panel = panel
		self.model = model
		if panel <> None:
			self.__set_id()
			self.__set_evt()
			self.impl = None
			if model == None:
				self.model = {}  # change this to a persistence/business object later

	def set_model(self,  model):
		self.model = model
		
	def set_impl(self, impl):
		self.impl = impl

	def __set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('mirror_ctrl'):
			id = self.panel.mirror_ctrl.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.mirror_ctrl.SetId(id)
			self.id_map['mirror_ctrl'] = id
			

	def __set_evt(self):
		pass
		

		if self.panel.__dict__.has_key('mirror_ctrl'):
			EVT_CHECKBOX(self.panel.mirror_ctrl,\
			self.id_map['mirror_ctrl'],\
			self.mirror_ctrl_checkbox_clicked)

	def mirror_ctrl_checkbox_clicked( self, event): 
		if self.impl <> None:
			self.impl.mirror_ctrl_checkbox_clicked(self, event) 
			

		print "mirror_ctrl_checkbox_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['ctrl']= obj.GetValue()
			print self.model['ctrl']
		
#creating a handler as gmStikoBrowser_handler from gui/gmStikoBrowser.py
# [('infoline', 'wxTextCtrl')]


class gmStikoBrowser_handler:

	def create_handler(self, panel, model = None):
		if model == None and self.model <> None:
			model = self.model
			
		return self.__init__(panel, model)

	def __init__(self, panel, model = None):
		self.panel = panel
		self.model = model
		if panel <> None:
			self.__set_id()
			self.__set_evt()
			self.impl = None
			if model == None:
				self.model = {}  # change this to a persistence/business object later

	def set_model(self,  model):
		self.model = model
		
	def set_impl(self, impl):
		self.impl = impl

	def __set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('infoline'):
			id = self.panel.infoline.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.infoline.SetId(id)
			self.id_map['infoline'] = id
			

	def __set_evt(self):
		pass
		

		if self.panel.__dict__.has_key('infoline'):
			EVT_TEXT(self.panel.infoline,\
			self.id_map['infoline'],\
			self.infoline_text_entered)

	def infoline_text_entered( self, event): 
		if self.impl <> None:
			self.impl.infoline_text_entered(self, event) 
			

		print "infoline_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['infoline']= obj.GetValue()
			print self.model['infoline']
		
#creating a handler as gmplNbPatientSelector_handler from gui/gmplNbPatientSelector.py
# []
#creating a handler as gmplNbSchedule_handler from gui/gmplNbSchedule.py
# []
