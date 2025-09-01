"""GNUmed data mining related widgets."""

#================================================================
__author__ = 'karsten.hilbert@gmx.net'
__license__ = 'GPL v2 or later (details at https://www.gnu.org)'


# stdlib
import sys
import fileinput
import logging
import csv


# 3rd party
import wx


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmMimeLib
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmMatchProvider
from Gnumed.pycommon import gmNetworkTools
from Gnumed.pycommon.gmExceptions import ConstructorError

from Gnumed.business import gmPerson
from Gnumed.business import gmDataMining
from Gnumed.business import gmPersonSearch

from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmListWidgets


_log = logging.getLogger('gm.ui')
#================================================================
class cPatientListingCtrl(gmListWidgets.cReportListCtrl):

	def __init__(self, *args, **kwargs):
		"""<patient_key> must index or name a column in self.__data"""
		try:
			self.patient_key = kwargs['patient_key']
			del kwargs['patient_key']
		except KeyError:
			self.patient_key = None

		gmListWidgets.cReportListCtrl.__init__(self, *args, **kwargs)

		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_list_item_activated, self)
	#------------------------------------------------------------
	def __get_patient_pk_data_key(self, data=None):
		if self.data is None:
			return None

		if len(self.data) == 0:
			return None

		if data is None:
			data = self.get_selected_item_data(only_one = True)

		if data is None:
			data = self.get_item_data(item_idx = 0)

		if data is None:
			return None

		if self.patient_key is not None:
			try:
				data[self.patient_key]
				return self.patient_key
			except (KeyError, IndexError, TypeError):
				# programming error
				_log.error('misconfigured identifier column <%s>', self.patient_key)

		_log.debug('identifier column not configured, trying to detect')

		if 'pk_patient' in data:
			return 'pk_patient'

		if 'fk_patient' in data:
			return 'fk_patient'

		if 'pk_identity' in data:
			return 'pk_identity'

		if 'fk_identity' in data:
			return 'fk_identity'

		if 'id_identity' in data:
			return 'id_identity'

		return gmListWidgets.get_choices_from_list (
			parent = self,
			msg = _(
				'The report result list does not contain any of the following columns:\n'
				'\n'
				' <%s> / pk_patient / fk_patient\n'
				' pk_identity / fk_identity / id_identity\n'
				'\n'
				'Select the column which contains patient IDs:\n'
			) % self.patient_key,
			caption = _('Choose column from query results ...'),
			choices = list(data),
			columns = [_('Column name')],
			single_selection = True
		)

	patient_pk_data_key = property(__get_patient_pk_data_key)
	#------------------------------------------------------------
	# event handling
	#------------------------------------------------------------
	def _on_list_item_activated(self, evt):
		data = self.get_selected_item_data(only_one = True)
		pk_pat_col = self.__get_patient_pk_data_key(data = data)

		if pk_pat_col is None:
			gmDispatcher.send(signal = 'statustext', msg = _('List not known to be patient-related.'))
			return

		pat_data = data[pk_pat_col]
		try:
			pat_pk = int(pat_data)
			pat = gmPerson.cPerson(aPK_obj = pat_pk)
		except (ValueError, TypeError):
			searcher = gmPersonSearch.cPatientSearcher_SQL()
			idents = searcher.get_identities(pat_data)
			if len(idents) == 0:
				gmDispatcher.send(signal = 'statustext', msg = _('No matching patient found.'))
				return
			if len(idents) == 1:
				pat = idents[0]
			else:
				from Gnumed.wxpython import gmPatSearchWidgets
				dlg = gmPatSearchWidgets.cSelectPersonFromListDlg(parent=wx.GetTopLevelParent(self), id=-1)
				dlg.set_persons(persons=idents)
				result = dlg.ShowModal()
				if result == wx.ID_CANCEL:
					dlg.DestroyLater()
					return
				pat = dlg.get_selected_person()
				dlg.DestroyLater()
		except ConstructorError:
			gmDispatcher.send(signal = 'statustext', msg = _('No matching patient found.'))
			return

		from Gnumed.wxpython import gmPatSearchWidgets
		gmPatSearchWidgets.set_active_patient(patient = pat)

