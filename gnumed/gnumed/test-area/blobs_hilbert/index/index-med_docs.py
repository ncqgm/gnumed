#!/usr/bin/python

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/blobs_hilbert/index/Attic/index-med_docs.py,v $
__version__ = "$Revision: 1.1 $"
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
import docXML

_log = gmLog.gmDefLog
__cfg__ = gmCfg.gmDefCfg

def create(parent):
	return indexFrame(parent)

[wxID_INDEXFRAME, wxID_INDEXFRAMEADDITIONCOMMENTBOX, wxID_INDEXFRAMEBEFNRBOX, wxID_INDEXFRAMEBEFUNDDATE, wxID_INDEXFRAMEDATEOFBIRTHBOX, wxID_INDEXFRAMEDELPICBUTTON, wxID_INDEXFRAMEDESCRIPTIONCHOICEBOX, wxID_INDEXFRAMEFIRSTNAMEBOX, wxID_INDEXFRAMEGETPAGESBUTTON, wxID_INDEXFRAMELASTNAMEBOX, wxID_INDEXFRAMELBOXPAGES, wxID_INDEXFRAMEMAINPANEL, wxID_INDEXFRAMEREADFAXBUTTON, wxID_INDEXFRAMESAVEBUTTON, wxID_INDEXFRAMESHORTDECRIPTIONBOX, wxID_INDEXFRAMESHOWPICBUTTON, wxID_INDEXFRAMESTATICTEXT1, wxID_INDEXFRAMESTATICTEXT10, wxID_INDEXFRAMESTATICTEXT11, wxID_INDEXFRAMESTATICTEXT12, wxID_INDEXFRAMESTATICTEXT13, wxID_INDEXFRAMESTATICTEXT2, wxID_INDEXFRAMESTATICTEXT3, wxID_INDEXFRAMESTATICTEXT4, wxID_INDEXFRAMESTATICTEXT5, wxID_INDEXFRAMESTATICTEXT6, wxID_INDEXFRAMESTATICTEXT7, wxID_INDEXFRAMESTATICTEXT8, wxID_INDEXFRAMESTATICTEXT9] = map(lambda _init_ctrls: wxNewId(), range(29))

