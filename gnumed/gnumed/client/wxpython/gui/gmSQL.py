# a simple wrapper for the SQL window
#############################################################################
#
# gmSQLWindow: convenience widget for quick "free style" SQL queries
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
#   10.06.2001 hherb initial implementation, untested
#   01.11.2001 hherb comments added, modified for distributed servers
#                  make no mistake: this module is still completely useless!
#
# @TODO: all testing, most of the implementation
#
############################################################################

"""Generic SQL query dialog
Usage: pnl = gmSQLWindow(parent, id, ...)
gmSQLWindow.GetResultListcontrol()returns a tuple with the list control object
and a list with all selected items

You can hook into the event loop by providing a callback function
for the  "item selected" event:
gmSQLWindow.SetCallbackOnSelected(my_callback_function)

my_callback_function should expect a list of tuples as result
the tuples returned are all selected rows

to get the attribute labels, call gmSQLWindow.GetLabels()"""

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/Attic/gmSQL.py,v $

__version__ = "$Revision: 1.15 $"

__author__ = "Dr. Horst Herb <hherb@gnumed.net>"
__license__ = "GPL"
__copyright__ = __author__

from wxPython.wx import *

import sys

from Gnumed.pycommon import gmPG, gmGuiBroker, gmLog, gmI18N
from Gnumed.wxpython import gmPlugin, gmSQLListControl, images_gnuMedGP_Toolbar

ID_COMBO_QUERY = wxNewId()
ID_BUTTON_RUNQUERY = wxNewId()
ID_BUTTON_CLEARQUERY = wxNewId()
ID_BUTTON_CLEARRESULTS = wxNewId()
ID_TEXTCTRL_QUERYRESULTS = wxNewId()
ID_LISTCTRLQUERYRESULT = wxNewId()
ID_CHOICE_SERVICE = wxNewId()

class RedirectToTextctrl:
    "helper class to allow redirection of stdout/stderr to a text control widget"
    def __init__(self, widget):
        self.widget=widget
    def write(self, s):
        self.widget.AppendText(s)


