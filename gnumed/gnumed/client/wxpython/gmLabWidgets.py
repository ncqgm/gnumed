"""This widgets lets you manage laboratory requests

 - add requests
 - keep track of pending requests
 - see import errors
 - review newly imported lab results
"""
#============================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmLabWidgets.py,v $
__version__ = "$Revision: 1.1 $"
__author__ = "Sebastian Hilbert <Sebastian.Hilbert@gmx.net>"

# system
import os.path, sys, os, re
# FIXME: debugging
import time

# 3rd party
from wxPython.wx import *
from wxPython.lib.mixins.listctrl import wxColumnSorterMixin, wxListCtrlAutoWidthMixin
from wxPython.grid import *

from Gnumed.pycommon import gmLog, gmI18N, gmPG, gmCfg, gmExceptions, gmWhoAmI, gmMatchProvider, gmGuiBroker
from Gnumed.business import gmPatient, gmClinicalRecord, gmPathLab
from Gnumed.wxpython import gmGuiHelpers, gmPhraseWheel
from Gnumed.pycommon.gmPyCompat import *

_log = gmLog.gmDefLog
if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)
_log.Log(gmLog.lInfo, __version__)
_cfg = gmCfg.gmDefCfgFile
_whoami = gmWhoAmI.cWhoAmI()

[   wxID_PNL_main,
	wxID_NB_LabJournal,
	wxID_LBOX_pending_results,
	wxID_PHRWH_labs,
	wxID_TXTCTRL_ids,
	wxID_BTN_save_request_ID,
	wxID_BTN_select_all,
	wxID_BTN_mark_reviewed
] = map(lambda _init_ctrls: wxNewId(), range(8))

#====================================
class cLabJournalCellRenderer(wxPyGridCellRenderer):
	def __init__(self):
		wxPyGridCellRenderer.__init__(self)

	def Draw(self, grid, attr, dc, rect, row, col, isSelected):
		dc.SetBackgroundMode(wxSOLID)
		dc.SetBrush(wxBrush(wxBLACK, wxSOLID))
		dc.SetPen(wxTRANSPARENT_PEN)
		dc.DrawRectangle(rect.x, rect.y, rect.width, rect.height)
		dc.SetBackgroundMode(wxTRANSPARENT)
		dc.SetFont(attr.GetFont())

		text = grid.GetCellValue(row, col)
		colors = [wxRED, wxWHITE, wxCYAN]
		x = rect.x + 1
		y = rect.y + 1
		for ch in text:
			dc.SetTextForeground(random.choice(colors))
			dc.DrawText(ch, x, y)
			w, h = dc.GetTextExtent(ch)
			x = x + w
			if x > rect.right - 5:
				break

#=======================================
class cLabReviewGrid(wxGrid):
	"""This wxGrid derivative displays lab data that has not yet been reviewed by a clinician.
	"""
	def __init__(self, parent, id):
		"""Set up our specialised grid.
		"""
		wxGrid.__init__(
			self,
			parent,
			id,
			pos = wxDefaultPosition,
			size = wxDefaultSize,
			style= wxWANTS_CHARS
			)

#====================================
class cLabWheel(gmPhraseWheel.cPhraseWheel):
	def __init__(self, parent):
		query = """
			select pk, internal_name
			from test_org
			"""
		self.mp = gmMatchProvider.cMatchProvider_SQL2('historica', query)
		self.mp.setThresholds(aWord=2, aSubstring=4)

		gmPhraseWheel.cPhraseWheel.__init__(
			self,
			parent = parent,
			id = -1,
			aMatchProvider = self.mp,
			size = wxDefaultSize,
			pos = wxDefaultPosition
		)
		self.SetToolTipString(_('choose which lab will process the probe with the specified ID'))

#====================================
# FIXME: is this really lab specific ?
class cLabIDListCtrl(wxListCtrl, wxListCtrlAutoWidthMixin):
	def __init__(self, parent, ID, pos=wxDefaultPosition, size=wxDefaultSize, style=0):
		wxListCtrl.__init__(self, parent, ID, pos, size, style)
		wxListCtrlAutoWidthMixin.__init__(self)

