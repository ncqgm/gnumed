from patient_model import *
from handler_frame import *
from gmGuiBroker import *
from gmDispatcher import *
from gmSignals import *
import time
import os, sys
from handler_popup  import *
from handler_timed_button import *
from handler_icd9_search import Search
import re
import traceback

ICD_TEXT_FILENAME='./wxpython/Dindex03.txt'


class UpdateCommand:
	def __init__(self, patient_model, info ,command_name, list_getter, list_changer,  widget_list_setter , list_unchanger ):
		self.patient_model = patient_model
		self.info = info
		self.list_getter = list_getter
		self.list_changer = list_changer
		self.widget_list_setter = widget_list_setter
		self.old_info = None
		self.command_name = command_name
		self.list_unchanger = list_unchanger
		pass
	def GetName(self):
		return self.command_name
	def CanUndo(self):
		return self.old_info <> None

	def Undo(self):
		if self.old_info == None:
			return
		self.list_unchanger(self.old_info)
		self.update_ui()

	def update_ui(self):
		self.widget_list_setter( self.list_getter(),  1)
		
	def Do(self):	
		print"before update info=",self.info
		self.old_info   = self.list_changer(self.info)
		print " list now = ", self.list_getter()
		print"after  update info=",self.info
		print"after  update old.info=",self.old_info
		self.update_ui()





class AllergyUpdateCommand:
	def __init__(self, patient_model, allergy):
		self.patient_model = patient_model
		self.allergy = allergy
		self.old_allergy = None
		pass
	def GetName(self):
		return "Update Allergy"
	def CanUndo(self):
		return self.old_allergy <> None

	def Undo(self):
		self.patient_model.add_allergy(self.old_allergy)
		self.update_ui()

	def update_ui(self):
		gb = GuiBroker()
		widget = gb['widgets']['AllergyPanel']
		widget.UpdateAllergiesWithList( self.patient_model.get_allergies(), clearFirst= 1 )
		
	def Do(self):	
		self.old_allergy = self.patient_model.add_allergy(self.allergy)
		print " list now = ", self.patient_model.get_allergy_list()
		self.update_ui()

		


	
class funcs_impl:
	def set_owner(self, owner_handler):
		self.owner = owner_handler
		if self.owner <> None and self.owner.panel <> None:
			self.panel= self.owner.panel
			self.get_refs_from_owner()
	
	def get_refs_from_owner(self):
		pass	
	

