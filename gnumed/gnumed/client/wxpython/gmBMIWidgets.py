"""GnuMed BMI calculator display widgets.

acknowledgments: Gui screen Design taken with permission from
                 DrsDesk BMICalc @ DrsDesk Software 1995-2002
                 and @ Dr.R Terry
                 Based on an early screen design by Michael Ireland
                 heavily commented for learning purposes by Dr. R Terry

copyright: authors

TODO:
 - button QUIT
 - patient related "normal" range
 - factor out Algo parts
"""
#===========================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmBMIWidgets.py,v $
# $Id: gmBMIWidgets.py,v 1.7 2005-07-24 18:52:55 ncq Exp $
__version__ = "$Revision: 1.7 $"
__author__  =  "Richard Terry <rterry@gnumed.net>,\
				Michael Bonert <bonerti@mie.utoronto.ca>,\
				Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL (details at http://www.gnu.org)"

import os.path

from wxPython.wx import *

from Gnumed.pycommon import gmI18N

#===========================================================================
class BMI_Colour_Scale(wxWindow):

	def __init__(self, parent, color=wxRED_BRUSH):
		wxWindow.__init__(self, parent, -1, wxDefaultPosition,size = (324,25))
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
		#draw the coloured elipses for each of the mass divisions
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
		#add the green elipse = normal mass range
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

		# initializations
		self.low_norm_mass=''	# mass for given height if BMI=20
		self.upp_norm_mass=''	# mass for given height if BMI=25
		self.focus=0		# set to avoid error on 'Reset'

		wxPanel.__init__ (
			self,
			parent = parent,
			id = id,
			pos = wxDefaultPosition,
			size = wxDefaultSize,
			style = wxSIMPLE_BORDER | wxTAB_TRAVERSAL
		)
		#------------------------------
		#sizer with heading label
		#------------------------------
		label = wxStaticText(
			self,
			-1,
			_("Current height/mass"),
			wxDefaultPosition,
			wxDefaultSize,
			style = wxALIGN_CENTRE
		)
		label.SetFont(wxFont(12,wxSWISS,wxNORMAL, wxBOLD,False,''))
		label.SetForegroundColour(wxColour(0,0,131))
		szr_upper_heading = wxBoxSizer(wxHORIZONTAL)
		szr_upper_heading.Add(label,1,0)
		#------------------------------
		#sizer holding the height stuff
		#------------------------------
		label = wxStaticText(self,-1,_("Height (cm)"),size = (1,20))
		label.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,False,''))
		label.SetForegroundColour(wxColour(0,0,131))

		self.txtheight = wxTextCtrl(self,-1,"",size=(100,20))
		self.txtheight.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,False,''))

		EVT_TEXT(self, self.txtheight.GetId(), self.EvtText_height)
		EVT_SET_FOCUS(self.txtheight, self.OnSetFocus_height)
		EVT_CHAR(self.txtheight, self.EvtChar_height)

		szr_height = wxBoxSizer(wxHORIZONTAL)
		szr_height.Add((10,1),0,0)
		szr_height.Add(label, 1, wxALIGN_CENTRE_VERTICAL, 0)
		szr_height.Add(self.txtheight, 1, wxALIGN_CENTRE_VERTICAL | wxEXPAND, 0)
		#------------------------------
		#sizer holding the mass stuff -- some people incorrectly call this stuff "weight"
		#------------------------------
		label = wxStaticText(self,-1,_("Mass (kg)"),size = (20,20))
		label.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,False,''))
		label.SetForegroundColour(wxColour(0,0,131))

		self.txtmass = wxTextCtrl(self,-1,"",size=(100,20))
		self.txtmass.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,False,''))

		EVT_TEXT(self, self.txtmass.GetId(), self.EvtText_mass)
		EVT_SET_FOCUS(self.txtmass, self.OnSetFocus_mass)
		EVT_CHAR(self.txtmass, self.EvtChar_mass)

		szr_mass = wxBoxSizer(wxHORIZONTAL)
		szr_mass.Add((10,1),0,0)
		szr_mass.Add(label, 1, wxALIGN_CENTRE_VERTICAL, 0)
		szr_mass.Add(self.txtmass, 1, wxALIGN_CENTRE_VERTICAL | wxEXPAND, 0)
		szr_mass.Add((5,5),1,0)
		#-----------------)-------------
		#sizer holding the BMI stuff
		#------------------------------
		label = wxStaticText(self,-1,_("BMI"),size = (100,20))
		label.SetFont(wxFont(13,wxSWISS,wxNORMAL,wxNORMAL,False,''))
		label.SetForegroundColour(wxColour(0,0,131))

  		self.txtbmi = wxTextCtrl(self,-1,"",size=(100,20), style = wxTE_READONLY)
		self.txtbmi.Enable(False)
		self.txtbmi.SetFont(wxFont(13,wxSWISS,wxNORMAL,wxNORMAL,False,''))

		szr_bmi = wxBoxSizer(wxHORIZONTAL)
		szr_bmi.Add((10,1),0,0)
		szr_bmi.Add(label,1,wxALIGN_CENTRE_VERTICAL|0,0)
		szr_bmi.Add(self.txtbmi,1,wxALIGN_CENTRE_VERTICAL | wxEXPAND,0)
		szr_bmi.Add((5,5),1,0)
		#--------------------------------------------------
		#the color ellipses to show where on scale of mass
		#--------------------------------------------------
		bmi_colour_scale = BMI_Colour_Scale(self)
		bmi_colour_scale.Enable(False)
		szr_col_scale = wxBoxSizer(wxHORIZONTAL)
		szr_col_scale.Add(bmi_colour_scale,1,wxEXPAND)
		#-----------------------------------------------------
		#put a slider control under the bmi colour range scale
		#-----------------------------------------------------
		self.slider = wxSlider(self, -1, 15, 15, 34, wxPoint(30, 60),
					wxSize(324, -1),
					wxSL_HORIZONTAL | wxSL_AUTOTICKS | wxSL_LABELS )
		self.slider.SetTickFreq(1, 1)
		EVT_SCROLL(self.slider, self.SLIDER_EVT)
		EVT_CHAR(self.slider, self.EvtChar_slider)

		szr_slider = wxBoxSizer(wxHORIZONTAL)
		szr_slider.Add(self.slider,1,wxEXPAND)
		#---------------------------------------------------------------------
		#Add the adjusted values heading, underlined, autoexpand to fill width
		#FIXME: find underline constant
		#---------------------------------------------------------------------
		label = wxStaticText(
			self,
			-1,
			_("Adjusted Values"),
			wxDefaultPosition,
			wxDefaultSize,
			style = wxALIGN_CENTRE
		)  #add underline
		label.SetFont(wxFont(12,wxSWISS,wxNORMAL, wxBOLD,False,''))
		label.SetForegroundColour(wxColour(0,0,131))

		szr_lower_heading = wxBoxSizer(wxHORIZONTAL)
		szr_lower_heading.Add(label,1,wxEXPAND)
		#-----------------------
		#Put in the goal mass
		#----------------------
		label = wxStaticText(self,-1,_("Goal mass"),size = (30,20))
		label.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,False,''))
		label.SetForegroundColour(wxColour(0,0,131))

		self.txtgoal= wxTextCtrl(self,-1,"",size=(100,20))
		self.txtgoal.SetFont(wxFont(14,wxSWISS,wxNORMAL,wxNORMAL,False,''))

		EVT_TEXT(self, self.txtgoal.GetId(), self.EvtText_goal)
		EVT_SET_FOCUS(self.txtgoal, self.OnSetFocus_goal)
		EVT_CHAR(self.txtgoal, self.EvtChar_goal)

		szr_goal_mass = wxBoxSizer(wxHORIZONTAL)
		szr_goal_mass.Add((10,1),0,0)
		szr_goal_mass.Add(label,1,wxALIGN_CENTRE_VERTICAL,0)
		szr_goal_mass.Add(self.txtgoal,1,wxALIGN_CENTRE_VERTICAL | wxEXPAND, 0)
		#-----------------------------
		#and the amount to loose in Kg
		#-----------------------------
		label = wxStaticText(self,-1,_("kg to loose"),size = (30,20))
		label.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,False,''))
		label.SetForegroundColour(wxColour(0,0,131))

		self.txtloss= wxTextCtrl(self,-1,"",size=(100,20))
		self.txtloss.SetFont(wxFont(12,wxSWISS,wxNORMAL,wxNORMAL,False,''))

		EVT_TEXT(self, self.txtloss.GetId(), self.EvtText_loss)
		EVT_SET_FOCUS(self.txtloss, self.OnSetFocus_loss)
		EVT_CHAR(self.txtloss, self.EvtChar_loss)

		szr_to_loose = wxBoxSizer(wxHORIZONTAL)
		szr_to_loose.Add((10,1),0,0)
		szr_to_loose.Add(label,1,wxALIGN_CENTRE_VERTICAL,0)
		szr_to_loose.Add(self.txtloss,1,wxALIGN_CENTRE_VERTICAL | wxEXPAND,0)
		#-----------------------------------------------------------------
		#finally add all the horizontal sizers from top down to main sizer
		#-----------------------------------------------------------------
		szr_main = wxBoxSizer(wxVERTICAL)
		szr_main.Add((1,5),0,0)
		szr_main.Add(szr_upper_heading,0,wxEXPAND)
		szr_main.Add((1,5),0,0)
		szr_main.Add(szr_height,0,0)
		szr_main.Add((1,5),0,0)
		szr_main.Add(szr_mass,0,0)
		szr_main.Add((1,5),0,0)
		szr_main.Add(szr_bmi,0,0)
		szr_main.Add((1,20),0,0)
		szr_main.Add(szr_col_scale,0,0)
		szr_main.Add(szr_slider,0,0)
		szr_main.Add(szr_lower_heading,0,wxEXPAND)
		szr_main.Add((1,5),0,0)
		szr_main.Add(szr_goal_mass,0,0)
		szr_main.Add((1,5),0,0)
		szr_main.Add(szr_to_loose,0,0)
		szr_main.Add((1,20),0,0)
		#---------------------------------------
		#set, fit and layout sizer so it appears
		#---------------------------------------
		self.SetSizer(szr_main)
		szr_main.Fit(self)
		self.SetAutoLayout(True)
		self.Show(True)
	#-----------------------------------------
	# event handlers
	#-----------------------------------------
	def OnSetFocus_height(self, event):
		self.focus=1
		event.Skip()
	#-----------------------------------------
	def OnSetFocus_mass(self, event):
		self.focus=2
		event.Skip()
	#-----------------------------------------
	def OnSetFocus_goal(self, event):
		self.focus=4
		event.Skip()
	#-----------------------------------------
	def OnSetFocus_loss(self, event):
		self.focus=5
		event.Skip()
	#-----------------------------------------
	def EvtText_height(self, event):
		if(self.focus==1):
			self.calc_ideal_mass_range()
			self.CalcBMI()
	#-----------------------------------------
	def EvtText_mass(self, event):
		if(self.focus==2):
			self.CalcBMI()
	#-----------------------------------------
	def EvtText_goal(self, event):
		if(self.focus==4):
			if(self.txtgoal.GetValue()!=''):
				try:
					self.txtloss.SetValue(str(eval(self.txtmass.GetValue())-eval(self.txtgoal.GetValue())))
					self.CalcNEWBMI()
				except:
					pass	# error handling
			else:
				self.txtloss.SetValue('')
	#-----------------------------------------
	def EvtText_loss(self, event):
		if(self.focus==5):
			self.loss=event.GetString()

			if(self.txtloss.GetValue()!=''):
				try:
					self.txtgoal.SetValue(str(eval(self.txtmass.GetValue())-eval(self.txtloss.GetValue())))
					self.CalcNEWBMI()
				except:
					pass	# error handling
			else:
				self.txtgoal.SetValue('')
	#-----------------------------------------
	def calc_ideal_mass_range(self):
		# FIXME: this needs to be done according to reference charts by ethnicity
		try:
			self.low_norm_mass=20.*((eval(self.txtheight.GetValue())/100.)**2)
			self.upp_norm_mass=25.*((eval(self.txtheight.GetValue())/100.)**2)
			print self.low_norm_mass, self.upp_norm_mass	# test

			# FIXME - display upp_norm_mass & low_norm_mass
			#bmi_colour_scale = BMI_Colour_Scale(self)
		except:
			pass 	# error handling
	#-----------------------------------------
	def CalcBMI(self):
		if(self.txtheight.GetValue()=='' or self.txtmass.GetValue()==''):
			self.txtbmi.SetValue('')
		else:
			try:
				self.txtbmi.SetValue(str(round(eval(self.txtmass.GetValue())/((eval(self.txtheight.GetValue())/100.)**2),1)))

				# initialize slider
				# round twice -- so slider value is the rounded value of "txtbmi" ***
				self.NEWBMI=round(round(eval(self.txtmass.GetValue())/((eval(self.txtheight.GetValue())/100.)**2),1),0)
				self.slider.SetValue(self.NEWBMI)

				# *** If values are entered into loss or goal the BMI slider slider values don't always match the
				#     calculated BMI values in self.txtbmi (due to rounding)  -- FIX ME
				#
				#     e.g.
				# 	if self.txtheight==168 && self.txtmass==86 && self.txtgoal==86
				#		then self.txtbmi=30.5  BUT self.slider=30
				#
				#     MORE DETAILS IN OLDER VERSION OF gmBMICalc.py
			except:
				pass	# error handling
	#-----------------------------------------
	def CalcNEWBMI(self):
		self.NEWBMI=round(eval(self.txtgoal.GetValue())/((eval(self.txtheight.GetValue())/100.)**2),0)
		self.slider.SetValue(self.NEWBMI)
	#-----------------------------------------
	def SLIDER_EVT(self, event):
		self.NEWBMI=self.slider.GetValue()
		try:
			self.txtgoal.SetValue(str(round(self.NEWBMI*(eval(self.txtheight.GetValue())/100.)**2,1)))
			self.txtloss.SetValue(str(eval(self.txtmass.GetValue())-eval(self.txtgoal.GetValue())))
		except:
			pass 	# error handling
	#-----------------------------------------
	# Moving between fields with the 'Enter' key
	def EvtChar_height(self, event):
                if(event.GetKeyCode()==13):		# height -> mass
			self.txtmass.SetFocus()
                else:
                         event.Skip()
	#-----------------------------------------
	def EvtChar_mass(self, event):
                if(event.GetKeyCode()==13):		# mass -> slider
			self.slider.SetFocus()
                else:
                         event.Skip()
	#-----------------------------------------
	def EvtChar_slider(self, event):
                if(event.GetKeyCode()==13):		# slider -> goal
			self.txtgoal.SetFocus()
                else:
                         event.Skip()
	#-----------------------------------------
	def EvtChar_goal(self, event):
                if(event.GetKeyCode()==13):		# goal -> loss
			self.txtloss.SetFocus()
                else:
                         event.Skip()
	#-----------------------------------------
	def EvtChar_loss(self, event):
		if(event.GetKeyCode()==13):		# loss -> height
			self.txtheight.SetFocus()
		else:
			event.Skip()

