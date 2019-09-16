#==================================================
# GNUmed SANE/TWAIN scanner classes
#==================================================



__license__ = "GPL v2 or later"
__author__ = """Sebastian Hilbert <Sebastian.Hilbert@gmx.net>, Karsten Hilbert <Karsten.Hilbert@gmx.net>"""


# stdlib
import sys
import os.path
import os
import time
import shutil
import io
import glob
import logging
#import stat


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmShellAPI
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmI18N
from Gnumed.pycommon import gmLog2


_log = logging.getLogger('gm.scanning')

_twain_module = None
_sane_module = None

use_XSane = True
#=======================================================
# TWAIN handling
#=======================================================
def _twain_import_module():
	global _twain_module
	if _twain_module is None:
		try:
			import twain
			_twain_module = twain
		except ImportError:
			_log.exception('cannot import TWAIN module (WinTWAIN.py)')
			raise
		_log.info("TWAIN version: %s" % _twain_module.Version())
#=======================================================
class cTwainScanner:

	# http://twainmodule.sourceforge.net/docs/index.html

	# FIXME: we need to handle this exception in the right place: <class 'twain.excTWCC_SUCCESS'>

	def __init__(self, calling_window=None):
		_twain_import_module()

		self.__calling_window = calling_window
		self.__src_manager = None
		self.__scanner = None
		self.__done_transferring_image = False

		self.__register_event_handlers()
	#---------------------------------------------------
	# external API
	#---------------------------------------------------
	def acquire_pages_into_files(self, delay=None, filename=None):
		if filename is None:
			filename = gmTools.get_unique_filename(prefix = 'gmScannedObj-', suffix = '.bmp')
		else:
			tmp, ext = os.path.splitext(filename)
			if ext != '.bmp':
				filename = filename + '.bmp'

		self.__filename = os.path.abspath(os.path.expanduser(filename))

		if not self.__init_scanner():
			raise OSError(-1, 'cannot init TWAIN scanner device')

		self.__done_transferring_image = False
		self.__scanner.RequestAcquire(True)

		return [self.__filename]
	#---------------------------------------------------
	def image_transfer_done(self):
		return self.__done_transferring_image
	#---------------------------------------------------
	def close(self):
		# close() is called after acquire_pages*() so if we destroy the source
		# before TWAIN is done we hang it, an RequestAcquire() only *requests*
		# a scan, we would have to wait for process_xfer to finisch before
		# destroying the source, and even then it might destroy state in the
		# non-Python TWAIN subsystem
		#**********************************
		# if we do this TWAIN does not work
		#**********************************
#		if self.__scanner is not None:
#			self.__scanner.destroy()

#		if self.__src_manager is not None:
#			self.__src_manager.destroy()

#		del self.__scanner
#		del self.__src_manager
		return
	#---------------------------------------------------
	# internal helpers
	#---------------------------------------------------
	def __init_scanner(self):
		if self.__scanner is not None:
			return True

		self.__init_src_manager()
		if self.__src_manager is None:
			return False

		# TWAIN will notify us when the image is scanned
		self.__src_manager.SetCallback(self._twain_event_callback)

		# no arg == show "select source" dialog
		try:
			self.__scanner = self.__src_manager.OpenSource()
		except _twain_module.excDSOpenFailed:
			_log.exception('cannot open TWAIN data source (image capture device)')
			gmLog2.log_stack_trace()
			return False

		if self.__scanner is None:
			_log.error("user canceled scan source selection dialog")
			return False

		_log.info("TWAIN data source: %s" % self.__scanner.GetSourceName())
		_log.debug("TWAIN data source config: %s" % str(self.__scanner.GetIdentity()))

		return True
	#---------------------------------------------------
	def __init_src_manager(self):

		if self.__src_manager is not None:
			return

		# clean up scanner driver since we will initialize the source manager
#		if self.__scanner is not None:
#			self.__scanner.destroy()			# this probably should not be done here
#			del self.__scanner					# try to sneak this back in later
#			self.__scanner = None				# this really should work

		# TWAIN talks to us via MS-Windows message queues
		# so we need to pass it a handle to ourselves,
		# the following fails with "attempt to create Pseudo Window failed",
		# I assume because the TWAIN vendors want to sabotage rebranding their GUI
