#!/usr/bin/env pythoncv

"""GnuMed xDT viewer.

TODO:

- popup menu on right-click
  - import this line
  - import all lines like this
  - search
  - print
  - ...
- on plugin.receivefocus():
     if not self.file_loaded:
	 	load file

- connect to gmDispatcher.patient_changed -> on signal check for patient file
  and parse in thread

"""
#=============================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/shilbert/Attic/gmXdtViewer.py,v $
# $Id: gmXdtViewer.py,v 1.9 2003-08-24 10:16:45 shilbert Exp $
__version__ = "$Revision: 1.9 $"
__author__ = "S.Hilbert, K.Hilbert"

import sys, os, string, fileinput, linecache
# location of our modules
if __name__ == "__main__":
	sys.path.append(os.path.join('.', 'modules'))
	sys.path.append(os.path.join('.', 'business'))

import gmLog
_log = gmLog.gmDefLog
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)
_log.Log(gmLog.lData, __version__)

if __name__ == "__main__":
	import gmI18N
	import gmXdtToolsLib
	
import gmExceptions

from gmGuiHelpers import gm_show_error

from wxPython.wx import *
from wxPython.lib.mixins.listctrl import wxColumnSorterMixin, wxListCtrlAutoWidthMixin

from gmXdtMappings import xdt_id_map, xdt_map_of_content_maps
from gmXdtObjects import xdtPatient


#=============================================================================
class gmXdtListCtrl(wxListCtrl, wxListCtrlAutoWidthMixin):
	def __init__(self, parent, ID, pos=wxDefaultPosition, size=wxDefaultSize, style=0):
		wxListCtrl.__init__(self, parent, ID, pos, size, style)
		wxListCtrlAutoWidthMixin.__init__(self)
#=============================================================================
class gmXdtViewerPanel(wxPanel):
	def __init__(self, parent, aFileName = None):
		self.filename = aFileName

		wxPanel.__init__(self, parent, -1, style=wxWANTS_CHARS)

		# our actual list
		tID = wxNewId()
		self.list = gmXdtListCtrl(
			self,
			tID,
			style=wxLC_REPORT|wxSUNKEN_BORDER|wxLC_VRULES
		)#|wxLC_HRULES)

		self.list.InsertColumn(0, _("XDT field"))
		self.list.InsertColumn(1, _("XDT field content"))

		# set up events
		EVT_SIZE(self, self.OnSize)

		EVT_LIST_ITEM_SELECTED(self, tID, self.OnItemSelected)
		EVT_LIST_ITEM_DESELECTED(self, tID, self.OnItemDeselected)
		EVT_LIST_ITEM_ACTIVATED(self, tID, self.OnItemActivated)
		EVT_LIST_DELETE_ITEM(self, tID, self.OnItemDelete)

		EVT_LIST_COL_CLICK(self, tID, self.OnColClick)
		EVT_LIST_COL_RIGHT_CLICK(self, tID, self.OnColRightClick)
