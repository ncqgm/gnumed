#!/usr/bin/python

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/blobs_hilbert/index/Attic/indexFrame.py,v $
__version__ = "$Revision: 1.6 $"
__author__ = "Sebastian Hilbert <Sebastian.Hilbert@gmx.net>"

from wxPython.wx import *
from wxPython.lib.anchors import LayoutAnchors

import Image, os, time, shutil, os.path

# location of our modules
sys.path.append(os.path.join('.', 'modules'))

from docPatient import *
from docDocument import cDocument
from gmPhraseWheel import *
import gmLog
gmLog.gmDefLog.SetAllLogLevels(gmLog.lData)
import gmCfg, gmI18N

_log = gmLog.gmDefLog
__cfg__ = gmCfg.gmDefCfg

def create(parent):
	return indexFrame(parent)

[wxID_INDEXFRAME, wxID_INDEXFRAMEADDITIONCOMMENTBOX, wxID_INDEXFRAMEBEFNRBOX, wxID_INDEXFRAMEBEFUNDDATE, wxID_INDEXFRAMEDATEOFBIRTHBOX, wxID_INDEXFRAMEDELPICBUTTON, wxID_INDEXFRAMEDESCRIPTIONCHOICEBOX, wxID_INDEXFRAMEFIRSTNAMEBOX, wxID_INDEXFRAMEGETPICSBUTTON, wxID_INDEXFRAMELASTNAMEBOX, wxID_INDEXFRAMELISTBOX1, wxID_INDEXFRAMEMAINPANEL, wxID_INDEXFRAMEREADFAXBUTTON, wxID_INDEXFRAMESAVEBUTTON, wxID_INDEXFRAMESHORTDECRIPTIONBOX, wxID_INDEXFRAMESHOWPICBUTTON, wxID_INDEXFRAMESTATICTEXT1, wxID_INDEXFRAMESTATICTEXT10, wxID_INDEXFRAMESTATICTEXT11, wxID_INDEXFRAMESTATICTEXT12, wxID_INDEXFRAMESTATICTEXT13, wxID_INDEXFRAMESTATICTEXT2, wxID_INDEXFRAMESTATICTEXT3, wxID_INDEXFRAMESTATICTEXT4, wxID_INDEXFRAMESTATICTEXT5, wxID_INDEXFRAMESTATICTEXT6, wxID_INDEXFRAMESTATICTEXT7, wxID_INDEXFRAMESTATICTEXT8, wxID_INDEXFRAMESTATICTEXT9] = map(lambda _init_ctrls: wxNewId(), range(29))

