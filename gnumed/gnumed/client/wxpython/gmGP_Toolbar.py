# GnuMed
# GPL

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/Attic/gmGP_Toolbar.py,v $
__version__ = "$Revision: 1.12 $"
__author__  = "R.Terry <rterry@gnumed.net>, I.Haywood <i.haywood@ugrad.unimelb.edu.au>"
#===========================================================
import sys, os.path
if __name__ == "__main__":
	sys.path.append(os.path.join('..', 'python-common'))

import gmLog, gmGuiBroker
import gmGP_PatientPicture

from wxPython.wx import *

# FIXME: need a better name here !
bg_col = wxColour(214,214,214)
#===========================================================
class cMainTopPanel(wxPanel):
	def __init__(self, parent,id):

		gb = gmGuiBroker.GuiBroker ()
		wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, wxRAISED_BORDER)
		self.SetBackgroundColour(bg_col)

		# layout:
		# .--------------------------------.
		# | patient | toolbar              |
		# | picture |----------------------|
		# |         | toolbar              |
		# `--------------------------------'

		# create patient picture
		self.patient_picture = gmGP_PatientPicture.cPatientPicture(self, -1)
		gb['main.patient_picture'] = self.patient_picture

		# create toolbars
		# - top (content is added elsewhere ...)
		self.szr_top_tb = wxBoxSizer (wxHORIZONTAL)
		# - bottom (holds most of the buttons)
		self.szr_bottom_tb = wxBoxSizer (wxHORIZONTAL)
		self.bottomline = wxPanel(self, -1)
		self.szr_bottom_tb.Add (self.bottomline, 1, wxGROW)
		# - stack them atop each other
		self.szr_toolbars = wxBoxSizer(wxVERTICAL)
		self.szr_toolbars.Add(1, 3, 0, wxEXPAND)	# ??? (IMHO: space is at too much of a premium for such padding)
		self.szr_toolbars.Add(self.szr_top_tb, 1, wxEXPAND)
		self.szr_toolbars.Add(self.szr_bottom_tb, 1, wxEXPAND | wxALL, 2)

		# create main sizer
		self.szr_main = wxBoxSizer(wxHORIZONTAL)
		# - insert patient picture
		self.szr_main.Add(self.patient_picture, 0, wxEXPAND)
		# - insert stacked toolbars
		self.szr_main.Add(self.szr_toolbars, 1, wxEXPAND)

		# init toolbars dict
		self.subbars = {}

		self.SetSizer(self.szr_main)	#set the sizer
		self.szr_main.Fit(self)			#set to minimum size as calculated by sizer
		self.SetAutoLayout(true)		#tell frame to use the sizer
		self.Show(true)
	#-------------------------------------------------------
	def AddWidgetRightBottom (self, widget):
		"""Insert a widget on the right-hand side of the bottom toolbar.
		"""
		self.szr_bottom_tb.Add(widget, 0, wxRIGHT, 0)
	#-------------------------------------------------------
	def AddWidgetLeftBottom (self, widget):
		"""Insert a widget on the left-hand side of the bottom toolbar.
		"""
		self.szr_bottom_tb.Prepend(widget, 0, wxALL, 0)
	#-------------------------------------------------------
	def AddWidgetTopLine (self, widget, proportion = 0, flag = wxEXPAND, border = 0):
		"""Inserts a widget onto the top line.
		"""
		self.szr_top_tb.Add(widget, proportion, flag, border)
	#-------------------------------------------------------
	def AddBar (self, key):
		"""Creates and returns a new empty toolbar, referenced by key.

		Key should correspond to the notebook page number as defined
		by the notebook (see gmPlugin.py), so that gmGuiMain can 
		display the toolbar with the notebook
		"""
		self.subbars[key] = wxToolBar (
			self.bottomline,
			-1,
			size = self.bottomline.GetClientSize(),
			style=wxTB_HORIZONTAL | wxNO_BORDER | wxTB_FLAT
		)

		self.subbars[key].SetToolBitmapSize((16,16))
		if len(self.subbars) == 1:
			self.subbars[key].Show(1)
			self.__current = key
		else:
			self.subbars[key].Hide()
		return self.subbars[key]
	#-------------------------------------------------------
	def ReFit (self):
		"""Refits the toolbar after its been changed
		"""
		tw = 0
		th = 0
		# get maximum size for the toolbar
		for i in self.subbars.values ():
			ntw, nth = i.GetSizeTuple ()
			if ntw > tw:
				tw = ntw
			if nth > th:
				th = nth
		#import pdb
		#pdb.set_trace ()
		sz = wxSize (tw, th)
		self.bottomline.SetSize(sz)
		for i in self.subbars.values():
			i.SetSize (sz)
		self.szr_main.Layout()
		self.szr_main.Fit(self)
	#-------------------------------------------------------
	def ShowBar (self, key):
		"""Displays the named toolbar.
		"""
		self.subbars[self.__current].Hide()
		try:
			self.subbars[key].Show(1)
			self.__current = key
		except KeyError:
			gmLog.gmDefLog.LogException("cannot show undefined toolbar [%s]" % key, sys.exc_info(), fatal=0)
	#-------------------------------------------------------
	def DeleteBar (self, key):
		"""Removes a toolbar.
		"""
		try:
			self.subbars[key].Destroy()
			del self.subbars[key]
			# FIXME: ??
			if self.__current == key and len(self.subbars):
				self.__current = self.subbars.keys()[0]
				self.subbars[self.__current].Show(1)
		except KeyError:
			gmLog.gmDefLog.LogException("cannot delete undefined toolbar [%s]" % key, sys.exc_info(), fatal=0)

#===========================================================	
if __name__ == "__main__":
	gb = gmGuiBroker.GuiBroker ()
	gb['gnumed_dir'] = '..'
	app = wxPyWidgetTester(size = (400, 200))
	app.SetWidget(cMainTopPanel, -1)
	app.MainLoop()
#===========================================================
# $Log: gmGP_Toolbar.py,v $
# Revision 1.12  2003-03-29 18:26:04  ncq
# - allow proportion/flag/border in AddWidgetTopLine()
#
# Revision 1.11  2003/03/29 13:46:44  ncq
# - make standalone work, cure sizerom
# - general cleanup, comment, clarify
#
# Revision 1.10  2003/01/12 00:24:02  ncq
# - CVS keywords
#
