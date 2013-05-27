"""GNUmed configuration related widgets.
"""
#================================================================
__version__ = '$Revision: 1.4 $'
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
from Gnumed.business import gmPraxis
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmListWidgets


_log = logging.getLogger('gm.ui')
_log.info(__version__)

#==============================================================================
def check_for_updates():

	dbcfg = gmCfg.cCfgSQL()

	url = dbcfg.get2 (
		option = u'horstspace.update.url',
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		bias = 'workplace',
		default = u'http://www.gnumed.de/downloads/gnumed-versions.txt'
	)

	consider_latest_branch = bool(dbcfg.get2 (
		option = u'horstspace.update.consider_latest_branch',
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		bias = 'workplace',
		default = True
	))

	_cfg = gmCfg2.gmCfgData()

	found, msg = gmNetworkTools.check_for_update (
		url = url,
		current_branch = _cfg.get(option = 'client_branch'),
		current_version = _cfg.get(option = 'client_version'),
		consider_latest_branch = consider_latest_branch
	)

	if found is False:
		gmDispatcher.send(signal = 'statustext', msg = _('Your client (%s) is up to date.') % _cfg.get(option = 'client_version'))
		return

	gmGuiHelpers.gm_show_info (
		msg,
		_('Checking for client updates')
	)
#================================================================
def list_configuration(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#---------------
	def refresh(lctrl):
		opts = gmCfg.get_all_options(order_by = u'owner, workplace, option')

		items = [ [
			o['owner'],
			o['workplace'],
			o['option'],
			o['value'],
			o['type'],
			gmTools.coalesce(o['description'], u'')
		] for o in opts ]
		lctrl.set_string_items(items)
		lctrl.set_data(opts)
	#---------------
	def tooltip(item):
		return (
			u'%s %s (#%s) %s\n'
			u'\n'
			u' %s @ %s\n'
			u'\n'
			u' %s: %s\n'
			u'%s'
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
				subsequent_indent = u' ' * 8
			),
			gmTools.wrap (
				text = gmTools.coalesce(item['description'], u'', u'\n%s'),
				width = 40,
				initial_indent = u' ',
				subsequent_indent = u' '
			)
		)
	#---------------
	def delete(item):
		delete_it = gmGuiHelpers.gm_show_question (
			aTitle = _('Deleting option'),
			aMessage = u'%s\n\n%s %s (#%s) %s\n\n%s\n\n%s' % (
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
def configure_string_from_list_option(parent=None, message=None, option=None, bias='user', default_value=u'', choices=None, columns=None, data=None, caption=None):

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
def configure_string_option(parent=None, message=None, option=None, bias=u'user', default_value=u'', validator=None):

	dbcfg = gmCfg.cCfgSQL()

	current_value = dbcfg.get2 (
		option = option,
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		bias = bias,
		default = default_value
	)

	if current_value is not None:
		current_value = u'%s' % current_value

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	while True:
		dlg = wx.TextEntryDialog (
			parent = parent,
			message = message,
			caption = _('Configuration'),
			defaultValue = gmTools.coalesce(current_value, u''),
			style = wx.OK | wx.CANCEL | wx.CENTRE
		)
		result = dlg.ShowModal()
		if result == wx.ID_CANCEL:
			dlg.Destroy()
			return None

		user_val = dlg.GetValue().strip()
		dlg.Destroy()

		if user_val == current_value:
			return user_val

		validated, user_val = validator(user_val)
		if validated:
			break

		gmDispatcher.send (
			signal = u'statustext',
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

	if (len(sys.argv) > 1):
		if sys.argv[1] == 'test':
			check_for_updates()

#================================================================
