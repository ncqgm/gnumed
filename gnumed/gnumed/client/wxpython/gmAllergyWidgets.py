"""GnuMed allergy related widgets.

"""
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmAllergyWidgets.py,v $
__version__ = "$Revision: 1.1 $"
__author__  = "R.Terry <rterry@gnumed.net>, H.Herb <hherb@gnumed.net>, K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL (details at http://www.gnu.org)'

import sys, time

from wxPython.wx import *

from Gnumed.pycommon import gmLog, gmDispatcher, gmSignals, gmPG, gmExceptions
from Gnumed.wxpython import gmPlugin_Patient, gmEditArea, gmDateTimeInput, gmTerryGuiParts
from Gnumed.business import gmPatient

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

ID_ALLERGYLIST = wxNewId()
ID_ALLERGIES = wxNewId ()
ID_ALL_MENU = wxNewId ()

#======================================================================
class gmAllergyEditArea(gmEditArea.gmEditArea):

	def __init__(self, parent, id):
		try:
			gmEditArea.gmEditArea.__init__(self, parent, id, aType = 'allergy')
		except gmExceptions.ConstructorError:
			_log.LogException('cannot instantiate allergy edit area', sys.exc_info(), verbose=1)
			raise
	#----------------------------------------------------
	def _define_fields(self, parent):
		# line 1
		self.fld_date_noted = gmDateTimeInput.gmDateInput(
			parent = parent,
			id = -1,
			style = wxSIMPLE_BORDER
		)
		self._add_field(
			line = 1,
			pos = 1,
			widget = self.fld_date_noted,
			weight = 1
		)
		# line 2
		self.fld_substance = gmEditArea.cEditAreaField(parent)
		self._add_field(
			line = 2,
			pos = 1,
			widget = self.fld_substance,
			weight = 1
		)
		# line 3
		self.fld_generic = gmEditArea.cEditAreaField(parent)
		self._add_field(
			line = 3,
			pos = 1,
			widget = self.fld_generic,
			weight = 6
		)
		self.fld_generic_specific = wxCheckBox(
			parent,
			-1,
			_("generics specific"),
			style = wxNO_BORDER
		)
		self._add_field(
			line = 3,
			pos = 2,
			widget = self.fld_generic_specific,
			weight = 0
		)
		# line 4
		self.fld_drug_class = gmEditArea.cEditAreaField(parent)
		self._add_field(
			line = 4,
			pos = 1,
			widget = self.fld_drug_class,
			weight = 0
		)
		# line 5
		# FIXME: add allergene, atc_code ?
		self.fld_reaction = gmEditArea.cEditAreaField(parent)
		self._add_field(
			line = 5,
			pos = 1,
			widget = self.fld_reaction,
			weight = 1
		)
		# line 6
		self.fld_progress_note = gmEditArea.cEditAreaField(parent)
		self._add_field(
			line = 6,
			pos = 1,
			widget = self.fld_progress_note,
			weight = 1
		)
		# line 7
		self.fld_is_allergy = wxRadioButton(parent, -1, _("Allergy"))
		self._add_field(
			line = 7,
			pos = 1,
			widget = self.fld_is_allergy,
			weight = 2
		)
		self.fld_is_sensitivity = wxRadioButton(parent, -1, _("Sensitivity"))
		self._add_field(
			line = 7,
			pos = 2,
			widget = self.fld_is_sensitivity,
			weight = 2
		)
		self.fld_is_definite_allergy = wxCheckBox(
			parent,
			-1,
			_("Definite"),
			style = wxNO_BORDER
		)
		self._add_field(
			line = 7,
			pos = 3,
			widget = self.fld_is_definite_allergy,
			weight = 2
		)
		self._add_field(
			line = 7,
			pos = 4,
			widget = self._make_standard_buttons(parent),
			weight = 1
		)
	#----------------------------------------------------
	def _define_prompts(self):
		self._add_prompt(line = 1, label = _("Date Noted"))
		self._add_prompt(line = 2, label = _("Brand/Substance"))
		self._add_prompt(line = 3, label = _("Generic"))
		self._add_prompt(line = 4, label = _("Drug Class"))
		self._add_prompt(line = 5, label = _("Reaction"))
		self._add_prompt(line = 6, label = _("Progress Note"))
		self._add_prompt(line = 7, label = '')
	#----------------------------------------------------
	def _save_new_entry(self):
		allergy = {}
		allergy['date noted'] = self.fld_date_noted.GetValue()
		allergy['substance'] = self.fld_substance.GetValue()
		allergy['generic'] = self.fld_generic.GetValue()
		allergy['is generic specific'] = self.fld_generic_specific.GetValue()
		allergy['drug class'] = self.fld_drug_class.GetValue()
		allergy['reaction'] = self.fld_reaction.GetValue()
		allergy['progress note'] = self.fld_progress_note.GetValue()
		allergy['is allergy'] = self.fld_is_allergy.GetValue()
		allergy['is sensitivity'] = self.fld_is_sensitivity.GetValue()
		allergy['is definite'] = self.fld_is_definite_allergy.GetValue()
		# FIXME: validation
		epr = self.patient.get_clinical_record()
		if epr is None:
			# FIXME: badder error message
			wxBell()
			_gb['main.statustext'](_('Cannot save allergy.'))
			return None
		status, data = epr.add_allergy(allergy)
		if status is None:
			wxBell()
			_gb['main.statustext'](_('Cannot save allergy.'))
			return None
		_gb['main.statustext'](_('Allergy saved.'))
		self.data = data
		return 1
	#----------------------------------------------------
	def set_data(self, allergy = None):
		"""Set edit area fields with allergy object data.

		- set defaults if no object is passed in, this will
		  result in a new object being created upon saving
		"""
		self.data = None
		# defaults
		if allergy is None:
			self.fld_date_noted.SetValue((time.strftime('%Y-%m-%d', time.localtime())))
			self.fld_substance.SetValue('')
			self.fld_generic.SetValue('')
			self.fld_generic_specific.SetValue(0)
			self.fld_drug_class.SetValue('')
			self.fld_reaction.SetValue('')
			self.fld_progress_note.SetValue('')
			self.fld_is_allergy.SetValue(1)
			self.fld_is_sensitivity.SetValue(0)
			self.fld_is_definite_allergy.SetValue(1)
			return 1
		# or data
		self.data = allergy
		print allergy.get_fields()
		try: self.fld_date_noted.SetValue(allergy['date noted'])
		except KeyError: pass
		try: self.fld_substance.SetValue(allergy['substance'])
		except KeyError: pass

		try: self.fld_progress_note.SetValue(allergy['progress note'])
		except KeyError: pass

		# example for checkboxes
