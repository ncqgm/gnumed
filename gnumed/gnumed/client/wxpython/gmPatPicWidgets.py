#--------------------------------
#embryonic gmGP_PatientPicture.py
#=====================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmPatPicWidgets.py,v $
# $Id: gmPatPicWidgets.py,v 1.1 2004-08-18 10:15:26 ncq Exp $
__version__ = "$Revision: 1.1 $"
__author__  = "R.Terry <rterry@gnumed.net>,\
			   I.Haywood <i.haywood@ugrad.unimelb.edu.au>,\
			   K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

# standard lib
import sys, os

# 3rd party
from wxPython.wx import *
from wxPython.lib.imagebrowser import *
import mx.DateTime as mxDT

# GnuMed
from Gnumed.pycommon import gmDispatcher, gmSignals, gmGuiBroker,gmLog
from Gnumed.business import gmMedDoc
from Gnumed.wxpython import gmGuiHelpers

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

ID_PUP_AquirePhoto = wxNewId()
ID_PUP_ImportPhoto = wxNewId()
ID_PUP_ExportPhoto = wxNewId()
ID_PUP_DeletePhoto = wxNewId()

# IMO this current_photo nonsense has to go -kh
current_patient = -1
current_photo = None

#=====================================================================
class cPatientPicture (wxStaticBitmap):
	"""A patient picture control ready for display.
		with popup menu to import/export
		delete or aquire menu items
	"""	
	def __init__(self, parent, id):
		global current_photo
		try:
			self.default_photo = os.path.join(gmGuiBroker.GuiBroker()['gnumed_dir'], 'bitmaps', 'any_body2.png')
			print 'after try', self.default_photo
		except:
			self.default_photo = "../bitmaps/any_body2.png"
		print 'default photo is', self.default_photo
		# just in case
		wxImage_AddHandler(wxPNGHandler())
		wxImage_AddHandler(wxJPEGHandler ())
		if not current_photo:
			print 'setting current photo'
			current_photo = self.default_photo
		img_data = wxImage(current_photo, wxBITMAP_TYPE_ANY)
		bmp_data = wxBitmapFromImage(img_data)
		del img_data
		self.desired_width = bmp_data.GetWidth ()
		self.desired_height = bmp_data.GetHeight ()

		wxStaticBitmap.__init__(
			self,
			parent,
			id,
			bmp_data,
			wxPoint(0, 0),
			wxSize(self.desired_width, self.desired_height)
		)

		self.__register_events()
	#-----------------------------------------------------------------
	# event handling
	#-----------------------------------------------------------------
	def __register_events(self):
		# wxPython events
		EVT_RIGHT_UP(self, self._on_RightClick_photo)
		EVT_MENU(self, ID_PUP_AquirePhoto, self._on_AquirePhoto)
		EVT_MENU(self, ID_PUP_ImportPhoto, self._on_ImportPhoto)
		EVT_MENU(self, ID_PUP_ExportPhoto, self._on_ExportPhoto)
		EVT_MENU(self, ID_PUP_DeletePhoto, self._on_DeletePhoto)

		# dispatcher signals
		gmDispatcher.connect(receiver=self._on_patient_selected, signal=gmSignals.patient_selected())
	#-----------------------------------------------------------------
	def _on_RightClick_photo(self, event):
		menu_patientphoto = wxMenu()
		menu_patientphoto.Append(ID_PUP_AquirePhoto, _("Aquire from imaging device"))
		menu_patientphoto.Append(ID_PUP_ImportPhoto, _("Import from file"))
		menu_patientphoto.Append(ID_PUP_ExportPhoto, _("Export to file"))
		menu_patientphoto.Append(ID_PUP_DeletePhoto, "Delete Photo - not sure what this means ?")
		self.PopupMenu(menu_patientphoto, event.GetPosition())
		menu_patientphoto.Destroy()
	#-----------------------------------------------------------------
	def _on_ImportPhoto(self,event):
		"""Import an existing photo."""
		imp_dlg = ImageDialog(self,os.getcwd())
    		imp_dlg.Centre()
		try:
			if imp_dlg.ShowModal() == wxID_OK:
				importedphoto= imp_dlg.GetFile()
				print "You Selected File: " + importedphoto       # show the selected file
# 				photo = dialogue.GetPath ()
 				self.setPhoto(self,photo)

