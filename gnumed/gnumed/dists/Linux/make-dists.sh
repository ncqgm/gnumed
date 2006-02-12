#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/dists/Linux/Attic/make-dists.sh,v $
# $Id: make-dists.sh,v 1.4 2006-02-12 18:07:06 shilbert Exp $
# license: GPL
# Karsten.Hilbert@gmx.net

REV=0.2
SUBREV=0
echo "=> client ..."
tar -cvhzf GNUmed-client.$REV.$SUBREV.tgz GNUmed-$REV/client install.sh GNUmed-$REV/GnuPublicLicense.txt GNUmed-$REV/check-prerequisites.py GNUmed-$REV/check-prerequisites.sh

echo "=> server ..."
tar -cvhzf GNUmed-server.$REV.$SUBREV.tgz GNUmed-$REV/server GNUmed-$REV/GnuPublicLicense.txt GNUmed-$REV/check-prerequisites.py GNUmed-$REV/check-prerequisites.sh

echo "=> client + server ..."
tar -cvzf GNUmed.$REV.$SUBREV.tgz GNUmed-client.$REV.$SUBREV.tgz GNUmed-server.$REV.$SUBREV.tgz

#============================================
# $Log: make-dists.sh,v $
# Revision 1.4  2006-02-12 18:07:06  shilbert
# - nearing v0.2
#
# Revision 1.3  2005/08/14 16:34:41  shilbert
# - bump up to rc5
# - cater for subrevisions
#
# Revision 1.2  2005/07/10 17:44:59  ncq
# - slightly better packages
#
