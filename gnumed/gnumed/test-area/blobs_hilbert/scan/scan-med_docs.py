#!/usr/bin/env python

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/blobs_hilbert/scan/Attic/scan-med_docs.py,v $
__version__ = "$Revision: 1.2 $"


from wxPython.wx import *
import Image,string,time,shutil,os,sys,gettext
import locale

# location of our modules
sys.path.append(os.path.join('.', 'modules'))

import gmLog,gmCfg,gmI18N
try:
	import twain 
	scan_drv = 'wintwain'
except ImportError:
	import sane 
	scan_drv = 'linsane'
#-------------------------------------------------
__author__ = "Sebastian Hilbert <Sebastian.Hilbert@gmx.net>"
_log = gmLog.gmDefLog
_cfg = gmCfg.gmDefCfg


def create(parent):
	return scanFrame(parent)

[wxID_SCANFRAME, wxID_SCANFRAMECHANGEPOS, wxID_SCANFRAMEDELPICBUTTON, wxID_SCANFRAMELISTBOX1, wxID_SCANFRAMESAVEBUTTON, wxID_SCANFRAMESCANBUTTON, wxID_SCANFRAMESCANWINDOW, wxID_SCANFRAMESHOWPICBUTTON, wxID_SCANFRAMESTATICTEXT1, wxID_SCANFRAMESTATICTEXT2, wxID_SCANFRAMESTATICTEXT3] = map(lambda _init_ctrls: wxNewId(), range(11))

