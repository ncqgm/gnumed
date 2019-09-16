# -*- coding: utf-8 -*-
"""GNUmed xDT viewer.

TODO:

- popup menu on right-click
  - import this line
  - import all lines like this
  - search
  - print
  - ...
"""
#=============================================================================
__author__ = "S.Hilbert, K.Hilbert"

import sys, os, os.path, io, logging


import wx


from Gnumed.wxpython import gmGuiHelpers, gmPlugin
from Gnumed.pycommon import gmI18N, gmDispatcher
from Gnumed.business import gmXdtMappings, gmXdtObjects
from Gnumed.wxGladeWidgets import wxgXdtListPnl
from Gnumed.wxpython import gmAccessPermissionWidgets


_log = logging.getLogger('gm.ui')

#=============================================================================
# FIXME: this belongs elsewhere under wxpython/
class cXdtListPnl(wxgXdtListPnl.wxgXdtListPnl):
	def __init__(self, *args, **kwargs):
		wxgXdtListPnl.wxgXdtListPnl.__init__(self, *args, **kwargs)

		self.filename = None

		self.__cols = [
			_('Field name'),
			_('Interpreted content'),
			_('xDT field ID'),
			_('Raw content')
		]
		self.__init_ui()
	#--------------------------------------------------------------
	def __init_ui(self):
		for col in range(len(self.__cols)):
			self._LCTRL_xdt.InsertColumn(col, self.__cols[col])
	#--------------------------------------------------------------
	# external API
	#--------------------------------------------------------------
	def select_file(self, path=None):
		if path is None:
			root_dir = os.path.expanduser(os.path.join('~', 'gnumed'))
		else:
			root_dir = path
		# get file name
		# - via file select dialog
		dlg = wx.FileDialog (
			parent = self,
			message = _("Choose an xDT file"),
			defaultDir = root_dir,
			defaultFile = '',
			wildcard = '%s (*.xDT)|*.?DT;*.?dt|%s (*)|*|%s (*.*)|*.*' % (_('xDT files'), _('all files'), _('all files (Win)')),
			style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
		)
		choice = dlg.ShowModal()
		fname = None
		if choice == wx.ID_OK:
			fname =  dlg.GetPath()
		dlg.DestroyLater()
		return fname
	#--------------------------------------------------------------
	def load_file(self, filename=None):
		if filename is None:
			filename = self.select_file()
		if filename is None:
			return True

		self.filename = None

		try:
			f = open(filename, 'r')
		except IOError:
			gmGuiHelpers.gm_show_error (
				_('Cannot access xDT file\n\n'
				  ' [%s]'),
				_('loading xDT file')
			)
			return False
		f.close()

		encoding = gmXdtObjects.determine_xdt_encoding(filename = filename)
		if encoding is None:
			encoding = 'utf8'
			gmDispatcher.send(signal = 'statustext', msg = _('Encoding missing in xDT file. Assuming [%s].') % encoding)
			_log.warning('xDT file [%s] does not define an encoding, assuming [%s]' % (filename, encoding))

		try:
			xdt_file = io.open(filename, mode = 'rt', encoding = encoding, errors = 'replace')
		except IOError:
			gmGuiHelpers.gm_show_error (
				_('Cannot access xDT file\n\n'
				  ' [%s]'),
				_('loading xDT file')
			)
			return False

		# parse and display file
		self._LCTRL_xdt.DeleteAllItems()

		self._LCTRL_xdt.InsertItem(index=0, label=_('name of xDT file'))
		self._LCTRL_xdt.SetItem(index=0, column=1, label=filename)

		idx = 1
		for line in xdt_file:
			line = line.replace('\015','')
			line = line.replace('\012','')
			length, field, content = line[:3], line[3:7], line[7:]

			try:
				left = gmXdtMappings.xdt_id_map[field]
			except KeyError:
				left = field

			try:
				right = gmXdtMappings.xdt_map_of_content_maps[field][content]
			except KeyError:
				right = content

			self._LCTRL_xdt.InsertItem(index=idx, label=left)
			self._LCTRL_xdt.SetItem(index=idx, column=1, label=right)
			self._LCTRL_xdt.SetItem(index=idx, column=2, label=field)
			self._LCTRL_xdt.SetItem(index=idx, column=3, label=content)
			idx += 1

		xdt_file.close()

		self._LCTRL_xdt.SetColumnWidth(0, wx.LIST_AUTOSIZE)
		self._LCTRL_xdt.SetColumnWidth(1, wx.LIST_AUTOSIZE)

		self._LCTRL_xdt.SetFocus()
		self._LCTRL_xdt.SetItemState (
			item = 0,
			state = wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
			stateMask = wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED
		)

		self.filename = filename
	#--------------------------------------------------------------
	# event handlers
	#--------------------------------------------------------------
	def _on_load_button_pressed(self, evt):
		self.load_file()
	#--------------------------------------------------------------
	# plugin API
	#--------------------------------------------------------------
	def repopulate_ui(self):
