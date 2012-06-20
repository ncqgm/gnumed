#!/bin/bash

POFILES=$@
for POFILE in ${POFILES} ; do
	msgfmt -v -c --statistics ${POFILE}
done
