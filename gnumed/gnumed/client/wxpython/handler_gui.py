# ['gmContacts.py', 'gmDrugDisplay.py', 'gmGuidelines.py', 'gmLock.py', 'gmManual.py', 'gmOffice.py', 'gmPatientWindowManager.py', 'gmPython.py', 'gmSQL.py', 'gmSnellen.py', 'gmStikoBrowser.py', 'gmplNbPatientSelector.py', 'gmplNbSchedule.py']

from wxPython.wx import * 
#creating a handler as gmContacts_handler from gui/gmContacts.py
# type_search_str =  class\s+(?P<new_type>\w+)\s*\(.*(?P<base_type>EditAreaTextBox|wxTextCtrl|wxComboBox|wxButton|wxRadioButton|wxCheckBox|wxListBox)
# found new type = TextBox_RedBold which is base_type wxTextCtrl

# found new type = TextBox_BlackNormal which is base_type wxTextCtrl

# [('txt_org_name', 'TextBox_RedBold'), ('txt_org_type', 'TextBox_RedBold'), ('txt_org_street', 'wxTextCtrl'), ('txt_org_suburb', 'TextBox_RedBold'), ('txt_org_zip', 'TextBox_RedBold'), ('txt_org_state', 'TextBox_RedBold'), ('txt_org_user1', 'TextBox_BlackNormal'), ('txt_org_user2', 'TextBox_BlackNormal'), ('txt_org_user3', 'TextBox_BlackNormal'), ('txt_org_category', 'TextBox_BlackNormal'), ('txt_org_phone', 'TextBox_BlackNormal'), ('txt_org_fax', 'TextBox_BlackNormal'), ('txt_org_mobile', 'TextBox_BlackNormal'), ('txt_org_email', 'TextBox_BlackNormal'), ('txt_org_internet', 'TextBox_BlackNormal'), ('txt_org_memo', 'wxTextCtrl'), ('combo_type', 'wxComboBox'), ('chbx_postaladdress', 'wxCheckBox')]


