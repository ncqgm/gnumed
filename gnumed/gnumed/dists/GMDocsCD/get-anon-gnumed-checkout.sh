#!/bin/sh

echo "anonymously checking out a fresh copy of the gnumed cvs tree"
CVS_RSH="ssh"
cvs -z9 -d:ext:anoncvs@subversions.gnu.org:/cvsroot/gnumed co -P gnumed