#		EVT_LIST_COL_BEGIN_DRAG(self, tID, self.OnColBeginDrag)
#		EVT_LIST_COL_DRAGGING(self, tID, self.OnColDragging)
#		EVT_LIST_COL_END_DRAG(self, tID, self.OnColEndDrag)

		EVT_LEFT_DCLICK(self.list, self.OnDoubleClick)
		EVT_RIGHT_DOWN(self.list, self.OnRightDown)

		if wxPlatform == '__WXMSW__':
			EVT_COMMAND_RIGHT_CLICK(self.list, tID, self.OnRightClick)
		elif wxPlatform == '__WXGTK__':
			EVT_RIGHT_UP(self.list, self.OnRightClick)
	#------------------------------------------------------------------------
	def populate_list(self, aFile = None):
		# if file name supplied, use it
		if aFile is not None:
			self.filename = aFile

		# sanity check
		if not os.path.isfile(self.filename):
			gm_show_error(
				_('[%s] is not the name of a valid file.\nCannot parse XDT data from it.' % self.filename),
				_('parsing XDT file')
			)
			return None

		# populate list
		items = self.__decode_xdt()
		for item_idx in range(len(items),0,-1):
			data = items[item_idx]
			idx = self.list.InsertItem(info=wxListItem())
			self.list.SetStringItem(index=idx, col=0, label=data[0])
			self.list.SetStringItem(index=idx, col=1, label=data[1])
			#self.list.SetItemData(item_idx, item_idx)

		# re-aspect
		self.list.SetColumnWidth(0, wxLIST_AUTOSIZE)
		self.list.SetColumnWidth(1, wxLIST_AUTOSIZE)

		# show how to select an item
		#self.list.SetItemState(5, wxLIST_STATE_SELECTED, wxLIST_STATE_SELECTED)

		# show how to change the colour of a couple items
		#item = self.list.GetItem(1)
		#item.SetTextColour(wxBLUE)
		#self.list.SetItem(item)
		#item = self.list.GetItem(4)
		#item.SetTextColour(wxRED)
		#self.list.SetItem(item)

		self.currentItem = 0
	#-------------------------------------------------------------------------
	def __decode_xdt(self):
		if self.filename is None:
			_log.Log(gmLog.lErr, "Need name of file to parse !")
			return None

		items = {}
		i = 1
		for line in fileinput.input(self.filename):
			# remove trailing CR and/or LF
			line = string.replace(line,'\015','')
			line = string.replace(line,'\012','') 
			length ,ID, content = line[:3], line[3:7], line[7:]

			try:
				left = xdt_id_map[ID]
			except KeyError:
				left = ID

			try:
				right = xdt_map_of_content_maps[ID][content]
			except KeyError:
				right = content

			items[i] = (left, right)
			i = i + 1

		fileinput.close()
		return items
	#-------------------------------------------------------------------------
	def OnRightDown(self, event):
		self.x = event.GetX()
		self.y = event.GetY()
		item, flags = self.list.HitTest((self.x, self.y))
		if flags & wxLIST_HITTEST_ONITEM:
			self.list.Select(item)
		event.Skip()
	#-------------------------------------------------------------------------
	def getColumnText(self, index, col):
		item = self.list.GetItem(index, col)
		return item.GetText()
	#-------------------------------------------------------------------------
	def OnItemSelected(self, event):
		self.currentItem = event.m_itemIndex
	#-------------------------------------------------------------------------
	def OnItemDeselected(self, evt):
		item = evt.GetItem()

		# Show how to reselect something we don't want deselected
#		if evt.m_itemIndex == 11:
#			wxCallAfter(self.list.SetItemState, 11, wxLIST_STATE_SELECTED, wxLIST_STATE_SELECTED)
	#-------------------------------------------------------------------------
	def OnItemActivated(self, event):
		self.currentItem = event.m_itemIndex
	#-------------------------------------------------------------------------
	def OnItemDelete(self, event):
		pass
	#-------------------------------------------------------------------------
	def OnColClick(self, event):
		pass
	#-------------------------------------------------------------------------
	def OnColRightClick(self, event):
		item = self.list.GetColumn(event.GetColumn())
	#-------------------------------------------------------------------------
#	def OnColBeginDrag(self, event):
#		pass
	#-------------------------------------------------------------------------
#	def OnColDragging(self, event):
#		pass
	#-------------------------------------------------------------------------