class gmContacts_handler:

	def create_handler(self, panel):
		return gmContacts_handler(panel)

	def __init__(self, panel):
		self.panel = panel
		if panel <> None:
			self.__set_id()
			self.__set_evt()

	def __set_id(self):
		self.id_map = {}


		id = self.panel.txt_org_name.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_org_name.SetId(id)
		self.id_map['txt_org_name'] = id
		

		id = self.panel.txt_org_type.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_org_type.SetId(id)
		self.id_map['txt_org_type'] = id
		

		id = self.panel.txt_org_street.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_org_street.SetId(id)
		self.id_map['txt_org_street'] = id
		

		id = self.panel.txt_org_suburb.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_org_suburb.SetId(id)
		self.id_map['txt_org_suburb'] = id
		

		id = self.panel.txt_org_zip.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_org_zip.SetId(id)
		self.id_map['txt_org_zip'] = id
		

		id = self.panel.txt_org_state.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_org_state.SetId(id)
		self.id_map['txt_org_state'] = id
		

		id = self.panel.txt_org_user1.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_org_user1.SetId(id)
		self.id_map['txt_org_user1'] = id
		

		id = self.panel.txt_org_user2.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_org_user2.SetId(id)
		self.id_map['txt_org_user2'] = id
		

		id = self.panel.txt_org_user3.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_org_user3.SetId(id)
		self.id_map['txt_org_user3'] = id
		

		id = self.panel.txt_org_category.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_org_category.SetId(id)
		self.id_map['txt_org_category'] = id
		

		id = self.panel.txt_org_phone.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_org_phone.SetId(id)
		self.id_map['txt_org_phone'] = id
		

		id = self.panel.txt_org_fax.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_org_fax.SetId(id)
		self.id_map['txt_org_fax'] = id
		

		id = self.panel.txt_org_mobile.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_org_mobile.SetId(id)
		self.id_map['txt_org_mobile'] = id
		

		id = self.panel.txt_org_email.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_org_email.SetId(id)
		self.id_map['txt_org_email'] = id
		

		id = self.panel.txt_org_internet.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_org_internet.SetId(id)
		self.id_map['txt_org_internet'] = id
		

		id = self.panel.txt_org_memo.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_org_memo.SetId(id)
		self.id_map['txt_org_memo'] = id
		

		id = self.panel.combo_type.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.combo_type.SetId(id)
		self.id_map['combo_type'] = id
		

		id = self.panel.chbx_postaladdress.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.chbx_postaladdress.SetId(id)
		self.id_map['chbx_postaladdress'] = id
		

	def __set_evt(self):
		pass
		

		EVT_TEXT(self.panel.txt_org_name,\
			self.id_map['txt_org_name'],\
			self.txt_org_name_text_entered)

		EVT_TEXT(self.panel.txt_org_type,\
			self.id_map['txt_org_type'],\
			self.txt_org_type_text_entered)

		EVT_TEXT(self.panel.txt_org_street,\
			self.id_map['txt_org_street'],\
			self.txt_org_street_text_entered)

		EVT_TEXT(self.panel.txt_org_suburb,\
			self.id_map['txt_org_suburb'],\
			self.txt_org_suburb_text_entered)

		EVT_TEXT(self.panel.txt_org_zip,\
			self.id_map['txt_org_zip'],\
			self.txt_org_zip_text_entered)

		EVT_TEXT(self.panel.txt_org_state,\
			self.id_map['txt_org_state'],\
			self.txt_org_state_text_entered)

		EVT_TEXT(self.panel.txt_org_user1,\
			self.id_map['txt_org_user1'],\
			self.txt_org_user1_text_entered)

		EVT_TEXT(self.panel.txt_org_user2,\
			self.id_map['txt_org_user2'],\
			self.txt_org_user2_text_entered)

		EVT_TEXT(self.panel.txt_org_user3,\
			self.id_map['txt_org_user3'],\
			self.txt_org_user3_text_entered)

		EVT_TEXT(self.panel.txt_org_category,\
			self.id_map['txt_org_category'],\
			self.txt_org_category_text_entered)

		EVT_TEXT(self.panel.txt_org_phone,\
			self.id_map['txt_org_phone'],\
			self.txt_org_phone_text_entered)

		EVT_TEXT(self.panel.txt_org_fax,\
			self.id_map['txt_org_fax'],\
			self.txt_org_fax_text_entered)

		EVT_TEXT(self.panel.txt_org_mobile,\
			self.id_map['txt_org_mobile'],\
			self.txt_org_mobile_text_entered)

		EVT_TEXT(self.panel.txt_org_email,\
			self.id_map['txt_org_email'],\
			self.txt_org_email_text_entered)

		EVT_TEXT(self.panel.txt_org_internet,\
			self.id_map['txt_org_internet'],\
			self.txt_org_internet_text_entered)

		EVT_TEXT(self.panel.txt_org_memo,\
			self.id_map['txt_org_memo'],\
			self.txt_org_memo_text_entered)

		EVT_TEXT(self.panel.combo_type,\
			self.id_map['combo_type'],\
			self.combo_type_text_entered)

		EVT_CHECKBOX(self.panel.chbx_postaladdress,\
			self.id_map['chbx_postaladdress'],\
			self.chbx_postaladdress_checkbox_clicked)

	def txt_org_name_text_entered( self, event):
		pass

		print "txt_org_name_text_entered received ", event
			

	def txt_org_type_text_entered( self, event):
		pass

		print "txt_org_type_text_entered received ", event
			

	def txt_org_street_text_entered( self, event):
		pass

		print "txt_org_street_text_entered received ", event
			

	def txt_org_suburb_text_entered( self, event):
		pass

		print "txt_org_suburb_text_entered received ", event
			

	def txt_org_zip_text_entered( self, event):
		pass

		print "txt_org_zip_text_entered received ", event
			

	def txt_org_state_text_entered( self, event):
		pass

		print "txt_org_state_text_entered received ", event
			

	def txt_org_user1_text_entered( self, event):
		pass

		print "txt_org_user1_text_entered received ", event
			

	def txt_org_user2_text_entered( self, event):
		pass

		print "txt_org_user2_text_entered received ", event
			

	def txt_org_user3_text_entered( self, event):
		pass

		print "txt_org_user3_text_entered received ", event
			

	def txt_org_category_text_entered( self, event):
		pass

		print "txt_org_category_text_entered received ", event
			

	def txt_org_phone_text_entered( self, event):
		pass

		print "txt_org_phone_text_entered received ", event
			

	def txt_org_fax_text_entered( self, event):
		pass

		print "txt_org_fax_text_entered received ", event
			

	def txt_org_mobile_text_entered( self, event):
		pass

		print "txt_org_mobile_text_entered received ", event
			

	def txt_org_email_text_entered( self, event):
		pass

		print "txt_org_email_text_entered received ", event
			

	def txt_org_internet_text_entered( self, event):
		pass

		print "txt_org_internet_text_entered received ", event
			

	def txt_org_memo_text_entered( self, event):
		pass

		print "txt_org_memo_text_entered received ", event
			

	def combo_type_text_entered( self, event):
		pass

		print "combo_type_text_entered received ", event
			

	def chbx_postaladdress_checkbox_clicked( self, event):
		pass

		print "chbx_postaladdress_checkbox_clicked received ", event
			
