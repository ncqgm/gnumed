# scanning for section headers,
	#	then for components in file  gmEditArea.py 
	#	and generating a script template for attaching
	#	a listener to the components.  

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

		
	
# type_search_str =  class\s+(?P<new_type>\w+)\s*\(.*(?P<base_type>wxTextCtrl|wxComboBox|wxButton|wxRadioButton|wxCheckBox|wxListBox)
# found new type = EditAreaTextBox which is base_type wxTextCtrl


class gmSECTION_SUMMARY_handler(base_handler):
	
	def __init__(self, panel, model = None, impl = None):
		base_handler.__init__(self, panel, model, impl)
		

	def set_name_map(self):
		map = {}
		
 
		comp_map = { 'component': self.get_valid_component('btnOK') ,
			'setter': self.get_valid_func( 'btnOK', 'None')  ,
			'comp_name' : 'btnOK','setter_name' :  'None' } 
		map['btnOK'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('btnClear') ,
			'setter': self.get_valid_func( 'btnClear', 'None')  ,
			'comp_name' : 'btnClear','setter_name' :  'None' } 
		map['btnClear'] = comp_map
		

		self.name_map = map
	

	def set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('btnOK'):
			self.set_id_common( 'btnOK',self.panel.btnOK)
			

		if self.panel.__dict__.has_key('btnClear'):
			self.set_id_common( 'btnClear',self.panel.btnClear)
			

	def set_evt(self):
		pass
		

		if self.panel.__dict__.has_key('btnOK'):
			EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.btnOK_button_clicked)

		if self.panel.__dict__.has_key('btnClear'):
			EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.btnClear_button_clicked)

	def btnOK_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btnOK_button_clicked(self, event) 
			

		print "btnOK_button_clicked received ", event
			

	def btnClear_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btnClear_button_clicked(self, event) 
			

		print "btnClear_button_clicked received ", event
			

class gmSECTION_DEMOGRAPHICS_handler(base_handler):
	
	def __init__(self, panel, model = None, impl = None):
		base_handler.__init__(self, panel, model, impl)
		

	def set_name_map(self):
		map = {}
		
 
		comp_map = { 'component': self.get_valid_component('btnOK') ,
			'setter': self.get_valid_func( 'btnOK', 'None')  ,
			'comp_name' : 'btnOK','setter_name' :  'None' } 
		map['btnOK'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('btnClear') ,
			'setter': self.get_valid_func( 'btnClear', 'None')  ,
			'comp_name' : 'btnClear','setter_name' :  'None' } 
		map['btnClear'] = comp_map
		

		self.name_map = map
	

	def set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('btnOK'):
			self.set_id_common( 'btnOK',self.panel.btnOK)
			

		if self.panel.__dict__.has_key('btnClear'):
			self.set_id_common( 'btnClear',self.panel.btnClear)
			

	def set_evt(self):
		pass
		

		if self.panel.__dict__.has_key('btnOK'):
			EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.btnOK_button_clicked)

		if self.panel.__dict__.has_key('btnClear'):
			EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.btnClear_button_clicked)

	def btnOK_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btnOK_button_clicked(self, event) 
			

		print "btnOK_button_clicked received ", event
			

	def btnClear_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btnClear_button_clicked(self, event) 
			

		print "btnClear_button_clicked received ", event
			

class gmSECTION_CLINICALNOTES_handler(base_handler):
	
	def __init__(self, panel, model = None, impl = None):
		base_handler.__init__(self, panel, model, impl)
		

	def set_name_map(self):
		map = {}
		
 
		comp_map = { 'component': self.get_valid_component('btnOK') ,
			'setter': self.get_valid_func( 'btnOK', 'None')  ,
			'comp_name' : 'btnOK','setter_name' :  'None' } 
		map['btnOK'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('btnClear') ,
			'setter': self.get_valid_func( 'btnClear', 'None')  ,
			'comp_name' : 'btnClear','setter_name' :  'None' } 
		map['btnClear'] = comp_map
		

		self.name_map = map
	

	def set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('btnOK'):
			self.set_id_common( 'btnOK',self.panel.btnOK)
			

		if self.panel.__dict__.has_key('btnClear'):
			self.set_id_common( 'btnClear',self.panel.btnClear)
			

	def set_evt(self):
		pass
		

		if self.panel.__dict__.has_key('btnOK'):
			EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.btnOK_button_clicked)

		if self.panel.__dict__.has_key('btnClear'):
			EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.btnClear_button_clicked)

	def btnOK_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btnOK_button_clicked(self, event) 
			

		print "btnOK_button_clicked received ", event
			

	def btnClear_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btnClear_button_clicked(self, event) 
			

		print "btnClear_button_clicked received ", event
			

class gmSECTION_FAMILYHISTORY_handler(base_handler):
	
	def __init__(self, panel, model = None, impl = None):
		base_handler.__init__(self, panel, model, impl)
		

	def set_name_map(self):
		map = {}
		
 
		comp_map = { 'component': self.get_valid_component('btnOK') ,
			'setter': self.get_valid_func( 'btnOK', 'None')  ,
			'comp_name' : 'btnOK','setter_name' :  'None' } 
		map['btnOK'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('btnClear') ,
			'setter': self.get_valid_func( 'btnClear', 'None')  ,
			'comp_name' : 'btnClear','setter_name' :  'None' } 
		map['btnClear'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_familymembername') ,
			'setter': self.get_valid_func( 'txt_familymembername', 'SetValue')  ,
			'comp_name' : 'txt_familymembername','setter_name' :  'SetValue' } 
		map['familymembername'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_familymemberrelationship') ,
			'setter': self.get_valid_func( 'txt_familymemberrelationship', 'SetValue')  ,
			'comp_name' : 'txt_familymemberrelationship','setter_name' :  'SetValue' } 
		map['familymemberrelationship'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_familymembercondition') ,
			'setter': self.get_valid_func( 'txt_familymembercondition', 'SetValue')  ,
			'comp_name' : 'txt_familymembercondition','setter_name' :  'SetValue' } 
		map['familymembercondition'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_familymemberconditioncomment') ,
			'setter': self.get_valid_func( 'txt_familymemberconditioncomment', 'SetValue')  ,
			'comp_name' : 'txt_familymemberconditioncomment','setter_name' :  'SetValue' } 
		map['familymemberconditioncomment'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_familymemberage_onset') ,
			'setter': self.get_valid_func( 'txt_familymemberage_onset', 'SetValue')  ,
			'comp_name' : 'txt_familymemberage_onset','setter_name' :  'SetValue' } 
		map['familymemberage_onset'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_familymembercaused_death') ,
			'setter': self.get_valid_func( 'txt_familymembercaused_death', 'SetValue')  ,
			'comp_name' : 'txt_familymembercaused_death','setter_name' :  'SetValue' } 
		map['familymembercaused_death'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_familymemberage_death') ,
			'setter': self.get_valid_func( 'txt_familymemberage_death', 'SetValue')  ,
			'comp_name' : 'txt_familymemberage_death','setter_name' :  'SetValue' } 
		map['familymemberage_death'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_familymemberprogressnotes') ,
			'setter': self.get_valid_func( 'txt_familymemberprogressnotes', 'SetValue')  ,
			'comp_name' : 'txt_familymemberprogressnotes','setter_name' :  'SetValue' } 
		map['familymemberprogressnotes'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_familymemberdate_of_birth') ,
			'setter': self.get_valid_func( 'txt_familymemberdate_of_birth', 'SetValue')  ,
			'comp_name' : 'txt_familymemberdate_of_birth','setter_name' :  'SetValue' } 
		map['familymemberdate_of_birth'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('rb_familymember_conditionconfidential') ,
			'setter': self.get_valid_func( 'rb_familymember_conditionconfidential', 'SetValue')  ,
			'comp_name' : 'rb_familymember_conditionconfidential','setter_name' :  'SetValue' } 
		map['familymember_conditionconfidential'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('btn_familymembernextcondition') ,
			'setter': self.get_valid_func( 'btn_familymembernextcondition', 'None')  ,
			'comp_name' : 'btn_familymembernextcondition','setter_name' :  'None' } 
		map['familymembernextcondition'] = comp_map
		

		self.name_map = map
	

	def set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('btnOK'):
			self.set_id_common( 'btnOK',self.panel.btnOK)
			

		if self.panel.__dict__.has_key('btnClear'):
			self.set_id_common( 'btnClear',self.panel.btnClear)
			

		if self.panel.__dict__.has_key('txt_familymembername'):
			self.set_id_common( 'txt_familymembername',self.panel.txt_familymembername)
			

		if self.panel.__dict__.has_key('txt_familymemberrelationship'):
			self.set_id_common( 'txt_familymemberrelationship',self.panel.txt_familymemberrelationship)
			

		if self.panel.__dict__.has_key('txt_familymembercondition'):
			self.set_id_common( 'txt_familymembercondition',self.panel.txt_familymembercondition)
			

		if self.panel.__dict__.has_key('txt_familymemberconditioncomment'):
			self.set_id_common( 'txt_familymemberconditioncomment',self.panel.txt_familymemberconditioncomment)
			

		if self.panel.__dict__.has_key('txt_familymemberage_onset'):
			self.set_id_common( 'txt_familymemberage_onset',self.panel.txt_familymemberage_onset)
			

		if self.panel.__dict__.has_key('txt_familymembercaused_death'):
			self.set_id_common( 'txt_familymembercaused_death',self.panel.txt_familymembercaused_death)
			

		if self.panel.__dict__.has_key('txt_familymemberage_death'):
			self.set_id_common( 'txt_familymemberage_death',self.panel.txt_familymemberage_death)
			

		if self.panel.__dict__.has_key('txt_familymemberprogressnotes'):
			self.set_id_common( 'txt_familymemberprogressnotes',self.panel.txt_familymemberprogressnotes)
			

		if self.panel.__dict__.has_key('txt_familymemberdate_of_birth'):
			self.set_id_common( 'txt_familymemberdate_of_birth',self.panel.txt_familymemberdate_of_birth)
			

		if self.panel.__dict__.has_key('rb_familymember_conditionconfidential'):
			self.set_id_common( 'rb_familymember_conditionconfidential',self.panel.rb_familymember_conditionconfidential)
			

		if self.panel.__dict__.has_key('btn_familymembernextcondition'):
			self.set_id_common( 'btn_familymembernextcondition',self.panel.btn_familymembernextcondition)
			

	def set_evt(self):
		pass
		

		if self.panel.__dict__.has_key('btnOK'):
			EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.btnOK_button_clicked)

		if self.panel.__dict__.has_key('btnClear'):
			EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.btnClear_button_clicked)

		if self.panel.__dict__.has_key('txt_familymembername'):
			EVT_TEXT(self.panel.txt_familymembername,\
			self.id_map['txt_familymembername'],\
			self.txt_familymembername_text_entered)

		if self.panel.__dict__.has_key('txt_familymemberrelationship'):
			EVT_TEXT(self.panel.txt_familymemberrelationship,\
			self.id_map['txt_familymemberrelationship'],\
			self.txt_familymemberrelationship_text_entered)

		if self.panel.__dict__.has_key('txt_familymembercondition'):
			EVT_TEXT(self.panel.txt_familymembercondition,\
			self.id_map['txt_familymembercondition'],\
			self.txt_familymembercondition_text_entered)

		if self.panel.__dict__.has_key('txt_familymemberconditioncomment'):
			EVT_TEXT(self.panel.txt_familymemberconditioncomment,\
			self.id_map['txt_familymemberconditioncomment'],\
			self.txt_familymemberconditioncomment_text_entered)

		if self.panel.__dict__.has_key('txt_familymemberage_onset'):
			EVT_TEXT(self.panel.txt_familymemberage_onset,\
			self.id_map['txt_familymemberage_onset'],\
			self.txt_familymemberage_onset_text_entered)

		if self.panel.__dict__.has_key('txt_familymembercaused_death'):
			EVT_TEXT(self.panel.txt_familymembercaused_death,\
			self.id_map['txt_familymembercaused_death'],\
			self.txt_familymembercaused_death_text_entered)

		if self.panel.__dict__.has_key('txt_familymemberage_death'):
			EVT_TEXT(self.panel.txt_familymemberage_death,\
			self.id_map['txt_familymemberage_death'],\
			self.txt_familymemberage_death_text_entered)

		if self.panel.__dict__.has_key('txt_familymemberprogressnotes'):
			EVT_TEXT(self.panel.txt_familymemberprogressnotes,\
			self.id_map['txt_familymemberprogressnotes'],\
			self.txt_familymemberprogressnotes_text_entered)

		if self.panel.__dict__.has_key('txt_familymemberdate_of_birth'):
			EVT_TEXT(self.panel.txt_familymemberdate_of_birth,\
			self.id_map['txt_familymemberdate_of_birth'],\
			self.txt_familymemberdate_of_birth_text_entered)

		if self.panel.__dict__.has_key('rb_familymember_conditionconfidential'):
			EVT_RADIOBUTTON(self.panel.rb_familymember_conditionconfidential,\
			self.id_map['rb_familymember_conditionconfidential'],\
			self.rb_familymember_conditionconfidential_radiobutton_clicked)

		if self.panel.__dict__.has_key('btn_familymembernextcondition'):
			EVT_BUTTON(self.panel.btn_familymembernextcondition,\
			self.id_map['btn_familymembernextcondition'],\
			self.btn_familymembernextcondition_button_clicked)

	def btnOK_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btnOK_button_clicked(self, event) 
			

		print "btnOK_button_clicked received ", event
			

	def btnClear_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btnClear_button_clicked(self, event) 
			

		print "btnClear_button_clicked received ", event
			

	def txt_familymembername_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_familymembername_text_entered(self, event) 
			

		print "txt_familymembername_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['familymembername']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['familymembername'] = str(obj.GetValue())
				
			print self.model, "familymembername = ",  self.model['familymembername']
		

	def txt_familymemberrelationship_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_familymemberrelationship_text_entered(self, event) 
			

		print "txt_familymemberrelationship_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['familymemberrelationship']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['familymemberrelationship'] = str(obj.GetValue())
				
			print self.model, "familymemberrelationship = ",  self.model['familymemberrelationship']
		

	def txt_familymembercondition_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_familymembercondition_text_entered(self, event) 
			

		print "txt_familymembercondition_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['familymembercondition']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['familymembercondition'] = str(obj.GetValue())
				
			print self.model, "familymembercondition = ",  self.model['familymembercondition']
		

	def txt_familymemberconditioncomment_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_familymemberconditioncomment_text_entered(self, event) 
			

		print "txt_familymemberconditioncomment_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['familymemberconditioncomment']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['familymemberconditioncomment'] = str(obj.GetValue())
				
			print self.model, "familymemberconditioncomment = ",  self.model['familymemberconditioncomment']
		

	def txt_familymemberage_onset_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_familymemberage_onset_text_entered(self, event) 
			

		print "txt_familymemberage_onset_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['familymemberage_onset']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['familymemberage_onset'] = str(obj.GetValue())
				
			print self.model, "familymemberage_onset = ",  self.model['familymemberage_onset']
		

	def txt_familymembercaused_death_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_familymembercaused_death_text_entered(self, event) 
			

		print "txt_familymembercaused_death_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['familymembercaused_death']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['familymembercaused_death'] = str(obj.GetValue())
				
			print self.model, "familymembercaused_death = ",  self.model['familymembercaused_death']
		

	def txt_familymemberage_death_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_familymemberage_death_text_entered(self, event) 
			

		print "txt_familymemberage_death_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['familymemberage_death']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['familymemberage_death'] = str(obj.GetValue())
				
			print self.model, "familymemberage_death = ",  self.model['familymemberage_death']
		

	def txt_familymemberprogressnotes_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_familymemberprogressnotes_text_entered(self, event) 
			

		print "txt_familymemberprogressnotes_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['familymemberprogressnotes']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['familymemberprogressnotes'] = str(obj.GetValue())
				
			print self.model, "familymemberprogressnotes = ",  self.model['familymemberprogressnotes']
		

	def txt_familymemberdate_of_birth_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_familymemberdate_of_birth_text_entered(self, event) 
			

		print "txt_familymemberdate_of_birth_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['familymemberdate_of_birth']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['familymemberdate_of_birth'] = str(obj.GetValue())
				
			print self.model, "familymemberdate_of_birth = ",  self.model['familymemberdate_of_birth']
		

	def rb_familymember_conditionconfidential_radiobutton_clicked( self, event): 
		if self.impl <> None:
			self.impl.rb_familymember_conditionconfidential_radiobutton_clicked(self, event) 
			

		print "rb_familymember_conditionconfidential_radiobutton_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['familymember_conditionconfidential']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['familymember_conditionconfidential'] = str(obj.GetValue())
				
			print self.model, "familymember_conditionconfidential = ",  self.model['familymember_conditionconfidential']
		

	def btn_familymembernextcondition_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btn_familymembernextcondition_button_clicked(self, event) 
			

		print "btn_familymembernextcondition_button_clicked received ", event
			

