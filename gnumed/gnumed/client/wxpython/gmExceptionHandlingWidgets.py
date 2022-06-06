"""GNUmed exception handling widgets."""
# ========================================================================
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later (details at https://www.gnu.org)"

import logging
import traceback
import sys
import os
import shutil
import datetime as pyDT
import re as regex


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x

from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmCfgINI
from Gnumed.pycommon import gmLog2
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmExceptions
from Gnumed.pycommon import gmNetworkTools
from Gnumed.pycommon.gmTools import u_box_horiz_single

from Gnumed.business import gmPraxis

from Gnumed.wxpython import gmGuiHelpers


_log = logging.getLogger('gm.gui')

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
# exception handlers
#-------------------------------------------------------------------------
def __ignore_dead_objects_from_async(t, v, tb):

	if t != RuntimeError:
		return False

	wx.EndBusyCursor()

	# try to ignore those, they come about from doing
	# async work in wx as Robin tells us
	_log.error('RuntimeError = dead object: %s', v)
	_log.warning('continuing and hoping for the best')
	return True

#-------------------------------------------------------------------------
def __handle_exceptions_on_shutdown(t, v, tb):

	if not application_is_closing:
		return False

	# dead object error ?
	if t == RuntimeError:
		return True

	gmLog2.log_stack_trace('exception on shutdown', t, v, tb)
	return True

#-------------------------------------------------------------------------
def __handle_import_error(t, v, tb):

	if t == OSError:
		if not hasattr(t, 'winerror'):
			return False
		if getattr(t, 'winerror') != 126:
			return False
	else:
		if t != ImportError:
			return False

	wx.EndBusyCursor()

	_log.error('module [%s] not installed', v)
	gmGuiHelpers.gm_show_error (
		aTitle = _('Missing GNUmed module'),
		aMessage = _(
			'GNUmed detected that parts of it are not\n'
			'properly installed. The following message\n'
			'names the missing part:\n'
			'\n'
			' "%s"\n'
			'\n'
			'Please make sure to get the missing\n'
			'parts installed. Otherwise some of the\n'
			'functionality will not be accessible.'
		) % v
	)
	return True

#-------------------------------------------------------------------------
def __handle_ctrl_c(t, v, tb):

	if t != KeyboardInterrupt:
		return False

	print("<Ctrl-C>: Shutting down ...")
	top_win = wx.GetApp().GetTopWindow()
	wx.CallAfter(top_win.Close)
	return True

#-------------------------------------------------------------------------
def __handle_access_violation(t, v, tb):

	if t != gmExceptions.AccessDenied:
		return False

	_log.error('access permissions violation detected')
	wx.EndBusyCursor()
	gmLog2.flush()
	txt = ' ' + v.errmsg
	if v.source is not None:
		txt += _('\n Source: %s') % v.source
	if v.code is not None:
		txt += _('\n Code: %s') % v.code
	if v.details is not None:
		txt += _('\n Details (first 250 characters):\n%s\n%s\n%s') % (
			u_box_horiz_single * 50,
			v.details[:250],
			u_box_horiz_single * 50
		)
	gmGuiHelpers.gm_show_error (
		aTitle = _('Access violation'),
		aMessage = _(
			'You do not have access to this part of GNUmed.\n'
			'\n'
			'%s'
		) % txt
	)
	return True

#-------------------------------------------------------------------------
def __handle_lost_db_connection(t, v, tb):

	if not gmPG2.exception_is_connection_loss(v):
		return False

	gmPG2.log_pg_exception_details(v)
	gmLog2.log_stack_trace('lost connection', t, v, tb)
	wx.EndBusyCursor()
	gmLog2.flush()
	gmGuiHelpers.gm_show_error (
		aTitle = _('Lost connection'),
		aMessage = _(
			'Since you were last working in GNUmed,\n'
			'your database connection timed out.\n'
			'\n'
			'This GNUmed session is now expired.\n'
			'\n'
			'You will have to close this client and\n'
			'restart a new GNUmed session.'
		)
	)
	return True

#-------------------------------------------------------------------------
def __handle_wxgtk_assertion(t, v, tb):
	if t != wx.wxAssertionError:
		return False
	_log.exception('a wxGTK assertion fired:')
	_log.warning('continuing and hoping for the best')
	return True

#-------------------------------------------------------------------------
def handle_uncaught_exception_wx(t, v, tb):

	_log.debug('unhandled exception caught:', exc_info = (t, v, tb))

	if __handle_access_violation(t, v, tb):
		return

	if __handle_ctrl_c(t, v, tb):
		return

	if __handle_exceptions_on_shutdown(t, v, tb):
		return

	if __ignore_dead_objects_from_async(t, v, tb):
		return

	if __handle_import_error(t, v, tb):
		return

	if __handle_wxgtk_assertion(t, v, tb):
		return

	# other exceptions
	_cfg = gmCfgINI.gmCfgData()
	if _cfg.get(option = 'debug') is False:
		_log.error('enabling debug mode')
		_cfg.set_option(option = 'debug', value = True)
		root_logger = logging.getLogger()
		root_logger.setLevel(logging.DEBUG)
		_log.debug('unhandled exception caught:', exc_info = (t, v, tb))

	if __handle_lost_db_connection(t, v, tb):
		return

	gmLog2.log_stack_trace(None, t, v, tb)

	# only do this here or else we can invalidate the stack trace
	# by Windows throwing an exception ... |-(
	# careful: MSW does reference counting on Begin/End* :-(
	wx.EndBusyCursor()

	name = os.path.basename(_logfile_name)
	name, ext = os.path.splitext(name)
	new_name = os.path.expanduser(os.path.join (
		'~',
		'.local',
		'gnumed',
		'error_logs',
		'%s_%s%s' % (name, pyDT.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'), ext)
	))

	dlg = cUnhandledExceptionDlg(None, -1, exception = (t, v, tb), logfile = new_name)
	dlg.ShowModal()
	comment = dlg._TCTRL_comment.GetValue()
	dlg.DestroyLater()
	if (comment is not None) and (comment.strip() != ''):
		_log.error('user comment: %s', comment.strip())

	_log.warning('syncing log file for backup to [%s]', new_name)
	gmLog2.flush()
	# keep a copy around
	shutil.copy2(_logfile_name, new_name)

#------------------------------------------------------------------------
def install_wx_exception_handler():

	global _logfile_name
	_logfile_name = gmLog2._logfile_name

	global _local_account
	_local_account = os.path.basename(os.path.expanduser('~'))

	set_helpdesk(gmPraxis.gmCurrentPraxisBranch().helpdesk)
	set_staff_name(_local_account)
	set_is_public_database(False)
	set_sender_email(None)
	set_client_version('gmExceptionHandlingWidgets.py <default>')

	gmDispatcher.connect(signal = 'application_closing', receiver = _on_application_closing)

	global APP_PID
	APP_PID = os.getpid()
	_log.debug('registered PID [%s] for aborting if necessary', APP_PID)

	global _prev_excepthook
	_prev_excepthook = sys.excepthook
	sys.excepthook = handle_uncaught_exception_wx

	return True

#------------------------------------------------------------------------
def uninstall_wx_exception_handler():
	if _prev_excepthook is None:
		sys.excepthook = sys.__excepthook__
		return True
	sys.excepthook = _prev_excepthook
	return True

#------------------------------------------------------------------------
def _on_application_closing():
	global application_is_closing
	# used to ignore a few exceptions, such as when the
	# C++ object has been destroyed before the Python one
	application_is_closing = True

# ========================================================================
def mail_log(parent=None, comment=None, helpdesk=None, sender=None, exception=None):

	if (comment is None) or (comment.strip() == ''):
		comment = wx.GetTextFromUser (
			message = _(
				'Please enter a short note on what you\n'
				'were about to do in GNUmed:'
			),
			caption = _('Sending bug report'),
			parent = parent
		)
		if comment.strip() == '':
			comment = '<user did not comment on bug report>'

	receivers = []
	if helpdesk is not None:
		receivers = regex.findall (
			'[\S]+@[\S]+',
			helpdesk.strip(),
			flags = regex.UNICODE
		)
	if len(receivers) == 0:
		if _is_public_database:
			receivers = ['gnumed-bugs@gnu.org']

	receiver_string = wx.GetTextFromUser (
		message = _(
			'Edit the list of email addresses to send the\n'
			'bug report to (separate addresses by spaces).\n'
			'\n'
			'Note that <gnumed-bugs@gnu.org> refers to\n'
			'the public (!) GNUmed bugs mailing list.'
		),
		caption = _('Sending bug report'),
		default_value = ','.join(receivers),
		parent = parent
	)
	if receiver_string.strip() == '':
		return

	receivers = regex.findall (
		'[\S]+@[\S]+',
		receiver_string,
		flags = regex.UNICODE
	)

	dlg = gmGuiHelpers.c2ButtonQuestionDlg (
		parent,
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
		) % '\n'.join(receivers),
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
		dlg.DestroyLater()
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

	if sender is None:
		sender = _('<not supplied>')
	else:
		if sender.strip() == '':
			sender = _('<not supplied>')

	if exception is None:
		exc_info = ''
	else:
		t, v, tb = exception
		exc_info = 'Exception:\n\n type: %s\n value: %s\n\nTraceback:\n\n%s' % (t, v, ''.join(traceback.format_tb(tb)))

	msg = """\
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

%s
""" % (comment, _client_version, _local_account, _staff_name, sender, exc_info)
	if include_log:
		_log.error(comment)
		_log.warning('syncing log file for emailing')
		gmLog2.flush()
		attachments = [ [_logfile_name, 'text/plain', 'quoted-printable'] ]
	else:
		attachments = None

	dlg.DestroyLater()

	wx.BeginBusyCursor()
	_cfg = gmCfgINI.gmCfgData()
	try:
		gmNetworkTools.compose_and_send_email (
			sender = '%s <%s>' % (_staff_name, gmNetworkTools.default_mail_sender),
			receiver = receivers,
			subject = '<bug>: %s' % comment,
			message = msg,
			server = gmNetworkTools.default_mail_server,
			auth = {'user': gmNetworkTools.default_mail_sender, 'password': 'gnumed-at-gmx-net'},
			debug = _cfg.get(option = 'debug'),
			attachments = attachments
		)
		gmDispatcher.send(signal='statustext', msg = _('Bug report has been emailed.'))
	except Exception:
		_log.exception('cannot send bug report')
		gmDispatcher.send(signal='statustext', msg = _('Bug report COULD NOT be emailed.'))
	finally:
		wx.EndBusyCursor()

# ========================================================================
from Gnumed.wxGladeWidgets import wxgUnhandledExceptionDlg

class cUnhandledExceptionDlg(wxgUnhandledExceptionDlg.wxgUnhandledExceptionDlg):

	def __init__(self, *args, **kwargs):

		self.__exception = kwargs['exception']
		del kwargs['exception']
		self.logfile = kwargs['logfile']
		del kwargs['logfile']

		wxgUnhandledExceptionDlg.wxgUnhandledExceptionDlg.__init__(self, *args, **kwargs)

		self.Title = '%s [PID %s]' % (self.Title, APP_PID)

		if _sender_email is not None:
			self._TCTRL_sender.SetValue(_sender_email)
		self._TCTRL_helpdesk.SetValue(_helpdesk)
		self._TCTRL_logfile.SetValue(self.logfile)
		t, v, tb = self.__exception
		self._TCTRL_traceback.SetValue ('%s: %s\n%s: %s\n%s' % (
			'type', t,
			'value', v,
			''.join(traceback.format_tb(tb))
		))
		self.Fit()

	#------------------------------------------
	def _on_close_gnumed_button_pressed(self, evt):
		evt.Skip()
		comment = self._TCTRL_comment.GetValue()
		if (comment is not None) and (comment.strip() != ''):
			_log.error('user comment: %s', comment.strip())
		_log.warning('syncing log file for backup to [%s]', self.logfile)
		gmLog2.flush()
		try:
			shutil.copy2(_logfile_name, self.logfile)
		except IOError:
			_log.error('cannot backup log file')
		top_win = wx.GetApp().GetTopWindow()
		wx.CallAfter(top_win.Close)

	#------------------------------------------
	def _on_abort_gnumed_button_pressed(self, evt):
		print('running os._exit(-999)')
		os._exit(-999)
		print('running os.abort()')
		os.abort()
		print('running os.kill(9) on current process')
		os.kill(APP_PID, 9)
		print('running sys.exit()')
		sys.exit(-999)
		# ideas:
		# - start timer thread with abort code from [close] button
		# - start a detached shell script at the OS level with "sleep 20 ; kill -15 PID ; kill -9 PID"

	#------------------------------------------
	def _on_mail_button_pressed(self, evt):
		evt.Skip()
		mail_log (
			parent = self,
			comment = self._TCTRL_comment.GetValue().strip(),
			helpdesk = self._TCTRL_helpdesk.GetValue().strip(),
			sender = self._TCTRL_sender.GetValue().strip(),
			exception = self.__exception
		)

	#------------------------------------------
	def _on_view_log_button_pressed(self, evt):
		evt.Skip()
		from Gnumed.pycommon import gmMimeLib
		gmLog2.flush()
		gmMimeLib.call_viewer_on_file(_logfile_name, block = False)

# ========================================================================