#	def OnColEndDrag(self, event):
#		pass
	#-------------------------------------------------------------------------
	def OnDoubleClick(self, event):
		event.Skip()
	#-------------------------------------------------------------------------
	def OnRightClick(self, event):
		return
		menu = wxMenu()
		tPopupID1 = 0
		tPopupID2 = 1
		tPopupID3 = 2
		tPopupID4 = 3
		tPopupID5 = 5

		# Show how to put an icon in the menu
		item = wxMenuItem(menu, tPopupID1,"One")
		item.SetBitmap(images.getSmilesBitmap())

		menu.AppendItem(item)
		menu.Append(tPopupID2, "Two")
		menu.Append(tPopupID3, "ClearAll and repopulate")
		menu.Append(tPopupID4, "DeleteAllItems")
		menu.Append(tPopupID5, "GetItem")
		EVT_MENU(self, tPopupID1, self.OnPopupOne)
		EVT_MENU(self, tPopupID2, self.OnPopupTwo)
		EVT_MENU(self, tPopupID3, self.OnPopupThree)
		EVT_MENU(self, tPopupID4, self.OnPopupFour)
		EVT_MENU(self, tPopupID5, self.OnPopupFive)
		self.PopupMenu(menu, wxPoint(self.x, self.y))
		menu.Destroy()
		event.Skip()
	#-------------------------------------------------------------------------
	def OnPopupOne(self, event):
		print "FindItem:", self.list.FindItem(-1, "Roxette")
		print "FindItemData:", self.list.FindItemData(-1, 11)
	#-------------------------------------------------------------------------
	def OnPopupTwo(self, event):
		pass
	#-------------------------------------------------------------------------
	def OnPopupThree(self, event):
		self.list.ClearAll()
		wxCallAfter(self.PopulateList)
		#wxYield()
		#self.PopulateList()
	#-------------------------------------------------------------------------
	def OnPopupFour(self, event):
		self.list.DeleteAllItems()
	#-------------------------------------------------------------------------
	def OnPopupFive(self, event):
		item = self.list.GetItem(self.currentItem)
		print item.m_text, item.m_itemId, self.list.GetItemData(self.currentItem)
	#-------------------------------------------------------------------------
	def OnSize(self, event):
		w,h = self.GetClientSizeTuple()
		self.list.SetDimensions(0, 0, w, h)

#======================================================
def _preprocess_file(afile,aCfg,apatlst,apatdir):
	# file valid ?
	if not os.path.isfile(afile):
		gm_show_error (
			_('XDT file [%s] not found. Aborting.' % afile),
			_('preprocessing XDT file'),
			gmLog.lErr
		)
		return None
	# check how many patients are in the file
	pats = gmXdtToolsLib.xdt_get_pats(afile)
	nr_pats = len(pats)
	# no patients
	if nr_pats == 0:
		gm_show_error(
			_('File [%s] does not contain any XDT formatted patient records. Aborting.' % afile),
			_('preprocessing XDT file')
		)
		return None
	# more than one patient
	selected_pat_file = afile
	if nr_pats > 1:
		# standalone allows multiple-patient files
		selected_pat_file = _split_and_select_pat(pats, afile, aCfg , apatlst, apatdir)
		if selected_pat_file is None:
			return None
	return selected_pat_file
