"""GNUmed praxis related widgets.

Praxis:

	Each database belongs to ONE praxis only. A praxis can
	have several branches. A praxis is at the same level
	as an organization, except that it is not explicitly
	defined. Rather, that ONE organization of which at least
	one unit is defined as a praxis branch IS the praxis.

Praxis branch

	Branches are the sites/locations of a praxis. There
	can be several branches. Each branch must link to
	units of ONE AND THE SAME organization (because
	it is not considered good data protection practice
	to mix charts of *different* organizations within
	one database). However, that organization which
	has units that are praxis branches can also have
	other units which are not branches :-)

copyright: authors
"""
#============================================================
__author__ = "K.Hilbert"
__license__ = "GPL v2 or later (details at https://www.gnu.org)"

import logging
import sys


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmCfgDB
from Gnumed.pycommon import gmCfgINI
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmMatchProvider

from Gnumed.business import gmPraxis
from Gnumed.business import gmStaff
from Gnumed.business import gmOrganization

from Gnumed.wxpython import gmOrganizationWidgets
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmAuthWidgets
from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmPlugin
from Gnumed.wxpython import gmCfgWidgets
from Gnumed.wxpython import gmPhraseWheel


_log = logging.getLogger('gm.praxis')
_cfg = gmCfgINI.gmCfgData()

#=========================================================================
def show_audit_trail(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	conn = gmAuthWidgets.get_dbowner_connection(procedure = _('showing audit trail'))
	if conn is None:
		return False

	#-----------------------------------
	def refresh(lctrl):
		cmd = 'SELECT * FROM audit.v_audit_trail ORDER BY audit_when_ts'
		rows = gmPG2.run_ro_queries(link_obj = conn, queries = [{'sql': cmd}])
		lctrl.set_string_items (
			[ [
				r['event_when'],
				r['event_by'],
				'%s %s %s' % (
					gmTools.coalesce(r['row_version_before'], gmTools.u_diameter),
					gmTools.u_arrow2right,
					gmTools.coalesce(r['row_version_after'], gmTools.u_diameter)
				),
				r['event_table'],
				r['event'],
				r['pk_audit']
			] for r in rows ]
		)
	#-----------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = '',
		caption = _('GNUmed database audit log ...'),
		columns = [ _('When'), _('Who'), _('Revisions'), _('Table'), _('Event'), '#' ],
		single_selection = True,
		refresh_callback = refresh
	)

