#!/usr/bin/env python

__version__ = ""
__author__ = "S.Hilbert, K.Hilbert"

import sys, os, string
# location of our modules
if __name__ == "__main__":
	#sys.path.append(os.path.join('..', '..', 'python-common'))
	#sys.path.append(os.path.join('..', '..', 'business'))
	sys.path.append(os.path.join('.','modules'))

import gmLog
_log = gmLog.gmDefLog
if __name__ == '__main__':
	_log.SetAllLogLevels(gmLog.lData)

_log.Log(gmLog.lData, __version__)

if __name__ == "__main__":
	import gmI18N

import gmCfg
_cfg = gmCfg.gmDefCfgFile


from wxPython.wx import *

[wxID_WXFRAME1, 
wxID_WXFRAME1NOTEBOOK1, 
wxID_WXFRAME1MAINPANEL, 
wxID_WXFRAME1STARTPANEL, 
wxID_WXFRAME1METADATAPANEL, 
wxID_WXFRAME1SCANPANEL, 
wxID_WXFRAME1INDEXPANEL, 
wxID_WXFRAME1IMPORTPANEL, 
wxID_WXFRAME1VIEWERPANEL,
wxID_WXFRAME1DATABASEPANEL,
wxID_WXFRAME1DUMPTOCFGFILEPANEL,
wxID_old_to_new_BTN,
wxID_new_to_old_BTN,
wxID_new_BTN,
wxID_old_to_new_rep_BTN,
wxID_new_to_old_rep_BTN,
wxID_check_metadata_BTN,
wxID_check_scan_BTN,
wxID_check_index_BTN,
wxID_check_import_BTN,
wxID_check_viewer_BTN,
wxID_check_database_BTN,
wxID_write_cfgfile_BTN,
wxID_new_rep_BTN,
wxID_tmp_dir_BTN,
wxID_export_dirBTN,
wxID_sel_idfile_BTN,
wxID_patient_fileBTN,
wxID_viewer_patient_fileBTN,
wxID_repository_dirBTN,
wxID_exit_BTN,
wxID_SelBOX_id_mode,
wxID_SelBOX_show_id,
wxID_SelBOX_do_barcodes,
wxID_SelBOX_JPEG_conv,
wxID_SelBOX_progressive_JPEG,
wxID_patient_format_view_LBOX,
wxID_patient_format_idx_LBOX,
wxID_patient_format_import_LBOX ] = map(lambda _init_ctrls: wxNewId(), range(39))

class gmConfigEditorPanel(wxPanel):
	def __init__(self, parent, aCfg = None):
		wxPanel.__init__(self, parent, -1)
		if aCfg is None:
			raise ValueError, "no config file given"
		self.cfg=aCfg
	
	def Populate(self):
		self.splitterwindow = wxSplitterWindow(self, -1)
		self.splitterwindow_right_pane = wxPanel(self.splitterwindow, -1)
		self.splitterwindow_left_pane = wxPanel(self.splitterwindow, -1)
		self.splitterwindow.SplitVertically(self.splitterwindow_left_pane, self.splitterwindow_right_pane,sashPosition = -100)
		self.parent_notebook = wxNotebook(self.splitterwindow_left_pane, -1, style=wxTAB_TRAVERSAL)
		self.CtrlsContainer = []
		# get the names of all the groups in a configfile and
		# add a notebook tab for each 
		groups  = self.cfg.getGroups()
		for group in groups:
			groupCtrlsList = {}
			# dynamically draw the rest
			panel_nb_page = wxPanel(
				parent = self.parent_notebook,
				id = -1,
				name = group,
				style = wxTAB_TRAVERSAL
			)

			# calculate rows automatically
			# -----------------------------
			# option | edit field | comment
			# -----------------------------
			fgszr_ctrls = wxFlexGridSizer(rows=0, cols=3, vgap=10, hgap=10)
			#fgszr_ctrls.AddGrowableCol(idx=0)
			fgszr_ctrls.AddGrowableCol(idx=1)
			fgszr_ctrls.AddGrowableCol(idx=2)
			# now get all available options in a group plus their descriptions
			# add descritiption and options as statictext
			options  = self.cfg.getOptions(group)
			# now get all available options in a group plus their descriptions
			# add description and options as statictext
			optionCtrlsList = {}
			for option in options:
				# option name == field label
				label = wxStaticText(parent=panel_nb_page, id=-1, label=option, style=wxALIGN_LEFT)
				fgszr_ctrls.Add(label)
				# edit field
				# FIXME: handle lists !  -> wxTE_MULTILINE
				if type (self.cfg.get(group, option)) is list :
					edit_field = wxTextCtrl(
						parent = panel_nb_page,
						id =  -1,
						value = "",
						style = wxTE_MULTILINE
						)
						
					for listoption in self.cfg.get(group, option):
						edit_field.AppendText(listoption)
				else:
					edit_field = wxTextCtrl(panel_nb_page, -1, str(self.cfg.get(group, option)))					
				optionCtrlsList[option] = edit_field
				fgszr_ctrls.Add(edit_field)
				# option comment
				tmp = str(string.join(self.cfg.getComment(group, option),"\n"))
				comment = wxStaticText(parent=panel_nb_page, id=-1, label=tmp, style=wxALIGN_LEFT)
				fgszr_ctrls.Add(comment)

			groupCtrlsList[group] = optionCtrlsList
			#append dictionary to a list
			self.CtrlsContainer.append(groupCtrlsList)
			# add page to notebook
			panel_nb_page.SetAutoLayout(1)
			panel_nb_page.SetSizer(fgszr_ctrls)
