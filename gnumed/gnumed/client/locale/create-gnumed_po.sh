#!/bin/bash

# - generate a current gnumed.pot file from GnuMed source
# - merge with existing translations
# - first arg should be ISO language code


BASE="../"							# where to look for files
POTNAME="gnumed.pot"				# what to call the result
LANGNAME="$1"						# what language are we working on


echo ""
echo "Looking for translatable strings ..."
echo " source: ${BASE}*.py"
echo " target: ${POTNAME}"


# create gnumed.pot
find ${BASE} -follow -name '*.py' -print0 | xargs -0 pygettext --no-location -v -o ${POTNAME} "-" &> create-${LANGNAME}-po.log
#find ${BASE} -follow -name '*.py' -print0 | xargs -0 xgettext -L Python -j -o ${LANGNAME}.po "-" &> create-${LANGNAME}-po.log


if [ "${LANGNAME}" == "" ]; then
	mv -f create-${LANGNAME}-po.log create-gnumed-pot.log
	exit
fi


# is there an additional file ?
if [ -f "${LANGNAME}-additional-translations.po" ]; then
	AUX_PO="-C ${LANGNAME}-additional-translations.po"
else
	AUX_PO=""
fi


if [ -f "${LANGNAME}.po" ]; then
	echo ""
	echo "Merging strings with old <${LANGNAME}> translations ..."
	echo ""
	echo " old translations:   ${LANGNAME}.po"
	TMP=`msgfmt -v -c --statistics -o tmp.pot ${LANGNAME}.po 2>&1`
	rm -f tmp.pot
	echo " old statistics:     ${TMP}"
	echo ""
	echo " references strings: ${AUX_PO}"
	echo " current strings:    ${POTNAME}"

	msgmerge -v -o gnumed-${LANGNAME}.po ${AUX_PO} ${LANGNAME}.po ${POTNAME} >> create-${LANGNAME}-po.log 2>&1
	mv -vf gnumed-${LANGNAME}.po ${LANGNAME}.po >> create-${LANGNAME}-po.log 2>&1
else
	cp -vf ${POTNAME} ${LANGNAME}.po >> create-${LANGNAME}-po.log 2>&1
fi;


echo ""
echo "Saving merged translations ..."
echo ""
echo " file :   ${LANGNAME}.po"
TMP=`msgfmt -v -c --statistics -o tmp.pot ${LANGNAME}.po 2>&1`
echo " stats: ${TMP}"
rm -f tmp.pot
