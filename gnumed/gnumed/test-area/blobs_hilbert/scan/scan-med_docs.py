#!/usr/bin/env python

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/blobs_hilbert/scan/Attic/scan-med_docs.py,v $
__version__ = "$Revision: 1.11 $"
__license__ = "GPL"
__author__ = "\
	Sebastian Hilbert <Sebastian.Hilbert@gmx.net>, \
	Karsten Hilbert <Karsten.Hilbert@gmx.net>"

from wxPython.wx import *
import string, time, shutil, os, sys, os.path, tempfile

# location of our modules
sys.path.append(os.path.join('.', 'modules'))

import gmLog
_log = gmLog.gmDefLog
_log.SetAllLogLevels(gmLog.lData)

import gmCfg, gmI18N
_cfg = gmCfg.gmDefCfg

try:
	import twain
	scan_drv = 'wintwain'
except ImportError:
	import sane
	scan_drv = 'linsane'

[	wxID_SCANFRAME,
	wxID_LBOX_doc_pages,
	wxID_BTN_del_page,
	wxID_BTN_show_page,
	wxID_BTN_move_page,
	wxID_BTN_save_doc,
	wxID_SCANFRAMESCANBUTTON,
	wxID_SCANFRAMESCANWINDOW,
	wxID_PNL_main
] = map(lambda _init_ctrls: wxNewId(), range(9))
#==================================================
class scanFrame(wxFrame):
	page = 0
	selected_pic = ''
	# a dict holding our objects
	acquired_pages = {}
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
		tmp = None
		try:
			tmp = os.path.abspath(os.path.expanduser(_cfg.get("repositories", "scan_tmp")))
		except:
			exc = sys.exc_info()
			_log.LogException('Cannot get tmp dir from config file', exc, fatal=0)
		# but use it only if it exists
		if tmp != None:
			if os.path.exists(tmp):
				tempfile.tempdir = tmp
		# temp files shall start with "obj-"
		tempfile.template = "obj-"
		_log.Log(gmLog.lData, 'using tmp dir [%s]' % tmp)
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

		#-- main window ------------------------
