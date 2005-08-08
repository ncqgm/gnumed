"""GnuMed patient picture widget.
"""

#--------------------------------
#embryonic gmGP_PatientPicture.py
#=====================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmPatPicWidgets.py,v $
# $Id: gmPatPicWidgets.py,v 1.9 2005-08-08 08:07:11 ncq Exp $
__version__ = "$Revision: 1.9 $"
__author__  = "R.Terry <rterry@gnumed.net>,\
			   I.Haywood <i.haywood@ugrad.unimelb.edu.au>,\
			   K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

# standard lib
import sys, os, shutil

# 3rd party
from wxPython import wx
from wxPython.lib import imagebrowser
import mx.DateTime as mxDT

# GnuMed
from Gnumed.pycommon import gmDispatcher, gmSignals, gmGuiBroker, gmLog, gmI18N
from Gnumed.business import gmMedDoc, gmPerson
from Gnumed.wxpython import gmGuiHelpers

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

ID_RefreshPhoto = wx.wxNewId()
ID_AcquirePhoto = wx.wxNewId()
ID_ImportPhoto = wx.wxNewId()
ID_ExportPhoto = wx.wxNewId()
ID_RemovePhoto = wx.wxNewId()

#=====================================================================
class cPatientPicture(wx.wxStaticBitmap):
	"""A patient picture control ready for display.
		with popup menu to import/export
		remove or Acquire from a device
	"""
	def __init__(self, parent, id, width=50, height=54):
		self.__fallback_pic_name = os.path.join(gmGuiBroker.GuiBroker()['resource dir'], 'bitmaps', 'empty-face-in-bust.png')
		self.__pat = gmPerson.gmCurrentPatient()
		# just in case
		wx.wxImage_AddHandler(wx.wxPNGHandler())
		wx.wxImage_AddHandler(wx.wxJPEGHandler())
		wx.wxImage_AddHandler(wx.wxGIFHandler())
		# load initial dummy bitmap
		img_data = wx.wxImage(self.__fallback_pic_name, wx.wxBITMAP_TYPE_ANY)
		bmp_data = wx.wxBitmapFromImage(img_data)
		del img_data
		# good default: 50x54
		self.desired_width = width
		self.desired_height = height
		wx.wxStaticBitmap.__init__(
			self,
			parent,
			id,
			bmp_data,
			wx.wxPoint(0, 0),
			wx.wxSize(self.desired_width, self.desired_height)
		)
		# pre-make menu
		self.__photo_menu = wx.wxMenu()
		self.__photo_menu.Append(ID_RefreshPhoto, _('Refresh photo'))
		self.__photo_menu.Append(ID_AcquirePhoto, _("Acquire from imaging device"))
		self.__photo_menu.Append(ID_ImportPhoto, _("Import from file"))
		self.__photo_menu.Append(ID_ExportPhoto, _("Export to file"))
		self.__photo_menu.Append(ID_RemovePhoto, _('Remove Photo'))

		self.__register_events()
	#-----------------------------------------------------------------
	# event handling
	#-----------------------------------------------------------------
	def __register_events(self):
		# wxPython events
		wx.EVT_RIGHT_UP(self, self._on_RightClick_photo)

		wx.EVT_MENU(self, ID_RefreshPhoto, self._on_RefreshPhoto)
		wx.EVT_MENU(self, ID_AcquirePhoto, self._on_AcquirePhoto)
		wx.EVT_MENU(self, ID_ImportPhoto, self._on_ImportPhoto)
		wx.EVT_MENU(self, ID_ExportPhoto, self._on_ExportPhoto)
		wx.EVT_MENU(self, ID_RemovePhoto, self._on_RemovePhoto)

		# dispatcher signals
		gmDispatcher.connect(receiver=self._on_patient_selected, signal=gmSignals.patient_selected())
	#-----------------------------------------------------------------
	def _on_RightClick_photo(self, event):
		if not self.__pat.is_connected():
			gmGuiHelpers.gm_beep_statustext(_('No active patient.'))
			return False
		self.PopupMenu(self.__photo_menu, event.GetPosition())
	#-----------------------------------------------------------------
	def _on_RefreshPhoto(self, event):
		"""(Re)fetch patient picture from DB *now*."""
		doc_folder = self.__pat.get_document_folder()
		photo = doc_folder.get_latest_mugshot()
		if photo is None:
			gmGuiHelpers.gm_beep_statustext(_('Cannot get most recent patient photo.'))
			return False
		fname = photo.export_to_file()
		if self.__set_pic_from_file(fname):
			return True
		if self.__set_pic_from_file():
			return True
		return False
	#-----------------------------------------------------------------
	def __set_pic_from_file(self, fname=None):
		if fname is None:
			fname = self.__fallback_pic_name
		try:
			img_data = wx.wxImage(fname, wx.wxBITMAP_TYPE_ANY)
			img_data.Rescale(self.desired_width, self.desired_height)
			bmp_data = wx.wxBitmapFromImage(img_data)
		except:
			_log.LogException('cannot set patient picture from [%s]' % fname, sys.exc_info())
			return False
		del img_data
		self.SetBitmap(bmp_data)
		self.__pic_name = fname
		return True
	#-----------------------------------------------------------------
	def _on_ImportPhoto(self, event):
		"""Import an existing photo."""

		# FIXME: read start path from option in DB
		imp_dlg = imagebrowser.ImageDialog(self, os.getcwd())
		imp_dlg.Centre()
		usr_action = imp_dlg.ShowModal()

		if usr_action != wx.wxID_OK:
			print "No file selected"
			return True

		new_pic_name = imp_dlg.GetFile()
		print "new pic name is", new_pic_name
		# try to set new patient picture
		if not self.__set_pic_from_file(new_pic_name):
			print "error setting new pic"
			return False

		# save in database
