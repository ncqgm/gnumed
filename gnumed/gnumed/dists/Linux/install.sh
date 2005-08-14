#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/dists/Linux/Attic/install.sh,v $
# $Id: install.sh,v 1.8 2005-08-14 16:44:29 shilbert Exp $
# $Revision: 1.8 $
# license: GPL
# sebastian.hilbert@gmx.net

# todo: 
# log install path for uninstall file
# log installation

# change this to match GNUmed version
REV=0.1

LOG="install-GNUmed-$REV.log"

echo "######################################################################################
#                                                                                    # 
# Welcome. You are about to install GNUmed. Please observe the output on the screen  #
# You will be prompted for target locations for GNUmed. The defaults provided give a #
# working setup on most systems and are considered safe. Your milage may vary.       #   
#                                                                                    #
#                                                      - GNUmed release team -       #
#                                                                                    #
######################################################################################"

echo "Installing GNUmed $REV ..." > $LOG

#mkdir -p /usr/lib/python/site-packages/Gnumed/ >> $LOG 2>&1
#mkdir -p /usr/share/doc/gnumed/client >> $LOG 2>&1
#mkdir -p /usr/lib/python/site-packages/Gnumed/exporters/ >> $LOG 2>&1
#mkdir -p /usr/lib/python/site-packages/Gnumed/importers/ >> $LOG 2>&1
#mkdir -p /etc/gnumed/ >> $LOG 2>&1
#mkdir -p /usr/lib/python/site-packages/Gnumed/ >> $LOG 2>&1
#mkdir -p /usr/share/gnumed/pixmaps/ >> $LOG 2>&1
#mkdir -p ./GNUmed-$REV/client/usr/share/locale/de/LC_MESSAGES/
#mkdir -p ./GNUmed-$REV/client/usr/share/locale/de_DE/LC_MESSAGES/
#mkdir -p ./GNUmed-$REV/client/usr/share/locale/fr/LC_MESSAGES/
#mkdir -p ./GNUmed-$REV/client/usr/share/locale/fr_FR/LC_MESSAGES/
#mkdir -p ./GNUmed-$REV/client/usr/share/locale/es/LC_MESSAGES/
#mkdir -p ./GNUmed-$REV/client/usr/share/locale/es_ES/LC_MESSAGES/

#####################################

dfltgmdir=/usr/share/gnumed
echo "client bitmap target directory [$dfltgmdir]:" 
read newgmdir
if [ "$newgmdir" = "" ]; then
	gmdir=$dfltgmdir
else
	gmdir=$newgmdir
fi
echo "GNUmed directory: $gmdir" >> $LOG 2>&1

mkdir -p $gmdir >> $LOG 2>&1
cp -R ./GNUmed-$REV/client/usr/share/gnumed/bitmaps $gmdir >> $LOG 2>&1
mkdir -p $gmdir/pixmaps >> $LOG 2>&1
cp -R ./GNUmed-$REV/client/usr/share/gnumed/pixmaps/gnumed.xpm $gmdir/pixmaps/gnumed.xpm >> $LOG 2>&1
#####################################
dfltpythondir=/usr/lib/python/site-packages/Gnumed
echo "python directory [$dfltpythondir]:" 
read newpythondir
if [ "$newpythondir" = "" ]; then
            pythondir=$dfltpythondir
else
            pythondir=$newpythondir
fi
echo "GNUmed Python directory: $pythondir" >> $LOG 2>&1

