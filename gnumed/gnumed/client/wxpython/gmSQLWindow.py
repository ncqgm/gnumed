#!/usr/bin/python
#############################################################################
#
# gmGuiMain - The application framework and main window of the
#             all signing all dancing GNUMed reference client.
#             (WORK IN PROGRESS)
# ---------------------------------------------------------------------------
#
# provides a text entry field for the query string as well
# as a list control that displays query results. On top of the
# list control a read-only multiline text widgets displays
# feedback from the database backend other than the query
# results.
#
# Usage: pnl = gmSQLWindow(parent, id, ...)
# To access the result widget, call gmSQLWindow.GetResultListcontrol()
# it will return the a tuple containing the list control object
# and a list with all selected items
#
# You can hook into the event loop by providing a callback function
# for the  "item selected" event:
# gmSQLWindow.SetCallbackOnSelected(my_callback_function)
#
# my_callback_function should expect a list of tuples as result
# the tuples returned are all selected rows
#
# to get the attribute labels, call gmSQLWindow.GetLabels()
#
#
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: wxPython (>= version 2.3.1)
# @change log:
#	10.06.2001 hherb initial implementation, untested
#	01.11.2001 hherb comments added, modified for distributed servers
#                  make no mistake: this module is still completely useless!
#
# @TODO: all testing, most of the implementation
#
############################################################################

"generic SQL query dialog"

from wxPython.wx import *
import types, time
import gmPG, gmLabels, gmGuiBroker

import gettext
_=gettext.gettext


ID_COMBO_QUERY = wxNewId()
ID_BUTTON_RUNQUERY = wxNewId()
ID_BUTTON_CLEARQUERY = wxNewId()
ID_BUTTON_CLEARRESULTS = wxNewId()
ID_TEXTCTRL_QUERYRESULTS = wxNewId()
ID_LISTCTRLQUERYRESULT = wxNewId()

