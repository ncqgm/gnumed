#!/usr/bin/env python
#----------------------------------------------------------------------
"""
This is a no-frills document display handler for the
GNUmed medical document database.

It knows nothing about the documents itself. All it does
is to let the user select a page to display and tries to
hand it over to an appropriate viewer.

For that it relies on proper mime type handling at the OS level.
"""
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/blobs_hilbert/viewer-tree/Attic/show-med_docs.py,v $
__version__ = "$Revision: 1.13 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
#================================================================
import os.path, sys, os

# location of our modules
if __name__ == '__main__':
	sys.path.append(os.path.join('.', 'modules'))

import gmLog
_log = gmLog.gmDefLog
if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)

_log.Log(gmLog.lData, __version__)

if __name__ == "__main__":
	import gmI18N

import gmCfg
_cfg = gmCfg.gmDefCfgFile

from docPatient import cPatient, gm2long_gender_map
from docDatabase import cDatabase
import docMime, docDocument

from wxPython.wx import *
#----------------------------------------------------------------------
#        self.tree = MyTreeCtrl(self, tID, wxDefaultPosition, wxDefaultSize,
#                               wxTR_HAS_BUTTONS | wxTR_EDIT_LABELS# | wxTR_MULTIPLE
#                               , self.log)

		# NOTE:  For some reason tree items have to have a data object in
		#        order to be sorted.  Since our compare just uses the labels
		#        we don't need any real data, so we'll just use None.

#        EVT_TREE_ITEM_EXPANDED  (self, tID, self.OnItemExpanded)
#        EVT_TREE_ITEM_COLLAPSED (self, tID, self.OnItemCollapsed)
#        EVT_TREE_SEL_CHANGED    (self, tID, self.OnSelChanged)
#        EVT_TREE_BEGIN_LABEL_EDIT(self, tID, self.OnBeginEdit)
#        EVT_TREE_END_LABEL_EDIT (self, tID, self.OnEndEdit)
#        EVT_TREE_ITEM_ACTIVATED (self, tID, self.OnActivate)

#        EVT_LEFT_DCLICK(self.tree, self.OnLeftDClick)
#        EVT_RIGHT_DOWN(self.tree, self.OnRightClick)
#        EVT_RIGHT_UP(self.tree, self.OnRightUp)

