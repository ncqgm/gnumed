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
__version__ = "$Revision: 1.18 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
#================================================================
import os.path, sys, os

# location of our modules
if __name__ == '__main__':
	# CVS
	sys.path.append(os.path.join('..', '..', 'python-common'))
	sys.path.append(os.path.join('..', '..', 'business'))
	# UNIX installation
	sys.path.append('/usr/share/gnumed/python-common')
	sys.path.append('/usr/share/gnumed/business')
	# Windows
	sys.path.append(os.path.join('.', 'modules'))

import gmLog
_log = gmLog.gmDefLog
if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)

_log.Log(gmLog.lData, __version__)

if __name__ == "__main__":
	import gmI18N
else:
	import gmGuiBroker

import gmCfg
_cfg = gmCfg.gmDefCfgFile

import gmPG
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
		self.curr_pat = gmTmpPatient.gmCurrentPatient()

		# connect handler
		EVT_TREE_ITEM_ACTIVATED (self, self.GetId(), self.OnActivate)
	#------------------------------------------------------------------------
	def update(self):
		if self.curr_pat['ID'] is None:
			_log.Log(gmLog.lErr, 'need patient for update')
			self.__show_error(
				aMessage = _('Cannot load documents.\nYou first need to select a patient.'),
				aTitle = _('loading document list')
			)
			return None

		if self.doc_list is not None:
			del self.doc_list

		if self.__populate_tree() is None:
			return None

		return 1
	#------------------------------------------------------------------------
	def __populate_tree(self):
		# FIXME: check if patient changed at all

		# clean old tree
		if not self.root is None:
			self.DeleteAllItems()

		# init new tree
		self.root = self.AddRoot(_("available documents (most recent on top)"), -1, -1)
		self.SetPyData(self.root, None)
		self.SetItemHasChildren(self.root, FALSE)

		# read documents from database
		doc_ids = self.curr_pat['document id list']
		if doc_ids is None:
			name = self.curr_pat['active name']
			self.__show_error(
				aMessage = _('Cannot find any documents for the patient\n[%s %s].') % (name['first'], name['last']),
				aTitle = _('loading document list')
			)
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
				# id = doc_med.id for retrival
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

		if __name__ == "__main__":
			tmp = "unknown_machine"
		else:
			gb = gmGuiBroker.GuiBroker()
			tmp = gb['workplace_name']

		exp_base = self.__dbcfg.get(
			machine = tmp,
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
			self.__show_error(
				aMessage = _('Document part does not seem to exist in database !!'),
				aTitle = _('showing document')
			)
			return None

		if __name__ == "__main__":
			chunksize = None
		else:
			gb = gmGuiBroker.GuiBroker()
			chunksize = self.__dbcfg.get(
				machine = gb['workplace_name'],
				option = "doc export chunk size"
			)
		if chunksize is None:
			# 1 MB
			chunksize = 1 * 1024 * 1024

		# make sure metadata is there
		tmp = obj['metadata']

		# retrieve object
		if not obj.export_to_file(aTempDir = exp_base, aChunkSize = chunksize):
			_log.Log(gmLog.lErr, "Cannot export object [%s] data from database !" % node_data['id'])
			self.__show_error(
				aMessage = _('Cannot export document part from database to file.'),
				aTitle = _('showing document')
			)
			return None

		fname = obj['filename']
		(result, msg) = gmMedDoc.call_viewer_on_file(fname)
		if not result:
			self.__show_error(
				aMessage = _('Cannot display object.\n%s.') % msg,
				aTitle = _('displaying page')
			)
			return None
		return 1
	#--------------------------------------------------------
	def __show_error(self, aMessage = None, aTitle = ''):
		# sanity checks
		tmp = aMessage
		if aMessage is None:
			tmp = _('programmer forgot to specify error message')

		tmp = tmp + _("\n\nPlease consult the error log for further information !")

		dlg = wxMessageDialog(
			NULL,
			tmp,
			aTitle,
			wxOK | wxICON_ERROR
		)
		dlg.ShowModal()
		dlg.Destroy()
		return 1
#== classes for standalone use ==================================
if __name__ == '__main__':

	# FIXME !! - need to take care of new gmCurrentPatient() stuff

	import gmLoginInfo
	import gmXdtObjects
	from gmXdtMappings import xdt_gmgender_map

	class cStandalonePanel(wxPanel):

		def __init__(self, parent, id):
			# get patient from file
			if self.__get_pat_data() is None:
				raise ConstructorError, "Cannot load patient data."

			# set up database connectivity
			auth_data = gmLoginInfo.LoginInfo(
				user = _cfg.get('database', 'user'),
				passwd = _cfg.get('database', 'password'),
				host = _cfg.get('database', 'host'),
				port = _cfg.get('database', 'port'),
				database = _cfg.get('database', 'database')
			)
			backend = gmPG.ConnectionPool(login = auth_data)

			# mangle date of birth into ISO8601 (yyyymmdd) for Postgres
			cooked_search_terms = {
				'globbing': None,
				'case sensitive': None,
				'dob': '%s%s%s' % (self.__xdt_pat['dob year'], self.__xdt_pat['dob month'], self.__xdt_pat['dob day']),
				'last name': self.__xdt_pat['last name'],
				'first name': self.__xdt_pat['first name'],
				'gender': self.__xdt_pat['gender']
			}

			# find matching patient IDs
			patient_ids = gmTmpPatient.get_patient_ids(cooked_search_terms)
			if patient_ids is None:
				self.__show_error(
					aMessage = _('This patient does not exist in the document database.\n"%s %s"') % (self.__xdt_pat['first name'], self.__xdt_pat['last name']),
					aTitle = _('searching patient')
				)
				_log.Log(gmLog.lPanic, self.__xdt_pat['all'])
				raise ConstructorError, "Patient from XDT file does not exist in database."

			# ambigous ?
			if len(patient_ids) != 1:
				self.__show_error(
					aMessage = _('Data in xDT file matches more than one patient in database !'),
					aTitle = _('searching patient')
				)
				_log.Log(gmLog.lPanic, self.__xdt_pat['all'])
				raise ConstructorError, "Problem getting patient ID from database. Aborting."

			try:
				gm_pat = gmTmpPatient.gmCurrentPatient(aPKey = patient_ids[0])
			except:
				# this is an emergency
				self.__show_error(
					aMessage = _('Cannot load patient from database !\nAborting.'),
					aTitle = _('searching patient')
				)
				_log.Log(gmLog.lPanic, 'Cannot access patient [%s] in database.' % patient_ids[0])
				_log.Log(gmLog.lPanic, self.__xdt_pat['all'])
				raise

			# make main panel
			wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize)
			self.SetTitle(_("stored medical documents"))

			# make patient panel
			gender = gmTmpPatient.gm2long_gender_map[xdt_gmgender_map[self.__xdt_pat['gender']]]
			self.pat_panel = wxStaticText(
				id = -1,
				parent = self,
				label = "%s %s (%s), %s.%s.%s" % (self.__xdt_pat['first name'], self.__xdt_pat['last name'], gender, self.__xdt_pat['dob day'], self.__xdt_pat['dob month'], self.__xdt_pat['dob year']),
				style = wxALIGN_CENTER
			)
			self.pat_panel.SetFont(wxFont(25, wxSWISS, wxNORMAL, wxNORMAL, 0, ""))

			# make document tree
			self.tree = cDocTree(self, -1)
			self.tree.update()
			self.tree.SelectItem(self.tree.root)

			szr_main = wxBoxSizer(wxVERTICAL)
			szr_main.Add(self.pat_panel, 0, wxEXPAND, 1)
			szr_main.Add(self.tree, 1, wxEXPAND, 9)

			self.SetAutoLayout(1)
			self.SetSizer(szr_main)
			szr_main.Fit(self)
			self.Layout()
		#--------------------------------------------------------
		def __get_pat_data(self):
			"""Get data of patient for which to retrieve documents.

			"""
			# FIXME: error checking
			pat_file = os.path.abspath(os.path.expanduser(_cfg.get("viewer", "patient file")))
			# FIXME: actually handle pat_format, too
			pat_format = _cfg.get("viewer", "patient file format")

			# get patient data from BDT file
			try:
				self.__xdt_pat = gmXdtObjects.xdtPatient(anXdtFile = pat_file)
			except:
				_log.LogException('Cannot read patient from xDT file [%s].' % pat_file, sys.exc_info())
				self.__show_error(
					aMessage = _('Cannot load patient from xDT file\n[%s].') % pat_file,
					aTitle = _('loading patient from xDT file')
				)
				return None

			return 1
		#--------------------------------------------------------
		def __show_error(self, aMessage = None, aTitle = ''):
			# sanity checks
			tmp = aMessage
			if aMessage is None:
				tmp = _('programmer forgot to specify error message')

			tmp = tmp + _("\n\nPlease consult the error log for further information !")

			dlg = wxMessageDialog(
				NULL,
				tmp,
				aTitle,
				wxOK | wxICON_ERROR
			)
			dlg.ShowModal()
			dlg.Destroy()
			return 1