#---------------------
def _split_and_select_pat(pats_in_file = None, afile = None , aCfg = None , apatlst = None, apatdir = None):
	# plugin handles single-patient files only
	if __name__ != '__main__':
		gm_show_error (
			_('The XDT file [%s] contains more than one patient.\nThe GnuMed plugin mode does not handle such XDT files.\nPlease use the standalone version to split the file by patient.') % afile,
			_('parsing XDT file'),
			gmLog.lErr
		)
		return None

	do_not_split = _("show as is")
	do_split = _("split by patient and let me select one")

	# ask user what to do
	dlg = wxSingleChoiceDialog(
		parent = NULL,
		message = _("The xDT file contains data on several patients.\n\nHow would you like to proceed ?"),
		caption = _("parsing XDT file"),
		choices = [do_not_split, do_split],
		style = wxOK | wxCANCEL
	)
	btn_pressed = dlg.ShowModal()
	dlg.Destroy()

	# user cancelled
	if btn_pressed == wxID_CANCEL:
		return None

	# user wants to see entire file
	choice = dlg.GetStringSelection()
	_log.Log(gmLog.lData, 'multiple patients in file: %s' % choice)
	if choice == do_not_split:
		return afile

	# user wants to split file by patient
	
	if not gmXdtToolsLib.split_xdt_file(afile,apatlst,aCfg):
		gm_show_error (
			_('Cannot split XDT file [%s] by patient.\nShowing file as is.'),
			_('parsing XDT file'),
			gmLog.lErr
		)
		return 1

	if pats_in_file is None:
		pats_in_file = gmXdtToolsLib.xdt_get_pats(afile)
	pat_select_list = []
	for pat_id in pats_in_file.keys():
		pat_select_list.append('%s:%s' % (pat_id, pats_in_file[pat_id]))
	dlg = wxSingleChoiceDialog (
		parent = NULL,
		message = _("Please select the patient you want to display."),
		caption = _("parsing XDT file"),
		choices = pat_select_list,
		style = wxOK | wxCANCEL
	)
	btn_pressed = dlg.ShowModal()
	dlg.Destroy()

	# user cancelled
	if btn_pressed == wxID_CANCEL:
		return None

	pat_selected = dlg.GetStringSelection()
	_log.Log(gmLog.lData, 'selected [%s]' % pat_selected)
	ID,name = string.split(pat_selected,':')
	data = gmXdtToolsLib.get_pat_data(afile,ID,name,patdir = apatdir, patlst = apatlst)
	# how many records were obtained for this patient ?
	path,files = data
	# none
	if len(files) == 0:
		gm_show_error(
			_('The XDT file apparently did not contain data for\npatient [%s] (%s).' % (name, ID)),
			_('parsing XDT file')
		)
		return None
	# one
	if len(files) == 1:
		afile = os.path.join(path, files[0])
		return 1
	dlg = wxSingleChoiceDialog (
		parent = NULL,
		message = _("Please select the record you want to display."),
		caption = _("parsing patient-list for records" ),
		choices = files,
		style = wxOK | wxCANCEL
	)
	btn_pressed = dlg.ShowModal()
	dlg.Destroy() 
	# user cancelled
	if btn_pressed == wxID_CANCEL:
		return None
	# show file(s)
	fname,ahash = string.split(dlg.GetStringSelection(),':')
	_log.Log(gmLog.lData, 'selected [%s]' % fname)
	afile = path + '/' + fname
	return afile
#======================================================
# main
#------------------------------------------------------
if __name__ == '__main__':
	import gmCLI
	import gmCfg
	#---------------------
	# set up dummy app
	class TestApp (wxApp):
		def OnInit (self):
			if not gmCLI.has_arg('--conf-file'):
				gm_show_error (
				_('No config file given on command line.\n\nFormat: --conf-file=<file>'),
				_('loading config file'),
				gmLog.lInfo
				)
				return 0
			aCfg = gmCfg.gmDefCfgFile
			# get export-dir
			apatdir = aCfg.get("xdt-viewer", "export-dir")
			pat_lst_fname = aCfg.get("xdt-viewer", "patient-list")
			# is there a patient list already ?
			apatlst = gmCfg.cCfgFile(aPath = apatdir ,aFile = pat_lst_fname, flags = 2)
			# has the user manually supplied a config file on the command line ?
			if not gmCLI.has_arg('--xdt-file'):
				gm_show_error (
					_('No XDT file given on command line.\n\nFormat: --xdt-file=<file>'),
					_('XDT Viewer: loading XDT file'),
					gmLog.lInfo
				)
				return 0
			# yes -> verify it
			fname = _preprocess_file(gmCLI.arg['--xdt-file'],aCfg,apatlst,apatdir)
			if fname is None:
			
				return None
			# OK -> show it
			frame = wxFrame (
				parent = NULL,
				id = -1,
				title = _("XDT Viewer"),
				size = wxSize(800,600)
			)
			viewer = gmXdtViewerPanel(frame, fname)
			viewer.populate_list()
			frame.Show(1)
			return 1
	#---------------------
	try:
		app = TestApp ()
		app.MainLoop ()
	except StandardError:
		_log.LogException('Unhandled exception.', sys.exc_info())
		raise
