
from wxPython.wx import *
import gmLog
gmSECTION_SUMMARY = 1
gmSECTION_DEMOGRAPHICS = 2
gmSECTION_CLINICALNOTES = 3
gmSECTION_FAMILYHISTORY = 4
gmSECTION_PASTHISTORY = 5
gmSECTION_VACCINATION = 6
gmSECTION_ALLERGIES = 7
gmSECTION_SCRIPT = 8
gmSECTION_REQUESTS = 9
gmSECTION_MEASUREMENTS = 10
gmSECTION_REFERRALS = 11
gmSECTION_RECALLS = 12


#------------------------------------------------------------
#text control class to be later replaced by the gmPhraseWheel
#------------------------------------------------------------
class  EditAreaTextBox(wxTextCtrl):
	def __init__ (self, parent, id, wxDefaultPostion, wxDefaultSize):
		wxTextCtrl.__init__(self,parent,id,"",wxDefaultPostion, wxDefaultSize,wxSIMPLE_BORDER)
		#self.SetBackgroundColour(wxColor(255,194,197))
		self.SetForegroundColour(wxColor(255,0,0))
		self.SetFont(wxFont(12,wxSWISS,wxBOLD,wxBOLD,false,'xselfont'))

#--------------------------------------------------
#Class which shows a blue bold label left justified
#--------------------------------------------------
class EditAreaPromptLabel(wxStaticText):
	def __init__(self, parent, id, prompt):
		wxStaticText.__init__(self,parent, id,prompt,wxDefaultPosition,wxDefaultSize,wxALIGN_LEFT) 
		self.SetFont(wxFont(10,wxSWISS,wxBOLD,wxBOLD,false,'xselfont'))
		self.SetForegroundColour(wxColour(0,0,131))
#------------------------------------------------------------
#temporary Class which shoes a aqua bold label left justified
#until I pass the rgb colours down to the routine above
#------------------------------------------------------------
class EditAreaPromptLabelAqua(wxStaticText):
	def __init__(self, parent, id, prompt):
		wxStaticText.__init__(self,parent, id,prompt,wxDefaultPosition,wxDefaultSize,wxALIGN_LEFT) 
		self.SetFont(wxFont(10,wxSWISS,wxBOLD,wxBOLD,false,'xselfont'))
		self.SetForegroundColour(wxColour(0,194,197))

#--------------------------------------------------------------------------------
#create the editorprompts class which expects a dictionary of labels passed to it
#with prompts relevent to the editing area.
#remove the if else from this once the edit area labelling is fixed
#--------------------------------------------------------------------------------
class EditAreaPrompts(wxPanel):
	def __init__(self,parent,id,prompt_array):
		wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, wxSIMPLE_BORDER )	
		self.SetBackgroundColour(wxColor(255,255,255))                                  #set background light gray
		self.sizer = wxGridSizer (len(prompt_array),1,2,2)                              #add grid sizer with n columns
		for key in prompt_array.keys():
			if key == 1:
				self.sizer.Add(EditAreaPromptLabelAqua(self,-1, " " + prompt_array[key]),0,wxEXPAND)
			else: 
			        self.sizer.Add(EditAreaPromptLabel(self,-1, " " + prompt_array[key]),0,wxEXPAND)
				
		self.SetSizer(self.sizer)  
		self.sizer.Fit(self)            
		self.SetAutoLayout(true)                
		#self.Show(true)
	