#--------------------------------------------------
class scanFrame(wxFrame):
#-------------------------------------------------

	tmpfilename="tmp.jpg"
	wxInitAllImageHandlers()
	picList = []
	page = 0
	selected_pic = ''
	myCfg = None
	
	#------------------------------------------
	def read_ini_file(self):
		# ini file given on command line ?
		if len(sys.argv) > 1:
			cfgName = sys.argv[1]
			# file missing
			if not os.path.exists(cfgName):
				__log__.Log(gmLog.lErr, "INI file %s (given on command line) not found." % cfgName)
				__log__.Log(gmLog.lPanic, "Cannot run without configuration file. Aborting.")
				sys.exit()
		# else look for ~/.gnumed/base_name.ini or ./base_name.ini
		else:
			# get base name from name of script
			base_name = os.path.splitext(os.path.basename(sys.argv[0]))[0] + ".ini"
			# first look in user's home
			cfgName = os.path.expanduser(os.path.join("~/.gnumed", base_name))
			# not there
			if not os.path.exists(cfgName):
				__log__.Log(gmLog.lWarn, "INI file %s not found." % cfgName)
				# look in directory of script (useful for Windows/DOS, mainly)
				cfgName = os.path.join(os.path.split(sys.argv[0])[0], base_name)
				if not os.path.exists(cfgName):
					__log__.Log(gmLog.lErr, "INI file %s not found." % cfgName)
					__log__.Log(gmLog.lPanic, "Cannot run without configuration file. Aborting.")
					sys.exit()
	
		# if we got here we have a valid file name
		__log__.Log(gmLog.lInfo, "config file: " +	cfgName)
		aCfg = ConfigParser.ConfigParser()
		aCfg.read(cfgName)
		return aCfg
	
	#-----------------------------------------------------------------------
	def show_pic(self,bild):
		try:
			bild=Image.open(bild)
			bild.show()
			return true
		except IOError:
			__log__.Log(gmLog.lErr, _("I am afraid but there is no such page or it could not be opened !"))
			dlg = wxMessageDialog(self, _('I am afraid but there is no such page or it could not be opened !'),_('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()
	
	#---------------------------------------------------------------
	#twain scan code
	def OpenScanner(self):
		if not self.SM:
			self.SM = twain.SourceManager(self.GetHandle())
			if not self.SM:
				return
		self.SM.SetCallback(self.OnTwainEvent)
		self.SD = self.SM.OpenSource()
		
	def Acquire(self):
		if not self.SD:
			self.OpenScanner()
			if not self.SD: return
		self.SD.RequestAcquire()
		
	def ProcessXFer(self):
		(handle, more_to_come) = self.SD.XferImageNatively()
		twain.DIBToBMFile(handle, self.tmpfilename)
		twain.GlobalHandleFree(handle)
		self.SD.HideUI()
		#save image-file to disk
		self.savePage(null)
		#update List of pages in GUI
		self.UpdatePicList()
		
	def OnTwainEvent(self, event):
		try:	  
			self.ProcessXFer()
		except:	   
			print _('I am afraid I was unable to get the image from the scanner')
			pass
	#----------------------------------------------------------------
	def savePage(self,im):
		if len(self.picList) != 0:
			lastPageInList=self.picList[len(self.picList)-1]
			biggest_number_strg=lastPageInList.replace(_('page'),'')
			biggest_number= int(biggest_number_strg) + 1
		# twain specific
		if scan_drv == 'wintwain':
			if len(self.picList) == 0:
				shutil.copy(self.tmpfilename,self.myCfg.get("tmpdir", "tmpdir") + _('page')+str(1)+'.bmp')
			else:
				shutil.copy(self.tmpfilename,self.myCfg.get("tmpdir", "tmpdir") + _('page') + `biggest_number` +'.bmp')
		# SANE way of life # Write the image out as a JPG file
		# Note : file format is determined by extension ; otherwise specify type
		else:
			if len(self.picList) == 0:
				im.save(self.myCfg.get("tmpdir", "tmpdir") + _('page')+str(1)+'.jpg')
				print "I just saved page 1"
				# remove when sane works one day
				return
			else:
				im.save(self.myCfg.get("tmpdir", "tmpdir") + _('page') + `biggest_number` +'.jpg')
				print "I just saved" + str(self.myCfg.get("tmpdir", "tmpdir") + _('page') + `biggest_number` +'.jpg')
	
	#-----------------------------------------------------------------
	def UpdatePicList(self):
		if len(self.picList) == 0:
			self.listBox1.Append(_('page1'))
			self.picList.append(_('page1'))
			
		else:
			lastPageInList=self.picList[len(self.picList)-1]
			biggest_number_strg=lastPageInList.replace(_('page'),'')
			biggest_number= int(biggest_number_strg) + 1
			self.listBox1.Append(_('page') + `biggest_number`)
			self.picList.append(_('page') + `biggest_number`)
			
	#-------------------------------------------------------------------
	def ScanWithSane(self):
		gmLog.gmDefLog.Log(gmLog.lInfo, "I use sane ")
		# tell App what scanner to use
		# fixme : might not work if more than one scanner available
		print 'SANE version:' , sane.init()
		available_scanner = sane.get_devices()
		# replace != by == when real scanner is available
		if sane.get_devices() == []:
			__log__.Log (gmLog.lErr, "sane did not find any scanner")
			dlg = wxMessageDialog(self, _('There is no scanner available'),_('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()
		else:	  
			#print 'SANE version:' , sane.init()
			print 'Available devices=', sane.get_devices() 
			#open scanner and get parameters
			scanner = sane.open(available_scanner[0][0])
			#tell me what parameters are supported
			print 'SaneDev object=', scanner
			print 'Device parameters:', scanner.get_parameters()
			#print 'Device parameters:', scanner.optlist
			# Set scan parameters
			# fixme : get those from config file
			#scanner.contrast=170 ; scanner.brightness=150 ; scanner.white_level=190
			#scanner.depth=6
			scanner.br_x=412.0 ; scanner.br_y=583.0
			# Initiate the scan
			scanner.start()
			# Get an Image object 
			im=scanner.snap()
			#save image-file to disk
			self.savePage(im)
			#update List of pages in GUI
			self.UpdatePicList()
			
	
	def _init_utils(self):
		pass

	def _init_ctrls(self, prnt):
		wxFrame.__init__(self, id = wxID_SCANFRAME, name = '', parent = prnt, pos = wxPoint(275, 184), size = wxSize(631, 473), style = wxDEFAULT_FRAME_STYLE, title = 'Befunde scannen')
		self._init_utils()
		self.SetClientSize(wxSize(631, 473))

		self.scanWindow = wxWindow(id = wxID_SCANFRAMESCANWINDOW, name = 'scanWindow', parent = self, pos = wxPoint(0, 0), size = wxSize(631, 473), style = 0)

		self.scanButton = wxButton(id = wxID_SCANFRAMESCANBUTTON, label = _('scan page'), name = 'scanButton', parent = self.scanWindow, pos = wxPoint(56, 80), size = wxSize(240, 64), style = 0)
		self.scanButton.SetToolTipString(_('scan a page'))
		EVT_BUTTON(self.scanButton, wxID_SCANFRAMESCANBUTTON, self.OnScanbuttonButton)

		self.saveButton = wxButton(id = wxID_SCANFRAMESAVEBUTTON, label = _('save document'), name = 'saveButton', parent = self.scanWindow, pos = wxPoint(408, 80), size = wxSize(152, 344), style = 0)
		EVT_BUTTON(self.saveButton, wxID_SCANFRAMESAVEBUTTON, self.OnSavebuttonButton)

		self.listBox1 = wxListBox(choices = [], id = wxID_SCANFRAMELISTBOX1, name = 'listBox1', parent = self.scanWindow, pos = wxPoint(56, 184), size = wxSize(240, 160), style = 0, validator = wxDefaultValidator)

		self.showPicButton = wxButton(id = wxID_SCANFRAMESHOWPICBUTTON, label = _('show'), name = 'showPicButton', parent = self.scanWindow, pos = wxPoint(64, 384), size = wxSize(80, 22), style = 0)
		self.showPicButton.SetToolTipString(_('show page'))
		EVT_BUTTON(self.showPicButton, wxID_SCANFRAMESHOWPICBUTTON, self.OnShowpicbuttonButton)

		self.delPicButton = wxButton(id = wxID_SCANFRAMEDELPICBUTTON, label = _('delete'), name = 'delPicButton', parent = self.scanWindow, pos = wxPoint(200, 384), size = wxSize(80, 22), style = 0)
		self.delPicButton.SetToolTipString(_('delete page'))
		EVT_BUTTON(self.delPicButton, wxID_SCANFRAMEDELPICBUTTON, self.OnDelpicbuttonButton)

		self.changePos = wxButton(id = wxID_SCANFRAMECHANGEPOS, label = _('change current Position'), name = 'changePos', parent = self.scanWindow, pos = wxPoint(104, 432), size = wxSize(144, 22), style = 0)
		EVT_BUTTON(self.changePos, wxID_SCANFRAMECHANGEPOS, self.OnChangeposButton)

		self.staticText1 = wxStaticText(id = wxID_SCANFRAMESTATICTEXT1, label = _('document pages'), name = 'staticText1', parent = self.scanWindow, pos = wxPoint(56, 160), size = wxSize(152, 16), style = 0)

		self.staticText2 = wxStaticText(id = wxID_SCANFRAMESTATICTEXT2, label = '1.', name = 'staticText2', parent = self.scanWindow, pos = wxPoint(56, 32), size = wxSize(19, 29), style = 0)
		self.staticText2.SetFont(wxFont(25, wxSWISS, wxNORMAL, wxNORMAL, false, ''))

		self.staticText3 = wxStaticText(id = wxID_SCANFRAMESTATICTEXT3, label = '2.', name = 'staticText3', parent = self.scanWindow, pos = wxPoint(408, 32), size = wxSize(19, 29), style = 0)
		self.staticText3.SetFont(wxFont(25, wxSWISS, wxNORMAL, wxNORMAL, false, ''))

	def __init__(self, parent):
		# get configuration
		self.myCfg = gmCfg.read_conf_file()
		self._init_ctrls(parent)
		# refresh
		shutil.rmtree(self.myCfg.get("tmpdir", "tmpdir"), true)
		os.mkdir(self.myCfg.get("tmpdir", "tmpdir"))
		(self.SM, self.SD) = (None, None)
		
	def OnScanbuttonButton(self, event):
		if scan_drv == 'wintwain':
			gmLog.gmDefLog.Log(gmLog.lInfo, "I use twain ")
			self.Acquire()
		else :
			self.ScanWithSane()
			gmLog.gmDefLog.Log(gmLog.lInfo, "I use SANE ")
		
	def OnShowpicbuttonButton(self, event):
		current_selection=self.listBox1.GetSelection()
		if not current_selection == -1:
			pic_selection=current_selection+1
			self.selected_pic=self.listBox1.GetString(current_selection)
			#for debugging only
			print "I show u:" + self.selected_pic
			if scan_drv == 'wintwain':
				self.show_pic(self.myCfg.get("tmpdir", "tmpdir") + self.selected_pic + '.bmp') 
			else:
				self.show_pic(self.myCfg.get("tmpdir", "tmpdir") + self.selected_pic + '.jpg') 
		else:
			dlg = wxMessageDialog(self, _('You did not select a page'),_('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()
				
	def OnDelpicbuttonButton(self, event):
		current_selection=self.listBox1.GetSelection()
		if current_selection == -1:
			dlg = wxMessageDialog(self, _('You did not select a page'),_('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()
		else:
			self.selected_pic=self.listBox1.GetString(current_selection)
			#del page from hdd												 
			if scan_drv == 'wintwain':
				try:
					os.remove(self.myCfg.get("tmpdir", "tmpdir") + self.selected_pic + '.bmp')
				except OSError:
					__log__.Log (gmLog.lErr, "I was unable to wipe the file " + self.myCfg.get("tmpdir", "tmpdir") + self.selected_pic + '.bmp' + " from disk because it simply was not there ")
			else:
				try:
					os.remove(self.myCfg.get("tmpdir", "tmpdir") + self.selected_pic + '.jpg')
				except OSError:
					__log__.Log (gmLog.lErr, "I was unable to wipe the file " + self.myCfg.get("tmpdir", "tmpdir") + self.selected_pic + '.jpg' + " from disk because it simply was not there ")
			#now rename (decrease index by 1) all pages above the deleted one
			i = current_selection
			#print self.picList												 
			for i in range(i,len(self.picList)-1):
				if scan_drv == 'wintwain':
					try:
						os.rename(self.myCfg.get("tmpdir", "tmpdir") + self.listBox1.GetString(i+1)+ '.bmp',self.myCfg.get("tmpdir", "tmpdir") + self.listBox1.GetString(i) + '.bmp')
					except OSError:
						__log__.Log (gmLog.lErr, "I was unable to rename the file " + self.myCfg.get("tmpdir", "tmpdir") + self.listBox1.GetString(i+1) + '.bmp' + " from disk because it simply was not there ")
				else:
					try:
						os.rename(self.myCfg.get("tmpdir", "tmpdir") + self.listBox1.GetString(i+1)+ '.jpg',self.myCfg.get("tmpdir", "tmpdir") + self.listBox1.GetString(i) + '.jpg')
					except OSError:
						__log__.Log (gmLog.lErr, "I was unable to rename the file " + self.myCfg.get("tmpdir", "tmpdir") + self.listBox1.GetString(i+1) + '.jpg' + " from disk because it simply was not there ")
				#print "I renamed" +str(self.myCfg.get("tmpdir", "tmpdir") + self.listBox1.GetString(i+1) + '.jpg') + "into" + str(self.myCfg.get("tmpdir", "tmpdir") + self.listBox1.GetString(i) + '.jpg')
			self.listBox1.Delete(current_selection)
			self.picList.remove(self.selected_pic)
			#rebuild list to clean the gap
			i = 0
			for i in range(len(self.picList)):
				if i == 0:
					self.picList = []
					self.listBox1 = wxListBox(choices = [], id = wxID_SCANFRAMELISTBOX1, name = 'listBox1', parent = self.scanWindow, pos = wxPoint(56, 184), size = wxSize(240, 160), style = 0, validator = wxDefaultValidator)
				self.UpdatePicList()	
	
	def OnSavebuttonButton(self, event):
		if self.picList != []:
			# create xml file
			out_file = open(self.myCfg.get("tmpdir", "tmpdir") + self.myCfg.get("metadata", "description"),"w")
			tmpdir_content = self.picList
			runs = len(tmpdir_content)
			x=0
			savedir = time.strftime("%a%d%b%Y%H%M%S", time.localtime())
			# here come the contents of the xml-file
			out_file.write ("<" + self.myCfg.get("metadata", "document_tag")+">\n")
			out_file.write ("<" + self.myCfg.get("metadata", "ref_tag") + ">" + savedir + "</" + self.myCfg.get("metadata", "ref_tag") + ">\n")
			while x < runs:
				out_file.write ("<image>" + tmpdir_content[x] + ".jpg" + "</image>\n")
				x=x+1
			out_file.write ("</" + self.myCfg.get("metadata", "document_tag")+">\n")
			out_file.close()
			# move files around
			shutil.copytree(self.myCfg.get("tmpdir", "tmpdir"),self.myCfg.get("source", "repositories") + savedir)
			# generate a file to tell import script that we are done here
			out_file = open(__cfg__.get("source", "repositories") + savedir + '/' + __cfg__.get("metadata", "checkpoint"),"w")
			# refresh
			shutil.rmtree(self.myCfg.get("tmpdir", "tmpdir"), true)
			os.mkdir(self.myCfg.get("tmpdir", "tmpdir"))
			self.picList = []	
			self.listBox1 = wxListBox(choices = [], id = wxID_SCANFRAMELISTBOX1, name = 'listBox1', parent = self.scanWindow, pos = wxPoint(56, 184), size = wxSize(240, 160), style = 0, validator = wxDefaultValidator)
			dlg = wxMessageDialog(self, _('please put down') + savedir + _('on paper copy for reference'),_('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()
		else:
			dlg = wxMessageDialog(self, _('There is nothing to save on disk ? Please aquire images frst'),_('Attention'), wxOK | wxICON_INFORMATION)
			try:
				dlg.ShowModal()
			finally:
				dlg.Destroy()
	
	def OnChangeposButton(self, event):
		pass
		##current_selection=self.listBox1.GetSelection()
		##if not current_selection == -1:
		##	  self.selected_pic=self.listBox1.GetString(current_selection)
			#picTochange
		##	  print "u want to change pos for :" + self.selected_pic
		##	 dlg = wxTextEntryDialog(self, _('please tell me the desired position for the page - string format : page[x]'),_('alter page position'), _('page'))
		##	  try:
		##		  if dlg.ShowModal() == wxID_OK:
		##			  answer = dlg.GetValue()
		##			  # Your code
		##			  print 'hello'
		##	  finally:
		##		  dlg.Destroy()
		##	  #first rename selected
		##	  tempposition=len(self.picList)+1	  
		##	  self.listBox1.Delete(current_selection)
		##	  self.picList.remove(self.selected_pic)
		##	  print self.picList
		##	  #del page from hdd
		
		##else:
		##	  dlg = wxMessageDialog(self, _('You did not select a page'),_('Attention'), wxOK | wxICON_INFORMATION)
		##	  try:
		##		  dlg.ShowModal()
		##	  finally:
		##		  dlg.Destroy()

from wxPython.wx import *
import scanFrame

modules ={'scanFrame': [0, '', 'scanFrame.py']}

class BoaApp(wxApp):
	def OnInit(self):
		wxInitAllImageHandlers()
		self.main = scanFrame.create(None)
		#workaround for running in wxProcess
		self.main.Show();self.main.Hide();self.main.Show() 
		self.SetTopWindow(self.main)
		return true

def main():
	application = BoaApp(0)
	application.MainLoop()

if __name__ == '__main__':
	main()
	