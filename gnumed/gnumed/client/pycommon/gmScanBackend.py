#==================================================
# GNUmed SANE/TWAIN scanner classes
#==================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/gmScanBackend.py,v $
# $Id: gmScanBackend.py,v 1.22 2007-01-18 12:34:01 ncq Exp $
__version__ = "$Revision: 1.22 $"
__license__ = "GPL"
__author__ = """Sebastian Hilbert <Sebastian.Hilbert@gmx.net>, Karsten Hilbert <Karsten.Hilbert@gmx.net>"""

#==================================================
# stdlib
import sys, os.path, os, Image, string, time, shutil, tempfile, codecs, glob, locale


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmLog, gmExceptions, gmShellAPI


_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

_twain_module = None
_sane_module = None

use_XSane = True
#=======================================================
class cTwainScanner:

	def __init__(self, calling_window=None):
		msg = u'cannot instantiate TWAIN driver class: %s'
		if not _twain_import_module():
			raise gmExceptions.ConstructorError, msg % u'cannot import TWAIN module'

		self.__register_event_handlers()

		self.__calling_window = calling_window
		self.__src_manager = None
		self.__scanner = None
		if not self.__init_src_manager():
			raise gmExceptions.ConstructorError, msg % u'cannot initialize TWAIN source manager'
	#---------------------------------------------------
	def __register_event_handlers(self):
		# FIXME: this means we cannot use more than one TWAIN source at once
		self.__twain_event_handlers = {
			_twain_module.MSG_XFERREADY: self._twain_handle_transfer,
			_twain_module.MSG_CLOSEDSREQ: self._twain_close_datasource,
			_twain_module.MSG_CLOSEDSOK: self._twain_save_state,
			_twain_module.MSG_DEVICEEVENT: self._twain_handle_src_event
		}
	#---------------------------------------------------
	def __init_src_manager(self):
		# open scanner manager
		if self.__src_manager is None:
			# TWAIN talks to us via MS-Windows message queues so we
			# need to pass it a handle to ourselves
			self.__src_manager = _twain_module.SourceManager(self.__calling_window.GetHandle(), ProductName = 'GNUmed - The EMR that never sleeps.')
			if not self.__src_manager:
				_log.Log(gmLog.lErr, "cannot get a handle for the TWAIN source manager")
				return False
			# TWAIN will notify us when the image is scanned
			self.__src_manager.SetCallback(self._twain_event_callback)
			_log.Log(gmLog.lData, "TWAIN source manager config: %s" % str(self.__src_manager.GetIdentity()))
			# clean up scanner driver
			if self.__scanner is not None:
				self.__scanner.destroy()
				del self.__scanner
			self.__scanner = None
		return True
	#---------------------------------------------------
	def __init_scanner(self):
