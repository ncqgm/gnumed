"""GnuMed patient picture widget.
"""

#--------------------------------------------
#embryonic gmGP_PatientPicture.py replacement
#=====================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmPatPicWidgets.py,v $
# $Id: gmPatPicWidgets.py,v 1.30 2008-07-07 13:43:17 ncq Exp $
__version__ = "$Revision: 1.30 $"
__author__  = "R.Terry <rterry@gnumed.net>,\
			   I.Haywood <i.haywood@ugrad.unimelb.edu.au>,\
			   K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

# standard lib
import sys, os, os.path, logging


# 3rd party
import wx, wx.lib.imagebrowser


# GNUmed
from Gnumed.pycommon import gmDispatcher, gmTools
from Gnumed.business import gmMedDoc, gmPerson
from Gnumed.wxpython import gmGuiHelpers


_log = logging.getLogger('gm.ui')
_log.info(__version__)

ID_AcquirePhoto = wx.NewId()
ID_ImportPhoto = wx.NewId()

#=====================================================================
class cPatientPicture(wx.StaticBitmap):
	"""A patient picture control ready for display.
		with popup menu to import/export
		remove or Acquire from a device
	"""
	def __init__(self, parent, id, width=50, height=54):

		# find assets
		paths = gmTools.gmPaths(app_name  = 'gnumed', wx = wx)
		self.__fallback_pic_name = os.path.join(paths.system_app_data_dir, 'bitmaps', 'empty-face-in-bust.png')

		# load initial dummy bitmap
		img_data = wx.Image(self.__fallback_pic_name, wx.BITMAP_TYPE_ANY)
		bmp_data = wx.BitmapFromImage(img_data)
		del img_data
		# good default: 50x54
		self.desired_width = width
		self.desired_height = height
		wx.StaticBitmap.__init__(
			self,
			parent,
			id,
			bmp_data,
			wx.Point(0, 0),
			wx.Size(self.desired_width, self.desired_height)
		)

		self.__pat = gmPerson.gmCurrentPatient()

		# pre-make menu
		self.__photo_menu = wx.Menu()
		ID = wx.NewId()
		self.__photo_menu.Append(ID, _('Refresh from database'))
		wx.EVT_MENU(self, ID, self._on_refresh_from_backend)
		self.__photo_menu.AppendSeparator()
		self.__photo_menu.Append(ID_AcquirePhoto, _("Acquire from imaging device"))
		self.__photo_menu.Append(ID_ImportPhoto, _("Import from file"))

		self.__register_events()
	#-----------------------------------------------------------------
	# event handling
	#-----------------------------------------------------------------
	def __register_events(self):
		# wxPython events
		wx.EVT_RIGHT_UP(self, self._on_RightClick_photo)

		wx.EVT_MENU(self, ID_AcquirePhoto, self._on_AcquirePhoto)
		wx.EVT_MENU(self, ID_ImportPhoto, self._on_ImportPhoto)

		# dispatcher signals
		gmDispatcher.connect(receiver=self._on_post_patient_selection, signal = u'post_patient_selection')
	#-----------------------------------------------------------------
	def _on_RightClick_photo(self, event):
		if not self.__pat.connected:
			gmDispatcher.send(signal='statustext', msg=_('No active patient.'))
			return False
		self.PopupMenu(self.__photo_menu, event.GetPosition())
	#-----------------------------------------------------------------
	def _on_refresh_from_backend(self, evt):
		self.__reload_photo()
	#-----------------------------------------------------------------
	def _on_ImportPhoto(self, event):
		"""Import an existing photo."""

		# get from file system
		imp_dlg = wx.lib.imagebrowser.ImageDialog(parent = self, set_dir = os.path.expanduser('~'))
		imp_dlg.Centre()
		if imp_dlg.ShowModal() != wx.ID_OK:
			return

		self.__import_pic_into_db(fname = imp_dlg.GetFile())
		self.__reload_photo()
	#-----------------------------------------------------------------
	def _on_AcquirePhoto(self, event):

		# get from image source
		from Gnumed.pycommon import gmScanBackend

		fnames = gmScanBackend.acquire_pages_into_files (
			delay = 5,
			tmpdir = os.path.expanduser(os.path.join('~', '.gnumed', 'tmp')),
			calling_window = self
		)
		if fnames is False:
			gmGuiHelpers.gm_show_error (
				aMessage = _('Patient photo could not be acquired from source.'),
				aTitle = _('acquiring photo')
			)
			return
		if len(fnames) == 0:		# no pages scanned
			return

		self.__import_pic_into_db(fname=fnames[0])
		self.__reload_photo()
	#-----------------------------------------------------------------
	# internal API
	#-----------------------------------------------------------------
	def __import_pic_into_db(self, fname=None):

		docs = gmMedDoc.search_for_document(patient_id = self.__pat.ID, type_id = gmMedDoc.MUGSHOT)
		if len(docs) == 0:
			emr = self.__pat.get_emr()
			epi = emr.add_episode(episode_name=_('Administration'))
			enc = emr.get_active_encounter()
			doc = gmMedDoc.create_document (
				patient_id = self.__pat.ID,
				document_type = gmMedDoc.MUGSHOT,
				episode = epi['pk_episode'],
				encounter = enc['pk_encounter']
			)
		else:
			doc = docs[0]

		obj = doc.add_part(file=fname)
		return True
	#-----------------------------------------------------------------
	def __reload_photo(self):
		"""(Re)fetch patient picture from DB."""

		doc_folder = self.__pat.get_document_folder()
		photo = doc_folder.get_latest_mugshot()

		if photo is None:
			fname = None