class gmSECTION_PASTHISTORY_handler(base_handler):
	
	def __init__(self, panel, model = None, impl = None):
		base_handler.__init__(self, panel, model, impl)
		

	def set_name_map(self):
		map = {}
		
 
		comp_map = { 'component': self.get_valid_component('btnOK') ,
			'setter': self.get_valid_func( 'btnOK', 'None')  ,
			'comp_name' : 'btnOK','setter_name' :  'None' } 
		map['btnOK'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('btnClear') ,
			'setter': self.get_valid_func( 'btnClear', 'None')  ,
			'comp_name' : 'btnClear','setter_name' :  'None' } 
		map['btnClear'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_condition') ,
			'setter': self.get_valid_func( 'txt_condition', 'SetValue')  ,
			'comp_name' : 'txt_condition','setter_name' :  'SetValue' } 
		map['condition'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('rb_sideleft') ,
			'setter': self.get_valid_func( 'rb_sideleft', 'SetValue')  ,
			'comp_name' : 'rb_sideleft','setter_name' :  'SetValue' } 
		map['sideleft'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('rb_sideright') ,
			'setter': self.get_valid_func( 'rb_sideright', 'SetValue')  ,
			'comp_name' : 'rb_sideright','setter_name' :  'SetValue' } 
		map['sideright'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('rb_sideboth') ,
			'setter': self.get_valid_func( 'rb_sideboth', 'SetValue')  ,
			'comp_name' : 'rb_sideboth','setter_name' :  'SetValue' } 
		map['sideboth'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_notes1') ,
			'setter': self.get_valid_func( 'txt_notes1', 'SetValue')  ,
			'comp_name' : 'txt_notes1','setter_name' :  'SetValue' } 
		map['notes1'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_notes2') ,
			'setter': self.get_valid_func( 'txt_notes2', 'SetValue')  ,
			'comp_name' : 'txt_notes2','setter_name' :  'SetValue' } 
		map['notes2'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_agenoted') ,
			'setter': self.get_valid_func( 'txt_agenoted', 'SetValue')  ,
			'comp_name' : 'txt_agenoted','setter_name' :  'SetValue' } 
		map['agenoted'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_yearnoted') ,
			'setter': self.get_valid_func( 'txt_yearnoted', 'SetValue')  ,
			'comp_name' : 'txt_yearnoted','setter_name' :  'SetValue' } 
		map['yearnoted'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('cb_active') ,
			'setter': self.get_valid_func( 'cb_active', 'SetValue')  ,
			'comp_name' : 'cb_active','setter_name' :  'SetValue' } 
		map['active'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('cb_operation') ,
			'setter': self.get_valid_func( 'cb_operation', 'SetValue')  ,
			'comp_name' : 'cb_operation','setter_name' :  'SetValue' } 
		map['operation'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('cb_confidential') ,
			'setter': self.get_valid_func( 'cb_confidential', 'SetValue')  ,
			'comp_name' : 'cb_confidential','setter_name' :  'SetValue' } 
		map['confidential'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('cb_significant') ,
			'setter': self.get_valid_func( 'cb_significant', 'SetValue')  ,
			'comp_name' : 'cb_significant','setter_name' :  'SetValue' } 
		map['significant'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_progressnotes') ,
			'setter': self.get_valid_func( 'txt_progressnotes', 'SetValue')  ,
			'comp_name' : 'txt_progressnotes','setter_name' :  'SetValue' } 
		map['progressnotes'] = comp_map
		

		self.name_map = map
	

	def set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('btnOK'):
			self.set_id_common( 'btnOK',self.panel.btnOK)
			

		if self.panel.__dict__.has_key('btnClear'):
			self.set_id_common( 'btnClear',self.panel.btnClear)
			

		if self.panel.__dict__.has_key('txt_condition'):
			self.set_id_common( 'txt_condition',self.panel.txt_condition)
			

		if self.panel.__dict__.has_key('rb_sideleft'):
			self.set_id_common( 'rb_sideleft',self.panel.rb_sideleft)
			

		if self.panel.__dict__.has_key('rb_sideright'):
			self.set_id_common( 'rb_sideright',self.panel.rb_sideright)
			

		if self.panel.__dict__.has_key('rb_sideboth'):
			self.set_id_common( 'rb_sideboth',self.panel.rb_sideboth)
			

		if self.panel.__dict__.has_key('txt_notes1'):
			self.set_id_common( 'txt_notes1',self.panel.txt_notes1)
			

		if self.panel.__dict__.has_key('txt_notes2'):
			self.set_id_common( 'txt_notes2',self.panel.txt_notes2)
			

		if self.panel.__dict__.has_key('txt_agenoted'):
			self.set_id_common( 'txt_agenoted',self.panel.txt_agenoted)
			

		if self.panel.__dict__.has_key('txt_yearnoted'):
			self.set_id_common( 'txt_yearnoted',self.panel.txt_yearnoted)
			

		if self.panel.__dict__.has_key('cb_active'):
			self.set_id_common( 'cb_active',self.panel.cb_active)
			

		if self.panel.__dict__.has_key('cb_operation'):
			self.set_id_common( 'cb_operation',self.panel.cb_operation)
			

		if self.panel.__dict__.has_key('cb_confidential'):
			self.set_id_common( 'cb_confidential',self.panel.cb_confidential)
			

		if self.panel.__dict__.has_key('cb_significant'):
			self.set_id_common( 'cb_significant',self.panel.cb_significant)
			

		if self.panel.__dict__.has_key('txt_progressnotes'):
			self.set_id_common( 'txt_progressnotes',self.panel.txt_progressnotes)
			

	def set_evt(self):
		pass
		

		if self.panel.__dict__.has_key('btnOK'):
			EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.btnOK_button_clicked)

		if self.panel.__dict__.has_key('btnClear'):
			EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.btnClear_button_clicked)

		if self.panel.__dict__.has_key('txt_condition'):
			EVT_TEXT(self.panel.txt_condition,\
			self.id_map['txt_condition'],\
			self.txt_condition_text_entered)

		if self.panel.__dict__.has_key('rb_sideleft'):
			EVT_RADIOBUTTON(self.panel.rb_sideleft,\
			self.id_map['rb_sideleft'],\
			self.rb_sideleft_radiobutton_clicked)

		if self.panel.__dict__.has_key('rb_sideright'):
			EVT_RADIOBUTTON(self.panel.rb_sideright,\
			self.id_map['rb_sideright'],\
			self.rb_sideright_radiobutton_clicked)

		if self.panel.__dict__.has_key('rb_sideboth'):
			EVT_RADIOBUTTON(self.panel.rb_sideboth,\
			self.id_map['rb_sideboth'],\
			self.rb_sideboth_radiobutton_clicked)

		if self.panel.__dict__.has_key('txt_notes1'):
			EVT_TEXT(self.panel.txt_notes1,\
			self.id_map['txt_notes1'],\
			self.txt_notes1_text_entered)

		if self.panel.__dict__.has_key('txt_notes2'):
			EVT_TEXT(self.panel.txt_notes2,\
			self.id_map['txt_notes2'],\
			self.txt_notes2_text_entered)

		if self.panel.__dict__.has_key('txt_agenoted'):
			EVT_TEXT(self.panel.txt_agenoted,\
			self.id_map['txt_agenoted'],\
			self.txt_agenoted_text_entered)

		if self.panel.__dict__.has_key('txt_yearnoted'):
			EVT_TEXT(self.panel.txt_yearnoted,\
			self.id_map['txt_yearnoted'],\
			self.txt_yearnoted_text_entered)

		if self.panel.__dict__.has_key('cb_active'):
			EVT_CHECKBOX(self.panel.cb_active,\
			self.id_map['cb_active'],\
			self.cb_active_checkbox_clicked)

		if self.panel.__dict__.has_key('cb_operation'):
			EVT_CHECKBOX(self.panel.cb_operation,\
			self.id_map['cb_operation'],\
			self.cb_operation_checkbox_clicked)

		if self.panel.__dict__.has_key('cb_confidential'):
			EVT_CHECKBOX(self.panel.cb_confidential,\
			self.id_map['cb_confidential'],\
			self.cb_confidential_checkbox_clicked)

		if self.panel.__dict__.has_key('cb_significant'):
			EVT_CHECKBOX(self.panel.cb_significant,\
			self.id_map['cb_significant'],\
			self.cb_significant_checkbox_clicked)

		if self.panel.__dict__.has_key('txt_progressnotes'):
			EVT_TEXT(self.panel.txt_progressnotes,\
			self.id_map['txt_progressnotes'],\
			self.txt_progressnotes_text_entered)

	def btnOK_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btnOK_button_clicked(self, event) 
			

		print "btnOK_button_clicked received ", event
			

	def btnClear_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btnClear_button_clicked(self, event) 
			

		print "btnClear_button_clicked received ", event
			

	def txt_condition_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_condition_text_entered(self, event) 
			

		print "txt_condition_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['condition']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['condition'] = str(obj.GetValue())
				
			print self.model, "condition = ",  self.model['condition']
		

	def rb_sideleft_radiobutton_clicked( self, event): 
		if self.impl <> None:
			self.impl.rb_sideleft_radiobutton_clicked(self, event) 
			

		print "rb_sideleft_radiobutton_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['sideleft']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['sideleft'] = str(obj.GetValue())
				
			print self.model, "sideleft = ",  self.model['sideleft']
		

	def rb_sideright_radiobutton_clicked( self, event): 
		if self.impl <> None:
			self.impl.rb_sideright_radiobutton_clicked(self, event) 
			

		print "rb_sideright_radiobutton_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['sideright']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['sideright'] = str(obj.GetValue())
				
			print self.model, "sideright = ",  self.model['sideright']
		

	def rb_sideboth_radiobutton_clicked( self, event): 
		if self.impl <> None:
			self.impl.rb_sideboth_radiobutton_clicked(self, event) 
			

		print "rb_sideboth_radiobutton_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['sideboth']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['sideboth'] = str(obj.GetValue())
				
			print self.model, "sideboth = ",  self.model['sideboth']
		

	def txt_notes1_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_notes1_text_entered(self, event) 
			

		print "txt_notes1_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['notes1']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['notes1'] = str(obj.GetValue())
				
			print self.model, "notes1 = ",  self.model['notes1']
		

	def txt_notes2_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_notes2_text_entered(self, event) 
			

		print "txt_notes2_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['notes2']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['notes2'] = str(obj.GetValue())
				
			print self.model, "notes2 = ",  self.model['notes2']
		

	def txt_agenoted_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_agenoted_text_entered(self, event) 
			

		print "txt_agenoted_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['agenoted']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['agenoted'] = str(obj.GetValue())
				
			print self.model, "agenoted = ",  self.model['agenoted']
		

	def txt_yearnoted_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_yearnoted_text_entered(self, event) 
			

		print "txt_yearnoted_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['yearnoted']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['yearnoted'] = str(obj.GetValue())
				
			print self.model, "yearnoted = ",  self.model['yearnoted']
		

	def cb_active_checkbox_clicked( self, event): 
		if self.impl <> None:
			self.impl.cb_active_checkbox_clicked(self, event) 
			

		print "cb_active_checkbox_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['active']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['active'] = str(obj.GetValue())
				
			print self.model, "active = ",  self.model['active']
		

	def cb_operation_checkbox_clicked( self, event): 
		if self.impl <> None:
			self.impl.cb_operation_checkbox_clicked(self, event) 
			

		print "cb_operation_checkbox_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['operation']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['operation'] = str(obj.GetValue())
				
			print self.model, "operation = ",  self.model['operation']
		

	def cb_confidential_checkbox_clicked( self, event): 
		if self.impl <> None:
			self.impl.cb_confidential_checkbox_clicked(self, event) 
			

		print "cb_confidential_checkbox_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['confidential']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['confidential'] = str(obj.GetValue())
				
			print self.model, "confidential = ",  self.model['confidential']
		

	def cb_significant_checkbox_clicked( self, event): 
		if self.impl <> None:
			self.impl.cb_significant_checkbox_clicked(self, event) 
			

		print "cb_significant_checkbox_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['significant']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['significant'] = str(obj.GetValue())
				
			print self.model, "significant = ",  self.model['significant']
		

	def txt_progressnotes_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_progressnotes_text_entered(self, event) 
			

		print "txt_progressnotes_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['progressnotes']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['progressnotes'] = str(obj.GetValue())
				
			print self.model, "progressnotes = ",  self.model['progressnotes']
		