#-------------------------------------------------------------------
#Creates all the sizers necessary to hold the top two menu's, picture
#from for patients picture, the main two left and right panels, with shadows
# Huh ??
#---------------------------------------------------------------------------
class BMI_Frame(wxFrame):#, BMICalc_Panel):

	def __init__(self, parent):
		# default frame style - maximize box + float on parent + centering + tabbing
		# wxFRAME_FLOAT_ON_PARENT makes it modal
		wxFrame.__init__(
			self,
			parent,
			-1,
			_("BMI Calculator"),
			style = wxMINIMIZE_BOX | wxMAXIMIZE_BOX | wxRESIZE_BORDER | wxCAPTION | wxALIGN_CENTER | wxALIGN_CENTER_VERTICAL | wxTAB_TRAVERSAL | wxSTAY_ON_TOP
		)
		EVT_CLOSE(self, self.OnCloseWindow)

		#-----------------------------------------------------
		#create an instance of the BMICalc_Panel
		#-----------------------------------------------------
		self.pnl_bmi = BMICalc_Panel(self,-1)
		#--------------------------------------------------
		# right hand vertical sizer
		#  -----------------------
		# | graph/text            |
		# |-----------------------|
		# | gap                   |
		# |-----------------------|
		# | btn | btn | btn | ... |
		#  -----------------------

		# surrogate text for graphics
		text4graph = wxTextCtrl(
			self,
			-1,
			"Hi Guys, this is a prototype BMI Calculator + graph.\n\n"
			"Comments please to rterry@gnumed.net..\n\n"
			"Can someone tell me how to centre this frame on the screen...\n\n"
			"This text box needs to be replaced by a graph class....\n"
			"which amongst other things could show this patients mass trends!!!!\n\n"
			"The mass range on the green epilpse would be calculated for each patient...\n\n"
			"BTW, don't worry about your weight, the 'normal' range (63-79) is hardcoded.",
			size=(200, 100),
			style = wxTE_MULTILINE | wxTE_READONLY
		)

		# buttons
		gszr_right_buttons = wxGridSizer(1, 4, 1, 4)  # rows, cols, hgap, vgap
		gszr_right_buttons.AddMany([
			(wxButton(self, 1010, _('&Reset')), 0, wxEXPAND)
#			,
#			(wxButton(self, 1011, _('&Print')), 0, wxEXPAND),
#			(wxButton(self, 1012, _('&Save')), 0, wxEXPAND),
#			(wxButton(self, 1013, _('&Handout')), 0, wxEXPAND)
		])

		EVT_BUTTON(self,1010,self.EvtReset)