#creating a handler as gmDrugDisplay_handler from gui/gmDrugDisplay.py
# [('comboProduct', 'wxComboBox'), ('btnBookmark', 'wxButton'), ('rbtnSearchAny', 'wxRadioButton'), ('rbtnSearchBrand', 'wxRadioButton'), ('rbtnSearchGeneric', 'wxRadioButton'), ('rbtnSearchIndication', 'wxRadioButton'), ('listbox_jumpto', 'wxListBox'), ('btnPrescribe', 'wxButton'), ('btnDisplay', 'wxButton'), ('btnPrint', 'wxButton'), ('listbox_drugchoice', 'wxListBox')]


class gmDrugDisplay_handler:

	def create_handler(self, panel):
		return gmDrugDisplay_handler(panel)

	def __init__(self, panel):
		self.panel = panel
		if panel <> None:
			self.__set_id()
			self.__set_evt()

	def __set_id(self):
		self.id_map = {}


		id = self.panel.comboProduct.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.comboProduct.SetId(id)
		self.id_map['comboProduct'] = id
		

		id = self.panel.btnBookmark.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btnBookmark.SetId(id)
		self.id_map['btnBookmark'] = id
		

		id = self.panel.rbtnSearchAny.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.rbtnSearchAny.SetId(id)
		self.id_map['rbtnSearchAny'] = id
		

		id = self.panel.rbtnSearchBrand.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.rbtnSearchBrand.SetId(id)
		self.id_map['rbtnSearchBrand'] = id
		

		id = self.panel.rbtnSearchGeneric.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.rbtnSearchGeneric.SetId(id)
		self.id_map['rbtnSearchGeneric'] = id
		

		id = self.panel.rbtnSearchIndication.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.rbtnSearchIndication.SetId(id)
		self.id_map['rbtnSearchIndication'] = id
		

		id = self.panel.listbox_jumpto.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.listbox_jumpto.SetId(id)
		self.id_map['listbox_jumpto'] = id
		

		id = self.panel.btnPrescribe.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btnPrescribe.SetId(id)
		self.id_map['btnPrescribe'] = id
		

		id = self.panel.btnDisplay.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btnDisplay.SetId(id)
		self.id_map['btnDisplay'] = id
		

		id = self.panel.btnPrint.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btnPrint.SetId(id)
		self.id_map['btnPrint'] = id
		

		id = self.panel.listbox_drugchoice.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.listbox_drugchoice.SetId(id)
		self.id_map['listbox_drugchoice'] = id
		

	def __set_evt(self):
		pass
		

		EVT_TEXT(self.panel.comboProduct,\
			self.id_map['comboProduct'],\
			self.comboProduct_text_entered)

		EVT_BUTTON(self.panel.btnBookmark,\
			self.id_map['btnBookmark'],\
			self.btnBookmark_button_clicked)

		EVT_RADIOBUTTON(self.panel.rbtnSearchAny,\
			self.id_map['rbtnSearchAny'],\
			self.rbtnSearchAny_radiobutton_clicked)

		EVT_RADIOBUTTON(self.panel.rbtnSearchBrand,\
			self.id_map['rbtnSearchBrand'],\
			self.rbtnSearchBrand_radiobutton_clicked)

		EVT_RADIOBUTTON(self.panel.rbtnSearchGeneric,\
			self.id_map['rbtnSearchGeneric'],\
			self.rbtnSearchGeneric_radiobutton_clicked)

		EVT_RADIOBUTTON(self.panel.rbtnSearchIndication,\
			self.id_map['rbtnSearchIndication'],\
			self.rbtnSearchIndication_radiobutton_clicked)

		EVT_LISTBOX(self.panel.listbox_jumpto,\
			self.id_map['listbox_jumpto'],\
			self.listbox_jumpto_list_box_single_clicked)

		EVT_LISTBOX_DCLICK(self.panel.listbox_jumpto,\
			self.id_map['listbox_jumpto'],\
			self.listbox_jumpto_list_box_double_clicked)

		EVT_BUTTON(self.panel.btnPrescribe,\
			self.id_map['btnPrescribe'],\
			self.btnPrescribe_button_clicked)

		EVT_BUTTON(self.panel.btnDisplay,\
			self.id_map['btnDisplay'],\
			self.btnDisplay_button_clicked)

		EVT_BUTTON(self.panel.btnPrint,\
			self.id_map['btnPrint'],\
			self.btnPrint_button_clicked)

		EVT_LISTBOX(self.panel.listbox_drugchoice,\
			self.id_map['listbox_drugchoice'],\
			self.listbox_drugchoice_list_box_single_clicked)

		EVT_LISTBOX_DCLICK(self.panel.listbox_drugchoice,\
			self.id_map['listbox_drugchoice'],\
			self.listbox_drugchoice_list_box_double_clicked)

	def comboProduct_text_entered( self, event):
		pass

		print "comboProduct_text_entered received ", event
			

	def btnBookmark_button_clicked( self, event):
		pass

		print "btnBookmark_button_clicked received ", event
			

	def rbtnSearchAny_radiobutton_clicked( self, event):
		pass

		print "rbtnSearchAny_radiobutton_clicked received ", event
			

	def rbtnSearchBrand_radiobutton_clicked( self, event):
		pass

		print "rbtnSearchBrand_radiobutton_clicked received ", event
			

	def rbtnSearchGeneric_radiobutton_clicked( self, event):
		pass

		print "rbtnSearchGeneric_radiobutton_clicked received ", event
			

	def rbtnSearchIndication_radiobutton_clicked( self, event):
		pass

		print "rbtnSearchIndication_radiobutton_clicked received ", event
			

	def listbox_jumpto_list_box_single_clicked( self, event):
		pass

		print "listbox_jumpto_list_box_single_clicked received ", event
			

	def listbox_jumpto_list_box_double_clicked( self, event):
		pass

		print "listbox_jumpto_list_box_double_clicked received ", event
			

	def btnPrescribe_button_clicked( self, event):
		pass

		print "btnPrescribe_button_clicked received ", event
			

	def btnDisplay_button_clicked( self, event):
		pass

		print "btnDisplay_button_clicked received ", event
			

	def btnPrint_button_clicked( self, event):
		pass

		print "btnPrint_button_clicked received ", event
			

	def listbox_drugchoice_list_box_single_clicked( self, event):
		pass

		print "listbox_drugchoice_list_box_single_clicked received ", event
			

	def listbox_drugchoice_list_box_double_clicked( self, event):
		pass

		print "listbox_drugchoice_list_box_double_clicked received ", event
			
