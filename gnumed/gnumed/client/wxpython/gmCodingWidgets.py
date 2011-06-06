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

class cGenericCodesPhraseWheel(gmPhraseWheel.cMultiPhraseWheel):

	def __init__(self, *args, **kwargs):

		super(cGenericCodesPhraseWheel, self).__init__(*args, **kwargs)

		query = u"""
			SELECT
				-- DISTINCT ON (list_label)
				data,
				list_label,
				field_label
			FROM (

				SELECT
					pk_generic_code
						AS data,
					(code || ' (' || coding_system || '): ' || term || ' (' || version || ' - ' || lang || ')')
						AS list_label,
					code AS
						field_label
				FROM
					ref.v_coded_terms
				WHERE
					term %(fragment_condition)s
						OR
					code %(fragment_condition)s
					%(ctxt_system)s
					%(ctxt_lang)s

			) AS applicable_codes
			ORDER BY list_label
			LIMIT 30
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
	#------------------------------------------------------------
	def _get_data_tooltip(self):
		if len(self.data) == 0:
			return u''

		return u';\n'.join([ i['list_label'] for i in self.data.values() ]) + u';'
	#------------------------------------------------------------
	def generic_linked_codes2item_dict(self, codes):
		if len(codes) == 0:
			return u'', {}

		code_dict = {}
		val = u''
		for code in codes:
			list_label = u'%s (%s): %s (%s - %s)' % (
				code['code'],
				code['name_short'],
				code['term'],
				code['version'],
				code['lang']
			)
			field_label = code['code']
			code_dict[field_label] = {'data': code['pk_generic_code'], 'field_label': field_label, 'list_label': list_label}
			val += u'%s; ' % field_label

		return val.strip(), code_dict
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
		app = wx.PyWidgetTester(size = (500, 40))
		pw = cGenericCodesPhraseWheel(app.frame, -1)
		#pw.set_context(context = u'zip', val = u'04318')
		app.frame.Show(True)
		app.MainLoop()
	#--------------------------------------------------------
	test_generic_codes_prw()

#================================================================
