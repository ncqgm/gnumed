"""GNUmed narrative handling widgets.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmNarrativeWidgets.py,v $
# $Id: gmNarrativeWidgets.py,v 1.1 2007-08-29 22:06:15 ncq Exp $
__version__ = "$Revision: 1.1 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

import sys


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmLog, gmI18N, gmDispatcher
from Gnumed.business import gmPerson, gmEMRStructItems
from Gnumed.wxpython import gmListWidgets, gmEMRStructWidgets
#gmGuiHelpers, gmMacro
from Gnumed.wxGladeWidgets import wxgMoveNarrativeDlg


_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

#============================================================
# narrative related widgets/functions
#------------------------------------------------------------
def select_narrative_from_episodes():

	pat = gmPerson.gmCurrentPatient()
	emr = pat.get_emr()

	selected_soap = []

	while 1:
		# 1) select health issues to select episodes from
		all_issues = emr.get_health_issues()
		dlg = gmEMRStructWidgets.cIssueListSelectorDlg(parent = None, id = -1, issues = all_issues)
		btn_pressed = dlg.ShowModal()
		selected_issues = dlg.get_selected_item_data()
		dlg.Destroy()

		if btn_pressed == wx.ID_CANCEL:
			return selected_soap

		# 2) select episodes to select items from
		issue_pks = [ i['pk'] for i in selected_issues ].append(None)
		all_epis = emr.get_episodes(issues = issue_pks)
		if len(all_epis) == 0:
			continue

		dlg = cEpisodeListSelectorDlg(parent = None, id = -1, episodes = all_epis)
		btn_pressed = dlg.ShowModal()
		selected_epis = dlg.get_selected_item_data()
		dlg.Destroy()

		if btn_pressed == wx.ID_CANCEL:
			continue

		# 3) select narrative corresponding to the above constraints
		epi_pks = [ epi['pk_episode'] for epi in selected_epis ]
		all_narr = emr.get_clin_narrative(episodes = epi_pks)
		if len(all_narr) == 0:
			continue

		dlg = cNarrativeListSelectorDlg(parent = None, id = -1, narrative = all_narr)
		btn_pressed = dlg.ShowModal()
		selected_narr = dlg.get_selected_item_data()
		dlg.Destroy()

		if btn_pressed == wx.ID_CANCEL:
			continue

		selected_soap.extend(selected_narr)
#------------------------------------------------------------
class cNarrativeListSelectorDlg(gmListWidgets.cGenericListSelectorDlg):

	# FIXME: support pre-selection

	def __init__(self, *args, **kwargs):

		narrative = kwargs['narrative']
		del kwargs['narrative']

		gmListWidgets.cGenericListSelectorDlg.__init__(self, *args, **kwargs)

		self.SetTitle(_('Select the narrative you are interested in ...'))
		# FIXME: add epi/issue
		self._LCTRL_items.set_columns([_('when'), _('who'), _('type'), _('entry')]) #, _('Episode'), u'', _('Health Issue')])
		# FIXME: date used should be date of encounter, not date_modified
		# FIXME: translate/sort by soap_cat
		self._LCTRL_items.set_string_items (
			items = [ [narr['date'].strftime('%Y-%m-%d %H:%M'), narr['provider'], narr['soap_cat'], narr['narrative'].replace('\n', '/').replace('\r', '/')] for narr in narrative ]
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
		app = wx.PyWidgetTester(size = (200, 50))
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
# Revision 1.1  2007-08-29 22:06:15  ncq
# - factored out narrative widgets
#
#
