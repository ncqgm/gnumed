#! /bin/bash -x

# original script found at http://www.geocities.com/ted_johnson2/knoppix.txt
# Set up filesystem mount points.
# /dev/hda1 is swap of 4096MB
# /dev/hda2 is ext2 fs of 4096MB
# /dev/hda3 is ext2 fs of 8192MB
#
# All of these need to be created ahead of time
# or edit the lines below to adjust to your FS
# layout.  Do not run this until you resolve all the
# fs layout settings.  You have been warned.

SWAP=/dev/hdc1; export SWAP
SOURCE=/dev/hdc2; export SOURCE
DEST=/dev/hdc3; export DEST

umount $SOURCE
umount $DEST

mke2fs $SOURCE
mke2fs $DEST

mkswap $SWAP
swapon $SWAP

rm -rf /mnt/source
rm -rf /mnt/master

mkdir /mnt/source
mount $SOURCE /mnt/source

mkdir /mnt/master
mount $DEST /mnt/master

mkdir /mnt/source/KNOPPIX/

# Begin copying the disk to the work directory.

cp -Rp /KNOPPIX/* /mnt/source/KNOPPIX/
cp -Rp /cdrom/* /mnt/master/

# If you changed the desktop to something more usable than the
# HORRIBLE default settings, your new settings will be copied.

#cp -Rp /home/knoppix/* /mnt/source/KNOPPIX/etc/skel/
#cp -Rp /home/knoppix/.kde/* /mnt/source/KNOPPIX/etc/skel/
#cp -Rp /home/knoppix/.kde/share/* /mnt/source/KNOPPIX/etc/skel/.kde/share/

# Remove some stuff.

rm /mnt/master/KNOPPIX/KNOPPIX
rm /mnt/master/KNOPPIX/boot.cat

# stop here so I can configure the system files that were on the read
# only fs - now they are in /mnt/source/KNOPPIX

echo "Going to chroot now. Press Ctrl-d to exit."
echo "Run 
mount -t proc /proc proc also 
vi /etc/resolv.conf and /etc/apt/sources.list (if u want to add local mirrors) then do 
apt-get update etc..."

chroot /mnt/source/KNOPPIX
#echo "Go fix stuff."
exit 0