[	wxID_PNL_main,
] = map(lambda _init_ctrls: wxNewId(), range(1))
#================================================================
class cDocTree(wxTreeCtrl):
	"""This wxTreeCtrl derivative displays a tree view of stored medical documents.
	"""

	def __init__(self, parent, id, aPatient = None, aConn = None):
		"""Set up our specialised tree.
		"""
		# sanity checks
		if aPatient is None:
			_log.Log(gmLog.lErr, "Cannot retrieve documents without knowing the patient !")
			return None

		if aConn is None:
			_log.Log(gmLog.lErr, "Cannot retrieve documents without database connection !")
			return None

		self.__conn = aConn

		# make sure aPatient knows its ID
		result = aPatient.getIDfromGNUmed(self.__conn)
		if result[0]:
			_log.Log(gmLog.lInfo, "Making document tree for patient with ID %s" % result[1])
		else:
			_log.Log(gmLog.lErr, "Patient data is ambigous. Aborting. %s" % str(result))
			return None

		# read documents from database
		self.doc_list = aPatient.getDocsFromGNUmed(self.__conn)
		if self.doc_list is None:
			_log.Log(gmLog.lErr, "Cannot find any documents.")
			return None

		wxTreeCtrl.__init__(self, parent, id, style=wxTR_NO_BUTTONS)

		# build tree from document list
		self.root = self.AddRoot(_("available documents"), -1, -1)
		self.SetPyData(self.root, None)
		self.SetItemHasChildren(self.root, TRUE)

		# add our documents as first level nodes
		for doc_id in self.doc_list.keys():
			doc = self.doc_list[doc_id]
			mdata = doc.getMetaData()
			c = mdata['comment'] + " " * 25
			r = mdata['reference'] + " " * 10
			tmp = "%s | %s | %s"
			label =  tmp % (mdata['date'][:10], c[:25], r[:10])
			doc_node = self.AppendItem(self.root, label)
			self.SetItemBold(doc_node, bold=TRUE)
			# we need to distinguish documents from objects in OnActivate
			# this is ugly
			data = {'doc_id': doc_id,
					'id'	: doc_id}
			self.SetPyData(doc_node, data)
			self.SetItemHasChildren(doc_node, TRUE)

			# now add objects as child nodes
			i = 1
			for oid in mdata['objects'].keys():
				obj = mdata['objects'][oid]
				p = str(i) +  " "
				c = str(obj['comment'])
				if c == "None":
					c = _("no comment available")
				tmp = _('page %s: \"%s\"')
				label = tmp % (p[:2], c)
				obj_node = self.AppendItem(doc_node, label)
				data = {'doc_id': doc_id,
						'id': oid}
				self.SetPyData(obj_node, data)
				i += 1
			# and expand
			self.Expand(doc_node)

		# and uncollapse
		self.Expand(self.root)

		EVT_TREE_ITEM_ACTIVATED (self, self.GetId(), self.OnActivate)
	#------------------------------------------------------------------------
	def OnActivate (self, event):
		item = event.GetItem()
		node_data = self.GetPyData(item)

		# exclude pseudo root node
		if node_data == None:
			return

		# do nothing with documents
		if node_data['id'] == node_data['doc_id']:
			return

		# but do everything with objects
		_log.Log(gmLog.lData, "User selected object %s from document %s" % (node_data['id'], node_data['doc_id']))
		exp_base = os.path.abspath(os.path.expanduser(_cfg.get("viewer", "export dir")))
		if not os.path.exists(exp_base):
			_log.Log(gmLog.lErr, "The directory '%s' does not exist ! Falling back to default temporary directory." % exp_base) # which is tempfile.tempdir == None == use system defaults
		else:
			_log.Log(gmLog.lData, "working into directory '%s'" % exp_base)

		# document handle
		doc = self.doc_list[node_data['doc_id']]
		mdata = doc.getMetaData()
		_log.Log(gmLog.lData, "document: %s" % mdata)

		# retrieve object
		if not doc.exportObjFromGNUmed(self.__conn, exp_base, node_data['id']):
			_log.Log(gmLog.lErr, "Cannot export object (%s) data from database !" % node_data['id'])
			return (1==0)

		obj = mdata['objects'][node_data['id']]
		fname = obj['file name']
		(result, msg) = docDocument.call_viewer_on_file(fname)
		if not result:
			dlg = wxMessageDialog(
				self,
				_('Cannot display page.\n%s.') % msg,
				_('displaying page'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None
		return 1
#== classes for standalone use ==================================
if __name__ == '__main__':

	class cStandalonePanel(wxPanel):

		def __init__(self, parent, id):
			if self.__connect_to_db() is None:
				_log.Log (gmLog.lErr, "No need to work without being able to connect to database.")
				raise AssertionError, "database connection needed"

			if self.__get_pat_data() is None:
				_log.Log (gmLog.lErr, "Cannot load patient data.")
				raise AssertionError, "Cannot load patient data."

			wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize)
			self.SetTitle(_("stored medical documents"))

			# make patient panel
			self.pat_panel = wxStaticText(
				id = -1,
				parent = self,
				label = "%s %s (%s), %s" % (self.__patient.firstnames, self.__patient.lastnames, gm2long_gender_map[self.__patient.gender], self.__patient.dob),
				style = wxALIGN_CENTER
			)
			self.pat_panel.SetFont(wxFont(25, wxSWISS, wxNORMAL, wxNORMAL, 0, ""))

			# make document tree
			self.tree = cDocTree(self, -1, self.__patient, self.__conn)
			self.tree.SelectItem(self.tree.root)

			szr_main = wxBoxSizer(wxVERTICAL)
			szr_main.Add(self.pat_panel, 0, wxEXPAND, 1)
			szr_main.Add(self.tree, 1, wxEXPAND, 9)

			self.SetAutoLayout(1)
			self.SetSizer(szr_main)
			szr_main.Fit(self)
			self.Layout()
		#--------------------------------------------------------
		def __del__(self):
			self.DB.disconnect()
		#--------------------------------------------------------
		def __connect_to_db(self):
			# connect to DB
			self.DB = cDatabase(_cfg)
			if self.DB is None:
				_log.Log (gmLog.lErr, "cannot create document database connection object")
				return None

			if self.DB.connect() is None:
				_log.Log (gmLog.lErr, "cannot connect to document database")
				return None

			self.__conn = self.DB.getConn()
			return 1
		#--------------------------------------------------------
		def __get_pat_data(self):
			"""Get data of patient for which to retrieve documents.

			FIXME: Presumably, this should be configurable so that different
			client applications can provide patient data in their own way.
			"""
			# FIXME: error checking
			pat_file = os.path.abspath(os.path.expanduser(_cfg.get("viewer", "patient file")))
			pat_format = _cfg.get("viewer", "patient file format")
			self.__patient = cPatient()
			# get patient data from BDT file
			if not self.__patient.loadFromFile(pat_format, pat_file):
				_log.Log(gmLog.lErr, "problem with reading patient data from xDT file " + pat_file)
				self.__patient = None
				return None
			return 1
#== classes for plugin use ======================================
else:
	class cTreePanel(wxPanel):

		def __init__(self, parent, id, aConn = None, aPat = None):
			# this should actually set up it's own connection, too
			if aConn is None:
				_log.Log(gmLog.lErr, "Cannot work without database connection.")
				return None

			# FIXME: actually this needs to connect to the currently selected patient
			# FIXME: register interest in patient_changed signal, too
			if aPat is None:
				_log.Log(gmLog.lErr, "Cannot work without patient data.")
				return None

			# set up widgets
			wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize)
			#self.SetTitle(_("stored medical documents"))

			# make document tree
			self.tree = cDocTree(self, -1, aPat, aConn)
			self.tree.SelectItem(self.tree.root)

			sizer = wxBoxSizer(wxVERTICAL)
			sizer.Add(self.tree, 1, wxEXPAND, 0)
			self.SetAutoLayout(1)
			self.SetSizer(sizer)
			sizer.Fit(self)
			self.Layout()
		#--------------------------------------------------------
		def __del__(self):
			# FIXME: return service handle
			#self.DB.disconnect()
			pass
#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':
	_log.Log (gmLog.lInfo, "starting display handler")

	if _cfg == None:
		_log.Log(gmLog.lErr, "Cannot run without config file.")
		sys.exit("Cannot run without config file.")

	application = wxPyWidgetTester(size=(640,480))
	application.SetWidget(cStandalonePanel,-1)
	application.MainLoop()

	_log.Log (gmLog.lInfo, "closing display handler")
else:
	import gmPlugin

	#---------------------------------------------------------------
	class gmShowMedDocs(gmPlugin.wxNotebookPlugin):
		def name (self):
			return "Show"

		def GetWidget (self, parent):
			return wxPanel (parent, -1)

		def MenuInfo (self):
			return ('tools', '&Show Documents')
#================================================================
# $Log: show-med_docs.py,v $
# Revision 1.13  2002-12-23 08:51:29  ncq
# - the remove script belongs into import/ of course
#
# Revision 1.12  2002/12/22 11:50:20  ncq
# - removed useless _() wrapper
#
# Revision 1.11  2002/12/13 11:22:34  ncq
# - further pluginification and cleanup
#
# Revision 1.10  2002/12/05 22:43:51  ncq
# - changed to sizers
# - prepared for plugin()
#
