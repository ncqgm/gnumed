# ['gmBMICalc.py', 'gmCalcPreg.py', 'gmCrypto.py', 'gmDemographics.py', 'gmGP_Allergies.py', 'gmGP_AnteNatal_3.py', 'gmGP_ClinicalSummary.py', 'gmGP_FamilyHistory.py', 'gmGP_Immunisation.py', 'gmGP_Measurements.py', 'gmGP_PastHistory.py', 'gmGP_Prescriptions.py', 'gmGP_Recalls.py', 'gmGP_Referrals.py', 'gmGP_Requests.py', 'gmGP_ScratchPadRecalls.py', 'gmGP_TabbedLists.py']

from wxPython.wx import * 
#creating a handler as gmBMICalc_handler from patient/gmBMICalc.py
# type_search_str =  class\s+(?P<new_type>\w+)\s*\(.*(?P<base_type>wxTextCtrl|wxComboBox|wxButton|wxRadioButton|wxCheckBox|wxListBox)
# [('txtHeight', 'wxTextCtrl')]


class gmBMICalc_handler:

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


		if self.panel.__dict__.has_key('txtHeight'):
			id = self.panel.txtHeight.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txtHeight.SetId(id)
			self.id_map['txtHeight'] = id
			

	def __set_evt(self):
		pass
		

		if self.panel.__dict__.has_key('txtHeight'):
			EVT_TEXT(self.panel.txtHeight,\
			self.id_map['txtHeight'],\
			self.txtHeight_text_entered)

	def txtHeight_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txtHeight_text_entered(self, event) 
			

		print "txtHeight_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['txtHeight']= obj.GetValue()
			print self.model['txtHeight']
		
#creating a handler as gmCalcPreg_handler from patient/gmCalcPreg.py
# []
#creating a handler as gmCrypto_handler from patient/gmCrypto.py
# []
#creating a handler as gmDemographics_handler from patient/gmDemographics.py
# found new type = TextBox_RedBold which is base_type wxTextCtrl

# found new type = TextBox_BlackNormal which is base_type wxTextCtrl

# [('addresslist', 'wxListBox'), ('combo_relationship', 'wxComboBox'), ('txt_surname', 'TextBox_RedBold'), ('combo_title', 'wxComboBox'), ('txt_firstname', 'TextBox_RedBold'), ('combo_sex', 'wxComboBox'), ('cb_preferredname', 'wxCheckBox'), ('txt_preferred', 'TextBox_RedBold'), ('txt_address', 'wxTextCtrl'), ('txt_suburb', 'TextBox_BlackNormal'), ('txt_zip', 'TextBox_BlackNormal'), ('txt_birthdate', 'TextBox_BlackNormal'), ('combo_maritalstatus', 'wxComboBox'), ('txt_occupation', 'TextBox_BlackNormal'), ('txt_countryofbirth', 'TextBox_BlackNormal'), ('btn_browseNOK', 'wxButton'), ('txt_nameNOK', 'wxTextCtrl'), ('txt_homephone', 'TextBox_BlackNormal'), ('txt_workphone', 'TextBox_BlackNormal'), ('txt_fax', 'TextBox_BlackNormal'), ('txt_email', 'TextBox_BlackNormal'), ('txt_web', 'TextBox_BlackNormal'), ('txt_mobile', 'TextBox_BlackNormal'), ('cb_addressresidence', 'wxCheckBox'), ('cb_addresspostal', 'wxCheckBox'), ('btn_photo_import', 'wxButton'), ('btn_photo_export', 'wxButton'), ('btn_photo_aquire', 'wxButton'), ('txt_findpatient', 'wxComboBox'), ('txt_age', 'wxTextCtrl'), ('txt_allergies', 'wxTextCtrl'), ('combo_consultation_type', 'wxComboBox')]