class gmSECTION_ALLERGIES_funcs_impl( funcs_impl):


	def __init__(self, patient_model):
	    self.patient_model= patient_model
	    #gmDispatcher.connect( self.drug_selected, gmSignals.drug_selected() )
	    self.allergy_list = None

	    self.configure_allergy_list()	

	    self.clear_allergy_action = None
	    pass	
	
	def get_refs_from_owner( self):
		self.panel = self.owner.panel
		self.create_allergy_drug_list_helper()

	def create_allergy_drug_list_helper(self):
		obj = self.owner.panel.text2_allergy_drug
		
		self.allergy_list = ListFrame(obj, wxNewId())
		self.allergy_list.set_list(self.patient_model.get_drug_allergy_list() )
		self.allergy_list.set_control( obj)
		self.allergy_list.set_is_filtering(1)
		self.allergy_list.set_list_listener(self.allergy_drug_selected)	

	def configure_allergy_list(self):
	    gb = GuiBroker()
	    wxlist = gb['widgets']['AllergyPanel'].list_allergy
	    EVT_LIST_ITEM_ACTIVATED(wxlist, wxlist.GetId(), self.allergy_list_item_activated)
	    wxlist.SetToolTipString('double-click to select a drug for editing')

	def allergy_list_item_activated( self,  event):

	    ix = event.GetIndex()

	    print "Index selected = ", ix 
	    headings = ['date_recorded', 'allergy_drug','allergy_class','drug_reaction']
	    wxList = event.GetEventObject()
	    map = {}
	    for i in xrange(0, len(headings)):
		map[headings[i]]= wxList.GetItem( ix, i+1).GetText()
	
	    self.owner.model.update(map)
	    self.owner.update_ui()	    	
	

	def drug_selected(self):
	    gb = guiBroker()
	    drug = gb['gmSECTION_ALLERGIES'].text2_allergy_drug.GetValue()
	    self.patient_model.set_selected_drug(drug)
	    aclass = self.patient_model.get_current_drug_class()
	    gb['gmSECTION_ALLERGIES'].text4_allergy_class.SetValue(aclass)        


        def allergy_drug_selected(self, event):
	    print self, " got this event ", event
	
	def check_entry_constraints(self, model):
		if  len(model.get('allergy_drug', "")) == 0 or \
			len (model.get('drug_reaction',"")) == 0:
			return " please enter drug,\n and reaction" 		

		if not self.patient_model.is_drug_in_class( model['allergy_drug'], model['allergy_class'] ):
			return 'drug is not in given drug class'
				
		return None 

	def enforce_constraints(self, model):
		aclass = self.patient_model.get_class_for_drug( model['allergy_drug'])
		if aclass <> None:
			model['allergy_class'] = aclass

	
	def btnOK_button_clicked( self, event):
		model = self.owner.model
		
		msg = self.check_entry_constraints(model)
		if msg <> None:	
			handler_popup(event.GetEventObject() , msg )
			return 0

		self.enforce_constraints( model)	

		allergy = {}
		allergy['key'] = time.time()
		allergy.update( model)
		command = AllergyUpdateCommand( self.patient_model, allergy)
		command.Do()
	
	
	def btnClear_button_clicked( self, event):
		if self.clear_allergy_action == None:
			self.clear_allergy_action = timed_clear_map_behaviour(self.owner)
		command = self.clear_allergy_action.check_time()
			

	def text1_date_recorded_text_entered( self, event):
		pass
	

	def text2_allergy_drug_text_entered( self, event):
                obj = event.GetEventObject()
	
		aclass = self.patient_model.get_class_for_drug(obj.GetValue())
		if aclass <> None:
		   self.panel.text4_allergy_class.SetValue( aclass)

		
	def text3_generic_drug_text_entered( self, event):
		pass
		

	def text4_allergy_class_text_entered( self, event):
		pass
	

	def text5_drug_reaction_text_entered( self, event):
		pass
	

	def cb1_generic_specific_checkbox_clicked( self, event):
		pass
	

	def rb1_is_allergy_radiobutton_clicked( self, event):
		pass
	

	def rb2_is_sensitivity_radiobutton_clicked( self, event):
		pass
	

	def cb2_is_definite_allergy_checkbox_clicked( self, event):
		pass


class condition_browser_funcs:
	
	def __init__(self, search_filename , text_ctrl, receive_func = None):
		try:
			print"****   \n\n\n ***** Looking for ICD9 in ", search_filename
			self.searcher = Search(search_filename)
	
		except:
		   	try: 
				traceback.print_tb(sys.exc_info()[2])
				traceback.print_exc()
				self.searcher = Search(os.path.split(search_filename)[1])		
		   	except:
				print sys.exc_info()
				traceback.print_tb(sys.exc_info()[2])
				traceback.print_exc()
				return
	
		l = ListFrame(text_ctrl, wxNewId())
		l.set_is_filtering(0)
		l.set_list_getter(self.compose_condition_list)	    
		l.set_selection_filter(self.walk_up_and_remove_parentheses)
		l.set_pre_filter_sink( receive_func)		

	def walk_up_leaf_selection( self, event):
		terms = []
		text = event.GetString()
		index = event.GetEventObject().FindString(text)
		long_text =  self.searcher.walk_up_leaf_selection( self.results, index)
		return long_text

	def remove_parentheses(self, text):
		return self.searcher.remove_parentheses(text)

	def walk_up_and_remove_parentheses(self, event):
		return self.remove_parentheses( self.walk_up_leaf_selection( event) )

	def compose_condition_list( self, event):
		text = event.GetEventObject().GetValue()
		self.results = self.searcher.get_results(text)
		#print "*** results = ",self. results, "\n\n**********"
		return self.results

	

