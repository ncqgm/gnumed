#!/usr/bin/python
#############################################################################
#
# gmExceptions - classes for exceptions gnumed modules may throw
# ---------------------------------------------------------------------------
#
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: nil
# @change log:
#	07.02.2002 hherb first draft, untested
#
# @TODO: Almost everything
############################################################################


class ConnectionError(Exception):
    #raised whenever the database backend connection fails
    def __init__(self, errmsg):
	self.errmsg=errmsg
	
    def __str__(self):
	return errmsg
    