#creating a handler as gmGuidelines_handler from gui/gmGuidelines.py
# [('infoline', 'wxTextCtrl')]


class gmGuidelines_handler:

	def create_handler(self, panel):
		return gmGuidelines_handler(panel)

	def __init__(self, panel):
		self.panel = panel
		if panel <> None:
			self.__set_id()
			self.__set_evt()

	def __set_id(self):
		self.id_map = {}


		id = self.panel.infoline.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.infoline.SetId(id)
		self.id_map['infoline'] = id
		

	def __set_evt(self):
		pass
		

		EVT_TEXT(self.panel.infoline,\
			self.id_map['infoline'],\
			self.infoline_text_entered)

	def infoline_text_entered( self, event):
		pass

		print "infoline_text_entered received ", event
			
#creating a handler as gmLock_handler from gui/gmLock.py
# []
#creating a handler as gmManual_handler from gui/gmManual.py
# [('infoline', 'wxTextCtrl')]


class gmManual_handler:

	def create_handler(self, panel):
		return gmManual_handler(panel)

	def __init__(self, panel):
		self.panel = panel
		if panel <> None:
			self.__set_id()
			self.__set_evt()

	def __set_id(self):
		self.id_map = {}


		id = self.panel.infoline.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.infoline.SetId(id)
		self.id_map['infoline'] = id
		

	def __set_evt(self):
		pass
		

		EVT_TEXT(self.panel.infoline,\
			self.id_map['infoline'],\
			self.infoline_text_entered)

	def infoline_text_entered( self, event):
		pass

		print "infoline_text_entered received ", event
			