#-------------------------------------
class indexFrame(wxFrame):
#-------------------------------------    
	picList = []
	validTypeList = []
	page = 0
	selected_pic = ''
	BefValue = ''
	Vorname = ''
	Nachname = ''
	Geburtsdatum = ''
	rawGeburtsdatum = ''
	queryGeburtsdatum = ''
	Obj_Name_value = ''
	Obj_Typ_value = ''
	Obj_Datum_value = ''
	Obj_Referenz_value = ''
	Obj_Beschreibung_value = ''
	
	patid = None
	docid = None
	#---------------------------------------------------------------------------
	def __init__(self, parent):
		# init ctrls
		self._init_ctrls(parent)

		# name of document description XML file
		self.desc_file = __cfg__.get("metadata", "description")
		# checkpoint file whether indexing can start
		self.can_index_file = __cfg__.get("metadata", "can_index")
		# get valid document types from ini-file
		self.valid_doc_types = string.split(__cfg__.get("metadata", "doctypes"),',')

		# items for phraseWheel
		self._init_phrase_wheel()
	#---------------------------------------------------------------------------
	def _init_utils(self):
		pass
	#---------------------------------------------------------------------------
	def _init_ctrls(self, prnt):
		# create our basic frame
		wxFrame.__init__(self, id = wxID_INDEXFRAME, name = 'indexFrame', parent = prnt, pos = wxPoint(361, 150), size = wxSize(763, 616), style = wxDEFAULT_FRAME_STYLE, title = _('assign documents'))
		self._init_utils()

		self.SetClientSize(wxSize(763, 616))

		self.main_panel = wxPanel(id = wxID_INDEXFRAMEMAINPANEL, name = 'main panel', parent = self, pos = wxPoint(0, 0), size = wxSize(763, 616), style = wxTAB_TRAVERSAL)
		self.main_panel.SetBackgroundColour(wxColour(225, 225, 225))

		self.BTN_get_pages = wxButton(
			id = wxID_INDEXFRAMEGETPICSBUTTON,
			label = _('load pages'),
			name = 'BTN_get_pages',
			parent = self.main_panel,
			pos = wxPoint(48, 160),
			size = wxSize(176, 22),
			style = 0
		)
		self.BTN_get_pages.SetToolTipString(_('retrieve all pages for this document'))
		EVT_BUTTON(self.BTN_get_pages, wxID_INDEXFRAMEGETPICSBUTTON, self.on_get_objects)

		self.readFaxButton = wxButton(id = wxID_INDEXFRAMEREADFAXBUTTON, label = _('load fax-document'), name = 'readFaxButton', parent = self.main_panel, pos = wxPoint(48, 232), size = wxSize(176, 22), style = 0)

		self.showPicButton = wxButton(id = wxID_INDEXFRAMESHOWPICBUTTON, label = _('show page'), name = 'showPicButton', parent = self.main_panel, pos = wxPoint(48, 400), size = wxSize(95, 22), style = 0)
		self.showPicButton.SetToolTipString(_('show page'))
		EVT_BUTTON(self.showPicButton, wxID_INDEXFRAMESHOWPICBUTTON, self.OnShowpicbuttonButton)

		self.delPicButton = wxButton(id = wxID_INDEXFRAMEDELPICBUTTON, label = _('delete page'), name = 'delPicButton', parent = self.main_panel, pos = wxPoint(143, 400), size = wxSize(90, 22), style = 0)
		EVT_BUTTON(self.delPicButton, wxID_INDEXFRAMEDELPICBUTTON, self.OnDelpicbuttonButton)

		self.listBox1 = wxListBox(choices = [], id = wxID_INDEXFRAMELISTBOX1, name = 'listBox1', parent = self.main_panel, pos = wxPoint(48, 288), size = wxSize(182, 94), style = 0, validator = wxDefaultValidator)

		self.FirstnameBox = wxTextCtrl(id = wxID_INDEXFRAMEFIRSTNAMEBOX, name = 'FirstnameBox', parent = self.main_panel, pos = wxPoint(304, 112), size = wxSize(152, 22), style = 0, value = self.Vorname)
		self.FirstnameBox.SetToolTipString(_('firstname'))
		self.FirstnameBox.Enable(false)
		self.FirstnameBox.SetBackgroundColour(wxColour(255, 255, 255))

		self.LastnameBox = wxTextCtrl(id = wxID_INDEXFRAMELASTNAMEBOX, name = 'LastnameBox', parent = self.main_panel, pos = wxPoint(304, 160), size = wxSize(152, 22), style = 0, value = self.Nachname)
		self.LastnameBox.SetBackgroundColour(wxColour(255, 255, 255))
		self.LastnameBox.Enable(false)

		self.DateOfBirthBox = wxTextCtrl(id = wxID_INDEXFRAMEDATEOFBIRTHBOX, name = 'DateOfBirthBox', parent = self.main_panel, pos = wxPoint(304, 232), size = wxSize(152, 22), style = 0, value = self.Geburtsdatum)
		self.DateOfBirthBox.SetToolTipString(_('date of birth'))
		self.DateOfBirthBox.Enable(false)

		self.BefundDate = wxTextCtrl(id = wxID_INDEXFRAMEBEFUNDDATE, name = 'BefundDate', parent = self.main_panel, pos = wxPoint(304, 312), size = wxSize(152, 22), style = 0, value = _('please fill in'))

		self.shortDecriptionBox = wxTextCtrl(id = wxID_INDEXFRAMESHORTDECRIPTIONBOX, name = 'shortDecriptionBox', parent = self.main_panel, pos = wxPoint(304, 368), size = wxSize(152, 22), style = 0, value = _('please fill in'))

		self.DescriptionChoiceBox = wxComboBox(
			choices = self.valid_doc_types,
			id = wxID_INDEXFRAMEDESCRIPTIONCHOICEBOX,
			name = 'DescriptionChoiceBox',
			parent = self.main_panel,
			pos = wxPoint(304, 416),
			size = wxSize(152, 22),
			style = 0,
			validator = wxDefaultValidator,
			value = _('choose document type')
		)
		self.DescriptionChoiceBox.SetLabel('')

		self.saveButton = wxButton(id = wxID_INDEXFRAMESAVEBUTTON, label = _('save document'), name = 'saveButton', parent = self.main_panel, pos = wxPoint(544, 112), size = wxSize(144, 328), style = 0)
		self.saveButton.SetToolTipString(_('save'))
		EVT_BUTTON(self.saveButton, wxID_INDEXFRAMESAVEBUTTON, self.OnSavebuttonButton)

		self.additionCommentBox = wxTextCtrl(id = wxID_INDEXFRAMEADDITIONCOMMENTBOX, name = 'additionCommentBox', parent = self.main_panel, pos = wxPoint(48, 488), size = wxSize(640, 88), style = wxTE_MULTILINE, value = ' ')

		self.staticText1 = wxStaticText(id = wxID_INDEXFRAMESTATICTEXT1, label = '1.', name = 'staticText1', parent = self.main_panel, pos = wxPoint(48, 56), size = wxSize(19, 29), style = 0)
		self.staticText1.SetFont(wxFont(25, wxSWISS, wxNORMAL, wxNORMAL, false, ''))

		self.staticText2 = wxStaticText(id = wxID_INDEXFRAMESTATICTEXT2, label = '2.', name = 'staticText2', parent = self.main_panel, pos = wxPoint(312, 56), size = wxSize(19, 29), style = 0)
		self.staticText2.SetFont(wxFont(25, wxSWISS, wxNORMAL, wxNORMAL, false, ''))

		self.staticText3 = wxStaticText(id = wxID_INDEXFRAMESTATICTEXT3, label = '3.', name = 'staticText3', parent = self.main_panel, pos = wxPoint(560, 56), size = wxSize(19, 29), style = 0)
		self.staticText3.SetFont(wxFont(25, wxSWISS, wxNORMAL, wxNORMAL, false, ''))

		self.staticText4 = wxStaticText(id = wxID_INDEXFRAMESTATICTEXT4, label = _('or'), name = 'staticText4', parent = self.main_panel, pos = wxPoint(48, 192), size = wxSize(49, 29), style = 0)
		self.staticText4.SetFont(wxFont(25, wxSWISS, wxNORMAL, wxNORMAL, false, ''))

		self.staticText5 = wxStaticText(id = wxID_INDEXFRAMESTATICTEXT5, label = _('document date (YYYY-MM-DD)'), name = 'staticText5', parent = self.main_panel, pos = wxPoint(304, 288), size = wxSize(158, 16), style = 0)

		self.staticText6 = wxStaticText(id = wxID_INDEXFRAMESTATICTEXT6, label = _('date of birth'), name = 'staticText6', parent = self.main_panel, pos = wxPoint(304, 208), size = wxSize(152, 16), style = 0)

		self.staticText7 = wxStaticText(id = wxID_INDEXFRAMESTATICTEXT7, label = _('string on document '), name = 'staticText7', parent = self.main_panel, pos = wxPoint(48, 96), size = wxSize(176, 16), style = 0)

		self.staticText8 = wxStaticText(id = wxID_INDEXFRAMESTATICTEXT8, label = _('pages'), name = 'staticText8', parent = self.main_panel, pos = wxPoint(48, 264), size = wxSize(152, 16), style = 0)

		self.staticText9 = wxStaticText(id = wxID_INDEXFRAMESTATICTEXT9, label = _('firstname'), name = 'staticText9', parent = self.main_panel, pos = wxPoint(304, 96), size = wxSize(152, 16), style = 0)

		self.staticText10 = wxStaticText(id = wxID_INDEXFRAMESTATICTEXT10, label = _('lastname'), name = 'staticText10', parent = self.main_panel, pos = wxPoint(304, 144), size = wxSize(152, 16), style = 0)

		self.staticText11 = wxStaticText(id = wxID_INDEXFRAMESTATICTEXT11, label = _('short comment'), name = 'staticText11', parent = self.main_panel, pos = wxPoint(304, 352), size = wxSize(152, 16), style = 0)

		self.staticText12 = wxStaticText(
			id = wxID_INDEXFRAMESTATICTEXT12,
			label = _('document type'),
			name = 'staticText12',
			parent = self.main_panel,
			pos = wxPoint(304, 400),
			size = wxSize(152, 16),
			style = 0
		)

		self.staticText13 = wxStaticText(
			id = wxID_INDEXFRAMESTATICTEXT13,
			label = _('additional comment'),
			name = 'staticText13',
			parent = self.main_panel,
			pos=wxPoint(48, 464),
			size = wxSize(143, 16),
			style = 0
		)
	#--------------------------------------------------------------------------
	def _init_phrase_wheel(self):
		"""Set up phrase wheel.

		- directory names in repository correspond to identification
		  strings on paper documents
		- when starting to type an ident the phrase wheel must
		  show matching directories
		"""

		# get document directories
		repository = __cfg__.get("repositories", "to_index")
		doc_dirs = os.listdir(repository)

		# generate list of choices
		phrase_wheel_choices = []
		for i in range(len(doc_dirs)):
			# DON'T fail on missing checkpoint files here yet
			# in order to facilitate maximum parallelity
			if not os.path.exists(os.path.join(doc_dirs[i], self.can_index_file)):
				_log.Log(gmLog.lInfo, "Document directory [%s] not yet checkpointed (%s) for indexing. Let's see who wins the race." % (doc_dirs[i], self.can_index_file))
			# same weight for all of them
			phrase_wheel_choices.append({'ID': i, 'label': doc_dirs[i], 'weight': 1})

		#<DEBUG>
		_log.Log(gmLog.lData, "document dirs: %s" % str(phrase_wheel_choices))
		#</DEBUG>

		mp = cMatchProvider_FixedList(phrase_wheel_choices)
		self.doc_id_wheel = cPhraseWheel(self.main_panel, self.clicked, pos = (48, 112), size = (176, 22), aMatchProvider=mp, aDelay = 400)
		self.doc_id_wheel.SetToolTipString(_('physical document ID'))

		self.doc_id_wheel.on_resize (None)
	#---------------------------------------------------------------------------
	def clicked (data):
		print "Selected :%s" % data
	#---------------------------------------------------------------------------
	def show_pic(self,bild):
		try:
			bild=Image.open(bild)
			bild.show()
			return true
		except IOError:
			dlg = wxMessageDialog(self, _('page could not be opened or does not exist'),_('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()
	#--------------------------------------------------------------------------
	def readPatientDat(self):
		# get patient data from BDT/XDT file
		pat_file = __cfg__.get("metadata", "patient")
		aPatient = cPatient()
		try:
			aPatient.loadFromFile("xdt",os.path.expanduser(os.path.join(__cfg__.get("metadata", "location"), pat_file)))
			self.Vorname = aPatient.firstnames
			self.Nachname =  aPatient.lastnames
			self.rawGeburtsdatum = aPatient.dob
		except:
			dlg = wxMessageDialog(self, _('unable to find XDT-file '),_('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()
			exc = sys.exc_info()
			_log.LogException ("Exception: problem with reading patient data from xDT file " + pat_file, exc)
			_log.LogException ("Exception: xDT file. I tried" + os.path.expanduser(os.path.join(__cfg__.get("metadata", "location"), pat_file)), exc)
			return None
		self.Geburtsdatum = self.rawGeburtsdatum[:4]  + '-' + self.rawGeburtsdatum[4:6] + '-' + self.rawGeburtsdatum[-2:]
		self.queryGeburtsdatum = self.rawGeburtsdatum
	#--------------------------------------------------------------------------
	def CompleteRefresh(self):
		self.FirstnameBox.Clear()
		self.LastnameBox.Clear()
		self.DateOfBirthBox.Clear()
		self.BefundDate.Clear()
		self.shortDecriptionBox.Clear()
		self.DescriptionChoiceBox.SetSelection(-1)
		self.additionCommentBox.Clear()
		self.picList = []
		self.listBox1.Clear()
	#--------------------------------------------------------------------------
	def UpdatePicList(self):
		if len(self.picList) == 0:
			self.listBox1.Append(_('page')+'1')
			self.picList.append(_('page')+'1')
		else:
			lastPageInList=self.picList[len(self.picList)-1]
			biggest_number_strg=lastPageInList.replace(_('page'),'')
			biggest_number= int(biggest_number_strg) + 1
			self.listBox1.Append(_('page') + `biggest_number`)
			self.picList.append(_('page') + `biggest_number`)
	#--------------------------------------------------------------------------
	def loadrecords(self):
		self.readPatientDat()
		self.BefValue=self.doc_id_wheel.GetLineText(0)
		# has the user supplied anything ?
		if not self.BefValue == '':
			if os.path.isdir(__cfg__.get("source", "repositories") + self.BefValue):
				working_dir = __cfg__.get("source", "repositories") + self.BefValue
				#print "U filled in:" + self.BefValue 
				try:
					#read self.desc_file
					in_file = open(__cfg__.get("source", "repositories") + self.BefValue + '/' + self.desc_file,"r")
					xml_content = in_file.read()
					in_file.close()
					xml_contentlist = string.split(xml_content,'\n')
					runs=len(xml_contentlist)
					x=0
					while x < runs:
						value = xml_contentlist[x]
						_log.Log (gmLog.lInfo, "teste " + value)
						try :
							# find all occurences of <image>
							string.index(value,'<image>')
							stripped_value = value[7:-8]
							# append occurence to list in gui
							if os.name == 'posix':
								self.listBox1.Append(string.replace(stripped_value,'.jpg',''))
							else:
								self.listBox1.Append(string.replace(stripped_value,'.bmp',''))
							self.picList.append(stripped_value)
							_log.Log (gmLog.lInfo, "added" + stripped_value + "to GUI-list")
							# increase and start over with next line
							x=x+1
						except ValueError:
							x=x+1
					x=0
					while x < runs:
						value = xml_contentlist[x]
						_log.Log (gmLog.lInfo, "once again" + value)
						try :
							# find all occurences of <ref_tag>
							string.index(value,'<'+__cfg__.get("metadata", "ref_tag")+'>')
							_log.Log (gmLog.lInfo, "tested" + value + "for string : " + __cfg__.get("metadata", "ref_tag"))
							self.Obj_Referenz_value = value[int(len(__cfg__.get("metadata", "ref_tag")))+2:-(int(len(__cfg__.get("metadata", "ref_tag")))+3)]
							x=x+1
						except ValueError:
							x=x+1
					# has there been a prior index session with this data ?
					if os.path.isfile(__cfg__.get("source", "repositories") + self.BefValue + '/' + self.can_index_file):
						x=0
						while x < runs:
							value = xml_contentlist[x]
							_log.Log (gmLog.lInfo, "once again" + value)
							try :
								# find all occurences of <date_tag>
								string.index(value,'<'+__cfg__.get("metadata", "date_tag")+'>')
								_log.Log (gmLog.lInfo, "tested" + value + "for string : " + __cfg__.get("metadata", "date_tag"))
								self.Obj_Datum_value = value[int(len(__cfg__.get("metadata", "date_tag")))+2:-(int(len(__cfg__.get("metadata", "date_tag")))+3)]
								x=x+1
							except ValueError:
								x=x+1
						x=0
						while x < runs:
							value = xml_contentlist[x]
							_log.Log (gmLog.lInfo, "test again" + value)
							try :
								# find all occurences of <type_tag>
								string.index(value,'<'+__cfg__.get("metadata", "type_tag")+'>')
								_log.Log (gmLog.lInfo, "tested" + value + "for string : " + __cfg__.get("metadata", "type_tag"))
								self.Obj_Typ_value = value[int(len(__cfg__.get("metadata", "type_tag")))+2:-(int(len(__cfg__.get("metadata", "type_tag")))+3)]
								x=x+1
							except ValueError:
								x=x+1
						x=0
						while x < runs:
							value = xml_contentlist[x]
							_log.Log (gmLog.lInfo, "test again" + value)
							try :
								# find all occurences of <comment_tag>
								string.index(value,'<'+__cfg__.get("metadata", "comment_tag")+'>')
								_log.Log (gmLog.lInfo, "tested" + value + "for string : " + __cfg__.get("metadata", "comment_tag"))
								self.Obj_Name_value = value[int(len(__cfg__.get("metadata", "comment_tag")))+2:-(int(len(__cfg__.get("metadata", "comment_tag")))+3)]
								x=x+1
							except ValueError:
								x=x+1
						x=0
						while x < runs:
							value = xml_contentlist[x]
							_log.Log (gmLog.lInfo, "test again" + value)
							try :
							   # find all occurences of <add_comment_tag>
								string.index(value,'<'+__cfg__.get("metadata", "add_comment_tag")+'>')
								_log.Log (gmLog.lInfo, "tested" + value + "for string : " + __cfg__.get("metadata", "add_comment_tag"))
								self.Obj_Beschreibung_value = value[int(len(__cfg__.get("metadata", "add_comment_tag")))+2:-(int(len(__cfg__.get("metadata", "add_comment_tag")))+3)]
								x=x+1
							except ValueError:
								x=x+1
					else :
						return
					
				except IOError:
					dlg = wxMessageDialog(self, _('unable to hunt down XML-file'),_('Attention'), wxOK | wxICON_INFORMATION)
					try:
						dlg.ShowModal()
					finally:
						dlg.Destroy()
			else:
				dlg = wxMessageDialog(self, _('Could not fine any documents relating to this document#'),_('Attention'), wxOK | wxICON_INFORMATION)
				try:
					dlg.ShowModal()
				finally:
					dlg.Destroy()
		else:
			dlg = wxMessageDialog(self, _('You did not fill in any document#'),_('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()
	#--------------------------------
	def updateGUIonLoadRecords(self):
		self.FirstnameBox.AppendText(self.Vorname)
		self.LastnameBox.AppendText(self.Nachname)
		self.DateOfBirthBox.AppendText(self.Geburtsdatum)
		#if not self.Obj_Datum_value == _('please fill in'):
		self.BefundDate.AppendText(self.Obj_Datum_value)
		#if not self.Obj_Name_value == _('please fill in'):
		self.shortDecriptionBox.AppendText(self.Obj_Name_value)
		#if not self.Obj_Typ_value =='':
		index = self.DescriptionChoiceBox.FindString(self.Obj_Typ_value)
		self.DescriptionChoiceBox.SetSelection(index)
		#if not self.Obj_Beschreibung_value =='':
		self.additionCommentBox.AppendText(self.Obj_Beschreibung_value)
	#----------------------------------------
	# event handlers
	#----------------------------------------
	def on__get_pages(self, event):
		self.CompleteRefresh()
		self.loadrecords()
		self.updateGUIonLoadRecords()
	#----------------------------------------
	def OnShowpicbuttonButton(self, event):
		self.BefValue=self.doc_id_wheel.GetLineText(0)
		current_selection=self.listBox1.GetSelection()
		if not current_selection == -1:
			pic_selection=current_selection+1
			self.selected_pic=self.listBox1.GetString(current_selection)
			#for debugging only
			print "I show u:" + self.selected_pic
			if os.name == 'posix':
				self.show_pic(__cfg__.get("source", "repositories") + self.BefValue + '/' + self.selected_pic + '.jpg')
			else:
				self.show_pic(__cfg__.get("source", "repositories") + self.BefValue + '/' + self.selected_pic + '.bmp')
		else:
			dlg = wxMessageDialog(self, _('You did not select a page'),_('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()

	def OnDelpicbuttonButton(self, event):
		current_selection=self.listBox1.GetSelection()
		self.BefValue=self.doc_id_wheel.GetLineText(0)
		if current_selection == -1:
			dlg = wxMessageDialog(self, _('You did not select a page'),_('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()
			
		else:
			self.selected_pic=self.listBox1.GetString(current_selection)
			#print self.picList
			#del page from hdd
			try:
				os.remove(__cfg__.get("source", "repositories") + self.BefValue + '/' + self.selected_pic + '.jpg')
			except OSError:
				_log.Log (gmLog.lErr, "I was unable to wipe the file " + __cfg__.get("source", "repositories") + self.BefValue + '/' + self.selected_pic + '.jpg' + " from disk because it simply was not there ")
				dlg = wxMessageDialog(self, _('I am afraid I was not able to delete the page from disk because it was not there'),_('Attention'), wxOK | wxICON_INFORMATION)
				try:
					dlg.ShowModal()
				finally:
					dlg.Destroy()
			#now rename (decrease index by 1) all pages above the deleted one
			i = current_selection
			#print self.picList
			for i in range(i,len(self.picList)-1):
				try:
					os.rename(__cfg__.get("source", "repositories") + self.BefValue + '/' + self.listBox1.GetString(i+1) + '.jpg',__cfg__.get("source", "repositories") + self.BefValue + '/' + self.listBox1.GetString(i) + '.jpg')
				except OSError:
					_log.Log (gmLog.lErr, "I was unable to rename the file " + __cfg__.get("source", "repositories") + self.BefValue + '/' + self.listBox1.GetString(i+1) + '.jpg' + " from disk because it simply was not there ")
				print "I renamed" +str(__cfg__.get("source", "repositories") + self.BefValue + '/' + self.listBox1.GetString(i+1) + '.jpg') + "into" + str(__cfg__.get("source", "repositories") + self.BefValue + '/' + self.listBox1.GetString(i) + '.jpg')
			
			#print "u want to del:" + self.selected_pic
			self.listBox1.Delete(current_selection)
			self.picList.remove(self.selected_pic + '.jpg')
			#rebuild list to clean the gap
			i = 0
			for i in range(len(self.picList)):
				if i == 0:
					self.picList = []
					self.listBox1 = wxListBox(choices = [], id = wxID_INDEXFRAMELISTBOX1, name = 'listBox1', parent = self.main_panel, pos = wxPoint(48, 288), size = wxSize(182, 94), style = 0, validator = wxDefaultValidator)
				self.UpdatePicList()        

	def OnSavebuttonButton(self, event):
		event.Skip()
		# check whether values for date of record, record type, short comment and extended comment
		# have been filled in
		date=self.BefundDate.GetLineText(0)
		datechecklist = string.split(date,'-')
		shortDescription=self.shortDecriptionBox.GetLineText(0)
		DescriptionChoice=self.DescriptionChoiceBox.GetSelection()
		additionalComment=self.additionCommentBox.GetLineText(0)
		# do some checking on the date
		if date == _('please fill in'):
			dlg = wxMessageDialog(self, _('You did not fill in a document date'),
			  _('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()
				
		elif len(date) != 10:
			dlg = wxMessageDialog(self, _('document date invalid'),
			  _('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()
				
		elif len(datechecklist) != 3:
			dlg = wxMessageDialog(self, _('date ( document date ) is invalid'),
			  _('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()
		
		elif len(datechecklist[0]) != 4:
			dlg = wxMessageDialog(self, _('date format ( year ) is invalid'),
			  _('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()
				
		elif int(datechecklist[0]) < 1900:
			dlg = wxMessageDialog(self, _('given year is unlikely'),
			  _('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()
		
		elif datechecklist[0] > time.strftime("%Y", time.localtime()):
			dlg = wxMessageDialog(self, _('I will not accept future dates'),
			  _('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()
				
		elif len(datechecklist[1]) != 2:
			dlg = wxMessageDialog(self, _('date (month) invalid'),
			  _('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()
		
		elif len(datechecklist[2]) != 2:
			dlg = wxMessageDialog(self, _('(day) invalid'),
			  _('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()
		
		elif int(datechecklist[1]) < 01 :
			dlg = wxMessageDialog(self, _('month must be inbetween 01 and 12'),
			  _('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()
		elif int(datechecklist[1]) > 12 :
			dlg = wxMessageDialog(self, _('month must be inbetween 01 and 12'),
			  _('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()
		
		elif int(datechecklist[2]) < 01 :
			dlg = wxMessageDialog(self, _('day must be inbetween 01 and 31'),
			  _('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()
				
		elif int(datechecklist[2]) > 31 :
			dlg = wxMessageDialog(self, _('day must be inbetween 01 and 31'),
			  _('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()
		
		elif shortDescription == _('please fill in'):
			dlg = wxMessageDialog(self, _('You did not fill in a short comment'),
			  _('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()
		
		elif shortDescription == '':
			dlg = wxMessageDialog(self, _('You did not fill in a short comment'),
			  _('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()
		
		elif DescriptionChoice == -1:
			dlg = wxMessageDialog(self, _('You did not select a document type'),
			  _('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()
		
		elif DescriptionChoice == 'please choose':
			dlg = wxMessageDialog(self, _('You did not select a document type'),
			  _('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()
		
		elif additionalComment == '':
			dlg = wxMessageDialog(self, _('please fill the box "additional comment"'),
			  _('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()
		
		else:
			in_file = open(__cfg__.get("source", "repositories") + self.BefValue + '/' + self.desc_file,"r")
			xml_content = in_file.read()
			in_file.close()
			#del old self.desc_file
			os.remove(__cfg__.get("source", "repositories") + self.BefValue + '/' + self.desc_file)
			# create xml file
			out_file = open(__cfg__.get("source", "repositories") + self.BefValue + '/' + self.desc_file,"w")
			tmpdir_content = self.picList
			runs = len(tmpdir_content)
			x=0
			out_file.write ("<" + __cfg__.get("metadata", "document_tag")    + ">\n")
			out_file.write ("<" + __cfg__.get("metadata", "name_tag")        + ">" + self.Nachname           + "</" + __cfg__.get("metadata", "name_tag")      + ">\n")
			out_file.write ("<" + __cfg__.get("metadata", "firstname_tag")   + ">" + self.Vorname            + "</" + __cfg__.get("metadata", "firstname_tag") + ">\n")
			out_file.write ("<" + __cfg__.get("metadata", "birth_tag")       + ">" + self.queryGeburtsdatum  + "</" + __cfg__.get("metadata", "birth_tag")     + ">\n" )
			out_file.write ("<" + __cfg__.get("metadata", "date_tag")        + ">" + self.BefundDate.GetLineText(0) + "</" + __cfg__.get("metadata", "date_tag") + ">\n" )
			out_file.write ("<" + __cfg__.get("metadata", "type_tag")        + ">" + self.DescriptionChoiceBox.GetStringSelection() + "</" + __cfg__.get("metadata", "type_tag") + ">\n")
			out_file.write ("<" + __cfg__.get("metadata", "comment_tag")     + ">" + self.shortDecriptionBox.GetLineText(0) + "</" + __cfg__.get("metadata", "comment_tag") + ">\n")
			out_file.write ("<" + __cfg__.get("metadata", "add_comment_tag") + ">" + self.additionCommentBox.GetValue() + "</" + __cfg__.get("metadata", "add_comment_tag") + ">\n")
			out_file.write ("<" + __cfg__.get("metadata", "ref_tag")         + ">" + self.Obj_Referenz_value + "</" + __cfg__.get("metadata", "ref_tag") + ">\n")
			while x < runs:
				out_file.write ("<image>" + tmpdir_content[x] + "</image>\n")
				x=x+1
			out_file.write ("</" + __cfg__.get("metadata", "document_tag") + ">")
			out_file.close()
			# copy XDT-file ( not the XML-file ) into repository directory
			pat_file = __cfg__.get("metadata", "patient")
			shutil.copy(os.path.expanduser(os.path.join(__cfg__.get("metadata", "location"), pat_file)),__cfg__.get("source", "repositories") + self.BefValue + '/')
			# generate a file to tell import script that we are done here
			out_file = open(__cfg__.get("source", "repositories") + self.BefValue + '/' + self.can_index_file,"w")
			#refresh everything
			self.picList = []
			self.Vorname = ''
			self.Nachname = ''
			self.Geburtsdatum = ''
			self.CompleteRefresh()
			# empty doc_id_wheel as well
			self.doc_id_wheel.Clear()
			# items for phraseWheel
			self.initgmPhraseWheel()
			
# this line is a replacement for gmPhraseWhell just in case it doesn't work 
#self.doc_id_wheel = wxTextCtrl(id = wxID_INDEXFRAMEBEFNRBOX, name = 'textCtrl1', parent = self.main_panel, pos = wxPoint(48, 112), size = wxSize(176, 22), style = 0, value = _('document#'))
