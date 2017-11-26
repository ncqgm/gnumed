#/bin/sh

LANG_LIST="ar bg ca cs da de el en_AU en_CA es fr id it ka nb nl pl pt pt_BR ro ru ru_RU sq sr sv tr uk zh_TW"

for CURR_LANG in ${LANG_LIST} ; do

	./create-gnumed_po.sh ${CURR_LANG}
	./create-gnumed_mo.sh ${CURR_LANG}

done
