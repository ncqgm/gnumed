#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/dists/Linux/Attic/make-dists.sh,v $
# $Id: make-dists.sh,v 1.2 2005-07-10 17:44:59 ncq Exp $
# license: GPL
# Karsten.Hilbert@gmx.net

REV=0.1

echo "=> client ..."
tar -cvhzf GNUmed-client.$REV.tgz GNUmed-$REV/client GNUmed-$REV/install.sh GNUmed-$REV/GnuPublicLicense.txt GNUmed-$REV/check-prerequisites.py GNUmed-$REV/check-prerequisites.sh

echo "=> server ..."
tar -cvhzf GNUmed-server.$REV.tgz GNUmed-$REV/server GNUmed-$REV/GnuPublicLicense.txt GNUmed-$REV/check-prerequisites.py GNUmed-$REV/check-prerequisites.sh

echo "=> client + server ..."
tar -cvzf GNUmed.$REV.tgz GNUmed-client.$REV.tgz GNUmed-server.$REV.tgz

#============================================
# $Log: make-dists.sh,v $
# Revision 1.2  2005-07-10 17:44:59  ncq
# - slightly better packages
#