else:
	import gmPlugin

	class gmXdtViewer(gmPlugin.wxNotebookPlugin):
		tab_name = 'XDT'

		def name (self):
			return gmXdtViewer.tab_name

		def GetWidget (self, parent):
			self.viewer = gmXdtViewerPanel(parent)
			return self.viewer

		def MenuInfo (self):
			return ('tools', _('&show XDT'))

		def ReceiveFocus(self):
			# get file name
			# - via file select dialog
			aWildcard = "%s (*.BDT)|*.BDT|%s (*.*)|*.*" % (_("xDT file"), _("all files"))
			aDefDir = os.path.abspath(os.path.expanduser(os.path.join('~', "gnumed/xdt/patient")))
			dlg = wxFileDialog(
				parent = NULL,
				message = _("Choose an xDT file"),
				defaultDir = aDefDir,
				defaultFile = "",
				wildcard = aWildcard,
				style = wxOPEN | wxFILE_MUST_EXIST
			)
			btn_pressed = dlg.ShowModal()
			fname = dlg.GetPath()
			dlg.Destroy()

#					gm_show_error(
#						_('File [%s] contains more than one patient. Aborting.' % afile),
#						_('preprocessing XDT file')
#					)

			if btn_pressed == wxID_OK:
				_log.Log(gmLog.lData, 'selected [%s]' % fname)
				self.viewer.populate_list(fname)

			# - via currently selected patient -> XDT files
			# ...

			return 1
#=============================================================================
# $Log: gmXdtViewer.py,v $
# Revision 1.9  2003-08-24 10:16:45  shilbert
# - now checks whether content is new or already exists as file from previuos sessions
#
# Revision 1.8  2003/08/24 09:24:13  ncq
# - make it work with single-patient files in standalone mode
#
# Revision 1.7  2003/08/23 13:23:29  shilbert
# - adapted some functions so that gmXdtToolsLib is no longer dependent on gmCfg
#
# Revision 1.6  2003/08/21 21:36:42  shilbert
# - make it work again after heavy refactoring by ncq
#
# Revision 1.5  2003/08/21 19:35:02  ncq
# - factor out splitting
#
# Revision 1.4  2003/08/20 22:59:53  shilbert
# - just code cleanup
#
# Revision 1.3  2003/08/20 22:52:12  shilbert
# - squashed some of the obvious bugs
# - initial testing for correct xdt structure
#
# Revision 1.2  2003/08/18 23:34:28  ncq
# - cleanup, somewhat restructured to show better way of going about things
#
# Revision 1.1  2003/08/18 20:32:03  shilbert
# - now handles the case that xdt-file contains more than one patient
# - splits into individual records / per patient
# - asks for patient to display
#
# Revision 1.8  2003/06/26 21:41:51  ncq
# - fatal->verbose
#
# Revision 1.7  2003/04/28 12:12:18  ncq
# - refactor name(), better CANCEL handling on file select dialog
#
# Revision 1.6  2003/04/25 13:04:39  ncq
# - reorder variable use so fname is defined when logging
#
# Revision 1.5  2003/02/19 15:56:33  ncq
# - don't fail on malformed lines
#
# Revision 1.4  2003/02/19 12:42:38  ncq
# - further dict()ified __decode_xdt()
#
# Revision 1.3  2003/02/16 13:54:47  ncq
# - renamed command line option to --xdt-file=
#
# Revision 1.2  2003/02/15 15:33:58  ncq
# - typo
#
# Revision 1.1  2003/02/15 14:21:49  ncq
# - on demand loading of Manual
# - further pluginization of showmeddocs
#
# Revision 1.5  2003/02/15 13:52:08  ncq
# - hey, works as a plugin too, now :-))
#
# Revision 1.4  2003/02/15 12:17:28  ncq
# - much better suited for plugin use
#
# Revision 1.3  2003/02/15 10:53:10  ncq
# - works standalone
#
# Revision 1.2  2003/02/13 15:51:09  ncq
# - added TODO
#
# Revision 1.1  2003/02/13 15:25:15  ncq
# - first version, works standalone only
#
