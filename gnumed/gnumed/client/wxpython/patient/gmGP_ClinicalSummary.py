from wxPython.wx import *
#from wxPython.stc import *
import gmGuiElement_DividerCaptionPanel        #panel class to display sub-headings or divider headings 
import gmGuiElement_AlertCaptionPanel          #panel to hold flashing
import gmPlugin
#--------------------------------------------------------------------
# A class for displaying a summary of patients clinical data in the
# form of a social history, family history, active problems, habits
# risk factos and an inbox
# This code is shit and needs fixing, here for gui development only
# TODO:almost everything
#--------------------------------------------------------------------	


ID_OVERVIEW = wxNewId ()
ID_OVERVIEWMENU = wxNewId ()

class ClinicalSummary(wxPanel):
    def __init__(self, parent,id):
	wxPanel.__init__(self,parent,id,wxDefaultPosition,wxDefaultSize,style = wxRAISED_BORDER)
	#------------------------------------------------------------------------
	#import social history if available this will be the top item on the page
	#------------------------------------------------------------------------
	try: 
	     import gmGP_SocialHistory
	     self.socialhistory = gmGP_SocialHistory.SocialHistory(self,-1)
	     
	except:
	     pass
	##------------------------------------------------------------------------
	##import social history if available this will be the top item on the page
	##------------------------------------------------------------------------
        try:                                                      
	     import gmGP_FamilyHistorySummary
	     self.familyhistorysummary = gmGP_FamilyHistorySummary.FamilyHistorySummary(self,-1)
	     
	except:
	     pass
        #---------------------------------------
	#import active problem list if available 
	#---------------------------------------

	try:                                                        
	     import gmGP_ActiveProblems
	     self.activeproblemlist = gmGP_ActiveProblems.ActiveProblems(self,-1)
	     
	except:
	     pass	       
	 
	#------------------------------
	#import habits and risk factors
	#------------------------------
        try:                                                        
	     import gmGP_HabitsRiskFactors
	     self.habitsriskfactors = gmGP_HabitsRiskFactors.HabitsRiskFactors(self,-1)
	     
	except:
	     pass
	
	#------------
	#import inbox
	#------------
        try:                                                        
	     import gmGP_Inbox
	     self.inbox = gmGP_Inbox.Inbox(self,-1)
	     
	except:
	     pass
	 
	self.heading1 = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,_("Active Problems" ))                         
        self.heading2 = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,_("     Habits            Risk Factors"))
	self.heading3 = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,_("Inbox"))
        self.alertpanel = gmGuiElement_AlertCaptionPanel.AlertCaptionPanel(self,-1,_("   Alerts   "))
	#------------------------------------------------------------ 
	#now that we have all the elements, construct the whole panel
	#------------------------------------------------------------
	self.sizer= wxBoxSizer(wxVERTICAL)
	self.sizer.Add(self.socialhistory,5,wxEXPAND)
	self.sizer.Add(self.familyhistorysummary,5,wxEXPAND)
	self.sizer.Add(self.heading1,0,wxEXPAND)   
	self.sizer.Add(self.activeproblemlist,8,wxEXPAND)
	self.sizer.Add(self.heading2,0,wxEXPAND)  
	self.sizer.Add(self.habitsriskfactors,5,wxEXPAND)
	self.sizer.Add(self.heading3,0,wxEXPAND)  
	self.sizer.Add(self.inbox,5,wxEXPAND)
	self.sizer.Add(self.alertpanel,0,wxEXPAND)
        self.SetSizer(self.sizer)                         #set the sizer 
	self.sizer.Fit(self)                              #set to minimum size as calculated by sizer
        self.SetAutoLayout(true)                     #tell frame to use the sizer
        self.Show(true) 

class gmGP_ClinicalSummary (gmPlugin.wxPatientPlugin):
	"""
	Plugin to encapsulate the clinical summary
	"""

	__icons = {
0: 'x\xda\xa5\x8c\xb1\n\xc3 \x10\x86\xf7<\xc5\x81\x06\x0b\xc2\xa1\x04JGI!c\x1c\
\xb2\xb8\x86\xd0\xa9\xa1\xf6\xfd\xa7zgQK;\xb4\xf4\xff]\xbe\xef\xbc;\xecw\xdb\
-\xca\x1e\x81\x9e\x01\xab\xbauQ\x08\x1b\x8c\xfb\xba]\x99B"1\x18*\xb3&\x9e8\
\xcc=\xf1\xc9P\x99#\xb11e.\xf3\x9c\xc2\xec\x88\xcf\x03\x95Y\xe4{e\x0e\x89\
\xe7x\xbb0\xf8|\xac\x1c\x07l\x12\x00\x9e2\xfa\xd2*\xab\xf3U\xea\x12\xd7J\xfc\
 \x11\xb5\x90\xbd\x94\xaf?\x7f[\x97\xe2\x8f\xf5\xb4\xfc\xd5\xfa\xbb\x0c\xae\
\xa6\xfe\x0cMX\xe2\x03\x87\xf0k1'
}

	def name (self):
		return 'Clinical Summary'

	def MenuInfo (self):
		return ('view', '&Summary')

	def GetIconData(self, anIconID = None):
		if anIconID == None:
			return self.__icons[0]
		else:
			if self.__icons.has_key(anIconID):
				return self.__icons[anIconID]
			else:
				return self.__icons[0]

	def GetWidget (self, parent):
		return ClinicalSummary (parent, -1)

	def register (self):
		gmPlugin.wxPatientPlugin.register (self)
		self.gb['patient.manager'].SetDefault ('Clinical Summary')
#----------------------------------------------------------------------
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (400, 500))
	app.SetWidget(ClinicalSummary, -1)
	app.MainLoop()
