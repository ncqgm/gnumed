# scanning for section headers,
#	then for components in file  gmEditArea.py 
#	and generating a script template for attaching
#	a listener to the components.  

from wxPython.wx import * 


class gmSECTION_SUMMARY_handler:

	def create_handler(self, panel):
		return gmSECTION_SUMMARY_handler(panel)

	def __init__(self, panel):
		self.panel = panel
		if panel <> None:
			self.__set_id()
			self.__set_evt()

	def __set_id(self):
		self.id_map = {}


		id = wxNewId()
		self.panel.btnOK.SetId(id)
		self.id_map['btnOK'] = id
		

		id = wxNewId()
		self.panel.btnClear.SetId(id)
		self.id_map['btnClear'] = id
		

	def __set_evt(self):
		pass
		

		EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.button_clicked_btnOK)

		EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.button_clicked_btnClear)

	def button_clicked_btnOK( self, event):
		pass

		print "button_clicked_btnOK received ", event
			

	def button_clicked_btnClear( self, event):
		pass

		print "button_clicked_btnClear received ", event
			


class gmSECTION_DEMOGRAPHICS_handler:

	def create_handler(self, panel):
		return gmSECTION_DEMOGRAPHICS_handler(panel)

	def __init__(self, panel):
		self.panel = panel
		if panel <> None:
			self.__set_id()
			self.__set_evt()

	def __set_id(self):
		self.id_map = {}


		id = wxNewId()
		self.panel.btnOK.SetId(id)
		self.id_map['btnOK'] = id
		

		id = wxNewId()
		self.panel.btnClear.SetId(id)
		self.id_map['btnClear'] = id
		

	def __set_evt(self):
		pass
		

		EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.button_clicked_btnOK)

		EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.button_clicked_btnClear)

	def button_clicked_btnOK( self, event):
		pass

		print "button_clicked_btnOK received ", event
			

	def button_clicked_btnClear( self, event):
		pass

		print "button_clicked_btnClear received ", event
			


class gmSECTION_CLINICALNOTES_handler:

	def create_handler(self, panel):
		return gmSECTION_CLINICALNOTES_handler(panel)

	def __init__(self, panel):
		self.panel = panel
		if panel <> None:
			self.__set_id()
			self.__set_evt()

	def __set_id(self):
		self.id_map = {}


		id = wxNewId()
		self.panel.btnOK.SetId(id)
		self.id_map['btnOK'] = id
		

		id = wxNewId()
		self.panel.btnClear.SetId(id)
		self.id_map['btnClear'] = id
		

	def __set_evt(self):
		pass
		

		EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.button_clicked_btnOK)

		EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.button_clicked_btnClear)

	def button_clicked_btnOK( self, event):
		pass

		print "button_clicked_btnOK received ", event
			

	def button_clicked_btnClear( self, event):
		pass

		print "button_clicked_btnClear received ", event
			


class gmSECTION_FAMILYHISTORY_handler:

	def create_handler(self, panel):
		return gmSECTION_FAMILYHISTORY_handler(panel)

	def __init__(self, panel):
		self.panel = panel
		if panel <> None:
			self.__set_id()
			self.__set_evt()

	def __set_id(self):
		self.id_map = {}


		id = wxNewId()
		self.panel.btnOK.SetId(id)
		self.id_map['btnOK'] = id
		

		id = wxNewId()
		self.panel.btnClear.SetId(id)
		self.id_map['btnClear'] = id
		

		id = wxNewId()
		self.panel.txt_familymembername.SetId(id)
		self.id_map['txt_familymembername'] = id
		

		id = wxNewId()
		self.panel.txt_familymemberrelationship.SetId(id)
		self.id_map['txt_familymemberrelationship'] = id
		

		id = wxNewId()
		self.panel.txt_familymembercondition.SetId(id)
		self.id_map['txt_familymembercondition'] = id
		

		id = wxNewId()
		self.panel.txt_familymemberconditioncomment.SetId(id)
		self.id_map['txt_familymemberconditioncomment'] = id
		

		id = wxNewId()
		self.panel.txt_familymemberage_onset.SetId(id)
		self.id_map['txt_familymemberage_onset'] = id
		

		id = wxNewId()
		self.panel.txt_familymembercaused_death.SetId(id)
		self.id_map['txt_familymembercaused_death'] = id
		

		id = wxNewId()
		self.panel.txt_familymemberage_death.SetId(id)
		self.id_map['txt_familymemberage_death'] = id
		

		id = wxNewId()
		self.panel.txt_familymemberprogressnotes.SetId(id)
		self.id_map['txt_familymemberprogressnotes'] = id
		

		id = wxNewId()
		self.panel.txt_familymemberdate_of_birth.SetId(id)
		self.id_map['txt_familymemberdate_of_birth'] = id
		

		id = wxNewId()
		self.panel.rb_familymember_conditionconfidential.SetId(id)
		self.id_map['rb_familymember_conditionconfidential'] = id
		

		id = wxNewId()
		self.panel.btn_familymembernextcondition.SetId(id)
		self.id_map['btn_familymembernextcondition'] = id
		

	def __set_evt(self):
		pass
		

		EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.button_clicked_btnOK)

		EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.button_clicked_btnClear)

		EVT_TEXT(self.panel.txt_familymembername,\
			self.id_map['txt_familymembername'],\
			self.text_entered_txt_familymembername)

		EVT_TEXT(self.panel.txt_familymemberrelationship,\
			self.id_map['txt_familymemberrelationship'],\
			self.text_entered_txt_familymemberrelationship)

		EVT_TEXT(self.panel.txt_familymembercondition,\
			self.id_map['txt_familymembercondition'],\
			self.text_entered_txt_familymembercondition)

		EVT_TEXT(self.panel.txt_familymemberconditioncomment,\
			self.id_map['txt_familymemberconditioncomment'],\
			self.text_entered_txt_familymemberconditioncomment)

		EVT_TEXT(self.panel.txt_familymemberage_onset,\
			self.id_map['txt_familymemberage_onset'],\
			self.text_entered_txt_familymemberage_onset)

		EVT_TEXT(self.panel.txt_familymembercaused_death,\
			self.id_map['txt_familymembercaused_death'],\
			self.text_entered_txt_familymembercaused_death)

		EVT_TEXT(self.panel.txt_familymemberage_death,\
			self.id_map['txt_familymemberage_death'],\
			self.text_entered_txt_familymemberage_death)

		EVT_TEXT(self.panel.txt_familymemberprogressnotes,\
			self.id_map['txt_familymemberprogressnotes'],\
			self.text_entered_txt_familymemberprogressnotes)

		EVT_TEXT(self.panel.txt_familymemberdate_of_birth,\
			self.id_map['txt_familymemberdate_of_birth'],\
			self.text_entered_txt_familymemberdate_of_birth)

		EVT_RADIOBUTTON(self.panel.rb_familymember_conditionconfidential,\
			self.id_map['rb_familymember_conditionconfidential'],\
			self.radiobutton_clicked_rb_familymember_conditionconfidential)

		EVT_BUTTON(self.panel.btn_familymembernextcondition,\
			self.id_map['btn_familymembernextcondition'],\
			self.button_clicked_btn_familymembernextcondition)

	def button_clicked_btnOK( self, event):
		pass

		print "button_clicked_btnOK received ", event
			

	def button_clicked_btnClear( self, event):
		pass

		print "button_clicked_btnClear received ", event
			

	def text_entered_txt_familymembername( self, event):
		pass

		print "text_entered_txt_familymembername received ", event
			

	def text_entered_txt_familymemberrelationship( self, event):
		pass

		print "text_entered_txt_familymemberrelationship received ", event
			

	def text_entered_txt_familymembercondition( self, event):
		pass

		print "text_entered_txt_familymembercondition received ", event
			

	def text_entered_txt_familymemberconditioncomment( self, event):
		pass

		print "text_entered_txt_familymemberconditioncomment received ", event
			

	def text_entered_txt_familymemberage_onset( self, event):
		pass

		print "text_entered_txt_familymemberage_onset received ", event
			

	def text_entered_txt_familymembercaused_death( self, event):
		pass

		print "text_entered_txt_familymembercaused_death received ", event
			

	def text_entered_txt_familymemberage_death( self, event):
		pass

		print "text_entered_txt_familymemberage_death received ", event
			

	def text_entered_txt_familymemberprogressnotes( self, event):
		pass

		print "text_entered_txt_familymemberprogressnotes received ", event
			

	def text_entered_txt_familymemberdate_of_birth( self, event):
		pass

		print "text_entered_txt_familymemberdate_of_birth received ", event
			

	def radiobutton_clicked_rb_familymember_conditionconfidential( self, event):
		pass

		print "radiobutton_clicked_rb_familymember_conditionconfidential received ", event
			

	def button_clicked_btn_familymembernextcondition( self, event):
		pass

		print "button_clicked_btn_familymembernextcondition received ", event
			