#====================================
class cLabJournalNB(wxNotebook):
	"""This wxNotebook derivative displays 'records still due' and lab-import related errors.
	"""
	def __init__(self, parent, id):
		"""Set up our specialised notebook.
		"""
		wxNotebook.__init__(
			self,
			parent,
			id,
			wxDefaultPosition,
			wxDefaultSize,
			0
		)
		# tab with pending requests
		self.PNL_due_tab = wxPanel( self, -1 )
		szr_due = self.__init_SZR_due()

		self.PNL_due_tab.SetAutoLayout( True )
		self.PNL_due_tab.SetSizer( szr_due )
		szr_due.Fit( self.PNL_due_tab )
		szr_due.SetSizeHints(self.PNL_due_tab)

		self.AddPage( self.PNL_due_tab, _("add | view pending requests"))

		# tab with errors
		self.PNL_errors_tab = wxPanel( self, -1)
		szr_errors = self.__init_SZR_import_errors()

		self.PNL_errors_tab.SetAutoLayout( True )
		self.PNL_errors_tab.SetSizer( szr_errors )
		szr_errors.Fit( self.PNL_errors_tab )
		szr_errors.SetSizeHints( self.PNL_errors_tab )

		self.AddPage( self.PNL_errors_tab, _("lab errors"))
		
		# tab with unreviewed lab results
		self.PNL_review_tab = wxPanel( self, -1)
		szr_review = self.__init_SZR_review_status()

		self.PNL_review_tab.SetAutoLayout( True )
		self.PNL_review_tab.SetSizer( szr_review )
		szr_review.Fit( self.PNL_review_tab )
		szr_review.SetSizeHints( self.PNL_review_tab )

		self.AddPage( self.PNL_review_tab, _("unreviewed results"))
		
		self.curr_pat = gmPatient.gmCurrentPatient()
	#------------------------------------------------------------------------
	def __init_SZR_due (self):

		vbszr = wxBoxSizer( wxVERTICAL )
		hbszr = wxStaticBoxSizer(wxStaticBox(self.PNL_due_tab, -1, _("add new request for current patient")), wxHORIZONTAL)
		
		self.lab_label = wxStaticText(
			name = 'lablabel',
			parent = self.PNL_due_tab,
			id = -1,
			label = _('Lab')
		)
		
		# available labs go here
		self.lab_wheel = cLabWheel(self.PNL_due_tab)
		self.lab_wheel.on_resize (None)
		self.lab_wheel.addCallback(self.on_lab_selected)

		hbszr.AddWindow(self.lab_label, 0, wxALIGN_CENTER | wxALL, 5)
		hbszr.AddWindow(self.lab_wheel, 0, wxALIGN_CENTER | wxALL, 5)

		#vbszr.Add(hbszr, 0, wxALIGN_LEFT | wxALL, 5)

		self.req_id_label = wxStaticText(
			name = 'req_id_label',
			parent = self.PNL_due_tab,
			id = -1,
			label = _("Specimen ID")
		)
		
		# request_id field
		self.fld_request_id = wxTextCtrl(
			self.PNL_due_tab,
			wxID_TXTCTRL_ids,
			"",
			wxDefaultPosition,
			wxSize(80,-1),
			0
			)
		
		hbszr.AddWindow(self.req_id_label, 0, wxALIGN_CENTER | wxALL, 5)
		hbszr.AddWindow(self.fld_request_id, 0, wxALIGN_CENTER| wxALL, 5 )

		# -- "save request id" button -----------
		self.BTN_save_request_ID = wxButton(
			name = 'BTN_save_request_ID',
			parent = self.PNL_due_tab,
			id = wxID_BTN_save_request_ID,
			label = _("save request ID")
		)
		self.BTN_save_request_ID.SetToolTipString(_('associate chosen lab and ID with current patient'))
		EVT_BUTTON(self.BTN_save_request_ID, wxID_BTN_save_request_ID, self.on_save_request_ID)

		hbszr.Add(self.BTN_save_request_ID, 0, wxALIGN_CENTER|wxALL, 5 )
		vbszr.Add(hbszr,0, wxALIGN_LEFT | wxALL, 5)
		
		# our actual list
		tID = wxNewId()
		self.lbox_pending = cLabIDListCtrl(
			self.PNL_due_tab,
			tID,
			size=wxDefaultSize,
			style=wxLC_REPORT|wxSUNKEN_BORDER|wxLC_VRULES
		)

		self.lbox_pending.InsertColumn(0, _("date"))
		self.lbox_pending.InsertColumn(1, _("lab"))
		self.lbox_pending.InsertColumn(2, _("sample id"))
		self.lbox_pending.InsertColumn(3, _("patient"))
		self.lbox_pending.InsertColumn(4, _("status"))
		
		vbszr.AddWindow( self.lbox_pending, 1, wxEXPAND|wxALIGN_CENTER|wxALL, 5 )
		return vbszr

	def __init_SZR_import_errors (self):
		vbszr = wxBoxSizer( wxVERTICAL )

		tID = wxNewId()
		self.lbox_errors = cLabIDListCtrl(
			self.PNL_errors_tab,
			tID,
			size=wxDefaultSize,
			style=wxLC_REPORT|wxSUNKEN_BORDER|wxLC_VRULES
		)

		vbszr.AddWindow(self.lbox_errors, 1, wxEXPAND| wxALIGN_CENTER | wxALL, 5)

		self.lbox_errors.InsertColumn(0, _("noticed when"))
		self.lbox_errors.InsertColumn(1, _("problem"))
		self.lbox_errors.InsertColumn(2, _("solution"))
		self.lbox_errors.InsertColumn(3, _("context"))
		return vbszr

	def __init_SZR_review_status (self):
	
		tID = wxNewId()
		vbszr = wxBoxSizer( wxVERTICAL )
		
		# create new grid		
		self.DataGrid = cLabReviewGrid(
				self.PNL_review_tab,
				tID
				)
				
		EVT_GRID_CELL_LEFT_CLICK(self.DataGrid, self.OnLeftSClick)
		EVT_GRID_CELL_LEFT_DCLICK(self.DataGrid, self.OnLeftDClick)
		#EVT_GRID_SELECT_CELL(self.DataGrid, self.OnSelectCell)
		EVT_KEY_UP(self.DataGrid, self.OnKeyPressed)
		
		self.DataGrid.CreateGrid(0, 8, wxGrid.wxGridSelectCells )
		self.DataGrid.SetDefaultCellAlignment(wxALIGN_LEFT,wxALIGN_CENTRE)
		renderer = apply(cLabJournalCellRenderer, ())
		self.DataGrid.SetDefaultRenderer(renderer)

		# There is a bug in wxGTK for this method...
		self.DataGrid.AutoSizeColumns(True)
		self.DataGrid.AutoSizeRows(True)
		# attribute objects let you keep a set of formatting values
		# in one spot, and reuse them if needed
		font = self.GetFont()
		font.SetWeight(wxNORMAL)
		attr = wxGridCellAttr()
		attr.SetFont(font)
		
		#attr.SetBackgroundColour(wxLIGHT_GREY)
		attr.SetReadOnly(True)
		#attr.SetAlignment(wxRIGHT, -1)
		self.DataGrid.SetLabelFont(font)

		# layout review grid
		self.DataGrid.SetColLabelValue(0, _('reviewed'))
		self.DataGrid.SetColLabelValue(1, _('relevant'))
		self.DataGrid.SetColLabelValue(2, _('patient'))
		self.DataGrid.SetColLabelValue(3, _('facility'))
		self.DataGrid.SetColLabelValue(4, _('analysis'))
		self.DataGrid.SetColLabelValue(5, _('result'))
		self.DataGrid.SetColLabelValue(6, _('range'))
		self.DataGrid.SetColLabelValue(7, _('info provided by lab'))
		
		# turn row labels off
		self.DataGrid.SetRowLabelSize(0)
		
		self.DataGrid.AutoSize()
		vbszr.AddWindow(self.DataGrid, 1, wxEXPAND | wxALIGN_CENTER | wxALL, 5)
		
		szr_buttons = wxBoxSizer(wxHORIZONTAL)
		
		# -- "select all requests" button -----------
		self.BTN_select_all = wxButton(
			name = 'BTN_select_all',
			parent = self.PNL_review_tab,
			id = wxID_BTN_select_all,
			label = _("select all requests")
		)
		self.BTN_select_all.SetToolTipString(_('select all requests'))
		EVT_BUTTON(self.BTN_select_all, wxID_BTN_select_all, self.on_select_all)
		szr_buttons.Add(self.BTN_select_all, 0, wxALIGN_CENTER_VERTICAL, 1)

		# -- "mark selected as reviewed" button -----------
		self.BTN_mark_reviewed = wxButton(
			name = 'BTN_mark_reviewed',
			parent = self.PNL_review_tab,
			id = wxID_BTN_mark_reviewed,
			label = _("mark selected requests as reviewed")
		)
		self.BTN_mark_reviewed.SetToolTipString(_('mark selected requests as reviewed'))
		EVT_BUTTON(self.BTN_mark_reviewed, wxID_BTN_mark_reviewed, self.on_mark_reviewed)
		szr_buttons.Add(self.BTN_mark_reviewed, 0, wxALIGN_CENTER_VERTICAL, 1)
		
		vbszr.Add(szr_buttons, 0, wxEXPAND | wxALIGN_CENTER | wxALL, 5)
		
		return vbszr
	
	#------------------------------------------------------------------------
	def update(self):
		if self.curr_pat['ID'] is None:
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
			item_idx = self.lbox_pending.InsertItem(info=wxListItem())
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
			item_idx = self.lbox_errors.InsertItem(info=wxListItem())
			# when was error reported
			self.lbox_errors.SetStringItem(index = item_idx, col=0, label=lab_error[1].date)
			# error
			self.lbox_errors.SetStringItem(index = item_idx, col=1, label=lab_error[4])
			# solution
			self.lbox_errors.SetStringItem(index = item_idx, col=2, label=lab_error[5])
			# context
			self.lbox_errors.SetStringItem(index = item_idx, col=3, label=lab_error[6])
		
		#------ unreviewed lab results PNL ------------------------------------
		#t1 = time.time()
		# FIXME: make configurable, make use of count visible lines func of wxlistctrl
		more_avail, data = gmPathLab.get_unreviewed_results(limit=50)
		#t2 = time.time()
		#print t2-t1
		
		self.dict_req_unreviewed = {}
		# clear grid
		self.DataGrid.ClearGrid()
		# add rows
		if self.DataGrid.GetNumberRows() == 0:
			self.DataGrid.AppendRows(len(data))
		# populate grid
		for item_idx in range(len(data)):
			result = data[item_idx]

			# -- chose boolean renderer for first and second column
			renderer = apply(wxGridCellBoolRenderer, ())
			self.DataGrid.SetCellRenderer(item_idx, 0 , renderer)
			self.DataGrid.SetCellRenderer(item_idx, 1 , renderer)
			# set all cells read only
			self.DataGrid.SetReadOnly(item_idx, 0, 1)
			self.DataGrid.SetReadOnly(item_idx, 1, 1)
			#self.DataGrid.SetReadOnly(item_idx, 2, True)
			# turn off grid
			self.DataGrid.EnableGridLines(0)
	
			# -- put reviewed status checkbox in first column
			self.DataGrid.SetColSize(0,self.DataGrid.GetColMinimalAcceptableWidth())
			self.DataGrid.SetCellValue(item_idx, 0, '1')
			# -- put relevant status checkbox in second column
			self.DataGrid.SetColSize(1,self.DataGrid.GetColMinimalAcceptableWidth())
			self.DataGrid.SetCellValue(item_idx, 0, '0')
			# -- abnormal ? -> display in red
			if (result['abnormal'] is not None) and (result['abnormal'].strip() != ''):
				self.DataGrid.SetCellTextColour(item_idx,2,wxRED)
				self.DataGrid.SetCellTextColour(item_idx,3,wxRED)
				self.DataGrid.SetCellTextColour(item_idx,4,wxRED)
				self.DataGrid.SetCellTextColour(item_idx,5,wxRED)
				self.DataGrid.SetCellTextColour(item_idx,6,wxRED)
				self.DataGrid.SetCellTextColour(item_idx,7,wxRED)
				# abnormal status from lab
				info = '(%s)' % result['abnormal']
				# technically abnormal -> defaults to relevant = true
				self.DataGrid.SetCellValue(item_idx, 1, '1')
			else:
				info = ''
				# technically normal -> defaults to relevant = false
				self.DataGrid.SetCellValue(item_idx, 1, '0')
			# -- patient
			pat = result.get_patient()
			self.DataGrid.SetCellValue(item_idx, 2, "%s %s (%s)" % (pat[2], pat[3] ,pat[4].date ))
			self.DataGrid.SetColSize(2,200)
			# -- rxd when
			self.DataGrid.SetCellValue(item_idx, 3, result['lab_rxd_when'].date)
			self.DataGrid.SetColSize(3,80)
			# -- test name
			self.DataGrid.SetCellValue(item_idx, 4, result['unified_name'])
			self.DataGrid.SetColSize(4,100)
			# -- result including unit
			# FIXME: what about val_unit empty ?
			self.DataGrid.SetCellValue(item_idx, 5, '%s %s' % (result['unified_val'], info))
			self.DataGrid.SetColSize(5,80)
			# -- normal range
			if result['val_normal_range'] is None:
				self.DataGrid.SetCellValue(item_idx, 6, '')
			else:
				self.DataGrid.SetCellValue(item_idx, 6, '%s %s' % (result['val_normal_range'], result['val_unit']))
			self.DataGrid.SetColSize(6,80)
			# -- notes from provider 
			if result['note_provider'] is None:
				self.DataGrid.SetCellValue(item_idx, 7, '')
			else:
				self.DataGrid.SetCellValue(item_idx, 7, result['note_provider'])
			# we need to track the request to be able to identify the request later
			self.dict_req_unreviewed[item_idx] = result

		# we show 50 items at once , notify user if there are more
		if more_avail:
			gmGuiHelpers.gm_beep_statustext(_('More unreviewed results available. Review some to see more.'))
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
		#	self.DataGrid.SetCellValue(row, col, '1')
		print "only stub for Crosscheck - please fix"
	#------------------------------------------------------------------------
	def OnSelectCell(self,event,selector=None):
		if selector is None:
			event.Skip()
			return None
		if selector in ['SelKEY','LDClick']: 
			#print 'key pressed %s' %selector
			col = self.DataGrid.GetGridCursorCol()
			row = self.DataGrid.GetGridCursorRow()
			sel = True
		if selector in ['LSClick']:
			#print 'key pressed %s' %selector
			col = event.GetCol()
			row = event.GetRow()
			sel = True
		if sel:
			if col == 0 or 1:
				if self.DataGrid.GetCellValue(row,col) == '1':
					self.DataGrid.SetCellValue(row,col,'0')
				else:
					self.DataGrid.SetCellValue(row,col,'1')
					self.CrosscheckRelevant()
			else:
				event.Skip()
		pass
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
		if not req_id is None or req_id.strip() == '':
			emr = self.curr_pat.get_clinical_record()
			if emr is None:
				# FIXME: error message
				return None

			test = gmPathLab.create_lab_request(
				lab=int(self.lab),
				req_id = req_id,
				pat_id = self.curr_pat['ID'],
				encounter_id = emr.get_active_encounter()['pk_encounter'],
				episode_id = emr.get_active_episode()['pk_episode']
			)
			# FIXME : react on succes or failure of save_request
			
		else :
			_log.Log(gmLog.lErr, 'No request ID typed in yet !')
			gmExceptions.gm_show_error (
				_('You must type in a request ID !\n\nUsually you will find the request ID written on\nthe barcode sticker on your probe container.'),
				_('saving request id')
			)
			return None
		# FIXME: maybe populate request list only ?
		# btw, we can make the sub-notebook tabs load data on-demand just
		# like the main notebook tabs :-)
		self.__populate_notebook()
	#------------------------------------------------
	def on_select_all(self, event):
		for item_idx in range(self.DataGrid.GetNumberRows()):
			self.DataGrid.SetCellValue(item_idx,0,'1')
	#------------------------------------------------
	def on_mark_reviewed(self, event):
		# look for checkmark
		reviewed_req = []
		for row in range(self.DataGrid.GetNumberRows()):
			if self.DataGrid.GetCellValue(row,0) == '1':
				# look up associated request
				req=self.dict_req_unreviewed[row]
				# check relevant status
				relevant = self.DataGrid.GetCellValue(row,1)
				if relevant =='1':
					req['relevant'] = 'true'
				else:
					req['relevant'] = 'false'
					
				reviewed_req.append(req)
		
		if len(reviewed_req) == 0:
			gmGuiHelpers.gm_show_error(
				aMessage = _("Unable to comply with your request.\nYou didn't mark any result as reviewed."),
				aTitle = _('setting request status to reviewed')
			)
			return None
		
		for req in reviewed_req:
			req['reviewed'] = 'true'
			req['pk_reviewer'] = _whoami.get_staff_ID()
			
			if not req['abnormal']:
				req['abnormal'] =''
			status, error = req.save_payload()
			# repopulate
			if status:
				self.__populate_notebook()
				
			else:
				_log.Log(gmLog.lErr, 'setting request status to reviewed failed %s' % error)
				gmGuiHelpers.gm_show_error(
					aMessage = _('Cannot change request status to reviewed.'),
				aTitle = _('update request status')
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
		
#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':
	_log.Log (gmLog.lInfo, "starting lab journal")

	if _cfg is None:
		_log.Log(gmLog.lErr, "Cannot run without config file.")
		sys.exit("Cannot run without config file.")

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
#================================================================
# $Log: gmLabWidgets.py,v $
# Revision 1.1  2004-07-15 15:03:41  ncq
# - factored out from wxpython/gui/gmLabJournal.py
#
