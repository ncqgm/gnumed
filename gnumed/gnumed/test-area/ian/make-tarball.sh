#!/bin/sh
# this is a script to generate gnumed client tarballs
# set $VERSION and $USER
VERSION=0.1
USER=ihaywood

cd $HOME
if [ ! -d my_gnumed ] ; then mkdir my_gnumed ; fi
cd my_gnumed
if [ -d gnumed-$VERSION ] ; then rm -R gnumed-$VERSION/ ; fi

# normally we should do this every time, but it takes so damn long
#if [ -d gnumed/ ] ; then rm -R gnumed/ ; fi
#cvs -d $USER@subversions.gnu.org:/cvsroot/gnumed export -D today gnumed

mkdir gnumed-$VERSION
cd gnumed-$VERSION
cp -R ../gnumed/README .
cp -R ../gnumed/gnumed/client/* .
find -name *~ -exec rm \{} \;
find -name *.pyc -exec rm \{} \;
cp ../gnumed/gnumed/test-area/ian/install.py .
chmod 755 install.py
mkdir man
mv doc/man-pages/gnumed.1 man
rmdir doc/man-pages

# this is the List of Shame. As modules get to a usable state they will be removed
cd wxpython
rm gmAppoint.py
cd ../business
rm gmForms.py # doesn't even byte-compile, how embarrassing
cd ../wxpython/patient
rm gmGP_FamilyHistory.py # ditto
rm gmGP_AnteNatal_3.py
rm gmGP_Measurements.py
rm gmGP_Prescriptions.py
rm gmGP_Recalls.py
rm gmGP_Referrals.py
rm gmGP_Requests.py

cd ../gui
rm gmplNbSchedule.py # ditto
rm gmDrugDisplay.py
rm gmGuidelines.py
rm gmOffice.py
rm gmSingleBoxSoapPlugin.py
rm gmPython.py
rm gmSQL.py

cd /home/ian/my_gnumed
tar cf gnumed-0.1.tar gnumed-0.1
if [ -f gnumed-0.1.tar.gz ] ; then rm gnumed-0.1.tar.gz ; fi
gzip -9 gnumed-0.1.tar


