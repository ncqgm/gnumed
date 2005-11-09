#!/usr/bin/env python
#==================================================
"""GnuMed/Archive document scanning.
@todo
use wxTreeCtrl instead of listbox
	should make page reordering easier
use extra toolbar with bitmap buttons for scan,save

"""
#==================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/Archive/scan/Attic/gmScanMedDocs.py,v $
__version__ = "$Revision: 1.7 $"
__license__ = "GPL"
__author__ =    "Sebastian Hilbert <Sebastian.Hilbert@gmx.net>, \
				 Karsten Hilbert <Karsten.Hilbert@gmx.net>"

#==================================================
import sys, os.path, os, Image, string, time, shutil, tempfile

from Gnumed.pycommon import gmLog
_log = gmLog.gmDefLog

if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)
	from Gnumed.pycommon import gmI18N

_log.Log(gmLog.lData, __version__)

from Gnumed.pycommon import gmCfg, gmMimeLib
_cfg = gmCfg.gmDefCfgFile

from Gnumed.pycommon import gmScanBackend

from wxPython.wx import *


#==================================================
[   wxID_LBOX_doc_pages,
	wxID_BTN_del_page,
	wxID_BTN_show_page,
	wxID_BTN_move_page,
	wxID_BTN_save_doc,
	wxID_BTN_acquire_page,
	wxID_PNL_main,
	wxID_PNL_BTN_del_page,
	wxID_PNL_BTN_show_page,
	wxID_PNL_BTN_move_page,
	wxID_PNL_BTN_save_doc,
	wxID_PNL_BTN_acquire_page,
	
] = map(lambda _init_ctrls: wxNewId(), range(12))
#==================================================
class ScanPanel(wxPanel):
	# a list holding our objects
	acquired_pages = []
	#----------------------------------------------
	def __init__(self, parent):
		wxPanel.__init__(self, parent, -1, wxDefaultPosition, wxDefaultSize)

		# get temp dir path from config file
		self.scan_tmp_dir = None
		tmp = _cfg.get("scanning", "tmp")
		if tmp == None:
			_log.Log(gmLog.lErr, 'Cannot get tmp dir from config file.')
		else:
			tmp = os.path.abspath(os.path.expanduser(tmp))
			if os.path.exists(tmp):
				self.scan_tmp_dir = tmp
		_log.Log(gmLog.lData, 'using tmp dir [%s]' % self.scan_tmp_dir)
		
		# -- main panel -----------------------
		self.PNL_main = wxPanel(
			parent = self,
			id = wxID_PNL_main
		)

		# -- "get next page" button -----------
		self.BTN_acquire_page = wxButton(
			name = 'BTN_acquire_page',
			parent = self.PNL_main,
			id = wxID_BTN_acquire_page,
			label = _("acquire image")
		)
		self.BTN_acquire_page.SetToolTipString(_('acquire the next image from the image source'))
		EVT_BUTTON(self.BTN_acquire_page, wxID_BTN_acquire_page, self.on_acquire_page)

		# -- list box with pages --------------
		self.LBOX_doc_pages = wxListBox(
			size = wxSize(300,300),
			choices = [],
			parent = self.PNL_main,
			id = wxID_LBOX_doc_pages,
			style = wxLB_SORT,
			validator = wxDefaultValidator
		)    
		self.LBOX_doc_pages.SetToolTipString(_('these pages make up the current document'))
		
		# -- show page button -----------------
		self.BTN_show_page = wxButton(
			name = 'BTN_show_page',
			parent = self.PNL_main,
			id = wxID_BTN_show_page,
			label = _("show page")
		)
		self.BTN_show_page.SetToolTipString(_('display selected part of the document'))
		EVT_BUTTON(self.BTN_show_page, wxID_BTN_show_page, self.on_show_page)
		
		# -- del page button ------------------
		self.BTN_del_page = wxButton(
			name = 'BTN_del_page',
			parent = self.PNL_main,
			id = wxID_BTN_del_page,
			label = _("delete page")
		)
		self.BTN_del_page.SetToolTipString(_('delete selected page from document'))
		EVT_BUTTON(self.BTN_del_page, wxID_BTN_del_page, self.on_del_page)
		
		# -- move page button -----------------     
		self.BTN_move_page = wxButton(
			name = 'BTN_move_page',
			parent = self.PNL_main,
			id = wxID_BTN_move_page,
			label = _("move page")
		)
		self.BTN_move_page.SetToolTipString(_('move selected page within document'))
		EVT_BUTTON(self.BTN_move_page, wxID_BTN_move_page, self.on_move_page)       
			
		# -- save doc button ------------------
		self.BTN_save_doc = wxButton(
			name = 'BTN_save_doc',
			parent = self.PNL_main,
			id = wxID_BTN_save_doc,
			label = _("save document")
		)
		self.BTN_save_doc.SetToolTipString(_('save all currently acquired pages as one document'))
		EVT_BUTTON(self.BTN_save_doc, wxID_BTN_save_doc, self.on_save_doc)
			
		self.staticText1 = wxStaticText(
			name = 'staticText1',
			parent = self.PNL_main,
			id = -1,
			label = _("document pages")
		)
		self.staticText2 = wxStaticText(
			name = 'staticText2',
			parent = self.PNL_main,
			id = -1,
			label = _("1) scan")
		)
		self.staticText3 = wxStaticText(
			name = 'staticText3',
			parent = self.PNL_main,
			id = -1,
			label = _("2) save")
		)
		self.__set_properties()
		self.__do_layout()
	#-----------------------------------
	def __set_properties(self):
		self.SetTitle(_("scan documents"))
		self.staticText2.SetFont(wxFont(25, wxSWISS, wxNORMAL, wxNORMAL, 0, ""))
		self.staticText3.SetFont(wxFont(25, wxSWISS, wxNORMAL, wxNORMAL, 0, ""))
		self.BTN_acquire_page.SetToolTipString(_("acquire the next image from the image source"))
		self.LBOX_doc_pages.SetToolTipString(_("these pages make up the current document"))
		self.LBOX_doc_pages.SetSelection(0)
		self.BTN_show_page.SetToolTipString(_("display selected part of the document"))
		self.BTN_del_page.SetToolTipString(_("delete selected page from document"))
		self.BTN_move_page.SetToolTipString(_("move selected page within document"))
		self.BTN_save_doc.SetToolTipString(_("save all currently acquired pages as one document"))
	#-----------------------------------
	def __do_layout(self):
		sizer_2 = wxBoxSizer(wxHORIZONTAL)
		grid_sizer_2 = wxGridSizer(2, 2, 0, 0)
	
		szr_left_col = wxBoxSizer(wxVERTICAL)
		szr_left_btns = wxBoxSizer(wxVERTICAL)
		szr_left_btns_top = wxBoxSizer(wxHORIZONTAL)
		
		szr_left_col.Add(self.staticText2, 0, wxBOTTOM, 10)
		szr_left_col.Add(self.BTN_acquire_page, 0, wxEXPAND|wxRIGHT, 20)
		szr_left_col.Add(self.staticText1, 0, wxTOP|wxBOTTOM, 5)
		szr_left_col.Add(self.LBOX_doc_pages, 1, wxEXPAND|wxRIGHT|wxBOTTOM, 20)
	
		szr_left_btns_top.Add(self.BTN_show_page, 0, wxALL, 5)
		szr_left_btns_top.Add(self.BTN_del_page, 0, wxALL, 5)
	
		szr_left_btns.Add(szr_left_btns_top, 0, wxALIGN_CENTER_HORIZONTAL|wxRIGHT, 20) 
		szr_left_btns.Add(self.BTN_move_page, 0, wxALIGN_TOP|wxALIGN_CENTER_HORIZONTAL|wxTOP, 10)
	
		szr_left_col.Add(szr_left_btns, 1, wxALIGN_CENTER_HORIZONTAL, 0)
	
		szr_right_col = wxBoxSizer(wxVERTICAL)
		szr_right_col.Add(self.staticText3, 0, wxBOTTOM, 10)
		szr_right_col.Add(self.BTN_save_doc, 1, wxEXPAND, 0)
	
		grid_sizer_2.Add(szr_left_col, 1, wxEXPAND|wxLEFT, 20)
		grid_sizer_2.Add(szr_right_col, 1, wxEXPAND|wxLEFT|wxRIGHT|wxBOTTOM, 40)
	
		self.PNL_main.SetAutoLayout(1)
		self.PNL_main.SetSizer(grid_sizer_2)
		grid_sizer_2.Fit(self.PNL_main)
		sizer_2.Add(self.PNL_main, 1, wxEXPAND, 0)
		self.SetAutoLayout(1)
		self.SetSizer(sizer_2)
		sizer_2.Fit(self)
		self.Layout()
	
	#-----------------------------------
	# event handlers
	#-----------------------------------
	def on_acquire_page(self, event):
		# make tmp file name
		# for now we know it's bitmap
		# FIXME: should be JPEG, perhaps ?
		# FIXME: get extension from config file
		tempfile.tempdir = self.scan_tmp_dir
		tempfile.template = 'obj-'
		fname = tempfile.mktemp('.jpg')
		# assemble some options to pass to scanner
		options= {}
		options['delay'] = 5
		print options
		img = gmScanBackend.acquire_page(options)
		if img is None:
			_dlg = wxMessageDialog(
				self,
				_('page could not be acquired. Please check the log file for details on what went wrong'),
				_('acquiring page'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None
		else:
			#save image file to disk
			img.save(fname)
			# and keep a reference
			self.acquired_pages.append(fname)
		# update list of pages in GUI
		self.__reload_LBOX_doc_pages()

		return 1
	#-----------------------------------
	def on_show_page(self, event):
		# did user select a page ?
		page_idx = self.LBOX_doc_pages.GetSelection()
		if page_idx == -1:
			dlg = wxMessageDialog(
				self,
				_('You must select a page before you can view it.'),
				_('displaying page'),
				wxOK | wxICON_INFORMATION
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		# now, which file was that again ?
		page_fname = self.LBOX_doc_pages.GetClientData(page_idx)

		(result, msg) = docDocument.call_viewer_on_file(page_fname)
		if not result:
			dlg = wxMessageDialog(
				self,
				_('Cannot display page %s.\n%s') % (page_idx+1, msg),
				_('displaying page'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None
		return 1
	#-----------------------------------
	def on_del_page(self, event):
		page_idx = self.LBOX_doc_pages.GetSelection()
		if page_idx == -1:
			dlg = wxMessageDialog(
				self,
				_('You must select a page before you can delete it.'),
				_('deleting page'),
				wxOK | wxICON_INFORMATION
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None
		else:
			page_fname = self.LBOX_doc_pages.GetClientData(page_idx)

			# 1) del item from self.acquired_pages
			self.acquired_pages[page_idx:(page_idx+1)] = []

			# 2) reload list box
			self.__reload_LBOX_doc_pages()

			# 3) kill file in the file system
			try:
				os.remove(page_fname)
			except:
				exc = sys.exc_info()
				_log.LogException("Cannot delete file.", exc, fatal=0)
				dlg = wxMessageDialog(
					self,
					_('Cannot delete page (file %s).\nSee log for details.') % page_fname,
					_('deleting page'),
					wxOK | wxICON_INFORMATION
				)
				dlg.ShowModal()
				dlg.Destroy()

			return 1
	#-----------------------------------
	def on_move_page(self, event):
		# 1) get page
		old_page_idx = self.LBOX_doc_pages.GetSelection()
		if old_page_idx == -1:
			dlg = wxMessageDialog(
				self,
				_('You must select a page before you can move it around.'),
				_('moving page'),
				wxOK | wxICON_INFORMATION
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		page_fname = self.LBOX_doc_pages.GetClientData(old_page_idx)
		path, name = os.path.split(page_fname)

		# 2) ask for new position
		new_page_idx = -1
		while new_page_idx == -1:
			dlg = wxTextEntryDialog(
				parent = self,
				message = _('Moving original page %s.\n(file %s in %s)\n\nPlease enter the new position for the page !') % ((old_page_idx+1), name, path),
				caption = _('moving page'),
				defaultValue = str(old_page_idx+1)
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
				if new_page_idx not in range(len(self.acquired_pages)):
					new_page_idx = -1
					continue

				# 3) move pages after the new position
				self.acquired_pages[old_page_idx:(old_page_idx+1)] = []
				self.acquired_pages[new_page_idx:new_page_idx] = [page_fname]

				# 5) update list box
				self.__reload_LBOX_doc_pages()

				return 1
			# or cancel moving ?
			elif btn == wxID_CANCEL:
				return 1
	#-----------------------------------
	def on_save_doc(self, event):
		# anything to do ?
		if self.acquired_pages == []:
			dlg = wxMessageDialog(
				self,
				_('You must acquire some images before\nyou can save them as a document !'),
				_('saving document'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		# get target directory
		target_repository = self.__get_target_repository()
		if not target_repository:
			return None

		# get document ID generation mode
		mode = self.__get_ID_mode()
		
		# get document ID
		if mode == "consecutive":
			doc_id = self.__get_next_consecutive_ID()
		else:
			doc_id = self.__get_random_ID(target_repository)

		# create barcode ?
		if self.__do_barcode():
			barcode = self.__generate_barcode(doc_id)
			if not barcode:
				return None
		else:
			barcode = None

		# create new directory in target repository
		doc_dir = self.__make_doc_dir(target_repository, doc_id)
		if not doc_dir:
			return None

		# write XML meta file
		if not self.__dump_metadata_to_xml(doc_dir):
			return None

		# copy data files there
		for i in range(len(self.acquired_pages)):
			old_name = self.acquired_pages[i]
			new_name = os.path.join(doc_dir, os.path.basename(old_name))
			try:
				shutil.copyfile(old_name, new_name)
			except:
				exc = sys.exc_info()
				_log.LogException("Can't move file [%s] into target repository [%s]." % (old_name, new_name), exc, fatal = 1)
				dlg = wxMessageDialog(
					self,
					_('Cannot copy page to target directory\n(%s -> %s).') % (old_name, new_name),
					_('saving document'),
					wxOK | wxICON_ERROR
				)
				dlg.ShowModal()
				dlg.Destroy()
				return None

		# unlock the directory for indexing
		if not self.__unlock_for_indexing(doc_dir):
			return None

		# remove old data files
		for i in range(len(self.acquired_pages)):
			old_name = self.acquired_pages[i]
			try:
				os.remove(old_name)
			except:
				exc = sys.exc_info()
				_log.LogException("Cannot remove source file [%s]." % old_name, exc, fatal = 0)

		# clean up gui/acquired_pages
		self.acquired_pages = []
		self.__reload_LBOX_doc_pages()

		# finally show doc ID for copying down on paper
		self.__show_doc_ID(doc_id)

		return 1
	#-----------------------------------
	# internal methods
	#-----------------------------------
	def __reload_LBOX_doc_pages(self):
		self.LBOX_doc_pages.Clear()
		if len(self.acquired_pages) > 0:    
			for i in range(len(self.acquired_pages)):
				fname = self.acquired_pages[i]
				path, name = os.path.split(fname)
				self.LBOX_doc_pages.Append(_('page %s (%s in %s)' % (i+1, name, path)), fname)
	
	#-----------------------------------
	# internal helper methods
	#-----------------------------------
	def __do_barcode(self):
		tmp = _cfg.get("scanning", "generate barcode")
		_log.Log(gmLog.lData, 'document barcode generation flag: <%s>' % tmp)
		if tmp in ['on', 'yes']:
			return 1
		else:
			return None
	#-----------------------------------
	def __generate_barcode(self, doc_id):
		tmp = _cfg.get("scanning", "barcode generation command")
		if not tmp:
			_log.Log(gmLog.lErr, 'Cannot get barcode generation command from config file.')
			return None

		if tmp.count("%s") == 1:
			barcode_cmd = tmp % doc_id
		else:
			barcode_cmd = tmp

		aPipe = os.popen(barcode_cmd, "w")
		if aPipe == None:
			_log.Log(gmLog.lData, "Cannot open pipe to [%s]." % barcode_cmd)
			return None

		if tmp.count("%s") != 1:
			aPipe.write('"%s"\n' % doc_id)

		barcode = aPipe.readline()
		ret_code = aPipe.close()

		if ret_code == None and barcode != "":
			return barcode
		else:
			_log.Log(gmLog.lErr, "Something went awry while calling `%s`." % barcode_cmd)
			_log.Log(gmLog.lErr, '%s (%s): exit(%s) -> <%s>' % (os.name, sys.platform, ret_code, barcode), gmLog.lCooked)
			return None
	#-----------------------------------
	def __get_ID_mode(self):
		tmp = _cfg.get("scanning", "document ID mode")

		if not tmp in ['random', 'consecutive']:
			_log.Log(gmLog.lErr, '"%s" is not a valid document ID generation mode. Falling back to "random".' % tmp)
			return "random"

		_log.Log(gmLog.lData, 'document ID generation mode is "%s"' % tmp)
		return tmp
	#-----------------------------------
	def __get_next_consecutive_ID(self):
		fname = _cfg.get("scanning", "document ID file")
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
				message = _('The most recently used document ID was <%s>.\nWe would use the ID <%s> for the current document.\nPlease confirm the ID or type in a new numeric ID.') % (last_ID, new_ID),
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
			_log.LogException('Cannot open file [%s] storing the most recently used document ID for saving the new ID.' % fname, exc, fatal=0)
			return None
		ID_file.write("%s\n" % new_ID)
		ID_file.close()

		return new_ID
	#-----------------------------------
	def __get_random_ID(self, aTarget):
		# set up temp file environment for creating unique random directory
		tempfile.tempdir = aTarget
		tempfile.template = ""
		# create temp dir name
		dirname = tempfile.mktemp(suffix = time.strftime(".%Y%m%d-%H%M%S", time.localtime()))
		# extract name for dir
		path, doc_ID = os.path.split(dirname)

		return doc_ID
	#-----------------------------------
	def __show_doc_ID(self, anID):
		show_ID = _cfg.get('scanning', 'show document ID')
		if show_ID == None:
			_log.Log(gmLog.lWarn, 'Cannot get option from config file.')
			show_ID = "yes"

		if show_ID != "no":
			dlg = wxMessageDialog(
				self,
				_("This is the reference ID for the current document:\n<%s>\nYou should write this down on the original documents.\n\nIf you don't care about the ID you can switch off this\nmessage in the config file.") % anID,
				_('document ID'),
				wxOK | wxICON_INFORMATION
			)
			dlg.ShowModal()
			dlg.Destroy()
	#-----------------------------------
	def __dump_metadata_to_xml(self, aDir):
		# FIXME: error handling
		content = []

		tag = _cfg.get("metadata", "document_tag")
		content.append('<%s>\n' % tag)

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
	def __get_target_repository(self):
		"""Retrieve and validate target repository configuration."""
		tmp = _cfg.get("index", "repository")
		if tmp == None:
			_log.Log(gmLog.lErr, 'Cannot get target repository for scans from config file.')
			dlg = wxMessageDialog(
				self,
				_('Cannot get target repository from config file.'),
				_('invalid configuration'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		# valid dir ?
		if not os.path.exists(tmp):
			_log.Log(gmLog.lErr, 'Target repository [%s] not accessible.' % tmp)
			dlg = wxMessageDialog(
				self,
				_('The configured target repository is not accessible.\n[%s]') % tmp,
				_('invalid configuration'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		return tmp
	#-----------------------------------
	def __make_doc_dir(self, repository, doc_dir):
		"""Make new document directory in target repository."""
		dirname = os.path.join(repository, doc_dir)
		if os.path.exists(dirname):
			_log.Log(gmLog.lErr, 'The subdirectory [%s] already exists in the repository [%s]. Cannot save current document there.' % (doc_dir, repository))
			dlg = wxMessageDialog(
				self,
				_('The subdirectory [%s] already exists in the repository [%s].\nCannot save current document there.') % (doc_dir, repository),
				_('saving document'),
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
				_("Cannot create the target repository subdirectory.\n(%s)") % dirname,
				_('saving document'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		return dirname
	#-----------------------------------
	def __unlock_for_indexing(self, aDir):
		"""Write checkpoint file so indexing can start."""
		can_index_file = _cfg.get('index', 'checkpoint file')
		if not can_index_file:
			dlg = wxMessageDialog(
				self,
				_('You must specify a checkpoint file for indexing in the config file.\nUse option <can index> in group [index].'),
				_('saving document'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		fullname = os.path.join(aDir, can_index_file)
		try:
			f = open(fullname, "wb")
		except:
			exc = sys.exc_info()
			_log.LogException("Cannot lock target directory with checkpoint file [%s]." % fullname, exc, fatal = 1)
			dlg = wxMessageDialog(
				self,
				_('Cannot lock target directory !\ncheckpoint file: %s.') % fullname,
				_('saving document'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None
		f.close()
		return 1
#======================================================
# main
#------------------------------------------------------
if __name__ == '__main__':
	if _cfg is None:
		_log.Log(gmLog.lErr, "Cannot run without config file.")
		sys.exit("Cannot run without config file.")
	try:
		application = wxPyWidgetTester(size=(800,600))
		application.SetWidget(ScanPanel)
		application.MainLoop()
	except:
		exc = sys.exc_info()
		_log.LogException('Unhandled exception.', exc, fatal=1)
		raise
else:
	import gmPlugin,images_Archive_plugin

class gmScanMedDocs(gmPlugin.wxNotebookPlugin):
		def name (self):
			return _("Scan")

		def GetWidget (self, parent):
			return ScanPanel (parent)

		def MenuInfo (self):
			return ('tools', _('&scan documents'))
			
		def DoToolbar (self, tb, widget):
			tool1 = tb.AddTool(
				wxID_PNL_BTN_acquire_page,
				images_Archive_plugin.getcontentsBitmap(),
				shortHelpString=_("acquire image"),
				isToggle=false
			)
			EVT_TOOL (tb, wxID_PNL_BTN_acquire_page, widget.on_acquire_page)
			
			# --------------------------------------------------------------
			tool1 = tb.AddTool(
				wxID_PNL_BTN_save_doc,
				images_Archive_plugin.getsaveBitmap(),
				shortHelpString=_("save document"),
				isToggle=false
			)
			EVT_TOOL (tb, wxID_PNL_BTN_save_doc, widget.on_save_doc)
			
			# -------------------------------------------------------------
			tool1 = tb.AddTool(
				wxID_PNL_BTN_del_page,
				images_Archive_plugin.getcontentsBitmap(),
				shortHelpString=_("delete page"),
				isToggle=false
			)
			EVT_TOOL (tb, wxID_PNL_BTN_del_page, widget.on_del_page)
			
			# -------------------------------------------------------------
			tool1 = tb.AddTool(
				wxID_PNL_BTN_show_page,
				images_Archive_plugin.getreportsBitmap(),
				shortHelpString=_("show page"),
				isToggle=false
			)
			EVT_TOOL (tb, wxID_PNL_BTN_show_page, widget.on_show_page)
	
			# -------------------------------------------------------------
			tool1 = tb.AddTool(
				wxID_PNL_BTN_move_page,
				images_Archive_plugin.getsort_A_ZBitmap(),
				shortHelpString=_("move page"),
				isToggle=false
			)
			EVT_TOOL (tb, wxID_PNL_BTN_move_page, widget.on_move_page)
		
		def ReceiveFocus(self):
			self.DoStatusText()
				
		def DoStatusText (self):
			# FIXME: people want an optional beep and an optional red backgound here
			#set_statustext = gb['main.statustext']
			txt = _('1:acquire some pages 2:save document') 
			if not self._set_status_txt(txt):
				return None
			return 1
	

#======================================================
# $Log: gmScanMedDocs.py,v $
# Revision 1.7  2005-11-09 10:46:11  ncq
# - cleanup
#
# Revision 1.6  2005/11/05 15:59:29  shilbert
# - scan functions were moved out to separate library --> gmScanBackend.py
#
# Revision 1.5  2005/09/27 20:22:44  ncq
# - a few wx2.6 fixes
#
# Revision 1.4  2004/02/25 09:46:19  ncq
# - import from pycommon now, not python-common
#
# Revision 1.3  2003/11/09 16:15:34  shilbert
# - plugin makes use of GNUmed's toolbar and statusbar
#
# Revision 1.2  2003/05/06 13:04:42  ncq
# - temporary fix to make it run standalone from gnumed/Archive/scan/
#
# Revision 1.1  2003/04/13 13:47:22  ncq
# - moved here from test_area
#
# Revision 1.21  2003/01/12 13:24:02  ncq
# - bmp to jpg conversion needs convert(RGB) at times
#
# Revision 1.20  2003/01/06 13:51:57  ncq
# - jpeg.progression seems to only work if jpeg.optimize works, too
#
# Revision 1.19  2002/12/28 23:06:15  ncq
# - *_name -> fname, various typos
#
# Revision 1.18  2002/12/28 22:10:21  ncq
# - Windows can't remove files sometimes
#
# Revision 1.17  2002/12/28 21:50:39  ncq
# - work around failing PIL.jpeg.optimize on files larger than the buffer
#
# Revision 1.16  2002/12/28 21:40:17  ncq
# - quality_value needs to be int()
#
# Revision 1.15  2002/12/27 11:17:00  ncq
# - implemented conversion to JPEG in TWAIN, too
#
# Revision 1.14  2002/12/08 12:40:54  ncq
# - fixed wxID list off by one
#
# Revision 1.13  2002/12/05 15:19:25  ncq
# - based on sizers now
#
# Revision 1.12  2002/11/18 16:59:08  ncq
# - further fixes by Basti (sane, barcode)
#
# Revision 1.11  2002/11/17 19:36:37  ncq
# - final fixes by Basti
#
# Revision 1.10  2002/11/17 18:24:50  ncq
# - str() needed in logging
#
# Revision 1.9  2002/11/17 18:17:43  ncq
# - sane + plugin fixes
#
# Revision 1.8  2002/11/17 17:09:43  ncq
# - yet more sane fixes
#
# Revision 1.7  2002/11/17 17:07:03  ncq
# - various sane related fixes
#
# Revision 1.6  2002/11/17 16:24:13  ncq
# - sane.* -> _sane.*
#
# Revision 1.5  2002/10/11 10:20:37  ncq
# - on demand loading of scanner library so we can at least
#   start on machines without SANE or TWAIN
#
# Revision 1.4  2002/10/08 21:05:48  ncq
# - it is group scanning, not scan
#
# Revision 1.3  2002/10/08 20:55:34  ncq
# - sorry for the cruft
#
# Revision 1.2  2002/10/08 20:54:26  ncq
# - clean up
# - use GNU barcode via pipe
#
# Revision 1.1  2002/10/06 23:25:49  ncq
# - scan-med_docs converted to using sizers
# - prepared for becoming a GnuMed plugin
#
# Revision 1.31  2002/09/30 08:13:36  ncq
# - unify show_doc_ID
#
# Revision 1.30  2002/09/29 16:06:26  ncq
# - cleaned up config file
#
# Revision 1.29  2002/09/16 23:20:58  ncq
# - added missing _()
#
# Revision 1.28  2002/09/13 10:46:04  ncq
# - change _ to - in random ID mode
#
# Revision 1.27  2002/09/12 23:51:15  ncq
# - close last known bug on moving pages - cannot move to end of list
#
# Revision 1.26  2002/09/12 20:43:42  ncq
# - import docDocument
#
# Revision 1.25  2002/09/12 20:42:22  ncq
# - fix double scan bug
# - move call_viewer into docDocument
#
# Revision 1.24  2002/09/10 21:18:12  ncq
# - saving/displaying now works
#
# Revision 1.23  2002/09/10 17:50:26  ncq
# - try this
#
