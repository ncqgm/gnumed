#!/bin/sh

# - generate a current gnumed.pot file from GnuMed source
# - merge with existing translations
# - first arg should be ISO language code

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/locale/create-gnumed_po.sh,v $
# $Revision: 1.7 $

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

echo "harvesting python source files in ${BASE} into the file ${POTNAME}"
find ${BASE} -follow -name '*.py' -print0 | xargs -0 pygettext --no-location -v -o ${POTNAME} "-" &> create-${LANGNAME}-po.log
#find ${BASE} -follow -name '*.py' -print0 | xargs -0 xgettext -L Python -j -o ${LANGNAME}.po "-" &> create-${LANGNAME}-po.log

echo "merging current source strings (${POTNAME}) with old translations (${LANGNAME}.po)"
if [ -f "${LANGNAME}.po" ]; then
	msgmerge -v -o gnumed-${LANGNAME}.po ${LANGNAME}.po ${POTNAME} >> create-${LANGNAME}-po.log 2>&1
	mv -vf gnumed-${LANGNAME}.po ${LANGNAME}.po
	#rm -vf ${POTNAME}
else
	cp -vf ${POTNAME} ${LANGNAME}.po
fi;

echo "you can now translate messages in ${LANGNAME}.po"