class gmSECTION_PASTHISTORY_handler:

	def create_handler(self, panel):
		return gmSECTION_PASTHISTORY_handler(panel)

	def __init__(self, panel):
		self.panel = panel
		if panel <> None:
			self.__set_id()
			self.__set_evt()

	def __set_id(self):
		self.id_map = {}


		id = wxNewId()
		self.panel.btnOK.SetId(id)
		self.id_map['btnOK'] = id
		

		id = wxNewId()
		self.panel.btnClear.SetId(id)
		self.id_map['btnClear'] = id
		

		id = wxNewId()
		self.panel.txt_condition.SetId(id)
		self.id_map['txt_condition'] = id
		

		id = wxNewId()
		self.panel.rb_sideleft.SetId(id)
		self.id_map['rb_sideleft'] = id
		

		id = wxNewId()
		self.panel.rb_sideright.SetId(id)
		self.id_map['rb_sideright'] = id
		

		id = wxNewId()
		self.panel.rb_sideboth.SetId(id)
		self.id_map['rb_sideboth'] = id
		

		id = wxNewId()
		self.panel.txt_notes1.SetId(id)
		self.id_map['txt_notes1'] = id
		

		id = wxNewId()
		self.panel.txt_notes2.SetId(id)
		self.id_map['txt_notes2'] = id
		

		id = wxNewId()
		self.panel.txt_agenoted.SetId(id)
		self.id_map['txt_agenoted'] = id
		

		id = wxNewId()
		self.panel.txt_yearnoted.SetId(id)
		self.id_map['txt_yearnoted'] = id
		

		id = wxNewId()
		self.panel.cb_active.SetId(id)
		self.id_map['cb_active'] = id
		

		id = wxNewId()
		self.panel.cb_operation.SetId(id)
		self.id_map['cb_operation'] = id
		

		id = wxNewId()
		self.panel.cb_confidential.SetId(id)
		self.id_map['cb_confidential'] = id
		

		id = wxNewId()
		self.panel.cb_significant.SetId(id)
		self.id_map['cb_significant'] = id
		

		id = wxNewId()
		self.panel.txt_progressnotes.SetId(id)
		self.id_map['txt_progressnotes'] = id
		

	def __set_evt(self):
		pass
		

		EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.button_clicked_btnOK)

		EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.button_clicked_btnClear)

		EVT_TEXT(self.panel.txt_condition,\
			self.id_map['txt_condition'],\
			self.text_entered_txt_condition)

		EVT_RADIOBUTTON(self.panel.rb_sideleft,\
			self.id_map['rb_sideleft'],\
			self.radiobutton_clicked_rb_sideleft)

		EVT_RADIOBUTTON(self.panel.rb_sideright,\
			self.id_map['rb_sideright'],\
			self.radiobutton_clicked_rb_sideright)

		EVT_RADIOBUTTON(self.panel.rb_sideboth,\
			self.id_map['rb_sideboth'],\
			self.radiobutton_clicked_rb_sideboth)

		EVT_TEXT(self.panel.txt_notes1,\
			self.id_map['txt_notes1'],\
			self.text_entered_txt_notes1)

		EVT_TEXT(self.panel.txt_notes2,\
			self.id_map['txt_notes2'],\
			self.text_entered_txt_notes2)

		EVT_TEXT(self.panel.txt_agenoted,\
			self.id_map['txt_agenoted'],\
			self.text_entered_txt_agenoted)

		EVT_TEXT(self.panel.txt_yearnoted,\
			self.id_map['txt_yearnoted'],\
			self.text_entered_txt_yearnoted)

		EVT_CHECKBOX(self.panel.cb_active,\
			self.id_map['cb_active'],\
			self.checkbox_clicked_cb_active)

		EVT_CHECKBOX(self.panel.cb_operation,\
			self.id_map['cb_operation'],\
			self.checkbox_clicked_cb_operation)

		EVT_CHECKBOX(self.panel.cb_confidential,\
			self.id_map['cb_confidential'],\
			self.checkbox_clicked_cb_confidential)

		EVT_CHECKBOX(self.panel.cb_significant,\
			self.id_map['cb_significant'],\
			self.checkbox_clicked_cb_significant)

		EVT_TEXT(self.panel.txt_progressnotes,\
			self.id_map['txt_progressnotes'],\
			self.text_entered_txt_progressnotes)

	def button_clicked_btnOK( self, event):
		pass

		print "button_clicked_btnOK received ", event
			

	def button_clicked_btnClear( self, event):
		pass

		print "button_clicked_btnClear received ", event
			

	def text_entered_txt_condition( self, event):
		pass

		print "text_entered_txt_condition received ", event
			

	def radiobutton_clicked_rb_sideleft( self, event):
		pass

		print "radiobutton_clicked_rb_sideleft received ", event
			

	def radiobutton_clicked_rb_sideright( self, event):
		pass

		print "radiobutton_clicked_rb_sideright received ", event
			

	def radiobutton_clicked_rb_sideboth( self, event):
		pass

		print "radiobutton_clicked_rb_sideboth received ", event
			

	def text_entered_txt_notes1( self, event):
		pass

		print "text_entered_txt_notes1 received ", event
			

	def text_entered_txt_notes2( self, event):
		pass

		print "text_entered_txt_notes2 received ", event
			

	def text_entered_txt_agenoted( self, event):
		pass

		print "text_entered_txt_agenoted received ", event
			

	def text_entered_txt_yearnoted( self, event):
		pass

		print "text_entered_txt_yearnoted received ", event
			

	def checkbox_clicked_cb_active( self, event):
		pass

		print "checkbox_clicked_cb_active received ", event
			

	def checkbox_clicked_cb_operation( self, event):
		pass

		print "checkbox_clicked_cb_operation received ", event
			

	def checkbox_clicked_cb_confidential( self, event):
		pass

		print "checkbox_clicked_cb_confidential received ", event
			

	def checkbox_clicked_cb_significant( self, event):
		pass

		print "checkbox_clicked_cb_significant received ", event
			

	def text_entered_txt_progressnotes( self, event):
		pass

		print "text_entered_txt_progressnotes received ", event
			


