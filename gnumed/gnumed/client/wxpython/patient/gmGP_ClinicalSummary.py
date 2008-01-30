try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

try:
	import cDividerCaption        #panel class to display sub-headings or divider headings
	import cAlertCaption          #panel to hold flashing
	import gmPlugin_Patient
	from gmPatientHolder import PatientHolder
	import gmDispatcher

except:
	print  "import error"
	sys.path.append('../')
	sys.path.append('../../pycommon')
	sys.path.append('../../business')
	import gmGuiElement_DividerCaptionPanel        #panel class to display sub-headings or divider headings
	import gmGuiElement_AlertCaptionPanel          #panel to hold flashing
	import gmPlugin_Patient
#--------------------------------------------------------------------
# A class for displaying a summary of patients clinical data in the
# form of a social history, family history, active problems, habits
# risk factos and an inbox
# This code is shit and needs fixing, here for gui development only
# TODO:almost everything
#--------------------------------------------------------------------

ID_OVERVIEW = wxNewId ()
ID_OVERVIEWMENU = wxNewId ()

class ClinicalSummary(wxPanel, PatientHolder):
	def __init__(self, parent,id):
		wxPanel.__init__(self,parent,id,wxDefaultPosition,wxDefaultSize,style = wxRAISED_BORDER)
		PatientHolder.__init__(self)
		#------------------------------------------------------------------------
		#import social history if available this will be the top item on the page
		#------------------------------------------------------------------------
		try:
			import gmGP_SocialHistory
			self.socialhistory = gmGP_SocialHistory.SocialHistory(self,-1)
		except:
			pass
		#------------------------------------------------------------------------
		#import social history if available this will be the top item on the page
		#------------------------------------------------------------------------
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
			sys.exit(0)
			pass

		self.heading1 = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,_("Active Problems" ))
		self.heading2 = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,_("     Habits            Risk Factors"))
		self.heading3 = gmGuiElement_DividerCaptionPanel.DividerCaptionPanel(self,-1,_("Inbox"))
		self.alertpanel = gmGuiElement_AlertCaptionPanel.AlertCaptionPanel(self,-1,_("   Alerts   "))
		#------------------------------------------------------------ 
		#now that we have all the elements, construct the whole panel
		#------------------------------------------------------------
		# FIXME: NO !! maybe we DON'T have all the elements ...
		self.sizer = wxBoxSizer(wxVERTICAL)
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
		self.SetAutoLayout(True)                     #tell frame to use the sizer
		self.Show(True) 
		gmDispatcher.connect(self._updateActiveProblemsUI, u'clin_history_updated')

	def _updateUI(self):
		self._updateActiveProblemsUI()

	def	_updateActiveProblemsUI(self):
		# remember wxCallAfter
		clinical = self.patient.get_emr().get_past_history()
		list = clinical.get_active_history()
		newList = []
		for id, v in list:
			newList.append( [id, clinical.short_format( v) ])
		self.activeproblemlist.SetData(newList, fitClientSize = 1)

