# ['gmContacts.py', 'gmDrugDisplay.py', 'gmGuidelines.py', 'gmLock.py', 'gmManual.py', 'gmOffice.py', 'gmPatientWindowManager.py', 'gmPython.py', 'gmSQL.py', 'gmShowMedDocs.py', 'gmSnellen.py', 'gmStikoBrowser.py', 'gmplNbPatientSelector.py', 'gmplNbSchedule.py']

from wxPython.wx import * 


class base_handler:

	def create_handler(self, panel, model = None):
		if model == None and self.model <> None:
			model = self.model
			
		return self.__init__(panel, model)

	def __init__(self, panel, model = None):
		self.panel = panel
		
		if panel <> None:
			self.set_id()
			self.set_evt()
			self.impl = None
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

		
	
#creating a handler as gmContacts_handler from gui/gmContacts.py
# type_search_str =  class\s+(?P<new_type>\w+)\s*\(.*(?P<base_type>wxTextCtrl|wxComboBox|wxButton|wxRadioButton|wxCheckBox|wxListBox)
# found new type = TextBox_RedBold which is base_type wxTextCtrl

# found new type = TextBox_BlackNormal which is base_type wxTextCtrl

# [('txt_org_name', 'TextBox_RedBold'), ('txt_org_type', 'TextBox_RedBold'), ('txt_org_street', 'wxTextCtrl'), ('txt_org_suburb', 'TextBox_RedBold'), ('txt_org_zip', 'TextBox_RedBold'), ('txt_org_state', 'TextBox_RedBold'), ('txt_org_user1', 'TextBox_BlackNormal'), ('txt_org_user2', 'TextBox_BlackNormal'), ('txt_org_user3', 'TextBox_BlackNormal'), ('txt_org_category', 'TextBox_BlackNormal'), ('txt_org_phone', 'TextBox_BlackNormal'), ('txt_org_fax', 'TextBox_BlackNormal'), ('txt_org_mobile', 'TextBox_BlackNormal'), ('txt_org_email', 'TextBox_BlackNormal'), ('txt_org_internet', 'TextBox_BlackNormal'), ('txt_org_memo', 'wxTextCtrl'), ('combo_type', 'wxComboBox'), ('chbx_postaladdress', 'wxCheckBox')]

