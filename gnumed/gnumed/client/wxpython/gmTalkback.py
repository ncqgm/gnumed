#!/usr/bin/env python

"""gmTalkback - the GNUmed talkback client.

This is a wxPython client for communicating errors back to
the developers. It is activated by the --talkback command
line argument.

Original code courtesy of David Guest.

@license: GPL
"""
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/Attic/gmTalkback.py,v $
__version__ = "$Revision: 1.9 $"
__author__  = "D. Guest <dguest@zeeclor.mine.nu>,\
			   K. Hilbert <Karsten.Hilbert@gmx.net>"

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

#  talkback
ID_BUTTON_CANCEL = wxNewId()
ID_BUTTON_SEND = wxNewId()
#=========================================================================
class cTalkbackFrame(wxFrame):
	def __init__(self, *args, **kwds):
		kwds["style"] = wxCAPTION|wxMINIMIZE_BOX|wxMAXIMIZE_BOX|wxSYSTEM_MENU|wxRESIZE_BORDER
		wxFrame.__init__(self, *args, **kwds)
		self.szr_main = wxBoxSizer(wxVERTICAL)

		self.szr_btns = wxBoxSizer(wxHORIZONTAL)
		self.btn_CANCEL = wxButton(self, ID_BUTTON_CANCEL, _("Don't send"), size=(-1, -1))
		self.btn_SEND = wxButton(self, ID_BUTTON_SEND, _("Send"), size=(-1, -1))

		self.szr_adr = wxBoxSizer(wxHORIZONTAL)
		self.field_to = wxTextCtrl(self, -1, "fixme@gnumed.net", size=(-1, -1), style=0)
		self.label_to = wxStaticText(self, -1, _("Send to"), size=(-1, -1), style=wxALIGN_RIGHT)
		self.field_from = wxTextCtrl(self, -1, "", size=(-1, -1), style=0)
		self.label_from = wxStaticText(self, -1, _("Your email address"), size=(-1, -1), style=wxALIGN_RIGHT)

		self.szr_desc = wxBoxSizer(wxHORIZONTAL)
		self.field_desc = wxTextCtrl(self, -1, _("I hit the big red button and ..."), size=(-1, -1), style=wxTE_MULTILINE)
		self.label_desc = wxStaticText(self, -1, _("Description/  \nComment  "), size=(-1, -1), style=wxALIGN_RIGHT)

		self.szr_hint = wxBoxSizer(wxHORIZONTAL)
		self.label_hint = wxStaticText(
			self,
			-1,
			_("An error occured in GnuMed. You can send a bug report from the window below."),
			size=(-1, -1),
			style=wxALIGN_CENTER
		)

		self.szr_title = wxBoxSizer(wxHORIZONTAL)
		self.label_title = wxStaticText(
			self,
			-1,
			_("GnuMed Talkback Facility"),
			size=(-1, -1),
			style=wxALIGN_CENTER
		)

		EVT_BUTTON(self, ID_BUTTON_CANCEL, self.onNoSend)
		EVT_BUTTON(self, ID_BUTTON_SEND, self.onSend)

		self.__set_properties()
		self.__do_layout()
	#-----------------------------------------------
	def setLogger(self, aLogger):
		self.mail_logger = aLogger
	#-----------------------------------------------
	def __set_properties(self):
		self.SetTitle(_("GNUmed Talkback"))
		self.label_title.SetFont(wxFont(16, wxSWISS, wxNORMAL, wxNORMAL, 0, ""))
	#-----------------------------------------------
	def __do_layout(self):
		self.szr_title.Add(self.label_title, 1, wxBOTTOM|wxRIGHT|wxTOP|wxALIGN_CENTER_HORIZONTAL|wxLEFT|wxALIGN_CENTER_VERTICAL, 5)
		self.szr_main.Add(self.szr_title, 1, wxALIGN_CENTER_HORIZONTAL, 0)

		self.szr_hint.Add(self.label_hint, 0, wxRIGHT|wxALIGN_CENTER_HORIZONTAL|wxLEFT|wxALIGN_CENTER_VERTICAL, 6)
		self.szr_main.Add(self.szr_hint, 1, wxEXPAND, 0)

		self.szr_desc.Add(self.label_desc, 0, wxALIGN_RIGHT|wxLEFT, 6)
		self.szr_desc.Add(self.field_desc, 3, wxBOTTOM|wxRIGHT|wxEXPAND, 8)
		self.szr_main.Add(self.szr_desc, 3, wxEXPAND, 0)

		self.szr_adr.Add(self.label_from, 0, wxRIGHT|wxALIGN_RIGHT|wxLEFT, 5)
		self.szr_adr.Add(self.field_from, 1, 0, 0)
		self.szr_adr.Add(self.label_to, 0, wxRIGHT|wxLEFT, 5)
		self.szr_adr.Add(self.field_to, 2, wxRIGHT, 8)
		self.szr_main.Add(self.szr_adr, 1, wxEXPAND, 0)

		self.szr_btns.Add(self.btn_CANCEL, 0, wxALIGN_CENTER_HORIZONTAL, 0)
		self.szr_btns.Add((20, 20), 0, wxEXPAND, 0)
		self.szr_btns.Add(self.btn_SEND, 0, 0, 0)
		self.szr_main.Add(self.szr_btns, 1, wxALIGN_CENTER_HORIZONTAL, 0)

		self.SetAutoLayout(1)
		self.SetSizer(self.szr_main)
		self.szr_main.Fit(self)
	#-----------------------------------------------	
	def onNoSend(self,event):
		self.Close(True)
	#-----------------------------------------------
	def onSend(self, event):
		self.mail_logger.setFrom (self.field_from.GetValue())
		self.mail_logger.setTo ([self.field_to.GetValue(),])
		self.mail_logger.setComment (self.field_desc.GetValue())
		self.mail_logger.flush()
		self.Close(True)
#=========================================================================
class cTalkbackApp(wxApp):
	def OnInit(self):
		self.frame = cTalkbackFrame(NULL, -1, "GNUmed Talks Back", wxDefaultPosition, size=wxSize(-1,-1), style= wxDEFAULT_FRAME_STYLE|wxNO_FULL_REPAINT_ON_RESIZE)
		self.frame.Show (True)
		self.SetTopWindow(self.frame)
		return True
    #-----------------------------------------------
	def setLogger(self, aLogger):
		self.frame.setLogger(aLogger)
#=========================================================================
def run(aLogger):
	# run email logger window
	app = cTalkbackApp(0)
	app.setLogger(aLogger)
	app.MainLoop()
#=========================================================================
if __name__ == '__main__':
	_ = lambda x:x
	import sys
	sys.path.append("../pycommon/")
	import gmLog
	email_logger = gmLog.cLogTargetEMail(gmLog.lData, aFrom = "GNUmed client <ncq>", aTo = ("",), anSMTPServer = "localhost")
	gmLog.gmDefLog.AddTarget(email_logger)
	run(email_logger)

#=========================================================================
# $Log: gmTalkback.py,v $
# Revision 1.9  2005-09-26 18:01:51  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.8  2005/03/29 07:31:28  ncq
# - cleanup
#
# Revision 1.7  2004/07/18 20:30:54  ncq
# - wxPython.true/false -> Python.True/False as Python tells us to do
#
# Revision 1.6  2004/02/25 09:46:22  ncq
# - import from pycommon now, not python-common
#
# Revision 1.5  2003/11/17 10:56:39  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:40  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.4  2002/09/30 10:57:56  ncq
# - make GnuMed consistent spelling in user-visible strings
#
# Revision 1.3  2002/09/10 07:46:56  ncq
# - added changelog keyword
#
