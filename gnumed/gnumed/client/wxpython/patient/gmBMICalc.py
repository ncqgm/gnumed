#!/usr/bin/python
#############################################################################
#
# gmBMICalc.py  Feedback: anything which is incorrect or ambiguous please
#                   mailto rterry@gnumed.net
# ---------------------------------------------------------------------------
#
# @author: Dr. Richard Terry
# 
# @acknowledgments: Gui screen Design taken with permission from
#                   DrsDesk BMICalc @ DrsDesk Software 1995-2002
#                   and @ Dr.R Terry
#                   Based on an early screen design by Michael Ireland
#                   heavily commented for learning purposes by Dr. R Terry
# @copyright: authors
# @license: GPL (details at http://www.gnu.org)
# @dependencies: wxPython (>= version 2.3.2)
# @change log:
#      
#
# @TODO: all testing and review 
#        bmi input boxes are not set to re-size
#	 just about evrything
#        this module is for GUI development/demonstration
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/patient/Attic/gmBMICalc.py,v $
__version__ = "$Revision: 1.12 $"
__author__  =  "Richard Terry <rterry@gnumed.net>,\
				Michael Bonert <bonerti@mie.utoronto.ca>"

#---------------------------------------------------------------------------
from wxPython.wx import *
#from wxPython.lib.wxPlotCanvas import *
#from wxPython.lib              import wxPlotCanvas  #insert these modules once graph active

#===========================================================================
# we need the icon data for standalone and plugin use, so we might
# just as well define it at the module level

_icons = {"""icon_BMI_calc""": \
'x\xda]\x90\xbd\n\x83P\x0c\x85\xf7>E ^,\x08\xe1\xbaT\xc7P\xc55\x83\xcb]\xc5\
\xb1\x82}\xff\xa9\x89\xf7Gm\x0c\xc2\xf9r\x92\x18\x9f\xdb\xb7}\xccu\xfb\x02K\
\x0fm\xfdX\xe6\x9a`\x85\xf7\xb6\xac\x9fC\x05U\xd8\xf5\xdd\xe0\xfd\xa1%\xeb\
\xae?4\x98\x1e\xfbq\x18\xa3nb\xdd\xfb\xe4\xdfMO\xfd\x94\xfb+\xd3\xde\x17\xcd\
Q\x97\xf9.\xd7\xa78\x0fs=\xef\xa3[@\x84a\xbfD(0h\xe6W\x82r\x8b\x04\xa9\x11\
\xb8D\x82A\x84\x99\xad\x82X\x16\x05\xe1\x8a\xb9\x12 w\x85BL"\xe8\xf49!\x08\
\x93\xf6*\xa4+\xac\x88\x9cC\xf9w:D\x10\xbc9\xd9\xc6\xc1\xddi\xbd`\xf0\xbc\
\xdd\xf6\xb2\x9dC\xc5\xa9\x1f\xaf\x8bc\x94\x99\x12\xf4\xef\xe9-1\r\xd2\x0fX\
\x95oP'}
#===========================================================================
class BMI_Colour_Scale(wxWindow):

	def __init__(self, parent, color=wxRED_BRUSH):
		wxWindow.__init__(self, parent, -1, wxDefaultPosition,size =(324,25))
		EVT_PAINT(self, self.OnPaint)

	def OnPaint(self, event):
		self.Draw(wxPaintDC(self))

	def Draw(self,dc):
		dc.BeginDrawing()
		dc.Clear()
		
		#------------------------------------------------
		#draw the graphics for underneath the BMI buttons
		#------------------------------------------------
		dc.SetBrush(wxBrush(wxColour(194,194,197), wxSOLID)) #222,222,222
		dc.SetPen(wxPen(wxColor(194,197,194), 1))
		dc.DrawRectangle(0, 0, 324, 30)
		#----------------------------------------------------------
		#draw the coloured elipses for each of the weight divisions
		#ie underweight, normal, overweight and obese
		#first yellow underweight
		#Pen = outside border = black (rgb 0 0 0 )
		#Brush= fill in the elipse = yellow (255,255,0)
		#Add text to foreground of the elipse in black
		#----------------------------------------------------------
		dc.SetPen(wxPen(wxColor(0,0,0), 1))
		dc.SetBrush(wxBrush(wxColour(255,255,0), wxSOLID))   #yellow
		dc.DrawEllipse(6, 5, 80,15)
		dc.SetFont(wxFont(8, wxSWISS, wxNORMAL, wxNORMAL))
		dc.SetTextForeground(wxColour(0,0,0))
		te = dc.GetTextExtent(_("Underweight"))
		dc.DrawText(_("Underweight"), 20,9)
		#------------------------------------------
		#add the green elipse = normal weight range
		#------------------------------------------
		dc.SetBrush(wxBrush(wxColour(0,194,0), wxSOLID)) #green
		dc.DrawEllipse(87, 5, 80,15)
		dc.SetBrush(wxBrush(wxColour(0,192,0), wxSOLID))
		dc.SetFont(wxFont(8, wxSWISS, wxNORMAL, wxNORMAL))
		dc.SetTextForeground(wxColour(0,0,0))
		te = dc.GetTextExtent(_("63< Normal >79"))
		dc.DrawText(_("63 - Normal - 79"),95,8)
		#------------------------------------------
		#add the orange elipse = overweight range
		#------------------------------------------
		dc.SetBrush(wxBrush(wxColour(255,128,0), wxSOLID))   #orange
		dc.DrawEllipse(168, 5, 80,15)
		dc.SetFont(wxFont(8, wxSWISS, wxNORMAL, wxNORMAL))
		dc.SetTextForeground(wxColour(0,0,0))
		te = dc.GetTextExtent(_("Overweight"))
		dc.DrawText(_("Overweight"), 180,9)
		#------------------------------------------
		#add the red elipse = overweight range
		#------------------------------------------
	
		dc.SetBrush(wxBrush(wxColour(192,0,0), wxSOLID)) #red
		dc.DrawEllipse(250, 5, 60,15)
		dc.SetFont(wxFont(8, wxSWISS, wxNORMAL, wxNORMAL))
		dc.SetTextForeground(wxColour(0,0,0))
		te = dc.GetTextExtent(_("Obese"))
		dc.DrawText(_("Obese"), 267,9)
		dc.EndDrawing()

	def SetColor(self, color):
		self.color = color
		self.Draw(wxClientDC(self))