class gmContacts_handler( base_handler):
	
	def __init__(self, panel, model = None):
		base_handler.__init__(self, panel, model)
		

	def set_name_map(self):
		map = {}
		
 
		comp_map = { 'component': self.get_valid_component('txt_org_name') ,
			'setter': self.get_valid_func( 'txt_org_name', 'SetValue')  ,
			'comp_name' : 'txt_org_name','setter_name' :  'SetValue' } 
		map['org_name'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_org_type') ,
			'setter': self.get_valid_func( 'txt_org_type', 'SetValue')  ,
			'comp_name' : 'txt_org_type','setter_name' :  'SetValue' } 
		map['org_type'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_org_street') ,
			'setter': self.get_valid_func( 'txt_org_street', 'SetValue')  ,
			'comp_name' : 'txt_org_street','setter_name' :  'SetValue' } 
		map['org_street'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_org_suburb') ,
			'setter': self.get_valid_func( 'txt_org_suburb', 'SetValue')  ,
			'comp_name' : 'txt_org_suburb','setter_name' :  'SetValue' } 
		map['org_suburb'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_org_zip') ,
			'setter': self.get_valid_func( 'txt_org_zip', 'SetValue')  ,
			'comp_name' : 'txt_org_zip','setter_name' :  'SetValue' } 
		map['org_zip'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_org_state') ,
			'setter': self.get_valid_func( 'txt_org_state', 'SetValue')  ,
			'comp_name' : 'txt_org_state','setter_name' :  'SetValue' } 
		map['org_state'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_org_user1') ,
			'setter': self.get_valid_func( 'txt_org_user1', 'SetValue')  ,
			'comp_name' : 'txt_org_user1','setter_name' :  'SetValue' } 
		map['org_user1'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_org_user2') ,
			'setter': self.get_valid_func( 'txt_org_user2', 'SetValue')  ,
			'comp_name' : 'txt_org_user2','setter_name' :  'SetValue' } 
		map['org_user2'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_org_user3') ,
			'setter': self.get_valid_func( 'txt_org_user3', 'SetValue')  ,
			'comp_name' : 'txt_org_user3','setter_name' :  'SetValue' } 
		map['org_user3'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_org_category') ,
			'setter': self.get_valid_func( 'txt_org_category', 'SetValue')  ,
			'comp_name' : 'txt_org_category','setter_name' :  'SetValue' } 
		map['org_category'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_org_phone') ,
			'setter': self.get_valid_func( 'txt_org_phone', 'SetValue')  ,
			'comp_name' : 'txt_org_phone','setter_name' :  'SetValue' } 
		map['org_phone'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_org_fax') ,
			'setter': self.get_valid_func( 'txt_org_fax', 'SetValue')  ,
			'comp_name' : 'txt_org_fax','setter_name' :  'SetValue' } 
		map['org_fax'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_org_mobile') ,
			'setter': self.get_valid_func( 'txt_org_mobile', 'SetValue')  ,
			'comp_name' : 'txt_org_mobile','setter_name' :  'SetValue' } 
		map['org_mobile'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_org_email') ,
			'setter': self.get_valid_func( 'txt_org_email', 'SetValue')  ,
			'comp_name' : 'txt_org_email','setter_name' :  'SetValue' } 
		map['org_email'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_org_internet') ,
			'setter': self.get_valid_func( 'txt_org_internet', 'SetValue')  ,
			'comp_name' : 'txt_org_internet','setter_name' :  'SetValue' } 
		map['org_internet'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_org_memo') ,
			'setter': self.get_valid_func( 'txt_org_memo', 'SetValue')  ,
			'comp_name' : 'txt_org_memo','setter_name' :  'SetValue' } 
		map['org_memo'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('combo_type') ,
			'setter': self.get_valid_func( 'combo_type', 'SetValue')  ,
			'comp_name' : 'combo_type','setter_name' :  'SetValue' } 
		map['type'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('chbx_postaladdress') ,
			'setter': self.get_valid_func( 'chbx_postaladdress', 'SetValue')  ,
			'comp_name' : 'chbx_postaladdress','setter_name' :  'SetValue' } 
		map['postaladdress'] = comp_map
		

		self.name_map = map
	

	def set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('txt_org_name'):
			self.set_id_common( 'txt_org_name',self.panel.txt_org_name)
			

		if self.panel.__dict__.has_key('txt_org_type'):
			self.set_id_common( 'txt_org_type',self.panel.txt_org_type)
			

		if self.panel.__dict__.has_key('txt_org_street'):
			self.set_id_common( 'txt_org_street',self.panel.txt_org_street)
			

		if self.panel.__dict__.has_key('txt_org_suburb'):
			self.set_id_common( 'txt_org_suburb',self.panel.txt_org_suburb)
			

		if self.panel.__dict__.has_key('txt_org_zip'):
			self.set_id_common( 'txt_org_zip',self.panel.txt_org_zip)
			

		if self.panel.__dict__.has_key('txt_org_state'):
			self.set_id_common( 'txt_org_state',self.panel.txt_org_state)
			

		if self.panel.__dict__.has_key('txt_org_user1'):
			self.set_id_common( 'txt_org_user1',self.panel.txt_org_user1)
			

		if self.panel.__dict__.has_key('txt_org_user2'):
			self.set_id_common( 'txt_org_user2',self.panel.txt_org_user2)
			

		if self.panel.__dict__.has_key('txt_org_user3'):
			self.set_id_common( 'txt_org_user3',self.panel.txt_org_user3)
			

		if self.panel.__dict__.has_key('txt_org_category'):
			self.set_id_common( 'txt_org_category',self.panel.txt_org_category)
			

		if self.panel.__dict__.has_key('txt_org_phone'):
			self.set_id_common( 'txt_org_phone',self.panel.txt_org_phone)
			

		if self.panel.__dict__.has_key('txt_org_fax'):
			self.set_id_common( 'txt_org_fax',self.panel.txt_org_fax)
			

		if self.panel.__dict__.has_key('txt_org_mobile'):
			self.set_id_common( 'txt_org_mobile',self.panel.txt_org_mobile)
			

		if self.panel.__dict__.has_key('txt_org_email'):
			self.set_id_common( 'txt_org_email',self.panel.txt_org_email)
			

		if self.panel.__dict__.has_key('txt_org_internet'):
			self.set_id_common( 'txt_org_internet',self.panel.txt_org_internet)
			

		if self.panel.__dict__.has_key('txt_org_memo'):
			self.set_id_common( 'txt_org_memo',self.panel.txt_org_memo)
			

		if self.panel.__dict__.has_key('combo_type'):
			self.set_id_common( 'combo_type',self.panel.combo_type)
			

		if self.panel.__dict__.has_key('chbx_postaladdress'):
			self.set_id_common( 'chbx_postaladdress',self.panel.chbx_postaladdress)
			

	def set_evt(self):
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
			try :
				self.model['org_name']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['org_name'] = str(obj.GetValue())
				
			print self.model, "org_name = ",  self.model['org_name']
		

	def txt_org_type_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_org_type_text_entered(self, event) 
			

		print "txt_org_type_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['org_type']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['org_type'] = str(obj.GetValue())
				
			print self.model, "org_type = ",  self.model['org_type']
		

	def txt_org_street_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_org_street_text_entered(self, event) 
			

		print "txt_org_street_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['org_street']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['org_street'] = str(obj.GetValue())
				
			print self.model, "org_street = ",  self.model['org_street']
		

	def txt_org_suburb_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_org_suburb_text_entered(self, event) 
			

		print "txt_org_suburb_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['org_suburb']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['org_suburb'] = str(obj.GetValue())
				
			print self.model, "org_suburb = ",  self.model['org_suburb']
		

	def txt_org_zip_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_org_zip_text_entered(self, event) 
			

		print "txt_org_zip_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['org_zip']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['org_zip'] = str(obj.GetValue())
				
			print self.model, "org_zip = ",  self.model['org_zip']
		

	def txt_org_state_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_org_state_text_entered(self, event) 
			

		print "txt_org_state_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['org_state']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['org_state'] = str(obj.GetValue())
				
			print self.model, "org_state = ",  self.model['org_state']
		

	def txt_org_user1_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_org_user1_text_entered(self, event) 
			

		print "txt_org_user1_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['org_user1']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['org_user1'] = str(obj.GetValue())
				
			print self.model, "org_user1 = ",  self.model['org_user1']
		

	def txt_org_user2_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_org_user2_text_entered(self, event) 
			

		print "txt_org_user2_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['org_user2']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['org_user2'] = str(obj.GetValue())
				
			print self.model, "org_user2 = ",  self.model['org_user2']
		

	def txt_org_user3_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_org_user3_text_entered(self, event) 
			

		print "txt_org_user3_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['org_user3']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['org_user3'] = str(obj.GetValue())
				
			print self.model, "org_user3 = ",  self.model['org_user3']
		

	def txt_org_category_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_org_category_text_entered(self, event) 
			

		print "txt_org_category_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['org_category']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['org_category'] = str(obj.GetValue())
				
			print self.model, "org_category = ",  self.model['org_category']
		

	def txt_org_phone_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_org_phone_text_entered(self, event) 
			

		print "txt_org_phone_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['org_phone']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['org_phone'] = str(obj.GetValue())
				
			print self.model, "org_phone = ",  self.model['org_phone']
		

	def txt_org_fax_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_org_fax_text_entered(self, event) 
			

		print "txt_org_fax_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['org_fax']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['org_fax'] = str(obj.GetValue())
				
			print self.model, "org_fax = ",  self.model['org_fax']
		

	def txt_org_mobile_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_org_mobile_text_entered(self, event) 
			

		print "txt_org_mobile_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['org_mobile']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['org_mobile'] = str(obj.GetValue())
				
			print self.model, "org_mobile = ",  self.model['org_mobile']
		

	def txt_org_email_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_org_email_text_entered(self, event) 
			

		print "txt_org_email_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['org_email']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['org_email'] = str(obj.GetValue())
				
			print self.model, "org_email = ",  self.model['org_email']
		

	def txt_org_internet_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_org_internet_text_entered(self, event) 
			

		print "txt_org_internet_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['org_internet']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['org_internet'] = str(obj.GetValue())
				
			print self.model, "org_internet = ",  self.model['org_internet']
		

	def txt_org_memo_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_org_memo_text_entered(self, event) 
			

		print "txt_org_memo_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['org_memo']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['org_memo'] = str(obj.GetValue())
				
			print self.model, "org_memo = ",  self.model['org_memo']
		

	def combo_type_text_entered( self, event): 
		if self.impl <> None:
			self.impl.combo_type_text_entered(self, event) 
			

		print "combo_type_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['type']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['type'] = str(obj.GetValue())
				
			print self.model, "type = ",  self.model['type']
		

	def chbx_postaladdress_checkbox_clicked( self, event): 
		if self.impl <> None:
			self.impl.chbx_postaladdress_checkbox_clicked(self, event) 
			

		print "chbx_postaladdress_checkbox_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['postaladdress']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['postaladdress'] = str(obj.GetValue())
				
			print self.model, "postaladdress = ",  self.model['postaladdress']
		
