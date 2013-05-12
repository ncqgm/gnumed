"""GNUmed encounter edit widgets."""
# -*- coding: UTF-8 -*-

#================================================================
# @thanks: this code has been based on 
#          progress note plugin and scan doc plugin 
#          by Karsten Hilbert, Sebastian Hilbert and Carlos Moro
#================================================================
__version__ = "$Revision: 2.2 $"
__author__ = "Jerzy Luszawski"
__license__ = "GPL"


import sys, os, types, logging, datetime as pyDT, tempfile
import libxml2, libxslt, cgi

import wx, wx.grid


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.business import gmPerson, gmEMRStructItems, gmClinNarrative, gmForms
from Gnumed.pycommon import gmTools, gmDispatcher, gmMatchProvider, gmDateTime, gmPG2, gmBusinessDBObject, gmExceptions
from Gnumed.wxpython import gmRegetMixin, gmPhraseWheel, gmGuiHelpers, gmMacro
from Gnumed.wxGladeWidgets import wxgEncounterEditPnl


_log = logging.getLogger('gm.ui')
_log.info(__version__)


# you may need to change these:
default_encounter_type = u'in surgery'
default_template = u'Printout - hospital admission - HTML'
encounter_description_discharge = u'in hospital - discharge'
encounter_description_admittance = u'in hospital - admission'
encounter_description_clinic_visit = 'in clinic - visit' 
print_context = u'print.encounter.'
print_all_progress_notes = u'print.episode.all progress notes'
# no need to change these: 
default_dialog_title = _('Gnumed - Encounter Edit plugin')
soap_categories = ['s', 'o', 'a', 'p']

class cFormTemplate(gmForms.cFormTemplate):
	"""add get_data function"""
	def get_data(self):
		"""Returns template data as string"""
		cmd = u'SELECT data FROM ref.paperwork_templates WHERE pk = %(pk)s'
		rows, idx = gmPG2.run_ro_queries (queries = [{'cmd': cmd, 'args': {'pk': self.pk_obj}}])
		if len(rows) == 0:
			raise gmExceptions.NoSuchBusinessObjectError, 'Cannot get data for template pk = %s' % (self.pk_obj)
			return
		return unicode(str(rows[0][0]), 'UTF-8')	# FIXME: why this conversion is needed?
#================================================================
# define a class for HTML forms (for printing)
#================================================================
class cFormXSLT(gmForms.cFormEngine):
	"""This class can create XML document from placeholders and supplied data,
	then process it with XSLT template and display results
	"""
	_preview_program = u'oowriter '	#this program must be in the system PATH
	def __init__ (self, template=None):
		self._FormData = None
		if template is None:
			_log.error(u'%s: cannot create form instance without a template' % __name__)
			return
		gmForms.cFormEngine.__init__(self, template = template)
		self._XSLTData = template.get_data()
		self._SQL_query = template['sql_query']
		#FIXME: what about encoding conversions?
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def process(self, sql_parameters):
		"""replaces placeholders with data"""

		rows, idx  = gmPG2.run_ro_queries(queries = [{'cmd': self._SQL_query, 'args': sql_parameters}], get_col_idx=True)

		#"""make XML file from dictionary"""

		__header = '<?xml version="1.0" encoding="UTF-8"?>\n'
		__body = rows[0][0]
		# __body = u'<rowset>\n'
		# for row in placeholders_data_rows:
			# __body += u'\t<row>\n'
			# for col in __cols:
				# print 'debug1\n'
				# print row[col]
				# __body += u'\t\t<%(col)s>%(value)s</%(col)s>\n' % {'col': col, 'value' : cgi.escape( gmTools.coalesce(row[col], u'') )}
			# __body += u'\t<\row>\n'
		# __body += u'</rowset>\n'

		# self._XMLData =__header.encode('utf-8') + __body.encode('utf-8')
		# removed explicit encoding, the __body seems to be already in utf-8, and while encoding it was treated as ascii
		self._XMLData =__header + __body
		#"""process XML data according to supplied XSLT, producing HTML"""

		styledoc = libxml2.parseDoc(self._XSLTData)
		style = libxslt.parseStylesheetDoc(styledoc)
		doc = libxml2.parseDoc(self._XMLData)
		result = style.applyStylesheet(doc, None)
		self._FormData = result.serialize()

		style.freeStylesheet()
		doc.freeDoc()
		result.freeDoc()
	#--------------------------------------------------------
	def preview(self):
		if self._FormData is None:
			raise ValueError, u'Previev request for empty form. Make sure the form is properly initialized and process() was performed'
		print "creating temp file"
		try:
			_handle, self.filename = tempfile.mkstemp('.html', 'gm-report-', text = True)

			os.write(_handle, self._FormData.encode('UTF-8'))
		except:
			print "no temp file"
			_log.error('%s: cannot write to temporary file' % __name__)
			return
		os.close(_handle)
		_command = self.__class__._preview_program + self.filename
		try:
			#os.spawnl(os.P_NOWAIT, 'swriter', 'swriter', filename)
			os.system(_command)
		except:
			_log.error('%s: cannot launch report preview program' % __name__)
		#os.unlink(self.filename) #delete file
		#FIXME: under Windows the temp file is deleted before preview program gets it (under Linux it works OK) 
	#--------------------------------------------------------
	def print_directly(self):
		#not so fast, look at it first
		self.preview()

#================================================================
# define a class for XML forms (for printing)
#================================================================
class cFormXML(gmForms.cFormEngine):
	"""This class can process HTML template,
	replace placeholders with supplied data and display results
	"""
	_prefix = u'<text:placeholder text:placeholder-type="text">&lt;'
	_postfix = u'&gt;</text:placeholder>'
	_preview_program = u'oowriter '	#this program must be in the system PATH
	def __init__ (self, template=None):
		self._FormData = None
		if template is None:
			_log.error(u'%s: cannot create form instance without a template' % __name__)
			return
		gmForms.cFormEngine.__init__(self, template = template)
		cmd = u'SELECT data FROM ref.paperwork_templates WHERE pk = %s'
		rows, idx = gmPG2.run_ro_queries (queries = [{'cmd': cmd, 'args': [template['pk_paperwork_template']]}])
		if len(rows) == 0:
			_log.error(u'%s: cannot get template data' % __name__)
			return
		self._FormData = unicode(str(rows[0][0]), 'UTF-8')	# since it is html form, data contains plain text
		#FIXME: what about encoding conversions?
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def process(self, placeholders_data):
		"""replaces placeholders with supplied data"""
		for _placeholder in placeholders_data.keys():
			_search = self.__class__._prefix + _placeholder + self.__class__._postfix
			self._FormData = self._FormData.replace(_search, makeXmlText(placeholders_data[_placeholder]))
	#--------------------------------------------------------
	def preview(self):
		try:
			_handle, self.filename = tempfile.mkstemp('.fodt', 'gm-report-', text = True)
			os.write(_handle, self._FormData.encode('UTF-8'))
		except:
			_log.error('%s: cannot write to temporary file' % (__name__))
			return
		os.close(_handle)
		_command = self.__class__._preview_program + self.filename
		try:
			#os.spawnl(os.P_NOWAIT, 'swriter', 'swriter', filename)
			os.system(_command)
		except:
			_log.error('%s: cannot launch report preview program' % __name__)
		#os.unlink(self.filename) #delete file
		#FIXME: under Windows the temp file is deleted before preview program gets it (under Linux it works OK) 
	#--------------------------------------------------------
	def print_directly(self):
		#not so fast, look at it first
		self.preview()