# 				#self.patientpicture.setPhoto (photo)
# 				self.default_photo = photo
# 				doc = gmMedDoc.create_document (self.patient.get_ID ())
# 				doc.update_metadata({'type ID':gmMedDoc.MUGSHOT})
# 				obj = gmMedDoc.create_object (doc)
# 				obj.update_data_from_file (photo)
			else:
				print "No file selected"
		except:
			_log.LogException ('failed to import photo', sys.exc_info (), verbose= 0)
	#-----------------------------------------------------------------
	def _on_ExportPhoto(self,event):
		exp_dlg = wxFileDialog (self, style=wxSAVE)
		if exp_dlg.ShowModal () == wxID_OK:
			shutil.copyfile (self.getPhoto(), exp_dlg.GetPath())
	#-----------------------------------------------------------------
	def _on_AquirePhoto(self,event):
		gmGuiHelpers.gm_show_info (
			_('This feature is not implemented yet.'),
			_('acquire patient photograph')
		)
	#-----------------------------------------------------------------
	def _on_DeletePhoto(self,event):
		gmGuiHelpers.gm_show_info (
			_('This feature is not implemented yet.'),
			_('delete patient photograph')
		)
	#-----------------------------------------------------------------
	def _on_patient_selected(self):
		print "updating patient photo, needs to be implemented, async"
	#-----------------------------------------------------------------
	# FIXME: do this async from _on_patient_selected
	def newPatient (self, signal, kwds):
		global current_patient
		global current_photo
		if kwds['ID'] != current_patient: # do't drag photo across net more than once
			current_patient = kwds['ID']
			docs = gmMedDoc.search_for_document (kwds['ID'], gmMedDoc.MUGSHOT)
			# FIXME: "where date = max(select date from ... where l1.pat=l2.pat)" ...
			# FIXME: or rather use v_latest_mugshot VO
			if docs: # get the latest in a series of photographs
				latest_date = mxDT.DateTime (1)
				latest_photo = None
				for i in docs:
					i.get_metadata ()
					if i.metadata['date'] > latest_date:
						latest_photo = i.metadata['objects'].keys ()[0]
				current_photo = gmMedDoc.gmMedObj (latest_photo).export_to_file ()
				if current_photo:
					self.setPhoto (current_photo)
			else:
				if current_photo != self.default_photo:
					current_photo = self.default_photo
					self.setPhoto (current_photo)
		else:
			self.setPhoto (current_photo)
	#-----------------------------------------------------------------
	def setPhoto (self, fname):
		"""
		Manually set the photograph to be photo in file fname
		"""
		img_data = wxImage (fname, wxBITMAP_TYPE_ANY)
		img_data.Rescale(self.desired_width, self.desired_height)
		bmp_data = wxBitmapFromImage(img = img_data)
		del img_data
		self.SetBitmap(bmp_data)
		self.Show(True)
	#-----------------------------------------------------------------
	def getPhoto (self):
		return current_photo

#====================================================
# main
#----------------------------------------------------
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (200, 200))
	app.SetWidget(cPatientPicture, -1)
	app.MainLoop()
#====================================================
# $Log: gmPatPicWidgets.py,v $
# Revision 1.1  2004-08-18 10:15:26  ncq
# - Richard is improving the patient picture
# - added popup menu
# - cleanups
#
# Revision 1.10  2004/06/13 22:31:48  ncq
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
# Revision 1.9  2004/06/01 07:59:55  ncq
# - comments improved
#
# Revision 1.8  2004/05/28 08:57:08  shilbert
# - bugfix for wxBitmapFromImage()
#
# Revision 1.7  2004/03/04 19:46:54  ncq
# - switch to package based import: from Gnumed.foo import bar
#
# Revision 1.6  2004/03/03 23:53:22  ihaywood
# GUI now supports external IDs,
# Demographics GUI now ALPHA (feature-complete w.r.t. version 1.0)
# but happy to consider cosmetic changes
#
# Revision 1.5  2004/03/03 14:53:16  ncq
# - comment on optimizing SQL for getting latest photo
#
# Revision 1.4  2004/03/03 05:24:01  ihaywood
# patient photograph support
#
# Revision 1.3  2003/11/17 10:56:38  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:39  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.2  2003/03/29 13:43:30  ncq
# - make standalone work, CVS keywords, general cleanup
# - change from wxPanel to wxStaticBitmap; load PNG, BMP, GIP automagically
# - alleviate sizer hell
#
