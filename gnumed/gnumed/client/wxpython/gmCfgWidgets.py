"""GNUmed configuration related widgets.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmCfgWidgets.py,v $
# $Id: gmCfgWidgets.py,v 1.4 2009-12-30 18:47:01 ncq Exp $
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
from Gnumed.pycommon import gmCfg, gmDispatcher, gmTools, gmCfg2
from Gnumed.business import gmSurgery
from Gnumed.wxpython import gmGuiHelpers, gmListWidgets


_log = logging.getLogger('gm.ui')
_log.info(__version__)

#==============================================================================
def check_for_updates():

	dbcfg = gmCfg.cCfgSQL()

	url = dbcfg.get2 (
		option = u'horstspace.update.url',
		workplace = gmSurgery.gmCurrentPractice().active_workplace,
		bias = 'workplace',
		default = u'http://www.gnumed.de/downloads/gnumed-versions.txt'
	)

	consider_latest_branch = bool(dbcfg.get2 (
		option = u'horstspace.update.consider_latest_branch',
		workplace = gmSurgery.gmCurrentPractice().active_workplace,
		bias = 'workplace',
		default = True
	))

	_cfg = gmCfg2.gmCfgData()

	found, msg = gmTools.check_for_update (
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
#================================================================
def configure_string_from_list_option(parent=None, message=None, option=None, bias='user', default_value=u'', choices=None, columns=None, data=None, caption=None):

	dbcfg = gmCfg.cCfgSQL()

	current_value = dbcfg.get2 (
		option = option,
		workplace = gmSurgery.gmCurrentPractice().active_workplace,
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
		workplace = gmSurgery.gmCurrentPractice().active_workplace,
		option = option,
		value = choice
	)

	return
#================================================================
def configure_string_option(parent=None, message=None, option=None, bias=u'user', default_value=u'', validator=None):

	dbcfg = gmCfg.cCfgSQL()

	current_value = dbcfg.get2 (
		option = option,
		workplace = gmSurgery.gmCurrentPractice().active_workplace,
		bias = bias,
		default = default_value
	)

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
			return

		user_val = dlg.GetValue().strip()
		dlg.Destroy()

		if user_val == current_value:
			return

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
		workplace = gmSurgery.gmCurrentPractice().active_workplace,
		option = option,
		value = user_val
	)

	return
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
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
			option = option,
			value = True
		)
	elif decision == wx.ID_NO:
		dbcfg.set (
			workplace = gmSurgery.gmCurrentPractice().active_workplace,
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
# $Log: gmCfgWidgets.py,v $
# Revision 1.4  2009-12-30 18:47:01  ncq
# - fix strange case of missing gmCfg2 import
#
# Revision 1.3  2009/12/21 15:03:34  ncq
# - check_for_updates should be here
#
# Revision 1.2  2009/10/20 10:25:43  ncq
# - support pre-selections in configure-string-from-list
#
# Revision 1.1  2008/01/16 19:25:18  ncq
# - new file, factored out from gmGuiHelpers
#
#