# 
# created with  python handler_generator.py -d patient >handler_patient.py                  



# ['gmBMICalc.py', 'gmCalcPreg.py', 'gmCrypto.py', 'gmDemographics.py', 'gmGP_Allergies.py', 'gmGP_AnteNatal_3.py', 'gmGP_ClinicalSummary.py', 'gmGP_FamilyHistory.py', 'gmGP_Immunisation.py', 'gmGP_Measurements.py', 'gmGP_PastHistory.py', 'gmGP_Prescriptions.py', 'gmGP_Recalls.py', 'gmGP_Referrals.py', 'gmGP_Requests.py', 'gmGP_ScratchPadRecalls.py', 'gmGP_TabbedLists.py']

from wxPython.wx import * 
#creating a handler as gmBMICalc_handler from patient/gmBMICalc.py
# [('txtHeight', 'wxTextCtrl')]


class gmBMICalc_handler:

	def create_handler(self, panel):
		return gmBMICalc_handler(panel)

	def __init__(self, panel):
		self.panel = panel
		if panel <> None:
			self.__set_id()
			self.__set_evt()

	def __set_id(self):
		self.id_map = {}


		id = wxNewId()
		self.panel.txtHeight.SetId(id)
		self.id_map['txtHeight'] = id
		

	def __set_evt(self):
		pass
		

		EVT_TEXT(self.panel.txtHeight,\
			self.id_map['txtHeight'],\
			self.txtHeight_text_entered)

	def txtHeight_text_entered( self, event):
		pass

		print "txtHeight_text_entered received ", event
			
#creating a handler as gmCalcPreg_handler from patient/gmCalcPreg.py
# []
#creating a handler as gmCrypto_handler from patient/gmCrypto.py
# []
#creating a handler as gmDemographics_handler from patient/gmDemographics.py
# [('addresslist', 'wxListBox'), ('combo_relationship', 'wxComboBox'), ('combo_title', 'wxComboBox'), ('combo_sex', 'wxComboBox'), ('cb_preferredname', 'wxCheckBox'), ('txt_address', 'wxTextCtrl'), ('combo_maritalstatus', 'wxComboBox'), ('btn_browseNOK', 'wxButton'), ('txt_nameNOK', 'wxTextCtrl'), ('cb_addressresidence', 'wxCheckBox'), ('cb_addresspostal', 'wxCheckBox'), ('btn_photo_import', 'wxButton'), ('btn_photo_export', 'wxButton'), ('btn_photo_aquire', 'wxButton'), ('txt_findpatient', 'wxComboBox'), ('txt_age', 'wxTextCtrl'), ('txt_allergies', 'wxTextCtrl'), ('combo_consultation_type', 'wxComboBox')]


