#======================================================================
# GnuMed immunisation/vaccination panel
# -------------------------------------
#
# this panel holds the immunisation details
#
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
#======================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/patient/gmGP_Immunisation.py,v $
# $Id: gmGP_Immunisation.py,v 1.32 2004-06-13 22:31:50 ncq Exp $
__version__ = "$Revision: 1.32 $"
__author__ = "R.Terry, S.J.Tan, K.Hilbert"

import sys

from Gnumed.wxpython.gmGuiElement_HeadingCaptionPanel import HeadingCaptionPanel
from Gnumed.wxpython.gmGuiElement_DividerCaptionPanel import DividerCaptionPanel
from Gnumed.wxpython.gmGuiElement_AlertCaptionPanel import AlertCaptionPanel

# panel class holding editing prompts and text boxes
from Gnumed.wxpython import gmEditArea, gmPlugin
from Gnumed.business import gmPatient
from Gnumed.pycommon import gmLog, gmDispatcher, gmSignals

_log = gmLog.gmDefLog
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)
_log.Log(gmLog.lData, __version__)

from wxPython.wx import *
import mx.DateTime as mxDT

ID_VaccinatedIndicationsList = wxNewId()
ID_VaccinationsPerRegimeList = wxNewId()
ID_MissingShots = wxNewId()

#======================================================================
# FIXME: vaccination business object,
# move to business/gmVaccination.py
class cVacc:
	pass
#======================================================================
class ImmunisationPanel(wxPanel):

	def __init__(self, parent,id):
		wxPanel.__init__(self, parent, id, wxDefaultPosition,wxDefaultSize,wxRAISED_BORDER)

		self.patient = gmPatient.gmCurrentPatient()

		#-----------------------------------------------
		# top part
		#-----------------------------------------------
		pnl_UpperCaption = HeadingCaptionPanel (self, -1, _("  IMMUNISATIONS  "))
		self.editarea = gmEditArea.gmVaccinationEditArea(self, -1)

		#-----------------------------------------------
		# middle part
		#-----------------------------------------------
		# divider headings below editing area
		indications_heading = DividerCaptionPanel(self, -1, _("Indications"))
		vaccinations_heading = DividerCaptionPanel(self, -1, _("Vaccinations"))
		szr_MiddleCap = wxBoxSizer(wxHORIZONTAL)
		szr_MiddleCap.Add(indications_heading, 1, wxEXPAND)
		szr_MiddleCap.Add(vaccinations_heading, 1, wxEXPAND)

		# left list: indications for which vaccinations have been given
		self.LBOX_vaccinated_indications = wxListBox(
			parent = self,
			id = ID_VaccinatedIndicationsList,
			choices = [],
			style = wxLB_HSCROLL | wxLB_NEEDED_SB | wxSUNKEN_BORDER
		)
		self.LBOX_vaccinated_indications.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, false, ''))

		# right list: when an indication has been selected on the left
		# display the corresponding vaccinations on the right
		self.LBOX_given_shots = wxListBox(
			parent = self,
			id = ID_VaccinationsPerRegimeList,
			choices = [],
			style = wxLB_HSCROLL | wxLB_NEEDED_SB | wxSUNKEN_BORDER
		)
		self.LBOX_given_shots.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, false, ''))

		szr_MiddleLists = wxBoxSizer(wxHORIZONTAL)
		szr_MiddleLists.Add(self.LBOX_vaccinated_indications, 4,wxEXPAND)
		szr_MiddleLists.Add(self.LBOX_given_shots, 6, wxEXPAND)

		#---------------------------------------------
		# bottom part
		#---------------------------------------------
		pnl_MiddleCaption3 = DividerCaptionPanel(self, -1, _("Missing Immunisations"))
		self.LBOX_missing_shots = wxListBox(
			parent = self,
			id = ID_MissingShots,
			size=(200, 100),
			choices= [],
			style = wxLB_HSCROLL | wxLB_NEEDED_SB | wxSUNKEN_BORDER
		)
		self.LBOX_missing_shots.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,false,''))
		# alert caption
		pnl_BottomCaption = AlertCaptionPanel(self, -1, _("  Alerts  "))

		#---------------------------------------------
		#add all elements to the main background sizer
		#---------------------------------------------
		self.mainsizer = wxBoxSizer(wxVERTICAL)
		self.mainsizer.Add(pnl_UpperCaption, 0, wxEXPAND)
		self.mainsizer.Add(self.editarea, 6, wxEXPAND)
		self.mainsizer.Add(szr_MiddleCap, 0, wxEXPAND)
		self.mainsizer.Add(szr_MiddleLists, 4, wxEXPAND)
		self.mainsizer.Add(pnl_MiddleCaption3, 0, wxEXPAND)
		self.mainsizer.Add(self.LBOX_missing_shots, 4, wxEXPAND)
		self.mainsizer.Add(pnl_BottomCaption, 0, wxEXPAND)

		self.SetSizer(self.mainsizer)
		self.mainsizer.Fit (self)
		self.SetAutoLayout(true)

		self.__register_interests()
	#----------------------------------------------------
	def __register_interests(self):
		# events
		EVT_SIZE(self, self.OnSize)
		EVT_LISTBOX(self, ID_VaccinatedIndicationsList, self.on_vaccinated_indication_selected)
		EVT_LISTBOX_DCLICK(self, ID_VaccinationsPerRegimeList, self.on_given_shot_selected)
		EVT_LISTBOX_DCLICK(self, ID_MissingShots, self.on_missing_shot_selected)
