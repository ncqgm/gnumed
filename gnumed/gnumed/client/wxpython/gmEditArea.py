#!/usr/bin/env python

from wxPython.wx import *

ID_PROGRESSNOTES = wxNewId()
gmSECTION_SUMMARY = 1
gmSECTION_DEMOGRAPHICS = 2
gmSECTION_CLINICALNOTES = 3
gmSECTION_FAMILYHISTORY = 4
gmSECTION_PASTHISTORY = 5
gmSECTION_VACCINATION = 6
gmSECTION_ALLERGIES = 7
gmSECTION_SCRIPT = 8
#--------------------------------------------
gmSECTION_REQUESTS = 9
ID_REQUEST_TYPE = wxNewId()
ID_REQUEST_COMPANY  = wxNewId()
ID_REQUEST_STREET  = wxNewId()
ID_REQUEST_SUBURB  = wxNewId()
ID_REQUEST_PHONE  = wxNewId()
ID_REQUEST_REQUESTS  = wxNewId()
ID_REQUEST_FORMNOTES = wxNewId()
ID_REQUEST_MEDICATIONS = wxNewId()
ID_REQUEST_INCLUDEALLMEDICATIONS  = wxNewId()
ID_REQUEST_COPYTO = wxNewId()
ID_REQUEST_BILL_BB = wxNewId()
ID_REQUEST_BILL_PRIVATE = wxNewId()
ID_REQUEST_BILL_wcover = wxNewId()
ID_REQUEST_BILL_REBATE  = wxNewId()
#---------------------------------------------
gmSECTION_MEASUREMENTS = 10
#---------------------------------------------
gmSECTION_REFERRALS = 11
ID_REFERRAL_CATEGORY        = wxNewId()
ID_REFERRAL_NAME        = wxNewId()
ID_REFERRAL_USEFIRSTNAME        = wxNewId()
ID_REFERRAL_ORGANISATION        = wxNewId()
ID_REFERRAL_HEADOFFICE        = wxNewId()
ID_REFERRAL_STREET1       = wxNewId()
ID_REFERRAL_STREET2        = wxNewId()
ID_REFERRAL_STREET3       = wxNewId()
ID_REFERRAL_SUBURB        = wxNewId()
ID_REFERRAL_POSTCODE        = wxNewId()
ID_REFERRAL_FOR        = wxNewId()
ID_REFERRAL_WPHONE        = wxNewId()
ID_REFERRAL_WFAX        = wxNewId()
ID_REFERRAL_WEMAIL        = wxNewId()
ID_REFERRAL_INCLUDE_MEDICATIONS        = wxNewId()
ID_REFERRAL_INCLUDE_SOCIALHISTORY       = wxNewId()
ID_REFERRAL_INCLUDE_FAMILYHISTORY        = wxNewId()
ID_REFERRAL_INCLUDE_PASTPROBLEMS        = wxNewId()
ID_REFERRAL_ACTIVEPROBLEMS       = wxNewId()
ID_REFERRAL_HABITS        = wxNewId()
ID_REFERRAL_INCLUDEALL        = wxNewId()
ID_BTN_PREVIEW = wxNewId()
ID_BTN_CLEAR = wxNewId()
ID_REFERRAL_COPYTO = wxNewId()
#----------------------------------------
gmSECTION_RECALLS = 12
ID_RECALLS_TOSEE  = wxNewId()
ID_RECALLS_TXT_FOR  = wxNewId()
ID_RECALLS_TXT_DATEDUE  = wxNewId()
ID_RECALLS_CONTACTMETHOD = wxNewId()
ID_RECALLS_APPNTLENGTH = wxNewId()
ID_RECALLS_TXT_ADDTEXT  = wxNewId()
ID_RECALLS_TXT_INCLUDEFORMS = wxNewId()
ID_RECALLS_TOSEE  = wxNewId()
ID_RECALLS_TXT_FOR  = wxNewId()
ID_RECALLS_TXT_DATEDUE  = wxNewId()
ID_RECALLS_CONTACTMETHOD = wxNewId()
ID_RECALLS_APPNTLENGTH = wxNewId()
ID_RECALLS_TXT_ADDTEXT  = wxNewId()
ID_RECALLS_TXT_INCLUDEFORMS = wxNewId()

richards_blue = wxColour(0,0,131)
richards_aqua = wxColour(0,194,197)

