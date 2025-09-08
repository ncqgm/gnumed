"""GNUmed measurement widgets."""
#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"


import sys
import logging
import datetime as pyDT
import decimal
import os
import os.path


import wx
import wx.grid
import wx.adv as wxh


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmNetworkTools
from Gnumed.pycommon import gmCfgDB
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmMatchProvider
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmMimeLib

from Gnumed.business import gmPerson
from Gnumed.business import gmStaff
from Gnumed.business import gmPathLab
from Gnumed.business import gmPraxis
from Gnumed.business import gmLOINC
from Gnumed.business import gmForms
from Gnumed.business import gmPersonSearch
from Gnumed.business import gmOrganization
from Gnumed.business import gmHL7
from Gnumed.business import gmIncomingData
from Gnumed.business import gmDocuments

from Gnumed.wxpython import gmRegetMixin
from Gnumed.wxpython import gmPlugin
from Gnumed.wxpython import gmEditArea
from Gnumed.wxpython import gmPhraseWheel
from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmOrganizationWidgets
from Gnumed.wxpython import gmEMRStructWidgets
from Gnumed.wxpython import gmCfgWidgets
from Gnumed.wxpython import gmDocumentWidgets
from Gnumed.wxpython import gmFormWidgets


_log = logging.getLogger('gm.ui')