#============================================================
def configure_fallback_primary_provider(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	staff = gmStaff.get_staff_list()
	choices = [ [
			s['short_alias'],
			'%s%s %s' % (
				gmTools.coalesce(s['title'], '', '%s '),
				s['firstnames'],
				s['lastnames']
			),
			s['l10n_role'],
			gmTools.coalesce(s['comment'], '')
		]
		for s in staff
		if s['is_active'] is True
	]
	data = [ s['pk_staff'] for s in staff if s['is_active'] is True ]

	gmCfgWidgets.configure_string_from_list_option (
		parent = parent,
		message = _(
			'\n'
			'Please select the provider to fall back to in case\n'
			'no primary provider is configured for a patient.\n'
		),
		option = 'patient.fallback_primary_provider',
		bias = 'user',
		default_value = None,
		choices = choices,
		columns = [_('Alias'), _('Provider'), _('Role'), _('Comment')],
		data = data,
		caption = _('Configuring fallback primary provider')
	)

#============================================================
# workplace plugin configuration widgets
#------------------------------------------------------------
def configure_workplace_plugins(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#-----------------------------------
	def delete(workplace):

		curr_workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace
		if workplace == curr_workplace:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot delete the active workplace.'), beep = True)
			return False

		dlg = gmGuiHelpers.c2ButtonQuestionDlg (
			parent,
			-1,
			caption = _('Deleting workplace ...'),
			question = _('Are you sure you want to delete this workplace ?\n\n "%s"\n') % workplace,
			show_checkbox = True,
			checkbox_msg = _('delete configuration, too'),
			checkbox_tooltip = _(
				'Check this if you want to delete all configuration items\n'
				'for this workplace along with the workplace itself.'
			),
			button_defs = [
				{'label': _('Delete'), 'tooltip': _('Yes, delete this workplace.'), 'default': True},
				{'label': _('Do NOT delete'), 'tooltip': _('No, do NOT delete this workplace'), 'default': False}
			]
		)

		decision = dlg.ShowModal()
		if decision != wx.ID_YES:
			dlg.DestroyLater()
			return False

		include_cfg = dlg.checkbox_is_checked()
		dlg.DestroyLater()

		dbo_conn = gmAuthWidgets.get_dbowner_connection(procedure = _('delete workplace'))
		if not dbo_conn:
			return False

		gmPraxis.delete_workplace(workplace = workplace, conn = dbo_conn, delete_config = include_cfg)
		return True
	#-----------------------------------
	def edit(workplace=None):
		if workplace is None:
			dlg = wx.TextEntryDialog (
				parent,
				_('Enter a descriptive name for the new workplace:'),
				caption = _('Configuring GNUmed workplaces ...'),
				value = '',
				style = wx.OK | wx.CENTRE
			)
			dlg.ShowModal()
			workplace = dlg.GetValue().strip()
			if workplace == '':
				gmGuiHelpers.gm_show_error(_('Cannot save a new workplace without a name.'), _('Configuring GNUmed workplaces ...'))
				return False
			curr_plugins = []
		else:
			curr_plugins = gmTools.coalesce(gmCfgDB.get4workplace (
				option = 'horstspace.notebook.plugin_load_order',
				workplace = workplace
				), []
			)

		msg = _(
			'Pick the plugin(s) to be loaded the next time the client is restarted under the workplace:\n'
			'\n'
			'    [%s]\n'
		) % workplace

		picker = gmListWidgets.cItemPickerDlg (
			parent,
			-1,
			title = _('Configuring workplace plugins ...'),
			msg = msg
		)
		picker.set_columns(['Available plugins'], ['Active plugins'])
		available_plugins = gmPlugin.get_installed_plugins(plugin_dir = 'gui')
		picker.set_choices(available_plugins)
		picker.set_picks(picks = curr_plugins[:])
		btn_pressed = picker.ShowModal()
		if btn_pressed != wx.ID_OK:
			picker.DestroyLater()
			return False

		new_plugins = picker.get_picks()
		picker.DestroyLater()
		if new_plugins == curr_plugins:
			return True

		if new_plugins is None:
			return True

		gmCfgDB.set (
			option = 'horstspace.notebook.plugin_load_order',
			value = new_plugins,
			workplace = workplace
		)

		return True
	#-----------------------------------
	def edit_old(workplace=None):

		available_plugins = gmPlugin.get_installed_plugins(plugin_dir='gui')
		if workplace is None:
			dlg = wx.TextEntryDialog (
				parent,
				_('Enter a descriptive name for the new workplace:'),
				caption = _('Configuring GNUmed workplaces ...'),
				value = '',
				style = wx.OK | wx.CENTRE
			)
			dlg.ShowModal()
			workplace = dlg.GetValue().strip()
			if workplace == '':
				gmGuiHelpers.gm_show_error(_('Cannot save a new workplace without a name.'), _('Configuring GNUmed workplaces ...'))
				return False
			curr_plugins = []
			choices = available_plugins
		else:
			curr_plugins = gmTools.coalesce(gmCfgDB.get4workplace (
				option = 'horstspace.notebook.plugin_load_order',
				workplace = workplace
				), []
			)
			choices = curr_plugins[:]
			for p in available_plugins:
				if p not in choices:
					choices.append(p)

		sels = range(len(curr_plugins))
		new_plugins = gmListWidgets.get_choices_from_list (
			parent = parent,
			msg = _(
				'\n'
				'Select the plugin(s) to be loaded the next time\n'
				'the client is restarted under the workplace:\n'
				'\n'
				' [%s]'
				'\n'
			) % workplace,
			caption = _('Configuring GNUmed workplaces ...'),
			choices = choices,
			selections = sels,
			columns = [_('Plugins')],
			single_selection = False
		)

		if new_plugins == curr_plugins:
			return True

		if new_plugins is None:
			return True

		gmCfgDB.set (
			option = 'horstspace.notebook.plugin_load_order',
			value = new_plugins,
			workplace = workplace
		)

		return True
	#-----------------------------------
	def clone(workplace=None):
		if workplace is None:
			return False

		new_name = wx.GetTextFromUser (
			message = _('Enter a name for the new workplace !'),
			caption = _('Cloning workplace'),
			default_value = '%s-2' % workplace,
			parent = parent
		).strip()
		if new_name == '':
			return False

		opt = 'horstspace.notebook.plugin_load_order'
		plugins = gmCfgDB.get4workplace(option = opt, workplace = workplace)
		gmCfgDB.set (
			option = opt,
			value = plugins,
			workplace = new_name
		)
		# FIXME: clone cfg, too
		return True

	#-----------------------------------
	def refresh(lctrl):
		workplaces = gmPraxis.gmCurrentPraxisBranch().workplaces
		curr_workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace
		try:
			sels = [workplaces.index(curr_workplace)]
		except ValueError:
			sels = []

		lctrl.set_string_items(workplaces)
		lctrl.set_selections(selections = sels)
	#-----------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _(
			'\nSelect the workplace to configure below.\n'
			'\n'
			'The currently active workplace is preselected.\n'
		),
		caption = _('Configuring GNUmed workplaces ...'),
		columns = [_('Workplace')],
		single_selection = True,
		refresh_callback = refresh,
		edit_callback = edit,
		new_callback = edit,
		delete_callback = delete,
		left_extra_button = (_('Clone'), _('Clone the selected workplace'), clone)
	)

