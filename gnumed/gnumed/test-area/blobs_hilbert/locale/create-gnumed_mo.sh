#!/bin/sh

# - generate a gnumed.mo file from a translated $LANG.po file
# - first arg should be ISO language code

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/blobs_hilbert/locale/Attic/create-gnumed_mo.sh,v $
# $Revision: 1.1 $

# what language are we working on
LANGNAME="$1"
if [ "${LANGNAME}" == "" ]; then
	echo "You must give an ISO language code as the first argument."
	exit
fi

MOFILE="${LANGNAME}-gnumed-archiv.mo"
POFILE="${LANGNAME}.po"

echo "generating gnumed-archiv.mo for language ${LANGNAME}"
msgfmt -v --statistics -o ${MOFILE} ${POFILE}

echo "You can now copy ${MOFILE} into the appropriate language"
echo "specific directory (such as ./${LANGNAME}/LC_MESSAGES/)."
