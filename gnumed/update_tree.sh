#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/update_tree.sh,v $
# $Revision: 1.1 $

echo "cleaning out debris"
find ./ -name '*.pyc' -exec rm -v '{}' ';'
echo "updating python client source from CVS"
cvs -z9 update