#creating a handler as gmDrugDisplay_handler from gui/gmDrugDisplay.py
# [('comboProduct', 'wxComboBox'), ('btnBookmark', 'wxButton'), ('rbtnSearchAny', 'wxRadioButton'), ('rbtnSearchBrand', 'wxRadioButton'), ('rbtnSearchGeneric', 'wxRadioButton'), ('rbtnSearchIndication', 'wxRadioButton'), ('listbox_jumpto', 'wxListBox'), ('btnPrescribe', 'wxButton'), ('btnDisplay', 'wxButton'), ('btnPrint', 'wxButton'), ('listbox_drugchoice', 'wxListBox')]

class gmDrugDisplay_handler( base_handler):
	
	def __init__(self, panel, model = None):
		base_handler.__init__(self, panel, model)
		

	def set_name_map(self):
		map = {}
		
 
		comp_map = { 'component': self.get_valid_component('comboProduct') ,
			'setter': self.get_valid_func( 'comboProduct', 'SetValue')  ,
			'comp_name' : 'comboProduct','setter_name' :  'SetValue' } 
		map['comboProduct'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('btnBookmark') ,
			'setter': self.get_valid_func( 'btnBookmark', 'None')  ,
			'comp_name' : 'btnBookmark','setter_name' :  'None' } 
		map['btnBookmark'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('rbtnSearchAny') ,
			'setter': self.get_valid_func( 'rbtnSearchAny', 'SetValue')  ,
			'comp_name' : 'rbtnSearchAny','setter_name' :  'SetValue' } 
		map['rbtnSearchAny'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('rbtnSearchBrand') ,
			'setter': self.get_valid_func( 'rbtnSearchBrand', 'SetValue')  ,
			'comp_name' : 'rbtnSearchBrand','setter_name' :  'SetValue' } 
		map['rbtnSearchBrand'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('rbtnSearchGeneric') ,
			'setter': self.get_valid_func( 'rbtnSearchGeneric', 'SetValue')  ,
			'comp_name' : 'rbtnSearchGeneric','setter_name' :  'SetValue' } 
		map['rbtnSearchGeneric'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('rbtnSearchIndication') ,
			'setter': self.get_valid_func( 'rbtnSearchIndication', 'SetValue')  ,
			'comp_name' : 'rbtnSearchIndication','setter_name' :  'SetValue' } 
		map['rbtnSearchIndication'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('listbox_jumpto') ,
			'setter': self.get_valid_func( 'listbox_jumpto', 'SetStringSelection')  ,
			'comp_name' : 'listbox_jumpto','setter_name' :  'SetStringSelection' } 
		map['jumpto'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('listbox_jumpto') ,
			'setter': self.get_valid_func( 'listbox_jumpto', 'SetStringSelection')  ,
			'comp_name' : 'listbox_jumpto','setter_name' :  'SetStringSelection' } 
		map['jumpto'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('btnPrescribe') ,
			'setter': self.get_valid_func( 'btnPrescribe', 'None')  ,
			'comp_name' : 'btnPrescribe','setter_name' :  'None' } 
		map['btnPrescribe'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('btnDisplay') ,
			'setter': self.get_valid_func( 'btnDisplay', 'None')  ,
			'comp_name' : 'btnDisplay','setter_name' :  'None' } 
		map['btnDisplay'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('btnPrint') ,
			'setter': self.get_valid_func( 'btnPrint', 'None')  ,
			'comp_name' : 'btnPrint','setter_name' :  'None' } 
		map['btnPrint'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('listbox_drugchoice') ,
			'setter': self.get_valid_func( 'listbox_drugchoice', 'SetStringSelection')  ,
			'comp_name' : 'listbox_drugchoice','setter_name' :  'SetStringSelection' } 
		map['drugchoice'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('listbox_drugchoice') ,
			'setter': self.get_valid_func( 'listbox_drugchoice', 'SetStringSelection')  ,
			'comp_name' : 'listbox_drugchoice','setter_name' :  'SetStringSelection' } 
		map['drugchoice'] = comp_map
		

		self.name_map = map
	

	def set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('comboProduct'):
			self.set_id_common( 'comboProduct',self.panel.comboProduct)
			

		if self.panel.__dict__.has_key('btnBookmark'):
			self.set_id_common( 'btnBookmark',self.panel.btnBookmark)
			

		if self.panel.__dict__.has_key('rbtnSearchAny'):
			self.set_id_common( 'rbtnSearchAny',self.panel.rbtnSearchAny)
			

		if self.panel.__dict__.has_key('rbtnSearchBrand'):
			self.set_id_common( 'rbtnSearchBrand',self.panel.rbtnSearchBrand)
			

		if self.panel.__dict__.has_key('rbtnSearchGeneric'):
			self.set_id_common( 'rbtnSearchGeneric',self.panel.rbtnSearchGeneric)
			

		if self.panel.__dict__.has_key('rbtnSearchIndication'):
			self.set_id_common( 'rbtnSearchIndication',self.panel.rbtnSearchIndication)
			

		if self.panel.__dict__.has_key('listbox_jumpto'):
			self.set_id_common( 'listbox_jumpto',self.panel.listbox_jumpto)
			

		if self.panel.__dict__.has_key('btnPrescribe'):
			self.set_id_common( 'btnPrescribe',self.panel.btnPrescribe)
			

		if self.panel.__dict__.has_key('btnDisplay'):
			self.set_id_common( 'btnDisplay',self.panel.btnDisplay)
			

		if self.panel.__dict__.has_key('btnPrint'):
			self.set_id_common( 'btnPrint',self.panel.btnPrint)
			

		if self.panel.__dict__.has_key('listbox_drugchoice'):
			self.set_id_common( 'listbox_drugchoice',self.panel.listbox_drugchoice)
			

	def set_evt(self):
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
			try :
				self.model['comboProduct']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['comboProduct'] = str(obj.GetValue())
				
			print self.model, "comboProduct = ",  self.model['comboProduct']
		

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
			try :
				self.model['rbtnSearchAny']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['rbtnSearchAny'] = str(obj.GetValue())
				
			print self.model, "rbtnSearchAny = ",  self.model['rbtnSearchAny']
		

	def rbtnSearchBrand_radiobutton_clicked( self, event): 
		if self.impl <> None:
			self.impl.rbtnSearchBrand_radiobutton_clicked(self, event) 
			

		print "rbtnSearchBrand_radiobutton_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['rbtnSearchBrand']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['rbtnSearchBrand'] = str(obj.GetValue())
				
			print self.model, "rbtnSearchBrand = ",  self.model['rbtnSearchBrand']
		

	def rbtnSearchGeneric_radiobutton_clicked( self, event): 
		if self.impl <> None:
			self.impl.rbtnSearchGeneric_radiobutton_clicked(self, event) 
			

		print "rbtnSearchGeneric_radiobutton_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['rbtnSearchGeneric']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['rbtnSearchGeneric'] = str(obj.GetValue())
				
			print self.model, "rbtnSearchGeneric = ",  self.model['rbtnSearchGeneric']
		

	def rbtnSearchIndication_radiobutton_clicked( self, event): 
		if self.impl <> None:
			self.impl.rbtnSearchIndication_radiobutton_clicked(self, event) 
			

		print "rbtnSearchIndication_radiobutton_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['rbtnSearchIndication']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['rbtnSearchIndication'] = str(obj.GetValue())
				
			print self.model, "rbtnSearchIndication = ",  self.model['rbtnSearchIndication']
		

	def listbox_jumpto_list_box_single_clicked( self, event): 
		if self.impl <> None:
			self.impl.listbox_jumpto_list_box_single_clicked(self, event) 
			

		print "listbox_jumpto_list_box_single_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['jumpto']= obj.GetStringSelection()
			except:
				# for dumbdbm persistent maps
				self.model['jumpto'] = str(obj.GetStringSelection())
				
			print self.model, "jumpto = ",  self.model['jumpto']
		

	def listbox_jumpto_list_box_double_clicked( self, event): 
		if self.impl <> None:
			self.impl.listbox_jumpto_list_box_double_clicked(self, event) 
			

		print "listbox_jumpto_list_box_double_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['jumpto']= obj.GetStringSelection()
			except:
				# for dumbdbm persistent maps
				self.model['jumpto'] = str(obj.GetStringSelection())
				
			print self.model, "jumpto = ",  self.model['jumpto']
		

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
			try :
				self.model['drugchoice']= obj.GetStringSelection()
			except:
				# for dumbdbm persistent maps
				self.model['drugchoice'] = str(obj.GetStringSelection())
				
			print self.model, "drugchoice = ",  self.model['drugchoice']
		

	def listbox_drugchoice_list_box_double_clicked( self, event): 
		if self.impl <> None:
			self.impl.listbox_drugchoice_list_box_double_clicked(self, event) 
			

		print "listbox_drugchoice_list_box_double_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['drugchoice']= obj.GetStringSelection()
			except:
				# for dumbdbm persistent maps
				self.model['drugchoice'] = str(obj.GetStringSelection())
				
			print self.model, "drugchoice = ",  self.model['drugchoice']
		
