#!/usr/bin/env python

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/blobs_hilbert/scan/Attic/scan-med_docs.py,v $
__version__ = "$Revision: 1.21 $"
__license__ = "GPL"
__author__ =	"Sebastian Hilbert <Sebastian.Hilbert@gmx.net>, \
				 Karsten Hilbert <Karsten.Hilbert@gmx.net>"

from wxPython.wx import *
import string, time, shutil, os, sys, os.path, tempfile

# location of our modules
sys.path.append(os.path.join('.', 'modules'))

import gmLog
_log = gmLog.gmDefLog
_log.SetAllLogLevels(gmLog.lData)

import gmCfg, gmI18N
_cfg = gmCfg.gmDefCfgFile

try:
	import twain
	scan_drv = 'wintwain'
except ImportError:
	exc = sys.exc_info()
	_log.LogException('Cannot import WinTWAIN.py.', exc, fatal=0)
	try:
		import sane
		scan_drv = 'linsane'
	except ImportError:
		exc = sys.exc_info()
		_log.LogException('Cannot import linSANE.py.', exc, fatal=0)
		raise _("Can import neither TWAIN nor SANE scanner access library.")

[	wxID_SCANFRAME,
	wxID_LBOX_doc_pages,
	wxID_BTN_del_page,
	wxID_BTN_show_page,
	wxID_BTN_move_page,
	wxID_BTN_save_doc,
	wxID_BTN_acquire_page,
	wxID_PNL_main
] = map(lambda _init_ctrls: wxNewId(), range(8))
#==================================================
class scanFrame(wxFrame):
	# a list holding our objects
	acquired_pages = []
	#----------------------------------------------
	def __init__(self, parent):
		self._init_ctrls(parent)

		# FIXME: dict this !!
		(self.TwainSrcMngr, self.TwainScanner) = (None, None)
		(self.SaneSrcMngr, self.SaneScanner) = (None, None)
		# like this:
		self.acquire_handler = {
			'wintwain': self.__acquire_from_twain,
			'linsane': self.__acquire_from_sane
		}

		# get temp dir path from config file
		self.scan_tmp_dir = None
		tmp = _cfg.get("repositories", "scan_tmp")
		if tmp == None:
			_log.Log(gmLog.lErr, 'Cannot get tmp dir from config file.')
		else:
			tmp = os.path.abspath(os.path.expanduser(tmp))
			if os.path.exists(tmp):
				self.scan_tmp_dir = tmp
		_log.Log(gmLog.lData, 'using tmp dir [%s]' % self.scan_tmp_dir)
	#----------------------------------------------
	def _init_utils(self):
		pass
	#----------------------------------------------
	def _init_ctrls(self, prnt):
		wxFrame.__init__(
			self,
			id = wxID_SCANFRAME,
			name = '',
			parent = prnt,
			pos = wxPoint(275, 184),
			size = wxSize(631, 473),
			style = wxDEFAULT_FRAME_STYLE,
			title = _('Scanning documents')
		)
		self._init_utils()
		self.SetClientSize(wxSize(631, 473))

		#-- main panel -------------
		self.PNL_main = wxPanel(
			id = wxID_PNL_main,
			name = 'PNL_main',
			parent = self,
			pos = wxPoint(0, 0),
			size = wxSize(631, 473),
			style = wxTAB_TRAVERSAL
		)
		self.PNL_main.SetBackgroundColour(wxColour(225, 225, 225))

		#-- "get next page" button -------------
		self.BTN_acquire_page = wxButton(
			id = wxID_BTN_acquire_page,
			label = _('acquire image'),
			name = 'BTN_acquire_page',
			parent = self.PNL_main,
			pos = wxPoint(56, 80),
			size = wxSize(240, 64),
			style = 0
		)
		self.BTN_acquire_page.SetToolTipString(_('acquire the next image from the image source'))
		EVT_BUTTON(self.BTN_acquire_page, wxID_BTN_acquire_page, self.on_acquire_page)

		#-- list box with pages -------------
		self.LBOX_doc_pages = wxListBox(
			choices = [],
			id = wxID_LBOX_doc_pages,
			name = 'LBOX_doc_pages',
			parent = self.PNL_main,
			pos = wxPoint(56, 184),
			size = wxSize(240, 160),
			style = wxLB_SORT,
			validator = wxDefaultValidator
		)
		self.LBOX_doc_pages.SetToolTipString(_('these pages make up the current document'))

		#-- show page button -------------
		self.BTN_show_page = wxButton(
			id = wxID_BTN_show_page,
			label = _('show page'),
			name = 'BTN_show_page',
			parent = self.PNL_main,
			pos = wxPoint(64, 384),
			size = wxSize(80, 22),
			style = 0
		)
		self.BTN_show_page.SetToolTipString(_('display selected part of the document'))
		EVT_BUTTON(self.BTN_show_page, wxID_BTN_show_page, self.on_show_page)

		#-- move page button -------------
		self.BTN_move_page = wxButton(
			id = wxID_BTN_move_page,
			label = _('move page'),
			name = 'BTN_move_page',
			parent = self.PNL_main,
			pos = wxPoint(104, 432),
			size = wxSize(144, 22),
			style = 0
		)
		self.BTN_move_page.SetToolTipString(_('move selected page within document'))
		EVT_BUTTON(self.BTN_move_page, wxID_BTN_move_page, self.on_move_page)

		#-- delete page button -------------
		self.BTN_del_page = wxButton(
			id = wxID_BTN_del_page,
			label = _('delete page'),
			name = 'BTN_del_page',
			parent = self.PNL_main,
			pos = wxPoint(200, 384),
			size = wxSize(80, 22),
			style = 0
		)
		self.BTN_del_page.SetToolTipString(_('delete selected page from document'))
		EVT_BUTTON(self.BTN_del_page, wxID_BTN_del_page, self.on_del_page)

		#-- "save document" button -------------
		self.BTN_save_doc = wxButton(
			id = wxID_BTN_save_doc,
			label = _('save document'),
			name = 'BTN_save_doc',
			parent = self.PNL_main,
			pos = wxPoint(408, 80),
			size = wxSize(152, 344),
			style = 0
		)
		self.BTN_save_doc.SetToolTipString(_('save all currently acquired pages as one document'))
		EVT_BUTTON(self.BTN_save_doc, wxID_BTN_save_doc, self.on_save_doc)

		self.staticText1 = wxStaticText(
			id = -1,
			label = _('document pages'),
			name = 'staticText1',
			parent = self.PNL_main,
			pos = wxPoint(56, 160),
			size = wxSize(152, 16),
			style = 0
		)

		self.staticText2 = wxStaticText(
			id = -1,
			label = '1) scan',
			name = 'staticText2',
			parent = self.PNL_main,
			pos = wxPoint(56, 32),
			size = wxSize(19, 29),
			style = 0
		)
		self.staticText2.SetFont(wxFont(25, wxSWISS, wxNORMAL, wxNORMAL, false, ''))

		self.staticText3 = wxStaticText(
			id = -1,
			label = '2) save',
			name = 'staticText3',
			parent = self.PNL_main,
			pos = wxPoint(408, 32),
			size = wxSize(19, 29),
			style = 0
		)
		self.staticText3.SetFont(wxFont(25, wxSWISS, wxNORMAL, wxNORMAL, false, ''))
	#-----------------------------------
	# event handlers
	#-----------------------------------
	def on_acquire_page(self, event):
		self.acquire_handler[scan_drv]()
	#-----------------------------------
	def on_show_page(self, event):
		page_idx = self.LBOX_doc_pages.GetSelection()

		if page_idx != -1:
			page_fname = self.LBOX_doc_pages.GetClientData(page_idx)

			if not os.path.exists(page_fname):
				_log.Log(gmLog.lErr, 'Cannot display page. File [%s] does not exist !' % page_fname)
				dlg = wxMessageDialog(
					self,
					_('Cannot display page %s. The file\n[%s]\ndoes not exist.' % (page_idx+1, page_fname)),
					_('data error'),
					wxOK | wxICON_ERROR
				)
				dlg.ShowModal()
				dlg.Destroy()
				return None

			import docMime

			mime_type = docMime.guess_mimetype(page_fname)
			viewer_cmd = docMime.get_viewer_cmd(mime_type, page_fname)

			if viewer_cmd == None:
				_log.Log(gmLog.lWarn, "Cannot determine viewer via standard mailcap mechanism. Desperately trying to guess.")
				new_fname = docMime.get_win_fname(mime_type)
				_log.Log(gmLog.lData, "%s -> %s -> %s" % (page_fname, mime_type, new_fname))
				shutil.copyfile(page_fname, new_fname)
				# FIXME: we should only do this on Windows !
				os.startfile(new_fname)
			else:
				_log.Log(gmLog.lData, "%s -> %s -> %s" % (page_fname, mime_type, viewer_cmd))
				os.system(viewer_cmd)
		else:
			dlg = wxMessageDialog(
				self,
				_('You must select a page before you can view it.'),
				_('Attention'),
				wxOK | wxICON_INFORMATION
			)
			dlg.ShowModal()
			dlg.Destroy()
	#-----------------------------------
	def on_del_page(self, event):
		page_idx = self.LBOX_doc_pages.GetSelection()
		if page_idx == -1:
			dlg = wxMessageDialog(
				self,
				_('You must select a page before you can delete it.'),
				_('Attention'),
				wxOK | wxICON_INFORMATION
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None
		else:
			page_fname = self.LBOX_doc_pages.GetClientData(page_idx)

			# 1) del item from self.acquired_pages
			tmp = self.acquired_pages[:page_idx] + self.acquired_pages[(page_idx+1):]
			self.acquired_pages = tmp

			# 2) reload list box
			self.__reload_LBOX_doc_pages()

			# 3) kill file in the file system
			os.remove(page_fname)

			return 1
	#-----------------------------------
	def on_move_page(self, event):
		# 1) get page
		page_idx = self.LBOX_doc_pages.GetSelection()
		if page_idx == -1:
			dlg = wxMessageDialog(
				self,
				_('You must select a page before you can move it around.'),
				_('Attention'),
				wxOK | wxICON_INFORMATION
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		page_fname = self.LBOX_doc_pages.GetClientData(page_idx)
		path, name = os.path.split(page_fname)

		# 2) ask for new position
		new_page_idx = -1
		while new_page_idx == -1:
			dlg = wxTextEntryDialog(
				parent = self,
				message = _('Moving page %s.\n(file %s in %s)\n\nPlease enter the new position for the page !' % ((page_idx+1), name, path)),
				caption = _('new page number'),
				defaultValue = str(page_idx+1)
			)
			btn = dlg.ShowModal()
			dlg.Destroy()
			# move ?
			if  btn == wxID_OK:
				tmp = dlg.GetValue()

				# numeric ?
				if not tmp.isdigit():
					new_page_idx = -1
					continue
				new_page_idx = int(tmp) - 1

				# in range ?
				if new_page_idx not in range(len(self.acquired_pages) - 1):
					new_page_idx = -1
					continue

				# 3) move pages after the new position
				head = self.acquired_pages[:new_page_idx]
				tail = self.acquired_pages[(new_page_idx+1):]
				self.acquired_pages = head + (page_fname,) + tail

				# 5) update list box
				self.__reload_LBOX_doc_pages()

				return 1
			# or cancel moving ?
			elif btn == wxID_CANCEL:
				return 1
	#-----------------------------------
	# internal methods
	#-----------------------------------
	def __reload_LBOX_doc_pages(self):
		if len(self.acquired_pages) > 0:
			self.LBOX_doc_pages.Clear()
			for i in range(len(self.acquired_pages)):
				fname = self.acquired_pages[i]
				path, name = os.path.split(fname)
				self.LBOX_doc_pages.Append(_('page %s (%s in %s)' % (i+1, name, path)), fname)
	#-----------------------------------
	# TWAIN related scanning code
	#-----------------------------------
	def __acquire_from_twain(self):
		_log.Log(gmLog.lInfo, "scanning with TWAIN source")
		# open scanner on demand
		if not self.TwainScanner:
			if not self.__open_twain_scanner():
				dlg = wxMessageDialog(
					self,
					_('Cannot connect to TWAIN source (scanner or camera).'),
					_('TWAIN source error'),
					wxOK | wxICON_ERROR
				)
				dlg.ShowModal()
				dlg.Destroy()
				return None

		self.TwainScanner.RequestAcquire()
	#-----------------------------------
	def __open_twain_scanner(self):
		# did we open the scanner before ?
		if not self.TwainSrcMngr:
			#_log.Log(gmLog.lData, "TWAIN version: %s" % twain.Version())
			# no, so we need to open it now
			# TWAIN talks to us via MS-Windows message queues so we
			# need to pass it a handle to ourselves
			self.TwainSrcMngr = twain.SourceManager(self.GetHandle())
			if not self.TwainSrcMngr:
				_log.Log(gmLog.lData, "cannot get a handle for the TWAIN source manager")
				return None

			# TWAIN will notify us when the image is scanned
			self.TwainSrcMngr.SetCallback(self.on_twain_event)

			_log.Log(gmLog.lData, "TWAIN source manager config: %s" % str(self.TwainSrcMngr.GetIdentity()))

		if not self.TwainScanner:
			self.TwainScanner = self.TwainSrcMngr.OpenSource()
			if not self.TwainScanner:
				_log.Log(gmLog.lData, "cannot open the scanner via the TWAIN source manager")
				return None

			_log.Log(gmLog.lData, "TWAIN data source: %s" % self.TwainScanner.GetSourceName())
			_log.Log(gmLog.lData, "TWAIN data source config: %s" % str(self.TwainScanner.GetIdentity()))
		return 1
	#-----------------------------------
	def on_twain_event(self, event):
		_log.Log(gmLog.lData, 'notification of pending image from TWAIN manager')
		_log.Log(gmLog.lData, 'image info: %s' % self.TwainScanner.GetImageInfo())

		# get from source
		try:
			(external_data_handle, more_images_pending) = self.TwainScanner.XferImageNatively()
		except:
			exc = sys.exc_info()
			_log.LogException('Unable to get global heap image handle !', exc, fatal=1)
			# free external image memory
			twain.GlobalHandleFree(external_data_handle)
			# hide the scanner user interface again
			self.TwainScanner.HideUI()
			return None

		_log.Log(gmLog.lData, '%s pending images' % more_images_pending)

		# make tmp file name
		# for now we know it's bitmap
		# FIXME: should be JPEG, perhaps ?
		tempfile.tempdir = self.scan_tmp_dir
		tempfile.template = 'obj-'
		fname = tempfile.mktemp('.bmp')
		try:
			# convert to bitmap file
			twain.DIBToBMFile(external_data_handle, fname)
		except:
			exc = sys.exc_info()
			_log.LogException('Unable to convert image in global heap handle into file [%s] !' % fname, exc, fatal=1)
			# free external image memory
			twain.GlobalHandleFree(external_data_handle)
			# hide the scanner user interface again
			self.TwainScanner.HideUI()
			return None

		# free external image memory
		twain.GlobalHandleFree(external_data_handle)
		# hide the scanner user interface again
		self.TwainScanner.HideUI()

		# and keep a reference
		self.acquired_pages.append(fname)
		#update list of pages in GUI
		self.__reload_LBOX_doc_pages()

		# FIXME:
		#if more_images_pending:

		return 1
	#-----------------------------------
	# SANE related scanning code
	#-----------------------------------
	def __acquire_from_sane(self):
		_log.Log(gmLog.lInfo, "scanning with SANE source")

		# open scanner on demand
		if not self.SaneScanner:
			if not self.__open_sane_scanner():
				dlg = wxMessageDialog(
					self,
					_('Cannot connect to SANE source (scanner or camera).'),
					_('SANE source error'),
					wxOK | wxICON_ERROR
				)
				dlg.ShowModal()
				dlg.Destroy()
				return None

		# Set scan parameters
		# FIXME: get those from config file
		#scanner.contrast=170 ; scanner.brightness=150 ; scanner.white_level=190
		#scanner.depth=6
		scanner.br_x = 412.0
		scanner.br_y = 583.0

		# make tmp file name
		# for now we know it's bitmap
		# FIXME: should be JPEG, perhaps ?
		# FIXME: get extension from config file
		tempfile.tempdir = self.scan_tmp_dir
		tempfile.template = 'obj-'
		fname = tempfile.mktemp('.jpg')
		try:
			# initiate the scan
			scanner.start()
			# get an Image object
			img = scanner.snap()
			#save image file to disk
			img.save(fname)
			# and keep a reference
			self.acquired_pages.appen(fname)

			# FIXME:
			#if more_images_pending:
		except:
			exc = sys.exc_info()
			_log.LogException('Unable to get image from scanner into [%s] !' % fname, exc, fatal=1)
			return None

		# update list of pages in GUI
		self.__reload_LBOX_doc_pages()
	#-----------------------------------
	def __open_sane_scanner(self):
		# did we open the scanner before ?
		if not self.SaneSrcMngr:
			# no, so we need to open it now
			try:
				init_result = sane.init()
			except:
				exc = sys.exc_info()
				_log.LogException('cannot init SANE', exc, fatal=1)
				self.SaneSrcMngr = None
				return None

			_log.Log(gmLog.lData, "SANE version: %s" % init_result)

		if not self.SaneScanner:
			# FIXME: actually we should use this to remember which device we work with
			devices = []
			devices = sane.get_devices()
			if devices == []:
				_log.Log (gmLog.lErr, "SANE did not find any devices")
				dlg = wxMessageDialog(
					self,
					_('Cannot find any SANE connected devices.'),
					_('SANE device error'),
					wxOK | wxICON_ERROR
				)
				dlg.ShowModal()
				dlg.Destroy()
				return None

			_log.Log(gmLog.lData, "available SANE devices: %s" % devices)

			try:
				# by default use the first device
				self.SaneScanner = sane.open(sane.get_devices()[0][0])
			except:
				exc = sys.exc_info()
				_log.LogException('cannot open SANE scanner', exc, fatal=1)
				return None

			_log.Log(gmLog.lData, 'opened SANE device: %s' % str(scanner))
			_log.Log(gmLog.lData, 'SANE device config: %s' % scanner.get_parameters())
			_log.Log(gmLog.lData, 'SANE device opts:' % scanner.optlist())

		return 1
	#-----------------------------------
	# internal helper methods
	#-----------------------------------
	def __get_ID_mode(self):
		tmp = _cfg.get("scanning", "document_ID_mode")

		if not tmp in ['random', 'consecutive']:
			_log.Log(gmLog.lErr, '"%s" is not a valid document ID generation mode. Falling back to "random".' % tmp)
			return "random"

		_log.Log(gmLog.lData, 'document ID generation mode is "%s"' % tmp)
		return tmp
	#-----------------------------------
	def __get_next_consecutive_ID(self):
		fname = _cfg.get("scanning", "document_ID_file")
		if fname == None:
			_log.Log(gmLog.lErr, 'Cannot get name of file with most recently used document ID from config file')
			return None

		fname = os.path.abspath(os.path.expanduser(fname))

		try:
			ID_file = open(fname, "rb")
		except:
			exc = sys.exc_info()
			_log.LogException('Cannot open file [%s] with most recently used document ID.' % fname, exc, fatal=0)
			return None

		last_ID = ID_file.readline()
		ID_file.close()

		# ask for confirmation of ID
		doc_id = -1
		new_ID = str(int(last_ID) + 1)
		while doc_id < 0:
			dlg = wxTextEntryDialog(
				parent = self,
				message = _('The most recently used document ID was "%s".\nWe would use the ID "%s" for the current document.\nPlease confirm the ID or type in a new numeric ID.\n\nYou should also write down this ID on the documents themselves.' % (last_ID, new_ID)),
				caption = _('document ID'),
				defaultValue = new_ID,
				style = wxOK | wxCentre
			)
			dlg.ShowModal()
			dlg.Destroy()
			tmp = dlg.GetValue()
			# numeric ?
			if not new_ID.isdigit():
				doc_id = -1
			else:
				doc_id = int(new_ID)

		# store new document ID as most recently used one
		try:
			ID_file = open(fname, "wb")
		except:
			exc = sys.exc_info()
			_log.LogException('Cannot open file [%s] with most recently used document ID for storing new ID.' % fname, exc, fatal=0)
			return None
		ID_file.write("%s\n" % new_ID)
		ID_file.close()

		return new_ID
	#-----------------------------------
	def __get_random_ID(self, target_repository):
		# set up temp file environment for creating unique random directory
		tempfile.tempdir = target_repository
		tempfile.template = ""
		# create temp dir name
		dirname = tempfile.mktemp(time.strftime("-%Y%m%d_%H%M%S", time.localtime()))
		# extract name for dir
		tmp = os.path.commonprefix(target_repository, dirname)
		doc_ID = tmp.replace(target_repository, '')

		show_ID = _cfg.get('scanning', 'show_document_ID')
		if show_ID == None:
			_log.Log(gmLog.lWarn, 'Cannot get option from config file.')
			show_ID = "yes"

		if show_ID != "no":
			dlg = wxMessageDialog(
				self,
				_("This is the reference ID for the current document:\n%s\nYou should write this down on the original documents.\n\nIf you don't care about the ID you can switch off this\nmessage in the config file." % doc_ID),
				_('random document ID'),
				wxOK | wxICON_INFORMATION
			)
			dlg.ShowModal()
			dlg.Destroy()

		return doc_ID
	#-----------------------------------
	def __dump_metadata_to_xml(self, aDir):
		# FIMXE: error handling
		content = []

		tag = _cfg.get("metadata", "document_tag")
		content.append('<%s>\n' % tag)

#		tag = _cfg.get("metadata", "ref_tag")
#		doc_ref = self.doc_id_wheel.GetLineText(0)
#		content.append('<%s>%s</%s>\n' % (tag, doc_ref, tag))

		tag = _cfg.get("metadata", "obj_tag")
		for idx in range(len(self.acquired_pages)):
			dirname, fname = os.path.split(self.acquired_pages[idx])
			content.append('<%s>%s</%s>\n' % (tag, fname, tag))

		content.append('</%s>\n' % _cfg.get("metadata", "document_tag"))

		# overwrite old XML metadata file and write new one
		xml_fname = os.path.join(aDir, _cfg.get("metadata", "description"))
		#os.remove(xml_fname)
		xml_file = open(xml_fname, "w")
		map(xml_file.write, content)
		xml_file.close()
		return 1
	#-----------------------------------
	def on_save_doc(self, event):
		return

		# - anything to do ?
		if self.acquired_images == []:
			dlg = wxMessageDialog(
				self,
				_('You must acquire some images before\nyou can save them as a document !'),
				_('missing images'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		# get target repository
		tmp = _cfg.get("repositories", "to_index")
		if tmp == None:
			_log.Log(gmLog.lErr, 'Cannot get target repository for scans from config file.')
			dlg = wxMessageDialog(
				self,
				_('Cannot get target repository from config file.'),
				_('missing config file option'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None
		target_repository = os.path.abspath(os.path.expanduser(tmp))

		# valid dir ?
		if not os.path.exists(target_repository):
			_log.Log(gmLog.lErr, 'Target repository [%s] not accessible.' % target_repository)
			dlg = wxMessageDialog(
				self,
				_('The configured target repository is not accessible.\n[%s]' % target_repository),
				_('invalid config value'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		# get document ID generation mode
		mode = self.__get_ID_mode()

		# get document ID
		if mode == "consecutive":
			doc_id = self.__get_next_consecutive_ID()
		else:
			doc_id = self.__get_random_ID(target_repository)

		# create new directory in target repository
		dirname = os.path.join(target_repository, doc_id)
		if os.path.exists(dirname):
			_log.Log(gmLog.lErr, 'The target repository subdirectory [%s] already exists. Cannot save current document there.' % dirname)
			dlg = wxMessageDialog(
				self,
				_("The target repository subdirectory already exists.\n(%s)\nCannot save current document there." % dirname),
				_('target directory subdirectory'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		try:
			os.mkdir(dirname)
		except:
			exc = sys.exc_info()
			_log.LogException('Cannot create target repository subdirectory [%s]' % dirname, exc, fatal=1)
			dlg = wxMessageDialog(
				self,
				_("Cannot create the target repository subdirectory.\n(%s)" % dirname),
				_('target directory subdirectory'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		# - write XML meta file
		if not self.__dump_metadata_to_xml(target_repository):
			return None

		# - move data files there
#################################################################

		# - write checkpoint file
		# - clean up gui/acquired_images

#		else:
#			full_dir = os.path.join(self.repository, self.doc_id_wheel.GetLineText(0))

#			self.__unlock_for_import(full_dir)
#			self.__clear_doc_fields()
#			self.doc_id_wheel.Clear()


		if self.picList != []:
			# create xml file
			out_file = open(_cfg.get("tmpdir", "tmpdir") + _cfg.get("metadata", "description"),"w")
			tmpdir_content = self.picList
			runs = len(tmpdir_content)
			x=0
			# here come the contents of the xml-file
			out_file.write ("<" + _cfg.get("metadata", "document_tag")+">\n")
			out_file.write ("<" + _cfg.get("metadata", "ref_tag") + ">" + savedir + "</" + _cfg.get("metadata", "ref_tag") + ">\n")
			while x < runs:
				out_file.write ("<image>" + tmpdir_content[x] + ".jpg" + "</image>\n")
				x=x+1
			out_file.write ("</" + _cfg.get("metadata", "document_tag")+">\n")
			out_file.close()

			# move files around
			shutil.copytree(_cfg.get("tmpdir", "tmpdir"),_cfg.get("source", "repositories") + savedir)
			# generate a file to tell import script that we are done here
			out_file = open(_cfg.get("source", "repositories") + savedir + '/' + _cfg.get("metadata", "checkpoint"),"w")
			# refresh
			shutil.rmtree(_cfg.get("tmpdir", "tmpdir"), true)
			os.mkdir(_cfg.get("tmpdir", "tmpdir"))

			self.picList = []	
			self.LBOX_doc_pages = wxListBox(choices = [], id = wxID_LBOX_doc_pages, name = 'LBOX_doc_pages', parent = self.PNL_main, pos = wxPoint(56, 184), size = wxSize(240, 160), style = 0, validator = wxDefaultValidator)
			dlg = wxMessageDialog(self, _('please put down') + savedir + _('on paper copy for reference'),_('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()
		else:
			dlg = wxMessageDialog(self, _('There is nothing to save on disk ? Please aquire images first'),_('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()

#======================================================
class ScanningApp(wxApp):
	def OnInit(self):
		wxInitAllImageHandlers()
		self.main = scanFrame(None)
		self.main.Centre(wxBOTH)
		self.main.Show(true)
		self.SetTopWindow(self.main)
		return true
#-----------------------------------
def main():
	application = ScanningApp(0)
	application.MainLoop()
#======================================================
# main
#------------------------------------------------------
if __name__ == '__main__':
	try:
		main()
	except:
		exc = sys.exc_info()
		_log.LogException('Unhandled exception.', exc, fatal=1)
		raise