class gmSECTION_VACCINATION_handler(base_handler):
	
	def __init__(self, panel, model = None, impl = None):
		base_handler.__init__(self, panel, model, impl)
		

	def set_name_map(self):
		map = {}
		
 
		comp_map = { 'component': self.get_valid_component('btnOK') ,
			'setter': self.get_valid_func( 'btnOK', 'None')  ,
			'comp_name' : 'btnOK','setter_name' :  'None' } 
		map['btnOK'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('btnClear') ,
			'setter': self.get_valid_func( 'btnClear', 'None')  ,
			'comp_name' : 'btnClear','setter_name' :  'None' } 
		map['btnClear'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_targetdisease') ,
			'setter': self.get_valid_func( 'txt_targetdisease', 'SetValue')  ,
			'comp_name' : 'txt_targetdisease','setter_name' :  'SetValue' } 
		map['targetdisease'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_vaccine') ,
			'setter': self.get_valid_func( 'txt_vaccine', 'SetValue')  ,
			'comp_name' : 'txt_vaccine','setter_name' :  'SetValue' } 
		map['vaccine'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_dategiven') ,
			'setter': self.get_valid_func( 'txt_dategiven', 'SetValue')  ,
			'comp_name' : 'txt_dategiven','setter_name' :  'SetValue' } 
		map['dategiven'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_serialno') ,
			'setter': self.get_valid_func( 'txt_serialno', 'SetValue')  ,
			'comp_name' : 'txt_serialno','setter_name' :  'SetValue' } 
		map['serialno'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_sitegiven') ,
			'setter': self.get_valid_func( 'txt_sitegiven', 'SetValue')  ,
			'comp_name' : 'txt_sitegiven','setter_name' :  'SetValue' } 
		map['sitegiven'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_progressnotes') ,
			'setter': self.get_valid_func( 'txt_progressnotes', 'SetValue')  ,
			'comp_name' : 'txt_progressnotes','setter_name' :  'SetValue' } 
		map['progressnotes'] = comp_map
		

		self.name_map = map
	

	def set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('btnOK'):
			self.set_id_common( 'btnOK',self.panel.btnOK)
			

		if self.panel.__dict__.has_key('btnClear'):
			self.set_id_common( 'btnClear',self.panel.btnClear)
			

		if self.panel.__dict__.has_key('txt_targetdisease'):
			self.set_id_common( 'txt_targetdisease',self.panel.txt_targetdisease)
			

		if self.panel.__dict__.has_key('txt_vaccine'):
			self.set_id_common( 'txt_vaccine',self.panel.txt_vaccine)
			

		if self.panel.__dict__.has_key('txt_dategiven'):
			self.set_id_common( 'txt_dategiven',self.panel.txt_dategiven)
			

		if self.panel.__dict__.has_key('txt_serialno'):
			self.set_id_common( 'txt_serialno',self.panel.txt_serialno)
			

		if self.panel.__dict__.has_key('txt_sitegiven'):
			self.set_id_common( 'txt_sitegiven',self.panel.txt_sitegiven)
			

		if self.panel.__dict__.has_key('txt_progressnotes'):
			self.set_id_common( 'txt_progressnotes',self.panel.txt_progressnotes)
			

	def set_evt(self):
		pass
		

		if self.panel.__dict__.has_key('btnOK'):
			EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.btnOK_button_clicked)

		if self.panel.__dict__.has_key('btnClear'):
			EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.btnClear_button_clicked)

		if self.panel.__dict__.has_key('txt_targetdisease'):
			EVT_TEXT(self.panel.txt_targetdisease,\
			self.id_map['txt_targetdisease'],\
			self.txt_targetdisease_text_entered)

		if self.panel.__dict__.has_key('txt_vaccine'):
			EVT_TEXT(self.panel.txt_vaccine,\
			self.id_map['txt_vaccine'],\
			self.txt_vaccine_text_entered)

		if self.panel.__dict__.has_key('txt_dategiven'):
			EVT_TEXT(self.panel.txt_dategiven,\
			self.id_map['txt_dategiven'],\
			self.txt_dategiven_text_entered)

		if self.panel.__dict__.has_key('txt_serialno'):
			EVT_TEXT(self.panel.txt_serialno,\
			self.id_map['txt_serialno'],\
			self.txt_serialno_text_entered)

		if self.panel.__dict__.has_key('txt_sitegiven'):
			EVT_TEXT(self.panel.txt_sitegiven,\
			self.id_map['txt_sitegiven'],\
			self.txt_sitegiven_text_entered)

		if self.panel.__dict__.has_key('txt_progressnotes'):
			EVT_TEXT(self.panel.txt_progressnotes,\
			self.id_map['txt_progressnotes'],\
			self.txt_progressnotes_text_entered)

	def btnOK_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btnOK_button_clicked(self, event) 
			

		print "btnOK_button_clicked received ", event
			

	def btnClear_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btnClear_button_clicked(self, event) 
			

		print "btnClear_button_clicked received ", event
			

	def txt_targetdisease_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_targetdisease_text_entered(self, event) 
			

		print "txt_targetdisease_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['targetdisease']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['targetdisease'] = str(obj.GetValue())
				
			print self.model, "targetdisease = ",  self.model['targetdisease']
		

	def txt_vaccine_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_vaccine_text_entered(self, event) 
			

		print "txt_vaccine_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['vaccine']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['vaccine'] = str(obj.GetValue())
				
			print self.model, "vaccine = ",  self.model['vaccine']
		

	def txt_dategiven_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_dategiven_text_entered(self, event) 
			

		print "txt_dategiven_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['dategiven']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['dategiven'] = str(obj.GetValue())
				
			print self.model, "dategiven = ",  self.model['dategiven']
		

	def txt_serialno_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_serialno_text_entered(self, event) 
			

		print "txt_serialno_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['serialno']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['serialno'] = str(obj.GetValue())
				
			print self.model, "serialno = ",  self.model['serialno']
		

	def txt_sitegiven_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_sitegiven_text_entered(self, event) 
			

		print "txt_sitegiven_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['sitegiven']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['sitegiven'] = str(obj.GetValue())
				
			print self.model, "sitegiven = ",  self.model['sitegiven']
		

	def txt_progressnotes_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_progressnotes_text_entered(self, event) 
			

		print "txt_progressnotes_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['progressnotes']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['progressnotes'] = str(obj.GetValue())
				
			print self.model, "progressnotes = ",  self.model['progressnotes']
		

class gmSECTION_ALLERGIES_handler(base_handler):
	
	def __init__(self, panel, model = None, impl = None):
		base_handler.__init__(self, panel, model, impl)
		

	def set_name_map(self):
		map = {}
		
 
		comp_map = { 'component': self.get_valid_component('btnOK') ,
			'setter': self.get_valid_func( 'btnOK', 'None')  ,
			'comp_name' : 'btnOK','setter_name' :  'None' } 
		map['btnOK'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('btnClear') ,
			'setter': self.get_valid_func( 'btnClear', 'None')  ,
			'comp_name' : 'btnClear','setter_name' :  'None' } 
		map['btnClear'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('text1') ,
			'setter': self.get_valid_func( 'text1', 'SetValue')  ,
			'comp_name' : 'text1','setter_name' :  'SetValue' } 
		map['text1'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('text2') ,
			'setter': self.get_valid_func( 'text2', 'SetValue')  ,
			'comp_name' : 'text2','setter_name' :  'SetValue' } 
		map['text2'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('text3') ,
			'setter': self.get_valid_func( 'text3', 'SetValue')  ,
			'comp_name' : 'text3','setter_name' :  'SetValue' } 
		map['text3'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('text4') ,
			'setter': self.get_valid_func( 'text4', 'SetValue')  ,
			'comp_name' : 'text4','setter_name' :  'SetValue' } 
		map['text4'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('text5') ,
			'setter': self.get_valid_func( 'text5', 'SetValue')  ,
			'comp_name' : 'text5','setter_name' :  'SetValue' } 
		map['text5'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('cb1') ,
			'setter': self.get_valid_func( 'cb1', 'SetValue')  ,
			'comp_name' : 'cb1','setter_name' :  'SetValue' } 
		map['cb1'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('rb1') ,
			'setter': self.get_valid_func( 'rb1', 'SetValue')  ,
			'comp_name' : 'rb1','setter_name' :  'SetValue' } 
		map['rb1'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('rb2') ,
			'setter': self.get_valid_func( 'rb2', 'SetValue')  ,
			'comp_name' : 'rb2','setter_name' :  'SetValue' } 
		map['rb2'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('cb2') ,
			'setter': self.get_valid_func( 'cb2', 'SetValue')  ,
			'comp_name' : 'cb2','setter_name' :  'SetValue' } 
		map['cb2'] = comp_map
		

		self.name_map = map
	

	def set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('btnOK'):
			self.set_id_common( 'btnOK',self.panel.btnOK)
			

		if self.panel.__dict__.has_key('btnClear'):
			self.set_id_common( 'btnClear',self.panel.btnClear)
			

		if self.panel.__dict__.has_key('text1'):
			self.set_id_common( 'text1',self.panel.text1)
			

		if self.panel.__dict__.has_key('text2'):
			self.set_id_common( 'text2',self.panel.text2)
			

		if self.panel.__dict__.has_key('text3'):
			self.set_id_common( 'text3',self.panel.text3)
			

		if self.panel.__dict__.has_key('text4'):
			self.set_id_common( 'text4',self.panel.text4)
			

		if self.panel.__dict__.has_key('text5'):
			self.set_id_common( 'text5',self.panel.text5)
			

		if self.panel.__dict__.has_key('cb1'):
			self.set_id_common( 'cb1',self.panel.cb1)
			

		if self.panel.__dict__.has_key('rb1'):
			self.set_id_common( 'rb1',self.panel.rb1)
			

		if self.panel.__dict__.has_key('rb2'):
			self.set_id_common( 'rb2',self.panel.rb2)
			

		if self.panel.__dict__.has_key('cb2'):
			self.set_id_common( 'cb2',self.panel.cb2)
			

	def set_evt(self):
		pass
		

		if self.panel.__dict__.has_key('btnOK'):
			EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.btnOK_button_clicked)

		if self.panel.__dict__.has_key('btnClear'):
			EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.btnClear_button_clicked)

		if self.panel.__dict__.has_key('text1'):
			EVT_TEXT(self.panel.text1,\
			self.id_map['text1'],\
			self.text1_text_entered)

		if self.panel.__dict__.has_key('text2'):
			EVT_TEXT(self.panel.text2,\
			self.id_map['text2'],\
			self.text2_text_entered)

		if self.panel.__dict__.has_key('text3'):
			EVT_TEXT(self.panel.text3,\
			self.id_map['text3'],\
			self.text3_text_entered)

		if self.panel.__dict__.has_key('text4'):
			EVT_TEXT(self.panel.text4,\
			self.id_map['text4'],\
			self.text4_text_entered)

		if self.panel.__dict__.has_key('text5'):
			EVT_TEXT(self.panel.text5,\
			self.id_map['text5'],\
			self.text5_text_entered)

		if self.panel.__dict__.has_key('cb1'):
			EVT_CHECKBOX(self.panel.cb1,\
			self.id_map['cb1'],\
			self.cb1_checkbox_clicked)

		if self.panel.__dict__.has_key('rb1'):
			EVT_RADIOBUTTON(self.panel.rb1,\
			self.id_map['rb1'],\
			self.rb1_radiobutton_clicked)

		if self.panel.__dict__.has_key('rb2'):
			EVT_RADIOBUTTON(self.panel.rb2,\
			self.id_map['rb2'],\
			self.rb2_radiobutton_clicked)

		if self.panel.__dict__.has_key('cb2'):
			EVT_CHECKBOX(self.panel.cb2,\
			self.id_map['cb2'],\
			self.cb2_checkbox_clicked)

	def btnOK_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btnOK_button_clicked(self, event) 
			

		print "btnOK_button_clicked received ", event
			

	def btnClear_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btnClear_button_clicked(self, event) 
			

		print "btnClear_button_clicked received ", event
			

	def text1_text_entered( self, event): 
		if self.impl <> None:
			self.impl.text1_text_entered(self, event) 
			

		print "text1_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['text1']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['text1'] = str(obj.GetValue())
				
			print self.model, "text1 = ",  self.model['text1']
		

	def text2_text_entered( self, event): 
		if self.impl <> None:
			self.impl.text2_text_entered(self, event) 
			

		print "text2_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['text2']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['text2'] = str(obj.GetValue())
				
			print self.model, "text2 = ",  self.model['text2']
		

	def text3_text_entered( self, event): 
		if self.impl <> None:
			self.impl.text3_text_entered(self, event) 
			

		print "text3_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['text3']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['text3'] = str(obj.GetValue())
				
			print self.model, "text3 = ",  self.model['text3']
		

	def text4_text_entered( self, event): 
		if self.impl <> None:
			self.impl.text4_text_entered(self, event) 
			

		print "text4_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['text4']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['text4'] = str(obj.GetValue())
				
			print self.model, "text4 = ",  self.model['text4']
		

	def text5_text_entered( self, event): 
		if self.impl <> None:
			self.impl.text5_text_entered(self, event) 
			

		print "text5_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['text5']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['text5'] = str(obj.GetValue())
				
			print self.model, "text5 = ",  self.model['text5']
		

	def cb1_checkbox_clicked( self, event): 
		if self.impl <> None:
			self.impl.cb1_checkbox_clicked(self, event) 
			

		print "cb1_checkbox_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['cb1']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['cb1'] = str(obj.GetValue())
				
			print self.model, "cb1 = ",  self.model['cb1']
		

	def rb1_radiobutton_clicked( self, event): 
		if self.impl <> None:
			self.impl.rb1_radiobutton_clicked(self, event) 
			

		print "rb1_radiobutton_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['rb1']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['rb1'] = str(obj.GetValue())
				
			print self.model, "rb1 = ",  self.model['rb1']
		

	def rb2_radiobutton_clicked( self, event): 
		if self.impl <> None:
			self.impl.rb2_radiobutton_clicked(self, event) 
			

		print "rb2_radiobutton_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['rb2']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['rb2'] = str(obj.GetValue())
				
			print self.model, "rb2 = ",  self.model['rb2']
		

	def cb2_checkbox_clicked( self, event): 
		if self.impl <> None:
			self.impl.cb2_checkbox_clicked(self, event) 
			

		print "cb2_checkbox_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['cb2']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['cb2'] = str(obj.GetValue())
				
			print self.model, "cb2 = ",  self.model['cb2']
		

