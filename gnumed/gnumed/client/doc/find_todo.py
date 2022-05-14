"""Find places marked with FIXME that need work.

example:

FIXME: plugin loading should be optional
"""
#=====================================================================
__version__ = "$Revision: 1.2 $"
__author__ = "Karsten Hilbert"
__license__ = "GPL v2 or later (details at https://www.gnu.org)"

import string, sys, fileinput

if len(sys.argv) < 2:
	print("Usage: find_todo.py <a_python_script> <a_python_script> ...")
	sys.exit(1)

#print "Searching for places to fix in", sys.argv[1:]

prev_file = ''
for line in fileinput.input():
	curr_file = fileinput.filename()
	if curr_file != prev_file:
		print('=> %s' % curr_file)
		prev_file = curr_file

	line = line.strip()
	if line.find('FIXME') != -1:
		line_no = fileinput.filelineno()
		line = line.replace('\015','')
		line = line.replace('\012','')
		print('#%s: %s' % (line_no, line))
