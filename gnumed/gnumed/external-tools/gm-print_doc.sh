#!/bin/sh

# ===========================================================
# Print documents via system tools.
#
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/external-tools/Attic/gm-print_doc.sh,v $
# $Id: gm-print_doc.sh,v 1.1 2009-12-21 23:04:26 ncq Exp $
# ===========================================================

TYPE="$1"
shift 1
FILES="$@"

if [ "${TYPE}" = "medication_list" ]; then
	kprinter -c ${FILES}
	rm -f ${FILES}
	exit 0
fi


exit 0
# ===========================================================
# $Log: gm-print_doc.sh,v $
# Revision 1.1  2009-12-21 23:04:26  ncq
# - default print script
#
#