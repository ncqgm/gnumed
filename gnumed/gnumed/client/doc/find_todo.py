"""Find places marked with FIXME that need work.

example:

FIXME: plugin loading should be optional
"""
#=====================================================================
# $Id
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/doc/find_todo.py,v $
__version__ = "$Revision: 1.1 $"
__author__ = "Karsten Hilbert"
__license__ = "GPL (details at http://www.gnu.org)"

import string, sys, fileinput

if len(sys.argv) < 2:
	print "Usage: find_todo.py <a_python_script> <a_python_script> ..."
	sys.exit(1)

print "Searching for places to fix in", sys.argv[1:]

prev_file = ""

for line in fileinput.input():
	curr_file = fileinput.filename()

	if prev_file != curr_file:
		print "%s:" % curr_file
		prev_file = curr_file

	line = line.strip()
	if line.find('FIXME') != -1:
		line_no = fileinput.filelineno()
		line = line.replace('\015','')
		line = line.replace('\012','')
		print '#%s: %s' % (line_no, line)

#=====================================================================
# $Log: find_todo.py,v $
# Revision 1.1  2005-01-19 08:39:49  ncq
# - moved here from pycommon/tools/
#
# Revision 1.2  2004/06/25 12:29:47  ncq
# - coding style
#
# Revision 1.1  2004/02/25 09:30:13  ncq
# - moved here from python-common
#