#============================================================
from Gnumed.wxGladeWidgets import wxgGreetingEditorDlg

class cGreetingEditorDlg(wxgGreetingEditorDlg.wxgGreetingEditorDlg):

	def __init__(self, *args, **kwargs):
		wxgGreetingEditorDlg.wxgGreetingEditorDlg.__init__(self, *args, **kwargs)

		self.praxis = gmPraxis.gmCurrentPraxisBranch()
		self._TCTRL_message.SetValue(self.praxis.db_logon_banner)
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_save_button_pressed(self, evt):
		self.praxis.db_logon_banner = self._TCTRL_message.GetValue().strip()
		if self.IsModal():
			self.EndModal(wx.ID_SAVE)
		else:
			self.Close()

#============================================================
def select_praxis_branch(parent=None):
	branches = gmPraxis.get_praxis_branches()
	if len(branches) == 0:
		if not set_active_praxis_branch(parent = parent, no_parent = False):
			return None

	# FIXME: needs implementation

#============================================================
def __create_praxis_and_branch():
	pk_cat = gmOrganization.create_org_category(category = 'Praxis')
	org = gmOrganization.create_org(_('Your praxis'), pk_cat)
	unit = org.add_unit(_('Your branch'))
	branch = gmPraxis.create_praxis_branch(pk_org_unit = unit['pk_org_unit'])
	_log.debug('auto-created praxis and branch because no organizations existed: %s', branch)
	gmGuiHelpers.gm_show_info (
		title = _('Praxis configuration ...'),
		info = _(
			'GNUmed has auto-created the following\n'
			'praxis branch for you (which you can\n'
			'later configure as needed):\n'
			'\n'
			'%s'
		) % branch.format()
	)
	return branch

#============================================================
def __create_branch_for_praxis(pk_org_unit:int):
	branch = gmPraxis.create_praxis_branch(pk_org_unit = pk_org_unit)
	_log.debug('auto-created praxis branch because only one organization without any unit existed: %s', branch)
	gmGuiHelpers.gm_show_info (
		title = _('Praxis configuration ...'),
		info = _(
			'GNUmed has auto-created the following\n'
			'praxis branch for you (which you can\n'
			'later configure as needed):\n'
			'\n'
			'%s'
		) % branch.format()
	)
	return branch

#============================================================
def __select_org_unit_as_branch():
	_log.debug('no praxis branches configured, selecting from organization units')
	msg = _(
			'No praxis branches configured currently.\n'
			'\n'
			'You MUST select one unit of one organization to be the\n'
			'branch (site, office) which you are logging in from.'
	)
	unit = gmOrganizationWidgets.select_org_unit(msg = msg, no_parent = True)
	if unit is None:
		_log.warning('no organization unit selected, aborting')
		return None

	_log.debug('org unit selected as praxis branch: %s', unit)
	branch = gmPraxis.create_praxis_branch(pk_org_unit = unit['pk_org_unit'])
	_log.debug('created praxis branch from org unit: %s', branch)
	return branch

