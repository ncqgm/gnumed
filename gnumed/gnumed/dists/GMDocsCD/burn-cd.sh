#!/bin/sh

BURN="/usr/local/bin/cdrecord"

echo "burning ISO file $1 onto CD"
$BURN -v gracetime=4 dev=/dev/hdc speed=8 -tao driveropts=burnfree -eject -overburn -data $1
