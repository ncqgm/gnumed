"""GnuMed allergy related widgets.

"""
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmAllergyWidgets.py,v $
__version__ = "$Revision: 1.31 $"
__author__  = "R.Terry <rterry@gnumed.net>, H.Herb <hherb@gnumed.net>, K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL (details at http://www.gnu.org)'

import sys, time, datetime as pyDT, logging


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmDispatcher, gmI18N, gmDateTime, gmTools, gmMatchProvider
from Gnumed.wxpython import gmDateTimeInput, gmTerryGuiParts, gmRegetMixin
from Gnumed.business import gmPerson, gmAllergy
from Gnumed.wxGladeWidgets import wxgAllergyEditAreaPnl, wxgAllergyEditAreaDlg, wxgAllergyManagerDlg

_log = logging.getLogger('gm.ui')
_log.info(__version__)

#======================================================================
class cAllergyEditAreaPnl(wxgAllergyEditAreaPnl.wxgAllergyEditAreaPnl):

	def __init__(self, *args, **kwargs):
		wxgAllergyEditAreaPnl.wxgAllergyEditAreaPnl.__init__(self, *args, **kwargs)

		try:
			self.__allergy = kwargs['allergy']
		except KeyError:
			self.__allergy = None

		mp = gmMatchProvider.cMatchProvider_SQL2 (
			queries = [u"""
select substance, substance
from clin.allergy
where substance %(fragment_condition)s

	union

select generics, generics
from clin.allergy
where generics %(fragment_condition)s

	union

select allergene, allergene
from clin.allergy
where allergene %(fragment_condition)s

	union

select atc_code, atc_code
from clin.allergy
where atc_code %(fragment_condition)s
"""
			]
		)
		mp.setThresholds(2, 3, 5)
		self._PRW_trigger.matcher = mp

		mp = gmMatchProvider.cMatchProvider_SQL2 (
			queries = [u"""
select narrative, narrative
from clin.allergy
where narrative %(fragment_condition)s
"""]
		)
		mp.setThresholds(2, 3, 5)
		self._PRW_reaction.matcher = mp
		self._PRW_reaction.enable_default_spellchecker()

