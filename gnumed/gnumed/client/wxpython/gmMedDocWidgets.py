"""GnuMed medical document handling widgets.
"""
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmMedDocWidgets.py,v $
__version__ = "$Revision: 1.1 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
#================================================================
import os.path, sys, re

from wxPython.wx import *

from Gnumed.pycommon import gmLog, gmI18N, gmCfg, gmWhoAmI, gmPG, gmMimeLib, gmExceptions
from Gnumed.business import gmPatient, gmMedDoc
from Gnumed.wxpython import gmGuiHelpers

_log = gmLog.gmDefLog
_cfg = gmCfg.gmDefCfgFile
_whoami = gmWhoAmI.cWhoAmI()

if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)
else:
	from Gnumed.pycommon import gmGuiBroker

_log.Log(gmLog.lInfo, __version__)

[	wxID_PNL_main,
	wxID_TB_BTN_show_page
] = map(lambda _init_ctrls: wxNewId(), range(2))

#		 self.tree = MyTreeCtrl(self, tID, wxDefaultPosition, wxDefaultSize,
#								wxTR_HAS_BUTTONS | wxTR_EDIT_LABELS# | wxTR_MULTIPLE
#								, self.log)

		# NOTE:	 For some reason tree items have to have a data object in
		#		 order to be sorted.  Since our compare just uses the labels
		#		 we don't need any real data, so we'll just use None.

#		 EVT_TREE_ITEM_EXPANDED	 (self, tID, self.OnItemExpanded)
#		 EVT_TREE_ITEM_COLLAPSED (self, tID, self.OnItemCollapsed)
#		 EVT_TREE_SEL_CHANGED	 (self, tID, self.OnSelChanged)
#		 EVT_TREE_BEGIN_LABEL_EDIT(self, tID, self.OnBeginEdit)
#		 EVT_TREE_END_LABEL_EDIT (self, tID, self.OnEndEdit)
#		 EVT_TREE_ITEM_ACTIVATED (self, tID, self.OnActivate)

#		 EVT_LEFT_DCLICK(self.tree, self.OnLeftDClick)

#============================================================
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
			raise gmExceptions.ConstructorError, "cDocTree.__init__(): need db conn"

		# connect to config database
		self.__dbcfg = gmCfg.cCfgSQL(
			aConn = self.__backend.GetConnection('default'),
			aDBAPI = gmPG.dbapi
		)

		wxTreeCtrl.__init__(self, parent, id, style=wxTR_NO_BUTTONS)

		self.root = None
		self.doc_list = None
		self.curr_pat = gmPatient.gmCurrentPatient()
		_log.Log(gmLog.lData, self.curr_pat)
		# connect handlers
		EVT_TREE_ITEM_ACTIVATED (self, self.GetId(), self.OnActivate)
		EVT_TREE_ITEM_RIGHT_CLICK(self, self.GetId(), self.__on_right_click)
	#------------------------------------------------------------------------
	def update(self):
		if self.curr_pat['ID'] is None:
			_log.Log(gmLog.lErr, 'need patient for update')
			gmGuiHelpers.gm_show_error(
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
		docs_folder = self.curr_pat.get_document_folder()
		doc_ids = docs_folder.get_doc_list()
		if doc_ids is None:
			name = self.curr_pat['demographic record'].get_names()
			gmGuiHelpers.gm_show_error(
				aMessage = _('Cannot find any documents for patient\n[%s %s].') % (name['first'], name['last']),
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
			mdata = doc.get_metadata()
			date = '%10s' % mdata['date'] + " " * 10
			typ = '%s' % mdata['type'] + " " * 25
			cmt = '"%s"' % mdata['comment'] + " " * 25
			ref = mdata['reference'] + " " * 15
			page_num = str(len(mdata['objects']))
			tmp = _('%s %s: %s (%s pages, %s)')
			# FIXME: handle date correctly
			label =	 tmp % (date[:10], typ[:25], cmt[:25], page_num, ref[:15])
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
				p = str(obj['index']) +	 " "
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
			tmp = _whoami.get_workplace()

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
			gmGuiHelpers.gm_show_error(
				aMessage = _('Document part does not seem to exist in database !!'),
				aTitle = _('showing document')
			)
			return None

		if __name__ == "__main__":
			chunksize = None
		else:
			gb = gmGuiBroker.GuiBroker()
			chunksize = self.__dbcfg.get(
				machine = _whoami.get_workplace(),
				option = "doc export chunk size"
			)
		if chunksize is None:
			# 1 MB
			chunksize = 1 * 1024 * 1024

		# make sure metadata is there
		tmp = obj.get_metadata()

		# retrieve object
		fname = obj.export_to_file(aTempDir = exp_base, aChunkSize = chunksize)
		if fname is None:
			_log.Log(gmLog.lErr, "Cannot export object [%s] data from database !" % node_data['id'])
			gmGuiHelpers.gm_show_error(
				aMessage = _('Cannot export document part from database to file.'),
				aTitle = _('showing document')
			)
			return None

		(result, msg) = gmMimeLib.call_viewer_on_file(fname)
		if not result:
			gmGuiHelpers.gm_show_error(
				aMessage = _('Cannot display object.\n%s.') % msg,
				aTitle = _('displaying page')
			)
			return None
		return 1
	#--------------------------------------------------------
	def __on_right_click(self, evt):
		item = evt.GetItem()
		node_data = self.GetPyData(item)

		# exclude pseudo root node
		if node_data is None:
			return None

		# objects
		if node_data['type'] == 'object':
			self.__handle_obj_context(node_data)

		# documents
		if node_data['type'] == 'document':
			self.__handle_doc_context(node_data)

		evt.Skip()
	#--------------------------------------------------------
	def __handle_doc_context(self, data):
		doc_id = data['id']
		try:
			doc = gmMedDoc.gmMedDoc(aPKey = doc_id)
		except:
			_log.LogException('Cannot init document [%s]' % doc_id, sys.exc_info())
			# FIXME: message box
			return None

		descriptions = doc['descriptions']

		# build menu
		wxIDs_desc = []
		desc_menu = wxMenu()
		for desc in descriptions:
			d_id = wxNewId()
			wxIDs_desc.append(d_id)
			# contract string
			tmp = re.split('\r\n+|\r+|\n+|\s+|\t+', desc)
			tmp = string.join(tmp, ' ')
			# but only use first 30 characters
			tmp = "%s ..." % tmp[:30]
			desc_menu.AppendItem(wxMenuItem(desc_menu, d_id, tmp))
			# connect handler
			EVT_MENU(desc_menu, d_id, self.__show_description)
		wxID_load_submenu = wxNewId()
		menu = wxMenu(title = _('document menu'))
		menu.AppendMenu(wxID_load_submenu, _('descriptions ...'), desc_menu)
		self.PopupMenu(menu, wxPyDefaultPosition)
		menu.Destroy()
	#--------------------------------------------------------
	def __show_description(self, evt):
		print "showing description"
	#--------------------------------------------------------
	def __handle_obj_context(self, data):
		print "handling object context menu"
#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':
	print "please write a unit test"

#============================================================
# $Log: gmMedDocWidgets.py,v $
# Revision 1.1  2004-06-26 23:39:34  ncq
# - factored out widgets for re-use
#
