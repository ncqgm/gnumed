# ['gmBMICalc.py', 'gmCalcPreg.py', 'gmCrypto.py', 'gmDemographics.py', 'gmGP_Allergies.py', 'gmGP_AnteNatal_3.py', 'gmGP_ClinicalSummary.py', 'gmGP_FamilyHistory.py', 'gmGP_Immunisation.py', 'gmGP_Measurements.py', 'gmGP_PastHistory.py', 'gmGP_Prescriptions.py', 'gmGP_Recalls.py', 'gmGP_Referrals.py', 'gmGP_Requests.py', 'gmGP_ScratchPadRecalls.py', 'gmGP_TabbedLists.py']

from wxPython.wx import * 


class base_handler:

	def create_handler(self, panel, model = None):
		if model == None and self.model <> None:
			model = self.model
			
		return  self.__init__(panel, model, self.impl)

	def __init__(self, panel, model = None, impl = None):
		self.panel = panel
		self.impl = impl	
		if panel <> None:
			self.set_id()
			self.set_evt()
			self.set_name_map()	

		self.set_model(model)
			
	def set_id(self):
		# pure virtual
		pass
	
	def set_evt(self):
		# pure virtual
		pass

	def set_name_map(self):
		# implement in subclasses,ie. pure virtual(c++) or abstact method( java)
		pass
		
	def set_model(self,  model):
		if model == None:
			self.model ={}
			return
		
		self.model = model
		
		
		if  len(model) > 0 and self.panel <> None:
			self.update_ui(model)
			
	def update_ui(self, model):
		
		if not  self.__dict__.has_key('name_map'):
			return
		if self.name_map == None:
			return
		
		for k in model.keys():
			v = model[k]
			map = self.name_map.get( k, None)
			if map == None:
				continue
			print "comp map = ", map
			setter = map.get('setter_name', None)
			if setter == None:
				continue
			component = map.get('comp_name')
			if component ==  None:
				continue
			
			#setter(component, v)
			try:
				exec( 'self.panel.%s.%s("%s")' % ( component, setter, v) )
			except:
				try:
					exec( 'self.panel.%s.%s(%s)' % ( component, setter, v) )
				except:
					print 'failed to set',component,setter,  v
			
			
		
	def set_impl(self, impl):
		self.impl = impl
		
	def get_valid_component( self , key):
		if self.panel.__dict__.has_key(key):
			return self.panel.__dict__[key]
		return None

	def get_valid_func( self, key , func):
		component =  self.get_valid_component(key)
		if component == None:
			return None
		if component.__class__.__dict__.has_key(func):
			return component.__class__.__dict__[func]
		else:
			print "unable to find ", func, "in component.class ", component.__class__.__name__
		return None

	def set_id_common(self, name ,  control ):
		id = control.GetId()
		if id <= 0:
			id = wxNewId()
			control.SetId(id)
		self.id_map[name] = id

		
	
#creating a handler as gmBMICalc_handler from patient/gmBMICalc.py
# type_search_str =  class\s+(?P<new_type>\w+)\s*\(.*(?P<base_type>wxTextCtrl|wxComboBox|wxButton|wxRadioButton|wxCheckBox|wxListBox)
# [('txtHeight', 'wxTextCtrl')]

class gmBMICalc_handler(base_handler):
	
	def __init__(self, panel, model = None, impl = None):
		base_handler.__init__(self, panel, model, impl)
		

	def set_name_map(self):
		map = {}
		
 
		comp_map = { 'component': self.get_valid_component('txtHeight') ,
			'setter': self.get_valid_func( 'txtHeight', 'SetValue')  ,
			'comp_name' : 'txtHeight','setter_name' :  'SetValue' } 
		map['txtHeight'] = comp_map
		

		self.name_map = map
	

	def set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('txtHeight'):
			self.set_id_common( 'txtHeight',self.panel.txtHeight)
			

	def set_evt(self):
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
			try :
				self.model['txtHeight']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['txtHeight'] = str(obj.GetValue())
				
			print self.model, "txtHeight = ",  self.model['txtHeight']
		
#creating a handler as gmCalcPreg_handler from patient/gmCalcPreg.py
# []
#creating a handler as gmCrypto_handler from patient/gmCrypto.py
# []
#creating a handler as gmDemographics_handler from patient/gmDemographics.py
# found new type = TextBox_RedBold which is base_type wxTextCtrl

# found new type = TextBox_BlackNormal which is base_type wxTextCtrl

