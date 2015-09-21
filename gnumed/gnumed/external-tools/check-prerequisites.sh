#!/bin/bash

echo "-------------------------------------------------------------"
echo "This script will check your environment for applications"
echo "and services the GNUmed client depends on."
echo ""
echo "Please make sure to also read the INSTALL and README files."
echo "-------------------------------------------------------------"

ME=`basename $0`
if test ! -e ./${ME} ; then
	echo ""
	echo "NOTE: Run this script from the directory it is in or it might fail !"
	echo ""
	read -p "Press [ENTER] to continue anyway."
fi

echo ""
echo "You need to be able to connect to a PostgreSQL"
echo "server. It is, however, non-trivial to reliably"
echo "test for that."
echo "If you want to work with a *local* database (on this"
echo "machine) you should see at least one process saying"
echo "'postgres' in the following list."
echo "If you don't you can still use our public database"
echo "at publicdb.gnumed.de for testing or connect to a"
echo "GNUmed database installed on another machine."
echo ""
echo "Process list:"
echo "-------------------------------------------------------------------------"
ps axww | grep postgr | grep -v "grep"
echo "-------------------------------------------------------------------------"
echo ""

echo "=> checking for Python interpreter ..."
PYBIN=`which python`
if [ "x${PYBIN}x" == "xx" ]; then
	echo "ERROR: You don't have Python installed."
	echo "ERROR: Python is available with your OS or from www.python.org"
else
	echo "=> found"
	echo -n "   ${PYBIN}: "
	python --version
fi

# make sure we can locally find the Python modules
# when running from a copy of the CVS tree
#cd gnumed
cd ..
ln -sT client Gnumed &> /dev/null

echo ""
read -p "Press <RETURN> key to continue."
echo    "-------------------------------"

${PYBIN} external-tools/check-prerequisites.py

cd -

echo ""
echo "-------------------------------------------------"
echo "I will now check for a few utilities which"
echo "make working with GNUmed more productive but"
echo "are not strictly required for standard operation."
read -p "Press <RETURN> key to continue."
echo    "-------------------------------"

echo -n " 'file' command... "
BIN=`which file`
if [ "x${BIN}x" == "xx" ]; then
	echo ""
	echo "  INFO : You don't seem to have the 'file' command installed."
	echo "  INFO : It is available with your OS. On Windows it is not needed."
else
	echo "found"
fi

echo -n " 'extract' command... "
BIN=`which extract`
if [ "x${BIN}x" == "xx" ]; then
	echo ""
	echo "  INFO : You don't seem to have the 'extract' command installed."
	echo "  INFO : It is available with your OS. On Windows it is not needed."
else
	echo "found"
fi


echo -n " 'Ginkgo CADx' DICOM viewer... "
BIN=`which ginkgocadx`
if [ "x${BIN}x" == "xx" ]; then
	echo ""
	echo "  INFO : You don't seem to have the 'ginkgocadx' command installed."
	echo "  INFO : This is the recommended DICOM viewer."
else
	echo "found"
fi


echo -n " 'Aeskulap' DICOM viewer... "
BIN=`which aeskulap`
if [ "x${BIN}x" == "xx" ]; then
	echo ""
	echo "  INFO : You don't seem to have the 'aeskulap' command installed."
	echo "  INFO : It is available with your OS. On Windows it is not needed."
else
	echo "found"
fi

echo -n " 'AMIDE' DICOM viewer... "
BIN=`which amide`
if [ "x${BIN}x" == "xx" ]; then
	echo ""
	echo "  INFO : You don't seem to have the 'amide' command installed."
	echo "  INFO : It is available with your OS. On Windows it is not needed."
else
	echo "found"
fi

echo -n " 'XMedCon' DICOM viewer... "
BIN=`which xmedcon`
if [ "x${BIN}x" == "xx" ]; then
	echo ""
	echo "  INFO : You don't seem to have the 'xmedcon' command installed."
	echo "  INFO : It is available with your OS. On Windows it is not needed."
else
	echo "found"
fi

echo -n " 'XSane' scanner frontend... "
BIN=`which xsane`
if [ "x${BIN}x" == "xx" ]; then
	echo ""
	echo "  INFO : You don't seem to have the 'xsane' command installed."
	echo "  INFO : It is available with your OS. On Windows it is not needed."
else
	echo "found"
fi

echo -n " 'aspell' spell checker... "
BIN=`which aspell`
if [ "x${BIN}x" == "xx" ]; then
	echo ""
	echo "  INFO : You don't seem to have the 'aspell' command installed."
	echo "  INFO : It is available with your OS."
else
	echo "found"
fi

echo -n " 'konsolekalender' KOrganizer controller... "
BIN=`which konsolekalendar`
if [ "x${BIN}x" == "xx" ]; then
	echo ""
	echo "  INFO : You don't seem to have the 'konsolekalendar' command installed."
	echo "  INFO : It is available with your OS."
else
	echo "found"
fi

