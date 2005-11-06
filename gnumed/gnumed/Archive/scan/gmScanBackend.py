#==================================================
# Shows how to scan a color image into a PIL rgb-image
#
# Get the path set up to find PIL modules if not installed yet:
#import sys ; sys.path.append('../PIL')

#==================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/Archive/scan/Attic/gmScanBackend.py,v $
__version__ = "$Revision: 1.2 $"
__license__ = "GPL"
__author__ =    "Sebastian Hilbert <Sebastian.Hilbert@gmx.net>, \
                 Karsten Hilbert <Karsten.Hilbert@gmx.net>"

#==================================================
import sys, os.path, os, Image, string, time, shutil, tempfile

from Gnumed.pycommon import gmLog, gmExceptions
_log = gmLog.gmDefLog
_log.SetAllLogLevels(gmLog.lData)

#from Gnumed.pycommon import gmI18N

_log.Log(gmLog.lData, __version__)

#from Gnumed.pycommon import gmCfg, gmMimeLib
#_cfg = gmCfg.gmDefCfgFile

_twain_module = None
_sane_module = None
#=======================================================
class cTwainScanner:

	_src_manager = None

	def __init__():
		if not self.__init_twain_module():
			raise gmExceptions.ConstructorError, 'cannot instantiate TWAIN driver class'
	#---------------------------------------------------
	def __init_twain_module(self, calling_window=None):
		global _twain_module
		if _twain_module is None:
			# import module
			try:
				import twain
				_twain_module = twain
			except ImportError:
				_log.LogException('cannot import TWAIN module (WinTWAIN.py)', sys.exc_info())
				return False

			_log.Log(gmLog.lInfo, "TWAIN version: %s" % _twain_module.Version())

		# open scanner manager
		if cTwainScanner._src_manager is None:
			# TWAIN talks to us via MS-Windows message queues so we
			# need to pass it a handle to ourselves
			cTwainScanner._src_manager = _twain_module.SourceManager(calling_window.GetHandle())
			if not cTwainScanner._src_manager:
				_log.Log(gmLog.lErr, "cannot get a handle for the TWAIN source manager")
				return False
			# TWAIN will notify us when the image is scanned
			cTwainScanner._src_manager.SetCallback(self._twain_event_callback)
			_log.Log(gmLog.lData, "TWAIN source manager config: %s" % str(cTwainScanner._src_manager.GetIdentity()))
		return True
	#---------------------------------------------------

	#---------------------------------------------------

def __open_twain_scanner(self):
	if not TwainScanner:
		TwainScanner = TwainSrcMngr.OpenSource()
		if not TwainScanner:
			_log.Log(gmLog.lData, "cannot open the scanner via the TWAIN source manager")
			return None

		_log.Log(gmLog.lData, "TWAIN data source: %s" % TwainScanner.GetSourceName())
		_log.Log(gmLog.lData, "TWAIN data source config: %s" % str(TwainScanner.GetIdentity()))
	return TwainScanner

#=======================================================
class cSaneScanner:

	_src_manager = None

	def __init__():
		if not self.__init_sane_module():
			raise gmExceptions.ConstructorError, 'cannot instantiate SANE driver class'	

		devices = None
		devices = _sane_module.get_devices()
		if devices is None:
			_log.Log(gmLog.lErr, "SANE module did not find any devices")
			raise gmExceptions.ConstructorError, 'cannot instantiate SANE driver class'
		_log.Log(gmLog.lData, 'SANE device list  : %s' % str(_sane_module.get_devices()))

#		try:
#			# by default use the first device
#			# FIXME: room for improvement - option
#			self.__scanner = _sane_module.open(_sane_module.get_devices()[0][0])
#		except:
#			_log.LogException('cannot open SANE scanner', sys.exc_info(), verbose=1)
#			raise gmExceptions.ConstructorError, 'cannot instantiate SANE driver class'