# [('addresslist', 'wxListBox'), ('combo_relationship', 'wxComboBox'), ('txt_surname', 'TextBox_RedBold'), ('combo_title', 'wxComboBox'), ('txt_firstname', 'TextBox_RedBold'), ('combo_sex', 'wxComboBox'), ('cb_preferredname', 'wxCheckBox'), ('txt_preferred', 'TextBox_RedBold'), ('txt_address', 'wxTextCtrl'), ('txt_suburb', 'TextBox_BlackNormal'), ('txt_zip', 'TextBox_BlackNormal'), ('txt_birthdate', 'TextBox_BlackNormal'), ('combo_maritalstatus', 'wxComboBox'), ('txt_occupation', 'TextBox_BlackNormal'), ('txt_countryofbirth', 'TextBox_BlackNormal'), ('btn_browseNOK', 'wxButton'), ('txt_nameNOK', 'wxTextCtrl'), ('txt_homephone', 'TextBox_BlackNormal'), ('txt_workphone', 'TextBox_BlackNormal'), ('txt_fax', 'TextBox_BlackNormal'), ('txt_email', 'TextBox_BlackNormal'), ('txt_web', 'TextBox_BlackNormal'), ('txt_mobile', 'TextBox_BlackNormal'), ('cb_addressresidence', 'wxCheckBox'), ('cb_addresspostal', 'wxCheckBox'), ('btn_photo_import', 'wxButton'), ('btn_photo_export', 'wxButton'), ('btn_photo_aquire', 'wxButton'), ('txt_findpatient', 'wxComboBox'), ('txt_age', 'wxTextCtrl'), ('txt_allergies', 'wxTextCtrl'), ('combo_consultation_type', 'wxComboBox')]

