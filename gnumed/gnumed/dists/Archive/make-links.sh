#!/bin/sh
#----------------------------------
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/dists/Archive/Attic/make-links.sh,v $
# $Revision: 1.2 $
# GPL
# Karsten.Hilbert@gmx.net
#----------------------------------
echo "setting up links for tgz creation"

#----------------------------------
echo "_____________"
echo "=> modules <="
echo "============="

mkdir -v modules
ln -vfs ../../../client/python-common/gmLog.py modules/gmLog.py
ln -vfs ../../../client/python-common/gmI18N.py modules/gmI18N.py
ln -vfs ../../../client/python-common/gmCfg.py modules/gmCfg.py
ln -vfs ../../../client/python-common/gmCLI.py modules/gmCLI.py
ln -vfs ../../../client/python-common/gmPG.py modules/gmPG.py
ln -vfs ../../../client/python-common/gmBackendListener.py modules/gmBackendListener.py
ln -vfs ../../../client/python-common/gmDispatcher.py modules/gmDispatcher.py
ln -vfs ../../../client/python-common/gmSignals.py modules/gmSignals.py
ln -vfs ../../../client/python-common/gmLoginInfo.py modules/gmLoginInfo.py
ln -vfs ../../../client/python-common/gmExceptions.py modules/gmExceptions.py
ln -vfs ../../../client/python-common/gmMimeLib.py modules/gmMimeLib.py
ln -vfs ../../../client/python-common/gmMimeMagic.py modules/gmMimeMagic.py

ln -vfs ../../../client/business/gmTmpPatient.py modules/gmTmpPatient.py
ln -vfs ../../../client/business/gmMedDoc.py modules/gmMedDoc.py
ln -vfs ../../../client/business/gmXdtObjects.py modules/gmXdtObjects.py
ln -vfs ../../../client/business/gmXdtMappings.py modules/gmXdtMappings.py

#----------------------------------
echo "____________"
echo "=> client <="
echo "============"

ln -vfs ../modules client/modules

ln -vfs ../../../client/wxpython/gui/gmShowMedDocs.py client/gmShowMedDocs.py
ln -vfs ../viewer/run-viewer.sh client/run-viewer.sh
ln -vfs ../viewer/run-viewer.bat client/run-viewer.bat

ln -vfs ../docs/sample.conf client/sample.conf
ln -vfs ../docs/README-client client/README

#ln -vfs ../../scan/gmScanMedDocs.py client/gmScanMedDocs.py
#ln -vfs ~/.gnumed/gnumed-archive.conf client/gnumed-archive.conf
#ln -vfs ../../import/import-med_docs.py client/import-med_docs.py
#ln -vfs ../../index/index-med_docs.py client/index-med_docs.py
#ln -vfs ../../import/run-importer.bat client/run-importer.bat
#ln -vfs ../../import/run-importer.sh client/run-importer.sh
#ln -vfs ../../import/remove-imported_dirs.sh client/remove-imported_dirs.sh
#ln -vfs ../../index/run-indexer.bat client/run-indexer.bat
#ln -vfs ../../index/run-indexer.sh client/run-indexer.sh
#ln -vfs ../../scan/run-scanner.bat client/run-scanner.bat
#ln -vfs ../../scan/run-scanner.sh client/run-scanner.sh

#mkdir client/doc
#ln -vfs ../../../client/README client/doc/README
#ln -vfs ../../../docs/README-GnuMed-Archiv-de.txt client/doc/README-GnuMed-Archiv-de.txt
#ln -vfs ../../../docs/sample.conf client/doc/sample.conf
#ln -vfs ../../../docs/TODO client/doc/TODO

#mkdir client/locale
#ln -vfs ../../../locale/de_DE@euro client/locale/de_DE@euro

#echo "=> server"
#mkdir server
#ln -vfs ~/.gnumed/gnumed-archive.conf server/gnumed-archive.conf
#ln -vfs ../../server/install.sh server/install.sh
#ln -vfs ../../server/bootstrap-archive.conf server/bootstrap-archive.conf
#ln -vfs ../../server/README server/README
#ln -vfs ../../server/gmArchiveAccounts.sql server/gmArchiveAccounts.sql
#ln -vfs ../../import/import-med_docs.py server/import-med_docs.py
#ln -vfs ../../import/remove-imported_dirs.sh server/remove-imported_dirs.sh
#ln -vfs ../../import/run-importer.sh server/run-importer.sh
#ln -vfs ../../modules server/modules
#ln -vfs ../../../../server/utils/bootstrap-gm_db_system.py server/bootstrap-gm_db_system.py
#ln -vfs ../../../../server/utils/bootstrap-archive.conf.sample server/bootstrap-archive.conf.sample
#ln -vfs ../../../../server/sql server/sql