#================================================================
# redefine an encounter class
#================================================================
class cEncounter(gmEMRStructItems.cEncounter):
	def __init__(self, create_new = False, connection = None, *args, **kwargs):

		"""If create_new = True parameters 'fk_patient' and 'enc_type' must be supplied.
		If parameter 'connection' is not None, the supplied connection object is used for 
		database operations, and the transaction is NOT closed, so it can be rolled back."""
		# process 'create_new' parameter, if False - just init gmClinNarrative.cNarrative
		if create_new:
			try:
				aPK_obj = self.__insert(fk_patient = kwargs['fk_patient'], enc_type = kwargs['enc_type'], connection = connection)
			except KeyError:
				_log.error(u'cannot create new cEncounter without required minimal data (fk_patient or enc_type missing)')
				raise gmExceptions.ConstructorError, "cannot create new cEncounter without required minimal data (fk_patient or enc_type missing)"
			else:
				gmEMRStructItems.cEncounter.__init__(self, aPK_obj = aPK_obj)
		else:
			gmEMRStructItems.cEncounter.__init__(self, *args, **kwargs)
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def update(self, *args, **kwargs):
		"""store data in existing records"""
		# just to rename this function
		self.save_payload(*args, **kwargs)
	#--------------------------------------------------------
	def delete(self):
		"""not implemented yet"""
		raise NotImplementedError
	#--------------------------------------------------------
	# internal functions
	#--------------------------------------------------------
	def __insert(self, fk_patient, enc_type, connection = None):
		#creates required record in database
		#returns pk of created record
		#no use of gmEMRStructItems.create_encounter 
		#because we need to init cEncounter using customized data in THIS class definition,
		#not the gmEMRStructItems.cEncounter, so we need pk_encounter.
		#
		#double check parameters
		_log.debug(u'%s: insert cEncounter: fk_patient = %s, enc_type = %s' % (__name__, fk_patient, enc_type))
		if ((fk_patient is None)
					or (enc_type is None)) :
			_log.error(u'%s: cannot create new cEncounter - invalid data (fk_patient = %s, enc_type = %s' % (__name__, fk_patient, enc_type))
			raise gmExceptions.ConstructorError, "cannot create new cEncounter - invalid data (fk_patient = %s, enc_type = %s)" % (fk_patient, enc_type)
		else:
			queries = [
				{'cmd': u"insert into clin.encounter (fk_patient, fk_location, fk_type) values ( %s, -1, %s)",
				 'args': [fk_patient, enc_type]},
				{'cmd': u"select currval('clin.encounter_pk_seq')"}
				]
			try:
				rows, idx = gmPG2.run_rw_queries(queries = queries, return_data=True, link_obj=connection)
			except:
				_log.error(u'%s: cannot create new cEncounter - database error' % __name__)
				raise gmExceptions.ConstructorError, 'cannot create new cEncounter - database error'
			return rows[0][0]	#return clin.encounter.pk

#================================================================
# redefine a narrative class
#================================================================
class cNarrative(gmClinNarrative.cNarrative):
	"""Redefine cNarrative, because we need more data.
			It is based on clin.v_pat_narrative_full instead of clin.v_pat_narrative.
	"""
	_cmd_fetch_payload = u"select * from clin.v_pat_narrative_full where pk_narrative=%s"
	_cmds_store_payload = [
		u"""update clin.clin_narrative set
				narrative=%(narrative)s,
				clin_when=%(clin_when)s,
				soap_cat=lower(%(soap_cat)s)
			where
				pk=%(pk_narrative)s and
				xmin=%(xmin_clin_narrative)s""",
		u"""select xmin_clin_narrative from clin.v_pat_narrative where pk_narrative=%(pk_narrative)s"""
		]

	_updatable_fields = [
		'narrative',
		'clin_when',
		'soap_cat'
		]
	def __init__(self, create_new = False, connection = None, *args, **kwargs):
		# process 'create_new' parameter, if False - just init gmClinNarrative.cNarrative
		if create_new:
			try: 
				aPK_obj = self.__insert(narrative=kwargs['narrative'], soap_cat=kwargs['soap_cat'], episode_id=kwargs['episode_id'], encounter_id=kwargs['encounter_id'], connection = connection)
			except KeyError:
				_log.error(u'cannot create new cNarrative - required data missing')
				raise gmExceptions.ConstructorError, "cannot create new cNarrative - required data missing"
			else:
				gmClinNarrative.cNarrative.__init__(self, aPK_obj = aPK_obj)
		else:
			gmClinNarrative.cNarrative.__init__(self, *args, **kwargs)
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def update(self, *args, **kwargs):
		"""store data in existing records"""
		# just to rename this function
		self.save_payload(*args, **kwargs)	
	#--------------------------------------------------------
	def delete(self):
		"""This cannot be allowed, because we would lost the history of changes."""
		#raise an error to catch it
		raise NotImplementedError
	#--------------------------------------------------------
	# internal functions
	#--------------------------------------------------------
	def __insert(self, narrative=None, soap_cat=None, episode_id=None, encounter_id=None, connection = None):
		#no use of gmClinNarrative.create_clin_narrative 
		#because we need to init cNarrative using customized data in THIS class definition,
		#not the gmClinNarrative.cNarrative
		#
		#double check parameters
		_log.debug(u'%s: insert cNarrative: narrative = %s, soap_cat = %s, episode_id = %s, encounter_id = %s' % (__name__, narrative, soap_cat, episode_id, encounter_id))
		if ((gmTools.coalesce(narrative, u'') == u'')
					or (gmTools.coalesce(soap_cat, u'') == u'')
					or (episode_id is None)
					or (encounter_id is None)) :
			_log.error(u'%s: cannot create new cNarrative - invalid data (narrative = %s, soap_cat = %s, episode_id = %s, encounter_id = %s)' % (__name__, narrative, soap_cat, episode_id, encounter_id))
			raise gmExceptions.ConstructorError, "cannot create new cNarrative - invalid data (narrative = %s, soap_cat = %s, episode_id = %s, encounter_id = %s)" % (narrative, soap_cat, episode_id, encounter_id)
		else:
			queries = [
				{'cmd': u"insert into clin.clin_narrative (fk_encounter, fk_episode, narrative, soap_cat) values (%s, %s, %s, lower(%s))",
				 'args': [encounter_id, episode_id, narrative, soap_cat]
				},
				{'cmd': u"select currval('clin.clin_narrative_pk_seq')"}
			]
			try:
				rows, idx = gmPG2.run_rw_queries(queries = queries, return_data=True, link_obj=connection)
			except:
				_log.error(u'%s: cannot create new cNarrative - database error' % __name__)
				raise gmExceptions.ConstructorError, "cannot create new cNarrative - database error"
			return rows[0][0]	#return clin.clin_narrative.pk

