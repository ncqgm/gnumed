#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/doc/make-apidocs.sh,v $
# $Revision: 1.1 $
# license: GPL
# author: Karsten.Hilbert@gmx.net

nice -n 19 epydoc -n GnuMed -u http://www.gnumed.org --no-private -o ~/gm-apidocs ~/gnumed/gnumed/client/ &> ~/epydoc.log

#============================================
# $Log: make-apidocs.sh,v $
# Revision 1.1  2004-07-14 10:11:04  ncq
# - first checkin
#
