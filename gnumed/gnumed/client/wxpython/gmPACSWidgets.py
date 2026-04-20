# -*- coding: utf-8 -*-
#============================================================

"""GNUmed PACS related widgets."""

__license__ = "GPL v2 or later"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

#============================================================
import os.path
import os
import sys
import re as regex
import logging
import datetime as pydt


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
else:
	try: _
	except NameError:
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain()
from Gnumed.pycommon import gmCfgINI
from Gnumed.pycommon import gmMimeLib
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmNetworkTools
from Gnumed.pycommon import gmConnectionPool

from Gnumed.business import gmPerson
from Gnumed.business import gmStaff
from Gnumed.business import gmPraxis
from Gnumed.business import gmDICOM
from Gnumed.business import gmProviderInbox

from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmRegetMixin


_log = logging.getLogger('gm.ui')

#============================================================
from Gnumed.wxGladeWidgets.wxgPACSPluginPnl import wxgPACSPluginPnl

class cPACSPluginPnl(wxgPACSPluginPnl, gmRegetMixin.cRegetOnPaintMixin):

	def __init__(self, *args, **kwargs):
		wxgPACSPluginPnl.__init__(self, *args, **kwargs)
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)
		self.__pacs = None
		self.__patient = gmPerson.gmCurrentPatient()
		self.__orthanc_patient = None
		self.__image_data = None
		self.__init_ui()
		self.__register_interests()
		self.__connect()

	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __init_ui(self):
		pool = gmConnectionPool.gmConnectionPool()
		try:
			host = pool.get_raw_connection().info.dsn_parameters['host'].split(',')[0]
		except KeyError:
			host = ''
		self._TCTRL_host.Value = host
		self._TCTRL_port.Value = '8042'

		self._LCTRL_studies.set_columns(columns = [_('Date'), _('Description'), _('Organization'), _('Authority')])
		self._LCTRL_studies.select_callback = self._on_studies_list_item_selected
		self._LCTRL_studies.deselect_callback = self._on_studies_list_item_deselected

		self._LCTRL_series.set_columns(columns = [_('Time'), _('Method'), _('Body part'), _('Description')])
		self._LCTRL_series.select_callback = self._on_series_list_item_selected
		self._LCTRL_series.deselect_callback = self._on_series_list_item_deselected

		self._LCTRL_details.set_columns(columns = [_('DICOM field'), _('Value')])
		self._LCTRL_details.set_column_widths()

		self._BMP_preview.SetBitmap(wx.Bitmap.FromRGBA(50,50, red=0, green=0, blue=0, alpha = wx.ALPHA_TRANSPARENT))

		# pre-make thumbnail context menu
		self.__thumbnail_menu = wx.Menu()
		item = self.__thumbnail_menu.Append(-1, _('Show in DICOM viewer'))
		self.Bind(wx.EVT_MENU, self._on_show_image_as_dcm, item)
		item = self.__thumbnail_menu.Append(-1, _('Show in image viewer'))
		self.Bind(wx.EVT_MENU, self._on_show_image_as_png, item)
		self.__thumbnail_menu.AppendSeparator()
		item = self.__thumbnail_menu.Append(-1, _('Copy to export area'))
		self.Bind(wx.EVT_MENU, self._on_copy_image_to_export_area, item)
		item = self.__thumbnail_menu.Append(-1, _('Save as DICOM file (.dcm)'))
		self.Bind(wx.EVT_MENU, self._on_save_image_as_dcm, item)
		item = self.__thumbnail_menu.Append(-1, _('Save as image file (.png)'))
		self.Bind(wx.EVT_MENU, self._on_save_image_as_png, item)

		# pre-make studies context menu
		self.__studies_menu = wx.Menu('Studies:')
		self.__studies_menu.AppendSeparator()
		item = self.__studies_menu.Append(-1, _('Show in DICOM viewer'))
		self.Bind(wx.EVT_MENU, self._on_studies_show_button_pressed, item)
		self.__studies_menu.AppendSeparator()
		# export
		item = self.__studies_menu.Append(-1, _('Selected into export area'))
		self.Bind(wx.EVT_MENU, self._on_copy_selected_studies_to_export_area, item)
		item = self.__studies_menu.Append(-1, _('ZIP of selected into export area'))
		self.Bind(wx.EVT_MENU, self._on_copy_zip_of_selected_studies_to_export_area, item)
		item = self.__studies_menu.Append(-1, _('All into export area'))
		self.Bind(wx.EVT_MENU, self._on_copy_all_studies_to_export_area, item)
		item = self.__studies_menu.Append(-1, _('ZIP of all into export area'))
		self.Bind(wx.EVT_MENU, self._on_copy_zip_of_all_studies_to_export_area, item)
		self.__studies_menu.AppendSeparator()
		# save
		item = self.__studies_menu.Append(-1, _('Save selected'))
		self.Bind(wx.EVT_MENU, self._on_save_selected_studies, item)
		item = self.__studies_menu.Append(-1, _('Save ZIP of selected'))
		self.Bind(wx.EVT_MENU, self._on_save_zip_of_selected_studies, item)
		item = self.__studies_menu.Append(-1, _('Save all'))
		self.Bind(wx.EVT_MENU, self._on_save_all_studies, item)
		item = self.__studies_menu.Append(-1, _('Save ZIP of all'))
		self.Bind(wx.EVT_MENU, self._on_save_zip_of_all_studies, item)
		self.__studies_menu.AppendSeparator()
		# dicomize
		item = self.__studies_menu.Append(-1, _('Add file to study (PDF/image)'))
		self.Bind(wx.EVT_MENU, self._on_add_file_to_study, item)

	#--------------------------------------------------------
	def __set_button_states(self):
		# disable all buttons
		# server
		self._BTN_browse_pacs.Disable()
		self._BTN_upload.Disable()
		self._BTN_modify_orthanc_content.Disable()
		# patient (= all studies of patient)
		self._BTN_browse_patient.Disable()
		self._BTN_verify_patient_data.Disable()
		# study
		self._BTN_browse_study.Disable()
		self._BTN_studies_show.Disable()
		self._BTN_studies_export.Disable()
		# series
		# image
		self._BTN_image_show.Disable()
		self._BTN_image_export.Disable()
		self._BTN_previous_image.Disable()
		self._BTN_next_image.Disable()

		if self.__pacs is None:
			return

		# server buttons
		self._BTN_browse_pacs.Enable()
		self._BTN_upload.Enable()
		self._BTN_modify_orthanc_content.Enable()

		if not self.__patient.connected:
			return

		# patient buttons (= all studies of patient)
		self._BTN_verify_patient_data.Enable()
		if self.__orthanc_patient is not None:
			self._BTN_browse_patient.Enable()

		if len(self._LCTRL_studies.selected_items) == 0:
			return

		# study buttons
		self._BTN_browse_study.Enable()
		self._BTN_studies_show.Enable()
		self._BTN_studies_export.Enable()

		if len(self._LCTRL_series.selected_items) == 0:
			return

		series = self._LCTRL_series.get_selected_item_data(only_one = True)
		if len(series['instances']) == 0:
			return

		# image buttons
		self._BTN_image_show.Enable()
		self._BTN_image_export.Enable()
		if len(series['instances']) > 1:
			self._BTN_previous_image.Enable()
			self._BTN_next_image.Enable()

	#--------------------------------------------------------
	def __reset_patient_data(self):
		self._LBL_patient_identification.SetLabel('')
		self._LCTRL_studies.set_string_items(items = [])
		self._LCTRL_series.set_string_items(items = [])
		self.__refresh_image()
		self.__refresh_details()

	#--------------------------------------------------------
	def __reset_server_identification(self):
		self._LBL_PACS_identification.SetLabel(_('<not connected>'))

	#--------------------------------------------------------
	def __reset_ui_content(self):
		self.__reset_server_identification()
		self.__reset_patient_data()
		self.__set_button_states()

	#-----------------------------------------------------
	def __connect(self):

		self.__pacs = None
		self.__orthanc_patient = None
		self.__set_button_states()
		self.__reset_server_identification()
		host = self._TCTRL_host.Value.strip()
		port = self._TCTRL_port.Value.strip()[:6]
		if port == '':
			self._LBL_PACS_identification.SetLabel(_('Cannot connect without port (try 8042).'))
			return False

		if len(port) < 4:
			return False

		try:
			int(port)
		except ValueError:
			self._LBL_PACS_identification.SetLabel(_('Invalid port (try 8042).'))
			return False

		user = self._TCTRL_user.Value
		if user == '':
			user = None
		self._LBL_PACS_identification.SetLabel(_('Connect to [%s] @ port %s as "%s".') % (host, port, user))
		password = self._TCTRL_password.Value
		if password == '':
			password = None
		pacs = gmDICOM.cOrthancServer()
		if not pacs.connect(host = host, port = port, user = user, password = password):		#, expected_aet = 'another AET'
			self._LBL_PACS_identification.SetLabel(_('Cannot connect to PACS.'))
			_log.error('error connecting to server: %s', pacs.connect_error)
			return False

		ident = pacs.server_identification
		label = _('PACS (Orthanc): "%s" (AET "%s") [%s]') % (
			ident['Name'],
			ident['DicomAet'],
			'SSL' if pacs.using_ssl else _('no SSL')
		)
		self._LBL_PACS_identification.SetLabel(label)
		lines = [
			_('SSL: in use') if pacs.using_ssl else _('SSL: NOT in use'),
			'',
			_('Server details:')
		]
		lines.extend([ ' %s: %s' % (key, val) for key, val in ident.items() ])
		self._LBL_PACS_identification.SetToolTip('\n'.join(lines))
		self.__pacs = pacs
		self.__set_button_states()
		self.__refresh_patient_data()
		return True

	#--------------------------------------------------------
	def __refresh_patient_data(self):

		self.__orthanc_patient = None

		if not self.__patient.connected:
			self.__reset_patient_data()
			self.__set_button_states()
			return True

		if not self.__pacs:
			return False

		tt_lines = [_('Known PACS IDs:')]
		for pacs_id in self.__patient.suggest_external_ids(target = 'PACS'):
			tt_lines.append(' ' + _('generic: %s') % pacs_id)
		for pacs_id in self.__patient.get_external_ids(id_type = 'PACS', issuer = self.__pacs.as_external_id_issuer):
			tt_lines.append(' ' + _('stored: "%(value)s" @ [%(issuer)s]') % pacs_id)
		tt_lines.append('')
		tt_lines.append(_('Patients found in PACS:'))

		info_lines = []
		# try to find patient
		matching_pats = self.__pacs.get_matching_patients(person = self.__patient)
		if len(matching_pats) == 0:
			info_lines.append(_('PACS: no patients with matching IDs found'))
		no_of_studies = 0
		for pat in matching_pats:
			info_lines.append('"%s" %s "%s (%s) %s"' % (
				pat['MainDicomTags']['PatientID'],
				gmTools.u_arrow2right,
				gmTools.coalesce(pat['MainDicomTags']['PatientName'], '?'),
				gmTools.coalesce(pat['MainDicomTags']['PatientSex'], '?'),
				gmTools.coalesce(pat['MainDicomTags']['PatientBirthDate'], '?')
			))
			no_of_studies += len(pat['Studies'])
			tt_lines.append('%s [#%s]' % (
				gmTools.format_dict_like (
					pat['MainDicomTags'],
					relevant_keys = ['PatientName', 'PatientSex', 'PatientBirthDate', 'PatientID'],
					template = ' %(PatientID)s = %(PatientName)s (%(PatientSex)s) %(PatientBirthDate)s',
					missing_key_template = '?'
				),
				pat['ID']
			))
		if len(matching_pats) > 1:
			info_lines.append(_('PACS: more than one patient with matching IDs found, carefully check studies'))
		self._LBL_patient_identification.SetLabel('\n'.join(info_lines))
		tt_lines.append('')
		tt_lines.append(_('Studies found: %s') % no_of_studies)
		self._LBL_patient_identification.SetToolTip('\n'.join(tt_lines))

		# get studies
		study_list_items = []
		study_list_data = []
		if len(matching_pats) > 0:
			# we don't at this point really expect more than one patient matching
			self.__orthanc_patient = matching_pats[0]
			for pat in self.__pacs.get_studies_list_by_orthanc_patient_list(orthanc_patients = matching_pats):
				for study in pat['studies']:
					docs = []
					if study['referring_doc'] is not None:
						docs.append(study['referring_doc'])
					if study['requesting_doc'] is None:
						if study['requesting_org'] is not None:
							docs.append(study['requesting_org'])
					else:
						if study['requesting_doc'] in docs:
							if study['requesting_org'] is not None:
								docs.append(study['requesting_org'])
						else:
							docs.append (
								'%s%s' % (
									study['requesting_doc'],
									gmTools.coalesce(study['requesting_org'], '', '@%s')
								)
							)
					if study['performing_doc'] is not None:
						if study['performing_doc'] not in docs:
							docs.append(study['performing_doc'])
					if study['operator_name'] is not None:
						if study['operator_name'] not in docs:
							docs.append(study['operator_name'])
					if study['radiographer_code'] is not None:
						if study['radiographer_code'] not in docs:
							docs.append(study['radiographer_code'])
					org_name = u'@'.join ([
						o for o in [study['radiology_dept'], study['radiology_org']]
						if o is not None
					])
					org = '%s%s%s' % (
						org_name,
						gmTools.coalesce(study['station_name'], '', ' [%s]'),
						gmTools.coalesce(study['radiology_org_addr'], '', ' (%s)').replace('\r\n', ' [CR] ')
					)
					if study['date'] is None:
						study_date = '?'
					else:
						study_date = '%s-%s-%s' % (
							study['date'][:4],
							study['date'][4:6],
							study['date'][6:8]
						)
					study_list_items.append ( [
						study_date,
						_('%s series%s') % (
							len(study['series']),
							gmTools.coalesce(study['description'], '', ': %s')
						),
						org.strip(),
						gmTools.u_arrow2right.join(docs)
					] )
					study_list_data.append(study)

		self._LCTRL_studies.set_string_items(items = study_list_items)
		self._LCTRL_studies.set_data(data = study_list_data)
		self._LCTRL_studies.SortListItems(0, 0)
		self._LCTRL_studies.set_column_widths()

		self.__refresh_image()
		self.__refresh_details()
		self.__set_button_states()

		return True

	#--------------------------------------------------------
	def __refresh_details(self):

		self._LCTRL_details.remove_items_safely()
		if self.__pacs is None:
			return

		# study available ?
		study_data = self._LCTRL_studies.get_selected_item_data(only_one = True)
		if study_data is None:
			return
		items = []
		items = [ [key, study_data['all_tags'][key]] for key in study_data['all_tags'] if ('%s' % study_data['all_tags'][key]).strip() != '' ]

		# series available ?
		series = self._LCTRL_series.get_selected_item_data(only_one = True)
		if series is None:
			self._LCTRL_details.set_string_items(items = items)
			self._LCTRL_details.set_column_widths()
			return
		items.append ([
			' %s ' % (gmTools.u_box_horiz_single * 5),
			'%s %s %s' % (
				gmTools.u_box_horiz_single * 3,
				_('Series'),
				gmTools.u_box_horiz_single * 10
			)
		])
		items.extend([ [key, series['all_tags'][key]] for key in series['all_tags'] if ('%s' % series['all_tags'][key]).strip() != '' ])

		# image available ?
		if self.__image_data is None:
			self._LCTRL_details.set_string_items(items = items)
			self._LCTRL_details.set_column_widths()
			return
		items.append ([
			' %s ' % (gmTools.u_box_horiz_single * 5),
			'%s %s %s' % (
				gmTools.u_box_horiz_single * 3,
				_('Image'),
				gmTools.u_box_horiz_single * 10
			)
		])
		tags = self.__pacs.get_instance_dicom_tags(instance_id = self.__image_data['uuid'])
		if tags is False:
			items.extend(['image', '<tags not found in PACS>'])
		else:
			items.extend([ [key, tags[key]] for key in tags if ('%s' % tags[key]).strip() != '' ])

		self._LCTRL_details.set_string_items(items = items)
		self._LCTRL_details.set_column_widths()

	#--------------------------------------------------------
	def __refresh_image(self, idx=None):

		self.__image_data = None
		self._SZR_image_buttons.StaticBox.SetLabel(_('Image'))
		self._BMP_preview.SetBitmap(wx.Bitmap.FromRGBA(50,50, red=0, green=0, blue=0, alpha = wx.ALPHA_TRANSPARENT))

		if idx is None:
			self._BMP_preview.ContainingSizer.Layout()
			return

		if self.__pacs is None:
			self._BMP_preview.ContainingSizer.Layout()
			return

		series = self._LCTRL_series.get_selected_item_data(only_one = True)
		if series is None:
			self._BMP_preview.ContainingSizer.Layout()
			return

		if idx > len(series['instances']) - 1:
			raise ValueError('trying to go beyond instances in series: %s of %s', idx, len(series['instances']))

		# get image
		uuid = series['instances'][idx]
		img_file = self.__pacs.get_instance_preview(instance_id = uuid)
		if img_file is None:
			self._BMP_preview.ContainingSizer.Layout()
			return

		# scale
		wx_bmp = gmGuiHelpers.file2scaled_image(filename = img_file, height = 100)
		# show
		if wx_bmp is None:
			_log.error('cannot load DICOM instance from PACS: %s', uuid)
		else:
			self.__image_data = {'idx': idx, 'uuid': uuid}
			self._BMP_preview.SetBitmap(wx_bmp)
			self._SZR_image_buttons.StaticBox.SetLabel(_('Image %s/%s') % (idx+1, len(series['instances'])))

		if idx == 0:
			self._BTN_previous_image.Disable()
		else:
			self._BTN_previous_image.Enable()
		if idx == len(series['instances']) - 1:
			self._BTN_next_image.Disable()
		else:
			self._BTN_next_image.Enable()

		self._BMP_preview.ContainingSizer.Layout()

	#--------------------------------------------------------
	def __show_image(self, as_dcm=False, as_png=False):
		if self.__image_data is None:
			return False

		uuid = self.__image_data['uuid']
		img_file = None
		if as_dcm:
			img_file = self.__pacs.get_instance(instance_id = uuid)
		if as_png:
			img_file = self.__pacs.get_instance_preview(instance_id = uuid)
		if img_file is not None:
			(success, msg) = gmMimeLib.call_viewer_on_file(img_file)
			if not success:
				gmGuiHelpers.gm_show_warning (
					warning = _('Cannot show image:\n%s') % msg,
					title = _('Previewing DICOM image')
				)
			return success

		# try DCM
		img_file = self.__pacs.get_instance(instance_id = uuid)
		(success, msg) = gmMimeLib.call_viewer_on_file(img_file)
		if success:
			return True

		# try PNG
		img_file = self.__pacs.get_instance_preview(instance_id = uuid)
		if img_file is not None:
			(success, msg) = gmMimeLib.call_viewer_on_file(img_file)
			if success:
				return True

		gmGuiHelpers.gm_show_warning (
			warning = _('Cannot show in DICOM or image viewer:\n%s') % msg,
			title = _('Previewing DICOM image')
		)

	#--------------------------------------------------------
	def __save_image(self, as_dcm=False, as_png=False, nice_filename=False):
		if self.__image_data is None:
			return False, None

		fnames = {}
		uuid = self.__image_data['uuid']
		if as_dcm:
			if nice_filename:
				fname = gmTools.get_unique_filename (
					prefix = '%s-orthanc_%s--' % (self.__patient.subdir_name, uuid),
					suffix = '.dcm',
					tmp_dir = gmTools.gmPaths().user_work_dir
				)
			else:
				fname = None
			img_fname = self.__pacs.get_instance(filename = fname, instance_id = uuid)
			if img_fname is None:
				gmGuiHelpers.gm_show_warning (
					warning = _('Cannot save image as DICOM file.'),
					title = _('Saving DICOM image')
				)
				return False, fnames

			fnames['dcm'] = img_fname
			gmDispatcher.send(signal = 'statustext', msg = _('Successfully saved as [%s].') % img_fname)

		if as_png:
			if nice_filename:
				fname = gmTools.get_unique_filename (
					prefix = '%s-orthanc_%s--' % (self.__patient.subdir_name, uuid),
					suffix = '.png',
					tmp_dir = gmTools.gmPaths().user_work_dir
				)
			else:
				fname = None
			img_fname = self.__pacs.get_instance_preview(filename = fname, instance_id = uuid)
			if img_fname is None:
				gmGuiHelpers.gm_show_warning (
					warning = _('Cannot save image as PNG file.'),
					title = _('Saving DICOM image')
				)
				return False, fnames
			fnames['png'] = img_fname
			gmDispatcher.send(signal = 'statustext', msg = _('Successfully saved as [%s].') % img_fname)

		return True, fnames

	#--------------------------------------------------------
	def __copy_image_to_export_area(self):
		if self.__image_data is None:
			return False

		success, fnames = self.__save_image(as_dcm = True, as_png = True)
		if not success:
			return False

		wx.BeginBusyCursor()
		self.__patient.export_area.add_files (
			filenames = [fnames['png'], fnames['dcm']],
			hint = _('DICOM image of [%s] from Orthanc PACS "%s" (AET "%s")') % (
				self.__orthanc_patient['MainDicomTags']['PatientID'],
				self.__pacs.server_identification['Name'],
				self.__pacs.server_identification['DicomAet']
			)
		)
		wx.EndBusyCursor()

		gmDispatcher.send(signal = 'statustext', msg = _('Successfully stored in export area.'))

	#--------------------------------------------------------
	#--------------------------------------------------------
	def __browse_studies(self):
		if self.__pacs is None:
			return

		study_data = self._LCTRL_studies.get_selected_item_data(only_one = True)
		if len(study_data) == 0:
			return

		gmNetworkTools.open_url_in_browser (
			self.__pacs.get_url_browse_study(study_id = study_data['orthanc_id']),
			new = 2,
			autoraise = True
		)

	#--------------------------------------------------------
	def __show_studies(self):
		if self.__pacs is None:
			return

		study_data = self._LCTRL_studies.get_selected_item_data(only_one = False)
		if len(study_data) == 0:
			return

		wx.BeginBusyCursor()
		target_dir = self.__pacs.get_studies_with_dicomdir(study_ids = [ s['orthanc_id'] for s in study_data ])
		wx.EndBusyCursor()
		if target_dir is False:
			gmGuiHelpers.gm_show_error (
				title = _('Showing DICOM studies'),
				error = _('Unable to show selected studies.')
			)
			return
		DICOMDIR = os.path.join(target_dir, 'DICOMDIR')
		if os.path.isfile(DICOMDIR):
			(success, msg) = gmMimeLib.call_viewer_on_file(DICOMDIR, block = False)
			if success:
				return
		else:
			_log.error('cannot find DICOMDIR in: %s', target_dir)

		gmMimeLib.call_viewer_on_file(target_dir, block = False)

		# FIXME: on failure export as JPG and call dir viewer

	#--------------------------------------------------------
	def __copy_all_studies_to_export_area(self):
		if self.__pacs is None:
			return

		study_data = self._LCTRL_studies.get_item_data()
		if len(study_data) == 0:
			return

		self.__copy_studies_to_export_area(study_data)

	#--------------------------------------------------------
	def __copy_selected_studies_to_export_area(self):
		if self.__pacs is None:
			return

		study_data = self._LCTRL_studies.get_selected_item_data(only_one = False)
		if len(study_data) == 0:
			return

		self.__copy_studies_to_export_area(study_data)

	#--------------------------------------------------------
	def __copy_studies_to_export_area(self, study_data):
		wx.BeginBusyCursor()
		target_dir = gmTools.mk_sandbox_dir (
			prefix = 'dcm-',
			base_dir = os.path.join(gmTools.gmPaths().user_tmp_dir, self.__patient.subdir_name)
		)
		target_dir = self.__pacs.get_studies_with_dicomdir(study_ids = [ s['orthanc_id'] for s in study_data ], target_dir = target_dir)
		if target_dir is False:
			wx.EndBusyCursor()
			gmGuiHelpers.gm_show_error (
				title = _('Copying DICOM studies'),
				error = _('Unable to put studies into export area.')
			)
			return

		comment = _('DICOM studies of [%s] from Orthanc PACS "%s" (AET "%s") [%s/]') % (
			self.__orthanc_patient['MainDicomTags']['PatientID'],
			self.__pacs.server_identification['Name'],
			self.__pacs.server_identification['DicomAet'],
			target_dir
		)
		if self.__patient.export_area.add_path(target_dir, comment):
			wx.EndBusyCursor()
			return

		wx.EndBusyCursor()
		gmGuiHelpers.gm_show_error (
			title = _('Adding DICOM studies to export area'),
			error = _('Cannot add the following path to the export area:\n%s ') % target_dir
		)

	#--------------------------------------------------------
	def __copy_zip_of_all_studies_to_export_area(self):
		if self.__pacs is None:
			return

		study_data = self._LCTRL_studies.get_item_data()
		if len(study_data) == 0:
			return

		self.__copy_zip_of_studies_to_export_area(study_data)

	#--------------------------------------------------------
	def __copy_zip_of_selected_studies_to_export_area(self):
		if self.__pacs is None:
			return

		study_data = self._LCTRL_studies.get_selected_item_data(only_one = False)
		if len(study_data) == 0:
			return

		self.__copy_zip_of_studies_to_export_area(study_data)

	#--------------------------------------------------------
	def __copy_zip_of_studies_to_export_area(self, study_data):
		wx.BeginBusyCursor()
		zip_fname = self.__pacs.get_studies_with_dicomdir (
			study_ids = [ s['orthanc_id'] for s in study_data ],
			create_zip = True
		)
		if zip_fname is False:
			wx.EndBusyCursor()
			gmGuiHelpers.gm_show_error (
				title = _('Adding DICOM studies to export area'),
				error = _('Unable to put ZIP of studies into export area.')
			)
			return

		# check size and confirm if huge
		zip_size = os.path.getsize(zip_fname)
		if zip_size > (300 * gmTools._MB):		# ~ 1/2 CD-ROM
			wx.EndBusyCursor()
			really_export = gmGuiHelpers.gm_show_question (
				title = _('Exporting DICOM studies'),
				question = _('The DICOM studies are %s in compressed size.\n\nReally move into export area ?') % gmTools.size2str(zip_size),
				cancel_button = False
			)
			if not really_export:
				return

		hint = _('DICOM studies of [%s] from Orthanc PACS "%s" (AET "%s")') % (
			self.__orthanc_patient['MainDicomTags']['PatientID'],
			self.__pacs.server_identification['Name'],
			self.__pacs.server_identification['DicomAet']
		)
		if self.__patient.export_area.add_file(filename = zip_fname, hint = hint):
			#gmDispatcher.send(signal = 'statustext', msg = _('Successfully saved as [%s].') % filename)
			wx.EndBusyCursor()
			return

		wx.EndBusyCursor()
		gmGuiHelpers.gm_show_error (
			title = _('Adding DICOM studies to export area'),
			error = _('Cannot add the following archive to the export area:\n%s ') % zip_fname
		)

	#--------------------------------------------------------
	def __save_selected_studies(self):
		if self.__pacs is None:
			return

		study_data = self._LCTRL_studies.get_selected_item_data(only_one = False)
		if len(study_data) == 0:
			return

		self.__save_studies_to_disk(study_data)

	#--------------------------------------------------------
	def __on_save_all_studies(self):
		if self.__pacs is None:
			return

		study_data = self._LCTRL_studies.get_item_data()
		if len(study_data) == 0:
			return

		self.__save_studies_to_disk(study_data)

	#--------------------------------------------------------
	def __save_studies_to_disk(self, study_data):
		default_path = os.path.join(gmTools.gmPaths().user_work_dir, self.__patient.subdir_name)
		gmTools.mkdir(default_path)
		dlg = wx.DirDialog (
			self,
			message = _('Select the directory into which to save the DICOM studies.'),
			defaultPath = default_path
		)
		choice = dlg.ShowModal()
		target_dir = dlg.GetPath()
		dlg.DestroyLater()
		if choice != wx.ID_OK:
			return True

		wx.BeginBusyCursor()
		target_dir = self.__pacs.get_studies_with_dicomdir(study_ids = [ s['orthanc_id'] for s in study_data ], target_dir = target_dir)
		wx.EndBusyCursor()

		if target_dir is False:
			gmGuiHelpers.gm_show_error (
				title = _('Saving DICOM studies'),
				error = _('Unable to save DICOM studies.')
			)
			return
		gmDispatcher.send(signal = 'statustext', msg = _('Successfully saved to [%s].') % target_dir)

	#--------------------------------------------------------
	def __save_zip_of_selected_studies(self):
		if self.__pacs is None:
			return

		study_data = self._LCTRL_studies.get_selected_item_data(only_one = False)
		if len(study_data) == 0:
			return

		self.__save_zip_of_studies_to_disk(study_data)

	#--------------------------------------------------------
	def ___on_save_zip_of_all_studies(self):
		if self.__pacs is None:
			return

		study_data = self._LCTRL_studies.get_item_data()
		if len(study_data) == 0:
			return

		self.__save_zip_of_studies_to_disk(study_data)

	#--------------------------------------------------------
	def __save_zip_of_studies_to_disk(self, study_data):
		default_path = os.path.join(gmTools.gmPaths().user_work_dir, self.__patient.subdir_name)
		gmTools.mkdir(default_path)
		dlg = wx.DirDialog (
			self,
			message = _('Select the directory into which to save the DICOM studies ZIP.'),
			defaultPath = default_path
		)
		choice = dlg.ShowModal()
		target_dir = dlg.GetPath()
		dlg.DestroyLater()
		if choice != wx.ID_OK:
			return True

		wx.BeginBusyCursor()
		filename = self.__pacs.get_studies_with_dicomdir(study_ids = [ s['orthanc_id'] for s in study_data ], target_dir = target_dir, create_zip = True)
		wx.EndBusyCursor()

		if filename is False:
			gmGuiHelpers.gm_show_error (
				title = _('Saving DICOM studies'),
				error = _('Unable to save DICOM studies as ZIP.')
			)
			return

		gmDispatcher.send(signal = 'statustext', msg = _('Successfully saved as [%s].') % filename)

	#--------------------------------------------------------
	def _on_add_file_to_study(self, evt):
		if self.__pacs is None:
			return

		study_data = self._LCTRL_studies.get_selected_item_data(only_one = False)
		if len(study_data) != 1:
			gmGuiHelpers.gm_show_info (
				title = _('Adding file to DICOM study'),
				info = _('For adding a file there must be exactly one (1) DICOM study selected.')
			)
			return

		# select file
		filename = None
		dlg = wx.FileDialog (
			parent = self,
			message = _('Select file (image or PDF) to add to DICOM study'),
			defaultDir = gmTools.gmPaths().user_work_dir,
			wildcard = "%s (*)|*|%s (*.pdf)|*.pdf" % (_('all files'), _('PDF files')),
			style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
		)
		choice = dlg.ShowModal()
		filename = dlg.GetPath()
		dlg.DestroyLater()
		if choice != wx.ID_OK:
			return

		if filename is None:
			return

		_log.debug('dicomize(%s)', filename)
		# export one instance as template
		instance_uuid = study_data[0]['series'][0]['instances'][-1]
		dcm_instance_template_fname = self.__pacs.get_instance(instance_id = instance_uuid)
		# dicomize file via template
		_cfg = gmCfgINI.gmCfgData()
		dcm_fname = gmDICOM.dicomize_file (
			filename = filename,
			dcm_template_file = dcm_instance_template_fname,
			dcm_transfer_series = False,			# create new series
			verbose = _cfg.get(option = 'debug')
			#, content_date =
		)
		if dcm_fname is None:
			gmGuiHelpers.gm_show_error (
				title = _('Adding file to DICOM study'),
				error = _('Cannot turn file\n\n %s\n\n into DICOM file.')
			)
			return

		# upload .dcm
		if self.__pacs.upload_dicom_file(dcm_fname):
			gmDispatcher.send(signal = 'statustext', msg = _('Successfully uploaded [%s] to Orthanc DICOM server.') % dcm_fname)
			self._schedule_data_reget()
			return

		gmGuiHelpers.gm_show_error (
			title = _('Adding file to DICOM study'),
			error = _('Cannot updload DICOM file\n\n %s\n\n into Orthanc PACS.') % dcm_fname
		)

	#--------------------------------------------------------
	#--------------------------------------------------------
	def __browse_patient(self):
		if self.__pacs is None:
			return

		gmNetworkTools.open_url_in_browser (
			self.__pacs.get_url_browse_patient(patient_id = self.__orthanc_patient['ID']),
			new = 2,
			autoraise = True
		)

	#--------------------------------------------------------
	#--------------------------------------------------------
	def __browse_pacs(self):
		if self.__pacs is None:
			return

		gmNetworkTools.open_url_in_browser (
			self.__pacs.url_browse_patients,
			new = 2,
			autoraise = True
		)

	#--------------------------------------------------------
	# reget-on-paint mixin API
	#--------------------------------------------------------
	def _populate_with_data(self):
		if not self.__patient.connected:
			self.__reset_ui_content()
			return True

		if not self.__refresh_patient_data():
			return False

		return True

	#--------------------------------------------------------
	# event handling
	#--------------------------------------------------------
	def __register_interests(self):

		# wxPython signals
		self._BMP_preview.Bind(wx.EVT_LEFT_DCLICK, self._on_preview_image_leftdoubleclicked)
		self._BMP_preview.Bind(wx.EVT_RIGHT_UP, self._on_preview_image_rightclicked)
		self._BTN_browse_study.Bind(wx.EVT_RIGHT_UP, self._on_studies_button_rightclicked)

		# client internal signals
		gmDispatcher.connect(signal = 'pre_patient_unselection', receiver = self._on_pre_patient_unselection)
		gmDispatcher.connect(signal = 'post_patient_selection', receiver = self._on_post_patient_selection)

		# generic database change signal
		gmDispatcher.connect(signal = 'gm_table_mod', receiver = self._on_database_signal)

	#--------------------------------------------------------
	def _on_pre_patient_unselection(self):
		# only empty out here, do NOT access the patient
		# or else we will access the old patient while it
		# may not be valid anymore ...
		self.__reset_patient_data()

	#--------------------------------------------------------
	def _on_post_patient_selection(self):
		self.__connect()
		self._schedule_data_reget()

	#--------------------------------------------------------
	def _on_database_signal(self, **kwds):

		if not self.__patient.connected:
			# probably not needed:
			#self._schedule_data_reget()
			return True

		if kwds['pk_identity'] != self.__patient.ID:
			return True

		if kwds['table'] == 'dem.lnk_identity2ext_id':
			self._schedule_data_reget()
			return True

		return True

	#--------------------------------------------------------
	# events: lists
	#--------------------------------------------------------
	def _on_series_list_item_selected(self, event):

		event.Skip()
		if self.__pacs is None:
			return

		study_data = self._LCTRL_studies.get_selected_item_data(only_one = True)
		if study_data is None:
			return

		series = self._LCTRL_series.get_selected_item_data(only_one = True)
		if series is None:
			self.__set_button_states()
			return

		if len(series['instances']) == 0:
			self.__refresh_image()
			self.__refresh_details()
			self.__set_button_states()
			return

		# set first image
		self.__refresh_image(0)
		self.__refresh_details()
		self.__set_button_states()
		self._BTN_previous_image.Disable()

	#--------------------------------------------------------
	def _on_series_list_item_deselected(self, event):
		event.Skip()

		self.__refresh_image()
		self.__refresh_details()
		self.__set_button_states()

	#--------------------------------------------------------
	def _on_studies_list_item_selected(self, event):
		event.Skip()
		if self.__pacs is None:
			return

		study_data = self._LCTRL_studies.get_item_data(item_idx = event.Index)
		series_list_items = []
		series_list_data = []
		for series in study_data['series']:

			series_time = ''
			if series['time'] is None:
				series['time'] = study_data['time']
			if series['time'] is None:
				series_time = '?'
			else:
				series_time = '%s:%s:%s' % (
					series['time'][:2],
					series['time'][2:4],
					series['time'][4:6]
				)

			series_desc_parts = []
			if series['description'] is not None:
				if series['protocol'] is None:
					series_desc_parts.append(series['description'].strip())
				else:
					if series['description'].strip() not in series['protocol'].strip():
						series_desc_parts.append(series['description'].strip())
			if series['protocol'] is not None:
				series_desc_parts.append('[%s]' % series['protocol'].strip())
			if series['performed_procedure_step_description'] is not None:
				series_desc_parts.append(series['performed_procedure_step_description'].strip())
			if series['acquisition_device_processing_description'] is not None:
				series_desc_parts.append(series['acquisition_device_processing_description'].strip())
			series_desc = ' / '.join(series_desc_parts)
			if len(series_desc) > 0:
				series_desc = ': ' + series_desc
			series_desc = _('%s image(s)%s') % (len(series['instances']), series_desc)

			series_list_items.append ([
				series_time,
				gmTools.coalesce(series['modality'], ''),
				gmTools.coalesce(series['body_part'], ''),
				series_desc
			])
			series_list_data.append(series)

		self._LCTRL_series.set_string_items(items = series_list_items)
		self._LCTRL_series.set_data(data = series_list_data)
		self._LCTRL_series.SortListItems(0)

		self.__refresh_image()
		self.__refresh_details()
		self.__set_button_states()

	#--------------------------------------------------------
	def _on_studies_list_item_deselected(self, event):
		event.Skip()

		self._LCTRL_series.remove_items_safely()
		self.__refresh_image()
		self.__refresh_details()
		self.__set_button_states()

	#--------------------------------------------------------
	# events: buttons
	#--------------------------------------------------------
	def _on_connect_button_pressed(self, event):
		event.Skip()

		if not self.__connect():
			self.__reset_patient_data()
			self.__set_button_states()
			return False

		if not self.__refresh_patient_data():
			self.__set_button_states()
			return False

		self.__set_button_states()
		return True

	#--------------------------------------------------------
	def _on_upload_button_pressed(self, event):
		event.Skip()
		if self.__pacs is None:
			return

		dlg = wx.DirDialog (
			self,
			message = _('Select the directory from which to recursively upload DICOM files.'),
			defaultPath = gmTools.gmPaths().user_work_dir
		)
		choice = dlg.ShowModal()
		dicom_dir = dlg.GetPath()
		dlg.DestroyLater()
		if choice != wx.ID_OK:
			return True

		wx.BeginBusyCursor()
		try:
			uploaded, not_uploaded, new_patients = self.__pacs.upload_from_directory (
				directory = dicom_dir,
				recursive = True,
				check_mime_type = False,
				ignore_other_files = True
			)
		finally:
			wx.EndBusyCursor()
		if not uploaded:
			gmGuiHelpers.gm_show_warning (
				warning = _('No files uploaded.'),
				title = _('Uploading DICOM files')
			)
			return

		if len(not_uploaded) == 0:
			q = _('Delete the uploaded DICOM files now ?')
		else:
			q = _('Some files have not been uploaded.\n\nDo you want to delete those DICOM files which *have* been sent to the PACS successfully ?')
			_log.error('not uploaded:')
			for f in not_uploaded:
				_log.error(f)
		delete_uploaded = gmGuiHelpers.gm_show_question (
			title = _('Uploading DICOM files'),
			question = q,
			cancel_button = False
		)
		wx.BeginBusyCursor()
		if delete_uploaded:
			try:
				for f in uploaded:
					gmTools.remove_file(f)
			finally:
				wx.EndBusyCursor()
		info = ''
		already_seen = []
		for orth_pat_id in new_patients:
			if orth_pat_id in already_seen:
				continue
			try:
				orth_pat = self.__pacs.get_patient(orth_pat_id)['MainDicomTags']
				_log.debug(orth_pat)
				info += '%s - %s - %s\n' % (orth_pat['PatientName'], orth_pat['PatientSex'], orth_pat['PatientBirthDate'])
				info += ' ID: %s\n' % orth_pat['PatientID']
				info += ' Orthanc: %s\n' % orth_pat_id
				already_seen.append(orth_pat_id)
			except Exception:
				_log.execption('cannot retrieve/process Orthanc data for patient [%s]', orth_pat_id)
			continue
		wx.EndBusyCursor()
		if not info:
			return

		info = _('Information has been added to the PACS for the following patients:\n\n') + info
		gmGuiHelpers.gm_show_info (
			title = _('Uploading DICOM files'),
			info = info
		)

	#--------------------------------------------------------
	def _on_modify_orthanc_content_button_pressed(self, event):
		event.Skip()
		if self.__pacs is None:
			return

		title = _('Working on: Orthanc "%s" (AET "%s" @ %s:%s, Version %s)') % (
			self.__pacs.server_identification['Name'],
			self.__pacs.server_identification['DicomAet'],
			self._TCTRL_host.Value.strip(),
			self._TCTRL_port.Value.strip(),
			self.__pacs.server_identification['Version']
		)
		dlg = cModifyOrthancContentDlg(self, -1, server = self.__pacs, title = title)
		dlg.ShowModal()
		dlg.DestroyLater()
		self._schedule_data_reget()

	#--------------------------------------------------------
	# - image menu and image buttons
	#--------------------------------------------------------
	def _on_show_image_as_dcm(self, event):
		self.__show_image(as_dcm = True)

	#--------------------------------------------------------
	def _on_show_image_as_png(self, event):
		self.__show_image(as_png = True)

	#--------------------------------------------------------
	def _on_copy_image_to_export_area(self, event):
		self.__copy_image_to_export_area()

	#--------------------------------------------------------
	def _on_save_image_as_png(self, event):
		self.__save_image(as_png = True, nice_filename = True)

	#--------------------------------------------------------
	def _on_save_image_as_dcm(self, event):
		self.__save_image(as_dcm = True, nice_filename = True)

	#--------------------------------------------------------
	#--------------------------------------------------------
	def _on_preview_image_leftdoubleclicked(self, event):
		self.__show_image()

	#--------------------------------------------------------
	def _on_preview_image_rightclicked(self, event):
		if self.__image_data is None:
			return False

		self.PopupMenu(self.__thumbnail_menu)

	#--------------------------------------------------------
	def _on_next_image_button_pressed(self, event):
		if self.__image_data is None:
			return

		self.__refresh_image(idx = self.__image_data['idx'] + 1)
		self.__refresh_details()

	#--------------------------------------------------------
	def _on_previous_image_button_pressed(self, event):
		if self.__image_data is None:
			return
		self.__refresh_image(idx = self.__image_data['idx'] - 1)
		self.__refresh_details()

	#--------------------------------------------------------
	def _on_button_image_show_pressed(self, event):
		self.__show_image()

	#--------------------------------------------------------
	def _on_button_image_export_pressed(self, event):
		self.__copy_image_to_export_area()

	#--------------------------------------------------------
	# - study menu and buttons
	#--------------------------------------------------------
	def _on_browse_study_button_pressed(self, event):
		self.__browse_studies()

	#--------------------------------------------------------
	def _on_studies_show_button_pressed(self, event):
		self.__show_studies()

	#--------------------------------------------------------
	def _on_studies_export_button_pressed(self, event):
		self.__copy_selected_studies_to_export_area()

	#--------------------------------------------------------
	def _on_studies_button_rightclicked(self, event):
		self.PopupMenu(self.__studies_menu)

	#--------------------------------------------------------
	def _on_copy_selected_studies_to_export_area(self, event):
		self.__copy_selected_studies_to_export_area()

	#--------------------------------------------------------
	def _on_copy_all_studies_to_export_area(self, event):
		self.__copy_all_studies_to_export_area()

	#--------------------------------------------------------
	def _on_copy_zip_of_selected_studies_to_export_area(self, event):
		self.__copy_zip_of_selected_studies_to_export_area()

	#--------------------------------------------------------
	def _on_copy_zip_of_all_studies_to_export_area(self, event):
		self.__copy_zip_of_all_studies_to_export_area()

	#--------------------------------------------------------
	def _on_save_selected_studies(self, event):
		self.__save_selected_studies()

	#--------------------------------------------------------
	def _on_save_zip_of_selected_studies(self, event):
		self.__save_zip_of_selected_studies()

	#--------------------------------------------------------
	def _on_save_all_studies(self, event):
		self.__save_all_studies()

	#--------------------------------------------------------
	def _on_save_zip_of_all_studies(self, event):
		self.__save_zip_of_all_studies()

	#--------------------------------------------------------
	# - patient buttons (= all studies)
	#--------------------------------------------------------
	def _on_browse_patient_button_pressed(self, event):
		self.__browse_patient()

	#--------------------------------------------------------
	def _on_verify_patient_data_button_pressed(self, event):
		if self.__pacs is None:
			return None

		if self.__orthanc_patient is None:
			return None

		patient_id = self.__orthanc_patient['ID']
		wx.BeginBusyCursor()
		try:
			bad_data = self.__pacs.verify_patient_data(patient_id)
		finally:
			wx.EndBusyCursor()
		if len(bad_data) == 0:
			gmDispatcher.send(signal = 'statustext', msg = _('Successfully verified DICOM data of patient.'))
			return

		gmGuiHelpers.gm_show_error (
			title = _('DICOM data error'),
			error = _(
				'There seems to be a data error in the DICOM files\n'
				'stored in the Orthanc server.\n'
				'\n'
				'Please check the inbox.'
			)
		)

		msg = _('Checksum error in DICOM data of this patient.\n\n')
		msg += _('DICOM server: %s\n\n') % bad_data[0]['orthanc']
		for bd in bad_data:
			msg += _('Orthanc patient ID [%s]\n %s: [%s]\n') % (
				bd['patient'],
				bd['type'],
				bd['instance']
			)
		prov = self.__patient.primary_provider
		if prov is None:
			prov = gmStaff.gmCurrentProvider()
		report = gmProviderInbox.create_inbox_message (
			message_type = _('error report'),
			message_category = 'clinical',
			patient = self.__patient.ID,
			staff = prov['pk_staff'],
			subject = _('DICOM data corruption')
		)
		report['data'] = msg
		report.save()

	#--------------------------------------------------------
	def _on_browse_pacs_button_pressed(self, event):
		self.__browse_pacs()