#================================================================
# define a class for HTML forms (for printing)
#================================================================
class cFormHtml(gmForms.cFormEngine):
	"""This class can process HTML template,
	replace placeholders with supplied data and display results
	"""
	_prefix = u'<!--$$'
	_postfix = u'/$$-->'
	_preview_program = u'oowriter '	#this program must be in the system PATH
	def __init__ (self, template=None):
		self._FormData = None
		if template is None:
			_log.error(u'%s: cannot create form instance without a template' % __name__)
			return
		gmForms.cFormEngine.__init__(self, template = template)
		cmd = u'SELECT data FROM ref.paperwork_templates WHERE pk = %s'
		rows, idx = gmPG2.run_ro_queries (queries = [{'cmd': cmd, 'args': [template['pk_paperwork_template']]}])
		if len(rows) == 0:
			_log.error(u'%s: cannot get template data' % __name__)
			return
		self._FormData = unicode(str(rows[0][0]), 'UTF-8')	# since it is html form, data contains plain text
		#FIXME: what about encoding conversions?
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def process(self, placeholders_data):
		"""replaces placeholders with supplied data"""
		for _placeholder in placeholders_data.keys():
			_search = self.__class__._prefix + _placeholder + self.__class__._postfix
			self._FormData = self._FormData.replace(_search, makeHtmlText(placeholders_data[_placeholder]))
	#--------------------------------------------------------
	def preview(self):
		try:
			_handle, self.filename = tempfile.mkstemp('.html', 'gm-report-', text = True)
			os.write(_handle, self._FormData.encode('UTF-8'))
		except:
			_log.error('%s: cannot write to temporary file' % __name__)
			return
		os.close(_handle)
		_command = self.__class__._preview_program + self.filename
		try:
			#os.spawnl(os.P_NOWAIT, 'swriter', 'swriter', filename)
			os.system(_command)
		except:
			_log.error('%s: cannot launch report preview program' % __name__)
		#os.unlink(self.filename) #delete file
		#FIXME: under Windows the temp file is deleted before preview program gets it (under Linux it works OK) 
	#--------------------------------------------------------
	def print_directly(self):
		#not so fast, look at it first
		self.preview()

#================================================================
# convenience functions
#================================================================
class cDBTransactionFailed(Exception):
	"""Raised when query fails, and we just need to know that 
	the transaction must be rolled back,
	regardless of the cause of failure."""
	def __init__(self, errmsg = None):
		if errmsg is not None:
			self.errmsg=errmsg
		else:
			self.errmsg = "%s: DB query failed, reason unknown" % self.__class__.__name__

	def __str__(self):
		return self.errmsg
#--------------------------------------------------------
def makeXmlText(text = u''):
			"""Simple conversion of text.  Create a more powerful version if you need"""
			xml_text = text
			xml_text = xml_text.replace('<', '&lt;')
			xml_text = xml_text.replace('>', '&gt;')
			xml_text = xml_text.replace('\n', '</text:p><text:p>')
			#FIXME: the following line is an exception to catch list formatting for one template only. 
			#it desperately needs more general solution of preserving formatiing while replacing placeholders
			xml_text = xml_text.replace('&lt;LI&gt;', '</text:p></text:list-item><text:list-item><text:p text:style-name="P34">')
			return xml_text
#--------------------------------------------------------
def report_display_xml(template=None, placeholders_data={}):
	""" Creates new HTML document	based on the template, 
	and replaces placeholders (fields in the template) with supplied data.
	This document is displayed in OpenOffice Writer and can be modified or printed."""
	# suggested place for this function: business/gmForms.py
	# this is slightly rewritten gmFormWidgets.create_new_letter
	# - changed placeholders handling

	if template is None:
		return False
	_report = cFormXML(template)
	_report.process(placeholders_data)
	_report.preview()
#--------------------------------------------------------

def get_latest_soap(pk_encounter = None):
	soap = {}	# it will become a dictionary with keys in ['s', 'o', 'a', 'p'] and cNarrative objects as values
	if pk_encounter is None :
		raise gmExceptions.NoSuchBusinessObjectError, 'No encounter with pk = %s' % (pk_encounter)
	else:
		cmd = u"""SELECT pk AS pk_narrative, soap_cat
							FROM 
								clin.clin_narrative cn 
								JOIN 
								( SELECT Max(modified_when) AS last_modified 
									FROM clin.clin_narrative
									WHERE fk_encounter = %(pk_encounter)s 
									GROUP BY soap_cat
								) latest_soap 
								ON cn.modified_when = latest_soap.last_modified
							WHERE fk_encounter = %(pk_encounter)s"""
		rows, idx = gmPG2.run_ro_queries (queries = [{'cmd': cmd, 'args': {'pk_encounter': pk_encounter}}])
		if len(rows) == 0:
			_log.info(u'%s: No no narratives for pk_encounter = %s' % (__name__, pk_encounter))
			#don't mind, will be initialized with None
		for row in rows:
			soap[row['soap_cat']] = cNarrative(aPK_obj = row['pk_narrative'])
		# fill missing soap_cat
		for soap_cat in soap_categories :
			if not ( soap_cat in soap ) :
				soap[soap_cat] = None
		return soap	

#--------------------------------------------------------
def get_encounter_type_pk(description=u''):
	# suggested place for this function: business/gmEMRStructItems.py
	if description != u'' :
		cmd = u'select pk from clin.encounter_type where description=%s'
		rows, idx = gmPG2.run_ro_queries (queries = [{'cmd': cmd, 'args': [description]}])
		if len(rows) == 0:
			raise gmExceptions.NoSuchBusinessObjectError, 'no encounter type [%s]' % (description)
			return None
		if len(rows) > 1:
			#this should never happen
			raise gmExceptions.NoSuchBusinessObjectError, """multiple encounter types matching [%s], don't know what to choose""" % (description)
		return rows[0][0]
	else:
		return None
#--------------------------------------------------------
def unique_encounters_check(description = u''):
	"""we want some encounter types to be unique within episode"""
	__unique_encounters_list = [
		'in hospital - admission',
		'in hospital - discharge'
		]	#FIXME: this should be stored in backend
	if description in __unique_encounters_list :
		return get_encounter_type_pk(description)
#--------------------------------------------------------
def get_paperwork_template_pk(template_type=u''):
	# suggested place for this function: business/gmForms.py
	# Be careful: it mathes either short or long description.
	# Currently neither short nor long description is UNIQUE:
	#    CONSTRAINT paperwork_templates_name_long_key UNIQUE (name_long, name_short)
	if template_type != u'' :
		cmd = u"""select pk_paperwork_template
			from ref.v_paperwork_templates
			where template_type=%(template_type)s"""
		rows, idx = gmPG2.run_ro_queries (queries = [{'cmd': cmd, 'args': {'template_type': template_type}}])
		if len(rows) == 0:
				raise gmExceptions.NoSuchBusinessObjectError, 'no template [%s]' % (template_type)
		return rows[0][0]
	else:
		return None