#creating a handler as gmGuidelines_handler from gui/gmGuidelines.py
# [('infoline', 'wxTextCtrl')]

class gmGuidelines_handler( base_handler):
	
	def __init__(self, panel, model = None):
		base_handler.__init__(self, panel, model)
		

	def set_name_map(self):
		map = {}
		
 
		comp_map = { 'component': self.get_valid_component('infoline') ,
			'setter': self.get_valid_func( 'infoline', 'SetValue')  ,
			'comp_name' : 'infoline','setter_name' :  'SetValue' } 
		map['infoline'] = comp_map
		

		self.name_map = map
	

	def set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('infoline'):
			self.set_id_common( 'infoline',self.panel.infoline)
			

	def set_evt(self):
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
			try :
				self.model['infoline']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['infoline'] = str(obj.GetValue())
				
			print self.model, "infoline = ",  self.model['infoline']
		
#creating a handler as gmLock_handler from gui/gmLock.py
# []
#creating a handler as gmManual_handler from gui/gmManual.py
# [('infoline', 'wxTextCtrl')]

class gmManual_handler( base_handler):
	
	def __init__(self, panel, model = None):
		base_handler.__init__(self, panel, model)
		

	def set_name_map(self):
		map = {}
		
 
		comp_map = { 'component': self.get_valid_component('infoline') ,
			'setter': self.get_valid_func( 'infoline', 'SetValue')  ,
			'comp_name' : 'infoline','setter_name' :  'SetValue' } 
		map['infoline'] = comp_map
		

		self.name_map = map
	

	def set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('infoline'):
			self.set_id_common( 'infoline',self.panel.infoline)
			

	def set_evt(self):
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
			try :
				self.model['infoline']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['infoline'] = str(obj.GetValue())
				
			print self.model, "infoline = ",  self.model['infoline']
		