echo -n " 'gnuplot' command... "
BIN=`which gnuplot`
if [ "x${BIN}x" == "xx" ]; then
	echo ""
	echo "  INFO : You don't seem to have the 'gnuplot' command installed."
	echo "  INFO : It is available with your OS or can be downloaded from the web."
else
	echo "found"
fi

echo -n " 'pdflatex' command... "
BIN=`which pdflatex`
if [ "x${BIN}x" == "xx" ]; then
	echo ""
	echo "  INFO : You don't seem to have the 'pdflatex' command installed."
	echo "  INFO : It is used to turn form templates into printable PDFs."
else
	echo "found"
fi

echo -n " 'kprinter4' command... "
BIN=`which kprinter4`
if [ "x${BIN}x" == "xx" ]; then
	echo ""
	echo "  INFO : You don't seem to have the 'kprinter' command installed."
	echo "  INFO : It is used to print files from KDE."
	echo "  INFO : On Windows it is not needed."
else
	echo "found"
fi

echo -n " 'pdf2ps' command... "
BIN=`which kprinter4`
if [ "x${BIN}x" == "xx" ]; then
	echo ""
	echo "  INFO : You don't seem to have the 'pdf2ps' command installed."
	echo "  INFO : It is used to print files from KDE."
	echo "  INFO : On Windows it is not needed."
else
	echo "found"
fi

echo -n " 'gtklp' command... "
BIN=`which gtklp`
if [ "x${BIN}x" == "xx" ]; then
	echo ""
	echo "  INFO : You don't seem to have the 'gktlp' command installed."
	echo "  INFO : It is used to print files from GNOME."
	echo "  INFO : On Windows it is not needed."
else
	echo "found"
fi

echo -n " 'convert' command... "
BIN=`which convert`
if [ "x${BIN}x" == "xx" ]; then
	echo ""
	echo "  INFO : You don't seem to have the 'convert' command installed."
	echo "  INFO : It comes with the ImageMagick package and is used"
	echo "  INFO : to convert files from one format into another."
else
	echo "found"
fi

echo -n " 'gpg' command... "
BIN=`which gpg`
if [ "x${BIN}x" == "xx" ]; then
	echo ""
	echo "  INFO : You don't seem to have the 'gpg' command installed."
	echo "  INFO : It comes with the GNU Privacy Guard (GnuPG) package"
	echo "  INFO : and is used to decrypt files and data."
else
	echo "found"
fi

echo -n " 'gm-print_doc' command... "
BIN=`which gm-print_doc`
if [ "x${BIN}x" == "xx" ]; then
	echo ""
	echo "  INFO : You don't seem to have the 'gm-print_doc' command installed."
	echo "  INFO : It is used to print files from GNUmed."
else
	echo "found"
fi

echo -n " 'gm-fax_doc' command... "
BIN=`which gm-fax_doc`
if [ "x${BIN}x" == "xx" ]; then
	echo ""
	echo "  INFO : You don't seem to have the 'gm-fax_doc' command installed."
	echo "  INFO : It is used to fax files from GNUmed."
else
	echo "found"
fi

echo -n " 'gm-mail_doc' command... "
BIN=`which gm-mail_doc`
if [ "x${BIN}x" == "xx" ]; then
	echo ""
	echo "  INFO : You don't seem to have the 'gm-mail_doc' command installed."
	echo "  INFO : It is used to e-mail files from GNUmed."
else
	echo "found"
fi

echo -n " 'gm-burn_doc' command... "
BIN=`which gm-burn_doc`
if [ "x${BIN}x" == "xx" ]; then
	echo ""
	echo "  INFO : You don't seem to have the 'gm-burn_doc' command installed."
	echo "  INFO : It is used to burn to disk an ISO image of files from GNUmed."
else
	echo "found"
fi

echo -n " 'gm-convert_file' command... "
BIN=`which gm-convert_file`
if [ "x${BIN}x" == "xx" ]; then
	echo ""
	echo "  INFO : You don't seem to have the 'gm-convert_file' command installed."
	echo "  INFO : It is used to convert files between formats from within GNUmed."
else
	echo "found"
fi

echo -n " 'gm-create_datamatrix' command... "
BIN=`which gm-create_datamatrix`
if [ "x${BIN}x" == "xx" ]; then
	echo ""
	echo "  INFO : You don't seem to have the 'gm-create_datamatrix' command installed."
	echo "  INFO : It is used to create data matrix barcodes from within GNUmed."
else
	echo "found"
fi

echo -n " 'gm-create_dicomdir' command... "
BIN=`which gm-create_dicomdir`
if [ "x${BIN}x" == "xx" ]; then
	echo ""
	echo "  INFO : You don't seem to have the 'gm-create_dicomdir' command installed."
	echo "  INFO : It is used to create DICOMDIR files from within GNUmed."
else
	echo "found"
fi

# obsolete
#echo -n " 'gm-download_data' command... "
#BIN=`which gm-download_data`
#if [ "x${BIN}x" == "xx" ]; then
#	echo ""
#	echo "  INFO : You don't seem to have the 'gm-download_data' command installed."
#	echo "  INFO : It is used to download data files from within GNUmed."
#else
#	echo "found"
#fi

#=================================================================
