"""loads handler onto widgets stored in widget map of guiBroker."""
load_handles = 1 # set to zero if want no handles
import gmGuiBroker 
import EditAreaHandler
from handler_gmSelectPersonImpl import *
from handler_patient import *
import cPickle 

from  wxPython.wx import *
import gmDispatcher, gmSignals


def configure_handlers():

	gb = gmGuiBroker.GuiBroker()
	gb['DlgSelectPerson_handler'] = gmSelectPerson_handler_impl()
	handler = gmDemographics_handler(None)
	try :
		model = cPickle.load(file('gmDemographics', 'r'))
	except:
		model = {}
		
	handler.set_model( model) 

	gb['models'] = {}
	gb['models']['gmDemographics'] = model
	gb['PatientsPanel_handler'] = handler

	frame = gb['main.frame']
	gmDispatcher.connect( save_models, gmSignals.application_clean_closing())

	#evt_handler =  CloseCleanupEvtHandler( frame)
	#evt_handler.SetEvtHandlerEnabled(1)
	#frame.PushEventHandler( evt_handler)
	#frame.SetEvtHandlerEnabled(1)
	#print "FRAME got event handler", evt_handler
		

	

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
				section_name =  EditAreaHandler.section_num_map[section]
				print "section = %d, or section name=%s\n" % (section, section_name) 


				# get a registered handler, and use it's cloning method create_handler to clone another handler for this editarea.rightside
				gb = gmGuiBroker.GuiBroker()
				
				if  gb.has_key( section_name ):
					gb[section_name].create_handler(widget.editarea.rightside) 	
					print "**** HANDLER IS IN ! (but it does nothing)"
					continue
				# remove this later, into main directory code

			handler_name = widget.__class__.__name__ + "_handler" 
			if gb.has_key( handler_name ):
				handler = gb[handler_name]
				handler.create_handler(widget)
				load_widget(widget, handler.model)
			continue

def init_handlers():
	configure_handlers()
	load_handlers()	

def main():
	init_handlers()

gmDispatcher.connect(init_handlers,  gmSignals.application_init())
