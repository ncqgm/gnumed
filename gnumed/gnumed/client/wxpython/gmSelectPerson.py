#!/usr/bin/python
#############################################################################
#
# gmSelectPerson : convenience widget that allows to search for people
#                   and pick a selection from a list box displaying the
#                   search results
# ---------------------------------------------------------------------------
#
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: gmSQLSimpleSearch
# @change log:
#	25.11.2001 hherb first draft, untested
#
# @TODO: Almost everything
############################################################################

from wxPython.wx import *
from gmSQLSimpleSearch import SQLSimpleSearch
import gettext
_ = gettext.gettext

ID_BUTTON_SELECT = wxNewId()
ID_BUTTON_ADD = wxNewId()
ID_BUTTON_NEW = wxNewId()
ID_BUTTON_MERGE = wxNewId()
ID_BUTTON_EDIT = wxNewId()



class DlgSelectPerson(SQLSimpleSearch):
	"The central dialog interface to all person related queries"

	def __init__(self, parent, id,
		pos = wxPyDefaultPosition, size = wxPyDefaultSize,
		style = wxTAB_TRAVERSAL, service = 'demographica' ):

		SQLSimpleSearch.__init__(self, parent, id, pos, size, style, service)
		#add a bottom row sizer to hold a few buttons
		self.__SelectedPersonId=None
		self.sizerButtons = wxBoxSizer( wxHORIZONTAL )
		#add a "select patient" button
		self.buttonSelect = wxButton( self, ID_BUTTON_SELECT, _("&Select"), wxDefaultPosition, wxDefaultSize, 0 )
		self.sizerButtons.AddWindow( self.buttonSelect, 0, wxALIGN_CENTRE|wxALL, 2 )
		#edit this patient
		self.buttonEdit = wxButton( self, ID_BUTTON_EDIT, _("&Edit"), wxDefaultPosition, wxDefaultSize, 0 )
		self.sizerButtons.AddWindow( self.buttonEdit, 0, wxALIGN_CENTRE|wxALL, 2 )
		#add a new patient
		self.buttonNew = wxButton( self, ID_BUTTON_NEW, _("&New"), wxDefaultPosition, wxDefaultSize, 0 )
		self.sizerButtons.AddWindow( self.buttonNew, 0, wxALIGN_CENTRE|wxALL, 2 )
		#add patient to this family / address button
		self.buttonAdd = wxButton( self, ID_BUTTON_ADD, _("&Add"), wxDefaultPosition, wxDefaultSize, 0 )
		self.sizerButtons.AddWindow( self.buttonAdd, 0, wxALIGN_CENTRE|wxALL, 2 )
		#merge two or more atient entries into one
		self.buttonMerge = wxButton( self, ID_BUTTON_MERGE, _("&Merge"), wxDefaultPosition, wxDefaultSize, 0 )
		self.sizerButtons.AddWindow( self.buttonMerge, 0, wxALIGN_CENTRE|wxALL, 2 )

		self.sizerTopVertical.AddSizer( self.sizerButtons, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 2 )


	def TransformQuery(self, searchexpr):
		"'virtual' function of the base class, adjusted to the needs of this dialog"
		selectclause = "select * from v_basic_person"
		orderclause = "order by lastnames, firstnames"
		if self.checkboxCaseInsensitive.GetValue():
			#perform (slower) case insensitive search
			whereclause = "where (lastnames ilike '%s')" % (searchexpr + '%')
		else:
			whereclause = "where (lastnames like '%s')" % (searchexpr +'%')

            	query = "%s %s %s;" % (selectclause, whereclause, orderclause)
		#<DEBUG>
		#print "gmSelectPerson transformed query to: ", query
		#</DEBUG>
		return query


	def ProcessSelection(self, index):
		if index is None:
			return None
		item = self.listctrlSearchResults.GetItem(index,0)
		self.__SelectedPersonId = int(item.GetText())
		#return self.SelectedPersonId
		#<DEBUG>
		#item = self.listctrlSearchResults.GetItem(index,2)
		#name = item.GetText()
		#item = self.listctrlSearchResults.GetItem(index,3)
		#name = name + ' ' + item.GetText()
		#print "The person selected was %s (id=%d)" % (name, personID)
		#</DEBUG>

	def GetSelectedPersonId(self):
		return self.__SelectedPersonId

if __name__ == "__main__":
	app = wxPyWidgetTester(size = (400, 500))
	app.SetWidget(DlgSelectPerson, -1)
	app.MainLoop()