#--------------------------------------------------------
def report_display_html(template=None, placeholders_data={}):
	""" Creates new HTML document	based on the template, 
	and replaces placeholders (fields in the template) with supplied data.
	This document is displayed in OpenOffice Writer and can be modified or printed."""
	# suggested place for this function: business/gmForms.py
	# this is slightly rewritten gmFormWidgets.create_new_letter
	# - changed placeholders handling

	if template is None:
		return False
	_report = cFormHtml(template)
	_report.process(placeholders_data)
	_report.preview()
#--------------------------------------------------------
def makeHtmlText(text = u''):
			"""Simple conversion of text.  Create a more powerful version if you need"""
			html_text = text
			html_text = html_text.replace('<', '&lt;')
			html_text = html_text.replace('>', '&gt;')
			html_text = html_text.replace('\n\n','<P>')
			html_text = html_text.replace('\n', '<BR>')
			return html_text
#--------------------------------------------------------
def match_provider_RFE():
	# select 25 most frequently used RFE and sort them alphabetically
	query = u"""
		SELECT reason_for_encounter, reason_for_encounter, reason_for_encounter 
		FROM
			(SELECT reason_for_encounter
			FROM clin.encounter
			WHERE (reason_for_encounter %(fragment_condition)s)
			GROUP BY reason_for_encounter 
			ORDER BY COUNT(reason_for_encounter ) DESC
			LIMIT 25
			) AS temp
		ORDER BY reason_for_encounter"""
	mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
	return mp
#--------------------------------------------------------
def match_provider_AOE():
	# select 25 most frequently used AOE and sort them alphabetically
	query = u"""
		SELECT assessment_of_encounter, assessment_of_encounter, assessment_of_encounter 
		FROM
			(SELECT assessment_of_encounter
			FROM clin.encounter
			WHERE (assessment_of_encounter %(fragment_condition)s)
			GROUP BY assessment_of_encounter 
			ORDER BY COUNT(assessment_of_encounter ) DESC
			LIMIT 25
			) AS temp
		ORDER BY assessment_of_encounter"""
	mp = gmMatchProvider.cMatchProvider_SQL2(queries=query)
	return mp