class gmDemographics_handler(base_handler):
	
	def __init__(self, panel, model = None, impl = None):
		base_handler.__init__(self, panel, model, impl)
		

	def set_name_map(self):
		map = {}
		
 
		comp_map = { 'component': self.get_valid_component('addresslist') ,
			'setter': self.get_valid_func( 'addresslist', 'SetStringSelection')  ,
			'comp_name' : 'addresslist','setter_name' :  'SetStringSelection' } 
		map['addresslist'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('addresslist') ,
			'setter': self.get_valid_func( 'addresslist', 'SetStringSelection')  ,
			'comp_name' : 'addresslist','setter_name' :  'SetStringSelection' } 
		map['addresslist'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('combo_relationship') ,
			'setter': self.get_valid_func( 'combo_relationship', 'SetValue')  ,
			'comp_name' : 'combo_relationship','setter_name' :  'SetValue' } 
		map['relationship'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_surname') ,
			'setter': self.get_valid_func( 'txt_surname', 'SetValue')  ,
			'comp_name' : 'txt_surname','setter_name' :  'SetValue' } 
		map['surname'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('combo_title') ,
			'setter': self.get_valid_func( 'combo_title', 'SetValue')  ,
			'comp_name' : 'combo_title','setter_name' :  'SetValue' } 
		map['title'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_firstname') ,
			'setter': self.get_valid_func( 'txt_firstname', 'SetValue')  ,
			'comp_name' : 'txt_firstname','setter_name' :  'SetValue' } 
		map['firstname'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('combo_sex') ,
			'setter': self.get_valid_func( 'combo_sex', 'SetValue')  ,
			'comp_name' : 'combo_sex','setter_name' :  'SetValue' } 
		map['sex'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('cb_preferredname') ,
			'setter': self.get_valid_func( 'cb_preferredname', 'SetValue')  ,
			'comp_name' : 'cb_preferredname','setter_name' :  'SetValue' } 
		map['preferredname'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_preferred') ,
			'setter': self.get_valid_func( 'txt_preferred', 'SetValue')  ,
			'comp_name' : 'txt_preferred','setter_name' :  'SetValue' } 
		map['preferred'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_address') ,
			'setter': self.get_valid_func( 'txt_address', 'SetValue')  ,
			'comp_name' : 'txt_address','setter_name' :  'SetValue' } 
		map['address'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_suburb') ,
			'setter': self.get_valid_func( 'txt_suburb', 'SetValue')  ,
			'comp_name' : 'txt_suburb','setter_name' :  'SetValue' } 
		map['suburb'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_zip') ,
			'setter': self.get_valid_func( 'txt_zip', 'SetValue')  ,
			'comp_name' : 'txt_zip','setter_name' :  'SetValue' } 
		map['zip'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_birthdate') ,
			'setter': self.get_valid_func( 'txt_birthdate', 'SetValue')  ,
			'comp_name' : 'txt_birthdate','setter_name' :  'SetValue' } 
		map['birthdate'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('combo_maritalstatus') ,
			'setter': self.get_valid_func( 'combo_maritalstatus', 'SetValue')  ,
			'comp_name' : 'combo_maritalstatus','setter_name' :  'SetValue' } 
		map['maritalstatus'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_occupation') ,
			'setter': self.get_valid_func( 'txt_occupation', 'SetValue')  ,
			'comp_name' : 'txt_occupation','setter_name' :  'SetValue' } 
		map['occupation'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_countryofbirth') ,
			'setter': self.get_valid_func( 'txt_countryofbirth', 'SetValue')  ,
			'comp_name' : 'txt_countryofbirth','setter_name' :  'SetValue' } 
		map['countryofbirth'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('btn_browseNOK') ,
			'setter': self.get_valid_func( 'btn_browseNOK', 'None')  ,
			'comp_name' : 'btn_browseNOK','setter_name' :  'None' } 
		map['browseNOK'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_nameNOK') ,
			'setter': self.get_valid_func( 'txt_nameNOK', 'SetValue')  ,
			'comp_name' : 'txt_nameNOK','setter_name' :  'SetValue' } 
		map['nameNOK'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_homephone') ,
			'setter': self.get_valid_func( 'txt_homephone', 'SetValue')  ,
			'comp_name' : 'txt_homephone','setter_name' :  'SetValue' } 
		map['homephone'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_workphone') ,
			'setter': self.get_valid_func( 'txt_workphone', 'SetValue')  ,
			'comp_name' : 'txt_workphone','setter_name' :  'SetValue' } 
		map['workphone'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_fax') ,
			'setter': self.get_valid_func( 'txt_fax', 'SetValue')  ,
			'comp_name' : 'txt_fax','setter_name' :  'SetValue' } 
		map['fax'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_email') ,
			'setter': self.get_valid_func( 'txt_email', 'SetValue')  ,
			'comp_name' : 'txt_email','setter_name' :  'SetValue' } 
		map['email'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_web') ,
			'setter': self.get_valid_func( 'txt_web', 'SetValue')  ,
			'comp_name' : 'txt_web','setter_name' :  'SetValue' } 
		map['web'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_mobile') ,
			'setter': self.get_valid_func( 'txt_mobile', 'SetValue')  ,
			'comp_name' : 'txt_mobile','setter_name' :  'SetValue' } 
		map['mobile'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('cb_addressresidence') ,
			'setter': self.get_valid_func( 'cb_addressresidence', 'SetValue')  ,
			'comp_name' : 'cb_addressresidence','setter_name' :  'SetValue' } 
		map['addressresidence'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('cb_addresspostal') ,
			'setter': self.get_valid_func( 'cb_addresspostal', 'SetValue')  ,
			'comp_name' : 'cb_addresspostal','setter_name' :  'SetValue' } 
		map['addresspostal'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('btn_photo_import') ,
			'setter': self.get_valid_func( 'btn_photo_import', 'None')  ,
			'comp_name' : 'btn_photo_import','setter_name' :  'None' } 
		map['photo_import'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('btn_photo_export') ,
			'setter': self.get_valid_func( 'btn_photo_export', 'None')  ,
			'comp_name' : 'btn_photo_export','setter_name' :  'None' } 
		map['photo_export'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('btn_photo_aquire') ,
			'setter': self.get_valid_func( 'btn_photo_aquire', 'None')  ,
			'comp_name' : 'btn_photo_aquire','setter_name' :  'None' } 
		map['photo_aquire'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_findpatient') ,
			'setter': self.get_valid_func( 'txt_findpatient', 'SetValue')  ,
			'comp_name' : 'txt_findpatient','setter_name' :  'SetValue' } 
		map['findpatient'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_age') ,
			'setter': self.get_valid_func( 'txt_age', 'SetValue')  ,
			'comp_name' : 'txt_age','setter_name' :  'SetValue' } 
		map['age'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_allergies') ,
			'setter': self.get_valid_func( 'txt_allergies', 'SetValue')  ,
			'comp_name' : 'txt_allergies','setter_name' :  'SetValue' } 
		map['allergies'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('combo_consultation_type') ,
			'setter': self.get_valid_func( 'combo_consultation_type', 'SetValue')  ,
			'comp_name' : 'combo_consultation_type','setter_name' :  'SetValue' } 
		map['consultation_type'] = comp_map
		

		self.name_map = map
	

	def set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('addresslist'):
			self.set_id_common( 'addresslist',self.panel.addresslist)
			

		if self.panel.__dict__.has_key('combo_relationship'):
			self.set_id_common( 'combo_relationship',self.panel.combo_relationship)
			

		if self.panel.__dict__.has_key('txt_surname'):
			self.set_id_common( 'txt_surname',self.panel.txt_surname)
			

		if self.panel.__dict__.has_key('combo_title'):
			self.set_id_common( 'combo_title',self.panel.combo_title)
			

		if self.panel.__dict__.has_key('txt_firstname'):
			self.set_id_common( 'txt_firstname',self.panel.txt_firstname)
			

		if self.panel.__dict__.has_key('combo_sex'):
			self.set_id_common( 'combo_sex',self.panel.combo_sex)
			

		if self.panel.__dict__.has_key('cb_preferredname'):
			self.set_id_common( 'cb_preferredname',self.panel.cb_preferredname)
			

		if self.panel.__dict__.has_key('txt_preferred'):
			self.set_id_common( 'txt_preferred',self.panel.txt_preferred)
			

		if self.panel.__dict__.has_key('txt_address'):
			self.set_id_common( 'txt_address',self.panel.txt_address)
			

		if self.panel.__dict__.has_key('txt_suburb'):
			self.set_id_common( 'txt_suburb',self.panel.txt_suburb)
			

		if self.panel.__dict__.has_key('txt_zip'):
			self.set_id_common( 'txt_zip',self.panel.txt_zip)
			

		if self.panel.__dict__.has_key('txt_birthdate'):
			self.set_id_common( 'txt_birthdate',self.panel.txt_birthdate)
			

		if self.panel.__dict__.has_key('combo_maritalstatus'):
			self.set_id_common( 'combo_maritalstatus',self.panel.combo_maritalstatus)
			

		if self.panel.__dict__.has_key('txt_occupation'):
			self.set_id_common( 'txt_occupation',self.panel.txt_occupation)
			

		if self.panel.__dict__.has_key('txt_countryofbirth'):
			self.set_id_common( 'txt_countryofbirth',self.panel.txt_countryofbirth)
			

		if self.panel.__dict__.has_key('btn_browseNOK'):
			self.set_id_common( 'btn_browseNOK',self.panel.btn_browseNOK)
			

		if self.panel.__dict__.has_key('txt_nameNOK'):
			self.set_id_common( 'txt_nameNOK',self.panel.txt_nameNOK)
			

		if self.panel.__dict__.has_key('txt_homephone'):
			self.set_id_common( 'txt_homephone',self.panel.txt_homephone)
			

		if self.panel.__dict__.has_key('txt_workphone'):
			self.set_id_common( 'txt_workphone',self.panel.txt_workphone)
			

		if self.panel.__dict__.has_key('txt_fax'):
			self.set_id_common( 'txt_fax',self.panel.txt_fax)
			

		if self.panel.__dict__.has_key('txt_email'):
			self.set_id_common( 'txt_email',self.panel.txt_email)
			

		if self.panel.__dict__.has_key('txt_web'):
			self.set_id_common( 'txt_web',self.panel.txt_web)
			

		if self.panel.__dict__.has_key('txt_mobile'):
			self.set_id_common( 'txt_mobile',self.panel.txt_mobile)
			

		if self.panel.__dict__.has_key('cb_addressresidence'):
			self.set_id_common( 'cb_addressresidence',self.panel.cb_addressresidence)
			

		if self.panel.__dict__.has_key('cb_addresspostal'):
			self.set_id_common( 'cb_addresspostal',self.panel.cb_addresspostal)
			

		if self.panel.__dict__.has_key('btn_photo_import'):
			self.set_id_common( 'btn_photo_import',self.panel.btn_photo_import)
			

		if self.panel.__dict__.has_key('btn_photo_export'):
			self.set_id_common( 'btn_photo_export',self.panel.btn_photo_export)
			

		if self.panel.__dict__.has_key('btn_photo_aquire'):
			self.set_id_common( 'btn_photo_aquire',self.panel.btn_photo_aquire)
			

		if self.panel.__dict__.has_key('txt_findpatient'):
			self.set_id_common( 'txt_findpatient',self.panel.txt_findpatient)
			

		if self.panel.__dict__.has_key('txt_age'):
			self.set_id_common( 'txt_age',self.panel.txt_age)
			

		if self.panel.__dict__.has_key('txt_allergies'):
			self.set_id_common( 'txt_allergies',self.panel.txt_allergies)
			

		if self.panel.__dict__.has_key('combo_consultation_type'):
			self.set_id_common( 'combo_consultation_type',self.panel.combo_consultation_type)
			

	def set_evt(self):
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
			try :
				self.model['addresslist']= obj.GetStringSelection()
			except:
				# for dumbdbm persistent maps
				self.model['addresslist'] = str(obj.GetStringSelection())
				
			print self.model, "addresslist = ",  self.model['addresslist']
		

	def addresslist_list_box_double_clicked( self, event): 
		if self.impl <> None:
			self.impl.addresslist_list_box_double_clicked(self, event) 
			

		print "addresslist_list_box_double_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['addresslist']= obj.GetStringSelection()
			except:
				# for dumbdbm persistent maps
				self.model['addresslist'] = str(obj.GetStringSelection())
				
			print self.model, "addresslist = ",  self.model['addresslist']
		

	def combo_relationship_text_entered( self, event): 
		if self.impl <> None:
			self.impl.combo_relationship_text_entered(self, event) 
			

		print "combo_relationship_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['relationship']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['relationship'] = str(obj.GetValue())
				
			print self.model, "relationship = ",  self.model['relationship']
		

	def txt_surname_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_surname_text_entered(self, event) 
			

		print "txt_surname_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['surname']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['surname'] = str(obj.GetValue())
				
			print self.model, "surname = ",  self.model['surname']
		

	def combo_title_text_entered( self, event): 
		if self.impl <> None:
			self.impl.combo_title_text_entered(self, event) 
			

		print "combo_title_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['title']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['title'] = str(obj.GetValue())
				
			print self.model, "title = ",  self.model['title']
		

	def txt_firstname_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_firstname_text_entered(self, event) 
			

		print "txt_firstname_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['firstname']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['firstname'] = str(obj.GetValue())
				
			print self.model, "firstname = ",  self.model['firstname']
		

	def combo_sex_text_entered( self, event): 
		if self.impl <> None:
			self.impl.combo_sex_text_entered(self, event) 
			

		print "combo_sex_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['sex']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['sex'] = str(obj.GetValue())
				
			print self.model, "sex = ",  self.model['sex']
		

	def cb_preferredname_checkbox_clicked( self, event): 
		if self.impl <> None:
			self.impl.cb_preferredname_checkbox_clicked(self, event) 
			

		print "cb_preferredname_checkbox_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['preferredname']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['preferredname'] = str(obj.GetValue())
				
			print self.model, "preferredname = ",  self.model['preferredname']
		

	def txt_preferred_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_preferred_text_entered(self, event) 
			

		print "txt_preferred_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['preferred']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['preferred'] = str(obj.GetValue())
				
			print self.model, "preferred = ",  self.model['preferred']
		

	def txt_address_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_address_text_entered(self, event) 
			

		print "txt_address_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['address']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['address'] = str(obj.GetValue())
				
			print self.model, "address = ",  self.model['address']
		

	def txt_suburb_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_suburb_text_entered(self, event) 
			

		print "txt_suburb_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['suburb']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['suburb'] = str(obj.GetValue())
				
			print self.model, "suburb = ",  self.model['suburb']
		

	def txt_zip_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_zip_text_entered(self, event) 
			

		print "txt_zip_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['zip']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['zip'] = str(obj.GetValue())
				
			print self.model, "zip = ",  self.model['zip']
		

	def txt_birthdate_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_birthdate_text_entered(self, event) 
			

		print "txt_birthdate_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['birthdate']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['birthdate'] = str(obj.GetValue())
				
			print self.model, "birthdate = ",  self.model['birthdate']
		

	def combo_maritalstatus_text_entered( self, event): 
		if self.impl <> None:
			self.impl.combo_maritalstatus_text_entered(self, event) 
			

		print "combo_maritalstatus_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['maritalstatus']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['maritalstatus'] = str(obj.GetValue())
				
			print self.model, "maritalstatus = ",  self.model['maritalstatus']
		

	def txt_occupation_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_occupation_text_entered(self, event) 
			

		print "txt_occupation_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['occupation']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['occupation'] = str(obj.GetValue())
				
			print self.model, "occupation = ",  self.model['occupation']
		

	def txt_countryofbirth_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_countryofbirth_text_entered(self, event) 
			

		print "txt_countryofbirth_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['countryofbirth']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['countryofbirth'] = str(obj.GetValue())
				
			print self.model, "countryofbirth = ",  self.model['countryofbirth']
		

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
			try :
				self.model['nameNOK']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['nameNOK'] = str(obj.GetValue())
				
			print self.model, "nameNOK = ",  self.model['nameNOK']
		

	def txt_homephone_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_homephone_text_entered(self, event) 
			

		print "txt_homephone_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['homephone']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['homephone'] = str(obj.GetValue())
				
			print self.model, "homephone = ",  self.model['homephone']
		

	def txt_workphone_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_workphone_text_entered(self, event) 
			

		print "txt_workphone_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['workphone']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['workphone'] = str(obj.GetValue())
				
			print self.model, "workphone = ",  self.model['workphone']
		

	def txt_fax_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_fax_text_entered(self, event) 
			

		print "txt_fax_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['fax']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['fax'] = str(obj.GetValue())
				
			print self.model, "fax = ",  self.model['fax']
		

	def txt_email_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_email_text_entered(self, event) 
			

		print "txt_email_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['email']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['email'] = str(obj.GetValue())
				
			print self.model, "email = ",  self.model['email']
		

	def txt_web_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_web_text_entered(self, event) 
			

		print "txt_web_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['web']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['web'] = str(obj.GetValue())
				
			print self.model, "web = ",  self.model['web']
		

	def txt_mobile_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_mobile_text_entered(self, event) 
			

		print "txt_mobile_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['mobile']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['mobile'] = str(obj.GetValue())
				
			print self.model, "mobile = ",  self.model['mobile']
		

	def cb_addressresidence_checkbox_clicked( self, event): 
		if self.impl <> None:
			self.impl.cb_addressresidence_checkbox_clicked(self, event) 
			

		print "cb_addressresidence_checkbox_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['addressresidence']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['addressresidence'] = str(obj.GetValue())
				
			print self.model, "addressresidence = ",  self.model['addressresidence']
		

	def cb_addresspostal_checkbox_clicked( self, event): 
		if self.impl <> None:
			self.impl.cb_addresspostal_checkbox_clicked(self, event) 
			

		print "cb_addresspostal_checkbox_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['addresspostal']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['addresspostal'] = str(obj.GetValue())
				
			print self.model, "addresspostal = ",  self.model['addresspostal']
		

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
			try :
				self.model['findpatient']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['findpatient'] = str(obj.GetValue())
				
			print self.model, "findpatient = ",  self.model['findpatient']
		

	def txt_age_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_age_text_entered(self, event) 
			

		print "txt_age_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['age']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['age'] = str(obj.GetValue())
				
			print self.model, "age = ",  self.model['age']
		

	def txt_allergies_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_allergies_text_entered(self, event) 
			

		print "txt_allergies_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['allergies']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['allergies'] = str(obj.GetValue())
				
			print self.model, "allergies = ",  self.model['allergies']
		

	def combo_consultation_type_text_entered( self, event): 
		if self.impl <> None:
			self.impl.combo_consultation_type_text_entered(self, event) 
			

		print "combo_consultation_type_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['consultation_type']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['consultation_type'] = str(obj.GetValue())
				
			print self.model, "consultation_type = ",  self.model['consultation_type']
		