#		EVT_RIGHT_UP(self.lb1, self.EvtRightButton)
		# client internal signals
		gmDispatcher.connect(signal=gmSignals.patient_selected(), receiver=self._on_patient_selected)
		# behaves just like patient_selected, really
		gmDispatcher.connect(signal=gmSignals.vaccinations_updated(), receiver=self._on_vaccinations_updated)
	#----------------------------------------------------
	# event handlers
	#----------------------------------------------------
	def OnSize (self, event):
		w, h = event.GetSize()
		self.mainsizer.SetDimension (0, 0, w, h)
	#----------------------------------------------------
	def on_given_shot_selected(self, event):
		"""
			Retrieve vaccination item object for a selected vaccinated indication
			and display in GUI
		"""
		id_vacc = event.GetClientData()
		epr = self.patient.get_clinical_record()
		if epr is None:
			# FIXME: error message
			return None
		self.editarea.set_data(epr.get_vaccinations(ID = id_vacc))
	#----------------------------------------------------
	def on_missing_shot_selected(self, event):
		print "now editing missing shot:", event.GetSelection(), event.GetString(), event.IsSelection(), event.GetClientData()
		id_vacc = event.GetClientData()
#		epr = self.patient.get_clinical_record()
	#----------------------------------------------------
	def on_vaccinated_indication_selected(self, event):
		"""Update right hand middle list to show vaccinations given for selected indication."""
		ind_list = event.GetEventObject()
		selected_item = ind_list.GetSelection()
		ind = ind_list.GetClientData(selected_item)
		# clear list
		self.LBOX_given_shots.Set([])
		epr = self.patient.get_clinical_record()
		if epr is None:
			# FIXME: error message
			return None
		shots = epr.get_vaccinations(indication_list = [ind])
		# FIXME: use Set() for entire array (but problem with client_data)
		for shot in shots:
			label = '%s: %s' % (shot['date'].Format('%m/%Y'), shot['vaccine'])
			data = shot['id']
			self.LBOX_given_shots.Append(label, data)
	#----------------------------------------------------
	def __reset_ui_content(self):
		# clear edit area
		self.editarea.set_data()
		# clear lists
		self.LBOX_vaccinated_indications.Clear()
		self.LBOX_given_shots.Clear()
		self.LBOX_missing_shots.Clear()

		# populate vaccinated-indications list
		epr = self.patient.get_clinical_record()
		if epr is None:
			# FIXME: error message
			return None
		status, indications = epr.get_vaccinated_indications()
		# FIXME: would be faster to use Set() but can't
		# use Set(labels, client_data), and have to know
		# line position in SetClientData :-(
		for indication in indications:
			self.LBOX_vaccinated_indications.Append(indication[1], indication[0])
