#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/dists/Distutils/Attic/setup_workspace.sh,v $
# $Id: setup_workspace.sh,v 1.2 2005-06-13 16:32:46 ncq Exp $

REV=$1

echo "setting up workspace"
cp -R ../../client/bitmaps ./GNUmed-$REV/
cp -R ../../client/business ./GNUmed-$REV/
cp -R ../../client/doc ./GNUmed-$REV/
cp -R ../../client/locale ./GNUmed-$REV/
cp -R ../../client/pycommon ./GNUmed-$REV/
cp -R ../../client/wxpython ./GNUmed-$REV/

echo "cleaning out debris"
find ./ -name '*.pyc' -exec rm -v '{}' ';'

#------------------------------------------
# $Log: setup_workspace.sh,v $
# Revision 1.2  2005-06-13 16:32:46  ncq
# - let user specify revision
#