class gmSECTION_SCRIPT_funcs_impl(funcs_impl):
		
	def __init__(self, patient_model):
	    self.patient_model= patient_model
	    self.list_classes = None
	    self.sel_key = None
	    self.undo_list = []
	 
	def get_refs_from_owner(self):
	    self.set_list_helpers()
	    self.set_menu_handlers()
	    self.set_list_actions()

	    

	def set_list_helpers(self):
		self.set_class_drug_list_interaction()
		self.set_reason_condition_list()

	def set_reason_condition_list(self):
		self.condition_browser = \
			condition_browser_funcs(ICD_TEXT_FILENAME,\
					self.panel.text1_prescription_reason)

	def set_class_drug_list_interaction(self):
		l = ListFrame( self.panel.text2_drug_class , wxNewId())
		l.set_is_filtering(1)
		l.set_list(self.patient_model.get_drug_classes())	    
		self.list_classes = l
		
		k = ListFrame( self.panel.text3_generic_drug , wxNewId())
		k.set_is_filtering(1)
		k.set_list([])
		self.list_drugs = k
		
		EVT_SET_FOCUS(self.panel.text3_generic_drug, self.set_drug_list_from_class)
		self.clear_script = timed_clear_map_behaviour(self.owner)

	def disable_too_hard_to_do_menu_items(self):
		menu = self.get_widget().aMenu
		items = menu.GetMenuItems()
		enable_list = [self.get_module().ID_DelItem ]
		for x in items:
			if x.GetId() not in enable_list:
				x.Enable(0)

	def get_widget(self):
		 return GuiBroker()['widgets']['PrescriptionPanel']

	def get_module(self):
		import patient
		return patient.gmGP_Prescriptions

	def set_menu_handlers(self):
		self.disable_too_hard_to_do_menu_items()
		EVT_MENU(self.get_widget(), self.get_module().ID_DelItem, self.delete_script)
		
		EVT_MENU(self.get_widget(), self.get_module().ID_Undo, self.undo_last_action)

	
	def set_list_actions(self):
		EVT_LIST_ITEM_SELECTED(self.get_widget().list_script, self.get_module().ID_SCRIPTLIST, self.remember_selected_script)

		

	def remember_selected_script(self, event):
		print "list selection made = ", event.GetIndex(), event.GetData()
		self.index = event.GetIndex()
		self.sel_key = event.GetData()

	
	def undo_last_action(self, event):
		if self.undo_list <> []:
			item = self.undo_list[-1]
			self.undo_list.remove(item)
			item.Undo()
			self.check_undo_status()
			

	def check_undo_status(self):
		menu = self.get_widget().aMenu
		menuitems = filter( lambda x : x.GetId() == self.get_module().ID_Undo, menu.GetMenuItems() )
		
		menuitems[0].Enable( self.undo_list <> [] )
			
			

	def do_command(self, command):
		command.Do()
		if command.CanUndo():
			self.undo_list.append(command)
		self.check_undo_status()

	
	def delete_script(self, event):
		print "DELETE SCRIPT CALLED"
		model = self.patient_model.script_model

		command = UpdateCommand( self.patient_model, \
			info = self.sel_key , \
			command_name = "Delete Script",\
list_getter=model.get_session_scripts_as_tuples_key_data , \
list_changer = self.patient_model.script_model.delete_session_script,\
widget_list_setter= self.get_widget().UpdateScriptWithList,\
list_unchanger=model.add_session_script)

		self.do_command(command)
		
	def set_drug_list_from_class(self, event):
		print "got kill focus"
		self.list_drugs.set_list( self.patient_model.get_drugs_for_class( self.owner.panel.text2_drug_class.GetValue() ))
				
	def check_entry_constraints( self, model):
		if len( model.get('prescription_reason','').strip()) == 0 or\
		len(model.get('generic_drug','').strip()) == 0 or\
		len(model.get('directions','').strip()) == 0 or \
		len(model.get('quantity','').strip()) == 0 :
			return " INCOMPLETE ENTRY:\n You need  a minimum of\n  a prescription reason,\n a generic drug name,\n prescription directions, \n and quantity."

		return None 

	def btnOK_button_clicked( self, event):
		msg = self.check_entry_constraints( self.owner.model)
		if msg <> None:	
			handler_popup(event.GetEventObject() , msg )
			return 0
		
		model = self.patient_model.script_model
		command = UpdateCommand( \
	patient_model = model,\
	info = self.owner.model ,\
	command_name = "Script Update",\
	list_getter=model.get_session_scripts_as_tuples_key_data,\
	list_changer=model.add_session_script , \
widget_list_setter = self.get_widget().UpdateScriptWithList,\
	list_unchanger=model.add_session_script )

		self.do_command(command)
		



	def btnClear_button_clicked( self, event):
		self.clear_script.check_time()
		pass
	

	def text1_prescription_reason_text_entered( self, event):
		pass
	

	def text2_drug_class_text_entered( self, event):
		pass
				


				
	

	def text3_generic_drug_text_entered( self, event):
		text = event.GetEventObject().GetValue()
		aclass = self.patient_model.get_class_for_drug(text)
		if aclass <> None:
			self.panel.text2_drug_class.SetValue(aclass)
	

	def text4_brand_drug_text_entered( self, event):
		pass
	

	def text5_strength_text_entered( self, event):
		pass
	

	def text6_directions_text_entered( self, event):
		pass
	

	def text7_for_duration_text_entered( self, event):
		pass
	

	def text8_prescription_progress_notes_text_entered( self, event):
		pass
	

	def text9_quantity_text_entered( self, event):
		pass
	

	def cb_veteran_checkbox_clicked( self, event):
		pass
	

	def cb_reg24_checkbox_clicked( self, event):
		pass
	

	def cb_usualmed_checkbox_clicked( self, event):
		pass
	

	def btn_authority_button_clicked( self, event):
		pass
	

	def btn_briefPI_button_clicked( self, event):
		pass
	

	def text10_repeats_text_entered( self, event):
		pass


	