#		self.LBOX_vaccinated_indications.Set(lines)
#		self.LBOX_vaccinated_indications.SetClientData(data)

		# populate missing-shots list
		missing_shots = epr.get_missing_vaccinations()
		if missing_shots is None:
			label = _('ERROR: cannot retrieve due/overdue vaccinations')
			self.LBOX_missing_shots.Append(label, None)
		else:
			# due
			due_template = _('%.0d weeks left: shot %s for %s in %s, due %s (%s)')
			overdue_template = _('overdue %.0dyrs %.0dwks: shot %s for %s in %s (%s)')
			for shot in missing_shots['due']:
				if shot['overdue']:
					years, days_left = divmod(shot['amount_overdue'].days, 364.25)
					weeks = days_left / 7
					# amount_overdue, seq_no, indication, regime, vacc_comment
					label = overdue_template % (
						years,
						weeks,
						shot['seq_no'],
						shot['l10n_indication'],
						shot['regime'],
						shot['vacc_comment']
					)
					self.LBOX_missing_shots.Append(label, None)	# pk_vacc_def
				else:
					# time_left, seq_no, regime, latest_due, vacc_comment
					label = due_template % (
						shot['time_left'].days / 7,
						shot['seq_no'],
						shot['indication'],
						shot['regime'],
						shot['latest_due'].Format('%m/%Y'),
						shot['vacc_comment']
					)
					self.LBOX_missing_shots.Append(label, None)	# pk_vacc_def
			# booster
			lbl_template = _('due now: booster for %s in %s (%s)')
			for shot in missing_shots['boosters']:
				# indication, regime, vacc_comment
				label = lbl_template % (
					shot['l10n_indication'],
					shot['regime'],
					shot['vacc_comment']
				)
				self.LBOX_missing_shots.Append(label, None)	# pk_vacc_def
	#----------------------------------------------------
	def _on_patient_selected(self, **kwargs):
		return 1
		# FIXME:
#		if has_focus:
#			wxCallAfter(self.__reset_ui_content)
#		else:
#			return 1
	#----------------------------------------------------
	def _on_vaccinations_updated(self, **kwargs):
		return 1
		# FIXME:
#		if has_focus:
#			wxCallAfter(self.__reset_ui_content)
#		else:
#			is_stale == True
#			return 1
#======================================================================
class gmGP_Immunisation(gmPlugin.wxPatientPlugin):
	"""Plugin to encapsulate the immunisation window."""

	__icons = {
"""icon_syringe""": 'x\xdam\xd0\xb1\n\x80 \x10\x06\xe0\xbd\xa7\xf8\xa1\xc1\xa6\x9f$\xe8\x01\x1a\
\x1a[Z\\#\x9a\x8a\xea\xfd\xa7N3\xf4\xb0C\x90\xff\xf3\x0e\xd4\xe6\xb8m5\x1b\
\xdbCV\x07k\xaae6\xc4\x8a\xe1X\xd6=$H\x9a\xaes\x0b\xc1I\xa8G\xa9\xb6\x8d\x87\
\xa9H\xa0@\xafe\xa7\xa8Bi\xa2\xdfs$\x19,G:\x175\xa1\x98W\x85\xc1\x9c\x1e\xcf\
Mc4\x85\x9f%\xfc\xae\x93!\xd5K_\xd4\x86\xf8\xa1?\x88\x12\xf9\x00 =F\x87'
}

	def name (self):
		return 'Immunisations Window'

	def MenuInfo (self):
		return ('view', '&Immunisation')

	def GetIconData(self, anIconID = None):
		if anIconID is None:
			return self.__icons[_("""icon_syringe""")]
		else:
			if self.__icons.has_key(anIconID):
				return self.__icons[anIconID]
			else:
				return self.__icons[_("""icon_syringe""")]

	def GetWidget (self, parent):
		return ImmunisationPanel (parent, -1)
