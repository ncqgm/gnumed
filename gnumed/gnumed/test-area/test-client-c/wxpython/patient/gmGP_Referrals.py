#!/usr/bin/python
#############################################################################
#
# gmGP_Referrals
# ----------------------------------
#
# This panel is the gui frontend to allow choice of person to refer to by name
# company or category
#
# @author: Dr. Richard Terry
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: wxPython (>= version 2.3.1)
# @change log:
#	    01.08.2002 rterry initial implementation, untested
#
# @TODO:almost everything
#	
#      
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/test-client-c/wxpython/patient/Attic/gmGP_Referrals.py,v $
# $Id: gmGP_Referrals.py,v 1.2 2003-10-25 08:29:40 sjtan Exp $
__version__ = "$Revision: 1.2 $"
__author__ = "R.Terry"

from wxPython.wx import *
import gmGuiElement_HeadingCaptionPanel		#panel class to display top headings
import gmGuiElement_DividerCaptionPanel		#panel class to display sub-headings or divider headings 
import gmGuiElement_AlertCaptionPanel		#panel to hold flashing alert messages
import gmEditArea             				#panel class holding editing prompts and text boxes
import gmPlugin, gmLog
from gmPatientHolder import PatientHolder


ID_REFERRALDATE = wxNewId ()
ID_REFERRALTXT  = wxNewId()
gmSECTION_REFERRALS = 11

requestprompts = {
1:("Category"),
2:("Name"),
3:("Organisation"),
4:("Street1"),
5:("Street2"),
6:("Street3"),
7:("Suburb"),		  
8:("Referral For"),
9:("Progress Notes"),
10:("Copy to"),
11:("Include"),
12:(""),		
13:("")
}

class ReferralsPanel (wxPanel, PatientHolder):
     def __init__(self,parent, id):
		wxPanel.__init__(self, parent, id,wxDefaultPosition,wxDefaultSize,wxRAISED_BORDER)
		PatientHolder.__init__(self)
		self.SetBackgroundColour(wxColor(222,222,222))
		#--------------------
		#add the main heading
		#--------------------
		self.referralspanelheading = gmGuiElement_HeadingCaptionPanel.HeadingCaptionPanel(self,-1,"     REFERRALS     ")
		#----------------------------------
		#put date at top - allow backdating
		#FIXME remove the date text below
		#----------------------------------
		self.sizer_top  = wxBoxSizer(wxHORIZONTAL)
		self.txt_referraldate = wxTextCtrl(self,ID_REFERRALDATE,"12/06/2002",wxDefaultPosition,wxDefaultSize)
		self.spacer = wxWindow(self,-1, wxDefaultPosition,wxDefaultSize,0) 
		self.spacer.SetBackgroundColour(wxColor(222,222,222))
		self.sizer_top.Add(self.spacer,6,wxEXPAND)
		self.sizer_top.Add(self.txt_referraldate,1,wxEXPAND|wxALL,2)
		self.sizer_top.Add(10,0,0)
		#---------------------------------------------
		#now create the editarea specific for referrals
		#---------------------------------------------
#		self.editarea = gmEditArea.EditArea(self,-1,requestprompts,gmSECTION_REFERRALS)
		self.editarea = gmEditArea.gmReferralEditArea(self, -1)
		#-----------------------------------------------------------------
		#add the divider headings for requests generated this consultation
		#-----------------------------------------------------------------
		self.referralsgenerated_subheading = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,_("Referral letter details"))
		self.sizer_referralsgenerated = wxBoxSizer(wxHORIZONTAL) 
		self.sizer_referralsgenerated.Add(self.referralsgenerated_subheading,1, wxEXPAND)
		#---------------------------------------------------------------------------------
		#control to write referral letter (expands to full size on double click or preview
		#FIXME ie someone should do this!
		#---------------------------------------------------------------------------------
		self.txt_referral_letter = wxTextCtrl(self, ID_REFERRALTXT,
	                "The gmGP_Referrals.py gui is a little contentious as those on the gnumed developers list will "
			"be aware. This is an interim version. The referral letter text would normally start here, not this"
			"comment. E.G:\n\n"
			"Thanks for assessing Bruce who has been complaining of severe retrosternal pains for 2 months, "
			"and trouble swallowing. He seems to have lost about 10Kg in weight, and his vomiting of blood "
			"would suggest possible carcinoma.\n \n"
			"I've explained the dd and he is expecting the worst.\n\n"
                        "Clicking the preview button would enlarge this text area to full left hand screen size"
                        "and have the practice header, name of person being referred to etc, and would still be editable."
                        "The letter is printed by clicking the currently non-existant print button on the menu bar above!" ,
		wxDefaultPosition,wxDefaultSize, style=wxTE_MULTILINE|wxNO_3D|wxSIMPLE_BORDER)
		self.txt_referral_letter.SetInsertionPoint(0)
		self.txt_referral_letter.SetFont(wxFont(12,wxSWISS, wxNORMAL, wxNORMAL, false, ''))
		#----------------------------------------
		#add an alert caption panel to the bottom
		#----------------------------------------
		self.alertpanel = gmGuiElement_AlertCaptionPanel.AlertCaptionPanel(self,-1,"  Alerts  ")
		#---------------------------------------------                                                                               
		#add all elements to the main background sizer
		#---------------------------------------------
		self.mainsizer = wxBoxSizer(wxVERTICAL)
		self.mainsizer.Add(self.referralspanelheading,0,wxEXPAND)
		self.mainsizer.Add(0,5,0)
		self.mainsizer.Add(self.sizer_top,0,wxEXPAND)
		self.mainsizer.Add(self.editarea,10,wxEXPAND)
		self.mainsizer.Add(self.referralsgenerated_subheading,0,wxEXPAND)
		self.mainsizer.Add(self.txt_referral_letter,6,wxEXPAND)
		self.mainsizer.Add(self.alertpanel,0,wxEXPAND)
		self.SetSizer(self.mainsizer)
		self.SetAutoLayout(true)
		self.Show(true)
	
#==============================================================		
class gmGP_Referrals (gmPlugin.wxPatientPlugin):
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
		return  ReferralsPanel (parent, -1)

#==============================================================
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (600, 600))
	app.SetWidget(ReferralsPanel, -1)
	app.MainLoop()
#==============================================================
# $Log: gmGP_Referrals.py,v $
# Revision 1.2  2003-10-25 08:29:40  sjtan
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