class SQLWindow(wxPanel):

    def __init__(self, parent, id,
        pos = wxDefaultPosition, size = wxDefaultSize,
        style = wxTAB_TRAVERSAL ):
        wxPanel.__init__(self, parent, id, pos, size, style)

        self.CallbackOnSelected = None
        self.labels = []
        self.broker = gmGuiBroker.GuiBroker()

        self.topsizer = wxBoxSizer( wxVERTICAL )
        self.topHsizer = wxBoxSizer( wxHORIZONTAL )

        self.staticServiceBox = wxStaticBox( self, -1, _("Service") )
        self.serviceHsizer = wxStaticBoxSizer( self.staticServiceBox, wxHORIZONTAL )
        self.topHsizer.AddSizer( self.serviceHsizer, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 0 )

        self.choiceService = wxChoice( self, ID_CHOICE_SERVICE, wxDefaultPosition, wxSize(80,-1), choices = ['config'])
        self.serviceHsizer.Add( self.choiceService, 1, wxALIGN_CENTRE|wxALL, 5 )

        self.staticQueryBox = wxStaticBox( self, -1, _("Query") )
        self.inputHsizer = wxStaticBoxSizer( self.staticQueryBox, wxHORIZONTAL )

        self.comboQueryInput = wxComboBox( self, ID_COMBO_QUERY, "", wxDefaultPosition, wxSize(200,-1), [], wxCB_DROPDOWN )
        self.inputHsizer.Add( self.comboQueryInput, 1, wxALIGN_CENTRE|wxALL, 5 )

        self.buttonRunQuery = wxButton( self, ID_BUTTON_RUNQUERY, _("&Run query"), wxDefaultPosition, wxDefaultSize, 0 )
        self.inputHsizer.Add( self.buttonRunQuery, 0, wxALIGN_CENTRE|wxALL, 5 )

        self.buttonClearQuery = wxButton( self, ID_BUTTON_CLEARQUERY, _("&Clear query"), wxDefaultPosition, wxDefaultSize, 0 )
        self.inputHsizer.Add( self.buttonClearQuery, 0, wxALIGN_CENTRE|wxALL, 5 )
        self.topHsizer.AddSizer( self.inputHsizer, 1, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 0 )

        self.staticFeedbackBox = wxStaticBox( self, -1, _("Tables in database  /  Feedback") )
        self.feedbackHsizer = wxStaticBoxSizer( self.staticFeedbackBox, wxHORIZONTAL )
        self.textQueryResults = wxTextCtrl( self, ID_TEXTCTRL_QUERYRESULTS, "", wxDefaultPosition, wxSize(-1,30), wxTE_MULTILINE|wxTE_READONLY )
        self.listTables = gmSQLListControl.SQLListControl( self, -1, wxDefaultPosition, wxSize(-1,80), wxLC_REPORT|wxSUNKEN_BORDER, hideid=False)
        self.stdout = RedirectToTextctrl(self.textQueryResults)
        self.stderr = self.stdout

        self.listTables.SetRedirectedOutput(self.stderr)
        self.feedbackHsizer.Add( self.listTables, 1, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5 )
        self.feedbackHsizer.Add( self.textQueryResults, 1, wxGROW|wxALIGN_CENTER_HORIZONTAL|wxALL, 5 )

        self.staticResultsBox = wxStaticBox( self, -1, _("Results") )
        self.resultsVsizer = wxStaticBoxSizer( self.staticResultsBox, wxVERTICAL )
        self.listQueryResults = gmSQLListControl.SQLListControl( self, ID_LISTCTRLQUERYRESULT, wxDefaultPosition, wxSize(-1,90), wxLC_REPORT|wxSUNKEN_BORDER )
        self.listQueryResults.SetRedirectedOutput(self.stderr, self.stdout)
        self.listQueryResults.SetStatusFunc(self.broker['main.statustext'])
        self.resultsVsizer.Add( self.listQueryResults, 1, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 5 )

        self.topsizer.AddSizer( self.topHsizer, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 0 )
        self.topsizer.AddSizer( self.feedbackHsizer, 1, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 0 )
        self.topsizer.AddSizer( self.resultsVsizer, 2, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 0 )

        self.ListServices()
        self.ListTables()

        #resize the panel depending on it's widgets
        self.SetAutoLayout( True )
        self.SetSizer( self.topsizer )
        #tell the parent window about our size
        self.topsizer.Fit( parent )
        self.topsizer.SetSizeHints( parent )

        # WDR: handler declarations for gmSQLWin
        EVT_LIST_ITEM_SELECTED(self, ID_LISTCTRLQUERYRESULT, self.OnResultSelected)
        EVT_COMBOBOX(self, ID_COMBO_QUERY, self.OnTextEntered)
        EVT_BUTTON(self, ID_BUTTON_CLEARQUERY, self.OnClearQuery)
        EVT_BUTTON(self, ID_BUTTON_RUNQUERY, self.OnRunQuery)
        EVT_CHOICE(self, ID_CHOICE_SERVICE, self.OnChangeService)




    def ListTables(self):
        "list all tables provided by the service chosen by the user"
        service = self.choiceService.GetStringSelection()
        #list all tables except the system tables
        self.listTables.SetQueryStr("select * from pg_tables where tablename not like 'pg%'", service)
        self.listTables.RunQuery()



    def ListServices(self):
        "list all available services the backend is connected to"

        services = gmPG.ConnectionPool().GetAvailableServices()
        for service in services:
            self.choiceService.Append(service)


    def RunQuery(self):
        service = self.choiceService.GetStringSelection()
        querystr = self.comboQueryInput.GetValue()
        self.listQueryResults.SetQueryStr(querystr, service)
        self.listQueryResults.RunQuery()

    def OnChangeService(self, event):
        self.ListTables()


    def OnResultSelected(self, event):
        if self.CallbackOnSelected:
            self.CallbackOnSelected()
        else:
            pass

    def OnTextEntered(self, event):
        self.RunQuery()


    def OnClearQuery(self, event):
        self.comboQueryInput.SetValue('')

    def OnRunQuery(self, event):
        self.RunQuery()

    def GetResultListctrl(self):
        return listQueryResults

    def SetCallbackOnSelected(self, callback):
        self.callbackOnSelected = callback

    def GetLabels():
        return self.labels



class gmSQL (gmPlugin.cNotebookPluginOld):
    """
    Plugin to encapsulate the cryptowidget
    """
    tab_name = _('SQL Search')

    def name (self):
        return gmSQL.tab_name


    def MenuInfo (self):
        return ('view', _('&SQL Search'))

    def GetWidget (self, parent):
        return SQLWindow (parent, -1)