#creating a handler as gmOffice_handler from gui/gmOffice.py
# []
#creating a handler as gmPatientWindowManager_handler from gui/gmPatientWindowManager.py
# []
#creating a handler as gmPython_handler from gui/gmPython.py
# []
#creating a handler as gmSQL_handler from gui/gmSQL.py
# [('comboQueryInput', 'wxComboBox'), ('buttonRunQuery', 'wxButton'), ('buttonClearQuery', 'wxButton'), ('textQueryResults', 'wxTextCtrl')]

class gmSQL_handler( base_handler):
	
	def __init__(self, panel, model = None):
		base_handler.__init__(self, panel, model)
		

	def set_name_map(self):
		map = {}
		
 
		comp_map = { 'component': self.get_valid_component('comboQueryInput') ,
			'setter': self.get_valid_func( 'comboQueryInput', 'SetValue')  ,
			'comp_name' : 'comboQueryInput','setter_name' :  'SetValue' } 
		map['comboQueryInput'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('buttonRunQuery') ,
			'setter': self.get_valid_func( 'buttonRunQuery', 'None')  ,
			'comp_name' : 'buttonRunQuery','setter_name' :  'None' } 
		map['buttonRunQuery'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('buttonClearQuery') ,
			'setter': self.get_valid_func( 'buttonClearQuery', 'None')  ,
			'comp_name' : 'buttonClearQuery','setter_name' :  'None' } 
		map['buttonClearQuery'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('textQueryResults') ,
			'setter': self.get_valid_func( 'textQueryResults', 'SetValue')  ,
			'comp_name' : 'textQueryResults','setter_name' :  'SetValue' } 
		map['textQueryResults'] = comp_map
		

		self.name_map = map
	

	def set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('comboQueryInput'):
			self.set_id_common( 'comboQueryInput',self.panel.comboQueryInput)
			

		if self.panel.__dict__.has_key('buttonRunQuery'):
			self.set_id_common( 'buttonRunQuery',self.panel.buttonRunQuery)
			

		if self.panel.__dict__.has_key('buttonClearQuery'):
			self.set_id_common( 'buttonClearQuery',self.panel.buttonClearQuery)
			

		if self.panel.__dict__.has_key('textQueryResults'):
			self.set_id_common( 'textQueryResults',self.panel.textQueryResults)
			

	def set_evt(self):
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
			try :
				self.model['comboQueryInput']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['comboQueryInput'] = str(obj.GetValue())
				
			print self.model, "comboQueryInput = ",  self.model['comboQueryInput']
		

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
			try :
				self.model['textQueryResults']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['textQueryResults'] = str(obj.GetValue())
				
			print self.model, "textQueryResults = ",  self.model['textQueryResults']
		
