#!/bin/sh

MKISO="/opt/schily/bin/mkisofs"
MKISOOPTS="-x ./hts-cache -m '*.sh' -x ./index.html -L -l -r -v"
#" -graft-points -sysid LINUX -volset-size 1 -volset-seqno 1 -rational-rock -full-iso9660-filenames -disable-deep-relocation -iso-level 2"
ISO="gnumed.iso"

rm hts-log.txt
rm hts-nohup.txt
rm $ISO
$MKISO $MKISOOPTS -o $ISO ./
