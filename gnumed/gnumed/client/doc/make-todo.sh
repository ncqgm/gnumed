#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/doc/make-todo.sh,v $
# $Revision: 1.1 $
# license: GPL
# author: Karsten.Hilbert@gmx.net

# where to look for files
BASE="../"

find ${BASE} -follow -name '*.py' -print0 | xargs -0 python find_todo.py > current-TODOs.lst

#============================================
# $Log: make-todo.sh,v $
# Revision 1.1  2005-01-19 09:16:32  ncq
# - improved readability
#
#