#creating a handler as gmGP_Allergies_handler from patient/gmGP_Allergies.py
# [('classtxt', 'wxTextCtrl')]

class gmGP_Allergies_handler(base_handler):
	
	def __init__(self, panel, model = None, impl = None):
		base_handler.__init__(self, panel, model, impl)
		

	def set_name_map(self):
		map = {}
		
 
		comp_map = { 'component': self.get_valid_component('classtxt') ,
			'setter': self.get_valid_func( 'classtxt', 'SetValue')  ,
			'comp_name' : 'classtxt','setter_name' :  'SetValue' } 
		map['classtxt'] = comp_map
		

		self.name_map = map
	

	def set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('classtxt'):
			self.set_id_common( 'classtxt',self.panel.classtxt)
			

	def set_evt(self):
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
			try :
				self.model['classtxt']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['classtxt'] = str(obj.GetValue())
				
			print self.model, "classtxt = ",  self.model['classtxt']
		
#creating a handler as gmGP_AnteNatal_3_handler from patient/gmGP_AnteNatal_3.py
# []
#creating a handler as gmGP_ClinicalSummary_handler from patient/gmGP_ClinicalSummary.py
# []
#creating a handler as gmGP_FamilyHistory_handler from patient/gmGP_FamilyHistory.py
# [('txt_social_history', 'wxTextCtrl')]