class gmDemographics_handler:

	def create_handler(self, panel):
		return gmDemographics_handler(panel)

	def __init__(self, panel):
		self.panel = panel
		if panel <> None:
			self.__set_id()
			self.__set_evt()

	def __set_id(self):
		self.id_map = {}


		id = wxNewId()
		self.panel.addresslist.SetId(id)
		self.id_map['addresslist'] = id
		

		id = wxNewId()
		self.panel.combo_relationship.SetId(id)
		self.id_map['combo_relationship'] = id
		

		id = wxNewId()
		self.panel.combo_title.SetId(id)
		self.id_map['combo_title'] = id
		

		id = wxNewId()
		self.panel.combo_sex.SetId(id)
		self.id_map['combo_sex'] = id
		

		id = wxNewId()
		self.panel.cb_preferredname.SetId(id)
		self.id_map['cb_preferredname'] = id
		

		id = wxNewId()
		self.panel.txt_address.SetId(id)
		self.id_map['txt_address'] = id
		

		id = wxNewId()
		self.panel.combo_maritalstatus.SetId(id)
		self.id_map['combo_maritalstatus'] = id
		

		id = wxNewId()
		self.panel.btn_browseNOK.SetId(id)
		self.id_map['btn_browseNOK'] = id
		

		id = wxNewId()
		self.panel.txt_nameNOK.SetId(id)
		self.id_map['txt_nameNOK'] = id
		

		id = wxNewId()
		self.panel.cb_addressresidence.SetId(id)
		self.id_map['cb_addressresidence'] = id
		

		id = wxNewId()
		self.panel.cb_addresspostal.SetId(id)
		self.id_map['cb_addresspostal'] = id
		

		id = wxNewId()
		self.panel.btn_photo_import.SetId(id)
		self.id_map['btn_photo_import'] = id
		

		id = wxNewId()
		self.panel.btn_photo_export.SetId(id)
		self.id_map['btn_photo_export'] = id
		

		id = wxNewId()
		self.panel.btn_photo_aquire.SetId(id)
		self.id_map['btn_photo_aquire'] = id
		

		id = wxNewId()
		self.panel.txt_findpatient.SetId(id)
		self.id_map['txt_findpatient'] = id
		

		id = wxNewId()
		self.panel.txt_age.SetId(id)
		self.id_map['txt_age'] = id
		

		id = wxNewId()
		self.panel.txt_allergies.SetId(id)
		self.id_map['txt_allergies'] = id
		

		id = wxNewId()
		self.panel.combo_consultation_type.SetId(id)
		self.id_map['combo_consultation_type'] = id
		

	def __set_evt(self):
		pass
		

		EVT_LISTBOX(self.panel.addresslist,\
			self.id_map['addresslist'],\
			self.addresslist_list_box_single_clicked)

		EVT_LISTBOX_DCLICK(self.panel.addresslist,\
			self.id_map['addresslist'],\
			self.addresslist_list_box_double_clicked)

		EVT_TEXT(self.panel.combo_relationship,\
			self.id_map['combo_relationship'],\
			self.combo_relationship_text_entered)

		EVT_TEXT(self.panel.combo_title,\
			self.id_map['combo_title'],\
			self.combo_title_text_entered)

		EVT_TEXT(self.panel.combo_sex,\
			self.id_map['combo_sex'],\
			self.combo_sex_text_entered)

		EVT_CHECKBOX(self.panel.cb_preferredname,\
			self.id_map['cb_preferredname'],\
			self.cb_preferredname_checkbox_clicked)

		EVT_TEXT(self.panel.txt_address,\
			self.id_map['txt_address'],\
			self.txt_address_text_entered)

		EVT_TEXT(self.panel.combo_maritalstatus,\
			self.id_map['combo_maritalstatus'],\
			self.combo_maritalstatus_text_entered)

		EVT_BUTTON(self.panel.btn_browseNOK,\
			self.id_map['btn_browseNOK'],\
			self.btn_browseNOK_button_clicked)

		EVT_TEXT(self.panel.txt_nameNOK,\
			self.id_map['txt_nameNOK'],\
			self.txt_nameNOK_text_entered)

		EVT_CHECKBOX(self.panel.cb_addressresidence,\
			self.id_map['cb_addressresidence'],\
			self.cb_addressresidence_checkbox_clicked)

		EVT_CHECKBOX(self.panel.cb_addresspostal,\
			self.id_map['cb_addresspostal'],\
			self.cb_addresspostal_checkbox_clicked)

		EVT_BUTTON(self.panel.btn_photo_import,\
			self.id_map['btn_photo_import'],\
			self.btn_photo_import_button_clicked)

		EVT_BUTTON(self.panel.btn_photo_export,\
			self.id_map['btn_photo_export'],\
			self.btn_photo_export_button_clicked)

		EVT_BUTTON(self.panel.btn_photo_aquire,\
			self.id_map['btn_photo_aquire'],\
			self.btn_photo_aquire_button_clicked)

		EVT_TEXT(self.panel.txt_findpatient,\
			self.id_map['txt_findpatient'],\
			self.txt_findpatient_text_entered)

		EVT_TEXT(self.panel.txt_age,\
			self.id_map['txt_age'],\
			self.txt_age_text_entered)

		EVT_TEXT(self.panel.txt_allergies,\
			self.id_map['txt_allergies'],\
			self.txt_allergies_text_entered)

		EVT_TEXT(self.panel.combo_consultation_type,\
			self.id_map['combo_consultation_type'],\
			self.combo_consultation_type_text_entered)

	def addresslist_list_box_single_clicked( self, event):
		pass

		print "addresslist_list_box_single_clicked received ", event
			

	def addresslist_list_box_double_clicked( self, event):
		pass

		print "addresslist_list_box_double_clicked received ", event
			

	def combo_relationship_text_entered( self, event):
		pass

		print "combo_relationship_text_entered received ", event
			

	def combo_title_text_entered( self, event):
		pass

		print "combo_title_text_entered received ", event
			

	def combo_sex_text_entered( self, event):
		pass

		print "combo_sex_text_entered received ", event
			

	def cb_preferredname_checkbox_clicked( self, event):
		pass

		print "cb_preferredname_checkbox_clicked received ", event
			

	def txt_address_text_entered( self, event):
		pass

		print "txt_address_text_entered received ", event
			

	def combo_maritalstatus_text_entered( self, event):
		pass

		print "combo_maritalstatus_text_entered received ", event
			

	def btn_browseNOK_button_clicked( self, event):
		pass

		print "btn_browseNOK_button_clicked received ", event
			

	def txt_nameNOK_text_entered( self, event):
		pass

		print "txt_nameNOK_text_entered received ", event
			

	def cb_addressresidence_checkbox_clicked( self, event):
		pass

		print "cb_addressresidence_checkbox_clicked received ", event
			

	def cb_addresspostal_checkbox_clicked( self, event):
		pass

		print "cb_addresspostal_checkbox_clicked received ", event
			

	def btn_photo_import_button_clicked( self, event):
		pass

		print "btn_photo_import_button_clicked received ", event
			

	def btn_photo_export_button_clicked( self, event):
		pass

		print "btn_photo_export_button_clicked received ", event
			

	def btn_photo_aquire_button_clicked( self, event):
		pass

		print "btn_photo_aquire_button_clicked received ", event
			

	def txt_findpatient_text_entered( self, event):
		pass

		print "txt_findpatient_text_entered received ", event
			

	def txt_age_text_entered( self, event):
		pass

		print "txt_age_text_entered received ", event
			

	def txt_allergies_text_entered( self, event):
		pass

		print "txt_allergies_text_entered received ", event
			

	def combo_consultation_type_text_entered( self, event):
		pass

		print "combo_consultation_type_text_entered received ", event
			
