"""GNUmed coding related widgets."""
#================================================================
__version__ = '$Revision: 1.4 $'
__author__ = 'karsten.hilbert@gmx.net'
__license__ = 'GPL (details at http://www.gnu.org)'

# stdlib
import logging, sys


# 3rd party
import wx


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')

from Gnumed.business import gmCoding
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmMatchProvider
from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmPhraseWheel


_log = logging.getLogger('gm.ui')
_log.info(__version__)

#================================================================
def browse_coded_terms(parent=None, coding_systems=None, languages=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	#------------------------------------------------------------
	def refresh(lctrl):
		coded_terms = gmCoding.get_coded_terms (
			coding_systems = coding_systems,
			languages = languages,
			order_by = u'term, coding_system, code'
		)
		items = [ [
			ct['term'],
			ct['code'],
			ct['coding_system'],
			gmTools.coalesce(ct['lang'], u''),
			ct['version'],
			ct['coding_system_long']
		] for ct in coded_terms ]
		lctrl.set_string_items(items)
		lctrl.set_data(coded_terms)
	#------------------------------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('Coded terms known to GNUmed.'),
		caption = _('Showing coded terms.'),
		columns = [ _('Term'), _('Code'), _('System'), _('Language'), _('Version'), _(u'Coding system details') ],
		single_selection = True,
		can_return_empty = True,
		ignore_OK_button = True,
		refresh_callback = refresh
#		edit_callback=None,
#		new_callback=None,
#		delete_callback=None,
#		left_extra_button=None,
#		middle_extra_button=None,
#		right_extra_button=None
	)

#================================================================

class cGenericCodesPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)

		query = u"""
			SELECT
				-- DISTINCT ON (list_label)
				data,
				list_label,
				field_label
			FROM (

				SELECT
					code AS data,
					(code || ' (' || lang || ' - ' || coding_system || ' - ' || version || '): ' || term) AS list_label,
					code AS field_label
				FROM
					ref.v_coded_terms
				WHERE
					term %(fragment_condition)s
					%(ctxt_system)s
					%(ctxt_lang)s

				UNION ALL

				SELECT
					code AS data,
					(code || ' (' || lang || ' - ' || coding_system || ' - ' || version || '): ' || term) AS list_label,
					code AS field_label
				FROM
					ref.v_coded_terms
				WHERE
					code %(fragment_condition)s
					%(ctxt_system)s
					%(ctxt_lang)s

			) AS applicable_codes
			ORDER BY list_label
			LIMIT 35
		"""
		ctxt = {
			'ctxt_system': {				# must be a TUPLE !
				'where_part': u'AND coding_system IN %(system)s',
				'placeholder': u'system'
			},
			'ctxt_lang': {
				'where_part': u'AND lang = %(lang)s',
				'placeholder': u'lang'
			}
		}

		mp = gmMatchProvider.cMatchProvider_SQL2(queries = query, context = ctxt)
		mp.setThresholds(2, 4, 5)
		mp.word_separators = '[ \t=+&/:-]+'
		#mp.print_queries = True

		self.phrase_separators = ';'
		self.selection_only = False			# not sure yet how this fares with multi-phrase input
		self.SetToolTipString(_('Select one or more codes that apply.'))
		self.matcher = mp
	#--------------------------------------------------------
	def _picklist_selection2display_string(self):
		return self._picklist.GetSelectedItemData()

#================================================================
# main
#----------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()
	from Gnumed.pycommon import gmPG2

	#--------------------------------------------------------
	def test_generic_codes_prw():
		gmPG2.get_connection()
		app = wx.PyWidgetTester(size = (200, 50))
		pw = cGenericCodesPhraseWheel(app.frame, -1)
		#pw.set_context(context = u'zip', val = u'04318')
		print pw.data
		app.frame.Show(True)
		app.MainLoop()
	#--------------------------------------------------------
	test_generic_codes_prw()

#================================================================
