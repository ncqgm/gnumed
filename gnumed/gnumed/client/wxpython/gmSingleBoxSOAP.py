"""GnuMed single box clinical notes input widget

This widget was suggested by David Guest on the mailing list.

All it does is to provide a single multi-line textbox for
typing clear-text clinical notes which are stored in clin_note.
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/Attic/gmSingleBoxSOAP.py,v $
# $Id: gmSingleBoxSOAP.py,v 1.1 2003-06-19 16:50:32 ncq Exp $
__version__ = "$Revision: 1.1 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

import sys

if __name__ == "__main__":
	sys.path.append ("../python-common/")
	import gmI18N

from wxPython.wx import *
#============================================================
class gmSingleBoxSOAP(wxTextCtrl):
	"""if we separate it out like this it can transparently gain features"""
	def __init__(self, *args, **kwargs):
		wxTextCtrl.__init__(self, *args, **kwargs)
#============================================================
class gmSingleBoxSOAPPanel(wxPanel):
	def __init__(self, *args, **kwargs):
		#kwargs["style"] = wxDEFAULT_FRAME_STYLE
		wxPanel.__init__(self, *args, **kwargs)
		self.__do_layout()
	#--------------------------------------------------------
	def __do_layout(self):
		# large box for free-text clinical notes
		self.soap_box = gmSingleBoxSOAP(
			self,
			-1,
			'',
			style = wxTE_MULTILINE
		)
		# buttons below that
		self.btn_save = wxButton(self, -1, _("save"))
		self.btn_clear = wxButton(self, -1, _("clear"))
		szr_btns = wxBoxSizer(wxHORIZONTAL)
		szr_btns.Add(self.btn_save, 1, wxALIGN_CENTER_HORIZONTAL, 0)
		szr_btns.Add(self.btn_clear, 1, wxALIGN_CENTER_HORIZONTAL, 0)
		# arrange widgets
		szr_outer = wxStaticBoxSizer(wxStaticBox(self, -1, _("SOAP clinical notes")), wxVERTICAL)
		szr_outer.Add(self.soap_box, 1, wxEXPAND, 0)
		szr_outer.Add(szr_btns, 0, wxEXPAND, 0)
		# and do layout
		self.SetAutoLayout(1)
		self.SetSizer(szr_outer)
		szr_outer.Fit(self)
		szr_outer.SetSizeHints(self)
		self.Layout()
#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":
	app = wxPyWidgetTester(size = (600, 600))
	app.SetWidget(gmSingleBoxSOAPPanel, -1)
	app.MainLoop()

#============================================================
# $Log: gmSingleBoxSOAP.py,v $
# Revision 1.1  2003-06-19 16:50:32  ncq
# - let's make something simple but functional first
#
#