#creating a handler as gmGP_Allergies_handler from patient/gmGP_Allergies.py
# [('classtxt', 'wxTextCtrl')]


class gmGP_Allergies_handler:

	def create_handler(self, panel):
		return gmGP_Allergies_handler(panel)

	def __init__(self, panel):
		self.panel = panel
		if panel <> None:
			self.__set_id()
			self.__set_evt()

	def __set_id(self):
		self.id_map = {}


		id = wxNewId()
		self.panel.classtxt.SetId(id)
		self.id_map['classtxt'] = id
		

	def __set_evt(self):
		pass
		

		EVT_TEXT(self.panel.classtxt,\
			self.id_map['classtxt'],\
			self.classtxt_text_entered)

	def classtxt_text_entered( self, event):
		pass

		print "classtxt_text_entered received ", event
			
#creating a handler as gmGP_AnteNatal_3_handler from patient/gmGP_AnteNatal_3.py
# []
#creating a handler as gmGP_ClinicalSummary_handler from patient/gmGP_ClinicalSummary.py
# []
#creating a handler as gmGP_FamilyHistory_handler from patient/gmGP_FamilyHistory.py
# [('txt_social_history', 'wxTextCtrl')]


class gmGP_FamilyHistory_handler:

	def create_handler(self, panel):
		return gmGP_FamilyHistory_handler(panel)

	def __init__(self, panel):
		self.panel = panel
		if panel <> None:
			self.__set_id()
			self.__set_evt()

	def __set_id(self):
		self.id_map = {}


		id = wxNewId()
		self.panel.txt_social_history.SetId(id)
		self.id_map['txt_social_history'] = id
		

	def __set_evt(self):
		pass
		

		EVT_TEXT(self.panel.txt_social_history,\
			self.id_map['txt_social_history'],\
			self.txt_social_history_text_entered)

	def txt_social_history_text_entered( self, event):
		pass

		print "txt_social_history_text_entered received ", event
			
#creating a handler as gmGP_Immunisation_handler from patient/gmGP_Immunisation.py
# [('missingimmunisation_listbox', 'wxListBox')]


class gmGP_Immunisation_handler:

	def create_handler(self, panel):
		return gmGP_Immunisation_handler(panel)

	def __init__(self, panel):
		self.panel = panel
		if panel <> None:
			self.__set_id()
			self.__set_evt()

	def __set_id(self):
		self.id_map = {}


		id = wxNewId()
		self.panel.missingimmunisation_listbox.SetId(id)
		self.id_map['missingimmunisation_listbox'] = id
		

	def __set_evt(self):
		pass
		

		EVT_LISTBOX(self.panel.missingimmunisation_listbox,\
			self.id_map['missingimmunisation_listbox'],\
			self.missingimmunisation_listbox_list_box_single_clicked)

		EVT_LISTBOX_DCLICK(self.panel.missingimmunisation_listbox,\
			self.id_map['missingimmunisation_listbox'],\
			self.missingimmunisation_listbox_list_box_double_clicked)

	def missingimmunisation_listbox_list_box_single_clicked( self, event):
		pass

		print "missingimmunisation_listbox_list_box_single_clicked received ", event
			

	def missingimmunisation_listbox_list_box_double_clicked( self, event):
		pass

		print "missingimmunisation_listbox_list_box_double_clicked received ", event
			
#creating a handler as gmGP_Measurements_handler from patient/gmGP_Measurements.py
# []
#creating a handler as gmGP_PastHistory_handler from patient/gmGP_PastHistory.py
# []
#creating a handler as gmGP_Prescriptions_handler from patient/gmGP_Prescriptions.py
# [('txt_scriptDate', 'wxTextCtrl'), ('interactiontxt', 'wxTextCtrl')]


