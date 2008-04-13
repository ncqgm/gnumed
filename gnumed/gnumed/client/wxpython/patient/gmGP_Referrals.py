#############################################################################
# This panel is the gui frontend to allow choice of person to
# refer to by name, company or category
#
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/patient/gmGP_Referrals.py,v $
# $Id: gmGP_Referrals.py,v 1.14 2008-04-13 14:39:49 ncq Exp $
__version__ = "$Revision: 1.14 $"
__author__ = "R.Terry, I.Haywood"

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

from Gnumed.wxpython import gmGuiElement_HeadingCaptionPanel, gmGuiElement_DividerCaptionPanel, gmGuiElement_AlertCaptionPanel, gmEditArea, gmPlugin_Patient
from Gnumed.wxpython.gmPatientHolder import PatientHolder

ID_REFERRALDATE = wxNewId()

#==============================================================
class ReferralsPanel (wxPanel, PatientHolder):
	def __init__(self,parent, id):
		PatientHolder.__init__(self)

		wxPanel.__init__(self, parent, id,wxDefaultPosition,wxDefaultSize,wxRAISED_BORDER)
		self.SetBackgroundColour(wxColor(222,222,222))
		# top heading
		self.referralspanelheading = gmGuiElement_HeadingCaptionPanel.HeadingCaptionPanel(self,-1,_("     REFERRALS     "))
		#----------------------------------
		# put date at top - allow backdating
		# FIXME remove the fixed date below
		# FIXME use gmDateTimeInput
		# FIXME shouldn't this be part of the editarea proper ?
		#----------------------------------
		szr_top = wxBoxSizer(wxHORIZONTAL)
		self.txt_referraldate = wxTextCtrl(self,ID_REFERRALDATE,"12/06/2002",wxDefaultPosition,wxDefaultSize)
		spacer_top = wxWindow(self, -1, wxDefaultPosition, wxDefaultSize, 0)
		spacer_top.SetBackgroundColour(wxColor(222,222,222))
		szr_top.Add(spacer_top, 6, wxEXPAND)
		szr_top.Add(self.txt_referraldate, 1, wxEXPAND|wxALL, 2)
		szr_top.Add(10, 0, 0)
		# create referrals specific editarea
		self.editarea = gmEditArea.gmReferralEditArea(self, -1)
		# add elements to the main background sizer
		self.szr_main = wxBoxSizer(wxVERTICAL)
		self.szr_main.Add(self.referralspanelheading, 0, wxEXPAND)
		self.szr_main.Add(0, 5, 0)
		self.szr_main.Add(szr_top, 0, wxEXPAND)
		self.szr_main.Add(self.editarea, 10, wxEXPAND)
		self.SetSizer(self.szr_main)
		self.SetAutoLayout(True)
		self.Show(True)

#==============================================================
class gmGP_Referrals (gmPlugin_Patient.wxPatientPlugin):
	"""
	Plugin to encapsulate the referrals window
	"""
	__icons = {
"""icon_outgoing_letter""": "x\xda]\xcd;\x0e\x830\x10\x04\xd0\x9eSXJ\xe1T+\\$r\x9dH.\xe3\x82f[\x84R\x05e\
r\xff*\xbb\xb6\xf1\x87\x11B\xccc\x0c\xd7\xfd\xe7\xa6\xc5\xba\xbb\x91\xebf\
\x9c\x9d\xd6\xc5\xc2l\xe6\xb1\xaf\xdb'5\x92v\xf1\xb3&u#\xfd\x85\xef;\x15\xd6\
\x97\xc1\x87g\xf0\xa9G\xed\xf3\\\xbb\xc9!.\x0f\x1d\x12\x1d\xda\x90\xa8jE\xa2\
\xa6m\t!\x9c\x96`\xddaX\x82\x13f-(\x96Q\x94\x0b\x02\xb1`\x04*\xb2*\xabq\x87\
\x8c\x1c\x1e1-G\xcc6\x1eG\x8c\xf2Q\xb9\xf5?\xeas \x0fQ\xa4?:Rj{",

"""icon_writing_pen""": 'x\xda\x8d\x901\x0b\xc3 \x10\x85\xf7\xfc\x8a\x83\x0e\x16\x02\x8ff\xa97+d\x8c\
C\x96[C\xe8\xd4P\xfb\xff\xa7\x1a\xb5P/\x85\xf6!\xc2\xf7\xdd\xbbA\xcf\xdbs\
\xe8f3\\)\x9dt\x99n\x99\rh%\xb7-\xeb=\x93$:Y\xb6\xder\xe6X\xf8\x92\x929\xec<\
\xf2\xe8+S\xe2)>n\x19\xfa}\xe8\xd8y\xc7u\xd8\xe6?\t\xe0 \x051BK\x04@\x94\x14\
\x049\xac#\xf4\x10%KQ\xc9Rle-\xb6\xb2\x16\xb5\xccE%\x01\xfa"?\xde\x8ew~\xfc\
\x12^\x04\x14P\xa7'
}

	def name (self):
		return 'Referrals'

	def MenuInfo (self):
		return ('view', '&Referrals') #FIXME fix the ampersand to a logical place in relationship to other buttons

	def GetIconData(self, anIconID = None):
		if anIconID == None:
			return self.__icons[_("""icon_writing_pen""")]
		else:
			if self.__icons.has_key(anIconID):
				return self.__icons[anIconID]
			else:
				return self.__icons[_("""icon_writing_pen""")]

	def GetWidget (self, parent):
		return  ReferralsPanel(parent, -1)

#==============================================================
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (600, 600))
	app.SetWidget(ReferralsPanel, -1)
	app.MainLoop()
#==============================================================
# $Log: gmGP_Referrals.py,v $
# Revision 1.14  2008-04-13 14:39:49  ncq
# - no more old style logging
#
# Revision 1.13  2005/09/26 18:01:53  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.12  2004/07/18 20:30:54  ncq
# - wxPython.true/false -> Python.True/False as Python tells us to do
#
# Revision 1.11  2004/06/25 13:28:00  ncq
# - logically separate notebook and clinical window plugins completely
#
# Revision 1.10  2004/03/10 14:16:47  ncq
# - readability, comments
#
# Revision 1.9  2004/03/10 12:56:01  ihaywood
# fixed sudden loss of main.shadow
# more work on referrals,
#
# Revision 1.8  2004/03/09 07:34:51  ihaywood
# reactivating plugins
#
# Revision 1.7  2003/11/17 10:56:42  sjtan
#
# synced and commiting.
#
# Revision 1.2  2003/10/25 08:29:40  sjtan
#
# uses gmDispatcher to send new currentPatient objects to toplevel gmGP_ widgets. Proprosal to use
# yaml serializer to store editarea data in  narrative text field of clin_root_item until
# clin_root_item schema stabilizes.
#
# Revision 1.1  2003/10/23 06:02:40  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.6  2003/02/02 13:34:28  ncq
# - cvs keyword metadata
#
# @change log:
#	    01.08.2002 rterry initial implementation, untested