class gmSECTION_PASTHISTORY_funcs_impl(funcs_impl):
	
	def __init__(self, patient_model):
		self.patient_model = patient_model	
		try:
			self.searcher = Search(ICD_TEXT_FILENAME)
		except: 
			print sys.exc_info()
			self.searcher = Search(os.path.split(ICD_TEXT_FILENAME)[1])
		self.is_active_problem = 0
		self.command_history = []
		self.age_setting = 0
		
	def get_refs_from_owner( self):
		self.set_list_helpers()
		self.clear = timed_clear_map_behaviour(self.owner)
		self.delete = timed_clear_map_behaviour(self.owner, "DELETE of shown problem.")
		self.set_list_functions()
		self.set_tooltips()
		
		pass


	def set_tooltips(self):
		self.panel.txt_condition.SetToolTipString('ctrl-space or right-mouse to browse ICD-9 terms. Can repeat until coding found. Arrow keys can scroll the visible list.') 

	
	def set_list_helpers(self):
		self.condition_browser_funcs = condition_browser_funcs(ICD_TEXT_FILENAME, self.panel.txt_condition, self.update_notes_with_extended_condition)
	

	def set_list_functions(self):
		EVT_LIST_ITEM_ACTIVATED( self.get_widget().active_problem_list,\
			self.get_module().ID_ACTIVEPROBLEMLIST, self.edit_active_problem)
		
		EVT_LIST_ITEM_ACTIVATED( self.get_widget().significant_problem_list,\
			self.get_module().ID_SIGNIFICANTPASTHISTORYLIST, self.edit_past_history_problem)                  

	
	def edit_active_problem(self, event):
		self.edit_data_map(key = event.GetData(),\
		data_getter = self.patient_model.problems_model.get_active_problem)

			
	def edit_past_history_problem(self, event):
		self.edit_data_map(key = event.GetData(),\
		data_getter =  self.patient_model.problems_model.get_past_history)

	def edit_data_map( self, data_getter, key):
		data_map = data_getter(key)
		self.owner.model.update(data_map)
		self.owner.update_ui( data_map)


        def get_widget(self):
	        return GuiBroker()['widgets']['PastHistoryPanel']
	
        def get_module(self):
                 import patient
                 return patient.gmGP_PastHistory
								 

	def check_entry_constraints( self, ui_model):
		return None





	def UpdateProblemsWithList(self, map, clearFirst):
		model = self.patient_model.problems_model
		model.set_is_active_problem_update(0)
		self.get_widget().update_significant_history_list(self.map_to_key_list_tuples(model.get_problems_map()), 1)
		model.set_is_active_problem_update(1)
		self.get_widget().update_active_problem_list(self.map_to_key_list_tuples(model.get_problems_map()) , 1)

	def map_to_key_list_tuples(self, map):
		tuple_map = {}
		for k,v in map.items():
			tuple_map[k] =  self.map_to_key_list_tuple(v)
		return tuple_map

	def map_to_key_list_tuple(self, map):
		list = []
		key = map['key']
		order = ['yearnoted', 'condition']
		for x in order:
			list.append( map.get(x, ' ') )
		return  list


	

	def update_notes_with_extended_condition( self, event):
		text = self.condition_browser_funcs.walk_up_leaf_selection(event)
		texts = text.split()
		i = len(texts)
		self.panel.txt_notes1.SetValue( " ".join(texts[0:i/2]))
		self.panel.txt_notes2.SetValue(" ".join(texts[i/2:] ))



	def do_command(self, command):
		self.command_history.append(command)
		command.Do()

	def btnOK_button_clicked( self, event):
		msg = self.check_entry_constraints( self.owner.model)
		if msg <> None:	
			handler_popup(event.GetEventObject() , msg )
			return 0
		
		model = self.patient_model.problems_model
		model.set_is_active_problem_update(self.is_active_problem)
		
		command = UpdateCommand( \
	patient_model = model,\
	info = self.owner.model ,\
	command_name = "Problem Update",\
	list_getter=model.get_problems_map, \
	list_changer=model.add_problem , \
	widget_list_setter = self.UpdateProblemsWithList,\
	list_unchanger=model.add_problem )
	
		self.do_command(command)
		
	def btnClear_button_clicked( self, event):
		self.clear.check_time()
		pass

        def btnDel_button_clicked( self, event):
		key = self.owner.model.get('key', 0)
		if self.delete.check_time():
			model = self.patient_model.problems_model
			command = UpdateCommand( \
		patient_model = model,\
		info = key ,\
		command_name = "Problem Delete",\
		list_getter=model.get_problems_map,\
		list_changer=model.remove_problem,\
		widget_list_setter = self.UpdateProblemsWithList,\
		list_unchanger=model.add_problem )
			
			self.do_command(command)	
		

				
	def txt_condition_text_entered( self, event):
		pass

	def rb_sideleft_radiobutton_clicked( self, event):
		pass
	

	def rb_sideright_radiobutton_clicked( self, event):
		pass
	

	def rb_sideboth_radiobutton_clicked( self, event):
		pass
	

	def txt_notes1_text_entered( self, event):
		pass
	

	def txt_notes2_text_entered( self, event):
		pass
	

	def txt_agenoted_text_entered( self, event):
		text = event.GetEventObject().GetValue()
		try:
			i = int(text)
			self.age_setting = 1
			self.panel.txt_yearnoted.SetValue( str( i + self.get_years_from_birthdate() ) )
			self.age_setting = 0
		except:
			info = sys.exc_info()
			traceback.print_tb(info[2])
			traceback.print_exc()
			
			pass
			
	def get_years_from_birthdate(self):
	        t = time.strptime(self.patient_model.demographics['birthdate'], "%d-%m-%Y")
                return  t[0]

	

	def txt_yearnoted_text_entered( self, event):
		if self.age_setting == 1:
			return
		text = event.GetEventObject().GetValue()
		try:
			i = int( text )
			age = i - self.get_years_from_birthdate()
			if age > 0:
				self.panel.txt_agenoted.SetValue(str(age))
		except:
			info = sys.exc_info()
			traceback.print_tb(info[2])
			traceback.print_exc()

			
	

	def cb_active_checkbox_clicked( self, event):
		self.is_active_problem = event.GetEventObject().GetValue()	

	def cb_operation_checkbox_clicked( self, event):
		pass
	

	def cb_confidential_checkbox_clicked( self, event):
		pass
	

	def cb_significant_checkbox_clicked( self, event):
		pass
	

	def txt_progressnotes_text_entered( self, event):
		pass
	

class gmSECTION_VACCINATION_funcs:
		

	def btnOK_button_clicked( self, event):
		pass
	

	def btnClear_button_clicked( self, event):
		pass
	

	def txt_targetdisease_text_entered( self, event):
		pass
	

	def txt_vaccine_text_entered( self, event):
		pass
	

	def txt_dategiven_text_entered( self, event):
		pass
	

	def txt_serialno_text_entered( self, event):
		pass
	

	def txt_sitegiven_text_entered( self, event):
		pass
	

	def txt_progressnotes_text_entered( self, event):
		pass
	