#============================================================
class gmGP_ClinicalSummary (gmPlugin_Patient.wxPatientPlugin):
	"""Plugin to encapsulate the clinical summary.
	"""

	__icons = {
"""icon_clinical_summary""": "x\xda]\x93IS\xab@\x14\x85\xf7\xfe\n\xaaP\xf3J4\x05\xf4\x88SIC\xe3\xca\xb8H\
\x95e\xb9s\xc0Y\x89q\xf6\xd7?\xee\xb9mLrO6\xdfI\xf7\x9d\x80\x7f\x8f\x93le<\
\xc8t\xd4\xff\xb4\x8a\xb2\xc1\xca\xf9x\xf0\x19]F\xb1\xb7F\xa6\xcco\xc4\x95\
\xd5*\xcd\xc15q\x99\x15\xc22g\xc4\xb2&\x81\x87\xc4i\x1f2\x05\xdf\x10\x9b\\\
\x17\xca\x83\xbfq\xbf0B0\x9f\x11\x17N\xe9\x8c\xeb\xe5\xc4H'\xc1\x15\xcek]\n\
\xce\xb7Ol\x9d\x15\xa6\x04\x9f\xe0~\xa5lf\xc0/8_\x93\xc0-q\xd3\x98&\xe5\xfb\
\x92\x99\x02\xdc\x81\xbd\xd7\x15\xe7\xdb\n\xf9{\x81\xd70\x7f\xe3\xaaR\x83\r\
\xd8\xe8\xdf\xfd|\xa1\xbe\xb4\xd6p\xbd+\xb0\xd6Y\xce\xf3\x8d\x89\x1d\x02|\
\x8ez\xda\xb8\xd0\xcf3X\xd5\xbe\xe2y-\xea{\xd9d\x02\xdc\x10+\xa7\xa4\xe4\xfb\
\xab\xf8\xbf\xb0}A\xf0-\xf6\xe5u\x13\xfa\xb9\x04[]\x05\xde@\xfe\xda\xab\xaa\
\x00\xaf\xcf\x98\xe7\xfd@>%Ex\xbe%\xfa-I`\x85yj\x128\xc6\xf9\x94\x04\xbe\xe3\
\xfed!8\x7f\x8a\xe7\xedH\xe0{\xf4\xe3\xb4\x0f\xfd\x8cx\x9f\xda\x86z\xa7x\xdf\
D\xe5\x9d\x02\xef\"\xbf0\xde\xf0|\x9b\xa8\x9fZm8\xff#\xee\xa7\xa5/\x98w\x88\
\x85!\x81\x0b\xe4KI\xe0\x0b\xcc\x9b\xd6e\xc5\xfc\x84|\xb9\xcd\r\xd7w\xfc\xfc\
g\xef\xc7!\xe6\xf7$\xb0@?\x92\x04\x8ez\x1eu\xcf-\xe0 ,S\x87\xe5\x1e\xcf\x98\
\x97w\x8ddU\xe9\n\x1e\xee\x1d\xff\x0b\x12\xf8\x07\xcd\x14\xf6wY\xaf\xfc\xf2\
\xeb2,\xeb\x01\xcb\xec\x97\xa5\x98\x13,\xdb\x92\xc0{8\xdf\x90\xc0\x1a\xcd\"\
\xc0\x13^\xae\xc9C\xbe)\xf7g|\x18v\x1b\xf9\xad1\x86_\xee#\xfex\xb4\x0f\x1f[\
\xb4\x14\x7f\xe6\xb0\x8fesx\xdau\xc7\xc9\xb2y\xd0u]\xbcd\xae\xae\xadw\x1b\
\x8b'\xf7\xb6v\xb6\xf77w\xb3y3\x17Ri)\xfb\x0e\xe3bf\x0e\xa5\x94\xe9K\xfc\xd9\
\xb6\xd3\xb7\xef?\xf3]\xca\xbbI\xdb\xb6\xe7\xafW3\xf3\xfaF\xc6\xb7\xbdw\xff\
\xf0\x98\xcc\xcc\xe3\x9f\xaf\xcb\xdek?.\x9e\xe7\xcd\xa7\xa3\xd1\xd4\xb9\x93$\
\x89\xe6\xcc\xbev\\\x9d\xc9\xa4\\4\x11\xc9\xf8\xcf\xac\x9b$\xc4\xe1\xc2\x96\
\x16W7\xfc\x0f\xc1\x87.\xac"
}

	def name (self):
		return 'Clinical Summary'

	def MenuInfo (self):
		return ('view', _('&Summary'))

	def GetIconData(self, anIconID = None):
		if anIconID == None:
			return self.__icons[_("""icon_clinical_summary""")]
		else:
			if self.__icons.has_key(anIconID):
				return self.__icons[anIconID]
			else:
				return self.__icons[_("""icon_clinical_summary""")]

	def GetWidget (self, parent):
		return ClinicalSummary (parent, -1)

	def register (self):
		gmPlugin_Patient.wxPatientPlugin.register (self)
		self.gb['clinical.manager'].SetDefault(self.__class__.__name__)
#----------------------------------------------------------------------
if __name__ == "__main__":
	sys.path.append('../../wxpython')
	app = wxPyWidgetTester(size = (400, 500))
	app.SetWidget(ClinicalSummary, -1)
	app.MainLoop()
