#needs cygtools ipc-daemon. This is in cygwin net install chooser.
#change this to your pgdata directory
DATADIR=/home/syan/pgdata

ipcclean.exe
ipc-daemon.exe &

rm $DATADIR/postmaster.pid

echo pg_ctl start -D $DATADIR  -o -i | sh





