"""
"""
#============================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/gmLabJournal.py,v $
__version__ = "$Revision: 1.29 $"
__author__ = "Sebastian Hilbert <Sebastian.Hilbert@gmx.net>"

# system
import os.path, sys, os, re
# FIXME: debugging
import time

from Gnumed.pycommon import gmLog
_log = gmLog.gmDefLog

if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)
	_ = lambda x:x
	from Gnumed.pycommon import gmI18N
else:
	from Gnumed.pycommon import gmGuiBroker

_log.Log(gmLog.lData, __version__)

from Gnumed.pycommon import gmPG, gmCfg, gmExceptions, gmWhoAmI, gmMatchProvider
from Gnumed.business import gmPatient, gmClinicalRecord, gmPathLab
from Gnumed.wxpython import gmGuiHelpers, gmPhraseWheel
from Gnumed.pycommon.gmPyCompat import *

# 3rd party
from wxPython.wx import *
from wxPython.lib.mixins.listctrl import wxColumnSorterMixin, wxListCtrlAutoWidthMixin
from wxPython.grid import *

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
class MyCustomRenderer(wxPyGridCellRenderer):
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
class gmLabIDListCtrl(wxListCtrl, wxListCtrlAutoWidthMixin):
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
		self.lbox_pending = gmLabIDListCtrl(
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
		self.lbox_errors = gmLabIDListCtrl(
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
		renderer = apply(MyCustomRenderer, ())
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
		self.DataGrid.SetColLabelValue(3, _('result from'))
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
			self.lbox_pending.SetStringItem(index = item_idx, col=0, label=request['clin_when'].date)
			# request lab
			lab = self.__get_labname(request['fk_test_org'])
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
				episode_id = emr.get_active_episode()['id_episode']
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
		
#== classes for plugin use ==================================
if __name__ != '__main__':
	class cPluginPanel(wxPanel):
		def __init__(self, parent, id):
			# set up widgets
			wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize)

			# make lab notebook
			self.nb = cLabJournalNB(self, -1)
			
			# just one vertical sizer
			sizer = wxBoxSizer(wxVERTICAL)
			szr_nb = wxNotebookSizer( self.nb )
			
			sizer.Add(szr_nb, 1, wxEXPAND, 0)
			self.SetAutoLayout(1)
			self.SetSizer(sizer)
			sizer.Fit(self)
			self.Layout()
		#--------------------------------------------------------
		def __del__(self):
			# FIXME: return service handle
			#self.DB.disconnect()
			pass

	#------------------------------------------------------------
	from Gnumed.wxpython import gmPlugin, images_Archive_plugin, images_Archive_plugin1

	class gmLabJournal(gmPlugin.wxNotebookPlugin):
		tab_name = _("lab journal")

		def name (self):
			return gmLabJournal.tab_name

		def GetWidget (self, parent):
			self._widget = cPluginPanel(parent, -1)
			return self._widget

		def MenuInfo (self):
			return ('tools', _('Show &lab journal'))

		def populate_with_data(self):
			# no use reloading if invisible
			if self.gb['main.notebook.raised_plugin'] != self.__class__.__name__:
				return 1
			if self._widget.nb.update() is None:
				_log.Log(gmLog.lErr, "cannot update lab journal with data")
				return None
			#self._widget.tree.SelectItem(self._widget.tree.root)
#			self.DoStatusText()
			return 1

		def can_receive_focus(self):
			# need patient
			if not self._verify_patient_avail():
				return None
			return 1

		def populate_toolbar (self, tb, widget):
			
			tb.AddControl(wxStaticBitmap(
				tb,
				-1,
				images_Archive_plugin.getvertical_separator_thinBitmap(),
				wxDefaultPosition,
				wxDefaultSize
			))
			
		def DoStatusText (self):
			# FIXME: people want an optional beep and an optional red backgound here
			#set_statustext = gb['main.statustext']
				txt = _('how are you doing today ?') 
				if not self._set_status_txt(txt):
					return None
				return 1
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
else:
	# we are being imported
	pass
#================================================================
# $Log: gmLabJournal.py,v $
# Revision 1.29  2004-06-20 16:50:51  ncq
# - carefully fool epydoc
#
# Revision 1.28  2004/06/20 13:48:02  shilbert
# - GUI polished
#
# Revision 1.27  2004/06/20 06:49:21  ihaywood
# changes required due to Epydoc's OCD
#
# Revision 1.26  2004/06/13 22:31:49  ncq
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
# Revision 1.25  2004/06/05 11:31:54  shilbert
# - GUI cleanup as per ncq's request
# - request reviewed via single-click, double-click, <SPACE> implemented
#
# Revision 1.24  2004/06/02 00:02:32  ncq
# - cleanup, indentation fixes
#
# Revision 1.23  2004/05/30 21:19:01  shilbert
# - completely redone review panel
#
# Revision 1.22  2004/05/29 20:20:30  shilbert
# - review stuff finally works
#
# Revision 1.21  2004/05/29 10:22:10  ncq
# - looking good, just some cleanup/comments as usual
#
# Revision 1.20  2004/05/28 21:11:56  shilbert
# - basically keep up with API changes
#
# Revision 1.19  2004/05/28 07:12:11  shilbert
# - finally real artwork
# - switched to new import regimen for artwork
#
# Revision 1.18  2004/05/27 08:47:35  shilbert
# - listctrl item insertion bugfix
#
# Revision 1.17  2004/05/26 14:05:21  ncq
# - cleanup
#
# Revision 1.16  2004/05/26 13:31:00  shilbert
# - cleanup, gui enhancements
#
# Revision 1.15  2004/05/26 11:07:04  shilbert
# - gui layout changes
#
# Revision 1.14  2004/05/25 13:26:49  ncq
# - cleanup
#
# Revision 1.13  2004/05/25 08:15:20  shilbert
# - make use of gmPathLab for db querries
# - introduce limit for user visible list items
#
# Revision 1.12  2004/05/22 23:29:09  shilbert
# - gui updates (import error context , ctrl labels )
#
# Revision 1.11  2004/05/18 20:43:17  ncq
# - check get_clinical_record() return status
#
# Revision 1.10  2004/05/18 19:38:54  shilbert
# - gui enhancements (wxExpand)
#
# Revision 1.9  2004/05/08 17:43:55  ncq
# - cleanup here and there
#
# Revision 1.8  2004/05/06 23:32:45  shilbert
# - now features a tab with unreviewed lab results
#
# Revision 1.7  2004/05/04 09:26:55  shilbert
# - handle more errors
#
# Revision 1.6  2004/05/04 08:42:04  shilbert
# - first working version, needs testing
#
# Revision 1.5  2004/05/04 07:19:34  shilbert
# - kind of works, still a bug in create_request()
#
# Revision 1.4  2004/05/01 10:29:46  shilbert
# - custom event handlig code removed, pending lab ids input almost completed
#
# Revision 1.3  2004/04/29 21:05:19  shilbert
# - some more work on auto update of id field
#
# Revision 1.2  2004/04/28 16:12:02  ncq
# - cleanups, as usual
#
# Revision 1.1  2004/04/28 07:20:00  shilbert
# - initial release after name change, lacks features
#
