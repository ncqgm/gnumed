#!/usr/bin/python
#############################################################################
#
# gmI18N - "Internationalisation" helper classes, functions and variables
#          Anything related to language dependency apart from the gettext library
#          goes here
# ---------------------------------------------------------------------------
#
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: gettext
# @change log:
#	25.10.2001 hherb first draft, untested
#
# @TODO: Almost everything
############################################################################

import gettext
# ADDED CODE Haywood 26/2/02
# set domain to 'gnumed' -- otherwise doesn't work on my setup
gettext.textdomain ('gnumed')
_ = gettext.gettext

gmTimeformat = _("%Y-%m-%d  %H:%M:%S")
