#!/usr/bin/python
############################################################################
#
# gmSelectPerson : convenience widget that allows to search for people
#                   and pick a selection from a list box displaying the
#                   search results
# --------------------------------------------------------------------------
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
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/Attic/gmSelectPerson.py,v $
__version__ = "$Revision: 1.22 $"

import string

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

from Gnumed.pycommon import gmDispatcher, gmSignals, gmLog
from Gnumed.wxpython.gmSQLSimpleSearch import SQLSimpleSearch
_log = gmLog.gmDefLog


ID_BUTTON_SELECT = wx.NewId()
ID_BUTTON_ADD = wx.NewId()
ID_BUTTON_NEW = wx.NewId()
ID_BUTTON_MERGE = wx.NewId()
ID_BUTTON_EDIT = wx.NewId()

#===========================================================================
class DlgSelectPerson(SQLSimpleSearch):
	"""The central dialog interface to all person related queries.
	It allows to select a patient via fractions of surname or first names and surname,
	to create a new person record, to delete and to modify records"""

	def __init__(self, parent, id=-1,
		pos = wx.DefaultPosition, size = wx.DefaultSize,
		style = wx.TAB_TRAVERSAL, service = 'demographica' ):

		SQLSimpleSearch.__init__(self, parent, id, pos, size, style, service)
		#gmDispatcher.connect(self.dummy, gmSignals.patient_selected())

		#add a bottom row sizer to hold a few buttons
		self.__selectedPersonId=None

		self.checkboxCaseInsensitive.SetValue(True)
		self.sizerButtons = wx.BoxSizer( wx.HORIZONTAL )
		#add a "select patient" button
		self.buttonSelect = wxButton( self, ID_BUTTON_SELECT, _("&Select"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.sizerButtons.Add( self.buttonSelect, 0, wx.ALIGN_CENTRE|wx.ALL, 2 )
		#edit this patient
		self.buttonEdit = wxButton( self, ID_BUTTON_EDIT, _("&Edit"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.sizerButtons.Add( self.buttonEdit, 0, wx.ALIGN_CENTRE|wx.ALL, 2 )
		#add a new patient
		self.buttonNew = wxButton( self, ID_BUTTON_NEW, _("&New"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.sizerButtons.Add( self.buttonNew, 0, wx.ALIGN_CENTRE|wx.ALL, 2 )
		#add patient to this family / address button
		self.buttonAdd = wxButton( self, ID_BUTTON_ADD, _("&Add"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.sizerButtons.Add( self.buttonAdd, 0, wx.ALIGN_CENTRE|wx.ALL, 2 )
		#merge two or more atient entries into one
		self.buttonMerge = wxButton( self, ID_BUTTON_MERGE, _("&Merge"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.sizerButtons.Add( self.buttonMerge, 0, wx.ALIGN_CENTRE|wx.ALL, 2 )

		self.sizerTopVertical.AddSizer( self.sizerButtons, 0, wxGROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 2 )

		self.__connect_commands()

	
	def __connect_commands(self):
		EVT_BUTTON( self.buttonNew, self.buttonNew.GetId(), self.__newButtonPressed)
		EVT_BUTTON( self.buttonAdd, self.buttonAdd.GetId(), self.__addButtonPressed)

	
	def __newButtonPressed(self, event):
		self._newPatient()

	def __addButtonPressed(self, event):
		self._addPatient()

	def __getDemographicsWidget(self):
		import gmGuiBroker
		broker = gmGuiBroker.GuiBroker()

		for x in broker['main.notebook.plugins']:
			if str(x.__class__).find('gmDemographics') <> -1:
				return x
		
		raise Error("Unable to find gmDemographics")	
		
	def _newPatient(self):
		x = self.__getDemographicsWidget()
		x.Raise()
		x.newPatient()
		return

	def _addPatient(self):
		#pass
		id = self.GetData()
		#print id
		import gmPerson
		patient = gmPerson.gmPerson(id)
		newId = patient.link_new_relative()
		#newPatient = gmPerson.gmPerson(newId)
		#new_demographics = newPatient.get_identity()
		#old_demographics = patient.get_identity()
		#new_demographics.copyAddresses(old_demographics)
		#new_demographics.setActiveName( "?", old_demographics.get_names()['last'])
		if newId == None:
			print "GOT no new patient"
			return
		# FIXME: are we sure of the ramifications here ?
		gmPerson.gmCurrentPatient(newId)
		x = self.__getDemographicsWidget()
		x.Raise()

		




	def TransformQuery(self, searchexpr):
		"""Creates a SQL query from the text string entered by the user into the
		combo box.
		'virtual' function of the base class, adjusted to the needs of this dialog"""
		selectclause = "select * from v_basic_person"
		orderclause = "order by lastnames, firstnames"
		searchclause = "like"
		if self.checkboxCaseInsensitive.GetValue():
			searchclause = "ilike"
		names = string.split(searchexpr, ' ')
		if len(names) > 1:
			whereclause = "where (lastnames %s '%s%%' and firstnames %s '%s%%')" % \
				(searchclause, names[1], searchclause, names[0])
		else:
			whereclause = "where (lastnames %s '%s%%')" % (searchclause, names[0])

            	query = "%s %s %s ;" % (selectclause, whereclause, orderclause)
		return query


	def ProcessSelection(self, index):
		"""This function is called when a patient has been activated in the list control
		via double click or select & CR"""
		if index is None:
			return None
		kwargs = {}
		item = self.listctrlSearchResults.GetItem(index,0)
		self._selectedPersonId = int(item.GetText())
		kwargs['ID'] = self._selectedPersonId
		data = self.GetLabels()
		for i in range(len(data)):
			item = self.listctrlSearchResults.GetItem(index,i)
			kwargs[data[i]] = item.GetText()
		_log.Log(gmLog.lData, "kwargs for PATIENT: %s" % kwargs)
		kwargs['signal']= gmSignals.patient_selected()
		kwargs['sender'] = 'patient.selector'
		gmDispatcher.send(gmSignals.patient_selected(), kwds=kwargs)
		return self._selectedPersonId


	def GetSelectedPersonId(self):
		"""Theoretically no need for this function - whoever is interested in the
		selected patient, should register interest in gmSignals.patient_selected()
		with gmDispatcher"""
		return self._selectedPersonId

	def dummy(self, **kwargs):
		kwds = kwargs['kwds']
		print "Notice from dummy: selected #%(ID)d" % (kwds)


if __name__ == "__main__":

	#define a callback function that shall be called whenever a patient is selected
	def callback(**kwargs):
		kwds = kwargs['kwds']
		print "selected #%(ID)d" % (kwds)

	#tell the dispatcher about this callback function and the event we are interested in
	gmDispatcher.connect(callback, gmSignals.patient_selected())

	_ = lambda x:x
	app = wxPyWidgetTester(size = (600, 300))
	app.SetWidget(DlgSelectPerson, -1)
	import gmPG
	db = gmPG.ConnectionPool()
	app.MainLoop()

