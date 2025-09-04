# -*- coding: utf-8 -*-
"""GNUmed expando based textual progress notes handling widgets."""
#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later (details at https://www.gnu.org)"

import sys
import logging


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x

from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmCfgDB

from Gnumed.business import gmPerson
from Gnumed.business import gmPraxis
from Gnumed.business import gmHealthIssue
from Gnumed.business import gmClinNarrative
from Gnumed.business import gmEpisode

from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmTextCtrl
from Gnumed.wxpython import gmVisualProgressNoteWidgets
from Gnumed.wxpython import gmEMRStructWidgets

_log = logging.getLogger('gm.ui')

#============================================================
from Gnumed.wxGladeWidgets import wxgProgressNotesEAPnl

class cProgressNotesEAPnl(gmTextCtrl.cExpandoTextCtrlHandling_PanelMixin, wxgProgressNotesEAPnl.wxgProgressNotesEAPnl):
	"""An Edit Area like panel for entering progress notes.

	(
		Subjective:					Codes:
			expando text ctrl
		Objective:					Codes:
			expando text ctrl
		Assessment:					Codes:
			expando text ctrl
		Plan:						Codes:
			expando text ctrl
	)
		OR
	SOAP editor (StyledTextCtrl)
		AND
	visual progress notes (panel with images)
		AND
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

		wxgProgressNotesEAPnl.wxgProgressNotesEAPnl.__init__(self, *args, **kwargs)

		self.__use_soap_fields = gmCfgDB.get4user (
			option = 'horstspace.soap_editor.use_one_field_per_soap_category',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			default = True
		)

		self.__soap_fields = [
			self._TCTRL_Soap,
			self._TCTRL_sOap,
			self._TCTRL_soAp,
			self._TCTRL_soaP
		]

		self.__init_ui()
		self.__register_interests()

		return

	#--------------------------------------------------------
	def __init_ui(self):
		if self.__use_soap_fields is False:
			for field in self.__soap_fields:
				field.Hide()
			self._LBL_Soap.Hide()
			self._PRW_Soap_codes.Hide()
			self._LBL_sOap.Hide()
			self._PRW_sOap_codes.Hide()
			self._LBL_soAp.Hide()
			self._PRW_soAp_codes.Hide()
			self._LBL_soaP.Hide()
			self._PRW_soaP_codes.Hide()
			self._STC_soap.Show()

		self.refresh_summary()
		if self.problem is not None:
			if self.problem['summary'] is None:
				self._TCTRL_episode_summary.SetValue('')
		self.refresh_visual_soap()

	#--------------------------------------------------------
	def refresh(self):
		self.refresh_summary()
		self.refresh_visual_soap()

	#--------------------------------------------------------
	def refresh_summary(self):
		self._TCTRL_episode_summary.SetValue('')
		self._PRW_episode_codes.SetText('', self._PRW_episode_codes.list2data_dict([]))
		self._LBL_summary.SetLabel(_('Episode synopsis'))

		# new problem ?
		if self.problem is None:
			return

		# issue-level problem ?
		if self.problem['type'] == 'issue':
			return

		# episode-level problem
		caption = _('Synopsis (%s)') % self.problem['modified_when'].strftime('%B %Y')
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

		if self.problem['type'] == 'issue':
			self._PNL_visual_soap.refresh(document_folder = None)
			return

		if self.problem['type'] == 'episode':
			pat = gmPerson.gmCurrentPatient()
			doc_folder = pat.get_document_folder()
			emr = pat.emr
			self._PNL_visual_soap.refresh (
				document_folder = doc_folder,
				episodes = [self.problem['pk_episode']],
				encounter = emr.active_encounter['pk_encounter']
			)
			return

	#--------------------------------------------------------
	def clear(self):
		self._TCTRL_episode_summary.SetValue('')
		self._LBL_summary.SetLabel(_('Episode synopsis'))
		self._PRW_episode_codes.SetText('', self._PRW_episode_codes.list2data_dict([]))
		self._PNL_visual_soap.clear()

		if self.__use_soap_fields:
			for field in self.__soap_fields:
				field.SetValue('')
		else:
			self._STC_soap.SetText_from_SOAP()

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
			episode = gmEpisode.cEpisode.from_problem(self.problem)

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
			episode = gmEpisode.cEpisode.from_problem(self.problem)

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

		gmClinNarrative.create_progress_note (
			soap = self.soap,
			episode_id = episode['pk_episode'],
			encounter_id = encounter
		)

		return True

	#--------------------------------------------------------
	# internal helpers
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
				'Enter a short working name for this new problem\n'
				'(which will become a new, unassociated episode):\n'
			)
		else:
			issue = gmHealthIssue.cHealthIssue.from_problem(self.problem)
			msg = _(
				'Enter a short working name for this new\n'
				'episode under the existing health issue\n'
				'\n'
				'"%s":\n'
			) % issue['description']

		dlg = wx.TextEntryDialog (
			self, msg,
			caption = _('Creating problem (episode) to save notelet under ...'),
			value = epi_name,
			style = wx.OK | wx.CANCEL | wx.CENTRE
		)
		decision = dlg.ShowModal()
		if decision != wx.ID_OK:
			return None

		epi_name = dlg.GetValue().strip()
		if epi_name == '':
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
			issue = gmHealthIssue.cHealthIssue.from_problem(self.problem)
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
		if self.__use_soap_fields:
			for field in self.__soap_fields:
				self.bind_expando_layout_event(field)
		self.bind_expando_layout_event(self._TCTRL_episode_summary)
		gmDispatcher.connect(signal = 'blobs.doc_obj_mod_db', receiver = self.refresh_visual_soap)

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_soap(self):
		if not self.__use_soap_fields:
			return self._STC_soap.soap

		soap = {}
		tmp = self._TCTRL_Soap.GetValue().strip()
		if tmp != '':
			soap['s'] = [tmp]
		tmp = self._TCTRL_sOap.GetValue().strip()
		if tmp != '':
			soap['o'] = [tmp]
		tmp = self._TCTRL_soAp.GetValue().strip()
		if tmp != '':
			soap['a'] = [tmp]
		tmp = self._TCTRL_soaP.GetValue().strip()
		if tmp != '':
			soap['p'] = [tmp]
		return soap

	soap = property(_get_soap)
	#--------------------------------------------------------
	def _get_empty(self):
		if self.__use_soap_fields:
			for field in self.__soap_fields:
				if field.GetValue().strip() != '':
					return False
		else:
			if not self._STC_soap.empty:
				return False

		# summary
		summary = self._TCTRL_episode_summary.GetValue().strip()
		if self.problem is None:
			if summary != '':
				return False
		elif self.problem['type'] == 'issue':
			if summary != '':
				return False
		else:
			if self.problem['summary'] is None:
				if summary != '':
					return False
			else:
				if summary != self.problem['summary'].strip():
					return False

		# codes
		new_codes = self._PRW_episode_codes.GetData()
		if self.problem is None:
			if len(new_codes) > 0:
				return False
		elif self.problem['type'] == 'issue':
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

	empty = property(_get_empty)

#============================================================
# main
#---------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

#	from Gnumed.business import gmPersonSearch

	#----------------------------------------
#	def test_cProgressNotesEAPnl():
#		gmPersonSearch.ask_for_patient()
#		application = wx.PyWidgetTester(size=(800,500))
#		#soap_input = cProgressNotesEAPnl(application.frame, -1)
#		application.frame.Show(True)
#		application.MainLoop()
	#----------------------------------------

#	test_cProgressNotesEAPnl()