#------------------------------------------------------------
from Gnumed.wxGladeWidgets.wxgModifyOrthancContentDlg import wxgModifyOrthancContentDlg

class cModifyOrthancContentDlg(wxgModifyOrthancContentDlg):
	def __init__(self, *args, **kwds):
		self.__srv = kwds['server']
		del kwds['server']
		title = kwds['title']
		del kwds['title']
		wxgModifyOrthancContentDlg.__init__(self, *args, **kwds)
		self.SetTitle(title)
		self._LCTRL_patients.set_columns( [_('Study date'), _('Patient ID (DICOM study)'), _('Name'), _('Birth date'), _('Gender'), _('Patient UID (Orthanc)'), _('Study')] )

	#--------------------------------------------------------
	def __refresh_patient_list(self):
		self._LCTRL_patients.set_string_items()
		search_term = self._TCTRL_search_term.Value.strip()
		if search_term == '':
			return

		studies = []
		studies.extend(self.__srv.search_studies_by_patient_name(name = search_term))
		studies.extend(self.__srv.search_studies_by_patient_id(patient_id = search_term))
		if len(studies) == 0:
			return

		list_items = []
		list_data = []
		for study in studies:
			mt = study['PatientMainDicomTags']
			try:
				gender = mt['PatientSex']
			except KeyError:
				gender = ''
			try:
				dob = mt['PatientBirthDate']
			except KeyError:
				dob = ''
			list_items.append ([
				study['MainDicomTags']['StudyDate'],
				mt['PatientID'],
				mt['PatientName'],
				dob,
				gender,
				study['ParentPatient'],
				study['ID']
			])
			list_data.append(mt['PatientID'])
		self._LCTRL_patients.set_string_items(list_items)
		self._LCTRL_patients.set_column_widths()
		self._LCTRL_patients.set_data(list_data)

	#--------------------------------------------------------
	def _on_search_patients_button_pressed(self, event):
		event.Skip()
		self.__refresh_patient_list()

	#--------------------------------------------------------
	def _on_suggest_patient_id_button_pressed(self, event):
		event.Skip()
		pat = gmPerson.gmCurrentPatient()
		if not pat.connected:
			return
		self._TCTRL_new_patient_id.Value = pat.suggest_external_id(target = 'PACS')

	#--------------------------------------------------------
	def _on_set_patient_id_button_pressed(self, event):
		event.Skip()
		new_id = self._TCTRL_new_patient_id.Value.strip()
		if new_id == '':
			return

		studies = self._LCTRL_patients.get_selected_item_data(only_one = False)
		if len(studies) == 0:
			return

		really_modify = gmGuiHelpers.gm_show_question (
			title = _('Modifying patient ID'),
			question = _(
				'Really modify %s DICOM studies to have the new patient ID\n\n'
				' [%s]\n\n'
				'stored in the Orthanc DICOM server ?'
			) % (
				len(studies),
				new_id
			),
			cancel_button = True
		)
		if not really_modify:
			return

		all_modified = True
		for study in studies:
			success = self.__srv.modify_patient_id(old_patient_id = study, new_patient_id = new_id)
			if not success:
				all_modified = False
		self.__refresh_patient_list()
		if not all_modified:
			gmGuiHelpers.gm_show_warning (
				title = _('Modifying patient ID'),
				warning = _(
					'I was unable to modify all DICOM studies selected.\n'
					'\n'
					'Please refer to the log file.'
				)
			)
		return all_modified