#		_log.Log(gmLog.lData, 'opened SANE device: %s' % str(self.__scanner))
#		_log.Log(gmLog.lData, 'SANE device config: %s' % str(self.__scanner.get_parameters()))
#		_log.Log(gmLog.lData, 'SANE device opts  : %s' % str(self.__scanner.optlist))
#		_log.Log(gmLog.lData, 'SANE device opts  : %s' % str(self.__scanner.get_options()))
	#---------------------------------------------------
	def __init_sane_module(self):
		# import module
		global _sane_module
		if _sane_module is None:
			try:
				import sane
				_sane_module = sane
			except ImportError:
				_log.LogException('cannot import SANE module', sys.exc_info())
				return False
		# open scanner manager
		if cSaneScanner._src_manager is None:
			# no, so we need to open it now
			try:
				init_result = _sane_module.init()
				_log.Log(gmLog.lInfo, "SANE version: %s" % str(init_result))
			except:
				_log.LogException('cannot init SANE module', sys.exc_info(), verbose=1)
				return False
		return True
	#---------------------------------------------------
	def acquire_page_into_file(self, delay=None, filename=None, tmpdir=None):
		if filename is None:
			print "autogeneration of file names not yet supported"
		# supposedly there is a method *.close() but it does not
		# seem to work, therefore I put in the following line (else
		# it reports a busy sane-device on the second and consecutive runs)
		try:
			# by default use the first device
			# FIXME: room for improvement - option
			self.__scanner = _sane_module.open(_sane_module.get_devices()[0][0])
		except:
			_log.LogException('cannot open SANE scanner', sys.exc_info(), verbose=1)
			return False

		_log.Log(gmLog.lData, 'opened SANE device: %s' % str(self.__scanner))
		_log.Log(gmLog.lData, 'SANE device config: %s' % str(self.__scanner.get_parameters()))
		_log.Log(gmLog.lData, 'SANE device opts  : %s' % str(self.__scanner.optlist))
		_log.Log(gmLog.lData, 'SANE device opts  : %s' % str(self.__scanner.get_options()))

		# Set scan parameters
		# FIXME: get those from config file
		#self.__scannercontrast=170 ; self.__scannerbrightness=150 ; self.__scannerwhite_level=190
		#self.__scannerdepth=6
		#self.__scannerbr_x = 412.0
		#self.__scannerbr_y = 583.0
		if delay is not None:
			time.sleep(sleep)
			_log.Log(gmLog.lData, 'some sane backends report device_busy if we advance too fast. delay set to %s sec' % sleep)
		try:
			self.__scanner.start()
			img = self.__scanner.snap()
			img.save(filename)
		except:
			_log.LogException('Unable to get image from scanner into [%s] !' % filename, sys.exc_info(), verbose=1)
			return False
		return True
#=======================================================

#---------------------------------------
# Initialize OS specific image aquisition backend
#---------------------------------------
def initialize_backend():
	global _twain_module
	global _sane_module
	try:
		import twain
		_twain_module = twain
		scan_drv = 'wintwain'
	except ImportError:
		exc = sys.exc_info()
		_log.LogException('Cannot import WinTWAIN.py.', exc, fatal=0)
		try:
			import sane
			_sane_module = sane
			scan_drv = 'linsane'
		except ImportError:
			exc = sys.exc_info()
			_log.LogException('Cannot import SANE.py.', exc, fatal=0)
			_log.Log(gmLog.lErr, "Can import neither TWAIN nor SANE scanner access library.")
			scan_drv=None
		return scan_drv

def get_device_parameters(scan_drv):
	if scan_drv == 'linsane':
		handler = self.__open_sane_scanner()
		params = handler.get_parameters()
		#print 'Device parameters:',
	elif scan_drv == 'wintwain':
		handler = self.__open_twain_scanner()
		#FIXME: complete this
		params = None
	else:
		params = None
	_log.Log(gmLog.lData, 'Device parameters: %s' % params)
	return params
	
