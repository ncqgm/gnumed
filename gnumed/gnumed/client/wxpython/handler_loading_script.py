"""loads handler onto widgets stored in widget map of guiBroker."""

import gmGuiBroker 
import EditAreaHandler

def load_handlers():
	gb = gmGuiBroker.GuiBroker()
	if gb.has_key('widgets'):
		map = gb['widgets']
		for k, widget  in map.items():
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
			continue
	
load_handlers()	