class gmSECTION_SCRIPT_handler(base_handler):
	
	def __init__(self, panel, model = None, impl = None):
		base_handler.__init__(self, panel, model, impl)
		

	def set_name_map(self):
		map = {}
		
 
		comp_map = { 'component': self.get_valid_component('btnOK') ,
			'setter': self.get_valid_func( 'btnOK', 'None')  ,
			'comp_name' : 'btnOK','setter_name' :  'None' } 
		map['btnOK'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('btnClear') ,
			'setter': self.get_valid_func( 'btnClear', 'None')  ,
			'comp_name' : 'btnClear','setter_name' :  'None' } 
		map['btnClear'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('text1') ,
			'setter': self.get_valid_func( 'text1', 'SetValue')  ,
			'comp_name' : 'text1','setter_name' :  'SetValue' } 
		map['text1'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('text2') ,
			'setter': self.get_valid_func( 'text2', 'SetValue')  ,
			'comp_name' : 'text2','setter_name' :  'SetValue' } 
		map['text2'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('text3') ,
			'setter': self.get_valid_func( 'text3', 'SetValue')  ,
			'comp_name' : 'text3','setter_name' :  'SetValue' } 
		map['text3'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('text4') ,
			'setter': self.get_valid_func( 'text4', 'SetValue')  ,
			'comp_name' : 'text4','setter_name' :  'SetValue' } 
		map['text4'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('text5') ,
			'setter': self.get_valid_func( 'text5', 'SetValue')  ,
			'comp_name' : 'text5','setter_name' :  'SetValue' } 
		map['text5'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('text6') ,
			'setter': self.get_valid_func( 'text6', 'SetValue')  ,
			'comp_name' : 'text6','setter_name' :  'SetValue' } 
		map['text6'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('text7') ,
			'setter': self.get_valid_func( 'text7', 'SetValue')  ,
			'comp_name' : 'text7','setter_name' :  'SetValue' } 
		map['text7'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('text8') ,
			'setter': self.get_valid_func( 'text8', 'SetValue')  ,
			'comp_name' : 'text8','setter_name' :  'SetValue' } 
		map['text8'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('text9') ,
			'setter': self.get_valid_func( 'text9', 'SetValue')  ,
			'comp_name' : 'text9','setter_name' :  'SetValue' } 
		map['text9'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('cb_veteran') ,
			'setter': self.get_valid_func( 'cb_veteran', 'SetValue')  ,
			'comp_name' : 'cb_veteran','setter_name' :  'SetValue' } 
		map['veteran'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('cb_reg24') ,
			'setter': self.get_valid_func( 'cb_reg24', 'SetValue')  ,
			'comp_name' : 'cb_reg24','setter_name' :  'SetValue' } 
		map['reg24'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('cb_usualmed') ,
			'setter': self.get_valid_func( 'cb_usualmed', 'SetValue')  ,
			'comp_name' : 'cb_usualmed','setter_name' :  'SetValue' } 
		map['usualmed'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('btn_authority') ,
			'setter': self.get_valid_func( 'btn_authority', 'None')  ,
			'comp_name' : 'btn_authority','setter_name' :  'None' } 
		map['authority'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('btn_briefPI') ,
			'setter': self.get_valid_func( 'btn_briefPI', 'None')  ,
			'comp_name' : 'btn_briefPI','setter_name' :  'None' } 
		map['briefPI'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('text10') ,
			'setter': self.get_valid_func( 'text10', 'SetValue')  ,
			'comp_name' : 'text10','setter_name' :  'SetValue' } 
		map['text10'] = comp_map
		

		self.name_map = map
	

	def set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('btnOK'):
			self.set_id_common( 'btnOK',self.panel.btnOK)
			

		if self.panel.__dict__.has_key('btnClear'):
			self.set_id_common( 'btnClear',self.panel.btnClear)
			

		if self.panel.__dict__.has_key('text1'):
			self.set_id_common( 'text1',self.panel.text1)
			

		if self.panel.__dict__.has_key('text2'):
			self.set_id_common( 'text2',self.panel.text2)
			

		if self.panel.__dict__.has_key('text3'):
			self.set_id_common( 'text3',self.panel.text3)
			

		if self.panel.__dict__.has_key('text4'):
			self.set_id_common( 'text4',self.panel.text4)
			

		if self.panel.__dict__.has_key('text5'):
			self.set_id_common( 'text5',self.panel.text5)
			

		if self.panel.__dict__.has_key('text6'):
			self.set_id_common( 'text6',self.panel.text6)
			

		if self.panel.__dict__.has_key('text7'):
			self.set_id_common( 'text7',self.panel.text7)
			

		if self.panel.__dict__.has_key('text8'):
			self.set_id_common( 'text8',self.panel.text8)
			

		if self.panel.__dict__.has_key('text9'):
			self.set_id_common( 'text9',self.panel.text9)
			

		if self.panel.__dict__.has_key('cb_veteran'):
			self.set_id_common( 'cb_veteran',self.panel.cb_veteran)
			

		if self.panel.__dict__.has_key('cb_reg24'):
			self.set_id_common( 'cb_reg24',self.panel.cb_reg24)
			

		if self.panel.__dict__.has_key('cb_usualmed'):
			self.set_id_common( 'cb_usualmed',self.panel.cb_usualmed)
			

		if self.panel.__dict__.has_key('btn_authority'):
			self.set_id_common( 'btn_authority',self.panel.btn_authority)
			

		if self.panel.__dict__.has_key('btn_briefPI'):
			self.set_id_common( 'btn_briefPI',self.panel.btn_briefPI)
			

		if self.panel.__dict__.has_key('text10'):
			self.set_id_common( 'text10',self.panel.text10)
			

	def set_evt(self):
		pass
		

		if self.panel.__dict__.has_key('btnOK'):
			EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.btnOK_button_clicked)

		if self.panel.__dict__.has_key('btnClear'):
			EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.btnClear_button_clicked)

		if self.panel.__dict__.has_key('text1'):
			EVT_TEXT(self.panel.text1,\
			self.id_map['text1'],\
			self.text1_text_entered)

		if self.panel.__dict__.has_key('text2'):
			EVT_TEXT(self.panel.text2,\
			self.id_map['text2'],\
			self.text2_text_entered)

		if self.panel.__dict__.has_key('text3'):
			EVT_TEXT(self.panel.text3,\
			self.id_map['text3'],\
			self.text3_text_entered)

		if self.panel.__dict__.has_key('text4'):
			EVT_TEXT(self.panel.text4,\
			self.id_map['text4'],\
			self.text4_text_entered)

		if self.panel.__dict__.has_key('text5'):
			EVT_TEXT(self.panel.text5,\
			self.id_map['text5'],\
			self.text5_text_entered)

		if self.panel.__dict__.has_key('text6'):
			EVT_TEXT(self.panel.text6,\
			self.id_map['text6'],\
			self.text6_text_entered)

		if self.panel.__dict__.has_key('text7'):
			EVT_TEXT(self.panel.text7,\
			self.id_map['text7'],\
			self.text7_text_entered)

		if self.panel.__dict__.has_key('text8'):
			EVT_TEXT(self.panel.text8,\
			self.id_map['text8'],\
			self.text8_text_entered)

		if self.panel.__dict__.has_key('text9'):
			EVT_TEXT(self.panel.text9,\
			self.id_map['text9'],\
			self.text9_text_entered)

		if self.panel.__dict__.has_key('cb_veteran'):
			EVT_CHECKBOX(self.panel.cb_veteran,\
			self.id_map['cb_veteran'],\
			self.cb_veteran_checkbox_clicked)

		if self.panel.__dict__.has_key('cb_reg24'):
			EVT_CHECKBOX(self.panel.cb_reg24,\
			self.id_map['cb_reg24'],\
			self.cb_reg24_checkbox_clicked)

		if self.panel.__dict__.has_key('cb_usualmed'):
			EVT_CHECKBOX(self.panel.cb_usualmed,\
			self.id_map['cb_usualmed'],\
			self.cb_usualmed_checkbox_clicked)

		if self.panel.__dict__.has_key('btn_authority'):
			EVT_BUTTON(self.panel.btn_authority,\
			self.id_map['btn_authority'],\
			self.btn_authority_button_clicked)

		if self.panel.__dict__.has_key('btn_briefPI'):
			EVT_BUTTON(self.panel.btn_briefPI,\
			self.id_map['btn_briefPI'],\
			self.btn_briefPI_button_clicked)

		if self.panel.__dict__.has_key('text10'):
			EVT_TEXT(self.panel.text10,\
			self.id_map['text10'],\
			self.text10_text_entered)

	def btnOK_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btnOK_button_clicked(self, event) 
			

		print "btnOK_button_clicked received ", event
			

	def btnClear_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btnClear_button_clicked(self, event) 
			

		print "btnClear_button_clicked received ", event
			

	def text1_text_entered( self, event): 
		if self.impl <> None:
			self.impl.text1_text_entered(self, event) 
			

		print "text1_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['text1']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['text1'] = str(obj.GetValue())
				
			print self.model, "text1 = ",  self.model['text1']
		

	def text2_text_entered( self, event): 
		if self.impl <> None:
			self.impl.text2_text_entered(self, event) 
			

		print "text2_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['text2']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['text2'] = str(obj.GetValue())
				
			print self.model, "text2 = ",  self.model['text2']
		

	def text3_text_entered( self, event): 
		if self.impl <> None:
			self.impl.text3_text_entered(self, event) 
			

		print "text3_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['text3']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['text3'] = str(obj.GetValue())
				
			print self.model, "text3 = ",  self.model['text3']
		

	def text4_text_entered( self, event): 
		if self.impl <> None:
			self.impl.text4_text_entered(self, event) 
			

		print "text4_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['text4']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['text4'] = str(obj.GetValue())
				
			print self.model, "text4 = ",  self.model['text4']
		

	def text5_text_entered( self, event): 
		if self.impl <> None:
			self.impl.text5_text_entered(self, event) 
			

		print "text5_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['text5']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['text5'] = str(obj.GetValue())
				
			print self.model, "text5 = ",  self.model['text5']
		

	def text6_text_entered( self, event): 
		if self.impl <> None:
			self.impl.text6_text_entered(self, event) 
			

		print "text6_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['text6']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['text6'] = str(obj.GetValue())
				
			print self.model, "text6 = ",  self.model['text6']
		

	def text7_text_entered( self, event): 
		if self.impl <> None:
			self.impl.text7_text_entered(self, event) 
			

		print "text7_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['text7']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['text7'] = str(obj.GetValue())
				
			print self.model, "text7 = ",  self.model['text7']
		

	def text8_text_entered( self, event): 
		if self.impl <> None:
			self.impl.text8_text_entered(self, event) 
			

		print "text8_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['text8']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['text8'] = str(obj.GetValue())
				
			print self.model, "text8 = ",  self.model['text8']
		

	def text9_text_entered( self, event): 
		if self.impl <> None:
			self.impl.text9_text_entered(self, event) 
			

		print "text9_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['text9']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['text9'] = str(obj.GetValue())
				
			print self.model, "text9 = ",  self.model['text9']
		

	def cb_veteran_checkbox_clicked( self, event): 
		if self.impl <> None:
			self.impl.cb_veteran_checkbox_clicked(self, event) 
			

		print "cb_veteran_checkbox_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['veteran']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['veteran'] = str(obj.GetValue())
				
			print self.model, "veteran = ",  self.model['veteran']
		

	def cb_reg24_checkbox_clicked( self, event): 
		if self.impl <> None:
			self.impl.cb_reg24_checkbox_clicked(self, event) 
			

		print "cb_reg24_checkbox_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['reg24']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['reg24'] = str(obj.GetValue())
				
			print self.model, "reg24 = ",  self.model['reg24']
		

	def cb_usualmed_checkbox_clicked( self, event): 
		if self.impl <> None:
			self.impl.cb_usualmed_checkbox_clicked(self, event) 
			

		print "cb_usualmed_checkbox_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['usualmed']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['usualmed'] = str(obj.GetValue())
				
			print self.model, "usualmed = ",  self.model['usualmed']
		

	def btn_authority_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btn_authority_button_clicked(self, event) 
			

		print "btn_authority_button_clicked received ", event
			

	def btn_briefPI_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btn_briefPI_button_clicked(self, event) 
			

		print "btn_briefPI_button_clicked received ", event
			

	def text10_text_entered( self, event): 
		if self.impl <> None:
			self.impl.text10_text_entered(self, event) 
			

		print "text10_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['text10']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['text10'] = str(obj.GetValue())
				
			print self.model, "text10 = ",  self.model['text10']
		