#		self._RBTN_type_sensitivity.MoveAfterInTabOrder(self._RBTN_type_allergy)
#		self._ChBOX_definite.MoveAfterInTabOrder(self._RBTN_type_sensitivity)

		self.refresh()
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def clear(self):
		self.__allergy = None
		return self.refresh()
	#--------------------------------------------------------
	def refresh(self, allergy=None):

		if allergy is not None:
			self.__allergy = allergy

		if self.__allergy is None:
			ts = gmDateTime.cFuzzyTimestamp (
				timestamp = pyDT.datetime.now(tz=gmDateTime.gmCurrentLocalTimezone),
				accuracy = gmDateTime.acc_days
			)
			self._DPRW_date_noted.SetData(data = ts)
			self._PRW_trigger.SetText()
			self._TCTRL_brand_name.SetValue('')
			self._TCTRL_generic.SetValue('')
			self._ChBOX_generic_specific.SetValue(1)
			self._TCTRL_atc_classes.SetValue('')
			self._PRW_reaction.SetText()
			self._RBTN_type_allergy.SetValue(1)
			self._RBTN_type_sensitivity.SetValue(0)
			self._ChBOX_definite.SetValue(1)
			return True

		if not isinstance(self.__allergy, gmAllergy.cAllergy):
			raise ValueError('[%s].refresh(): expected gmAllergy.cAllergy instance, got [%s] instead' % (self.__class__.__name__, self.__allergy))

		ts = gmDateTime.cFuzzyTimestamp (
			timestamp = self.__allergy['date'],
			accuracy = gmDateTime.acc_days
		)
		self._DPRW_date_noted.SetData(data=ts)
		self._PRW_trigger.SetText(value = self.__allergy['substance'])
		self._TCTRL_brand_name.SetValue(self.__allergy['substance'])
		self._TCTRL_generic.SetValue(gmTools.coalesce(self.__allergy['generics'], ''))
		self._ChBOX_generic_specific.SetValue(self.__allergy['generic_specific'])
		self._TCTRL_atc_classes.SetValue(gmTools.coalesce(self.__allergy['atc_code'], ''))
		self._PRW_reaction.SetText(value = gmTools.coalesce(self.__allergy['reaction'], ''))
		if self.__allergy['type'] == 'allergy':
			self._RBTN_type_allergy.SetValue(1)
		else:
			self._RBTN_type_sensitivity.SetValue(1)
		self._ChBOX_definite.SetValue(self.__allergy['definite'])
	#--------------------------------------------------------
	def __is_valid_for_save(self):

		if self._PRW_trigger.GetValue().strip() == '':
			self._PRW_trigger.SetBackgroundColour('pink')
			self._PRW_trigger.Refresh()
			self._PRW_trigger.SetFocus()
			return False
		self._PRW_trigger.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
		self._PRW_trigger.Refresh()

		return True
	#--------------------------------------------------------
	def save(self, can_create=True):
		if not self.__is_valid_for_save():
			return False

		if self.__allergy is None:
			if not can_create:
				gmDispatcher.send(signal='statustext', msg=_('Creating new allergy not allowed.'))
				return False

			pat = gmPerson.gmCurrentPatient()
			emr = pat.get_emr()

			if self._RBTN_type_allergy.GetValue():
				allg_type = 'allergy'
			else:
				allg_type = 'sensitivity'
			self.__allergy = emr.add_allergy (
				substance = self._PRW_trigger.GetValue().strip(),
				allg_type = allg_type
			)

		# and update it with known data
		self.__allergy['date'] = self._DPRW_date_noted.GetData().get_pydt()
		self.__allergy['substance'] = self._PRW_trigger.GetValue().strip()
		# FIXME: determine brandname/generic/etc from substance (trigger field)
		self.__allergy['generic_specific'] = (True and self._ChBOX_generic_specific.GetValue())
		self.__allergy['reaction'] = self._PRW_reaction.GetValue().strip()
		self.__allergy['definite'] = (True and self._ChBOX_definite.GetValue())
		if self._RBTN_type_allergy.GetValue():
			 self.__allergy['pk_type'] = 'allergy'
		else:
			self.__allergy['pk_type'] = 'sensitivity'

		self.__allergy.save_payload()

		return True
#======================================================================
class cAllergyEditAreaDlg(wxgAllergyEditAreaDlg.wxgAllergyEditAreaDlg):

	def __init__(self, *args, **kwargs):

		try:
			allergy = kwargs['allergy']
			del kwargs['allergy']
		except KeyError:
			allergy = None

		wxgAllergyEditAreaDlg.wxgAllergyEditAreaDlg.__init__(self, *args, **kwargs)

		if allergy is None:
#			self._BTN_save.SetLabel(_('&Save'))
			self._BTN_clear.SetLabel(_('&Clear'))
		else:
#			self._BTN_save.SetLabel(_('Update'))
			self._BTN_clear.SetLabel(_('&Restore'))

		self._PNL_edit_area.refresh(allergy = allergy)
	#--------------------------------------------------------
	def _on_save_button_pressed(self, evt):
		if self._PNL_edit_area.save():
			if self.IsModal():
				self.EndModal(wx.ID_OK)
			else:
				self.Close()
	#--------------------------------------------------------
	def _on_clear_button_pressed(self, evt):
		self._PNL_edit_area.refresh()
