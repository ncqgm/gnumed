#############################################################################
#
# gmDataPanelMixin - Provides a uniform means of data sensitivity to a GUI panel
# ---------------------------------------------------------------------------
#
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: nil
############################################################################

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/test-client-c/python-common/Attic/gmDataPanelMixin.py,v $
__version__ = "$Revision: 1.1 $"
__author__ = "H.Herb <hherb@gnumed.net>"
# $Log: gmDataPanelMixin.py,v $
# Revision 1.1  2003-10-23 06:02:39  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.3  2003/01/16 14:45:03  ncq
# - debianized
#
# Revision 1.2  2003/01/06 04:52:55  ihaywood
# resurrected gmDemographics.py
#
# Revision 1.1  2002/10/13 11:49:50  hherb
# provides a uniform means of data sensitivity to a GUI panel
#

"""Provides a uniform means of data sensitivity to a GUI panel"""

import gmPG

class DataPanelMixin :

	def __init__(self, dbbroker=None):
		if dbbroker is None:
			dbbroker = gmPG.ConnectionPool ()
		self._dbbroker = dbbroker	# a gmPG database broker object
		self._dirty = 0		# true if the data has been modified
		self._loaded = 0	# true if the panel has been filled with data loaded from the backend
		self._data = {}		# a dictionary containing the data displayed in this panel;
					# key words are the column names returned by the query/queries

	
	def OnDefault(self):
		"""Virtual function: has to put all widgets into their default state"""
		pass
	
	def OnLoadData(self, **kwds):
		"""Virtual function: loads data from the backend and updates the
		correlating widgets. 'kwds' is a dictionary argument for
		arbitrary query arguments like primary keys"""
		self._loaded = 1
		
	def OnSaveData(self, **kwds):
		"""Virtual function: saves the data from this panel to the backend;
		if not 'self._loaded', it is inserted, else if 'self._dirty is true, updated"""
		pass
		
	def OnUndo(self):
		"""restores the data as loaded from the backend if 'self._loaded is true,
		else retores the default"""
		pass