#----------------------------------------------------------
#Class central to gnumed data input
#allows data entry of multiple different types.e.g scripts,
#referrals, measurements, recalls etc
#@TODO : just about everything
#section = calling section eg allergies, script
#----------------------------------------------------------
class EditTextBoxes(wxPanel):
	def __init__(self,parent,id,editareaprompts,section):
		wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize,style = wxRAISED_BORDER)	
		self.SetBackgroundColour(wxColor(222,222,222))                         #background of whole panel
		self.szr_edit_area = wxBoxSizer(wxVERTICAL)                         # vertical sizer for edit are (?need)
		self.gs = wxGridSizer(len(editareaprompts), 1, 0, 0)                     # rows, cols, hgap, vgap
		#--------------------------------------------------
		#create line sizers to hold text boxes in the grid
		#--------------------------------------------------
		self.sizer_line1 = wxBoxSizer(wxHORIZONTAL) 
		self.sizer_line2 = wxBoxSizer(wxHORIZONTAL) 
		self.sizer_line3 = wxBoxSizer(wxHORIZONTAL) 
		self.sizer_line4 = wxBoxSizer(wxHORIZONTAL) 
		self.sizer_line5 = wxBoxSizer(wxHORIZONTAL) 
		self.sizer_line6 = wxBoxSizer(wxHORIZONTAL) 
		self.sizer_line7 = wxBoxSizer(wxHORIZONTAL) 
		self.sizer_line8 = wxBoxSizer(wxHORIZONTAL) 
		self.btnOK = wxButton(self,-1,"Ok")
		self.btnClear = wxButton(self,-1,"Clear")
		self.btnOKsizer = wxBoxSizer(wxHORIZONTAL)
		gmLog.gmDefLog.Log ( "before if statements")
		if section == gmSECTION_SUMMARY:
		      pass
	        elif section == gmSECTION_DEMOGRAPHICS:
		      pass
                elif section == gmSECTION_CLINICALNOTES:
		      pass
	        elif section == gmSECTION_FAMILYHISTORY:
		      pass
	        elif section == gmSECTION_PASTHISTORY:
		      self.txt_condition = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
                      self.rb_sideleft = wxRadioButton(self, 32, " (L) ", wxDefaultPosition,wxDefaultSize)
	              self.rb_sideright = wxRadioButton(self, 33, "(R)", wxDefaultPosition,wxDefaultSize,wxSUNKEN_BORDER)
		      self.rb_sideboth = wxRadioButton(self, 33, "Both", wxDefaultPosition,wxDefaultSize)
		      self.rbsizer = wxBoxSizer(wxHORIZONTAL)
		      self.rbsizer.Add(self.rb_sideleft,1,wxEXPAND)
		      self.rbsizer.Add(self.rb_sideright,1,wxEXPAND) 
                      self.rbsizer.Add(self.rb_sideboth,1,wxEXPAND)
		      self.sizer_line1.Add(self.txt_condition,4,wxEXPAND)
		      self.sizer_line1.Add(self.rb_sideleft,1,wxEXPAND|wxALL,2)
		      self.sizer_line1.Add(self.rb_sideright,1,wxEXPAND|wxALL,2) 
                      self.sizer_line1.Add(self.rb_sideboth,1,wxEXPAND|wxALL,2)
                      self.txt_notes1 = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      self.txt_notes2= EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
	              self.txt_agenoted = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      self.sizer_line4.Add(self.txt_agenoted,1,wxEXPAND)
		      self.sizer_line4.Add(5,0,5)
		      self.txt_yearnoted  = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      self.sizer_line5.Add(self.txt_yearnoted,1,wxEXPAND)
		      self.sizer_line5.Add(5,0,5)
		      cb_active = wxCheckBox(self, -1, " Active ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
		      cb_operation = wxCheckBox(self, -1, " Operation ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
		      cb_confidential = wxCheckBox(self, -1, " Confidential ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
		      cb_significant = wxCheckBox(self, -1, " Significant ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
	              self.txt_progressnotes  = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      self.sizer_line6.Add(cb_active,1,wxEXPAND)
		      self.sizer_line6.Add(cb_operation,1,wxEXPAND)
	              self.sizer_line6.Add(cb_confidential,1,wxEXPAND)
		      self.sizer_line6.Add(cb_significant,1,wxEXPAND)
	              self.gs.Add(self.sizer_line1,0,wxEXPAND)
		      self.gs.Add(self.txt_notes1,0,wxEXPAND)
		      self.gs.Add(self.txt_notes2,0,wxEXPAND)
		      self.gs.Add(self.sizer_line4,0,wxEXPAND)
		      self.gs.Add(self.sizer_line5,0,wxEXPAND)
		      self.gs.Add(self.sizer_line6,0,wxEXPAND)
		      self.gs.Add(self.txt_progressnotes,0,wxEXPAND)
		      self.sizer_line7.Add(5,0,6)
		      self.sizer_line7.Add(self.btnOK,1,wxEXPAND|wxALL,2)
	              self.sizer_line7.Add(self.btnClear,1,wxEXPAND|wxALL,2)   
		      self.gs.Add(self.sizer_line7,0,wxEXPAND)
		      #self.anylist = wxListCtrl(self, -1,  wxDefaultPosition,wxDefaultSize,wxLC_REPORT|wxLC_LIST|wxSUNKEN_BORDER)

		elif section == gmSECTION_VACCINATION:
		   
		      self.txt_targetdisease = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      self.txt_vaccine = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      self.txt_dategiven= EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      self.txt_serialno = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      self.txt_sitegiven  = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
	              self.txt_progressnotes  = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
	              self.gs.Add(self.txt_targetdisease,0,wxEXPAND)
		      self.gs.Add(self.txt_vaccine,0,wxEXPAND)
		      self.gs.Add(self.txt_dategiven,0,wxEXPAND)
		      self.gs.Add(self.txt_serialno,0,wxEXPAND)
		      self.gs.Add(self.txt_sitegiven,0,wxEXPAND)
		      self.gs.Add(self.txt_progressnotes,0,wxEXPAND)
		      self.sizer_line6.Add(5,0,6)
		      self.sizer_line6.Add(self.btnOK,1,wxEXPAND|wxALL,2)
	              self.sizer_line6.Add(self.btnClear,1,wxEXPAND|wxALL,2)    
		      self.gs.Add(self.sizer_line6,1,wxEXPAND)
		
	        
		elif section == gmSECTION_ALLERGIES:
		      gmLog.gmDefLog.Log ( "section allergies")
		      #self.sizer = wxGridSizer (len(prompt_array),1,2,2)    
		      gmLog.gmDefLog.Log ( len(editareaprompts))
		      self.text1 = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      self.text2 = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      self.text3 = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      self.text4 = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      self.text5 = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      self.cb1 = wxCheckBox(self, -1, " generic specific", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)	
		      self.rb1 = wxRadioButton(self, 32, " Allergy ", wxDefaultPosition,wxDefaultSize)
		      self.rb2 = wxRadioButton(self, 33, "Sensitivity", wxDefaultPosition,wxDefaultSize)
		      self.cb2 = wxCheckBox(self, -1, " Definate", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
		      
		      
		      self.sizer_line3.Add(self.text3,6,wxEXPAND)           #the generic compound text plus
		      self.sizer_line3.Add(self.cb1,3,wxEXPAND)             #check box saying 'generic specific' 
		      self.sizer_line6.Add(5,0,0)                           #space to push the first radio button off the edge
		      self.sizer_line6.Add(self.rb1,2,wxEXPAND)             #radiobutton for allergy
		      self.sizer_line6.Add(self.rb2,2,wxEXPAND)             #radiobutton for sensitivity
		      self.sizer_line6.Add(self.cb2,2,wxEXPAND)             #check box to say if it is definate (default = is - set this)
		      self.sizer_line6.Add(self.btnOK,1,wxEXPAND|wxALL,4)   #the ok button with a gap around it (4)
		      self.sizer_line6.Add(self.btnClear,1,wxEXPAND|wxALL,4)#the clear button with a gap around it(4) 
		      self.gs.Add(self.text1,0,wxEXPAND)
		      self.gs.Add(self.text2,0,wxEXPAND)
		      self.gs.Add(self.sizer_line3,0,wxEXPAND)
		      self.gs.Add(self.text4,0,wxEXPAND)
		      self.gs.Add(self.text5,0,wxEXPAND)
		      self.gs.Add(self.sizer_line6,0,wxEXPAND)				
		elif section == gmSECTION_SCRIPT:
		      gmLog.gmDefLog.Log ( "in script section now")
		      self.text1 = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      self.text2 = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      self.text3 = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      self.text4 = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      self.text5 = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      self.text6 = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      self.text7 = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      self.text8 = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      self.text9 = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      lbl_veterans = EditAreaPromptLabel(self,-1,"  Veteran  ")
		      lbl_reg24 = EditAreaPromptLabel(self,-1,"  Reg 24  ")
		      lbl_quantity = EditAreaPromptLabel(self,-1,"  Quantity  ")
		      lbl_repeats = EditAreaPromptLabel(self,-1,"  Repeats  ")
		      lbl_usualmed = EditAreaPromptLabel(self,-1,"  Usual  ")
		      cb_veteran  = wxCheckBox(self, -1, " Yes ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
		      cb_reg24 = wxCheckBox(self, -1, " Yes ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
		      cb_usualmed = wxCheckBox(self, -1, " Yes ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
		      self.sizer_auth_PI = wxBoxSizer(wxHORIZONTAL)
		      self.btn_authority = wxButton(self,-1,">Authority")     #create authority script
		      self.btn_briefPI   = wxButton(self,-1,"Brief PI")       #show brief drug product information
		      self.sizer_auth_PI.Add(self.btn_authority,1,wxEXPAND|wxALL,2)  #put authority button and PI button
		      self.sizer_auth_PI.Add(self.btn_briefPI,1,wxEXPAND|wxALL,2)    #on same sizer
		      
		      self.text10 = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      self.sizer_line3.Add(self.text3,5,wxEXPAND)
		      self.sizer_line3.Add(lbl_veterans,1,wxEXPAND)
        	      self.sizer_line3.Add(cb_veteran,1,wxEXPAND)
		      self.sizer_line4.Add(self.text4,5,wxEXPAND)
		      self.sizer_line4.Add(lbl_reg24,1,wxEXPAND)
        	      self.sizer_line4.Add(cb_reg24,1,wxEXPAND)
		      self.sizer_line5.Add(self.text5,5,wxEXPAND)
		      self.sizer_line5.Add(lbl_quantity,1,wxEXPAND)
        	      self.sizer_line5.Add(self.text9,1,wxEXPAND)
		      self.sizer_line6.Add(self.text6,5,wxEXPAND)
		      self.sizer_line6.Add(lbl_repeats,1,wxEXPAND)
        	      self.sizer_line6.Add(self.text10,1,wxEXPAND)
		      self.sizer_line7.Add(self.text7,5,wxEXPAND)
		      self.sizer_line7.Add(lbl_usualmed,1,wxEXPAND)
        	      self.sizer_line7.Add(cb_usualmed,1,wxEXPAND)
		      self.sizer_line8.Add(5,0,0)
		      self.sizer_line8.Add(self.sizer_auth_PI,2,wxEXPAND)
		      self.sizer_line8.Add(5,0,2)
		      self.sizer_line8.Add(self.btnOK,1,wxEXPAND|wxALL,2)
		      self.sizer_line8.Add(self.btnClear,1,wxEXPAND|wxALL,2)
		      self.gs.Add(self.text1,1,wxEXPAND) #prescribe for
		      self.gs.Add(self.text2,1,wxEXPAND) #prescribe by class
		      self.gs.Add(self.sizer_line3,1,wxEXPAND) #prescribe by generic, lbl_veterans, cb_veteran
		      self.gs.Add(self.sizer_line4,1,wxEXPAND) #prescribe by brand, lbl_reg24, cb_reg24
		      self.gs.Add(self.sizer_line5,1,wxEXPAND) #drug strength, lbl_quantity, text_quantity 
		      self.gs.Add(self.sizer_line6,1,wxEXPAND) #txt_directions, lbl_repeats, text_repeats 
		      self.gs.Add(self.sizer_line7,1,wxEXPAND) #text_for,lbl_usual,chk_usual
		      self.gs.Add(self.text8,1,wxEXPAND)            #text_progressNotes
		      self.gs.Add(self.sizer_line8,1,wxEXPAND)
		      
		      
	        elif section == gmSECTION_REQUESTS:
			
		      pass
	        elif section == gmSECTION_MEASUREMENTS:
		      pass
	        elif section == gmSECTION_REFERRALS:
		      pass
		elif section == gmSECTION_RECALLS:
		      pass
		     
		else:
			      gmLog.gmDefLog.Log ( "not section allergies")
			      
	        
		self.szr_edit_area.Add(self.gs,1,wxEXPAND)
		self.SetSizer(self.szr_edit_area)  
		self.szr_edit_area.Fit(self)            
		self.SetAutoLayout(true)                
		self.Show(true)
class EditArea(wxPanel):
	def __init__(self,parent,id,editareaprompts,section):
		wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize,style = 0 )	
		self.SetBackgroundColour(wxColor(222,222,222))
		#-----------------------
		#create background sizer
		#-----------------------
		self.szr_central_container = wxBoxSizer(wxHORIZONTAL)
		#--------------------------------------------------------------
		#create edit prompts panel and its shadow underneath using text
		#passed to the routine by dictionary editareaprompts
		#--------------------------------------------------------------
		self.szr_edit_prompts = wxBoxSizer(wxVERTICAL)                     #sizer to hold prompts panel
		self.prompts = EditAreaPrompts(self,-1,editareaprompts)            #create instance of prompt panel 
	        self.szr_edit_prompts.Add(self.prompts, 97,wxEXPAND)               #add prompts panel - 97% or height
		szr_edit_prompts_shadow_under = wxBoxSizer (wxHORIZONTAL)          #Hsizer to hold shadow under prompts
		self.edit_prompts_shadow_under = wxWindow(self,-1,
					    wxDefaultPosition,wxDefaultSize,0)     #window for under shadow
		self.edit_prompts_shadow_under.SetBackgroundColour(wxColor(131,129,131))           #make it dark gray
		szr_edit_prompts_shadow_under.Add(5,0,0,wxEXPAND)                   #1:add the space to indent the shadow under
		szr_edit_prompts_shadow_under.Add(self.edit_prompts_shadow_under,10,wxEXPAND) #add the shadow under itself
		self.szr_edit_prompts.Add(szr_edit_prompts_shadow_under,5,wxEXPAND) #add the shadow under the prompts panel 
		self.szr_edit_prompts_shadow_right = wxBoxSizer(wxVERTICAL)         #sizer to right of prompts to hold shadow
		self.edit_prompts_shadow_right = wxWindow(self,-1,wxDefaultPosition,wxDefaultSize,0) #make right hand shadow
		self.edit_prompts_shadow_right.SetBackgroundColour(wxColor(131,129,131))             #which will be gray        
		self.szr_edit_prompts_shadow_right.Add(0,5,0,wxEXPAND)                               #1:add space before shadow starts
		self.szr_edit_prompts_shadow_right.Add(self.edit_prompts_shadow_right,1,wxEXPAND)    #add the gray vertical shadow 
                #-------------------------------------------------------------------------
		#create the editing area itself, consisting of a grid sizer with n rows
		#(size of the prompt array passed to it), plus shadows underneath and to
		#the right.
		#-------------------------------------------------------------------------
		self.szr_edit_area = wxBoxSizer(wxVERTICAL)
		self.rightside = EditTextBoxes(self,-1,editareaprompts,section)
		self.szr_edit_area.Add(self.rightside,92,wxEXPAND)
		self.right_shadow_under = wxWindow(self,-1,
				     wxDefaultPosition,wxDefaultSize,0)             # shadow under is a window
		self.right_shadow_under.SetBackgroundColour(wxColor(131,129,131))   # coloured gray
		self.szr_edit_area_shadow_under = wxBoxSizer (wxHORIZONTAL)         
		self.szr_edit_area_shadow_under.Add(5,0,0,wxEXPAND)                          #1:add the space at start of shadow
		self.szr_edit_area_shadow_under.Add(self.right_shadow_under,12,wxEXPAND)
		self.szr_edit_area.Add(self.szr_edit_area_shadow_under,5,wxEXPAND)
	
		
		#-----------------------------------------------------------------------
		#now make the shadow to the right of the tabbed lists panel, out of a
		#vertical sizer, with a spacer at the top and a button filling the rest
		#-----------------------------------------------------------------------
		self.edit_area_shadow_right = wxWindow(self,-1,wxDefaultPosition,wxDefaultSize,0)
		self.edit_area_shadow_right.SetBackgroundColour(wxColor(131,129,131)) #gray shadow
		self.szr_edit_area_shadow_right = wxBoxSizer(wxVERTICAL)
		self.szr_edit_area_shadow_right.Add(0,5,0,wxEXPAND) #1:add the space
		self.szr_edit_area_shadow_right.Add(self.edit_area_shadow_right,1,wxEXPAND)

		#-------------------------------------------
		#add the shadow under the main summary panel
		#-------------------------------------------
		self.szr_main_panels = wxBoxSizer(wxHORIZONTAL)
		self.szr_main_panels.Add(self.szr_edit_prompts,10,wxEXPAND)
		self.szr_main_panels.Add(self.szr_edit_prompts_shadow_right,1,wxEXPAND)
		self.szr_main_panels.Add(5,0,0,wxEXPAND)
		self.szr_main_panels.Add(self.szr_edit_area,89,wxEXPAND)
		self.szr_main_panels.Add(self.szr_edit_area_shadow_right,1,wxEXPAND)
		self.szr_central_container.Add(self.szr_main_panels,1,wxEXPAND|wxALL,5)
		#--------------------------------------------------------------------
		#now create the  the main sizer to contain all the others on the form
		#--------------------------------------------------------------------
		self.szr_main_container = wxBoxSizer(wxVERTICAL)
		#--------------------------------------------------------------------------
		#Now add the top panel to the main background sizer of the whole frame, and
		#underneath that add a panel for demo purposes
		#--------------------------------------------------------------------------
		self.szr_main_container.Add(self.szr_central_container,10, wxEXPAND)
		self.SetSizer(self.szr_main_container)        #set the sizer 
		self.szr_main_container.Fit(self)             #set to minimum size as calculated by sizer
		self.SetAutoLayout(true)                 #tell frame to use the sizer
		self.Show(true)                          #show the panel 
		
        	
	
		
		
	
	def ConstructSizers(self):	
		pass
	def ConstructAllergies(self):
		#-------------------------------------------------------------------------
		#now create the controls necessary to add to the edit area for allergies
		#-------------------------------------------------------------------------
		pass
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (400, 500))
	app.SetWidget(EditArea, -1)
	app.MainLoop()

 