#------------------------------------------------------------
# outdated:
#def upload_files():
#	event.Skip()
#	dlg = wx.DirDialog (
#		self,
#		message = _('Select the directory from which to recursively upload DICOM files.'),
#		defaultPath = gmTools.gmPaths().user_work_dir
#	)
#	choice = dlg.ShowModal()
#	dicom_dir = dlg.GetPath()
#	dlg.DestroyLater()
#	if choice != wx.ID_OK:
#		return True
#	wx.BeginBusyCursor()
#	try:
#		uploaded, not_uploaded = self.__pacs.upload_from_directory (
#			directory = dicom_dir,
#			recursive = True,
#			check_mime_type = False,
#			ignore_other_files = True
#		)
#	finally:
#		wx.EndBusyCursor()
#	if len(not_uploaded) == 0:
#		q = _('Delete the uploaded DICOM files now ?')
#	else:
#		q = _('Some files have not been uploaded.\n\nDo you want to delete those DICOM files which have been sent to the PACS successfully ?')
#		_log.error('not uploaded:')
#		for f in not_uploaded:
#			_log.error(f)
#		delete_uploaded = gmGuiHelpers.gm_show_question (
#		title = _('Uploading DICOM files'),
#		question = q,
#		cancel_button = False
#	)
#	if not delete_uploaded:
#		return
#	wx.BeginBusyCursor()
#	for f in uploaded:
#		gmTools.remove_file(f)
#	wx.EndBusyCursor()

#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmLog2
	gmLog2.print_logfile_name()
	del _
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain()

	from Gnumed.pycommon import gmPG2

	#from Gnumed.wxpython import gmGuiTest

	#----------------------------------------------------------------
	#----------------------------------------------------------------
	def test_plugin():
		wx.Log.EnableLogging(enable = False)

	#----------------------------------------------------------------
	#----------------------------------------------------------------
	#test_plugin()

	gmPG2.request_login_params(setup_pool = True)
	gmStaff.set_current_provider_to_logged_on_user()
	gmPraxis.gmCurrentPraxisBranch.from_first_branch()
