#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/update_tree.sh,v $
# $Revision: 1.5 $

export CVS_RSH="ssh"
echo "cleaning out debris"
find ./ -name '*.pyc' -exec rm -v '{}' ';'
echo "diffing against CVS just to be sure"
cvs -z9 diff | tee diff-before-update.log
echo "updating python client source from CVS"
cvs -z9 update -d | tee update.log