#			gmDispatcher.send(signal='statustext', msg=_('Cannot get most recent patient photo from database.'))
		else:
			fname = photo.export_to_file()

		return self.__set_pic_from_file(fname)
	#-----------------------------------------------------------------
	def __set_pic_from_file(self, fname=None):
		if fname is None:
			fname = self.__fallback_pic_name
		try:
			img_data = wx.Image(fname, wx.BITMAP_TYPE_ANY)
			img_data.Rescale(self.desired_width, self.desired_height)
			bmp_data = wx.BitmapFromImage(img_data)
		except:
			_log.exception('cannot set patient picture from [%s]', fname)
			gmDispatcher.send(signal='statustext', msg=_('Cannot set patient picture from [%s].') % fname)
			return False
		del img_data
		self.SetBitmap(bmp_data)
		self.__pic_name = fname
		return True
	#-----------------------------------------------------------------
	def _on_post_patient_selection(self):
		self.__reload_photo()

#====================================================
# main
#----------------------------------------------------
if __name__ == "__main__":
	app = wx.PyWidgetTester(size = (200, 200))
	app.SetWidget(cPatientPicture, -1)
	app.MainLoop()
#====================================================
# $Log: gmPatPicWidgets.py,v $
# Revision 1.30  2008-07-07 13:43:17  ncq
# - current patient .connected
#
# Revision 1.29  2008/01/30 14:03:42  ncq
# - use signal names directly
# - switch to std lib logging
#
# Revision 1.28  2007/09/10 12:37:37  ncq
# - don't send signal on not finding patient pic
#   a) it's quite obvious
#   b) it might obscure more important messages
#
# Revision 1.27  2007/08/12 00:12:41  ncq
# - no more gmSignals.py
#
# Revision 1.26  2007/08/07 21:42:40  ncq
# - cPaths -> gmPaths
#
# Revision 1.25  2007/07/22 09:27:48  ncq
# - tmp/ now in .gnumed/
#
# Revision 1.24  2007/05/08 11:16:32  ncq
# - need to import gmTools
#
# Revision 1.23  2007/05/07 12:35:20  ncq
# - improve use of gmTools.cPaths()
#
# Revision 1.22  2007/04/23 01:10:58  ncq
# - add menu item to refresh from database
#
# Revision 1.21  2007/04/11 14:52:47  ncq
# - lots of cleanup
# - properly implement popup menu actions
#
# Revision 1.20  2006/12/21 16:54:32  ncq
# - inage handlers already inited
#
# Revision 1.19  2006/11/24 10:01:31  ncq
# - gm_beep_statustext() -> gm_statustext()
#
# Revision 1.18  2006/07/30 18:47:38  ncq
# - better comment
#
# Revision 1.17  2006/05/15 13:36:00  ncq
# - signal cleanup:
#   - activating_patient -> pre_patient_selection
#   - patient_selected -> post_patient_selection
#
# Revision 1.16  2006/04/29 19:47:36  ncq
# - improve commented out code :-)
#
# Revision 1.15  2006/01/13 13:52:17  ncq
# - create_document_part is gone, make comment on new way
#
# Revision 1.14  2006/01/01 20:38:03  ncq
# - properly use create_document()
#
# Revision 1.13  2005/09/28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.12  2005/09/28 15:57:48  ncq
# - a whole bunch of wx.Foo -> wx.Foo
#
# Revision 1.11  2005/09/27 20:44:59  ncq
# - wx.wx* -> wx.*
#
# Revision 1.10  2005/09/26 18:01:51  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
#
# Revision 1.9  2005/08/08 08:07:11  ncq
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
# - add tooltip but doesn't work with wx.Bitmap
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
# - bugfix for wx.BitmapFromImage()
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
# - change from wx.Panel to wx.StaticBitmap; load PNG, BMP, GIP automagically
# - alleviate sizer hell
#