class gmGP_Prescriptions_handler:

	def create_handler(self, panel):
		return gmGP_Prescriptions_handler(panel)

	def __init__(self, panel):
		self.panel = panel
		if panel <> None:
			self.__set_id()
			self.__set_evt()

	def __set_id(self):
		self.id_map = {}


		id = wxNewId()
		self.panel.txt_scriptDate.SetId(id)
		self.id_map['txt_scriptDate'] = id
		

		id = wxNewId()
		self.panel.interactiontxt.SetId(id)
		self.id_map['interactiontxt'] = id
		

	def __set_evt(self):
		pass
		

		EVT_TEXT(self.panel.txt_scriptDate,\
			self.id_map['txt_scriptDate'],\
			self.txt_scriptDate_text_entered)

		EVT_TEXT(self.panel.interactiontxt,\
			self.id_map['interactiontxt'],\
			self.interactiontxt_text_entered)

	def txt_scriptDate_text_entered( self, event):
		pass

		print "txt_scriptDate_text_entered received ", event
			

	def interactiontxt_text_entered( self, event):
		pass

		print "interactiontxt_text_entered received ", event
			
#creating a handler as gmGP_Recalls_handler from patient/gmGP_Recalls.py
# []
#creating a handler as gmGP_Referrals_handler from patient/gmGP_Referrals.py
# [('txt_referraldate', 'wxTextCtrl'), ('txt_referral_letter', 'wxTextCtrl')]


class gmGP_Referrals_handler:

	def create_handler(self, panel):
		return gmGP_Referrals_handler(panel)

	def __init__(self, panel):
		self.panel = panel
		if panel <> None:
			self.__set_id()
			self.__set_evt()

	def __set_id(self):
		self.id_map = {}


		id = wxNewId()
		self.panel.txt_referraldate.SetId(id)
		self.id_map['txt_referraldate'] = id
		

		id = wxNewId()
		self.panel.txt_referral_letter.SetId(id)
		self.id_map['txt_referral_letter'] = id
		

	def __set_evt(self):
		pass
		

		EVT_TEXT(self.panel.txt_referraldate,\
			self.id_map['txt_referraldate'],\
			self.txt_referraldate_text_entered)

		EVT_TEXT(self.panel.txt_referral_letter,\
			self.id_map['txt_referral_letter'],\
			self.txt_referral_letter_text_entered)

	def txt_referraldate_text_entered( self, event):
		pass

		print "txt_referraldate_text_entered received ", event
			

	def txt_referral_letter_text_entered( self, event):
		pass

		print "txt_referral_letter_text_entered received ", event
			
#creating a handler as gmGP_Requests_handler from patient/gmGP_Requests.py
# [('txt_requestDate', 'wxTextCtrl')]


class gmGP_Requests_handler:

	def create_handler(self, panel):
		return gmGP_Requests_handler(panel)

	def __init__(self, panel):
		self.panel = panel
		if panel <> None:
			self.__set_id()
			self.__set_evt()

	def __set_id(self):
		self.id_map = {}


		id = wxNewId()
		self.panel.txt_requestDate.SetId(id)
		self.id_map['txt_requestDate'] = id
		

	def __set_evt(self):
		pass
		

		EVT_TEXT(self.panel.txt_requestDate,\
			self.id_map['txt_requestDate'],\
			self.txt_requestDate_text_entered)

	def txt_requestDate_text_entered( self, event):
		pass

		print "txt_requestDate_text_entered received ", event
			
#creating a handler as gmGP_ScratchPadRecalls_handler from patient/gmGP_ScratchPadRecalls.py
# [('scratchpad_txt', 'wxTextCtrl')]


class gmGP_ScratchPadRecalls_handler:

	def create_handler(self, panel):
		return gmGP_ScratchPadRecalls_handler(panel)

	def __init__(self, panel):
		self.panel = panel
		if panel <> None:
			self.__set_id()
			self.__set_evt()

	def __set_id(self):
		self.id_map = {}


		id = wxNewId()
		self.panel.scratchpad_txt.SetId(id)
		self.id_map['scratchpad_txt'] = id
		

	def __set_evt(self):
		pass
		

		EVT_TEXT(self.panel.scratchpad_txt,\
			self.id_map['scratchpad_txt'],\
			self.scratchpad_txt_text_entered)

	def scratchpad_txt_text_entered( self, event):
		pass

		print "scratchpad_txt_text_entered received ", event
			
#creating a handler as gmGP_TabbedLists_handler from patient/gmGP_TabbedLists.py
# []