#		if not self.__init_src_manager():
#			return False
		if self.__scanner is None:
			# FIXME: set source by string
			self.__scanner = self.__src_manager.OpenSource()
			if self.__scanner is None:
				_log.Log(gmLog.lErr, "cannot open scanner via TWAIN source manager")
				return False
			_log.Log(gmLog.lInfo, "TWAIN data source: %s" % self.__scanner.GetSourceName())
			_log.Log(gmLog.lData, "TWAIN data source config: %s" % str(self.__scanner.GetIdentity()))
		return True
	#---------------------------------------------------
	def close(self):
		if self.__scanner is not None:
			self.__scanner.destroy()
			del self.__scanner
		if self.__src_manager is not None:
			self.__src_manager.destroy()
			del self.__src_manager
		return
	#---------------------------------------------------
	# TWAIN callback handling
	#---------------------------------------------------
	def _twain_event_callback(self, twain_event):
		_log.Log(gmLog.lData, 'notification of TWAIN event <%s>' % str(twain_event))
		self.__twain_event_handlers[twain_event]()
		return
	#---------------------------------------------------
	def _twain_close_datasource(self):
		_log.Log(gmLog.lInfo, "being asked to close data source")
		self.__scanner = None
		return True
	#---------------------------------------------------
	def _twain_save_state():
		_log.Log(gmLog.lInfo, "being asked to save application state")
		return True
	#---------------------------------------------------
	def _twain_handle_src_event():
		_log.Log(gmLog.lInfo, "being asked to handle device specific event")
		return True
	#---------------------------------------------------
	def _twain_handle_transfer(self):
		_log.Log(gmLog.lData, 'receiving image from TWAIN source')
		_log.Log(gmLog.lData, 'image info: %s' % self.__scanner.GetImageInfo())

		# get from source
		try:
			(external_data_handle, more_images_pending) = self.__scanner.XferImageNatively()
		except:
			_log.LogException('XferImageNatively() failed, unable to get global heap image handle', sys.exc_info(), verbose=1)
			# free external image memory
			_twain_module.GlobalHandleFree(external_data_handle)
			# hide the scanner user interface again
			self.__scanner.HideUI()
			return False

		_log.Log(gmLog.lData, '%s pending images' % more_images_pending)

		try:
			# convert DIB to standard bitmap file
			_twain_module.DIBToBMFile(external_data_handle, self.__filename)
		except:
			_log.LogException('DIBToBMFile() failed, unable to convert image in global heap handle into file [%s]' % self.__filename, sys.exc_info(), verbose=1)
			# free external image memory
			_twain_module.GlobalHandleFree(external_data_handle)
			# hide the scanner user interface again
			self.__scanner.HideUI()
			return False
		# free external image memory
		_twain_module.GlobalHandleFree(external_data_handle)
		# hide the scanner user interface again
		self.__scanner.HideUI()

		return True
	#---------------------------------------------------
	def acquire_pages_into_files(self, delay=None, filename=None, tmpdir=None):
		if filename is None:
			if tmpdir is None:
				(handle, filename) = tempfile.mkstemp(suffix='.bmp', prefix='gmScannedObj-')
			else:
				(handle, filename) = tempfile.mkstemp(suffix='.bmp', prefix='gmScannedObj-', dir=tmpdir)
		else:
			tmp, ext = os.path.splitext(filename)
			if ext != '.bmp':
				filename = filename + '.bmp'

		self.__filename = os.path.abspath(os.path.expanduser(filename))

		if not self.__init_scanner():
			return False

		self.__scanner.RequestAcquire()
		return [self.__filename]
	#---------------------------------------------------
#	def dummy(self):
#
#		# make tmp file name
#		tempfile.tempdir = self.scan_tmp_dir
#		tempfile.template = 'obj-'
#		bmp_name = tempfile.mktemp('.bmp')
#		fname = bmp_name
#
#		# convert to JPEG ?
#		do_jpeg = _cfg.get("scanning", "convert to JPEG")
#		if do_jpeg in ["yes", "on"]:
#			jpg_name = tempfile.mktemp('.jpg')
#			fname = jpg_name
#			# get JPEG quality factor
#			quality_value = _cfg.get("scanning", "JPEG quality level")
#			if quality_value is None:
#				_log.Log(gmLog.lWarn, "JPEG quality level not specified in config file, using default level of 75")
#				quality_value = 75
#			else:
#				if quality_value.isdigit():
#					quality_value = int(quality_value, 10)
#				else:
#					_log.Log(gmLog.lWarn, "JPEG quality level [%s] not a number, using default level of 75" % quality_value)
#					quality_value = 75
#			# do we want progression ?
#			progression_flag = _cfg.get("scanning", "progressive JPEG")
#			_log.Log(gmLog.lData, "JPEG conversion: quality level: %s, progression: %s" % (quality_value, progression_flag))
#			kwds = {}
#			kwds['quality'] = quality_value
#			if progression_flag in ["yes", "on"]:
#				kwds['optimize'] = 1
#				kwds['progressive'] = 1
#			# actually convert to JPEG
#			try:
#				Image.open(bmp_name).convert('RGB').save(jpg_name, **kwds)
#			except:
#				_log.LogException("optimized JPEG write failed, turning off optimization", sys.exc_info(), fatal=0)
#				Image.open(bmp_name).convert('RGB').save(jpg_name)
#			# remove bitmap (except Windows can't do that sometimes :-(
#			try:
#				os.remove(bmp_name)
#			except:
#				_log.LogException("Can't remove bitmap.", sys.exc_info(), fatal=0)
#=======================================================
class cSaneScanner:

	# for testing uncomment "test" backend in /etc/sane/dll.conf

	_src_manager = None

	def __init__(self, device=None):
		msg = 'cannot instantiate SANE driver class'
		if not _sane_import_module():
			raise gmExceptions.ConstructorError, msg

		# FIXME: need to test against devs[x][0]