def get_device_properties(self):
	pass
	
#-----------------------------------
# TWAIN related scanning code
#-----------------------------------
def twain_event_callback(self, twain_event):
	_log.Log(gmLog.lData, 'notification of TWAIN event <%s>' % str(twain_event))
	return self.twain_event_handler[twain_event]()
#-----------------------------------
def __twain_handle_transfer(self):
	_log.Log(gmLog.lInfo, 'receiving image')
	_log.Log(gmLog.lData, 'image info: %s' % self.TwainScanner.GetImageInfo())

	# get from source
	try:
		(external_data_handle, more_images_pending) = self.TwainScanner.XferImageNatively()
	except:
		_log.LogException('Unable to get global heap image handle !', sys.exc_info(), verbose=1)
		# free external image memory
		_twain_module.GlobalHandleFree(external_data_handle)
		# hide the scanner user interface again
		self.TwainScanner.HideUI()
		return None

	_log.Log(gmLog.lData, '%s pending images' % more_images_pending)

	# make tmp file name
	tempfile.tempdir = self.scan_tmp_dir
	tempfile.template = 'obj-'
	bmp_name = tempfile.mktemp('.bmp')
	fname = bmp_name
	try:
		# convert to bitmap file
		_twain_module.DIBToBMFile(external_data_handle, bmp_name)
	except:
		exc = sys.exc_info()
		_log.LogException('Unable to convert image in global heap handle into file [%s] !' % bmp_name, exc, fatal=1)
		# free external image memory
		_twain_module.GlobalHandleFree(external_data_handle)
		# hide the scanner user interface again
		self.TwainScanner.HideUI()
		return None
	# free external image memory
	_twain_module.GlobalHandleFree(external_data_handle)

	# convert to JPEG ?
	do_jpeg = _cfg.get("scanning", "convert to JPEG")
	if do_jpeg in ["yes", "on"]:
		jpg_name = tempfile.mktemp('.jpg')
		fname = jpg_name
		# get JPEG quality factor
		quality_value = _cfg.get("scanning", "JPEG quality level")
		if quality_value is None:
			_log.Log(gmLog.lWarn, "JPEG quality level not specified in config file, using default level of 75")
			quality_value = 75
		else:
			if quality_value.isdigit():
				quality_value = int(quality_value, 10)
			else:
				_log.Log(gmLog.lWarn, "JPEG quality level [%s] not a number, using default level of 75" % quality_value)
				quality_value = 75
		# do we want progression ?
		progression_flag = _cfg.get("scanning", "progressive JPEG")
		_log.Log(gmLog.lData, "JPEG conversion: quality level: %s, progression: %s" % (quality_value, progression_flag))
		kwds = {}
		kwds['quality'] = quality_value
		if progression_flag in ["yes", "on"]:
			kwds['optimize'] = 1
			kwds['progressive'] = 1
		# actually convert to JPEG
		try:
			Image.open(bmp_name).convert('RGB').save(jpg_name, **kwds)
		except:
			_log.LogException("optimized JPEG write failed, turning off optimization", sys.exc_info(), fatal=0)
			Image.open(bmp_name).convert('RGB').save(jpg_name)
		# remove bitmap (except Windows can't do that sometimes :-(
		try:
			os.remove(bmp_name)
		except:
			_log.LogException("Can't remove bitmap.", sys.exc_info(), fatal=0)

	# hide the scanner user interface again
	self.TwainScanner.HideUI()
	# and keep a reference
	self.acquired_pages.append(fname)
	#update list of pages in GUI
	self.__reload_LBOX_doc_pages()
	# FIXME: if more_images_pending:
	return 1
#-----------------------------------
def __twain_close_datasource():
	_log.Log(gmLog.lData, "being asked to close data source")
	return 1
#-----------------------------------
def __twain_save_state():
	_log.Log(gmLog.lData, "being asked to save application state")
	return 1