#================================================================
# display widgets
#================================================================
class cEncounterEditPnl(wxgEncounterEditPnl.wxgEncounterEditPnl, gmRegetMixin.cRegetOnPaintMixin):
	"""Panel for editing detailed operation description. Used as notebook page."""
	# FIXME: dispatcher handling needs thorough check and perhaps rewrite
	# I don't know what gmRegetMixin.cRegetOnPaintMixin is for, so I left it as is.
	def __init__(self, *args, **kwargs):

		wxgEncounterEditPnl.wxgEncounterEditPnl.__init__(self, *args, **kwargs)
		# supply required methods
		self._PhWheel_RFE.matcher = match_provider_RFE()
		self._PhWheel_AOE.matcher = match_provider_AOE()
		for enc_type in  gmEMRStructItems.get_encounter_types() :
			self._CBox_EncounterType.Append( enc_type[0], enc_type[1]) #FIXME: check what happens when translated types are present
		gmRegetMixin.cRegetOnPaintMixin.__init__(self)
		self.__patient = gmPerson.gmCurrentPatient()
		#self._pnl_emr_tree._emr_tree is an object of class gmEMRBrowser.cEMRTree
		#self.__emr = self._pnl_emr_tree._emr_tree
		self.__emr = self._pnl_emr_tree
		self.__cache = {}	# cache of UI field values, set by __set_field_values
		self.__soap = {} # dictionary of cNarrative for current encounter
		self.__soap_narrative = {} # dictionary of narrative fields of cNarrative objects for current encounter
		self.__skip_dispatcher_signal = False	#used within self.save()
		self.__init_ui()
		self.__make_popup_menus()
		#FIXME: set __curr_node to latest encounter
		self.__register_interests()
	# --------------------------------------------------------
	#  event handling
	# --------------------------------------------------------
	def __make_popup_menus(self):

		# - episodes
		self.__epi_context_popup = wx.Menu(title = _('Episode Menu'))

		menu_id = wx.NewId()
		self.__epi_context_popup.AppendItem(wx.MenuItem(self.__epi_context_popup, menu_id, _('Print all progress notes')))
		wx.EVT_MENU(self.__epi_context_popup, menu_id, self.__print_all_progress_notes)
	def __register_interests(self):
		# need help with dispatcher signals
		#gmDispatcher.connect(signal = u'pre_patient_selection', receiver = self._on_pre_patient_selection)
		gmDispatcher.connect(signal = u'post_patient_selection', receiver = self._schedule_data_reget)
		#gmDispatcher.connect(signal = u'test_result_mod_db', receiver = self._schedule_data_reget)
		#gmDispatcher.connect(signal = u'reviewed_test_results_mod_db', receiver = self._schedule_data_reget)
		gmDispatcher.connect(signal = 'episode_mod_db', receiver = self._on_episode_issue_mod_db)
		gmDispatcher.connect(signal = 'health_issue_mod_db', receiver = self._on_episode_issue_mod_db)
		gmDispatcher.send(signal = u'register_pre_exit_callback', callback = self._pre_exit_callback)
		self.__patient.register_pre_selection_callback(callback = self._pre_selection_callback)

		wx.EVT_TREE_SEL_CHANGING (self.__emr, self.__emr.GetId(), self._before_tree_item_selection_changed)
		wx.EVT_TREE_SEL_CHANGED (self.__emr, self.__emr.GetId(), self._on_tree_item_selected)
		wx.EVT_TREE_ITEM_RIGHT_CLICK (self.__emr, self.__emr.GetId(), self._on_tree_item_right_clicked)

	#--------------------------------------------------------
	def _before_tree_item_selection_changed(self, event):
		# try to save data
		if self.save():
			event.Skip()
		else:
			#go back
			event.Veto()
			gmGuiHelpers.gm_show_info(aMessage = _('Either save or discard changes before changing selection.'), aTitle = default_dialog_title)
	#--------------------------------------------------------
	def _on_tree_item_selected(self, event):
		self.__curr_node = event.GetItem()
		self.__show_details_for_selected_node(self.__curr_node)
		node_data = self.__emr.GetPyData(self.__curr_node)
		if isinstance(node_data, gmEMRStructItems.cEpisode):
			self._btn_discharge.Enable(True)
		else:
			self._btn_discharge.Enable(False)
		if isinstance(node_data, cEncounter):
			self._btn_print.Enable(True)
		else:
			self._btn_print.Enable(False)
		return True

	#--------------------------------------------------------
	def _on_tree_item_right_clicked(self, event):
		"""Right button clicked: display the popup for the tree"""

		node = event.GetItem()
		self.__emr.SelectItem(node)
		self.__curr_node = node
		self.__curr_node_data = self.__emr.GetPyData(self.__curr_node)

		pos = wx.DefaultPosition
		if isinstance(self.__curr_node_data, gmEMRStructItems.cEpisode):
			self.__handle_episode_context(pos=pos)
		else:
			pass
		event.Skip()
	def __handle_episode_context(self, pos=wx.DefaultPosition):
			self.__emr.PopupMenu(self.__epi_context_popup, pos)
	def __print_all_progress_notes(self, event):
		template = cFormTemplate(aPK_obj=get_paperwork_template_pk(template_type=print_all_progress_notes))
		_report = cFormXSLT(template)
		_report.process(sql_parameters = {'pkeys': self.__curr_node_data['pk_episode']})
		_report.preview()
	#--------------------------------------------------------
	def _discard_btn_pressed(self, event): # wxGlade: wxgEncounterEditPnl.<event_handler>
		self.__show_details_for_selected_node(self.__curr_node)
	#--------------------------------------------------------
	def _discharge_btn_pressed(self, event): # wxGlade: wxgEncounterEditPnl.<event_handler>
		node_data = self.__emr.GetPyData(self.__curr_node)
		if not isinstance(node_data, gmEMRStructItems.cEpisode):
			gmGuiHelpers.gm_show_info(aMessage = _('Select an episode from the EMR tree to prepare discharge encounter.\n'), aTitle = default_dialog_title)
			return
		if self._is_modified():
			gmGuiHelpers.gm_show_info(aMessage = _('For automatic preparation of discharge encounter all fields must be blank'), aTitle = default_dialog_title)
			return
		# check if there is no other discharge encouter
		cmd = u"""SELECT DISTINCT epi.pk AS episode_pk, enc.pk AS encounter_pk
								 FROM clin.encounter enc
								 JOIN clin.clin_narrative cn ON enc.pk = cn.fk_encounter
								 JOIN clin.episode epi ON cn.fk_episode = epi.pk
								 JOIN clin.encounter_type et ON enc.fk_type = et.pk
							WHERE et.description = %s AND epi.pk = %s
						"""
		rows, idx = gmPG2.run_ro_queries (queries = [{'cmd': cmd, 'args': [encounter_description_discharge, node_data['pk_episode']]}])
		if len(rows) > 0:
			gmGuiHelpers.gm_show_info(aMessage = _('Encounter "'+ encounter_description_discharge + '" already exists for this episode'), aTitle = default_dialog_title)
			return
		# find admission encounter and fetch corresponding narrative
		# cmd remains the same as above, only parameter changes
		rows, idx = gmPG2.run_ro_queries (queries = [{'cmd': cmd, 'args': [encounter_description_admittance, node_data['pk_episode']]}])
		if len(rows) > 1:		# this should never happen
			#FIXME: convert this to raise an error and write to log
			gmGuiHelpers.gm_show_info(aMessage = _('Multiple "' + encounter_description_admittance + '" encounters exists for this episode'), aTitle = default_dialog_title)
			return
		if len(rows) == 0:
			gmGuiHelpers.gm_show_info(aMessage = _('No "' + encounter_description_admittance + '" encounter exists for this episode.\nYou must enter everything manually.'), aTitle = default_dialog_title)
			return
		if len(rows) == 1:	# put initial data into current fields
			self.__soap_admittance = get_latest_soap(pk_encounter = rows[0]['encounter_pk'])
			#set field values directly, to preserve cached (empty) values and trigger update on save
			self._CBox_EncounterType.SetValue(encounter_description_discharge)
			self._PhWheel_AOE.SetText(gmTools.coalesce(node_data['description'], u''))
			self._Txt_Narrative_s.SetValue(gmTools.coalesce(self.__soap_admittance['s']['narrative'], u''))
			self._Txt_Narrative_o.SetValue(gmTools.coalesce(self.__soap_admittance['o']['narrative'], u''))
	#--------------------------------------------------------
	def _print_btn_pressed(self, event): # wxGlade: wxgEncounterEditPnl.<event_handler>
		node_data = self.__emr.GetPyData(self.__curr_node)
		if not isinstance(node_data, cEncounter):
			# cancel print
			gmGuiHelpers.gm_show_info(aMessage = _('Select an encounter from the EMR tree before printing.\nIf you just created new encounter - save it first.'), aTitle = default_dialog_title)
			return
		if self._is_modified():
			if self.save():
				self.__show_details_for_selected_node(self.__curr_node)
					#it works (__curr_node is not changed after save), need to check how
			else:
				# cancel print
				gmGuiHelpers.gm_show_info(aMessage = _('Either save or discard changes before printing.'), aTitle = default_dialog_title)
				return
		self
		if self._CBox_EncounterType.GetClientData(self._CBox_EncounterType.GetSelection()) == encounter_description_admittance:
			template = gmForms.cFormTemplate(aPK_obj=get_paperwork_template_pk(template_type=print_context + encounter_description_admittance))
			#physician = gmPerson.cStaff(aPK_obj=node_data['modified_by'])
			#physician_full_name = '%(firstname_initial)s. %(lastname)s' % {
			#	'lastname': physician['lastnames'],
			#	'firstname_initial': physician['firstnames'][0]
			#	}
			data = {
				'lastname': self.__patient.get_active_name()['lastnames'],
				'firstname': self.__patient.get_active_name()['firstnames'],
				'birth_date': self.__patient['dob'].strftime('%Y-%m-%d'),
				'admittance_date': node_data['started'].strftime('%Y-%m-%d'),
				'narrative_s': self.__soap_narrative['s'],
				'narrative_o': self.__soap_narrative['o'],
				'admitting_physician': u''	#FIXME: now we haven't got it in cEncounter
				}
			#report_display(template=template, placeholders_data=data)
			report_display_html(template=template, placeholders_data=data)
		elif self._CBox_EncounterType.GetClientData(self._CBox_EncounterType.GetSelection()) == encounter_description_discharge:
			template = gmForms.cFormTemplate(aPK_obj=get_paperwork_template_pk(template_type=print_context + encounter_description_discharge))
			# check if there is the date of admission encouter
			cmd = u"""SELECT encounter_started
								FROM clin.v_emr_tree
								WHERE pk_episode = (
									SELECT pk_episode
									FROM clin.v_emr_tree
										WHERE pk_encounter = %s )
											AND
											encounter_l10n_type = %s
							"""
			rows, idx = gmPG2.run_ro_queries (queries = [{'cmd': cmd, 'args': [node_data['pk_encounter'], encounter_description_admittance]}])
			if len(rows) == 1:
				__admittance_date = rows[0][0].strftime('%Y-%m-%d') #FIXME: what if it is Null?
			else:
				__admittance_date = u''
			data = {
				'lastname': self.__patient.get_active_name()['lastnames'],
				'firstname': self.__patient.get_active_name()['firstnames'],
				'birth_date': self.__patient['dob'].strftime('%Y-%m-%d'),
				'admittance_date': __admittance_date,
				'discharge_date': node_data['started'].strftime('%Y-%m-%d'),
				'discharge_diagnosis': self._PhWheel_AOE.GetValue().strip(),
				'discharge_narrative_s': self.__soap_narrative['s'],
				'discharge_narrative_o': self.__soap_narrative['o'],
				'discharge_narrative_a': self.__soap_narrative['a'],
				#FIXME: the following line is an exception to catch list formatting for one template only. 
				#it desperately needs more general solution of preserving formatiing while replacing placeholders
				'discharge_narrative_p': self.__soap_narrative['p'].replace('\n', '<LI>'),
				}
			report_display_xml(template=template, placeholders_data=data)
		elif self._CBox_EncounterType.GetClientData(self._CBox_EncounterType.GetSelection()) == encounter_description_clinic_visit:
			template = cFormTemplate(aPK_obj=get_paperwork_template_pk(template_type=print_context + encounter_description_clinic_visit + '.consultation letter'))
			_report = cFormXSLT(template)
			_report.process(sql_parameters = {'pkeys': node_data['pk_encounter']})
			_report.preview()

		else:
			raise NotImplementedError
	#--------------------------------------------------------
	def _save_btn_pressed(self, event): # wxGlade: wxgOperationPnl.<event_handler>
		if self.save():
			# self.__show_details_for_selected_node(self.__curr_node)
			# ^^^ this is not enough when creating new encounter or episode
			# FIXME: how to get back to the node with recently modified object?
			self.__init_ui()
			self.__show_details_for_selected_node(self.__curr_node)
	#--------------------------------------------------------
	def _on_pre_patient_selection(self):
		wx.CallAfter(self.__on_pre_patient_selection)
	#--------------------------------------------------------
	def __on_pre_patient_selection(self):
		# FIXME: need to implement this
		pass
	#--------------------------------------------------------
	def _pre_exit_callback(self):
		"""The client is about to be shut down.
		Shutdown will not proceed before this returns.
		"""
		self.save()
	#--------------------------------------------------------
	def _on_episode_issue_mod_db(self):
		_log.debug(u'%s: got dispatcher signal - episode or issue was modified' % __name__)
		if not self.__skip_dispatcher_signal:
			self.save()
			self.__init_ui()
	#--------------------------------------------------------
	def _pre_selection_callback(self):
		"""Another patient is about to be activated.

		Patient change will not proceed before this returns.
		"""
		return self.save()

	#--------------------------------------------------------
	def save(self):
		""" returns True if successful, False otherwise"""
		need_save = []
		#FIXME: move _is_modified up a level
		if not self._is_modified():
			_log.debug('%s: data not modified, not saved' % __name__)
			return True
		if not self.__is_valid_for_save():
			_log.error('%s: invalid data, not saved' % __name__)
			return False
		if not gmGuiHelpers.gm_show_question(aMessage=_('Save changes?'), aTitle=default_dialog_title):
			_log.debug('%s: user canceled save operation' % __name__)
			return False

		#OK, we have to save the contents, let's try...
		self.__skip_dispatcher_signal = True	#avoid signals generated by this save
		try:
			#--------------------------------------------------------------------
			#check what objects must be created and create them
			#--------------------------------------------------------------------
			object_data = self.__emr.GetPyData(self.__curr_node)
			#episode = None
			if isinstance(object_data, cEncounter):
				encounter = object_data
				episode = self.__emr.GetPyData(self.__emr.GetItemParent(self.__curr_node))
				#we have encounter, skip all creation procedures
			else:	#must create encounter
				encounter = cEncounter(create_new = True, fk_patient = self.__patient.ID, 
																									enc_type = get_encounter_type_pk(description = self._CBox_EncounterType.GetClientData(self._CBox_EncounterType.GetSelection())))
				_log.info(u'encounter created')
				self.__soap = get_latest_soap(encounter['pk_encounter'])	#this all will be None, it's OK
				if isinstance(object_data, gmEMRStructItems.cEpisode):
					episode = object_data
					#we have encounter and episode now, that's all we need
				else:	#must create new episode, too
					#decide if associated to health issue or not - all we need is pk of HealthIssue
					#if self.__curr_node == self.__emr.GetRootItem() :	#why must I use '==' and not 'is' operator?
						#node is tree root, will create unassociated episode
						#_issue_pk = None
						#go on, objects will be created later
					if isinstance(object_data, gmEMRStructItems.cHealthIssue):
						#create associated episode
						_issue_pk = object_data['pk_health_issue']
					else:
						_issue_pk = None
					#go on, objects will be created later
					#--------------------------------------------------------------------
					#get proposed name for episode (code from gmSOAPWidgets)
					if len(self._PhWheel_AOE.GetValue().strip()) !=  0 :
						epi_name = self._PhWheel_AOE.GetValue().strip()
					else:
						epi_name = self._PhWheel_RFE.GetValue().strip()
					dlg = wx.TextEntryDialog (
						parent = self,
						message = _('Enter a descriptive name for the new episode:'),
						caption = _('Adding a new episode'),
						defaultValue = epi_name.replace('\r', '//').replace('\n', '//'),
						style = wx.OK | wx.CANCEL | wx.CENTRE
						)
					decision = dlg.ShowModal()
					if decision != wx.ID_OK:
						_log.info('%s: user canceled adding new episode' % __name__)
						self.__skip_dispatcher_signal = False
						return False
					epi_name = dlg.GetValue().strip()
					if epi_name == u'':
						gmGuiHelpers.gm_show_error(_('Cannot save a new episode without a name.'), default_dialog_title)
						self.__skip_dispatcher_signal = False
						return False
					#--------------------------------------------------------------------
					#create new episode
					episode = gmEMRStructItems.create_episode (
							pk_health_issue = _issue_pk,
							episode_name = epi_name,
							is_open = False,	#we should deal with this some day
							encounter = encounter['pk_encounter'],
							allow_dupes = True
						)
				#Since we needed to create an encounter at least the _CBox_EncounterType was modified, 
				#so the encounter will be updated in the next step
				#and 'start' and 'last_affirmed' will be set correctly.
				#There will be at least one narrative because __is_valid_for_save passed.
			#--------------------------------------------------------------------
			#now we should have all tree objects existing (created or already present)
			#update object contents
			#--------------------------------------------------------------------
			if self._is_modified_encounter() :
				encounter['reason_for_encounter']= gmTools.none_if(value=self._PhWheel_RFE.GetValue().strip(), none_equivalent=u'')
				encounter['assessment_of_encounter']= gmTools.none_if(value=self._PhWheel_AOE.GetValue().strip(), none_equivalent=u'')
				encounter['pk_type']=get_encounter_type_pk(description = self._CBox_EncounterType.GetClientData(self._CBox_EncounterType.GetSelection()))
				encounter['started']=self._PhWheel_encounter_started.GetData().get_pydt()
				encounter['last_affirmed']= pyDT.datetime.now(tz = gmDateTime.gmCurrentLocalTimezone)
				need_save.append(encounter)
			#check and save each narrative - they are separate objects
			for soap_cat in soap_categories :
					if self._is_modified_narrative(soap_cat = soap_cat) :
						_log.info('%s: narrative_%s modified' % (__name__, soap_cat))
						#cannot simply delete narrative, so if it's empty mark it "### erased ###"
						text_to_update = self.__dict__['_Txt_Narrative_%s' % soap_cat].GetValue().strip()
						if text_to_update == u'':
							text_to_update =  _(u'### erased ###')
						if self.__soap[soap_cat] is None:	#create new cNarrative
							self.__soap[soap_cat] = cNarrative(create_new = True,
																		narrative=text_to_update,
																		soap_cat=soap_cat, 
																		episode_id=episode['pk_episode'], 
																		encounter_id=encounter['pk_encounter'])
						#always update narrative['clin_when']
						narrative = self.__soap[soap_cat]
						narrative['narrative'] = text_to_update
						narrative['clin_when']=self._PhWheel_encounter_started.GetData().get_pydt()
						need_save.append(narrative)
			#--------------------------------------------------------------------
			#update data in backend
			#--------------------------------------------------------------------
			for item in need_save :
				item.update()
			_log.info('%s: data saved' % __name__)
		except:
			#FIXME: should roll back changes, but how?
			#maybe use cached emr, look into gmEMRStructWidgets(?)
			#at least restore data from cache to encounter and narrative objects
			_log.error('%s: could not save data' % __name__)
			raise
			self.__skip_dispatcher_signal = False
			return False
		self.__skip_dispatcher_signal = False
		return True

	#--------------------------------------------------------
	def __is_valid_for_save(self):
		valid = True
		#------------------------------------------------------
		#formal checks
		#------------------------------------------------------
		#check in reverse order, so that the upper-most field finally gets the focus
		if not self._PhWheel_encounter_started.is_valid_timestamp():
			self._PhWheel_encounter_started.SetBackgroundColour('pink')
			self._PhWheel_encounter_started.Refresh()
			self._PhWheel_encounter_started.SetFocus()
			valid = False
		if self._CBox_EncounterType.GetValue().strip() == u'':
			self._CBox_EncounterType.SetBackgroundColour('pink')
			self._CBox_EncounterType.Refresh()
			self._CBox_EncounterType.SetFocus()
			valid = False
		#at least one narrative must exist
		if self._Txt_Narrative_s.GetValue().strip() == u'' and self._Txt_Narrative_o.GetValue().strip() == u'' and self._Txt_Narrative_a.GetValue().strip() == u'' and self._Txt_Narrative_p.GetValue().strip() == u'' :
			valid = False
			gmGuiHelpers.gm_show_error(_('At least one narrative field must be filled.'), default_dialog_title)
			#FIXME: display a message
		#------------------------------------------------------
		#business logic checks
		#------------------------------------------------------
		__t_unique_encounter_check = unique_encounters_check(self._CBox_EncounterType.GetClientData(self._CBox_EncounterType.GetSelection()).strip())
		if __t_unique_encounter_check is not None :
			#check if there is no encounter of the same type within this episode
			if isinstance(self.__emr.GetPyData(self.__curr_node), cEncounter) :
				__t_encounter_pk = self.__emr.GetPyData(self.__curr_node)['pk_encounter']
				__t_episode_pk = self.__emr.GetPyData(self.__emr.GetItemParent(self.__curr_node))['pk_episode']
			elif isinstance(self.__emr.GetPyData(self.__curr_node), gmEMRStructItems.cEpisode) :
				__t_encounter_pk = None
				__t_episode_pk = self.__emr.GetPyData(self.__curr_node)['pk_episode']
			else:
				__t_encounter_pk = None
				__t_episode_pk = None
			if __t_episode_pk is not None : #check only if there is existing episode
				queries = [
					{'cmd': u"""SELECT emr.pk_encounter 
											FROM
												 clin.v_emr_tree emr
												 JOIN
												 clin.encounter enc
												 ON emr.pk_encounter = enc.pk
											WHERE
												 (emr.pk_episode = %(pk_episode)s)
												 AND (enc.fk_type = %(pk_type)s)""",
					 'args': { 'pk_episode' : __t_episode_pk, 'pk_type' : __t_unique_encounter_check }
					}]
				rows, idx = gmPG2.run_ro_queries(queries = queries)
				if (len(rows) != 0) and (rows[0][0] != __t_encounter_pk) :
					#there exists another encounter of the same type, 
					valid = False
					gmGuiHelpers.gm_show_error(_('An episode cannot have multiple encounters of type ') + '"' + self._CBox_EncounterType.GetValue().strip() + '".', default_dialog_title)
		return valid

	#--------------------------------------------------------
	def _is_modified(self):
		# FIXME: replace it with general function/property independent of field names
		# check for data from each object independently
		if self._is_modified_encounter() :
			return True
		for soap_cat in soap_categories :
			if self._is_modified_narrative(soap_cat = soap_cat) :
				return True
		return False
	#--------------------------------------------------------
	def _is_modified_encounter(self):
		if self.__cache['_PhWheel_RFE'] <> self._PhWheel_RFE.GetValue() :
			return True
		if self.__cache['_PhWheel_AOE'] <> self._PhWheel_AOE.GetValue() :
			return True
		if self.__cache['_CBox_EncounterType'] <> self._CBox_EncounterType.GetClientData(self._CBox_EncounterType.GetSelection()) :
			return True
		if self.__cache['_PhWheel_encounter_started'] <> self._PhWheel_encounter_started.GetData().get_pydt() :
			return True
		return False
	#--------------------------------------------------------
	def _is_modified_narrative(self, soap_cat = None):
		if self.__cache['_Txt_Narrative_%s' % soap_cat] <> self.__dict__['_Txt_Narrative_%s' % soap_cat].GetValue().strip() :
			#adding white space will not trigger update, sorry
			return True
		if (self.__cache['_PhWheel_encounter_started'] <> self._PhWheel_encounter_started.GetData().get_pydt() 
			and self.__cache['_Txt_Narrative_%s' % soap_cat]<> u''):
			#if narrative exists we must change clin_when in narrative
			return True
		return False
	#--------------------------------------------------------
	# internal API
	#--------------------------------------------------------
	def __init_ui(self):
		"""Fills UI with data."""
		if not self.__patient.connected:
			#init fields with empty values, filling the cache by the way
			self.__set_field_values()
			return False
		#-----------------------------------------------------------
		# init the EMR tree
		self.__emr.DeleteAllItems()
		root_item = self.__emr.AddRoot(_('%s EMR') % self.__patient['description'])
		self.__emr.SetPyData(root_item, None)
		self.__emr.SetItemHasChildren(root_item, True)
		# get data from backend
		cmd= u'select * from clin.v_emr_tree where pk_patient=%(pat)s'
		rows, idx  = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {'pat': self.__patient.ID}}],	get_col_idx = False)
		if rows is None:
			_log.info('patient [%s] has no EMR data' % self.__patient.ID)
			return True
		# put data into the tree
		self.__populate_tree(self.__emr, rows)
		self.__curr_node = self.__emr.GetRootItem()
		# FIXME: make last episode selected by default
		self.__emr.ExpandAll()
		#-----------------------------------------------------------
		# init details
		#self.__set_field_values()
		self.__show_details_for_selected_node(self.__curr_node)
		return True
	#--------------------------------------------------------
	def __populate_tree(self, tree, data):
		"""populates tree with supplied data
		data must contain pairs of pk and description for issue, episode, and encounter
		tree must be initialized with root node"""
		#emr = self.__patient.get_emr()
		issues = {}
		episodes = {}
		encounters = {}
		root = tree.GetRootItem()
		for row in data:
			if row['pk_issue'] in issues:
				if row['pk_episode'] in episodes:
					if row['pk_encounter'] in encounters:
						#this shoud never happen, duplicates should not be generated in data
						#FIXME: if it does happen, should raise an exception
						_log.error('tree creation error: duplicate encounters')
					else:
						#there may be episodes without encounters, we still need them in the tree
						if (not row['pk_encounter'] is None):
							encounters[row['pk_encounter']] = tree.AppendItem(episodes[row['pk_episode']], row['encounter_started'].strftime('%Y-%m-%d')+': '+row['encounter_l10n_type'])
							tree.SetPyData(encounters[row['pk_encounter']], cEncounter(aPK_obj=row['pk_encounter']))

				else:
					episodes[row['pk_episode']] = tree.AppendItem(issues[row['pk_issue']], gmTools.coalesce(row['episode_description'], u''))
					tree.SetPyData(episodes[row['pk_episode']], gmEMRStructItems.cEpisode(aPK_obj=row['pk_episode']))
					tree.SetItemBold(episodes[row['pk_episode']])
					if not (row['pk_encounter'] is None):
						encounters[row['pk_encounter']] = tree.AppendItem(episodes[row['pk_episode']], row['encounter_started'].strftime('%Y-%m-%d')+': '+row['encounter_l10n_type'])
						tree.SetPyData(encounters[row['pk_encounter']], cEncounter(aPK_obj=row['pk_encounter']))
			else:
				if row['pk_issue']is None:
					issues[row['pk_issue']] = tree.AppendItem(root, _('Unattributed episodes'))
					tree.SetPyData(issues[row['pk_issue']], {'description': _('Unattributed episodes'), 'pk': None})
				else:
					issues[row['pk_issue']] = tree.AppendItem(root, gmTools.coalesce(row['issue_description'], u''))
					tree.SetPyData(issues[row['pk_issue']], gmEMRStructItems.cHealthIssue(aPK_obj=row['pk_issue']))
				episodes[row['pk_episode']] = tree.AppendItem(issues[row['pk_issue']], gmTools.coalesce(row['episode_description'], u''))
				tree.SetPyData(episodes[row['pk_episode']], gmEMRStructItems.cEpisode(aPK_obj=row['pk_episode']))
				tree.SetItemBold(episodes[row['pk_episode']])
				if not (row['pk_encounter'] is None):
						encounters[row['pk_encounter']] = tree.AppendItem(episodes[row['pk_episode']], row['encounter_started'].strftime('%Y-%m-%d')+': '+row['encounter_l10n_type'])
						tree.SetPyData(encounters[row['pk_encounter']], cEncounter(aPK_obj=row['pk_encounter']))
		return tree
	#--------------------------------------------------------
	def __show_details_for_selected_node(self, node = None):
		"""If selected node is an encounter, displays detailed information and corresponding narrative"""
		if node is None:
			node = self.__curr_node	#FIXME: how to make this default in the definition line?
		node_data = self.__emr.GetPyData(node)
		# update displayed text
		if isinstance(node_data, cEncounter):
			self.__soap = get_latest_soap(pk_encounter = node_data['pk_encounter'])
			# get narratives from cNarrative objects(if they exist)
			for soap_cat in self.__soap.keys() :
				if self.__soap[soap_cat] is None:
					self.__soap_narrative[soap_cat] = u''
				else:
					self.__soap_narrative[soap_cat] = self.__soap[soap_cat]['narrative']
			self.__set_field_values(
				encounter_type = node_data['l10n_type'],
				encounter_RFE = node_data['reason_for_encounter'],
				encounter_AOE = node_data['assessment_of_encounter'],
				encounter_started = node_data['started'],
				narrative_s = self.__soap_narrative['s'],
				narrative_o = self.__soap_narrative['o'],
				narrative_a = self.__soap_narrative['a'],
				narrative_p = self.__soap_narrative['p']
				)
		else:
			#node is root (patient?) , or health issue, or episode, nothing to display
			self.__set_field_values()
	#--------------------------------------------------------
	def __set_field_values(self, encounter_type = u'', encounter_RFE = None, encounter_AOE = None, encounter_started = pyDT.datetime.today(),
					narrative_s = '', narrative_o = '', narrative_a = '', narrative_p = ''):
		"""Sets values of all fields, showing details of encounter and corresponding narratives."""
		self._PhWheel_RFE.SetText(gmTools.coalesce(encounter_RFE, u''))
		self._PhWheel_AOE.SetText(gmTools.coalesce(encounter_AOE, u''))
		if encounter_type is None:
			#FIXME: raise an error
			pass
		else:
			self._CBox_EncounterType.SetValue(encounter_type)
		self._PhWheel_encounter_started.SetText(encounter_started.strftime('%Y-%m-%d'), encounter_started)
		self._Txt_Narrative_s.SetValue(gmTools.coalesce(narrative_s, u''))
		self._Txt_Narrative_o.SetValue(gmTools.coalesce(narrative_o, u''))
		self._Txt_Narrative_a.SetValue(gmTools.coalesce(narrative_a, u''))
		self._Txt_Narrative_p.SetValue(gmTools.coalesce(narrative_p, u''))
		# store current values in cache, for later checking if something was modified or restoring previous contents
		self.__cache['_PhWheel_RFE']=self._PhWheel_RFE.GetValue()
		self.__cache['_PhWheel_AOE']=self._PhWheel_AOE.GetValue()
		self.__cache['_CBox_EncounterType']=self._CBox_EncounterType.GetClientData(self._CBox_EncounterType.GetSelection())
		self.__cache['_PhWheel_encounter_started']=self._PhWheel_encounter_started.GetData().get_pydt()
		self.__cache['_Txt_Narrative_s']=self._Txt_Narrative_s.GetValue()
		self.__cache['_Txt_Narrative_o']=self._Txt_Narrative_o.GetValue()
		self.__cache['_Txt_Narrative_a']=self._Txt_Narrative_a.GetValue()
		self.__cache['_Txt_Narrative_p']=self._Txt_Narrative_p.GetValue()
	#--------------------------------------------------------
	# reget mixin API
	#--------------------------------------------------------
	def _populate_with_data(self):
		"""Populate fields with data."""
		#pat = gmPerson.gmCurrentPatient()
		patient = self.__patient
		if patient.connected:
			self.__init_ui()
			return True
		else:
			_log.error('[_populate_with_data]: no patient do display...')
		return False
#================================================================
# main
#----------------------------------------------------------------
if __name__ == "__main__":
	print "no test code"
	# but it can be tested using gmEncounterEditPlugin

#================================================================
# $Log: gmEncounterEditWidgets.py,v $
# Revision 2.2  Fri May 02 22:10:13 CEST 2013 @13 /Internet Time/ jl
# - minor editions to catch up with current version of Gnumed
# Revision 2.1.1  Thu Aug 20 00:19:19 CEST 2009 @13 /Internet Time/ jl
# - changed for Leo IDE
# Revision 1.1  Tue Sep 09 01:19:09 CEST 2008 @13 /Internet Time/ jl
# - first public release: widgets for adding and editing encounter, based on progress note plugin by Karsten Hilbert, Sebastian Hilbert and Carlos Moro
