"""GNUmed narrative handling widgets.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmNarrativeWidgets.py,v $
# $Id: gmNarrativeWidgets.py,v 1.3 2007-09-07 22:45:58 ncq Exp $
__version__ = "$Revision: 1.3 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

import sys


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmLog, gmI18N, gmDispatcher
from Gnumed.business import gmPerson, gmEMRStructItems, gmClinNarrative
from Gnumed.wxpython import gmListWidgets, gmEMRStructWidgets
#gmGuiHelpers, gmMacro
from Gnumed.wxGladeWidgets import wxgMoveNarrativeDlg


_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
#============================================================
# narrative related widgets/functions
#------------------------------------------------------------
def select_narrative_from_episodes(parent = None):

	pat = gmPerson.gmCurrentPatient()
	emr = pat.get_emr()

	selected_soap = {}
	selected_issue_pks = []
	selected_episode_pks = []
	selected_narrative_pks = []

	while 1:
		# 1) select health issues to select episodes from
		all_issues = emr.get_health_issues()
		all_issues.insert(0, gmEMRStructItems.get_dummy_health_issue())
		dlg = gmEMRStructWidgets.cIssueListSelectorDlg (
			parent = parent,
			id = -1,
			issues = all_issues,
			msg = _('\n In the list below mark the health issues you want to report on.\n')
		)
		selection_idxs = []
		for idx in range(len(all_issues)):
			if all_issues[idx]['pk'] in selected_issue_pks:
				selection_idxs.append(idx)
		if len(selection_idxs) != 0:
			dlg.set_selections(selections = selection_idxs)
		btn_pressed = dlg.ShowModal()
		selected_issues = dlg.get_selected_item_data()
		dlg.Destroy()

		if btn_pressed == wx.ID_CANCEL:
			return selected_soap.values()

		selected_issue_pks = [ i['pk'] for i in selected_issues ]

		while 1:
			# 2) select episodes to select items from
			all_epis = emr.get_episodes(issues = selected_issue_pks)

			if len(all_epis) == 0:
				gmDispatcher.send(signal = 'statustext', msg = _('No episodes recorded for the health issues selected.'))
				break

			dlg = gmEMRStructWidgets.cEpisodeListSelectorDlg (
				parent = parent,
				id = -1,
				episodes = all_epis,
				msg = _(
					'\n These are the episodes known for the health issues just selected.\n\n'
					' Now, mark the the episodes you want to report on.\n'
				)
			)
			selection_idxs = []
			for idx in range(len(all_epis)):
				if all_epis[idx]['pk_episode'] in selected_episode_pks:
					selection_idxs.append(idx)
			if len(selection_idxs) != 0:
				dlg.set_selections(selections = selection_idxs)
			btn_pressed = dlg.ShowModal()
			selected_epis = dlg.get_selected_item_data()
			dlg.Destroy()

			if btn_pressed == wx.ID_CANCEL:
				break

			selected_episode_pks = [ i['pk_episode'] for i in selected_epis ]

			# 3) select narrative corresponding to the above constraints
			all_narr = emr.get_clin_narrative(episodes = selected_episode_pks)

			if len(all_narr) == 0:
				gmDispatcher.send(signal = 'statustext', msg = _('No narrative available for selected episodes.'))
				continue

			dlg = cNarrativeListSelectorDlg (
				parent = parent,
				id = -1,
				narrative = all_narr,
				msg = _(
					'\n This is the clinical narrative for the chosen episodes.\n\n'
					' Now, mark the entries you want to include in your report.\n'
				)
			)
			selection_idxs = []
			for idx in range(len(all_narr)):
				if all_narr[idx]['pk_narrative'] in selected_narrative_pks:
					selection_idxs.append(idx)
			if len(selection_idxs) != 0:
				dlg.set_selections(selections = selection_idxs)
			btn_pressed = dlg.ShowModal()
			selected_narr = dlg.get_selected_item_data()
			dlg.Destroy()

			if btn_pressed == wx.ID_CANCEL:
				continue

			selected_narrative_pks = [ i['pk_narrative'] for i in selected_narr ]
			for narr in selected_narr:
				selected_soap[narr['pk_narrative']] = narr
#------------------------------------------------------------
class cNarrativeListSelectorDlg(gmListWidgets.cGenericListSelectorDlg):

	def __init__(self, *args, **kwargs):

		narrative = kwargs['narrative']
		del kwargs['narrative']

		gmListWidgets.cGenericListSelectorDlg.__init__(self, *args, **kwargs)

		self.SetTitle(_('Select the narrative you are interested in ...'))
		# FIXME: add epi/issue
		self._LCTRL_items.set_columns([_('when'), _('who'), _('type'), _('entry')]) #, _('Episode'), u'', _('Health Issue')])
		# FIXME: date used should be date of encounter, not date_modified
		self._LCTRL_items.set_string_items (
			items = [ [narr['date'].strftime('%Y-%m-%d %H:%M'), narr['provider'], gmClinNarrative.soap_cat2l10n[narr['soap_cat']], narr['narrative'].replace('\n', '/').replace('\r', '/')] for narr in narrative ]
		)
		self._LCTRL_items.set_column_widths()
		self._LCTRL_items.set_data(data = narrative)
#------------------------------------------------------------
class cMoveNarrativeDlg(wxgMoveNarrativeDlg.wxgMoveNarrativeDlg):

	def __init__(self, *args, **kwargs):

		self.encounter = kwargs['encounter']
		self.source_episode = kwargs['episode']
		del kwargs['encounter']
		del kwargs['episode']

		wxgMoveNarrativeDlg.wxgMoveNarrativeDlg.__init__(self, *args, **kwargs)

		self.LBL_source_episode.SetLabel(u'%s%s' % (self.source_episode['description'], gmTools.coalesce(self.source_episode['health_issue'], u'', u' (%s)')))
		self.LBL_encounter.SetLabel('%s: %s %s - %s' % (
			self.encounter['started'].strftime('%x').decode(gmI18N.get_encoding()),
			self.encounter['l10n_type'],
			self.encounter['started'].strftime('%H:%M'),
			self.encounter['last_affirmed'].strftime('%H:%M')
		))
		pat = gmPerson.gmCurrentPatient()
		emr = pat.get_emr()
		narr = emr.get_clin_narrative(episodes=[self.source_episode['pk_episode']], encounters=[self.encounter['pk_encounter']])
		if len(narr) == 0:
			narr = [{'narrative': _('There is no narrative for this episode in this encounter.')}]
		self.LBL_narrative.SetLabel(u'\n'.join([n['narrative'] for n in narr]))

	#------------------------------------------------------------
	def _on_move_button_pressed(self, event):

		target_episode = self._PRW_episode_selector.GetData(can_create = False)

		if target_episode is None:
			gmDispatcher.send(signal='statustext', msg=_('Must select episode to move narrative to first.'))
			# FIXME: set to pink
			self._PRW_episode_selector.SetFocus()
			return False

		target_episode = gmEMRStructItems.cEpisode(aPK_obj=target_episode)

		self.encounter.transfer_clinical_data (
			source_episode = self.source_episode,
			target_episode = target_episode
		)

		if self.IsModal():
			self.EndModal(wx.ID_OK)
		else:
			self.Close()

#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)
	gmI18N.activate_locale()
	gmI18N.install_domain(domain = 'gnumed')

	#----------------------------------------
	def test_select_narrative_from_episodes():
		pat = gmPerson.ask_for_patient()
		gmPerson.set_active_patient(patient = pat)
		app = wx.PyWidgetTester(size = (200, 200))
		sels = select_narrative_from_episodes()
		print "selected:"
		for sel in sels:
			print sel
	#----------------------------------------
#	def test_cFormTemplateEditAreaPnl():
#		app = wx.PyWidgetTester(size = (400, 300))
#		pnl = cFormTemplateEditAreaPnl(app.frame, -1, template = gmForms.cFormTemplate(aPK_obj=4))
#		app.frame.Show(True)
#		app.MainLoop()
#		return
	#----------------------------------------
	if (len(sys.argv) > 1) and (sys.argv[1] == 'test'):
		test_select_narrative_from_episodes()

#============================================================
# $Log: gmNarrativeWidgets.py,v $
# Revision 1.3  2007-09-07 22:45:58  ncq
# - much improved select_narrative_from_episodes()
#
# Revision 1.2  2007/09/07 10:59:17  ncq
# - greatly improve select_narrative_by_episodes
#   - remember selections
#   - properly levelled looping
# - fix test suite
#
# Revision 1.1  2007/08/29 22:06:15  ncq
# - factored out narrative widgets
#
#