#============================================================
def __update_most_recently_selected_branch(branch):
	prefs_file = _cfg.get(option = 'user_preferences_file')
	gmCfgINI.set_option_in_INI_file (
		filename = prefs_file,
		group = 'preferences',
		option = 'most recently used praxis branch',
		value = branch.format(one_line = True)
	)
	_cfg.reload_file_source(filename = prefs_file)

#============================================================
def __get_most_recently_selected_branch():
	return _cfg.get (
		group = 'preferences',
		option = 'most recently used praxis branch',
		source_order = [
			('explicit', 'return'),
			('workbase', 'return'),
			('local', 'return'),
			('user', 'return')
		]
	)

#============================================================
def set_active_praxis_branch(parent=None, no_parent=False):

	if no_parent:
		parent = None
	else:
		if parent is None:
			parent = wx.GetApp().GetTopWindow()

	branches = gmPraxis.get_praxis_branches()

	if len(branches) == 1:
		_log.debug('only one praxis branch configured, activating')
		gmPraxis.gmCurrentPraxisBranch(branches[0])
		return True

	if len(branches) == 0:
		orgs = gmOrganization.get_orgs()
		if len(orgs) == 0:
			new_branch_of_new_praxis = __create_praxis_and_branch()
			gmPraxis.gmCurrentPraxisBranch(new_branch_of_new_praxis)
			return True

		if len(orgs) == 1:
			units = orgs[0].units
			if len(units) == 1:
				branch = __create_branch_for_praxis(units[0]['pk_org_unit'])
				gmPraxis.gmCurrentPraxisBranch(branch)
				return True

		branch = __select_org_unit_as_branch()
		if branch is None:
			return False

		gmPraxis.gmCurrentPraxisBranch(branch)
		return True

	most_recent_branch = __get_most_recently_selected_branch()

	#--------------------
	def refresh(lctrl):
		branches = gmPraxis.get_praxis_branches()
		items = [
			[	b['branch'],
				gmTools.coalesce(b['l10n_unit_category'], '')
			] for b in branches
		]
		lctrl.set_string_items(items = items)
		lctrl.set_data(data = branches)
		if most_recent_branch is not None:
			for idx in range(len(branches)):
				if branches[idx].format(one_line = True) == most_recent_branch:
					lctrl.selections = [idx]
					break
	#--------------------

	branch = gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _("Select the branch of praxis [%s] which you are logging in from.\n") % branches[0]['praxis'],
		caption = _('Praxis branch selection ...'),
		columns = [_('Branch'), _('Branch type')],
		can_return_empty = False,
		single_selection = True,
		refresh_callback = refresh
	)
	if branch is None:
		_log.warning('no praxis branch selected, aborting')
		return False

	__update_most_recently_selected_branch(branch)
	gmPraxis.gmCurrentPraxisBranch(branch)
	return True