class gmDemographics_handler:

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


		if self.panel.__dict__.has_key('addresslist'):
			id = self.panel.addresslist.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.addresslist.SetId(id)
			self.id_map['addresslist'] = id
			

		if self.panel.__dict__.has_key('combo_relationship'):
			id = self.panel.combo_relationship.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.combo_relationship.SetId(id)
			self.id_map['combo_relationship'] = id
			

		if self.panel.__dict__.has_key('txt_surname'):
			id = self.panel.txt_surname.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_surname.SetId(id)
			self.id_map['txt_surname'] = id
			

		if self.panel.__dict__.has_key('combo_title'):
			id = self.panel.combo_title.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.combo_title.SetId(id)
			self.id_map['combo_title'] = id
			

		if self.panel.__dict__.has_key('txt_firstname'):
			id = self.panel.txt_firstname.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_firstname.SetId(id)
			self.id_map['txt_firstname'] = id
			

		if self.panel.__dict__.has_key('combo_sex'):
			id = self.panel.combo_sex.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.combo_sex.SetId(id)
			self.id_map['combo_sex'] = id
			

		if self.panel.__dict__.has_key('cb_preferredname'):
			id = self.panel.cb_preferredname.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.cb_preferredname.SetId(id)
			self.id_map['cb_preferredname'] = id
			

		if self.panel.__dict__.has_key('txt_preferred'):
			id = self.panel.txt_preferred.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_preferred.SetId(id)
			self.id_map['txt_preferred'] = id
			

		if self.panel.__dict__.has_key('txt_address'):
			id = self.panel.txt_address.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_address.SetId(id)
			self.id_map['txt_address'] = id
			

		if self.panel.__dict__.has_key('txt_suburb'):
			id = self.panel.txt_suburb.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_suburb.SetId(id)
			self.id_map['txt_suburb'] = id
			

		if self.panel.__dict__.has_key('txt_zip'):
			id = self.panel.txt_zip.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_zip.SetId(id)
			self.id_map['txt_zip'] = id
			

		if self.panel.__dict__.has_key('txt_birthdate'):
			id = self.panel.txt_birthdate.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_birthdate.SetId(id)
			self.id_map['txt_birthdate'] = id
			

		if self.panel.__dict__.has_key('combo_maritalstatus'):
			id = self.panel.combo_maritalstatus.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.combo_maritalstatus.SetId(id)
			self.id_map['combo_maritalstatus'] = id
			

		if self.panel.__dict__.has_key('txt_occupation'):
			id = self.panel.txt_occupation.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_occupation.SetId(id)
			self.id_map['txt_occupation'] = id
			

		if self.panel.__dict__.has_key('txt_countryofbirth'):
			id = self.panel.txt_countryofbirth.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_countryofbirth.SetId(id)
			self.id_map['txt_countryofbirth'] = id
			

		if self.panel.__dict__.has_key('btn_browseNOK'):
			id = self.panel.btn_browseNOK.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.btn_browseNOK.SetId(id)
			self.id_map['btn_browseNOK'] = id
			

		if self.panel.__dict__.has_key('txt_nameNOK'):
			id = self.panel.txt_nameNOK.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_nameNOK.SetId(id)
			self.id_map['txt_nameNOK'] = id
			

		if self.panel.__dict__.has_key('txt_homephone'):
			id = self.panel.txt_homephone.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_homephone.SetId(id)
			self.id_map['txt_homephone'] = id
			

		if self.panel.__dict__.has_key('txt_workphone'):
			id = self.panel.txt_workphone.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_workphone.SetId(id)
			self.id_map['txt_workphone'] = id
			

		if self.panel.__dict__.has_key('txt_fax'):
			id = self.panel.txt_fax.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_fax.SetId(id)
			self.id_map['txt_fax'] = id
			

		if self.panel.__dict__.has_key('txt_email'):
			id = self.panel.txt_email.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_email.SetId(id)
			self.id_map['txt_email'] = id
			

		if self.panel.__dict__.has_key('txt_web'):
			id = self.panel.txt_web.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_web.SetId(id)
			self.id_map['txt_web'] = id
			

		if self.panel.__dict__.has_key('txt_mobile'):
			id = self.panel.txt_mobile.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_mobile.SetId(id)
			self.id_map['txt_mobile'] = id
			

		if self.panel.__dict__.has_key('cb_addressresidence'):
			id = self.panel.cb_addressresidence.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.cb_addressresidence.SetId(id)
			self.id_map['cb_addressresidence'] = id
			

		if self.panel.__dict__.has_key('cb_addresspostal'):
			id = self.panel.cb_addresspostal.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.cb_addresspostal.SetId(id)
			self.id_map['cb_addresspostal'] = id
			

		if self.panel.__dict__.has_key('btn_photo_import'):
			id = self.panel.btn_photo_import.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.btn_photo_import.SetId(id)
			self.id_map['btn_photo_import'] = id
			

		if self.panel.__dict__.has_key('btn_photo_export'):
			id = self.panel.btn_photo_export.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.btn_photo_export.SetId(id)
			self.id_map['btn_photo_export'] = id
			

		if self.panel.__dict__.has_key('btn_photo_aquire'):
			id = self.panel.btn_photo_aquire.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.btn_photo_aquire.SetId(id)
			self.id_map['btn_photo_aquire'] = id
			

		if self.panel.__dict__.has_key('txt_findpatient'):
			id = self.panel.txt_findpatient.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_findpatient.SetId(id)
			self.id_map['txt_findpatient'] = id
			

		if self.panel.__dict__.has_key('txt_age'):
			id = self.panel.txt_age.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_age.SetId(id)
			self.id_map['txt_age'] = id
			

		if self.panel.__dict__.has_key('txt_allergies'):
			id = self.panel.txt_allergies.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_allergies.SetId(id)
			self.id_map['txt_allergies'] = id
			

		if self.panel.__dict__.has_key('combo_consultation_type'):
			id = self.panel.combo_consultation_type.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.combo_consultation_type.SetId(id)
			self.id_map['combo_consultation_type'] = id
			

	def __set_evt(self):
		pass
		

		if self.panel.__dict__.has_key('addresslist'):
			EVT_LISTBOX(self.panel.addresslist,\
			self.id_map['addresslist'],\
			self.addresslist_list_box_single_clicked)

		if self.panel.__dict__.has_key('addresslist'):
			EVT_LISTBOX_DCLICK(self.panel.addresslist,\
			self.id_map['addresslist'],\
			self.addresslist_list_box_double_clicked)

		if self.panel.__dict__.has_key('combo_relationship'):
			EVT_TEXT(self.panel.combo_relationship,\
			self.id_map['combo_relationship'],\
			self.combo_relationship_text_entered)

		if self.panel.__dict__.has_key('txt_surname'):
			EVT_TEXT(self.panel.txt_surname,\
			self.id_map['txt_surname'],\
			self.txt_surname_text_entered)

		if self.panel.__dict__.has_key('combo_title'):
			EVT_TEXT(self.panel.combo_title,\
			self.id_map['combo_title'],\
			self.combo_title_text_entered)

		if self.panel.__dict__.has_key('txt_firstname'):
			EVT_TEXT(self.panel.txt_firstname,\
			self.id_map['txt_firstname'],\
			self.txt_firstname_text_entered)

		if self.panel.__dict__.has_key('combo_sex'):
			EVT_TEXT(self.panel.combo_sex,\
			self.id_map['combo_sex'],\
			self.combo_sex_text_entered)

		if self.panel.__dict__.has_key('cb_preferredname'):
			EVT_CHECKBOX(self.panel.cb_preferredname,\
			self.id_map['cb_preferredname'],\
			self.cb_preferredname_checkbox_clicked)

		if self.panel.__dict__.has_key('txt_preferred'):
			EVT_TEXT(self.panel.txt_preferred,\
			self.id_map['txt_preferred'],\
			self.txt_preferred_text_entered)

		if self.panel.__dict__.has_key('txt_address'):
			EVT_TEXT(self.panel.txt_address,\
			self.id_map['txt_address'],\
			self.txt_address_text_entered)

		if self.panel.__dict__.has_key('txt_suburb'):
			EVT_TEXT(self.panel.txt_suburb,\
			self.id_map['txt_suburb'],\
			self.txt_suburb_text_entered)

		if self.panel.__dict__.has_key('txt_zip'):
			EVT_TEXT(self.panel.txt_zip,\
			self.id_map['txt_zip'],\
			self.txt_zip_text_entered)

		if self.panel.__dict__.has_key('txt_birthdate'):
			EVT_TEXT(self.panel.txt_birthdate,\
			self.id_map['txt_birthdate'],\
			self.txt_birthdate_text_entered)

		if self.panel.__dict__.has_key('combo_maritalstatus'):
			EVT_TEXT(self.panel.combo_maritalstatus,\
			self.id_map['combo_maritalstatus'],\
			self.combo_maritalstatus_text_entered)

		if self.panel.__dict__.has_key('txt_occupation'):
			EVT_TEXT(self.panel.txt_occupation,\
			self.id_map['txt_occupation'],\
			self.txt_occupation_text_entered)

		if self.panel.__dict__.has_key('txt_countryofbirth'):
			EVT_TEXT(self.panel.txt_countryofbirth,\
			self.id_map['txt_countryofbirth'],\
			self.txt_countryofbirth_text_entered)

		if self.panel.__dict__.has_key('btn_browseNOK'):
			EVT_BUTTON(self.panel.btn_browseNOK,\
			self.id_map['btn_browseNOK'],\
			self.btn_browseNOK_button_clicked)

		if self.panel.__dict__.has_key('txt_nameNOK'):
			EVT_TEXT(self.panel.txt_nameNOK,\
			self.id_map['txt_nameNOK'],\
			self.txt_nameNOK_text_entered)

		if self.panel.__dict__.has_key('txt_homephone'):
			EVT_TEXT(self.panel.txt_homephone,\
			self.id_map['txt_homephone'],\
			self.txt_homephone_text_entered)

		if self.panel.__dict__.has_key('txt_workphone'):
			EVT_TEXT(self.panel.txt_workphone,\
			self.id_map['txt_workphone'],\
			self.txt_workphone_text_entered)

		if self.panel.__dict__.has_key('txt_fax'):
			EVT_TEXT(self.panel.txt_fax,\
			self.id_map['txt_fax'],\
			self.txt_fax_text_entered)

		if self.panel.__dict__.has_key('txt_email'):
			EVT_TEXT(self.panel.txt_email,\
			self.id_map['txt_email'],\
			self.txt_email_text_entered)

		if self.panel.__dict__.has_key('txt_web'):
			EVT_TEXT(self.panel.txt_web,\
			self.id_map['txt_web'],\
			self.txt_web_text_entered)

		if self.panel.__dict__.has_key('txt_mobile'):
			EVT_TEXT(self.panel.txt_mobile,\
			self.id_map['txt_mobile'],\
			self.txt_mobile_text_entered)

		if self.panel.__dict__.has_key('cb_addressresidence'):
			EVT_CHECKBOX(self.panel.cb_addressresidence,\
			self.id_map['cb_addressresidence'],\
			self.cb_addressresidence_checkbox_clicked)

		if self.panel.__dict__.has_key('cb_addresspostal'):
			EVT_CHECKBOX(self.panel.cb_addresspostal,\
			self.id_map['cb_addresspostal'],\
			self.cb_addresspostal_checkbox_clicked)

		if self.panel.__dict__.has_key('btn_photo_import'):
			EVT_BUTTON(self.panel.btn_photo_import,\
			self.id_map['btn_photo_import'],\
			self.btn_photo_import_button_clicked)

		if self.panel.__dict__.has_key('btn_photo_export'):
			EVT_BUTTON(self.panel.btn_photo_export,\
			self.id_map['btn_photo_export'],\
			self.btn_photo_export_button_clicked)

		if self.panel.__dict__.has_key('btn_photo_aquire'):
			EVT_BUTTON(self.panel.btn_photo_aquire,\
			self.id_map['btn_photo_aquire'],\
			self.btn_photo_aquire_button_clicked)

		if self.panel.__dict__.has_key('txt_findpatient'):
			EVT_TEXT(self.panel.txt_findpatient,\
			self.id_map['txt_findpatient'],\
			self.txt_findpatient_text_entered)

		if self.panel.__dict__.has_key('txt_age'):
			EVT_TEXT(self.panel.txt_age,\
			self.id_map['txt_age'],\
			self.txt_age_text_entered)

		if self.panel.__dict__.has_key('txt_allergies'):
			EVT_TEXT(self.panel.txt_allergies,\
			self.id_map['txt_allergies'],\
			self.txt_allergies_text_entered)

		if self.panel.__dict__.has_key('combo_consultation_type'):
			EVT_TEXT(self.panel.combo_consultation_type,\
			self.id_map['combo_consultation_type'],\
			self.combo_consultation_type_text_entered)

	def addresslist_list_box_single_clicked( self, event): 
		if self.impl <> None:
			self.impl.addresslist_list_box_single_clicked(self, event) 
			

		print "addresslist_list_box_single_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['addresslist']= obj.GetStringSelection()
			print self.model['addresslist']
		

	def addresslist_list_box_double_clicked( self, event): 
		if self.impl <> None:
			self.impl.addresslist_list_box_double_clicked(self, event) 
			

		print "addresslist_list_box_double_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['addresslist']= obj.GetStringSelection()
			print self.model['addresslist']
		

	def combo_relationship_text_entered( self, event): 
		if self.impl <> None:
			self.impl.combo_relationship_text_entered(self, event) 
			

		print "combo_relationship_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['relationship']= obj.GetValue()
			print self.model['relationship']
		

	def txt_surname_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_surname_text_entered(self, event) 
			

		print "txt_surname_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['surname']= obj.GetValue()
			print self.model['surname']
		

	def combo_title_text_entered( self, event): 
		if self.impl <> None:
			self.impl.combo_title_text_entered(self, event) 
			

		print "combo_title_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['title']= obj.GetValue()
			print self.model['title']
		

	def txt_firstname_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_firstname_text_entered(self, event) 
			

		print "txt_firstname_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['firstname']= obj.GetValue()
			print self.model['firstname']
		

	def combo_sex_text_entered( self, event): 
		if self.impl <> None:
			self.impl.combo_sex_text_entered(self, event) 
			

		print "combo_sex_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['sex']= obj.GetValue()
			print self.model['sex']
		

	def cb_preferredname_checkbox_clicked( self, event): 
		if self.impl <> None:
			self.impl.cb_preferredname_checkbox_clicked(self, event) 
			

		print "cb_preferredname_checkbox_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['preferredname']= obj.GetValue()
			print self.model['preferredname']
		

	def txt_preferred_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_preferred_text_entered(self, event) 
			

		print "txt_preferred_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['preferred']= obj.GetValue()
			print self.model['preferred']
		

	def txt_address_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_address_text_entered(self, event) 
			

		print "txt_address_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['address']= obj.GetValue()
			print self.model['address']
		

	def txt_suburb_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_suburb_text_entered(self, event) 
			

		print "txt_suburb_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['suburb']= obj.GetValue()
			print self.model['suburb']
		

	def txt_zip_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_zip_text_entered(self, event) 
			

		print "txt_zip_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['zip']= obj.GetValue()
			print self.model['zip']
		

	def txt_birthdate_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_birthdate_text_entered(self, event) 
			

		print "txt_birthdate_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['birthdate']= obj.GetValue()
			print self.model['birthdate']
		

	def combo_maritalstatus_text_entered( self, event): 
		if self.impl <> None:
			self.impl.combo_maritalstatus_text_entered(self, event) 
			

		print "combo_maritalstatus_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['maritalstatus']= obj.GetValue()
			print self.model['maritalstatus']
		

	def txt_occupation_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_occupation_text_entered(self, event) 
			

		print "txt_occupation_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['occupation']= obj.GetValue()
			print self.model['occupation']
		

	def txt_countryofbirth_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_countryofbirth_text_entered(self, event) 
			

		print "txt_countryofbirth_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['countryofbirth']= obj.GetValue()
			print self.model['countryofbirth']
		

	def btn_browseNOK_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btn_browseNOK_button_clicked(self, event) 
			

		print "btn_browseNOK_button_clicked received ", event
			

	def txt_nameNOK_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_nameNOK_text_entered(self, event) 
			

		print "txt_nameNOK_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['nameNOK']= obj.GetValue()
			print self.model['nameNOK']
		

	def txt_homephone_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_homephone_text_entered(self, event) 
			

		print "txt_homephone_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['homephone']= obj.GetValue()
			print self.model['homephone']
		

	def txt_workphone_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_workphone_text_entered(self, event) 
			

		print "txt_workphone_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['workphone']= obj.GetValue()
			print self.model['workphone']
		

	def txt_fax_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_fax_text_entered(self, event) 
			

		print "txt_fax_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['fax']= obj.GetValue()
			print self.model['fax']
		

	def txt_email_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_email_text_entered(self, event) 
			

		print "txt_email_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['email']= obj.GetValue()
			print self.model['email']
		

	def txt_web_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_web_text_entered(self, event) 
			

		print "txt_web_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['web']= obj.GetValue()
			print self.model['web']
		

	def txt_mobile_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_mobile_text_entered(self, event) 
			

		print "txt_mobile_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['mobile']= obj.GetValue()
			print self.model['mobile']
		

	def cb_addressresidence_checkbox_clicked( self, event): 
		if self.impl <> None:
			self.impl.cb_addressresidence_checkbox_clicked(self, event) 
			

		print "cb_addressresidence_checkbox_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['addressresidence']= obj.GetValue()
			print self.model['addressresidence']
		

	def cb_addresspostal_checkbox_clicked( self, event): 
		if self.impl <> None:
			self.impl.cb_addresspostal_checkbox_clicked(self, event) 
			

		print "cb_addresspostal_checkbox_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['addresspostal']= obj.GetValue()
			print self.model['addresspostal']
		

	def btn_photo_import_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btn_photo_import_button_clicked(self, event) 
			

		print "btn_photo_import_button_clicked received ", event
			

	def btn_photo_export_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btn_photo_export_button_clicked(self, event) 
			

		print "btn_photo_export_button_clicked received ", event
			

	def btn_photo_aquire_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btn_photo_aquire_button_clicked(self, event) 
			

		print "btn_photo_aquire_button_clicked received ", event
			

	def txt_findpatient_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_findpatient_text_entered(self, event) 
			

		print "txt_findpatient_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['findpatient']= obj.GetValue()
			print self.model['findpatient']
		

	def txt_age_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_age_text_entered(self, event) 
			

		print "txt_age_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['age']= obj.GetValue()
			print self.model['age']
		

	def txt_allergies_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_allergies_text_entered(self, event) 
			

		print "txt_allergies_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['allergies']= obj.GetValue()
			print self.model['allergies']
		

	def combo_consultation_type_text_entered( self, event): 
		if self.impl <> None:
			self.impl.combo_consultation_type_text_entered(self, event) 
			

		print "combo_consultation_type_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['consultation_type']= obj.GetValue()
			print self.model['consultation_type']
		