#-----------------------------------
def __twain_handle_src_event():
	_log.Log(gmLog.lInfo, "being asked to handle device specific event")
	return 1
#-----------------------------------
def __acquire_from_twain(self):
	_log.Log(gmLog.lInfo, "scanning with TWAIN source")
	# open scanner on demand
	if not TwainScanner:
		if not self.__open_twain_scanner():
			dlg = wxMessageDialog(
				self,
				_('Cannot connect to TWAIN source (scanner or camera).'),
				_('acquiring page'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

	TwainScanner.RequestAcquire()
	return 1
#-----------------------------------
#def __open_twain_scanner(self):
#	(TwainSrcMngr, TwainScanner) = (None, None)
#	# did we open the scanner before ?
#	if not TwainSrcMngr:
#		#_log.Log(gmLog.lData, "TWAIN version: %s" % _twain_module.Version())
#		# no, so we need to open it now
#		# TWAIN talks to us via MS-Windows message queues so we
#		# need to pass it a handle to ourselves
#		TwainSrcMngr = _twain_module.SourceManager(self.GetHandle())
#		if not TwainSrcMngr:
#			_log.Log(gmLog.lData, "cannot get a handle for the TWAIN source manager")
#			return None
#
#		# TWAIN will notify us when the image is scanned
#		TwainSrcMngr.SetCallback(self.twain_event_callback)
#
#		_log.Log(gmLog.lData, "TWAIN source manager config: %s" % str(TwainSrcMngr.GetIdentity()))
#
#	if not TwainScanner:
#		TwainScanner = TwainSrcMngr.OpenSource()
#		if not TwainScanner:
#			_log.Log(gmLog.lData, "cannot open the scanner via the TWAIN source manager")
#			return None
#
#		_log.Log(gmLog.lData, "TWAIN data source: %s" % TwainScanner.GetSourceName())
#		_log.Log(gmLog.lData, "TWAIN data source config: %s" % str(TwainScanner.GetIdentity()))
#	return TwainScanner
#-----------------------------------
# SANE related scanning code
#-----------------------------------
#def __acquire_from_sane(options={'tmpdir':None,'delay':None}):
#	_log.Log(gmLog.lInfo, "scanning with SANE source")
#
#	# supposedly there is a method *.close() but it does not
#	# seem to work, therefore I put in the following line (else
#	# it reports a busy sane-device on the second and consecutive runs)
#	SaneScanner = None
#	# open scanner on demand
#	if not SaneScanner:
#		SaneScanner = __open_sane_scanner()
#		if not SaneScanner:
#			_log.Log(gmLog.lErr, "Cannot connect to SANE source (scanner or camera).")
#			return None
#	# Set scan parameters
#	# FIXME: get those from config file
#	#scanner.contrast=170 ; scanner.brightness=150 ; scanner.white_level=190
#	#scanner.depth=6
#	#SaneScanner.br_x = 412.0
#	#SaneScanner.br_y = 583.0
#	try:
#		# some sane backends report device_busy if we advance too fast
#		sleep = options['delay']
#		if sleep is not None:
#			time.sleep(sleep)
#		_log.Log(gmLog.lData, 'some sane backends report device_busy if we advance too fast. delay set to %s sec' % sleep)
#	except KeyError:
#		pass
#	try:
#		# initiate the scan
#		SaneScanner.start()
#		# get an Image object
#		img = SaneScanner.snap()
#		return img
#	except:
#		exc = sys.exc_info()
#		_log.LogException('Unable to get image from scanner into [%s] !' % fname, exc, fatal=1)
#		return None
#-----------------------------------
#def __open_sane_scanner():
#	# FIXME: dict this !!
#	(SaneSrcMngr, SaneScanner) = (None, None)
#	# did we open the scanner before ?
#	if not SaneSrcMngr:
#		# no, so we need to open it now
#		try:
#			init_result = _sane_module.init()
#		except:
#			exc = sys.exc_info()
#			_log.LogException('cannot init SANE', exc, fatal=1)
#			SaneSrcMngr = None
#			return None
#
#		_log.Log(gmLog.lData, "SANE version: %s" % str(init_result))
#
#	if not SaneScanner:
#		# FIXME: actually we should use this to remember which device we work with
#		devices = []
#		devices = _sane_module.get_devices()
#		if devices == []:
#			_log.Log (gmLog.lErr, "SANE did not find any devices")
#			return None
#
#		_log.Log(gmLog.lData, "available SANE devices: %s" % devices)
#		try:
#			# by default use the first device
#			SaneScanner = _sane_module.open(_sane_module.get_devices()[0][0])
#		except:
#			exc = sys.exc_info()
#			_log.LogException('cannot open SANE scanner', exc, fatal=1)
#			return None
#
#		_log.Log(gmLog.lData, 'SANE device list  : %s' % str(_sane_module.get_devices()))
#		_log.Log(gmLog.lData, 'opened SANE device: %s' % str(SaneScanner))
#		_log.Log(gmLog.lData, 'SANE device config: %s' % str(SaneScanner.get_parameters()))
#		_log.Log(gmLog.lData, 'SANE device opts  : %s' % str(SaneScanner.optlist))
#		_log.Log(gmLog.lData, 'SANE device opts  : %s' % str(SaneScanner.get_options()))
#	return SaneScanner

def acquire_page(options={}):
	scan_drv = "unknown"
	try:
		# if we did not load the scanner driver yet
		if scan_drv == "unknown":
			scan_drv = initialize_backend()
			if scan_drv is None:
				_log.Log (gmLog.lErr, _('Cannot load any scanner driver (SANE or TWAIN).'))
				return None
		# like this:
		acquire_handler = {
		'wintwain': __acquire_from_twain,
		'linsane': __acquire_from_sane
		}
		if scan_drv == 'wintwain':
			self.twain_event_handler = {
				twain.MSG_XFERREADY: self.__twain_handle_transfer,
				twain.MSG_CLOSEDSREQ: self.__twain_close_datasource,
				twain.MSG_CLOSEDSOK: self.__twain_save_state,
				twain.MSG_DEVICEEVENT: self.__twain_handle_src_event
			}
		img = acquire_handler[scan_drv](options)
		if not img:
			_log.Log (gmLog.lErr, _('Failed to get data from scanner'))
			return None
		else:
			return img
	except:
		exc = sys.exc_info()
		_log.LogException('Unhandled exception.', exc, fatal=1)
		raise


if __name__ == '__main__':
	# if we start standalone we should import gmFoo from local copies
	# or remove the dependency on gmFoo
	from Gnumed.pycommon import gmLog
	_log = gmLog.gmDefLog
	_log.SetAllLogLevels(gmLog.lData)
	
	from Gnumed.pycommon import gmI18N

	_log.Log(gmLog.lData, __version__)

	#from Gnumed.pycommon import gmCfg, gmMimeLib
	#_cfg = gmCfg.gmDefCfgFile
	
	#provide some default options for testing
	options = {}
	#options['tmpdir'] = tempfile.gettempdir()
	options['delay'] = 5
	img = acquire_page(options)
	if not img:
		print 'Page could not be acquired. Please check the log file for details on what went wrong'
	else:
		# make tmp file name
		# for now we know it's bitmap
		# FIXME: should be JPEG, perhaps ?
		# FIXME: get extension from config file
		scan_tmp_dir = tempfile.gettempdir()
		_log.Log(gmLog.lData, 'using tmp dir [%s]' % scan_tmp_dir)
		tempfile.tempdir = scan_tmp_dir
		tempfile.template = 'obj-'
		fname = tempfile.mktemp('.jpg')
		# save image file to disk
		img.save(fname)
		# show image
		#img.show()
	
