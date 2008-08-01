#!/bin/bash

# - generate a gnumed.mo file from a translated $LANG.po file
# - first arg should be ISO language code

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/locale/create-gnumed_mo.sh,v $
# $Revision: 1.4 $

# what language are we working on
LANGNAME="$1"
if [ "${LANGNAME}" == "" ]; then
	echo "You must give an ISO language code as the first argument."
	exit
fi

MOFILE="${LANGNAME}-gnumed.mo"
POFILE="${LANGNAME}.po"


echo ""
echo "compiling translation for GNUmed"
echo " target language      : ${LANGNAME}"
echo " raw translations     : ${POFILE}"
echo " compiled translations: ${MOFILE}"
echo ""
msgfmt -v --statistics -o ${MOFILE} ${POFILE}


echo ""
echo "You can now copy \"${MOFILE}\" into the appropriate"
echo "language specific directory (such as ./${LANGNAME}/LC_MESSAGES/)."
echo ""
