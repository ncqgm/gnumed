"""
"""
#============================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/Attic/gmShowLab.py,v $
__version__ = "$Revision: 1.8 $"
__author__ = "Sebastian Hilbert <Sebastian.Hilbert@gmx.net>"

# system
import os.path, sys, os, re, string, random

from Gnumed.pycommon import gmLog
_log = gmLog.gmDefLog

if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)
	from Gnumed.pycommon import gmI18N
else:
	from Gnumed.pycommon import gmGuiBroker

_log.Log(gmLog.lData, __version__)

from Gnumed.pycommon import gmPG, gmCfg, gmExceptions, gmWhoAmI
from Gnumed.business import gmPatient, gmClinicalRecord
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.pycommon.gmPyCompat import *

# 3rd party
from wxPython.wx import *
from wxPython.grid import * 

_cfg = gmCfg.gmDefCfgFile
_whoami = gmWhoAmI.cWhoAmI()

[   wxID_PNL_main,
	wxID_LAB_GRID
] = map(lambda _init_ctrls: wxNewId(), range(2))
#================================================================
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


    def GetBestSize(self, grid, attr, dc, row, col):
        text = grid.GetCellValue(row, col)
        dc.SetFont(attr.GetFont())
        w, h = dc.GetTextExtent(text)
        return wxSize(w, h)


    def Clone(self):
        return MyCustomRenderer()


class cLabDataGrid(wxGrid):
	"""This wxGrid derivative displays a grid view of stored lab data.
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
		
		wxGrid.__init__(
			self,
			parent,
			id,
			pos = wxDefaultPosition,
			size = wxDefaultSize,
			style= wxWANTS_CHARS
			)
		
		self.curr_pat = gmPatient.gmCurrentPatient()

		#EVT_GRID_CELL_LEFT_DCLICK(self, self.OnLeftDClick)
		
		# create new grid
		self.DataGrid = self.CreateGrid(0, 0, wxGrid.wxGridSelectCells )
		self.SetDefaultCellAlignment(wxALIGN_RIGHT,wxALIGN_CENTRE)
		#renderer = apply(wxGridCellStringRenderer, ())
		renderer = apply(MyCustomRenderer, ())
		self.SetDefaultRenderer(renderer)
		
		# There is a bug in wxGTK for this method...
		self.AutoSizeColumns(True)
		self.AutoSizeRows(True)
		# attribute objects let you keep a set of formatting values
		# in one spot, and reuse them if needed
		font = self.GetFont()
		#font.SetWeight(wxBOLD)
		attr = wxGridCellAttr()
		attr.SetFont(font)
		#attr.SetBackgroundColour(wxLIGHT_GREY)
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
		if self.curr_pat['ID'] is None:
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
		# FIXME: check if patient changed at all
		emr = self.curr_pat.get_clinical_record()
		if emr is None:
			# FIXME: error message
			return None
		# FIXME: there might be too many results to handle in memory
		lab = emr.get_lab_results()

		if lab is None or len(lab)==0:
			name = self.curr_pat['demographic record'].get_names()
			gmGuiHelpers.gm_show_error(
				aMessage = _('Cannot find any lab data for patient\n[%s %s].') % (name['first'], name['last']),
				aTitle = _('loading lab record list')
				)
			return None
			
		else:
			dates, test_names = self.__compile_stats(lab)
			# sort tests before pushing onto the grid 
			"""	
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
			#sort_mode = gmPatient.getsort_mode() # yet to be written
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
				#test_count = {}
				#test_types = self.__get_test_types(lab_ids)
				#for id in test_types:
				#	if test_types[id] in test_count.keys():
				#		test_count[test_types[id]] = test_count[test_types[id]]+1
				#	else:
				#		test_count[test_types[id]] = 1
				# try to be smart, sort tests by usage
				#sorted = self.sort_by_value(test_count)
				#sorted.reverse()
				pass
			else :
				"""
				set up notebook tab
				"""
				pass
			
			if sort_mode == 2:
				"""
				start with smart sorting tab
				"""
				pass
			
			if sort_mode == 3:
				"""
				get first user defined tab
				"""
				pass
			
			
			# clear grid
			self.ClearGrid()
			# now add columns
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
			
			#push data onto the grid
			cells = []
			for item in lab:
				data = str(item['val_num'])
				unit = str(item['val_unit'])
				# get  x,y position for data item
				x,y = self.__GetDataCell(item, xorder=dates, yorder=test_names)
				tuple = []
				tuple.append(str(x)+','+str(y))
				if tuple in cells:
					celldata = self.GetCellValue(int(x), int(y))
					data = celldata+'\n'+ data + unit
					self.SetCellValue(int(x), int(y), data)
				
				# you can set cell attributes for the whole row (or column)
				#self.SetRowAttr(int(y), attr)
				#self.SetColAttr(int(x), attr)
				#self.SetCellRenderer(int(x), int(y), renderer)
				else:
					self.SetCellValue(int(x), int(y), data+unit)
					"""same test might have been issued multiple times (same day)
					 we keep reference of used cells 
					 if a cell needs to be filled but already contains data we get the data and join the values
					 this is crap but I don't know a better solution"""
					cells.append(tuple)

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
	def __GetDataCell(self, item=None, xorder=None, yorder=None):
		x = xorder.index(item['val_when'].date)
		y= yorder.index(item['unified_name'])
		return (y,x)
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
	#--------------------------------------------------------
	#def __show_description(self, evt):
	#    print "showing description"
	#--------------------------------------------------------
	#def __handle_obj_context(self, data):
	#    print "handling object context menu"
	#--------------------------------------------------------
	
