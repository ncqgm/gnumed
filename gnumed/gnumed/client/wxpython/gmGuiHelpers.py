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
# $Id: gmGuiHelpers.py,v 1.32 2006-01-15 13:19:16 shilbert Exp $
__version__ = "$Revision: 1.32 $"
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"

import sys, string, os

if __name__ == '__main__':
	sys.exit("This is not intended to be run standalone !")

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

from Gnumed.pycommon import gmLog, gmGuiBroker
_log = gmLog.gmDefLog
_log.Log(gmLog.lData, __version__)

_set_status_text = None
# ========================================================================
def gm_show_error(aMessage = None, aTitle = None, aLogLevel = None):
	if aMessage is None:
		aMessage = _('programmer forgot to specify error message')

	if aLogLevel is not None:
		log_msg = string.replace(aMessage, '\015', ' ')
		log_msg = string.replace(log_msg, '\012', ' ')
		_log.Log(aLogLevel, log_msg)

	aMessage = str(aMessage) + _("\n\nPlease consult the error log for all the gory details !")

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
def gm_SingleChoiceDialog(aMessage = None, aTitle = None, aLogLevel = None, choices = None):
    if aMessage is None:
        aMessage = _('programmer forgot to specify info message')

    if aLogLevel is not None:
        log_msg = string.replace(aMessage, '\015', ' ')
        log_msg = string.replace(log_msg, '\012', ' ')
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
def gm_show_info(aMessage = None, aTitle = None, aLogLevel = None):
	if aMessage is None:
		aMessage = _('programmer forgot to specify info message')

	if aLogLevel is not None:
		log_msg = string.replace(aMessage, '\015', ' ')
		log_msg = string.replace(log_msg, '\012', ' ')
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
		log_msg = string.replace(aMessage, '\015', ' ')
		log_msg = string.replace(log_msg, '\012', ' ')
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
def gm_show_question(aMessage = None, aTitle = None):
	# sanity checks
	if aMessage is None:
		aMessage = _('programmer forgot to specify question')
	if aTitle is None:
		aTitle = _('generic user question dialog')

	dlg = wx.MessageDialog(
		None,
		aMessage,
		aTitle,
		wx.YES_NO | wx.ICON_QUESTION | wx.STAY_ON_TOP
	)
	btn_pressed = dlg.ShowModal()
	dlg.Destroy()

	if btn_pressed == wx.ID_YES:
		return True
	else:
		return False
#-------------------------------------------------------------------------
# FIXME: actually make this use a signal !
def gm_beep_statustext(aMessage=None, aLogLevel=None):
	if aMessage is None:
		aMessage = _('programmer forgot to specify alert message')

	if aLogLevel is not None:
		log_msg = string.replace(aMessage, '\015', ' ')
		log_msg = string.replace(log_msg, '\012', ' ')
		_log.Log(aLogLevel, log_msg)

	wx.Bell()

	# only now and here can we assume that wxWindows
	# is sufficiently initialized
	global _set_status_text
	if _set_status_text is None:
		try:
			_set_status_text = gmGuiBroker.GuiBroker()['main.statustext']
		except KeyError:
			_log.LogException('called too early, cannot set status text', sys.exc_info(), verbose=0)
			print "Status message:", aMessage
			return 1

	_set_status_text(aMessage)
	return 1
#------------------------------------------------------------------------
def gm_icon (name):
	"""
	Returns a icon based on the name
	Hint: run names through gettext ()
	"""
	fname = os.path.join(gmGuiBroker.GuiBroker ()['gnumed_dir'], 'bitmaps', '%s.png' % name)
	img = wx.Image(fname, wx.BITMAP_TYPE_ANY)
	return wx.BitmapFromImage(img)
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
class cTextObjectValidator(wx.PyValidator):
	"""
	This validator is used to ensure that the user has entered any value
	into the input object (wx.TextControl, gmPhraseWheel, gmDateInput,
	wx.Combo). Any wx.Window control with a GetValue method returning
	a StringType.
	"""
	#--------------------------------------------------------
	def __init__(self, required = True, only_digits = False):
		"""
		Standard constructor, defining the behaviour of the validator.
		@param required - When true, the input text control must be filled
		@type required - BooleanType
		
		@param only_digits - When true, only digits are valid entries
		@type only_digits - BooleanType
		"""
		wx.PyValidator.__init__(self)
		
		self.__required = required
		self.__only_digits = only_digits
		if self.__only_digits:
			wx.EVT_CHAR(self, self.OnChar)
	#--------------------------------------------------------
	def Clone(self):
		"""
		Standard cloner.
		Note that every validator must implement the Clone() method.
		"""
		return cTextObjectValidator(self.__required, self.__only_digits)
	#--------------------------------------------------------
	def Validate(self, parent = None):
		"""
		Validate the contents of the given text control.
		"""
		textCtrl = self.GetWindow()
		text = textCtrl.GetValue()
		
		if len(text) == 0 and self.__required:
			msg = _('A text object must contain some text!')
			gm_show_error(msg, _('Required field'), gmLog.lErr)
			textCtrl.SetBackgroundColour('pink')
			textCtrl.SetFocus()
			textCtrl.Refresh()
			return False
		elif self.__only_digits:
			for char in text:
				if not char in string.digits:
					msg = _('A text object must contain only digits!')
					gm_show_error(msg, _('Numeric field'), gmLog.lErr)
					textCtrl.SetBackgroundColour('pink')
					textCtrl.SetFocus()
					textCtrl.Refresh()					
					return False
		else:
			textCtrl.SetBackgroundColour(
			wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
			textCtrl.Refresh()
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
		key = event.KeyCode()
		if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
			event.Skip()
			return
		if self.__only_digits and chr(key) in string.digits:
			event.Skip()
			return

		if not wx.Validator_IsSilent():
			wx.Bell()

		# Returning without calling even.Skip eats the event before it
		# gets to the text control
		return



class cReturnTraversalTextCtrl (wx.TextCtrl):
	"""
	Acts exactly like a plain TextCtrl except that RETURN also
	calls wxWindow.Navigate ()

	FIXME: detect 2.4 and then make self.Navigate a no-op
	"""


	def __init__ (self, *args):
		wx.TextCtrl.__init__ (self, *args)
		wx.EVT_TEXT_ENTER (self, self.GetId(), self.__on_enter)

	def __on_enter (self, event):
		self.Navigate ()
	
# ========================================================================
# $Log: gmGuiHelpers.py,v $
# Revision 1.32  2006-01-15 13:19:16  shilbert
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
