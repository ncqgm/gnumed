"""loads handler onto widgets stored in widget map of guiBroker."""
import handler_all_gen
handler_all_gen.main()
import gmGuiBroker 
from handler_editarea_defs import *
from handler_gmSelectPersonImpl import *
from handler_patient import *
import cPickle 

from  wxPython.wx import *
import gmDispatcher, gmSignals
import handler_gui
from  handler_gui import *
import handler_editarea_impl
import patient_model


def configure_handlers():

	gb = gmGuiBroker.GuiBroker()
	gb['gmSelectPerson_handler'] = gmSelectPerson_handler_impl()
	handler = gmDemographics_mapping_handler(None)
	try :
		model = cPickle.load(file('gmDemographics', 'r'))
	except:
		model = {}
		
	handler.set_model( model) 

	gb['models'] = {}
	gb['models']['gmDemographics'] = model
	gb['gmDemographics_handler'] = handler

	gb['models']['patient'] = patient_model.patient_model()
	pat_model = gb['models']['patient'] 
	# temporary kludge
	pat_model.demographics = model
	
	gb['gmSECTION_ALLERGIES'].set_impl( handler_editarea_impl.gmSECTION_ALLERGIES_funcs_impl(pat_model))
	gb['gmSECTION_SCRIPT'].set_impl( handler_editarea_impl.gmSECTION_SCRIPT_funcs_impl(pat_model))

	gb['gmSECTION_PASTHISTORY'].set_impl( handler_editarea_impl.gmSECTION_PASTHISTORY_funcs_impl(pat_model))


	gmDispatcher.connect( save_models, gmSignals.application_clean_closing())

		

	

def save_models():
	gb = gmGuiBroker.GuiBroker()
	
	cPickle.dump(gb['models']['gmDemographics'] ,  file('gmDemographics', 'w'))

def load_widget(widget, model):
	if model <> None:
		wkeys = widget.__dict__.keys()
		for k in model.keys():
			if model[k] <> None:
				pass
				# code to compare the widget names
				
	

def load_handlers():
	gb = gmGuiBroker.GuiBroker()
	if gb.has_key('widgets'):
		map = gb['widgets']
		for k, widget  in map.items():
			print "widget found = ",k, widget
			if widget.__dict__.has_key('editarea'):
				#all set to put in hooks
				section = widget.editarea.rightside.section
				section_name =  section_num_map[section]
				print "section = %d, or section name=%s\n" % (section, section_name) 


				# get a registered handler, and use it's cloning method create_handler to clone another handler for this editarea.rightside
				gb = gmGuiBroker.GuiBroker()
				
				if  gb.has_key( section_name ):
					gb[section_name].create_handler(widget.editarea.rightside) 	
					continue
				# remove this later, into main directory code

			handler_name = widget.__module__ + "_handler" 
			handler_name = string.split(handler_name, '.')[-1]
			if gb.has_key( handler_name ):
				handler = gb[handler_name]
				handler.create_handler(widget)
				load_widget(widget, handler.model)

			if not gb.has_key( handler_name ):
				print"there is no handler for ", handler_name

def init_handlers():
	configure_handlers()
	load_handlers()	

def main():
	handler_all_gen.main()
	init_handlers()

gmDispatcher.connect(init_handlers,  gmSignals.application_init())
