#======================================================================
# GnuMed immunisation/vaccination patient plugin
#
# this plugin holds the immunisation details
#
# @copyright: author
#======================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/patient/gmGP_Immunisation.py,v $
# $Id: gmGP_Immunisation.py,v 1.35 2004-07-17 11:00:31 ncq Exp $
__version__ = "$Revision: 1.35 $"
__author__ = "R.Terry, S.J.Tan, K.Hilbert"
__license__ = 'GPL (details at http://www.gnu.org)'

from Gnumed.wxpython import gmPlugin_Patient, gmVaccWidgets

#======================================================================
class gmGP_Immunisation(gmPlugin_Patient.wxPatientPlugin):
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
		return gmVaccWidgets.ImmunisationPanel (parent, -1)
#======================================================================
# main
#----------------------------------------------------------------------
if __name__ == "__main__":
	print "there isn't really any unit test for this"
#	from wxPython.wx import *
#	app = wxPyWidgetTester(size = (600, 600))
#	app.SetWidget(gmVaccWidgets.ImmunisationPanel, -1)
#	app.MainLoop()
#======================================================================
# $Log: gmGP_Immunisation.py,v $
# Revision 1.35  2004-07-17 11:00:31  ncq
# - cleanup
#
# Revision 1.34  2004/07/15 23:16:21  ncq
# - refactor vaccinations GUI code into
#   - gmVaccWidgets.py: layout manager independant widgets
#   - gui/gmVaccinationsPlugins.py: Horst space notebook plugin
#   - patient/gmPG_Immunisation.py: erstwhile Richard space patient plugin
#
# Revision 1.33  2004/06/25 13:28:00  ncq
# - logically separate notebook and clinical window plugins completely
#
# Revision 1.32  2004/06/13 22:31:50  ncq
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
