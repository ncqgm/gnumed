#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/bootstrap/Attic/make-links.sh,v $
# $Id: make-links.sh,v 1.1 2003-02-25 08:26:49 ncq Exp $

echo "setting up links"

ln -vfs ../../client/python-common modules
ln -vfs ../sql sql