class gmGP_FamilyHistory_handler(base_handler):
	
	def __init__(self, panel, model = None, impl = None):
		base_handler.__init__(self, panel, model, impl)
		

	def set_name_map(self):
		map = {}
		
 
		comp_map = { 'component': self.get_valid_component('txt_social_history') ,
			'setter': self.get_valid_func( 'txt_social_history', 'SetValue')  ,
			'comp_name' : 'txt_social_history','setter_name' :  'SetValue' } 
		map['social_history'] = comp_map
		

		self.name_map = map
	

	def set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('txt_social_history'):
			self.set_id_common( 'txt_social_history',self.panel.txt_social_history)
			

	def set_evt(self):
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
			try :
				self.model['social_history']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['social_history'] = str(obj.GetValue())
				
			print self.model, "social_history = ",  self.model['social_history']
		
#creating a handler as gmGP_Immunisation_handler from patient/gmGP_Immunisation.py
# [('missingimmunisation_listbox', 'wxListBox')]

class gmGP_Immunisation_handler(base_handler):
	
	def __init__(self, panel, model = None, impl = None):
		base_handler.__init__(self, panel, model, impl)
		

	def set_name_map(self):
		map = {}
		
 
		comp_map = { 'component': self.get_valid_component('missingimmunisation_listbox') ,
			'setter': self.get_valid_func( 'missingimmunisation_listbox', 'SetStringSelection')  ,
			'comp_name' : 'missingimmunisation_listbox','setter_name' :  'SetStringSelection' } 
		map['listbox'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('missingimmunisation_listbox') ,
			'setter': self.get_valid_func( 'missingimmunisation_listbox', 'SetStringSelection')  ,
			'comp_name' : 'missingimmunisation_listbox','setter_name' :  'SetStringSelection' } 
		map['listbox'] = comp_map
		

		self.name_map = map
	

	def set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('missingimmunisation_listbox'):
			self.set_id_common( 'missingimmunisation_listbox',self.panel.missingimmunisation_listbox)
			

	def set_evt(self):
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
			try :
				self.model['listbox']= obj.GetStringSelection()
			except:
				# for dumbdbm persistent maps
				self.model['listbox'] = str(obj.GetStringSelection())
				
			print self.model, "listbox = ",  self.model['listbox']
		

	def missingimmunisation_listbox_list_box_double_clicked( self, event): 
		if self.impl <> None:
			self.impl.missingimmunisation_listbox_list_box_double_clicked(self, event) 
			

		print "missingimmunisation_listbox_list_box_double_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['listbox']= obj.GetStringSelection()
			except:
				# for dumbdbm persistent maps
				self.model['listbox'] = str(obj.GetStringSelection())
				
			print self.model, "listbox = ",  self.model['listbox']
		
