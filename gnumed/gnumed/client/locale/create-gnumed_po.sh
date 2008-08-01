#!/bin/bash

# - generate a current gnumed.pot file from GnuMed source
# - merge with existing translations
# - first arg should be ISO language code

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/locale/create-gnumed_po.sh,v $
# $Revision: 1.10 $

# what language are we working on
LANGNAME="$1"
if [ "${LANGNAME}" == "" ]; then
	echo "You must give an ISO language code as the first argument."
	exit
fi

# where to look for files
BASE="../"
# what to call the result
POTNAME="gnumed.pot"


echo ""
echo "Looking for translatable strings ..."
echo " source: ${BASE}*.py"
echo " target: ${POTNAME}"
find ${BASE} -follow -name '*.py' -print0 | xargs -0 pygettext --no-location -v -o ${POTNAME} "-" &> create-${LANGNAME}-po.log
#find ${BASE} -follow -name '*.py' -print0 | xargs -0 xgettext -L Python -j -o ${LANGNAME}.po "-" &> create-${LANGNAME}-po.log


if [ -f "${LANGNAME}.po" ]; then
	echo ""
	echo "Merging strings with previous translations ..."
	echo " current strings : ${POTNAME}"
	echo " old translations: ${LANGNAME}.po"
	msgmerge -v -o gnumed-${LANGNAME}.po ${LANGNAME}.po ${POTNAME} >> create-${LANGNAME}-po.log 2>&1
	mv -vf gnumed-${LANGNAME}.po ${LANGNAME}.po >> create-${LANGNAME}-po.log 2>&1
else
	cp -vf ${POTNAME} ${LANGNAME}.po >> create-${LANGNAME}-po.log 2>&1
fi;

echo ""
echo "Strings now ready for translation in file \"${LANGNAME}.po\" ..."
echo ""