#creating a handler as gmGP_Allergies_handler from patient/gmGP_Allergies.py
# [('classtxt', 'wxTextCtrl')]


class gmGP_Allergies_handler:

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


		if self.panel.__dict__.has_key('classtxt'):
			id = self.panel.classtxt.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.classtxt.SetId(id)
			self.id_map['classtxt'] = id
			

	def __set_evt(self):
		pass
		

		if self.panel.__dict__.has_key('classtxt'):
			EVT_TEXT(self.panel.classtxt,\
			self.id_map['classtxt'],\
			self.classtxt_text_entered)

	def classtxt_text_entered( self, event): 
		if self.impl <> None:
			self.impl.classtxt_text_entered(self, event) 
			

		print "classtxt_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['classtxt']= obj.GetValue()
			print self.model['classtxt']
		
#creating a handler as gmGP_AnteNatal_3_handler from patient/gmGP_AnteNatal_3.py
# []
#creating a handler as gmGP_ClinicalSummary_handler from patient/gmGP_ClinicalSummary.py
# []
#creating a handler as gmGP_FamilyHistory_handler from patient/gmGP_FamilyHistory.py
# [('txt_social_history', 'wxTextCtrl')]


class gmGP_FamilyHistory_handler:

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


		if self.panel.__dict__.has_key('txt_social_history'):
			id = self.panel.txt_social_history.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_social_history.SetId(id)
			self.id_map['txt_social_history'] = id
			

	def __set_evt(self):
		pass
		

		if self.panel.__dict__.has_key('txt_social_history'):
			EVT_TEXT(self.panel.txt_social_history,\
			self.id_map['txt_social_history'],\
			self.txt_social_history_text_entered)

	def txt_social_history_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_social_history_text_entered(self, event) 
			

		print "txt_social_history_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['social_history']= obj.GetValue()
			print self.model['social_history']
		
