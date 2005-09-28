#############################################################################
#
# gmSQLSimpleSearch - a widget for simple database search & selection interaction
# ---------------------------------------------------------------------------
#
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: gmPG, gmLoginInfo
# @change log:
#	06.10.2001 hherb first draft, untested
#
# @TODO: testing & writing the module test function
#	 a context menu (right click) for most common actions (like delete row)
############################################################################

"""
gmSQLSimpleSearch - a widget for simple database search & selection interaction
"""
try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

from Gnumed.wxpython import gmSQLListControl
from Gnumed.pycommon import gmI18N

ID_COMBO_SEARCHEXPR = wx.NewId()
ID_BUTTON_SEARCH = wx.NewId()
ID_CHECKBOX_CASEINSENSITIVE = wx.NewId()
ID_LISTCTRL = wx.NewId()

class SQLSimpleSearch(wx.Panel):
	"""
	gmSQLSimpleSearch - a widget for simple database
	search & selection interaction
	"""
	
	def __init__(self, parent, id,
		pos = wx.DefaultPosition, size = wx.DefaultSize,
		style = wx.TAB_TRAVERSAL, service = 'default' ):

		self.selected = None

		#the backend service to connect to
		self.SetService(service)

		wx.Panel.__init__(self, parent, id, pos, size, style)

		self.sizerTopVertical = wx.BoxSizer( wx.VERTICAL )

		self.sizerSearchExpr = wx.BoxSizer( wx.HORIZONTAL )

		self.comboSearchExpr = wxComboBox( self, ID_COMBO_SEARCHEXPR, "", wx.DefaultPosition, wx.Size(170,-1),
			[''] , wx.CB_DROPDOWN )
		self.sizerSearchExpr.Add( self.comboSearchExpr, 1, wx.ALIGN_CENTRE|wx.ALL, 2 )

		self.buttonSearch = wxButton( self, ID_BUTTON_SEARCH, _("&Search"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.sizerSearchExpr.Add( self.buttonSearch, 0, wx.ALIGN_CENTRE|wx.ALL, 2 )

		self.checkboxCaseInsensitive = wxCheckBox( self, ID_CHECKBOX_CASEINSENSITIVE, _("&Case insensitive"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.sizerSearchExpr.Add( self.checkboxCaseInsensitive, 0, wx.ALIGN_CENTRE|wx.ALL, 2 )

		self.sizerTopVertical.AddSizer( self.sizerSearchExpr, 0, wxGROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 2 )

		self.sizerSearchResults = wx.BoxSizer( wx.HORIZONTAL )

		self.listctrlSearchResults = gmSQLListControl.SQLListControl( self, ID_LISTCTRL, wxDefaultPosition, wxSize(160,120), wxLC_REPORT|wxSUNKEN_BORDER|wx.LC_VRULES|wx.LC_HRULES )
		self.sizerSearchResults.Add( self.listctrlSearchResults, 1, wxGROW|wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 2 )

		self.sizerTopVertical.AddSizer( self.sizerSearchResults, 1, wxGROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 2 )

		self.SetAutoLayout( True )
		self.SetSizer( self.sizerTopVertical )
		#if call_fit == True:
		#	sizerTopVertical.Fit( self )
		#	sizerTopVertical.SetSizeHints( self )

		EVT_LIST_KEY_DOWN(self, ID_LISTCTRL, self.OnSearchResultKeyDown)
		EVT_LIST_ITEM_RIGHT_CLICK(self, ID_LISTCTRL, self.OnSearchResultItemRightClicked)
		EVT_LIST_ITEM_ACTIVATED(self, ID_LISTCTRL, self.OnSearchResultItemActivated)
		EVT_LIST_ITEM_DESELECTED(self, ID_LISTCTRL, self.OnSearchResultItemDeselected)
		EVT_LIST_ITEM_SELECTED(self, ID_LISTCTRL, self.OnSearchResultItemSelected)
		EVT_CHECKBOX(self, ID_CHECKBOX_CASEINSENSITIVE, self.OnCaseInsensitiveCheckbox)
		EVT_BUTTON(self, ID_BUTTON_SEARCH, self.OnSearch)
		EVT_BUTTON(self, wx.ID_CANCEL, self.OnCancel)
		EVT_CHAR(self, self.OnChar)
		EVT_IDLE(self, self.OnIdle)


	def SetService(self, service):
		"determine the database service the query will run on"
		self.__service = service

	def TransferDataToWindow(self):
		print "TransferDataToWindow(self):"
		return True

	def TransferDataFromWindow(self):
		print "def TransferDataFromWindow(self):"
		return True


	def OnSearchResultKeyDown(self, event):
		print "def OnSearchResultKeyDown(self, event):"


	def OnSearchResultItemRightClicked(self, event):
		print "def OnSearchResultItemRightClicked(self, event):"


	def OnSearchResultItemActivated(self, event):
		#print "def OnSearchResultItemActivated(self, event):"
		self.selected = event.GetIndex()
		self.ProcessSelection(self.selected)
		#event.Skip()

	def OnSearchResultItemDeselected(self, event):
		#print "def OnSearchResultItemDeselected(self, event):"
		pass
		#event.Skip()

	def OnSearchResultItemSelected(self, event):
		#print "def OnSearchResultItemSelected(self, event):"
		self.selected = event.GetIndex()
		#event.Skip()



	def OnCaseInsensitiveCheckbox(self, event):
		#print "def OnCaseInsensitiveCheckbox(self, event):"
		pass

	def OnSearch(self, event):
		self.Search()
		event.Skip(True)


	def OnIdle(self, event):
		event.Skip(True)

	def OnChar(self, event):
		print "def OnChar(self, event):"
		event.Skip(True)

	def OnCancel(self, event):
		print "def OnCancel(self, event):"
		event.Skip(True)

	def Search(self):
		searchexpr = self.comboSearchExpr.GetValue()
		querystr = self.TransformQuery(searchexpr)
		self.listctrlSearchResults.SetQueryStr(querystr, self.__service)
		#print "gmSQLSimpleSearch.py: running query %s on service %s" % (querystr, self.__service)
		self.listctrlSearchResults.RunQuery()

	def TransformQuery(self, searchexpr):
		"this method should be overridden by derived classes if neccessary"
		print "this should never show up!"
		return searchexpr


	def GetSelection(self):
		return self.selected
		#self.listctrlSearchResults.GetSelection()

	def GetLabels(self):
		"returns the list control column labels"
		return self.listctrlSearchResults.GetLabels()


	def ProcessSelection(self, index):
		if index is None:
			return None
		data = self.listctrlSearchResults.GetItemText(index)
		return int(data)


	def GetData(self):
		# some subclasses override ProcessSelection, so specify this class's ProcessSelection	
		return SQLSimpleSearch.ProcessSelection(self, self.GetSelection())