#		if self.filename is None:
#			self.load_file()
		return
#=============================================================================
class gmXdtViewerPanel(wx.Panel):
	def __init__(self, parent, aFileName = None):
		wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)

		# our actual list
		tID = wx.NewId()
		self.list = gmXdtListCtrl(
			self,
			tID,
			style=wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_VRULES
		)#|wx.LC_HRULES)

		self.list.InsertColumn(0, _("XDT field"))
		self.list.InsertColumn(1, _("XDT field content"))

		self.filename = aFileName

		# set up events
		wx.EVT_SIZE(self, self.OnSize)

		wx.EVT_LIST_ITEM_SELECTED(self, tID, self.OnItemSelected)
		wx.EVT_LIST_ITEM_DESELECTED(self, tID, self.OnItemDeselected)
		wx.EVT_LIST_ITEM_ACTIVATED(self, tID, self.OnItemActivated)
		wx.EVT_LIST_DELETE_ITEM(self, tID, self.OnItemDelete)

		wx.EVT_LIST_COL_CLICK(self, tID, self.OnColClick)
		wx.EVT_LIST_COL_RIGHT_CLICK(self, tID, self.OnColRightClick)
#		wx.EVT_LIST_COL_BEGIN_DRAG(self, tID, self.OnColBeginDrag)
#		wx.EVT_LIST_COL_DRAGGING(self, tID, self.OnColDragging)
#		wx.EVT_LIST_COL_END_DRAG(self, tID, self.OnColEndDrag)

		wx.EVT_LEFT_DCLICK(self.list, self.OnDoubleClick)
		wx.EVT_RIGHT_DOWN(self.list, self.OnRightDown)

		if wx.Platform == '__WXMSW__':
			wx.EVT_COMMAND_RIGHT_CLICK(self.list, tID, self.OnRightClick)
		elif wx.Platform == '__WXGTK__':
			wx.EVT_RIGHT_UP(self.list, self.OnRightClick)

	#-------------------------------------------------------------------------
	def Populate(self):

		# populate list
		items = self.__decode_xdt()
		for item_idx in range(len(items),0,-1):
			data = items[item_idx]
			idx = self.list.InsertItem(info=wx.ListItem())
			self.list.SetItem(index=idx, column=0, label=data[0])
			self.list.SetItem(index=idx, column=1, label=data[1])
			#self.list.SetItemData(item_idx, item_idx)

		# reaspect
		self.list.SetColumnWidth(0, wx.LIST_AUTOSIZE)
		self.list.SetColumnWidth(1, wx.LIST_AUTOSIZE)

		# show how to select an item
		#self.list.SetItemState(5, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)

		# show how to change the colour of a couple items
		#item = self.list.GetItem(1)
		#item.SetTextColour(wx.BLUE)
		#self.list.SetItem(item)
		#item = self.list.GetItem(4)
		#item.SetTextColour(wxRED)
		#self.list.SetItem(item)

		self.currentItem = 0
	#-------------------------------------------------------------------------
	def __decode_xdt(self):
		if self.filename is None:
			_log.error("Need name of file to parse !")
			return None

		xDTFile = fileinput.input(self.filename)
		items = {}
		i = 1
		for line in xDTFile:
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
		if flags & wx.LIST_HITTEST_ONITEM:
			self.list.Select(item)
		event.Skip()
	#-------------------------------------------------------------------------
	def getColumnText(self, index, col):
		item = self.list.GetItem(index, col)
		return item.GetText()
	#-------------------------------------------------------------------------
	def OnItemSelected(self, event):
		self.currentItem = event.ItemIndex
	#-------------------------------------------------------------------------
	def OnItemDeselected(self, evt):
		item = evt.GetItem()

		# Show how to reselect something we don't want deselected
