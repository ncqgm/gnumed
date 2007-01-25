#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/remove_pyc.sh,v $
# $Revision: 1.6 $

echo "cleaning out debris"
find ./ -name '*.pyc' -exec rm -v '{}' ';'
find ./ -name '*.py~' -exec rm -v '{}' ';'
find ./ -name 'wxg*.wxg~' -exec rm -v '{}' ';'
find ./ -name '*.log' -exec rm -v '{}' ';'
find ./ -name '*.tgz' -exec rm -v '{}' ';'
find ./ -name '*.bz2' -exec rm -v '{}' ';'