#======================================================================
class cAllergyManagerDlg(wxgAllergyManagerDlg.wxgAllergyManagerDlg):

	def __init__(self, *args, **kwargs):
		wxgAllergyManagerDlg.wxgAllergyManagerDlg.__init__(self, *args, **kwargs)

		self.__set_columns()
		# MacOSX crashes on this with:
		#  exception type : wx._core.PyAssertionError
		#  exception value: C++ assertion "i" failed at /BUILD/wxPython-src-2.8.3.0/src/common/wincmn.cpp(2634) in DoMoveInTabOrder(): MoveBefore/AfterInTabOrder(): win is not a sibling
		# while Win/Linux work just fine
		#self._PNL_edit_area._ChBOX_definite.MoveAfterInTabOrder(self._BTN_save)
		self.__refresh_ui()
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __set_columns(self):
		self._LCTRL_allergies.set_columns (columns = [
			_('Type'),
			_('Certainty'),
			_('Trigger'),
			_('Reaction')
		])
	#--------------------------------------------------------
	def __refresh_ui(self):

		pat = gmPerson.gmCurrentPatient()
		emr = pat.get_emr()
		allergies = emr.get_allergies()
		no_of_allergies = len(allergies)

		self._LCTRL_allergies.DeleteAllItems()
		if no_of_allergies > 0:
			emr.allergic_state = 1
			for allergy in allergies:
				row_idx = self._LCTRL_allergies.InsertStringItem(no_of_allergies, label = allergy['l10n_type'])
				if allergy['definite']:
					label = _('definite')
				else:
					label = u''
				self._LCTRL_allergies.SetStringItem(index = row_idx, col = 1, label = label)
				self._LCTRL_allergies.SetStringItem(index = row_idx, col = 2, label = allergy['descriptor'])
				self._LCTRL_allergies.SetStringItem(index = row_idx, col = 3, label = gmTools.coalesce(allergy['reaction'], u''))
			self._LCTRL_allergies.set_data(data=allergies)
		else:
			row_idx = self._LCTRL_allergies.InsertStringItem(no_of_allergies, label = _('allergic state'))
			self._LCTRL_allergies.SetStringItem(index = row_idx, col = 3, label = gmAllergy.allergic_state2str(state = emr.allergic_state))

		self._LCTRL_allergies.set_column_widths (widths = [
			wx.LIST_AUTOSIZE,
			wx.LIST_AUTOSIZE,
			wx.LIST_AUTOSIZE,
			wx.LIST_AUTOSIZE
		])

		self._LCTRL_allergies.Enable(no_of_allergies <> 0)
		self._BTN_undisclosed.Enable((no_of_allergies == 0))
		self._BTN_none.Enable((no_of_allergies == 0))
		self._BTN_unknown.Enable((no_of_allergies == 0))

		self._PNL_edit_area.clear()
		self._BTN_delete.Enable(False)
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_dismiss_button_pressed(self, evt):
		if self.IsModal():
			self.EndModal(wx.ID_OK)
		else:
			self.Close()
	#--------------------------------------------------------
	def _on_clear_button_pressed(self, evt):
		self._LCTRL_allergies.deselect_selected_item()
		self._PNL_edit_area.clear()
		self._BTN_delete.Enable(False)
	#--------------------------------------------------------
	def _on_delete_button_pressed(self, evt):
		allergy = self._LCTRL_allergies.get_selected_item_data(only_one=True)
		pat = gmPerson.gmCurrentPatient()
		emr = pat.get_emr()
		emr.delete_allergy(pk_allergy = allergy['pk_allergy'])
		self.__refresh_ui()
	#--------------------------------------------------------
	def _on_list_item_selected(self, evt):
		allergy = self._LCTRL_allergies.get_selected_item_data(only_one=True)
		self._PNL_edit_area.refresh(allergy=allergy)
		self._BTN_delete.Enable(True)
	#--------------------------------------------------------
	def _on_save_button_pressed(self, evt):
		if not self._PNL_edit_area.save():
			return False
		self.__refresh_ui()
	#--------------------------------------------------------
	def _on_undisclosed_button_pressed(self, evt):
		pat = gmPerson.gmCurrentPatient()
		emr = pat.get_emr()
		emr.allergic_state = -1
		self.__refresh_ui()
	#--------------------------------------------------------
	def _on_unknown_button_pressed(self, evt):
		pat = gmPerson.gmCurrentPatient()
		emr = pat.get_emr()
		emr.allergic_state = None
		self.__refresh_ui()
	#--------------------------------------------------------
	def _on_none_button_pressed(self, evt):
		pat = gmPerson.gmCurrentPatient()
		emr = pat.get_emr()
		emr.allergic_state = 0
		self.__refresh_ui()
