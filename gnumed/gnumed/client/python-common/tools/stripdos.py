#!/usr/bin/python

# license GPL
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/python-common/tools/Attic/stripdos.py,v $
__version__ = "$Revision: 1.2 $"

import sys, string, glob, os.path

files = glob.glob("*.TXT")
files.extend(glob.glob("*.txt"))
files.extend(glob.glob("*.Txt"))

for file in files:
	f = open(file)
	new_name = string.lower(os.path.splitext(os.path.basename(file))[0]) + '.unix'
	if os.path.exists(new_name):
		print "will not overwrite existing file [%s -> %s]" % (file, new_name)
		continue
	print "converting [%s -> %s]" % (file, new_name)
	fo = open(new_name, "wb")
	lines = f.readlines()
	f.close()
	for line in lines:
		unixline = string.replace(line, "\r\n", "\n")
		fo.write(unixline)
	fo.close()
#=====================================================
# $Log: stripdos.py,v $
# Revision 1.2  2003-04-17 20:49:27  ncq
# - TMP.TXT -> tmp.unix
#
# Revision 1.1  2002/10/01 10:41:24  ncq
# - as per Richard's request
#
