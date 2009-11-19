#!/bin/bash

#==============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/external-tools/gm-remove_person.sh,v $
# $Id: gm-remove_person.sh,v 1.2 2009-11-19 15:07:34 ncq Exp $
#
# author: Karsten Hilbert
# license: GPL v2
#
# This script can be used to remove a person
# from a GNUmed database.
#
#==============================================================

SQL_FILE="/tmp/gm-remove_person.sql"

#==============================================================
# There really should not be any need to
# change anything below this line.
#==============================================================

TARGET_DB="$1"
PERSON_PK="$2"
END_TX="$3"
if test -z ${PERSON_PK} ; then
	echo "============================================================="
	echo "usage: $0 <target database> <person PK>"
	echo ""
	echo " <target database>: a GNUmed database (such as \"gnumed_v12\")"
	echo " <person PK>: primary key of a person in that database"
	echo "============================================================="
	exit 1
fi

if test -z ${END_TX} ; then
	END_TX="rollback"
fi

echo ""
echo "Creating removal script ..."
echo "    ${SQL_FILE}"

echo "" > $SQL_FILE

(
cat <<-EOF
	-- GNUmed person removal script
	-- \$Id: gm-remove_person.sh,v 1.2 2009-11-19 15:07:34 ncq Exp $

	\set ON_ERROR_STOP 1
	set default_transaction_read_only to off;

	begin;

	-- delete data
	delete from clin.lab_request where fk_encounter in (
	    select pk from clin.encounter where fk_patient = ${PERSON_PK}
	);


	-- delete episodes
	delete from clin.episode where fk_encounter in (
	    select pk from clin.encounter where fk_patient = ${PERSON_PK}
	);

	-- delete encounters
	delete from clin.encounter where fk_patient = ${PERSON_PK};

	-- delete names
	delete from dem.names where id_identity = ${PERSON_PK};

	-- delete identity
	alter table dem.identity disable rule r_del_identity;
	delete from dem.identity where pk = ${PERSON_PK};
	alter table dem.identity enable rule r_del_identity;

	${END_TX};
EOF
) >> $SQL_FILE


echo ""
echo "Are you sure you want to remove the person #${PERSON_PK}"
echo "irrevocably from the database \"${TARGET_DB}\" ?"
echo ""
read -e -p "Remove ? [yes / NO]:"
if test "$REPLY" == "yes"; then
	echo ""
	echo "Removing person #${PERSON_PK} from database \"${TARGET_DB}\" ..."
	LOG="gm-remove_person.log"

	psql -U gm-dbo -d ${TARGET_DB} -f ${SQL_FILE} &> ${LOG}
	if test $? -ne 0 ; then
		echo "ERROR: failed to remove person."
		echo "       see: ${LOG}"
		exit 1
	fi
fi

rm ${SQL_FILE}

#==============================================================
# $Log: gm-remove_person.sh,v $
# Revision 1.2  2009-11-19 15:07:34  ncq
# - bump db version
#
# Revision 1.1  2009/09/08 12:44:29  ncq
# - relocated from elsewhere
#
# Revision 1.2  2009/08/08 10:37:38  ncq
# - better docs
#
# Revision 1.1  2009/08/08 10:00:01  ncq
# - new
#
# Revision 1.3  2008/12/17 22:00:45  ncq
#