"""GNUmed configuration related widgets.
"""
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
from Gnumed.pycommon import gmCfg
from Gnumed.pycommon import gmNetworkTools
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmCfg2
from Gnumed.pycommon import gmWorkerThread
from Gnumed.pycommon import gmConnectionPool
from Gnumed.business import gmPraxis
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmListWidgets


_log = logging.getLogger('gm.ui')

#==============================================================================
def _get_update_status():
	dbcfg = gmCfg.cCfgSQL()
	url = dbcfg.get2 (
		option = 'horstspace.update.url',
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		bias = 'workplace',
		default = 'https://www.gnumed.de/downloads/gnumed-versions.txt'
	)
	consider_latest_branch = bool(dbcfg.get2 (
		option = 'horstspace.update.consider_latest_branch',
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		bias = 'workplace',
		default = True
	))
	_cfg = gmCfg2.gmCfgData()
	update_found, msg = gmNetworkTools.check_for_update (
		url = url,
		current_branch = _cfg.get(option = 'client_branch'),
		current_version = _cfg.get(option = 'client_version'),
		consider_latest_branch = consider_latest_branch
	)
	return update_found, msg

#------------------------------------------------------------------------------
def _signal_update_status(status):

	update_found, msg = status
	if update_found is False:
		_cfg = gmCfg2.gmCfgData()
		gmDispatcher.send(signal = 'statustext', msg = _('Your client (%s) is up to date.') % _cfg.get(option = 'client_version'))
		return

	gmGuiHelpers.gm_show_info(msg, _('Checking for client updates'))

#------------------------------------------------------------------------------
def _async_signal_update_status(status):
	gmConnectionPool.gmConnectionPool().discard_pooled_connection_of_thread()
	wx.CallAfter(_signal_update_status, status)

#------------------------------------------------------------------------------
def check_for_updates(do_async=False):
	if do_async:
		gmWorkerThread.execute_in_worker_thread (
			payload_function = _get_update_status,
			payload_kwargs = None,
			completion_callback = _async_signal_update_status,
			worker_name = 'UpdChk'
		)
		return

	_signal_update_status(_get_update_status())

#================================================================
def list_configuration(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#---------------
	def refresh(lctrl):
		opts = gmCfg.get_all_options(order_by = 'owner, workplace, option')

		items = [ [
			o['owner'],
			o['workplace'],
			o['option'],
			o['value'],
			o['type'],
			gmTools.coalesce(o['description'], '')
		] for o in opts ]
		lctrl.set_string_items(items)
		lctrl.set_data(opts)
	#---------------
	def tooltip(item):
		return (
			'%s %s (#%s) %s\n'
			'\n'
			' %s @ %s\n'
			'\n'
			' %s: %s\n'
			'%s'
		) % (
			gmTools.u_box_horiz_single * 3,
			item['option'],
			item['pk_cfg_item'],
			gmTools.u_box_horiz_single * 3,
			item['owner'],
			item['workplace'],
			item['type'],
			gmTools.wrap(
				text = item['value'],
				width = 40,
				subsequent_indent = ' ' * 8
			),
			gmTools.wrap (
				text = gmTools.coalesce(item['description'], '', '\n%s'),
				width = 40,
				initial_indent = ' ',
				subsequent_indent = ' '
			)
		)
	#---------------
	def delete(item):
		delete_it = gmGuiHelpers.gm_show_question (
			aTitle = _('Deleting option'),
			aMessage = '%s\n\n%s %s (#%s) %s\n\n%s\n\n%s' % (
				tooltip(item),
				gmTools.u_box_horiz_single * 3,
				item['option'],
				item['pk_cfg_item'],
				gmTools.u_box_horiz_single * 3,
				_('Do you really want to delete this option ?'),
				_('(GNUmed will re-create options as needed.)')
			)
		)
		if not delete_it:
			return False

		from Gnumed.wxpython.gmAuthWidgets import get_dbowner_connection
		conn = get_dbowner_connection(procedure = _('Deleting option'))
		if conn is None:
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot connect as database owner. Unable to delete option.'))
			return False

		cfg = gmCfg.cCfgSQL()
		cfg.delete(conn = conn, pk_option = item['pk_cfg_item'])
		return True
	#---------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = _('All configured options currently in the database.'),
		caption = _('All configured options'),
		columns = [ _('User'), _('Workplace'), _('Option'), _('Value'), _('Type'), _('Description') ],
		refresh_callback = refresh,
		delete_callback = delete,
		ignore_OK_button = True,
		list_tooltip_callback = tooltip
	)