class SQLWindow(wxPanel):

	def __init__(self, parent, id,
		pos = wxPyDefaultPosition, size = wxPyDefaultSize,
		style = wxTAB_TRAVERSAL ):
		wxPanel.__init__(self, parent, id, pos, size, style)

		self.CallbackOnSelected = None
		self.lables = []
		self.broker = gmGuiBroker.GuiBroker()

		self.topsizer = wxBoxSizer( wxVERTICAL )

		self.staticQueryBox = wxStaticBox( self, -1, _("Query") )
		self.inputHsizer = wxStaticBoxSizer( self.staticQueryBox, wxHORIZONTAL )

		self.comboQueryInput = wxComboBox( self, ID_COMBO_QUERY, "", wxDefaultPosition, wxSize(140,-1), [], wxCB_DROPDOWN )
		self.inputHsizer.AddWindow( self.comboQueryInput, 1, wxALIGN_CENTRE|wxALL, 5 )

		self.buttonRunQuery = wxButton( self, ID_BUTTON_RUNQUERY, _("&Run query"), wxDefaultPosition, wxDefaultSize, 0 )
		self.inputHsizer.AddWindow( self.buttonRunQuery, 0, wxALIGN_CENTRE|wxALL, 5 )

		self.buttonClearQuery = wxButton( self, ID_BUTTON_CLEARQUERY, _("&Clear query"), wxDefaultPosition, wxDefaultSize, 0 )
		self.inputHsizer.AddWindow( self.buttonClearQuery, 0, wxALIGN_CENTRE|wxALL, 5 )

		self.buttonClearResults = wxButton( self, ID_BUTTON_CLEARRESULTS, _("Clear &results"), wxDefaultPosition, wxDefaultSize, 0 )
		self.inputHsizer.AddWindow( self.buttonClearResults, 0, wxALIGN_CENTRE|wxALL, 5 )

		self.topsizer.AddSizer( self.inputHsizer, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5 )

		self.staticResultsBox = wxStaticBox( self, -1, _("Results") )
		self.resultsVsizer = wxStaticBoxSizer( self.staticResultsBox, wxVERTICAL )

		self.textQueryResults = wxTextCtrl( self, ID_TEXTCTRL_QUERYRESULTS, "", wxDefaultPosition, wxSize(70,70), wxTE_MULTILINE|wxTE_READONLY )
		self.resultsVsizer.AddWindow( self.textQueryResults, 1, wxGROW|wxALIGN_CENTER_HORIZONTAL|wxALL, 5 )

		self.listQueryResults = wxListCtrl( self, ID_LISTCTRLQUERYRESULT, wxDefaultPosition, wxSize(160,120), wxLC_REPORT|wxSUNKEN_BORDER )
		self.resultsVsizer.AddWindow( self.listQueryResults, 3, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5 )

		self.topsizer.AddSizer( self.resultsVsizer, 1, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5 )

		set_sizer=true
		if set_sizer == true:
			self.SetAutoLayout( true )
			self.SetSizer( self.topsizer )
		call_fit=true
		if call_fit == true:
			self.topsizer.Fit( parent )
			self.topsizer.SetSizeHints( parent )

		# WDR: handler declarations for gmSQLWin
		EVT_LIST_ITEM_SELECTED(self, ID_LISTCTRLQUERYRESULT, self.OnResultSelected)
		EVT_COMBOBOX(self, ID_COMBO_QUERY, self.OnTextEntered)
		EVT_BUTTON(self, ID_BUTTON_CLEARRESULTS, self.OnClearResults)
		EVT_BUTTON(self, ID_BUTTON_CLEARQUERY, self.OnClearQuery)
		EVT_BUTTON(self, ID_BUTTON_RUNQUERY, self.OnRunQuery)




	def OnResultSelected(self, event):
		if self.CallbackOnSelected:
			self.CallbackOnSelected()
		else:
			pass

	def OnTextEntered(self, event):
		wxLogMessage("SQL Window: OnTextEntered")


	def OnClearResults(self, event):
		self.textQueryResults.Clear()
		self.listQueryResults().ClearAll()

	def OnClearQuery(self, event):
		self.comboQueryInput.SetValue('')

	def OnRunQuery(self, event):
		messagewidget  = self.textQueryResults
		resultwidget = self.listQueryResults
		querystr = self.comboQueryInput.GetValue()
		try:
			conn = gmPG.ConnectionPool().GetConnection('default')
		except:
			messagewidget.AppendText("Backend connection failed.")
			return

   		#time needed for database AND gui handling
        	t1f = time.time()
        	#time needed for database query
        	t1 = time.time()

		query = conn.query(querystr)
		queryresult = query.getresult()
		t2 = time.time()
		messagewidget.AppendText("Query [%s] returned %d tuples in %3.3f sec\n\n" \
					% (querystr, query.ntuples(), t2-t1))

		#set list control labels depending on the returned fields
		self.labels = query.listfields()
		gmLabels.LabelListControl(resultwidget, self.labels)

		rowcount=resultwidget.GetItemCount()
		for row in queryresult:
			ds = ''
			colcount = 0
			for attr in row:
				if colcount==0:
					resultwidget.InsertStringItem(rowcount,str(attr))
				else:
					resultwidget.SetStringItem(rowcount,colcount, str(attr))
                		colcount +=1
            		rowcount +=1

		#adjust column width accorcing to the query results
		for w in range(0, len(query.listfields())):
			resultwidget.SetColumnWidth(w, wxLIST_AUTOSIZE)
		# get the main window's status line "set" function:
		status = self.broker['main.statustext']
		t2f = time.time()
		status("%d records found; retrieved and displayed in %1.3f sec." % (query.ntuples(), t2f-t1f))



	def GetResultListctrl(self):
		return listQueryResults

	def SetCallbackOnSelected(self, callback):
		self.callbackOnSelected = callback

	def GetLabels():
		return self.labels