#================================================================
# HL7 related widgets
#================================================================
def show_hl7_file(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	# select file
	paths = gmTools.gmPaths()
	dlg = wx.FileDialog (
		parent = parent,
		message = _('Show HL7 file:'),
		# make configurable:
		defaultDir = paths.user_work_dir,
		wildcard = "hl7 files|*.hl7|HL7 files|*.HL7|all files|*",
		style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
	)
	choice = dlg.ShowModal()
	hl7_name = dlg.GetPath()
	dlg.DestroyLater()
	if choice != wx.ID_OK:
		return False

	formatted_name = gmHL7.format_hl7_file (
		hl7_name,
		skip_empty_fields = True,
		return_filename = True,
		fix_hl7 = True
	)
	gmMimeLib.call_viewer_on_file(aFile = formatted_name, block = False)
	return True

#================================================================
def unwrap_HL7_from_XML(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	# select file
	paths = gmTools.gmPaths()
	dlg = wx.FileDialog (
		parent = parent,
		message = _('Extract HL7 from XML file:'),
		# make configurable:
		defaultDir = paths.user_work_dir,
		wildcard = "xml files|*.xml|XML files|*.XML|all files|*",
		style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
	)
	choice = dlg.ShowModal()
	xml_name = dlg.GetPath()
	dlg.DestroyLater()
	if choice != wx.ID_OK:
		return False

	target_dir = os.path.split(xml_name)[0]
	xml_path = './/Message'
	hl7_name = gmHL7.extract_HL7_from_XML_CDATA(xml_name, xml_path, target_dir = target_dir)
	if hl7_name is None:
		gmGuiHelpers.gm_show_error (
			title = _('Extracting HL7 from XML file'),
			error = (
			'Cannot unwrap HL7 data from XML file\n'
			'\n'
			' [%s]\n'
			'\n'
			'(CDATA of [%s] nodes)'
			) % (
				xml_name,
				xml_path
			)
		)
		return False

	gmDispatcher.send(signal = 'statustext', msg = _('Unwrapped HL7 into [%s] from [%s].') % (hl7_name, xml_name), beep = False)
	return True

#================================================================
def stage_hl7_file(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	paths = gmTools.gmPaths()
	dlg = wx.FileDialog (
		parent = parent,
		message = _('Select HL7 file for staging:'),
		# make configurable:
		defaultDir = paths.user_work_dir,
		wildcard = ".hl7 files|*.hl7|.HL7 files|*.HL7|all files|*",
		style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
	)
	choice = dlg.ShowModal()
	hl7_name = dlg.GetPath()
	dlg.DestroyLater()
	if choice != wx.ID_OK:
		return False

	target_dir = os.path.join(paths.user_tmp_dir, 'hl7')
	success, PID_names = gmHL7.split_hl7_file(hl7_name, target_dir = target_dir, encoding = 'utf8')
	if not success:
		gmGuiHelpers.gm_show_error (
			title = _('Staging HL7 file'),
			error = _(
				'There was a problem with splitting the HL7 file\n'
				'\n'
				' %s'
			) % hl7_name
		)
		return False

	failed_files = []
	for PID_name in PID_names:
		if not gmHL7.stage_single_PID_hl7_file(PID_name, source = _('generic'), encoding = 'utf8'):
			failed_files.append(PID_name)
	if len(failed_files) > 0:
		gmGuiHelpers.gm_show_error (
			title = _('Staging HL7 file'),
			error = _(
				'There was a problem with staging the following files\n'
				'\n'
				' %s'
			) % '\n '.join(failed_files)
		)
		return False

	gmDispatcher.send(signal = 'statustext', msg = _('Staged HL7 from [%s].') % hl7_name, beep = False)
	return True

#================================================================
def browse_incoming(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	#------------------------------------------------------------
	def show_hl7(staged_item):
		if staged_item is None:
			return False
		if 'HL7' not in staged_item['data_type']:
			return False
		filename = staged_item.save_to_file()
		if filename is None:
			filename = gmTools.get_unique_filename()
		tmp_file = open(filename, mode = 'at', encoding = 'utf8')
		tmp_file.write('\n')
		tmp_file.write('-' * 80)
		tmp_file.write('\n')
		tmp_file.write(gmTools.coalesce(staged_item['comment'], ''))
		tmp_file.close()
		gmMimeLib.call_viewer_on_file(aFile = filename, block = False)
		return False
	#------------------------------------------------------------
	def import_hl7(staged_item):
		if staged_item is None:
			return False
		if 'HL7' not in staged_item['data_type']:
			return False
		unset_identity_on_error = False
		if staged_item['pk_identity'] is None:
			pat = gmPerson.gmCurrentPatient()
			if pat.connected:
				answer = gmGuiHelpers.gm_show_question (
					title = _('Importing HL7 data'),
					question = _(
						'There has not been a patient explicitly associated\n'
						'with this chunk of HL7 data. However, the data file\n'
						'contains the following patient identification information:\n'
						'\n'
						' %s\n'
						'\n'
						'Do you want to import the HL7 under the current patient ?\n'
						'\n'
						' %s\n'
						'\n'
						'Selecting [NO] makes GNUmed try to find a patient matching the HL7 data.\n'
					) % (
						staged_item.patient_identification,
						pat.description_gender
					),
					cancel_button = True
				)
				if answer is None:
					return False
				if answer is True:
					unset_identity_on_error = True
					staged_item['pk_identity'] = pat.ID

		success, log_name = gmHL7.process_staged_single_PID_hl7_file(staged_item)
		if success:
			return True

		if unset_identity_on_error:
			staged_item['pk_identity'] = None
			staged_item.save()

		gmGuiHelpers.gm_show_error (
			error = _('Error processing HL7 data.'),
			title = _('Processing staged HL7 data.')
		)
		return False

	#------------------------------------------------------------
	def delete(staged_item):
		if staged_item is None:
			return False
		do_delete = gmGuiHelpers.gm_show_question (
			title = _('Deleting incoming data'),
			question = _(
				'Do you really want to delete the incoming data ?\n'
				'\n'
				'Note that deletion is not reversible.'
			)
		)
		if not do_delete:
			return False
		return gmIncomingData.delete_incoming_data(pk_incoming_data = staged_item['pk_incoming_data'])
	#------------------------------------------------------------
	def refresh(lctrl):
		incoming = gmIncomingData.get_incoming_data()
		items = [ [
			gmTools.coalesce(i['data_type'], ''),
			'%s, %s (%s) %s' % (
				gmTools.coalesce(i['lastnames'], ''),
				gmTools.coalesce(i['firstnames'], ''),
				gmDateTime.format_dob(i['dob'], format = '%Y %b %d', none_string = _('unknown DOB')),
				gmTools.coalesce(i['gender'], '')
			),
			gmTools.coalesce(i['external_data_id'], ''),
			i['pk_incoming_data']
		] for i in incoming ]
		lctrl.set_string_items(items)
		lctrl.set_data(incoming)
	#------------------------------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = None,
		caption = _('Showing unmatched incoming data'),
		columns = [ _('Type'), _('Identification'), _('Reference'), '#' ],
		single_selection = True,
		can_return_empty = False,
		ignore_OK_button = True,
		refresh_callback = refresh,
#		edit_callback=None,
#		new_callback=None,
		delete_callback = delete,
		left_extra_button = [_('Show'), _('Show formatted HL7'), show_hl7],
		middle_extra_button = [_('Import'), _('Import HL7 data into patient chart'), import_hl7]
#		right_extra_button=None
	)

#================================================================
# convenience functions
#================================================================
def call_browser_on_measurement_type(measurement_type=None):
	url = gmCfgDB.get4user (
		option = 'external.urls.measurements_search',
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		default = gmPathLab.URL_test_result_information_search
	)
	base_url = gmCfgDB.get4user (
		option = 'external.urls.measurements_encyclopedia',
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		default = gmPathLab.URL_test_result_information
	)
	if measurement_type is None:
		url = base_url
	measurement_type = measurement_type.strip()
	if measurement_type == '':
		url = base_url
	url = url % {'search_term': measurement_type}
	gmNetworkTools.open_url_in_browser(url = url)

#----------------------------------------------------------------
def edit_measurement(parent=None, measurement=None, single_entry=False, presets=None):
	ea = cMeasurementEditAreaPnl(parent, -1)
	ea.data = measurement
	ea.mode = gmTools.coalesce(measurement, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea, single_entry = single_entry)
	dlg.SetTitle(gmTools.coalesce(measurement, _('Adding new measurement'), _('Editing measurement')))
	if presets is not None:
		ea.set_fields(presets)
	if dlg.ShowModal() == wx.ID_OK:
		dlg.DestroyLater()
		return True

	dlg.DestroyLater()
	return False

#----------------------------------------------------------------
def manage_measurements(parent=None, single_selection=False, emr=None, measurements2manage=None, message=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	if emr is None:
		if measurements2manage is None:
			emr = gmPerson.gmCurrentPatient().emr

	#------------------------------------------------------------
	def edit(measurement=None):
		return edit_measurement(parent = parent, measurement = measurement, single_entry = True)

	#------------------------------------------------------------
	def delete(measurement):
		gmPathLab.delete_test_result(result = measurement)
		return True

	#------------------------------------------------------------
	def do_review(lctrl):
		data = lctrl.get_selected_item_data()
		if len(data) == 0:
			return

		return review_tests(parent = parent, tests = data)

	#------------------------------------------------------------
	def do_plot(lctrl):
		data = lctrl.get_selected_item_data()
		if len(data) == 0:
			return

		return plot_measurements(parent = parent, tests = data)

	#------------------------------------------------------------
	def do_print(lctrl):
		return print_measurements(tests = lctrl.get_selected_item_data())

	#------------------------------------------------------------
	def get_tooltip(measurement):
		return measurement.format(with_review=True, with_evaluation=True, with_ranges=True)

	#------------------------------------------------------------
	def refresh(lctrl):
		if measurements2manage is None:
			results = emr.get_test_results(order_by = 'clin_when DESC, unified_abbrev, unified_name')
		else:
			results = measurements2manage
		items = [ [
			r['clin_when'].strftime('%Y %b %d %H:%M'),
			r['unified_abbrev'],
			'%s%s%s%s' % (
				gmTools.bool2subst (
					boolean = (not r['reviewed'] or (not r['review_by_you'] and r['you_are_responsible'])),
					true_return = 'u' + gmTools.u_writing_hand,
					false_return = ''
				),
				r['unified_val'],
				gmTools.coalesce(r['val_unit'], '', ' %s'),
				gmTools.coalesce(r['abnormality_indicator'], '', ' %s')
			),
			r['unified_name'],
			gmTools.coalesce(r['comment'], ''),
			r['pk_test_result']
		] for r in results ]
		lctrl.set_string_items(items)
		lctrl.set_data(results)

	#------------------------------------------------------------
	return gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = message,
		caption = _('Showing test results.'),
		columns = [ _('When'), _('Abbrev'), _('Value'), _('Name'), _('Comment'), '#' ],
		single_selection = single_selection,
		can_return_empty = False,
		refresh_callback = refresh,
		edit_callback = edit,
		new_callback = edit,
		delete_callback = delete,
		list_tooltip_callback = get_tooltip,
		left_extra_button = (_('Review'), _('Review current selection'), do_review, True),
		middle_extra_button = (_('Plot'), _('Plot current selection'), do_plot, False),
		right_extra_button = (_('Print'), _('Print current selection'), do_print, False)
	)

#================================================================
def configure_default_top_lab_panel(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	panels = gmPathLab.get_test_panels(order_by = 'description')
	gmCfgWidgets.configure_string_from_list_option (
		parent = parent,
		message = _('Select the measurements panel to show in the top pane for continuous monitoring.'),
		option = 'horstspace.top_panel.lab_panel',
		bias = 'user',
		default_value = None,
		choices = [ '%s%s' % (p['description'], gmTools.coalesce(p['comment'], '', ' (%s)')) for p in panels ],
		columns = [_('Lab panel')],
		data = [ p['pk_test_panel'] for p in panels ],
		caption = _('Configuring continuous monitoring measurements panel')
	)

#================================================================
def configure_default_gnuplot_template(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	template = gmFormWidgets.manage_form_templates (
		parent = parent,
		active_only = True,
		template_types = ['gnuplot script']
	)

	option = 'form_templates.default_gnuplot_template'

	if template is None:
		gmDispatcher.send(signal = 'statustext', msg = _('No default Gnuplot script template selected.'), beep = True)
		return None

	if template['engine'] != 'G':
		gmDispatcher.send(signal = 'statustext', msg = _('No default Gnuplot script template selected.'), beep = True)
		return None

	gmCfgDB.set (
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		option = option,
		value = '%s - %s' % (template['name_long'], template['external_version'])
	)
	return template

#============================================================
def get_default_gnuplot_template(parent = None):

	option = 'form_templates.default_gnuplot_template'
	# load from option
	default_template_name = gmCfgDB.get4user (
		option = option,
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace
	)
	# not configured -> try to configure
	if default_template_name is None:
		gmDispatcher.send('statustext', msg = _('No default Gnuplot template configured.'), beep = False)
		default_template = configure_default_gnuplot_template(parent = parent)
		# still not configured -> return
		if default_template is None:
			gmGuiHelpers.gm_show_error (
				error = _('There is no default Gnuplot one-type script template configured.'),
				title = _('Plotting test results')
			)
			return None
		return default_template

	# now it MUST be configured (either newly or previously)
	# but also *validly* ?
	try:
		name, ver = default_template_name.split(' - ')
	except Exception:
		# not valid
		_log.exception('problem splitting Gnuplot script template name [%s]', default_template_name)
		gmDispatcher.send(signal = 'statustext', msg = _('Problem loading Gnuplot script template.'), beep = True)
		return None

	default_template = gmForms.get_form_template(name_long = name, external_version = ver)
	if default_template is None:
		default_template = configure_default_gnuplot_template(parent = parent)
		# still not configured -> return
		if default_template is None:
			gmGuiHelpers.gm_show_error (
				error = _('Cannot load default Gnuplot script template [%s - %s]') % (name, ver),
				title = _('Plotting test results')
			)
			return None

	return default_template

#----------------------------------------------------------------
def plot_measurements(parent=None, tests:list=None, format:str=None, show_year:bool=True, use_default_template:bool=False) -> bool:
	"""Plot measurement results with GNUplot.

	Args:
		parent: wxPython parent window
		tests: measurements for which to export data
		format: GNUplot output format, say, "wxt", "png", "latex", "x11"
		show_year: whether to show year on x-axis
		use_default_template: whether to use default template or ask user to select template

	Returns:
		True/False.
	"""
	# only valid for one-type plotting
	if use_default_template:
		template = get_default_gnuplot_template()
	else:
		from Gnumed.wxpython import gmFormWidgets
		template = gmFormWidgets.manage_form_templates (
			parent = parent,
			active_only = True,
			template_types = ['gnuplot script']
		)
	if template is None:
		gmGuiHelpers.gm_show_error (
			error = _('Cannot plot without a plot script.'),
			title = _('Plotting test results')
		)
		return False

	pat = gmPerson.gmCurrentPatient()
	fname_data = gmPathLab.export_results_for_gnuplot(results = tests, show_year = show_year, patient = pat)
	script = template.instantiate(use_sandbox = True)
	script.data_filename = fname_data
	script.generate_output(format = format) 		# Gnuplot output terminal, wxt = wxWidgets window

	fname_png = fname_data + '.png'
	if os.path.exists(fname_png):
		gmMimeLib.call_viewer_on_file(fname_png)
		store_in_export_area = gmGuiHelpers.gm_show_question (
			title = _('Plotted lab results'),
			question = _('Put a copy of the lab results plot into the export area of this patient ?')
		)
		if store_in_export_area:
			pat.export_area.add_file (
				filename = fname_png,
				hint = _('lab results plot')
			)
	return True

#----------------------------------------------------------------
def plot_adjacent_measurements(parent=None, test=None, format=None, show_year=True, plot_singular_result=True, use_default_template=False):

	earlier, later = test.get_adjacent_results(desired_earlier_results = 2, desired_later_results = 2)
	results2plot = []
	if earlier is not None:
		results2plot.extend(earlier)
	results2plot.append(test)
	if later is not None:
		results2plot.extend(later)
	if len(results2plot) == 1:
		if not plot_singular_result:
			return
	plot_measurements (
		parent = parent,
		tests = results2plot,
		format = format,
		show_year = show_year,
		use_default_template = use_default_template
	)

#----------------------------------------------------------------
def print_measurements(tests=None) -> bool:
	if not tests:
		tests = None
		print_all = gmGuiHelpers.gm_show_question (
			title = _('Printing measurements'),
			question = _('No measurements selected.\n\nPrint ALL results of patient ?')
		)
		if not print_all:
			return True

	labs_list = save_failsafe_test_results_list(test_results = tests, max_width = 80)
	gmMimeLib.call_editor_on_file(filename = labs_list, block = True)
	return True

#----------------------------------------------------------------
def generate_failsafe_test_results_list(pk_patient=None, test_results:list=None, max_width:int=80, eol:str=None) -> str|list:
	if not pk_patient:
		pk_patient = gmPerson.gmCurrentPatient().ID
	lines, footer = gmFormWidgets.generate_failsafe_form_wrapper (
		pk_patient = pk_patient,
		title = _('Lab results -- %s') % gmDateTime.pydt_now_here().strftime('%Y %b %d'),
		max_width = max_width
	)
	lines.extend(gmPathLab.generate_failsafe_test_results_entries (
		pk_patient = pk_patient,
		test_results = test_results,
		max_width = max_width
	))
	lines.append('')
	lines.extend(footer)
	if eol:
		return eol.join(lines)

	return lines

#------------------------------------------------------------
def save_failsafe_test_results_list(pk_patient=None, test_results=None, max_width:int=80, filename:str=None) -> str:
	if not filename:
		filename = gmTools.get_unique_filename()
	with open(filename, 'w', encoding = 'utf8') as tr_file:
		tr_file.write(generate_failsafe_test_results_list(pk_patient = pk_patient, test_results = test_results, max_width = max_width, eol = '\n'))
	return filename

#================================================================
#from Gnumed.wxGladeWidgets import wxgPrimaryCareVitalsInputPnl
#
# Taillenumfang: Mitte zwischen unterster Rippe und
# hoechstem Teil des Beckenkamms
# Maenner: maessig: 94-102, deutlich: > 102  .. erhoeht
# Frauen:  maessig: 80-88,  deutlich: > 88   .. erhoeht
#
#================================================================
# display widgets
#================================================================
from Gnumed.wxGladeWidgets import wxgLabRelatedDocumentsPnl

class cLabRelatedDocumentsPnl(wxgLabRelatedDocumentsPnl.wxgLabRelatedDocumentsPnl):
	"""This panel handles documents related to the lab result it is handed.
	"""
	def __init__(self, *args, **kwargs):
		wxgLabRelatedDocumentsPnl.wxgLabRelatedDocumentsPnl.__init__(self, *args, **kwargs)

		self.__reference = None

		self.__init_ui()
		self.__register_events()

	#------------------------------------------------------------
	# internal helpers
	#------------------------------------------------------------
	def __init_ui(self):
		self.__repopulate_ui()

	#------------------------------------------------------------
	def __register_events(self):
		gmDispatcher.connect(signal = 'gm_table_mod', receiver = self._on_database_signal)

	#------------------------------------------------------------
	def __repopulate_ui(self):
		self._BTN_list_documents.Disable()
		self._LBL_no_of_docs.SetLabel(_('no related documents'))
		self._LBL_no_of_docs.ContainingSizer.Layout()

		if self.__reference is None:
			self._LBL_no_of_docs.SetToolTip(_('There is no lab reference to find related documents for.'))
			return

		lab_doc_types = gmCfgDB.get4user (
			option = 'horstspace.lab_doc_types',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace
		)
		if lab_doc_types is None:
			self._LBL_no_of_docs.SetToolTip(_('No document types declared to contain lab results.'))
			return

		if len(lab_doc_types) == 0:
			self._LBL_no_of_docs.SetToolTip(_('No document types declared to contain lab results.'))
			return

		pks_doc_types = gmDocuments.map_types2pk(lab_doc_types)
		if len(pks_doc_types) == 0:
			self._LBL_no_of_docs.SetToolTip(_('No valid document types declared to contain lab results.'))
			return

		txt = _('Document types assumed to contain lab results:')
		txt += '\n '
		txt += '\n '.join(lab_doc_types)
		self._LBL_no_of_docs.SetToolTip(txt)
		if isinstance(self.__reference, gmPathLab.cTestResult):
			pk_current_episode = self.__reference['pk_episode']
		else:
			pk_current_episode = self.__reference
		docs = gmDocuments.search_for_documents (
			pk_episode = pk_current_episode,
			pk_types = [ dt['pk_doc_type'] for dt in pks_doc_types ]
		)
		if len(docs) == 0:
			return

		self._LBL_no_of_docs.SetLabel(_('Related documents: %s') % len(docs))
		self._LBL_no_of_docs.ContainingSizer.Layout()
		self._BTN_list_documents.Enable()

	#------------------------------------------------------------
	# event handlers
	#------------------------------------------------------------
	def _on_database_signal(self, **kwds):
		if self.__reference is None:
			return True

		if kwds['table'] not in ['clin.test_result', 'blobs.doc_med']:
			return True

		if isinstance(self.__reference, gmPathLab.cTestResult):
			if kwds['pk_of_row'] != self.__reference['pk_test_result']:
				return True

		self.__repopulate_ui()
		return True

	#------------------------------------------------------------
	def _on_select_lab_doc_types_button_pressed(self, event):
		event.Skip()
		doc_types = gmDocuments.get_document_types()
		gmCfgWidgets.configure_list_from_list_option (
			parent = self,
			message = _('Select the document types which are assumed to contain lab results.'),
			option = 'horstspace.lab_doc_types',
			bias = 'user',
			choices = [ dt['l10n_type'] for dt in doc_types ],
			columns = [_('Document types')]#,
			#data = None,
			#caption = None,
			#picks = None
		)
		self.__repopulate_ui()

	#------------------------------------------------------------
	def _on_list_documents_button_pressed(self, event):
		event.Skip()
		lab_doc_types = gmCfgDB.get4user (
			option = 'horstspace.lab_doc_types',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace
		)
		d_types = gmDocuments.map_types2pk(lab_doc_types)
		if isinstance(self.__reference, gmPathLab.cTestResult):
			pk_current_episode = self.__reference['pk_episode']
		else:
			pk_current_episode = self.__reference
		gmDocumentWidgets.manage_documents (
			parent = self,
			msg = _('Documents possibly related to this episode'),
			pk_types = [ dt['pk_doc_type'] for dt in d_types ],
			pk_episodes = [ pk_current_episode ]
		)

	#------------------------------------------------------------
	# properties
	#------------------------------------------------------------
	def _set_lab_reference(self, value):
		"""Either a test result or an episode PK."""
		if isinstance(self.__reference, gmPathLab.cTestResult):
			pk_old_episode = self.__reference['pk_episode']
		else:
			pk_old_episode = self.__reference
		if isinstance(value, gmPathLab.cTestResult):
			pk_new_episode = value['pk_episode']
		else:
			pk_new_episode = value
		self.__reference = value
		if pk_new_episode != pk_old_episode:
			self.__repopulate_ui()
		return

	lab_reference = property(lambda x:x, _set_lab_reference)

#================================================================
from Gnumed.wxGladeWidgets.wxgMeasurementsAsListPnl import wxgMeasurementsAsListPnl

class cMeasurementsAsListPnl(wxgMeasurementsAsListPnl, gmRegetMixin.cRegetOnPaintMixin):
	"""A class for displaying all measurement results as a simple list.

	- operates on a cPatient instance handed to it and NOT on the currently active patient
	"""
	def __init__(self, *args, **kwargs):
		wxgMeasurementsAsListPnl.__init__(self, *args, **kwargs)

		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		self.__patient = None

		self.__init_ui()
		self.__register_events()

	#------------------------------------------------------------
	# internal helpers
	#------------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_results.set_columns([_('When'), _('Test'), _('Result'), _('Reference')])
		self._LCTRL_results.edit_callback = self._on_edit
		self._PNL_related_documents.lab_reference = None

	#------------------------------------------------------------
	def __register_events(self):
		gmDispatcher.connect(signal = 'gm_table_mod', receiver = self._on_database_signal)

	#------------------------------------------------------------
	def __repopulate_ui(self):
		if self.__patient is None:
			self._LCTRL_results.set_string_items([])
			self._TCTRL_measurements.SetValue('')
			self._PNL_related_documents.lab_reference = None
			return

		results = self.__patient.emr.get_test_results(order_by = 'clin_when DESC, unified_abbrev, unified_name')
		items = []
		data = []
		for r in results:
			range_info = gmTools.coalesce (
				r.formatted_clinical_range,
				r.formatted_normal_range
			)
			review = gmTools.bool2subst (
				r['reviewed'],
				'',
				' ' + gmTools.u_writing_hand,
				' ' + gmTools.u_writing_hand
			)
			items.append ([
				r['clin_when'].strftime('%Y %b %d  %H:%M'),
				r['abbrev_tt'],
				'%s%s%s%s' % (
					gmTools.strip_empty_lines(text = r['unified_val'])[0],
					gmTools.coalesce(r['val_unit'], '', ' %s'),
					gmTools.coalesce(r['abnormality_indicator'], '', ' %s'),
					review
				),
				gmTools.coalesce(range_info, '')
			])
			data.append({'data': r, 'formatted': r.format(with_source_data = True)})

		self._LCTRL_results.set_string_items(items)
		self._LCTRL_results.set_column_widths([wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE])
		self._LCTRL_results.set_data(data)
		if len(items) > 0:
			self._LCTRL_results.Select(idx = 0, on = 1)
			self._TCTRL_measurements.SetValue(self._LCTRL_results.get_item_data(item_idx = 0)['formatted'])

		self._LCTRL_results.SetFocus()

	#------------------------------------------------------------
	def _on_edit(self):
		item_data = self._LCTRL_results.get_selected_item_data(only_one = True)
		if item_data is None:
			return
		if edit_measurement(parent = self, measurement = item_data['data'], single_entry = True):
			self.__repopulate_ui()

	#------------------------------------------------------------
	# event handlers
	#------------------------------------------------------------
	def _on_database_signal(self, **kwds):
		if self.__patient is None:
			return True

		if kwds['pk_identity'] is not None:				# review table doesn't have pk_identity yet
			if kwds['pk_identity'] != self.__patient.ID:
				return True

		if kwds['table'] not in ['clin.test_result', 'clin.reviewed_test_results']:
			return True

		self._schedule_data_reget()
		return True

	#------------------------------------------------------------
	def _on_result_selected(self, event):
		event.Skip()
		item_data = self._LCTRL_results.get_item_data(item_idx = event.Index)
		self._TCTRL_measurements.SetValue(item_data['formatted'])
		self._PNL_related_documents.lab_reference = item_data['data']

	#------------------------------------------------------------
	# reget mixin API
	#------------------------------------------------------------
	def _populate_with_data(self):
		self.__repopulate_ui()
		return True

	#------------------------------------------------------------
	# properties
	#------------------------------------------------------------
	def _get_patient(self):
		return self.__patient

	def _set_patient(self, patient):
		if (self.__patient is None) and (patient is None):
			return
		if (self.__patient is None) or (patient is None):
			self.__patient = patient
			self._schedule_data_reget()
			return
		if self.__patient.ID == patient.ID:
			return
		self.__patient = patient
		self._schedule_data_reget()

	patient = property(_get_patient, _set_patient)

#================================================================
from Gnumed.wxGladeWidgets.wxgMeasurementsByDayPnl import wxgMeasurementsByDayPnl

class cMeasurementsByDayPnl(wxgMeasurementsByDayPnl, gmRegetMixin.cRegetOnPaintMixin):
	"""A class for displaying measurement results as a list partitioned by day.

	- operates on a cPatient instance handed to it and NOT on the currently active patient
	"""
	def __init__(self, *args, **kwargs):
		wxgMeasurementsByDayPnl.__init__(self, *args, **kwargs)

		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		self.__patient = None
		self.__date_format = str('%Y %b %d')

		self.__init_ui()
		self.__register_events()

	#------------------------------------------------------------
	# internal helpers
	#------------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_days.set_columns([_('Day')])
		self._LCTRL_results.set_columns([_('Time'), _('Test'), _('Result'), _('Reference')])
		self._LCTRL_results.new_callback = self._on_add
		self._LCTRL_results.edit_callback = self._on_edit
		self._LCTRL_results.delete_callback = self._on_delete
		self._PNL_related_documents.lab_reference = None

	#------------------------------------------------------------
	def __register_events(self):
		gmDispatcher.connect(signal = 'gm_table_mod', receiver = self._on_database_signal)

	#------------------------------------------------------------
	def __clear(self):
		self._LCTRL_days.set_string_items()
		self._LCTRL_results.set_string_items()
		self._TCTRL_measurements.SetValue('')
		self._PNL_related_documents.lab_reference = None

	#------------------------------------------------------------
	def __repopulate_ui(self):
		if self.__patient is None:
			self.__clear()
			return

		idx_selected_day = self._LCTRL_days.GetFirstSelected()
		if idx_selected_day == -1:
			idx_selected_day = 0
		dates = self.__patient.emr.get_dates_for_results(reverse_chronological = True)
		items = [ ['%s%s' % (
					d['clin_when_day'].strftime(self.__date_format),
					gmTools.bool2subst(d['is_reviewed'], '', gmTools.u_writing_hand, gmTools.u_writing_hand)
				)]
			for d in dates
		]
		self._LCTRL_days.set_string_items(items)
		self._LCTRL_days.set_data(dates)
		if len(items) > 0:
			if idx_selected_day > len(items):
				idx_selected_day = 0
			self._LCTRL_days.Select(idx = idx_selected_day, on = 1)
			self._LCTRL_days.SetFocus()

	#------------------------------------------------------------
	def _on_edit(self):
		item_data = self._LCTRL_results.get_selected_item_data(only_one = True)
		if item_data is None:
			return
		if edit_measurement(parent = self, measurement = item_data['data'], single_entry = True):
			self.__repopulate_ui()

	#------------------------------------------------------------
	def _on_add(self):
		result = self._LCTRL_results.get_item_data(item_idx = 0)['data']
		presets = {
			'clin_when': {'data': result['clin_when']},
			'pk_episode': {'data': result['pk_episode']}
		}
		added = edit_measurement(parent = self, measurement = None, single_entry = False, presets = presets)
		if added:
			self.__repopulate_ui()
		self._LCTRL_results.SetFocus()

	#------------------------------------------------------------
	def _on_delete(self):
		item_data = self._LCTRL_results.get_selected_item_data(only_one = True)
		if item_data is None:
			return False

		result = item_data['data']
		delete = gmGuiHelpers.gm_show_question (
			question = _('Really delete test result ?\n\n%s') % result.format(),
			title = _('Deleting test result')
		)
		if not delete:
			return False

		return gmPathLab.delete_test_result(result = result)

	#------------------------------------------------------------
	# event handlers
	#------------------------------------------------------------
	def _on_database_signal(self, **kwds):
		if self.__patient is None:
			return True

		if kwds['pk_identity'] is not None:				# review table doesn't have pk_identity yet
			if kwds['pk_identity'] != self.__patient.ID:
				return True

		if kwds['table'] not in ['clin.test_result', 'clin.reviewed_test_results']:
			return True

		self._schedule_data_reget()
		return True

	#------------------------------------------------------------
	def _on_day_selected(self, event):
		event.Skip()

		day = self._LCTRL_days.get_item_data(item_idx = event.Index)['clin_when_day']
		results = self.__patient.emr.get_results_for_day(timestamp = day)
		items = []
		data = []
		for r in results:
			range_info = gmTools.coalesce (
				r.formatted_clinical_range,
				r.formatted_normal_range
			)
			review = gmTools.bool2subst (
				r['reviewed'],
				'',
				' ' + gmTools.u_writing_hand,
				' ' + gmTools.u_writing_hand
			)
			items.append ([
				r['clin_when'].strftime('%H:%M'),
				r['abbrev_tt'],
				'%s%s%s%s' % (
					gmTools.strip_empty_lines(text = r['unified_val'])[0],
					gmTools.coalesce(r['val_unit'], '', ' %s'),
					gmTools.coalesce(r['abnormality_indicator'], '', ' %s'),
					review
				),
				gmTools.coalesce(range_info, '')
			])
			data.append({'data': r, 'formatted': r.format(with_source_data = True)})

		self._LCTRL_results.set_string_items(items)
		self._LCTRL_results.set_column_label(1, _('Test (%s%s)') % (gmTools.u_sum, len(items)))
		self._LCTRL_results.set_column_widths([wx.LIST_AUTOSIZE_USEHEADER, wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE])
		self._LCTRL_results.set_data(data)
		self._LCTRL_results.Select(idx = 0, on = 1)

	#------------------------------------------------------------
	def _on_result_selected(self, event):
		event.Skip()
		item_data = self._LCTRL_results.get_item_data(item_idx = event.Index)
		self._TCTRL_measurements.SetValue(item_data['formatted'])
		self._PNL_related_documents.lab_reference = item_data['data']

	#------------------------------------------------------------
	# reget mixin API
	#------------------------------------------------------------
	def _populate_with_data(self):
		self.__repopulate_ui()
		return True

	#------------------------------------------------------------
	# properties
	#------------------------------------------------------------
	def _get_patient(self):
		return self.__patient

	def _set_patient(self, patient):
		if (self.__patient is None) and (patient is None):
			return
		if patient is None:
			self.__patient = None
			self.__clear()
			return
		if self.__patient is None:
			self.__patient = patient
			self._schedule_data_reget()
			return
		if self.__patient.ID == patient.ID:
			return
		self.__patient = patient
		self._schedule_data_reget()

	patient = property(_get_patient, _set_patient)

#================================================================
from Gnumed.wxGladeWidgets.wxgMeasurementsByIssuePnl import wxgMeasurementsByIssuePnl

class cMeasurementsByIssuePnl(wxgMeasurementsByIssuePnl, gmRegetMixin.cRegetOnPaintMixin):
	"""A class for displaying measurement results as a list partitioned by issue/episode.

	- operates on a cPatient instance handed to it and NOT on the currently active patient
	"""
	def __init__(self, *args, **kwargs):
		wxgMeasurementsByIssuePnl.__init__(self, *args, **kwargs)

		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		self.__patient = None

		self.__init_ui()
		self.__register_events()

	#------------------------------------------------------------
	# internal helpers
	#------------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_issues.set_columns([_('Problem')])
		self._LCTRL_results.set_columns([_('When'), _('Test'), _('Result'), _('Reference')])
		self._PNL_related_documents.lab_reference = None

	#------------------------------------------------------------
	def __register_events(self):
		gmDispatcher.connect(signal = 'gm_table_mod', receiver = self._on_database_signal)
		self._LCTRL_issues.select_callback = self._on_problem_selected
		self._LCTRL_results.edit_callback = self._on_edit
		self._LCTRL_results.select_callback = self._on_result_selected

	#------------------------------------------------------------
	def __clear(self):
		self._LCTRL_issues.set_string_items()
		self._LCTRL_results.set_string_items()
		self._TCTRL_measurements.SetValue('')
		self._PNL_related_documents.lab_reference = None

	#------------------------------------------------------------
	def __repopulate_ui(self):
		if self.__patient is None:
			self.__clear()
			return

		probs = self.__patient.emr.get_issues_or_episodes_for_results()
		items = [ ['%s%s' % (
			gmTools.coalesce (
				value2test = p['pk_health_issue'],
				value2return = '',
				return_instead = gmTools.u_diameter + ':'
			),
			gmTools.shorten_words_in_line(text = p['problem'], min_word_length = 5, max_length = 30)
		)] for p in probs ]
		self._LCTRL_issues.set_string_items(items)
		self._LCTRL_issues.set_data([ {'pk_issue': p['pk_health_issue'], 'pk_episode': p['pk_episode']} for p in probs ])
		if len(items) > 0:
			self._LCTRL_issues.Select(idx = 0, on = 1)
			self._LCTRL_issues.SetFocus()

	#------------------------------------------------------------
	def _on_edit(self):
		item_data = self._LCTRL_results.get_selected_item_data(only_one = True)
		if item_data is None:
			return
		if edit_measurement(parent = self, measurement = item_data['data'], single_entry = True):
			self.__repopulate_ui()

	#------------------------------------------------------------
	# event handlers
	#------------------------------------------------------------
	def _on_database_signal(self, **kwds):
		if self.__patient is None:
			return True

		if kwds['pk_identity'] is not None:				# review table doesn't have pk_identity yet
			if kwds['pk_identity'] != self.__patient.ID:
				return True

		if kwds['table'] not in ['clin.test_result', 'clin.reviewed_test_results']:
			return True

		self._schedule_data_reget()
		return True

	#------------------------------------------------------------
	def _on_problem_selected(self, event):
		event.Skip()

		pk_issue = self._LCTRL_issues.get_item_data(item_idx = event.Index)['pk_issue']
		if pk_issue is None:
			pk_episode = self._LCTRL_issues.get_item_data(item_idx = event.Index)['pk_episode']
			results = self.__patient.emr.get_results_for_episode(pk_episode = pk_episode)
		else:
			results = self.__patient.emr.get_results_for_issue(pk_health_issue = pk_issue)
		items = []
		data = []
		for r in results:
			range_info = gmTools.coalesce (
				r.formatted_clinical_range,
				r.formatted_normal_range
			)
			review = gmTools.bool2subst (
				r['reviewed'],
				'',
				' ' + gmTools.u_writing_hand,
				' ' + gmTools.u_writing_hand
			)
			items.append ([
				r['clin_when'].strftime('%Y %b %d  %H:%M'),
				r['abbrev_tt'],
				'%s%s%s%s' % (
					gmTools.strip_empty_lines(text = r['unified_val'])[0],
					gmTools.coalesce(r['val_unit'], '', ' %s'),
					gmTools.coalesce(r['abnormality_indicator'], '', ' %s'),
					review
				),
				gmTools.coalesce(range_info, '')
			])
			data.append({'data': r, 'formatted': r.format(with_source_data = True)})

		self._LCTRL_results.set_string_items(items)
		self._LCTRL_results.set_column_widths([wx.LIST_AUTOSIZE_USEHEADER, wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE])
		self._LCTRL_results.set_data(data)
		self._LCTRL_results.Select(idx = 0, on = 1)
		self._TCTRL_measurements.SetValue(self._LCTRL_results.get_item_data(item_idx = 0)['formatted'])

	#------------------------------------------------------------
	def _on_result_selected(self, event):
		event.Skip()
		item_data = self._LCTRL_results.get_item_data(item_idx = event.Index)
		self._TCTRL_measurements.SetValue(item_data['formatted'])
		self._PNL_related_documents.lab_reference = item_data['data']

	#------------------------------------------------------------
	# reget mixin API
	#------------------------------------------------------------
	def _populate_with_data(self):
		self.__repopulate_ui()
		return True

	#------------------------------------------------------------
	# properties
	#------------------------------------------------------------
	def _get_patient(self):
		return self.__patient

	def _set_patient(self, patient):
		if (self.__patient is None) and (patient is None):
			return
		if patient is None:
			self.__patient = None
			self.__clear()
			return
		if self.__patient is None:
			self.__patient = patient
			self._schedule_data_reget()
			return
		if self.__patient.ID == patient.ID:
			return
		self.__patient = patient
		self._schedule_data_reget()

	patient = property(_get_patient, _set_patient)

#================================================================
from Gnumed.wxGladeWidgets import wxgMeasurementsByBatteryPnl

class cMeasurementsByBatteryPnl(wxgMeasurementsByBatteryPnl.wxgMeasurementsByBatteryPnl, gmRegetMixin.cRegetOnPaintMixin):
	"""A grid class for displaying measurement results filtered by battery/panel.

	- operates on a cPatient instance handed to it and NOT on the currently active patient
	"""
	def __init__(self, *args, **kwargs):
		wxgMeasurementsByBatteryPnl.wxgMeasurementsByBatteryPnl.__init__(self, *args, **kwargs)

		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		self.__patient = None

		self.__init_ui()
		self.__register_events()

	#------------------------------------------------------------
	# internal helpers
	#------------------------------------------------------------
	def __init_ui(self):
		self._GRID_results_battery.show_by_panel = True

	#------------------------------------------------------------
	def __register_events(self):
		gmDispatcher.connect(signal = 'gm_table_mod', receiver = self._on_database_signal)

		self._PRW_panel.add_callback_on_selection(callback = self._on_panel_selected)
		self._PRW_panel.add_callback_on_modified(callback = self._on_panel_selection_modified)

	#------------------------------------------------------------
	def __repopulate_ui(self):
		self._GRID_results_battery.patient = self.__patient
		return True

	#--------------------------------------------------------
	def __on_panel_selected(self, panel):
		if panel is None:
			self._TCTRL_panel_comment.SetValue('')
			self._GRID_results_battery.panel_to_show = None
		else:
			pnl = self._PRW_panel.GetData(as_instance = True)
			self._TCTRL_panel_comment.SetValue(gmTools.coalesce (
				pnl['comment'],
				''
			))
			self._GRID_results_battery.panel_to_show = pnl
#		self.Layout()

	#--------------------------------------------------------
	def __on_panel_selection_modified(self):
		self._TCTRL_panel_comment.SetValue('')
		if self._PRW_panel.GetValue().strip() == '':
			self._GRID_results_battery.panel_to_show = None
#			self.Layout()

	#------------------------------------------------------------
	# event handlers
	#------------------------------------------------------------
	def _on_database_signal(self, **kwds):
		if self.__patient is None:
			return True

		if kwds['pk_identity'] is not None:				# review table doesn't have pk_identity yet
			if kwds['pk_identity'] != self.__patient.ID:
				return True

		if kwds['table'] not in ['clin.test_result', 'clin.reviewed_test_results']:
			return True

		self._schedule_data_reget()
		return True

	#------------------------------------------------------------
	def _on_manage_panels_button_pressed(self, event):
		manage_test_panels(parent = self)

	#--------------------------------------------------------
	def _on_panel_selected(self, panel):
		wx.CallAfter(self.__on_panel_selected, panel=panel)

	#--------------------------------------------------------
	def _on_panel_selection_modified(self):
		wx.CallAfter(self.__on_panel_selection_modified)

	#------------------------------------------------------------
	# reget mixin API
	#------------------------------------------------------------
	def _populate_with_data(self):
		self.__repopulate_ui()
		return True

	#------------------------------------------------------------
	# properties
	#------------------------------------------------------------
	def _get_patient(self):
		return self.__patient

	def _set_patient(self, patient):
		if (self.__patient is None) and (patient is None):
			return
		if (self.__patient is None) or (patient is None):
			self.__patient = patient
			self._schedule_data_reget()
			return
		if self.__patient.ID == patient.ID:
			return
		self.__patient = patient
		self._schedule_data_reget()

	patient = property(_get_patient, _set_patient)

#================================================================
from Gnumed.wxGladeWidgets.wxgMeasurementsAsMostRecentListPnl import wxgMeasurementsAsMostRecentListPnl

class cMeasurementsAsMostRecentListPnl(wxgMeasurementsAsMostRecentListPnl, gmRegetMixin.cRegetOnPaintMixin):
	"""A list ctrl class for displaying measurement results.

		- most recent results
		- possibly filtered by battery/panel

	- operates on a cPatient instance handed to it and NOT on the currently active patient
	"""
	def __init__(self, *args, **kwargs):
		wxgMeasurementsAsMostRecentListPnl.__init__(self, *args, **kwargs)

		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		self.__patient = None

		self.__init_ui()
		self.__register_events()

	#------------------------------------------------------------
	# internal helpers
	#------------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_results.set_columns([_('Test'), _('Result'), _('When'), _('Range')])
		self._CHBOX_show_missing.Disable()
		self._PNL_related_documents.lab_reference = None

	#------------------------------------------------------------
	def __register_events(self):
		gmDispatcher.connect(signal = 'gm_table_mod', receiver = self._on_database_signal)

		self._PRW_panel.add_callback_on_selection(callback = self._on_panel_selected)
		self._PRW_panel.add_callback_on_modified(callback = self._on_panel_selection_modified)

		self._LCTRL_results.select_callback = self._on_result_selected
		self._LCTRL_results.edit_callback = self._on_edit

	#------------------------------------------------------------
	def __repopulate_ui(self):

		self._TCTRL_details.SetValue('')
		self._PNL_related_documents.lab_reference = None
		if self.__patient is None:
			self._LCTRL_results.remove_items_safely()
			return

		pnl = self._PRW_panel.GetData(as_instance = True)
		if pnl is None:
			results = gmPathLab.get_most_recent_result_for_test_types (
				pk_patient = self.__patient.ID,
				consider_meta_type = True
			)
		else:
			results = pnl.get_most_recent_results (
				pk_patient = self.__patient.ID,
				#order_by = ,
				group_by_meta_type = True,
				include_missing = self._CHBOX_show_missing.IsChecked()
			)
		items = []
		data = []
		for r in results:
			if isinstance(r, gmPathLab.cTestResult):
				result_type = gmTools.coalesce (
					value2test = r['pk_meta_test_type'],
					return_instead = r['abbrev_tt'],
					value2return = '%s%s' % (gmTools.u_sum, r['abbrev_meta'])
				)
				review = gmTools.bool2subst (
					r['reviewed'],
					'',
					' ' + gmTools.u_writing_hand,
					' ' + gmTools.u_writing_hand
				)
				result_val = '%s%s%s%s' % (
					gmTools.strip_empty_lines(text = r['unified_val'])[0],
					gmTools.coalesce(r['val_unit'], '', ' %s'),
					gmTools.coalesce(r['abnormality_indicator'], '', ' %s'),
					review
				)
				result_when = _('%s ago (%s)') % (
					gmDateTime.format_interval_medically(interval = gmDateTime.pydt_now_here() - r['clin_when']),
					r['clin_when'].strftime('%Y %b %d  %H:%M')
				)
				range_info = gmTools.coalesce (
					r.formatted_clinical_range,
					r.formatted_normal_range
				)
				tt = r.format(with_source_data = True)
			else:
				result_type = r
				result_val = _('missing')
				loinc_data = gmLOINC.loinc2data(r)
				if loinc_data is None:
					result_when = _('LOINC not found')
					tt = u''
				else:
					result_when = loinc_data['term']
					tt = gmLOINC.format_loinc(r)
				range_info = None
			items.append([result_type, result_val, result_when, gmTools.coalesce(range_info, '')])
			data.append({'data': r, 'formatted': tt})

		self._LCTRL_results.set_string_items(items)
		self._LCTRL_results.set_column_widths([wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE])
		self._LCTRL_results.set_data(data)

		if len(items) > 0:
			self._LCTRL_results.Select(idx = 0, on = 1)
		self._LCTRL_results.SetFocus()

		return True

	#--------------------------------------------------------
	def __on_panel_selected(self, panel):
		if panel is None:
			self._TCTRL_panel_comment.SetValue('')
			self._CHBOX_show_missing.Disable()
		else:
			pnl = self._PRW_panel.GetData(as_instance = True)
			self._TCTRL_panel_comment.SetValue(gmTools.coalesce(pnl['comment'], ''))
		self.__repopulate_ui()
		self._CHBOX_show_missing.Enable()

	#--------------------------------------------------------
	def __on_panel_selection_modified(self):
		self._TCTRL_panel_comment.SetValue('')
		if self._PRW_panel.Value.strip() == u'':
			self.__repopulate_ui()
			self._CHBOX_show_missing.Disable()

	#------------------------------------------------------------
	# event handlers
	#------------------------------------------------------------
	def _on_database_signal(self, **kwds):
		if self.__patient is None:
			return True

		if kwds['pk_identity'] is not None:				# review table doesn't have pk_identity yet
			if kwds['pk_identity'] != self.__patient.ID:
				return True

		if kwds['table'] not in ['clin.test_result', 'clin.reviewed_test_results', 'clin.test_panel']:
			return True

		self._schedule_data_reget()
		return True

	#------------------------------------------------------------
	def _on_manage_panels_button_pressed(self, event):
		manage_test_panels(parent = self)

	#--------------------------------------------------------
	def _on_panel_selected(self, panel):
		wx.CallAfter(self.__on_panel_selected, panel = panel)

	#--------------------------------------------------------
	def _on_panel_selection_modified(self):
		wx.CallAfter(self.__on_panel_selection_modified)

	#------------------------------------------------------------
	def _on_result_selected(self, event):
		event.Skip()
		item_data = self._LCTRL_results.get_item_data(item_idx = event.Index)
		self._TCTRL_details.SetValue(item_data['formatted'])
		if isinstance(item_data['data'], gmPathLab.cTestResult):
			self._PNL_related_documents.lab_reference = item_data['data']
		else:
			self._PNL_related_documents.lab_reference = None

	#------------------------------------------------------------
	def _on_edit(self):
		item_data = self._LCTRL_results.get_selected_item_data(only_one = True)
		if item_data is None:
			return
		if isinstance(item_data['data'], gmPathLab.cTestResult):
			if edit_measurement(parent = self, measurement = item_data['data'], single_entry = True):
				self.__repopulate_ui()

	#------------------------------------------------------------
	def _on_show_missing_toggled(self, event):
		event.Skip()
		# should not happen
		if self._PRW_panel.GetData(as_instance = False) is None:
			return
		self.__repopulate_ui()

	#------------------------------------------------------------
	# reget mixin API
	#------------------------------------------------------------
	def _populate_with_data(self):
		self.__repopulate_ui()
		return True

	#------------------------------------------------------------
	# properties
	#------------------------------------------------------------
	def _get_patient(self):
		return self.__patient

	def _set_patient(self, patient):
		if (self.__patient is None) and (patient is None):
			return
		if (self.__patient is None) or (patient is None):
			self.__patient = patient
			self._schedule_data_reget()
			return
		if self.__patient.ID == patient.ID:
			return
		self.__patient = patient
		self._schedule_data_reget()

	patient = property(_get_patient, _set_patient)

#================================================================
from Gnumed.wxGladeWidgets import wxgMeasurementsAsTablePnl

class cMeasurementsAsTablePnl(wxgMeasurementsAsTablePnl.wxgMeasurementsAsTablePnl, gmRegetMixin.cRegetOnPaintMixin):
	"""A panel for holding a grid displaying all measurement results.

	- operates on a cPatient instance handed to it and NOT on the currently active patient
	"""
	def __init__(self, *args, **kwargs):
		wxgMeasurementsAsTablePnl.wxgMeasurementsAsTablePnl.__init__(self, *args, **kwargs)

		gmRegetMixin.cRegetOnPaintMixin.__init__(self)

		self.__patient = None

		self.__init_ui()
		self.__register_events()

	#------------------------------------------------------------
	# internal helpers
	#------------------------------------------------------------
	def __init_ui(self):
		self.__action_button_popup = wx.Menu(title = _('Perform on selected results:'))

		item = self.__action_button_popup.Append(-1, _('Review and &sign'))
		self.Bind(wx.EVT_MENU, self.__on_sign_current_selection, item)

		item = self.__action_button_popup.Append(-1, _('Plot'))
		self.Bind(wx.EVT_MENU, self.__on_plot_current_selection, item)

		#item = self.__action_button_popup.Append(-1, _('Export to &file'))
		#self.Bind(wx.EVT_MENU, self._GRID_results_all.current_selection_to_file, item)
		#self.__action_button_popup.Enable(id = item.Id, enable = False)

		#item = self.__action_button_popup.Append(-1, _('Export to &clipboard'))
		#self.Bind(wx.EVT_MENU, self._GRID_results_all.current_selection_to_clipboard, item)
		#self.__action_button_popup.Enable(id = item.Id, enable = False)

		item = self.__action_button_popup.Append(-1, _('&Delete'))
		self.Bind(wx.EVT_MENU, self.__on_delete_current_selection, item)

		# FIXME: create inbox message to staff to phone patient to come in
		# FIXME: generate and let edit a SOAP narrative and include the values

		self._GRID_results_all.show_by_panel = False

	#------------------------------------------------------------
	def __register_events(self):
		gmDispatcher.connect(signal = 'gm_table_mod', receiver = self._on_database_signal)

	#------------------------------------------------------------
	def __repopulate_ui(self):
		self._GRID_results_all.patient = self.__patient
		#self._GRID_results_battery.Fit()
		self.Layout()
		return True

	#------------------------------------------------------------
	def __on_sign_current_selection(self, evt):
		self._GRID_results_all.sign_current_selection()

	#------------------------------------------------------------
	def __on_plot_current_selection(self, evt):
		self._GRID_results_all.plot_current_selection()

	#------------------------------------------------------------
	def __on_delete_current_selection(self, evt):
		self._GRID_results_all.delete_current_selection()

	#------------------------------------------------------------
	# event handlers
	#------------------------------------------------------------
	def _on_database_signal(self, **kwds):
		if self.__patient is None:
			return True

		if kwds['pk_identity'] is not None:				# review table doesn't have pk_identity yet
			if kwds['pk_identity'] != self.__patient.ID:
				return True

		if kwds['table'] not in ['clin.test_result', 'clin.reviewed_test_results']:
			return True

		self._schedule_data_reget()
		return True

	#--------------------------------------------------------
	def _on_add_button_pressed(self, event):
		edit_measurement(parent = self, measurement = None)

	#--------------------------------------------------------
	def _on_manage_types_button_pressed(self, event):
		event.Skip()
		manage_measurement_types(parent = self)

	#--------------------------------------------------------
	def _on_review_button_pressed(self, evt):
		self.PopupMenu(self.__action_button_popup)

	#--------------------------------------------------------
	def _on_select_button_pressed(self, evt):
		if self._RBTN_my_unsigned.GetValue() is True:
			self._GRID_results_all.select_cells(unsigned_only = True, accountables_only = True, keep_preselections = False)
		elif self._RBTN_all_unsigned.GetValue() is True:
			self._GRID_results_all.select_cells(unsigned_only = True, accountables_only = False, keep_preselections = False)

	#------------------------------------------------------------
	# reget mixin API
	#------------------------------------------------------------
	def _populate_with_data(self):
		self.__repopulate_ui()
		return True

	#------------------------------------------------------------
	# properties
	#------------------------------------------------------------
	def _get_patient(self):
		return self.__patient

	def _set_patient(self, patient):
		if (self.__patient is None) and (patient is None):
			return
		if (self.__patient is None) or (patient is None):
			self.__patient = patient
			self._schedule_data_reget()
			return
		if self.__patient.ID == patient.ID:
			return
		self.__patient = patient
		self._schedule_data_reget()

	patient = property(_get_patient, _set_patient)

#================================================================
# notebook based measurements plugin
#================================================================
class cMeasurementsNb(wx.Notebook, gmPlugin.cPatientChange_PluginMixin):
	"""Notebook displaying measurements pages:

		- by test battery
		- by day
		- by issue/episode
		- most-recent list, perhaps by panel
		- full grid
		- full list

	Used as a main notebook plugin page.

	Operates on the active patient.
	"""
	#--------------------------------------------------------
	def __init__(self, parent, id):

		wx.Notebook.__init__ (
			self,
			parent = parent,
			id = id,
			style = wx.NB_TOP | wx.NB_MULTILINE | wx.NO_BORDER,
			name = self.__class__.__name__
		)
		_log.debug('created wx.Notebook: %s with ID %s', self.__class__.__name__, self.Id)
		gmPlugin.cPatientChange_PluginMixin.__init__(self)
		self.__patient = gmPerson.gmCurrentPatient()
		self.__init_ui()
		self.SetSelection(0)

	#--------------------------------------------------------
	# patient change plugin API
	#--------------------------------------------------------
	def _on_current_patient_unset(self, **kwds):
		for page_idx in range(self.GetPageCount()):
			page = self.GetPage(page_idx)
			page.patient = None

	#--------------------------------------------------------
	def _post_patient_selection(self, **kwds):
		for page_idx in range(self.GetPageCount()):
			page = self.GetPage(page_idx)
			page.patient = self.__patient.patient

	#--------------------------------------------------------
	# notebook plugin API
	#--------------------------------------------------------
	def repopulate_ui(self):
		if self.__patient.connected:
			pat = self.__patient.patient
		else:
			pat = None
		for page_idx in range(self.GetPageCount()):
			page = self.GetPage(page_idx)
			page.patient = pat

		return True

	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __init_ui(self):

		# by day
		new_page = cMeasurementsByDayPnl(self, -1)
		new_page.patient = None
		self.AddPage (
			page = new_page,
			text = _('Days'),
			select = True
		)

		# by issue
		new_page = cMeasurementsByIssuePnl(self, -1)
		new_page.patient = None
		self.AddPage (
			page = new_page,
			text = _('Problems'),
			select = False
		)

		# by test panel
		new_page = cMeasurementsByBatteryPnl(self, -1)
		new_page.patient = None
		self.AddPage (
			page = new_page,
			text = _('Panels'),
			select = False
		)

		# most-recent, by panel
		new_page = cMeasurementsAsMostRecentListPnl(self, -1)
		new_page.patient = None
		self.AddPage (
			page = new_page,
			text = _('Most recent'),
			select = False
		)

		# full grid
		new_page = cMeasurementsAsTablePnl(self, -1)
		new_page.patient = None
		self.AddPage (
			page = new_page,
			text = _('Table'),
			select = False
		)

		# full list
		new_page = cMeasurementsAsListPnl(self, -1)
		new_page.patient = None
		self.AddPage (
			page = new_page,
			text = _('List'),
			select = False
		)

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_patient(self):
		return self.__patient

	def _set_patient(self, patient):
		self.__patient = patient
		if self.__patient.connected:
			pat = self.__patient.patient
		else:
			pat = None
		for page_idx in range(self.GetPageCount()):
			page = self.GetPage(page_idx)
			page.patient = pat

	patient = property(_get_patient, _set_patient)

#================================================================
class cMeasurementsGrid(wx.grid.Grid):
	"""A grid class for displaying measurement results.

	- operates on a cPatient instance handed to it
	- does NOT listen to the currently active patient
	- thereby it can display any patient at any time
	"""
	# FIXME: sort-by-battery
	# FIXME: filter out empty
	# FIXME: filter by tests of a selected date
	# FIXME: dates DESC/ASC by cfg
	# FIXME: mouse over column header: display date info
	def __init__(self, *args, **kwargs):

		wx.grid.Grid.__init__(self, *args, **kwargs)

		self.__patient = None
		self.__panel_to_show = None
		self.__show_by_panel = False
		self.__cell_data = {}
		self.__row_label_data = []
		self.__col_label_data = []

		self.__prev_row = None
		self.__prev_col = None
		self.__prev_label_row = None
		self.__date_format = gmTools.strip_prefix (
			_('lab_grid_date_format::%Y\n%b %d'),
			'lab_grid_date_format'
		).lstrip(':')
		self.__init_ui()
		self.__register_events()

	#------------------------------------------------------------
	# external API
	#------------------------------------------------------------
	def delete_current_selection(self):
		if not self.IsSelection():
			gmDispatcher.send(signal = 'statustext', msg = _('No results selected for deletion.'))
			return True

		selected_cells = self.get_selected_cells()
		if len(selected_cells) > 20:
			results = None
			msg = _(
				'There are %s results marked for deletion.\n'
				'\n'
				'Are you sure you want to delete these results ?'
			) % len(selected_cells)
		else:
			results = self.__cells_to_data(cells = selected_cells, exclude_multi_cells = False)
			txt = '\n'.join([ '%s %s (%s): %s %s%s' % (
					r['clin_when'].strftime('%x %H:%M'),
					r['unified_abbrev'],
					r['unified_name'],
					r['unified_val'],
					r['val_unit'],
					gmTools.coalesce(r['abnormality_indicator'], '', ' (%s)')
				) for r in results
			])
			msg = _(
				'The following results are marked for deletion:\n'
				'\n'
				'%s\n'
				'\n'
				'Are you sure you want to delete these results ?'
			) % txt

		dlg = gmGuiHelpers.c2ButtonQuestionDlg (
			self,
			-1,
			caption = _('Deleting test results'),
			question = msg,
			button_defs = [
				{'label': _('Delete'), 'tooltip': _('Yes, delete all the results.'), 'default': False},
				{'label': _('Cancel'), 'tooltip': _('No, do NOT delete any results.'), 'default': True}
			]
		)
		decision = dlg.ShowModal()

		if decision == wx.ID_YES:
			if results is None:
				results = self.__cells_to_data(cells = selected_cells, exclude_multi_cells = False)
			for result in results:
				gmPathLab.delete_test_result(result)

	#------------------------------------------------------------
	def sign_current_selection(self):
		if not self.IsSelection():
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot sign results. No results selected.'))
			return True

		selected_cells = self.get_selected_cells()
		tests = self.__cells_to_data(cells = selected_cells, exclude_multi_cells = False)

		return review_tests(parent = self, tests = tests)

	#------------------------------------------------------------
	def plot_current_selection(self):

		if not self.IsSelection():
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot plot results. No results selected.'))
			return True

		tests = self.__cells_to_data (
			cells = self.get_selected_cells(),
			exclude_multi_cells = False,
			auto_include_multi_cells = True
		)

		plot_measurements(parent = self, tests = tests)

	#------------------------------------------------------------
	def get_selected_cells(self):
		"""Assemble list of all selected cells."""

		all_selected_cells = []
		# individually selected cells (ctrl-click)
		all_selected_cells += [ cell_coords.Get() for cell_coords in self.GetSelectedCells() ]
		# add cells from fully selected rows
		fully_selected_rows = self.GetSelectedRows()
		all_selected_cells += list (
			(row, col)
				for row in fully_selected_rows
				for col in range(self.GetNumberCols())
		)
		# add cells from fully selected columns
		fully_selected_cols = self.GetSelectedCols()
		all_selected_cells += list (
			(row, col)
				for row in range(self.GetNumberRows())
				for col in fully_selected_cols
		)
		# add cells from selection blocks
		selected_blocks = zip(self.GetSelectionBlockTopLeft(), self.GetSelectionBlockBottomRight())
		for top_left_corner, bottom_right_corner in selected_blocks:
			all_selected_cells += [
				(row, col)
					for row in range(top_left_corner[0], bottom_right_corner[0] + 1)
					for col in range(top_left_corner[1], bottom_right_corner[1] + 1)
			]
		return set(all_selected_cells)

	#------------------------------------------------------------
	def select_cells(self, unsigned_only=False, accountables_only=False, keep_preselections=False):
		"""Select a range of cells according to criteria.

		unsigned_only: include only those which are not signed at all yet
		accountable_only: include only those for which the current user is responsible
		keep_preselections: broaden (rather than replace) the range of selected cells

		Combinations are powerful !
		"""
		wx.BeginBusyCursor()
		self.BeginBatch()

		if not keep_preselections:
			self.ClearSelection()

		for col_idx in self.__cell_data:
			for row_idx in self.__cell_data[col_idx]:
				# loop over results in cell and only include
				# those multi-value cells that are not ambiguous
				do_not_include = False
				for result in self.__cell_data[col_idx][row_idx]:
					if unsigned_only:
						if result['reviewed']:
							do_not_include = True
							break
					if accountables_only:
						if not result['you_are_responsible']:
							do_not_include = True
							break
				if do_not_include:
					continue

				self.SelectBlock(row_idx, col_idx, row_idx, col_idx, addToSelected = True)

		self.EndBatch()
		wx.EndBusyCursor()

	#------------------------------------------------------------
	def repopulate_grid(self):
		self.empty_grid()
		if self.__patient is None:
			return

		if self.__show_by_panel:
			if self.__panel_to_show is None:
				return
			tests = self.__panel_to_show.get_test_types_for_results (
				self.__patient.ID,
				order_by = 'unified_abbrev',
				unique_meta_types = True
			)
			self.__repopulate_grid (
				tests4rows = tests,
				test_pks2show = [ tt['pk_test_type'] for tt in self.__panel_to_show['test_types'] ]
			)
			return

		emr = self.__patient.emr
		tests = emr.get_test_types_for_results(order_by = 'unified_abbrev', unique_meta_types = True)
		self.__repopulate_grid(tests4rows = tests)

	#------------------------------------------------------------
	def __repopulate_grid(self, tests4rows=None, test_pks2show=None):

		if len(tests4rows) == 0:
			return

		emr = self.__patient.emr

		self.__row_label_data = tests4rows
		row_labels = [ '%s%s' % (
				gmTools.bool2subst(test_type['is_fake_meta_type'], '', gmTools.u_sum, ''),
				test_type['unified_abbrev']
			) for test_type in self.__row_label_data
		]

		self.__col_label_data = [ d['clin_when_day'] for d in emr.get_dates_for_results (
			tests = test_pks2show,
			reverse_chronological = True
		)]
		col_labels = [ date.strftime(self.__date_format) for date in self.__col_label_data ]

		results = emr.get_test_results_by_date (
			tests = test_pks2show,
			reverse_chronological = True
		)

		self.BeginBatch()

		# rows
		self.AppendRows(numRows = len(row_labels))
		for row_idx in range(len(row_labels)):
			self.SetRowLabelValue(row_idx, row_labels[row_idx])

		# columns
		self.AppendCols(numCols = len(col_labels))
		for col_idx in range(len(col_labels)):
			self.SetColLabelValue(col_idx, col_labels[col_idx])

		# cell values (list of test results)
		for result in results:
			row_idx = row_labels.index('%s%s' % (
				gmTools.bool2subst(result['is_fake_meta_type'], '', gmTools.u_sum, ''),
				result['unified_abbrev']
			))
			col_idx = col_labels.index(result['clin_when'].strftime(self.__date_format))

			try:
				self.__cell_data[col_idx]
			except KeyError:
				self.__cell_data[col_idx] = {}

			# the tooltip always shows the youngest sub result details
			if row_idx in self.__cell_data[col_idx]:
				self.__cell_data[col_idx][row_idx].append(result)
				self.__cell_data[col_idx][row_idx].sort(key = lambda x: x['clin_when'], reverse = True)
			else:
				self.__cell_data[col_idx][row_idx] = [result]

			# rebuild cell display string
			vals2display = []
			cell_has_out_of_bounds_value = False
			for sub_result in self.__cell_data[col_idx][row_idx]:

				if sub_result.is_considered_abnormal:
					cell_has_out_of_bounds_value = True

				abnormality_indicator = sub_result.formatted_abnormality_indicator
				if abnormality_indicator is None:
					abnormality_indicator = ''
				if abnormality_indicator != '':
					abnormality_indicator = ' (%s)' % abnormality_indicator[:3]

				missing_review = False
				# warn on missing review if
				# a) no review at all exists or
				if not sub_result['reviewed']:
					missing_review = True
				# b) there is a review but
				else:
					# current user is reviewer and hasn't reviewed
					if sub_result['you_are_responsible'] and not sub_result['review_by_you']:
						missing_review = True

				needs_superscript = False

				# can we display the full sub_result length ?
				if sub_result.is_long_text:
					lines = gmTools.strip_empty_lines (
						text = sub_result['unified_val'],
						eol = '\n',
						return_list = True
					)
					needs_superscript = True
					tmp = lines[0][:7]
				else:
					val = gmTools.strip_empty_lines (
						text = sub_result['unified_val'],
						eol = '\n',
						return_list = False
					).replace('\n', '//')
					if len(val) > 8:
						needs_superscript = True
						tmp = val[:7]
					else:
						tmp = '%.8s' % val[:8]

				# abnormal ?
				tmp = '%s%.6s' % (tmp, abnormality_indicator)

				# is there a comment ?
				has_sub_result_comment = gmTools.coalesce (
					gmTools.coalesce(sub_result['note_test_org'], sub_result['comment']),
					''
				).strip() != ''
				if has_sub_result_comment:
					needs_superscript = True

				if needs_superscript:
					tmp = '%s%s' % (tmp, gmTools.u_superscript_one)

				# lacking a review ?
				if missing_review:
					tmp = '%s %s' % (tmp, gmTools.u_writing_hand)
				else:
					if sub_result['is_clinically_relevant']:
						tmp += ' !'

				# part of a multi-result cell ?
				if len(self.__cell_data[col_idx][row_idx]) > 1:
					tmp = '%s %s' % (sub_result['clin_when'].strftime('%H:%M'), tmp)

				vals2display.append(tmp)

			self.SetCellValue(row_idx, col_idx, '\n'.join(vals2display))
			self.SetCellAlignment(row_idx, col_idx, horiz = wx.ALIGN_RIGHT, vert = wx.ALIGN_CENTRE)
			# We used to color text in cells holding abnormals
			# in firebrick red but that would color ALL text (including
			# normals) and not only the abnormals within that
			# cell. Shading, however, only says that *something*
			# inside that cell is worthy of attention.
			#if sub_result_relevant:
			#	font = self.GetCellFont(row_idx, col_idx)
			#	self.SetCellTextColour(row_idx, col_idx, 'firebrick')
			#	font.SetWeight(wx.FONTWEIGHT_BOLD)
			#	self.SetCellFont(row_idx, col_idx, font)
			if cell_has_out_of_bounds_value:
				#self.SetCellBackgroundColour(row_idx, col_idx, 'cornflower blue')
				self.SetCellBackgroundColour(row_idx, col_idx, 'PALE TURQUOISE')

		self.EndBatch()

		self.AutoSize()
		self.AdjustScrollbars()
		self.ForceRefresh()

		#self.Fit()

		return

	#------------------------------------------------------------
	def empty_grid(self):
		self.BeginBatch()
		self.ClearGrid()
		# Windows cannot do nothing, it rather decides to assert()
		# on thinking it is supposed to do nothing
		if self.GetNumberRows() > 0:
			self.DeleteRows(pos = 0, numRows = self.GetNumberRows())
		if self.GetNumberCols() > 0:
			self.DeleteCols(pos = 0, numCols = self.GetNumberCols())
		self.EndBatch()
		self.__cell_data = {}
		self.__row_label_data = []
		self.__col_label_data = []

	#------------------------------------------------------------
	def get_row_tooltip(self, row=None):
		# include details about test types included ?

		# sometimes, for some reason, there is no row and
		# wxPython still tries to find a tooltip for it
		try:
			tt = self.__row_label_data[row]
		except IndexError:
			return ' '

		if tt['is_fake_meta_type']:
			return tt.format(patient = self.__patient.ID)

		meta_tt = tt.meta_test_type
		txt = meta_tt.format(with_tests = True, patient = self.__patient.ID)

		return txt

	#------------------------------------------------------------
	def get_cell_tooltip(self, col=None, row=None):
		try:
			cell_results = self.__cell_data[col][row]
		except KeyError:
			# FIXME: maybe display the most recent or when the most recent was ?
			cell_results = None

		if cell_results is None:
			return ' '

		is_multi_cell = False
		if len(cell_results) > 1:
			is_multi_cell = True
		result = cell_results[0]

		tt = ''
		# header
		if is_multi_cell:
			tt += _('Details of most recent (topmost) result !               \n')
		if result.is_long_text:
			tt += gmTools.strip_empty_lines(text = result['val_alpha'], eol = '\n', return_list = False)
			return tt

		tt += result.format(with_review = True, with_evaluation = True, with_ranges = True)
		return tt

	#------------------------------------------------------------
	# internal helpers
	#------------------------------------------------------------
	def __init_ui(self):
		#self.SetMinSize(wx.DefaultSize)
		self.SetMinSize((10, 10))

		self.CreateGrid(0, 1)
		self.EnableEditing(0)
		self.EnableDragGridSize(1)

		# column labels
		# setting this screws up the labels: they are cut off and displaced
		#self.SetColLabelAlignment(wx.ALIGN_CENTER, wx.ALIGN_BOTTOM)

		# row labels
		self.SetRowLabelSize(wx.grid.GRID_AUTOSIZE)		# starting with 2.8.8
		#self.SetRowLabelSize(150)
		self.SetRowLabelAlignment(horiz = wx.ALIGN_LEFT, vert = wx.ALIGN_CENTRE)
		font = self.GetLabelFont()
		font.SetWeight(wx.FONTWEIGHT_LIGHT)
		self.SetLabelFont(font)

		# add link to left upper corner
		url = gmCfgDB.get4user (
			option = 'external.urls.measurements_encyclopedia',
			workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
			default = gmPathLab.URL_test_result_information
		)

		self.__WIN_corner = self.GetGridCornerLabelWindow()		# a wx.Window instance

		LNK_lab = wxh.HyperlinkCtrl (
			self.__WIN_corner,
			-1,
			label = _('Tests'),
			style = wxh.HL_DEFAULT_STYLE			# wx.TE_READONLY|wx.TE_CENTRE| wx.NO_BORDER |
		)
		LNK_lab.SetURL(url)
		LNK_lab.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BACKGROUND))
		LNK_lab.SetToolTip(_(
			'Navigate to an encyclopedia of measurements\n'
			'and test methods on the web.\n'
			'\n'
			' <%s>'
		) % url)

		SZR_inner = wx.BoxSizer(wx.HORIZONTAL)
		SZR_inner.Add((20, 20), 1, wx.EXPAND, 0)		# spacer
		SZR_inner.Add(LNK_lab, 0, wx.ALIGN_CENTER_VERTICAL, 0)		#wx.ALIGN_CENTER wx.EXPAND
		SZR_inner.Add((20, 20), 1, wx.EXPAND, 0)		# spacer

		SZR_corner = wx.BoxSizer(wx.VERTICAL)
		SZR_corner.Add((20, 20), 1, wx.EXPAND, 0)		# spacer
		SZR_corner.Add(SZR_inner, 0, wx.EXPAND)			# inner sizer with centered hyperlink
		SZR_corner.Add((20, 20), 1, wx.EXPAND, 0)		# spacer

		self.__WIN_corner.SetSizer(SZR_corner)
		SZR_corner.Fit(self.__WIN_corner)

	#------------------------------------------------------------
	def __resize_corner_window(self, evt):
		self.__WIN_corner.Layout()

	#------------------------------------------------------------
	def __cells_to_data(self, cells=None, exclude_multi_cells=False, auto_include_multi_cells=False):
		"""List of <cells> must be in row / col order."""
		data = []
		for row, col in cells:
			try:
				# cell data is stored col / row
				data_list = self.__cell_data[col][row]
			except KeyError:
				continue

			if len(data_list) == 1:
				data.append(data_list[0])
				continue

			if exclude_multi_cells:
				gmDispatcher.send(signal = 'statustext', msg = _('Excluding multi-result field from further processing.'))
				continue

			if auto_include_multi_cells:
				data.extend(data_list)
				continue

			data_to_include = self.__get_choices_from_multi_cell(cell_data = data_list)
			if data_to_include is None:
				continue
			data.extend(data_to_include)

		return data

	#------------------------------------------------------------
	def __get_choices_from_multi_cell(self, cell_data=None, single_selection=False):
		data = gmListWidgets.get_choices_from_list (
			parent = self,
			msg = _(
				'Your selection includes a field with multiple results.\n'
				'\n'
				'Please select the individual results you want to work on:'
			),
			caption = _('Selecting test results'),
			choices = [ [d['clin_when'], '%s: %s' % (d['abbrev_tt'], d['name_tt']), d['unified_val']] for d in cell_data ],
			columns = [ _('Date / Time'), _('Test'), _('Result') ],
			data = cell_data,
			single_selection = single_selection
		)
		return data

	#------------------------------------------------------------
	# event handling
	#------------------------------------------------------------
	def __register_events(self):
		# dynamic tooltips: GridWindow, GridRowLabelWindow, GridColLabelWindow, GridCornerLabelWindow
		self.GetGridWindow().Bind(wx.EVT_MOTION, self.__on_mouse_over_cells)
		self.GetGridRowLabelWindow().Bind(wx.EVT_MOTION, self.__on_mouse_over_row_labels)
		#self.GetGridColLabelWindow().Bind(wx.EVT_MOTION, self.__on_mouse_over_col_labels)

		# sizing left upper corner window
		self.Bind(wx.EVT_SIZE, self.__resize_corner_window)

		# editing cells
		self.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.__on_cell_left_dclicked)

	#------------------------------------------------------------
	def __on_cell_left_dclicked(self, evt):
		col = evt.GetCol()
		row = evt.GetRow()

		try:
			self.__cell_data[col][row]
		except KeyError:		# empty cell
			presets = {}
			col_date = self.__col_label_data[col]
			presets['clin_when'] = {'data': col_date}
			test_type = self.__row_label_data[row]
			if test_type['pk_meta_test_type'] is not None:
				temporally_closest_result_of_row_type = test_type.meta_test_type.get_temporally_closest_result(col_date, self.__patient.ID)
				if temporally_closest_result_of_row_type is not None:
					# pre-set test type field to test type of
					# "temporally most adjacent" existing result :-)
					presets['pk_test_type'] = {'data': temporally_closest_result_of_row_type['pk_test_type']}
				# one might also, instead of considering only the "temporally most adjacent"
				# one, look at the most adjacent one coming from the same *lab* as other
				# results on the desired data ....
			same_day_results = gmPathLab.get_results_for_day (
				timestamp = col_date,
				patient = self.__patient.ID,
				order_by = None
			)
			if len(same_day_results) > 0:
				# pre-set episode field to episode of
				# existing results on the day in question
				presets['pk_episode'] = {'data': same_day_results[0]['pk_episode']}
			# maybe ['comment'] as in "medical context" ? - not thought through yet
			# no need to set because because setting pk_test_type will do so:
			#	presets['val_unit']
			#	presets['val_normal_min']
			#	presets['val_normal_max']
			#	presets['val_normal_range']
			#	presets['val_target_min']
			#	presets['val_target_max']
			#	presets['val_target_range']
			edit_measurement (
				parent = self,
				measurement = None,
				single_entry = True,
				presets = presets
			)
			return

		if len(self.__cell_data[col][row]) > 1:
			data = self.__get_choices_from_multi_cell(cell_data = self.__cell_data[col][row], single_selection = True)
		else:
			data = self.__cell_data[col][row][0]

		if data is None:
			return

		edit_measurement(parent = self, measurement = data, single_entry = True)

	#------------------------------------------------------------
#     def OnMouseMotionRowLabel(self, evt):
#         x, y = self.CalcUnscrolledPosition(evt.GetPosition())
#         row = self.YToRow(y)
#         label = self.table().GetRowHelpValue(row)
#         self.GetGridRowLabelWindow().SetToolTip(label or "")
#         evt.Skip()
	def __on_mouse_over_row_labels(self, evt):

		# Use CalcUnscrolledPosition() to get the mouse position within the
		# entire grid including what's offscreen
		x, y = self.CalcUnscrolledPosition(evt.GetX(), evt.GetY())

		row = self.YToRow(y)

		if self.__prev_label_row == row:
			return

		self.__prev_label_row == row

		evt.GetEventObject().SetToolTip(self.get_row_tooltip(row = row))
	#------------------------------------------------------------
#     def OnMouseMotionColLabel(self, evt):
#         x, y = self.CalcUnscrolledPosition(evt.GetPosition())
#         col = self.XToCol(x)
#         label = self.table().GetColHelpValue(col)
#         self.GetGridColLabelWindow().SetToolTip(label or "")
#         evt.Skip()
	#------------------------------------------------------------
	def __on_mouse_over_cells(self, evt):
		"""Calculate where the mouse is and set the tooltip dynamically."""

		# Use CalcUnscrolledPosition() to get the mouse position within the
		# entire grid including what's offscreen
		x, y = self.CalcUnscrolledPosition(evt.GetX(), evt.GetY())

		# use this logic to prevent tooltips outside the actual cells
		# apply to GetRowSize, too
#        tot = 0
#        for col in range(self.NumberCols):
#            tot += self.GetColSize(col)
#            if xpos <= tot:
#                self.tool_tip.Tip = 'Tool tip for Column %s' % (
#                    self.GetColLabelValue(col))
#                break
#            else:  # mouse is in label area beyond the right-most column
#            self.tool_tip.Tip = ''

		row, col = self.XYToCell(x, y)

		if (row == self.__prev_row) and (col == self.__prev_col):
			return

		self.__prev_row = row
		self.__prev_col = col

		evt.GetEventObject().SetToolTip(self.get_cell_tooltip(col=col, row=row))

	#------------------------------------------------------------
	# properties
	#------------------------------------------------------------
	def _get_patient(self):
		return self.__patient

	def _set_patient(self, patient):
		self.__patient = patient
		self.repopulate_grid()

	patient = property(_get_patient, _set_patient)
	#------------------------------------------------------------
	def _set_panel_to_show(self, panel):
		self.__panel_to_show = panel
		self.repopulate_grid()

	panel_to_show = property(lambda x:x, _set_panel_to_show)
	#------------------------------------------------------------
	def _set_show_by_panel(self, show_by_panel):
		self.__show_by_panel = show_by_panel
		self.repopulate_grid()

	show_by_panel = property(lambda x:x, _set_show_by_panel)

#================================================================
# integrated measurements plugin
#================================================================
from Gnumed.wxGladeWidgets import wxgMeasurementsPnl

class cMeasurementsPnl(wxgMeasurementsPnl.wxgMeasurementsPnl, gmRegetMixin.cRegetOnPaintMixin):
	"""Panel holding a grid with lab data. Used as notebook page."""

	def __init__(self, *args, **kwargs):

		wxgMeasurementsPnl.wxgMeasurementsPnl.__init__(self, *args, **kwargs)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)
		self.__display_mode = 'grid'
		self.__init_ui()
		self.__register_interests()
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		gmDispatcher.connect(signal = 'pre_patient_unselection', receiver = self._on_pre_patient_unselection)
		gmDispatcher.connect(signal = 'post_patient_selection', receiver = self._on_post_patient_selection)
		gmDispatcher.connect(signal = 'clin.test_result_mod_db', receiver = self._schedule_data_reget)
		gmDispatcher.connect(signal = 'clin.reviewed_test_results_mod_db', receiver = self._schedule_data_reget)
	#--------------------------------------------------------
	def _on_post_patient_selection(self):
		self._schedule_data_reget()
	#--------------------------------------------------------
	def _on_pre_patient_unselection(self):
		self._GRID_results_all.patient = None
		self._GRID_results_battery.patient = None
	#--------------------------------------------------------
	def _on_add_button_pressed(self, event):
		edit_measurement(parent = self, measurement = None)
	#--------------------------------------------------------
	def _on_manage_types_button_pressed(self, event):
		event.Skip()
		manage_measurement_types(parent = self)
	#--------------------------------------------------------
	def _on_list_button_pressed(self, event):
		event.Skip()
		manage_measurements(parent = self, single_selection = True)#, emr = pat.emr)
	#--------------------------------------------------------
	def _on_review_button_pressed(self, evt):
		self.PopupMenu(self.__action_button_popup)
	#--------------------------------------------------------
	def _on_select_button_pressed(self, evt):
		if self._RBTN_my_unsigned.GetValue() is True:
			self._GRID_results_all.select_cells(unsigned_only = True, accountables_only = True, keep_preselections = False)
		elif self._RBTN_all_unsigned.GetValue() is True:
			self._GRID_results_all.select_cells(unsigned_only = True, accountables_only = False, keep_preselections = False)
	#--------------------------------------------------------
	def _on_manage_panels_button_pressed(self, event):
		manage_test_panels(parent = self)
	#--------------------------------------------------------
	def _on_display_mode_button_pressed(self, event):
		event.Skip()
		if self.__display_mode == 'grid':
			self._BTN_display_mode.SetLabel(_('All: as &Grid'))
			self.__display_mode = 'day'
			#self._GRID_results_all.Hide()
			self._PNL_results_all_grid.Hide()
			if self._PNL_results_all_listed.patient is None:
				self._PNL_results_all_listed.patient = self._GRID_results_all.patient
			self._PNL_results_all_listed.Show()
		else:
			self._BTN_display_mode.SetLabel(_('All: by &Day'))
			self.__display_mode = 'grid'
			self._PNL_results_all_listed.Hide()
			if self._GRID_results_all.patient is None:
				self._GRID_results_all.patient = self._PNL_results_all_listed.patient
			#self._GRID_results_all.Show()
			self._PNL_results_all_grid.Show()
		self.Layout()
	#--------------------------------------------------------
	def __on_sign_current_selection(self, evt):
		self._GRID_results_all.sign_current_selection()
	#--------------------------------------------------------
	def __on_plot_current_selection(self, evt):
		self._GRID_results_all.plot_current_selection()
	#--------------------------------------------------------
	def __on_delete_current_selection(self, evt):
		self._GRID_results_all.delete_current_selection()
	#--------------------------------------------------------
	def _on_panel_selected(self, panel):
		wx.CallAfter(self.__on_panel_selected, panel=panel)
	#--------------------------------------------------------
	def __on_panel_selected(self, panel):
		if panel is None:
			self._TCTRL_panel_comment.SetValue('')
			self._GRID_results_battery.panel_to_show = None
			#self._GRID_results_battery.Hide()
			self._PNL_results_battery_grid.Hide()
		else:
			pnl = self._PRW_panel.GetData(as_instance = True)
			self._TCTRL_panel_comment.SetValue(gmTools.coalesce (
				pnl['comment'],
				''
			))
			self._GRID_results_battery.panel_to_show = pnl
			#self._GRID_results_battery.Show()
			self._PNL_results_battery_grid.Show()
		self._GRID_results_battery.Fit()
		self._GRID_results_all.Fit()
		self.Layout()
	#--------------------------------------------------------
	def _on_panel_selection_modified(self):
		wx.CallAfter(self.__on_panel_selection_modified)
	#--------------------------------------------------------
	def __on_panel_selection_modified(self):
		self._TCTRL_panel_comment.SetValue('')
		if self._PRW_panel.GetValue().strip() == '':
			self._GRID_results_battery.panel_to_show = None
			#self._GRID_results_battery.Hide()
			self._PNL_results_battery_grid.Hide()
			self.Layout()
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __init_ui(self):
		self.SetMinSize((10, 10))

		self.__action_button_popup = wx.Menu(title = _('Perform on selected results:'))

		item = self.__action_button_popup.Append(-1, _('Review and &sign'))
		self.Bind(wx.EVT_MENU, self.__on_sign_current_selection, item)

		item = self.__action_button_popup.Append(-1, _('Plot'))
		self.Bind(wx.EVT_MENU, self.__on_plot_current_selection, item)

		item = self.__action_button_popup.Append(-1, _('Export to &file'))
		self.Bind(wx.EVT_MENU, self._GRID_results_all.current_selection_to_file, item)
		#self.__action_button_popup.Enable(id = menu_id, enable = False)
		item.Enable(enable = False)

		item = self.__action_button_popup.Append(-1, _('Export to &clipboard'))
		self.Bind(wx.EVT_MENU, self._GRID_results_all.current_selection_to_clipboard, item)
		#self.__action_button_popup.Enable(id = menu_id, enable = False)
		item.Enable(enable = False)

		item = self.__action_button_popup.Append(-1, _('&Delete'))
		self.Bind(wx.EVT_MENU, self.__on_delete_current_selection, item)

		# FIXME: create inbox message to staff to phone patient to come in
		# FIXME: generate and let edit a SOAP narrative and include the values

		self._PRW_panel.add_callback_on_selection(callback = self._on_panel_selected)
		self._PRW_panel.add_callback_on_modified(callback = self._on_panel_selection_modified)

		self._GRID_results_battery.show_by_panel = True
		self._GRID_results_battery.panel_to_show = None
		#self._GRID_results_battery.Hide()
		self._PNL_results_battery_grid.Hide()
		self._BTN_display_mode.SetLabel(_('All: by &Day'))
		#self._GRID_results_all.Show()
		self._PNL_results_all_grid.Show()
		self._PNL_results_all_listed.Hide()
		self.Layout()

		self._PRW_panel.SetFocus()
	#--------------------------------------------------------
	# reget mixin API
	#--------------------------------------------------------
	def _populate_with_data(self):
		pat = gmPerson.gmCurrentPatient()
		if pat.connected:
			self._GRID_results_battery.patient = pat
			if self.__display_mode == 'grid':
				self._GRID_results_all.patient = pat
				self._PNL_results_all_listed.patient = None
			else:
				self._GRID_results_all.patient = None
				self._PNL_results_all_listed.patient = pat
		else:
			self._GRID_results_battery.patient = None
			self._GRID_results_all.patient = None
			self._PNL_results_all_listed.patient = None
		return True

#================================================================
# editing widgets
#================================================================
def review_tests(parent=None, tests=None):

	if tests is None:
		return True

	if len(tests) == 0:
		return True

	if parent is None:
		parent = wx.GetApp().GetTopWindow()
	if len(tests) > 10:
		test_count = len(tests)
		tests2show = None
	else:
		test_count = None
		tests2show = tests
	dlg = cMeasurementsReviewDlg(parent, -1, tests = tests2show, test_count = test_count)
	decision = dlg.ShowModal()
	if decision != wx.ID_APPLY:
		return True

	wx.BeginBusyCursor()
	if dlg._RBTN_confirm_abnormal.GetValue():
		abnormal = None
	elif dlg._RBTN_results_normal.GetValue():
		abnormal = False
	else:
		abnormal = True
	if dlg._RBTN_confirm_relevance.GetValue():
		relevant = None
	elif dlg._RBTN_results_not_relevant.GetValue():
		relevant = False
	else:
		relevant = True
	comment = None
	if len(tests) == 1:
		comment = dlg._TCTRL_comment.GetValue()
	make_responsible = dlg._CHBOX_responsible.IsChecked()
	dlg.DestroyLater()
	for test in tests:
		test.set_review (
			technically_abnormal = abnormal,
			clinically_relevant = relevant,
			comment = comment,
			make_me_responsible = make_responsible
		)
	wx.EndBusyCursor()
	return True

#----------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgMeasurementsReviewDlg

class cMeasurementsReviewDlg(wxgMeasurementsReviewDlg.wxgMeasurementsReviewDlg):

	def __init__(self, *args, **kwargs):

		try:
			tests = kwargs['tests']
			del kwargs['tests']
			test_count = len(tests)
			try: del kwargs['test_count']
			except KeyError: pass
		except KeyError:
			tests = None
			test_count = kwargs['test_count']
			del kwargs['test_count']

		wxgMeasurementsReviewDlg.wxgMeasurementsReviewDlg.__init__(self, *args, **kwargs)

		if tests is None:
			msg = _('%s results selected. Too many to list individually.') % test_count
		else:
			msg = '\n'.join (
				[	'%s: %s %s (%s)' % (
						t['unified_abbrev'],
						t['unified_val'],
						t['val_unit'],
						t['clin_when'].strftime('%Y %b %d')
					) for t in tests
				]
			)

		self._LBL_tests.SetLabel(msg)

		if test_count == 1:
			self._TCTRL_comment.Enable(True)
			self._TCTRL_comment.SetValue(gmTools.coalesce(tests[0]['review_comment'], ''))
			if tests[0]['you_are_responsible']:
				self._CHBOX_responsible.Enable(False)

		self.Fit()
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def _on_signoff_button_pressed(self, evt):
		if self.IsModal():
			self.EndModal(wx.ID_APPLY)
		else:
			self.Close()

#================================================================
from Gnumed.wxGladeWidgets import wxgMeasurementEditAreaPnl

class cMeasurementEditAreaPnl(wxgMeasurementEditAreaPnl.wxgMeasurementEditAreaPnl, gmEditArea.cGenericEditAreaMixin):
	"""This edit area saves *new* measurements into the active patient only."""

	def __init__(self, *args, **kwargs):

		try:
			self.__default_date = kwargs['date']
			del kwargs['date']
		except KeyError:
			self.__default_date = None

		wxgMeasurementEditAreaPnl.wxgMeasurementEditAreaPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.__register_interests()

		self.successful_save_msg = _('Successfully saved measurement.')

		self._DPRW_evaluated.display_accuracy = gmDateTime.ACC_MINUTES

	#--------------------------------------------------------
	# generic edit area mixin API
	#----------------------------------------------------------------
	def set_fields(self, fields):
		self._TCTRL_result.SetFocus()
		try:
			self._PRW_test.SetData(data = fields['pk_test_type']['data'])
		except KeyError:
			self._PRW_test.SetFocus()
		try:
			self._DPRW_evaluated.SetData(data = fields['clin_when']['data'])
		except KeyError:
			pass
		try:
			self._PRW_problem.SetData(data = fields['pk_episode']['data'])
		except KeyError:
			pass
		try:
			self._PRW_units.SetText(fields['val_unit']['data'], fields['val_unit']['data'], True)
		except KeyError:
			pass
		try:
			self._TCTRL_normal_min.SetValue(fields['val_normal_min']['data'])
		except KeyError:
			pass
		try:
			self._TCTRL_normal_max.SetValue(fields['val_normal_max']['data'])
		except KeyError:
			pass
		try:
			self._TCTRL_normal_range.SetValue(fields['val_normal_range']['data'])
		except KeyError:
			pass
		try:
			self._TCTRL_target_min.SetValue(fields['val_target_min']['data'])
		except KeyError:
			pass
		try:
			self._TCTRL_target_max.SetValue(fields['val_target_max']['data'])
		except KeyError:
			pass
		try:
			self._TCTRL_target_range.SetValue(fields['val_target_range']['data'])
		except KeyError:
			pass

	#--------------------------------------------------------
	def _refresh_as_new(self):
		self._PRW_test.SetText('', None, True)
		self.__refresh_loinc_info()
		self.__refresh_previous_value()
		self.__update_units_context()
		self._TCTRL_result.SetValue('')
		self._PRW_units.SetText('', None, True)
		self._PRW_abnormality_indicator.SetText('', None, True)
		if self.__default_date is None:
			self._DPRW_evaluated.SetData(data = pyDT.datetime.now(tz = gmDateTime.gmCurrentLocalTimezone))
		else:
			self._DPRW_evaluated.SetData(data =	None)
		self._TCTRL_note_test_org.SetValue('')
		self._PRW_intended_reviewer.SetData(gmStaff.gmCurrentProvider()['pk_staff'])
		self._PRW_problem.SetData()
		self._TCTRL_narrative.SetValue('')
		self._CHBOX_review.SetValue(False)
		self._CHBOX_abnormal.SetValue(False)
		self._CHBOX_relevant.SetValue(False)
		self._CHBOX_abnormal.Enable(False)
		self._CHBOX_relevant.Enable(False)
		self._TCTRL_review_comment.SetValue('')
		self._TCTRL_normal_min.SetValue('')
		self._TCTRL_normal_max.SetValue('')
		self._TCTRL_normal_range.SetValue('')
		self._TCTRL_target_min.SetValue('')
		self._TCTRL_target_max.SetValue('')
		self._TCTRL_target_range.SetValue('')
		self._TCTRL_norm_ref_group.SetValue('')

		self._PRW_test.SetFocus()
	#--------------------------------------------------------
	def _refresh_from_existing(self):
		self._PRW_test.SetData(data = self.data['pk_test_type'])
		self.__refresh_loinc_info()
		self.__refresh_previous_value()
		self.__update_units_context()
		self._TCTRL_result.SetValue(self.data['unified_val'])
		self._PRW_units.SetText(self.data['val_unit'], self.data['val_unit'], True)
		self._PRW_abnormality_indicator.SetText (
			gmTools.coalesce(self.data['abnormality_indicator'], ''),
			gmTools.coalesce(self.data['abnormality_indicator'], ''),
			True
		)
		self._DPRW_evaluated.SetData(data = self.data['clin_when'])
		self._TCTRL_note_test_org.SetValue(gmTools.coalesce(self.data['note_test_org'], ''))
		self._PRW_intended_reviewer.SetData(self.data['pk_intended_reviewer'])
		self._PRW_problem.SetData(self.data['pk_episode'])
		self._TCTRL_narrative.SetValue(gmTools.coalesce(self.data['comment'], ''))
		self._CHBOX_review.SetValue(False)
		self._CHBOX_abnormal.SetValue(gmTools.coalesce(self.data['is_technically_abnormal'], False))
		self._CHBOX_relevant.SetValue(gmTools.coalesce(self.data['is_clinically_relevant'], False))
		self._CHBOX_abnormal.Enable(False)
		self._CHBOX_relevant.Enable(False)
		self._TCTRL_review_comment.SetValue(gmTools.coalesce(self.data['review_comment'], ''))
		self._TCTRL_normal_min.SetValue(str(gmTools.coalesce(self.data['val_normal_min'], '')))
		self._TCTRL_normal_max.SetValue(str(gmTools.coalesce(self.data['val_normal_max'], '')))
		self._TCTRL_normal_range.SetValue(gmTools.coalesce(self.data['val_normal_range'], ''))
		self._TCTRL_target_min.SetValue(str(gmTools.coalesce(self.data['val_target_min'], '')))
		self._TCTRL_target_max.SetValue(str(gmTools.coalesce(self.data['val_target_max'], '')))
		self._TCTRL_target_range.SetValue(gmTools.coalesce(self.data['val_target_range'], ''))
		self._TCTRL_norm_ref_group.SetValue(gmTools.coalesce(self.data['norm_ref_group'], ''))

		self._TCTRL_result.SetFocus()
	#--------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._PRW_test.SetText('', None, True)
		self.__refresh_loinc_info()
		self.__refresh_previous_value()
		self.__update_units_context()
		self._TCTRL_result.SetValue('')
		self._PRW_units.SetText('', None, True)
		self._PRW_abnormality_indicator.SetText('', None, True)
		self._DPRW_evaluated.SetData(data = self.data['clin_when'])
		self._TCTRL_note_test_org.SetValue('')
		self._PRW_intended_reviewer.SetData(self.data['pk_intended_reviewer'])
		self._PRW_problem.SetData(self.data['pk_episode'])
		self._TCTRL_narrative.SetValue('')
		self._CHBOX_review.SetValue(False)
		self._CHBOX_abnormal.SetValue(False)
		self._CHBOX_relevant.SetValue(False)
		self._CHBOX_abnormal.Enable(False)
		self._CHBOX_relevant.Enable(False)
		self._TCTRL_review_comment.SetValue('')
		self._TCTRL_normal_min.SetValue('')
		self._TCTRL_normal_max.SetValue('')
		self._TCTRL_normal_range.SetValue('')
		self._TCTRL_target_min.SetValue('')
		self._TCTRL_target_max.SetValue('')
		self._TCTRL_target_range.SetValue('')
		self._TCTRL_norm_ref_group.SetValue('')

		self._PRW_test.SetFocus()
	#--------------------------------------------------------
	def _valid_for_save(self):

		validity = True

		if not self._DPRW_evaluated.is_valid_timestamp():
			self._DPRW_evaluated.display_as_valid(False)
			validity = False
		else:
			self._DPRW_evaluated.display_as_valid(True)

		val = self._TCTRL_result.GetValue().strip()
		if val == '':
			validity = False
			self.display_ctrl_as_valid(self._TCTRL_result, False)
		else:
			self.display_ctrl_as_valid(self._TCTRL_result, True)
			numeric, val = gmTools.input2decimal(val)
			if numeric:
				if self._PRW_units.GetValue().strip() == '':
					self._PRW_units.display_as_valid(False)
					validity = False
				else:
					self._PRW_units.display_as_valid(True)
			else:
				self._PRW_units.display_as_valid(True)

		if self._PRW_problem.GetValue().strip() == '':
			self._PRW_problem.display_as_valid(False)
			validity = False
		else:
			self._PRW_problem.display_as_valid(True)

		if self._PRW_test.GetValue().strip() == '':
			self._PRW_test.display_as_valid(False)
			validity = False
		else:
			self._PRW_test.display_as_valid(True)

		if self._PRW_intended_reviewer.GetData() is None:
			self._PRW_intended_reviewer.display_as_valid(False)
			validity = False
		else:
			self._PRW_intended_reviewer.display_as_valid(True)

		ctrls = [self._TCTRL_normal_min, self._TCTRL_normal_max, self._TCTRL_target_min, self._TCTRL_target_max]
		for widget in ctrls:
			val = widget.GetValue().strip()
			if val == '':
				continue
			try:
				decimal.Decimal(val.replace(',', '.', 1))
				self.display_ctrl_as_valid(widget, True)
			except Exception:
				validity = False
				self.display_ctrl_as_valid(widget, False)

		if validity is False:
			self.StatusText = _('Cannot save result. Invalid or missing essential input.')

		return validity
	#--------------------------------------------------------
	def _save_as_new(self):

		emr = gmPerson.gmCurrentPatient().emr

		success, result = gmTools.input2decimal(self._TCTRL_result.GetValue())
		if success:
			v_num = result
			v_al = None
		else:
			v_al = self._TCTRL_result.GetValue().strip()
			v_num = None

		pk_type = self._PRW_test.GetData()
		if pk_type is None:
			abbrev = self._PRW_test.GetValue().strip()
			name = self._PRW_test.GetValue().strip()
			unit = gmTools.coalesce(self._PRW_units.GetData(), self._PRW_units.GetValue()).strip()
			lab = manage_measurement_orgs (
				parent = self,
				msg = _('Please select (or create) a lab for the new test type [%s in %s]') % (name, unit)
			)
			if lab is not None:
				lab = lab['pk_test_org']
			tt = gmPathLab.create_measurement_type (
				lab = lab,
				abbrev = abbrev,
				name = name,
				unit = unit
			)
			pk_type = tt['pk_test_type']

		tr = emr.add_test_result (
			episode = self._PRW_problem.GetData(can_create=True, is_open=False),
			type = pk_type,
			intended_reviewer = self._PRW_intended_reviewer.GetData(),
			val_num = v_num,
			val_alpha = v_al,
			unit = self._PRW_units.GetValue()
		)

		tr['clin_when'] = self._DPRW_evaluated.GetData().get_pydt()

		ctrls = [
			('abnormality_indicator', self._PRW_abnormality_indicator),
			('note_test_org', self._TCTRL_note_test_org),
			('comment', self._TCTRL_narrative),
			('val_normal_range', self._TCTRL_normal_range),
			('val_target_range', self._TCTRL_target_range),
			('norm_ref_group', self._TCTRL_norm_ref_group)
		]
		for field, widget in ctrls:
			tr[field] = widget.GetValue().strip()

		ctrls = [
			('val_normal_min', self._TCTRL_normal_min),
			('val_normal_max', self._TCTRL_normal_max),
			('val_target_min', self._TCTRL_target_min),
			('val_target_max', self._TCTRL_target_max)
		]
		for field, widget in ctrls:
			val = widget.GetValue().strip()
			if val == '':
				tr[field] = None
			else:
				tr[field] = decimal.Decimal(val.replace(',', '.', 1))

		tr.save_payload()

		if self._CHBOX_review.GetValue() is True:
			tr.set_review (
				technically_abnormal = self._CHBOX_abnormal.GetValue(),
				clinically_relevant = self._CHBOX_relevant.GetValue(),
				comment = gmTools.none_if(self._TCTRL_review_comment.GetValue().strip(), ''),
				make_me_responsible = False
			)

		self.data = tr

#		wx.CallAfter (
#			plot_adjacent_measurements,
#			test = self.data,
#			plot_singular_result = False,
#			use_default_template = True
#		)

		return True
	#--------------------------------------------------------
	def _save_as_update(self):

		success, result = gmTools.input2decimal(self._TCTRL_result.GetValue())
		if success:
			v_num = result
			v_al = None
		else:
			v_num = None
			v_al = self._TCTRL_result.GetValue().strip()

		pk_type = self._PRW_test.GetData()
		if pk_type is None:
			abbrev = self._PRW_test.GetValue().strip()
			name = self._PRW_test.GetValue().strip()
			unit = gmTools.coalesce(self._PRW_units.GetData(), self._PRW_units.GetValue()).strip()
			lab = manage_measurement_orgs (
				parent = self,
				msg = _('Please select (or create) a lab for the new test type [%s in %s]') % (name, unit)
			)
			if lab is not None:
				lab = lab['pk_test_org']
			tt = gmPathLab.create_measurement_type (
				lab = None,
				abbrev = abbrev,
				name = name,
				unit = unit
			)
			pk_type = tt['pk_test_type']

		tr = self.data

		tr['pk_episode'] = self._PRW_problem.GetData(can_create=True, is_open=False)
		tr['pk_test_type'] = pk_type
		tr['pk_intended_reviewer'] = self._PRW_intended_reviewer.GetData()
		tr['val_num'] = v_num
		tr['val_alpha'] = v_al
		tr['val_unit'] = gmTools.coalesce(self._PRW_units.GetData(), self._PRW_units.GetValue()).strip()
		tr['clin_when'] = self._DPRW_evaluated.GetData().get_pydt()

		ctrls = [
			('abnormality_indicator', self._PRW_abnormality_indicator),
			('note_test_org', self._TCTRL_note_test_org),
			('comment', self._TCTRL_narrative),
			('val_normal_range', self._TCTRL_normal_range),
			('val_target_range', self._TCTRL_target_range),
			('norm_ref_group', self._TCTRL_norm_ref_group)
		]
		for field, widget in ctrls:
			tr[field] = widget.GetValue().strip()

		ctrls = [
			('val_normal_min', self._TCTRL_normal_min),
			('val_normal_max', self._TCTRL_normal_max),
			('val_target_min', self._TCTRL_target_min),
			('val_target_max', self._TCTRL_target_max)
		]
		for field, widget in ctrls:
			val = widget.GetValue().strip()
			if val == '':
				tr[field] = None
			else:
				tr[field] = decimal.Decimal(val.replace(',', '.', 1))

		tr.save_payload()

		if self._CHBOX_review.GetValue() is True:
			tr.set_review (
				technically_abnormal = self._CHBOX_abnormal.GetValue(),
				clinically_relevant = self._CHBOX_relevant.GetValue(),
				comment = gmTools.none_if(self._TCTRL_review_comment.GetValue().strip(), ''),
				make_me_responsible = False
			)

#		wx.CallAfter (
#			plot_adjacent_measurements,
#			test = self.data,
#			plot_singular_result = False,
#			use_default_template = True
#		)

		return True
	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):
		self._PRW_test.add_callback_on_lose_focus(self._on_leave_test_prw)
		self._PRW_abnormality_indicator.add_callback_on_lose_focus(self._on_leave_indicator_prw)
		self._PRW_units.add_callback_on_lose_focus(self._on_leave_unit_prw)
	#--------------------------------------------------------
	def _on_leave_test_prw(self):
		self.__refresh_loinc_info()
		self.__refresh_previous_value()
		self.__update_units_context()
		# only works if we've got a unit set
		self.__update_normal_range()
		self.__update_clinical_range()
	#--------------------------------------------------------
	def _on_leave_unit_prw(self):
		# maybe we've got a unit now ?
		self.__update_normal_range()
		self.__update_clinical_range()
	#--------------------------------------------------------
	def _on_leave_indicator_prw(self):
		# if the user hasn't explicitly enabled reviewing
		if not self._CHBOX_review.GetValue():
			self._CHBOX_abnormal.SetValue(self._PRW_abnormality_indicator.GetValue().strip() != '')
	#--------------------------------------------------------
	def _on_review_box_checked(self, evt):
		self._CHBOX_abnormal.Enable(self._CHBOX_review.GetValue())
		self._CHBOX_relevant.Enable(self._CHBOX_review.GetValue())
		self._TCTRL_review_comment.Enable(self._CHBOX_review.GetValue())
	#--------------------------------------------------------
	def _on_test_info_button_pressed(self, event):
		pk = self._PRW_test.GetData()
		if pk is not None:
			tt = gmPathLab.cMeasurementType(aPK_obj = pk)
			search_term = '%s %s %s' % (
				tt['name'],
				tt['abbrev'],
				gmTools.coalesce(tt['loinc'], '')
			)
		else:
			search_term = self._PRW_test.GetValue()

		search_term = search_term.replace(' ', '+')

		call_browser_on_measurement_type(measurement_type = search_term)
	#--------------------------------------------------------
	def _on_manage_episodes_button_pressed(self, event):
		event.Skip()
		gmEMRStructWidgets.manage_episodes(parent = self)
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __update_units_context(self):

		if self._PRW_test.GetData() is None:
			self._PRW_units.unset_context(context = 'pk_type')
			self._PRW_units.unset_context(context = 'loinc')
			if self._PRW_test.GetValue().strip() == '':
				self._PRW_units.unset_context(context = 'test_name')
			else:
				self._PRW_units.set_context(context = 'test_name', val = self._PRW_test.GetValue().strip())
			return

		tt = self._PRW_test.GetData(as_instance = True)

		self._PRW_units.set_context(context = 'pk_type', val = tt['pk_test_type'])
		self._PRW_units.set_context(context = 'test_name', val = tt['name'])

		if tt['loinc'] is not None:
			self._PRW_units.set_context(context = 'loinc', val = tt['loinc'])

		# closest unit
		if self._PRW_units.GetValue().strip() == '':
			clin_when = self._DPRW_evaluated.GetData()
			if clin_when is None:
				unit = tt.temporally_closest_unit
			else:
				clin_when = clin_when.get_pydt()
				unit = tt.get_temporally_closest_unit(timestamp = clin_when)
			if unit is None:
				self._PRW_units.SetText('', unit, True)
			else:
				self._PRW_units.SetText(unit, unit, True)

	#--------------------------------------------------------
	def __update_normal_range(self):
		unit = self._PRW_units.GetValue().strip()
		if unit == '':
			return
		if self._PRW_test.GetData() is None:
			return
		for ctrl in [self._TCTRL_normal_min, self._TCTRL_normal_max, self._TCTRL_normal_range, self._TCTRL_norm_ref_group]:
			if ctrl.GetValue().strip() != '':
				return
		tt = self._PRW_test.GetData(as_instance = True)
		test_w_range = tt.get_temporally_closest_normal_range (
			unit,
			timestamp = self._DPRW_evaluated.GetData().get_pydt()
		)
		if test_w_range is None:
			return
		self._TCTRL_normal_min.SetValue(str(gmTools.coalesce(test_w_range['val_normal_min'], '')))
		self._TCTRL_normal_max.SetValue(str(gmTools.coalesce(test_w_range['val_normal_max'], '')))
		self._TCTRL_normal_range.SetValue(gmTools.coalesce(test_w_range['val_normal_range'], ''))
		self._TCTRL_norm_ref_group.SetValue(gmTools.coalesce(test_w_range['norm_ref_group'], ''))

	#--------------------------------------------------------
	def __update_clinical_range(self):
		unit = self._PRW_units.GetValue().strip()
		if unit == '':
			return
		if self._PRW_test.GetData() is None:
			return
		for ctrl in [self._TCTRL_target_min, self._TCTRL_target_max, self._TCTRL_target_range]:
			if ctrl.GetValue().strip() != '':
				return
		tt = self._PRW_test.GetData(as_instance = True)
		test_w_range = tt.get_temporally_closest_target_range (
			unit,
			gmPerson.gmCurrentPatient().ID,
			timestamp = self._DPRW_evaluated.GetData().get_pydt()
		)
		if test_w_range is None:
			return
		self._TCTRL_target_min.SetValue(str(gmTools.coalesce(test_w_range['val_target_min'], '')))
		self._TCTRL_target_max.SetValue(str(gmTools.coalesce(test_w_range['val_target_max'], '')))
		self._TCTRL_target_range.SetValue(gmTools.coalesce(test_w_range['val_target_range'], ''))

	#--------------------------------------------------------
	def __refresh_loinc_info(self):

		self._TCTRL_loinc.SetValue('')

		if self._PRW_test.GetData() is None:
			return

		tt = self._PRW_test.GetData(as_instance = True)

		if tt['loinc'] is None:
			return

		info = gmLOINC.loinc2term(loinc = tt['loinc'])
		if len(info) == 0:
			self._TCTRL_loinc.SetValue('')
			return

		self._TCTRL_loinc.SetValue('%s: %s' % (tt['loinc'], info[0]))

	#--------------------------------------------------------
	def __refresh_previous_value(self):
		self._TCTRL_previous_value.SetValue('')
		# it doesn't make much sense to show the most
		# recent value when editing an existing one
		if self.data is not None:
			return

		if self._PRW_test.GetData() is None:
			return

		tt = self._PRW_test.GetData(as_instance = True)
		most_recent_results = tt.get_most_recent_results (
			max_no_of_results = 1,
			patient = gmPerson.gmCurrentPatient().ID
		)
		if len(most_recent_results) == 0:
			return

		most_recent = most_recent_results[0]
		self._TCTRL_previous_value.SetValue(_('%s ago: %s%s%s (%s%s)') % (
			gmDateTime.format_interval_medically(gmDateTime.pydt_now_here() - most_recent['clin_when']),
			most_recent['unified_val'],
			gmTools.coalesce(most_recent['val_unit'], ''),
			gmTools.coalesce(most_recent['abnormality_indicator'], '', ' "%s"'),
			most_recent['abbrev_tt'],
			gmTools.coalesce(most_recent.formatted_range, '', ': %s')
		))
		self._TCTRL_previous_value.SetToolTip(most_recent.format (
			with_review = True,
			with_evaluation = False,
			with_ranges = True,
			with_episode = True,
			with_type_details=True
		))