#===========================================================================		
class BMICalc_Panel(wxPanel):
	def __init__(self, parent, id):
		wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, wxSIMPLE_BORDER )	
		sizer = wxBoxSizer(wxVERTICAL)
		#------------------------------
		#sizer with heading label
		#------------------------------
		lblheading = wxStaticText(
			self,
			-1,
			_("Current height/weight"),
			wxDefaultPosition,
			wxDefaultSize,
			style = wxALIGN_CENTRE
		)
		lblheading.SetFont(wxFont(12,wxSWISS,wxNORMAL, wxBOLD,false,''))
		lblheading.SetForegroundColour(wxColour(0,0,131))
		szr_left1 = wxBoxSizer(wxHORIZONTAL)
		szr_left1.Add(lblheading,1,0)
		#------------------------------
		#sizer holding the height stuff
		#------------------------------
		szr_left2 = wxBoxSizer(wxHORIZONTAL)
		label1 = wxStaticText(self,-1,_("Height (cm)"),size = (1,20))
		label1.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,false,''))
		label1.SetForegroundColour(wxColour(0,0,131))
		self.txtHeight = wxTextCtrl(self,-1,"",size=(100,20))
		self.txtHeight.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,false,''))
		szr_left2.Add(10,1,0,0)
		szr_left2.Add(label1,1,wxALIGN_CENTRE_VERTICAL|0)
		szr_left2.Add(self.txtHeight,1,wxALIGN_CENTRE_VERTICAL|0)
		#------------------------------
		#sizer holding the weight stuff
		#------------------------------
		szr_left3 = wxBoxSizer(wxHORIZONTAL)
		label2 = wxStaticText(self,-1,_("Weight (kg)"),size = (20,20))
		label2.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,false,''))
		label2.SetForegroundColour(wxColour(0,0,131))

		txtWeight = wxTextCtrl(self,-1,"",size=(100,20))
		txtWeight.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,false,''))
		szr_left3.Add(10,1,0,0)
		szr_left3.Add(label2,1,wxALIGN_CENTRE_VERTICAL|0)
		szr_left3.Add(txtWeight,1,wxALIGN_CENTRE_VERTICAL|0)
		szr_left3.Add(5,5,1,0)
		#------------------------------
		#sizer holding the BMI stuff
		#------------------------------
		szr_left4 = wxBoxSizer(wxHORIZONTAL)
		label3 = wxStaticText(self,-1,_("BMI"),size = (100,20))
		label3.SetFont(wxFont(13,wxSWISS,wxNORMAL,wxNORMAL,false,''))
		label3.SetForegroundColour(wxColour(0,0,131))

		txtbmi = wxTextCtrl(self,-1,"",size=(100,20))
		txtbmi.SetFont(wxFont(13,wxSWISS,wxNORMAL,wxNORMAL,false,''))
		szr_left4.Add(10,1,0,0)
		szr_left4.Add(label3,1,wxALIGN_CENTRE_VERTICAL|0)
		szr_left4.Add(txtbmi,1,wxALIGN_CENTRE_VERTICAL|0)
		szr_left4.Add(5,5,1,0)
		#--------------------------------------------------
		#the color elipses to show where on scale of weight
		#--------------------------------------------------
		bmi_colour_scale = BMI_Colour_Scale(self)
		szr_left5 = wxBoxSizer(wxHORIZONTAL)
		szr_left5.Add(bmi_colour_scale,1,wxEXPAND)
		#-----------------------------------------------------
		#put a slider control under the bmi colour range scale
		#-----------------------------------------------------
		slider = wxSlider(self, -1, 0, 0, 35, wxPoint(30, 60),
							wxSize(324, -1),
							wxSL_HORIZONTAL | wxSL_AUTOTICKS | wxSL_LABELS )
		slider.SetTickFreq(1, 1)
		szr_left6 = wxBoxSizer(wxHORIZONTAL)
		szr_left6.Add(slider,1,wxEXPAND)
		#---------------------------------------------------------------------
		#Add the adjusted values heading, underlined, autoexpand to fill width
		#TOFIX - find underline constant
		#---------------------------------------------------------------------
		szr_left7 = wxBoxSizer(wxHORIZONTAL)
		label4 = wxStaticText(self,-1,_("Adjusted Values"),wxDefaultPosition,wxDefaultSize,style = wxALIGN_CENTRE)  #add underline
		label4.SetFont(wxFont(12,wxSWISS,wxNORMAL, wxBOLD,false,''))
		label4.SetForegroundColour(wxColour(0,0,131))
		szr_left7.Add(label4,1,wxEXPAND)
		#-----------------------
		#Put in the goal weight
		#----------------------
		lblgoal = wxStaticText(self,-1,_("Goal weight"),size = (30,20))
		lblgoal.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,false,''))
		lblgoal.SetForegroundColour(wxColour(0,0,131))
		txtgoal= wxTextCtrl(self,-1,"",size=(100,20))
		txtgoal.SetFont(wxFont(14,wxSWISS,wxNORMAL,wxNORMAL,false,''))
		szr_left8 = wxBoxSizer(wxHORIZONTAL)
		szr_left8.Add(10,1,0,0)
		szr_left8.Add(lblgoal,1,0)
		szr_left8.Add(txtgoal,1,0)
		#-----------------------------
		#and the amount to loose in Kg
		#-----------------------------
		lblloss = wxStaticText(self,-1,_("kg to loose"),size = (30,20))
		lblloss.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,false,''))
		lblloss.SetForegroundColour(wxColour(0,0,131))
		txtloss= wxTextCtrl(self,-1,"",size=(100,20))
		txtloss.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,false,''))
		szr_left9 = wxBoxSizer(wxHORIZONTAL)
		szr_left9.Add(10,1,0,0)	
		szr_left9.Add(lblloss,1,0)
		szr_left9.Add(txtloss,1,0)
		#-----------------------------------------------------------------
		#finally add all the horizontal sizers from top down to main sizer
		#-----------------------------------------------------------------
		sizer.Add(1,5,0,0)
		sizer.Add(szr_left1,0,wxEXPAND)
		sizer.Add(1,5,0,0)
		sizer.Add(szr_left2,0,0)
		sizer.Add(1,5,0,0)
		sizer.Add(szr_left3,0,0)
		sizer.Add(1,5,0,0)
		sizer.Add(szr_left4,0,0)
		sizer.Add(1,20,0,0)
		sizer.Add(szr_left5,0,0)
		sizer.Add(szr_left6,0,0)
		sizer.Add(szr_left7,0,wxEXPAND)
		sizer.Add(1,5,0,0)
		sizer.Add(szr_left8,0,0)
		sizer.Add(1,5,0,0)
		sizer.Add(szr_left9,0,0)
		sizer.Add(1,20,0,0)
		#---------------------------------------
		#set, fit and layout sizer so it appears
		#---------------------------------------
		self.SetSizer(sizer)
		sizer.Fit(self)
		self.SetAutoLayout(true)
		self.Show(true)