class gmSECTION_REQUESTS_handler(base_handler):
	
	def __init__(self, panel, model = None, impl = None):
		base_handler.__init__(self, panel, model, impl)
		

	def set_name_map(self):
		map = {}
		
 
		comp_map = { 'component': self.get_valid_component('btnOK') ,
			'setter': self.get_valid_func( 'btnOK', 'None')  ,
			'comp_name' : 'btnOK','setter_name' :  'None' } 
		map['btnOK'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('btnClear') ,
			'setter': self.get_valid_func( 'btnClear', 'None')  ,
			'comp_name' : 'btnClear','setter_name' :  'None' } 
		map['btnClear'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_request_type') ,
			'setter': self.get_valid_func( 'txt_request_type', 'SetValue')  ,
			'comp_name' : 'txt_request_type','setter_name' :  'SetValue' } 
		map['request_type'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_request_company') ,
			'setter': self.get_valid_func( 'txt_request_company', 'SetValue')  ,
			'comp_name' : 'txt_request_company','setter_name' :  'SetValue' } 
		map['request_company'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_request_street') ,
			'setter': self.get_valid_func( 'txt_request_street', 'SetValue')  ,
			'comp_name' : 'txt_request_street','setter_name' :  'SetValue' } 
		map['request_street'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_request_suburb') ,
			'setter': self.get_valid_func( 'txt_request_suburb', 'SetValue')  ,
			'comp_name' : 'txt_request_suburb','setter_name' :  'SetValue' } 
		map['request_suburb'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_request_phone') ,
			'setter': self.get_valid_func( 'txt_request_phone', 'SetValue')  ,
			'comp_name' : 'txt_request_phone','setter_name' :  'SetValue' } 
		map['request_phone'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_request_requests') ,
			'setter': self.get_valid_func( 'txt_request_requests', 'SetValue')  ,
			'comp_name' : 'txt_request_requests','setter_name' :  'SetValue' } 
		map['request_requests'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_request_notes') ,
			'setter': self.get_valid_func( 'txt_request_notes', 'SetValue')  ,
			'comp_name' : 'txt_request_notes','setter_name' :  'SetValue' } 
		map['request_notes'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_request_medications') ,
			'setter': self.get_valid_func( 'txt_request_medications', 'SetValue')  ,
			'comp_name' : 'txt_request_medications','setter_name' :  'SetValue' } 
		map['request_medications'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_request_copyto') ,
			'setter': self.get_valid_func( 'txt_request_copyto', 'SetValue')  ,
			'comp_name' : 'txt_request_copyto','setter_name' :  'SetValue' } 
		map['request_copyto'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_request_progressnotes') ,
			'setter': self.get_valid_func( 'txt_request_progressnotes', 'SetValue')  ,
			'comp_name' : 'txt_request_progressnotes','setter_name' :  'SetValue' } 
		map['request_progressnotes'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('cb_includeallmedications') ,
			'setter': self.get_valid_func( 'cb_includeallmedications', 'SetValue')  ,
			'comp_name' : 'cb_includeallmedications','setter_name' :  'SetValue' } 
		map['includeallmedications'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('rb_request_bill_bb') ,
			'setter': self.get_valid_func( 'rb_request_bill_bb', 'SetValue')  ,
			'comp_name' : 'rb_request_bill_bb','setter_name' :  'SetValue' } 
		map['request_bill_bb'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('rb_request_bill_private') ,
			'setter': self.get_valid_func( 'rb_request_bill_private', 'SetValue')  ,
			'comp_name' : 'rb_request_bill_private','setter_name' :  'SetValue' } 
		map['request_bill_private'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('rb_request_bill_rebate') ,
			'setter': self.get_valid_func( 'rb_request_bill_rebate', 'SetValue')  ,
			'comp_name' : 'rb_request_bill_rebate','setter_name' :  'SetValue' } 
		map['request_bill_rebate'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('rb_request_bill_wcover') ,
			'setter': self.get_valid_func( 'rb_request_bill_wcover', 'SetValue')  ,
			'comp_name' : 'rb_request_bill_wcover','setter_name' :  'SetValue' } 
		map['request_bill_wcover'] = comp_map
		

		self.name_map = map
	

	def set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('btnOK'):
			self.set_id_common( 'btnOK',self.panel.btnOK)
			

		if self.panel.__dict__.has_key('btnClear'):
			self.set_id_common( 'btnClear',self.panel.btnClear)
			

		if self.panel.__dict__.has_key('txt_request_type'):
			self.set_id_common( 'txt_request_type',self.panel.txt_request_type)
			

		if self.panel.__dict__.has_key('txt_request_company'):
			self.set_id_common( 'txt_request_company',self.panel.txt_request_company)
			

		if self.panel.__dict__.has_key('txt_request_street'):
			self.set_id_common( 'txt_request_street',self.panel.txt_request_street)
			

		if self.panel.__dict__.has_key('txt_request_suburb'):
			self.set_id_common( 'txt_request_suburb',self.panel.txt_request_suburb)
			

		if self.panel.__dict__.has_key('txt_request_phone'):
			self.set_id_common( 'txt_request_phone',self.panel.txt_request_phone)
			

		if self.panel.__dict__.has_key('txt_request_requests'):
			self.set_id_common( 'txt_request_requests',self.panel.txt_request_requests)
			

		if self.panel.__dict__.has_key('txt_request_notes'):
			self.set_id_common( 'txt_request_notes',self.panel.txt_request_notes)
			

		if self.panel.__dict__.has_key('txt_request_medications'):
			self.set_id_common( 'txt_request_medications',self.panel.txt_request_medications)
			

		if self.panel.__dict__.has_key('txt_request_copyto'):
			self.set_id_common( 'txt_request_copyto',self.panel.txt_request_copyto)
			

		if self.panel.__dict__.has_key('txt_request_progressnotes'):
			self.set_id_common( 'txt_request_progressnotes',self.panel.txt_request_progressnotes)
			

		if self.panel.__dict__.has_key('cb_includeallmedications'):
			self.set_id_common( 'cb_includeallmedications',self.panel.cb_includeallmedications)
			

		if self.panel.__dict__.has_key('rb_request_bill_bb'):
			self.set_id_common( 'rb_request_bill_bb',self.panel.rb_request_bill_bb)
			

		if self.panel.__dict__.has_key('rb_request_bill_private'):
			self.set_id_common( 'rb_request_bill_private',self.panel.rb_request_bill_private)
			

		if self.panel.__dict__.has_key('rb_request_bill_rebate'):
			self.set_id_common( 'rb_request_bill_rebate',self.panel.rb_request_bill_rebate)
			

		if self.panel.__dict__.has_key('rb_request_bill_wcover'):
			self.set_id_common( 'rb_request_bill_wcover',self.panel.rb_request_bill_wcover)
			

	def set_evt(self):
		pass
		

		if self.panel.__dict__.has_key('btnOK'):
			EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.btnOK_button_clicked)

		if self.panel.__dict__.has_key('btnClear'):
			EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.btnClear_button_clicked)

		if self.panel.__dict__.has_key('txt_request_type'):
			EVT_TEXT(self.panel.txt_request_type,\
			self.id_map['txt_request_type'],\
			self.txt_request_type_text_entered)

		if self.panel.__dict__.has_key('txt_request_company'):
			EVT_TEXT(self.panel.txt_request_company,\
			self.id_map['txt_request_company'],\
			self.txt_request_company_text_entered)

		if self.panel.__dict__.has_key('txt_request_street'):
			EVT_TEXT(self.panel.txt_request_street,\
			self.id_map['txt_request_street'],\
			self.txt_request_street_text_entered)

		if self.panel.__dict__.has_key('txt_request_suburb'):
			EVT_TEXT(self.panel.txt_request_suburb,\
			self.id_map['txt_request_suburb'],\
			self.txt_request_suburb_text_entered)

		if self.panel.__dict__.has_key('txt_request_phone'):
			EVT_TEXT(self.panel.txt_request_phone,\
			self.id_map['txt_request_phone'],\
			self.txt_request_phone_text_entered)

		if self.panel.__dict__.has_key('txt_request_requests'):
			EVT_TEXT(self.panel.txt_request_requests,\
			self.id_map['txt_request_requests'],\
			self.txt_request_requests_text_entered)

		if self.panel.__dict__.has_key('txt_request_notes'):
			EVT_TEXT(self.panel.txt_request_notes,\
			self.id_map['txt_request_notes'],\
			self.txt_request_notes_text_entered)

		if self.panel.__dict__.has_key('txt_request_medications'):
			EVT_TEXT(self.panel.txt_request_medications,\
			self.id_map['txt_request_medications'],\
			self.txt_request_medications_text_entered)

		if self.panel.__dict__.has_key('txt_request_copyto'):
			EVT_TEXT(self.panel.txt_request_copyto,\
			self.id_map['txt_request_copyto'],\
			self.txt_request_copyto_text_entered)

		if self.panel.__dict__.has_key('txt_request_progressnotes'):
			EVT_TEXT(self.panel.txt_request_progressnotes,\
			self.id_map['txt_request_progressnotes'],\
			self.txt_request_progressnotes_text_entered)

		if self.panel.__dict__.has_key('cb_includeallmedications'):
			EVT_CHECKBOX(self.panel.cb_includeallmedications,\
			self.id_map['cb_includeallmedications'],\
			self.cb_includeallmedications_checkbox_clicked)

		if self.panel.__dict__.has_key('rb_request_bill_bb'):
			EVT_RADIOBUTTON(self.panel.rb_request_bill_bb,\
			self.id_map['rb_request_bill_bb'],\
			self.rb_request_bill_bb_radiobutton_clicked)

		if self.panel.__dict__.has_key('rb_request_bill_private'):
			EVT_RADIOBUTTON(self.panel.rb_request_bill_private,\
			self.id_map['rb_request_bill_private'],\
			self.rb_request_bill_private_radiobutton_clicked)

		if self.panel.__dict__.has_key('rb_request_bill_rebate'):
			EVT_RADIOBUTTON(self.panel.rb_request_bill_rebate,\
			self.id_map['rb_request_bill_rebate'],\
			self.rb_request_bill_rebate_radiobutton_clicked)

		if self.panel.__dict__.has_key('rb_request_bill_wcover'):
			EVT_RADIOBUTTON(self.panel.rb_request_bill_wcover,\
			self.id_map['rb_request_bill_wcover'],\
			self.rb_request_bill_wcover_radiobutton_clicked)

	def btnOK_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btnOK_button_clicked(self, event) 
			

		print "btnOK_button_clicked received ", event
			

	def btnClear_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btnClear_button_clicked(self, event) 
			

		print "btnClear_button_clicked received ", event
			

	def txt_request_type_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_request_type_text_entered(self, event) 
			

		print "txt_request_type_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['request_type']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['request_type'] = str(obj.GetValue())
				
			print self.model, "request_type = ",  self.model['request_type']
		

	def txt_request_company_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_request_company_text_entered(self, event) 
			

		print "txt_request_company_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['request_company']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['request_company'] = str(obj.GetValue())
				
			print self.model, "request_company = ",  self.model['request_company']
		

	def txt_request_street_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_request_street_text_entered(self, event) 
			

		print "txt_request_street_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['request_street']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['request_street'] = str(obj.GetValue())
				
			print self.model, "request_street = ",  self.model['request_street']
		

	def txt_request_suburb_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_request_suburb_text_entered(self, event) 
			

		print "txt_request_suburb_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['request_suburb']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['request_suburb'] = str(obj.GetValue())
				
			print self.model, "request_suburb = ",  self.model['request_suburb']
		

	def txt_request_phone_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_request_phone_text_entered(self, event) 
			

		print "txt_request_phone_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['request_phone']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['request_phone'] = str(obj.GetValue())
				
			print self.model, "request_phone = ",  self.model['request_phone']
		

	def txt_request_requests_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_request_requests_text_entered(self, event) 
			

		print "txt_request_requests_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['request_requests']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['request_requests'] = str(obj.GetValue())
				
			print self.model, "request_requests = ",  self.model['request_requests']
		

	def txt_request_notes_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_request_notes_text_entered(self, event) 
			

		print "txt_request_notes_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['request_notes']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['request_notes'] = str(obj.GetValue())
				
			print self.model, "request_notes = ",  self.model['request_notes']
		

	def txt_request_medications_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_request_medications_text_entered(self, event) 
			

		print "txt_request_medications_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['request_medications']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['request_medications'] = str(obj.GetValue())
				
			print self.model, "request_medications = ",  self.model['request_medications']
		

	def txt_request_copyto_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_request_copyto_text_entered(self, event) 
			

		print "txt_request_copyto_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['request_copyto']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['request_copyto'] = str(obj.GetValue())
				
			print self.model, "request_copyto = ",  self.model['request_copyto']
		

	def txt_request_progressnotes_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_request_progressnotes_text_entered(self, event) 
			

		print "txt_request_progressnotes_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['request_progressnotes']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['request_progressnotes'] = str(obj.GetValue())
				
			print self.model, "request_progressnotes = ",  self.model['request_progressnotes']
		

	def cb_includeallmedications_checkbox_clicked( self, event): 
		if self.impl <> None:
			self.impl.cb_includeallmedications_checkbox_clicked(self, event) 
			

		print "cb_includeallmedications_checkbox_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['includeallmedications']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['includeallmedications'] = str(obj.GetValue())
				
			print self.model, "includeallmedications = ",  self.model['includeallmedications']
		

	def rb_request_bill_bb_radiobutton_clicked( self, event): 
		if self.impl <> None:
			self.impl.rb_request_bill_bb_radiobutton_clicked(self, event) 
			

		print "rb_request_bill_bb_radiobutton_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['request_bill_bb']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['request_bill_bb'] = str(obj.GetValue())
				
			print self.model, "request_bill_bb = ",  self.model['request_bill_bb']
		

	def rb_request_bill_private_radiobutton_clicked( self, event): 
		if self.impl <> None:
			self.impl.rb_request_bill_private_radiobutton_clicked(self, event) 
			

		print "rb_request_bill_private_radiobutton_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['request_bill_private']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['request_bill_private'] = str(obj.GetValue())
				
			print self.model, "request_bill_private = ",  self.model['request_bill_private']
		

	def rb_request_bill_rebate_radiobutton_clicked( self, event): 
		if self.impl <> None:
			self.impl.rb_request_bill_rebate_radiobutton_clicked(self, event) 
			

		print "rb_request_bill_rebate_radiobutton_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['request_bill_rebate']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['request_bill_rebate'] = str(obj.GetValue())
				
			print self.model, "request_bill_rebate = ",  self.model['request_bill_rebate']
		

	def rb_request_bill_wcover_radiobutton_clicked( self, event): 
		if self.impl <> None:
			self.impl.rb_request_bill_wcover_radiobutton_clicked(self, event) 
			

		print "rb_request_bill_wcover_radiobutton_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['request_bill_wcover']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['request_bill_wcover'] = str(obj.GetValue())
				
			print self.model, "request_bill_wcover = ",  self.model['request_bill_wcover']
		

