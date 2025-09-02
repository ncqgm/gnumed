"""GNUmed coding related widgets."""
#================================================================
__author__ = 'karsten.hilbert@gmx.net'
__license__ = 'GPL v2 or later (details at https://www.gnu.org)'

# stdlib
import logging, sys


# 3rd party
import wx


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x

from Gnumed.business import gmCoding

from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmMatchProvider

from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmPhraseWheel


_log = logging.getLogger('gm.ui')

#================================================================
def browse_data_sources(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	#------------------------------------------------------------
	def refresh(lctrl):
		srcs = gmCoding.get_data_sources()
		items = [ [
			'%s (%s): %s' % (
				s['name_short'],
				gmTools.coalesce(s['lang'], '?'),
				s['version']
			),
			s['name_long'].split('\n')[0].split('\r')[0],
			s['source'].split('\n')[0].split('\r')[0],
			gmTools.coalesce(s['description'], '').split('\n')[0].split('\r')[0],
			s['pk']
		] for s in srcs ]
		lctrl.set_string_items(items)
		lctrl.set_data(srcs)
	#------------------------------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('Sources of reference data registered in GNUmed.'),
		caption = _('Showing data sources'),
		columns = [ _('System'), _('Name'), _('Source'), _('Description'), '#' ],
		single_selection = True,
		can_return_empty = False,
		ignore_OK_button = True,
		refresh_callback = refresh
#		edit_callback=None,
#		new_callback=None,
#		delete_callback=None,
#		left_extra_button=None,
#		middle_extra_button=None,
#		right_extra_button=None
	)

#----------------------------------------------------------------
class cDataSourcePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)

		query = """
			SELECT DISTINCT ON (list_label)
				pk
					AS data,
				name_short || ' (' || version || ')'
					AS field_label,
				name_short || ' ' || version || ' (' || name_long || ')'
					AS list_label
			FROM
				ref.data_source
			WHERE
				name_short %(fragment_condition)s
					OR
				name_long %(fragment_condition)s
			ORDER BY list_label
			LIMIT 50
		"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries = query)
		mp.setThresholds(1, 2, 4)
#		mp.word_separators = '[ \t=+&:@]+'
		self.SetToolTip(_('Select a data source / coding system.'))
		self.matcher = mp
		self.selection_only = True

#================================================================
def browse_coded_terms(parent=None, coding_systems=None, languages=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	#------------------------------------------------------------
	def refresh(lctrl):
		coded_terms = gmCoding.get_coded_terms (
			coding_systems = coding_systems,
			languages = languages,
			order_by = 'term, coding_system, code'
		)
		items = [ [
			ct['term'],
			ct['code'],
			ct['coding_system'],
			gmTools.coalesce(ct['lang'], ''),
			ct['version'],
			ct['coding_system_long']
		] for ct in coded_terms ]
		lctrl.set_string_items(items)
		lctrl.set_data(coded_terms)
	#------------------------------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('Coded terms known to GNUmed (may take a while to load).'),
		caption = _('Showing coded terms.'),
		columns = [ _('Term'), _('Code'), _('System'), _('Language'), _('Version'), _('Coding system details') ],
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

		query = """
			SELECT
				-- DISTINCT ON (list_label)
				data,
				list_label,
				field_label
			FROM (

				SELECT
					pk_generic_code
						AS data,
					(code || ' (' || coding_system || '): ' || term || ' (' || version || coalesce(' - ' || lang, '') || ')')
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
				'where_part': 'AND coding_system IN %(system)s',
				'placeholder': 'system'
			},
			'ctxt_lang': {
				'where_part': 'AND lang = %(lang)s',
				'placeholder': 'lang'
			}
		}

		mp = gmMatchProvider.cMatchProvider_SQL2(queries = query, context = ctxt)
		mp.setThresholds(2, 4, 5)
		mp.word_separators = '[ \t=+&/:-]+'
		#mp.print_queries = True

		self.phrase_separators = ';'
		self.selection_only = False			# not sure yet how this fares with multi-phrase input
		self.SetToolTip(_('Select one or more codes that apply.'))
		self.matcher = mp

		self.add_callback_on_lose_focus(callback = self.__on_losing_focus)
	#------------------------------------------------------------
	def __on_losing_focus(self):
		self._adjust_data_after_text_update()
		if self.GetValue().strip() == '':
			return

		if len(self.data) != len(self.displayed_strings):
			self.display_as_valid(valid = None)
			return

		self.display_as_valid(valid = True)
	#------------------------------------------------------------
	def _get_data_tooltip(self):
		if len(self.data) == 0:
			return ''

		return ';\n'.join([ i['list_label'] for i in self.data.values() ]) + ';'
	#------------------------------------------------------------
	def generic_linked_codes2item_dict(self, codes):
		if len(codes) == 0:
			return '', {}

		code_dict = {}
		val = ''
		for code in codes:
			list_label = '%s (%s): %s (%s - %s)' % (
				code['code'],
				code['name_short'],
				code['term'],
				code['version'],
				code['lang']
			)
			field_label = code['code']
			code_dict[field_label] = {'data': code['pk_generic_code'], 'field_label': field_label, 'list_label': list_label}
			val += '%s; ' % field_label

		return val.strip(), code_dict
#================================================================
# main
#----------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmPG2

	#--------------------------------------------------------
	def test_generic_codes_prw():
		gmPG2.get_connection()
#		app = wx.PyWidgetTester(size = (500, 40))
		#pw = cGenericCodesPhraseWheel(app.frame, -1)
		#pw.set_context(context = u'zip', val = u'04318')
#		app.frame.Show(True)
#		app.MainLoop()
	#--------------------------------------------------------
	test_generic_codes_prw()

#================================================================
