#--------------------------------
#embryonic gmGP_PatientPicture.py
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/Attic/gmGP_PatientPicture.py,v $
# $Id: gmGP_PatientPicture.py,v 1.13 2005-09-28 21:27:30 ncq Exp $
__version__ = "$Revision: 1.13 $"
__author__  = "R.Terry <rterry@gnumed.net>,\
			   I.Haywood <i.haywood@ugrad.unimelb.edu.au>,\
			   K.Hilbert <Karsten.Hilbert@gmx.net>"

import sys, os.path

from Gnumed.pycommon import gmDispatcher, gmSignals, gmGuiBroker
from Gnumed.business import gmMedDoc

import mx.DateTime as mxDT
try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

current_patient = -1
current_photo = None

#====================================================
class cPatientPicture (wx.StaticBitmap):
	"""A patient picture control ready for display.
	"""
	
	def __init__(self, parent, id):
		global current_photo
		try:
			self.default_photo = os.path.join(gmGuiBroker.GuiBroker()['gnumed_dir'], 'bitmaps', 'any_body2.png')
		except:
			self.default_photo = "../bitmaps/any_body2.png"

		# just in case
		wx.Image_AddHandler(wxPNGHandler())
		wx.Image_AddHandler(wx.JPEGHandler ())
		if not current_photo:
			current_photo = self.default_photo
		img_data = wx.Image(current_photo, wx.BITMAP_TYPE_ANY)
		bmp_data = wx.BitmapFromImage(img_data)
		self.x = bmp_data.GetWidth ()
		self.y = bmp_data.GetHeight ()
		del img_data

		wx.StaticBitmap.__init__(
			self,
			parent,
			id,
			bmp_data,
			wxPoint(0, 0),
			wx.Size(self.x, self.y)
		)

		gmDispatcher.connect(receiver=self._on_patient_selected, signal=gmSignals.patient_selected())

	def _on_patient_selected(self):
		print "updating patient photo, needs to be implemented, async"

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

	def setPhoto (self, fname):
		"""
		Manually set the photograph to be photo in file fname
		"""
		img_data = wx.Image (fname, wx.BITMAP_TYPE_ANY)
		img_data.Rescale (self.x, self.y)
		bmp_data = wx.BitmapFromImage (img = img_data)
		self.SetBitmap (bmp_data)
		del img_data

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
# $Log: gmGP_PatientPicture.py,v $
# Revision 1.13  2005-09-28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.12  2005/09/28 15:57:48  ncq
# - a whole bunch of wx.Foo -> wx.Foo
#
# Revision 1.11  2005/09/26 18:01:50  ncq
# - use proper way to import wx26 vs wx2.4
# - note: THIS WILL BREAK RUNNING THE CLIENT IN SOME PLACES
# - time for fixup
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
