#!/bin/bash

# - generate a gnumed.mo file from a translated $LANG.po file
# - first arg should be ISO language code

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
msgfmt -v -c --statistics -o ${MOFILE} ${POFILE}


echo ""
echo "activating translation ${LANGNAME}"
mkdir ${LANGNAME}
cd ${LANGNAME}
mkdir LC_MESSAGES
cd LC_MESSAGES
ln -s ../../${MOFILE} gnumed.mo
cd ../../
echo ""