mkdir -p $pythondir/business >> $LOG 2>&1
cp -R ./GNUmed-$REV/client/usr/lib/python/site-packages/Gnumed/business $pythondir >> $LOG 2>&1
mkdir -p $pythondir/exporters >> $LOG 2>&1
cp -R ./GNUmed-$REV/client/usr/lib/python/site-packages/Gnumed/exporters/*.py $pythondir/exporters/ >> $LOG 2>&1
mkdir -p $pythondir/importers >> $LOG 2>&1
cp -R ./GNUmed-$REV/client/usr/lib/python/site-packages/Gnumed/importers/*.py $pythondir/importers/ >> $LOG 2>&1
cp -R ./GNUmed-$REV/client/usr/lib/python/site-packages/Gnumed/sitecustomize.py $pythondir >> $LOG 2>&1
mkdir -p $pythondir/pycommon >> $LOG 2>&1
cp -R ./GNUmed-$REV/client/usr/lib/python/site-packages/Gnumed/pycommon $pythondir >> $LOG 2>&1
mkdir -p $pythondir/wxpython >> $LOG 2>&1
cp -R ./GNUmed-$REV/client/usr/lib/python/site-packages/Gnumed/wxpython $pythondir >> $LOG 2>&1
cp -R ./GNUmed-$REV/client/usr/lib/python/site-packages/Gnumed/__init__.py $pythondir >> $LOG 2>&1

#######################################
dfltdocdir=/usr/share/doc/gnumed
echo "client documentation target directory [$dfltdocdir]:" 
read newdocdir
if [ "$newdocdir" = "" ]; then
            docdir=$dfltdocdir
else
            docdir=$newdocdir
fi
echo "GNUmed documentation directory: $docdir" >> $LOG 2>&1

mkdir -p $docdir/client >> $LOG 2>&1
mkdir -p $docdir/examples >> $LOG 2>&1
cp -R ./GNUmed-$REV/client/usr/share/doc/gnumed/client/user-manual $docdir/client >> $LOG 2>&1
cp -R ./GNUmed-$REV/client/usr/share/doc/gnumed/medical_knowledge $docdir >> $LOG 2>&1
cp -R ./GnuPublicLicense.txt $docdir >> $LOG 2>&1
cp -R ./GNUmed-$REV/client/etc/gnumed/*.conf $docdir/examples >> $LOG 2>&1

#######################################
dfltconfdir=/etc/gnumed
echo "client config files target directory [$dfltconfdir]:" 
read newconfdir
if [ "$newconfdir" = "" ]; then
            confdir=$dfltconfdir
else
            confdir=$newconfdir
fi
echo "GNUmed configuration directory: $confdir" >> $LOG 2>&1

mkdir -p $confdir >> $LOG 2>&1
cp -R ./GNUmed-$REV/client/etc/gnumed/*.conf $confdir >> $LOG 2>&1

#######################################
dfltlocaledir=/usr/share/locale
echo "client language files target directory [$dfltlocaledir]:" 
read newlocaledir
if [ "$newlocaledir" = "" ]; then
            localedir=$dfltlocaledir
else
            localedir=$newlocaledir
fi
echo "GNUmed locale directory: $localedir" >> $LOG 2>&1

mkdir $localedir >> $LOG 2>&1
cp -R ./GNUmed-$REV/client/usr/share/locale $localedir >> $LOG 2>&1
#######################################

cp -R ./GNUmed-$REV/client/usr/bin/gnumed /usr/bin >> $LOG 2>&1

# FIXME: put this some decent place
cp -R ./check-prerequisites.py $docdir >> $LOG 2>&1
cp -R ./check-prerequisites.sh $docdir >> $LOG 2>&1

echo "In case of problems there is a log file here:"
echo $LOG

#================================================
# $Log: install.sh,v $
# Revision 1.8  2005-08-14 16:44:29  shilbert
# - add cfg file examples to documentation directory
#
# Revision 1.7  2005/08/03 20:42:57  ncq
# - actually capture log output
#
# Revision 1.6  2005/07/18 19:35:25  shilbert
# - now respects user input for destination paths
#
# Revision 1.5  2005/07/16 10:57:34  shilbert
# - install user manual from wiki instead of old stuff in CVS
#
# Revision 1.4  2005/07/10 18:26:12  ncq
# - announce the log file at the end
#
# Revision 1.3  2005/07/10 18:24:48  ncq
# - log what we do into a log file
#
# Revision 1.2  2005/07/10 17:54:04  ncq
# - put check-* into doc dir for now
#
