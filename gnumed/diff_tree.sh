#!/bin/bash

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/diff_tree.sh,v $
# $Revision: 1.5 $

./remove_pyc.sh

export CVS_RSH="ssh"
echo "diffing local copy against CVS master tree"
cvs -z9 diff | tee public-tree.diff