#		doc = gmMedDoc.create_document(self.__pat['ID'])
#		doc.update_metadata({'type ID': gmMedDoc.MUGSHOT})
#		obj = gmMedDoc.create_document_part(doc)
#		obj.update_data_from_file(photo)

		self.Show(True)

		return True
	#-----------------------------------------------------------------
	def _on_ExportPhoto(self, event):
		exp_dlg = wx.wxFileDialog (self, style=wx.wxSAVE)
		if exp_dlg.ShowModal() == wx.wxID_OK:
			shutil.copyfile (self.__pic_name, exp_dlg.GetPath())
	#-----------------------------------------------------------------
	def _on_AcquirePhoto(self,event):
		gmGuiHelpers.gm_show_info (
			_('This feature is not implemented yet.'),
			_('acquire patient photograph')
		)
	#-----------------------------------------------------------------
	def _on_RemovePhoto(self,event):
		gmGuiHelpers.gm_show_info (
			_('This feature is not implemented yet.'),
			_('remove patient photograph')
		)
	#-----------------------------------------------------------------
	def _on_patient_selected(self):
#		print "pulling patient photo from DB, needs to be implemented, async"
		self.__set_pic_from_file()

#====================================================
# main
#----------------------------------------------------
if __name__ == "__main__":
	app = wx.wxPyWidgetTester(size = (200, 200))
	app.SetWidget(cPatientPicture, -1)
	app.MainLoop()
#====================================================
# $Log: gmPatPicWidgets.py,v $
# Revision 1.9  2005-08-08 08:07:11  ncq
# - cleanup
#
# Revision 1.8  2005/02/05 10:58:09  ihaywood
# fixed patient picture problem (gratutious use of a named parameter)
# more rationalisation of loggin in gmCfg
#
# Revision 1.7  2005/01/31 10:37:26  ncq
# - gmPatient.py -> gmPerson.py
#
# Revision 1.6  2004/10/11 20:18:17  ncq
# - GnuMed now sports a patient pic in the top panel
# - not loaded when changing patient (rather reverting to empty face)
# - use right-click context menu "refresh photo" manually
# - only Kirk has a picture so far
#
# Revision 1.5  2004/09/18 13:54:37  ncq
# - improve strings
#
# Revision 1.4  2004/08/20 13:23:43  ncq
# - aquire -> acquire
#
# Revision 1.3  2004/08/19 14:37:30  ncq
# - fix missing import
#
# Revision 1.2  2004/08/19 14:07:54  ncq
# - cleanup
# - add tooltip but doesn't work with wxBitmap
#
# Revision 1.1  2004/08/18 10:15:26  ncq
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