#======================================================================
# main
#----------------------------------------------------------------------
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (600, 600))
	app.SetWidget(ImmunisationPanel, -1)
	app.MainLoop()
#======================================================================
# $Log: gmGP_Immunisation.py,v $
# Revision 1.32  2004-06-13 22:31:50  ncq
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
# Revision 1.31  2004/05/18 22:40:04  ncq
# - latest due -> latest_due
#
# Revision 1.30  2004/05/18 20:43:17  ncq
# - check get_clinical_record() return status
#
# Revision 1.29  2004/05/13 19:27:10  ncq
# - dealing with VOs now, not dicts anymore, when calling get_missing_vaccinations()
#
# Revision 1.28  2004/05/13 00:07:35  ncq
# - work with new/improved get_missing_vaccinations()
#
# Revision 1.27  2004/04/24 12:59:17  ncq
# - all shiny and new, vastly improved vaccinations
#   handling via clinical item objects
# - mainly thanks to Carlos Moro
#
# Revision 1.26  2004/03/09 07:34:51  ihaywood
# reactivating plugins
#
# Revision 1.25  2004/02/25 09:46:23  ncq
# - import from pycommon now, not python-common
#
# Revision 1.24  2004/02/02 16:19:49  ncq
# - adapt to new indication-based views in missing vaccs list
#
# Revision 1.23  2004/01/26 22:07:45  ncq
# - handling failure to retrieve vacc_ind into business object
#
# Revision 1.22  2004/01/26 21:53:39  ncq
# - gracefully handle failure to retrieve vaccinated indications list
#
# Revision 1.21  2004/01/18 21:54:39  ncq
# - rework from schedule/disease to indication paradigm
# - make progress note work in edit area
# - connect to vacc_mod_db signal and properly handle it
# - _update_ui_content()
#
# Revision 1.20  2004/01/06 10:09:06  ncq
# - reorder due/overdue listing
#
# Revision 1.19  2003/12/29 17:10:59  uid66147
# - upon selection transfer given_vaccination into edit area for modification
#
# Revision 1.18  2003/12/02 02:12:06  ncq
# - further cleanups
# - lower list: format dates sanely, hook up double-click
# - only edit area workup left
#
# Revision 1.17  2003/12/01 01:07:30  ncq
# - rip out, clean up
# - connect middle two lists
# - start connecting bottom list - doesn't display date/time properly yet
#
# Revision 1.16  2003/11/30 01:12:10  ncq
# - lots of cleanup
# - listen to patient_selected
# - actually fetch middle two lists from database
#
# Revision 1.15  2003/11/17 10:56:41  sjtan
#
# synced and commiting.
#
# manual edit areas modelled after r.terry's specs.
# Revision 1.14  2003/11/09 14:53:53  ncq
# - work on backend link
#
# Revision 1.13  2003/10/26 01:36:14  ncq
# - gmTmpPatient -> gmPatient
#
# Revision 1.12  2003/10/19 12:25:07  ncq
# - start connecting to backend
#
# Revision 1.11  2003/09/21 00:24:19  sjtan
#
# rollback.
#
# Revision 1.9  2003/02/07 14:29:32  ncq
# - == None -> is None
#
# Revision 1.8  2003/02/07 12:18:14  ncq
# - cvs metadata keywords
#
# @change log:
#	10.06.2002 rterry initial implementation, untested
#	30.07.2002 rterry icons inserted in file, code cleaned up
