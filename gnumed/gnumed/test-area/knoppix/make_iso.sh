#!/bin/sh
# this script creates an ISO-CD-image which is bootable
# adapt the directories mentioned to match your system environment
mkisofs -pad -l -r -J -v -V "KNOPPIX" -b KNOPPIX/boot.img -c KNOPPIX/boot.cat -hide-rr-moved -o /mnt/hda4/knoppix.iso /mnt/hda4/master
