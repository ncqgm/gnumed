#/bin/sh

LANG_LIST="ca de el es fr it nb nl pl pt pt_BR ru"

for CURR_LANG in ${LANG_LIST} ; do

	./create-gnumed_po.sh ${CURR_LANG}
	./create-gnumed_mo.sh ${CURR_LANG}

done