#================================================================
def configure_string_from_list_option(parent=None, message=None, option=None, bias='user', default_value='', choices=None, columns=None, data=None, caption=None):

	dbcfg = gmCfg.cCfgSQL()

	current_value = dbcfg.get2 (
		option = option,
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		bias = bias,
		default = default_value
	)

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	if caption is None:
		caption = _('Configuration')

	selections = None
	if current_value is not None:
		try:
			selections = [choices.index(current_value)]
		except ValueError:
			pass

	choice = gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = message,
		caption = caption,
		choices = choices,
		columns = columns,
		data = data,
		selections = selections,
		single_selection = True,
		can_return_empty = False
	)

	# aborted
	if choice is None:
		return

	# same value selected again
	if choice == current_value:
		return

	dbcfg = gmCfg.cCfgSQL()
	dbcfg.set (
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		option = option,
		value = choice
	)

	return

#================================================================
def configure_list_from_list_option(parent=None, message=None, option=None, bias='user', default_value=None, choices=None, columns=None, data=None, caption=None, picks=None):

	if default_value is None:
		default_value = []

	dbcfg = gmCfg.cCfgSQL()

	current_value = dbcfg.get2 (
		option = option,
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		bias = bias,
		default = default_value
	)

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	if caption is None:
		caption = _('Configuration')

	# setup item picker
	picker = gmListWidgets.cItemPickerDlg(parent, -1, msg = message)
	picker.set_columns(columns)
	picker.set_choices(choices)
	picker.set_picks(picks)
	result = picker.ShowModal()
	if result == wx.ID_CANCEL:
		picker.DestroyLater()
		return

	picks = picker.get_picks()
	picker.DestroyLater()

	dbcfg.set (
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		option = option,
		value = picks
	)

	return

#================================================================
def configure_string_option(parent=None, message=None, option=None, bias='user', default_value='', validator=None):

	dbcfg = gmCfg.cCfgSQL()

	current_value = dbcfg.get2 (
		option = option,
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		bias = bias,
		default = default_value
	)

	if current_value is not None:
		current_value = '%s' % current_value

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	if validator is None:
		validator = lambda in_val: (True, in_val)

	while True:
		dlg = wx.TextEntryDialog (
			parent,
			message,
			caption = _('Configuration'),
			value = gmTools.coalesce(current_value, ''),
			style = wx.OK | wx.CANCEL | wx.CENTRE
		)
		result = dlg.ShowModal()
		if result == wx.ID_CANCEL:
			dlg.DestroyLater()
			return None

		user_val = dlg.GetValue().strip()
		dlg.DestroyLater()

		if user_val == current_value:
			return user_val

		validated, user_val = validator(user_val)
		if validated:
			break
		gmDispatcher.send (
			signal = 'statustext',
			msg = _('Value [%s] not valid for option <%s>.') % (user_val, option),
			beep = True
		)

	dbcfg = gmCfg.cCfgSQL()
	dbcfg.set (
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		option = option,
		value = user_val
	)

	return user_val

#================================================================
def configure_boolean_option(parent=None, question=None, option=None, button_tooltips=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	tooltips = [
		_('Set "%s" to <True>.') % option,
		_('Set "%s" to <False>.') % option,
		_('Abort the dialog and do not change the current setting.')
	]
	if button_tooltips is not None:
		for idx in range(len(button_tooltips)):
			tooltips[idx] = button_tooltips[idx]

	dlg = gmGuiHelpers.c3ButtonQuestionDlg (
		parent,
		-1,
		caption = _('Configuration'),
		question = question,
		button_defs = [
			{'label': _('Yes'), 'tooltip': tooltips[0]},
			{'label': _('No'), 'tooltip': tooltips[1]},
			{'label': _('Cancel'), 'tooltip': tooltips[2], 'default': True}
		]
	)

	decision = dlg.ShowModal()
	dbcfg = gmCfg.cCfgSQL()
	if decision == wx.ID_YES:
		dbcfg.set (
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			option = option,
			value = True
		)
	elif decision == wx.ID_NO:
		dbcfg.set (
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			option = option,
			value = False
		)

	return

#================================================================
if __name__ == '__main__':

	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmPG2
	gmPG2.request_login_params(setup_pool = True)

	check_for_updates()
