"""GnuMed serial port tools.

These functions are complementing pySerial.

@license: GPL (details at http://www.gnu.org)
@copyright: author
"""
#===========================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmSerialTools.py,v $
# $Id: gmSerialTools.py,v 1.3 2008-01-30 14:05:31 ncq Exp $
__version__ = "$Revision: 1.3 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__licence__ = "GPL (details at http://www.gnu.org)"

import time, string, logging


_log = logging.getLogger('gm.serial')
_log.info(__version__)
#----------------------------------------------------
# general utility
#----------------------------------------------------
def wait_for_str(aDrv = None, aString = '', aTimeout = 2500, max_bytes = 2048):
	"""Wait for a particular string with timeout.

	- timeout in milliseconds, please
	"""
	if aString == '':
		return (1, '')

	if aDrv is None:
		_log.error("need source for incoming data")
		return (0, '')

	if max_bytes < len(aString):
		max_bytes = len(aString) + 1

	rxd = ''
	loop = 0
	slice = 100
	# how many loops ?
	max_loops = abs(aTimeout / slice)
	# wait for data
	while loop < max_loops:
		loop += 1
		# something there
		if aDrv.inWaiting() > 0:
			# get all there is
			while aDrv.inWaiting() > 0:
				rxd = rxd + aDrv.read(size = 1)
				# did this contain our expected string already ?
				if string.find(rxd, aString) > -1:
					return (1, rxd)
				# did we exceed our character buffer limit ?
				# this stops runaway serial ports
				if len(rxd) >= max_bytes:
					_log.error('exceeded maximum # of bytes (%s) to receive' % max_bytes)
					return (0, rxd)
		# nothing there, wait a slice
		else:
			if len(rxd) >= max_bytes:
				_log.error('exceeded maximum # of bytes to receive')
				return (0, rxd)
			time.sleep(float(slice) / 1000)

	# hm, waited for aTimeout but expected string not received
	_log.warning('wait for [%s] timed out after %s ms', aString, aTimeout)
	_log.debug(rxd)
	return (0, rxd)
#--------------------------------------------------------
def wait_for_data(aDrv = None, aTimeout = 2500):
	"""Wait for any incoming with timeout.

	- timeout in milliseconds, please
	"""
	if aDrv is None:
		_log.error("Need source for incoming data !")
		return 0

	loop = 0
	slice = 100
	# how many loops ?
	max_loops = abs(aTimeout / slice)
	# wait for data
	while loop < max_loops:
		# nothing there, wait a slice
		if aDrv.inWaiting() == 0:
			loop += 1
			time.sleep(float(slice) / 1000)
		else:
			return 1

	# hm, waited for aTimeout but expected string not received
	_log.warning('Timed out after %s ms while waiting for data.' % aTimeout)
	return 0
#========================================================
# $Log: gmSerialTools.py,v $
# Revision 1.3  2008-01-30 14:05:31  ncq
# - std lib logging
#
# Revision 1.2  2004/12/23 16:19:34  ncq
# - add licence
#
# Revision 1.1  2004/02/25 09:30:13  ncq
# - moved here from python-common
#
# Revision 1.3  2003/11/21 15:59:47  ncq
# - some cleanup
#
# Revision 1.2  2003/11/19 17:59:49  ncq
# - slice must be float()ed to support sub-second slices
#
# Revision 1.1  2003/11/19 17:35:28  ncq
# - initial check in
#