#		devs = _sane_module.get_devices()
#		if device not in devs:
#			_log.Log(gmLog.lErr, "device [%s] not found in list of devices detected by SANE" % device)
#			_log.Log(gmLog.lErr, str(devs))
#			raise gmExceptions.ConstructorError, msg

		self.__device = device
		_log.Log(gmLog.lInfo, 'using SANE device [%s]' % self.__device)

		if not self.__init_scanner():
			raise gmExceptions.ConstructorError, msg
	#---------------------------------------------------
	def __init_scanner(self):
		try:
			self.__scanner = _sane_module.open(self.__device)
		except:
			_log.LogException('cannot open SANE scanner', sys.exc_info(), verbose=0)
			return False

		_log.Log(gmLog.lData, 'opened SANE device: %s' % str(self.__scanner))
		_log.Log(gmLog.lData, 'SANE device config: %s' % str(self.__scanner.get_parameters()))
		_log.Log(gmLog.lData, 'SANE device opts	 : %s' % str(self.__scanner.optlist))
		_log.Log(gmLog.lData, 'SANE device opts	 : %s' % str(self.__scanner.get_options()))

		return True
	#---------------------------------------------------
	def close(self):
		self.__scanner.close()
	#---------------------------------------------------
	def acquire_pages_into_files(self, delay=None, filename=None, tmpdir=None):
		if filename is None:
			if tmpdir is None:
				(handle, filename) = tempfile.mkstemp(suffix='.bmp', prefix='gmScannedObj-')
			else:
				(handle, filename) = tempfile.mkstemp(suffix='.bmp', prefix='gmScannedObj-', dir=tmpdir)
		else:
			tmp, ext = os.path.splitext(filename)
			if ext != '.bmp':
				filename = filename + '.bmp'

		filename = os.path.abspath(os.path.expanduser(filename))

		if delay is not None:
			time.sleep(delay)
			_log.Log(gmLog.lData, 'some sane backends report device_busy if we advance too fast. delay set to %s sec' % delay)

		try:
			self.__scanner.start()
			img = self.__scanner.snap()
			img.save(filename)
		except:
			_log.LogException('Unable to get image from scanner into [%s] !' % filename, sys.exc_info(), verbose=1)
			return False

		return [filename]
	#---------------------------------------------------