#		try:
#			if allergy['is booster']:
#				self.fld_is_booster.SetValue(1)
#			else:
#				self.fld_is_booster.SetValue(0)
#		except KeyError: pass

		return 1

#======================================================================
class cAllergyPanel(wxPanel):
	"""Allergy details panel.

		This panel will hold all the allergy details and
		allow entry of those details via the editing area
	"""

	def __init__(self, parent,id):
		wxPanel.__init__(self, parent, id,wxDefaultPosition,wxDefaultSize,wxRAISED_BORDER)
		# main heading
		self.allergypanelheading = gmTerryGuiParts.cHeadingCaption(
			self,
			-1,
			_("ALLERGIES")
		)
		# edit area specific for allergies
		self.editarea = gmAllergyEditArea(self, -1)
		# divider headings below edit area
		self.drug_subheading = gmTerryGuiParts.cDividerCaption(
			self,
			-1,
			_("Allergy and Sensitivity - Summary")
		)
		self.sizer_divider_drug_generic = wxBoxSizer(wxHORIZONTAL)
		self.sizer_divider_drug_generic.Add(self.drug_subheading, 1, wxEXPAND)
		#--------------------------------------------------------------------------------------
		#add the list to contain the drugs person is allergic to
		#
		# c++ Default Constructor:
		# wxListCtrl(wxWindow* parent, wxWindowID id, const wxPoint& pos = wxDefaultPosition,
		# const wxSize& size = wxDefaultSize, long style = wxLC_ICON,
		# const wxValidator& validator = wxDefaultValidator, const wxString& name = "listCtrl")
		#--------------------------------------------------------------------------------------
		self.list_allergy = wxListCtrl(
			self,
			ID_ALLERGYLIST,
			wxPyDefaultPosition,
			wxPyDefaultSize,
			wxLC_REPORT | wxLC_NO_HEADER | wxSUNKEN_BORDER
		)
		self.list_allergy.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, false, ''))
		# add some dummy data to the allergy list
		self._constructListColumns()
		#-------------------------------------------------------------
		#loop through the scriptdata array and add to the list control
		#note the different syntax for the first coloum of each row
		#i.e. here > self.list_allergy.InsertStringItem(x, data[0])!!
		#-------------------------------------------------------------
		#add a richtext control or a wxTextCtrl multiline to display the class text information
		#e.g. would contain say information re the penicillins
		self.classtext_subheading = gmTerryGuiParts.cDividerCaption(
			self,
			-1,
			"Class notes for celecoxib"
		)
		self.classtxt = wxTextCtrl(self,-1,
			"A member of a new class of nonsteroidal anti-inflammatory agents (COX-2 selective NSAIDs) which have a mechanism of action that inhibits prostaglandin synthesis primarily by inhibition of cyclooxygenase 2 (COX-2). At therapeutic doses these have no effect on prostanoids synthesised by activation of COX-1 thereby not interfering with normal COX-1 related physiological processes in tissues, particularly the stomach, intestine and platelets.",
			size = (200, 100),
			style = wxTE_MULTILINE
		)
		self.classtxt.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,false,''))
		# add elements to main background sizer
		self.mainsizer = wxBoxSizer(wxVERTICAL)
		self.mainsizer.Add(self.allergypanelheading,0,wxEXPAND)
		self.mainsizer.Add(self.editarea,6,wxEXPAND)
		self.mainsizer.Add(self.sizer_divider_drug_generic,0,wxEXPAND)
		self.mainsizer.Add(self.list_allergy,5,wxEXPAND)
		self.mainsizer.Add(self.classtext_subheading,0,wxEXPAND)
		self.mainsizer.Add(self.classtxt,4,wxEXPAND)
		self.SetSizer(self.mainsizer)
		self.mainsizer.Fit
		self.SetAutoLayout(true)
		self.Show(true)

		self.__pat = gmPatient.gmCurrentPatient()
		self.__register_interests()
	#-----------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(self.UpdateAllergies, gmSignals.allergy_updated())

