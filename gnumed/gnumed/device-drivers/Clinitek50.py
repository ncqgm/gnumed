"""Clinitek 50 Urinalysis device driver.

This device is made by Bayer Diagnostics.

@license: GPL
"""
#========================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/device-drivers/Clinitek50.py,v $
__version__ = "$Revision: 1.3 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

# stock python
import sys, os.path

if __name__ == '__main__':
	sys.path.append('../client/python-common/')

import gmLog
_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)

import gmExceptions, gmSerialTools

# 3rd party
import serial, mx.DateTime as mxDT

#========================================================
class cClinitek50:

	# constant declarations
	ETX = chr(3)
	ENQ = cmd_req_ID = chr(5)
	ACK = cmd_ACK_packet = chr(6)
	DC1 = XON = chr(17)
	DC2 = cmd_req_data = chr(18)
	DC3 = XOFF = chr(19)
	NAK = cmd_NAK_packet = chr(21)
	EOL = CRLF = '\r\n'
	timeout = 3000
	max_packet_size = 1024
	packet_header = '\2\r\n'		# STX CR LF
	dev_id = '6510'
	known_good_dev_revs = ('  ', 'A ')
	known_good_sw_versions = ('01.00', '01.02')
	known_stix_types = ('MULTISTIX 8 SG',)
	time_format = '%H%M'

	def __init__(self, aPort = 0, aDateFormat = '%y%m%d'):
		"""Setup low level driver and check attached device."""
		# instantiate low level hardware driver
		try:
			# those values are fixed according to the specs
			self.__drv = serial.Serial (
				aPort,
				baudrate = 9600,
				bytesize = serial.EIGHTBITS,
				parity = serial.PARITY_NONE,
				stopbits = serial.STOPBITS_ONE,
				timeout = 2,
				xonxoff = 1
			)
		except:
			_log.LogException('cannot open serial port', sys.exc_info(), verbose = 1)
			raise

		# must be LOW according to specs,
		# if set to HIGH and connected the device
		# controller will enter programming mode
		self.__drv.setDTR(0)
		self.__drv.flushInput()
		self.__drv.flushOutput()

		_log.Log(gmLog.lData, self.__drv)

		self.__date_format = aDateFormat

		if not self.__detect_device():
			raise gmExceptions.ConstructorError, 'cannot detect and verify Clinitek 50 device'
	#----------------------------------------------------
	# API
	#----------------------------------------------------
	def get_record(self):
		# enable data transfer
		self.__drv.write(cClinitek50.XON)
		# request data
		self.__drv.write(cClinitek50.cmd_req_data)
		packet = self.__receive_packet()
		if packet is None:
			return None
		if packet == -1:
			return -1
		if not self.__verify_data_packet(packet):
			# NAK packet
			self.__drv.write(cClinitek50.cmd_NAK_packet)
			return None
		self.__drv.write(cClinitek50.cmd_ACK_packet)
		return packet
	#----------------------------------------------------
	# internal helpers
	#----------------------------------------------------
	def __detect_device(self):
		self.__drv.write(cClinitek50.cmd_req_ID)
		packet = self.__receive_packet()
		if packet is None:
			return None
		if not self.__verify_detect_packet(packet):
			return None
		return 1
	#----------------------------------------------------		
	def __receive_packet(self):
		"""
		-1		: no more data in device
		None	: error
		other	: packet
		"""
		# wait for ETX which is supposed to terminate all packets
		successful, packet = gmSerialTools.wait_for_str (
			self.__drv,
			cClinitek50.ETX,
			cClinitek50.timeout,
			cClinitek50.max_packet_size
		)
		if not successful:
			if packet == cClinitek50.NAK:
				_log.Log(gmLog.lErr, 'no more data in device')
				return -1
			else:
				_log.Log(gmLog.lErr, 'receiving packet from device failed')
				return None
		if not self.__verify_generic_packet_structure(packet):
			# NAK packet
			self.__drv.write(cClinitek50.cmd_NAK_packet)
			return None
		_log.Log(gmLog.lData, 'received generically valid packet')
		return packet
	#----------------------------------------------------
	def __verify_generic_packet_structure(self, packet):
		# does it start with STX CR LF ?
		if packet[:3] != cClinitek50.packet_header:
			_log.Log(gmLog.lErr, 'packet does not start with STX CR LF')
			_log.Log(gmLog.lData, packet, gmLog.lCooked)
			return None
		# does it have at least 5 lines ?
		if not len(string.split(packet, cClinitek50.EOL)) > 4:
			_log.Log(gmLog.lErr, 'packet does not have at least 5 lines')
			_log.Log(gmLog.lData, packet, gmLog.lCooked)
			return None
		# does it have a valid checksum ?
		rxd_crc = '0x%s' % packet[-3:-1]
		calced_crc = hex(reduce(lambda x, y: x + ord(y), tuple(packet[1:-3]), 0) & 255)
		if calced_crc != rxd_crc:
			_log.Log(gmLog.lErr, 'packet checksum error: received [%s] vs. calculated [%s]')
			_log.Log(gmLog.lData, packet, gmLog.lCooked)
			return None
		# seems valid
		return 1
	#----------------------------------------------------
	def __verify_detect_packet(self, packet):
		lines = string.split(packet, cClinitek50.EOL)
		# product ID: 6510 = Clinitek 50
		tmp = lines[1][:4]
		if tmp != cClinitek50.dev_id:
			_log.Log(gmLog.lErr, 'device does not seem to be a Clinitek 50, product ID is [%s], expected [%s]' % (tmp, cClinitek50.dev_id))
			_log.Log(gmLog.lData, lines)
			return None
		# product revision
		tmp = lines[1][4:6]
		if tmp not in cClinitek50.known_good_dev_revs:
			_log.Log(gmLog.lWarn, 'product revision [%s] untested, trying to continue anyways' % tmp)
		# software version
		tmp = lines[1][6:11]
		if tmp not in cClinitek50.known_good_sw_versions:
			_log.Log(gmLog.lWarn, 'software version [%s] untested, trying to continue anyways' % tmp)
		# date/time
		timestamp = mxDT.strptime(lines[1][12:22], self.__date_format + cClinitek50.time_format)
		_log.Log(gmLog.lInfo, 'device timestamp: %s' % timestamp)
		_log.Log(gmLog.lInfo, 'system timestamp: %s' % mxDT.now())
		age = mxDT.Age(mxDT.now(), timestamp)
		if age.hours > 6:
			_log.Log(gmLog.lErr, 'device time is off by %s, please correct that' % age)
			return None
		# language-unit profile
		(lang, units) = string.split(lines[2], ' - ')
		_log.Log(gmLog.lInfo, 'language: %s' % lang)
		_log.Log(gmLog.lInfo, 'unit system: %s' % units)
		# STIX type
		stix_type = string.trim(line[3])
		if not stix_type in cClinitek50.known_stix_types:
			_log.Log(gmLog.lErr, "don't know how to handle stix of type %s" % stix_type)
			return None
		# seems valid
		return 1
	#----------------------------------------------------
	def __verify_data_packet(self, packet):
		print "skipping verification of data packet"
		# seems valid
		return 1
