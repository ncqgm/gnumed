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
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/gmXdtViewer.py,v $
# $Id: gmXdtViewer.py,v 1.31 2007-12-26 14:35:51 ncq Exp $
__version__ = "$Revision: 1.31 $"
__author__ = "S.Hilbert, K.Hilbert"

import sys, os, os.path, codecs


import wx


from Gnumed.wxpython import gmGuiHelpers, gmPlugin
from Gnumed.pycommon import gmLog2, gmI18N, gmDispatcher
from Gnumed.business import gmXdtMappings, gmXdtObjects
from Gnumed.wxGladeWidgets import wxgXdtListPnl

_log = logging.getLogger('gm.ui')
_log.Log(gmLog.lInfo, __version__)

#=============================================================================
# FIXME: this belongs elsewhere under wxpython/
class cXdtListPnl(wxgXdtListPnl.wxgXdtListPnl):
	def __init__(self, *args, **kwargs):
		wxgXdtListPnl.wxgXdtListPnl.__init__(self, *args, **kwargs)

		self.filename = None

		self.__cols = [
			_('xDT field'),
			_('field content'),
			_('xDT field ID')
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
			root_dir = os.path.expanduser(os.path.join('~', 'gnumed', 'xDT'))
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
			style = wx.OPEN | wx.FILE_MUST_EXIST
		)
		choice = dlg.ShowModal()
		fname = None
		if choice == wx.ID_OK:
			fname =  dlg.GetPath()
		dlg.Destroy()
		return fname
	#--------------------------------------------------------------
	def load_file(self, filename=None):
		if filename is None:
			filename = self.select_file()
		if filename is None:
			return True

		self.filename = None

		try:
			f = file(filename, 'r')
		except IOError:
			gmGuiHelpers.gm_show_error (
				_('Cannot access xDT file\n\n'
				  ' [%s]'),
				_('loading xDT file'),
				gmLog.lErr
			)
			return False
		f.close()

		encoding = gmXdtObjects.determine_xdt_encoding(filename = filename)
		if encoding is None:
			encoding = 'utf8'
			gmDispatcher.send(signal = 'statustext', msg = _('Encoding missing in xDT file. Assuming [%s].') % encoding)
			_log.warning('xDT file [%s] does not define an encoding, assuming [%s]' % (filename, encoding))

		try:
			xdt_file = codecs.open(filename=filename, mode='rU', encoding=encoding, errors='replace')
		except IOError:
			gmGuiHelpers.gm_show_error (
				_('Cannot access xDT file\n\n'
				  ' [%s]'),
				_('loading xDT file'),
				gmLog.lErr
			)
			return False

		# parse and display file
		self._LCTRL_xdt.DeleteAllItems()

		self._LCTRL_xdt.InsertStringItem(index=0, label=_('name of xDT file'))
		self._LCTRL_xdt.SetStringItem(index=0, col=1, label=filename)

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

			self._LCTRL_xdt.InsertStringItem(index=idx, label=left)
			self._LCTRL_xdt.SetStringItem(index=idx, col=1, label=right)
			self._LCTRL_xdt.SetStringItem(index=idx, col=2, label=field)
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
		if self.filename is None:
			self.load_file()
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
			self.list.SetStringItem(index=idx, col=0, label=data[0])
			self.list.SetStringItem(index=idx, col=1, label=data[1])
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
		self.currentItem = event.m_itemIndex
	#-------------------------------------------------------------------------
	def OnItemDeselected(self, evt):
		item = evt.GetItem()

		# Show how to reselect something we don't want deselected
#		if evt.m_itemIndex == 11:
#			wxCallAfter(self.list.SetItemState, 11, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
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
		wx.CallAfter(self.PopulateList)
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
class gmXdtViewer(gmPlugin.cNotebookPlugin):
	"""Plugin to encapsulate xDT list-in-panel viewer"""

	tab_name = _('xDT Viewer')

	def name(self):
		return gmXdtViewer.tab_name

	def GetWidget(self, parent):
		self._widget = cXdtListPnl(parent, -1)
		return self._widget

	def MenuInfo(self):
		return ('tools', _('xDT viewer'))

	def can_receive_focus(self):
		return True
#======================================================
# main
#------------------------------------------------------
if __name__ == '__main__':
	from Gnumed.pycommon import gmCfg2

	cfg = gmCfg2.gmCfgData()
	cfg.add_cli(long_options=['xdt-file'])
	#---------------------
	# set up dummy app
	class TestApp (wx.App):
		def OnInit (self):

			fname = ""
			# has the user manually supplied a config file on the command line ?
			fname = cfg.get(option = '--xdt-file', source_order = [('cli', 'return')])
			if fname is not None.
				_log.debug('XDT file is [%s]' % fname)
				# file valid ?
				if not os.access(fname, os.R_OK):
					title = _('Opening xDT file')
					msg = _('Cannot open xDT file.\n'
							'[%s]') % fname
					gmGuiHelpers.gm_show_error(msg, title, gmLog.lErr)
					return False
			else:
				title = _('Opening xDT file')
				msg = _('You must provide an xDT file on the command line.\n'
						'Format: --xdt-file=<file>')
				gmGuiHelpers.gm_show_error(msg, title, gmLog.lWarn)
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
	try:
		app = TestApp ()
		app.MainLoop ()
	except StandardError:
		_log.exception('Unhandled exception.')
		raise