class gmSECTION_MEASUREMENTS_handler(base_handler):
	
	def __init__(self, panel, model = None, impl = None):
		base_handler.__init__(self, panel, model, impl)
		

	def set_name_map(self):
		map = {}
		
 
		comp_map = { 'component': self.get_valid_component('btnOK') ,
			'setter': self.get_valid_func( 'btnOK', 'None')  ,
			'comp_name' : 'btnOK','setter_name' :  'None' } 
		map['btnOK'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('btnClear') ,
			'setter': self.get_valid_func( 'btnClear', 'None')  ,
			'comp_name' : 'btnClear','setter_name' :  'None' } 
		map['btnClear'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('combo_measurement_type') ,
			'setter': self.get_valid_func( 'combo_measurement_type', 'SetValue')  ,
			'comp_name' : 'combo_measurement_type','setter_name' :  'SetValue' } 
		map['measurement_type'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_measurement_value') ,
			'setter': self.get_valid_func( 'txt_measurement_value', 'SetValue')  ,
			'comp_name' : 'txt_measurement_value','setter_name' :  'SetValue' } 
		map['measurement_value'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_txt_measurement_date') ,
			'setter': self.get_valid_func( 'txt_txt_measurement_date', 'SetValue')  ,
			'comp_name' : 'txt_txt_measurement_date','setter_name' :  'SetValue' } 
		map['txt_measurement_date'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_txt_measurement_comment') ,
			'setter': self.get_valid_func( 'txt_txt_measurement_comment', 'SetValue')  ,
			'comp_name' : 'txt_txt_measurement_comment','setter_name' :  'SetValue' } 
		map['txt_measurement_comment'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_txt_measurement_progressnote') ,
			'setter': self.get_valid_func( 'txt_txt_measurement_progressnote', 'SetValue')  ,
			'comp_name' : 'txt_txt_measurement_progressnote','setter_name' :  'SetValue' } 
		map['txt_measurement_progressnote'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('btn_nextvalue') ,
			'setter': self.get_valid_func( 'btn_nextvalue', 'None')  ,
			'comp_name' : 'btn_nextvalue','setter_name' :  'None' } 
		map['nextvalue'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('btn_graph') ,
			'setter': self.get_valid_func( 'btn_graph', 'None')  ,
			'comp_name' : 'btn_graph','setter_name' :  'None' } 
		map['graph'] = comp_map
		

		self.name_map = map
	

	def set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('btnOK'):
			self.set_id_common( 'btnOK',self.panel.btnOK)
			

		if self.panel.__dict__.has_key('btnClear'):
			self.set_id_common( 'btnClear',self.panel.btnClear)
			

		if self.panel.__dict__.has_key('combo_measurement_type'):
			self.set_id_common( 'combo_measurement_type',self.panel.combo_measurement_type)
			

		if self.panel.__dict__.has_key('txt_measurement_value'):
			self.set_id_common( 'txt_measurement_value',self.panel.txt_measurement_value)
			

		if self.panel.__dict__.has_key('txt_txt_measurement_date'):
			self.set_id_common( 'txt_txt_measurement_date',self.panel.txt_txt_measurement_date)
			

		if self.panel.__dict__.has_key('txt_txt_measurement_comment'):
			self.set_id_common( 'txt_txt_measurement_comment',self.panel.txt_txt_measurement_comment)
			

		if self.panel.__dict__.has_key('txt_txt_measurement_progressnote'):
			self.set_id_common( 'txt_txt_measurement_progressnote',self.panel.txt_txt_measurement_progressnote)
			

		if self.panel.__dict__.has_key('btn_nextvalue'):
			self.set_id_common( 'btn_nextvalue',self.panel.btn_nextvalue)
			

		if self.panel.__dict__.has_key('btn_graph'):
			self.set_id_common( 'btn_graph',self.panel.btn_graph)
			

	def set_evt(self):
		pass
		

		if self.panel.__dict__.has_key('btnOK'):
			EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.btnOK_button_clicked)

		if self.panel.__dict__.has_key('btnClear'):
			EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.btnClear_button_clicked)

		if self.panel.__dict__.has_key('combo_measurement_type'):
			EVT_TEXT(self.panel.combo_measurement_type,\
			self.id_map['combo_measurement_type'],\
			self.combo_measurement_type_text_entered)

		if self.panel.__dict__.has_key('txt_measurement_value'):
			EVT_TEXT(self.panel.txt_measurement_value,\
			self.id_map['txt_measurement_value'],\
			self.txt_measurement_value_text_entered)

		if self.panel.__dict__.has_key('txt_txt_measurement_date'):
			EVT_TEXT(self.panel.txt_txt_measurement_date,\
			self.id_map['txt_txt_measurement_date'],\
			self.txt_txt_measurement_date_text_entered)

		if self.panel.__dict__.has_key('txt_txt_measurement_comment'):
			EVT_TEXT(self.panel.txt_txt_measurement_comment,\
			self.id_map['txt_txt_measurement_comment'],\
			self.txt_txt_measurement_comment_text_entered)

		if self.panel.__dict__.has_key('txt_txt_measurement_progressnote'):
			EVT_TEXT(self.panel.txt_txt_measurement_progressnote,\
			self.id_map['txt_txt_measurement_progressnote'],\
			self.txt_txt_measurement_progressnote_text_entered)

		if self.panel.__dict__.has_key('btn_nextvalue'):
			EVT_BUTTON(self.panel.btn_nextvalue,\
			self.id_map['btn_nextvalue'],\
			self.btn_nextvalue_button_clicked)

		if self.panel.__dict__.has_key('btn_graph'):
			EVT_BUTTON(self.panel.btn_graph,\
			self.id_map['btn_graph'],\
			self.btn_graph_button_clicked)

	def btnOK_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btnOK_button_clicked(self, event) 
			

		print "btnOK_button_clicked received ", event
			

	def btnClear_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btnClear_button_clicked(self, event) 
			

		print "btnClear_button_clicked received ", event
			

	def combo_measurement_type_text_entered( self, event): 
		if self.impl <> None:
			self.impl.combo_measurement_type_text_entered(self, event) 
			

		print "combo_measurement_type_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['measurement_type']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['measurement_type'] = str(obj.GetValue())
				
			print self.model, "measurement_type = ",  self.model['measurement_type']
		

	def txt_measurement_value_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_measurement_value_text_entered(self, event) 
			

		print "txt_measurement_value_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['measurement_value']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['measurement_value'] = str(obj.GetValue())
				
			print self.model, "measurement_value = ",  self.model['measurement_value']
		

	def txt_txt_measurement_date_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_txt_measurement_date_text_entered(self, event) 
			

		print "txt_txt_measurement_date_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['txt_measurement_date']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['txt_measurement_date'] = str(obj.GetValue())
				
			print self.model, "txt_measurement_date = ",  self.model['txt_measurement_date']
		

	def txt_txt_measurement_comment_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_txt_measurement_comment_text_entered(self, event) 
			

		print "txt_txt_measurement_comment_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['txt_measurement_comment']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['txt_measurement_comment'] = str(obj.GetValue())
				
			print self.model, "txt_measurement_comment = ",  self.model['txt_measurement_comment']
		

	def txt_txt_measurement_progressnote_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_txt_measurement_progressnote_text_entered(self, event) 
			

		print "txt_txt_measurement_progressnote_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['txt_measurement_progressnote']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['txt_measurement_progressnote'] = str(obj.GetValue())
				
			print self.model, "txt_measurement_progressnote = ",  self.model['txt_measurement_progressnote']
		

	def btn_nextvalue_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btn_nextvalue_button_clicked(self, event) 
			

		print "btn_nextvalue_button_clicked received ", event
			

	def btn_graph_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btn_graph_button_clicked(self, event) 
			

		print "btn_graph_button_clicked received ", event
			