#================================================================
from Gnumed.wxGladeWidgets import wxgPatientListingPnl

class cPatientListingPnl(wxgPatientListingPnl.wxgPatientListingPnl):

	def __init__(self, *args, **kwargs):

		try:
			button_defs = kwargs['button_defs'][:5]
			del kwargs['button_defs']
		except KeyError:
			button_defs = []

		try:
			msg = kwargs['message']
			del kwargs['message']
		except KeyError:
			msg = None

		wxgPatientListingPnl.wxgPatientListingPnl.__init__(self, *args, **kwargs)

		if msg is not None:
			self._lbl_msg.SetLabel(msg)

		buttons = [self._BTN_1, self._BTN_2, self._BTN_3, self._BTN_4, self._BTN_5]
		for idx in range(len(button_defs)):
			button_def = button_defs[idx]
			if button_def['label'].strip() == '':
				continue
			buttons[idx].SetLabel(button_def['label'])
			buttons[idx].SetToolTip(button_def['tooltip'])
			buttons[idx].Enable(True)

		self.Fit()
	#------------------------------------------------------------
	# event handling
	#------------------------------------------------------------
	def _on_BTN_1_pressed(self, event):
		event.Skip()
	#------------------------------------------------------------
	def _on_BTN_2_pressed(self, event):
		event.Skip()
	#------------------------------------------------------------
	def _on_BTN_3_pressed(self, event):
		event.Skip()
	#------------------------------------------------------------
	def _on_BTN_4_pressed(self, event):
		event.Skip()
	#------------------------------------------------------------
	def _on_BTN_5_pressed(self, event):
		event.Skip()

#================================================================
from Gnumed.wxGladeWidgets import wxgDataMiningPnl

class cDataMiningPnl(wxgDataMiningPnl.wxgDataMiningPnl):

	def __init__(self, *args, **kwargs):
		wxgDataMiningPnl.wxgDataMiningPnl.__init__(self, *args, **kwargs)

		self.__init_ui()

		# make me a file drop target
		dt = gmGuiHelpers.cFileDropTarget(target = self)
		self.SetDropTarget(dt)
	#--------------------------------------------------------
	def __init_ui(self):
		mp = gmMatchProvider.cMatchProvider_SQL2 (
			queries = ["""
				SELECT DISTINCT ON (label)
					cmd,
					label
				FROM cfg.report_query
				WHERE
					label %(fragment_condition)s
						OR
					cmd %(fragment_condition)s
			"""]
		)
		mp.setThresholds(2,3,5)
		self._PRW_report_name.matcher = mp
		self._PRW_report_name.add_callback_on_selection(callback = self._on_report_selected)
		self._PRW_report_name.add_callback_on_lose_focus(callback = self._auto_load_report)
	#--------------------------------------------------------
	def _auto_load_report(self, *args, **kwargs):
		if self._TCTRL_query.GetValue() == '':
			if self._PRW_report_name.GetData() is not None:
				self._TCTRL_query.SetValue(self._PRW_report_name.GetData())
				self._BTN_run.SetFocus()
	#--------------------------------------------------------
	def _on_report_selected(self, *args, **kwargs):
		self._TCTRL_query.SetValue(self._PRW_report_name.GetData())
		self._BTN_run.SetFocus()
	#--------------------------------------------------------
	# file drop target API
	#--------------------------------------------------------
	def _drop_target_consume_filenames(self, filenames):
		# act on first file only
		fname = filenames[0]
		_log.debug('importing SQL from <%s>', fname)
		# act on text files only
		mime_type = gmMimeLib.guess_mimetype(fname)
		_log.debug('mime type: %s', mime_type)
		if not mime_type.startswith('text/'):
			_log.debug('not a text file')
			gmDispatcher.send(signal='statustext', msg = _('Cannot read SQL from [%s]. Not a text file.') % fname, beep = True)
			return False