#== classes for standalone use ==================================
if __name__ == '__main__':

	from Gnumed.pycommon import gmLoginInfo
	from Gnumed.business import gmXdtObjects, gmXdtMappings, gmDemographicRecord

	wxID_btn_quit = wxNewId()

	class cStandalonePanel(wxPanel):

		def __init__(self, parent, id):
			# get patient from file
			if self.__get_pat_data() is None:
				raise gmExceptions.ConstructorError, "Cannot load patient data."

			# set up database connectivity
			auth_data = gmLoginInfo.LoginInfo(
				user = _cfg.get('database', 'user'),
				passwd = _cfg.get('database', 'password'),
				host = _cfg.get('database', 'host'),
				port = _cfg.get('database', 'port'),
				database = _cfg.get('database', 'database')
			)
			backend = gmPG.ConnectionPool(login = auth_data)

			# mangle date of birth into ISO8601 (yyyymmdd) for Postgres
			cooked_search_terms = {
				#'dob': '%s%s%s' % (self.__xdt_pat['dob year'], self.__xdt_pat['dob month'], self.__xdt_pat['dob day']),
				'lastnames': self.__xdt_pat['last name'],
				'firstnames': self.__xdt_pat['first name'],
				'gender': self.__xdt_pat['gender']
			}
			# find matching patient IDs
			searcher = gmPatient.cPatientSearcher_SQL()
			patient_ids = searcher.get_patient_ids(search_dict = cooked_search_terms)
			if patient_ids is None or len(patient_ids)== 0:
				gmGuiHelpers.gm_show_error(
					aMessage = _('This patient does not exist in the document database.\n"%s %s"') % (self.__xdt_pat['first name'], self.__xdt_pat['last name']),
					aTitle = _('searching patient')
				)
				_log.Log(gmLog.lPanic, self.__xdt_pat['all'])
				raise gmExceptions.ConstructorError, "Patient from XDT file does not exist in database."

			# ambigous ?
			if len(patient_ids) != 1:
				gmGuiHelpers.gm_show_error(
					aMessage = _('Data in xDT file matches more than one patient in database !'),
					aTitle = _('searching patient')
				)
				_log.Log(gmLog.lPanic, self.__xdt_pat['all'])
				raise gmExceptions.ConstructorError, "Problem getting patient ID from database. Aborting."

			try:
				gm_pat = gmPatient.gmCurrentPatient(aPKey = patient_ids[0])
			except:
				# this is an emergency
				gmGuiHelpers.gm_show_error(
					aMessage = _('Cannot load patient from database !\nAborting.'),
					aTitle = _('searching patient')
				)
				_log.Log(gmLog.lPanic, 'Cannot access patient [%s] in database.' % patient_ids[0])
				_log.Log(gmLog.lPanic, self.__xdt_pat['all'])
				raise

			# make main panel
			wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize)
			self.SetTitle(_("Stored lab data"))

			# make patient panel
			gender = gmDemographicRecord.map_gender_gm2long[gmXdtMappings.map_gender_xdt2gm[self.__xdt_pat['gender']]]
			self.pat_panel = wxStaticText(
				id = -1,
				parent = self,
				label = "%s %s (%s), %s.%s.%s" % (self.__xdt_pat['first name'], self.__xdt_pat['last name'], gender, self.__xdt_pat['dob day'], self.__xdt_pat['dob month'], self.__xdt_pat['dob year']),
				style = wxALIGN_CENTER
			)
			self.pat_panel.SetFont(wxFont(25, wxSWISS, wxNORMAL, wxNORMAL, 0, ""))

			# make lab record grid 
			self.grid = cLabDataGrid(self, -1)
			self.grid.update()

			# buttons
			btn_quit = wxButton(
				parent = self,
				id = wxID_btn_quit,
				label = _('Quit')
			)
			EVT_BUTTON (btn_quit, wxID_btn_quit, self.__on_quit)
			szr_buttons = wxBoxSizer(wxHORIZONTAL)
			szr_buttons.Add(btn_quit, 0, wxALIGN_CENTER_VERTICAL, 1)

			# layout
			szr_main = wxBoxSizer(wxVERTICAL)
			#szr_grid = wxGridSizer(0,wxEXPAND,0)
			szr_main.Add(self.pat_panel, 0, wxEXPAND, 1)
			szr_main.Add(self.grid, 1,wxEXPAND, 1)
			#szr_main.Add(szr_grid, 1, wxEXPAND, 9)
			#szr_grid.Add(self.grid, 1, wxEXPAND, 9)
			szr_main.Add(szr_buttons, 0, wxEXPAND, 1)

			self.SetAutoLayout(1)
			self.SetSizer(szr_main)
			#szr_main.Fit(self)
			self.Layout()
		#--------------------------------------------------------
		def __get_pat_data(self):
			"""Get data of patient for which to retrieve documents.

			"""
			# FIXME: error checking
			pat_file = os.path.abspath(os.path.expanduser(_cfg.get("viewer", "patient file")))
			# FIXME: actually handle pat_format, too
			pat_format = _cfg.get("viewer", "patient file format")

			# get patient data from BDT file
			try:
				self.__xdt_pat = gmXdtObjects.xdtPatient(anXdtFile = pat_file)
			except:
				_log.LogException('Cannot read patient from xDT file [%s].' % pat_file, sys.exc_info())
				gmGuiHelpers.gm_show_error(
					aMessage = _('Cannot load patient from xDT file\n[%s].') % pat_file,
					aTitle = _('loading patient from xDT file')
				)
				return None

			return 1
		#--------------------------------------------------------
		def __on_quit(self, evt):
			app = wxGetApp()
			app.ExitMainLoop()
		#--------------------------------------------------------
		def __show_error(self, aMessage = None, aTitle = ''):
			# sanity checks
			tmp = aMessage
			if aMessage is None:
				tmp = _('programmer forgot to specify error message')

			tmp = tmp + _("\n\nPlease consult the error log for further information !")

			dlg = wxMessageDialog(
				NULL,
				tmp,
				aTitle,
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return 1
#== classes for plugin use ======================================
else:

	class cPluginGridPanel(wxPanel):
		def __init__(self, parent, id):
			# set up widgets
			wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize)

			# make document tree
			self.grid = cLabDataGrid(self, -1)

			# just one vertical sizer
			sizer = wxBoxSizer(wxVERTICAL)
			sizer.Add(self.grid, 1,wxEXPAND, 1)
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

	class gmShowLab(gmPlugin.wxNotebookPlugin):
		tab_name = _("path lab")

		def name (self):
			return gmShowLab.tab_name

		def GetWidget (self, parent):
			self.panel = cPluginGridPanel(parent, -1)
			return self.panel

		def MenuInfo (self):
			return ('tools', _('Show &archived lab data'))

		def ReceiveFocus(self):
			if self.panel.grid.update() is None:
				_log.Log(gmLog.lErr, "cannot update grid with lab data")
				return None
			# FIXME: register interest in patient_changed signal, too
			self.panel.Layout()
			self.panel.Refresh()
			return 1

		def can_receive_focus(self):
			# need patient
			if not self._verify_patient_avail():
				return None
			return 1

		def DoToolbar (self, tb, widget):
			#tool1 = tb.AddTool(
			#   wxID_PNL_BTN_load_pages,
			#   images_Archive_plugin.getcontentsBitmap(),
			#   shortHelpString=_("load pages"),
			#   isToggle=false
			#)
			#EVT_TOOL (tb, wxID_PNL_BTN_load_pages, widget.on_load_pages)

			#tool1 = tb.AddTool(
			#   wxID_PNL_BTN_save_data,
			#   images_Archive_plugin.getsaveBitmap(),
			#   shortHelpString=_("save document"),
			#   isToggle=false
			#)
			#EVT_TOOL (tb, wxID_PNL_BTN_save_data, widget.on_save_data)
			
			#tool1 = tb.AddTool(
			#   wxID_PNL_BTN_del_page,
			#   images_Archive_plugin.getcontentsBitmap(),
			#   shortHelpString=_("delete page"),
			#   isToggle=false
			#)
			#EVT_TOOL (tb, wxID_PNL_BTN_del_page, widget.on_del_page)
			
			#tool1 = tb.AddTool(
			#    wxID_TB_BTN_show_page,
			#    images_Archive_plugin.getreportsBitmap(),
			#    shortHelpString=_("show document"),
			#    isToggle=false
			#)
			#EVT_TOOL (tb, wxID_TB_BTN_show_page, cDocTree.OnActivate)
	
			#tool1 = tb.AddTool(
			#   wxID_PNL_BTN_select_files,
			#   images_Archive_plugin1.getfoldersearchBitmap(),
			#   shortHelpString=_("select files"),
			#   isToggle=false
			#)
			#EVT_TOOL (tb, wxID_PNL_BTN_select_files, widget.on_select_files)
		
			tb.AddControl(wxStaticBitmap(
				tb,
				-1,
				images_Archive_plugin.getvertical_separator_thinBitmap(),
				wxDefaultPosition,
				wxDefaultSize
			))
#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':
	_log.Log (gmLog.lInfo, "starting lab viewer")

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
	_log.Log (gmLog.lInfo, "closing lab viewer")
else:
	# we are being imported
	pass
#================================================================
# $Log: gmShowLab.py,v $
# Revision 1.8  2004-05-21 07:28:55  shilbert
# - multiline cells now actually work
# - grid now fully expands as per request by ncq
#
# Revision 1.7  2004/05/18 20:43:17  ncq
# - check get_clinical_record() return status
#
# Revision 1.6  2004/04/20 00:15:36  ncq
# - slight deuglification
#
# Revision 1.5  2004/04/16 22:28:07  shilbert
# - code cleanups , make use of 'def __compile_stats():'
# - framework for user defined lab profiles
#
# Revision 1.4  2004/04/16 00:27:13  ncq
# - PyCompat
#
# Revision 1.3  2004/04/15 20:14:14  shilbert
# - supports multiline text, uses custom renderer
# - changes in font, data alignment
#
# Revision 1.2  2004/04/15 09:52:22  shilbert
# - display unified_name instead of lab_name as requested by ncq
#
# Revision 1.1  2004/04/15 09:45:31  ncq
# - first functional version, still ugly
#