#		if evt.ItemIndex == 11:
#			wxCallAfter(self.list.SetItemState, 11, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
	#-------------------------------------------------------------------------
	def OnItemActivated(self, event):
		self.currentItem = event.ItemIndex
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
		menu = wx.Menu()
		tPopupID1 = 0
		tPopupID2 = 1
		tPopupID3 = 2
		tPopupID4 = 3
		tPopupID5 = 5

		# Show how to put an icon in the menu
		item = wx.MenuItem(menu, tPopupID1,"One")
		item.SetBitmap(images.getSmilesBitmap())

		menu.AppendItem(item)
		menu.Append(tPopupID2, "Two")
		menu.Append(tPopupID3, "ClearAll and repopulate")
		menu.Append(tPopupID4, "DeleteAllItems")
		menu.Append(tPopupID5, "GetItem")
		wx.EVT_MENU(self, tPopupID1, self.OnPopupOne)
		wx.EVT_MENU(self, tPopupID2, self.OnPopupTwo)
		wx.EVT_MENU(self, tPopupID3, self.OnPopupThree)
		wx.EVT_MENU(self, tPopupID4, self.OnPopupFour)
		wx.EVT_MENU(self, tPopupID5, self.OnPopupFive)
		self.PopupMenu(menu, wxPoint(self.x, self.y))
		menu.DestroyLater()
		event.Skip()
	#-------------------------------------------------------------------------
	def OnPopupOne(self, event):
		print("FindItem:", self.list.FindItem(-1, "Roxette"))
		print("FindItemData:", self.list.FindItemData(-1, 11))
	#-------------------------------------------------------------------------
	def OnPopupTwo(self, event):
		pass
	#-------------------------------------------------------------------------
	def OnPopupThree(self, event):
		self.list.ClearAll()
		wx.CallAfter(self.PopulateList)
		#wxYield()
		#self.PopulateList()
	#-------------------------------------------------------------------------
	def OnPopupFour(self, event):
		self.list.DeleteAllItems()
	#-------------------------------------------------------------------------
	def OnPopupFive(self, event):
		item = self.list.GetItem(self.currentItem)
		print(item.Text, item.Id, self.list.GetItemData(self.currentItem))
	#-------------------------------------------------------------------------
	def OnSize(self, event):
		w,h = self.GetClientSize()
		self.list.SetDimensions(0, 0, w, h)
#======================================================
class gmXdtViewer(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate xDT list-in-panel viewer"""

	tab_name = _('xDT viewer')
	required_minimum_role = 'non-clinical access'

	@gmAccessPermissionWidgets.verify_minimum_required_role (
		required_minimum_role,
		activity = _('loading plugin <%s>') % tab_name,
		return_value_on_failure = False,
		fail_silently = False
	)
	def register(self):
		gmPlugin.cNotebookPlugin.register(self)
	#-------------------------------------------------

	def name(self):
		return gmXdtViewer.tab_name

	def GetWidget(self, parent):
		self._widget = cXdtListPnl(parent, -1)
		return self._widget

	def MenuInfo(self):
		return ('tools', _('&xDT viewer'))

	def can_receive_focus(self):
		return True
#======================================================
# main
#------------------------------------------------------
if __name__ == '__main__':
	from Gnumed.pycommon import gmCfg2

	cfg = gmCfg2.gmCfgData()
	cfg.add_cli(long_options=['xdt-file='])
	#---------------------
	# set up dummy app
	class TestApp (wx.App):
		def OnInit (self):

			fname = ""
			# has the user manually supplied a config file on the command line ?
			fname = cfg.get(option = '--xdt-file', source_order = [('cli', 'return')])
			if fname is not None:
				_log.debug('XDT file is [%s]' % fname)
				# file valid ?
				if not os.access(fname, os.R_OK):
					title = _('Opening xDT file')
					msg = _('Cannot open xDT file.\n'
							'[%s]') % fname
					gmGuiHelpers.gm_show_error(msg, title)
					return False
			else:
				title = _('Opening xDT file')
				msg = _('You must provide an xDT file on the command line.\n'
						'Format: --xdt-file=<file>')
				gmGuiHelpers.gm_show_error(msg, title)
				return False

			frame = wx.Frame(
				parent = None,
				id = -1,
				title = _("XDT Viewer"),
				size = wx.Size(800,600)
			)
			pnl = gmXdtViewerPanel(frame, fname)
			pnl.Populate()
			frame.Show(1)
			return True
	#---------------------
	app = TestApp ()
	app.MainLoop ()

#=============================================================================