#		self.__src_manager = _twain_module.SourceManager(self.__calling_window.GetHandle(), ProductName = 'GNUmed - The EMR that never sleeps.')
		try:
			self.__src_manager = _twain_module.SourceManager(self.__calling_window.GetHandle())

		except _twain_module.excSMLoadFileFailed:
			_log.exception('failed to load TWAIN_32.DLL')
			return

		except _twain_module.excSMGetProcAddressFailed:
			_log.exception('failed to jump into TWAIN_32.DLL')
			return

		except _twain_module.excSMOpenFailed:
			_log.exception('failed to open Source Manager')
			return

		_log.info("TWAIN source manager config: %s" % str(self.__src_manager.GetIdentity()))
	#---------------------------------------------------
	# TWAIN callback handling
	#---------------------------------------------------
	def __register_event_handlers(self):
		self.__twain_event_handlers = {
			_twain_module.MSG_XFERREADY: self._twain_handle_transfer_in_memory,
			_twain_module.MSG_CLOSEDSREQ: self._twain_close_datasource,
			_twain_module.MSG_CLOSEDSOK: self._twain_save_state,
			_twain_module.MSG_DEVICEEVENT: self._twain_handle_src_event
		}
	#---------------------------------------------------
	def _twain_event_callback(self, twain_event):
		_log.debug('notification of TWAIN event <%s>' % str(twain_event))
		self.__twain_event_handlers[twain_event]()
		self.__scanner = None
		return
	#---------------------------------------------------
	def _twain_close_datasource(self):
		_log.info("being asked to close data source")
	#---------------------------------------------------
	def _twain_save_state(self):
		_log.info("being asked to save application state")
	#---------------------------------------------------
	def _twain_handle_src_event(self):
		_log.info("being asked to handle device specific event")
	#---------------------------------------------------
	def _twain_handle_transfer_in_memory(self):

		# FIXME: handle several images

		_log.debug('receiving image from TWAIN source')
		_log.debug('image info: %s' % self.__scanner.GetImageInfo())
		_log.debug('image layout: %s' % str(self.__scanner.GetImageLayout()))

		# get image from source
		(external_data_handle, more_images_pending) = self.__scanner.XferImageNatively()
		try:
			# convert DIB to standard bitmap file (always .bmp)
			_twain_module.DIBToBMFile(external_data_handle, self.__filename)
		finally:
			_twain_module.GlobalHandleFree(external_data_handle)
		_log.debug('%s pending images' % more_images_pending)

		# hide the scanner user interface again
#		self.__scanner.HideUI()						# needed ?
#		self.__scanner = None		# not sure why this should be needed, simple_wx does it, though

		self.__done_transferring_image = True
	#---------------------------------------------------
	def _twain_handle_transfer_by_file(self):

		# the docs say this is not required to be implemented
		# therefor we can't use it by default :-(
		# UNTESTED !!!!

		_log.debug('receiving image from TWAIN source')
		_log.debug('image info: %s' % self.__scanner.GetImageInfo())
		_log.debug('image layout: %s' % self.__scanner.GetImageLayout())

		self.__scanner.SetXferFileName(self.__filename)	# FIXME: allow format

		more_images_pending = self.__scanner.XferImageByFile()
		_log.debug('%s pending images' % more_images_pending)

		# hide the scanner user interface again
		self.__scanner.HideUI()
#		self.__scanner = None

		return 
#=======================================================
# SANE handling
#=======================================================
def _sane_import_module():
	global _sane_module
	if _sane_module is None:
		try:
			import sane
		except ImportError:
			_log.exception('cannot import SANE module')
			raise
		_sane_module = sane
		init_result = _sane_module.init()
		_log.info("SANE version: %s" % str(init_result))
		_log.debug('SANE device list: %s' % str(_sane_module.get_devices()))
#=======================================================
class cSaneScanner:

	# for testing uncomment "test" backend in /etc/sane/dll.conf

	_src_manager = None

	def __init__(self, device=None):
		_sane_import_module()

		# FIXME: need to test against devs[x][0]