class gmSECTION_VACCINATION_handler:

	def create_handler(self, panel):
		return gmSECTION_VACCINATION_handler(panel)

	def __init__(self, panel):
		self.panel = panel
		if panel <> None:
			self.__set_id()
			self.__set_evt()

	def __set_id(self):
		self.id_map = {}


		id = wxNewId()
		self.panel.btnOK.SetId(id)
		self.id_map['btnOK'] = id
		

		id = wxNewId()
		self.panel.btnClear.SetId(id)
		self.id_map['btnClear'] = id
		

		id = wxNewId()
		self.panel.txt_targetdisease.SetId(id)
		self.id_map['txt_targetdisease'] = id
		

		id = wxNewId()
		self.panel.txt_vaccine.SetId(id)
		self.id_map['txt_vaccine'] = id
		

		id = wxNewId()
		self.panel.txt_dategiven.SetId(id)
		self.id_map['txt_dategiven'] = id
		

		id = wxNewId()
		self.panel.txt_serialno.SetId(id)
		self.id_map['txt_serialno'] = id
		

		id = wxNewId()
		self.panel.txt_sitegiven.SetId(id)
		self.id_map['txt_sitegiven'] = id
		

		id = wxNewId()
		self.panel.txt_progressnotes.SetId(id)
		self.id_map['txt_progressnotes'] = id
		

	def __set_evt(self):
		pass
		

		EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.button_clicked_btnOK)

		EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.button_clicked_btnClear)

		EVT_TEXT(self.panel.txt_targetdisease,\
			self.id_map['txt_targetdisease'],\
			self.text_entered_txt_targetdisease)

		EVT_TEXT(self.panel.txt_vaccine,\
			self.id_map['txt_vaccine'],\
			self.text_entered_txt_vaccine)

		EVT_TEXT(self.panel.txt_dategiven,\
			self.id_map['txt_dategiven'],\
			self.text_entered_txt_dategiven)

		EVT_TEXT(self.panel.txt_serialno,\
			self.id_map['txt_serialno'],\
			self.text_entered_txt_serialno)

		EVT_TEXT(self.panel.txt_sitegiven,\
			self.id_map['txt_sitegiven'],\
			self.text_entered_txt_sitegiven)

		EVT_TEXT(self.panel.txt_progressnotes,\
			self.id_map['txt_progressnotes'],\
			self.text_entered_txt_progressnotes)

	def button_clicked_btnOK( self, event):
		pass

		print "button_clicked_btnOK received ", event
			

	def button_clicked_btnClear( self, event):
		pass

		print "button_clicked_btnClear received ", event
			

	def text_entered_txt_targetdisease( self, event):
		pass

		print "text_entered_txt_targetdisease received ", event
			

	def text_entered_txt_vaccine( self, event):
		pass

		print "text_entered_txt_vaccine received ", event
			

	def text_entered_txt_dategiven( self, event):
		pass

		print "text_entered_txt_dategiven received ", event
			

	def text_entered_txt_serialno( self, event):
		pass

		print "text_entered_txt_serialno received ", event
			

	def text_entered_txt_sitegiven( self, event):
		pass

		print "text_entered_txt_sitegiven received ", event
			

	def text_entered_txt_progressnotes( self, event):
		pass

		print "text_entered_txt_progressnotes received ", event
			


class gmSECTION_ALLERGIES_handler:

	def create_handler(self, panel):
		return gmSECTION_ALLERGIES_handler(panel)

	def __init__(self, panel):
		self.panel = panel
		if panel <> None:
			self.__set_id()
			self.__set_evt()

	def __set_id(self):
		self.id_map = {}


		id = wxNewId()
		self.panel.btnOK.SetId(id)
		self.id_map['btnOK'] = id
		

		id = wxNewId()
		self.panel.btnClear.SetId(id)
		self.id_map['btnClear'] = id
		

		id = wxNewId()
		self.panel.text1.SetId(id)
		self.id_map['text1'] = id
		

		id = wxNewId()
		self.panel.text2.SetId(id)
		self.id_map['text2'] = id
		

		id = wxNewId()
		self.panel.text3.SetId(id)
		self.id_map['text3'] = id
		

		id = wxNewId()
		self.panel.text4.SetId(id)
		self.id_map['text4'] = id
		

		id = wxNewId()
		self.panel.text5.SetId(id)
		self.id_map['text5'] = id
		

		id = wxNewId()
		self.panel.cb1.SetId(id)
		self.id_map['cb1'] = id
		

		id = wxNewId()
		self.panel.rb1.SetId(id)
		self.id_map['rb1'] = id
		

		id = wxNewId()
		self.panel.rb2.SetId(id)
		self.id_map['rb2'] = id
		

		id = wxNewId()
		self.panel.cb2.SetId(id)
		self.id_map['cb2'] = id
		

	def __set_evt(self):
		pass
		

		EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.button_clicked_btnOK)

		EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.button_clicked_btnClear)

		EVT_TEXT(self.panel.text1,\
			self.id_map['text1'],\
			self.text_entered_text1)

		EVT_TEXT(self.panel.text2,\
			self.id_map['text2'],\
			self.text_entered_text2)

		EVT_TEXT(self.panel.text3,\
			self.id_map['text3'],\
			self.text_entered_text3)

		EVT_TEXT(self.panel.text4,\
			self.id_map['text4'],\
			self.text_entered_text4)

		EVT_TEXT(self.panel.text5,\
			self.id_map['text5'],\
			self.text_entered_text5)

		EVT_CHECKBOX(self.panel.cb1,\
			self.id_map['cb1'],\
			self.checkbox_clicked_cb1)

		EVT_RADIOBUTTON(self.panel.rb1,\
			self.id_map['rb1'],\
			self.radiobutton_clicked_rb1)

		EVT_RADIOBUTTON(self.panel.rb2,\
			self.id_map['rb2'],\
			self.radiobutton_clicked_rb2)

		EVT_CHECKBOX(self.panel.cb2,\
			self.id_map['cb2'],\
			self.checkbox_clicked_cb2)

	def button_clicked_btnOK( self, event):
		pass

		print "button_clicked_btnOK received ", event
			

	def button_clicked_btnClear( self, event):
		pass

		print "button_clicked_btnClear received ", event
			

	def text_entered_text1( self, event):
		pass

		print "text_entered_text1 received ", event
			

	def text_entered_text2( self, event):
		pass

		print "text_entered_text2 received ", event
			

	def text_entered_text3( self, event):
		pass

		print "text_entered_text3 received ", event
			

	def text_entered_text4( self, event):
		pass

		print "text_entered_text4 received ", event
			

	def text_entered_text5( self, event):
		pass

		print "text_entered_text5 received ", event
			

	def checkbox_clicked_cb1( self, event):
		pass

		print "checkbox_clicked_cb1 received ", event
			

	def radiobutton_clicked_rb1( self, event):
		pass

		print "radiobutton_clicked_rb1 received ", event
			

	def radiobutton_clicked_rb2( self, event):
		pass

		print "radiobutton_clicked_rb2 received ", event
			

	def checkbox_clicked_cb2( self, event):
		pass

		print "checkbox_clicked_cb2 received ", event
			


