#!/bin/bash

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/update_tree.sh,v $
# $Revision: 1.9 $

./remove_pyc.sh

export CVS_RSH="ssh"
echo "diffing against CVS just to be sure"
cvs -z9 diff | tee before-update.diff
echo "updating python client source from CVS"
cvs -z9 update -dP | tee update.log
