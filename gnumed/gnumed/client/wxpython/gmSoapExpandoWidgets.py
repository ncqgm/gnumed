# -*- coding: utf-8 -*-
"""GNUmed expando based textual progress notes handling widgets."""
#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later (details at http://www.gnu.org)"

import sys
import logging


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')

from Gnumed.pycommon import gmI18N

if __name__ == '__main__':
	gmI18N.activate_locale()
	gmI18N.install_domain()

from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmDateTime

from Gnumed.business import gmPerson
from Gnumed.business import gmEMRStructItems

from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmVisualProgressNoteWidgets
from Gnumed.wxpython import gmTextCtrl

_log = logging.getLogger('gm.ui')

#============================================================
from Gnumed.wxGladeWidgets import wxgSoapNoteExpandoEditAreaPnl

class cSoapNoteExpandoEAPnl(gmTextCtrl.cExpandoTextCtrlHandling_PanelMixin, wxgSoapNoteExpandoEditAreaPnl.wxgSoapNoteExpandoEditAreaPnl):
	"""An Edit Area like panel for entering progress notes.

	Subjective:					Codes:
		expando text ctrl
	Objective:					Codes:
		expando text ctrl
	Assessment:					Codes:
		expando text ctrl
	Plan:						Codes:
		expando text ctrl
	visual progress notes
		panel with images
	Episode synopsis:			Codes:
		expando text ctrl

	- knows the problem this edit area is about
	- can deal with issue or episode type problems
	"""
	def __init__(self, *args, **kwargs):

		try:
			self.problem = kwargs['problem']
			del kwargs['problem']
		except KeyError:
			self.problem = None

		wxgSoapNoteExpandoEditAreaPnl.wxgSoapNoteExpandoEditAreaPnl.__init__(self, *args, **kwargs)

		self.__init_ui()

		self.soap_fields = [
			self._TCTRL_Soap,
			self._TCTRL_sOap,
			self._TCTRL_soAp,
			self._TCTRL_soaP
		]
		self.__register_interests()

	#--------------------------------------------------------
	def __init_ui(self):
		self.refresh_summary()
		if self.problem is not None:
			if self.problem['summary'] is None:
				self._TCTRL_episode_summary.SetValue(u'')
		self.refresh_visual_soap()
	#--------------------------------------------------------
	def refresh(self):
		self.refresh_summary()
		self.refresh_visual_soap()
	#--------------------------------------------------------
	def refresh_summary(self):
		self._TCTRL_episode_summary.SetValue(u'')
		self._PRW_episode_codes.SetText(u'', self._PRW_episode_codes.list2data_dict([]))
		self._LBL_summary.SetLabel(_('Episode synopsis'))

		# new problem ?
		if self.problem is None:
			return

		# issue-level problem ?
		if self.problem['type'] == u'issue':
			return

		# episode-level problem
		caption = _(u'Synopsis (%s)') % (
			gmDateTime.pydt_strftime (
				self.problem['modified_when'],
				format = '%B %Y',
				accuracy = gmDateTime.acc_days
			)
		)
		self._LBL_summary.SetLabel(caption)

		if self.problem['summary'] is not None:
			self._TCTRL_episode_summary.SetValue(self.problem['summary'].strip())

		val, data = self._PRW_episode_codes.generic_linked_codes2item_dict(self.problem.generic_codes)
		self._PRW_episode_codes.SetText(val, data)
	#--------------------------------------------------------
	def refresh_visual_soap(self):
		if self.problem is None:
			self._PNL_visual_soap.refresh(document_folder = None)
			return

		if self.problem['type'] == u'issue':
			self._PNL_visual_soap.refresh(document_folder = None)
			return

		if self.problem['type'] == u'episode':
			pat = gmPerson.gmCurrentPatient()
			doc_folder = pat.get_document_folder()
			emr = pat.get_emr()
			self._PNL_visual_soap.refresh (
				document_folder = doc_folder,
				episodes = [self.problem['pk_episode']],
				encounter = emr.active_encounter['pk_encounter']
			)
			return
	#--------------------------------------------------------
	def clear(self):
		self._TCTRL_episode_summary.SetValue(u'')
		self._LBL_summary.SetLabel(_('Episode synopsis'))
		self._PRW_episode_codes.SetText(u'', self._PRW_episode_codes.list2data_dict([]))
		self._PNL_visual_soap.clear()

		for field in self.soap_fields:
			field.SetValue(u'')
	#--------------------------------------------------------
	def add_visual_progress_note(self):
		fname, discard_unmodified = gmVisualProgressNoteWidgets.select_visual_progress_note_template(parent = self)
		if fname is None:
			return False

		if self.problem is None:
			issue = None
			episode = None
		elif self.problem['type'] == 'issue':
			issue = self.problem['pk_health_issue']
			episode = None
		else:
			issue = self.problem['pk_health_issue']
			episode = gmEMRStructItems.problem2episode(self.problem)

		wx.CallAfter (
			gmVisualProgressNoteWidgets.edit_visual_progress_note,
			filename = fname,
			episode = episode,
			discard_unmodified = discard_unmodified,
			health_issue = issue
		)
	#--------------------------------------------------------
	def save(self, emr=None, episode_name_candidates=None, encounter=None):

		if self.empty:
			return True

		# new episode (standalone=unassociated or new-in-issue)
		if (self.problem is None) or (self.problem['type'] == 'issue'):
			episode = self.__create_new_episode(emr = emr, episode_name_candidates = episode_name_candidates)
			# user cancelled
			if episode is None:
				return False
		# existing episode
		else:
			episode = emr.problem2episode(self.problem)

		if encounter is None:
			encounter = emr.current_encounter['pk_encounter']

		# set summary but only if not already set above for a
		# newly created episode (either standalone or within
		# a health issue)
		if self.problem is not None:
			if self.problem['type'] == 'episode':
				episode['summary'] = self._TCTRL_episode_summary.GetValue().strip()
				episode.save()

		# codes for episode
		episode.generic_codes = [ d['data'] for d in self._PRW_episode_codes.GetData() ]

		self._save_soap(pk_episode = episode['pk_episode'], pk_encounter = encounter)

		return True
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def _save_soap(self, pk_episode, pk_encounter):
		soap = self.soap
		for cat in soap:
			if len(soap[cat]) == 0:
				continue
			saved, data = gmClinNarrative.create_clin_narrative (
				soap_cat = cat,
				narrative = soap[cat],
				episode_id = pk_episode,
				encounter_id = pk_encounter
			)

		# codes per narrative !
