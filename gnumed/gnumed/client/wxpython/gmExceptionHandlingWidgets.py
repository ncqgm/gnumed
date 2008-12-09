"""GNUmed exception handling widgets."""
# ========================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmExceptionHandlingWidgets.py,v $
# $Id: gmExceptionHandlingWidgets.py,v 1.6 2008-12-09 23:29:54 ncq Exp $
__version__ = "$Revision: 1.6 $"
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"

import logging, exceptions, traceback, re as regex, sys, os, shutil, datetime as pyDT, codecs


import wx


from Gnumed.business import gmSurgery
from Gnumed.pycommon import gmDispatcher, gmTools, gmCfg2, gmI18N, gmLog2
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxGladeWidgets import wxgUnhandledExceptionDlg


_log2 = logging.getLogger('gm.gui')
_log2.info(__version__)

_prev_excepthook = None
application_is_closing = False
#=========================================================================
def set_client_version(version):
	global _client_version
	_client_version = version
#-------------------------------------------------------------------------
def set_sender_email(email):
	global _sender_email
	_sender_email = email
#-------------------------------------------------------------------------
def set_helpdesk(helpdesk):
	global _helpdesk
	_helpdesk = helpdesk
#-------------------------------------------------------------------------
def set_staff_name(staff_name):
	global _staff_name
	_staff_name = staff_name
#-------------------------------------------------------------------------
def set_is_public_database(value):
	global _is_public_database
	_is_public_database = value
