# -*- coding: utf-8 -*-

"""GNUmed ATC handling widgets."""

#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"

import logging
import sys


import wx

if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmMatchProvider
from Gnumed.pycommon import gmDispatcher

from Gnumed.business import gmATC

from Gnumed.wxpython import gmAuthWidgets
from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmPhraseWheel


_log = logging.getLogger('gm.ui.atc')

#============================================================
def browse_atc_reference_deprecated(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	#------------------------------------------------------------
	def refresh(lctrl):
		atcs = gmATC.get_reference_atcs()

		items = [ [
			a['atc'],
			a['term'],
			gmTools.coalesce(a['unit'], ''),
			gmTools.coalesce(a['administrative_route'], ''),
			gmTools.coalesce(a['comment'], ''),
			a['version'],
			a['lang']
		] for a in atcs ]
		lctrl.set_string_items(items)
		lctrl.set_data(atcs)
	#------------------------------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('\nThe ATC codes as known to GNUmed.\n'),
		caption = _('Showing ATC codes.'),
		columns = [ 'ATC', _('Term'), _('Unit'), _('Route'), _('Comment'), _('Version'), _('Language') ],
		single_selection = True,
		refresh_callback = refresh
	)

#============================================================
def update_atc_reference_data():

	dlg = wx.FileDialog (
		parent = None,
		message = _('Choose an ATC import config file'),
		defaultDir = gmTools.gmPaths().user_work_dir,
		defaultFile = '',
		wildcard = "%s (*.conf)|*.conf|%s (*)|*" % (_('config files'), _('all files')),
		style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
	)

	result = dlg.ShowModal()
	if result == wx.ID_CANCEL:
		return

	cfg_file = dlg.GetPath()
	dlg.DestroyLater()

	conn = gmAuthWidgets.get_dbowner_connection(procedure = _('importing ATC reference data'))
	if conn is None:
		return False

	wx.BeginBusyCursor()

	if gmATC.atc_import(cfg_fname = cfg_file, conn = conn):
		gmDispatcher.send(signal = 'statustext', msg = _('Successfully imported ATC reference data.'))
	else:
		gmDispatcher.send(signal = 'statustext', msg = _('Importing ATC reference data failed.'), beep = True)

	wx.EndBusyCursor()
	return True

#============================================================
class cATCPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		query = """
			SELECT DISTINCT ON (data)
				data,
				field_label,
				list_label
			FROM (
				(
					SELECT
						code AS data,
						(code || ': ' || term)
							AS list_label,
						(code || ' (' || term || ')')
							AS field_label
					FROM ref.atc
					WHERE
						term %(fragment_condition)s
							OR
						code %(fragment_condition)s
				) UNION ALL (
					SELECT
						atc as data,
						(atc || ': ' || description)
							AS list_label,
						(atc || ' (' || description || ')')
							AS field_label
					FROM ref.substance
					WHERE
						description %(fragment_condition)s
							OR
						atc %(fragment_condition)s
				) UNION ALL (
					SELECT
						atc_code AS data,
						(atc_code || ': ' || description || ' (' || preparation || ')')
							AS list_label,
						(atc_code || ': ' || description)
							AS field_label
					FROM ref.drug_product
					WHERE
						description %(fragment_condition)s
							OR
						atc_code %(fragment_condition)s
				)
				-- it would be nice to be able to include ref.vacc_indication but that's hard to do in SQL
			) AS candidates
			WHERE data IS NOT NULL
			ORDER BY data, list_label
			LIMIT 50"""

		mp = gmMatchProvider.cMatchProvider_SQL2(queries = query)
		mp.setThresholds(1, 2, 4)
#		mp.word_separators = '[ \t=+&:@]+'
		self.SetToolTip(_('Select an ATC (Anatomical-Therapeutic-Chemical) code.'))
		self.matcher = mp
		self.selection_only = True

#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmPG2

	#----------------------------------------
	gmPG2.get_connection()
	app = wx.PyWidgetTester(size = (600, 80))
	app.SetWidget(cATCPhraseWheel, -1)
	app.MainLoop()