class gmSECTION_SCRIPT_handler:

	def create_handler(self, panel):
		return gmSECTION_SCRIPT_handler(panel)

	def __init__(self, panel):
		self.panel = panel
		if panel <> None:
			self.__set_id()
			self.__set_evt()

	def __set_id(self):
		self.id_map = {}


		id = wxNewId()
		self.panel.btnOK.SetId(id)
		self.id_map['btnOK'] = id
		

		id = wxNewId()
		self.panel.btnClear.SetId(id)
		self.id_map['btnClear'] = id
		

		id = wxNewId()
		self.panel.text1.SetId(id)
		self.id_map['text1'] = id
		

		id = wxNewId()
		self.panel.text2.SetId(id)
		self.id_map['text2'] = id
		

		id = wxNewId()
		self.panel.text3.SetId(id)
		self.id_map['text3'] = id
		

		id = wxNewId()
		self.panel.text4.SetId(id)
		self.id_map['text4'] = id
		

		id = wxNewId()
		self.panel.text5.SetId(id)
		self.id_map['text5'] = id
		

		id = wxNewId()
		self.panel.text6.SetId(id)
		self.id_map['text6'] = id
		

		id = wxNewId()
		self.panel.text7.SetId(id)
		self.id_map['text7'] = id
		

		id = wxNewId()
		self.panel.text8.SetId(id)
		self.id_map['text8'] = id
		

		id = wxNewId()
		self.panel.text9.SetId(id)
		self.id_map['text9'] = id
		

		id = wxNewId()
		self.panel.cb_veteran.SetId(id)
		self.id_map['cb_veteran'] = id
		

		id = wxNewId()
		self.panel.cb_reg24.SetId(id)
		self.id_map['cb_reg24'] = id
		

		id = wxNewId()
		self.panel.cb_usualmed.SetId(id)
		self.id_map['cb_usualmed'] = id
		

		id = wxNewId()
		self.panel.btn_authority.SetId(id)
		self.id_map['btn_authority'] = id
		

		id = wxNewId()
		self.panel.btn_briefPI.SetId(id)
		self.id_map['btn_briefPI'] = id
		

		id = wxNewId()
		self.panel.text10.SetId(id)
		self.id_map['text10'] = id
		

	def __set_evt(self):
		pass
		

		EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.button_clicked_btnOK)

		EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.button_clicked_btnClear)

		EVT_TEXT(self.panel.text1,\
			self.id_map['text1'],\
			self.text_entered_text1)

		EVT_TEXT(self.panel.text2,\
			self.id_map['text2'],\
			self.text_entered_text2)

		EVT_TEXT(self.panel.text3,\
			self.id_map['text3'],\
			self.text_entered_text3)

		EVT_TEXT(self.panel.text4,\
			self.id_map['text4'],\
			self.text_entered_text4)

		EVT_TEXT(self.panel.text5,\
			self.id_map['text5'],\
			self.text_entered_text5)

		EVT_TEXT(self.panel.text6,\
			self.id_map['text6'],\
			self.text_entered_text6)

		EVT_TEXT(self.panel.text7,\
			self.id_map['text7'],\
			self.text_entered_text7)

		EVT_TEXT(self.panel.text8,\
			self.id_map['text8'],\
			self.text_entered_text8)

		EVT_TEXT(self.panel.text9,\
			self.id_map['text9'],\
			self.text_entered_text9)

		EVT_CHECKBOX(self.panel.cb_veteran,\
			self.id_map['cb_veteran'],\
			self.checkbox_clicked_cb_veteran)

		EVT_CHECKBOX(self.panel.cb_reg24,\
			self.id_map['cb_reg24'],\
			self.checkbox_clicked_cb_reg24)

		EVT_CHECKBOX(self.panel.cb_usualmed,\
			self.id_map['cb_usualmed'],\
			self.checkbox_clicked_cb_usualmed)

		EVT_BUTTON(self.panel.btn_authority,\
			self.id_map['btn_authority'],\
			self.button_clicked_btn_authority)

		EVT_BUTTON(self.panel.btn_briefPI,\
			self.id_map['btn_briefPI'],\
			self.button_clicked_btn_briefPI)

		EVT_TEXT(self.panel.text10,\
			self.id_map['text10'],\
			self.text_entered_text10)

	def button_clicked_btnOK( self, event):
		pass

		print "button_clicked_btnOK received ", event
			

	def button_clicked_btnClear( self, event):
		pass

		print "button_clicked_btnClear received ", event
			

	def text_entered_text1( self, event):
		pass

		print "text_entered_text1 received ", event
			

	def text_entered_text2( self, event):
		pass

		print "text_entered_text2 received ", event
			

	def text_entered_text3( self, event):
		pass

		print "text_entered_text3 received ", event
			

	def text_entered_text4( self, event):
		pass

		print "text_entered_text4 received ", event
			

	def text_entered_text5( self, event):
		pass

		print "text_entered_text5 received ", event
			

	def text_entered_text6( self, event):
		pass

		print "text_entered_text6 received ", event
			

	def text_entered_text7( self, event):
		pass

		print "text_entered_text7 received ", event
			

	def text_entered_text8( self, event):
		pass

		print "text_entered_text8 received ", event
			

	def text_entered_text9( self, event):
		pass

		print "text_entered_text9 received ", event
			

	def checkbox_clicked_cb_veteran( self, event):
		pass

		print "checkbox_clicked_cb_veteran received ", event
			

	def checkbox_clicked_cb_reg24( self, event):
		pass

		print "checkbox_clicked_cb_reg24 received ", event
			

	def checkbox_clicked_cb_usualmed( self, event):
		pass

		print "checkbox_clicked_cb_usualmed received ", event
			

	def button_clicked_btn_authority( self, event):
		pass

		print "button_clicked_btn_authority received ", event
			

	def button_clicked_btn_briefPI( self, event):
		pass

		print "button_clicked_btn_briefPI received ", event
			

	def text_entered_text10( self, event):
		pass

		print "text_entered_text10 received ", event
			


