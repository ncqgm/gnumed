#!/bin/sh
#----------------------------------
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/dists/Archive/Attic/make-links.sh,v $
# $Revision: 1.4 $
# GPL
# Karsten.Hilbert@gmx.net
#----------------------------------
echo "setting up links for tgz creation"

#----------------------------------
echo "_____________"
echo "=> modules <="
echo "============="

mkdir -v modules
ln -vs ../../../client/python-common/gmLog.py modules/gmLog.py
ln -vs ../../../client/python-common/gmI18N.py modules/gmI18N.py
ln -vs ../../../client/python-common/gmCfg.py modules/gmCfg.py
ln -vs ../../../client/python-common/gmCLI.py modules/gmCLI.py
ln -vs ../../../client/python-common/gmPG.py modules/gmPG.py
ln -vs ../../../client/python-common/gmBackendListener.py modules/gmBackendListener.py
ln -vs ../../../client/python-common/gmDispatcher.py modules/gmDispatcher.py
ln -vs ../../../client/python-common/gmSignals.py modules/gmSignals.py
ln -vs ../../../client/python-common/gmLoginInfo.py modules/gmLoginInfo.py
ln -vs ../../../client/python-common/gmExceptions.py modules/gmExceptions.py
ln -vs ../../../client/python-common/gmMimeLib.py modules/gmMimeLib.py
ln -vs ../../../client/python-common/gmMimeMagic.py modules/gmMimeMagic.py

ln -vs ../../../client/business/gmTmpPatient.py modules/gmTmpPatient.py
ln -vs ../../../client/business/gmMedDoc.py modules/gmMedDoc.py
ln -vs ../../../client/business/gmXdtObjects.py modules/gmXdtObjects.py
ln -vs ../../../client/business/gmXdtMappings.py modules/gmXdtMappings.py

#----------------------------------
echo "____________"
echo "=> client <="
echo "============"

mkdir -v client
ln -vs ../modules client/modules

ln -vs ../../../client/wxpython/gui/gmShowMedDocs.py client/gmShowMedDocs.py
ln -vs ../viewer/run-viewer.sh client/run-viewer.sh
ln -vs ../viewer/run-viewer.bat client/run-viewer.bat

ln -vs ../docs/sample.conf client/sample.conf
ln -vs ../docs/README-client client/README

mkdir -vp client/locale/de_DE@euro/LC_MESSAGES
ln -vs ../../../../../../client/locale/de-gnumed.mo client/locale/de_DE@euro/LC_MESSAGES/gnumed.mo



#ln -vs ../../scan/gmScanMedDocs.py client/gmScanMedDocs.py
#ln -vs ~/.gnumed/gnumed-archive.conf client/gnumed-archive.conf
#ln -vs ../../import/import-med_docs.py client/import-med_docs.py
#ln -vs ../../index/index-med_docs.py client/index-med_docs.py
#ln -vs ../../import/run-importer.bat client/run-importer.bat
#ln -vs ../../import/run-importer.sh client/run-importer.sh
#ln -vs ../../import/remove-imported_dirs.sh client/remove-imported_dirs.sh
#ln -vs ../../index/run-indexer.bat client/run-indexer.bat
#ln -vs ../../index/run-indexer.sh client/run-indexer.sh
#ln -vs ../../scan/run-scanner.bat client/run-scanner.bat
#ln -vs ../../scan/run-scanner.sh client/run-scanner.sh

#mkdir client/doc
#ln -vs ../../../client/README client/doc/README
#ln -vs ../../../docs/README-GnuMed-Archiv-de.txt client/doc/README-GnuMed-Archiv-de.txt
#ln -vs ../../../docs/sample.conf client/doc/sample.conf
#ln -vs ../../../docs/TODO client/doc/TODO

#mkdir client/locale
#ln -vs ../../../locale/de_DE@euro client/locale/de_DE@euro

#echo "=> server"
#mkdir server
#ln -vs ~/.gnumed/gnumed-archive.conf server/gnumed-archive.conf
#ln -vs ../../server/install.sh server/install.sh
#ln -vs ../../server/bootstrap-archive.conf server/bootstrap-archive.conf
#ln -vs ../../server/README server/README
#ln -vs ../../server/gmArchiveAccounts.sql server/gmArchiveAccounts.sql
#ln -vs ../../import/import-med_docs.py server/import-med_docs.py
#ln -vs ../../import/remove-imported_dirs.sh server/remove-imported_dirs.sh
#ln -vs ../../import/run-importer.sh server/run-importer.sh
#ln -vs ../../modules server/modules
#ln -vs ../../../../server/utils/bootstrap-gm_db_system.py server/bootstrap-gm_db_system.py
#ln -vs ../../../../server/utils/bootstrap-archive.conf.sample server/bootstrap-archive.conf.sample
#ln -vs ../../../../server/sql server/sql
