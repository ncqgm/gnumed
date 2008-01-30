"""This widgets lets you manage laboratory requests

 - add requests
 - keep track of pending requests
 - see import errors
 - review newly imported lab results
"""
#============================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmLabWidgets.py,v $
__version__ = "$Revision: 1.30 $"
__author__ = "Sebastian Hilbert <Sebastian.Hilbert@gmx.net>"

# system
import os.path, sys, os, re, random
# FIXME: debugging
import time

# 3rd party
import wx
import wx.lib.mixins.listctrl as listmixins
#import wx.ColumnSorterMixin, wx.ListCtrlAutoWidthMixin
#from wxPython import grid

from Gnumed.pycommon import gmLog, gmI18N, gmPG2, gmCfg, gmExceptions, gmMatchProvider, gmGuiBroker, gmDispatcher
from Gnumed.business import gmPerson, gmClinicalRecord, gmPathLab
from Gnumed.wxpython import gmGuiHelpers, gmPhraseWheel

_log = gmLog.gmDefLog
if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)
_log.Log(gmLog.lInfo, __version__)

[	wx.ID_LAB_GRID,
	wx.ID_NB_LabJournal,
	wx.ID_LBOX_pending_results,
	wx.ID_PHRWH_labs,
	wx.ID_TextCtrl_req_id,
	wx.ID_BTN_save_request_ID,
	wx.ID_BTN_select_all,
	wx.ID_BTN_mark_reviewed,
	wx.ID_pending_requests,
	wx.ID_lbox_errors,
	wx.ID_grid_unreviewed_results
] = map(lambda _init_ctrls: wx.NewId(), range(11))
#=========================================================
class cLabDataGridCellRenderer(wxPyGridCellRenderer):
    def __init__(self):
        wxPyGridCellRenderer.__init__(self)

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        dc.SetBackgroundMode(wx.SOLID)
        dc.SetBrush(wx.Brush(wx.BLACK, wx.SOLID))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangle(rect.x, rect.y, rect.width, rect.height)

        dc.SetBackgroundMode(wx.TRANSPARENT)
        dc.SetFont(attr.GetFont())

        text = grid.GetCellValue(row, col)
        colors = [wxRED, wx.WHITE, wx.CYAN]
        x = rect.x + 1
        y = rect.y + 1
        for ch in text:
            dc.SetTextForeground(random.choice(colors))
            dc.DrawText(ch, x, y)
            w, h = dc.GetTextExtent(ch)
            x = x + w
            if x > rect.right - 5:
                break


    def GetBestSize(self, grid, attr, dc, row, col):
        text = grid.GetCellValue(row, col)
        dc.SetFont(attr.GetFont())
        w, h = dc.GetTextExtent(text)
        return wx.Size(w, h)


    def Clone(self):
        return cLabDataGridCellRenderer()
#=========================================================
class cLabJournalCellRenderer(wxPyGridCellRenderer):
	def __init__(self):
		wxPyGridCellRenderer.__init__(self)

	def Draw(self, grid, attr, dc, rect, row, col, isSelected):
		dc.SetBackgroundMode(wx.SOLID)
		dc.SetBrush(wx.Brush(wx.BLACK, wx.SOLID))
		dc.SetPen(wx.TRANSPARENT_PEN)
		dc.DrawRectangle(rect.x, rect.y, rect.width, rect.height)
		dc.SetBackgroundMode(wx.TRANSPARENT)
		dc.SetFont(attr.GetFont())

		text = grid.GetCellValue(row, col)
		colors = [wxRED, wx.WHITE, wx.CYAN]
		x = rect.x + 1
		y = rect.y + 1
		for ch in text:
			dc.SetTextForeground(random.choice(colors))
			dc.DrawText(ch, x, y)
			w, h = dc.GetTextExtent(ch)
			x = x + w
			if x > rect.right - 5:
				break

#=========================================================
class cLabReviewGrid(wx.Grid):
	"""This wx.Grid derivative displays lab data that has not yet been reviewed by a clinician.
	"""
	def __init__(self, parent, id):
		"""Set up our specialised grid.
		"""
		wx.Grid.__init__(
			self,
			parent,
			id,
			pos = wx.DefaultPosition,
			size = wx.DefaultSize,
			style= wx.WANTS_CHARS
		)
#=========================================================
class cLabWheel(gmPhraseWheel.cPhraseWheel):
	def __init__(self, parent):
		query = """
			select pk, internal_name
			from test_org
			"""
		mp = gmMatchProvider.cMatchProvider_SQL2([query])
		mp.setThresholds(aWord=2, aSubstring=4)

		gmPhraseWheel.cPhraseWheel.__init__(
			self,
			parent = parent,
			id = -1,
			size = wx.DefaultSize,
			pos = wx.DefaultPosition
		)
		self.SetToolTipString(_('choose which lab will process the probe with the specified ID'))
		self.matcher = mp