class gmSECTION_REQUESTS_handler:

	def create_handler(self, panel):
		return gmSECTION_REQUESTS_handler(panel)

	def __init__(self, panel):
		self.panel = panel
		if panel <> None:
			self.__set_id()
			self.__set_evt()

	def __set_id(self):
		self.id_map = {}


		id = wxNewId()
		self.panel.btnOK.SetId(id)
		self.id_map['btnOK'] = id
		

		id = wxNewId()
		self.panel.btnClear.SetId(id)
		self.id_map['btnClear'] = id
		

		id = wxNewId()
		self.panel.txt_request_type.SetId(id)
		self.id_map['txt_request_type'] = id
		

		id = wxNewId()
		self.panel.txt_request_company.SetId(id)
		self.id_map['txt_request_company'] = id
		

		id = wxNewId()
		self.panel.txt_request_street.SetId(id)
		self.id_map['txt_request_street'] = id
		

		id = wxNewId()
		self.panel.txt_request_suburb.SetId(id)
		self.id_map['txt_request_suburb'] = id
		

		id = wxNewId()
		self.panel.txt_request_phone.SetId(id)
		self.id_map['txt_request_phone'] = id
		

		id = wxNewId()
		self.panel.txt_request_requests.SetId(id)
		self.id_map['txt_request_requests'] = id
		

		id = wxNewId()
		self.panel.txt_request_notes.SetId(id)
		self.id_map['txt_request_notes'] = id
		

		id = wxNewId()
		self.panel.txt_request_medications.SetId(id)
		self.id_map['txt_request_medications'] = id
		

		id = wxNewId()
		self.panel.txt_request_copyto.SetId(id)
		self.id_map['txt_request_copyto'] = id
		

		id = wxNewId()
		self.panel.txt_request_progressnotes.SetId(id)
		self.id_map['txt_request_progressnotes'] = id
		

		id = wxNewId()
		self.panel.cb_includeallmedications.SetId(id)
		self.id_map['cb_includeallmedications'] = id
		

		id = wxNewId()
		self.panel.rb_request_bill_bb.SetId(id)
		self.id_map['rb_request_bill_bb'] = id
		

		id = wxNewId()
		self.panel.rb_request_bill_private.SetId(id)
		self.id_map['rb_request_bill_private'] = id
		

		id = wxNewId()
		self.panel.rb_request_bill_rebate.SetId(id)
		self.id_map['rb_request_bill_rebate'] = id
		

		id = wxNewId()
		self.panel.rb_request_bill_wcover.SetId(id)
		self.id_map['rb_request_bill_wcover'] = id
		

	def __set_evt(self):
		pass
		

		EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.button_clicked_btnOK)

		EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.button_clicked_btnClear)

		EVT_TEXT(self.panel.txt_request_type,\
			self.id_map['txt_request_type'],\
			self.text_entered_txt_request_type)

		EVT_TEXT(self.panel.txt_request_company,\
			self.id_map['txt_request_company'],\
			self.text_entered_txt_request_company)

		EVT_TEXT(self.panel.txt_request_street,\
			self.id_map['txt_request_street'],\
			self.text_entered_txt_request_street)

		EVT_TEXT(self.panel.txt_request_suburb,\
			self.id_map['txt_request_suburb'],\
			self.text_entered_txt_request_suburb)

		EVT_TEXT(self.panel.txt_request_phone,\
			self.id_map['txt_request_phone'],\
			self.text_entered_txt_request_phone)

		EVT_TEXT(self.panel.txt_request_requests,\
			self.id_map['txt_request_requests'],\
			self.text_entered_txt_request_requests)

		EVT_TEXT(self.panel.txt_request_notes,\
			self.id_map['txt_request_notes'],\
			self.text_entered_txt_request_notes)

		EVT_TEXT(self.panel.txt_request_medications,\
			self.id_map['txt_request_medications'],\
			self.text_entered_txt_request_medications)

		EVT_TEXT(self.panel.txt_request_copyto,\
			self.id_map['txt_request_copyto'],\
			self.text_entered_txt_request_copyto)

		EVT_TEXT(self.panel.txt_request_progressnotes,\
			self.id_map['txt_request_progressnotes'],\
			self.text_entered_txt_request_progressnotes)

		EVT_CHECKBOX(self.panel.cb_includeallmedications,\
			self.id_map['cb_includeallmedications'],\
			self.checkbox_clicked_cb_includeallmedications)

		EVT_RADIOBUTTON(self.panel.rb_request_bill_bb,\
			self.id_map['rb_request_bill_bb'],\
			self.radiobutton_clicked_rb_request_bill_bb)

		EVT_RADIOBUTTON(self.panel.rb_request_bill_private,\
			self.id_map['rb_request_bill_private'],\
			self.radiobutton_clicked_rb_request_bill_private)

		EVT_RADIOBUTTON(self.panel.rb_request_bill_rebate,\
			self.id_map['rb_request_bill_rebate'],\
			self.radiobutton_clicked_rb_request_bill_rebate)

		EVT_RADIOBUTTON(self.panel.rb_request_bill_wcover,\
			self.id_map['rb_request_bill_wcover'],\
			self.radiobutton_clicked_rb_request_bill_wcover)

	def button_clicked_btnOK( self, event):
		pass

		print "button_clicked_btnOK received ", event
			

	def button_clicked_btnClear( self, event):
		pass

		print "button_clicked_btnClear received ", event
			

	def text_entered_txt_request_type( self, event):
		pass

		print "text_entered_txt_request_type received ", event
			

	def text_entered_txt_request_company( self, event):
		pass

		print "text_entered_txt_request_company received ", event
			

	def text_entered_txt_request_street( self, event):
		pass

		print "text_entered_txt_request_street received ", event
			

	def text_entered_txt_request_suburb( self, event):
		pass

		print "text_entered_txt_request_suburb received ", event
			

	def text_entered_txt_request_phone( self, event):
		pass

		print "text_entered_txt_request_phone received ", event
			

	def text_entered_txt_request_requests( self, event):
		pass

		print "text_entered_txt_request_requests received ", event
			

	def text_entered_txt_request_notes( self, event):
		pass

		print "text_entered_txt_request_notes received ", event
			

	def text_entered_txt_request_medications( self, event):
		pass

		print "text_entered_txt_request_medications received ", event
			

	def text_entered_txt_request_copyto( self, event):
		pass

		print "text_entered_txt_request_copyto received ", event
			

	def text_entered_txt_request_progressnotes( self, event):
		pass

		print "text_entered_txt_request_progressnotes received ", event
			

	def checkbox_clicked_cb_includeallmedications( self, event):
		pass

		print "checkbox_clicked_cb_includeallmedications received ", event
			

	def radiobutton_clicked_rb_request_bill_bb( self, event):
		pass

		print "radiobutton_clicked_rb_request_bill_bb received ", event
			

	def radiobutton_clicked_rb_request_bill_private( self, event):
		pass

		print "radiobutton_clicked_rb_request_bill_private received ", event
			

	def radiobutton_clicked_rb_request_bill_rebate( self, event):
		pass

		print "radiobutton_clicked_rb_request_bill_rebate received ", event
			

	def radiobutton_clicked_rb_request_bill_wcover( self, event):
		pass

		print "radiobutton_clicked_rb_request_bill_wcover received ", event
			


