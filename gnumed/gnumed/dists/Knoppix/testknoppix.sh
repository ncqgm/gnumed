#next two lines use one of my scripts to mount hdc2 and hdc3
export SOURCE=hdc2
export MASTER=hdc3


if test ! -d /mnt/source
then
	mkdir /mnt/source
fi

if test ! -d /mnt/master
then
	mkdir /mnt/master
fi

mount /dev/$SOURCE /mnt/source
mount /dev/$SOURCE /mnt/master

if test -d /mnt/source/KNOPPIX
then
# because knoppix boot floppy may incorrectly use this to boot
	mv /mnt/source/KNOPPIX /mnt/source/sourceknoppix
fi

#backup previous iso - dont really need to
mv /mnt/master/knoppix.iso /mnt/master/knoppix.iso.old

#make an iso
mkisofs  -R -L -allow-multidot -l -V "KNOPPIX iso9660 filesystem" -o /mnt/master/knoppix.iso -hide-rr-moved -v /mnt/source/sourceknoppix

ls -l /mnt/master/knoppix.iso

echo "Now trying to compress: the Maximum file size that knoppix.iso should be is somewhere between 2062500KB (works) and 2125000KB (doesnt work)."

#now compress it
create_compressed_fs /mnt/master/knoppix.iso  65536 > /mnt/master/KNOPPIX/KNOPPIX

echo If it compressed fine.. you are probably hearing an excessive amount of disk activity and its time to put your knoppix boot floppy in and restart

