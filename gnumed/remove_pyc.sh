#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/remove_pyc.sh,v $
# $Revision: 1.4 $

echo "cleaning out debris"
find ./ -name '*.pyc' -exec rm -v '{}' ';'
find ./ -name '*.py~' -exec rm -v '{}' ';'
find ./ -name 'wxg*.wxg~' -exec rm -v '{}' ';'
find ./ -name '*.mo' -exec rm -v '{}' ';'
