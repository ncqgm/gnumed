#!/bin/sh
#this script compresses 1.6GB of data 
#on the CD into a compressed filesystem
#change the mount points/directories to match your system environment
mkisofs -R -U -V "KNOPPIX.net filesystem" -P "GNUmed www.gnumed.de" -hide-rr-moved -cache-inodes -no-bak -pad /mnt/hda4/source/KNOPPIX | nice -5 /usr/bin/create_compressed_fs - 65536 > /mnt/hda4/master/KNOPPIX/KNOPPIX
