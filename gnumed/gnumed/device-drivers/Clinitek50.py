"""Clinitek 50 Urinalysis device driver.

@license: GPL
"""
#========================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/device-drivers/Clinitek50.py,v $
__version__ = "$Revision: 1.1 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

# stock python
import sys, os.path

import gmLog
_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

import gmExceptions, gmSerialPort

# 3rd party
import serial

#========================================================
class cClinitek50:

	cmd_req_ID = chr(5)
	cmd_NAK_packet = chr(21)
	ETX = chr(3)
	timeout = 3000
	max_packet_size = 1024
	packet_header = '\2\r\n'		# STX CR LF
	EOL = '\r\n'
	dev_id = '6510'
	known_good_dev_revs = ('  ', 'A ')
	known_good_sw_versions = ('01.00', '01.02')

	def __init__(self, aPort = 0):
		"""Setup low level driver and check attached device."""
		# instantiate low level hardware driver
		try:
			self.__drv = serial.Serial (
				aPort,
				baudrate = 9600,
				bytesize = serial.EIGHTBITS,
				parity = serial.PARITY_NONE,
				stopbits = serial.STOPBITS_ONE,
				timeout = 2,
				xonxoff = 1
			)
		except StandardError:
			_log.LogException('cannot open serial port', sys.exc_info(), verbose = 1)
			raise

		self.__drv.setDTR(level = 0)
		self.__drv.flushInput()
		self.__drv.flushOutput()

		_log.Log(gmLog.lData, self.__drv)

		if not self.__detect_device():
			raise gmExceptions.ConstructorError


		# check attached device
		_log.Log(gmLog.lInfo, 'device info: "%s"' % self.getVerObsolete())
		# verify model/firmware
		result = self.getVer()
		_log.Log(gmLog.lInfo, 'device info: "%s"' % result)
		if result is None:
			_log.Log(gmLog.lPanic, 'device info request timed out, no device/link error/cable failure')
			raise IOError, "cannot detect device"
		# check for known firmware strings
		if result['data'] not in self.__known_devices:
			_log.Log(gmLog.lWarn, 'It is not known whether the device "%s" will work properly with' % result['payload'])
			_log.Log(gmLog.lWarn, 'this driver. Please report your mileage and the device id string')
			_log.Log(gmLog.lWarn, 'to the authors at %s.' % __author__)
			_log.Log(gmLog.lInfo, 'Currently known device id strings:')
			_log.Log(gmLog.lInfo, str(self.__known_devices))
	#----------------------------------------------------
	def __detect_device(self):
		self.__drv.write(gmClinitek50.cmd_req_ID)
		packet = self.__get_packet()
		if packet is None:
			return None
		if not self.__verify_detect_packet(packet):
			return None
		return 1
	#----------------------------------------------------
	def __get_packet(self):
		# wait for ETX which is supposed to terminate all packets
		successful, packet = gmSerialPort.wait_for_str (
			self.__drv,
			gmClinitek50.ETX,
			gmClinitek50.timeout,
			gmClinitek50.max_packet_size
		)
		if not successful:
			_log.Log(gmLog.lErr, 'receiving packet from device failed')
			_log.Log(gmLog.lData, packet, gmLog.lCooked)
			return None
		if not self.__verify_generic_packet_structure(packet):
			# NAK packet
			self.__drv.write(gmClinitek50.cmd_NAK_packet)
			return None
		return packet
	#----------------------------------------------------
	def __verify_generic_packet_structure(self, packet):
		# does it start with STX CR LF ?
		if packet[:3] != gmClinitek50.packet_header:
			_log.Log(gmLog.lErr, 'packet does not start with STX CR LF')
			_log.Log(gmLog.lData, packet, gmLog.lCooked)
			return None
		# does it have at least 5 lines ?
		if not len(string.split(packet, gmClinitek50.EOL)) > 4:
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
		lines = string.split(packet, gmClinitek50.EOL)
		# product ID: 6510 = Clinitek 50
		tmp = lines[1][:4]
		if tmp != gmClinitek50.dev_id:
			_log.Log(gmLog.lErr, 'device does not seem to be a Clinitek 50, product ID is [%s], expected [%s]' % (tmp, gmClinitek50.dev_id))
			_log.Log(gmLog.lData, lines)
			return None
		# product revision
		tmp = lines[1][4:6]
		if tmp not in gmClinitek50.known_good_dev_revs:
			_log.Log(gmLog.lWarn, 'product revision [%s] untested, trying to continue anyways' % tmp)
		# software version
		tmp = lines[6:11]
		if tmp not in gmClinitek50.known_good_sw_versions:
			_log.Log(gmLog.lWarn, 'software version [%s] untested, trying to continue anyways' % tmp)

#========================================================
# main
#========================================================

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
# Revision 1.1  2003-11-17 01:34:55  ncq
# - initial checkin, non-functional
#