#			fgszr_ctrls.Fit(panel_nb_page)
#			fgszr_ctrls.SetSizeHints(panel_nb_page)
			self.parent_notebook.AddPage(panel_nb_page, group)
			# make notebook sizer work
			szr_nb = wxNotebookSizer(self.parent_notebook)
			# assemble parts into main window
			szr_main_pnl = wxBoxSizer(wxVERTICAL)
		
		szr_right_splitwindow = wxBoxSizer(wxVERTICAL)
		self.write_cfgfile_BTN  = wxButton (self.splitterwindow_right_pane,wxID_write_cfgfile_BTN,_('write configfile'))
		self.exit_BTN  = wxButton (self.splitterwindow_right_pane,wxID_exit_BTN,_('exit'))
		EVT_BUTTON(self.write_cfgfile_BTN, wxID_write_cfgfile_BTN, self.__dump_to_cfgfile)
		EVT_BUTTON(self.exit_BTN, wxID_exit_BTN, self.__exit)
		self.splitterwindow_left_pane.SetAutoLayout(1)
		self.splitterwindow_left_pane.SetSizer(szr_nb)
		szr_nb.Fit(self.splitterwindow_left_pane)
		szr_nb.SetSizeHints(self.splitterwindow_left_pane)
		szr_right_splitwindow.Add(self.write_cfgfile_BTN, 0, 0, 0)
		szr_right_splitwindow.Add(self.exit_BTN, 0, 0, 0)
		self.splitterwindow_right_pane.SetAutoLayout(1)
		self.splitterwindow_right_pane.SetSizer(szr_right_splitwindow)
		szr_right_splitwindow.Fit(self.splitterwindow_right_pane)
		szr_right_splitwindow.SetSizeHints(self.splitterwindow_right_pane)
		# the option edit notebook
		szr_main_pnl.Add(self.splitterwindow, 1, wxEXPAND, 0)
		self.SetAutoLayout(1)
		self.SetSizer(szr_main_pnl)
		szr_main_pnl.Fit(self)
		szr_main_pnl.SetSizeHints(self)
		self.Layout()
			
	def __dump_to_cfgfile(self, aDir):
		# retrieve individual dicts from list of groupdicts 
		for elementsdict in self.CtrlsContainer:
			#retrieve list of groupsnames ( key in each dict)  
			temp = elementsdict.keys()
			for groups in temp:
				#print groups
				# retrieve dict of options for this group 
				optionsdict = elementsdict[groups]
				temp = optionsdict.keys()
				for option in temp:
					if type (self.cfg.get(groups, option)) is list :
						tmp = optionsdict[option].GetValue()
						data = string.split(tmp,"\n")
					else:
						data = optionsdict[option].GetValue()
					self.cfg.set(groups,option,data)
				
	    	#self.cfg.store()
		
	def __exit(self,evt):
		sys.exit()

#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':
	_log.Log (gmLog.lInfo, "starting config editor")
	#---------------------
	# set up dummy app
	class TestApp (wxApp):
		def OnInit (self):
			aFilename = None
			# no config file found so far
			if _cfg is None:
				_log.Log(gmLog.lData, "No config file found. Use command line option --conf-file=<file name>")
				# get file name via file select dialog
				aWildcard = "%s (*.conf)|*.conf|%s (*.*)|*.*" % (_("config files"), _("all files"))
				aDefDir = os.path.abspath(os.path.expanduser('~'))
				dlg = wxFileDialog(
					parent = NULL,
					message = _("Choose a config file"),
					defaultDir = aDefDir,
					defaultFile = "",
					wildcard = aWildcard,
					style = wxOPEN | wxFILE_MUST_EXIST
				)
				if dlg.ShowModal() == wxID_OK:
					aFilename = dlg.GetPath()
				dlg.Destroy()
				_log.Log(gmLog.lData, 'selected [%s]' % aFilename)
				tmp = gmCfg.cCfgFile(aFile=aFilename)
			else:
				tmp = _cfg

			frame = wxFrame(
				parent=NULL,
				id = -1,
				title = _("configfile editor"),
				size = wxSize(800,600)
			)

			pnl = gmConfigEditorPanel(frame,aCfg=tmp)
			pnl.Populate()
			frame.Show(1)
			return 1
	#---------------------
	try:
		app = TestApp ()
		app.MainLoop ()
	except StandardError:
		_log.LogException('Unhandled exception.', sys.exc_info(), fatal=1)
		raise

else:
	import gmPlugin

	class gmConfigEditor(gmPlugin.wxNotebookPlugin):
		def name (self):
			return _("config")

		def GetWidget (self, parent):
			self.configeditor = gmConfigEditorPanel(parent)
			return self.viewer

		def MenuInfo (self):
			return ('tools', _('&configuration'))

		def ReceiveFocus(self):

#			self.viewer.filename = fname
#			self.viewer.Populate()
			return 1

#===========================================
# $Log: gmConfigeditor.py,v $
# Revision 1.11  2003-04-15 18:41:19  shilbert
# - now handles options as lists if applicable
#
# Revision 1.10  2003/04/15 02:31:13  ncq
# - some cleanup
#
# Revision 1.9  2003/04/14 20:47:04  shilbert
# - reworked layout, asks for file if none given
#
# Revision 1.8  2003/04/14 10:06:07  ncq
# - manually reworked sizers to make more sense
#
# Revision 1.7  2003/04/13 17:42:00  shilbert
# - typos in panel names fixed
#
# Revision 1.6  2003/04/13 17:37:47  shilbert
#  - now save changes
#
# Revision 1.5  2003/04/13 15:08:17  ncq
# - some cleanup, added comments
#
# Revision 1.4  2003/04/12 17:07:17  shilbert
# complete rewrite
# converted from static to dynamic
#
# Revision 1.3  2003/04/05 00:22:05  shilbert
# clean up
#