#	def dummy(self):
#		pass
#		# supposedly there is a method *.close() but it does not
#		# seem to work, therefore I put in the following line (else
#		# it reports a busy sane-device on the second and consecutive runs)
#		try:
#			# by default use the first device
#			# FIXME: room for improvement - option
#			self.__scanner = _sane_module.open(_sane_module.get_devices()[0][0])
#		except:
#			_log.LogException('cannot open SANE scanner', sys.exc_info(), verbose=1)
#			return False
#
#		# Set scan parameters
#		# FIXME: get those from config file
#		#self.__scannercontrast=170 ; self.__scannerbrightness=150 ; self.__scannerwhite_level=190
#		#self.__scannerdepth=6
#		#self.__scannerbr_x = 412.0
#		#self.__scannerbr_y = 583.0
#==================================================
class cXSaneScanner:

	_filetype = '.png'					# FIXME: configurable, TIFF ?
	_xsanerc = os.path.expanduser(os.path.join('~',".sane","xsane","xsane.rc"))
	_xsanerc_backup = os.path.expanduser(os.path.join('~',".sane","xsane","xsane.rc.gnumed.bak"))

	#----------------------------------------------
	def __init__(self):
		# while not strictly necessary it is good to fail early
		# this will tell us fairly safely whether XSane is properly installed
		if not os.access(cXSaneScanner._xsanerc, os.W_OK):
			raise IOError('XSane not properly installed for this user, no write access for [%s]' % cXSaneScanner._xsanerc)
	#----------------------------------------------
	def close(self):
		pass
	#----------------------------------------------
	def acquire_pages_into_files(self, delay=None, filename=None, tmpdir=None):
		"""Call XSane.

		<filename name part must have format name-xxx.ext>
		"""
		if filename is None:
			if tmpdir is None:
				(handle, filename) = tempfile.mkstemp(suffix=cXSaneScanner._filetype, prefix='gmScannedObj-')
			else:
				(handle, filename) = tempfile.mkstemp(suffix=cXSaneScanner._filetype, prefix='gmScannedObj-', dir=tmpdir)
		else:
			tmp, ext = os.path.splitext(filename)
			if ext != cXSaneScanner._filetype:
				filename = filename + cXSaneScanner._filetype

		filename = os.path.abspath(os.path.expanduser(filename))
		path, name = os.path.split(filename)

		self.__prepare_xsanerc(tmpdir=path)

		gmShellAPI.run_command_in_shell (
			command = 'xsane --no-mode-selection --save --force-filename "%s"' % filename, 
			blocking = True
		)

		self.__restore_xsanerc()

		return glob.glob(filename.replace('###', '*'))
	#----------------------------------------------
	# internal API
	#----------------------------------------------
	def __prepare_xsanerc(self, tmpdir=None):

		shutil.copy2(cXSaneScanner._xsanerc, cXSaneScanner._xsanerc_backup)

		# our closest bet, might contain umalauts
		enc = locale.getlocale()[1]
		fread = codecs.open(cXSaneScanner._xsanerc_backup, mode = "rU", encoding = enc)
		fwrite = codecs.open(cXSaneScanner._xsanerc, mode = "w", encoding = enc)

		val_dict = {
			'filetype': cXSaneScanner._filetype,
			'tmp-path': tmpdir,
			'working-directory': tmpdir
		}

		for idx, line in enumerate(fread):
			line = line.replace(fread.newlines, '')

			if idx % 2 == 0:			# even lines are keys
				key = line.strip('"')
			else: 						# odd lines are corresponding values
				try:
					value = val_dict[key]
				except KeyError:
					value = line
				fwrite.write('"%s"%s' % (key, fread.newlines))
				fwrite.write('%s%s' % (value, fread.newlines))

		fwrite.close()
		fread.close()

		return True
	#----------------------------------------------
	def __restore_xsanerc(self):
		shutil.copy2(cXSaneScanner._xsanerc_backup, cXSaneScanner._xsanerc)
#==================================================
def _twain_import_module():
	global _twain_module
	if _twain_module is None:
		try:
			import twain
			_twain_module = twain
		except ImportError:
			_log.LogException('cannot import TWAIN module (WinTWAIN.py)', sys.exc_info(), verbose=0)
			return False
		_log.Log(gmLog.lInfo, "TWAIN version: %s" % _twain_module.Version())
	return True
#-----------------------------------------------------
def _sane_import_module():
	global _sane_module
	if _sane_module is None:
		try:
			import sane
		except ImportError:
			_log.LogException('cannot import SANE module', sys.exc_info(), verbose=0)
			return False
		_sane_module = sane
		try:
			init_result = _sane_module.init()
		except:
			_log.LogException('cannot init SANE module', sys.exc_info(), verbose=1)
			return False
		_log.Log(gmLog.lInfo, "SANE version: %s" % str(init_result))
		_log.Log(gmLog.lData, 'SANE device list: %s' % str(_sane_module.get_devices()))
	return True
#-----------------------------------------------------
def get_devices():
	if _twain_import_module():
		# TWAIN does not support get_devices():
		# devices can only be selected from within TWAIN itself
		return None
	if use_XSane:
		return None
	if _sane_import_module():
		return _sane_module.get_devices()
	return False
