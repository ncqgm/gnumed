#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/dists/Archive/Attic/make-dists.sh,v $
# $Revision: 1.1 $
# GPL
# Karsten.Hilbert@gmx.net

echo "=> client ..."
tar -cvhzf gnumed-archive-client.tgz client

echo "=> server ..."
tar -cvhzf gnumed-archive-server.tgz server

echo "=> client + server ..."
tar -cvzf gnumed-archive.tgz gnumed-archive-client.tgz gnumed-archive-server.tgz