#-------------------------------------------------------------------------
def handle_uncaught_exception_wx(t, v, tb):

	_log2.debug('unhandled exception caught:', exc_info = (t, v, tb))

	# careful: MSW does reference counting on Begin/End* :-(
	try: wx.EndBusyCursor()
	except: pass

	# dead object error on shutdown ?
	if application_is_closing:
		if t == wx._core.PyDeadObjectError:
			return

	# failed import ?
	if t == exceptions.ImportError:
		gmGuiHelpers.gm_show_error (
			aTitle = _('Missing GNUmed module'),
			aMessage = _(
				'GNUmed detected that parts of it are not\n'
				'properly insalled. The following message\n'
				'names the missing part:\n'
				'\n'
				' "%s"\n'
				'\n'
				'Please make sure to get the missing\n'
				'parts installed. Otherwise some of the\n'
				'functionality will not be accessible.'
			) % v
		)
		_log2.error('module [%s] not installed', v)
		return

	# other exceptions
	_log2.error('enabling debug mode')
	_cfg = gmCfg2.gmCfgData()
	_cfg.set_option(option = 'debug', value = True)
	root_logger = logging.getLogger()
	root_logger.setLevel(logging.DEBUG)
	gmLog2.log_stack_trace()

	name = os.path.basename(_logfile_name)
	name, ext = os.path.splitext(name)
	new_name = os.path.expanduser(os.path.join (
		'~',
		'gnumed',
		'logs',
		'%s_%s%s' % (name, pyDT.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'), ext)
	))

	dlg = cUnhandledExceptionDlg(parent = None, id = -1, exception = (t, v, tb), logfile = new_name)
	dlg.ShowModal()
	comment = dlg._TCTRL_comment.GetValue()
	dlg.Destroy()
	if (comment is not None) and (comment.strip() != u''):
		_log2.error(u'user comment: %s', comment.strip())

	_log2.warning('syncing log file for backup to [%s]', new_name)
	gmLog2.flush()
	shutil.copy2(_logfile_name, new_name)
# ------------------------------------------------------------------------
def install_wx_exception_handler():

	global _logfile_name
	_logfile_name = gmLog2._logfile_name

	global _local_account
	_local_account = os.path.basename(os.path.expanduser('~'))

	set_helpdesk(gmSurgery.gmCurrentPractice().helpdesk)
	set_staff_name(_local_account)
	set_is_public_database(False)
	set_sender_email(None)
	set_client_version(__version__)

	gmDispatcher.connect(signal = 'application_closing', receiver = _on_application_closing)

	global _prev_excepthook
	_prev_excepthook = sys.excepthook
	sys.excepthook = handle_uncaught_exception_wx

	return True
# ------------------------------------------------------------------------
def uninstall_wx_exception_handler():
	if _prev_excepthook is None:
		sys.excepthook = sys.__excepthook__
		return True
	sys.excepthook = _prev_excepthook
	return True
# ------------------------------------------------------------------------
def _on_application_closing():
	global application_is_closing
	# used to ignore a few exceptions, such as when the
	# C++ object has been destroyed before the Python one
	application_is_closing = True
# ========================================================================
class cUnhandledExceptionDlg(wxgUnhandledExceptionDlg.wxgUnhandledExceptionDlg):

	def __init__(self, *args, **kwargs):

		exception = kwargs['exception']
		del kwargs['exception']
		self.logfile = kwargs['logfile']
		del kwargs['logfile']

		wxgUnhandledExceptionDlg.wxgUnhandledExceptionDlg.__init__(self, *args, **kwargs)

		if _sender_email is not None:
			self._TCTRL_sender.SetValue(_sender_email)
		self._TCTRL_helpdesk.SetValue(_helpdesk)
		self._TCTRL_logfile.SetValue(self.logfile)
		t, v, tb = exception
		self._TCTRL_exc_type.SetValue(str(t))
		self._TCTRL_exc_value.SetValue(str(v))
		self._TCTRL_traceback.SetValue(''.join(traceback.format_tb(tb)))

		self.Fit()
	#------------------------------------------
	def _on_close_gnumed_button_pressed(self, evt):
		comment = self._TCTRL_comment.GetValue()
		if (comment is not None) and (comment.strip() != u''):
			_log2.error(u'user comment: %s', comment.strip())
		_log2.warning('syncing log file for backup to [%s]', self.logfile)
		gmLog2.flush()
		shutil.copy2(_logfile_name, self.logfile)
		top_win = wx.GetApp().GetTopWindow()
		wx.CallAfter(top_win.Close)
		evt.Skip()
	#------------------------------------------
	def _on_mail_button_pressed(self, evt):

		comment = self._TCTRL_comment.GetValue()
		if (comment is None) or (comment.strip() == u''):
			comment = wx.GetTextFromUser (
				message = _(
					'Please enter a short note on what you\n'
					'were about to do in GNUmed:'
				),
				caption = _('Sending bug report'),
				parent = self
			)
			if comment.strip() == u'':
				comment = u'user did not comment on bug report'

		receivers = regex.findall (
			'[\S]+@[\S]+',
			self._TCTRL_helpdesk.GetValue().strip(),
			flags = regex.UNICODE | regex.LOCALE
		)
		if len(receivers) == 0:
			if _is_public_database:
				receivers = [u'gnumed-devel@gnu.org']

		receiver_string = wx.GetTextFromUser (
			message = _(
				'Edit the list of email addresses to send the\n'
				'bug report to (separate addresses by spaces).\n'
				'\n'
				'Note that <gnumed-devel@gnu.org> refers to\n'
				'the public (!) GNUmed mailing list.'
			),
			caption = _('Sending bug report'),
			default_value = ','.join(receivers),
			parent = self
		)
		if receiver_string.strip() == u'':
			evt.Skip()
			return

		receivers = regex.findall (
			'[\S]+@[\S]+',
			receiver_string,
			flags = regex.UNICODE | regex.LOCALE
		)

		dlg = gmGuiHelpers.c2ButtonQuestionDlg (
			self,
			-1,
			caption = _('Sending bug report'),
			question = _(
				'Your bug report will be sent to:\n'
				'\n'
				'%s\n'
				'\n'
				'Make sure you have reviewed the log file for potentially\n'
				'sensitive information before sending out the bug report.\n'
				'\n'
				'Note that emailing the report may take a while depending\n'
				'on the speed of your internet connection.\n'
			) % u'\n'.join(receivers),
			button_defs = [
				{'label': _('Send report'), 'tooltip': _('Yes, send the bug report.')},
				{'label': _('Cancel'), 'tooltip': _('No, do not send the bug report.')}
			],
			show_checkbox = True,
			checkbox_msg = _('include log file in bug report')
		)
		dlg._CHBOX_dont_ask_again.SetValue(_is_public_database)
		go_ahead = dlg.ShowModal()
		if go_ahead == wx.ID_NO:
			dlg.Destroy()
			evt.Skip()
			return

		include_log = dlg._CHBOX_dont_ask_again.GetValue()
		if not _is_public_database:
			if include_log:
				result = gmGuiHelpers.gm_show_question (
					_(
						'The database you are connected to is marked as\n'
						'"in-production with controlled access".\n'
						'\n'
						'You indicated that you want to include the log\n'
						'file in your bug report. While this is often\n'
						'useful for debugging the log file might contain\n'
						'bits of patient data which must not be sent out\n'
						'without de-identification.\n'
						'\n'
						'Please confirm that you want to include the log !'
					),
					_('Sending bug report')
				)
				include_log = (result is True)

		sender_email = gmTools.coalesce(self._TCTRL_sender.GetValue(), _('<not supplied>'))
		msg = u"""\
Report sent via GNUmed's handler for unexpected exceptions.

user comment  : %s

client version: %s

system account: %s
staff member  : %s
sender email  : %s

 # enable Launchpad bug tracking
 affects gnumed
 tag automatic-report
 importance medium

""" % (comment, _client_version, _local_account, _staff_name, sender_email)
		if include_log:
			_log2.error(comment)
			_log2.warning('syncing log file for emailing')
			gmLog2.flush()
			for line in codecs.open(_logfile_name, 'rU', 'utf8', 'replace'):
				msg = msg + line

		dlg.Destroy()

		wx.BeginBusyCursor()
		try:
			gmTools.send_mail (
				sender = '%s <%s>' % (_staff_name, gmTools.default_mail_sender),
				receiver = receivers,
				subject = u'<bug>: %s' % comment,
				message = msg,
				encoding = gmI18N.get_encoding(),
				server = gmTools.default_mail_server,
				auth = {'user': gmTools.default_mail_sender, 'password': u'gnumed-at-gmx-net'}
			)
		except StandardError:
			_log.exception('cannot send bug report')
		wx.EndBusyCursor()
		gmDispatcher.send(signal='statustext', msg = _('Bug report has been emailed.'))

		evt.Skip()
	#------------------------------------------
	def _on_view_log_button_pressed(self, evt):
		from Gnumed.pycommon import gmMimeLib
		gmLog2.flush()
		gmMimeLib.call_viewer_on_file(_logfile_name, block = False)
		evt.Skip()
# ========================================================================
# $Log: gmExceptionHandlingWidgets.py,v $
# Revision 1.6  2008-12-09 23:29:54  ncq
# - trap exceptions during smtp handling inside top-level exception handler
#
# Revision 1.5  2008/11/20 19:50:45  ncq
# - improved wording
#
# Revision 1.4  2008/10/12 16:17:57  ncq
# - include client version at top of bug email
# - improved launchpad tracking tags
#
# Revision 1.3  2008/07/28 20:26:49  ncq
# - fixed include_log logic
#
# Revision 1.2  2008/07/16 11:10:46  ncq
# - set_sender_email and use it
# - some cleanup and better docs
#
# Revision 1.1  2008/05/13 12:32:54  ncq
# - factor out exception handling widgets
#
#