#		EVT_LIST_ITEM_ACTIVATED( self.list_allergy, self.list_allergy.GetId(), self._allergySelected)
	#-----------------------------------------------
	def populate(self):
		self.__reset_ui_content()
	#-----------------------------------------------
	def __reset_ui_content(self):
		self.editarea.set_data()
		# FIXME: populate lists etc.
	#-----------------------------------------------
	def _updateUI(self):
		self.UpdateAllergies()

	def _constructListColumns(self):
		self.list_allergy.InsertColumn(0, _("Type"))
		self.list_allergy.InsertColumn(1, _("Status"))
		self.list_allergy.InsertColumn(2, _("Class"))
		self.list_allergy.InsertColumn(3, _("Substance"))
		self.list_allergy.InsertColumn(4, _("Generic"))
		self.list_allergy.InsertColumn(5, _("Reaction"))
		
	
#	def _allergySelected(self, event):
#		ix = event.GetIndex()
#		allergy_map = self.get_allergies().get_allergy_items()
#		for id, values in allergy_map.items():
#			if ix == 0:
#				self.editarea.setInputFieldValues( values, id)
#			ix -= 1
			

		

#	def _update_list_row( self, i,id,  val_map):
#		if val_map['is allergy'] == 1:
#			atype = _('allergy')
#		else:
#			atype = _('sensitivity')
#		if val_map['definite']:
#			surety = 'definite'
#		else:
#			surety = 'uncertain'

#		self.list_allergy.SetItemData( i, id  )
#		self.list_allergy.InsertStringItem( i, atype )
		
#		list = [  surety, val_map['allergy class'], val_map['substance'], val_map['generics'], val_map['reaction'] ]
#		for j in xrange(0, len( list) ):
#			self.list_allergy.SetStringItem( i, j+1, list[j] )
		

	def UpdateAllergies(self, **kwargs):
#		# remember wxCallAfter
#		try:
			#epr = self.__pat.get_clinical_record()
			#allergies = epr['allergies']
#			allergy_map = self.get_allergies()
			# { 941: map_values, 2: map_values }
			
#		except:
#			_log.LogException( "problem getting allergy list", sys.exc_info(), 4)
#			return None

#		_log.Data("Allergies " + str(allergy_map))

#		i = 0
#		self.list_allergy.DeleteAllItems()
#		self._constructListColumns()
		
#		for id, val_map in allergy_map.items():
#			self._update_list_row(i, id, val_map)
#			i = i + 1
			
#		for column in range(0,3):
#			self.list_allergy.SetColumnWidth(column, wxLIST_AUTOSIZE)

		return 1
#======================================================================
# main
#----------------------------------------------------------------------
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (600, 600))
	app.SetWidget(cAllergyPanel, -1)
	app.MainLoop()
#======================================================================
# $Log: gmAllergyWidgets.py,v $
# Revision 1.1  2004-07-17 21:16:38  ncq
# - cleanup/refactor allergy widgets:
#   - Horst space plugin added
#   - Richard space plugin separated out
#   - plugin independant GUI code aggregated
#   - allergies edit area factor out from generic edit area file
#
#
