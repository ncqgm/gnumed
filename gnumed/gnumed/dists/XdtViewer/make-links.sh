#!/bin/sh

#========================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/dists/XdtViewer/Attic/make-links.sh,v $
# $Id: make-links.sh,v 1.2 2003-02-16 14:07:03 ncq Exp $

echo "making links"
ln -vfs ../../client/wxpython/gui/gmXdtViewer.py gmXdtViewer.py

mkdir -v modules
ln -vfs ../../../client/python-common/gmCLI.py modules/gmCLI.py
ln -vfs ../../../client/python-common/gmI18N.py modules/gmI18N.py
ln -vfs ../../../client/python-common/gmLog.py modules/gmLog.py
ln -vfs ../../../client/business/gmXdtMappings.py modules/gmXdtMappings.py

mkdir locale
mkdir locale/de_DE@euro
mkdir locale/de_DE@euro/LC_MESSAGES
ln -vfs ../../../../../client/locale/de-gnumed.mo locale/de_DE@euro/LC_MESSAGES/gnumed.mo

echo "done"
#========================================================
# $Log: make-links.sh,v $
# Revision 1.2  2003-02-16 14:07:03  ncq
# - add link to translation
#
# Revision 1.1  2003/02/15 17:14:32  ncq
# - first check in
#
