#!/bin/sh

# $Source: 
# $Revision: 1.1 $
# GPL
# Karsten.Hilbert@gmx.net

REV=0.1

echo "=> client ..."
tar -cvhzf GNUmed-client_$REV.tar.gz GNUmed-$REV/client check-prerequisites.py check-prerequisites.sh GnuPublicLicense.txt install.sh

echo "=> server ..."
tar -cvhzf GNUmed-server_$REV.tar.gz GNUmed-$REV/server check-prerequisites.py check-prerequisites.sh GnuPublicLicense.txt

echo "=> client + server ..."
tar -cvzf GNUmed.tgz GNUmed-client_$REV.tar.gz GNUmed-server_$REV.tar.gz
