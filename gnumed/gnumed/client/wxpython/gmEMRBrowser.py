"""GnuMed patient EMR tree browser.
"""
#================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmEMRBrowser.py,v $
# $Id: gmEMRBrowser.py,v 1.7 2005-01-31 10:37:26 ncq Exp $
__version__ = "$Revision: 1.7 $"
__author__ = "cfmoro1976@yahoo.es"
__license__ = "GPL"

import os.path, sys

from wxPython import wx

from Gnumed.pycommon import gmLog, gmI18N, gmPG, gmDispatcher, gmSignals
from Gnumed.exporters import gmPatientExporter
from Gnumed.business import gmEMRStructItems, gmPerson
from Gnumed.wxpython import gmRegetMixin
from Gnumed.pycommon.gmPyCompat import *

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
#============================================================
class cEMRBrowserPanel(wx.wxPanel, gmRegetMixin.cRegetOnPaintMixin):

	def __init__(self, parent, id):
		"""
		Contructs a new instance of EMR browser panel

		parent - Wx parent widget
		id - Wx widget id
		"""
		# Call parents constructors
		wx.wxPanel.__init__ (
			self,
			parent,
			id,
			wx.wxPyDefaultPosition,
			wx.wxPyDefaultSize,
			wx.wxNO_BORDER
		)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		self.__pat = gmPerson.gmCurrentPatient()
		self.__exporter = gmPatientExporter.cEmrExport(patient = self.__pat)

		self.__do_layout()
		self.__register_interests()
		self.__reset_ui_content()

	#--------------------------------------------------------
	def __do_layout(self):
		"""
		Arranges EMR browser layout
		"""
		# splitter window
		self.__tree_narr_splitter = wx.wxSplitterWindow(self, -1)
		# emr tree
		self.__emr_tree = wx.wxTreeCtrl (
			self.__tree_narr_splitter,
			-1,
			style=wx.wxTR_HAS_BUTTONS | wx.wxNO_BORDER
		)
		# narrative details text control
		self.__narr_TextCtrl = wx.wxTextCtrl (
			self.__tree_narr_splitter,
			-1,
			style=wx.wxTE_MULTILINE | wx.wxTE_READONLY | wx.wxTE_DONTWRAP
		)
		# set up splitter
		# FIXME: read/save value from/into backend
		self.__tree_narr_splitter.SetMinimumPaneSize(20)
		self.__tree_narr_splitter.SplitVertically(self.__emr_tree, self.__narr_TextCtrl)

		self.__szr_main = wx.wxBoxSizer(wx.wxVERTICAL)
		self.__szr_main.Add(self.__tree_narr_splitter, 1, wx.wxEXPAND, 0)

		self.SetAutoLayout(1)
		self.SetSizer(self.__szr_main)
		self.__szr_main.Fit(self)
		self.__szr_main.SetSizeHints(self)
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		"""
		Configures enabled event signals
		"""
		# wx.wxPython events
		wx.EVT_TREE_SEL_CHANGED(self.__emr_tree, self.__emr_tree.GetId(), self._on_tree_item_selected)
		# client internal signals
		gmDispatcher.connect(signal=gmSignals.patient_selected(), receiver=self._on_patient_selected)
	#--------------------------------------------------------
	def _on_patient_selected(self):
		"""Patient changed."""
		self.__exporter.set_patient(self.__pat)
		self._schedule_data_reget()
	#--------------------------------------------------------
	def _on_tree_item_selected(self, event):
		"""
		Displays information for a selected tree node
		"""
		sel_item = event.GetItem()
		sel_item_obj = self.__emr_tree.GetPyData(sel_item)

		if(isinstance(sel_item_obj, gmEMRStructItems.cEncounter)):
			header = _('Encounter\n=========\n\n')
			epi = self.__emr_tree.GetPyData(self.__emr_tree.GetItemParent(sel_item))
			txt = self.__exporter.dump_encounter_info(episode=epi, encounter=sel_item_obj)

		elif (isinstance(sel_item_obj, gmEMRStructItems.cEpisode)):
			header = _('Episode\n=======\n\n')
			txt = self.__exporter.dump_episode_info(episode=sel_item_obj)

		elif (isinstance(sel_item_obj, gmEMRStructItems.cHealthIssue)):
			header = _('Health Issue\n============\n\n')
			txt = self.__exporter.dump_issue_info(issue=sel_item_obj)

		else:
			header = _('Summary\n=======\n\n')
			txt = self.__exporter.dump_summary_info()

		self.__narr_TextCtrl.Clear()
		self.__narr_TextCtrl.WriteText(header)
		self.__narr_TextCtrl.WriteText(txt)
	#--------------------------------------------------------
	# reget mixin API
	#--------------------------------------------------------
	def _populate_with_data(self):
		"""
		Fills UI with data.
		"""
		self.__reset_ui_content()
		if self.refresh_tree():
			return True
		return False
		
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------		
	def refresh_tree(self):
		"""
		Updates EMR browser data
		"""
		# EMR tree root item
		demos = self.__pat.get_demographic_record()
		names = demos.get_names()
		root_item = self.__emr_tree.AddRoot(_('%s %s EMR') % (names['first'], names['last']))

		# Obtain all the tree from exporter
		self.__exporter.get_historical_tree(self.__emr_tree)

		# Expand root node and display patient summary info
		self.__emr_tree.Expand(root_item)
		self.__narr_TextCtrl.WriteText(_('Summary\n=======\n\n'))
		self.__narr_TextCtrl.WriteText(self.__exporter.dump_summary_info(0))

		# Set sash position
		self.__tree_narr_splitter.SetSashPosition(self.__tree_narr_splitter.GetSizeTuple()[0]/3, True)

		# FIXME: error handling
		return True

	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __reset_ui_content(self):
		"""
		Clear all information displayed in browser (tree and details area)
		"""
		self.__emr_tree.DeleteAllItems()
		self.__narr_TextCtrl.Clear()
	#--------------------------------------------------------