#------------------------------------------------------------
#text control class to be later replaced by the gmPhraseWheel
#------------------------------------------------------------
class  EditAreaTextBox(wxTextCtrl):
	def __init__ (self, parent, id, wxDefaultPostion, wxDefaultSize):
		wxTextCtrl.__init__(self,parent,id,"",wxDefaultPostion, wxDefaultSize,wxSIMPLE_BORDER)
		#self.SetBackgroundColour(wxColor(255,194,197))
		self.SetForegroundColour(wxColor(255,0,0))
		self.SetFont(wxFont(12,wxSWISS,wxBOLD,wxBOLD,false,''))

#--------------------------------------------------
#Class which shows a blue bold label left justified
#--------------------------------------------------
class EditAreaPromptLabel(wxStaticText):
	def __init__(self, parent, id, prompt, aColor = richards_blue):
		wxStaticText.__init__(self,parent, id,prompt,wxDefaultPosition,wxDefaultSize,wxALIGN_LEFT) 
		self.SetFont(wxFont(10,wxSWISS,wxBOLD,wxBOLD,false,''))
		self.SetForegroundColour(aColor)
#------------------------------------------------------------
#temporary Class which shoes a aqua bold label left justified
#until I pass the rgb colours down to the routine above
#------------------------------------------------------------
#class EditAreaPromptLabelAqua(wxStaticText):
#	def __init__(self, parent, id, prompt):
#		wxStaticText.__init__(self,parent, id,prompt,wxDefaultPosition,wxDefaultSize,wxALIGN_LEFT) 
#		self.SetFont(wxFont(10,wxSWISS,wxBOLD,wxBOLD,false,''))
#		self.SetForegroundColour()

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
				self.sizer.Add(EditAreaPromptLabel(self,-1, " " + prompt_array[key],aColor=richards_aqua),0,wxEXPAND)
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
		wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize,style = wxRAISED_BORDER|wxTAB_TRAVERSAL)	
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
		self.sizer_line9 = wxBoxSizer(wxHORIZONTAL) 
		self.sizer_line10 = wxBoxSizer(wxHORIZONTAL) 
		self.sizer_line11 = wxBoxSizer(wxHORIZONTAL) 
		self.sizer_line12 = wxBoxSizer(wxHORIZONTAL)
		self.btnOK = wxButton(self,-1,"Ok")
		self.btnClear = wxButton(self,-1,"Clear")
		self.sizer_btnokclear = wxBoxSizer(wxHORIZONTAL)
		self.sizer_btnokclear.Add(self.btnOK,1,wxEXPAND,wxALL,1)
		self.sizer_btnokclear.Add(5,0,0)
		self.sizer_btnokclear.Add(self.btnClear,1,wxEXPAND,wxALL,1)
		if section == gmSECTION_SUMMARY:
		      pass
	        elif section == gmSECTION_DEMOGRAPHICS:
		      pass
                elif section == gmSECTION_CLINICALNOTES:
		      pass
	        elif section == gmSECTION_FAMILYHISTORY:
		      self.txt_familymembername = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      self.txt_familymemberrelationship = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      self.txt_familymembercondition = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      self.txt_familymemberconditioncomment = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      self.txt_familymemberage_onset = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      self.txt_familymembercaused_death = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      self.txt_familymemberage_death = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      self.txt_familymemberprogressnotes = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      self.txt_familymemberdate_of_birth = EditAreaTextBox(self,-1,wxDefaultPosition,wxDefaultSize)
		      self.rb_familymember_conditionconfidential = wxRadioButton(self, 32, " Confidential ", wxDefaultPosition,wxDefaultSize)
		      self.btn_familymembernextcondition = wxButton(self,-1,"Next Condition")
		      self.lbl_familymember_DOB = EditAreaPromptLabel(self,-1,"  Date of Birth  ")
		      self.lbl_familymember_age_of_death = EditAreaPromptLabel(self,-1,"  Age of Death  ")
		      self.sizer_line1.Add(self.txt_familymembername,4,wxEXPAND)
		      self.sizer_line1.Add(self.lbl_familymember_DOB,2,wxEXPAND)
		      self.sizer_line1.Add(self.txt_familymemberdate_of_birth,4,wxEXPAND)
		      self.sizer_line2.Add(self.txt_familymemberrelationship,4,wxEXPAND)
		      self.sizer_line2.Add(self.lbl_familymember_age_of_death,2,wxEXPAND)
		      self.sizer_line2.Add(self.txt_familymemberage_death,4,wxEXPAND)
		      self.sizer_line3.Add(self.txt_familymembercondition, 6,wxEXPAND)
		      self.sizer_line3.Add(self.rb_familymember_conditionconfidential, 4,wxEXPAND)
		      #self.sizer_line4.Add(self.txt_familymemberconditioncomment, 1,wxEXPAND)
		      self.sizer_line5.Add(self.txt_familymemberage_onset, 1,wxEXPAND)
		      self.sizer_line5.Add(2,2,8)
		      self.sizer_line6.Add(self.txt_familymembercaused_death, 1,wxEXPAND)
		      self.sizer_line6.Add(2,2,8)
		      self.sizer_line7.Add(self.txt_familymemberprogressnotes, 1,wxEXPAND)
		      self.sizer_line8.AddSpacer(10,0,0)
		      self.sizer_line8.Add(self.btn_familymembernextcondition,0,wxEXPAND|wxALL,1)
		      self.sizer_line8.Add(2,1,5)
		      self.sizer_line8.Add(self.btnOK,1,wxEXPAND|wxALL,1)
	              self.sizer_line8.Add(self.btnClear,1,wxEXPAND|wxALL,1)  
		      
		       
		     
		      self.gs.Add(self.sizer_line1,0,wxEXPAND)
		      self.gs.Add(self.sizer_line2,0,wxEXPAND)
		      self.gs.Add(self.sizer_line3,0,wxEXPAND)
		      self.gs.Add(self.txt_familymemberconditioncomment,0,wxEXPAND)
		      self.gs.Add(self.sizer_line5,0,wxEXPAND)
		      self.gs.Add(self.sizer_line6,0,wxEXPAND)
		      self.gs.Add(self.txt_familymemberprogressnotes,0,wxEXPAND)
		      self.gs.Add(self.sizer_line8,0,wxEXPAND)
		      
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
		      gmLog.gmDefLog.Log (gmLog.lData, "section allergies")
		      #self.sizer = wxGridSizer (len(prompt_array),1,2,2)    
		      #gmLog.gmDefLog.Log (gmLog.lData, len(editareaprompts))
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
		      gmLog.gmDefLog.Log (gmLog.lData, "in script section now")
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
		      #----------------------------------------------------------------------------- 	
	              #editing area for general requests e.g pathology, radiology, physiotherapy etc
		      #create textboxes, radiobuttons etc
		      #-----------------------------------------------------------------------------
		      self.txt_request_type = EditAreaTextBox(self,ID_REQUEST_TYPE,wxDefaultPosition,wxDefaultSize)
		      self.txt_request_company = EditAreaTextBox(self,ID_REQUEST_COMPANY,wxDefaultPosition,wxDefaultSize)
		      self.txt_request_street = EditAreaTextBox(self,ID_REQUEST_STREET,wxDefaultPosition,wxDefaultSize)
		      self.txt_request_suburb = EditAreaTextBox(self,ID_REQUEST_SUBURB,wxDefaultPosition,wxDefaultSize)
		      self.txt_request_phone= EditAreaTextBox(self,ID_REQUEST_PHONE,wxDefaultPosition,wxDefaultSize)
		      self.txt_request_requests = EditAreaTextBox(self,ID_REQUEST_REQUESTS,wxDefaultPosition,wxDefaultSize)
		      self.txt_request_notes = EditAreaTextBox(self,ID_REQUEST_FORMNOTES,wxDefaultPosition,wxDefaultSize)
		      self.txt_request_medications = EditAreaTextBox(self,ID_REQUEST_MEDICATIONS,wxDefaultPosition,wxDefaultSize)
		      self.txt_request_copyto = EditAreaTextBox(self,ID_REQUEST_COPYTO,wxDefaultPosition,wxDefaultSize)
		      self.txt_request_progressnotes = EditAreaTextBox(self,ID_PROGRESSNOTES,wxDefaultPosition,wxDefaultSize)
		      self.lbl_companyphone = EditAreaPromptLabel(self,-1,"  Phone  ")
		      self.cb_includeallmedications = wxCheckBox(self, -1, " Include all medications ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
		      self.rb_request_bill_bb = wxRadioButton(self, ID_REQUEST_BILL_BB, "Bulk Bill ", wxDefaultPosition,wxDefaultSize)
	              self.rb_request_bill_private = wxRadioButton(self, ID_REQUEST_BILL_PRIVATE, "Private", wxDefaultPosition,wxDefaultSize,wxSUNKEN_BORDER)
		      self.rb_request_bill_rebate = wxRadioButton(self, ID_REQUEST_BILL_REBATE, "Rebate", wxDefaultPosition,wxDefaultSize)
		      self.rb_request_bill_wcover = wxRadioButton(self, ID_REQUEST_BILL_wcover, "w/cover", wxDefaultPosition,wxDefaultSize)
		      #--------------------------------------------------------------
                      #add controls to sizers where multiple controls per editor line
		      #--------------------------------------------------------------
                      self.sizer_request_optionbuttons = wxBoxSizer(wxHORIZONTAL)
		      self.sizer_request_optionbuttons.Add(self.rb_request_bill_bb,1,wxEXPAND)
		      self.sizer_request_optionbuttons.Add(self.rb_request_bill_private ,1,wxEXPAND)
                      self.sizer_request_optionbuttons.Add(self.rb_request_bill_rebate  ,1,wxEXPAND)
                      self.sizer_request_optionbuttons.Add(self.rb_request_bill_wcover  ,1,wxEXPAND)
		      self.sizer_line4.Add(self.txt_request_suburb,4,wxEXPAND)
		      self.sizer_line4.Add(self.lbl_companyphone,1,wxEXPAND)
		      self.sizer_line4.Add(self.txt_request_phone,2,wxEXPAND)
		      self.sizer_line7.Add(self.txt_request_medications, 4,wxEXPAND)
		      self.sizer_line7.Add(self.cb_includeallmedications,3,wxEXPAND)
		      self.sizer_line10.AddSizer(self.sizer_request_optionbuttons,3,wxEXPAND)
		      self.sizer_line10.AddSizer(self.sizer_btnokclear,1,wxEXPAND)
		      #self.sizer_line10.Add(self.btnOK,1,wxEXPAND|wxALL,1)
	              #self.sizer_line10.Add(self.btnClear,1,wxEXPAND|wxALL,1)  
		      #------------------------------------------------------------------
		      #add either controls or sizers with controls to vertical grid sizer
		      #------------------------------------------------------------------
                      self.gs.Add(self.txt_request_type,0,wxEXPAND)                   #e.g Pathology
		      self.gs.Add(self.txt_request_company,0,wxEXPAND)                #e.g Douglas Hanly Moir
		      self.gs.Add(self.txt_request_street,0,wxEXPAND)                 #e.g 120 Big Street  
		      self.gs.AddSizer(self.sizer_line4,0,wxEXPAND)                   #e.g RYDE NSW Phone 02 1800 222 365
		      self.gs.Add(self.txt_request_requests,0,wxEXPAND)               #e.g FBC;ESR;UEC;LFTS
		      self.gs.Add(self.txt_request_notes,0,wxEXPAND)                  #e.g generally tired;weight loss;
		      self.gs.AddSizer(self.sizer_line7,0,wxEXPAND)                   #e.g Lipitor;losec;zyprexa
		      self.gs.Add(self.txt_request_copyto,0,wxEXPAND)                 #e.g Dr I'm All Heart, 120 Big Street Smallville
		      self.gs.Add(self.txt_request_progressnotes,0,wxEXPAND)          #emphasised to patient must return for results 
                      self.sizer_line8.Add(5,0,6)
		      self.sizer_line8.Add(self.btnOK,1,wxEXPAND|wxALL,2)
	              self.sizer_line8.Add(self.btnClear,1,wxEXPAND|wxALL,2)   
		      self.gs.Add(self.sizer_line10,0,wxEXPAND)                       #options:b/bill private, rebate,w/cover btnok,btnclear
		      
	        elif section == gmSECTION_MEASUREMENTS:
		      pass
	        elif section == gmSECTION_REFERRALS:
		      self.btnpreview = wxButton(self,-1,"Preview")
		      self.sizer_btnpreviewok = wxBoxSizer(wxHORIZONTAL)
		      #--------------------------------------------------------
	              #editing area for referral letters, insurance letters etc
		      #create textboxes, checkboxes etc
		      #--------------------------------------------------------
		      self.txt_referralcategory = EditAreaTextBox(self,ID_REFERRAL_CATEGORY,wxDefaultPosition,wxDefaultSize)
		      self.txt_referralname = EditAreaTextBox(self,ID_REFERRAL_NAME,wxDefaultPosition,wxDefaultSize)
		      self.txt_referralorganisation = EditAreaTextBox(self,ID_REFERRAL_ORGANISATION,wxDefaultPosition,wxDefaultSize)
		      self.txt_referralstreet1 = EditAreaTextBox(self,ID_REFERRAL_STREET1,wxDefaultPosition,wxDefaultSize)
		      self.txt_referralstreet2 = EditAreaTextBox(self,ID_REFERRAL_STREET2,wxDefaultPosition,wxDefaultSize)
		      self.txt_referralstreet3 = EditAreaTextBox(self,ID_REFERRAL_STREET3,wxDefaultPosition,wxDefaultSize)
		      self.txt_referralsuburb = EditAreaTextBox(self,ID_REFERRAL_SUBURB,wxDefaultPosition,wxDefaultSize)
		      self.txt_referralpostcode = EditAreaTextBox(self,ID_REFERRAL_POSTCODE,wxDefaultPosition,wxDefaultSize)
		      self.txt_referralfor = EditAreaTextBox(self,ID_REFERRAL_FOR,wxDefaultPosition,wxDefaultSize)
		      self.txt_referralwphone= EditAreaTextBox(self,ID_REFERRAL_WPHONE,wxDefaultPosition,wxDefaultSize)
		      self.txt_referralwfax= EditAreaTextBox(self,ID_REFERRAL_WFAX,wxDefaultPosition,wxDefaultSize)
		      self.txt_referralwemail= EditAreaTextBox(self,ID_REFERRAL_WEMAIL,wxDefaultPosition,wxDefaultSize)
		      #self.txt_referralrequests = EditAreaTextBox(self,ID_REFERRAL_REQUESTS,wxDefaultPosition,wxDefaultSize)
		      #self.txt_referralnotes = EditAreaTextBox(self,ID_REFERRAL_FORMNOTES,wxDefaultPosition,wxDefaultSize)
		      #self.txt_referralmedications = EditAreaTextBox(self,ID_REFERRAL_MEDICATIONS,wxDefaultPosition,wxDefaultSize)
		      self.txt_referralcopyto = EditAreaTextBox(self,ID_REFERRAL_COPYTO,wxDefaultPosition,wxDefaultSize)
		      self.txt_referralprogressnotes = EditAreaTextBox(self,ID_PROGRESSNOTES,wxDefaultPosition,wxDefaultSize)
		      self.lbl_referralwphone = EditAreaPromptLabel(self,-1,"  W Phone  ")
		      self.lbl_referralwfax = EditAreaPromptLabel(self,-1,"  W Fax  ")
		      self.lbl_referralwemail = EditAreaPromptLabel(self,-1,"  W Email  ")
		      self.lbl_referralpostcode = EditAreaPromptLabel(self,-1,"  Postcode  ")
		      self.chkbox_referral_usefirstname = wxCheckBox(self, -1, " Use Firstname ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
		      self.chkbox_referral_headoffice = wxCheckBox(self, -1, " Head Office ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
		      self.chkbox_referral_medications = wxCheckBox(self, -1, " Medications ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
		      self.chkbox_referral_socialhistory = wxCheckBox(self, -1, " Social History ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
		      self.chkbox_referral_familyhistory = wxCheckBox(self, -1, " Family History ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
		      self.chkbox_referral_pastproblems = wxCheckBox(self, -1, " Past Problems ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
		      self.chkbox_referral_activeproblems = wxCheckBox(self, -1, " Active Problems ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
		      self.chkbox_referral_habits = wxCheckBox(self, -1, " Habits ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
		      #self.chkbox_referral_Includeall = wxCheckBox(self, -1, " Include all of the above ", wxDefaultPosition,wxDefaultSize, wxNO_BORDER)
		      #--------------------------------------------------------------
                      #add controls to sizers where multiple controls per editor line
		      #--------------------------------------------------------------
		      self.sizer_line2.Add(self.txt_referralname,2,wxEXPAND) 
		      self.sizer_line2.Add(self.chkbox_referral_usefirstname,2,wxEXPAND)
		      self.sizer_line3.Add(self.txt_referralorganisation,2,wxEXPAND)
		      self.sizer_line3.Add(self.chkbox_referral_headoffice,2, wxEXPAND)
		      self.sizer_line4.Add(self.txt_referralstreet1,2,wxEXPAND)
		      self.sizer_line4.Add(self.lbl_referralwphone,1,wxEXPAND)
		      self.sizer_line4.Add(self.txt_referralwphone,1,wxEXPAND)
		      self.sizer_line5.Add(self.txt_referralstreet2,2,wxEXPAND)
		      self.sizer_line5.Add(self.lbl_referralwfax,1,wxEXPAND)
		      self.sizer_line5.Add(self.txt_referralwfax,1,wxEXPAND)
		      self.sizer_line6.Add(self.txt_referralstreet3,2,wxEXPAND)
		      self.sizer_line6.Add(self.lbl_referralwemail,1,wxEXPAND)
		      self.sizer_line6.Add(self.txt_referralwemail,1,wxEXPAND)
		      self.sizer_line7.Add(self.txt_referralsuburb,2,wxEXPAND)
		      self.sizer_line7.Add(self.lbl_referralpostcode,1,wxEXPAND)
		      self.sizer_line7.Add(self.txt_referralpostcode,1,wxEXPAND)
		      self.sizer_line10.Add(self.chkbox_referral_medications,1,wxEXPAND)
	              self.sizer_line10.Add(self.chkbox_referral_socialhistory,1,wxEXPAND)
		      self.sizer_line10.Add(self.chkbox_referral_familyhistory,1,wxEXPAND)
		      self.sizer_line11.Add(self.chkbox_referral_pastproblems  ,1,wxEXPAND)
		      self.sizer_line11.Add(self.chkbox_referral_activeproblems  ,1,wxEXPAND)
		      self.sizer_line11.Add(self.chkbox_referral_habits  ,1,wxEXPAND)
		      self.sizer_btnpreviewok.Add(self.btnpreview,0,wxEXPAND)
		      self.sizer_btnokclear.Add(self.btnClear,0, wxEXPAND)
		      
		      #------------------------------------------------------------------
		      #add either controls or sizers with controls to vertical grid sizer
		      #------------------------------------------------------------------
                      self.gs.Add(self.txt_referralcategory,0,wxEXPAND)               #e.g Othopaedic surgeon
		      self.gs.Add(self.sizer_line2,0,wxEXPAND)                        #e.g Dr B Breaker
		      self.gs.Add(self.sizer_line3,0,wxEXPAND)                        #e.g General Orthopaedic servies
		      self.gs.Add(self.sizer_line4,0,wxEXPAND)                        #e.g street1
		      self.gs.Add(self.sizer_line5,0,wxEXPAND)                        #e.g street2
		      self.gs.Add(self.sizer_line6,0,wxEXPAND)                        #e.g street3
		      self.gs.Add(self.sizer_line7,0,wxEXPAND)                        #e.g suburb and postcode
		      self.gs.Add(self.txt_referralfor,0,wxEXPAND)                    #e.g Referral for an opinion
		      self.gs.Add(self.txt_referralcopyto,0,wxEXPAND)                 #e.g Dr I'm All Heart, 120 Big Street Smallville
		      self.gs.Add(self.txt_referralprogressnotes,0,wxEXPAND)          #emphasised to patient must return for results 
		      self.gs.AddSizer(self.sizer_line10,0,wxEXPAND)                   #e.g check boxes to include medications etc
		      self.gs.Add(self.sizer_line11,0,wxEXPAND)                       #e.g check boxes to include active problems etc
		      #self.spacer = wxWindow(self,-1,wxDefaultPosition,wxDefaultSize)
		      #self.spacer.SetBackgroundColour(wxColor(255,255,255))
		      self.sizer_line12.Add(5,0,6)
		      #self.sizer_line12.Add(self.spacer,6,wxEXPAND)
		      self.sizer_line12.Add(self.btnpreview,1,wxEXPAND|wxALL,2)
	              self.sizer_line12.Add(self.btnClear,1,wxEXPAND|wxALL,2)    
	              self.gs.Add(self.sizer_line12,0,wxEXPAND)                       #btnpreview and btn clear
		      
		elif section == gmSECTION_RECALLS:
		      #FIXME remove present options in this combo box	  #FIXME defaults need to be loaded from database	  
		      self.combo_tosee = wxComboBox(self, ID_RECALLS_TOSEE, "", wxDefaultPosition,wxDefaultSize, ['Doctor1','Doctor2','Nurse1','Dietition'], wxCB_READONLY ) #wxCB_DROPDOWN)
		      self.combo_tosee.SetFont(wxFont(12,wxSWISS,wxBOLD,wxBOLD,false,'xselfont'))
		      self.combo_tosee.SetForegroundColour(wxColor(255,0,0))
		      #FIXME defaults need to be loaded from database
		      self.combo_recall_method = wxComboBox(self, ID_RECALLS_CONTACTMETHOD, "", wxDefaultPosition,wxDefaultSize, ['Letter','Telephone','Email','Carrier pigeon'], wxCB_READONLY )
		      self.combo_recall_method.SetFont(wxFont(12,wxSWISS,wxBOLD,wxBOLD,false,'xselfont'))
		      self.combo_recall_method.SetForegroundColour(wxColor(255,0,0))
		      #FIXME defaults need to be loaded from database
                      self.combo_apptlength = wxComboBox(self, ID_RECALLS_APPNTLENGTH, "", wxDefaultPosition,wxDefaultSize, ['brief','standard','long','prolonged'], wxCB_READONLY )
		      self.combo_apptlength.SetFont(wxFont(12,wxSWISS,wxBOLD,wxBOLD,false,'xselfont'))
		      self.combo_apptlength.SetForegroundColour(wxColor(255,0,0))
		      self.txt_recall_for = EditAreaTextBox(self,ID_RECALLS_TXT_FOR, wxDefaultPosition,wxDefaultSize)
		      self.txt_recall_due = EditAreaTextBox(self,ID_RECALLS_TXT_DATEDUE, wxDefaultPosition,wxDefaultSize)
		      self.txt_recall_addtext = EditAreaTextBox(self,ID_RECALLS_TXT_ADDTEXT,wxDefaultPosition,wxDefaultSize)
		      self.txt_recall_include = EditAreaTextBox(self,ID_RECALLS_TXT_INCLUDEFORMS,wxDefaultPosition,wxDefaultSize)
		      self.txt_recall_progressnotes = EditAreaTextBox(self,ID_PROGRESSNOTES,wxDefaultPosition,wxDefaultSize)
		      self.lbl_recall_consultlength = EditAreaPromptLabel(self,-1,"  Appointment length  ")
		      #sizer_lkine1 has the method of recall and the appointment length
		      self.sizer_line1.Add(self.combo_recall_method,1,wxEXPAND)
		      self.sizer_line1.Add(self.lbl_recall_consultlength,1,wxEXPAND)
		      self.sizer_line1.Add(self.combo_apptlength,1,wxEXPAND)
		      #Now add the controls to the grid sizer
                      self.gs.Add(self.combo_tosee,1,wxEXPAND)                       #list of personel for patient to see
		      self.gs.Add(self.txt_recall_for,1,wxEXPAND)                    #the actual recall may be free text or word wheel  
		      self.gs.Add(self.txt_recall_due,1,wxEXPAND)                    #date of future recall 
		      self.gs.Add(self.txt_recall_addtext,1,wxEXPAND)                #added explanation e.g 'come fasting' 
		      self.gs.Add(self.txt_recall_include,1,wxEXPAND)                #any forms to be sent out first eg FBC
		      self.gs.AddSizer(self.sizer_line1,1,wxEXPAND)                        #the contact method, appointment length
		      self.gs.Add(self.txt_recall_progressnotes,1,wxEXPAND)          #add any progress notes for consultation
		      self.sizer_line8.Add(5,0,6)
		      self.sizer_line8.Add(self.btnOK,1,wxEXPAND|wxALL,2)
	              self.sizer_line8.Add(self.btnClear,1,wxEXPAND|wxALL,2)    
		      self.gs.Add(self.sizer_line8,1,wxEXPAND)
     
		else:
		      pass
			      
	        
		self.szr_edit_area.Add(self.gs,1,wxEXPAND)
		self.SetSizer(self.szr_edit_area)  
		self.szr_edit_area.Fit(self)            
		self.SetAutoLayout(true)                
		self.Show(true)
class EditArea(wxPanel):
	def __init__(self,parent,id,editareaprompts,section):
		wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize,style = wxNO_BORDER )	
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

if __name__ == "__main__":
	import sys
	sys.path.append ("../python-common/")
	import gmLog
	app = wxPyWidgetTester(size = (400, 500))
	app.SetWidget(EditArea, -1)
	app.MainLoop()
else:
	import gmLog
