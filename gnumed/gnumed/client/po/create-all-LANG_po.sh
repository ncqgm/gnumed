#/bin/sh

LANG_LIST="ca de el en_CA es fr it nb nl pl pt pt_BR ru ru_RU sr sv"

for CURR_LANG in ${LANG_LIST} ; do

	./create-gnumed_po.sh ${CURR_LANG}
	./create-gnumed_mo.sh ${CURR_LANG}

done