#-------------------------------------
class indexFrame(wxFrame):
#-------------------------------------
	doc_pages = []
	page = 0
	selected_pic = ''
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

		# get valid document types from ini-file
		self.valid_doc_types = string.split(__cfg__.get("metadata", "doctypes"),',')

		# init ctrls
		self._init_ctrls(parent)

		# we are indexing data from one particular patient
		# this is a design decision
		if not self.__load_patient():
			raise ValueError
		self.__fill_pat_fields()

		# repository base
		self.repository = os.path.expanduser(__cfg__.get("repositories", "to_index"))
		# name of document description XML file
		self.desc_file_name = __cfg__.get("metadata", "description")
		# checkpoint file whether indexing can start
		self.can_index_file = __cfg__.get("metadata", "can_index")

		# items for phraseWheel
		if not self._init_phrase_wheel():
			raise ValueError
	#---------------------------------------------------------------------------
	def _init_utils(self):
		pass
	#---------------------------------------------------------------------------
	def _init_ctrls(self, prnt):

		#-- basic frame -------------
		wxFrame.__init__(
			self,
			id = wxID_INDEXFRAME,
			name = 'indexFrame',
			parent = prnt,
			pos = wxPoint(361, 150),
			size = wxSize(763, 616),
			style = wxDEFAULT_FRAME_STYLE,
			title = _('Please select a document for this patient.')
		)
		self._init_utils()
		self.SetClientSize(wxSize(763, 616))

		#-- main panel -------------
		self.PNL_main = wxPanel(
			id = wxID_INDEXFRAMEMAINPANEL,
			name = 'main panel',
			parent = self,
			pos = wxPoint(0, 0),
			size = wxSize(763, 616),
			style = wxTAB_TRAVERSAL
		)
		self.PNL_main.SetBackgroundColour(wxColour(225, 225, 225))

		#-- load pages button -------------
		self.BTN_get_pages = wxButton(
			id = wxID_INDEXFRAMEGETPAGESBUTTON,
			label = _('load pages'),
			name = 'BTN_get_pages',
			parent = self.PNL_main,
			pos = wxPoint(48, 160),
			size = wxSize(176, 22),
			style = 0
		)
		self.BTN_get_pages.SetToolTipString(_('load all pages for this document'))
		EVT_BUTTON(self.BTN_get_pages, wxID_INDEXFRAMEGETPAGESBUTTON, self.on_get_pages)

		#-- load fax button -------------
		self.BTN_read_fax = wxButton(
			id = wxID_INDEXFRAMEREADFAXBUTTON,
			label = _('load fax-document'),
			name = 'BTN_read_fax',
			parent = self.PNL_main,
			pos = wxPoint(48, 232),
			size = wxSize(176, 22),
			style = 0
		)

		self.showPicButton = wxButton(id = wxID_INDEXFRAMESHOWPICBUTTON, label = _('show page'), name = 'showPicButton', parent = self.PNL_main, pos = wxPoint(48, 400), size = wxSize(95, 22), style = 0)
		self.showPicButton.SetToolTipString(_('show page'))
		EVT_BUTTON(self.showPicButton, wxID_INDEXFRAMESHOWPICBUTTON, self.OnShowpicbuttonButton)

		self.delPicButton = wxButton(id = wxID_INDEXFRAMEDELPICBUTTON, label = _('delete page'), name = 'delPicButton', parent = self.PNL_main, pos = wxPoint(143, 400), size = wxSize(90, 22), style = 0)
		EVT_BUTTON(self.delPicButton, wxID_INDEXFRAMEDELPICBUTTON, self.OnDelpicbuttonButton)

		#-- list box with pages -------------
		self.LBOX_doc_pages = wxListBox(
			choices = [],
			id = wxID_INDEXFRAMELBOXPAGES,
			name = 'LBOX_doc_pages',
			parent = self.PNL_main,
			pos = wxPoint(48, 288),
			size = wxSize(182, 94),
			style = 0,
			validator = wxDefaultValidator
		)

		#-- first name text box -------------
		self.TBOX_first_name = wxTextCtrl(
			id = wxID_INDEXFRAMEFIRSTNAMEBOX,
			name = 'TBOX_first_name',
			parent = self.PNL_main,
			pos = wxPoint(304, 112),
			size = wxSize(152, 22),
			style = wxTE_READONLY,
			value = 'loading ...'
		)
		self.TBOX_first_name.SetToolTipString(_('first name of patient'))
		self.TBOX_first_name.SetBackgroundColour(wxColour(255, 255, 255))
		#self.TBOX_first_name.Enable(false)

		#-- last name text box -------------
		self.TBOX_last_name = wxTextCtrl(
			id = wxID_INDEXFRAMELASTNAMEBOX,
			name = 'TBOX_last_name',
			parent = self.PNL_main,
			pos = wxPoint(304, 160),
			size = wxSize(152, 22),
			style = wxTE_READONLY,
			value = 'loading ...'
		)
		self.TBOX_first_name.SetToolTipString(_('last name of patient'))
		self.TBOX_last_name.SetBackgroundColour(wxColour(255, 255, 255))
		#self.TBOX_last_name.Enable(false)

		#-- dob text box -------------
		self.TBOX_dob = wxTextCtrl(
			id = wxID_INDEXFRAMEDATEOFBIRTHBOX,
			name = 'TBOX_dob',
			parent = self.PNL_main,
			pos = wxPoint(304, 232),
			size = wxSize(152, 22),
			style = wxTE_READONLY,
			value = 'loading ...'
		)
		self.TBOX_dob.SetToolTipString(_('date of birth'))
		#self.TBOX_last_name.SetBackgroundColour(wxColour(255, 255, 255))
		#self.TBOX_dob.Enable(false)

		#-- document date text box -------------
		self.TBOX_doc_date = wxTextCtrl(
			id = wxID_INDEXFRAMEBEFUNDDATE,
			name = 'TBOX_doc_date',
			parent = self.PNL_main,
			pos = wxPoint(304, 312),
			size = wxSize(152, 22),
			style = 0,
			value = _('please fill in')
		)

		#-- document comment text box -------------
		self.TBOX_desc_short = wxTextCtrl(
			id = wxID_INDEXFRAMESHORTDECRIPTIONBOX,
			name = 'TBOX_desc_short',
			parent = self.PNL_main,
			pos = wxPoint(304, 368),
			size = wxSize(152, 22),
			style = 0,
			value = _('please fill in')
		)

		#-- document type selection box -------------
		self.SelBOX_doc_type = wxComboBox(
			choices = self.valid_doc_types,
			id = wxID_INDEXFRAMEDESCRIPTIONCHOICEBOX,
			name = 'SelBOX_doc_type',
			parent = self.PNL_main,
			pos = wxPoint(304, 416),
			size = wxSize(152, 22),
			style = 0,
			validator = wxDefaultValidator,
			value = _('choose document type')
		)
		self.SelBOX_doc_type.SetLabel('')

		self.saveButton = wxButton(id = wxID_INDEXFRAMESAVEBUTTON, label = _('save document'), name = 'saveButton', parent = self.PNL_main, pos = wxPoint(544, 112), size = wxSize(144, 328), style = 0)
		self.saveButton.SetToolTipString(_('save'))
		EVT_BUTTON(self.saveButton, wxID_INDEXFRAMESAVEBUTTON, self.OnSavebuttonButton)

		self.additionCommentBox = wxTextCtrl(id = wxID_INDEXFRAMEADDITIONCOMMENTBOX, name = 'additionCommentBox', parent = self.PNL_main, pos = wxPoint(48, 488), size = wxSize(640, 88), style = wxTE_MULTILINE, value = ' ')

		self.staticText1 = wxStaticText(id = wxID_INDEXFRAMESTATICTEXT1, label = '1.', name = 'staticText1', parent = self.PNL_main, pos = wxPoint(48, 56), size = wxSize(19, 29), style = 0)
		self.staticText1.SetFont(wxFont(25, wxSWISS, wxNORMAL, wxNORMAL, false, ''))

		self.staticText2 = wxStaticText(id = wxID_INDEXFRAMESTATICTEXT2, label = '2.', name = 'staticText2', parent = self.PNL_main, pos = wxPoint(312, 56), size = wxSize(19, 29), style = 0)
		self.staticText2.SetFont(wxFont(25, wxSWISS, wxNORMAL, wxNORMAL, false, ''))

		self.staticText3 = wxStaticText(id = wxID_INDEXFRAMESTATICTEXT3, label = '3.', name = 'staticText3', parent = self.PNL_main, pos = wxPoint(560, 56), size = wxSize(19, 29), style = 0)
		self.staticText3.SetFont(wxFont(25, wxSWISS, wxNORMAL, wxNORMAL, false, ''))

		self.staticText4 = wxStaticText(id = wxID_INDEXFRAMESTATICTEXT4, label = _('or'), name = 'staticText4', parent = self.PNL_main, pos = wxPoint(48, 192), size = wxSize(49, 29), style = 0)
		self.staticText4.SetFont(wxFont(25, wxSWISS, wxNORMAL, wxNORMAL, false, ''))

		self.staticText5 = wxStaticText(id = wxID_INDEXFRAMESTATICTEXT5, label = _('document date (YYYY-MM-DD)'), name = 'staticText5', parent = self.PNL_main, pos = wxPoint(304, 288), size = wxSize(158, 16), style = 0)

		self.staticText6 = wxStaticText(id = wxID_INDEXFRAMESTATICTEXT6, label = _('date of birth'), name = 'staticText6', parent = self.PNL_main, pos = wxPoint(304, 208), size = wxSize(152, 16), style = 0)

		self.staticText7 = wxStaticText(id = wxID_INDEXFRAMESTATICTEXT7, label = _('string on document '), name = 'staticText7', parent = self.PNL_main, pos = wxPoint(48, 96), size = wxSize(176, 16), style = 0)

		self.staticText8 = wxStaticText(id = wxID_INDEXFRAMESTATICTEXT8, label = _('pages'), name = 'staticText8', parent = self.PNL_main, pos = wxPoint(48, 264), size = wxSize(152, 16), style = 0)

		self.staticText9 = wxStaticText(id = wxID_INDEXFRAMESTATICTEXT9, label = _('firstname'), name = 'staticText9', parent = self.PNL_main, pos = wxPoint(304, 96), size = wxSize(152, 16), style = 0)

		self.staticText10 = wxStaticText(id = wxID_INDEXFRAMESTATICTEXT10, label = _('lastname'), name = 'staticText10', parent = self.PNL_main, pos = wxPoint(304, 144), size = wxSize(152, 16), style = 0)

		self.staticText11 = wxStaticText(id = wxID_INDEXFRAMESTATICTEXT11, label = _('short comment'), name = 'staticText11', parent = self.PNL_main, pos = wxPoint(304, 352), size = wxSize(152, 16), style = 0)

		self.staticText12 = wxStaticText(
			id = wxID_INDEXFRAMESTATICTEXT12,
			label = _('document type'),
			name = 'staticText12',
			parent = self.PNL_main,
			pos = wxPoint(304, 400),
			size = wxSize(152, 16),
			style = 0
		)

		self.staticText13 = wxStaticText(
			id = wxID_INDEXFRAMESTATICTEXT13,
			label = _('additional comment'),
			name = 'staticText13',
			parent = self.PNL_main,
			pos=wxPoint(48, 464),
			size = wxSize(143, 16),
			style = 0
		)
	#--------------------------------
	def _init_phrase_wheel(self):
		"""Set up phrase wheel.

		- directory names in self.repository correspond to identification
		  strings on paper documents
		- when starting to type an ident the phrase wheel must
		  show matching directories
		"""

		# get document directories
		doc_dirs = os.listdir(self.repository)

		# generate list of choices
		phrase_wheel_choices = []
		for i in range(len(doc_dirs)):
			full_dir = os.path.join(self.repository, doc_dirs[i])

			# don't add stray files
			if not os.path.isdir(full_dir):
				_log.Log(gmLog.lData, "ignoring stray file [%s]" % doc_dirs[i])
				continue

			# DON'T fail on missing checkpoint files here yet
			# in order to facilitate maximum parallelity
			if not os.path.exists(os.path.join(full_dir, self.can_index_file)):
				_log.Log(gmLog.lInfo, "Document directory [%s] not yet checkpointed with [%s] for indexing. Skipping." % (full_dir, self.can_index_file))
				continue

			# same weight for all of them
			phrase_wheel_choices.append({'ID': i, 'label': doc_dirs[i], 'weight': 1})

		#<DEBUG>
		_log.Log(gmLog.lData, "document dirs: %s" % str(phrase_wheel_choices))
		#</DEBUG>

		if len(phrase_wheel_choices) == 0:
			_log.Log(gmLog.lWarn, "No document directories in repository. Nothing to do !.")
			dlg = wxMessageDialog(
				self,
				_("There are no documents in the repository.\n(%s)\n\nSeems like there's nothing to do today." % self.repository),
				_('Information'),
				wxOK | wxICON_INFORMATION
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		# FIXME: we need to set this to non-learning mode
		mp = cMatchProvider_FixedList(phrase_wheel_choices)
		self.doc_id_wheel = cPhraseWheel(
			self.PNL_main,
			self.wheel_callback,
			pos = (48, 112),
			size = (176, 22),
			aMatchProvider=mp,
			aDelay = 400
		)
		self.doc_id_wheel.SetToolTipString(_('physical document ID'))
		self.doc_id_wheel.on_resize (None)

		return 1
	#----------------------------------------
	# event handlers
	#----------------------------------------
	def on_get_pages(self, event):
		_log.Log(gmLog.lData, "Trying to load document.")
		if not self.__load_doc():
			_log.Log(gmLog.lErr, "Cannot load document object file list.")
			dlg = wxMessageDialog(
				self,
				_('Cannot load document object file list from xDT file.\n\nPlease consult the error log for details.'),
				_('Error'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		self.__fill_doc_fields()
	#----------------------------------------

	#---------------------------------------------------------------------------
	def wheel_callback (self, data):
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
	#----------------------------------------
	# internal methods
	#----------------------------------------
	def __load_patient(self):
		# later on we might want to provide access
		# to other methods of getting the patient

		# get patient data from BDT/XDT file
		pat_file = os.path.expanduser(__cfg__.get("metadata", "patient_file"))
		self.myPatient = cPatient()
		if not self.myPatient.loadFromFile("xdt", pat_file):
			_log.Log(gmLog.lPanic, "Cannot read patient from xDT file [%s]" % pat_file)
			dlg = wxMessageDialog(
				self,
				_('Cannot load patient from xDT file.\n\nPlease consult the error log for details.'),
				_('Error'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None


#		self.Geburtsdatum = self.rawGeburtsdatum[:4]  + '-' + self.rawGeburtsdatum[4:6] + '-' + self.rawGeburtsdatum[-2:]
#		self.queryGeburtsdatum = self.rawGeburtsdatum
		return 1
	#----------------------------------------
	def __fill_pat_fields(self):
		self.TBOX_first_name.SetValue(self.myPatient.firstnames)
		self.TBOX_last_name.SetValue(self.myPatient.lastnames)
		self.TBOX_dob.SetValue(self.myPatient.dob)
	#----------------------------------------
	#----------------------------------------
	def __clear_doc_fields(self):
		# clear fields
		self.TBOX_doc_date.SetValue(_('please fill in'))
		self.TBOX_desc_short.SetValue(_('please fill in'))
		self.additionCommentBox.SetValue(_('please fill in'))
		self.SelBOX_doc_type.SetSelection(-1)
		self.LBOX_doc_pages.Clear()
	#----------------------------------------
	def __load_doc(self):
		# make sure to get the first line only :-)
		curr_doc_id = self.doc_id_wheel.GetLineText(0)

		# has the user supplied anything ?
		if curr_doc_id == '':
			_log.Log(gmLog.lErr, 'No document ID typed in yet !')
			dlg = wxMessageDialog(
				self,
				_('You must type in a document ID !\n\nUsually you will find the document ID written on\nthe physical sheet of paper. There should be only one\nper document even if there are multiple pages.'),
				_('missing document ID'),
				wxOK | wxICON_EXCLAMATION
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		# well, so load the document from that directory
		work_dir = os.path.join(self.repository, curr_doc_id)
		_log.Log(gmLog.lData, 'working in [%s]' % work_dir)

		# check for metadata file
		fname = os.path.join(work_dir, self.desc_file_name)
		if not os.path.exists (fname):
			_log.Log(gmLog.lErr, 'Cannot access metadata file [%s].' % fname)
			dlg = wxMessageDialog(self, 
				_('Cannot access metadata file\n[%s].\nPlease see error log for details.' % fname),
				_('Error'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		# actually get pages
		self.myDoc = cDocument()
		if not self.myDoc.LoadImgListFromXML(fname , work_dir):
			_log.Log(gmLog.lErr, 'Cannot load image list from metadata file [%s].' % fname)
			dlg = wxMessageDialog(self, 
				_('Cannot load image list from metadata file [%s].\nPlease see error log for details.' % fname),
				_('Error'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		return 1
	#----------------------------------------
	def __fill_doc_fields():
		self.__clear_doc_fields()
		pageLst = self.myDoc.getMetaData()['objects']
		for page_num, fname in pageLst.items():
			self.LBOX_doc_pages.Append(_('page %s') % page_num, {'number': page_num, 'file': fname})
	#----------------------------------------
	def OnShowpicbuttonButton(self, event):
		self.BefValue=self.doc_id_wheel.GetLineText(0)
		current_selection=self.LBOX_doc_pages.GetSelection()
		if not current_selection == -1:
			pic_selection=current_selection+1
			self.selected_pic=self.LBOX_doc_pages.GetString(current_selection)
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
		current_selection=self.LBOX_doc_pages.GetSelection()
		self.BefValue=self.doc_id_wheel.GetLineText(0)
		if current_selection == -1:
			dlg = wxMessageDialog(self, _('You did not select a page'),_('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()
			
		else:
			self.selected_pic=self.LBOX_doc_pages.GetString(current_selection)
			#print self.doc_pages
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
			#print self.doc_pages
			for i in range(i,len(self.doc_pages)-1):
				try:
					os.rename(__cfg__.get("source", "repositories") + self.BefValue + '/' + self.LBOX_doc_pages.GetString(i+1) + '.jpg',__cfg__.get("source", "repositories") + self.BefValue + '/' + self.LBOX_doc_pages.GetString(i) + '.jpg')
				except OSError:
					_log.Log (gmLog.lErr, "I was unable to rename the file " + __cfg__.get("source", "repositories") + self.BefValue + '/' + self.LBOX_doc_pages.GetString(i+1) + '.jpg' + " from disk because it simply was not there ")
				print "I renamed" +str(__cfg__.get("source", "repositories") + self.BefValue + '/' + self.LBOX_doc_pages.GetString(i+1) + '.jpg') + "into" + str(__cfg__.get("source", "repositories") + self.BefValue + '/' + self.LBOX_doc_pages.GetString(i) + '.jpg')
			
			#print "u want to del:" + self.selected_pic
			self.LBOX_doc_pages.Delete(current_selection)
			self.doc_pages.remove(self.selected_pic + '.jpg')
			#rebuild list to clean the gap
			i = 0
			for i in range(len(self.doc_pages)):
				if i == 0:
					self.doc_pages = []
					self.LBOX_doc_pages = wxListBox(choices = [], id = wxID_INDEXFRAMELBOXPAGES, name = 'LBOX_doc_pages', parent = self.PNL_main, pos = wxPoint(48, 288), size = wxSize(182, 94), style = 0, validator = wxDefaultValidator)
				self.UpdatePicList()        

	def OnSavebuttonButton(self, event):
		event.Skip()
		# check whether values for date of record, record type, short comment and extended comment
		# have been filled in
		date=self.TBOX_doc_date.GetLineText(0)
		datechecklist = string.split(date,'-')
		shortDescription=self.TBOX_desc_short.GetLineText(0)
		DescriptionChoice=self.SelBOX_doc_type.GetSelection()
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
			in_file = open(__cfg__.get("source", "repositories") + self.BefValue + '/' + self.desc_file_name,"r")
			xml_content = in_file.read()
			in_file.close()
			#del old self.desc_file_name
			os.remove(__cfg__.get("source", "repositories") + self.BefValue + '/' + self.desc_file_name)
			# create xml file
			out_file = open(__cfg__.get("source", "repositories") + self.BefValue + '/' + self.desc_file_name,"w")
			tmpdir_content = self.doc_pages
			runs = len(tmpdir_content)
			x=0
			out_file.write ("<" + __cfg__.get("metadata", "document_tag")    + ">\n")
			out_file.write ("<" + __cfg__.get("metadata", "name_tag")        + ">" + self.Nachname           + "</" + __cfg__.get("metadata", "name_tag")      + ">\n")
			out_file.write ("<" + __cfg__.get("metadata", "firstname_tag")   + ">" + self.Vorname            + "</" + __cfg__.get("metadata", "firstname_tag") + ">\n")
			out_file.write ("<" + __cfg__.get("metadata", "birth_tag")       + ">" + self.queryGeburtsdatum  + "</" + __cfg__.get("metadata", "birth_tag")     + ">\n" )
			out_file.write ("<" + __cfg__.get("metadata", "date_tag")        + ">" + self.TBOX_doc_date.GetLineText(0) + "</" + __cfg__.get("metadata", "date_tag") + ">\n" )
			out_file.write ("<" + __cfg__.get("metadata", "type_tag")        + ">" + self.SelBOX_doc_type.GetStringSelection() + "</" + __cfg__.get("metadata", "type_tag") + ">\n")
			out_file.write ("<" + __cfg__.get("metadata", "comment_tag")     + ">" + self.TBOX_desc_short.GetLineText(0) + "</" + __cfg__.get("metadata", "comment_tag") + ">\n")
			out_file.write ("<" + __cfg__.get("metadata", "add_comment_tag") + ">" + self.additionCommentBox.GetValue() + "</" + __cfg__.get("metadata", "add_comment_tag") + ">\n")
			out_file.write ("<" + __cfg__.get("metadata", "ref_tag")         + ">" + self.Obj_Referenz_value + "</" + __cfg__.get("metadata", "ref_tag") + ">\n")
			while x < runs:
				out_file.write ("<image>" + tmpdir_content[x] + "</image>\n")
				x=x+1
			out_file.write ("</" + __cfg__.get("metadata", "document_tag") + ">")
			out_file.close()
			# copy XDT-file ( not the XML-file ) into self.repository directory
			pat_file = __cfg__.get("metadata", "patient")
			shutil.copy(os.path.expanduser(os.path.join(__cfg__.get("metadata", "location"), pat_file)),__cfg__.get("source", "repositories") + self.BefValue + '/')
			# generate a file to tell import script that we are done here
			out_file = open(__cfg__.get("source", "repositories") + self.BefValue + '/' + self.can_index_file,"w")
			#refresh everything
			self.Vorname = ''
			self.Nachname = ''
			self.Geburtsdatum = ''
			self.__clear_doc_data()
			# empty doc_id_wheel as well
			self.doc_id_wheel.Clear()
			# items for phraseWheel
			self.initgmPhraseWheel()
#======================================================
class IndexerApp(wxApp):
	def OnInit(self):
		wxInitAllImageHandlers()
		self.main = create(None)
		#workaround for running in wxProcess
		#self.main.Show();self.main.Hide();self.main.Show()
		self.main.Centre(wxBOTH)
		self.main.Show(true)
		self.SetTopWindow(self.main)
		return true
#------------------------------------------------------
def main():
	application = IndexerApp(0)
	application.MainLoop()
#======================================================
# main
#------------------------------------------------------
if __name__ == '__main__':
	main()

# this line is a replacement for gmPhraseWhell just in case it doesn't work 
#self.doc_id_wheel = wxTextCtrl(id = wxID_INDEXFRAMEBEFNRBOX, name = 'textCtrl1', parent = self.PNL_main, pos = wxPoint(48, 112), size = wxSize(176, 22), style = 0, value = _('document#'))

#				try:
#					#read self.desc_file_name
#					desc_filee = 
#					xml_content = desc_filee.read()
#					desc_filee.close()
#
#					xml_contentlist = string.split(xml_content,'\n')
#					runs=len(xml_contentlist)
#					x=0
#					while x < runs:
#						value = xml_contentlist[x]
#						_log.Log (gmLog.lInfo, "teste " + value)
#						try :
#							# find all occurences of <image>
#							string.index(value,'<image>')
#							stripped_value = value[7:-8]
#							# append occurence to list in gui
#							if os.name == 'posix':
#								self.LBOX_doc_pages.Append(string.replace(stripped_value,'.jpg',''))
#							else:
#								self.LBOX_doc_pages.Append(string.replace(stripped_value,'.bmp',''))
#							self.doc_pages.append(stripped_value)
#							_log.Log (gmLog.lInfo, "added" + stripped_value + "to GUI-list")
#							# increase and start over with next line
#							x=x+1
#						except ValueError:
#							x=x+1
#					x=0
#					while x < runs:
#						value = xml_contentlist[x]
#						_log.Log (gmLog.lInfo, "once again" + value)
#						try :
#							# find all occurences of <ref_tag>
#							string.index(value,'<'+__cfg__.get("metadata", "ref_tag")+'>')
#							_log.Log (gmLog.lInfo, "tested" + value + "for string : " + __cfg__.get("metadata", "ref_tag"))
#							self.Obj_Referenz_value = value[int(len(__cfg__.get("metadata", "ref_tag")))+2:-(int(len(__cfg__.get("metadata", "ref_tag")))+3)]
#							x=x+1
#						except ValueError:
#							x=x+1
#
#					# has there been a prior index session with this data ?
#					if os.path.isfile(__cfg__.get("source", "repositories") + curr_doc_id + '/' + self.can_index_file):
#						x=0
#						while x < runs:
#							value = xml_contentlist[x]
#							_log.Log (gmLog.lInfo, "once again" + value)
#							try :
#								# find all occurences of <date_tag>
#								string.index(value,'<'+__cfg__.get("metadata", "date_tag")+'>')
#								_log.Log (gmLog.lInfo, "tested" + value + "for string : " + __cfg__.get("metadata", "date_tag"))
#								self.Obj_Datum_value = value[int(len(__cfg__.get("metadata", "date_tag")))+2:-(int(len(__cfg__.get("metadata", "date_tag")))+3)]
#								x=x+1
#							except ValueError:
#								x=x+1
#						x=0
#						while x < runs:
#							value = xml_contentlist[x]
#							_log.Log (gmLog.lInfo, "test again" + value)
#							try :
#								# find all occurences of <type_tag>
#								string.index(value,'<'+__cfg__.get("metadata", "type_tag")+'>')
#								_log.Log (gmLog.lInfo, "tested" + value + "for string : " + __cfg__.get("metadata", "type_tag"))
#								self.Obj_Typ_value = value[int(len(__cfg__.get("metadata", "type_tag")))+2:-(int(len(__cfg__.get("metadata", "type_tag")))+3)]
#								x=x+1
#							except ValueError:
#								x=x+1
#						x=0
#						while x < runs:
#							value = xml_contentlist[x]
#							_log.Log (gmLog.lInfo, "test again" + value)
#							try :
#								# find all occurences of <comment_tag>
#								string.index(value,'<'+__cfg__.get("metadata", "comment_tag")+'>')
#								_log.Log (gmLog.lInfo, "tested" + value + "for string : " + __cfg__.get("metadata", "comment_tag"))
#								self.Obj_Name_value = value[int(len(__cfg__.get("metadata", "comment_tag")))+2:-(int(len(__cfg__.get("metadata", "comment_tag")))+3)]
#								x=x+1
#							except ValueError:
#								x=x+1
#						x=0
#						while x < runs:
#							value = xml_contentlist[x]
#							_log.Log (gmLog.lInfo, "test again" + value)
#							try :
#							   # find all occurences of <add_comment_tag>
#								string.index(value,'<'+__cfg__.get("metadata", "add_comment_tag")+'>')
#								_log.Log (gmLog.lInfo, "tested" + value + "for string : " + __cfg__.get("metadata", "add_comment_tag"))
#								self.Obj_Beschreibung_value = value[int(len(__cfg__.get("metadata", "add_comment_tag")))+2:-(int(len(__cfg__.get("metadata", "add_comment_tag")))+3)]
#								x=x+1
#							except ValueError:
#								x=x+1
#					else :
#						return
#					
#			else:
#				dlg = wxMessageDialog(self, _('Could not fine any documents relating to this document#'),_('Attention'), wxOK | wxICON_INFORMATION)
#				try:
#					dlg.ShowModal()
#				finally:
#					dlg.Destroy()


	#----------------------------------------
#	def UpdatePicList(self):
#		if len(self.doc_pages) == 0:
#			self.LBOX_doc_pages.Append(_('page')+'1')
#			self.doc_pages.append(_('page')+'1')
#		else:
#			lastPageInList=self.doc_pages[len(self.doc_pages)-1]
#			biggest_number_strg=lastPageInList.replace(_('page'),'')
#			biggest_number= int(biggest_number_strg) + 1
#			self.LBOX_doc_pages.Append(_('page') + `biggest_number`)
#			self.doc_pages.append(_('page') + `biggest_number`)
	#--------------------------------
#	def updateGUIonLoadRecords(self):
#		self.TBOX_dob.AppendText(self.Geburtsdatum)
#		#if not self.Obj_Datum_value == _('please fill in'):
#		self.TBOX_doc_date.AppendText(self.Obj_Datum_value)
#		#if not self.Obj_Name_value == _('please fill in'):
#		self.TBOX_desc_short.AppendText(self.Obj_Name_value)
#		#if not self.Obj_Typ_value =='':
#		index = self.SelBOX_doc_type.FindString(self.Obj_Typ_value)
#		self.SelBOX_doc_type.SetSelection(index)
#		#if not self.Obj_Beschreibung_value =='':
#		self.additionCommentBox.AppendText(self.Obj_Beschreibung_value)