class gmSECTION_MEASUREMENTS_handler:

	def create_handler(self, panel):
		return gmSECTION_MEASUREMENTS_handler(panel)

	def __init__(self, panel):
		self.panel = panel
		if panel <> None:
			self.__set_id()
			self.__set_evt()

	def __set_id(self):
		self.id_map = {}


		id = wxNewId()
		self.panel.btnOK.SetId(id)
		self.id_map['btnOK'] = id
		

		id = wxNewId()
		self.panel.btnClear.SetId(id)
		self.id_map['btnClear'] = id
		

		id = wxNewId()
		self.panel.combo_measurement_type.SetId(id)
		self.id_map['combo_measurement_type'] = id
		

		id = wxNewId()
		self.panel.txt_measurement_value.SetId(id)
		self.id_map['txt_measurement_value'] = id
		

		id = wxNewId()
		self.panel.txt_txt_measurement_date.SetId(id)
		self.id_map['txt_txt_measurement_date'] = id
		

		id = wxNewId()
		self.panel.txt_txt_measurement_comment.SetId(id)
		self.id_map['txt_txt_measurement_comment'] = id
		

		id = wxNewId()
		self.panel.txt_txt_measurement_progressnote.SetId(id)
		self.id_map['txt_txt_measurement_progressnote'] = id
		

		id = wxNewId()
		self.panel.btn_nextvalue.SetId(id)
		self.id_map['btn_nextvalue'] = id
		

		id = wxNewId()
		self.panel.btn_graph.SetId(id)
		self.id_map['btn_graph'] = id
		

	def __set_evt(self):
		pass
		

		EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.button_clicked_btnOK)

		EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.button_clicked_btnClear)

		EVT_TEXT(self.panel.combo_measurement_type,\
			self.id_map['combo_measurement_type'],\
			self.text_entered_combo_measurement_type)

		EVT_TEXT(self.panel.txt_measurement_value,\
			self.id_map['txt_measurement_value'],\
			self.text_entered_txt_measurement_value)

		EVT_TEXT(self.panel.txt_txt_measurement_date,\
			self.id_map['txt_txt_measurement_date'],\
			self.text_entered_txt_txt_measurement_date)

		EVT_TEXT(self.panel.txt_txt_measurement_comment,\
			self.id_map['txt_txt_measurement_comment'],\
			self.text_entered_txt_txt_measurement_comment)

		EVT_TEXT(self.panel.txt_txt_measurement_progressnote,\
			self.id_map['txt_txt_measurement_progressnote'],\
			self.text_entered_txt_txt_measurement_progressnote)

		EVT_BUTTON(self.panel.btn_nextvalue,\
			self.id_map['btn_nextvalue'],\
			self.button_clicked_btn_nextvalue)

		EVT_BUTTON(self.panel.btn_graph,\
			self.id_map['btn_graph'],\
			self.button_clicked_btn_graph)

	def button_clicked_btnOK( self, event):
		pass

		print "button_clicked_btnOK received ", event
			

	def button_clicked_btnClear( self, event):
		pass

		print "button_clicked_btnClear received ", event
			

	def text_entered_combo_measurement_type( self, event):
		pass

		print "text_entered_combo_measurement_type received ", event
			

	def text_entered_txt_measurement_value( self, event):
		pass

		print "text_entered_txt_measurement_value received ", event
			

	def text_entered_txt_txt_measurement_date( self, event):
		pass

		print "text_entered_txt_txt_measurement_date received ", event
			

	def text_entered_txt_txt_measurement_comment( self, event):
		pass

		print "text_entered_txt_txt_measurement_comment received ", event
			

	def text_entered_txt_txt_measurement_progressnote( self, event):
		pass

		print "text_entered_txt_txt_measurement_progressnote received ", event
			

	def button_clicked_btn_nextvalue( self, event):
		pass

		print "button_clicked_btn_nextvalue received ", event
			

	def button_clicked_btn_graph( self, event):
		pass

		print "button_clicked_btn_graph received ", event
			


