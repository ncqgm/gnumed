#--------------------------------
#embryonic gmGP_PatientPicture.py
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/Attic/gmGP_PatientPicture.py,v $
# $Id: gmGP_PatientPicture.py,v 1.6 2004-03-03 23:53:22 ihaywood Exp $
__version__ = "$Revision: 1.6 $"
__author__  = "R.Terry <rterry@gnumed.net>,\
			   I.Haywood <i.haywood@ugrad.unimelb.edu.au>,\
			   K.Hilbert <Karsten.Hilbert@gmx.net>"

			   

import sys, os.path
import gmGuiBroker
import gmDispatcher, gmSignals, gmMedDoc
import mx.DateTime as mxDT
from wxPython.wx import *
current_patient = -1
current_photo = None

#====================================================
class cPatientPicture (wxStaticBitmap):
	"""A patient picture control ready for display.
	"""
	
	def __init__(self, parent, id):
		global current_photo
		try:
			self.default_photo = os.path.join(gmGuiBroker.GuiBroker()['gnumed_dir'], 'bitmaps', 'any_body2.png')
		except:
			self.default_photo = "../bitmaps/any_body2.png"

		# just in case
	        wxImage_AddHandler(wxPNGHandler())
		wxImage_AddHandler(wxJPEGHandler ())
		if not current_photo:
			current_photo = self.default_photo
		img_data = wxImage(current_photo, wxBITMAP_TYPE_ANY)
		bmp_data = wxBitmapFromImage(img = img_data)
		self.x = bmp_data.GetWidth ()
		self.y = bmp_data.GetHeight ()
		del img_data

		wxStaticBitmap.__init__(
			self,
			parent,
			id,
			bmp_data,
			wxPoint(0, 0),
			wxSize(self.x, self.y)
		)

		gmDispatcher.connect (self.newPatient, gmSignals.patient_selected ())

	def newPatient (self, signal, kwds):
		global current_patient
		global current_photo
		if kwds['ID'] != current_patient: # do't drag photo across net more than once
			current_patient = kwds['ID']
			docs = gmMedDoc.search_for_document (kwds['ID'], gmMedDoc.MUGSHOT)
			# FIXME: "where date = max(select date from ... where l1.pat=l2.pat)" ...
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
		img_data = wxImage (fname, wxBITMAP_TYPE_ANY)
		img_data.Rescale (self.x, self.y)
		bmp_data = wxBitmapFromImage (img = img_data)
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
# Revision 1.6  2004-03-03 23:53:22  ihaywood
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