#======================================================================
class cAllergyPanel(wx.Panel, gmRegetMixin.cRegetOnPaintMixin):
	"""Allergy details panel.

		This panel will hold all the allergy details and
		allow entry of those details via the editing area.
	"""
	#----------------------------------------------------
	def __init__(self, parent, id=-1):
		wx.Panel.__init__(self, parent, id, wx.DefaultPosition, wx.DefaultSize, wx.RAISED_BORDER)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)
		self.__do_layout()
		self.__pat = gmPerson.gmCurrentPatient()
		self.__register_interests()
		self.__reset_ui_content()
	#----------------------------------------------------
	def __do_layout(self):
		# -- top part --
		pnl_UpperCaption = gmTerryGuiParts.cHeadingCaption(self, -1, _("ALLERGIES"))
		self.editarea = gmAllergyEditArea(self, -1)

		# -- middle part --
		# divider headings below edit area
		pnl_MiddleCaption = gmTerryGuiParts.cDividerCaption(self, -1, _("Allergy and Sensitivity - Summary"))
#		self.sizer_divider_drug_generic = wx.BoxSizer(wxHORIZONTAL)
#		self.sizer_divider_drug_generic.Add(pnl_MiddleCaption, 1, wxEXPAND)
		self.LCTRL_allergies = wx.ListCtrl (
			parent = self,
			id = ID_ALLERGY_LIST,
			pos = wx.DefaultPosition,
			size = wx.DefaultSize,
			style = wx.LC_SINGLE_SEL | wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_HRULES | wx.LC_VRULES | wx.VSCROLL
		)
		self.LCTRL_allergies.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, False, ''))
		self.LCTRL_allergies.InsertColumn(0, _("Type"))
		self.LCTRL_allergies.InsertColumn(1, _("Status"))
		self.LCTRL_allergies.InsertColumn(2, _("ATC/Class"))
		self.LCTRL_allergies.InsertColumn(3, _("Substance"))
		self.LCTRL_allergies.InsertColumn(4, _("Generics"))
		self.LCTRL_allergies.InsertColumn(5, _("Reaction"))

		# -- bottom part --
		pnl_LowerCaption = gmTerryGuiParts.cDividerCaption(self, -1, _('Class notes'))
		#add a richtext control or a wxTextCtrl multiline to display the class text information
		#e.g. would contain say information re the penicillins
		self.class_notes = wx.TextCtrl (
			self,
			-1,
			"A member of a new class of nonsteroidal anti-inflammatory agents (COX-2 selective NSAIDs) which have a mechanism of action that inhibits prostaglandin synthesis primarily by inhibition of cyclooxygenase 2 (COX-2). At therapeutic doses these have no effect on prostanoids synthesised by activation of COX-1 thereby not interfering with normal COX-1 related physiological processes in tissues, particularly the stomach, intestine and platelets.",
			size = (200, 100),
			style = wx.TE_MULTILINE | wx.TE_READONLY
		)
		self.class_notes.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, False, ''))

		# -- add elements to main background sizer --
		self.mainsizer = wx.BoxSizer(wx.VERTICAL)
		self.mainsizer.Add(pnl_UpperCaption, 0, wx.EXPAND)
		self.mainsizer.Add(self.editarea, 6, wx.EXPAND)