class gmSECTION_REFERRALS_handler:

	def create_handler(self, panel):
		return gmSECTION_REFERRALS_handler(panel)

	def __init__(self, panel):
		self.panel = panel
		if panel <> None:
			self.__set_id()
			self.__set_evt()

	def __set_id(self):
		self.id_map = {}


		id = wxNewId()
		self.panel.btnOK.SetId(id)
		self.id_map['btnOK'] = id
		

		id = wxNewId()
		self.panel.btnClear.SetId(id)
		self.id_map['btnClear'] = id
		

		id = wxNewId()
		self.panel.btnpreview.SetId(id)
		self.id_map['btnpreview'] = id
		

		id = wxNewId()
		self.panel.txt_referralcategory.SetId(id)
		self.id_map['txt_referralcategory'] = id
		

		id = wxNewId()
		self.panel.txt_referralname.SetId(id)
		self.id_map['txt_referralname'] = id
		

		id = wxNewId()
		self.panel.txt_referralorganisation.SetId(id)
		self.id_map['txt_referralorganisation'] = id
		

		id = wxNewId()
		self.panel.txt_referralstreet1.SetId(id)
		self.id_map['txt_referralstreet1'] = id
		

		id = wxNewId()
		self.panel.txt_referralstreet2.SetId(id)
		self.id_map['txt_referralstreet2'] = id
		

		id = wxNewId()
		self.panel.txt_referralstreet3.SetId(id)
		self.id_map['txt_referralstreet3'] = id
		

		id = wxNewId()
		self.panel.txt_referralsuburb.SetId(id)
		self.id_map['txt_referralsuburb'] = id
		

		id = wxNewId()
		self.panel.txt_referralpostcode.SetId(id)
		self.id_map['txt_referralpostcode'] = id
		

		id = wxNewId()
		self.panel.txt_referralfor.SetId(id)
		self.id_map['txt_referralfor'] = id
		

		id = wxNewId()
		self.panel.txt_referralwphone.SetId(id)
		self.id_map['txt_referralwphone'] = id
		

		id = wxNewId()
		self.panel.txt_referralwfax.SetId(id)
		self.id_map['txt_referralwfax'] = id
		

		id = wxNewId()
		self.panel.txt_referralwemail.SetId(id)
		self.id_map['txt_referralwemail'] = id
		

		id = wxNewId()
		self.panel.txt_referralcopyto.SetId(id)
		self.id_map['txt_referralcopyto'] = id
		

		id = wxNewId()
		self.panel.txt_referralprogressnotes.SetId(id)
		self.id_map['txt_referralprogressnotes'] = id
		

		id = wxNewId()
		self.panel.chkbox_referral_usefirstname.SetId(id)
		self.id_map['chkbox_referral_usefirstname'] = id
		

		id = wxNewId()
		self.panel.chkbox_referral_headoffice.SetId(id)
		self.id_map['chkbox_referral_headoffice'] = id
		

		id = wxNewId()
		self.panel.chkbox_referral_medications.SetId(id)
		self.id_map['chkbox_referral_medications'] = id
		

		id = wxNewId()
		self.panel.chkbox_referral_socialhistory.SetId(id)
		self.id_map['chkbox_referral_socialhistory'] = id
		

		id = wxNewId()
		self.panel.chkbox_referral_familyhistory.SetId(id)
		self.id_map['chkbox_referral_familyhistory'] = id
		

		id = wxNewId()
		self.panel.chkbox_referral_pastproblems.SetId(id)
		self.id_map['chkbox_referral_pastproblems'] = id
		

		id = wxNewId()
		self.panel.chkbox_referral_activeproblems.SetId(id)
		self.id_map['chkbox_referral_activeproblems'] = id
		

		id = wxNewId()
		self.panel.chkbox_referral_habits.SetId(id)
		self.id_map['chkbox_referral_habits'] = id
		

	def __set_evt(self):
		pass
		

		EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.button_clicked_btnOK)

		EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.button_clicked_btnClear)

		EVT_BUTTON(self.panel.btnpreview,\
			self.id_map['btnpreview'],\
			self.button_clicked_btnpreview)

		EVT_TEXT(self.panel.txt_referralcategory,\
			self.id_map['txt_referralcategory'],\
			self.text_entered_txt_referralcategory)

		EVT_TEXT(self.panel.txt_referralname,\
			self.id_map['txt_referralname'],\
			self.text_entered_txt_referralname)

		EVT_TEXT(self.panel.txt_referralorganisation,\
			self.id_map['txt_referralorganisation'],\
			self.text_entered_txt_referralorganisation)

		EVT_TEXT(self.panel.txt_referralstreet1,\
			self.id_map['txt_referralstreet1'],\
			self.text_entered_txt_referralstreet1)

		EVT_TEXT(self.panel.txt_referralstreet2,\
			self.id_map['txt_referralstreet2'],\
			self.text_entered_txt_referralstreet2)

		EVT_TEXT(self.panel.txt_referralstreet3,\
			self.id_map['txt_referralstreet3'],\
			self.text_entered_txt_referralstreet3)

		EVT_TEXT(self.panel.txt_referralsuburb,\
			self.id_map['txt_referralsuburb'],\
			self.text_entered_txt_referralsuburb)

		EVT_TEXT(self.panel.txt_referralpostcode,\
			self.id_map['txt_referralpostcode'],\
			self.text_entered_txt_referralpostcode)

		EVT_TEXT(self.panel.txt_referralfor,\
			self.id_map['txt_referralfor'],\
			self.text_entered_txt_referralfor)

		EVT_TEXT(self.panel.txt_referralwphone,\
			self.id_map['txt_referralwphone'],\
			self.text_entered_txt_referralwphone)

		EVT_TEXT(self.panel.txt_referralwfax,\
			self.id_map['txt_referralwfax'],\
			self.text_entered_txt_referralwfax)

		EVT_TEXT(self.panel.txt_referralwemail,\
			self.id_map['txt_referralwemail'],\
			self.text_entered_txt_referralwemail)

		EVT_TEXT(self.panel.txt_referralcopyto,\
			self.id_map['txt_referralcopyto'],\
			self.text_entered_txt_referralcopyto)

		EVT_TEXT(self.panel.txt_referralprogressnotes,\
			self.id_map['txt_referralprogressnotes'],\
			self.text_entered_txt_referralprogressnotes)

		EVT_CHECKBOX(self.panel.chkbox_referral_usefirstname,\
			self.id_map['chkbox_referral_usefirstname'],\
			self.checkbox_clicked_chkbox_referral_usefirstname)

		EVT_CHECKBOX(self.panel.chkbox_referral_headoffice,\
			self.id_map['chkbox_referral_headoffice'],\
			self.checkbox_clicked_chkbox_referral_headoffice)

		EVT_CHECKBOX(self.panel.chkbox_referral_medications,\
			self.id_map['chkbox_referral_medications'],\
			self.checkbox_clicked_chkbox_referral_medications)

		EVT_CHECKBOX(self.panel.chkbox_referral_socialhistory,\
			self.id_map['chkbox_referral_socialhistory'],\
			self.checkbox_clicked_chkbox_referral_socialhistory)

		EVT_CHECKBOX(self.panel.chkbox_referral_familyhistory,\
			self.id_map['chkbox_referral_familyhistory'],\
			self.checkbox_clicked_chkbox_referral_familyhistory)

		EVT_CHECKBOX(self.panel.chkbox_referral_pastproblems,\
			self.id_map['chkbox_referral_pastproblems'],\
			self.checkbox_clicked_chkbox_referral_pastproblems)

		EVT_CHECKBOX(self.panel.chkbox_referral_activeproblems,\
			self.id_map['chkbox_referral_activeproblems'],\
			self.checkbox_clicked_chkbox_referral_activeproblems)

		EVT_CHECKBOX(self.panel.chkbox_referral_habits,\
			self.id_map['chkbox_referral_habits'],\
			self.checkbox_clicked_chkbox_referral_habits)

	def button_clicked_btnOK( self, event):
		pass

		print "button_clicked_btnOK received ", event
			

	def button_clicked_btnClear( self, event):
		pass

		print "button_clicked_btnClear received ", event
			

	def button_clicked_btnpreview( self, event):
		pass

		print "button_clicked_btnpreview received ", event
			

	def text_entered_txt_referralcategory( self, event):
		pass

		print "text_entered_txt_referralcategory received ", event
			

	def text_entered_txt_referralname( self, event):
		pass

		print "text_entered_txt_referralname received ", event
			

	def text_entered_txt_referralorganisation( self, event):
		pass

		print "text_entered_txt_referralorganisation received ", event
			

	def text_entered_txt_referralstreet1( self, event):
		pass

		print "text_entered_txt_referralstreet1 received ", event
			

	def text_entered_txt_referralstreet2( self, event):
		pass

		print "text_entered_txt_referralstreet2 received ", event
			

	def text_entered_txt_referralstreet3( self, event):
		pass

		print "text_entered_txt_referralstreet3 received ", event
			

	def text_entered_txt_referralsuburb( self, event):
		pass

		print "text_entered_txt_referralsuburb received ", event
			

	def text_entered_txt_referralpostcode( self, event):
		pass

		print "text_entered_txt_referralpostcode received ", event
			

	def text_entered_txt_referralfor( self, event):
		pass

		print "text_entered_txt_referralfor received ", event
			

	def text_entered_txt_referralwphone( self, event):
		pass

		print "text_entered_txt_referralwphone received ", event
			

	def text_entered_txt_referralwfax( self, event):
		pass

		print "text_entered_txt_referralwfax received ", event
			

	def text_entered_txt_referralwemail( self, event):
		pass

		print "text_entered_txt_referralwemail received ", event
			

	def text_entered_txt_referralcopyto( self, event):
		pass

		print "text_entered_txt_referralcopyto received ", event
			

	def text_entered_txt_referralprogressnotes( self, event):
		pass

		print "text_entered_txt_referralprogressnotes received ", event
			

	def checkbox_clicked_chkbox_referral_usefirstname( self, event):
		pass

		print "checkbox_clicked_chkbox_referral_usefirstname received ", event
			

	def checkbox_clicked_chkbox_referral_headoffice( self, event):
		pass

		print "checkbox_clicked_chkbox_referral_headoffice received ", event
			

	def checkbox_clicked_chkbox_referral_medications( self, event):
		pass

		print "checkbox_clicked_chkbox_referral_medications received ", event
			

	def checkbox_clicked_chkbox_referral_socialhistory( self, event):
		pass

		print "checkbox_clicked_chkbox_referral_socialhistory received ", event
			

	def checkbox_clicked_chkbox_referral_familyhistory( self, event):
		pass

		print "checkbox_clicked_chkbox_referral_familyhistory received ", event
			

	def checkbox_clicked_chkbox_referral_pastproblems( self, event):
		pass

		print "checkbox_clicked_chkbox_referral_pastproblems received ", event
			

	def checkbox_clicked_chkbox_referral_activeproblems( self, event):
		pass

		print "checkbox_clicked_chkbox_referral_activeproblems received ", event
			

	def checkbox_clicked_chkbox_referral_habits( self, event):
		pass

		print "checkbox_clicked_chkbox_referral_habits received ", event
			


