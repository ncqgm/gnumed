#======================================================================
# GnuMed immunisation/vaccination panel
# -------------------------------------
#
# this panel holds the immunisation details
#
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: wxPython (>= version 2.3.1)
#======================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/patient/gmGP_Immunisation.py,v $
# $Id: gmGP_Immunisation.py,v 1.16 2003-11-30 01:12:10 ncq Exp $
__version__ = "$Revision: 1.16 $"
__author__ = "R.Terry, S.J.Tan, K.Hilbert"

import sys

if __name__ == "__main__":
	# FIXME: this will not work on other platforms
	sys.path.append("../../python-common")
	sys.path.append("../../business")
	sys.path.append("../")
	import gmI18N

from gmGuiElement_HeadingCaptionPanel import HeadingCaptionPanel
from gmGuiElement_DividerCaptionPanel import DividerCaptionPanel
from gmGuiElement_AlertCaptionPanel import AlertCaptionPanel

# panel class holding editing prompts and text boxes
import gmEditArea
import gmPlugin, gmPatient, gmDispatcher, gmSignals

from gmPatientHolder import PatientHolder

import gmLog
_log = gmLog.gmDefLog
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)
_log.Log(gmLog.lData, __version__)

from wxPython.wx import *

ID_IMMUNISATIONLIST = wxNewId()
ID_IMMUNISATIONS = wxNewId()
ID_ALL_MENU  = wxNewId()

gmSECTION_IMMUNISATIONS = 6
#------------------------------------
#Dummy data to simulate items
#------------------------------------
scheduledata = {
1 : ("Influenza","null"),
2 : ("Tetanus","null"),
3 : ("Typhoid","null"),
}
vaccinedata = {
1 : ("Fluvax","15/03/2001"),
2 : ("Vaxigrip","22/04/2002"),
}

immunisationprompts = {
1:("Target Disease"),
2:("Vaccine"),
3:("Date Given"),
4:("Serial No."),
5:("Site injected"),
6:("Progress Notes"),
7:("")    
}
#======================================================================
class ImmunisationPanel(wxPanel, PatientHolder):

	def __init__(self, parent,id):
		wxPanel.__init__(self, parent, id, wxDefaultPosition,wxDefaultSize,wxRAISED_BORDER)
#		PatientHolder.__init__(self)
		self.patient = gmPatient.gmCurrentPatient()
		#--------------------
		#add the main heading
		#--------------------
		pnl_UpperCaption = HeadingCaptionPanel (self, -1, _("  IMMUNISATIONS  "))
		#--------------------------------------------------
		#now create the editarea specific for immunisations
		#--------------------------------------------------
		self.editarea = gmEditArea.gmVaccinationEditArea(self,-1)
		#,immunisationprompts,gmSECTION_IMMUNISATIONS)

		#-----------------------------------------------
		# middle part
		#-----------------------------------------------
		# divider headings below editing area
		vaccinated_regimes_heading = DividerCaptionPanel(self, -1, _("Disease or Schedule"))
		vaccine_given_heading = DividerCaptionPanel(self, -1, _("Vaccine Given"))
		szr_MiddleCaption1 = wxBoxSizer(wxHORIZONTAL)
		szr_MiddleCaption1.Add(vaccinated_regimes_heading, 1, wxEXPAND)
		szr_MiddleCaption1.Add(vaccine_given_heading, 1, wxEXPAND)

		# left list: regimes for which vaccinations have been given
		self.vaccinated_regimes_list = wxListBox(
			parent = self,
			id = ID_IMMUNISATIONLIST,
			choices = [],
			style = wxLB_HSCROLL | wxLB_NEEDED_SB | wxSUNKEN_BORDER
		)

		self.vaccinated_regimes_list.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, false, ''))

		# right list: vaccines the patient received
		self.vaccines_given_list = wxListBox(
			parent = self,
			id = ID_IMMUNISATIONLIST,
			choices = [],
			style = wxLB_HSCROLL | wxLB_NEEDED_SB | wxSUNKEN_BORDER
		)
		self.vaccines_given_list.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, false, ''))

		# and place them
		szr_MiddleCaption2 = wxBoxSizer(wxHORIZONTAL)
		szr_MiddleCaption2.Add(self.vaccinated_regimes_list,4,wxEXPAND)
		szr_MiddleCaption2.Add(self.vaccines_given_list,6, wxEXPAND)

		#--------------------------------------------------------------------------------------
		pnl_MiddleCaption3 = DividerCaptionPanel(self, -1, _("Missing Immunisations"))
#		epr = self.pat['clinical record']
#		missing_shots = epr.get_missing_vaccinations()
#		missing_shots = epr['vaccination status']
		# FIXME: get list of due vaccs, too, and highlight those
		self.LBOX_missing_shots = wxListBox(
			self,
			-1,
			size=(200, 100),
			choices= [ "Schedule: Pneumococcal - no vaccination recorded"],
			style=wxLB_SINGLE
		)
		self.LBOX_missing_shots.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,false,''))
		#----------------------------------------
		#add an alert caption panel to the bottom
		#----------------------------------------
		pnl_BottomCaption = AlertCaptionPanel(self, -1, _("  Alerts  "))
		#---------------------------------------------
		#add all elements to the main background sizer
		#---------------------------------------------
		self.mainsizer = wxBoxSizer(wxVERTICAL)
		self.mainsizer.Add(pnl_UpperCaption, 0, wxEXPAND)
#		self.mainsizer.Add(self.dummypanel1,1,wxEXPAND)
		self.mainsizer.Add(self.editarea, 6, wxEXPAND)
		self.mainsizer.Add(szr_MiddleCaption1, 0, wxEXPAND)
		self.mainsizer.Add(szr_MiddleCaption2, 4, wxEXPAND)
		self.mainsizer.Add(pnl_MiddleCaption3, 0, wxEXPAND)
		self.mainsizer.Add(self.LBOX_missing_shots, 4, wxEXPAND)
		self.mainsizer.Add(pnl_BottomCaption, 0, wxEXPAND)

		self.SetSizer(self.mainsizer)
		self.mainsizer.Fit (self)
		self.SetAutoLayout(true)
		EVT_SIZE (self, self.OnSize)

		self.__register_interests()
	#----------------------------------------------------
	def __register_interests(self):
		# client internal signals
		gmDispatcher.connect(signal=gmSignals.patient_selected(), receiver=self._on_patient_selected)
	#----------------------------------------------------
	def OnSize (self, event):
		w, h = event.GetSize ()
		self.mainsizer.SetDimension (0, 0, w, h)
	#----------------------------------------------------
	def _on_patient_selected(self, **kwargs):
		print "******** updating vaccination lists"
		# FIXME: only do this if visible ...
		epr = self.patient.get_clinical_record()
		shots, idx = epr.get_vaccinations()
		# populate vaccinated-regimes list
		data = []
		for shot in shots:
			data.append('%s (%s)' % (shot[idx['regime']], shot[idx['indication']]))
		self.vaccinated_regimes_list.Set(data)
		# populate vaccines-given list
		data = []
		for shot in shots:
			data.append('%s: %s (%s)' % (shot[idx['date']].Format('%Y-%m-%d'), shot[idx['vaccine']], shot[idx['vaccine_short']]))
		self.vaccines_given_list.Set(data)

		# FIXME: start listening to this patients *vaccination* updates
#		gmDispatcher.connect(signal=gmSignals.allergy_updated(), receiver=self._update_allergies)

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
# Revision 1.16  2003-11-30 01:12:10  ncq
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