#creating a handler as gmGP_Immunisation_handler from patient/gmGP_Immunisation.py
# [('missingimmunisation_listbox', 'wxListBox')]


class gmGP_Immunisation_handler:

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


		if self.panel.__dict__.has_key('missingimmunisation_listbox'):
			id = self.panel.missingimmunisation_listbox.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.missingimmunisation_listbox.SetId(id)
			self.id_map['missingimmunisation_listbox'] = id
			

	def __set_evt(self):
		pass
		

		if self.panel.__dict__.has_key('missingimmunisation_listbox'):
			EVT_LISTBOX(self.panel.missingimmunisation_listbox,\
			self.id_map['missingimmunisation_listbox'],\
			self.missingimmunisation_listbox_list_box_single_clicked)

		if self.panel.__dict__.has_key('missingimmunisation_listbox'):
			EVT_LISTBOX_DCLICK(self.panel.missingimmunisation_listbox,\
			self.id_map['missingimmunisation_listbox'],\
			self.missingimmunisation_listbox_list_box_double_clicked)

	def missingimmunisation_listbox_list_box_single_clicked( self, event): 
		if self.impl <> None:
			self.impl.missingimmunisation_listbox_list_box_single_clicked(self, event) 
			

		print "missingimmunisation_listbox_list_box_single_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['listbox']= obj.GetStringSelection()
			print self.model['listbox']
		

	def missingimmunisation_listbox_list_box_double_clicked( self, event): 
		if self.impl <> None:
			self.impl.missingimmunisation_listbox_list_box_double_clicked(self, event) 
			

		print "missingimmunisation_listbox_list_box_double_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['listbox']= obj.GetStringSelection()
			print self.model['listbox']
		