#		devs = _sane_module.get_devices()
#		if device not in devs:
#			_log.error("device [%s] not found in list of devices detected by SANE" % device)
#			_log.error(str(devs))
#			raise gmExceptions.ConstructorError, msg

		self.__device = device
		_log.info('using SANE device [%s]' % self.__device)

		self.__init_scanner()
	#---------------------------------------------------
	def __init_scanner(self):
		self.__scanner = _sane_module.open(self.__device)

		_log.debug('opened SANE device: %s' % str(self.__scanner))
		_log.debug('SANE device config: %s' % str(self.__scanner.get_parameters()))
		_log.debug('SANE device opts	 : %s' % str(self.__scanner.optlist))
		_log.debug('SANE device opts	 : %s' % str(self.__scanner.get_options()))

		return True
	#---------------------------------------------------
	def close(self):
		self.__scanner.close()
	#---------------------------------------------------
	def acquire_pages_into_files(self, delay=None, filename=None):
		if filename is None:
			filename = gmTools.get_unique_filename(prefix='gmScannedObj-', suffix='.bmp')
		else:
			tmp, ext = os.path.splitext(filename)
			if ext != '.bmp':
				filename = filename + '.bmp'

		filename = os.path.abspath(os.path.expanduser(filename))

		if delay is not None:
			time.sleep(delay)
			_log.debug('some sane backends report device_busy if we advance too fast. delay set to %s sec' % delay)

		_log.debug('Trying to get image from scanner into [%s] !' % filename)
		self.__scanner.start()
		img = self.__scanner.snap()
		img.save(filename)

		return [filename]
	#---------------------------------------------------
	def image_transfer_done(self):
		return True
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
#		except Exception:
#			_log.exception('cannot open SANE scanner')
#			return False
#
#		# Set scan parameters
#		# FIXME: get those from config file
#		#self.__scannercontrast=170 ; self.__scannerbrightness=150 ; self.__scannerwhite_level=190
#		#self.__scannerdepth=6
#		#self.__scannerbr_x = 412.0
#		#self.__scannerbr_y = 583.0

#==================================================
# XSane handling
#==================================================
class cXSaneScanner:

	_FILETYPE = '.png'

	#----------------------------------------------
	def __init__(self):
		# while not strictly necessary it is good to fail early
		# this will tell us fairly safely whether XSane is properly installed
		self._stock_xsanerc = os.path.expanduser(os.path.join('~', '.sane', 'xsane', 'xsane.rc'))
		try:
			open(self._stock_xsanerc, 'r').close()
		except IOError:
			msg = (
				'XSane not properly installed for this user:\n\n'
				' [%s] not found\n\n'
				'Start XSane once before using it with GNUmed.'
			) % self._stock_xsanerc
			raise ImportError(msg)

		# make sure we've got a custom xsanerc for
		# the user to modify manually
		self._gm_custom_xsanerc = os.path.expanduser(os.path.join('~', '.gnumed', 'gm-xsanerc.conf'))
		try:
			open(self._gm_custom_xsanerc, 'r+b').close()
		except IOError:
			_log.info('creating [%s] from [%s]', self._gm_custom_xsanerc, self._stock_xsanerc)
			shutil.copyfile(self._stock_xsanerc, self._gm_custom_xsanerc)

		self.device_settings_file = None
		self.default_device = None
	#----------------------------------------------
	def close(self):
		pass
	#----------------------------------------------
	def acquire_pages_into_files(self, delay=None, filename=None):
		"""Call XSane.

		<filename> name part must have format name-001.ext>
		"""
		if filename is None:
			filename = gmTools.get_unique_filename(prefix = 'gm-scan-')

		name, ext = os.path.splitext(filename)
		filename = '%s-001%s' % (name, cXSaneScanner._FILETYPE)
		filename = os.path.abspath(os.path.expanduser(filename))

		cmd = 'xsane --no-mode-selection --save --force-filename "%s" --xsane-rc "%s" %s %s' % (
			filename,
			self.__get_session_xsanerc(),
			gmTools.coalesce(self.device_settings_file, '', '--device-settings %s'),
			gmTools.coalesce(self.default_device, '')
		)
		normal_exit = gmShellAPI.run_command_in_shell(command = cmd, blocking = True)

		if normal_exit:
			flist = glob.glob(filename.replace('001', '*'))
			flist.sort()
			return flist

		raise OSError(-1, 'error running XSane as [%s]' % cmd)
	#---------------------------------------------------
	def image_transfer_done(self):
		return True
	#----------------------------------------------
	# internal API
	#----------------------------------------------
	def __get_session_xsanerc(self):

		# create an xsanerc for this session
		session_xsanerc = gmTools.get_unique_filename (
			prefix = 'gm-session_xsanerc-',
			suffix = '.conf'
		)
		_log.debug('GNUmed -> XSane session xsanerc: %s', session_xsanerc)

		# our closest bet, might contain umlauts
		enc = gmI18N.get_encoding()
		fread = io.open(self._gm_custom_xsanerc, mode = "rt", encoding = enc)
		fwrite = io.open(session_xsanerc, mode = "wt", encoding = enc)

		paths = gmTools.gmPaths()
		val_dict = {
			'tmp-path': paths.tmp_dir,
			'working-directory': paths.tmp_dir,
			'filename': '<--force-filename>',
			'filetype': cXSaneScanner._FILETYPE,
			'skip-existing-numbers': '1',
			'filename-counter-step': '1',
			'filename-counter-len': '3'
		}

		for idx, line in enumerate(fread):
			line = line.replace('\n', '')
			line = line.replace('\r', '')

			if idx % 2 == 0:			# even lines are keys
				curr_key = line.strip('"')
				fwrite.write('"%s"\n' % curr_key)
			else: 						# odd lines are corresponding values
				try:
					value = val_dict[curr_key]
					_log.debug('replaced [%s] with [%s]', curr_key, val_dict[curr_key])
				except KeyError:
					value = line
				fwrite.write('%s\n' % value)

		fwrite.flush()
		fwrite.close()
		fread.close()

		return session_xsanerc
