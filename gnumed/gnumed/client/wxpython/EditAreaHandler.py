# scanning for section headers,
	#	then for components in file  gmEditArea.py 
	#	and generating a script template for attaching
	#	a listener to the components.  

from wxPython.wx import * 
# type_search_str =  class\s+(?P<new_type>\w+)\s*\(.*(?P<base_type>EditAreaTextBox|wxTextCtrl|wxComboBox|wxButton|wxRadioButton|wxCheckBox|wxListBox)
# found new type = EditAreaTextBox which is base_type wxTextCtrl



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


		id = self.panel.btnOK.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btnOK.SetId(id)
		self.id_map['btnOK'] = id
		

		id = self.panel.btnClear.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btnClear.SetId(id)
		self.id_map['btnClear'] = id
		

	def __set_evt(self):
		pass
		

		EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.btnOK_button_clicked)

		EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.btnClear_button_clicked)

	def btnOK_button_clicked( self, event):
		pass

		print "btnOK_button_clicked received ", event
			

	def btnClear_button_clicked( self, event):
		pass

		print "btnClear_button_clicked received ", event
			


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


		id = self.panel.btnOK.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btnOK.SetId(id)
		self.id_map['btnOK'] = id
		

		id = self.panel.btnClear.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btnClear.SetId(id)
		self.id_map['btnClear'] = id
		

	def __set_evt(self):
		pass
		

		EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.btnOK_button_clicked)

		EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.btnClear_button_clicked)

	def btnOK_button_clicked( self, event):
		pass

		print "btnOK_button_clicked received ", event
			

	def btnClear_button_clicked( self, event):
		pass

		print "btnClear_button_clicked received ", event
			


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


		id = self.panel.btnOK.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btnOK.SetId(id)
		self.id_map['btnOK'] = id
		

		id = self.panel.btnClear.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btnClear.SetId(id)
		self.id_map['btnClear'] = id
		

	def __set_evt(self):
		pass
		

		EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.btnOK_button_clicked)

		EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.btnClear_button_clicked)

	def btnOK_button_clicked( self, event):
		pass

		print "btnOK_button_clicked received ", event
			

	def btnClear_button_clicked( self, event):
		pass

		print "btnClear_button_clicked received ", event
			


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


		id = self.panel.btnOK.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btnOK.SetId(id)
		self.id_map['btnOK'] = id
		

		id = self.panel.btnClear.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btnClear.SetId(id)
		self.id_map['btnClear'] = id
		

		id = self.panel.txt_familymembername.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_familymembername.SetId(id)
		self.id_map['txt_familymembername'] = id
		

		id = self.panel.txt_familymemberrelationship.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_familymemberrelationship.SetId(id)
		self.id_map['txt_familymemberrelationship'] = id
		

		id = self.panel.txt_familymembercondition.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_familymembercondition.SetId(id)
		self.id_map['txt_familymembercondition'] = id
		

		id = self.panel.txt_familymemberconditioncomment.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_familymemberconditioncomment.SetId(id)
		self.id_map['txt_familymemberconditioncomment'] = id
		

		id = self.panel.txt_familymemberage_onset.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_familymemberage_onset.SetId(id)
		self.id_map['txt_familymemberage_onset'] = id
		

		id = self.panel.txt_familymembercaused_death.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_familymembercaused_death.SetId(id)
		self.id_map['txt_familymembercaused_death'] = id
		

		id = self.panel.txt_familymemberage_death.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_familymemberage_death.SetId(id)
		self.id_map['txt_familymemberage_death'] = id
		

		id = self.panel.txt_familymemberprogressnotes.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_familymemberprogressnotes.SetId(id)
		self.id_map['txt_familymemberprogressnotes'] = id
		

		id = self.panel.txt_familymemberdate_of_birth.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_familymemberdate_of_birth.SetId(id)
		self.id_map['txt_familymemberdate_of_birth'] = id
		

		id = self.panel.rb_familymember_conditionconfidential.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.rb_familymember_conditionconfidential.SetId(id)
		self.id_map['rb_familymember_conditionconfidential'] = id
		

		id = self.panel.btn_familymembernextcondition.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btn_familymembernextcondition.SetId(id)
		self.id_map['btn_familymembernextcondition'] = id
		

	def __set_evt(self):
		pass
		

		EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.btnOK_button_clicked)

		EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.btnClear_button_clicked)

		EVT_TEXT(self.panel.txt_familymembername,\
			self.id_map['txt_familymembername'],\
			self.txt_familymembername_text_entered)

		EVT_TEXT(self.panel.txt_familymemberrelationship,\
			self.id_map['txt_familymemberrelationship'],\
			self.txt_familymemberrelationship_text_entered)

		EVT_TEXT(self.panel.txt_familymembercondition,\
			self.id_map['txt_familymembercondition'],\
			self.txt_familymembercondition_text_entered)

		EVT_TEXT(self.panel.txt_familymemberconditioncomment,\
			self.id_map['txt_familymemberconditioncomment'],\
			self.txt_familymemberconditioncomment_text_entered)

		EVT_TEXT(self.panel.txt_familymemberage_onset,\
			self.id_map['txt_familymemberage_onset'],\
			self.txt_familymemberage_onset_text_entered)

		EVT_TEXT(self.panel.txt_familymembercaused_death,\
			self.id_map['txt_familymembercaused_death'],\
			self.txt_familymembercaused_death_text_entered)

		EVT_TEXT(self.panel.txt_familymemberage_death,\
			self.id_map['txt_familymemberage_death'],\
			self.txt_familymemberage_death_text_entered)

		EVT_TEXT(self.panel.txt_familymemberprogressnotes,\
			self.id_map['txt_familymemberprogressnotes'],\
			self.txt_familymemberprogressnotes_text_entered)

		EVT_TEXT(self.panel.txt_familymemberdate_of_birth,\
			self.id_map['txt_familymemberdate_of_birth'],\
			self.txt_familymemberdate_of_birth_text_entered)

		EVT_RADIOBUTTON(self.panel.rb_familymember_conditionconfidential,\
			self.id_map['rb_familymember_conditionconfidential'],\
			self.rb_familymember_conditionconfidential_radiobutton_clicked)

		EVT_BUTTON(self.panel.btn_familymembernextcondition,\
			self.id_map['btn_familymembernextcondition'],\
			self.btn_familymembernextcondition_button_clicked)

	def btnOK_button_clicked( self, event):
		pass

		print "btnOK_button_clicked received ", event
			

	def btnClear_button_clicked( self, event):
		pass

		print "btnClear_button_clicked received ", event
			

	def txt_familymembername_text_entered( self, event):
		pass

		print "txt_familymembername_text_entered received ", event
			

	def txt_familymemberrelationship_text_entered( self, event):
		pass

		print "txt_familymemberrelationship_text_entered received ", event
			

	def txt_familymembercondition_text_entered( self, event):
		pass

		print "txt_familymembercondition_text_entered received ", event
			

	def txt_familymemberconditioncomment_text_entered( self, event):
		pass

		print "txt_familymemberconditioncomment_text_entered received ", event
			

	def txt_familymemberage_onset_text_entered( self, event):
		pass

		print "txt_familymemberage_onset_text_entered received ", event
			

	def txt_familymembercaused_death_text_entered( self, event):
		pass

		print "txt_familymembercaused_death_text_entered received ", event
			

	def txt_familymemberage_death_text_entered( self, event):
		pass

		print "txt_familymemberage_death_text_entered received ", event
			

	def txt_familymemberprogressnotes_text_entered( self, event):
		pass

		print "txt_familymemberprogressnotes_text_entered received ", event
			

	def txt_familymemberdate_of_birth_text_entered( self, event):
		pass

		print "txt_familymemberdate_of_birth_text_entered received ", event
			

	def rb_familymember_conditionconfidential_radiobutton_clicked( self, event):
		pass

		print "rb_familymember_conditionconfidential_radiobutton_clicked received ", event
			

	def btn_familymembernextcondition_button_clicked( self, event):
		pass

		print "btn_familymembernextcondition_button_clicked received ", event
			


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


		id = self.panel.btnOK.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btnOK.SetId(id)
		self.id_map['btnOK'] = id
		

		id = self.panel.btnClear.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btnClear.SetId(id)
		self.id_map['btnClear'] = id
		

		id = self.panel.txt_condition.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_condition.SetId(id)
		self.id_map['txt_condition'] = id
		

		id = self.panel.rb_sideleft.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.rb_sideleft.SetId(id)
		self.id_map['rb_sideleft'] = id
		

		id = self.panel.rb_sideright.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.rb_sideright.SetId(id)
		self.id_map['rb_sideright'] = id
		

		id = self.panel.rb_sideboth.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.rb_sideboth.SetId(id)
		self.id_map['rb_sideboth'] = id
		

		id = self.panel.txt_notes1.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_notes1.SetId(id)
		self.id_map['txt_notes1'] = id
		

		id = self.panel.txt_notes2.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_notes2.SetId(id)
		self.id_map['txt_notes2'] = id
		

		id = self.panel.txt_agenoted.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_agenoted.SetId(id)
		self.id_map['txt_agenoted'] = id
		

		id = self.panel.txt_yearnoted.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_yearnoted.SetId(id)
		self.id_map['txt_yearnoted'] = id
		

		id = self.panel.cb_active.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.cb_active.SetId(id)
		self.id_map['cb_active'] = id
		

		id = self.panel.cb_operation.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.cb_operation.SetId(id)
		self.id_map['cb_operation'] = id
		

		id = self.panel.cb_confidential.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.cb_confidential.SetId(id)
		self.id_map['cb_confidential'] = id
		

		id = self.panel.cb_significant.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.cb_significant.SetId(id)
		self.id_map['cb_significant'] = id
		

		id = self.panel.txt_progressnotes.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_progressnotes.SetId(id)
		self.id_map['txt_progressnotes'] = id
		

	def __set_evt(self):
		pass
		

		EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.btnOK_button_clicked)

		EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.btnClear_button_clicked)

		EVT_TEXT(self.panel.txt_condition,\
			self.id_map['txt_condition'],\
			self.txt_condition_text_entered)

		EVT_RADIOBUTTON(self.panel.rb_sideleft,\
			self.id_map['rb_sideleft'],\
			self.rb_sideleft_radiobutton_clicked)

		EVT_RADIOBUTTON(self.panel.rb_sideright,\
			self.id_map['rb_sideright'],\
			self.rb_sideright_radiobutton_clicked)

		EVT_RADIOBUTTON(self.panel.rb_sideboth,\
			self.id_map['rb_sideboth'],\
			self.rb_sideboth_radiobutton_clicked)

		EVT_TEXT(self.panel.txt_notes1,\
			self.id_map['txt_notes1'],\
			self.txt_notes1_text_entered)

		EVT_TEXT(self.panel.txt_notes2,\
			self.id_map['txt_notes2'],\
			self.txt_notes2_text_entered)

		EVT_TEXT(self.panel.txt_agenoted,\
			self.id_map['txt_agenoted'],\
			self.txt_agenoted_text_entered)

		EVT_TEXT(self.panel.txt_yearnoted,\
			self.id_map['txt_yearnoted'],\
			self.txt_yearnoted_text_entered)

		EVT_CHECKBOX(self.panel.cb_active,\
			self.id_map['cb_active'],\
			self.cb_active_checkbox_clicked)

		EVT_CHECKBOX(self.panel.cb_operation,\
			self.id_map['cb_operation'],\
			self.cb_operation_checkbox_clicked)

		EVT_CHECKBOX(self.panel.cb_confidential,\
			self.id_map['cb_confidential'],\
			self.cb_confidential_checkbox_clicked)

		EVT_CHECKBOX(self.panel.cb_significant,\
			self.id_map['cb_significant'],\
			self.cb_significant_checkbox_clicked)

		EVT_TEXT(self.panel.txt_progressnotes,\
			self.id_map['txt_progressnotes'],\
			self.txt_progressnotes_text_entered)

	def btnOK_button_clicked( self, event):
		pass

		print "btnOK_button_clicked received ", event
			

	def btnClear_button_clicked( self, event):
		pass

		print "btnClear_button_clicked received ", event
			

	def txt_condition_text_entered( self, event):
		pass

		print "txt_condition_text_entered received ", event
			

	def rb_sideleft_radiobutton_clicked( self, event):
		pass

		print "rb_sideleft_radiobutton_clicked received ", event
			

	def rb_sideright_radiobutton_clicked( self, event):
		pass

		print "rb_sideright_radiobutton_clicked received ", event
			

	def rb_sideboth_radiobutton_clicked( self, event):
		pass

		print "rb_sideboth_radiobutton_clicked received ", event
			

	def txt_notes1_text_entered( self, event):
		pass

		print "txt_notes1_text_entered received ", event
			

	def txt_notes2_text_entered( self, event):
		pass

		print "txt_notes2_text_entered received ", event
			

	def txt_agenoted_text_entered( self, event):
		pass

		print "txt_agenoted_text_entered received ", event
			

	def txt_yearnoted_text_entered( self, event):
		pass

		print "txt_yearnoted_text_entered received ", event
			

	def cb_active_checkbox_clicked( self, event):
		pass

		print "cb_active_checkbox_clicked received ", event
			

	def cb_operation_checkbox_clicked( self, event):
		pass

		print "cb_operation_checkbox_clicked received ", event
			

	def cb_confidential_checkbox_clicked( self, event):
		pass

		print "cb_confidential_checkbox_clicked received ", event
			

	def cb_significant_checkbox_clicked( self, event):
		pass

		print "cb_significant_checkbox_clicked received ", event
			

	def txt_progressnotes_text_entered( self, event):
		pass

		print "txt_progressnotes_text_entered received ", event
			


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


		id = self.panel.btnOK.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btnOK.SetId(id)
		self.id_map['btnOK'] = id
		

		id = self.panel.btnClear.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btnClear.SetId(id)
		self.id_map['btnClear'] = id
		

		id = self.panel.txt_targetdisease.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_targetdisease.SetId(id)
		self.id_map['txt_targetdisease'] = id
		

		id = self.panel.txt_vaccine.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_vaccine.SetId(id)
		self.id_map['txt_vaccine'] = id
		

		id = self.panel.txt_dategiven.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_dategiven.SetId(id)
		self.id_map['txt_dategiven'] = id
		

		id = self.panel.txt_serialno.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_serialno.SetId(id)
		self.id_map['txt_serialno'] = id
		

		id = self.panel.txt_sitegiven.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_sitegiven.SetId(id)
		self.id_map['txt_sitegiven'] = id
		

		id = self.panel.txt_progressnotes.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_progressnotes.SetId(id)
		self.id_map['txt_progressnotes'] = id
		

	def __set_evt(self):
		pass
		

		EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.btnOK_button_clicked)

		EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.btnClear_button_clicked)

		EVT_TEXT(self.panel.txt_targetdisease,\
			self.id_map['txt_targetdisease'],\
			self.txt_targetdisease_text_entered)

		EVT_TEXT(self.panel.txt_vaccine,\
			self.id_map['txt_vaccine'],\
			self.txt_vaccine_text_entered)

		EVT_TEXT(self.panel.txt_dategiven,\
			self.id_map['txt_dategiven'],\
			self.txt_dategiven_text_entered)

		EVT_TEXT(self.panel.txt_serialno,\
			self.id_map['txt_serialno'],\
			self.txt_serialno_text_entered)

		EVT_TEXT(self.panel.txt_sitegiven,\
			self.id_map['txt_sitegiven'],\
			self.txt_sitegiven_text_entered)

		EVT_TEXT(self.panel.txt_progressnotes,\
			self.id_map['txt_progressnotes'],\
			self.txt_progressnotes_text_entered)

	def btnOK_button_clicked( self, event):
		pass

		print "btnOK_button_clicked received ", event
			

	def btnClear_button_clicked( self, event):
		pass

		print "btnClear_button_clicked received ", event
			

	def txt_targetdisease_text_entered( self, event):
		pass

		print "txt_targetdisease_text_entered received ", event
			

	def txt_vaccine_text_entered( self, event):
		pass

		print "txt_vaccine_text_entered received ", event
			

	def txt_dategiven_text_entered( self, event):
		pass

		print "txt_dategiven_text_entered received ", event
			

	def txt_serialno_text_entered( self, event):
		pass

		print "txt_serialno_text_entered received ", event
			

	def txt_sitegiven_text_entered( self, event):
		pass

		print "txt_sitegiven_text_entered received ", event
			

	def txt_progressnotes_text_entered( self, event):
		pass

		print "txt_progressnotes_text_entered received ", event
			


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


		id = self.panel.btnOK.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btnOK.SetId(id)
		self.id_map['btnOK'] = id
		

		id = self.panel.btnClear.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btnClear.SetId(id)
		self.id_map['btnClear'] = id
		

		id = self.panel.text1.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.text1.SetId(id)
		self.id_map['text1'] = id
		

		id = self.panel.text2.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.text2.SetId(id)
		self.id_map['text2'] = id
		

		id = self.panel.text3.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.text3.SetId(id)
		self.id_map['text3'] = id
		

		id = self.panel.text4.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.text4.SetId(id)
		self.id_map['text4'] = id
		

		id = self.panel.text5.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.text5.SetId(id)
		self.id_map['text5'] = id
		

		id = self.panel.cb1.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.cb1.SetId(id)
		self.id_map['cb1'] = id
		

		id = self.panel.rb1.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.rb1.SetId(id)
		self.id_map['rb1'] = id
		

		id = self.panel.rb2.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.rb2.SetId(id)
		self.id_map['rb2'] = id
		

		id = self.panel.cb2.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.cb2.SetId(id)
		self.id_map['cb2'] = id
		

	def __set_evt(self):
		pass
		

		EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.btnOK_button_clicked)

		EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.btnClear_button_clicked)

		EVT_TEXT(self.panel.text1,\
			self.id_map['text1'],\
			self.text1_text_entered)

		EVT_TEXT(self.panel.text2,\
			self.id_map['text2'],\
			self.text2_text_entered)

		EVT_TEXT(self.panel.text3,\
			self.id_map['text3'],\
			self.text3_text_entered)

		EVT_TEXT(self.panel.text4,\
			self.id_map['text4'],\
			self.text4_text_entered)

		EVT_TEXT(self.panel.text5,\
			self.id_map['text5'],\
			self.text5_text_entered)

		EVT_CHECKBOX(self.panel.cb1,\
			self.id_map['cb1'],\
			self.cb1_checkbox_clicked)

		EVT_RADIOBUTTON(self.panel.rb1,\
			self.id_map['rb1'],\
			self.rb1_radiobutton_clicked)

		EVT_RADIOBUTTON(self.panel.rb2,\
			self.id_map['rb2'],\
			self.rb2_radiobutton_clicked)

		EVT_CHECKBOX(self.panel.cb2,\
			self.id_map['cb2'],\
			self.cb2_checkbox_clicked)

	def btnOK_button_clicked( self, event):
		pass

		print "btnOK_button_clicked received ", event
			

	def btnClear_button_clicked( self, event):
		pass

		print "btnClear_button_clicked received ", event
			

	def text1_text_entered( self, event):
		pass

		print "text1_text_entered received ", event
			

	def text2_text_entered( self, event):
		pass

		print "text2_text_entered received ", event
			

	def text3_text_entered( self, event):
		pass

		print "text3_text_entered received ", event
			

	def text4_text_entered( self, event):
		pass

		print "text4_text_entered received ", event
			

	def text5_text_entered( self, event):
		pass

		print "text5_text_entered received ", event
			

	def cb1_checkbox_clicked( self, event):
		pass

		print "cb1_checkbox_clicked received ", event
			

	def rb1_radiobutton_clicked( self, event):
		pass

		print "rb1_radiobutton_clicked received ", event
			

	def rb2_radiobutton_clicked( self, event):
		pass

		print "rb2_radiobutton_clicked received ", event
			

	def cb2_checkbox_clicked( self, event):
		pass

		print "cb2_checkbox_clicked received ", event
			


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


		id = self.panel.btnOK.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btnOK.SetId(id)
		self.id_map['btnOK'] = id
		

		id = self.panel.btnClear.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btnClear.SetId(id)
		self.id_map['btnClear'] = id
		

		id = self.panel.text1.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.text1.SetId(id)
		self.id_map['text1'] = id
		

		id = self.panel.text2.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.text2.SetId(id)
		self.id_map['text2'] = id
		

		id = self.panel.text3.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.text3.SetId(id)
		self.id_map['text3'] = id
		

		id = self.panel.text4.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.text4.SetId(id)
		self.id_map['text4'] = id
		

		id = self.panel.text5.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.text5.SetId(id)
		self.id_map['text5'] = id
		

		id = self.panel.text6.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.text6.SetId(id)
		self.id_map['text6'] = id
		

		id = self.panel.text7.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.text7.SetId(id)
		self.id_map['text7'] = id
		

		id = self.panel.text8.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.text8.SetId(id)
		self.id_map['text8'] = id
		

		id = self.panel.text9.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.text9.SetId(id)
		self.id_map['text9'] = id
		

		id = self.panel.cb_veteran.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.cb_veteran.SetId(id)
		self.id_map['cb_veteran'] = id
		

		id = self.panel.cb_reg24.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.cb_reg24.SetId(id)
		self.id_map['cb_reg24'] = id
		

		id = self.panel.cb_usualmed.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.cb_usualmed.SetId(id)
		self.id_map['cb_usualmed'] = id
		

		id = self.panel.btn_authority.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btn_authority.SetId(id)
		self.id_map['btn_authority'] = id
		

		id = self.panel.btn_briefPI.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btn_briefPI.SetId(id)
		self.id_map['btn_briefPI'] = id
		

		id = self.panel.text10.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.text10.SetId(id)
		self.id_map['text10'] = id
		

	def __set_evt(self):
		pass
		

		EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.btnOK_button_clicked)

		EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.btnClear_button_clicked)

		EVT_TEXT(self.panel.text1,\
			self.id_map['text1'],\
			self.text1_text_entered)

		EVT_TEXT(self.panel.text2,\
			self.id_map['text2'],\
			self.text2_text_entered)

		EVT_TEXT(self.panel.text3,\
			self.id_map['text3'],\
			self.text3_text_entered)

		EVT_TEXT(self.panel.text4,\
			self.id_map['text4'],\
			self.text4_text_entered)

		EVT_TEXT(self.panel.text5,\
			self.id_map['text5'],\
			self.text5_text_entered)

		EVT_TEXT(self.panel.text6,\
			self.id_map['text6'],\
			self.text6_text_entered)

		EVT_TEXT(self.panel.text7,\
			self.id_map['text7'],\
			self.text7_text_entered)

		EVT_TEXT(self.panel.text8,\
			self.id_map['text8'],\
			self.text8_text_entered)

		EVT_TEXT(self.panel.text9,\
			self.id_map['text9'],\
			self.text9_text_entered)

		EVT_CHECKBOX(self.panel.cb_veteran,\
			self.id_map['cb_veteran'],\
			self.cb_veteran_checkbox_clicked)

		EVT_CHECKBOX(self.panel.cb_reg24,\
			self.id_map['cb_reg24'],\
			self.cb_reg24_checkbox_clicked)

		EVT_CHECKBOX(self.panel.cb_usualmed,\
			self.id_map['cb_usualmed'],\
			self.cb_usualmed_checkbox_clicked)

		EVT_BUTTON(self.panel.btn_authority,\
			self.id_map['btn_authority'],\
			self.btn_authority_button_clicked)

		EVT_BUTTON(self.panel.btn_briefPI,\
			self.id_map['btn_briefPI'],\
			self.btn_briefPI_button_clicked)

		EVT_TEXT(self.panel.text10,\
			self.id_map['text10'],\
			self.text10_text_entered)

	def btnOK_button_clicked( self, event):
		pass

		print "btnOK_button_clicked received ", event
			

	def btnClear_button_clicked( self, event):
		pass

		print "btnClear_button_clicked received ", event
			

	def text1_text_entered( self, event):
		pass

		print "text1_text_entered received ", event
			

	def text2_text_entered( self, event):
		pass

		print "text2_text_entered received ", event
			

	def text3_text_entered( self, event):
		pass

		print "text3_text_entered received ", event
			

	def text4_text_entered( self, event):
		pass

		print "text4_text_entered received ", event
			

	def text5_text_entered( self, event):
		pass

		print "text5_text_entered received ", event
			

	def text6_text_entered( self, event):
		pass

		print "text6_text_entered received ", event
			

	def text7_text_entered( self, event):
		pass

		print "text7_text_entered received ", event
			

	def text8_text_entered( self, event):
		pass

		print "text8_text_entered received ", event
			

	def text9_text_entered( self, event):
		pass

		print "text9_text_entered received ", event
			

	def cb_veteran_checkbox_clicked( self, event):
		pass

		print "cb_veteran_checkbox_clicked received ", event
			

	def cb_reg24_checkbox_clicked( self, event):
		pass

		print "cb_reg24_checkbox_clicked received ", event
			

	def cb_usualmed_checkbox_clicked( self, event):
		pass

		print "cb_usualmed_checkbox_clicked received ", event
			

	def btn_authority_button_clicked( self, event):
		pass

		print "btn_authority_button_clicked received ", event
			

	def btn_briefPI_button_clicked( self, event):
		pass

		print "btn_briefPI_button_clicked received ", event
			

	def text10_text_entered( self, event):
		pass

		print "text10_text_entered received ", event
			


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


		id = self.panel.btnOK.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btnOK.SetId(id)
		self.id_map['btnOK'] = id
		

		id = self.panel.btnClear.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btnClear.SetId(id)
		self.id_map['btnClear'] = id
		

		id = self.panel.txt_request_type.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_request_type.SetId(id)
		self.id_map['txt_request_type'] = id
		

		id = self.panel.txt_request_company.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_request_company.SetId(id)
		self.id_map['txt_request_company'] = id
		

		id = self.panel.txt_request_street.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_request_street.SetId(id)
		self.id_map['txt_request_street'] = id
		

		id = self.panel.txt_request_suburb.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_request_suburb.SetId(id)
		self.id_map['txt_request_suburb'] = id
		

		id = self.panel.txt_request_phone.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_request_phone.SetId(id)
		self.id_map['txt_request_phone'] = id
		

		id = self.panel.txt_request_requests.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_request_requests.SetId(id)
		self.id_map['txt_request_requests'] = id
		

		id = self.panel.txt_request_notes.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_request_notes.SetId(id)
		self.id_map['txt_request_notes'] = id
		

		id = self.panel.txt_request_medications.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_request_medications.SetId(id)
		self.id_map['txt_request_medications'] = id
		

		id = self.panel.txt_request_copyto.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_request_copyto.SetId(id)
		self.id_map['txt_request_copyto'] = id
		

		id = self.panel.txt_request_progressnotes.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_request_progressnotes.SetId(id)
		self.id_map['txt_request_progressnotes'] = id
		

		id = self.panel.cb_includeallmedications.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.cb_includeallmedications.SetId(id)
		self.id_map['cb_includeallmedications'] = id
		

		id = self.panel.rb_request_bill_bb.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.rb_request_bill_bb.SetId(id)
		self.id_map['rb_request_bill_bb'] = id
		

		id = self.panel.rb_request_bill_private.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.rb_request_bill_private.SetId(id)
		self.id_map['rb_request_bill_private'] = id
		

		id = self.panel.rb_request_bill_rebate.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.rb_request_bill_rebate.SetId(id)
		self.id_map['rb_request_bill_rebate'] = id
		

		id = self.panel.rb_request_bill_wcover.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.rb_request_bill_wcover.SetId(id)
		self.id_map['rb_request_bill_wcover'] = id
		

	def __set_evt(self):
		pass
		

		EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.btnOK_button_clicked)

		EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.btnClear_button_clicked)

		EVT_TEXT(self.panel.txt_request_type,\
			self.id_map['txt_request_type'],\
			self.txt_request_type_text_entered)

		EVT_TEXT(self.panel.txt_request_company,\
			self.id_map['txt_request_company'],\
			self.txt_request_company_text_entered)

		EVT_TEXT(self.panel.txt_request_street,\
			self.id_map['txt_request_street'],\
			self.txt_request_street_text_entered)

		EVT_TEXT(self.panel.txt_request_suburb,\
			self.id_map['txt_request_suburb'],\
			self.txt_request_suburb_text_entered)

		EVT_TEXT(self.panel.txt_request_phone,\
			self.id_map['txt_request_phone'],\
			self.txt_request_phone_text_entered)

		EVT_TEXT(self.panel.txt_request_requests,\
			self.id_map['txt_request_requests'],\
			self.txt_request_requests_text_entered)

		EVT_TEXT(self.panel.txt_request_notes,\
			self.id_map['txt_request_notes'],\
			self.txt_request_notes_text_entered)

		EVT_TEXT(self.panel.txt_request_medications,\
			self.id_map['txt_request_medications'],\
			self.txt_request_medications_text_entered)

		EVT_TEXT(self.panel.txt_request_copyto,\
			self.id_map['txt_request_copyto'],\
			self.txt_request_copyto_text_entered)

		EVT_TEXT(self.panel.txt_request_progressnotes,\
			self.id_map['txt_request_progressnotes'],\
			self.txt_request_progressnotes_text_entered)

		EVT_CHECKBOX(self.panel.cb_includeallmedications,\
			self.id_map['cb_includeallmedications'],\
			self.cb_includeallmedications_checkbox_clicked)

		EVT_RADIOBUTTON(self.panel.rb_request_bill_bb,\
			self.id_map['rb_request_bill_bb'],\
			self.rb_request_bill_bb_radiobutton_clicked)

		EVT_RADIOBUTTON(self.panel.rb_request_bill_private,\
			self.id_map['rb_request_bill_private'],\
			self.rb_request_bill_private_radiobutton_clicked)

		EVT_RADIOBUTTON(self.panel.rb_request_bill_rebate,\
			self.id_map['rb_request_bill_rebate'],\
			self.rb_request_bill_rebate_radiobutton_clicked)

		EVT_RADIOBUTTON(self.panel.rb_request_bill_wcover,\
			self.id_map['rb_request_bill_wcover'],\
			self.rb_request_bill_wcover_radiobutton_clicked)

	def btnOK_button_clicked( self, event):
		pass

		print "btnOK_button_clicked received ", event
			

	def btnClear_button_clicked( self, event):
		pass

		print "btnClear_button_clicked received ", event
			

	def txt_request_type_text_entered( self, event):
		pass

		print "txt_request_type_text_entered received ", event
			

	def txt_request_company_text_entered( self, event):
		pass

		print "txt_request_company_text_entered received ", event
			

	def txt_request_street_text_entered( self, event):
		pass

		print "txt_request_street_text_entered received ", event
			

	def txt_request_suburb_text_entered( self, event):
		pass

		print "txt_request_suburb_text_entered received ", event
			

	def txt_request_phone_text_entered( self, event):
		pass

		print "txt_request_phone_text_entered received ", event
			

	def txt_request_requests_text_entered( self, event):
		pass

		print "txt_request_requests_text_entered received ", event
			

	def txt_request_notes_text_entered( self, event):
		pass

		print "txt_request_notes_text_entered received ", event
			

	def txt_request_medications_text_entered( self, event):
		pass

		print "txt_request_medications_text_entered received ", event
			

	def txt_request_copyto_text_entered( self, event):
		pass

		print "txt_request_copyto_text_entered received ", event
			

	def txt_request_progressnotes_text_entered( self, event):
		pass

		print "txt_request_progressnotes_text_entered received ", event
			

	def cb_includeallmedications_checkbox_clicked( self, event):
		pass

		print "cb_includeallmedications_checkbox_clicked received ", event
			

	def rb_request_bill_bb_radiobutton_clicked( self, event):
		pass

		print "rb_request_bill_bb_radiobutton_clicked received ", event
			

	def rb_request_bill_private_radiobutton_clicked( self, event):
		pass

		print "rb_request_bill_private_radiobutton_clicked received ", event
			

	def rb_request_bill_rebate_radiobutton_clicked( self, event):
		pass

		print "rb_request_bill_rebate_radiobutton_clicked received ", event
			

	def rb_request_bill_wcover_radiobutton_clicked( self, event):
		pass

		print "rb_request_bill_wcover_radiobutton_clicked received ", event
			


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


		id = self.panel.btnOK.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btnOK.SetId(id)
		self.id_map['btnOK'] = id
		

		id = self.panel.btnClear.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btnClear.SetId(id)
		self.id_map['btnClear'] = id
		

		id = self.panel.combo_measurement_type.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.combo_measurement_type.SetId(id)
		self.id_map['combo_measurement_type'] = id
		

		id = self.panel.txt_measurement_value.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_measurement_value.SetId(id)
		self.id_map['txt_measurement_value'] = id
		

		id = self.panel.txt_txt_measurement_date.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_txt_measurement_date.SetId(id)
		self.id_map['txt_txt_measurement_date'] = id
		

		id = self.panel.txt_txt_measurement_comment.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_txt_measurement_comment.SetId(id)
		self.id_map['txt_txt_measurement_comment'] = id
		

		id = self.panel.txt_txt_measurement_progressnote.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_txt_measurement_progressnote.SetId(id)
		self.id_map['txt_txt_measurement_progressnote'] = id
		

		id = self.panel.btn_nextvalue.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btn_nextvalue.SetId(id)
		self.id_map['btn_nextvalue'] = id
		

		id = self.panel.btn_graph.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btn_graph.SetId(id)
		self.id_map['btn_graph'] = id
		

	def __set_evt(self):
		pass
		

		EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.btnOK_button_clicked)

		EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.btnClear_button_clicked)

		EVT_TEXT(self.panel.combo_measurement_type,\
			self.id_map['combo_measurement_type'],\
			self.combo_measurement_type_text_entered)

		EVT_TEXT(self.panel.txt_measurement_value,\
			self.id_map['txt_measurement_value'],\
			self.txt_measurement_value_text_entered)

		EVT_TEXT(self.panel.txt_txt_measurement_date,\
			self.id_map['txt_txt_measurement_date'],\
			self.txt_txt_measurement_date_text_entered)

		EVT_TEXT(self.panel.txt_txt_measurement_comment,\
			self.id_map['txt_txt_measurement_comment'],\
			self.txt_txt_measurement_comment_text_entered)

		EVT_TEXT(self.panel.txt_txt_measurement_progressnote,\
			self.id_map['txt_txt_measurement_progressnote'],\
			self.txt_txt_measurement_progressnote_text_entered)

		EVT_BUTTON(self.panel.btn_nextvalue,\
			self.id_map['btn_nextvalue'],\
			self.btn_nextvalue_button_clicked)

		EVT_BUTTON(self.panel.btn_graph,\
			self.id_map['btn_graph'],\
			self.btn_graph_button_clicked)

	def btnOK_button_clicked( self, event):
		pass

		print "btnOK_button_clicked received ", event
			

	def btnClear_button_clicked( self, event):
		pass

		print "btnClear_button_clicked received ", event
			

	def combo_measurement_type_text_entered( self, event):
		pass

		print "combo_measurement_type_text_entered received ", event
			

	def txt_measurement_value_text_entered( self, event):
		pass

		print "txt_measurement_value_text_entered received ", event
			

	def txt_txt_measurement_date_text_entered( self, event):
		pass

		print "txt_txt_measurement_date_text_entered received ", event
			

	def txt_txt_measurement_comment_text_entered( self, event):
		pass

		print "txt_txt_measurement_comment_text_entered received ", event
			

	def txt_txt_measurement_progressnote_text_entered( self, event):
		pass

		print "txt_txt_measurement_progressnote_text_entered received ", event
			

	def btn_nextvalue_button_clicked( self, event):
		pass

		print "btn_nextvalue_button_clicked received ", event
			

	def btn_graph_button_clicked( self, event):
		pass

		print "btn_graph_button_clicked received ", event
			


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


		id = self.panel.btnOK.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btnOK.SetId(id)
		self.id_map['btnOK'] = id
		

		id = self.panel.btnClear.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btnClear.SetId(id)
		self.id_map['btnClear'] = id
		

		id = self.panel.btnpreview.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btnpreview.SetId(id)
		self.id_map['btnpreview'] = id
		

		id = self.panel.txt_referralcategory.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_referralcategory.SetId(id)
		self.id_map['txt_referralcategory'] = id
		

		id = self.panel.txt_referralname.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_referralname.SetId(id)
		self.id_map['txt_referralname'] = id
		

		id = self.panel.txt_referralorganisation.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_referralorganisation.SetId(id)
		self.id_map['txt_referralorganisation'] = id
		

		id = self.panel.txt_referralstreet1.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_referralstreet1.SetId(id)
		self.id_map['txt_referralstreet1'] = id
		

		id = self.panel.txt_referralstreet2.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_referralstreet2.SetId(id)
		self.id_map['txt_referralstreet2'] = id
		

		id = self.panel.txt_referralstreet3.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_referralstreet3.SetId(id)
		self.id_map['txt_referralstreet3'] = id
		

		id = self.panel.txt_referralsuburb.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_referralsuburb.SetId(id)
		self.id_map['txt_referralsuburb'] = id
		

		id = self.panel.txt_referralpostcode.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_referralpostcode.SetId(id)
		self.id_map['txt_referralpostcode'] = id
		

		id = self.panel.txt_referralfor.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_referralfor.SetId(id)
		self.id_map['txt_referralfor'] = id
		

		id = self.panel.txt_referralwphone.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_referralwphone.SetId(id)
		self.id_map['txt_referralwphone'] = id
		

		id = self.panel.txt_referralwfax.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_referralwfax.SetId(id)
		self.id_map['txt_referralwfax'] = id
		

		id = self.panel.txt_referralwemail.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_referralwemail.SetId(id)
		self.id_map['txt_referralwemail'] = id
		

		id = self.panel.txt_referralcopyto.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_referralcopyto.SetId(id)
		self.id_map['txt_referralcopyto'] = id
		

		id = self.panel.txt_referralprogressnotes.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_referralprogressnotes.SetId(id)
		self.id_map['txt_referralprogressnotes'] = id
		

		id = self.panel.chkbox_referral_usefirstname.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.chkbox_referral_usefirstname.SetId(id)
		self.id_map['chkbox_referral_usefirstname'] = id
		

		id = self.panel.chkbox_referral_headoffice.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.chkbox_referral_headoffice.SetId(id)
		self.id_map['chkbox_referral_headoffice'] = id
		

		id = self.panel.chkbox_referral_medications.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.chkbox_referral_medications.SetId(id)
		self.id_map['chkbox_referral_medications'] = id
		

		id = self.panel.chkbox_referral_socialhistory.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.chkbox_referral_socialhistory.SetId(id)
		self.id_map['chkbox_referral_socialhistory'] = id
		

		id = self.panel.chkbox_referral_familyhistory.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.chkbox_referral_familyhistory.SetId(id)
		self.id_map['chkbox_referral_familyhistory'] = id
		

		id = self.panel.chkbox_referral_pastproblems.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.chkbox_referral_pastproblems.SetId(id)
		self.id_map['chkbox_referral_pastproblems'] = id
		

		id = self.panel.chkbox_referral_activeproblems.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.chkbox_referral_activeproblems.SetId(id)
		self.id_map['chkbox_referral_activeproblems'] = id
		

		id = self.panel.chkbox_referral_habits.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.chkbox_referral_habits.SetId(id)
		self.id_map['chkbox_referral_habits'] = id
		

	def __set_evt(self):
		pass
		

		EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.btnOK_button_clicked)

		EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.btnClear_button_clicked)

		EVT_BUTTON(self.panel.btnpreview,\
			self.id_map['btnpreview'],\
			self.btnpreview_button_clicked)

		EVT_TEXT(self.panel.txt_referralcategory,\
			self.id_map['txt_referralcategory'],\
			self.txt_referralcategory_text_entered)

		EVT_TEXT(self.panel.txt_referralname,\
			self.id_map['txt_referralname'],\
			self.txt_referralname_text_entered)

		EVT_TEXT(self.panel.txt_referralorganisation,\
			self.id_map['txt_referralorganisation'],\
			self.txt_referralorganisation_text_entered)

		EVT_TEXT(self.panel.txt_referralstreet1,\
			self.id_map['txt_referralstreet1'],\
			self.txt_referralstreet1_text_entered)

		EVT_TEXT(self.panel.txt_referralstreet2,\
			self.id_map['txt_referralstreet2'],\
			self.txt_referralstreet2_text_entered)

		EVT_TEXT(self.panel.txt_referralstreet3,\
			self.id_map['txt_referralstreet3'],\
			self.txt_referralstreet3_text_entered)

		EVT_TEXT(self.panel.txt_referralsuburb,\
			self.id_map['txt_referralsuburb'],\
			self.txt_referralsuburb_text_entered)

		EVT_TEXT(self.panel.txt_referralpostcode,\
			self.id_map['txt_referralpostcode'],\
			self.txt_referralpostcode_text_entered)

		EVT_TEXT(self.panel.txt_referralfor,\
			self.id_map['txt_referralfor'],\
			self.txt_referralfor_text_entered)

		EVT_TEXT(self.panel.txt_referralwphone,\
			self.id_map['txt_referralwphone'],\
			self.txt_referralwphone_text_entered)

		EVT_TEXT(self.panel.txt_referralwfax,\
			self.id_map['txt_referralwfax'],\
			self.txt_referralwfax_text_entered)

		EVT_TEXT(self.panel.txt_referralwemail,\
			self.id_map['txt_referralwemail'],\
			self.txt_referralwemail_text_entered)

		EVT_TEXT(self.panel.txt_referralcopyto,\
			self.id_map['txt_referralcopyto'],\
			self.txt_referralcopyto_text_entered)

		EVT_TEXT(self.panel.txt_referralprogressnotes,\
			self.id_map['txt_referralprogressnotes'],\
			self.txt_referralprogressnotes_text_entered)

		EVT_CHECKBOX(self.panel.chkbox_referral_usefirstname,\
			self.id_map['chkbox_referral_usefirstname'],\
			self.chkbox_referral_usefirstname_checkbox_clicked)

		EVT_CHECKBOX(self.panel.chkbox_referral_headoffice,\
			self.id_map['chkbox_referral_headoffice'],\
			self.chkbox_referral_headoffice_checkbox_clicked)

		EVT_CHECKBOX(self.panel.chkbox_referral_medications,\
			self.id_map['chkbox_referral_medications'],\
			self.chkbox_referral_medications_checkbox_clicked)

		EVT_CHECKBOX(self.panel.chkbox_referral_socialhistory,\
			self.id_map['chkbox_referral_socialhistory'],\
			self.chkbox_referral_socialhistory_checkbox_clicked)

		EVT_CHECKBOX(self.panel.chkbox_referral_familyhistory,\
			self.id_map['chkbox_referral_familyhistory'],\
			self.chkbox_referral_familyhistory_checkbox_clicked)

		EVT_CHECKBOX(self.panel.chkbox_referral_pastproblems,\
			self.id_map['chkbox_referral_pastproblems'],\
			self.chkbox_referral_pastproblems_checkbox_clicked)

		EVT_CHECKBOX(self.panel.chkbox_referral_activeproblems,\
			self.id_map['chkbox_referral_activeproblems'],\
			self.chkbox_referral_activeproblems_checkbox_clicked)

		EVT_CHECKBOX(self.panel.chkbox_referral_habits,\
			self.id_map['chkbox_referral_habits'],\
			self.chkbox_referral_habits_checkbox_clicked)

	def btnOK_button_clicked( self, event):
		pass

		print "btnOK_button_clicked received ", event
			

	def btnClear_button_clicked( self, event):
		pass

		print "btnClear_button_clicked received ", event
			

	def btnpreview_button_clicked( self, event):
		pass

		print "btnpreview_button_clicked received ", event
			

	def txt_referralcategory_text_entered( self, event):
		pass

		print "txt_referralcategory_text_entered received ", event
			

	def txt_referralname_text_entered( self, event):
		pass

		print "txt_referralname_text_entered received ", event
			

	def txt_referralorganisation_text_entered( self, event):
		pass

		print "txt_referralorganisation_text_entered received ", event
			

	def txt_referralstreet1_text_entered( self, event):
		pass

		print "txt_referralstreet1_text_entered received ", event
			

	def txt_referralstreet2_text_entered( self, event):
		pass

		print "txt_referralstreet2_text_entered received ", event
			

	def txt_referralstreet3_text_entered( self, event):
		pass

		print "txt_referralstreet3_text_entered received ", event
			

	def txt_referralsuburb_text_entered( self, event):
		pass

		print "txt_referralsuburb_text_entered received ", event
			

	def txt_referralpostcode_text_entered( self, event):
		pass

		print "txt_referralpostcode_text_entered received ", event
			

	def txt_referralfor_text_entered( self, event):
		pass

		print "txt_referralfor_text_entered received ", event
			

	def txt_referralwphone_text_entered( self, event):
		pass

		print "txt_referralwphone_text_entered received ", event
			

	def txt_referralwfax_text_entered( self, event):
		pass

		print "txt_referralwfax_text_entered received ", event
			

	def txt_referralwemail_text_entered( self, event):
		pass

		print "txt_referralwemail_text_entered received ", event
			

	def txt_referralcopyto_text_entered( self, event):
		pass

		print "txt_referralcopyto_text_entered received ", event
			

	def txt_referralprogressnotes_text_entered( self, event):
		pass

		print "txt_referralprogressnotes_text_entered received ", event
			

	def chkbox_referral_usefirstname_checkbox_clicked( self, event):
		pass

		print "chkbox_referral_usefirstname_checkbox_clicked received ", event
			

	def chkbox_referral_headoffice_checkbox_clicked( self, event):
		pass

		print "chkbox_referral_headoffice_checkbox_clicked received ", event
			

	def chkbox_referral_medications_checkbox_clicked( self, event):
		pass

		print "chkbox_referral_medications_checkbox_clicked received ", event
			

	def chkbox_referral_socialhistory_checkbox_clicked( self, event):
		pass

		print "chkbox_referral_socialhistory_checkbox_clicked received ", event
			

	def chkbox_referral_familyhistory_checkbox_clicked( self, event):
		pass

		print "chkbox_referral_familyhistory_checkbox_clicked received ", event
			

	def chkbox_referral_pastproblems_checkbox_clicked( self, event):
		pass

		print "chkbox_referral_pastproblems_checkbox_clicked received ", event
			

	def chkbox_referral_activeproblems_checkbox_clicked( self, event):
		pass

		print "chkbox_referral_activeproblems_checkbox_clicked received ", event
			

	def chkbox_referral_habits_checkbox_clicked( self, event):
		pass

		print "chkbox_referral_habits_checkbox_clicked received ", event
			


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


		id = self.panel.btnOK.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btnOK.SetId(id)
		self.id_map['btnOK'] = id
		

		id = self.panel.btnClear.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.btnClear.SetId(id)
		self.id_map['btnClear'] = id
		

		id = self.panel.combo_tosee.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.combo_tosee.SetId(id)
		self.id_map['combo_tosee'] = id
		

		id = self.panel.combo_recall_method.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.combo_recall_method.SetId(id)
		self.id_map['combo_recall_method'] = id
		

		id = self.panel.combo_apptlength.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.combo_apptlength.SetId(id)
		self.id_map['combo_apptlength'] = id
		

		id = self.panel.txt_recall_for.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_recall_for.SetId(id)
		self.id_map['txt_recall_for'] = id
		

		id = self.panel.txt_recall_due.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_recall_due.SetId(id)
		self.id_map['txt_recall_due'] = id
		

		id = self.panel.txt_recall_addtext.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_recall_addtext.SetId(id)
		self.id_map['txt_recall_addtext'] = id
		

		id = self.panel.txt_recall_include.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_recall_include.SetId(id)
		self.id_map['txt_recall_include'] = id
		

		id = self.panel.txt_recall_progressnotes.GetId()
		if id  <= 0:
			id = wxNewId()
			self.panel.txt_recall_progressnotes.SetId(id)
		self.id_map['txt_recall_progressnotes'] = id
		

	def __set_evt(self):
		pass
		

		EVT_BUTTON(self.panel.btnOK,\
			self.id_map['btnOK'],\
			self.btnOK_button_clicked)

		EVT_BUTTON(self.panel.btnClear,\
			self.id_map['btnClear'],\
			self.btnClear_button_clicked)

		EVT_TEXT(self.panel.combo_tosee,\
			self.id_map['combo_tosee'],\
			self.combo_tosee_text_entered)

		EVT_TEXT(self.panel.combo_recall_method,\
			self.id_map['combo_recall_method'],\
			self.combo_recall_method_text_entered)

		EVT_TEXT(self.panel.combo_apptlength,\
			self.id_map['combo_apptlength'],\
			self.combo_apptlength_text_entered)

		EVT_TEXT(self.panel.txt_recall_for,\
			self.id_map['txt_recall_for'],\
			self.txt_recall_for_text_entered)

		EVT_TEXT(self.panel.txt_recall_due,\
			self.id_map['txt_recall_due'],\
			self.txt_recall_due_text_entered)

		EVT_TEXT(self.panel.txt_recall_addtext,\
			self.id_map['txt_recall_addtext'],\
			self.txt_recall_addtext_text_entered)

		EVT_TEXT(self.panel.txt_recall_include,\
			self.id_map['txt_recall_include'],\
			self.txt_recall_include_text_entered)

		EVT_TEXT(self.panel.txt_recall_progressnotes,\
			self.id_map['txt_recall_progressnotes'],\
			self.txt_recall_progressnotes_text_entered)

	def btnOK_button_clicked( self, event):
		pass

		print "btnOK_button_clicked received ", event
			

	def btnClear_button_clicked( self, event):
		pass

		print "btnClear_button_clicked received ", event
			

	def combo_tosee_text_entered( self, event):
		pass

		print "combo_tosee_text_entered received ", event
			

	def combo_recall_method_text_entered( self, event):
		pass

		print "combo_recall_method_text_entered received ", event
			

	def combo_apptlength_text_entered( self, event):
		pass

		print "combo_apptlength_text_entered received ", event
			

	def txt_recall_for_text_entered( self, event):
		pass

		print "txt_recall_for_text_entered received ", event
			

	def txt_recall_due_text_entered( self, event):
		pass

		print "txt_recall_due_text_entered received ", event
			

	def txt_recall_addtext_text_entered( self, event):
		pass

		print "txt_recall_addtext_text_entered received ", event
			

	def txt_recall_include_text_entered( self, event):
		pass

		print "txt_recall_include_text_entered received ", event
			

	def txt_recall_progressnotes_text_entered( self, event):
		pass

		print "txt_recall_progressnotes_text_entered received ", event
			
section_num_map =  {1: 'gmSECTION_SUMMARY', 2: 'gmSECTION_DEMOGRAPHICS', 3: 'gmSECTION_CLINICALNOTES', 4: 'gmSECTION_FAMILYHISTORY', 5: 'gmSECTION_PASTHISTORY', 6: 'gmSECTION_VACCINATION', 7: 'gmSECTION_ALLERGIES', 8: 'gmSECTION_SCRIPT', 9: 'gmSECTION_REQUESTS', 10: 'gmSECTION_MEASUREMENTS', 11: 'gmSECTION_REFERRALS', 12: 'gmSECTION_RECALLS'}

import gmGuiBroker
gb = gmGuiBroker.GuiBroker()
for k,v in section_num_map.items():
	exec("prototype = %s_handler(None)" % v)
	gb[v] = prototype
	