#-----------------------------------------------------
def acquire_pages_into_files(device=None, delay=None, filename=None, tmpdir=None, calling_window=None):
	try:
		scanner = cTwainScanner(calling_window=calling_window)
	except gmExceptions.ConstructorError:
		if use_XSane:
			_log.Log(gmLog.lData, 'using XSane')
			try:
				scanner = cXSaneScanner()
			except IOError:
				_log.LogException('Cannot load any scanner driver (XSANE or TWAIN).', verbose=False)
				return None
		else:
			_log.Log(gmLog.lData, 'using SANE directly')
			try:
				scanner = cSaneScanner(device=device)
			except gmExceptions.ConstructorError:
				_log.LogException('Cannot load any scanner driver (SANE or TWAIN).', verbose=False)
				return None

	_log.Log(gmLog.lData, 'requested filename: [%s]' % filename)
	fnames = scanner.acquire_pages_into_files(filename=filename, delay=delay, tmpdir=tmpdir)
	scanner.close()
	_log.Log(gmLog.lData, 'acquired page into files: %s' % str(fnames))

	return fnames
#==================================================
# main
#==================================================
if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)

#	from Gnumed.pycommon import gmI18N

	print "devices:"
	print get_devices()

	setups = [
		{'dev': 'test:0', 'file': 'x1-test0-1-0001'},
		{'dev': 'test:1', 'file': 'x2-test1-1-0001.bmp'},
		{'dev': 'test:0', 'file': 'x3-test0-2-0001.bmp-ccc'}
	]

	idx = 1
	for setup in setups:
		print "scanning page #%s from device [%s]" % (idx, setup['dev'])
		idx += 1
		fnames = acquire_pages_into_files(device = setup['dev'], filename = setup['file'], delay = (idx*5))
		if fnames is False:
			print "error, cannot acquire page"
		else:
			print " image files:", fnames


#==================================================
# $Log: gmScanBackend.py,v $
# Revision 1.22  2007-01-18 12:34:01  ncq
# - must init self.__scanner/self.__src_manager
#
# Revision 1.21  2007/01/18 12:08:56  ncq
# - try to once again fix/improve TWAIN scanning
#
# Revision 1.20  2006/12/27 16:42:53  ncq
# - cleanup
# - add XSane interface in cXSaneScanner as worked out by Kai Schmidt
# - acquire_pages_into_files() now returns a list
# - fix test suite
#
# Revision 1.19  2006/09/02 21:11:59  ncq
# - improved test suite
#
# Revision 1.18  2006/08/29 18:41:58  ncq
# - improve test suite
#
# Revision 1.17  2006/08/29 18:33:02  ncq
# - forward port TWAIN fixes from 0.2 branch
#
# Revision 1.16  2006/05/14 20:42:20  ncq
# - properly handle get_devices()
#
# Revision 1.15  2006/05/13 23:42:13  shilbert
# - getting there, TWAIN now lets me take more than one image in one session
#
# Revision 1.14  2006/05/13 23:18:11  shilbert
# - fix more TWAIN issues
#
# Revision 1.13  2006/05/13 21:36:15  shilbert
# - fixed some TWAIN rleated issues
#
# Revision 1.12  2006/01/17 19:45:32  ncq
# - close scanner when done
# - cleanup
#
# Revision 1.11  2006/01/16 19:42:18  ncq
# - improve unit test
#
# Revision 1.10  2006/01/16 19:41:29  ncq
# - properly init sane now
#
# Revision 1.9  2006/01/16 19:35:41  ncq
# - can only get sane device list after init()
#
# Revision 1.8  2006/01/16 19:27:26  ncq
# - cleaner layout
# - report_devices() -> get_devices()
#
# Revision 1.7  2006/01/15 14:00:28  ncq
# - reconvert spaces to tabs
#
# Revision 1.6	2006/01/15 13:16:06	 shilbert
# - support for multiple scanners was added
#
# Revision 1.5	2006/01/15 10:04:37	 shilbert
# - scanner device has not been passed on to the acquire_image function - fixed
#
# Revision 1.4	2005/11/27 13:05:45	 ncq
# - used calling_window in the wrong place ...
#
# Revision 1.3	2005/11/27 10:38:46	 ncq
# - use secure creation of file names when not given
#
# Revision 1.2	2005/11/27 08:48:45	 ncq
# - some old cruft removed
# - example code useful being kept around for now commented out
#
# Revision 1.1	2005/11/26 16:53:43	 shilbert
# - moved here from Archive
# - needed by gmScanIdxMedDocs plugin
#
# Revision 1.7	2005/11/09 11:30:21	 ncq
# - activate sane test scanner
#
