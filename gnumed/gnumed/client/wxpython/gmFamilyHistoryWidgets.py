"""GNUmed family history related widgets."""
#================================================================
__author__ = 'karsten.hilbert@gmx.net'
__license__ = 'GPL v2 or later (details at http://www.gnu.org)'

# stdlib
import logging, sys


# 3rd party
import wx


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime
from Gnumed.business import gmPerson
from Gnumed.wxpython import gmListWidgets


_log = logging.getLogger('gm.ui')

#================================================================
def manage_family_history(parent=None):

	pat = gmPerson.gmCurrentPatient()
	emr = pat.get_emr()

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#------------------------------------------------------------
	def refresh(lctrl):
		fhx = emr.get_family_history()
		items = [ [
			f['l10n_relation'],
			f['condition'],
			gmTools.bool2subst(f['contributed_to_death'], _('yes'), _('no'), u'?'),
			gmTools.coalesce(f['age_noted'], u''),
			gmDateTime.format_interval (
				interval = f['age_of_death'],
				accuracy_wanted = gmDateTime.acc_years,
				none_string = u''
			),
			gmTools.coalesce(f['name_relative'], u''),
			gmTools.coalesce(f['dob_relative'], u'', function_initial = ('strftime', '%Y-%m-%d'))
		] for f in fhx ]
		lctrl.set_string_items(items)
		lctrl.set_data(fhx)
	#------------------------------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('Family history of this patient.'),
		caption = _('Showing family history.'),
		columns = [ _('Relationship'), _('Condition'), _('Fatal'), _('Noted'), _('Died'), _('Name'), _('Born') ],
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

	#--------------------------------------------------------
#	def test_generic_codes_prw():
#		gmPG2.get_connection()
#		app = wx.PyWidgetTester(size = (500, 40))
#		pw = cGenericCodesPhraseWheel(app.frame, -1)
##		#pw.set_context(context = u'zip', val = u'04318')
#		app.frame.Show(True)
#		app.MainLoop()
	#--------------------------------------------------------
#	test_generic_codes_prw()

#================================================================