#creating a handler as gmGP_Measurements_handler from patient/gmGP_Measurements.py
# []
#creating a handler as gmGP_PastHistory_handler from patient/gmGP_PastHistory.py
# []
#creating a handler as gmGP_Prescriptions_handler from patient/gmGP_Prescriptions.py
# [('txt_scriptDate', 'wxTextCtrl'), ('interactiontxt', 'wxTextCtrl')]


class gmGP_Prescriptions_handler:

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


		if self.panel.__dict__.has_key('txt_scriptDate'):
			id = self.panel.txt_scriptDate.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_scriptDate.SetId(id)
			self.id_map['txt_scriptDate'] = id
			

		if self.panel.__dict__.has_key('interactiontxt'):
			id = self.panel.interactiontxt.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.interactiontxt.SetId(id)
			self.id_map['interactiontxt'] = id
			

	def __set_evt(self):
		pass
		

		if self.panel.__dict__.has_key('txt_scriptDate'):
			EVT_TEXT(self.panel.txt_scriptDate,\
			self.id_map['txt_scriptDate'],\
			self.txt_scriptDate_text_entered)

		if self.panel.__dict__.has_key('interactiontxt'):
			EVT_TEXT(self.panel.interactiontxt,\
			self.id_map['interactiontxt'],\
			self.interactiontxt_text_entered)

	def txt_scriptDate_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_scriptDate_text_entered(self, event) 
			

		print "txt_scriptDate_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['scriptDate']= obj.GetValue()
			print self.model['scriptDate']
		

	def interactiontxt_text_entered( self, event): 
		if self.impl <> None:
			self.impl.interactiontxt_text_entered(self, event) 
			

		print "interactiontxt_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['interactiontxt']= obj.GetValue()
			print self.model['interactiontxt']
		
