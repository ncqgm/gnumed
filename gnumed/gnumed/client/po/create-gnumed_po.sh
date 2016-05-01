#!/bin/bash

# - generate a current gnumed.pot file from GNUmed source
# - merge with existing translations
# - first arg should be ISO language code


BASE="../"												# where to look for files
POTNAME="gnumed.pot"									# what to call the result
LANGNAME="$1"											# what language are we working on
AUXNAME="additional-translations/${LANGNAME}.po"


echo ""
echo "Collecting translatable strings ..."
echo "  source file definition: ${BASE}*.py"


# create gnumed.pot
find ${BASE} -follow -name '*.py' -print0 | xargs -0 xgettext -L Python --foreign-user --no-location -o ${POTNAME} "-" &> create-${LANGNAME}-po.log


if [ "${LANGNAME}" == "" ]; then
	mv -f create-${LANGNAME}-po.log create-gnumed-pot.log
	exit
fi


# is there an additional file ?
if [ -f "${AUXNAME}" ]; then
	AUX_PO_ARG="-C ${AUXNAME}"
else
	AUX_PO_ARG=""
fi


if [ -f "${LANGNAME}.po" ]; then
	echo ""
	echo "Merging translatable strings with existing translations for <${LANGNAME}> ..."
	echo ""
	echo "    translatable strings: ${POTNAME}"
	echo ""
	echo "        old translations: ${LANGNAME}.po"
	TMP=`msgfmt -v --check-header --check-domain --check-accelerators --statistics -o tmp.pot ${LANGNAME}.po 2>&1`
	rm -f tmp.pot
	echo "              statistics: ${TMP}"

	if [ -f "${AUXNAME}" ]; then
		echo ""
		echo " additional translations: ${AUXNAME}"
		TMP=`msgfmt -v --check-header --check-domain --check-accelerators --statistics -o tmp.pot ${AUXNAME} 2>&1`
		rm -f tmp.pot
		echo "              statistics: ${TMP}"
	fi

	msgmerge -v -o gnumed-${LANGNAME}.po ${AUX_PO_ARG} ${LANGNAME}.po ${POTNAME} >> create-${LANGNAME}-po.log 2>&1
	mv -vf gnumed-${LANGNAME}.po ${LANGNAME}.po >> create-${LANGNAME}-po.log 2>&1
else
	cp -vf ${POTNAME} ${LANGNAME}.po >> create-${LANGNAME}-po.log 2>&1
fi;


if [ -f "${AUXNAME}" ]; then
	mv -vf ${AUXNAME} ${AUXNAME}.done >> create-${LANGNAME}-po.log 2>&1
fi;


echo ""
echo "  final translation file: ${LANGNAME}.po"
TMP=`msgfmt -v --check-header --check-domain --check-accelerators --statistics -o tmp.pot ${LANGNAME}.po 2>&1`
echo "              statistics: ${TMP}"
rm -f tmp.pot
echo ""
