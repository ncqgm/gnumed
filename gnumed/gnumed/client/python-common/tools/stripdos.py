#!/usr/bin/python

# license GPL
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/python-common/tools/Attic/stripdos.py,v $
__version__ = "$Revision: 1.1 $"

import sys, string, glob
files = glob.glob("*.TXT")
for file in files:
	f = open(file)
	print "Processing file", file
	fo = open(file+'.unix', "w")
	lines = f.readlines()
	f.close()
	for line in lines:
		unixline = string.replace(line, "\r\n", "\n")
		fo.write(unixline)
	fo.close()
#=====================================================
# $Log: stripdos.py,v $
# Revision 1.1  2002-10-01 10:41:24  ncq
# - as per Richard's request
#
