#!/bin/sh

MKISO="/opt/schily/bin/mkisofs"
MKISOOPTS="-graft-points -sysid LINUX -volset-size 1 -volset-seqno 1 -rational-rock -full-iso9660-filenames -disable-deep-relocation -iso-level 2"

ISO="gnumed.iso"
FILES2BURN="./gnumed ./salaam.homeunix.com ./backblue.gif ./external.html ./fade.gif index.htm autorun.pif autorun.bat autorun.inf cdrom.ico get-anon-gnumed-checkout.sh get-api-doc.sh get-latest-snapshot.sh get-schema-doc.sh get-wiki.sh"

rm hts-log.txt
rm hts-nohup.txt
rm $ISO
$MKISO $MKISOOPTS -o $ISO $FILES2BURN
