#!/usr/bin/env python

"""gmTalkback - the GNUmed talkback client.

This is a wxPython client for communicating errors back to
the developers. It is activated by the --talkback command
line argument.

Original code courtesy of David Guest.

@license: GPL
"""
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/Attic/gmTalkback.py,v $
__version__ = "$Revision: 1.12 $"
__author__  = "D. Guest <dguest@zeeclor.mine.nu>,\
			   K. Hilbert <Karsten.Hilbert@gmx.net>"

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

#  talkback
ID_BUTTON_CANCEL = wx.NewId()
ID_BUTTON_SEND = wx.NewId()
#=========================================================================
class cTalkbackFrame(wx.Frame):
	def __init__(self, *args, **kwds):
		kwds["style"] = wx.CAPTION|wx.MINIMIZE_BOX|wx.MAXIMIZE_BOX|wx.SYSTEM_MENU|wx.RESIZE_BORDER
		wx.Frame.__init__(self, *args, **kwds)
		self.szr_main = wx.BoxSizer(wx.VERTICAL)

		self.szr_btns = wx.BoxSizer(wx.HORIZONTAL)
		self.btn_CANCEL = wx.Button(self, ID_BUTTON_CANCEL, _("Don't send"), size=(-1, -1))
		self.btn_SEND = wx.Button(self, ID_BUTTON_SEND, _("Send"), size=(-1, -1))

		self.szr_adr = wx.BoxSizer(wx.HORIZONTAL)
		self.field_to = wx.TextCtrl(self, -1, "fixme@gnumed.net", size=(-1, -1), style=0)
		self.label_to = wx.StaticText(self, -1, _("Send to"), size=(-1, -1), style=wx.ALIGN_RIGHT)
		self.field_from = wx.TextCtrl(self, -1, "", size=(-1, -1), style=0)
		self.label_from = wx.StaticText(self, -1, _("Your email address"), size=(-1, -1), style=wx.ALIGN_RIGHT)

		self.szr_desc = wx.BoxSizer(wx.HORIZONTAL)
		self.field_desc = wx.TextCtrl(self, -1, _("I hit the big red button and ..."), size=(-1, -1), style=wx.TE_MULTILINE)
		self.label_desc = wx.StaticText(self, -1, _("Description/  \nComment  "), size=(-1, -1), style=wx.ALIGN_RIGHT)

		self.szr_hint = wx.BoxSizer(wx.HORIZONTAL)
		self.label_hint = wx.StaticText(
			self,
			-1,
			_("An error occured in GnuMed. You can send a bug report from the window below."),
			size=(-1, -1),
			style=wx.ALIGN_CENTER
		)

		self.szr_title = wx.BoxSizer(wx.HORIZONTAL)
		self.label_title = wx.StaticText(
			self,
			-1,
			_("GnuMed Talkback Facility"),
			size=(-1, -1),
			style=wx.ALIGN_CENTER
		)

		wx.EVT_BUTTON(self, ID_BUTTON_CANCEL, self.onNoSend)
		wx.EVT_BUTTON(self, ID_BUTTON_SEND, self.onSend)

		self.__set_properties()
		self.__do_layout()
	#-----------------------------------------------
	def setLogger(self, aLogger):
		self.mail_logger = aLogger
	#-----------------------------------------------
	def __set_properties(self):
		self.SetTitle(_("GNUmed Talkback"))
		self.label_title.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.NORMAL, 0, ""))
	#-----------------------------------------------
	def __do_layout(self):
		self.szr_title.Add(self.label_title, 1, wx.BOTTOM|wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_HORIZONTAL|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
		self.szr_main.Add(self.szr_title, 1, wx.ALIGN_CENTER_HORIZONTAL, 0)

		self.szr_hint.Add(self.label_hint, 0, wx.RIGHT|wx.ALIGN_CENTER_HORIZONTAL|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 6)
		self.szr_main.Add(self.szr_hint, 1, wx.EXPAND, 0)

		self.szr_desc.Add(self.label_desc, 0, wx.ALIGN_RIGHT|wx.LEFT, 6)
		self.szr_desc.Add(self.field_desc, 3, wx.BOTTOM|wx.RIGHT|wx.EXPAND, 8)
		self.szr_main.Add(self.szr_desc, 3, wx.EXPAND, 0)

		self.szr_adr.Add(self.label_from, 0, wx.RIGHT|wx.ALIGN_RIGHT|wx.LEFT, 5)
		self.szr_adr.Add(self.field_from, 1, 0, 0)
		self.szr_adr.Add(self.label_to, 0, wx.RIGHT|wx.LEFT, 5)
		self.szr_adr.Add(self.field_to, 2, wx.RIGHT, 8)
		self.szr_main.Add(self.szr_adr, 1, wx.EXPAND, 0)

		self.szr_btns.Add(self.btn_CANCEL, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
		self.szr_btns.Add((20, 20), 0, wx.EXPAND, 0)
		self.szr_btns.Add(self.btn_SEND, 0, 0, 0)
		self.szr_main.Add(self.szr_btns, 1, wx.ALIGN_CENTER_HORIZONTAL, 0)

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
class cTalkbackApp(wx.App):
	def OnInit(self):
		self.frame = cTalkbackFrame(None, -1, "GNUmed Talks Back", wx.DefaultPosition, size=wx.Size(-1,-1), style= wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE)
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
# Revision 1.12  2005-10-28 08:12:48  shilbert
# - fix more wx.Foo vs. wxFoo instances
#
# Revision 1.11  2005/09/28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.10  2005/09/28 15:57:48  ncq
# - a whole bunch of wx.Foo -> wx.Foo
#
# Revision 1.9  2005/09/26 18:01:51  ncq
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