#		EVT_BUTTON(self,1011,self.EvtPrint)
#		EVT_BUTTON(self,1012,self.EvtSave)
#		EVT_BUTTON(self,1013,self.EvtHandout)

		# arrange them
		szr_right_col = wxBoxSizer(wxVERTICAL)
		szr_right_col.Add(text4graph,1,wxEXPAND)
		szr_right_col.Add((1,5),0,wxEXPAND)
		szr_right_col.Add(gszr_right_buttons,0,wxEXPAND)

		#--------------------------------------------------
		# horizontal main sizer
		#  --------------------------
		# | input   | g | graph/text |
		# | fields  | a |------------|
		# |         | p | buttons    |
		#  --------------------------
		szr_main = wxBoxSizer(wxHORIZONTAL)
		szr_main.Add(self.pnl_bmi, 0, wxEXPAND | wxALL, 10)
		szr_main.Add((5, 0), 0, wxEXPAND)
		szr_main.Add(szr_right_col, 1, wxEXPAND | wxALL, 10)

		self.SetSizer(szr_main)
		szr_main.Fit(self)
		self.SetAutoLayout(True)

		# get icon
		if __name__ == '__main__':
			png_fname = os.path.join('..', 'bitmaps', 'bmi_calculator.png')
		else:
			from Gnumed.pycommon import gmGuiBroker
			gb = gmGuiBroker.GuiBroker()
			png_fname = os.path.join(gb['gnumed_dir'], 'bitmaps', 'bmi_calculator.png')
		icon = wxEmptyIcon()
		icon.LoadFile(png_fname, wxBITMAP_TYPE_PNG)
		self.SetIcon(icon)
	#-----------------------------------------
	def EvtReset(self, event):
		# reset variables
		self.pnl_bmi.low_norm_mass=''
		self.pnl_bmi.upp_norm_mass=''

		# reset textbox & slider
		self.pnl_bmi.txtheight.SetValue('')
		self.pnl_bmi.txtmass.SetValue('')
		self.pnl_bmi.txtbmi.SetValue('')
		self.pnl_bmi.txtgoal.SetValue('')
		self.pnl_bmi.txtloss.SetValue('')
		self.pnl_bmi.slider.SetValue(0)

	#-----------------------------------------
	def EvtPrint(self, event):
		pass 					# TODO
	#-----------------------------------------
	def EvtSave(self, event):
		pass 					# TODO
	#-----------------------------------------
	def EvtHandout(self, event):
		pass 					# TODO
	#-------------------------------------------
	def OnCloseWindow(self, event):
		self.Destroy()