class gmSECTION_REFERRALS_handler(base_handler):
	
	def __init__(self, panel, model = None, impl = None):
		base_handler.__init__(self, panel, model, impl)
		

	def set_name_map(self):
		map = {}
		
 
		comp_map = { 'component': self.get_valid_component('btnOK') ,
			'setter': self.get_valid_func( 'btnOK', 'None')  ,
			'comp_name' : 'btnOK','setter_name' :  'None' } 
		map['btnOK'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('btnClear') ,
			'setter': self.get_valid_func( 'btnClear', 'None')  ,
			'comp_name' : 'btnClear','setter_name' :  'None' } 
		map['btnClear'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('btnpreview') ,
			'setter': self.get_valid_func( 'btnpreview', 'None')  ,
			'comp_name' : 'btnpreview','setter_name' :  'None' } 
		map['btnpreview'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_referralcategory') ,
			'setter': self.get_valid_func( 'txt_referralcategory', 'SetValue')  ,
			'comp_name' : 'txt_referralcategory','setter_name' :  'SetValue' } 
		map['referralcategory'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_referralname') ,
			'setter': self.get_valid_func( 'txt_referralname', 'SetValue')  ,
			'comp_name' : 'txt_referralname','setter_name' :  'SetValue' } 
		map['referralname'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_referralorganisation') ,
			'setter': self.get_valid_func( 'txt_referralorganisation', 'SetValue')  ,
			'comp_name' : 'txt_referralorganisation','setter_name' :  'SetValue' } 
		map['referralorganisation'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_referralstreet1') ,
			'setter': self.get_valid_func( 'txt_referralstreet1', 'SetValue')  ,
			'comp_name' : 'txt_referralstreet1','setter_name' :  'SetValue' } 
		map['referralstreet1'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_referralstreet2') ,
			'setter': self.get_valid_func( 'txt_referralstreet2', 'SetValue')  ,
			'comp_name' : 'txt_referralstreet2','setter_name' :  'SetValue' } 
		map['referralstreet2'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_referralstreet3') ,
			'setter': self.get_valid_func( 'txt_referralstreet3', 'SetValue')  ,
			'comp_name' : 'txt_referralstreet3','setter_name' :  'SetValue' } 
		map['referralstreet3'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_referralsuburb') ,
			'setter': self.get_valid_func( 'txt_referralsuburb', 'SetValue')  ,
			'comp_name' : 'txt_referralsuburb','setter_name' :  'SetValue' } 
		map['referralsuburb'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_referralpostcode') ,
			'setter': self.get_valid_func( 'txt_referralpostcode', 'SetValue')  ,
			'comp_name' : 'txt_referralpostcode','setter_name' :  'SetValue' } 
		map['referralpostcode'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_referralfor') ,
			'setter': self.get_valid_func( 'txt_referralfor', 'SetValue')  ,
			'comp_name' : 'txt_referralfor','setter_name' :  'SetValue' } 
		map['referralfor'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_referralwphone') ,
			'setter': self.get_valid_func( 'txt_referralwphone', 'SetValue')  ,
			'comp_name' : 'txt_referralwphone','setter_name' :  'SetValue' } 
		map['referralwphone'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_referralwfax') ,
			'setter': self.get_valid_func( 'txt_referralwfax', 'SetValue')  ,
			'comp_name' : 'txt_referralwfax','setter_name' :  'SetValue' } 
		map['referralwfax'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_referralwemail') ,
			'setter': self.get_valid_func( 'txt_referralwemail', 'SetValue')  ,
			'comp_name' : 'txt_referralwemail','setter_name' :  'SetValue' } 
		map['referralwemail'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_referralcopyto') ,
			'setter': self.get_valid_func( 'txt_referralcopyto', 'SetValue')  ,
			'comp_name' : 'txt_referralcopyto','setter_name' :  'SetValue' } 
		map['referralcopyto'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_referralprogressnotes') ,
			'setter': self.get_valid_func( 'txt_referralprogressnotes', 'SetValue')  ,
			'comp_name' : 'txt_referralprogressnotes','setter_name' :  'SetValue' } 
		map['referralprogressnotes'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('chkbox_referral_usefirstname') ,
			'setter': self.get_valid_func( 'chkbox_referral_usefirstname', 'SetValue')  ,
			'comp_name' : 'chkbox_referral_usefirstname','setter_name' :  'SetValue' } 
		map['referral_usefirstname'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('chkbox_referral_headoffice') ,
			'setter': self.get_valid_func( 'chkbox_referral_headoffice', 'SetValue')  ,
			'comp_name' : 'chkbox_referral_headoffice','setter_name' :  'SetValue' } 
		map['referral_headoffice'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('chkbox_referral_medications') ,
			'setter': self.get_valid_func( 'chkbox_referral_medications', 'SetValue')  ,
			'comp_name' : 'chkbox_referral_medications','setter_name' :  'SetValue' } 
		map['referral_medications'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('chkbox_referral_socialhistory') ,
			'setter': self.get_valid_func( 'chkbox_referral_socialhistory', 'SetValue')  ,
			'comp_name' : 'chkbox_referral_socialhistory','setter_name' :  'SetValue' } 
		map['referral_socialhistory'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('chkbox_referral_familyhistory') ,
			'setter': self.get_valid_func( 'chkbox_referral_familyhistory', 'SetValue')  ,
			'comp_name' : 'chkbox_referral_familyhistory','setter_name' :  'SetValue' } 
		map['referral_familyhistory'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('chkbox_referral_pastproblems') ,
			'setter': self.get_valid_func( 'chkbox_referral_pastproblems', 'SetValue')  ,
			'comp_name' : 'chkbox_referral_pastproblems','setter_name' :  'SetValue' } 
		map['referral_pastproblems'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('chkbox_referral_activeproblems') ,
			'setter': self.get_valid_func( 'chkbox_referral_activeproblems', 'SetValue')  ,
			'comp_name' : 'chkbox_referral_activeproblems','setter_name' :  'SetValue' } 
		map['referral_activeproblems'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('chkbox_referral_habits') ,
			'setter': self.get_valid_func( 'chkbox_referral_habits', 'SetValue')  ,
			'comp_name' : 'chkbox_referral_habits','setter_name' :  'SetValue' } 
		map['referral_habits'] = comp_map
		

		self.name_map = map
	

	def set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('btnOK'):
			self.set_id_common( 'btnOK',self.panel.btnOK)
			

		if self.panel.__dict__.has_key('btnClear'):
			self.set_id_common( 'btnClear',self.panel.btnClear)
			

		if self.panel.__dict__.has_key('btnpreview'):
			self.set_id_common( 'btnpreview',self.panel.btnpreview)
			

		if self.panel.__dict__.has_key('txt_referralcategory'):
			self.set_id_common( 'txt_referralcategory',self.panel.txt_referralcategory)
			

		if self.panel.__dict__.has_key('txt_referralname'):
			self.set_id_common( 'txt_referralname',self.panel.txt_referralname)
			

		if self.panel.__dict__.has_key('txt_referralorganisation'):
			self.set_id_common( 'txt_referralorganisation',self.panel.txt_referralorganisation)
			

		if self.panel.__dict__.has_key('txt_referralstreet1'):
			self.set_id_common( 'txt_referralstreet1',self.panel.txt_referralstreet1)
			

		if self.panel.__dict__.has_key('txt_referralstreet2'):
			self.set_id_common( 'txt_referralstreet2',self.panel.txt_referralstreet2)
			

		if self.panel.__dict__.has_key('txt_referralstreet3'):
			self.set_id_common( 'txt_referralstreet3',self.panel.txt_referralstreet3)
			

		if self.panel.__dict__.has_key('txt_referralsuburb'):
			self.set_id_common( 'txt_referralsuburb',self.panel.txt_referralsuburb)
			

		if self.panel.__dict__.has_key('txt_referralpostcode'):
			self.set_id_common( 'txt_referralpostcode',self.panel.txt_referralpostcode)
			

		if self.panel.__dict__.has_key('txt_referralfor'):
			self.set_id_common( 'txt_referralfor',self.panel.txt_referralfor)
			

		if self.panel.__dict__.has_key('txt_referralwphone'):
			self.set_id_common( 'txt_referralwphone',self.panel.txt_referralwphone)
			

		if self.panel.__dict__.has_key('txt_referralwfax'):
			self.set_id_common( 'txt_referralwfax',self.panel.txt_referralwfax)
			

		if self.panel.__dict__.has_key('txt_referralwemail'):
			self.set_id_common( 'txt_referralwemail',self.panel.txt_referralwemail)
			

		if self.panel.__dict__.has_key('txt_referralcopyto'):
			self.set_id_common( 'txt_referralcopyto',self.panel.txt_referralcopyto)
			

		if self.panel.__dict__.has_key('txt_referralprogressnotes'):
			self.set_id_common( 'txt_referralprogressnotes',self.panel.txt_referralprogressnotes)
			

		if self.panel.__dict__.has_key('chkbox_referral_usefirstname'):
			self.set_id_common( 'chkbox_referral_usefirstname',self.panel.chkbox_referral_usefirstname)
			

		if self.panel.__dict__.has_key('chkbox_referral_headoffice'):
			self.set_id_common( 'chkbox_referral_headoffice',self.panel.chkbox_referral_headoffice)
			

		if self.panel.__dict__.has_key('chkbox_referral_medications'):
			self.set_id_common( 'chkbox_referral_medications',self.panel.chkbox_referral_medications)
			

		if self.panel.__dict__.has_key('chkbox_referral_socialhistory'):
			self.set_id_common( 'chkbox_referral_socialhistory',self.panel.chkbox_referral_socialhistory)
			

		if self.panel.__dict__.has_key('chkbox_referral_familyhistory'):
			self.set_id_common( 'chkbox_referral_familyhistory',self.panel.chkbox_referral_familyhistory)
			

		if self.panel.__dict__.has_key('chkbox_referral_pastproblems'):
			self.set_id_common( 'chkbox_referral_pastproblems',self.panel.chkbox_referral_pastproblems)
			

		if self.panel.__dict__.has_key('chkbox_referral_activeproblems'):
			self.set_id_common( 'chkbox_referral_activeproblems',self.panel.chkbox_referral_activeproblems)
			

		if self.panel.__dict__.has_key('chkbox_referral_habits'):
			self.set_id_common( 'chkbox_referral_habits',self.panel.chkbox_referral_habits)
			

	def set_evt(self):
		pass
		

		if self.panel.__dict__.has_key('btnOK'):
			EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.btnOK_button_clicked)

		if self.panel.__dict__.has_key('btnClear'):
			EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.btnClear_button_clicked)

		if self.panel.__dict__.has_key('btnpreview'):
			EVT_BUTTON(self.panel.btnpreview,\
			self.id_map['btnpreview'],\
			self.btnpreview_button_clicked)

		if self.panel.__dict__.has_key('txt_referralcategory'):
			EVT_TEXT(self.panel.txt_referralcategory,\
			self.id_map['txt_referralcategory'],\
			self.txt_referralcategory_text_entered)

		if self.panel.__dict__.has_key('txt_referralname'):
			EVT_TEXT(self.panel.txt_referralname,\
			self.id_map['txt_referralname'],\
			self.txt_referralname_text_entered)

		if self.panel.__dict__.has_key('txt_referralorganisation'):
			EVT_TEXT(self.panel.txt_referralorganisation,\
			self.id_map['txt_referralorganisation'],\
			self.txt_referralorganisation_text_entered)

		if self.panel.__dict__.has_key('txt_referralstreet1'):
			EVT_TEXT(self.panel.txt_referralstreet1,\
			self.id_map['txt_referralstreet1'],\
			self.txt_referralstreet1_text_entered)

		if self.panel.__dict__.has_key('txt_referralstreet2'):
			EVT_TEXT(self.panel.txt_referralstreet2,\
			self.id_map['txt_referralstreet2'],\
			self.txt_referralstreet2_text_entered)

		if self.panel.__dict__.has_key('txt_referralstreet3'):
			EVT_TEXT(self.panel.txt_referralstreet3,\
			self.id_map['txt_referralstreet3'],\
			self.txt_referralstreet3_text_entered)

		if self.panel.__dict__.has_key('txt_referralsuburb'):
			EVT_TEXT(self.panel.txt_referralsuburb,\
			self.id_map['txt_referralsuburb'],\
			self.txt_referralsuburb_text_entered)

		if self.panel.__dict__.has_key('txt_referralpostcode'):
			EVT_TEXT(self.panel.txt_referralpostcode,\
			self.id_map['txt_referralpostcode'],\
			self.txt_referralpostcode_text_entered)

		if self.panel.__dict__.has_key('txt_referralfor'):
			EVT_TEXT(self.panel.txt_referralfor,\
			self.id_map['txt_referralfor'],\
			self.txt_referralfor_text_entered)

		if self.panel.__dict__.has_key('txt_referralwphone'):
			EVT_TEXT(self.panel.txt_referralwphone,\
			self.id_map['txt_referralwphone'],\
			self.txt_referralwphone_text_entered)

		if self.panel.__dict__.has_key('txt_referralwfax'):
			EVT_TEXT(self.panel.txt_referralwfax,\
			self.id_map['txt_referralwfax'],\
			self.txt_referralwfax_text_entered)

		if self.panel.__dict__.has_key('txt_referralwemail'):
			EVT_TEXT(self.panel.txt_referralwemail,\
			self.id_map['txt_referralwemail'],\
			self.txt_referralwemail_text_entered)

		if self.panel.__dict__.has_key('txt_referralcopyto'):
			EVT_TEXT(self.panel.txt_referralcopyto,\
			self.id_map['txt_referralcopyto'],\
			self.txt_referralcopyto_text_entered)

		if self.panel.__dict__.has_key('txt_referralprogressnotes'):
			EVT_TEXT(self.panel.txt_referralprogressnotes,\
			self.id_map['txt_referralprogressnotes'],\
			self.txt_referralprogressnotes_text_entered)

		if self.panel.__dict__.has_key('chkbox_referral_usefirstname'):
			EVT_CHECKBOX(self.panel.chkbox_referral_usefirstname,\
			self.id_map['chkbox_referral_usefirstname'],\
			self.chkbox_referral_usefirstname_checkbox_clicked)

		if self.panel.__dict__.has_key('chkbox_referral_headoffice'):
			EVT_CHECKBOX(self.panel.chkbox_referral_headoffice,\
			self.id_map['chkbox_referral_headoffice'],\
			self.chkbox_referral_headoffice_checkbox_clicked)

		if self.panel.__dict__.has_key('chkbox_referral_medications'):
			EVT_CHECKBOX(self.panel.chkbox_referral_medications,\
			self.id_map['chkbox_referral_medications'],\
			self.chkbox_referral_medications_checkbox_clicked)

		if self.panel.__dict__.has_key('chkbox_referral_socialhistory'):
			EVT_CHECKBOX(self.panel.chkbox_referral_socialhistory,\
			self.id_map['chkbox_referral_socialhistory'],\
			self.chkbox_referral_socialhistory_checkbox_clicked)

		if self.panel.__dict__.has_key('chkbox_referral_familyhistory'):
			EVT_CHECKBOX(self.panel.chkbox_referral_familyhistory,\
			self.id_map['chkbox_referral_familyhistory'],\
			self.chkbox_referral_familyhistory_checkbox_clicked)

		if self.panel.__dict__.has_key('chkbox_referral_pastproblems'):
			EVT_CHECKBOX(self.panel.chkbox_referral_pastproblems,\
			self.id_map['chkbox_referral_pastproblems'],\
			self.chkbox_referral_pastproblems_checkbox_clicked)

		if self.panel.__dict__.has_key('chkbox_referral_activeproblems'):
			EVT_CHECKBOX(self.panel.chkbox_referral_activeproblems,\
			self.id_map['chkbox_referral_activeproblems'],\
			self.chkbox_referral_activeproblems_checkbox_clicked)

		if self.panel.__dict__.has_key('chkbox_referral_habits'):
			EVT_CHECKBOX(self.panel.chkbox_referral_habits,\
			self.id_map['chkbox_referral_habits'],\
			self.chkbox_referral_habits_checkbox_clicked)

	def btnOK_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btnOK_button_clicked(self, event) 
			

		print "btnOK_button_clicked received ", event
			

	def btnClear_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btnClear_button_clicked(self, event) 
			

		print "btnClear_button_clicked received ", event
			

	def btnpreview_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btnpreview_button_clicked(self, event) 
			

		print "btnpreview_button_clicked received ", event
			

	def txt_referralcategory_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_referralcategory_text_entered(self, event) 
			

		print "txt_referralcategory_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['referralcategory']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['referralcategory'] = str(obj.GetValue())
				
			print self.model, "referralcategory = ",  self.model['referralcategory']
		

	def txt_referralname_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_referralname_text_entered(self, event) 
			

		print "txt_referralname_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['referralname']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['referralname'] = str(obj.GetValue())
				
			print self.model, "referralname = ",  self.model['referralname']
		

	def txt_referralorganisation_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_referralorganisation_text_entered(self, event) 
			

		print "txt_referralorganisation_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['referralorganisation']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['referralorganisation'] = str(obj.GetValue())
				
			print self.model, "referralorganisation = ",  self.model['referralorganisation']
		

	def txt_referralstreet1_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_referralstreet1_text_entered(self, event) 
			

		print "txt_referralstreet1_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['referralstreet1']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['referralstreet1'] = str(obj.GetValue())
				
			print self.model, "referralstreet1 = ",  self.model['referralstreet1']
		

	def txt_referralstreet2_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_referralstreet2_text_entered(self, event) 
			

		print "txt_referralstreet2_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['referralstreet2']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['referralstreet2'] = str(obj.GetValue())
				
			print self.model, "referralstreet2 = ",  self.model['referralstreet2']
		

	def txt_referralstreet3_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_referralstreet3_text_entered(self, event) 
			

		print "txt_referralstreet3_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['referralstreet3']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['referralstreet3'] = str(obj.GetValue())
				
			print self.model, "referralstreet3 = ",  self.model['referralstreet3']
		

	def txt_referralsuburb_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_referralsuburb_text_entered(self, event) 
			

		print "txt_referralsuburb_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['referralsuburb']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['referralsuburb'] = str(obj.GetValue())
				
			print self.model, "referralsuburb = ",  self.model['referralsuburb']
		

	def txt_referralpostcode_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_referralpostcode_text_entered(self, event) 
			

		print "txt_referralpostcode_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['referralpostcode']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['referralpostcode'] = str(obj.GetValue())
				
			print self.model, "referralpostcode = ",  self.model['referralpostcode']
		

	def txt_referralfor_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_referralfor_text_entered(self, event) 
			

		print "txt_referralfor_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['referralfor']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['referralfor'] = str(obj.GetValue())
				
			print self.model, "referralfor = ",  self.model['referralfor']
		

	def txt_referralwphone_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_referralwphone_text_entered(self, event) 
			

		print "txt_referralwphone_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['referralwphone']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['referralwphone'] = str(obj.GetValue())
				
			print self.model, "referralwphone = ",  self.model['referralwphone']
		

	def txt_referralwfax_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_referralwfax_text_entered(self, event) 
			

		print "txt_referralwfax_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['referralwfax']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['referralwfax'] = str(obj.GetValue())
				
			print self.model, "referralwfax = ",  self.model['referralwfax']
		

	def txt_referralwemail_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_referralwemail_text_entered(self, event) 
			

		print "txt_referralwemail_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['referralwemail']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['referralwemail'] = str(obj.GetValue())
				
			print self.model, "referralwemail = ",  self.model['referralwemail']
		

	def txt_referralcopyto_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_referralcopyto_text_entered(self, event) 
			

		print "txt_referralcopyto_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['referralcopyto']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['referralcopyto'] = str(obj.GetValue())
				
			print self.model, "referralcopyto = ",  self.model['referralcopyto']
		

	def txt_referralprogressnotes_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_referralprogressnotes_text_entered(self, event) 
			

		print "txt_referralprogressnotes_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['referralprogressnotes']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['referralprogressnotes'] = str(obj.GetValue())
				
			print self.model, "referralprogressnotes = ",  self.model['referralprogressnotes']
		

	def chkbox_referral_usefirstname_checkbox_clicked( self, event): 
		if self.impl <> None:
			self.impl.chkbox_referral_usefirstname_checkbox_clicked(self, event) 
			

		print "chkbox_referral_usefirstname_checkbox_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['referral_usefirstname']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['referral_usefirstname'] = str(obj.GetValue())
				
			print self.model, "referral_usefirstname = ",  self.model['referral_usefirstname']
		

	def chkbox_referral_headoffice_checkbox_clicked( self, event): 
		if self.impl <> None:
			self.impl.chkbox_referral_headoffice_checkbox_clicked(self, event) 
			

		print "chkbox_referral_headoffice_checkbox_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['referral_headoffice']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['referral_headoffice'] = str(obj.GetValue())
				
			print self.model, "referral_headoffice = ",  self.model['referral_headoffice']
		

	def chkbox_referral_medications_checkbox_clicked( self, event): 
		if self.impl <> None:
			self.impl.chkbox_referral_medications_checkbox_clicked(self, event) 
			

		print "chkbox_referral_medications_checkbox_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['referral_medications']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['referral_medications'] = str(obj.GetValue())
				
			print self.model, "referral_medications = ",  self.model['referral_medications']
		

	def chkbox_referral_socialhistory_checkbox_clicked( self, event): 
		if self.impl <> None:
			self.impl.chkbox_referral_socialhistory_checkbox_clicked(self, event) 
			

		print "chkbox_referral_socialhistory_checkbox_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['referral_socialhistory']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['referral_socialhistory'] = str(obj.GetValue())
				
			print self.model, "referral_socialhistory = ",  self.model['referral_socialhistory']
		

	def chkbox_referral_familyhistory_checkbox_clicked( self, event): 
		if self.impl <> None:
			self.impl.chkbox_referral_familyhistory_checkbox_clicked(self, event) 
			

		print "chkbox_referral_familyhistory_checkbox_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['referral_familyhistory']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['referral_familyhistory'] = str(obj.GetValue())
				
			print self.model, "referral_familyhistory = ",  self.model['referral_familyhistory']
		

	def chkbox_referral_pastproblems_checkbox_clicked( self, event): 
		if self.impl <> None:
			self.impl.chkbox_referral_pastproblems_checkbox_clicked(self, event) 
			

		print "chkbox_referral_pastproblems_checkbox_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['referral_pastproblems']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['referral_pastproblems'] = str(obj.GetValue())
				
			print self.model, "referral_pastproblems = ",  self.model['referral_pastproblems']
		

	def chkbox_referral_activeproblems_checkbox_clicked( self, event): 
		if self.impl <> None:
			self.impl.chkbox_referral_activeproblems_checkbox_clicked(self, event) 
			

		print "chkbox_referral_activeproblems_checkbox_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['referral_activeproblems']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['referral_activeproblems'] = str(obj.GetValue())
				
			print self.model, "referral_activeproblems = ",  self.model['referral_activeproblems']
		

	def chkbox_referral_habits_checkbox_clicked( self, event): 
		if self.impl <> None:
			self.impl.chkbox_referral_habits_checkbox_clicked(self, event) 
			

		print "chkbox_referral_habits_checkbox_clicked received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['referral_habits']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['referral_habits'] = str(obj.GetValue())
				
			print self.model, "referral_habits = ",  self.model['referral_habits']
		

