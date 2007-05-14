"""GnuMed GUI helper classes and functions

This module provides some convenient wxPython GUI
helper thingies that are widely used throughout
GnuMed.

This source code is protected by the GPL licensing scheme.
Details regarding the GPL are available at http://www.gnu.org
You may use and share it as long as you don't deny this right
to anybody else.
"""
# ========================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmGuiHelpers.py,v $
# $Id: gmGuiHelpers.py,v 1.59 2007-05-14 08:36:13 ncq Exp $
__version__ = "$Revision: 1.59 $"
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"

import sys, os, shutil, datetime as pyDT, traceback

if __name__ == '__main__':
	sys.exit("This is not intended to be run standalone !")

import wx

from Gnumed.business import gmSurgery
from Gnumed.pycommon import gmLog, gmGuiBroker, gmPG2, gmLoginInfo, gmDispatcher, gmSignals
from Gnumed.wxGladeWidgets import wxg3ButtonQuestionDlg, wxg2ButtonQuestionDlg, wxgUnhandledExceptionDlg

_log = gmLog.gmDefLog
_log.Log(gmLog.lData, __version__)

_prev_excepthook = None

# ========================================================================
def handle_uncaught_exception_wx(t, v, tb):

	_log.LogException('unhandled exception caught', (t,v,tb), verbose=True)

	for target in _log.get_targets():
		if not isinstance(target, gmLog.cLogTargetFile):
			continue
		name = os.path.basename(target.ID)
		name, ext = os.path.splitext(name)
		new_name = os.path.expanduser(os.path.join (
			'~',
			'gnumed',
			'logs',
			'%s_%s%s' % (name, pyDT.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'), ext)
		))
		_log.Log(gmLog.lWarn, 'syncing log file for backup to [%s]' % new_name)
		_log.flush()
		shutil.copy2(target.ID, new_name)

	wx.EndBusyCursor()

	dlg = cUnhandledExceptionDlg(parent = None, id = -1, exception = (t, v, tb), logfile = new_name)
	dlg.ShowModal()
	dlg.Destroy()
# ------------------------------------------------------------------------
def install_wx_exception_handler():
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
# ========================================================================
class cUnhandledExceptionDlg(wxgUnhandledExceptionDlg.wxgUnhandledExceptionDlg):

	def __init__(self, *args, **kwargs):

		exception = kwargs['exception']
		del kwargs['exception']
		logfile = kwargs['logfile']
		del kwargs['logfile']

		wxgUnhandledExceptionDlg.wxgUnhandledExceptionDlg.__init__(self, *args, **kwargs)

		office = gmSurgery.gmCurrentPractice()
		self._TCTRL_helpdesk.SetValue(office.helpdesk)
		self._TCTRL_logfile.SetValue(logfile)
		t, v, tb = exception
		self._TCTRL_exc_type.SetValue(str(t))
		self._TCTRL_exc_value.SetValue(str(v))
		self._TCTRL_traceback.SetValue(''.join(traceback.format_tb(tb)))

		self.Fit()
	#------------------------------------------
	def _on_close_gnumed_button_pressed(self, evt):
		top_win = wx.GetApp().GetTopWindow()
		wx.CallAfter(top_win.Close)
		evt.Skip()
# ========================================================================
class c2ButtonQuestionDlg(wxg2ButtonQuestionDlg.wxg2ButtonQuestionDlg):

	def __init__(self, *args, **kwargs):

		caption = kwargs['caption']
		question = kwargs['question']
		button_defs = kwargs['button_defs'][:2]
		try:
			show_checkbox = kwargs['show_checkbox']
			del kwargs['show_checkbox']
		except KeyError:
			show_checkbox = False

		del kwargs['caption']
		del kwargs['question']
		del kwargs['button_defs']

		wxg2ButtonQuestionDlg.wxg2ButtonQuestionDlg.__init__(self, *args, **kwargs)

		self.SetTitle(title = caption)
		self._LBL_question.SetLabel(label = question)

		if not show_checkbox:
			self._CHBOX_dont_ask_again.Hide()

		buttons = [self._BTN_1, self._BTN_2]
		for idx in range(len(button_defs)):
			buttons[idx].SetLabel(label = button_defs[idx]['label'])
			buttons[idx].SetToolTipString(button_defs[idx]['tooltip'])
			if button_defs[idx]['default']:
				buttons[idx].SetDefault()

		self.Fit()
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_BTN_1_pressed(self, evt):
		if self.IsModal():
			self.EndModal(wx.ID_YES)
		else:
			self.Close()
	#--------------------------------------------------------
	def _on_BTN_2_pressed(self, evt):
		if self.IsModal():
			self.EndModal(wx.ID_NO)
		else:
			self.Close()
# ========================================================================
class c3ButtonQuestionDlg(wxg3ButtonQuestionDlg.wxg3ButtonQuestionDlg):

	def __init__(self, *args, **kwargs):

		caption = kwargs['caption']
		question = kwargs['question']
		button_defs = kwargs['button_defs'][:3]

		del kwargs['caption']
		del kwargs['question']
		del kwargs['button_defs']

		wxg3ButtonQuestionDlg.wxg3ButtonQuestionDlg.__init__(self, *args, **kwargs)

		self.SetTitle(title = caption)
		self._LBL_question.SetLabel(label = question)

		buttons = [self._BTN_1, self._BTN_2, self._BTN_3]
		for idx in range(len(button_defs)):
			buttons[idx].SetLabel(label = button_defs[idx]['label'])
			buttons[idx].SetToolTipString(button_defs[idx]['tooltip'])
			if button_defs[idx]['default']:
				buttons[idx].SetDefault()

		self.Fit()
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_BTN_1_pressed(self, evt):
		if self.IsModal():
			self.EndModal(wx.ID_YES)
		else:
			self.Close()
	#--------------------------------------------------------
	def _on_BTN_2_pressed(self, evt):
		if self.IsModal():
			self.EndModal(wx.ID_NO)
		else:
			self.Close()
# ========================================================================
class cTreeExpansionHistoryMixin:
	"""TreeCtrl mixin class to record expansion history."""
	def __init__(self):
		if not isinstance(self, wx.TreeCtrl):
			raise TypeError('[%s]: mixin can only be applied to wx.TreeCtrl, not [%s]' % (cTreeExpansionHistoryMixin, self.__class__.__name__))
		self.expansion_state = {}
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------
	def snapshot_expansion(self):
		self.__record_subtree_expansion(start_node_id = self.GetRootItem())
	#--------------------------------------------------------
	def restore_expansion(self):
		if len(self.expansion_state) == 0:
			return True
		self.__restore_subtree_expansion(start_node_id = self.GetRootItem())
	#--------------------------------------------------------
	def print_expansion(self):
		if len(self.expansion_state) == 0:
			print "currently no expansion snapshot available"
			return True
		print "last snapshot of state of expansion"
		print "-----------------------------------"
		print "listing expanded nodes:"
		for node_id in self.expansion_state.keys():
			print "node ID:", node_id
			print "  selected:", self.expansion_state[node_id]
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __record_subtree_expansion(self, start_node_id=None):
		"""This records node expansion states based on the item label.

		A side effect of this is that identically named items can
		become unduly synchronized in their expand state after a
		snapshot/restore cycle.

		Better choices might be

			id(item.GetPyData()) or
			item.GetPyData().get_tree_uid()

		where get_tree_uid():

			'[%s:%s]' % (self.__class__.__name__, id(self))

		or some such. This would survive renaming of the item.

		For database items it may be useful to include the
		primary key which would - contrary to id() - survive
		reloads from the database.
		"""
		# protect against empty tree where not even
		# a root node exists
		if not start_node_id.IsOk():
			return True

		if not self.IsExpanded(start_node_id):
			return True

		self.expansion_state[self.GetItemText(start_node_id)] = self.IsSelected(start_node_id)

		child_id, cookie = self.GetFirstChild(start_node_id)
		while child_id.IsOk():
			self.__record_subtree_expansion(start_node_id = child_id)
			child_id, cookie = self.GetNextChild(start_node_id, cookie)

		return
	#--------------------------------------------------------
	def __restore_subtree_expansion(self, start_node_id=None):
		start_node_label = self.GetItemText(start_node_id)
		try:
			node_selected = self.expansion_state[start_node_label]
		except KeyError:
			return

		self.Expand(start_node_id)
		if node_selected:
			self.SelectItem(start_node_id)

		child_id, cookie = self.GetFirstChild(start_node_id)
		while child_id.IsOk():
			self.__restore_subtree_expansion(start_node_id = child_id)
			child_id, cookie = self.GetNextChild(start_node_id, cookie)

		return
# ========================================================================
class cFileDropTarget(wx.FileDropTarget):
	"""Generic file drop target class.

	Protocol:
		Widgets being declared file drop targets
		must provide the method:

			add_filenames(filenames)
	"""
	#-----------------------------------------------
	def __init__(self, target):
		wx.FileDropTarget.__init__(self)
		self.target = target
	#-----------------------------------------------
	def OnDropFiles(self, x, y, filenames):
		self.target.add_filenames(filenames)
# ========================================================================
def gm_SingleChoiceDialog(aMessage = None, aTitle = None, aLogLevel = None, choices = None):
    if aMessage is None:
        aMessage = _('programmer forgot to specify info message')

    if aLogLevel is not None:
        log_msg = aMessage.replace('\015', ' ').replace('\012', ' ')
        _log.Log(aLogLevel, log_msg)

    if aTitle is None:
        aTitle = _('generic single choice dialog')

    dlg = wx.SingleChoiceDialog (
        parent = None,
        message = aMessage,
        caption = aTitle,
        choices = choices,
        style = wx.OK | wx.CANCEL | wx.CENTRE
    )
    btn_pressed = dlg.ShowModal()
    dlg.Destroy()

    if btn_pressed == wx.ID_OK:
        return dlg.GetSelection()
    else:
        return False
#-------------------------------------------------------------------------
def gm_show_error(aMessage = None, aTitle = None, aLogLevel = None):
	if aMessage is None:
		aMessage = _('programmer forgot to specify error message')

	if aLogLevel is not None:
		log_msg = aMessage.replace('\015', ' ').replace('\012', ' ')
		_log.Log(aLogLevel, log_msg)

	aMessage += _("\n\nPlease consult the error log for all the gory details !")

	if aTitle is None:
		aTitle = _('generic error message')

	print "-" * len(aTitle)
	print aTitle
	print "-" * len(aTitle)
	print aMessage

	dlg = wx.MessageDialog (
		parent = None,
		message = aMessage,
		caption = aTitle,
		style = wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP
	)
	dlg.ShowModal()
	dlg.Destroy()
	return True
#-------------------------------------------------------------------------
def gm_show_info(aMessage = None, aTitle = None, aLogLevel = None):
	if aMessage is None:
		aMessage = _('programmer forgot to specify info message')

	if aLogLevel is not None:
		log_msg = aMessage.replace('\015', ' ').replace('\012', ' ')
		_log.Log(aLogLevel, log_msg)

	if aTitle is None:
		aTitle = _('generic info message')

	dlg = wx.MessageDialog (
		parent = None,
		message = aMessage,
		caption = aTitle,
		style = wx.OK | wx.ICON_INFORMATION | wx.STAY_ON_TOP
	)
	dlg.ShowModal()
	dlg.Destroy()
	return True
#-------------------------------------------------------------------------
def gm_show_warning(aMessage = None, aTitle = None, aLogLevel = None):
	if aMessage is None:
		aMessage = _('programmer forgot to specify warning')

	if aLogLevel is not None:
		log_msg = aMessage.replace('\015', ' ').replace('\012', ' ')
		_log.Log(aLogLevel, log_msg)

	if aTitle is None:
		aTitle = _('generic warning message')

	dlg = wx.MessageDialog (
		parent = None,
		message = aMessage,
		caption = aTitle,
		style = wx.OK | wx.ICON_EXCLAMATION | wx.STAY_ON_TOP
	)
	dlg.ShowModal()
	dlg.Destroy()
	return True
#-------------------------------------------------------------------------
def gm_show_question(aMessage = 'programmer forgot to specify question', aTitle = 'generic user question dialog', cancel_button=False):
	if cancel_button:
		style = wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION | wx.STAY_ON_TOP
	else:
		style = wx.YES_NO | wx.ICON_QUESTION | wx.STAY_ON_TOP

	dlg = wx.MessageDialog (
		None,
		aMessage,
		aTitle,
		style
	)
	btn_pressed = dlg.ShowModal()
	dlg.Destroy()

	if btn_pressed == wx.ID_YES:
		return True
	elif btn_pressed == wx.ID_NO:
		return False
	else:
		return None
#-------------------------------------------------------------------------
def gm_statustext(aMessage=None, aLogLevel=None, beep=True):

	print "***** gm_statustext deprecated *****"
	gmDispatcher.send(gmSignals.statustext(), msg=aMessage, loglevel=aLogLevel, beep=beep)
	return True
#-------------------------------------------------------------------------
def get_dbowner_connection(procedure=None, dbo_password=None):
	if procedure is None:
		procedure = _('<restricted procedure>')

	# 1) get password for gm-dbo
	if dbo_password is None:
		pwd_gm_dbo = wx.GetPasswordFromUser (
			message = _("""
 [%s]

This is a restricted procedure. We need the
password for the GNUmed database owner.

Please enter the password for <gm-dbo>:""") % procedure,
			caption = procedure
		)
		if pwd_gm_dbo == '':
			return None
	else:
		pwd_gm_dbo = dbo_password

	# 2) connect as gm-dbo
	login = gmPG2.get_default_login()
	dsn = gmPG2.make_psycopg2_dsn(database=login.database, host=login.host, port=login.port, user='gm-dbo', password=pwd_gm_dbo)
	try:
		conn = gmPG2.get_connection(dsn=dsn, readonly=False, verbose=True, pooled=False)
	except:
		_log.LogException('cannot connect')
		gm_show_error (
			aMessage = _('Cannot connect as the GNUmed database owner <gm-dbo>.'),
			aTitle = procedure,
			aLogLevel = gmLog.lErr
		)
		return None

	return conn
#----------------------------------------------------------------------
def makePageTitle(wizPg, title):
	"""
	Utility function to create the main sizer of a wizard's page.
	
	@param wizPg The wizard page widget
	@type wizPg A wx.WizardPageSimple instance	
	@param title The wizard page's descriptive title
	@type title A StringType instance		
	"""
	sizer = wx.BoxSizer(wx.VERTICAL)
	wizPg.SetSizer(sizer)
	title = wx.StaticText(wizPg, -1, title)
	title.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
	sizer.Add(title, 0, wx.ALIGN_CENTRE|wx.ALL, 2)
	sizer.Add(wx.StaticLine(wizPg, -1), 0, wx.EXPAND|wx.ALL, 2)
	return sizer	
#============================================================
import string			# remove !

class cTextWidgetValidator(wx.PyValidator):
	"""
	This validator is used to ensure that the user has entered any value
	into the input object (wx.TextControl, gmPhraseWheel, gmDateInput,
	wx.Combo). Any wx.Window control with a GetValue method returning
	a StringType.
	"""
	#--------------------------------------------------------
	def __init__(self, message=None, non_empty=True, only_digits=False):
		"""
		Standard constructor, defining the behaviour of the validator.
		@param non_empty - When true, the input text control must be filled
		@type non_empty - BooleanType
		
		@param only_digits - When true, only digits are valid entries
		@type only_digits - BooleanType
		"""
		wx.PyValidator.__init__(self)

		self.__non_empty = non_empty
		self.__only_digits = only_digits
		if message is None:
			if self.__only_digits:
				self.__msg = _('This field can only contain digits.')
			else:
				self.__msg = _('This field cannot be empty.')
		else:
			self.__msg = message

		if self.__only_digits:
			wx.EVT_CHAR(self, self.OnChar)
	#--------------------------------------------------------
	def Clone(self):
		"""
		Standard cloner.
		Note that every validator must implement the Clone() method.
		"""
		return cTextWidgetValidator(self.__non_empty, self.__only_digits)
	#--------------------------------------------------------
	def Validate(self, parent = None):
		"""Validate the contents of the given text control."""
		ctrl = self.GetWindow()
		val = ctrl.GetValue()

		if self.__non_empty and val.strip() == '':
			print self.__msg
			ctrl.SetBackgroundColour('pink')
			ctrl.SetFocus()
			ctrl.Refresh()
			return False
		elif self.__only_digits:
			for char in val:
				if not char in string.digits:
					print self.__msg
					ctrl.SetBackgroundColour('pink')
					ctrl.SetFocus()
					ctrl.Refresh()					
					return False
		else:
			ctrl.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
			ctrl.Refresh()
			return True
	#--------------------------------------------------------
	def TransferToWindow(self):
		""" Transfer data from validator to window.
		The default implementation returns False, indicating that an error
		occurred.  We simply return True, as we don't do any data transfer.
		"""
		return True # Prevent wxDialog from complaining.	
	#--------------------------------------------------------
	def TransferFromWindow(self):
		""" Transfer data from window to validator.
		The default implementation returns False, indicating that an error
		occurred.  We simply return True, as we don't do any data transfer.
		"""
		# FIXME: workaround for Validate to be called when clicking a wizard's
		# Finish button
		return self.Validate()
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def OnChar(self, event):
		"""
		Callback function invoked on key press.
		
		@param event - The event object containing context information
		@type event - wx.Event
		"""
		key = event.GetKeyCode()
		if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
			event.Skip()
			return
		if self.__only_digits and chr(key) in string.digits:
			event.Skip()
			return

		if not wx.Validator_IsSilent():
			wx.Bell()

		# Returning without calling event.Skip eats the event
		# before it gets to the text control
		return

# ========================================================================
# $Log: gmGuiHelpers.py,v $
# Revision 1.59  2007-05-14 08:36:13  ncq
# - in c2ButtonQuestionDlg make keyword show_checkbox option defaulting to False
#
# Revision 1.58  2007/05/11 14:15:59  ncq
# - display help desk in exception handler
# - properly handle keep running/close client buttons
#
# Revision 1.57  2007/05/08 16:04:40  ncq
# - add wxPython based exception display handler
#
# Revision 1.56  2007/04/27 13:28:48  ncq
# - implement c2ButtonQuestionDlg
#
# Revision 1.55  2007/04/23 01:06:42  ncq
# - add password argument to get_dbowner_connection()
#
# Revision 1.54  2007/04/11 20:41:58  ncq
# - remove gm_icon()
#
# Revision 1.53  2007/04/09 22:02:40  ncq
# - fix docstring
#
# Revision 1.52  2007/03/18 14:07:14  ncq
# - factor out hook script running
#
# Revision 1.51  2007/03/02 15:32:56  ncq
# - turn gm_statustext() into signal sender with depreciation
#   warning (should used gmDispatcher.send() now)
#
# Revision 1.50  2007/02/19 16:13:36  ncq
# - add run_hook_script()
#
# Revision 1.49  2007/02/18 16:57:38  ncq
# - make sure gm-dbo connections aren't returned from the pool
#
# Revision 1.48  2007/01/20 22:52:27  ncq
# - .KeyCode -> GetKeyCode()
#
# Revision 1.47  2007/01/16 13:59:51  ncq
# - protect against empty trees in expansion history mixin
#
# Revision 1.46  2007/01/15 13:04:25  ncq
# - c3ButtonQuestionDlg
# - remove cReturnTraversalTextCtrl
#
# Revision 1.45  2007/01/13 22:43:41  ncq
# - remove str() raising Unicode exceptions
#
# Revision 1.44  2007/01/13 22:19:37  ncq
# - cTreeExpansionHistoryMixin
#
# Revision 1.43  2007/01/12 13:09:46  ncq
# - cFileDropTarget
#
# Revision 1.42  2006/12/15 15:24:06  ncq
# - cleanup
#
# Revision 1.41  2006/11/24 09:53:24  ncq
# - gm_beep_statustext() -> gm_statustext(beep=True)
#
# Revision 1.40  2006/11/05 14:18:57  ncq
# - missing "style ="
#
# Revision 1.39  2006/10/24 13:23:31  ncq
# - use gmPG2.get_default_login() in get_dbowner_connection()
#
# Revision 1.38  2006/10/08 11:03:09  ncq
# - convert to gmPG2
#
# Revision 1.37  2006/09/03 11:29:30  ncq
# - add cancel_button argument to show_question
#
# Revision 1.36  2006/08/01 22:03:49  ncq
# - cleanup
#
# Revision 1.35  2006/06/20 09:42:42  ncq
# - cTextObjectValidator -> cTextWidgetValidator
# - add custom invalid message to text widget validator
# - variable renaming, cleanup
# - fix demographics validation
#
# Revision 1.34  2006/06/17 16:42:48  ncq
# - add get_dbowner_connection()
#
# Revision 1.33  2006/05/01 18:47:32  ncq
# - cleanup
#
# Revision 1.32  2006/01/15 13:19:16  shilbert
# - gm_SingleChoiceDialog was added
# - wxpython 2.6 does not support client data associated with item
#
# Revision 1.31  2005/10/27 21:37:29  shilbert
# fixed wxYES|NO into wx.YES|NO
#
# Revision 1.30  2005/10/11 21:14:10  ncq
# - remove out-of-place LogException() call
#
# Revision 1.29  2005/10/09 08:07:56  ihaywood
# a textctrl that uses return for navigation wx 2.6 only
#
# Revision 1.28  2005/10/04 13:09:49  sjtan
# correct syntax errors; get soap entry working again.
#
# Revision 1.27  2005/10/04 00:04:45  sjtan
# convert to wx.; catch some transitional errors temporarily
#
# Revision 1.26  2005/09/28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.25  2005/09/28 15:57:48  ncq
# - a whole bunch of wx.Foo -> wx.Foo
#
# Revision 1.24  2005/09/26 18:01:50  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.23  2005/09/12 15:09:42  ncq
# - cleanup
#
# Revision 1.22  2005/06/10 16:11:14  shilbert
# szr.AddWindow() -> Add() such that wx2.5 works
#
# Revision 1.21  2005/06/08 01:27:50  cfmoro
# Validator fix
#
# Revision 1.20  2005/05/05 06:27:52  ncq
# - add wx.STAY_ON_TOP in an effort to keep popups up front
#
# Revision 1.19  2005/04/24 14:48:57  ncq
# - improved wording
#
# Revision 1.18  2005/04/10 12:09:16  cfmoro
# GUI implementation of the first-basic (wizard) page for patient details input
#
# Revision 1.17  2005/03/06 09:21:08  ihaywood
# stole a couple of icons from Richard's demo code
#
# Revision 1.16  2004/12/21 21:00:35  ncq
# - if no status text handler available, dump to stdout
#
# Revision 1.15  2004/12/21 19:40:56  ncq
# - fix faulty LogException() usage
#
# Revision 1.14  2004/09/25 13:10:40  ncq
# - in gm_beep_statustext() make aMessage a defaulted keyword argument
#
# Revision 1.13  2004/08/19 13:56:51  ncq
# - added gm_show_warning()
#
# Revision 1.12  2004/08/18 10:18:42  ncq
# - added gm_show_info()
#
# Revision 1.11  2004/05/28 13:30:27  ncq
# - set_status_text -> _set_status_text so nobody
#   gets the idea to use it directly
#
# Revision 1.10  2004/05/26 23:23:35  shilbert
# - import statement fixed
#
# Revision 1.9  2004/04/11 10:10:56  ncq
# - cleanup
#
# Revision 1.8  2004/04/10 01:48:31  ihaywood
# can generate referral letters, output to xdvi at present
#
# Revision 1.7  2004/03/04 19:46:54  ncq
# - switch to package based import: from Gnumed.foo import bar
#
# Revision 1.6  2003/12/29 16:49:18  uid66147
# - cleanup, gm_beep_statustext()
#
# Revision 1.5  2003/11/17 10:56:38  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:39  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.4  2003/08/26 12:35:52  ncq
# - properly replace \n\r
#
# Revision 1.3  2003/08/24 09:15:20  ncq
# - remove spurious self's
#
# Revision 1.2  2003/08/24 08:58:07  ncq
# - use gm_show_*
#
# Revision 1.1  2003/08/21 00:11:48  ncq
# - adds some widely used wxPython GUI helper functions
#