#		self.mainsizer.Add(self.sizer_divider_drug_generic,0,wxEXPAND)
		self.mainsizer.Add(pnl_MiddleCaption, 0, wx.EXPAND)
		self.mainsizer.Add(self.LCTRL_allergies, 5, wx.EXPAND)
		self.mainsizer.Add(pnl_LowerCaption, 0, wx.EXPAND)
		self.mainsizer.Add(self.class_notes, 4, wx.EXPAND)

		self.SetAutoLayout(True)
		self.SetSizer(self.mainsizer)
		self.mainsizer.Fit(self)
	#-----------------------------------------------
	def __register_interests(self):
		wx.EVT_LIST_ITEM_ACTIVATED(self, ID_ALLERGY_LIST, self._on_allergy_activated)

		# client internal signals
		gmDispatcher.connect(signal = u'post_patient_selection', receiver=self._schedule_data_reget)
#		gmDispatcher.connect(signal = u'vaccinations_updated', receiver=self._schedule_data_reget)
	#-----------------------------------------------
	def __reset_ui_content(self):
		self.editarea.set_data()
		self.LCTRL_allergies.DeleteAllItems()
	#-----------------------------------------------
	def _populate_with_data(self):
		if not self.__pat.is_connected():
			return False

		self.LCTRL_allergies.DeleteAllItems()

		emr = self.__pat.get_emr()
		allergies = emr.get_allergies()
		if allergies is None:
			return False
		for list_line in range(len(allergies)):
			allg = allergies[list_line]
			list_line = self.LCTRL_allergies.InsertStringItem(list_line, allg['l10n_type'])
			# FIXME: check with Richard design specs
			if allg['definite']:
				self.LCTRL_allergies.SetStringItem(list_line, 1, _('definite'))
			else:
				self.LCTRL_allergies.SetStringItem(list_line, 1, _('likely'))
			if allg['atc_code'] is not None:
				self.LCTRL_allergies.SetStringItem(list_line, 2, allg['atc_code'])
			self.LCTRL_allergies.SetStringItem(list_line, 3, allg['substance'])
			if allg['generics'] is not None:
				self.LCTRL_allergies.SetStringItem(list_line, 4, allg['generics'])
			self.LCTRL_allergies.SetStringItem(list_line, 5, allg['reaction'])
			self.LCTRL_allergies.SetItemData(list_line, allg['pk_allergy'])
		for col in range(5):
			self.LCTRL_allergies.SetColumnWidth(col, wx.LIST_AUTOSIZE)
		# FIXME: resize event needed ?
		return True
	#-----------------------------------------------
	def _on_allergy_activated(self, evt):
		pk_allg = evt.GetData()
		emr = self.__pat.get_emr()
		allgs = emr.get_allergies(ID_list=[pk_allg])
		self.editarea.set_data(allergy = allgs[0])
#======================================================================
# main
#----------------------------------------------------------------------
if __name__ == "__main__":

	gmI18N.activate_locale()
	gmI18N.install_domain(domain='gnumed')

	#-----------------------------------------------
	def test_allergy_edit_area_dlg():
		app = wx.PyWidgetTester(size = (600, 600))
		dlg = cAllergyEditAreaDlg(parent=app.frame, id=-1)
		dlg.ShowModal()
#		emr = pat.get_emr()
#		allergy = emr.get_allergies()[0]
#		dlg = cAllergyEditAreaDlg(parent=app.frame, id=-1, allergy=allergy)
#		dlg.ShowModal()
		return
	#-----------------------------------------------
	def test_allergy_manager_dlg():
		app = wx.PyWidgetTester(size = (800, 600))
		dlg = cAllergyManagerDlg(parent=app.frame, id=-1)
		dlg.ShowModal()
		return
	#-----------------------------------------------
	if len(sys.argv) > 1 and sys.argv[1] == 'test':

		pat = gmPerson.ask_for_patient()
		if pat is None:
			sys.exit(0)
		gmPerson.set_active_patient(pat)

		#test_allergy_edit_area_dlg()
		test_allergy_manager_dlg()

