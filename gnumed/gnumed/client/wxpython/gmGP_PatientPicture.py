#--------------------------------
#embryonic gmGP_PatientPicture.py
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/Attic/gmGP_PatientPicture.py,v $
# $Id: gmGP_PatientPicture.py,v 1.3 2003-11-17 10:56:38 sjtan Exp $
__version__ = "$Revision: 1.3 $"
__author__  = "R.Terry <rterry@gnumed.net>,\
			   I.Haywood <i.haywood@ugrad.unimelb.edu.au>,\
			   K.Hilbert <Karsten.Hilbert@gmx.net>"

			   

import sys, os.path



if __name__ != "__main__":
	import gmGuiBroker


from wxPython.wx import *
#====================================================
class cPatientPicture (wxStaticBitmap):
	"""A patient picture control ready for display.
	"""

	
	def __init__(self, parent, id):
		try:
			path = os.path.join(gmGuiBroker.GuiBroker()['gnumed_dir'], 'bitmaps', 'any_body2.png')
		except:
			path= "../bitmaps/any_body2.png"

		# just in case
	        wxImage_AddHandler(wxPNGHandler())
		pic_name = path
		img_data = wxImage(pic_name, wxBITMAP_TYPE_ANY)
		bmp_data = wxBitmapFromImage(img = img_data)
		del img_data

		wxStaticBitmap.__init__(
			self,
			parent,
			id,
			bmp_data,
			wxPoint(0, 0),
			wxSize(bmp_data.GetWidth(), bmp_data.GetHeight())
		)

		# FIXME: register interest in patient change so we can load pic

#====================================================
# main
#----------------------------------------------------
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (200, 200))
	app.SetWidget(cPatientPicture, -1)
	app.MainLoop()
#====================================================
# $Log: gmGP_PatientPicture.py,v $
# Revision 1.3  2003-11-17 10:56:38  sjtan
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