#=============================================================================
# $Log: gmXdtViewer.py,v $
# Revision 1.31  2007-12-26 14:35:51  ncq
# - move to gmLog2/gmCfg2
#
# Revision 1.30  2007/12/11 12:49:26  ncq
# - explicit signal handling
#
# Revision 1.29  2007/08/29 14:43:43  ncq
# - show xDT field ID in third column to enable more comfortable debugging
#
# Revision 1.28  2007/08/12 00:12:41  ncq
# - no more gmSignals.py
#
# Revision 1.27  2007/05/21 13:06:39  ncq
# - proper chatch-all wildcard * rather than *.*
#
# Revision 1.26  2007/05/14 13:11:25  ncq
# - use statustext() signal
#
# Revision 1.25  2007/01/21 12:22:44  ncq
# - use determine_xdt_encoding()
#
# Revision 1.24  2006/11/24 10:01:31  ncq
# - gm_beep_statustext() -> gm_statustext()
#
# Revision 1.23  2006/10/31 16:05:40  ncq
# - exit first scan as soon as encoding was found
# - assume iso8859-1 if not found
# - display LDT file name in first line of list control
#
# Revision 1.22  2006/10/30 16:48:13  ncq
# - bring back in line with the plugin framework
#
# Revision 1.21  2006/07/19 20:32:11  ncq
# - cleanup
#
# Revision 1.20  2005/12/06 16:44:16  ncq
# - make it work standalone again
#
# Revision 1.19  2005/09/28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.18  2005/09/26 18:01:52  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.17  2004/08/04 17:16:02  ncq
# - wx.NotebookPlugin -> cNotebookPlugin
# - derive cNotebookPluginOld from cNotebookPlugin
# - make cNotebookPluginOld warn on use and implement old
#   explicit "main.notebook.raised_plugin"/ReceiveFocus behaviour
# - ReceiveFocus() -> receive_focus()
#
# Revision 1.16  2004/06/25 12:37:21  ncq
# - eventually fix the import gmI18N issue
#
# Revision 1.15  2004/06/13 22:31:49  ncq
# - gb['main.toolbar'] -> gb['main.top_panel']
# - self.internal_name() -> self.__class__.__name__
# - remove set_widget_reference()
# - cleanup
# - fix lazy load in _on_patient_selected()
# - fix lazy load in ReceiveFocus()
# - use self._widget in self.GetWidget()
# - override populate_with_data()
# - use gb['main.notebook.raised_plugin']
#
# Revision 1.14	 2004/03/19 20:43:32  shilbert
# - fixed import
#
# Revision 1.13	 2004/03/19 10:22:12  ncq
# - even better help
#
# Revision 1.12	 2004/03/19 10:20:29  ncq
# - in standalone, display nice message upon xdt file load errors
#
# Revision 1.11	 2004/03/19 08:27:50  ncq
# - fix imports, return BOOL from OnInit
#
# Revision 1.10	 2004/03/18 09:43:02  ncq
# - import gmI18N if standalone
#
# Revision 1.9	2003/11/17 10:56:41	 sjtan
#
# synced and commiting.
#
# Revision 1.1	2003/10/23 06:02:40	 sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.8	2003/06/26 21:41:51	 ncq
# - fatal->verbose
#
# Revision 1.7	2003/04/28 12:12:18	 ncq
# - refactor name(), better CANCEL handling on file select dialog
#
# Revision 1.6	2003/04/25 13:04:39	 ncq
# - reorder variable use so fname is defined when logging
#
# Revision 1.5	2003/02/19 15:56:33	 ncq
# - don't fail on malformed lines
#
# Revision 1.4	2003/02/19 12:42:38	 ncq
# - further dict()ified __decode_xdt()
#
# Revision 1.3	2003/02/16 13:54:47	 ncq
# - renamed command line option to --xdt-file=
#
# Revision 1.2	2003/02/15 15:33:58	 ncq
# - typo
#
# Revision 1.1	2003/02/15 14:21:49	 ncq
# - on demand loading of Manual
# - further pluginization of showmeddocs
#
# Revision 1.5	2003/02/15 13:52:08	 ncq
# - hey, works as a plugin too, now :-))
#
# Revision 1.4	2003/02/15 12:17:28	 ncq
# - much better suited for plugin use
#
# Revision 1.3	2003/02/15 10:53:10	 ncq
# - works standalone
#
# Revision 1.2	2003/02/13 15:51:09	 ncq
# - added TODO
#
# Revision 1.1	2003/02/13 15:25:15	 ncq
# - first version, works standalone only
#