#========================================================
# main
#========================================================
if __name__ == '__main__':
	# try to init device
	try:
		dev = cClinitek50(0)
	except:
		print "cannot init device"
		sys.exit()
	while 1:
		packet = dev.get_record()
		if packet == -1:
			break
		print packet
#========================================================
# docs
#========================================================

#detection cmd answer:

#STXCR LF
#6510  01.02 9706201349CR LF
#DEUTSCH - CONV.CR LF
#MULTISTIX 8 SGCR LF
#48ETX


#sample data block:

#STXCR LF
#6510  01.02 9703031111CR LF
#008 HELL GELB     CR LF
#GLU  NEGATIV        CR LF
#BIL  NEGATIV        CR LF
#KET  NEGATIV        CR LF
#SG   >=1.030        CR LF
#pH   5.0            CR LF
#PRO  NEGATIV        CR LF
#UBG  0.2 mg/dL      CR LF
#NIT  NEGATIV        CR LF
#OBL* Ca 10 Ery/uL   CR LF
#LEU  0 Leu/uL       CR LF
#4CETX


# Bayer Diagnostics Part Numbers
# ------------------------------
# 40453171  9 pin Sub-D female adapter
# 40453170  25 pin Sub-D female adapter
# 40453172  2m connector cable
# 6517      connector kit

#========================================================
# $Log: Clinitek50.py,v $
# Revision 1.3  2003-11-20 01:37:41  ncq
# - should be able to read data records albeit no verification
#
# Revision 1.2  2003/11/19 18:11:39  ncq
# - should be able to detect devices
#
# Revision 1.1  2003/11/17 01:34:55  ncq
# - initial checkin, non-functional
#
