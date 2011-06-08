#!/usr/bin/python
#############################################################################
#
# gmPersonNotebook : convenience widget that displays a notebook widget
#                     Notebook pages contain a person search & selection
#                     widget as well as pages displaying information about
#                     the selected person
# ---------------------------------------------------------------------------
#
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL v2 or later (details at http://www.gnu.org)
# @dependencies:
# @change log:
#	18.12.2001 hherb first draft, untested
#
# @TODO: Almost everything
############################################################################

from wxPython.wx import *
import gmSelectPerson, gmPersonDetailsDlg, gmCachedPerson, gmSQLSimpleSearch, gmGuiBroker

ID_NOTEBOOK=wxNewId()

class PersonNotebook(wxPanel):
	def __init__(self, parent, id):
		wxPanel.__init__(self, parent, id)

		self.__guibroker = gmGuiBroker.GuiBroker()

		self.__sizer = wxBoxSizer( wxVERTICAL )
		#resize the panel depending on it's widgets
		self.SetAutoLayout( true )
		self.SetSizer( self.__sizer )

		self.__nb = wxNotebook(self, ID_NOTEBOOK, wxDefaultPosition, wxSize(400,200), 0)
		EVT_NOTEBOOK_PAGE_CHANGED(self, ID_NOTEBOOK, self.OnPageChanged)
		#allow self-sizing according to page sizes
		self.__nbs = wxNotebookSizer(self.__nb)
		self.__sizer.AddSizer(self.__nbs, 1, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 0 )

		#Search Patient dialog
		self.SearchPersonDlg = gmSelectPerson.DlgSelectPerson(self.__nb, -1)
		self.__nb.AddPage(self.SearchPersonDlg, _("Search"))
		#Person details dialog
		self.PersonDetailsDlg = gmPersonDetailsDlg.PersonDetailsDlg(self.__nb, -1)
		self.__nb.AddPage(self.PersonDetailsDlg, _("Details"))

		self.RegisterEvents()

		self.__person = gmCachedPerson.CachedPerson()

		#tell the parent window about our size
		self.__sizer.Fit( parent )
		self.__sizer.SetSizeHints( parent )

		self.__person.notify_me("PersonNotebook", self.OnDataUpdate)
	
	def OnDataUpdate( self, updater , id):
		self.SearchPersonDlg.Search()	

	def RegisterEvents(self):
		EVT_BUTTON(self, gmSelectPerson.ID_BUTTON_SELECT, self.OnPersonSelected)
		EVT_LIST_ITEM_ACTIVATED(self, gmSQLSimpleSearch.ID_LISTCTRL, self.OnPersonSelected)
		EVT_BUTTON(self, gmSelectPerson.ID_BUTTON_EDIT, self.OnPersonEdit)

	def OnPersonEdit( self, evt):
		self.__nb.SetSelection(1)

	def OnPersonSelected(self, evt):
		personId = self.SearchPersonDlg.GetSelectedPersonId()
		print "Person selected!", personId
		self.__person.setId(personId)
		p = self.__person.dictresult()
		print "info retrieved ", p
		if p is not None:
			self.__guibroker["main.SetWindowTitle"]("GNUMed: %s %s" % (p["firstnames"], p["lastnames"]) )

		

		self.PersonDetailsDlg.OnDataUpdate(self, p['id'])	



	def OnPageChanged(self, evt):
		print "On Notebook page changed"


if __name__ == "__main__":
	_ = lambda x:x
	app = wxPyWidgetTester(size = (400, 500))
	app.SetWidget(PersonNotebook, -1)
	app.MainLoop()