#================================================================
# measurement type handling
#================================================================
def pick_measurement_types(parent=None, msg=None, right_column=None, picks=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	if msg is None:
		msg = _('Pick the relevant measurement types.')

	if right_column is None:
		right_columns = [_('Picked')]
	else:
		right_columns = [right_column]

	picker = gmListWidgets.cItemPickerDlg(parent, -1, msg = msg)
	picker.set_columns(columns = [_('Known measurement types')], columns_right = right_columns)
	types = gmPathLab.get_measurement_types(order_by = 'unified_abbrev')
	picker.set_choices (
		choices = [
			'%s: %s%s' % (
				t['unified_abbrev'],
				t['unified_name'],
				gmTools.coalesce(t['name_org'], '', ' (%s)')
			)
			for t in types
		],
		data = types
	)
	if picks is not None:
		picker.set_picks (
			picks = [
				'%s: %s%s' % (
					p['unified_abbrev'],
					p['unified_name'],
					gmTools.coalesce(p['name_org'], '', ' (%s)')
				)
				for p in picks
			],
			data = picks
		)
	result = picker.ShowModal()

	if result == wx.ID_CANCEL:
		picker.DestroyLater()
		return None

	picks = picker.picks
	picker.DestroyLater()
	return picks

#----------------------------------------------------------------
def manage_measurement_types(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#------------------------------------------------------------
	def edit(test_type=None):
		ea = cMeasurementTypeEAPnl(parent, -1, type = test_type)
		dlg = gmEditArea.cGenericEditAreaDlg2 (
			parent = parent,
			id = -1,
			edit_area = ea,
			single_entry = gmTools.bool2subst((test_type is None), False, True)
		)
		dlg.SetTitle(gmTools.coalesce(test_type, _('Adding measurement type'), _('Editing measurement type')))

		if dlg.ShowModal() == wx.ID_OK:
			dlg.DestroyLater()
			return True

		dlg.DestroyLater()
		return False

	#------------------------------------------------------------
	def delete(measurement_type):
		if measurement_type.in_use:
			gmDispatcher.send (
				signal = 'statustext',
				beep = True,
				msg = _('Cannot delete measurement type [%s (%s)] because it is in use.') % (measurement_type['name'], measurement_type['abbrev'])
			)
			return False
		gmPathLab.delete_measurement_type(measurement_type = measurement_type['pk_test_type'])
		return True

	#------------------------------------------------------------
	def get_tooltip(test_type):
		return test_type.format()

	#------------------------------------------------------------
	def manage_aggregates(test_type):
		manage_meta_test_types(parent = parent)
		return False

	#------------------------------------------------------------
	def manage_panels_of_type(test_type):
		if test_type['loinc'] is None:
			return False
		all_panels = gmPathLab.get_test_panels(order_by = 'description')
		curr_panels = test_type.test_panels
		if curr_panels is None:
			curr_panels = []
		panel_candidates = [ p for p in all_panels if p['pk_test_panel'] not in [
			c_pnl['pk_test_panel'] for c_pnl in curr_panels
		] ]
		picker = gmListWidgets.cItemPickerDlg(parent, -1, title = 'Panels with [%s]' % test_type['abbrev'])
		picker.set_columns(['Panels available'], ['Panels [%s] is to be on' % test_type['abbrev']])
		picker.set_choices (
			choices = [ u'%s (%s)' % (c['description'], gmTools.coalesce(c['comment'], '')) for c in panel_candidates ],
			data = panel_candidates
		)
		picker.set_picks (
			picks = [ u'%s (%s)' % (c['description'], gmTools.coalesce(c['comment'], '')) for c in curr_panels ],
			data = curr_panels
		)
		exit_type = picker.ShowModal()
		if exit_type == wx.ID_CANCEL:
			return False

		# add picked panels which aren't currently in the panel list
		panels2add = [ p for p in picker.picks if p['pk_test_panel'] not in [
			c_pnl['pk_test_panel'] for c_pnl in curr_panels
		] ]
		# remove unpicked panels off the current panel list
		panels2remove = [ p for p in curr_panels if p['pk_test_panel'] not in [
			picked_pnl['pk_test_panel'] for picked_pnl in picker.picks
		] ]
		for new_panel in panels2add:
			new_panel.add_loinc(test_type['loinc'])
		for stale_panel in panels2remove:
			stale_panel.remove_loinc(test_type['loinc'])

		return True

	#------------------------------------------------------------
	def refresh(lctrl):
		mtypes = gmPathLab.get_measurement_types(order_by = 'name, abbrev')
		items = [ [
			m['abbrev'],
			m['name'],
			gmTools.coalesce(m['reference_unit'], ''),
			gmTools.coalesce(m['loinc'], ''),
			gmTools.coalesce(m['comment_type'], ''),
			gmTools.coalesce(m['name_org'], '?'),
			gmTools.coalesce(m['comment_org'], ''),
			m['pk_test_type']
		] for m in mtypes ]
		lctrl.set_string_items(items)
		lctrl.set_data(mtypes)

	#------------------------------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		caption = _('Measurement types.'),
		columns = [ _('Abbrev'), _('Name'), _('Unit'), _('LOINC'), _('Comment'), _('Org'), _('Comment'), '#' ],
		single_selection = True,
		refresh_callback = refresh,
		edit_callback = edit,
		new_callback = edit,
		delete_callback = delete,
		list_tooltip_callback = get_tooltip,
		left_extra_button = (_('%s &Aggregate') % gmTools.u_sum, _('Manage aggregations (%s) of tests into groups.') % gmTools.u_sum, manage_aggregates),
		middle_extra_button = (_('Select panels'), _('Select panels the focussed test type is to belong to.'), manage_panels_of_type)
	)

#----------------------------------------------------------------
class cMeasurementTypePhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		query = """
SELECT DISTINCT ON (field_label)
	pk_test_type AS data,
	name
		|| ' ('
		|| coalesce (
			(SELECT unit || ' @ ' || organization FROM clin.v_test_orgs c_vto WHERE c_vto.pk_test_org = c_vtt.pk_test_org),
			'%(in_house)s'
			)
		|| ')'
	AS field_label,
	name
		|| ' ('
		|| abbrev || ', '
		|| coalesce(abbrev_meta || ': ' || name_meta || ', ', '')
		|| coalesce (
			(SELECT unit || ' @ ' || organization FROM clin.v_test_orgs c_vto WHERE c_vto.pk_test_org = c_vtt.pk_test_org),
			'%(in_house)s'
			)
		|| ')'
	AS list_label
FROM
	clin.v_test_types c_vtt
WHERE
	abbrev_meta %%(fragment_condition)s
		OR
	name_meta %%(fragment_condition)s
		OR
	abbrev %%(fragment_condition)s
		OR
	name %%(fragment_condition)s
ORDER BY field_label
LIMIT 50""" % {'in_house': _('generic / in house lab')}

		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(1, 2, 4)
		mp.word_separators = '[ \t:@]+'
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.matcher = mp
		self.SetToolTip(_('Select the type of measurement.'))
		self.selection_only = False

	#------------------------------------------------------------
	def _data2instance(self, link_obj=None):
		if self.GetData() is None:
			return None

		return gmPathLab.cMeasurementType(aPK_obj = self.GetData())

	#------------------------------------------------------------
	def set_from_instance(self, instance):
		lab = gmPathLab.cTestOrg(aPK_obj = instance['pk_test_org'])
		field_label = '%s (%s @ %s)' % (
			instance['name'],
			lab['unit'],
			lab['organization']
		)
		return self.SetText(value = field_label, data = instance['pk_test_type'])

	#------------------------------------------------------------
	def set_from_pk(self, pk):
		return self.set_from_instance(gmPathLab.cMeasurementType(aPK_obj = pk))

	#---------------------------------------------------------
	def SetData(self, data=None):
		return self.set_from_pk(pk = data)

#----------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgMeasurementTypeEAPnl

class cMeasurementTypeEAPnl(wxgMeasurementTypeEAPnl.wxgMeasurementTypeEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['type']
			del kwargs['type']
		except KeyError:
			data = None

		wxgMeasurementTypeEAPnl.wxgMeasurementTypeEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)
		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

		self.__init_ui()

	#----------------------------------------------------------------
	def __init_ui(self):

		# name phraseweel
		query = """
select distinct on (name)
	pk,
	name
from clin.test_type
where
	name %(fragment_condition)s
order by name
limit 50"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(1, 2, 4)
		self._PRW_name.matcher = mp
		self._PRW_name.selection_only = False
		self._PRW_name.add_callback_on_lose_focus(callback = self._on_name_lost_focus)

		# abbreviation
		query = """
select distinct on (abbrev)
	pk,
	abbrev
from clin.test_type
where
	abbrev %(fragment_condition)s
order by abbrev
limit 50"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(1, 2, 3)
		self._PRW_abbrev.matcher = mp
		self._PRW_abbrev.selection_only = False

		# unit
		self._PRW_reference_unit.selection_only = False

		# loinc
		mp = gmLOINC.cLOINCMatchProvider()
		mp.setThresholds(1, 2, 4)
		#mp.print_queries = True
		#mp.word_separators = '[ \t:@]+'
		self._PRW_loinc.matcher = mp
		self._PRW_loinc.selection_only = False
		self._PRW_loinc.add_callback_on_lose_focus(callback = self._on_loinc_lost_focus)

	#----------------------------------------------------------------
	def _on_name_lost_focus(self):

		test = self._PRW_name.GetValue().strip()

		if test == '':
			self._PRW_reference_unit.unset_context(context = 'test_name')
			return

		self._PRW_reference_unit.set_context(context = 'test_name', val = test)

	#----------------------------------------------------------------
	def _on_loinc_lost_focus(self):
		loinc = self._PRW_loinc.GetData()

		if loinc is None:
			self._TCTRL_loinc_info.SetValue('')
			self._PRW_reference_unit.unset_context(context = 'loinc')
			return

		self._PRW_reference_unit.set_context(context = 'loinc', val = loinc)

		info = gmLOINC.loinc2term(loinc = loinc)
		if len(info) == 0:
			self._TCTRL_loinc_info.SetValue('')
			return

		self._TCTRL_loinc_info.SetValue(info[0])

	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		has_errors = False
		for field in [self._PRW_name, self._PRW_abbrev, self._PRW_reference_unit]:
			if field.GetValue().strip() in ['', None]:
				has_errors = True
				field.display_as_valid(valid = False)
			else:
				field.display_as_valid(valid = True)
			field.Refresh()

		return (not has_errors)

	#----------------------------------------------------------------
	def _save_as_new(self):

		pk_org = self._PRW_test_org.GetData()
		if pk_org is None:
			pk_org = gmPathLab.create_test_org (
				name = gmTools.none_if(self._PRW_test_org.GetValue().strip(), '')
			)['pk_test_org']

		tt = gmPathLab.create_measurement_type (
			lab = pk_org,
			abbrev = self._PRW_abbrev.GetValue().strip(),
			name = self._PRW_name.GetValue().strip(),
			unit = gmTools.coalesce (
				self._PRW_reference_unit.GetData(),
				self._PRW_reference_unit.GetValue()
			).strip()
		)
		if self._PRW_loinc.GetData() is not None:
			tt['loinc'] = gmTools.none_if(self._PRW_loinc.GetData().strip(), '')
		else:
			tt['loinc'] = gmTools.none_if(self._PRW_loinc.GetValue().strip(), '')
		tt['comment_type'] = gmTools.none_if(self._TCTRL_comment_type.GetValue().strip(), '')
		tt['pk_meta_test_type'] = self._PRW_meta_type.GetData()

		tt.save()

		self.data = tt

		return True
	#----------------------------------------------------------------
	def _save_as_update(self):

		pk_org = self._PRW_test_org.GetData()
		if pk_org is None:
			pk_org = gmPathLab.create_test_org (
				name = gmTools.none_if(self._PRW_test_org.GetValue().strip(), '')
			)['pk_test_org']

		self.data['pk_test_org'] = pk_org
		self.data['abbrev'] = self._PRW_abbrev.GetValue().strip()
		self.data['name'] = self._PRW_name.GetValue().strip()
		self.data['reference_unit'] = gmTools.coalesce (
			self._PRW_reference_unit.GetData(),
			self._PRW_reference_unit.GetValue()
		).strip()
		old_loinc = self.data['loinc']
		if self._PRW_loinc.GetData() is not None:
			self.data['loinc'] = gmTools.none_if(self._PRW_loinc.GetData().strip(), '')
		else:
			self.data['loinc'] = gmTools.none_if(self._PRW_loinc.GetValue().strip(), '')
		new_loinc = self.data['loinc']
		self.data['comment_type'] = gmTools.none_if(self._TCTRL_comment_type.GetValue().strip(), '')
		self.data['pk_meta_test_type'] = self._PRW_meta_type.GetData()
		self.data.save()

		# was it, AND can it be, on any panel ?
		if None not in [old_loinc, new_loinc]:
			# would it risk being dropped from any panel ?
			if new_loinc != old_loinc:
				for panel in gmPathLab.get_test_panels(loincs = [old_loinc]):
					pnl_loincs = panel.included_loincs
					if new_loinc not in pnl_loincs:
						pnl_loincs.append(new_loinc)
						panel.included_loincs = pnl_loincs
					# do not remove old_loinc as it may sit on another
					# test type which we haven't removed it from yet

		return True

	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._PRW_name.SetText('', None, True)
		self._on_name_lost_focus()
		self._PRW_abbrev.SetText('', None, True)
		self._PRW_reference_unit.SetText('', None, True)
		self._PRW_loinc.SetText('', None, True)
		self._on_loinc_lost_focus()
		self._TCTRL_comment_type.SetValue('')
		self._PRW_test_org.SetText('', None, True)
		self._PRW_meta_type.SetText('', None, True)

		self._PRW_name.SetFocus()
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._PRW_name.SetText(self.data['name'], self.data['name'], True)
		self._on_name_lost_focus()
		self._PRW_abbrev.SetText(self.data['abbrev'], self.data['abbrev'], True)
		self._PRW_reference_unit.SetText (
			gmTools.coalesce(self.data['reference_unit'], ''),
			self.data['reference_unit'],
			True
		)
		self._PRW_loinc.SetText (
			gmTools.coalesce(self.data['loinc'], ''),
			self.data['loinc'],
			True
		)
		self._on_loinc_lost_focus()
		self._TCTRL_comment_type.SetValue(gmTools.coalesce(self.data['comment_type'], ''))
		self._PRW_test_org.SetText (
			gmTools.coalesce(self.data['pk_test_org'], '', self.data['name_org']),
			self.data['pk_test_org'],
			True
		)
		if self.data['pk_meta_test_type'] is None:
			self._PRW_meta_type.SetText('', None, True)
		else:
			self._PRW_meta_type.SetText('%s: %s' % (self.data['abbrev_meta'], self.data['name_meta']), self.data['pk_meta_test_type'], True)

		self._PRW_name.SetFocus()
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()
		self._PRW_test_org.SetText (
			gmTools.coalesce(self.data['pk_test_org'], '', self.data['name_org']),
			self.data['pk_test_org'],
			True
		)
		self._PRW_name.SetFocus()

#================================================================
_SQL_units_from_test_results = """
	-- via clin.v_test_results.pk_type (for types already used in results)
	SELECT
		val_unit AS data,
		val_unit AS field_label,
		val_unit || ' (' || name_tt || ')' AS list_label,
		1 AS rank
	FROM
		clin.v_test_results
	WHERE
		(
			val_unit %(fragment_condition)s
				OR
			reference_unit %(fragment_condition)s
		)
		%(ctxt_type_pk)s
		%(ctxt_test_name)s
"""

_SQL_units_from_test_types = """
	-- via clin.test_type (for types not yet used in results)
	SELECT
		reference_unit AS data,
		reference_unit AS field_label,
		reference_unit || ' (' || name || ')' AS list_label,
		2 AS rank
	FROM
		clin.test_type
	WHERE
		reference_unit %(fragment_condition)s
		%(ctxt_ctt)s
"""

_SQL_units_from_loinc_ipcc = """
	-- via ref.loinc.ipcc_units
	SELECT
		ipcc_units AS data,
		ipcc_units AS field_label,
		ipcc_units || ' (LOINC.ipcc: ' || term || ')' AS list_label,
		3 AS rank
	FROM
		ref.loinc
	WHERE
		ipcc_units %(fragment_condition)s
		%(ctxt_loinc)s
		%(ctxt_loinc_term)s
"""

_SQL_units_from_loinc_submitted = """
	-- via ref.loinc.submitted_units
	SELECT
		submitted_units AS data,
		submitted_units AS field_label,
		submitted_units || ' (LOINC.submitted:' || term || ')' AS list_label,
		3 AS rank
	FROM
		ref.loinc
	WHERE
		submitted_units %(fragment_condition)s
		%(ctxt_loinc)s
		%(ctxt_loinc_term)s
"""

_SQL_units_from_loinc_example = """
	-- via ref.loinc.example_units
	SELECT
		example_units AS data,
		example_units AS field_label,
		example_units || ' (LOINC.example: ' || term || ')' AS list_label,
		3 AS rank
	FROM
		ref.loinc
	WHERE
		example_units %(fragment_condition)s
		%(ctxt_loinc)s
		%(ctxt_loinc_term)s
"""

_SQL_units_from_substance_doses = """
	-- via ref.v_substance_doses.unit
	SELECT
		unit AS data,
		unit AS field_label,
		unit || ' (' || substance || ')' AS list_label,
		2 AS rank
	FROM
		ref.v_substance_doses
	WHERE
		unit %(fragment_condition)s
		%(ctxt_substance)s
"""

_SQL_units_from_substance_doses2 = """
	-- via ref.v_substance_doses.dose_unit
	SELECT
		dose_unit AS data,
		dose_unit AS field_label,
		dose_unit || ' (' || substance || ')' AS list_label,
		2 AS rank
	FROM
		ref.v_substance_doses
	WHERE
		dose_unit %(fragment_condition)s
		%(ctxt_substance)s
"""

#----------------------------------------------------------------
class cUnitPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		query = """
SELECT DISTINCT ON (data)
	data,
	field_label,
	list_label
FROM (

	SELECT
		data,
		field_label,
		list_label,
		rank
	FROM (
		(%s) UNION ALL
		(%s) UNION ALL
		(%s) UNION ALL
		(%s) UNION ALL
		(%s) UNION ALL
		(%s) UNION ALL
		(%s)
	) AS all_matching_units
	WHERE data IS NOT NULL
	ORDER BY rank, list_label

) AS ranked_matching_units
LIMIT 50""" % (
			_SQL_units_from_test_results,
			_SQL_units_from_test_types,
			_SQL_units_from_loinc_ipcc,
			_SQL_units_from_loinc_submitted,
			_SQL_units_from_loinc_example,
			_SQL_units_from_substance_doses,
			_SQL_units_from_substance_doses2
		)

		ctxt = {
			'ctxt_type_pk': {
				'where_part': 'AND pk_test_type = %(pk_type)s',
				'placeholder': 'pk_type'
			},
			'ctxt_test_name': {
				'where_part': 'AND %(test_name)s IN (name_tt, name_meta, abbrev_meta)',
				'placeholder': 'test_name'
			},
			'ctxt_ctt': {
				'where_part': 'AND %(test_name)s IN (name, abbrev)',
				'placeholder': 'test_name'
			},
			'ctxt_loinc': {
				'where_part': 'AND code = %(loinc)s',
				'placeholder': 'loinc'
			},
			'ctxt_loinc_term': {
				'where_part': 'AND term ~* %(test_name)s',
				'placeholder': 'test_name'
			},
			'ctxt_substance': {
				'where_part': 'AND description ~* %(substance)s',
				'placeholder': 'substance'
			}
		}

		mp = gmMatchProvider.cMatchProvider_SQL2(queries = query, context = ctxt)
		mp.setThresholds(1, 2, 4)
		#mp.print_queries = True
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.matcher = mp
		self.SetToolTip(_('Select the desired unit for the amount or measurement.'))
		self.selection_only = False
		self.phrase_separators = '[;|]+'

#================================================================

#================================================================
class cTestResultIndicatorPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		query = """
select distinct abnormality_indicator,
	abnormality_indicator, abnormality_indicator
from clin.v_test_results
where
	abnormality_indicator %(fragment_condition)s
order by abnormality_indicator
limit 25"""

		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(1, 1, 2)
		mp.ignored_chars = "[.'\\\[\]#$%_]+" + '"'
		mp.word_separators = '[ \t&:]+'
		gmPhraseWheel.cPhraseWheel.__init__ (
			self,
			*args,
			**kwargs
		)
		self.matcher = mp
		self.SetToolTip(_('Select an indicator for the level of abnormality.'))
		self.selection_only = False

#================================================================
# measurement org widgets / functions
#----------------------------------------------------------------
def edit_measurement_org(parent=None, org=None):
	ea = cMeasurementOrgEAPnl(parent, -1)
	ea.data = org
	ea.mode = gmTools.coalesce(org, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent, -1, edit_area = ea)
	dlg.SetTitle(gmTools.coalesce(org, _('Adding new diagnostic org'), _('Editing diagnostic org')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.DestroyLater()
		return True
	dlg.DestroyLater()
	return False
#----------------------------------------------------------------
def manage_measurement_orgs(parent=None, msg=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#------------------------------------------------------------
	def edit(org=None):
		return edit_measurement_org(parent = parent, org = org)
	#------------------------------------------------------------
	def refresh(lctrl):
		orgs = gmPathLab.get_test_orgs()
		lctrl.set_string_items ([
			(o['unit'], o['organization'], gmTools.coalesce(o['test_org_contact'], ''), gmTools.coalesce(o['comment'], ''), o['pk_test_org'])
			for o in orgs
		])
		lctrl.set_data(orgs)
	#------------------------------------------------------------
	def delete(test_org):
		gmPathLab.delete_test_org(test_org = test_org['pk_test_org'])
		return True
	#------------------------------------------------------------
	if msg is None:
		msg = _('\nThese are the diagnostic orgs (path labs etc) currently defined in GNUmed.\n\n')

	return gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = msg,
		caption = _('Showing diagnostic orgs.'),
		columns = [_('Name'), _('Organization'), _('Contact'), _('Comment'), '#'],
		single_selection = True,
		refresh_callback = refresh,
		edit_callback = edit,
		new_callback = edit,
		delete_callback = delete
	)

#----------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgMeasurementOrgEAPnl

class cMeasurementOrgEAPnl(wxgMeasurementOrgEAPnl.wxgMeasurementOrgEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['org']
			del kwargs['org']
		except KeyError:
			data = None

		wxgMeasurementOrgEAPnl.wxgMeasurementOrgEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

		#self.__init_ui()
	#----------------------------------------------------------------
#	def __init_ui(self):
#		# adjust phrasewheels etc
	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):
		has_errors = False
		if self._PRW_org_unit.GetData() is None:
			if self._PRW_org_unit.GetValue().strip() == '':
				has_errors = True
				self._PRW_org_unit.display_as_valid(valid = False)
			else:
				self._PRW_org_unit.display_as_valid(valid = True)
		else:
			self._PRW_org_unit.display_as_valid(valid = True)

		return (not has_errors)
	#----------------------------------------------------------------
	def _save_as_new(self):
		data = gmPathLab.create_test_org (
			name = self._PRW_org_unit.GetValue().strip(),
			comment = self._TCTRL_comment.GetValue().strip(),
			pk_org_unit = self._PRW_org_unit.GetData()
		)
		data['test_org_contact'] = self._TCTRL_contact.GetValue().strip()
		data.save()
		self.data = data
		return True
	#----------------------------------------------------------------
	def _save_as_update(self):
		# get or create the org unit
		name = self._PRW_org_unit.GetValue().strip()
		org = gmOrganization.org_exists(organization = name)
		if org is None:
			org = gmOrganization.create_org (
				organization = name,
				category = 'Laboratory'
			)
		org_unit = gmOrganization.create_org_unit (
			pk_organization = org['pk_org'],
			unit = name
		)
		# update test_org fields
		self.data['pk_org_unit'] = org_unit['pk_org_unit']
		self.data['test_org_contact'] = self._TCTRL_contact.GetValue().strip()
		self.data['comment'] = self._TCTRL_comment.GetValue().strip()
		self.data.save()
		return True
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._PRW_org_unit.SetText(value = '', data = None)
		self._TCTRL_contact.SetValue('')
		self._TCTRL_comment.SetValue('')
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._PRW_org_unit.SetText(value = self.data['unit'], data = self.data['pk_org_unit'])
		self._TCTRL_contact.SetValue(gmTools.coalesce(self.data['test_org_contact'], ''))
		self._TCTRL_comment.SetValue(gmTools.coalesce(self.data['comment'], ''))
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()
	#----------------------------------------------------------------
	def _on_manage_orgs_button_pressed(self, event):
		gmOrganizationWidgets.manage_orgs(parent = self)

#----------------------------------------------------------------
class cMeasurementOrgPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		query = """
SELECT DISTINCT ON (list_label)
	pk_test_org AS data,
	unit || ' (' || organization || ')' AS field_label,
	unit || ' @ ' || organization AS list_label
FROM clin.v_test_orgs
WHERE
	unit %(fragment_condition)s
		OR
	organization %(fragment_condition)s
ORDER BY list_label
LIMIT 50"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(1, 2, 4)
		#mp.word_separators = '[ \t:@]+'
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.matcher = mp
		self.SetToolTip(_('The name of the path lab/diagnostic organisation.'))
		self.selection_only = False
	#------------------------------------------------------------
	def _create_data(self, link_obj=None):
		if self.GetData() is not None:
			_log.debug('data already set, not creating')
			return

		if self.GetValue().strip() == '':
			_log.debug('cannot create new lab, missing name')
			return

		lab = gmPathLab.create_test_org(name = self.GetValue().strip())
		self.SetText(value = lab['unit'], data = lab['pk_test_org'])
		return

	#------------------------------------------------------------
	def _data2instance(self, link_obj=None):
		return gmPathLab.cTestOrg(aPK_obj = self.GetData())

#================================================================
# Meta test type widgets
#----------------------------------------------------------------
def edit_meta_test_type(parent=None, meta_test_type=None):
	ea = cMetaTestTypeEAPnl(parent, -1)
	ea.data = meta_test_type
	ea.mode = gmTools.coalesce(meta_test_type, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2 (
		parent = parent,
		id = -1,
		edit_area = ea,
		single_entry = gmTools.bool2subst((meta_test_type is None), False, True)
	)
	dlg.SetTitle(gmTools.coalesce(meta_test_type, _('Adding new meta test type'), _('Editing meta test type')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.DestroyLater()
		return True
	dlg.DestroyLater()
	return False

#----------------------------------------------------------------
def manage_meta_test_types(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#------------------------------------------------------------
	def edit(meta_test_type=None):
		return edit_meta_test_type(parent = parent, meta_test_type = meta_test_type)
	#------------------------------------------------------------
	def delete(meta_test_type):
		gmPathLab.delete_meta_type(meta_type = meta_test_type['pk'])
		return True
	#----------------------------------------
	def get_tooltip(data):
		if data is None:
			return None
		return data.format(with_tests = True)
	#------------------------------------------------------------
	def refresh(lctrl):
		mtts = gmPathLab.get_meta_test_types()
		items = [ [
			m['abbrev'],
			m['name'],
			gmTools.coalesce(m['loinc'], ''),
			gmTools.coalesce(m['comment'], ''),
			m['pk']
		] for m in mtts ]
		lctrl.set_string_items(items)
		lctrl.set_data(mtts)
	#----------------------------------------

	msg = _(
		'\n'
		'These are the meta test types currently defined in GNUmed.\n'
		'\n'
		'Meta test types allow you to aggregate several actual test types used\n'
		'by pathology labs into one logical type.\n'
		'\n'
		'This is useful for grouping together results of tests which come under\n'
		'different names but really are the same thing. This often happens when\n'
		'you switch labs or the lab starts using another test method.\n'
	)

	gmListWidgets.get_choices_from_list (
		parent = parent,
		msg = msg,
		caption = _('Showing meta test types.'),
		columns = [_('Abbrev'), _('Name'), _('LOINC'), _('Comment'), '#'],
		single_selection = True,
		list_tooltip_callback = get_tooltip,
		edit_callback = edit,
		new_callback = edit,
		delete_callback = delete,
		refresh_callback = refresh
	)

#----------------------------------------------------------------
class cMetaTestTypePRW(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		query = """
SELECT DISTINCT ON (field_label)
	c_mtt.pk
		AS data,
	c_mtt.abbrev || ': ' || name
		AS field_label,
	c_mtt.abbrev || ': ' || name
		||	coalesce (
				' (' || c_mtt.comment || ')',
				''
			)
		||	coalesce (
				', LOINC: ' || c_mtt.loinc,
				''
			)
	AS list_label
FROM
	clin.meta_test_type c_mtt
WHERE
	abbrev %(fragment_condition)s
		OR
	name %(fragment_condition)s
		OR
	loinc %(fragment_condition)s
ORDER BY field_label
LIMIT 50"""

		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(1, 2, 4)
		mp.word_separators = '[ \t:@]+'
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.matcher = mp
		self.SetToolTip(_('Select the meta test type.'))
		self.selection_only = True
	#------------------------------------------------------------
	def _data2instance(self, link_obj=None):
		if self.GetData() is None:
			return None

		return gmPathLab.cMetaTestType(aPK_obj = self.GetData())

#----------------------------------------------------------------
from Gnumed.wxGladeWidgets import wxgMetaTestTypeEAPnl

class cMetaTestTypeEAPnl(wxgMetaTestTypeEAPnl.wxgMetaTestTypeEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['meta_test_type']
			del kwargs['meta_test_type']
		except KeyError:
			data = None

		wxgMetaTestTypeEAPnl.wxgMetaTestTypeEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		# Code using this mixin should set mode and data
		# after instantiating the class:
		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

		self.__init_ui()
	#----------------------------------------------------------------
	def __init_ui(self):
		# loinc
		mp = gmLOINC.cLOINCMatchProvider()
		mp.setThresholds(1, 2, 4)
		#mp.print_queries = True
		#mp.word_separators = '[ \t:@]+'
		self._PRW_loinc.matcher = mp
		self._PRW_loinc.selection_only = False
		self._PRW_loinc.add_callback_on_lose_focus(callback = self._on_loinc_lost_focus)

	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):

		validity = True

		if self._PRW_abbreviation.GetValue().strip() == '':
			validity = False
			self._PRW_abbreviation.display_as_valid(False)
			self.StatusText = _('Missing abbreviation for meta test type.')
			self._PRW_abbreviation.SetFocus()
		else:
			self._PRW_abbreviation.display_as_valid(True)

		if self._PRW_name.GetValue().strip() == '':
			validity = False
			self._PRW_name.display_as_valid(False)
			self.StatusText = _('Missing name for meta test type.')
			self._PRW_name.SetFocus()
		else:
			self._PRW_name.display_as_valid(True)

		return validity
	#----------------------------------------------------------------
	def _save_as_new(self):

		# save the data as a new instance
		data = gmPathLab.create_meta_type (
			name = self._PRW_name.GetValue().strip(),
			abbreviation = self._PRW_abbreviation.GetValue().strip(),
			return_existing = False
		)
		if data is None:
			self.StatusText = _('This meta test type already exists.')
			return False
		data['loinc'] = self._PRW_loinc.GetData()
		data['comment'] = self._TCTRL_comment.GetValue().strip()
		data.save()
		self.data = data
		return True
	#----------------------------------------------------------------
	def _save_as_update(self):
		self.data['name'] = self._PRW_name.GetValue().strip()
		self.data['abbrev'] = self._PRW_abbreviation.GetValue().strip()
		self.data['loinc'] = self._PRW_loinc.GetData()
		self.data['comment'] = self._TCTRL_comment.GetValue().strip()
		self.data.save()
		return True
	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._PRW_name.SetText('', None)
		self._PRW_abbreviation.SetText('', None)
		self._PRW_loinc.SetText('', None)
		self._TCTRL_loinc_info.SetValue('')
		self._TCTRL_comment.SetValue('')
		self._LBL_member_detail.SetLabel('')

		self._PRW_name.SetFocus()
	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()
	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._PRW_name.SetText(self.data['name'], self.data['pk'])
		self._PRW_abbreviation.SetText(self.data['abbrev'], self.data['abbrev'])
		self._PRW_loinc.SetText(gmTools.coalesce(self.data['loinc'], ''), self.data['loinc'])
		self.__refresh_loinc_info()
		self._TCTRL_comment.SetValue(gmTools.coalesce(self.data['comment'], ''))
		self.__refresh_members()

		self._PRW_name.SetFocus()
	#----------------------------------------------------------------
	# event handlers
	#----------------------------------------------------------------
	def _on_loinc_lost_focus(self):
		self.__refresh_loinc_info()
	#----------------------------------------------------------------
	# internal helpers
	#----------------------------------------------------------------
	def __refresh_loinc_info(self):
		loinc = self._PRW_loinc.GetData()

		if loinc is None:
			self._TCTRL_loinc_info.SetValue('')
			return

		info = gmLOINC.loinc2term(loinc = loinc)
		if len(info) == 0:
			self._TCTRL_loinc_info.SetValue('')
			return

		self._TCTRL_loinc_info.SetValue(info[0])
	#----------------------------------------------------------------
	def __refresh_members(self):
		if self.data is None:
			self._LBL_member_detail.SetLabel('')
			return

		types = self.data.included_test_types
		if len(types) == 0:
			self._LBL_member_detail.SetLabel('')
			return

		lines = []
		for tt in types:
			lines.append('%s (%s%s) [#%s] @ %s' % (
				tt['name'],
				tt['abbrev'],
				gmTools.coalesce(tt['loinc'], '', ', LOINC: %s'),
				tt['pk_test_type'],
				tt['name_org']
			))
		self._LBL_member_detail.SetLabel('\n'.join(lines))

#================================================================
# test panel handling
#================================================================
def edit_test_panel(parent=None, test_panel=None):
	ea = cTestPanelEAPnl(parent, -1)
	ea.data = test_panel
	ea.mode = gmTools.coalesce(test_panel, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2 (
		parent = parent,
		id = -1,
		edit_area = ea,
		single_entry = gmTools.bool2subst((test_panel is None), False, True)
	)
	dlg.SetTitle(gmTools.coalesce(test_panel, _('Adding new test panel'), _('Editing test panel')))
	if dlg.ShowModal() == wx.ID_OK:
		dlg.DestroyLater()
		return True
	dlg.DestroyLater()
	return False

#----------------------------------------------------------------
def manage_test_panels(parent=None):

	if parent is None:
		parent = wx.GetApp().GetTopWindow()

	#------------------------------------------------------------
	def edit(test_panel=None):
		return edit_test_panel(parent = parent, test_panel = test_panel)
	#------------------------------------------------------------
	def delete(test_panel):
		gmPathLab.delete_test_panel(pk = test_panel['pk_test_panel'])
		return True
	#------------------------------------------------------------
	def get_tooltip(test_panel):
		return test_panel.format()
	#------------------------------------------------------------
	def refresh(lctrl):
		panels = gmPathLab.get_test_panels(order_by = 'description')
		items = [ [
			p['description'],
			gmTools.coalesce(p['comment'], ''),
			p['pk_test_panel']
		] for p in panels ]
		lctrl.set_string_items(items)
		lctrl.set_data(panels)
	#------------------------------------------------------------
	gmListWidgets.get_choices_from_list (
		parent = parent,
		caption = 'GNUmed: ' + _('Test panels list'),
		columns = [ _('Name'), _('Comment'), '#' ],
		single_selection = True,
		refresh_callback = refresh,
		edit_callback = edit,
		new_callback = edit,
		delete_callback = delete,
		list_tooltip_callback = get_tooltip
	)

#----------------------------------------------------------------
class cTestPanelPRW(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
		query = """
SELECT
	pk_test_panel
		AS data,
	description
		AS field_label,
	description
		AS list_label
FROM
	clin.v_test_panels
WHERE
	description %(fragment_condition)s
ORDER BY field_label
LIMIT 30"""
		mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
		mp.setThresholds(1, 2, 4)
		#mp.word_separators = '[ \t:@]+'
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.matcher = mp
		self.SetToolTip(_('Select a test panel.'))
		self.selection_only = True
	#------------------------------------------------------------
	def _data2instance(self, link_obj=None):
		if self.GetData() is None:
			return None
		return gmPathLab.cTestPanel(aPK_obj = self.GetData())
	#------------------------------------------------------------
	def _get_data_tooltip(self):
		if self.GetData() is None:
			return None
		return gmPathLab.cTestPanel(aPK_obj = self.GetData()).format()

#====================================================================
from Gnumed.wxGladeWidgets import wxgTestPanelEAPnl

class cTestPanelEAPnl(wxgTestPanelEAPnl.wxgTestPanelEAPnl, gmEditArea.cGenericEditAreaMixin):

	def __init__(self, *args, **kwargs):

		try:
			data = kwargs['panel']
			del kwargs['panel']
		except KeyError:
			data = None

		wxgTestPanelEAPnl.wxgTestPanelEAPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

		self.__loincs = None

		self.mode = 'new'
		self.data = data
		if data is not None:
			self.mode = 'edit'

		self.__init_ui()

	#----------------------------------------------------------------
	def __init_ui(self):
		self._LCTRL_loincs.set_columns([_('LOINC'), _('Term'), _('Units')])
		self._LCTRL_loincs.set_column_widths(widths = [wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE, wx.LIST_AUTOSIZE])
		#self._LCTRL_loincs.set_resize_column(column = 2)
		self._LCTRL_loincs.delete_callback = self._remove_loincs_from_list
		self.__refresh_loinc_list()

		self._PRW_loinc.final_regex = r'.*'
		self._PRW_loinc.add_callback_on_selection(callback = self._on_loinc_selected)

	#----------------------------------------------------------------
	def __refresh_loinc_list(self):
		self._LCTRL_loincs.remove_items_safely()
		if self.__loincs is None:
			if self.data is None:
				return
			self.__loincs = self.data['loincs']

		items = []
		for loinc in self.__loincs:
			loinc_detail = gmLOINC.loinc2data(loinc = loinc)
			if loinc_detail is None:
				# check for test type with this pseudo loinc
				ttypes = gmPathLab.get_measurement_types(loincs = [loinc])
				if len(ttypes) == 0:
					items.append([loinc, _('LOINC not found'), ''])
				else:
					for tt in ttypes:
						items.append([loinc, _('not a LOINC') + u'; %(name)s @ %(name_org)s [#%(pk_test_type)s]' % tt, ''])
				continue
			items.append ([
				loinc,
				loinc_detail['term'],
				gmTools.coalesce(loinc_detail['example_units'], '', '%s')
			])

		self._LCTRL_loincs.set_string_items(items)
		self._LCTRL_loincs.set_column_widths()

	#----------------------------------------------------------------
	# generic Edit Area mixin API
	#----------------------------------------------------------------
	def _valid_for_save(self):
		validity = True

		if self.__loincs is None:
			if self.data is not None:
				self.__loincs = self.data['loincs']

		if self.__loincs is None:
			# not fatal despite panel being useless
			self.StatusText = _('No LOINC codes selected.')
			self._PRW_loinc.SetFocus()

		if self._TCTRL_description.GetValue().strip() == '':
			validity = False
			self.display_tctrl_as_valid(tctrl = self._TCTRL_description, valid = False)
			self._TCTRL_description.SetFocus()
		else:
			self.display_tctrl_as_valid(tctrl = self._TCTRL_description, valid = True)

		return validity

	#----------------------------------------------------------------
	def _save_as_new(self):
		data = gmPathLab.create_test_panel(description = self._TCTRL_description.GetValue().strip())
		data['comment'] = self._TCTRL_comment.GetValue().strip()
		data.save()
		if self.__loincs is not None:
			data.included_loincs = self.__loincs
		self.data = data
		return True

	#----------------------------------------------------------------
	def _save_as_update(self):
		self.data['description'] = self._TCTRL_description.GetValue().strip()
		self.data['comment'] = self._TCTRL_comment.GetValue().strip()
		self.data.save()
		if self.__loincs is not None:
			self.data.included_loincs = self.__loincs
		return True

	#----------------------------------------------------------------
	def _refresh_as_new(self):
		self._TCTRL_description.SetValue('')
		self._TCTRL_comment.SetValue('')
		self._PRW_loinc.SetText('', None)
		self._LBL_loinc.SetLabel('')
		self.__loincs = None
		self.__refresh_loinc_list()

		self._TCTRL_description.SetFocus()

	#----------------------------------------------------------------
	def _refresh_as_new_from_existing(self):
		self._refresh_as_new()

	#----------------------------------------------------------------
	def _refresh_from_existing(self):
		self._TCTRL_description.SetValue(self.data['description'])
		self._TCTRL_comment.SetValue(gmTools.coalesce(self.data['comment'], ''))
		self._PRW_loinc.SetText('', None)
		self._LBL_loinc.SetLabel('')
		self.__loincs = self.data['loincs']
		self.__refresh_loinc_list()

		self._PRW_loinc.SetFocus()

	#----------------------------------------------------------------
	# event handlers
	#----------------------------------------------------------------
	def _on_loinc_selected(self, loinc):
		loinc = self._PRW_loinc.GetData()
		if loinc is None:
			self._LBL_loinc.SetLabel('')
			return
		loinc_detail = gmLOINC.loinc2data(loinc = loinc)
		if loinc_detail is None:
			loinc_str = _('no LOINC details found')
		else:
			loinc_str = '%s: %s%s' % (
				loinc,
				loinc_detail['term'],
				gmTools.coalesce(loinc_detail['example_units'], '', ' (%s)')
			)
		self._LBL_loinc.SetLabel(loinc_str)

	#----------------------------------------------------------------
	def _on_add_loinc_button_pressed(self, event):
		event.Skip()

		loinc = self._PRW_loinc.GetData()
		if loinc is None:
			loinc = self._PRW_loinc.GetValue().strip()
		if loinc.strip() == '':
			return

		if self.__loincs is None:
			self.__loincs = [loinc]
		else:
			if loinc in self.__loincs:
				return
			self.__loincs.append(loinc)

		self.__refresh_loinc_list()
		self._PRW_loinc.SetText('', None)
		self._LBL_loinc.SetLabel('')

		self._PRW_loinc.SetFocus()

	#----------------------------------------------------------------
	def _on_remove_loinc_button_pressed(self, event):
		event.Skip()
		self._remove_loincs_from_list()

	#----------------------------------------------------------------
	def _remove_loincs_from_list(self):
		loincs2remove = self._LCTRL_loincs.selected_item_data
		if loincs2remove is None:
			return
		for loinc in loincs2remove:
			try:
				while True:
					self.__loincs.remove(loinc[0])
			except ValueError:
				pass
		self.__refresh_loinc_list()

#================================================================
# main
#----------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.wxpython import gmPatSearchWidgets
	from Gnumed.wxpython import gmGuiTest

	gmDateTime.init()

	#------------------------------------------------------------
	#def test_grid():
		#pat = gmPersonSearch.ask_for_patient()
		#app = wx.PyWidgetTester(size = (500, 300))
		#lab_grid = cMeasurementsGrid(app.frame, -1)
		#lab_grid.patient = pat
		#app.frame.Show()
		#app.MainLoop()
	#------------------------------------------------------------
	def test_test_ea_pnl():
		pat = gmPersonSearch.ask_for_patient()
		gmPatSearchWidgets.set_active_patient(patient=pat)
		#app = wx.PyWidgetTester(size = (500, 300))
		#cMeasurementEditAreaPnl(app.frame, -1)
		#app.frame.Show()
		#app.MainLoop()

	#------------------------------------------------------------
	def test_print_results():
		print_measurements()

	#------------------------------------------------------------
#	def test_primary_care_vitals_pnl():
#		app = wx.PyWidgetTester(size = (500, 300))
#		pnl = wxgPrimaryCareVitalsInputPnl.wxgPrimaryCareVitalsInputPnl(app.frame, -1)
#		app.frame.Show()
#		app.MainLoop()
	#------------------------------------------------------------
	#pat = gmPerson.cPerson(12)
	#gmGuiTest.test_widget(cCurrentSubstancesGrid, patient = 12)

	main_frame = gmGuiTest.setup_widget_test_env(patient = 12)
	gmStaff.set_current_provider_to_logged_on_user()

	#test_grid()
	#test_test_ea_pnl()
	#test_primary_care_vitals_pnl()

	test_print_results()

#================================================================
