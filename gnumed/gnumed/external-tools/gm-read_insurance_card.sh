#!/bin/bash

#==============================================================
# author: Karsten Hilbert
# license: GPL v2 or later
#
#==============================================================

#set -x

CONF="/etc/gnumed/gm-read_insurance_card.sh"

#==============================================================
# There really should not be any need to
# change anything below this line.
#==============================================================

# load config file
if [ -r ${CONF} ] ; then
	. ${CONF}
else
	echo "Cannot read configuration file ${CONF}. Aborting."
	exit 1
fi


VK_READER_OUTPUT_FORMAT="4"		# JSON only
VK_READER_PROTOKOLL="n"			# j/n, keeps XML
VK_READER_DEBUG="n"				# j/n


CCReader ${VK_READER_PORT} ${VK_READER_CTN} ${VK_READER_OUTPUT_FORMAT} ${VK_READER_PROTOKOLL} ${VK_READER_DEBUG}