#creating a handler as gmGP_Measurements_handler from patient/gmGP_Measurements.py
# []
#creating a handler as gmGP_PastHistory_handler from patient/gmGP_PastHistory.py
# []
#creating a handler as gmGP_Prescriptions_handler from patient/gmGP_Prescriptions.py
# [('txt_scriptDate', 'wxTextCtrl'), ('interactiontxt', 'wxTextCtrl')]

class gmGP_Prescriptions_handler(base_handler):
	
	def __init__(self, panel, model = None, impl = None):
		base_handler.__init__(self, panel, model, impl)
		

	def set_name_map(self):
		map = {}
		
 
		comp_map = { 'component': self.get_valid_component('txt_scriptDate') ,
			'setter': self.get_valid_func( 'txt_scriptDate', 'SetValue')  ,
			'comp_name' : 'txt_scriptDate','setter_name' :  'SetValue' } 
		map['scriptDate'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('interactiontxt') ,
			'setter': self.get_valid_func( 'interactiontxt', 'SetValue')  ,
			'comp_name' : 'interactiontxt','setter_name' :  'SetValue' } 
		map['interactiontxt'] = comp_map
		

		self.name_map = map
	

	def set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('txt_scriptDate'):
			self.set_id_common( 'txt_scriptDate',self.panel.txt_scriptDate)
			

		if self.panel.__dict__.has_key('interactiontxt'):
			self.set_id_common( 'interactiontxt',self.panel.interactiontxt)
			

	def set_evt(self):
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
			try :
				self.model['scriptDate']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['scriptDate'] = str(obj.GetValue())
				
			print self.model, "scriptDate = ",  self.model['scriptDate']
		

	def interactiontxt_text_entered( self, event): 
		if self.impl <> None:
			self.impl.interactiontxt_text_entered(self, event) 
			

		print "interactiontxt_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['interactiontxt']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['interactiontxt'] = str(obj.GetValue())
				
			print self.model, "interactiontxt = ",  self.model['interactiontxt']
		
