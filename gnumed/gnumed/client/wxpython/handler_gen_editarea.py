usage=""" python editarea_gen_listener.py  > EditAreaHandler.py   and generates handler
	hooks for the different uis in gmEditArea.

	  Any handling code will be lost so must backup old handler scripts to later 
	  cut and paste. Could use a wxGlade like mechanism for merging user code with
	  generated code.

	  Name changes on gmEditArea will be reflected onto EditAreaHandler ,
	  and the function names will change if the editarea component names are changed.
	  """
	 	

import fileinput
import re

import string
import sys

target = 'gmEditArea.py'
		
from  handler_generator	import generator	
 
		

def process_section(gen,  map):
#	print "#the section map = ", map
	gen.process_list(map['components'])
	gen.print_class( map['name'])

if __name__ == "__main__":
	
	lines = fileinput.input(target)

	print """# scanning for section headers,
	#	then for components in file """, target, """
	#	and generating a script template for attaching
	#	a listener to the components.  """
	section_str = '.*section\s*==\s*(?P<section>\w+)'
	prog_section_start = re.compile(section_str, re.I )



	prog_def = re.compile( '(?P<name>gmSECTION\w+)\s*=\s*(?P<number>[0-9]+)')
	section_num_map = {}

		
	section_map = {}

	gen = generator()
	gen.print_setup()
	common_comps = []
	for l in lines:
		re_match_obj = prog_def.match(l)
		if re_match_obj <> None:
			section_num_map[int(re_match_obj.group('number'))] = re_match_obj.group('name')
			continue
		# match a section start : the state 'creating map' is when section_map.has_key['name'] 
		re_match_obj =  prog_section_start.match(l)
		if re_match_obj <> None:
			sys.stderr.write('\nSection is %s\n' % re_match_obj.group('section') )
			if section_map <> {} :
				process_section(gen, section_map)

			section_map = {}
			section_map['name'] = re_match_obj.group('section') 
			section_map['components'] = []
			section_map['components'].extend( common_comps)
			continue
			
		# match for components	
		#sys.stderr.write( "#checking  %s against %s\n"% (l,  prog_map.keys()))

		prog_map = gen.get_prog_map()

		name_type = gen.get_name_type_for_line(l)
		if name_type <> None and section_map.has_key('name'):
			sys.stderr.write( '#*** %s is a %s\n'% name_type )
			section_map['components'].append( ( name_type ))
			continue

		if name_type <> None :
			common_comps.append( name_type )
		


	if section_map.has_key('name'):
		process_section(gen, section_map)

	print "section_num_map = ", section_num_map

	print """
import gmGuiBroker
gb = gmGuiBroker.GuiBroker()
for k,v in section_num_map.items():
	exec("prototype = %s_handler(None)" % v)
	gb[v] = prototype
	"""


		


