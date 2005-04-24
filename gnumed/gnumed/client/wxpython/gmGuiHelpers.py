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
# $Id: gmGuiHelpers.py,v 1.19 2005-04-24 14:48:57 ncq Exp $
__version__ = "$Revision: 1.19 $"
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"

import sys, string, os

if __name__ == '__main__':
	sys.exit("This is not intended to be run standalone !")

from wxPython.wx import *

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

	dlg = wxMessageDialog (
		parent = NULL,
		message = aMessage,
		caption = aTitle,
		style = wxOK | wxICON_ERROR
	)
	dlg.ShowModal()
	dlg.Destroy()
	return True
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

	dlg = wxMessageDialog (
		parent = NULL,
		message = aMessage,
		caption = aTitle,
		style = wxOK | wxICON_INFORMATION
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

	dlg = wxMessageDialog (
		parent = NULL,
		message = aMessage,
		caption = aTitle,
		style = wxOK | wxICON_EXCLAMATION
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

	dlg = wxMessageDialog(
		NULL,
		aMessage,
		aTitle,
		wxYES_NO | wxICON_QUESTION
	)
	btn_pressed = dlg.ShowModal()
	dlg.Destroy()

	if btn_pressed == wxID_YES:
		return True
	else:
		return False
#-------------------------------------------------------------------------
def gm_beep_statustext(aMessage=None, aLogLevel=None):
	if aMessage is None:
		aMessage = _('programmer forgot to specify alert message')

	if aLogLevel is not None:
		log_msg = string.replace(aMessage, '\015', ' ')
		log_msg = string.replace(log_msg, '\012', ' ')
		_log.Log(aLogLevel, log_msg)

	wxBell()

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
	img = wxImage(fname, wxBITMAP_TYPE_ANY)
	return wxBitmapFromImage(img)
#----------------------------------------------------------------------
def makePageTitle(wizPg, title):
	"""
	Utility function to create the main sizer of a wizard's page.
	
	@param wizPg The wizard page widget
	@type wizPg A wxWizardPageSimple instance	
	@param title The wizard page's descriptive title
	@type title A StringType instance		
	"""
	sizer = wxBoxSizer(wxVERTICAL)
	wizPg.SetSizer(sizer)
	title = wxStaticText(wizPg, -1, title)
	title.SetFont(wxFont(10, wxSWISS, wxNORMAL, wxBOLD))
	sizer.AddWindow(title, 0, wxALIGN_CENTRE|wxALL, 2)
	sizer.AddWindow(wxStaticLine(wizPg, -1), 0, wxEXPAND|wxALL, 2)
	return sizer	
#============================================================
class cTextObjectValidator(wxPyValidator):
	"""
	This validator is used to ensure that the user has entered any value
	into the input object (wxTextControl, gmPhraseWheel, gmDateInput,
	wxCombo). Any wxWindow control with a GetValue method returning
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
		wxPyValidator.__init__(self)
		
		self.__required = required
		self.__only_digits = only_digits
		if self.__only_digits:
			EVT_CHAR(self, self.OnChar)
	#--------------------------------------------------------
	def Clone(self):
		"""
		Standard cloner.
		Note that every validator must implement the Clone() method.
		"""
		return cTextObjectValidator(self.__required, self.__only_digits)
	#--------------------------------------------------------
	def Validate(self):
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
			wxSystemSettings_GetColour(wxSYS_COLOUR_WINDOW))
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
		@type event - wxEvent
		"""
		key = event.KeyCode()
		if key < WXK_SPACE or key == WXK_DELETE or key > 255:
			event.Skip()
			return
		if self.__only_digits and chr(key) in string.digits:
			event.Skip()
			return

		if not wxValidator_IsSilent():
			wxBell()

		# Returning without calling even.Skip eats the event before it
		# gets to the text control
		return			
# ========================================================================
# $Log: gmGuiHelpers.py,v $
# Revision 1.19  2005-04-24 14:48:57  ncq
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