#============================================================
def manage_praxis_branches(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#---------------------------
	def get_unit_tooltip(unit):
		if unit is None:
			return None
		return '\n'.join(unit.format(with_address = True, with_org = True, with_comms = True))
	#---------------------------
	def manage_orgs():
		gmOrganizationWidgets.manage_orgs(parent = parent)
	#---------------------------

	branches = gmPraxis.get_praxis_branches()
	org = branches[0].organization
	praxis = branches[0]['praxis']

	msg = _(
		'Pick those units of "%s" which are branches of your praxis !\n'
		'\n'
		'Note that no other client should be connected at this time.\n'
		'\n'
		'If you want to select another organization entirely\n'
		'first remove all existing branches.\n'
	) % praxis

	picker = gmListWidgets.cItemPickerDlg(parent, -1, msg = msg)
	picker.extra_button = (
		_('Manage units'),
		_('Manage organizations and their units'),
		manage_orgs
	)
	picker.left_item_tooltip_callback = get_unit_tooltip
	picker.right_item_tooltip_callback = get_unit_tooltip
	picker.set_columns(columns = [_('Units of "%s"') % praxis], columns_right = [_('Branches of your praxis')])
	units = org.units
	branch_unit_pks = [b['pk_org_unit'] for b in branches]
	branch_units = []
	for unit in units:
		if unit['pk_org_unit'] in branch_unit_pks:
			branch_units.append(unit)
	items = [ '%s%s' % (u['unit'], gmTools.coalesce(u['l10n_unit_category'], '', ' (%s)')) for u in units ]
	picker.set_choices(choices = items, data = units)
	items = [ '%s%s' % (u['unit'], gmTools.coalesce(u['l10n_unit_category'], '', ' (%s)')) for u in branch_units ]
	picker.set_picks(picks = items, data = branch_units)
	del units
	del branch_unit_pks
	del branch_units
	del items

	result = picker.ShowModal()

	if result == wx.ID_CANCEL:
		picker.DestroyLater()
		return None

	picks = picker.picks
	picker.DestroyLater()

	failed_delete_msg = _(
		'Cannot delete praxis branch(es).\n'
		'\n'
		'There are probably clients logged in\n'
		'from other locations. You need to log out\n'
		'all but this client before the praxis can\n'
		'be reconfigured.'
	)

	if len(picks) == 0:
		if not gmPraxis.delete_praxis_branches():
			gmGuiHelpers.gm_show_error (
				error = failed_delete_msg,
				title = _('Configuring praxis ...')
			)
			return False
		while not set_active_praxis_branch(parent = parent):
			pass
		return

	pk_picked_units = [p['pk_org_unit'] for p in picks]
	pk_branches_to_keep = [
		b['pk_praxis_branch'] for b in gmPraxis.get_praxis_branches()
		if b['pk_org_unit'] in pk_picked_units
	]
	if len(pk_branches_to_keep) == 0:
		if not gmPraxis.delete_praxis_branches():
			gmGuiHelpers.gm_show_error (
				error = failed_delete_msg,
				title = _('Configuring praxis ...')
			)
			return False
	else:
		if not gmPraxis.delete_praxis_branches(except_pk_praxis_branches = pk_branches_to_keep):
			gmGuiHelpers.gm_show_error (
				error = failed_delete_msg,
				title = _('Configuring praxis ...')
			)
			return False
	gmPraxis.create_praxis_branches(pk_org_units = pk_picked_units)

	# detect whether active branch in kept branches
	if gmPraxis.gmCurrentPraxisBranch()['pk_praxis_branch'] in pk_branches_to_keep:
		return

	while not set_active_praxis_branch(parent = parent):
		pass

#============================================================
class cPraxisBranchPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		query = """(
			SELECT
				pk_praxis_branch AS data,
				branch || ' (' || praxis || ')' AS field_label,
				branch || coalesce(' (' || l10n_unit_category || ')', '') || ' of ' || l10n_organization_category || ' "' || praxis || '"' AS list_label
			FROM
				dem.v_praxis_branches
			WHERE
				branch %(fragment_condition)s

			)	UNION	(

			SELECT
				pk_praxis_branch AS data,
				branch || ' (' || praxis || ')' AS field_label,
				branch || coalesce(' (' || l10n_unit_category || ')', '') || ' of ' || l10n_organization_category || ' "' || praxis || '"' AS list_label
			FROM
				dem.v_praxis_branches
			WHERE
				praxis %(fragment_condition)s

			)	UNION	(

			SELECT
				pk_praxis_branch AS data,
				branch || ' (' || praxis || ')' AS field_label,
				branch || coalesce(' (' || l10n_unit_category || ')', '') || ' of ' || l10n_organization_category || ' "' || praxis || '"' AS list_label
			FROM
				dem.v_praxis_branches
			WHERE
				l10n_unit_category %(fragment_condition)s

			)
		ORDER BY
			list_label
		LIMIT 50"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(1, 2, 4)
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.SetToolTip(_("Select a praxis branch."))
		self.matcher = mp
		self.selection_only = True
		self.picklist_delay = 300
	#--------------------------------------------------------
	def _get_data_tooltip(self):
		if self.GetData() is None:
			return None
		branch = self._data2instance()
		if branch is None:
			return None
		return branch.format()
	#--------------------------------------------------------
	def _data2instance(self, link_obj=None):
		if self.GetData() is None:
			return None
		return gmPraxis.cPraxisBranch(aPK_obj = self.GetData())

#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

#	from Gnumed.pycommon import gmPG2
#	from Gnumed.pycommon import gmI18N
#	gmI18N.activate_locale()
#	gmI18N.install_domain()

	def test_configure_wp_plugins():
		#app = wx.PyWidgetTester(size = (400, 300))
		configure_workplace_plugins()

	#--------------------------------------------------------
	#test_org_unit_prw()
	#test_configure_wp_plugins()
