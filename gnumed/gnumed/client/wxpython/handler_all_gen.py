"""Run this to generate the default handlers"""

import os

def gen_cmd( cmd, filename_out):
	fin = os.popen(cmd)
	f = file( filename_out, 'w')
	f.writelines( fin.readlines())
	f.close()
	fin.close()

if __name__ == '__main__':
	print "generating"
	gen_cmd( 'python handler_generator.py -d patient', 'handler_patient.py')
	gen_cmd( 'python handler_generator.py -f gmSelectPerson.py', 'handler_gmSelectPerson.py')
	gen_cmd( 'python handler_generator.py -d gui', 'handler_gui.py')
	gen_cmd( 'python handler_gen_editarea.py', 'EditAreaHandler.py')

	
