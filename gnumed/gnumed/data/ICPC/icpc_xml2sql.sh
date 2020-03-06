#/bin/sh

xml2 < sdicpc.xml | grep '^/stammdatei/body/ICPC_liste/ICPC_stammsatz/.*/@V=.*$' | sed -e "s/'Infektion der/Infektion der/" > sdicpc.flat
rm -v v15-*.sql
python3 ./icpc_flat2sql.py sdicpc.flat

rm -v sdicpc.flat
