#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/diff_tree.sh,v $
# $Revision: 1.1 $

echo "cleaning out debris"
find ./ -name '*.pyc' -exec rm -v '{}' ';'
echo "diffing local copy against CVS master tree"
cvs -z9 diff | tee diff.log
