#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/blobs_hilbert/dist/Attic/make-dists.sh,v $
# $Revision: 1.2 $
# GPL
# Karsten.Hilbert@gmx.net

echo "=> client ..."
tar -cvhzf gnumed-archive-client.tgz client

echo "=> server ..."
tar -cvhzf gnumed-archive-server.tgz server

tar -cvzf gnumed-archive.tgz gnumed-archive-client.tgz gnumed-archive-server.tgz