#	def set_patient(self, patient):
#		"""
#		Configures EMR browser patient and instantiates exporter.
#		Appropiate for standalaone use.
#		patient - The patient to display EMR for
#		"""
#		self.__patient = patient
#		self.__exporter.set_patient(patient)

#== Module convenience functions (for standalone use) =======================
def prompted_input(prompt, default=None):
	"""
	Obtains entry from standard input
	
	promp - Promt text to display in standard output
	default - Default value (for user to press only intro)
	"""
	usr_input = raw_input(prompt)
	if usr_input == '':
		return default
	return usr_input
#------------------------------------------------------------				 
def askForPatient():
	"""
		Main module application patient selection function.
	"""
	
	# Variable initializations
	pat_searcher = gmPerson.cPatientSearcher_SQL()

	# Ask patient to dump and set in exporter object
	patient_term = prompted_input("\nPatient search term (or 'bye' to exit) (eg. Kirk): ")
	if patient_term == 'bye':
		return None
	search_ids = pat_searcher.get_patient_ids(search_term = patient_term)
	if search_ids is None or len(search_ids) == 0:
		prompted_input("No patient matches the query term. Press any key to continue.")
		return None
	elif len(search_ids) > 1:
		prompted_input("Various patients match the query term. Press any key to continue.")
		return None
	patient_id = search_ids[0]
	patient = gmPerson.gmCurrentPatient(patient_id)
	return patient
	
#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':

	from Gnumed.pycommon import gmCfg

	_log.SetAllLogLevels(gmLog.lData)
	_log.Log (gmLog.lInfo, "starting emr browser...")

	_cfg = gmCfg.gmDefCfgFile	 
	if _cfg is None:
		_log.Log(gmLog.lErr, "Cannot run without config file.")
		sys.exit("Cannot run without config file.")

	try:
		# make sure we have a db connection
		gmPG.set_default_client_encoding('latin1')
		pool = gmPG.ConnectionPool()
		
		# obtain patient
		patient = askForPatient()
		if patient is None:
			print "No patient. Exiting gracefully..."
			sys.exit(0)

		# display standalone browser
		application = wx.wxPyWidgetTester(size=(800,600))
		emr_browser = cEMRBrowserPanel(application.frame, -1)
#		emr_browser.set_patient(patient)		
		emr_browser.refresh_tree()
		
		application.frame.Show(True)
		application.MainLoop()
		
		# clean up
		if patient is not None:
			try:
				patient.cleanup()
			except:
				print "error cleaning up patient"
	except StandardError:
		_log.LogException("unhandled exception caught !", sys.exc_info(), 1)
		# but re-raise them
		raise
	try:
		pool.StopListeners()
	except:
		_log.LogException('unhandled exception caught', sys.exc_info(), verbose=1)
		raise

	_log.Log (gmLog.lInfo, "closing emr browser...")

#================================================================
# $Log: gmEMRBrowser.py,v $
# Revision 1.7  2005-01-31 10:37:26  ncq
# - gmPatient.py -> gmPerson.py
#
# Revision 1.6  2004/10/31 00:37:13  cfmoro
# Fixed some method names. Refresh function made public for easy reload, eg. standalone. Refresh browser at startup in standalone mode
#
# Revision 1.5  2004/09/06 18:57:27  ncq
# - Carlos pluginized the lot ! :-)
# - plus some fixes/tabified it
#
# Revision 1.4	2004/09/01 22:01:45	 ncq
# - actually use Carlos' issue/episode summary code
#
# Revision 1.3	2004/08/11 09:46:24	 ncq
# - now that EMR exporter supports SOAP notes - display them
#
# Revision 1.2	2004/07/26 00:09:27	 ncq
# - Carlos brings us data display for the encounters - can REALLY browse EMR now !
#
# Revision 1.1	2004/07/21 12:30:25	 ncq
# - initial checkin
#