#creating a handler as gmGP_Recalls_handler from patient/gmGP_Recalls.py
# []
#creating a handler as gmGP_Referrals_handler from patient/gmGP_Referrals.py
# [('txt_referraldate', 'wxTextCtrl'), ('txt_referral_letter', 'wxTextCtrl')]


class gmGP_Referrals_handler:

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


		if self.panel.__dict__.has_key('txt_referraldate'):
			id = self.panel.txt_referraldate.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_referraldate.SetId(id)
			self.id_map['txt_referraldate'] = id
			

		if self.panel.__dict__.has_key('txt_referral_letter'):
			id = self.panel.txt_referral_letter.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_referral_letter.SetId(id)
			self.id_map['txt_referral_letter'] = id
			

	def __set_evt(self):
		pass
		

		if self.panel.__dict__.has_key('txt_referraldate'):
			EVT_TEXT(self.panel.txt_referraldate,\
			self.id_map['txt_referraldate'],\
			self.txt_referraldate_text_entered)

		if self.panel.__dict__.has_key('txt_referral_letter'):
			EVT_TEXT(self.panel.txt_referral_letter,\
			self.id_map['txt_referral_letter'],\
			self.txt_referral_letter_text_entered)

	def txt_referraldate_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_referraldate_text_entered(self, event) 
			

		print "txt_referraldate_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['referraldate']= obj.GetValue()
			print self.model['referraldate']
		

	def txt_referral_letter_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_referral_letter_text_entered(self, event) 
			

		print "txt_referral_letter_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['referral_letter']= obj.GetValue()
			print self.model['referral_letter']
		
