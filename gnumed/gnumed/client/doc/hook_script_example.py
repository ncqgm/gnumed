#===========================================================================
#
# Example script to be run off GNUmed hooks.
#
# It will print a message to the stdout window
# or console whenever any hook is invoked.
#
# Copy this file to ~/.gnumed/scripts/hook_script.py and modify as needed.
#
#===========================================================================
__version__ = "$Revision: 1.4 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later (details at http://www.gnu.org)"

#from Gnumed.wxpython import gmGuiHelpers, gmPatSearchWidgets
#from Gnumed.business import gmPerson

#def on_startup_after_GUI_init():
	# examine external patient sources
	#gmPatSearchWidgets.get_person_from_external_sources(search_immediately=False, activate_immediately=True)

#def request_user_attention():
	# signal user to look at GNUmed
	#gmGuiHelpers.gm_show_info(_('Hey, GNUmed wants you to take a look at it !'))

#def on_app_activated_startup():
	#pass

#def on_app_activated():
	# might want to look at external sources again
	#gmPatSearchWidgets.get_person_from_external_sources(search_immediately=False, activate_immediately=True)

#def on_post_patient_activation():
#def on_app_deactivated():
	# might want to export the active patient into an xDT file
	#curr_pat = gmPerson.gmCurrentPatient()
	#if curr_pat.connected:
	#	enc = 'cp850'			# FIXME: configurable
	#	fname = os.path.expanduser(os.path.join('~', '.gnumed', 'current-patient.gdt'))
	#	curr_pat.export_as_gdt(filename = fname, encoding = enc)

# main entry point
def run_script(hook=None):

	if hook is None:
		hook = _('no hook specified, please report bug')

	print('GNUmed invoked the hook [%s]' % hook)

	# a few examples:

	#if hook == u'startup-after-GUI-init':
	#	on_startup_after_GUI_init()

	#if hook == u'request_user_attention':
	#	on_request_user_attention()

	#if hook == u'app_activated_startup':
	#	on_app_activated_startup()

	#if hook == u'app_activated':
	#	on_app_activated()

	#if hook == u'app_deactivated':
	#	on_app_deactivated()

	#if hook == u'post_patient_activation':
	#	on_post_patient_activation()

	return

#===========================================================================