#-------------------------------------------------------------------
#Creates all the sizers necessary to hold the top two menu's, picture
#from for patients picture, the main two left and right panels, with shadows
#---------------------------------------------------------------------------
class BMI_Frame(wxFrame):

	def __init__(self, parent):
		wxFrame.__init__(self, parent, -1, _("BMI Calculator"))

		EVT_CLOSE(self, self.OnCloseWindow)
		#-----------------------------------------------------
		#create an instance of the BMICalc_Panel and add it to
		#the left hand sizer - a vertical box sizer
		#-----------------------------------------------------
		self.bmipanel = BMICalc_Panel(self,-1)
		szr_vbs_left = wxBoxSizer(wxVERTICAL)
		szr_vbs_left.Add(self.bmipanel,1,wxEXPAND)
		#-----------------------------------------------------
		#Create the right hand vertical box sizer and add to
		#it the area the graph will occupy and  the buttons
		#underneath the graph. A button is here to occupy
		#the space that will be occupied by the graph
		#-----------------------------------------------------
                #pretendgraph =wxButton(self,-1,"The graph goes here")
		t3 = wxTextCtrl(
			self,
			-1,
			"Hi Guys, this is a prototype BMI Calculator + graph.\n\n"
			"Comments please to rterry@gnumed.net..\n\n"
			"The text boxes are set not to resize at the moment..\n\n"
			"Can someone tell me how to remove the maximizing button...\n\n"
			"Can someone tell me how to centre this frame on the screen...\n\n"
			"This text box needs to be replaced by a graph class....\n"
			"which amongst other things could show this patients weight trends!!!!\n\n"
			"The weight range on the green epilpse would be calculated for each patient...\n\n"
		 	"Bye for now...\n\n",
			size=(200, 100),
			style=wxTE_MULTILINE
		)
		gs = wxGridSizer(1, 4, 1, 4)  # rows, cols, hgap, vgap
		gs.AddMany([
			(wxButton(self, 1010, '&Reset'), 0, wxEXPAND),
			(wxButton(self, 1010, '&Print'), 0, wxEXPAND),
			(wxButton(self, 1010, '&Save'),	0, wxEXPAND),
			(wxButton(self, 1010, '&Handout'), 0, wxEXPAND),
		])
		#-----------------------------------------------------------------
		#Now create the right hand vertical box sizer and stack the graph,
		#gap, and gridsizer containing the horizontal buttons onto it
		#-----------------------------------------------------------------
		szr_vbs_right = wxBoxSizer(wxVERTICAL)                           #create vertical box sizer
		szr_vbs_right.Add(t3,8,wxEXPAND)                       #add a pretend graph
		szr_vbs_right.Add(1,5,0,wxEXPAND)                                #gap under graph, above buttons
		szr_vbs_right.Add(gs,1,wxEXPAND)                                 #Add the row of buttons
		#-------------------------------------------------------------------
		#Now create a sizer which will contain the left hand sizer + BMICalc
		#and the right hand sizer (graph + buttons). This is a horizontal
		#sizer so will get visually(calc:space:graph+buttons)
		#-------------------------------------------------------------------
		szr_main_panels = wxBoxSizer(wxHORIZONTAL)                      #add the BMICalc_Panel instance
		szr_main_panels.Add(szr_vbs_left,1,wxEXPAND)                    #put a small gap in between
		szr_main_panels.Add(5,0,0,wxEXPAND)
		szr_main_panels.Add(szr_vbs_right,1,wxEXPAND)
		#--------------------------------------------------------------------
		#now create the  the main sizer of the frame with a border around it
		#--------------------------------------------------------------------
		szr_main_container = wxBoxSizer(wxVERTICAL)
		szr_main_container.Add(szr_main_panels,1, wxEXPAND|wxALL,10)
		self.SetSizer(szr_main_container)        #set the sizer
		szr_main_container.Fit(self)             #set to minimum size as calculated by sizer
		self.SetAutoLayout(true)                 #tell frame to use the sizer
		self.Show(true)                          #show the frame
	