#creating a handler as gmGP_Requests_handler from patient/gmGP_Requests.py
# [('txt_requestDate', 'wxTextCtrl')]


class gmGP_Requests_handler:

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


		if self.panel.__dict__.has_key('txt_requestDate'):
			id = self.panel.txt_requestDate.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.txt_requestDate.SetId(id)
			self.id_map['txt_requestDate'] = id
			

	def __set_evt(self):
		pass
		

		if self.panel.__dict__.has_key('txt_requestDate'):
			EVT_TEXT(self.panel.txt_requestDate,\
			self.id_map['txt_requestDate'],\
			self.txt_requestDate_text_entered)

	def txt_requestDate_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_requestDate_text_entered(self, event) 
			

		print "txt_requestDate_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['requestDate']= obj.GetValue()
			print self.model['requestDate']
		
#creating a handler as gmGP_ScratchPadRecalls_handler from patient/gmGP_ScratchPadRecalls.py
# [('scratchpad_txt', 'wxTextCtrl')]


class gmGP_ScratchPadRecalls_handler:

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


		if self.panel.__dict__.has_key('scratchpad_txt'):
			id = self.panel.scratchpad_txt.GetId()
			if id  <= 0:
				id = wxNewId()
				self.panel.scratchpad_txt.SetId(id)
			self.id_map['scratchpad_txt'] = id
			

	def __set_evt(self):
		pass
		

		if self.panel.__dict__.has_key('scratchpad_txt'):
			EVT_TEXT(self.panel.scratchpad_txt,\
			self.id_map['scratchpad_txt'],\
			self.scratchpad_txt_text_entered)

	def scratchpad_txt_text_entered( self, event): 
		if self.impl <> None:
			self.impl.scratchpad_txt_text_entered(self, event) 
			

		print "scratchpad_txt_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			self.model['txt']= obj.GetValue()
			print self.model['txt']
		
#creating a handler as gmGP_TabbedLists_handler from patient/gmGP_TabbedLists.py
# []