#creating a handler as gmGP_Recalls_handler from patient/gmGP_Recalls.py
# []
#creating a handler as gmGP_Referrals_handler from patient/gmGP_Referrals.py
# [('txt_referraldate', 'wxTextCtrl'), ('txt_referral_letter', 'wxTextCtrl')]

class gmGP_Referrals_handler(base_handler):
	
	def __init__(self, panel, model = None, impl = None):
		base_handler.__init__(self, panel, model, impl)
		

	def set_name_map(self):
		map = {}
		
 
		comp_map = { 'component': self.get_valid_component('txt_referraldate') ,
			'setter': self.get_valid_func( 'txt_referraldate', 'SetValue')  ,
			'comp_name' : 'txt_referraldate','setter_name' :  'SetValue' } 
		map['referraldate'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_referral_letter') ,
			'setter': self.get_valid_func( 'txt_referral_letter', 'SetValue')  ,
			'comp_name' : 'txt_referral_letter','setter_name' :  'SetValue' } 
		map['referral_letter'] = comp_map
		

		self.name_map = map
	

	def set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('txt_referraldate'):
			self.set_id_common( 'txt_referraldate',self.panel.txt_referraldate)
			

		if self.panel.__dict__.has_key('txt_referral_letter'):
			self.set_id_common( 'txt_referral_letter',self.panel.txt_referral_letter)
			

	def set_evt(self):
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
			try :
				self.model['referraldate']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['referraldate'] = str(obj.GetValue())
				
			print self.model, "referraldate = ",  self.model['referraldate']
		

	def txt_referral_letter_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_referral_letter_text_entered(self, event) 
			

		print "txt_referral_letter_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['referral_letter']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['referral_letter'] = str(obj.GetValue())
				
			print self.model, "referral_letter = ",  self.model['referral_letter']
		
