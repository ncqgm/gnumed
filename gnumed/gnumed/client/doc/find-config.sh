#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/doc/find-config.sh,v $
# $Revision: 1.1 $
# license: GPL
# author: Karsten.Hilbert@gmx.net

# where to look for files
BASE="../"

find ${BASE} -follow -name '*.py' -print0 | xargs -0 grep "option.*=.*\'\'" > current-options.lst

#============================================
# $Log: find-config.sh,v $
# Revision 1.1  2007-03-18 13:17:00  ncq
# - find config options from source
#
#