#== if run as standalone =======================================================
if __name__ == '__main__':
	# set up dummy app
	class TestApp (wxApp):
		def OnInit (self):
			frame = BMI_Frame(None)
			frame.Show(True)
			return True
	#---------------------
	wxInitAllImageHandlers()
	app = TestApp()
	app.MainLoop()

#=====================================================================
# $Log: gmBMIWidgets.py,v $
# Revision 1.7  2005-07-24 18:52:55  ncq
# - comment out not-yet-functional buttons
#
# Revision 1.6  2005/07/16 11:34:47  ncq
# - just cleanup
#
# Revision 1.5  2005/06/16 07:03:19  rterry
# Fixed Sizer syntax to work with 2.6.1 (eg (10,0,0,0) should be ((10,0),0,0)
# multiple occurence
# Note this form cannot be closed currently needs fixing-
# Richard Terry
#
# Revision 1.4  2004/08/09 00:02:20  ncq
# - fix bitmap path when standalone
#
# Revision 1.3  2004/08/06 09:03:35  ncq
# - look for bmi_calculator.png in bitmaps/
#
# Revision 1.2  2004/08/06 08:56:04  ncq
# - cleanups after surgery
#
# Revision 1.1  2004/08/06 08:47:13  ncq
# - moved here from wxpython/patient/ as it is not a patient plugin
#
# Revision 1.30  2004/07/18 20:30:54  ncq
# - wxPython.true/false -> Python.True/False as Python tells us to do
#
# Revision 1.29  2004/06/13 22:31:49  ncq
# - gb['main.toolbar'] -> gb['main.top_panel']
# - self.internal_name() -> self.__class__.__name__
# - remove set_widget_reference()
# - cleanup
# - fix lazy load in _on_patient_selected()
# - fix lazy load in ReceiveFocus()
# - use self._widget in self.GetWidget()
# - override populate_with_data()
# - use gb['main.notebook.raised_plugin']
#
# Revision 1.28  2004/03/14 22:36:33  ncq
# - Andreas will find any bug I try to sneak in, even missing ,
#
# Revision 1.27  2004/03/12 13:25:43  ncq
# - note on hardcoded normal range
#
# Revision 1.26  2004/03/10 15:48:36  ncq
# - new import scheme
#
# Revision 1.25  2003/11/17 10:56:41  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:40  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.24  2003/05/12 01:39:27  michaelb
# minor bug fix - hitting 'Reset' before a field was selected used to result in an error
#
# Revision 1.23  2003/04/28 04:32:44  michaelb
# some minor clean-up (removal of note and spaces)
#
# Revision 1.21  2003/04/26 08:45:56  ncq
# - removed some left-over cruft, i18n()ed buttons, added comments on BMI reference charts
#
# Revision 1.20  2003/04/26 03:32:30  michaelb
# misc. clean-up, elimination of variables that can be done without
#
# Revision 1.19  2003/04/22 05:10:11  michaelb
# reset button now works, initialization of BMI slider on entry of mass & height, something Karsten won't like ('tabbing' w/ enter), TODO/FIXME comments
#
# Revision 1.18  2003/04/20 22:47:06  ncq
# - skip color scale and bmi text field on tab order
#
# Revision 1.17  2003/04/20 12:26:56  ncq
# - clean up, sizer streamlining
#
# Revision 1.16  2003/04/20 02:40:52  michaelb
# tabbing btw fields/slider works, calculation works (slider functional, 'Goal mass' & 'kg to loose' functional)
#
# Revision 1.15  2003/04/14 07:35:54  ncq
# - moved standalone icon acquision inside OnInit to alleviate segfault
#
# Revision 1.14  2003/04/14 04:04:41  michaelb
# changed 'weight' to 'mass' in most places, calculation now partially functional
#
# Revision 1.13  2003/04/05 00:39:23  ncq
# - "patient" is now "clinical", changed all the references
#
# Revision 1.12  2003/01/14 20:18:57  ncq
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
