#!/bin/env python
#This software is free software by the terms of the GPL v2 or later license

"""This module provides a (modal) dialog presenting a list
of choices. The user can either quickly make a selection by
the usual means (keyboard, mouse), cancel, or select "new"
The dialog needs to be fed with a list of dictionaries
The dialog returns:
index of this list or
-1 if cancelled or
-2 if "new" was selected
The list item can be accessed via GetSelection()"""


__version__ = "$Revision: 1.1 $"

__author__ = "Dr. Horst Herb <hherb@gnumed.net>"
__license__ = "GPL"
__copyright__ = __author__



from wxPython.wx import *

# text translation function for localization purposes
import gettext
_ = gettext.gettext


ID_LISTCTRL = wxNewId()
ID_NEW = wxNewId()

CANCELLED = -1
NEW_ITEM = -2

class QuickSelectionDlg(wxDialog):
	"""present choices to the user in the form of a list control
	in a modal dialog. User can choose to cancel or request a new
	item. You must call SetItemDict before you can use it"""

	def __init__(self, parent, id, title,
		pos = wxPyDefaultPosition, size = wxPyDefaultSize,
		style = wxDEFAULT_DIALOG_STYLE|wxRESIZE_BORDER ):
		wxDialog.__init__(self, parent, id, title, pos, size, style)

		self.itemdict = []
		self.selection = -1

		GenerateDialog( self, true )
		#won't work on Windoze otherwise:
		self.listctrl.SetFocus()

		EVT_LIST_ITEM_SELECTED(self, ID_LISTCTRL, self.OnItemCursor)
		EVT_LIST_ITEM_ACTIVATED(self, ID_LISTCTRL, self.OnItemSelected)
		EVT_BUTTON(self, ID_NEW, self.OnNew)
		EVT_BUTTON(self, wxID_OK, self.OnOk)
		EVT_BUTTON(self, wxID_CANCEL, self.OnCancel)


	def SetItemDict(self, itemdict, labels=None):
		"""Loads a list of dictionaries (itemdict) into the list
		control. Only dictionary entries as specified in the list
		"labels" will be wshown, in the order as stated by "labels".
		If labels is None, all dictionary entries will be dispalyed
		in the order of the dictionary (beyond control)"""

		self.itemdict = itemdict
		if labels==None:
			#caution: sequence of keys is quite unpredictable!
			self.labels=itemdict.keys()
		else:
			self.labels=labels
		self.listctrl.ClearAll()
		for i in range(len(self.labels)):
        		self.listctrl.InsertColumn(i, self.labels[i])
		rowcount=0
		for row in range(len(itemdict)):
			self.listctrl.InsertStringItem(rowcount,str(itemdict[rowcount][labels[0]]))
			colcount = 1
			for label in labels[1:]:
				self.listctrl.SetStringItem(rowcount,colcount, str(itemdict[rowcount][label]))
                		colcount +=1
            		rowcount +=1

		#adjust column width according to the query results
		for w in range(0, len(self.labels)):
			self.listctrl.SetColumnWidth(w, wxLIST_AUTOSIZE)


	def GetSelection(self):
		"""Call this function to access the selected list item
		after the dialog has been closed"""
		if self.selection > -1:
			return self.itemdict[self.selection]
		else:
			return None

	def OnItemCursor(self, event):
		self.selection = event.ItemIndex

	def OnItemSelected(self, event):
		self.selection = event.ItemIndex
		self.EndModal(event.ItemIndex)

	def OnOk(self, event):
		self.EndModal(self.selection)


	def OnCancel(self, event):
		self.selection = CANCELLED
		self.EndModal(CANCELLED)

	def OnNew(self, event):
		self.selection = NEW_ITEM
		self.EndModal(NEW_ITEM)



def GenerateDialog( parent, call_fit = true, set_sizer = true ):
    parent.szrTop = wxBoxSizer( wxVERTICAL )

    parent.listctrl = wxListCtrl( parent, ID_LISTCTRL, wxDefaultPosition, wxSize(160,120), wxLC_REPORT|wxSUNKEN_BORDER )
    parent.szrTop.AddWindow( parent.listctrl, 1, wxGROW|wxALIGN_CENTER_VERTICAL, 5 )

    parent.szrButtons = wxBoxSizer( wxHORIZONTAL )

    parent.btnOK = wxButton( parent, wxID_OK, _("&OK"), wxDefaultPosition, wxDefaultSize, 0 )
    parent.szrButtons.AddWindow( parent.btnOK, 1, wxALIGN_CENTRE, 5 )

    parent.btnNew = wxButton( parent, ID_NEW, _("&New"), wxDefaultPosition, wxDefaultSize, 0 )
    parent.szrButtons.AddWindow( parent.btnNew, 1, wxALIGN_CENTRE, 5 )

    parent.btnCancel = wxButton( parent, wxID_CANCEL, _("&Cancel"), wxDefaultPosition, wxDefaultSize, 0 )
    parent.szrButtons.AddWindow( parent.btnCancel, 1, wxALIGN_CENTRE, 5 )

    parent.szrTop.AddSizer( parent.szrButtons, 0, wxGROW|wxALIGN_CENTER_VERTICAL, 5 )

    if set_sizer == true:
        parent.SetAutoLayout( true )
        parent.SetSizer( parent.szrTop )
        if call_fit == true:
            parent.szrTop.Fit( parent )
            parent.szrTop.SetSizeHints( parent )

    return parent.szrTop


if __name__ == "__main__":

	example = [{"name":"Bloggs, Joe", "dob":"01/02/1903", "id":1},
	{"name":"Doe, Tom", "dob":"12/03/1933", "id":2},
	{"name":"Lary, Mary", "dob":"22/10/1965", "id":3}]

	ID_TEST = wxNewId()
	ID_EXIT = wxNewId()
	class testapp (wxApp):

		def OnInit (self):
			frame = wxFrame(None,-4, "Testing...", size=wxSize (600, 400),
					style=wxDEFAULT_FRAME_STYLE|
					wxNO_FULL_REPAINT_ON_RESIZE)
			filemenu= wxMenu()
			filemenu.Append(ID_TEST, "&Test","Testing this module")
			filemenu.AppendSeparator()
			filemenu.Append(ID_EXIT,"E&xit"," Terminate the program")
			# Creating the menubar.
			menuBar = wxMenuBar()
			menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBa
			frame.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
			txt = wxStaticText( frame, -1, _("Select 'test' from the 'File' menu"), wxDefaultPosition, wxDefaultSize, 0 )
			EVT_MENU(frame, ID_TEST, self.OnTest)
			EVT_MENU(frame, ID_EXIT, self.OnCloseWindow)
			frame.Show(1)
			return 1


		def OnTest(self,e):
			d=QuickSelectionDlg(None, -1, "test")
			d.SetItemDict(example, ["name", "id"])
			retval = d.ShowModal() # Shows it
			if retval > CANCELLED:
				print d.GetSelection()
			elif retval == NEW_ITEM:
				print "user requests a new item"
			else:
				print "user has cancelled"
			d.Destroy() # finally destroy it when finished.

		def OnCloseWindow (self, e):
			self.ExitMainLoop ()


	app = testapp (0)
	app.MainLoop ()