#==================================================
def get_devices():
	try:
		_twain_import_module()
		# TWAIN does not support get_devices():
		# devices can only be selected from within TWAIN itself
		return None
	except ImportError:
		pass

	if use_XSane:
		# neither does XSane
		return None

	_sane_import_module()
	return _sane_module.get_devices()
#-----------------------------------------------------
def acquire_pages_into_files(device=None, delay=None, filename=None, calling_window=None, xsane_device_settings=None):
	"""Connect to a scanner and return the scanned pages as a file list.

	returns:
		- list of filenames: names of scanned pages, may be []
		- None: unable to connect to scanner
	"""
	try:
		scanner = cTwainScanner(calling_window=calling_window)
		_log.debug('using TWAIN')
	except ImportError:
		if use_XSane:
			_log.debug('using XSane')
			scanner = cXSaneScanner()
			scanner.device_settings_file = xsane_device_settings
			scanner.default_device = device
		else:
			_log.debug('using SANE directly')
			scanner = cSaneScanner(device=device)

	_log.debug('requested filename: [%s]' % filename)
	fnames = scanner.acquire_pages_into_files(filename=filename, delay=delay)
	scanner.close()
	_log.debug('acquired pages into files: %s' % str(fnames))

	return fnames
#==================================================
# main
#==================================================
if __name__ == '__main__':

	if len(sys.argv) > 1 and sys.argv[1] == 'test':

		logging.basicConfig(level=logging.DEBUG)

		print("devices:")
		print(get_devices())

		sys.exit()

		setups = [
			{'dev': 'test:0', 'file': 'x1-test0-1-0001'},
			{'dev': 'test:1', 'file': 'x2-test1-1-0001.bmp'},
			{'dev': 'test:0', 'file': 'x3-test0-2-0001.bmp-ccc'}
		]

		idx = 1
		for setup in setups:
			print("scanning page #%s from device [%s]" % (idx, setup['dev']))
			idx += 1
			fnames = acquire_pages_into_files(device = setup['dev'], filename = setup['file'], delay = (idx*5))
			if fnames is False:
				print("error, cannot acquire page")
			else:
				print(" image files:", fnames)