#creating a handler as gmShowMedDocs_handler from gui/gmShowMedDocs.py
# []
#creating a handler as gmSnellen_handler from gui/gmSnellen.py
# [('mirror_ctrl', 'wxCheckBox')]

class gmSnellen_handler( base_handler):
	
	def __init__(self, panel, model = None):
		base_handler.__init__(self, panel, model)
		

	def set_name_map(self):
		map = {}
		
 
		comp_map = { 'component': self.get_valid_component('mirror_ctrl') ,
			'setter': self.get_valid_func( 'mirror_ctrl', 'SetValue')  ,
			'comp_name' : 'mirror_ctrl','setter_name' :  'SetValue' } 
		map['ctrl'] = comp_map
		

		self.name_map = map
	

	def set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('mirror_ctrl'):
			self.set_id_common( 'mirror_ctrl',self.panel.mirror_ctrl)
			

	def set_evt(self):
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
			try :
				self.model['ctrl']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['ctrl'] = str(obj.GetValue())
				
			print self.model, "ctrl = ",  self.model['ctrl']
		
#creating a handler as gmStikoBrowser_handler from gui/gmStikoBrowser.py
# [('infoline', 'wxTextCtrl')]

class gmStikoBrowser_handler( base_handler):
	
	def __init__(self, panel, model = None):
		base_handler.__init__(self, panel, model)
		

	def set_name_map(self):
		map = {}
		
 
		comp_map = { 'component': self.get_valid_component('infoline') ,
			'setter': self.get_valid_func( 'infoline', 'SetValue')  ,
			'comp_name' : 'infoline','setter_name' :  'SetValue' } 
		map['infoline'] = comp_map
		

		self.name_map = map
	

	def set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('infoline'):
			self.set_id_common( 'infoline',self.panel.infoline)
			

	def set_evt(self):
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
			try :
				self.model['infoline']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['infoline'] = str(obj.GetValue())
				
			print self.model, "infoline = ",  self.model['infoline']
		
#creating a handler as gmplNbPatientSelector_handler from gui/gmplNbPatientSelector.py
# []
#creating a handler as gmplNbSchedule_handler from gui/gmplNbSchedule.py
# []