class gmSECTION_RECALLS_handler(base_handler):
	
	def __init__(self, panel, model = None, impl = None):
		base_handler.__init__(self, panel, model, impl)
		

	def set_name_map(self):
		map = {}
		
 
		comp_map = { 'component': self.get_valid_component('btnOK') ,
			'setter': self.get_valid_func( 'btnOK', 'None')  ,
			'comp_name' : 'btnOK','setter_name' :  'None' } 
		map['btnOK'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('btnClear') ,
			'setter': self.get_valid_func( 'btnClear', 'None')  ,
			'comp_name' : 'btnClear','setter_name' :  'None' } 
		map['btnClear'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('combo_tosee') ,
			'setter': self.get_valid_func( 'combo_tosee', 'SetValue')  ,
			'comp_name' : 'combo_tosee','setter_name' :  'SetValue' } 
		map['tosee'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('combo_recall_method') ,
			'setter': self.get_valid_func( 'combo_recall_method', 'SetValue')  ,
			'comp_name' : 'combo_recall_method','setter_name' :  'SetValue' } 
		map['recall_method'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('combo_apptlength') ,
			'setter': self.get_valid_func( 'combo_apptlength', 'SetValue')  ,
			'comp_name' : 'combo_apptlength','setter_name' :  'SetValue' } 
		map['apptlength'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_recall_for') ,
			'setter': self.get_valid_func( 'txt_recall_for', 'SetValue')  ,
			'comp_name' : 'txt_recall_for','setter_name' :  'SetValue' } 
		map['recall_for'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_recall_due') ,
			'setter': self.get_valid_func( 'txt_recall_due', 'SetValue')  ,
			'comp_name' : 'txt_recall_due','setter_name' :  'SetValue' } 
		map['recall_due'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_recall_addtext') ,
			'setter': self.get_valid_func( 'txt_recall_addtext', 'SetValue')  ,
			'comp_name' : 'txt_recall_addtext','setter_name' :  'SetValue' } 
		map['recall_addtext'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_recall_include') ,
			'setter': self.get_valid_func( 'txt_recall_include', 'SetValue')  ,
			'comp_name' : 'txt_recall_include','setter_name' :  'SetValue' } 
		map['recall_include'] = comp_map
		
 
		comp_map = { 'component': self.get_valid_component('txt_recall_progressnotes') ,
			'setter': self.get_valid_func( 'txt_recall_progressnotes', 'SetValue')  ,
			'comp_name' : 'txt_recall_progressnotes','setter_name' :  'SetValue' } 
		map['recall_progressnotes'] = comp_map
		

		self.name_map = map
	

	def set_id(self):
		self.id_map = {}


		if self.panel.__dict__.has_key('btnOK'):
			self.set_id_common( 'btnOK',self.panel.btnOK)
			

		if self.panel.__dict__.has_key('btnClear'):
			self.set_id_common( 'btnClear',self.panel.btnClear)
			

		if self.panel.__dict__.has_key('combo_tosee'):
			self.set_id_common( 'combo_tosee',self.panel.combo_tosee)
			

		if self.panel.__dict__.has_key('combo_recall_method'):
			self.set_id_common( 'combo_recall_method',self.panel.combo_recall_method)
			

		if self.panel.__dict__.has_key('combo_apptlength'):
			self.set_id_common( 'combo_apptlength',self.panel.combo_apptlength)
			

		if self.panel.__dict__.has_key('txt_recall_for'):
			self.set_id_common( 'txt_recall_for',self.panel.txt_recall_for)
			

		if self.panel.__dict__.has_key('txt_recall_due'):
			self.set_id_common( 'txt_recall_due',self.panel.txt_recall_due)
			

		if self.panel.__dict__.has_key('txt_recall_addtext'):
			self.set_id_common( 'txt_recall_addtext',self.panel.txt_recall_addtext)
			

		if self.panel.__dict__.has_key('txt_recall_include'):
			self.set_id_common( 'txt_recall_include',self.panel.txt_recall_include)
			

		if self.panel.__dict__.has_key('txt_recall_progressnotes'):
			self.set_id_common( 'txt_recall_progressnotes',self.panel.txt_recall_progressnotes)
			

	def set_evt(self):
		pass
		

		if self.panel.__dict__.has_key('btnOK'):
			EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.btnOK_button_clicked)

		if self.panel.__dict__.has_key('btnClear'):
			EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.btnClear_button_clicked)

		if self.panel.__dict__.has_key('combo_tosee'):
			EVT_TEXT(self.panel.combo_tosee,\
			self.id_map['combo_tosee'],\
			self.combo_tosee_text_entered)

		if self.panel.__dict__.has_key('combo_recall_method'):
			EVT_TEXT(self.panel.combo_recall_method,\
			self.id_map['combo_recall_method'],\
			self.combo_recall_method_text_entered)

		if self.panel.__dict__.has_key('combo_apptlength'):
			EVT_TEXT(self.panel.combo_apptlength,\
			self.id_map['combo_apptlength'],\
			self.combo_apptlength_text_entered)

		if self.panel.__dict__.has_key('txt_recall_for'):
			EVT_TEXT(self.panel.txt_recall_for,\
			self.id_map['txt_recall_for'],\
			self.txt_recall_for_text_entered)

		if self.panel.__dict__.has_key('txt_recall_due'):
			EVT_TEXT(self.panel.txt_recall_due,\
			self.id_map['txt_recall_due'],\
			self.txt_recall_due_text_entered)

		if self.panel.__dict__.has_key('txt_recall_addtext'):
			EVT_TEXT(self.panel.txt_recall_addtext,\
			self.id_map['txt_recall_addtext'],\
			self.txt_recall_addtext_text_entered)

		if self.panel.__dict__.has_key('txt_recall_include'):
			EVT_TEXT(self.panel.txt_recall_include,\
			self.id_map['txt_recall_include'],\
			self.txt_recall_include_text_entered)

		if self.panel.__dict__.has_key('txt_recall_progressnotes'):
			EVT_TEXT(self.panel.txt_recall_progressnotes,\
			self.id_map['txt_recall_progressnotes'],\
			self.txt_recall_progressnotes_text_entered)

	def btnOK_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btnOK_button_clicked(self, event) 
			

		print "btnOK_button_clicked received ", event
			

	def btnClear_button_clicked( self, event): 
		if self.impl <> None:
			self.impl.btnClear_button_clicked(self, event) 
			

		print "btnClear_button_clicked received ", event
			

	def combo_tosee_text_entered( self, event): 
		if self.impl <> None:
			self.impl.combo_tosee_text_entered(self, event) 
			

		print "combo_tosee_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['tosee']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['tosee'] = str(obj.GetValue())
				
			print self.model, "tosee = ",  self.model['tosee']
		

	def combo_recall_method_text_entered( self, event): 
		if self.impl <> None:
			self.impl.combo_recall_method_text_entered(self, event) 
			

		print "combo_recall_method_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['recall_method']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['recall_method'] = str(obj.GetValue())
				
			print self.model, "recall_method = ",  self.model['recall_method']
		

	def combo_apptlength_text_entered( self, event): 
		if self.impl <> None:
			self.impl.combo_apptlength_text_entered(self, event) 
			

		print "combo_apptlength_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['apptlength']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['apptlength'] = str(obj.GetValue())
				
			print self.model, "apptlength = ",  self.model['apptlength']
		

	def txt_recall_for_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_recall_for_text_entered(self, event) 
			

		print "txt_recall_for_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['recall_for']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['recall_for'] = str(obj.GetValue())
				
			print self.model, "recall_for = ",  self.model['recall_for']
		

	def txt_recall_due_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_recall_due_text_entered(self, event) 
			

		print "txt_recall_due_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['recall_due']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['recall_due'] = str(obj.GetValue())
				
			print self.model, "recall_due = ",  self.model['recall_due']
		

	def txt_recall_addtext_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_recall_addtext_text_entered(self, event) 
			

		print "txt_recall_addtext_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['recall_addtext']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['recall_addtext'] = str(obj.GetValue())
				
			print self.model, "recall_addtext = ",  self.model['recall_addtext']
		

	def txt_recall_include_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_recall_include_text_entered(self, event) 
			

		print "txt_recall_include_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['recall_include']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['recall_include'] = str(obj.GetValue())
				
			print self.model, "recall_include = ",  self.model['recall_include']
		

	def txt_recall_progressnotes_text_entered( self, event): 
		if self.impl <> None:
			self.impl.txt_recall_progressnotes_text_entered(self, event) 
			

		print "txt_recall_progressnotes_text_entered received ", event
			
	
		if event <> None:
			obj = event.GetEventObject()
			try :
				self.model['recall_progressnotes']= obj.GetValue()
			except:
				# for dumbdbm persistent maps
				self.model['recall_progressnotes'] = str(obj.GetValue())
				
			print self.model, "recall_progressnotes = ",  self.model['recall_progressnotes']
		
section_num_map =  {1: 'gmSECTION_SUMMARY', 2: 'gmSECTION_DEMOGRAPHICS', 3: 'gmSECTION_CLINICALNOTES', 4: 'gmSECTION_FAMILYHISTORY', 5: 'gmSECTION_PASTHISTORY', 6: 'gmSECTION_VACCINATION', 7: 'gmSECTION_ALLERGIES', 8: 'gmSECTION_SCRIPT', 9: 'gmSECTION_REQUESTS', 10: 'gmSECTION_MEASUREMENTS', 11: 'gmSECTION_REFERRALS', 12: 'gmSECTION_RECALLS'}

import gmGuiBroker
gb = gmGuiBroker.GuiBroker()
for k,v in section_num_map.items():
	exec("prototype = %s_handler(None)" % v)
	gb[v] = prototype
	
