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
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gui/gmShowMedDocs.py,v $
__version__ = "$Revision: 1.5 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
#================================================================
import os.path, sys, os

# location of our modules
if __name__ == '__main__':
	sys.path.append(os.path.join('..', '..', 'python-common'))
	sys.path.append(os.path.join('..', '..', 'business'))

import gmLog
_log = gmLog.gmDefLog
if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)

_log.Log(gmLog.lData, __version__)

if __name__ == "__main__":
	import gmI18N

import gmCfg
_cfg = gmCfg.gmDefCfgFile

import gmPG, gmGuiBroker
import gmTmpPatient, gmMedDoc
from gmExceptions import ConstructorError

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
	def __init__(self, parent, id):
		"""Set up our specialised tree.
		"""
		# get connection
		self.__backend = gmPG.ConnectionPool()
		self.__defconn = self.__backend.GetConnection('blobs')
		if self.__defconn is None:
			_log.Log(gmLog.lErr, "Cannot retrieve documents without database connection !")
			raise ConstructorError, "cDocTree.__init__(): need db conn"

		# connect to config database
		self.__dbcfg = gmCfg.cCfgSQL(
			aConn = self.__backend.GetConnection('default'),
			aDBAPI = gmPG.dbapi
		)

		wxTreeCtrl.__init__(self, parent, id, style=wxTR_NO_BUTTONS)

		self.root = None
		self.doc_list = None

		# connect handler
		EVT_TREE_ITEM_ACTIVATED (self, self.GetId(), self.OnActivate)
	#------------------------------------------------------------------------
	def update(self, aPatient = None):
		if aPatient is None:
			_log.Log(gmLog.lErr, 'need patient object for update')
			return None
		self.pat = aPatient

		if self.doc_list is not None:
			del self.doc_list

		if self.__populate_tree() is None:
			return None

		return 1
	#------------------------------------------------------------------------
	def __populate_tree(self):
		# FIXME: check if patient changed at all ?

		# clean old tree
		if not self.root is None:
			self.DeleteAllItems()

		# init new tree
		self.root = self.AddRoot(_("available documents (most recent on top)"), -1, -1)
		self.SetPyData(self.root, None)
		self.SetItemHasChildren(self.root, FALSE)

		# read documents from database
		doc_ids = self.pat['document id list']
		if doc_ids is None:
			name = self.pat['active name']
			dlg = wxMessageDialog(
				self,
				_('Cannot find any documents for the patient\n[%s %s].') % (name['first'], name['last']),
				_('searching patient documents'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None

		# fill new tree from document list
		self.SetItemHasChildren(self.root, TRUE)

		# add our documents as first level nodes
		self.doc_list = {}
		for doc_id in doc_ids:
			try:
				doc = gmMedDoc.gmMedDoc(aPKey = doc_id)
			except:
				continue

			self.doc_list[doc_id] = doc

			mdata = doc['metadata']
			date = '%10s' % mdata['date'] + " " * 10
			typ = '%s' % mdata['type'] + " " * 25
			cmt = '"%s"' % mdata['comment'] + " " * 25
			ref = mdata['reference'] + " " * 15
			page_num = str(len(mdata['objects']))
			tmp = _('%s %s: %s (%s pages, %s)')
			# FIXME: handle date correctly
			label =  tmp % (date[:10], typ[:25], cmt[:25], page_num, ref[:15])
			doc_node = self.AppendItem(self.root, label)
			self.SetItemBold(doc_node, bold=TRUE)
			# id: doc_med.id for access
			# date: for sorting
			data = {
				'type': 'document',
				'id': doc_id,
				'date': mdata['date']
			}
			self.SetPyData(doc_node, data)
			self.SetItemHasChildren(doc_node, TRUE)

			# now add objects as child nodes
			i = 1
			for obj_id in mdata['objects'].keys():
				obj = mdata['objects'][obj_id]
				p = str(obj['index']) +  " "
				c = str(obj['comment'])
				s = str(obj['size'])
				if c == "None":
					c = _("no comment available")
				tmp = _('page %s: \"%s\" (%s bytes)')
				label = tmp % (p[:2], c, s)
				obj_node = self.AppendItem(doc_node, label)
				# id = doc_med.id for retrieval
				# seq_idx for sorting
				data = {
					'type': 'object',
					'id': obj_id,
					'seq_idx'	: obj['index']
				}
				self.SetPyData(obj_node, data)
				i += 1
			# and expand
			#self.Expand(doc_node)

		# and uncollapse
		self.Expand(self.root)

		return 1
	#------------------------------------------------------------------------
	def OnCompareItems (self, item1, item2):
		"""Used in sorting items.

		-1 - 1 < 2
		 0 - 1 = 2
		 1 - 1 > 2
		"""
		data1 = self.GetPyData(item1)
		data2 = self.GetPyData(item2)

		# doc node
		if data1['type'] == 'document':
			# compare dates
			if data1['date'] > data2['date']:
				return -1
			elif data1['date'] == data2['date']:
				return 0
			return 1
		# object node
		else:
			# compare sequence IDs (= "page number")
			if data1['seq_idx'] < data2['seq_idx']:
				return -1
			elif data1['seq_idx'] == data2['seq_idx']:
				return 0
			return 1
	#------------------------------------------------------------------------
	def OnActivate (self, event):
		item = event.GetItem()
		node_data = self.GetPyData(item)

		# exclude pseudo root node
		if node_data is None:
			return None

		# do nothing with documents yet
		if node_data['type'] == 'document':
			return None

		# but do everything with objects
		obj_id = node_data['id']
		_log.Log(gmLog.lData, "User selected object [%s]" % obj_id)

		gb = gmGuiBroker.GuiBroker()
		exp_base = self.__dbcfg.get(
			machine = gb['workplace_name'],
			option = "doc export dir"
		)
		if exp_base is None:
			exp_base = ''
		else:
			exp_base = os.path.abspath(os.path.expanduser(exp_base))
		if not os.path.exists(exp_base):
			_log.Log(gmLog.lErr, "The directory [%s] does not exist ! Falling back to default temporary directory." % exp_base) # which is tempfile.tempdir == None == use system defaults
		else:
			_log.Log(gmLog.lData, "working into directory [%s]" % exp_base)

		# instantiate object
		try:
			obj = gmMedDoc.gmMedObj(aPKey = obj_id)
		except:
			_log.LogException('Cannot instantiate object [%s]' % obj_id, sys.exc_info())
			return None

		chunksize = self.__dbcfg.get(
			machine = gb['workplace_name'],
			option = "doc export chunk size"
		)
		if chunksize is None:
			# 1 MB
			chunksize = 1 * 1024 * 1024

		# retrieve object
		if not obj.export_to_file(aTempDir = exp_base, aChunkSize = chunksize):
			_log.Log(gmLog.lErr, "Cannot export object [%s] data from database !" % node_data['id'])
			return None

		fname = obj['filename']
		(result, msg) = gmMedDoc.call_viewer_on_file(fname)
		if not result:
			dlg = wxMessageDialog(
				self,
				_('Cannot display object.\n%s.') % msg,
				_('displaying page'),
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return None
		return 1
#== classes for standalone use ==================================
if __name__ == '__main__':

	#import docPatient
	from docDatabase import cDatabase
	import docMime, docDocument

	class cStandalonePanel(wxPanel):

		def __init__(self, parent, id):
			if self.__connect_to_db() is None:
				_log.Log (gmLog.lErr, "No need to work without being able to connect to database.")
				raise AssertionError, "database connection needed"

			if self.__get_pat_data() is None:
				_log.Log (gmLog.lErr, "Cannot load patient data.")
				raise AssertionError, "Cannot load patient data."

			# make sure aPatient knows its ID
			result = aPatient.getIDfromGNUmed(self.__defconn)
			if not result[0]:
				if result[1] is None:
					dlg = wxMessageDialog(
						parent,
						_('This patient does not exist in the document database.\n"%s %s"') % (aPatient.firstnames, aPatient.lastnames),
						_('searching patient documents'),
						wxOK | wxICON_ERROR
					)
					dlg.ShowModal()
					dlg.Destroy()
					raise AssertionError
				else:
					_log.Log(gmLog.lErr, "Patient data is ambigous. Aborting. (IDs: %s)" % str(result[1]))
					raise AssertionError
			else:
				_log.Log(gmLog.lInfo, "Making document tree for patient with ID %s" % result[1])

			wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize)
			self.SetTitle(_("stored medical documents"))

			# make patient panel
			self.pat_panel = wxStaticText(
				id = -1,
				parent = self,
				label = "%s %s (%s), %s" % (self.__patient.firstnames, self.__patient.lastnames, docPatient.gm2long_gender_map[self.__patient.gender], self.__patient.dob),
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

			"""
			# FIXME: error checking
			pat_file = os.path.abspath(os.path.expanduser(_cfg.get("viewer", "patient file")))
			pat_format = _cfg.get("viewer", "patient file format")
			self.__patient = docPatient.cPatient()
			# get patient data from BDT file
			if not self.__patient.loadFromFile(pat_format, pat_file):
				_log.Log(gmLog.lErr, "problem with reading patient data from xDT file " + pat_file)
				self.__patient = None
				return None
			return 1
#== classes for plugin use ======================================
else:
	#------------------------------------------------------------
	class cPluginTreePanel(wxPanel):
		def __init__(self, parent, id):
			# set up widgets
			wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize)

			# make document tree
			self.tree = cDocTree(self, -1)
			#self.tree.update(self.__pat)

			# just one vertical sizer
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
	#------------------------------------------------------------
	import gmPlugin

	class gmShowMedDocs(gmPlugin.wxNotebookPlugin):
		def name (self):
			return _("Archive")

		def GetWidget (self, parent):
			self.panel = cPluginTreePanel(parent, -1)
			return self.panel

		def MenuInfo (self):
			return ('tools', _('&Show documents in archive'))

		def ReceiveFocus(self):
			# get patient object
			# FIXME: should be done in __init__()
			self.__pat = gmTmpPatient.gmDefPatient
			if self.__pat is None:
				_log.Log(gmLog.lErr, "Cannot work without patient object.")
				#raise ConstructorError, "cPluginTreePanel.__init__(): need patient object"
			# FIXME: register interest in patient_changed signal, too

			self.panel.tree.update(self.__pat)
			self.panel.tree.SelectItem(self.panel.tree.root)

#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':
	_log.Log (gmLog.lInfo, "starting display handler")

	if _cfg == None:
		_log.Log(gmLog.lErr, "Cannot run without config file.")
		sys.exit("Cannot run without config file.")

	# catch all remaining exceptions
	try:
		application = wxPyWidgetTester(size=(640,480))
		application.SetWidget(cStandalonePanel,-1)
		application.MainLoop()
	except:
		_log.LogException("unhandled exception caught !", sys.exc_info(), fatal=1)
		# but re-raise them
		raise

	_log.Log (gmLog.lInfo, "closing display handler")
else:
	# we are being imported
	pass
#================================================================
# $Log: gmShowMedDocs.py,v $
# Revision 1.5  2003-02-17 16:10:50  ncq
# - plugin mode seems to be fully working, actually calls viewers on files
#
# Revision 1.4  2003/02/15 14:21:49  ncq
# - on demand loading of Manual
# - further pluginization of showmeddocs
#
# Revision 1.3  2003/02/11 18:26:16  ncq
# - fix exp_base buglet in OnActivate
#
# Revision 1.2  2003/02/09 23:41:09  ncq
# - reget doc list on receiving focus thus being able to react to selection of a different patient
#
# Revision 1.1  2003/02/09 20:07:31  ncq
# - works as a plugin, patient hardcoded, though
#
# Revision 1.8  2003/01/26 17:00:18  ncq
# - support chunked object retrieval
#
# Revision 1.7  2003/01/25 00:21:42  ncq
# - show nr of bytes on object in metadata :-)
#
