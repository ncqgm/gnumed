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

class cCodePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)

		query = u"""
		"""

		mp = gmMatchProvider.cMatchProvider_SQL2(queries = query)
		mp.setThresholds(2, 3, 4)

		mp.word_separators = '[ \t=+&/:-]+'
		self.phrase_separators = ';'
		self.selection_only = False			# not sure yet how this fares with multi-phrase input
		self.SetToolTipString(_('Select one or more codes that apply.'))
		self.matcher = mp


#================================================================
# main
#----------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

#	from Gnumed.pycommon import gmI18N
#	gmI18N.activate_locale()
#	gmI18N.install_domain()

#================================================================
