#!/usr/bin/env python
#----------------------------------------------------------------------
"""
This is a no-frills document display handler for the
GNUmed medical document database.

It knows nothing about the documents itself. All it does
is to let the user select a page to display and tries to
hand it over to an appropriate viewer.

For that it relies on mime types.
"""
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/blobs_hilbert/viewer-tree/Attic/show-med_docs.py,v $
__version__ = "$Revision: 1.8 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
#----------------------------------------------------------------------
import os.path, sys, os

from wxPython import wx

# location of our modules
sys.path.append(os.path.join('.', 'modules'))

from docPatient import cPatient, gm2long_gender_map
from docDatabase import cDatabase
import docMime, docDocument

import gmLog, gmCfg, gmI18N
#----------------------------------------------------------------------
_log = gmLog.gmDefLog
_cfg = gmCfg.gmDefCfgFile

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

class cDocTree(wx.wxTreeCtrl):
	"""
	This wxTreeCtrl derivative displays a tree view of a Python namespace.
	Anything from which the dir() command returns a non-empty list is a branch
	in this tree.
	"""

	def __init__(self, parent, id, aPatient = None, aConn = None):
		"""Set up our specialised tree.
		"""
		# sanity checks
		if aPatient == None:
			_log.Log(gmLog.lErr, "Cannot retrieve documents without knowing the patient !")
			return None

		if aConn == None:
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
		if self.doc_list == None:
			_log.Log(gmLog.lErr, "Cannot find any documents.")
			return None

		wx.wxTreeCtrl.__init__(self, parent, id, style=wx.wxTR_NO_BUTTONS)

		# build tree from document list
		self.root = self.AddRoot(_("available documents"), -1, -1)
		self.SetPyData(self.root, None)
		self.SetItemHasChildren(self.root, wx.TRUE)

		# add our documents as first level nodes
		for doc_id in self.doc_list.keys():
			doc = self.doc_list[doc_id]
			mdata = doc.getMetaData()
			c = mdata['comment'] + " " * 25
			r = mdata['reference'] + " " * 10
			tmp = _("date: %s | comment: %s | reference: %s")
			label =  tmp % (mdata['date'][:10], c[:25], r[:10])
			doc_node = self.AppendItem(self.root, label)
			# we need to distinguish documents from objects in OnActivate
			# this is ugly
			data = {'doc_id': doc_id,
					'id'	: doc_id}
			self.SetPyData(doc_node, data)
			self.SetItemHasChildren(doc_node, wx.TRUE)

			# now add objects as child nodes
			i = 1
			for oid in mdata['objects'].keys():
				obj = mdata['objects'][oid]
				p = str(i) +  " "
				c = str(obj['comment'])
				if c == "None":
					c = "no comment available"
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

		wx.EVT_TREE_ITEM_ACTIVATED (self, self.GetId(), self.OnActivate)
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
				_('Cannot display page %s.\n%s') % (page_idx+1, msg),
				_('displaying page'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None
		return 1
#------------------------------------------------------------------------
class MyFrame(wx.wxFrame):
	"""Very standard Frame class. Nothing special here!"""

	def __init__(self):
		if self.__connect_to_db() == None:
			_log.Log (gmLog.lErr, "No need to work without being able to connect to database.")
			return None

		aPat = self.__get_pat_data()
		if aPat == None:
			_log.Log (gmLog.lErr, "Cannot get patient data.")
			return None

		# setup basic frame
		wx.wxFrame.__init__(self, None, -1, _("stored medical documents"), wx.wxDefaultPosition, wx.wxSize(800,500))

		# make split window
		split_win = wx.wxSplitterWindow(self, -1)

		# make patient panel
		title = "%s %s (%s), %s" % (aPat.firstnames, aPat.lastnames, gm2long_gender_map[aPat.gender], aPat.dob)
		# FIXME: adjust font + bold + size
		pat_panel = wx.wxStaticText(split_win, -1, title, wx.wxDefaultPosition, wx.wxDefaultSize, wx.wxALIGN_LEFT)

		# make document tree
		tree = cDocTree(split_win, -1, aPat, self.__conn)
		tree.SelectItem(tree.root)

		# place widgets in window
		split_win.SplitHorizontally(pat_panel, tree, 50)
	#------------------------------------------------------------------------
	def __del__(self):
		self.DB.disconnect()
	#--------------------------------------------------------------
	def __connect_to_db(self):
		# connect to DB
		self.DB = cDatabase(_cfg)
		if self.DB == None:
			_log.Log (gmLog.lErr, "cannot create document database connection object")
			return None

		if self.DB.connect() == None:
			_log.Log (gmLog.lErr, "cannot connect to document database")
			return None

		self.__conn = self.DB.getConn()
		return (1==1)
	#--------------------------------------------------------------
	def __get_pat_data(self):
		"""Get data of patient for which to retrieve documents.

		Presumably, this should be configurable so that different
		client applications can provide patient data in their own way.
		"""
		# FIXME: error checking
		pat_file = _cfg.get("viewer", "patient file")
		pat_format = _cfg.get("viewer", "patient file format")
		aPatient = cPatient()
		# FIXME: the method of getting the patient should be configurable
		# get patient data from BDT file
		if not aPatient.loadFromFile(pat_format, os.path.abspath(os.path.expanduser(pat_file))):
			_log.Log(gmLog.lErr, "problem with reading patient data from xDT file " + pat_file)
			return None

		return aPatient
#------------------------------------------------------------------
class MyApp(wx.wxApp):
	"""This class is even less interesting than MyFrame."""

	def OnInit(self):
		"""OnInit. Boring, boring, boring!"""
		frame = MyFrame()
		frame.Show(wx.TRUE)
		self.SetTopWindow(frame)
		return wx.TRUE
#----------------------------------------------------------------
# MAIN
#----------------------------------------------------------------
_log.Log (gmLog.lInfo, "starting display handler")
_log.SetAllLogLevels(gmLog.lData)

if _cfg == None:
	_log.Log(gmLog.lErr, "Cannot run without config file.")
	sys.exit("Cannot run without config file.")

if __name__ == '__main__':
	app = MyApp(0)
	app.MainLoop()

_log.Log (gmLog.lInfo, "closing display handler")
