# Start new file here. Call it something else.
#
# Why does the process hang on the /mnt directory as
# well as the .gnome-desktop directory?  I don't know -
# so I remove them for now.

#rm -rf /mnt/source/KNOPPIX/mnt/*
#rm -rf /mnt/source/KNOPPIX/home/*
#rm -rf /mnt/source/KNOPPIX/etc/skel/.gnome-desktop
find /mnt -name *.ogg | xargs rm

# remove cached apps - need to do this when chrooted
#apt-get clean
#updatedb

# Make the disk. Notice I don't pipe the output directly - that failed on me a few times....

mkisofs  -R -L -allow-multidot -l -V "KNOPPIX iso9660 filesystem" -o /mnt/master/knoppix.iso -hide-rr-moved -v /mnt/source/KNOPPIX
create_compressed_fs /mnt/master/knoppix.iso  65536 > /mnt/master/KNOPPIX/KNOPPIX

# Clean up a bit.
#rm -rf /mnt/source/*
rm -rf /mnt/master/knoppix.iso

# Make the final .iso image.
mkisofs -l -r -J -V "knoppix-debian-med" -hide-rr-moved -v -b KNOPPIX/boot-en.img -c KNOPPIX/boot.cat -o /mnt/source/knoppix_cd.iso /mnt/master