#	def getBitmap (self):
#		return wxBitmapFromXPMData (cPickle.loads(zlib.decompress(_icons[_("""icon_BMI_calc""")] )))

	def OnCloseWindow(self, event):
		self.Destroy()
#== if run as standalone =======================================================
if __name__ == '__main__':
	# enable us to find our modules
	import sys
	sys.path.append('modules')
	sys.path.append('..')

	import gmI18N
	import cPickle, zlib

	# get icon
	try:
		icon_xpm_data = cPickle.loads(zlib.decompress(_icons[_("""icon_BMI_calc""")]))
	except KeyError:
		icon_xpm_data = cPickle.loads(zlib.decompress(_icons["""icon_BMI_calc"""]))
	icon = wxEmptyIcon()
	icon.CopyFromBitmap(wxBitmapFromXPMData(icon_xpm_data))

	# set up dummy app
	class TestApp (wxApp):
		def OnInit (self):
			frame = BMI_Frame(None)
			frame.SetIcon(icon)
			frame.Show(1)
			return true
	#---------------------
	app = TestApp()
	app.MainLoop()
#== if run as plugin ===========================================================
else:
	import gmPlugin

	ID_BMIMENU = wxNewId ()
	ID_BMITOOL = wxNewId ()

	#---------------------
	class gmBMICalc (gmPlugin.wxBasePlugin):
		def name (self):
			return 'BMICalcPlugin'
		#---------------------
		def register (self):
			menu = self.gb['main.toolsmenu']
			menu.Append (ID_BMIMENU, _("BMI"), _("Body Mass Index Calculator"))
			EVT_MENU (self.gb['main.frame'], ID_BMIMENU, self.OnBMITool)

			self.tb = self.gb['main.toolbar']
			self.tool = wxToolBar (self.tb, -1, style=wxTB_HORIZONTAL|wxNO_BORDER|wxTB_FLAT)
			self.tool.AddTool(
				ID_BMITOOL,
				self.GetIcon(),
				shortHelpString = _("BMI Calculator")
			)
			self.tb.AddWidgetRightBottom (self.tool)
			EVT_TOOL (self.tool, ID_BMITOOL, self.OnBMITool)
			# kind = wxITEM_NORMAL,
		#---------------------
		def unregister (self):
			#tb2 = self.gb['toolbar.Patient']
			#tb2.DeleteTool (ID_BMITOOL)
			menu = self.gb['main.toolsmenu']
			menu.Delete (ID_BMIMENU)
		#---------------------
		def OnBMITool (self, event):
			# FIXME: update patient ID
			frame = BMI_Frame(self.gb['main.frame'])
			icon_xpm_data = self.GetIcon()
			icon = wxEmptyIcon()
			icon.CopyFromBitmap(icon_xpm_data)
			frame.SetIcon(icon)
			frame.Show (1)
		#---------------------
		def GetIconData(self, anIconID = None):
			try:
				return _icons[anIconID]
			except KeyError:
				try:
					return _icons[_("""icon_BMI_calc""")]
				except KeyError:
					return _icons["""icon_BMI_calc"""]
#=====================================================================
# $Log: gmBMICalc.py,v $
# Revision 1.12  2003-01-14 20:18:57  ncq
# - fixed setfont() problem
#
# Revision 1.11  2003/01/12 18:51:32  ncq
# - fixed segfault on invocation as plugin
#
# Revision 1.10  2003/01/12 17:13:54  ncq
# - streamlined import based on invocation
#
# Revision 1.9  2003/01/12 02:14:06  ncq
# - CVS keywords
# - clean separation in standalone and plugin
#
