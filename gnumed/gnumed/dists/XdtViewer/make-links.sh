#!/bin/sh

#========================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/dists/XdtViewer/Attic/make-links.sh,v $
# $Id: make-links.sh,v 1.3 2005-12-06 22:46:48 shilbert Exp $

echo "making links"
ln -vfs ../../client/wxpython/gui/gmXdtViewer.py gmXdtViewer.py

mkdir -v modules
ln -vfs ../../../client/pycommon/gmCLI.py modules/gmCLI.py
ln -vfs ../../../client/pycommon/gmI18N.py modules/gmI18N.py
ln -vfs ../../../client/pycommon/gmLog.py modules/gmLog.py
ln -vfs ../../../client/business/gmXdtMappings.py modules/gmXdtMappings.py

mkdir locale
mkdir locale/de_DE@euro
mkdir locale/de_DE@euro/LC_MESSAGES
ln -vfs ../../../../../client/locale/de-gnumed.mo locale/de_DE@euro/LC_MESSAGES/gnumed.mo

mkdir data
mkdir data/xDT
ln -vfs ../../../../data/BDT/adt-01_99-bdt-02_94.bdt data/xDT/adt-01_99-bdt-02_94.bdt

echo "done"
#========================================================
# $Log: make-links.sh,v $
# Revision 1.3  2005-12-06 22:46:48  shilbert
# - fix some paths to math current CVS
#
# Revision 1.2  2003/02/16 14:07:03  ncq
# - add link to translation
#
# Revision 1.1  2003/02/15 17:14:32  ncq
# - first check in
#
