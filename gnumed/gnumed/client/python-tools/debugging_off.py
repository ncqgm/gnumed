#!/usr/bin/python
###############################################################
# This is to disable excess debugging in production releases.
#
# theory of operation:
#
# debugging comments that should be off in a release build
# must be fenced off by the two tags #<DEBUG> and #</DEBUG>
#
# example:
#
#	do.something()
#
#	#<DEBUG>
#	log.log(everything)
#	shout.at(user)
#	#</DEBUG>
#
#	do.something_else(now)
#
#--------------------------------------------------------------
# @author: Karsten Hilbert
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @Date: $Date: 2002-06-16 19:34:43 $
# @version $Revision: 1.3 $ $Date: 2002-06-16 19:34:43 $ $Author: ncq $
###############################################################

import string, sys, fileinput

if len(sys.argv) < 2:
	print "Usage: debugging_off.py <a_python_script> <a_python_script> ..."
	sys.exit(1)

print "Removing excess debugging from", sys.argv[1:]

for line in fileinput.input(inplace=1, backup='.bak1'):
	line = string.replace(line, '\015','')
	line = string.replace(line, '\012','')
	tmp = string.lstrip(line)

	# find start of tagged debugging
	if string.find(tmp, "#<DEBUG>", 0, 8) == 0:
		left, right = string.split(line, '#<DEBUG>', 1)
		print left + '"""#<DEBUG>' + right

	# find end of tagged debugging
	elif string.find(tmp, "#</DEBUG>", 0, 9) == 0:
		left, right = string.split(line, '#</DEBUG>', 1)
		print left + '#</DEBUG>"""' + right

	else:
		print line
