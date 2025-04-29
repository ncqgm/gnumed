#!/bin/bash

POFILES=$@
for POFILE in ${POFILES} ; do
	msgfmt --verbose --check --check-accelerators --statistics ${POFILE}
done