#== classes for plugin use ======================================
else:

	class cPluginTreePanel(wxPanel):
		def __init__(self, parent, id):
			# set up widgets
			wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize)

			# make document tree
			self.tree = cDocTree(self, -1)

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
			return _("Documents")

		def GetWidget (self, parent):
			self.panel = cPluginTreePanel(parent, -1)
			return self.panel

		def MenuInfo (self):
			return ('tools', _('Show &archived documents'))

		def ReceiveFocus(self):
			# get patient object
			if self.panel.tree.update() is None:
				_log.Log(gmLog.lErr, "cannot update document tree")
				return None
			# FIXME: register interest in patient_changed signal, too
			self.panel.tree.SelectItem(self.panel.tree.root)

#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':
	_log.Log (gmLog.lInfo, "starting display handler")

	if _cfg is None:
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
# Revision 1.18  2003-04-18 16:40:04  ncq
# - works again as standalone
#
# Revision 1.17  2003/04/04 20:49:22  ncq
# - make plugin work with gmCurrentPatient
#
# Revision 1.16  2003/04/01 12:31:53  ncq
# - we can't use constant reference self.patient if we don't register interest
#   in gmSignals.patient_changed, hence, acquire patient when needed
#
# Revision 1.15  2003/03/25 19:57:09  ncq
# - add helper __show_error()
#
# Revision 1.14  2003/03/23 02:38:46  ncq
# - updated Hilmar's fix
#
# Revision 1.13  2003/03/02 17:03:19  ncq
# - make sure metadata is retrieved
#
# Revision 1.12  2003/03/02 11:13:01  hinnef
# preliminary fix for crash on ReceiveFocus()
#
# Revision 1.11  2003/02/25 23:30:31  ncq
# - need sys.exc_info() in LogException
#
# Revision 1.10  2003/02/24 23:14:53  ncq
# - adapt to get_patient_ids actually returning a flat list of IDs now
#
# Revision 1.9  2003/02/21 13:54:17  ncq
# - added even more likely and unlikely user warnings
#
# Revision 1.8  2003/02/20 01:25:18  ncq
# - read login data from config file again
#
# Revision 1.7  2003/02/19 15:19:43  ncq
# - remove extra print()
#
# Revision 1.6  2003/02/18 02:45:21  ncq
# - almost fixed standalone mode again
#
# Revision 1.5  2003/02/17 16:10:50  ncq
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
