#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/blobs_hilbert/dist/Attic/make-links.sh,v $
# $Revision: 1.3 $
# GPL
# Karsten.Hilbert@gmx.net

echo "setting up links for tgz creation"

echo "=> client"
mkdir client
ln -vfs ../../scan/gmScanMedDocs.py client/gmScanMedDocs.py
ln -vfs ~/.gnumed/gnumed-archive.conf client/gnumed-archive.conf
ln -vfs ../../import/import-med_docs.py client/import-med_docs.py
ln -vfs ../../index/index-med_docs.py client/index-med_docs.py
ln -vfs ../../import/run-importer.bat client/run-importer.bat
ln -vfs ../../import/run-importer.sh client/run-importer.sh
ln -vfs ../../import/remove-imported_dirs.sh client/remove-imported_dirs.sh
ln -vfs ../../index/run-indexer.bat client/run-indexer.bat
ln -vfs ../../index/run-indexer.sh client/run-indexer.sh
ln -vfs ../../scan/run-scanner.bat client/run-scanner.bat
ln -vfs ../../scan/run-scanner.sh client/run-scanner.sh
ln -vfs ../../viewer-tree/run-viewer.bat client/run-viewer.bat
ln -vfs ../../viewer-tree/run-viewer.sh client/run-viewer.sh
ln -vfs ../../viewer-tree/show-med_docs.py client/show-med_docs.py
ln -vfs ../../modules client/modules

mkdir client/doc
ln -vfs ../../../client/README client/doc/README
ln -vfs ../../../docs/README-GnuMed-Archiv-de.txt client/doc/README-GnuMed-Archiv-de.txt
ln -vfs ../../../docs/sample.conf client/doc/sample.conf
ln -vfs ../../../docs/TODO client/doc/TODO

mkdir client/locale
ln -vfs ../../../locale/de_DE@euro client/locale/de_DE@euro

echo "=> server"
mkdir server
ln -vfs ../../server/bootstrap-gm_db_system.conf server/bootstrap-gm_db_system.conf
ln -vfs ../../../../server/utils/bootstrap-gm_db_system.py server/bootstrap-gm_db_system.py
ln -vfs ../../../../server/sql/country.specific/de/german-doc_types.sql server/german-doc_types.sql
ln -vfs ../../../../server/sql/gmBlobs.sql server/gmBlobs.sql
ln -vfs ../../../../server/sql/gmconfiguration.sql server/gmconfiguration.sql
ln -vfs ../../../../server/sql/gmgis.sql server/gmgis.sql
ln -vfs ../../../../server/sql/gmidentity.sql server/gmidentity.sql
ln -vfs ../../../../server/sql/gmSchemaRevision.sql server/gmSchemaRevision.sql
ln -vfs ../../../../server/utils/gmUserSetup.py server/gmUserSetup.py
ln -vfs ~/.gnumed/gnumed-archive.conf server/gnumed-archive.conf
ln -vfs ../../import/import-med_docs.py server/import-med_docs.py
ln -vfs ../../import/remove-imported_dirs.sh client/remove-imported_dirs.sh
ln -vfs ../../server/install.sh server/install.sh
ln -vfs ../../modules server/modules
ln -vfs ../../server/README server/README
ln -vfs ../../import/run-importer.sh server/run-importer.sh
ln -vfs ../../../../server/utils/setup-local_users.conf.sample server/setup-local_users.conf.sample