#		for note in soap_notes:
#			if note['soap_cat'] == u's':
#				codes = self._PRW_Soap_codes
#			elif note['soap_cat'] == u'o':
#			elif note['soap_cat'] == u'a':
#			elif note['soap_cat'] == u'p':

	#--------------------------------------------------------
	def __create_new_episode(self, emr=None, episode_name_candidates=None):

		episode_name_candidates.append(self._TCTRL_episode_summary.GetValue().strip())
		for candidate in episode_name_candidates:
			if candidate is None:
				continue
			epi_name = candidate.strip().replace('\r', '//').replace('\n', '//')
			break

		if self.problem is None:
			msg = _(
				u'Enter a short working name for this new problem\n'
				u'(which will become a new, unassociated episode):\n'
			)
		else:
			issue = emr.problem2issue(self.problem)
			msg = _(
				u'Enter a short working name for this new\n'
				u'episode under the existing health issue\n'
				u'\n'
				u'"%s":\n'
			) % issue['description']

		dlg = wx.TextEntryDialog (
			parent = self,
			message = msg,
			caption = _('Creating problem (episode) to save notelet under ...'),
			defaultValue = epi_name,
			style = wx.OK | wx.CANCEL | wx.CENTRE
		)
		decision = dlg.ShowModal()
		if decision != wx.ID_OK:
			return None

		epi_name = dlg.GetValue().strip()
		if epi_name == u'':
			gmGuiHelpers.gm_show_error(_('Cannot save a new problem without a name.'), _('saving progress note'))
			return None

		# create episode
		new_episode = emr.add_episode (
			episode_name = epi_name[:45],
			pk_health_issue = None,
			is_open = True,
			allow_dupes = True		# this ensures we get a new episode even if a same-name one already exists
		)
		new_episode['summary'] = self._TCTRL_episode_summary.GetValue().strip()
		new_episode.save()

		if self.problem is not None:
			issue = emr.problem2issue(self.problem)
			if not gmEMRStructWidgets.move_episode_to_issue(episode = new_episode, target_issue = issue, save_to_backend = True):
				gmGuiHelpers.gm_show_warning (
					_(
						'The new episode:\n'
						'\n'
						' "%s"\n'
						'\n'
						'will remain unassociated despite the editor\n'
						'having been invoked from the health issue:\n'
						'\n'
						' "%s"'
					) % (
						new_episode['description'],
						issue['description']
					),
					_('saving progress note')
				)

		return new_episode
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		for field in self.soap_fields:
			self.bind_expando_layout_event(field)
		self.bind_expando_layout_event(self._TCTRL_episode_summary)
		gmDispatcher.connect(signal = u'blobs.doc_obj_mod_db', receiver = self.refresh_visual_soap)

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_soap(self):

		soap = {}

		tmp = self._TCTRL_Soap.GetValue().strip()
		if tmp != u'':
			soap['s'] = [tmp]

		tmp = self._TCTRL_sOap.GetValue().strip()
		if tmp != u'':
			soap['o'] = [tmp]

		tmp = self._TCTRL_soAp.GetValue().strip()
		if tmp != u'':
			soap['a'] = [tmp]

		tmp = self._TCTRL_soaP.GetValue().strip()
		if tmp != u'':
			soap['p'] = [tmp]

		return soap

	soap = property(_get_soap, lambda x:x)
	#--------------------------------------------------------
	def _get_empty(self):

		# soap fields
		for field in self.soap_fields:
			if field.GetValue().strip() != u'':
				return False

		# summary
		summary = self._TCTRL_episode_summary.GetValue().strip()
		if self.problem is None:
			if summary != u'':
				return False
		elif self.problem['type'] == u'issue':
			if summary != u'':
				return False
		else:
			if self.problem['summary'] is None:
				if summary != u'':
					return False
			else:
				if summary != self.problem['summary'].strip():
					return False

		# codes
		new_codes = self._PRW_episode_codes.GetData()
		if self.problem is None:
			if len(new_codes) > 0:
				return False
		elif self.problem['type'] == u'issue':
			if len(new_codes) > 0:
				return False
		else:
			old_code_pks = self.problem.generic_codes
			if len(old_code_pks) != len(new_codes):
				return False
			for code in new_codes:
				if code['data'] not in old_code_pks:
					return False

		return True

	empty = property(_get_empty, lambda x:x)

#============================================================
# main
#---------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != u'test':
		sys.exit()

	#----------------------------------------
	def test_cSoapNoteExpandoEAPnl():
		pat = gmPersonSearch.ask_for_patient()
		application = wx.PyWidgetTester(size=(800,500))
		soap_input = cSoapNoteExpandoEAPnl(application.frame, -1)
		application.frame.Show(True)
		application.MainLoop()
	#----------------------------------------

	test_cSoapNoteExpandoEAPnl()