#		app = wxPyWidgetTester(size = (600, 600))
#		app.SetWidget(cAllergyPanel, -1)
#		app.MainLoop()
#======================================================================
# $Log: gmAllergyWidgets.py,v $
# Revision 1.31  2008-03-06 18:29:29  ncq
# - standard lib logging only
#
# Revision 1.30  2008/01/30 14:03:41  ncq
# - use signal names directly
# - switch to std lib logging
#
# Revision 1.29  2008/01/16 19:38:15  ncq
# - wxMAC doesn't like some Move*InTabOrder()
#
# Revision 1.28  2007/10/25 12:19:53  ncq
# - no more useless allergy update
#
# Revision 1.27  2007/09/10 18:35:27  ncq
# - help wxPython a bit with tab order
# - fix a faulty variable access
# - improve test suite
#
# Revision 1.26  2007/08/12 00:06:59  ncq
# - no more gmSignals.py
#
# Revision 1.25  2007/07/10 20:28:36  ncq
# - consolidate install_domain() args
#
# Revision 1.24  2007/04/02 18:39:52  ncq
# - gmFuzzyTimestamp -> gmDateTime
#
# Revision 1.23  2007/03/27 09:59:47  ncq
# - enable spell checker on allergy.reaction
#
# Revision 1.22  2007/03/26 16:49:50  ncq
# - "reaction" can be empty
#
# Revision 1.21  2007/03/22 11:04:15  ncq
# - activate prw match providers
#
# Revision 1.20  2007/03/21 08:14:01  ncq
# - improved allergy manager
# - cleanup
#
# Revision 1.19  2007/03/18 13:57:43  ncq
# - re-add lost 1.19
#
# Revision 1.19  2007/03/12 12:25:15  ncq
# - add allergy edit area panel/dialog
# - improved test suite
#
# Revision 1.18  2007/02/04 15:49:31  ncq
# - use SetText() on phrasewheel
#
# Revision 1.17  2006/10/25 07:46:44  ncq
# - Format() -> strftime() since datetime.datetime does not have .Format()
#
# Revision 1.16  2006/10/24 13:20:57  ncq
# - do not import gmPG
#
# Revision 1.15  2006/05/15 13:35:59  ncq
# - signal cleanup:
#   - activating_patient -> pre_patient_selection
#   - patient_selected -> post_patient_selection
#
# Revision 1.14  2006/05/04 09:49:20  ncq
# - get_clinical_record() -> get_emr()
# - adjust to changes in set_active_patient()
# - need explicit set_active_patient() after ask_for_patient() if wanted
#
# Revision 1.13  2006/01/03 12:12:03  ncq
# - make epydoc happy re _()
#
# Revision 1.12  2005/12/27 18:46:39  ncq
# - use gmI18N
#
# Revision 1.11  2005/09/28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.10  2005/09/28 15:57:47  ncq
# - a whole bunch of wx.Foo -> wx.Foo
#
# Revision 1.9  2005/09/26 18:01:50  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.8  2005/09/24 09:17:27  ncq
# - some wx2.6 compatibility fixes
#
# Revision 1.7  2005/03/20 17:49:11  ncq
# - default for id
#
# Revision 1.6  2005/01/31 10:37:26  ncq
# - gmPatient.py -> gmPerson.py
#
# Revision 1.5  2004/12/15 21:55:00  ncq
# - adapt to cleanly separated old/new style edit area
#
# Revision 1.4  2004/10/27 12:17:22  ncq
# - robustify should there not be an active patient
#
# Revision 1.3  2004/10/11 20:14:16  ncq
# - use RegetOnPaintMixin
# - attach to backend
# - cleanup, remove cruft
#
# Revision 1.2  2004/07/18 20:30:53  ncq
# - wxPython.true/false -> Python.True/False as Python tells us to do
#
# Revision 1.1  2004/07/17 21:16:38  ncq
# - cleanup/refactor allergy widgets:
#   - Horst space plugin added
#   - Richard space plugin separated out
#   - plugin independant GUI code aggregated
#   - allergies edit area factor out from generic edit area file
#
#