#creating a handler as gmOffice_handler from gui/gmOffice.py
# []
#creating a handler as gmPatientWindowManager_handler from gui/gmPatientWindowManager.py
# []
#creating a handler as gmPython_handler from gui/gmPython.py
# []
#creating a handler as gmSQL_handler from gui/gmSQL.py
# [('comboQueryInput', 'wxComboBox'), ('buttonRunQuery', 'wxButton'), ('buttonClearQuery', 'wxButton'), ('textQueryResults', 'wxTextCtrl')]


class gmSQL_handler:

	def create_handler(self, panel):
		return gmSQL_handler(panel)

	def __init__(self, panel):
		self.panel = panel
		if panel <> None:
			self.__set_id()
			self.__set_evt()

	def __set_id(self):
		self.id_map = {}


		id = self.panel.comboQueryInput.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.comboQueryInput.SetId(id)
		self.id_map['comboQueryInput'] = id
		

		id = self.panel.buttonRunQuery.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.buttonRunQuery.SetId(id)
		self.id_map['buttonRunQuery'] = id
		

		id = self.panel.buttonClearQuery.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.buttonClearQuery.SetId(id)
		self.id_map['buttonClearQuery'] = id
		

		id = self.panel.textQueryResults.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.textQueryResults.SetId(id)
		self.id_map['textQueryResults'] = id
		

	def __set_evt(self):
		pass
		

		EVT_TEXT(self.panel.comboQueryInput,\
			self.id_map['comboQueryInput'],\
			self.comboQueryInput_text_entered)

		EVT_BUTTON(self.panel.buttonRunQuery,\
			self.id_map['buttonRunQuery'],\
			self.buttonRunQuery_button_clicked)

		EVT_BUTTON(self.panel.buttonClearQuery,\
			self.id_map['buttonClearQuery'],\
			self.buttonClearQuery_button_clicked)

		EVT_TEXT(self.panel.textQueryResults,\
			self.id_map['textQueryResults'],\
			self.textQueryResults_text_entered)

	def comboQueryInput_text_entered( self, event):
		pass

		print "comboQueryInput_text_entered received ", event
			

	def buttonRunQuery_button_clicked( self, event):
		pass

		print "buttonRunQuery_button_clicked received ", event
			

	def buttonClearQuery_button_clicked( self, event):
		pass

		print "buttonClearQuery_button_clicked received ", event
			

	def textQueryResults_text_entered( self, event):
		pass

		print "textQueryResults_text_entered received ", event
			
#creating a handler as gmSnellen_handler from gui/gmSnellen.py
# [('mirror_ctrl', 'wxCheckBox')]


class gmSnellen_handler:

	def create_handler(self, panel):
		return gmSnellen_handler(panel)

	def __init__(self, panel):
		self.panel = panel
		if panel <> None:
			self.__set_id()
			self.__set_evt()

	def __set_id(self):
		self.id_map = {}


		id = self.panel.mirror_ctrl.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.mirror_ctrl.SetId(id)
		self.id_map['mirror_ctrl'] = id
		

	def __set_evt(self):
		pass
		

		EVT_CHECKBOX(self.panel.mirror_ctrl,\
			self.id_map['mirror_ctrl'],\
			self.mirror_ctrl_checkbox_clicked)

	def mirror_ctrl_checkbox_clicked( self, event):
		pass

		print "mirror_ctrl_checkbox_clicked received ", event
			
#creating a handler as gmStikoBrowser_handler from gui/gmStikoBrowser.py
# [('infoline', 'wxTextCtrl')]


class gmStikoBrowser_handler:

	def create_handler(self, panel):
		return gmStikoBrowser_handler(panel)

	def __init__(self, panel):
		self.panel = panel
		if panel <> None:
			self.__set_id()
			self.__set_evt()

	def __set_id(self):
		self.id_map = {}


		id = self.panel.infoline.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.infoline.SetId(id)
		self.id_map['infoline'] = id
		

	def __set_evt(self):
		pass
		

		EVT_TEXT(self.panel.infoline,\
			self.id_map['infoline'],\
			self.infoline_text_entered)

	def infoline_text_entered( self, event):
		pass

		print "infoline_text_entered received ", event
			
#creating a handler as gmplNbPatientSelector_handler from gui/gmplNbPatientSelector.py
# []
#creating a handler as gmplNbSchedule_handler from gui/gmplNbSchedule.py
# []
