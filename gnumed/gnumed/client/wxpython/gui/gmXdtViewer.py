#!/usr/bin/env python

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
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/gmXdtViewer.py,v $
# $Id: gmXdtViewer.py,v 1.3 2003-02-16 13:54:47 ncq Exp $
__version__ = "$Revision: 1.3 $"
__author__ = "S.Hilbert, K.Hilbert"

import sys,os,fileinput,string,linecache
# location of our modules
if __name__ == "__main__":
	sys.path.append(os.path.join('.', 'modules'))

import gmLog
_log = gmLog.gmDefLog
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)
_log.Log(gmLog.lData, __version__)

if __name__ == "__main__":
	import gmI18N

from wxPython.wx import *
from wxPython.lib.mixins.listctrl import wxColumnSorterMixin, wxListCtrlAutoWidthMixin

from gmXdtMappings import xdt_id_map, xdt_packet_type_map
#=============================================================================
class gmXdtListCtrl(wxListCtrl, wxListCtrlAutoWidthMixin):
	def __init__(self, parent, ID, pos=wxDefaultPosition, size=wxDefaultSize, style=0):
		wxListCtrl.__init__(self, parent, ID, pos, size, style)
		wxListCtrlAutoWidthMixin.__init__(self)
#=============================================================================
class gmXdtViewerPanel(wxPanel):
	def __init__(self, parent, aFileName = None):
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

		self.filename = aFileName

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

	#-------------------------------------------------------------------------
	def Populate(self):

		# populate list
		items = self.__decode_xdt()
		for item_idx in range(len(items),0,-1):
			data = items[item_idx]
			idx = self.list.InsertItem(info=wxListItem())
			self.list.SetStringItem(index=idx, col=0, label=data[0])
			self.list.SetStringItem(index=idx, col=1, label=data[1])
			#self.list.SetItemData(item_idx, item_idx)

		# reaspect
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

		xDTFile = fileinput.input(self.filename)
		items = {}
		i = 1
		for line in xDTFile:
			# remove trailing CR and/or LF
			line = string.replace(line,'\015','')
			line = string.replace(line,'\012','') 
			length ,ID, content = line[:3], line[3:7], line[7:]

			if ID == '8000':
				tmp = xdt_packet_type_map[content]
				content = tmp
			try:
				items[i] = (xdt_id_map[ID], content)
			except:
				pass
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
# main
#------------------------------------------------------
if __name__ == '__main__':
	import gmCLI
	#---------------------
	# set up dummy app
	class TestApp (wxApp):
		def OnInit (self):

			fname = ""
			# has the user manually supplied a config file on the command line ?
			if gmCLI.has_arg('--xdt-file'):
				fname = gmCLI.arg['--xdt-file']
				_log.Log(gmLog.lData, 'XDT file is [%s]' % fname)
				# file valid ?
				if not os.path.exists(fname):
					_log.Log(gmLog.lErr, "XDT file [%s] not found. Aborting." % fname)
					return None
			else:
				_log.Log(gmLog.lData, "No XDT file given on command line. Format: --xdt-file=<file>")
				return None

			frame = wxFrame(
				parent=NULL,
				id = -1,
				title = _("XDT Viewer"),
				size = wxSize(800,600)
			)
			pnl = gmXdtViewerPanel(frame, fname)
			pnl.Populate()
			frame.Show(1)
			return 1
	#---------------------
	try:
		app = TestApp ()
		app.MainLoop ()
	except StandardError:
		_log.LogException('Unhandled exception.', sys.exc_info(), fatal=1)
		raise

else:
	import gmPlugin

	class gmXdtViewer(gmPlugin.wxNotebookPlugin):
		def name (self):
			return 'XDT'

		def GetWidget (self, parent):
			self.viewer = gmXdtViewerPanel(parent)
			return self.viewer

		def MenuInfo (self):
			return ('tools', _('&show XDT'))

		def ReceiveFocus(self):
			# get file name
			# - via file select dialog
			aWildcard = "%s (*.BDT)|*.BDT|%s (*.*)|*.*" % (_("xDT file"), _("all files"))
			aDefDir = os.path.abspath(os.path.expanduser(os.path.join('~', "gnumed")))
			dlg = wxFileDialog(
				parent = NULL,
				message = _("Choose an xDT file"),
				defaultDir = aDefDir,
				defaultFile = "",
				wildcard = aWildcard,
				style = wxOPEN | wxFILE_MUST_EXIST
			)
			if dlg.ShowModal() == wxID_OK:
				fname = dlg.GetPath()
			dlg.Destroy()
			_log.Log(gmLog.lData, 'selected [%s]' % fname)

			# - via currently selected patient -> XDT files
			# ...

			self.viewer.filename = fname
			self.viewer.Populate()
			return 1
#=============================================================================
# $Log: gmXdtViewer.py,v $
# Revision 1.3  2003-02-16 13:54:47  ncq
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