#=========================================================
# FIXME: is this really lab specific ?
class cLabIDListCtrl(wx.ListCtrl, wx.ListCtrlAutoWidthMixin):
	def __init__(self, parent, id, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
		wx.ListCtrl.__init__(self, parent, id, pos, size, style)
		wx.ListCtrlAutoWidthMixin.__init__(self)

#=========================================================
class cLabJournalNB(wx.Notebook):
	"""This wx.Notebook derivative displays 'records still due' and lab-import related errors.
	"""
	def __init__(self, parent, id):
		"""Set up our specialised notebook.
		"""
		wx.Notebook.__init__(
			self,
			parent,
			id,
			wx.DefaultPosition,
			wx.DefaultSize,
			0
		)

		self.__pat = gmPerson.gmCurrentPatient()

		self.__do_layout_requests_page()
		self.__do_layout_errors_page()
		self.__do_layout_review_page()
		self.__do_layout_config_page()

		self.__register_events()
	#------------------------------------------------------------------------
	def __do_layout_config_page(self):
		pnl_page = wx.Panel(self, -1)



		szr_page = wx.BoxSizer(wx.VERTICAL)
#		szr_page.Add(hbszr,0, wxALIGN_LEFT | wxALL, 5)
#		szr_page.Add(self.lbox_pending, 1, wxEXPAND | wxALIGN_CENTER | wxALL, 5)

		pnl_page.SetAutoLayout(True)
		pnl_page.SetSizer(szr_page)
		szr_page.Fit(pnl_page)
		szr_page.SetSizeHints(pnl_page)

		self.AddPage(pnl_page, _("lab config"))
	#------------------------------------------------------------------------
	def __do_layout_requests_page(self):
		# notebook tab with pending requests
		pnl_page = wx.Panel(self, -1)

		# -- add request area --
		hbszr = wx.StaticBoxSizer(
			wx.StaticBox(
				pnl_page,
				-1,
				_("add new request for current patient")
			),
			wx.HORIZONTAL
		)
		# label
		lab_label = wx.StaticText(
			name = 'lablabel',
			parent = pnl_page,
			id = -1,
			label = _('Lab')
		)
		# phrase wheel
		self.lab_wheel = cLabWheel(pnl_page)
		self.lab_wheel.on_resize (None)
		self.lab_wheel.add_callback_on_selection(self.on_lab_selected)
		# label
		req_id_label = wx.StaticText(
			name = 'req_id_label',
			parent = pnl_page,
			id = -1,
			label = _("Specimen ID")
		)
		# request_id field
		self.fld_request_id = wx.TextCtrl (
			pnl_page,
			wx.ID_TextCtrl_req_id,
			"",
			wx.DefaultPosition,
			wx.Size(80,-1),
			0
		)
		# "save request id" button
		self.BTN_save_request_ID = wx.Button(
			name = 'BTN_save_request_ID',
			parent = pnl_page,
			id = wx.ID_BTN_save_request_ID,
			label = _("save lab request")
		)
		self.BTN_save_request_ID.SetToolTipString(_('associate chosen lab and ID with current patient'))

		hbszr.Add(lab_label, 0, wx.ALIGN_CENTER | wx.ALL, 5)
		hbszr.Add(self.lab_wheel, 0, wx.ALIGN_CENTER | wx.ALL, 5)
		hbszr.Add(req_id_label, 0, wx.ALIGN_CENTER | wx.ALL, 5)
		hbszr.Add(self.fld_request_id, 0, wx.ALIGN_CENTER| wx.ALL, 5)
		hbszr.Add(self.BTN_save_request_ID, 0, wx.ALIGN_CENTER | wx.ALL, 5)

		# -- add list of pending requests --
		self.lbox_pending = cLabIDListCtrl(
			pnl_page,
			wx.ID_pending_requests,
			size = wx.DefaultSize,
			style = wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_VRULES
		)

		self.lbox_pending.InsertColumn(0, _("date"))
		self.lbox_pending.InsertColumn(1, _("lab"))
		self.lbox_pending.InsertColumn(2, _("sample id"))
		self.lbox_pending.InsertColumn(3, _("patient"))
		self.lbox_pending.InsertColumn(4, _("status"))

		szr_page = wx.BoxSizer(wx.VERTICAL)
		szr_page.Add(hbszr,0, wx.ALIGN_LEFT | wx.ALL, 5)
		szr_page.Add(self.lbox_pending, 1, wxEXPAND | wx.ALIGN_CENTER | wx.ALL, 5)
#		szr_page.Add(self.lbox_pending, 1, wxEXPAND | wxALIGN_CENTER | wxALL, 5)

		pnl_page.SetAutoLayout(True)
		pnl_page.SetSizer(szr_page)
		szr_page.Fit(pnl_page)
		szr_page.SetSizeHints(pnl_page)

		self.AddPage(pnl_page, _("pending requests"))
	#------------------------------------------------------------------------
	def __do_layout_errors_page(self):
		pnl_page = wx.Panel( self, -1)

		self.lbox_errors = cLabIDListCtrl (
			parent = pnl_page,
			id = wx.ID_lbox_errors,
			size = wx.DefaultSize,
			style = wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_VRULES
		)
		self.lbox_errors.InsertColumn(0, _("noticed when"))
		self.lbox_errors.InsertColumn(1, _("problem"))
		self.lbox_errors.InsertColumn(2, _("solution"))
		self.lbox_errors.InsertColumn(3, _("context"))

		szr_page = wx.BoxSizer(wx.VERTICAL)
		szr_page.Add(self.lbox_errors, 1, wxEXPAND| wx.ALIGN_CENTER | wx.ALL, 5)
#		szr_page.Add(self.lbox_errors, 1, wxEXPAND| wxALIGN_CENTER | wxALL, 5)

		pnl_page.SetAutoLayout(True)
		pnl_page.SetSizer(szr_page)
		szr_page.Fit(pnl_page)
		szr_page.SetSizeHints(pnl_page)

		self.AddPage(pnl_page, _("lab errors"))
	#------------------------------------------------------------------------
	def __do_layout_review_page(self):
		pnl_page = wx.Panel( self, -1)

		# -- create new grid --
		self.__grid_unreviewed_results = cLabReviewGrid(
			pnl_page,
			wx.ID_grid_unreviewed_results
		)
		self.__grid_unreviewed_results.CreateGrid(0, 8, wx.Grid.wx.GridSelectCells)
		self.__grid_unreviewed_results.SetDefaultCellAlignment(wx.ALIGN_LEFT, wx.ALIGN_CENTRE)
		# there is a bug in wxGTK for this method...
		self.__grid_unreviewed_results.AutoSizeColumns(True)
		self.__grid_unreviewed_results.AutoSizeRows(True)
		# what is this supposed to do ?!?
		renderer = apply(cLabJournalCellRenderer, ())
		self.__grid_unreviewed_results.SetDefaultRenderer(renderer)
		# attribute objects let you keep a set of formatting values
		# in one spot, and reuse them if needed
#		font = self.GetFont()
#		font.SetWeight(wxNORMAL)
#		attr = wxGridCellAttr()
#		attr.SetFont(font)
		#attr.SetBackgroundColour(wx.LIGHT_GREY)
#		attr.SetReadOnly(True)
		#attr.SetAlignment(wxRIGHT, -1)
#		self.__grid_unreviewed_results.SetLabelFont(font)
		# layout review grid
		self.__grid_unreviewed_results.SetColLabelValue(0, _('reviewed'))
		self.__grid_unreviewed_results.SetColLabelValue(1, _('relevant'))
		self.__grid_unreviewed_results.SetColLabelValue(2, _('patient'))
		self.__grid_unreviewed_results.SetColLabelValue(3, _('facility'))
		self.__grid_unreviewed_results.SetColLabelValue(4, _('analysis'))
		self.__grid_unreviewed_results.SetColLabelValue(5, _('result'))
		self.__grid_unreviewed_results.SetColLabelValue(6, _('range'))
		self.__grid_unreviewed_results.SetColLabelValue(7, _('info provided by lab'))
		# turn row labels off
		self.__grid_unreviewed_results.SetRowLabelSize(0)
		self.__grid_unreviewed_results.AutoSize()

		# -- add buttons --
		# "select all requests"
		self.BTN_select_all = wx.Button(
			name = 'BTN_select_all',
			parent = pnl_page,
			id = wx.ID_BTN_select_all,
			label = _("select all requests")
		)
		self.BTN_select_all.SetToolTipString(_('select all requests'))
		# "mark selected as reviewed"
		self.BTN_mark_reviewed = wx.Button(
			name = 'BTN_mark_reviewed',
			parent = pnl_page,
			id = wx.ID_BTN_mark_reviewed,
			label = _("mark selected requests as reviewed")
		)
		self.BTN_mark_reviewed.SetToolTipString(_('mark selected requests as reviewed'))

		szr_buttons = wx.BoxSizer(wx.HORIZONTAL)
		szr_buttons.Add(self.BTN_select_all, 0, wx.ALIGN_CENTER_VERTICAL, 1)
		szr_buttons.Add(self.BTN_mark_reviewed, 0, wx.ALIGN_CENTER_VERTICAL, 1)

		# -- do layout --
		szr_page = wx.BoxSizer(wx.VERTICAL)
		szr_page.Add(self.__grid_unreviewed_results, 1, wxEXPAND | wx.ALIGN_CENTER | wx.ALL, 5)
		szr_page.Add(szr_buttons, 0, wxEXPAND | wx.ALIGN_CENTER | wx.ALL, 5)

		pnl_page.SetAutoLayout(True)
		pnl_page.SetSizer(szr_page)
		szr_page.Fit(pnl_page)
		szr_page.SetSizeHints(pnl_page)

		self.AddPage(pnl_page, _("unreviewed results"))
	#------------------------------------------------------------------------
	def __register_events(self):
		wx.EVT_BUTTON(self.BTN_save_request_ID, wx.ID_BTN_save_request_ID, self.on_save_request_ID)
		wx.EVT_BUTTON(self.BTN_select_all, wx.ID_BTN_select_all, self.on_select_all)
		wx.EVT_BUTTON(self.BTN_mark_reviewed, wx.ID_BTN_mark_reviewed, self._on_mark_reviewed)

		wx.EVT_GRID_CELL_LEFT_CLICK(self.__grid_unreviewed_results, self.OnLeftSClick)
		wx.EVT_GRID_CELL_LEFT_DCLICK(self.__grid_unreviewed_results, self.OnLeftDClick)
		#wx.EVT_GRID_SELECT_CELL(self.__grid_unreviewed_results, self.OnSelectCell)
		wx.EVT_KEY_UP(self.__grid_unreviewed_results, self.OnKeyPressed)
	#------------------------------------------------------------------------
	def update(self):
		if self.__pat['pk'] is None:
			gmGuiHelpers.gm_show_error(
				aMessage = _('Cannot load lab journal.\nYou first need to select a patient.'),
				aTitle = _('loading lab journal')
			)
			return None

		if self.__populate_notebook() is None:
			return None
		return 1
	#------------------------------------------------------------------------
	def __populate_notebook(self):
		
		self.fld_request_id.Clear()
		self.lab_wheel.Clear()
		
		#------ due PNL ------------------------------------
		# FIXME: make limit configurable
		too_many, pending_requests = gmPathLab.get_pending_requests(limit=250)
		# clear list
		self.lbox_pending.DeleteAllItems()
		# FIXME: make use of too_many
		for request in pending_requests:
			item_idx = self.lbox_pending.InsertItem(info=wx.ListItem())
			# request date
			self.lbox_pending.SetStringItem(index = item_idx, col=0, label=request['sampled_when'].date)
			# request lab
			lab = self.__get_labname(request['pk_test_org'])
			self.lbox_pending.SetStringItem(index = item_idx, col=1, label=lab[0][0])
			# request id
			self.lbox_pending.SetStringItem(index = item_idx, col=2, label=request['request_id'])
			# patient
			pat = request.get_patient()
			self.lbox_pending.SetStringItem(index = item_idx, col=3, label="%s %s (%s)" % (pat[2], pat[3], pat[4].date))
			self.lbox_pending.SetStringItem(index = item_idx, col=4, label=_('pending'))
			# FIXME: make use of rest data in patient via mouse over context
			
		#----- import errors PNL -----------------------
		lab_errors = self.__get_import_errors()
		# clear list
		self.lbox_errors.DeleteAllItems()
		# populate list
		for lab_error in lab_errors:
			item_idx = self.lbox_errors.InsertItem(info=wx.ListItem())
			# when was error reported
			self.lbox_errors.SetStringItem(index = item_idx, col=0, label=lab_error[1].date)
			# error
			self.lbox_errors.SetStringItem(index = item_idx, col=1, label=lab_error[4])
			# solution
			self.lbox_errors.SetStringItem(index = item_idx, col=2, label=lab_error[5])
			# context
			self.lbox_errors.SetStringItem(index = item_idx, col=3, label=lab_error[6])
		
		#------ unreviewed lab results PNL ------------------------------------
		# FIXME: make configurable, make use of count visible lines func of wxlistctrl
		more_avail, self.dict_unreviewed_results = gmPathLab.get_unreviewed_results(limit=50)

		# FIXME: react to errors

		# clear grid
		self.__grid_unreviewed_results.ClearGrid()
		# set number of rows
		if self.__grid_unreviewed_results.GetNumberRows() == 0:
			self.__grid_unreviewed_results.AppendRows(len(self.dict_unreviewed_results))
		# populate grid
		for item_idx in range(len(self.dict_unreviewed_results)):
			result = self.dict_unreviewed_results[item_idx]

			# boolean renderer for first and second column
			renderer = apply(wx.GridCellBoolRenderer, ())
			self.__grid_unreviewed_results.SetCellRenderer(item_idx, 0 , renderer)
			self.__grid_unreviewed_results.SetCellRenderer(item_idx, 1 , renderer)
			# set all cells read only
			self.__grid_unreviewed_results.SetReadOnly(item_idx, 0, 1)
			self.__grid_unreviewed_results.SetReadOnly(item_idx, 1, 1)
			#self.__grid_unreviewed_results.SetReadOnly(item_idx, 2, True)
			self.__grid_unreviewed_results.EnableGridLines(0)
			# "reviewed" checkbox in first column
			try:
				self.__grid_unreviewed_results.SetColSize(0, self.__grid_unreviewed_results.GetColMinimalAcceptableWidth())
			except AttributeError:
				pass
			self.__grid_unreviewed_results.SetCellValue(item_idx, 0, '0')
			# "relevant" checkbox in second column
			try:
				self.__grid_unreviewed_results.SetColSize(1, self.__grid_unreviewed_results.GetColMinimalAcceptableWidth())
			except AttributeError:
				pass
			self.__grid_unreviewed_results.SetCellValue(item_idx, 1, '0')
			# abnormal ? -> display in red
			if (result['abnormal'] is not None) and (result['abnormal'].strip() != ''):
				self.__grid_unreviewed_results.SetCellTextColour(item_idx,2,wx.RED)
				self.__grid_unreviewed_results.SetCellTextColour(item_idx,3,wx.RED)
				self.__grid_unreviewed_results.SetCellTextColour(item_idx,4,wx.RED)
				self.__grid_unreviewed_results.SetCellTextColour(item_idx,5,wx.RED)
				self.__grid_unreviewed_results.SetCellTextColour(item_idx,6,wx.RED)
				self.__grid_unreviewed_results.SetCellTextColour(item_idx,7,wx.RED)
				# abnormal status from lab
				info = '(%s)' % result['abnormal']
				# technically abnormal -> defaults to relevant = true
				self.__grid_unreviewed_results.SetCellValue(item_idx, 1, '1')
			else:
				info = ''
				# technically normal -> defaults to relevant = False
				self.__grid_unreviewed_results.SetCellValue(item_idx, 1, '0')
			# patient
			pat = result.get_patient()
			self.__grid_unreviewed_results.SetCellValue(item_idx, 2, "%s %s (%s)" % (pat[2], pat[3], pat[4].date))
			self.__grid_unreviewed_results.SetColSize(2,200)
			# rxd when
			self.__grid_unreviewed_results.SetCellValue(item_idx, 3, result['lab_rxd_when'].date)
			self.__grid_unreviewed_results.SetColSize(3,80)
			# test name
			self.__grid_unreviewed_results.SetCellValue(item_idx, 4, result['unified_name'])
			self.__grid_unreviewed_results.SetColSize(4,100)
			# result including unit
			# FIXME: what about val_unit empty ?
			self.__grid_unreviewed_results.SetCellValue(item_idx, 5, '%s %s' % (result['unified_val'], info))
			self.__grid_unreviewed_results.SetColSize(5,80)
			# normal range
			if result['val_normal_range'] is None:
				self.__grid_unreviewed_results.SetCellValue(item_idx, 6, '')
			else:
				self.__grid_unreviewed_results.SetCellValue(item_idx, 6, '%s %s' % (result['val_normal_range'], result['val_unit']))
			self.__grid_unreviewed_results.SetColSize(6,80)
			# FIXME: target range
			# notes from provider
			if result['note_provider'] is None:
				self.__grid_unreviewed_results.SetCellValue(item_idx, 7, '')
			else:
				self.__grid_unreviewed_results.SetCellValue(item_idx, 7, result['note_provider'])

		# we show 50 items at once , notify user if there are more
		if more_avail:
			gmDispatcher.send(signal = 'statustext', msg =_('More unreviewed results available. Review some to see more.'))
	#------------------------------------------------------------------------
	def __get_import_errors(self):
		query = """select * from housekeeping_todo where category='lab'"""
		import_errors = gmPG.run_ro_query('historica', query)
		return import_errors
	#------------------------------------------------------------------------
	def __get_labname(self, data):
		# FIXME: eventually, this will be done via a cOrg value object class
		query= """select internal_name from test_org where pk=%s"""
		labs = gmPG.run_ro_query('historica', query, None, data)
		return labs

	#-----------------------------------
	# event handlers
	#------------------------------------------------------------------------
	def OnLeftSClick(self, event):
		self.OnSelectCell(event, selector='LSClick')
		event.Skip()	
	#------------------------------------------------------------------------
	def OnLeftDClick(self, event):
		self.OnSelectCell(event, selector='LDClick')
		event.Skip()
	#------------------------------------------------------------------------
	def CrosscheckRelevant(self):
		# reviewed checked -> check relevant if result is abnormal
		#if (result['abnormal'] is not None) and (result['abnormal'].strip() != ''):
		#	self.__grid_unreviewed_results.SetCellValue(row, col, '1')
		print "only stub for Crosscheck - please fix"
	#------------------------------------------------------------------------
	def OnSelectCell(self, event, selector=None):
		if selector is None:
#			event.Skip()
			return None

		if selector in ['SelKEY', 'LDClick']: 
			#print 'key pressed %s' %selector
			col = self.__grid_unreviewed_results.GetGridCursorCol()
			row = self.__grid_unreviewed_results.GetGridCursorRow()
		if selector in ['LSClick']:
			#print 'key pressed %s' %selector
			col = event.GetCol()
			row = event.GetRow()

		if col in [0,1]:
			if self.__grid_unreviewed_results.GetCellValue(row,col) == '1':		# if set
				self.__grid_unreviewed_results.SetCellValue(row,col, '0')		# then unset
			else:																# if unset
				self.__grid_unreviewed_results.SetCellValue(row,col,'1')		# then set
				self.CrosscheckRelevant()
			event.Skip()
	#-------------------------------------------------------
	def OnKeyPressed (self, key):
		"""Is called when a key is pressed."""
		#key.Skip()

		# user moved down
		if key.GetKeyCode() == WXK_DOWN:
			key.Skip()
			#self.__on_down_arrow(key)
			return
		# user moved up
		if key.GetKeyCode() == WXK_UP:
			key.Skip()
			#self.__on_up_arrow(key)
			return

		# FIXME: need PAGE UP/DOWN//POS1/END here
			
		#user pressed <SPACE>
		if key.GetKeyCode() == WXK_SPACE:
			self.OnSelectCell(key,selector='SelKEY')
			return
	# -------------------------------------------------
	def on_save_request_ID(self, event):
		req_id = self.fld_request_id.GetValue()
		if (req_id is None) or (req_id.strip() == ''):
			gmGuiHelpers.gm_show_error (
				_('You must type in a request ID !\n\nUsually you will find the request ID written on\nthe barcode sticker on your probe container.'),
				_('saving request id')
			)
			return None
		emr = self.__pat.get_emr()
		request = emr.add_lab_request(lab=int(self.lab), req_id = req_id)
		if request is None:
			gmDispatcher.send(signal = 'statustext', msg =_('Cannot save lab request.'))
			return None

		# FIXME: maybe populate request list only ?
		# btw, we can make the sub-notebook tabs load data on-demand just
		# like the main notebook tabs :-)
		self.__populate_notebook()
	#------------------------------------------------
	def on_select_all(self, event):
		for item_idx in range(self.__grid_unreviewed_results.GetNumberRows()):
			self.__grid_unreviewed_results.SetCellValue(item_idx, 0, '1')
	#------------------------------------------------
	def _on_mark_reviewed(self, event):
		reviewed_results = []
		for row in range(self.__grid_unreviewed_results.GetNumberRows()):
			if self.__grid_unreviewed_results.GetCellValue(row, 0) == '1':
				# look up associated request
				result = self.dict_unreviewed_results[row]
				reviewed_results.append(result)
				# update "relevant" status
				relevant = self.__grid_unreviewed_results.GetCellValue(row, 1)
				if relevant == '1':
					result['relevant'] = 'true'
				else:
					result['relevant'] = 'false'

		if len(reviewed_results) == 0:
			gmGuiHelpers.beep_status_text(_('No results marked as reviewed.'))
			event.Skip()
			return None
		
		for result in reviewed_results:
			result['reviewed'] = 'true'
			result['pk_reviewer'] = gmPerson.gmCurrentProvider()['pk_staff']
			if not result['abnormal']:
				result['abnormal'] = ''
			successfull, error = result.save_payload()
			# repopulate
			if successfull:
				self.__populate_notebook()
			else:
				_log.Log(gmLog.lErr, 'setting result status to reviewed failed %s' % error)
				gmGuiHelpers.gm_show_error (
					aMessage = _('Cannot mark results as "reviewed":\n%s') % error,
					aTitle = _('update result status')
				)
				return None
			
		event.Skip()
	#--------------------------------------------------------
	def __on_right_click(self, evt):
		event.Skip()
	#-------------------------------------------------------
	def on_lab_selected(self,data):
		if data is None:
			self.fld_request_id.SetValue('')
			return None
		# propose new request id
		nID = gmPathLab.get_next_request_ID(int(data))
		if not nID is None:
			# set field to that
			self.fld_request_id.SetValue(nID)
		# FIXME : this is needed so save_request_ID knows about the lab
		self.lab =  data

#=========================================================
class cLabDataGrid(wx.Grid):
	"""This wx.Grid derivative displays a grid view of stored lab data.
	"""
	def __init__(self, parent, id):
		"""Set up our specialised grid.
		"""
		# get connection
		self.__backend = gmPG.ConnectionPool()
		self.__defconn = self.__backend.GetConnection('blobs')
		if self.__defconn is None:
			_log.Log(gmLog.lErr, "Cannot retrieve lab data without database connection !")
			raise gmExceptions.ConstructorError, "cLabDataGrid.__init__(): need db conn"

		# connect to config database
		self.__dbcfg = gmCfg.cCfgSQL(
			aConn = self.__backend.GetConnection('default'),
			aDBAPI = gmPG.dbapi
		)
		
		wx.Grid.__init__(
			self,
			parent,
			id,
			pos = wx.DefaultPosition,
			size = wx.DefaultSize,
			style= wx.WANTS_CHARS
			)
		
		self.__pat = gmPerson.gmCurrentPatient()

		#wx.EVT_GRID_CELL_LEFT_DCLICK(self, self.OnLeftDClick)
		
		# create new grid
		self.__grid_unreviewed_results = self.CreateGrid(0, 0, wx.Grid.wx.GridSelectCells )
		self.SetDefaultCellAlignment(wx.ALIGN_RIGHT,wx.ALIGN_CENTRE)
		#renderer = apply(wxGridCellStringRenderer, ())
		renderer = apply(cLabDataGridCellRenderer, ())
		self.SetDefaultRenderer(renderer)
		
		# There is a bug in wxGTK for this method...
		self.AutoSizeColumns(True)
		self.AutoSizeRows(True)
		# attribute objects let you keep a set of formatting values
		# in one spot, and reuse them if needed
		font = self.GetFont()
		#font.SetWeight(wx.BOLD)
		attr = wx.GridCellAttr()
		attr.SetFont(font)
		#attr.SetBackgroundColour(wx.LIGHT_GREY)
		attr.SetReadOnly(True)
		#attr.SetAlignment(wxRIGHT, -1)
		#attr.IncRef()
		#self.SetLabelFont(font)
	

	# I do this because I don't like the default behaviour of not starting the
	# cell editor on double clicks, but only a second click.
	def OnLeftDClick(self, evt):
		if self.CanEnableCellControl():
			self.EnableCellEditControl()

	#------------------------------------------------------------------------
	def update(self):
		if self.__pat['pk'] is None:
			_log.Log(gmLog.lErr, 'need patient for update')
			gmGuiHelpers.gm_show_error(
				aMessage = _('Cannot load lab data.\nYou first need to select a patient.'),
				aTitle = _('loading lab data')
			)
			return None

		if self.__populate_grid() is None:
			return None

		return 1
		
	#------------------------------------------------------------------------
	def __populate_grid(self):
		"""Fill grid with data.

		sorting:
			1) check user's preferred way of sorting
				none defaults to smart sorting
			2) check if user defined lab profiles
				- add a notebook tab for each profile
				- postpone profile dependent stats until tab is selected
			sort modes :
				1: no profiles -> smart sorting only
				2: profile -> smart sorting first
				3: profile -> user defined profile order
		"""
		emr = self.__pat.get_emr()
		# FIXME: there might be too many results to handle in memory
		results = emr.get_lab_results()
		if results is None:
			name = self.__pat.get_names()
			gmGuiHelpers.gm_show_error (
				aMessage = _('Error loading lab data for patient\n[%s %s].') % (name['firstnames'], name['lastnames']),
				aTitle = _('loading lab data')
			)
			return None
		if len(results) == 0:
			gmDispatcher.send(signal = 'statustext', msg =_('No lab data available.'))
			return None
			
		dates, test_names = self.__compile_stats(results)
		# sort tests before pushing onto the grid 
		#sort_mode = gmPerson.getsort_mode() # yet to be written
		sort_mode = 1 # get real here :-)
			
		if sort_mode == 1:
			"""
			2) look at the the most recent date a test was performed on
				move these tests to the top
			3) sort by runs starting with most recent date
				a run is a series of consecutive dates a particular test was done on
				sort by length of the runs
				longest run will move to the top
			"""
			pass

		# clear grid
		self.ClearGrid()
		# add columns
		if self.GetNumberCols() == 0:
			self.AppendCols(len(dates))
			# set column labels
			for i in range(len(dates)):
				self.SetColLabelValue(i, dates[i])
		# add rows
		if self.GetNumberRows() == 0:
			self.AppendRows(len(test_names))
			# add labels
			for i in range(len(test_names)):
				self.SetRowLabelValue(i, test_names[i])
		# push data onto grid
		cells = []
		for result in results:
			# get  x,y position for result
			x = dates.index(result['val_when'].date)
			y = test_names.index(result['unified_name'])
			cell_data = self.GetCellValue(x, y)
			if cell_data == '':
				self.SetCellValue(x, y, '%s %s' % (result['unified_val'], result['val_unit']))
			else:
				self.SetCellValue(x, y, '%s\n%s %s' % (cell_data, result['unified_val'], result['val_unit']))
			# you can set cell attributes for the whole row (or column)
			#self.SetRowAttr(int(y), attr)
			#self.SetColAttr(int(x), attr)
			#self.SetCellRenderer(int(x), int(y), renderer)

		self.AutoSize()
		return 1
	#------------------------------------------------------------------------
	def __compile_stats(self, lab_results=None):
		# parse record for dates and tests
		dates = []
		test_names = []
		for result in lab_results:
			if result['val_when'].date not in dates:
				dates.append(result['val_when'].date)
			if result['unified_name'] not in test_names:
				test_names.append(result['unified_name'])
		dates.sort()
		
		return dates, test_names
	#------------------------------------------------------------------------
	#def sort_by_value(self, d=None):
	#    """ Returns the keys of dictionary d sorted by their values """
	#    items=d.items()
	#    backitems=[ [v[1],v[0]] for v in items]
	#    backitems.sort()
	#    return [ backitems[i][1] for i in range(0,len(backitems))]
	
	#--------------------------------------------------------
	def __on_right_click(self, evt):
		pass
		#evt.Skip()

#=========================================================
# MAIN
#---------------------------------------------------------
if __name__ == '__main__':
	_log.Log (gmLog.lInfo, "starting lab journal")

	# catch all remaining exceptions
	try:
		application = wxPyWidgetTester(size=(640,480))
		application.SetWidget(cStandalonePanel,-1)
		application.MainLoop()
	except:
		_log.LogException("unhandled exception caught !", sys.exc_info(), 1)
		# but re-raise them
		raise
	#gmPG.StopListeners()
	_log.Log (gmLog.lInfo, "closing lab journal")
#=========================================================
# $Log: gmLabWidgets.py,v $
# Revision 1.30  2008-01-30 14:08:06  ncq
# - do not use old cfg file support anymore
#
# Revision 1.29  2008/01/11 16:15:32  ncq
# - first/last -> first-/lastnames
#
# Revision 1.28  2007/08/28 14:18:13  ncq
# - no more gm_statustext()
#
# Revision 1.27  2007/02/22 17:41:13  ncq
# - adjust to gmPerson changes
#
# Revision 1.26  2007/02/05 12:15:23  ncq
# - no more aMatchProvider/selection_only in cPhraseWheel.__init__()
#
# Revision 1.25  2007/01/20 22:52:27  ncq
# - .KeyCode -> GetKeyCode()
#
# Revision 1.24  2007/01/18 22:07:52  ncq
# - (Get)KeyCode() -> KeyCode so 2.8 can do
#
# Revision 1.23  2006/11/24 10:01:31  ncq
# - gm_beep_statustext() -> gm_statustext()
#
# Revision 1.22  2006/10/25 07:21:57  ncq
# - no more gmPG
#
# Revision 1.21  2006/08/04 05:46:15  ncq
# - fix wx import style
#
# Revision 1.20  2006/07/19 20:29:50  ncq
# - import cleanup
#
# Revision 1.19  2006/05/12 12:18:11  ncq
# - whoami -> whereami cleanup
# - use gmCurrentProvider()
#
# Revision 1.18  2006/05/04 09:49:20  ncq
# - get_clinical_record() -> get_emr()
# - adjust to changes in set_active_patient()
# - need explicit set_active_patient() after ask_for_patient() if wanted
#
# Revision 1.17  2005/12/27 18:57:47  ncq
# - fix syntax error
#
# Revision 1.16  2005/09/28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.15  2005/09/28 15:57:48  ncq
# - a whole bunch of wx.Foo -> wx.Foo
#
# Revision 1.14  2005/09/26 18:01:51  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.13  2005/09/24 09:17:29  ncq
# - some wx2.6 compatibility fixes
#
# Revision 1.12  2005/06/10 23:22:43  ncq
# - SQL2 match provider now requires query *list*
#
# Revision 1.11  2005/05/05 06:28:23  ncq
# - renamed phrasewheel methods
#
# Revision 1.10  2005/03/06 14:54:19  ncq
# - szr.AddWindow() -> Add() such that wx2.5 works
# - 'demographic record' -> get_identity()
#
# Revision 1.9  2005/02/15 18:33:08  ncq
# - identity.id -> pk
#
# Revision 1.8  2005/01/31 10:37:26  ncq
# - gmPatient.py -> gmPerson.py
#
# Revision 1.7  2004/10/27 12:18:19  ncq
# - insignificant cleanup
#
# Revision 1.6  2004/10/20 21:47:24  ncq
# - cleanup, improve variable naming/error handling
# - in LabJournal consolidate layouting
#
# Revision 1.5  2004/10/01 13:33:41  ncq
# - older wxPythons don't have grid.GetColMinimalAcceptableWidth so do try: except:
#
# Revision 1.4  2004/09/29 19:14:31  ncq
# - id -> pk
#
# Revision 1.3  2004/07/18 20:30:53  ncq
# - wxPython.true/false -> Python.True/False as Python tells us to do
#
# Revision 1.2  2004/07/15 15:55:14  ncq
# - include factored out code from gui/gmShowLab.py
#
# Revision 1.1  2004/07/15 15:03:41  ncq
# - factored out from wxpython/gui/gmLabJournal.py
#