#		self.WIN_main = wxWindow(
#			id = wxID_SCANFRAMESCANWINDOW,
#			name = 'WIN_main',
#			parent = self,
#			pos = wxPoint(0, 0),
#			size = wxSize(631, 473),
#			style = 0
#		)

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
		self.BTN_acquire_image = wxButton(
			id = wxID_SCANFRAMESCANBUTTON,
			label = _('acquire image'),
			name = 'BTN_acquire_image',
			parent = self.PNL_main,
			pos = wxPoint(56, 80),
			size = wxSize(240, 64),
			style = 0
		)
		self.BTN_acquire_image.SetToolTipString(_('acquire the next image from the image source'))
		EVT_BUTTON(self.BTN_acquire_image, wxID_SCANFRAMESCANBUTTON, self.on_acquire_image)

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
		self.BTN_save_doc.SetToolTipString(_('save all currently acquired images as one document'))
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
	def on_acquire_image(self, event):
		_log.Log(gmLog.lData, "trying to acquire image")
		self.acquire_handler[scan_drv]
	#-----------------------------------
	def on_show_page(self, event):
		page_idx = self.LBOX_doc_pages.GetSelection()

		if page_idx != -1:
			page_data = self.LBOX_doc_pages.GetClientData(page_idx)
			page_fname = page_data['file name']

			import docMime

			mime_type = docMime.guess_mimetype(page_fname)
			viewer_cmd = docMime.get_viewer_cmd(mime_type, page_fname)

			if viewer_cmd == None:
				_log.Log(gmLog.lWarn, "Cannot determine viewer via standard mailcap mechanism. Desperately trying to guess.")
				new_fname = docMime.get_win_fname(mime_type)
				_log.Log(gmLog.lData, "%s -> %s -> %s" % (page_fname, mime_type, new_fname))
				shutil.copyfile(page_fname, new_fname)
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
			page_data = self.LBOX_doc_pages.GetClientData(page_idx)
			page_fname = page_data['file name']
			page_seq_ID = page_data['index']

			# 1) del item from self.acquired_pages
			#  - move trailing items forward one position
			for idx in range(page_seq_ID, len(self.acquired_pages)):
				self.acquired_pages[idx] = self.acquired_pages[idx+1]
			#  - remove last item
			del self.acquired_pages[len(self.acquired_pages)]

			# 2) reload list box
			self.__reload_LBOX_doc_pages()

			# 3) kill file in os
			os.remove(page_fname)

			return 1
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
			_log.Log(gmLog.lData, "TWAIN version: %s" % twain.Version())
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
			_log.Log(gmLog.lData, "TWAIN data source config: %s" % str(self.TwainScanner.GetIdentitiy()))
		return 1
	#-----------------------------------
	def on_twain_event(self, event):
		# self.TwainScanner.GetImageInfo()
		_log.Log(gmLog.Data, 'notification of pending image from TWAIN manager')

		# just so we can us fname down below in case tempfile.mktemp() fails
		fname = ""
		try:
			fname = tempfile.mktemp()
			# get from source
			(external_data_handle, more_images_pending) = self.TwainScanner.XferImageNatively()
			# convert to bitmap file
			# FIXME: should be JPEG
			twain.DIBToBMFile(external_data_handle, fname)
			# free external image memory
			twain.GlobalHandleFree(external_data_handle)
			# and keep a reference (put nothing at [0])
			self.acquired_images[len(self.acquired_images)+1] = fname

			# FIXME:
			#if more_images_pending:
		except:
			exc = sys.exc_info()
			_log.LogException('Unable to get image from scanner into [%s] !' % fname, exc, fatal=1)
			# hide the scanner user interface again
			self.TwainScanner.HideUI()
			return None

		# hide the scanner user interface again
		self.TwainScanner.HideUI()

		#update list of pages in GUI
		self.__reload_LBOX_doc_pages()
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

		# just so we can us fname down below in case tempfile.mktemp() fails
		fname = ""
		try:
			# FIXME: get extension from config file
			fname = tempfile.mktemp('.jpg')
			# initiate the scan
			scanner.start()
			# get an Image object
			img = scanner.snap()
			#save image file to disk
			img.save(fname)
			# and keep a reference (put nothing at [0])
			self.acquired_images[len(self.acquired_images)+1] = fname

			# FIXME:
			#if more_images_pending:
		except:
			exc = sys.exc_info()
			_log.LogException('Unable to get image from scanner into [%s] !' % fname, exc, fatal=1)
			return None

		#update list of pages in GUI
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
				dlg = wxMessageDialog(self, _('There is no scanner available'),_('Attention'), wxOK | wxICON_INFORMATION)
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
	# internal methods
	#-----------------------------------
	def __reload_LBOX_doc_pages(self):
		if len(self.acquired_images) > 0:
			self.LBOX_doc_pages.Clear()
			for seq_ID, fname in self.acquired_images.items():
				path, name = os.path.split(fname)
				self.LBOX_doc_pages.Append(_('page %s (%s in %s)') % (seq_ID, name, path), {'index': seq_ID, 'file name': fname})
	#-----------------------------------
	def on_save_doc(self, event):
		return
		if self.picList != []:
			# create xml file
			out_file = open(_cfg.get("tmpdir", "tmpdir") + _cfg.get("metadata", "description"),"w")
			tmpdir_content = self.picList
			runs = len(tmpdir_content)
			x=0
			savedir = time.strftime("%a%d%b%Y%H%M%S", time.localtime())
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
			dlg = wxMessageDialog(self, _('There is nothing to save on disk ? Please aquire images frst'),_('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()
	#-----------------------------------
	def on_move_page(self, event):
		pass
		##current_selection=self.LBOX_doc_pages.GetSelection()
		##if not current_selection == -1:
		##	  self.selected_pic=self.LBOX_doc_pages.GetString(current_selection)
			#picTochange
		##	  print "u want to change pos for :" + self.selected_pic
		##	 dlg = wxTextEntryDialog(self, _('please tell me the desired position for the page - string format : page[x]'),_('alter page position'), _('page'))
		##	  try:
		##		  if dlg.ShowModal() == wxID_OK:
		##			  answer = dlg.GetValue()
		##			  # Your code
		##			  print 'hello'
		##	  finally:
		##		  dlg.Destroy()
		##	  #first rename selected
		##	  tempposition=len(self.picList)+1	  
		##	  self.LBOX_doc_pages.Delete(current_selection)
		##	  self.picList.remove(self.selected_pic)
		##	  print self.picList
		##	  #del page from hdd
		
		##else:
		##	  dlg = wxMessageDialog(self, _('You did not select a page'),_('Attention'), wxOK | wxICON_INFORMATION)
		##	  try:
		##		  dlg.ShowModal()
		##	  finally:
		##		  dlg.Destroy()

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

#======================================================
	#-----------------------------------
#	def savePage(self,im):
#		if len(self.picList) != 0:
#			lastPageInList=self.picList[len(self.picList)-1]
#			biggest_number_strg=lastPageInList.replace(_('page'),'')
#			biggest_number= int(biggest_number_strg) + 1

		# twain specific
#		if scan_drv == 'wintwain':
#			if len(self.picList) == 0:
#				shutil.copy(self.tmpfilename,_cfg.get("tmpdir", "tmpdir") + _('page')+str(1)+'.bmp')
#			else:
#				shutil.copy(self.tmpfilename,_cfg.get("tmpdir", "tmpdir") + _('page') + `biggest_number` +'.bmp')
		# SANE way of life # Write the image out as a JPG file
		# Note : file format is determined by extension ; otherwise specify type
#		else:
#			if len(self.picList) == 0:
#				im.save(_cfg.get("tmpdir", "tmpdir") + _('page')+str(1)+'.jpg')
#				print "I just saved page 1"
				# remove when sane works one day
#				return
#			else:
#				im.save(_cfg.get("tmpdir", "tmpdir") + _('page') + `biggest_number` +'.jpg')
#				print "I just saved" + str(_cfg.get("tmpdir", "tmpdir") + _('page') + `biggest_number` +'.jpg')
	
	#-----------------------------------

#	def UpdatePicList(self):
#		if len(self.picList) == 0:
#			self.LBOX_doc_pages.Append(_('page1'))
#			self.picList.append(_('page1'))
#		else:
#			lastPageInList=self.picList[len(self.picList)-1]
#			biggest_number_strg=lastPageInList.replace(_('page'),'')
#			biggest_number= int(biggest_number_strg) + 1
#			self.LBOX_doc_pages.Append(_('page') + `biggest_number`)
#			self.picList.append(_('page') + `biggest_number`)

