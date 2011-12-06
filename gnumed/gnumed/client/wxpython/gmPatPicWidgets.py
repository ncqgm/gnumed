"""GNUmed patient picture widget."""

#=====================================================================
__author__  = "R.Terry <rterry@gnumed.net>,\
			   I.Haywood <i.haywood@ugrad.unimelb.edu.au>,\
			   K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"

# standard lib
import sys, os, os.path, logging


# 3rd party
import wx, wx.lib.imagebrowser


# GNUmed
from Gnumed.pycommon import gmDispatcher, gmTools, gmI18N
from Gnumed.business import gmDocuments, gmPerson
from Gnumed.wxpython import gmGuiHelpers


_log = logging.getLogger('gm.ui')


ID_AcquirePhoto = wx.NewId()
ID_ImportPhoto = wx.NewId()
ID_Refresh = wx.NewId()

#=====================================================================
class cPatientPicture(wx.StaticBitmap):
	"""A patient picture control ready for display.
		with popup menu to import/export
		remove or Acquire from a device
	"""
	def __init__(self, *args, **kwargs):

		wx.StaticBitmap.__init__(self, *args, **kwargs)

		paths = gmTools.gmPaths(app_name = u'gnumed', wx = wx)
		self.__fallback_pic_name = os.path.join(paths.system_app_data_dir, 'bitmaps', 'empty-face-in-bust.png')
		self.__desired_width = 50
		self.__desired_height = 54
		self.__pat = gmPerson.gmCurrentPatient()

		self.__init_ui()
		self.__register_events()
	#-----------------------------------------------------------------
	# event handling
	#-----------------------------------------------------------------
	def __register_events(self):
		# wxPython events
		wx.EVT_RIGHT_UP(self, self._on_RightClick_photo)
		wx.EVT_MENU(self, ID_AcquirePhoto, self._on_AcquirePhoto)
		wx.EVT_MENU(self, ID_ImportPhoto, self._on_ImportPhoto)
		wx.EVT_MENU(self, ID_Refresh, self._on_refresh_from_backend)

		# dispatcher signals
		gmDispatcher.connect(receiver=self._on_post_patient_selection, signal = u'post_patient_selection')
	#-----------------------------------------------------------------
	def _on_post_patient_selection(self):
		self.__reload_photo()
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

		try:
			fnames = gmScanBackend.acquire_pages_into_files (
				delay = 5,
				tmpdir = os.path.expanduser(os.path.join('~', '.gnumed', 'tmp')),
				calling_window = self
			)
		except OSError:
			_log.exception('problem acquiring image from source')
			gmGuiHelpers.gm_show_error (
				aMessage = _(
					'No image could be acquired from the source.\n\n'
					'This may mean the scanner driver is not properly installed.\n\n'
					'On Windows you must install the TWAIN Python module\n'
					'while on Linux and MacOSX it is recommended to install\n'
					'the XSane package.'
				),
				aTitle = _('Acquiring photo')
			)
			return

		if fnames is False:
			gmGuiHelpers.gm_show_error (
				aMessage = _('Patient photo could not be acquired from source.'),
				aTitle = _('Acquiring photo')
			)
			return

		if len(fnames) == 0:		# no pages scanned
			return

		self.__import_pic_into_db(fname=fnames[0])
		self.__reload_photo()
	#-----------------------------------------------------------------
	# internal API
	#-----------------------------------------------------------------
	def __init_ui(self):
		# pre-make context menu
		self.__photo_menu = wx.Menu()
		self.__photo_menu.Append(ID_Refresh, _('Refresh from database'))
		self.__photo_menu.AppendSeparator()
		self.__photo_menu.Append(ID_AcquirePhoto, _("Acquire from imaging device"))
		self.__photo_menu.Append(ID_ImportPhoto, _("Import from file"))

		self.__set_pic_from_file()
	#-----------------------------------------------------------------
	def __import_pic_into_db(self, fname=None):

		docs = gmDocuments.search_for_document(patient_id = self.__pat.ID, type_id = gmDocuments.MUGSHOT)
		if len(docs) == 0:
			emr = self.__pat.get_emr()
			epi = emr.add_episode(episode_name=_('Administration'))
			enc = emr.active_encounter
			doc = gmDocuments.create_document (
				document_type = gmDocuments.MUGSHOT,
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
			self.SetToolTipString (_(
				'Patient picture.\n'
				'\n'
				'Right-click for context menu.'
			))
#			gmDispatcher.send(signal='statustext', msg=_('Cannot get most recent patient photo from database.'))
		else:
			fname = photo.export_to_file()
			self.SetToolTipString (_(
				'Patient picture (%s).\n'
				'\n'
				'Right-click for context menu.'
			) % photo['date_generated'].strftime('%b %Y').decode(gmI18N.get_encoding()))

		return self.__set_pic_from_file(fname)
	#-----------------------------------------------------------------
	def __set_pic_from_file(self, fname=None):
		if fname is None:
			fname = self.__fallback_pic_name
		try:
			img_data = wx.Image(fname, wx.BITMAP_TYPE_ANY)
			img_data.Rescale(self.__desired_width, self.__desired_height)
			bmp_data = wx.BitmapFromImage(img_data)
		except:
			_log.exception('cannot set patient picture from [%s]', fname)
			gmDispatcher.send(signal='statustext', msg=_('Cannot set patient picture from [%s].') % fname)
			return False
		del img_data
		self.SetBitmap(bmp_data)
		self.__pic_name = fname

		return True

#====================================================
# main
#----------------------------------------------------
if __name__ == "__main__":
	app = wx.PyWidgetTester(size = (200, 200))
	app.SetWidget(cPatientPicture, -1)
	app.MainLoop()
#====================================================
