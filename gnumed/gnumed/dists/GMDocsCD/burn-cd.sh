#!/bin/sh

echo "burning ISO file $1 onto CD"
/usr/local/bin/cdrecord -v gracetime=4 dev=/dev/hdc speed=8 -tao driveropts=burnfree -eject -overburn -data $1