#creating a handler as gmGP_Requests_handler from patient/gmGP_Requests.py
# [('txt_requestDate', 'wxTextCtrl')]

class gmGP_Requests_handler(base_handler):
	
	def __init__(self, panel, model = None, impl = None):
		base_handler.__init__(self, panel, model, impl)
		

	def set_name_map(self):
		map = {}
		
 
		comp_map = { 'component': self.get_valid_component('txt_requestDate') ,
			'setter': self.get_valid_func( 'txt_requestDate', 'SetValue')  ,
			'comp_name' : 'txt_requestDate','setter_name' :  'SetValue' } 
		map['requestDate'] = comp_map
		

		self.name_map = map
	

	def set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('txt_requestDate'):
			self.set_id_common( 'txt_requestDate',self.panel.txt_requestDate)
			

	def set_evt(self):
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
			try :
				self.model['requestDate']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['requestDate'] = str(obj.GetValue())
				
			print self.model, "requestDate = ",  self.model['requestDate']
		
#creating a handler as gmGP_ScratchPadRecalls_handler from patient/gmGP_ScratchPadRecalls.py
# [('scratchpad_txt', 'wxTextCtrl')]

class gmGP_ScratchPadRecalls_handler(base_handler):
	
	def __init__(self, panel, model = None, impl = None):
		base_handler.__init__(self, panel, model, impl)
		

	def set_name_map(self):
		map = {}
		
 
		comp_map = { 'component': self.get_valid_component('scratchpad_txt') ,
			'setter': self.get_valid_func( 'scratchpad_txt', 'SetValue')  ,
			'comp_name' : 'scratchpad_txt','setter_name' :  'SetValue' } 
		map['txt'] = comp_map
		

		self.name_map = map
	

	def set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('scratchpad_txt'):
			self.set_id_common( 'scratchpad_txt',self.panel.scratchpad_txt)
			

	def set_evt(self):
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
			try :
				self.model['txt']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['txt'] = str(obj.GetValue())
				
			print self.model, "txt = ",  self.model['txt']
		
#creating a handler as gmGP_TabbedLists_handler from patient/gmGP_TabbedLists.py
# []
