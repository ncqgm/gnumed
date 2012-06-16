#!/bin/bash

#==============================================================
# This script can be used to remove a person
# from a GNUmed database.
#
# author: Karsten Hilbert
# license: GPL v2 or later
#==============================================================

SQL_FILE="/tmp/gm-remove_person.sql"

#==============================================================
# There really should not be any need to
# change anything below this line.
#==============================================================

TARGET_DB="$1"
PERSON_PK="$2"

# You will need to understand what this does
# before exerting the power of setting it.
#
# You may want to start studying here:
#
#	http://en.wikipedia.org/wiki/Database_transaction
#
# Use the Source, Luke.
END_TX="$3"

if test -z ${PERSON_PK} ; then
	echo "============================================================="
	echo "usage: $0 <target database> <person PK>"
	echo ""
	echo " <target database>: a GNUmed database (such as \"gnumed_vNN\")"
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
	\set ON_ERROR_STOP 1
	set default_transaction_read_only to off;
	begin;
	select dem.remove_person(${PERSON_PK});
	${END_TX};
EOF
) >> $SQL_FILE


echo ""
echo "Are you sure you want to remove the person #${PERSON_PK}"
echo "*irrevocably* from the database \"${TARGET_DB}\" ?"
echo ""
read -e -p "Remove ? [yes / NO]: "
if test "$REPLY" == "yes"; then
	echo ""
	echo "Removing person #${PERSON_PK} from database \"${TARGET_DB}\" ..."
	LOG="gm-remove_person.log"

	psql -a -U gm-dbo -d ${TARGET_DB} -f ${SQL_FILE} &> ${LOG}
	if test $? -ne 0 ; then
		echo "ERROR: failed to remove person."
		echo "       see: ${LOG}"
		echo ""
		echo "-----------------------------------------------------"
		cat ${SQL_FILE} >> ${LOG}
		exit 1
	fi

	if test "${END_TX}" != "commit"; then
		echo ""
		echo "This test seems fine. You should be good to go for real."
		echo "Learn about END_TX from the source of this script at:"
		echo ""
		echo $0
		echo ""
	fi
fi

rm ${SQL_FILE}

#==============================================================