class gmSECTION_RECALLS_handler:

	def create_handler(self, panel):
		return gmSECTION_RECALLS_handler(panel)

	def __init__(self, panel):
		self.panel = panel
		if panel <> None:
			self.__set_id()
			self.__set_evt()

	def __set_id(self):
		self.id_map = {}


		id = wxNewId()
		self.panel.btnOK.SetId(id)
		self.id_map['btnOK'] = id
		

		id = wxNewId()
		self.panel.btnClear.SetId(id)
		self.id_map['btnClear'] = id
		

		id = wxNewId()
		self.panel.combo_tosee.SetId(id)
		self.id_map['combo_tosee'] = id
		

		id = wxNewId()
		self.panel.combo_recall_method.SetId(id)
		self.id_map['combo_recall_method'] = id
		

		id = wxNewId()
		self.panel.combo_apptlength.SetId(id)
		self.id_map['combo_apptlength'] = id
		

		id = wxNewId()
		self.panel.txt_recall_for.SetId(id)
		self.id_map['txt_recall_for'] = id
		

		id = wxNewId()
		self.panel.txt_recall_due.SetId(id)
		self.id_map['txt_recall_due'] = id
		

		id = wxNewId()
		self.panel.txt_recall_addtext.SetId(id)
		self.id_map['txt_recall_addtext'] = id
		

		id = wxNewId()
		self.panel.txt_recall_include.SetId(id)
		self.id_map['txt_recall_include'] = id
		

		id = wxNewId()
		self.panel.txt_recall_progressnotes.SetId(id)
		self.id_map['txt_recall_progressnotes'] = id
		

	def __set_evt(self):
		pass
		

		EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.button_clicked_btnOK)

		EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.button_clicked_btnClear)

		EVT_TEXT(self.panel.combo_tosee,\
			self.id_map['combo_tosee'],\
			self.text_entered_combo_tosee)

		EVT_TEXT(self.panel.combo_recall_method,\
			self.id_map['combo_recall_method'],\
			self.text_entered_combo_recall_method)

		EVT_TEXT(self.panel.combo_apptlength,\
			self.id_map['combo_apptlength'],\
			self.text_entered_combo_apptlength)

		EVT_TEXT(self.panel.txt_recall_for,\
			self.id_map['txt_recall_for'],\
			self.text_entered_txt_recall_for)

		EVT_TEXT(self.panel.txt_recall_due,\
			self.id_map['txt_recall_due'],\
			self.text_entered_txt_recall_due)

		EVT_TEXT(self.panel.txt_recall_addtext,\
			self.id_map['txt_recall_addtext'],\
			self.text_entered_txt_recall_addtext)

		EVT_TEXT(self.panel.txt_recall_include,\
			self.id_map['txt_recall_include'],\
			self.text_entered_txt_recall_include)

		EVT_TEXT(self.panel.txt_recall_progressnotes,\
			self.id_map['txt_recall_progressnotes'],\
			self.text_entered_txt_recall_progressnotes)

	def button_clicked_btnOK( self, event):
		pass

		print "button_clicked_btnOK received ", event
			

	def button_clicked_btnClear( self, event):
		pass

		print "button_clicked_btnClear received ", event
			

	def text_entered_combo_tosee( self, event):
		pass

		print "text_entered_combo_tosee received ", event
			

	def text_entered_combo_recall_method( self, event):
		pass

		print "text_entered_combo_recall_method received ", event
			

	def text_entered_combo_apptlength( self, event):
		pass

		print "text_entered_combo_apptlength received ", event
			

	def text_entered_txt_recall_for( self, event):
		pass

		print "text_entered_txt_recall_for received ", event
			

	def text_entered_txt_recall_due( self, event):
		pass

		print "text_entered_txt_recall_due received ", event
			

	def text_entered_txt_recall_addtext( self, event):
		pass

		print "text_entered_txt_recall_addtext received ", event
			

	def text_entered_txt_recall_include( self, event):
		pass

		print "text_entered_txt_recall_include received ", event
			

	def text_entered_txt_recall_progressnotes( self, event):
		pass

		print "text_entered_txt_recall_progressnotes received ", event
			
section_num_map =  {1: 'gmSECTION_SUMMARY', 2: 'gmSECTION_DEMOGRAPHICS', 3: 'gmSECTION_CLINICALNOTES', 4: 'gmSECTION_FAMILYHISTORY', 5: 'gmSECTION_PASTHISTORY', 6: 'gmSECTION_VACCINATION', 7: 'gmSECTION_ALLERGIES', 8: 'gmSECTION_SCRIPT', 9: 'gmSECTION_REQUESTS', 10: 'gmSECTION_MEASUREMENTS', 11: 'gmSECTION_REFERRALS', 12: 'gmSECTION_RECALLS'}

import gmGuiBroker
gb = gmGuiBroker.GuiBroker()
for k,v in section_num_map.items():
	exec("prototype = %s_handler(None)" % v)
	gb[v] = prototype

