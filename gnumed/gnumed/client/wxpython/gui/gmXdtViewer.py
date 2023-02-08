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

import os, os.path, io, logging


import wx


from Gnumed.wxpython import gmGuiHelpers, gmPlugin
from Gnumed.pycommon import gmDispatcher, gmTools
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
			root_dir = gmTools.gmPaths().user_work_dir
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
			field, content = line[3:7], line[7:]

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
	from Gnumed.pycommon import gmCfgINI

	cfg = gmCfgINI.gmCfgData()
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
			pnl = cXdtListPnl(frame)
			pnl.Populate()
			frame.Show(1)
			return True

	#---------------------
	app = TestApp ()
	app.MainLoop ()
