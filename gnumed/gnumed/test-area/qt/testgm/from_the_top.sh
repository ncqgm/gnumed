QTBASE=/usr/lib/qt3/bin

$QTBASE/qmake -project
$QTBASE/qmake
sh patch_makefile.sh
make
sh create_testgm.sh