#		# act on "small" files only
#		stat_val = os.stat(fname)
#		if stat_val.st_size > 5000:
#			gmDispatcher.send(signal='statustext', msg = _('Cannot read SQL from [%s]. File too big (> 2000 bytes).') % fname, beep = True)
#			return False
		# all checks passed
		for line in fileinput.input(fname):
			self._TCTRL_query.AppendText(line)
	#--------------------------------------------------------
	# notebook plugin API
	#--------------------------------------------------------
	def repopulate_ui(self):
		pass
	#--------------------------------------------------------
	# event handlers
	#--------------------------------------------------------
	def _on_contribute_button_pressed(self, evt):
		report = self._PRW_report_name.GetValue().strip()
		if report == '':
			gmDispatcher.send(signal = 'statustext', msg = _('Report must have a name for contribution.'), beep = False)
			return

		query = self._TCTRL_query.GetValue().strip()
		if query == '':
			gmDispatcher.send(signal = 'statustext', msg = _('Report must have a query for contribution.'), beep = False)
			return

		do_it = gmGuiHelpers.gm_show_question (
			_(	'Be careful that your contribution (the query itself) does\n'
				'not contain any person-identifiable search parameters.\n'
				'\n'
				'Note, however, that no query result data whatsoever\n'
				'is included in the contribution that will be sent.\n'
				'\n'
				'Are you sure you wish to send this query to\n'
				'the gnumed community mailing list?\n'
			),
			_('Contributing custom report')
		)
		if not do_it:
			return

		msg = """--- This is a report definition contributed by a GNUmed user.

--- Save it as a text file and drop it onto the Report Generator
--- inside GNUmed in order to take advantage of the contribution.

----------------------------------------

--- %s

%s

----------------------------------------

--- The GNUmed client.
""" % (report, query)

		auth = {'user': gmNetworkTools.default_mail_sender, 'password': 'gnumed-at-gmx-net'}
		if not gmNetworkTools.compose_and_send_email (
			sender = 'GNUmed Report Generator <gnumed@gmx.net>',
			receiver = ['gnumed-devel@gnu.org'],
			subject = 'user contributed report',
			message = msg,
			server = gmNetworkTools.default_mail_server,
			auth = auth
		):
			gmDispatcher.send(signal = 'statustext', msg = _('Unable to send mail. Cannot contribute report [%s] to GNUmed community.') % report, beep = True)
			return False

		gmDispatcher.send(signal = 'statustext', msg = _('Thank you for your contribution to the GNUmed community!'), beep = False)
		return True
	#--------------------------------------------------------
	def _on_schema_button_pressed(self, evt):
		# will block when called in text mode (that is, from a terminal, too !)
		gmNetworkTools.open_url_in_browser(url = 'https://www.gnumed.de/bin/view/Gnumed/DatabaseSchema')
	#--------------------------------------------------------
	def _on_delete_button_pressed(self, evt):
		report = self._PRW_report_name.GetValue().strip()
		if report == '':
			return True
		if gmDataMining.delete_report_definition(name=report):
			self._PRW_report_name.SetText()
			self._TCTRL_query.SetValue('')
			gmDispatcher.send(signal='statustext', msg = _('Deleted report definition [%s].') % report, beep=False)
			return True
		gmDispatcher.send(signal='statustext', msg = _('Error deleting report definition [%s].') % report, beep=True)
		return False
	#--------------------------------------------------------
	def _on_clear_button_pressed(self, evt):
		self._PRW_report_name.SetText()
		self._TCTRL_query.SetValue('')
		self._LCTRL_result.set_columns()
	#--------------------------------------------------------
	def _on_save_button_pressed(self, evt):
		report = self._PRW_report_name.GetValue().strip()
		if report == '':
			gmDispatcher.send(signal='statustext', msg = _('Cannot save report definition without name.'), beep=True)
			return False
		query = self._TCTRL_query.GetValue().strip()
		if query == '':
			gmDispatcher.send(signal='statustext', msg = _('Cannot save report definition without query.'), beep=True)
			return False
		# FIXME: check for exists and ask for permission
		if gmDataMining.save_report_definition(name=report, query=query, overwrite=True):
			gmDispatcher.send(signal='statustext', msg = _('Saved report definition [%s].') % report, beep=False)
			return True
		gmDispatcher.send(signal='statustext', msg = _('Error saving report definition [%s].') % report, beep=True)
		return False
	#--------------------------------------------------------
	def _on_visualize_button_pressed(self, evt):

		try:
			# better fail early
			import Gnuplot
		except ImportError:
			gmGuiHelpers.gm_show_info (
				info = _('Cannot import "Gnuplot" python module.'),
				title = _('Query result visualizer')
			)
			return

		x_col = gmListWidgets.get_choices_from_list (
			parent = self,
			msg = _('Choose a column to be used as the X-Axis:'),
			caption = _('Choose column from query results ...'),
			choices = list(self.query_results[0]),
			columns = [_('Column name')],
			single_selection = True
		)
		if x_col is None:
			return

		y_col = gmListWidgets.get_choices_from_list (
			parent = self,
			msg = _('Choose a column to be used as the Y-Axis:'),
			caption = _('Choose column from query results ...'),
			choices = list(self.query_results[0]),
			columns = [_('Column name')],
			single_selection = True
		)
		if y_col is None:
			return

		# FIXME: support debugging (debug=1) depending on --debug
		gp = Gnuplot.Gnuplot(persist=1)
		if self._PRW_report_name.GetValue().strip() != '':
			gp.title(_('GNUmed report: %s') % self._PRW_report_name.GetValue().strip()[:40])
		else:
			gp.title(_('GNUmed report results'))
		gp.xlabel(x_col)
		gp.ylabel(y_col)
		try:
			gp.plot([ [r[x_col], r[y_col]] for r in self.query_results ])
		except Exception:
			_log.exception('unable to plot results from [%s:%s]' % (x_col, y_col))
			gmDispatcher.send(signal = 'statustext', msg = _('Error plotting data.'), beep = True)

	#--------------------------------------------------------
	def _on_waiting_list_button_pressed(self, event):
		event.Skip()

		pat_pk_key = self._LCTRL_result.patient_pk_data_key
		if pat_pk_key is None:
			gmGuiHelpers.gm_show_info (
				info = _('These report results do not seem to contain per-patient data.'),
				title = _('Using report results')
			)
			return

		zone = wx.GetTextFromUser (
			_('Enter a waiting zone to put patients in:'),
			caption = _('Using report results'),
			default_value = _('search results')
		)
		if zone.strip() == '':
			return

		data = self._LCTRL_result.get_selected_item_data(only_one = False)
		if data is None:
			use_all = gmGuiHelpers.gm_show_question (
				title = _('Using report results'),
				question = _('No results selected.\n\nTransfer ALL patients from results to waiting list ?'),
				cancel_button = True
			)
			if not use_all:
				return
			data = self._LCTRL_result.data

		comment = self._PRW_report_name.GetValue().strip()
		for item in data:
			pat = gmPerson.cPerson(aPK_obj = item[pat_pk_key])
			pat.put_on_waiting_list (comment = comment, zone = zone)

	#--------------------------------------------------------
	def _on_save_results_button_pressed(self, event):
		event.Skip()

		user_query = self._TCTRL_query.GetValue().strip().strip(';')
		if user_query == '':
			return

		pat = None
		curr_pat = gmPerson.gmCurrentPatient()
		if curr_pat.connected:
			pat = curr_pat.ID
		success, hint, cols, rows = gmDataMining.run_report_query (
			query = user_query,
			limit = None,
			pk_identity = pat
		)

		if not success:
			return

		if len(rows) == 0:
			return

		dlg = wx.FileDialog (
			parent = self,
			message = _("Save SQL report query results as CSV in..."),
			defaultDir = gmTools.gmPaths().user_work_dir,
			defaultFile = 'gm-query_results.csv',
			wildcard = '%s (*.csv)|*.csv|%s (*)|*' % (_("CSV files"), _("all files")),
			style = wx.FD_SAVE
		)
		choice = dlg.ShowModal()
		csv_name = dlg.GetPath()
		dlg.DestroyLater()
		if choice != wx.ID_OK:
			return

		csv_file = open(csv_name, mode = 'wt', encoding = 'utf8')
		csv_file.write('#-------------------------------------------------------------------------------------\n')
		csv_file.write('# GNUmed SQL report results\n')
		csv_file.write('#\n')
		csv_file.write('# Report: "%s"\n' % self._PRW_report_name.GetValue().strip())
		csv_file.write('#\n')
		csv_file.write('# SQL:\n')
		for line in user_query.split('\n'):
			csv_file.write('# %s\n' % line)
		csv_file.write('#\n')
		csv_file.write('# ID of active patient: %s\n' % pat)
		csv_file.write('#\n')
		csv_file.write('# hits found: %s\n' % len(rows))
		csv_file.write('#-------------------------------------------------------------------------------------\n')

		csv_writer = csv.writer(csv_file)
		csv_writer.writerow(cols)
		for row in rows:
			csv_writer.writerow(row)

		csv_file.close()

	#--------------------------------------------------------
	def _on_run_button_pressed(self, evt):

		self._BTN_visualize.Enable(False)
		self._BTN_waiting_list.Enable(False)
		self._BTN_save_results.Enable(False)

		user_query = self._TCTRL_query.GetValue().strip().strip(';')
		if user_query == '':
			return True

		limit = 1001
		pat = None
		curr_pat = gmPerson.gmCurrentPatient()
		if curr_pat.connected:
			pat = curr_pat.ID
		success, hint, cols, rows = gmDataMining.run_report_query (
			query = user_query,
			limit = limit,
			pk_identity = pat
		)

		self._LCTRL_result.set_columns()

		if len(rows) == 0:
			self._LCTRL_result.set_columns([_('Results')])
			self._LCTRL_result.set_string_items([[_('Report returned no data.')]])
			self._LCTRL_result.set_column_widths()
			gmDispatcher.send('statustext', msg = _('No data returned for this report.'), beep = True)
			return True

		gmDispatcher.send(signal = 'statustext', msg = _('Found %s results.') % len(rows))

		if len(rows) == 1001:
			gmGuiHelpers.gm_show_info (
				info = _(
					'This query returned at least %s results.\n'
					'\n'
					'GNUmed will only show the first %s rows.\n'
					'\n'
					'You may want to narrow down the WHERE conditions\n'
					'or use LIMIT and OFFSET to batchwise go through\n'
					'all the matching rows.'
				) % (limit, limit-1),
				title = _('Report Generator')
			)
			rows = rows[:-1]		# make it true :-)

		self._LCTRL_result.set_columns(cols)
		for row in rows:
			try:
				label = str(gmTools.coalesce(row[0], '')).replace('\n', '<LF>').replace('\r', '<CR>')
			except UnicodeDecodeError:
				label = _('not str()able')
			if len(label) > 150:
				label = label[:150] + gmTools.u_ellipsis
			row_num = self._LCTRL_result.InsertItem(sys.maxsize, label)
			for col_idx in range(1, len(row)):
				try:
					label = str(gmTools.coalesce(row[col_idx], '')).replace('\n', '<LF>').replace('\r', '<CR>')[:250]
				except UnicodeDecodeError:
					label = _('not str()able')
				if len(label) > 150:
					label = label[:150] + gmTools.u_ellipsis
				self._LCTRL_result.SetItem (
					index = row_num,
					column = col_idx,
					label = label
				)
		# must be called explicitly, because string items are set above without calling set_string_items
		self._LCTRL_result._invalidate_sorting_metadata()
		self._LCTRL_result.set_column_widths()
		self._LCTRL_result.set_data(data = rows)

		self.query_results = rows
		self._BTN_visualize.Enable(True)
		self._BTN_waiting_list.Enable(True)
		self._BTN_save_results.Enable(True)

		return success

#================================================================
# main
#----------------------------------------------------------------
if __name__ == '__main__':
	from Gnumed.pycommon import gmDateTime
	gmDateTime.init()

	#------------------------------------------------------------
#	def test_pat_list_ctrl():
#		app = wx.PyWidgetTester(size = (400, 500))
#		lst = cPatientListingCtrl(app.frame, patient_key = 0)
#		lst.set_columns(['name', 'comment'])
#		lst.set_string_items([
#			['Kirk', 'Kirk by name'],
#			['#12', 'Kirk by ID'],
#			['unknown', 'unknown patient']
#		])
##		app.SetWidget(cPatientListingCtrl, patient_key = 0)
#		app.frame.Show()
#		app.MainLoop()
	#------------------------------------------------------------

#	test_pat_list_ctrl()
