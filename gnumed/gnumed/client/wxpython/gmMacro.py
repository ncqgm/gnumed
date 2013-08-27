#  coding: utf8
"""GNUmed macro primitives.

This module implements functions a macro can legally use.
"""
#=====================================================================
__author__ = "K.Hilbert <karsten.hilbert@gmx.net>"

import sys
import time
import random
import types
import logging
import os
import codecs


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmI18N
if __name__ == '__main__':
	gmI18N.activate_locale()
	gmI18N.install_domain()
from Gnumed.pycommon import gmGuiBroker
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmBorg
from Gnumed.pycommon import gmExceptions
from Gnumed.pycommon import gmCfg2
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmMimeLib

from Gnumed.business import gmPerson
from Gnumed.business import gmStaff
from Gnumed.business import gmDemographicRecord
from Gnumed.business import gmMedication
from Gnumed.business import gmPathLab
from Gnumed.business import gmPersonSearch
from Gnumed.business import gmVaccination
from Gnumed.business import gmKeywordExpansion
from Gnumed.business import gmPraxis

from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmNarrativeWidgets
from Gnumed.wxpython import gmPatSearchWidgets
from Gnumed.wxpython import gmPersonContactWidgets
from Gnumed.wxpython import gmPlugin
from Gnumed.wxpython import gmEMRStructWidgets
from Gnumed.wxpython import gmListWidgets
from Gnumed.wxpython import gmDemographicsWidgets
from Gnumed.wxpython import gmDocumentWidgets
from Gnumed.wxpython import gmKeywordExpansionWidgets
from Gnumed.wxpython import gmPraxisWidgets


_log = logging.getLogger('gm.scripting')
_cfg = gmCfg2.gmCfgData()

#=====================================================================
# values for the following placeholders must be injected from the outside before
# using them, in use they must conform to the "placeholder::::max length" syntax,
# as long as they resolve to None they return their respective names so the
# developers can know which placeholder was not set
_injectable_placeholders = {
	u'form_name_long': None,
	u'form_name_short': None,
	u'form_version': None
}


# the following must satisfy the pattern "$<name::args::(optional) max string length>$" when used
known_variant_placeholders = [
	# generic:
	u'free_text',							# show a dialog for entering some free text
											# args: <message> shown in input dialog, must not contain "//" or "::"
	u'text_snippet',						# a text snippet, taken from the keyword expansion mechanism
											# args: <snippet name>//<template>
	u'data_snippet',						# a binary snippet, taken from the keyword expansion mechanism
											# args: <snippet name>//<template>//<optional target mime type>//<optional target extension>
											# returns full path to an exported copy of the
											# data rather than the data itself,
											#	template: string template for outputting the path
											#	target mime type: a mime type into which to convert the image, no conversion if not given
											#	target extension: target file name extension, derived from target mime type if not given
	u'tex_escape',							# "args" holds: string to escape
	u'today',								# "args" holds: strftime format
	u'gender_mapper',						# "args" holds: <value when person is male> // <is female> // <is other>
											#				eg. "male//female//other"
											#				or: "Lieber Patient//Liebe Patientin"
	u'client_version',						# the version of the current client as a string (no "v" in front)

	# patient demographics:
	u'name',								# args: template for name parts arrangement
	u'date_of_birth',						# args: strftime date/time format directive

	u'patient_address',						# args: <type of address>//<optional formatting template>
	u'adr_street',							# args: <type of address>
	u'adr_number',
	u'adr_subunit',
	u'adr_location',
	u'adr_suburb',
	u'adr_postcode',
	u'adr_region',
	u'adr_country',

	u'patient_comm',						# args: <comm channel type as per database>//<%(key)s-template>
	u'patient_tags',						# "args" holds: <%(key)s-template>//<separator>
#	u'patient_tags_table',					# "args" holds: no args

	u'patient_photo',						# args: <template>//<optional target mime type>//<optional target extension>
											# returns full path to an exported copy of the
											# image rather than the image data itself,
											# returns u'' if no mugshot available,
											#	template: string template for outputting the path
											#	target mime type: a mime type into which to convert the image, no conversion if not given
											#	target extension: target file name extension, derived from target mime type if not given

	u'external_id',							# args: <type of ID>//<issuer of ID>


	# clinical record related:
	u'soap',
	u'soap_s',
	u'soap_o',
	u'soap_a',
	u'soap_p',
	u'soap_u',
	u'soap_admin',							# get all or subset of SOAPU/ADMIN, no template in args needed
	u'progress_notes',						# "args" holds: categories//template
											# 	categories: string with 'soapu '; ' ' == None == admin
											#	template:	u'something %s something'		(do not include // in template !)

	u'soap_for_encounters',					# lets the user select a list of encounters for which
											# LaTeX formatted progress notes are emitted:
											# "args": soap categories // strftime date format

	u'soap_by_issue',						# lets the user select a list of issues and
											# then SOAP entries from those issues
											# "args": soap categories // strftime date format // template

	u'soap_by_episode',						# lets the user select a list of issues and
											# then SOAP entries from those issues
											# "args": soap categories // strftime date format // template

	u'emr_journal',							# "args" format:   <categories>//<template>//<line length>//<time range>//<target format>
											#	categories:	   string with any of "s", "o", "a", "p", "u", " ";
											#				   (" " == None == admin category)
											#	template:	   something %s something else
											#				   (Do not include // in the template !)
											#	line length:   the maximum length of individual lines, not the total placeholder length
											#	time range:		the number of weeks going back in time if given as a single number,
											#					or else it must be a valid PostgreSQL interval definition (w/o the ::interval)
											#	target format: "tex" or anything else, if "tex", data will be tex-escaped	(currently only "latex")

	u'current_meds',						# "args" holds: line template//<select>
											#	<select>: if this is present the user will be asked which meds to export
	u'current_meds_for_rx',					# formats substance intakes either by substance (non-brand intakes or by
											# brand (once per brand intake, even if multi-component)
											# args: <line template>
											#	<line_template>: template into which to insert each intake, keys from
											#	                 clin.v_substance_intakes, special additional keys:
											#	                 %(contains)s -- list of components
											#	                 %(amount2dispense)s -- how much/many to dispense
	u'current_meds_table',					# "args" holds: format, options
	u'current_meds_notes',					# "args" holds: format, options

	u'lab_table',							# "args" holds: format (currently "latex" only)
	u'test_results',						# "args":			<%(key)s-template>//<date format>//<line separator (EOL)>

	u'latest_vaccs_table',					# "args" holds: format, options
	u'vaccination_history',					# "args": <%(key)s-template//date format> to format one vaccination per line

	u'allergy_state',						# args: no args needed
	u'allergies',							# "args" holds: line template, one allergy per line
	u'allergy_list',						# "args" holds: template per allergy, allergies on one line
	u'problems',							# "args" holds: line template, one problem per line
	u'PHX',									# Past medical HiXtory, "args" holds: line template//separator//strftime date format//escape style (latex, currently)
	u'encounter_list',						# "args" holds: per-encounter template, each ends up on one line

	u'documents',							# "args" format:	<select>//<description>//<template>//<path template>//<path>
											#	select:			let user select which documents to include,
											#					optional, if not given: all documents included
											#	description:	whether to include descriptions, optional
											#	template:		something %(field)s something else,
											#					(do not include "//" itself in the template),
											#	path template:	the template for outputting the path to exported
											#					copies of the document pages, if not given no pages
											#					are exported, this template can contain "%(name)s"
											#					and/or "%(fullpath)s" which is replaced by the
											#					appropriate value for each exported file
											#	path:			into which path to export copies of the document pages,
											#					temp dir if not given

	u'reminders',							# "args":			<template>//<date format>
											#	template:		something %(field)s something else,
											#					(do not include "//" itself in the template)

	# provider related:
	u'current_provider',					# args: no args needed
	u'current_provider_external_id',		# args: <type of ID>//<issuer of ID>
	u'primary_praxis_provider',				# primary provider for current patient in this praxis
	u'primary_praxis_provider_external_id',	# args: <type of ID>//<issuer of ID>

	# praxis related:
	u'praxis',								# args: <template>//select
											#	template:		something %(field)s something else,
											#					(do not include "//" itself in the template),
											#	select:			if this is present allow selection of the
											#					branch rather than using the current branch
	u'praxis_address',						# args: <optional formatting template>

	# billing related:
	u'bill',								# args: template for string replacement
	u'bill_item'							# args: template for string replacement
]

# http://help.libreoffice.org/Common/List_of_Regular_Expressions
# except that OOo cannot be non-greedy |-(
#default_placeholder_regex = r'\$<.+?>\$'				# previous working placeholder
	# regex logic:
	# starts with "$"
	# followed by "<"
	# followed by > 0 characters but NOT "<" but ONLY up to the NEXT ":"
	# followed by "::"
	# followed by any number of characters  but ONLY up to the NEXT ":"
	# followed by "::"
	# followed by any number of numbers
	# followed by ">"
	# followed by "$"
default_placeholder_regex = r'\$<[^<:]+::.*?::\d*?>\$'		# this one works [except that OOo cannot be non-greedy |-(    ]
first_order_placeholder_regex =   r'\$<<<[^<:]+?::.*::\d*?>>>\$'
second_order_placeholder_regex = r'\$<<[^<:]+?::.*::\d*?>>\$'
third_order_placeholder_regex =  r'\$<[^<:]+::.*?::\d*?>\$'


#default_placeholder_regex = r'\$<(?:(?!\$<).)+>\$'		# non-greedy equivalent, uses lookahead (but not supported by LO either |-o  )

default_placeholder_start = u'$<'
default_placeholder_end = u'>$'
#=====================================================================
def show_placeholders():
	fname = gmTools.get_unique_filename(prefix = 'gm-placeholders-', suffix = '.txt')
	ph_file = codecs.open(filename = fname, mode = 'wb', encoding = 'utf8', errors = 'replace')

	ph_file.write(u'Here you can find some more documentation on placeholder use:\n')
	ph_file.write(u'\n http://wiki.gnumed.de/bin/view/Gnumed/GmManualLettersForms\n\n\n')

	ph_file.write(u'Variable placeholders (use like: $<PLACEHOLDER_NAME::ARGUMENTS::MAX OUTPUT LENGTH>$):\n')
	for ph in known_variant_placeholders:
		ph_file.write(u' %s\n' % ph)
	ph_file.write(u'\n')

	ph_file.write(u'Injectable placeholders (use like: $<PLACEHOLDER_NAME::ARGUMENTS::MAX OUTPUT LENGTH>$):\n')
	for ph in _injectable_placeholders:
		ph_file.write(u' %s\n' % ph)
	ph_file.write(u'\n')

	ph_file.close()
	gmMimeLib.call_viewer_on_file(aFile = fname, block = False)
#=====================================================================
class gmPlaceholderHandler(gmBorg.cBorg):
	"""Returns values for placeholders.

	- patient related placeholders operate on the currently active patient
	- is passed to the forms handling code, for example

	Return values when .debug is False:
	- errors with placeholders return None
	- placeholders failing to resolve to a value return an empty string

	Return values when .debug is True:
	- errors with placeholders return an error string
	- placeholders failing to resolve to a value return a warning string

	There are several types of placeholders:

	injectable placeholders
		- they must be set up before use by set_placeholder()
		- they should be removed after use by unset_placeholder()
		- the syntax is like extended static placeholders
		- they are listed in _injectable_placeholders

	variant placeholders
		- those are listed in known_variant_placeholders
		- they are parsed into placeholder, data, and maximum length
		- the length is optional
		- data is passed to the handler

	Note that this cannot be called from a non-gui thread unless
	wrapped in wx.CallAfter().
	"""
	def __init__(self, *args, **kwargs):

		self.pat = gmPerson.gmCurrentPatient()
		self.debug = False

		self.invalid_placeholder_template = _('invalid placeholder >>>>>%s<<<<<')

		self.__cache = {}

		self.__esc_style = None
		self.__esc_func = lambda x:x
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def set_placeholder(self, key=None, value=None):
		_injectable_placeholders[key]
		_injectable_placeholders[key] = value
	#--------------------------------------------------------
	def unset_placeholder(self, key=None):
		_injectable_placeholders[key]
		_injectable_placeholders[key] = None
	#--------------------------------------------------------
	def set_cache_value(self, key=None, value=None):
		self.__cache[key] = value
	#--------------------------------------------------------
	def unset_cache_value(self, key=None):
		del self.__cache[key]
	#--------------------------------------------------------
	def _set_escape_style(self, escape_style=None):
		self.__esc_style = escape_style
		return

	escape_style = property(lambda x:x, _set_escape_style)
	#--------------------------------------------------------
	def _set_escape_function(self, escape_function=None):
		if escape_function is None:
			self.__esc_func = lambda x:x
			return
		if not callable(escape_function):
			raise ValueError(u'[%s._set_escape_function]: <%s> not callable' % (self.__class__.__name__, escape_function))
		self.__esc_func = escape_function
		return

	escape_function = property(lambda x:x, _set_escape_function)
	#--------------------------------------------------------
	placeholder_regex = property(lambda x: default_placeholder_regex, lambda x:x)

	first_order_placeholder_regex = property(lambda x: first_order_placeholder_regex, lambda x:x)
	second_order_placeholder_regex = property(lambda x: second_order_placeholder_regex, lambda x:x)
	third_order_placeholder_regex = property(lambda x: third_order_placeholder_regex, lambda x:x)
	#--------------------------------------------------------
	# __getitem__ API
	#--------------------------------------------------------
	def __getitem__(self, placeholder):
		"""Map self['placeholder'] to self.placeholder.

		This is useful for replacing placeholders parsed out
		of documents as strings.

		Unknown/invalid placeholders still deliver a result but
		it will be glaringly obvious if debugging is enabled.
		"""
		_log.debug('replacing [%s]', placeholder)

		original_placeholder = placeholder

		# remove leading/trailing '$<(<<)' and '(>>)>$'
		if placeholder.startswith(default_placeholder_start):
			placeholder = placeholder.lstrip('$').lstrip('<')
			if placeholder.endswith(default_placeholder_end):
				placeholder = placeholder.rstrip('$').rstrip('>')
			else:
				_log.error('placeholder must either start with [%s] and end with [%s] or neither of both', default_placeholder_start, default_placeholder_end)
				if self.debug:
					return self._escape(self.invalid_placeholder_template % original_placeholder)
				return None

		# injectable placeholder ?
		parts = placeholder.split('::::', 1)
		if len(parts) == 2:
			name, lng = parts
			is_an_injectable = True
			try:
				val = _injectable_placeholders[name]
			except KeyError:
				is_an_injectable = False
			except:
				_log.exception('injectable placeholder handling error: %s', original_placeholder)
				if self.debug:
					return self._escape(self.invalid_placeholder_template % original_placeholder)
				return None
			if is_an_injectable:
				if val is None:
					if self.debug:
						return self._escape(u'injectable placeholder [%s]: no value available' % name)
					return placeholder
				try:
					lng = int(lng.strip())
				except (TypeError, ValueError):
					lng = len(val)
				return val[:lng]

		# variable placeholders
		if len(placeholder.split('::', 2)) < 3:
			_log.error('invalid placeholder structure: %s', original_placeholder)
			if self.debug:
				return self._escape(self.invalid_placeholder_template % original_placeholder)
			return None

		name, data = placeholder.split('::', 1)
		data, lng_str = data.rsplit('::', 1)
		_log.debug('placeholder parts: name=[%s]; length=[%s]; options=>>>%s<<<', name, lng_str, data)
		try:
			lng = int(lng_str.strip())
		except (TypeError, ValueError):
			lng = None

		handler = getattr(self, '_get_variant_%s' % name, None)
		if handler is None:
			_log.warning('no handler <_get_variant_%s> for placeholder %s', name, original_placeholder)
			if self.debug:
				return self._escape(self.invalid_placeholder_template % original_placeholder)
			return None

		try:
			if lng is None:
				return handler(data = data)
			return handler(data = data)[:lng]
		except:
			_log.exception('placeholder handling error: %s', original_placeholder)
			if self.debug:
				return self._escape(self.invalid_placeholder_template % original_placeholder)
			return None

		_log.error('something went wrong, should never get here')
		return None
	#--------------------------------------------------------
	# placeholder handlers
	#--------------------------------------------------------
	def _get_variant_client_version(self, data=None):
		return self._escape (
			gmTools.coalesce (
				_cfg.get(option = u'client_version'),
				u'%s' % self.__class__.__name__
			)
		)
	#--------------------------------------------------------
	def _get_variant_reminders(self, data=None):

		from Gnumed.wxpython import gmProviderInboxWidgets

		template = _('due %(due_date)s: %(comment)s (%(interval_due)s)')
		date_format = '%Y %b %d'

		data_parts = data.split('//')

		if len(data_parts) > 0:
			if data_parts[0].strip() != u'':
				template = data_parts[0]

		if len(data_parts) > 1:
			if data_parts[1].strip() != u'':
				date_format = data_parts[1]

		reminders = gmProviderInboxWidgets.manage_reminders(patient = self.pat.ID)

		if reminders is None:
			return u''

		if len(reminders) == 0:
			return u''

		lines = [ template % r.fields_as_dict(date_format = date_format, escape_style = self.__esc_style) for r in reminders ]

		return u'\n'.join(lines)
	#--------------------------------------------------------
	def _get_variant_documents(self, data=None):

		select = False
		include_descriptions = False
		template = u'%s'
		path_template = None
		export_path = None

		data_parts = data.split('//')

		if u'select' in data_parts:
			select = True
			data_parts.remove(u'select')

		if u'description' in data_parts:
			include_descriptions = True
			data_parts.remove(u'description')

		template = data_parts[0]

		if len(data_parts) > 1:
			path_template = data_parts[1]

		if len(data_parts) > 2:
			export_path = data_parts[2]

		# create path
		if export_path is not None:
			export_path = os.path.normcase(os.path.expanduser(export_path))
			gmTools.mkdir(export_path)

		# select docs
		if select:
			docs = gmDocumentWidgets.manage_documents(msg = _('Select the patient documents to reference from the new document.'), single_selection = False)
		else:
			docs = self.pat.document_folder.documents

		if docs is None:
			return u''

		lines = []
		for doc in docs:
			lines.append(template % doc.fields_as_dict(date_format = '%Y %b %d', escape_style = self.__esc_style))
			if include_descriptions:
				for desc in doc.get_descriptions(max_lng = None):
					lines.append(self._escape(desc['text'] + u'\n'))
			if path_template is not None:
				for part_name in doc.export_parts_to_files(export_dir = export_path):
					path, name = os.path.split(part_name)
					lines.append(path_template % {'fullpath': part_name, 'name': name})

		return u'\n'.join(lines)
	#--------------------------------------------------------
	def _get_variant_encounter_list(self, data=None):

		encounters = gmEMRStructWidgets.select_encounters(single_selection = False)
		if not encounters:
			return u''

		template = data

		lines = []
		for enc in encounters:
			try:
				lines.append(template % enc.fields_as_dict(date_format = '%Y %b %d', escape_style = self.__esc_style))
			except:
				lines.append(u'error formatting encounter')
				_log.exception('problem formatting encounter list')
				_log.error('template: %s', template)
				_log.error('encounter: %s', encounter)

		return u'\n'.join(lines)
	#--------------------------------------------------------
	def _get_variant_soap_for_encounters(self, data=None):
		"""Select encounters from list and format SOAP thereof.

		data: soap_cats (' ' -> None -> admin) // date format
		"""
		# defaults
		cats = None
		date_format = None

		if data is not None:
			data_parts = data.split('//')

			# part[0]: categories
			if len(data_parts[0]) > 0:
				cats = []
				if u' ' in data_parts[0]:
					cats.append(None)
					data_parts[0] = data_parts[0].replace(u' ', u'')
				cats.extend(list(data_parts[0]))

			# part[1]: date format
			if len(data_parts) > 1:
				if len(data_parts[1]) > 0:
					date_format = data_parts[1]

		encounters = gmEMRStructWidgets.select_encounters(single_selection = False)
		if not encounters:
			return u''

		chunks = []
		for enc in encounters:
			chunks.append(enc.format_latex (
				date_format = date_format,
				soap_cats = cats,
				soap_order = u'soap_rank, date'
			))

		return u''.join(chunks)
	#--------------------------------------------------------
	def _get_variant_emr_journal(self, data=None):
		# default: all categories, neutral template
		cats = list(u'soapu')
		cats.append(None)
		template = u'%s'
		interactive = True
		line_length = 9999
		target_format = None
		time_range = None

		if data is not None:
			data_parts = data.split('//')

			# part[0]: categories
			cats = []
			# ' ' -> None == admin
			for c in list(data_parts[0]):
				if c == u' ':
					c = None
				cats.append(c)
			# '' -> SOAP + None
			if cats == u'':
				cats = list(u'soapu').append(None)

			# part[1]: template
			if len(data_parts) > 1:
				template = data_parts[1]

			# part[2]: line length
			if len(data_parts) > 2:
				try:
					line_length = int(data_parts[2])
				except:
					line_length = 9999

			# part[3]: weeks going back in time
			if len(data_parts) > 3:
				try:
					time_range = 7 * int(data_parts[3])
				except:
					#time_range = None			# infinite
					# pass on literally, meaning it must be a valid PG interval string
					time_range = data_parts[3]

			# part[4]: output format
			if len(data_parts) > 4:
				target_format = data_parts[4]

		# FIXME: will need to be a generator later on
		narr = self.pat.emr.get_as_journal(soap_cats = cats, time_range = time_range)

		if len(narr) == 0:
			return u''

		keys = narr[0].keys()
		lines = []
		line_dict = {}
		for n in narr:
			for key in keys:
				if isinstance(n[key], basestring):
					line_dict[key] = self._escape(text = n[key])
					continue
				line_dict[key] = n[key]
			try:
				lines.append((template % line_dict)[:line_length])
			except KeyError:
				return u'invalid key in template [%s], valid keys: %s]' % (template, str(keys))

		return u'\n'.join(lines)
	#--------------------------------------------------------
	def _get_variant_soap_by_issue(self, data=None):
		return self.__get_variant_soap_by_issue_or_episode(data = data, mode = u'issue')
	#--------------------------------------------------------
	def _get_variant_soap_by_episode(self, data=None):
		return self.__get_variant_soap_by_issue_or_episode(data = data, mode = u'episode')
	#--------------------------------------------------------
	def __get_variant_soap_by_issue_or_episode(self, data=None, mode=None):

		# default: all categories, neutral template
		cats = list(u'soapu')
		cats.append(None)

		date_format = None
		template = u'%s'

		if data is not None:
			data_parts = data.split('//')

			# part[0]: categories
			if len(data_parts[0]) > 0:
				cats = []
				if u' ' in data_parts[0]:
					cats.append(None)
				cats.extend(list(data_parts[0].replace(u' ', u'')))

			# part[1]: date format
			if len(data_parts) > 1:
				if len(data_parts[1]) > 0:
					date_format = data_parts[1]

			# part[2]: template
			if len(data_parts) > 2:
				if len(data_parts[2]) > 0:
					template = data_parts[2]

		if mode == u'issue':
			narr = gmNarrativeWidgets.select_narrative_by_issue(soap_cats = cats)
		else:
			narr = gmNarrativeWidgets.select_narrative_by_episode(soap_cats = cats)

		if narr is None:
			return u''

		if len(narr) == 0:
			return u''

		try:
			narr = [ template % n.fields_as_dict(date_format = date_format, escape_style = self.__esc_style) for n in narr ]
		except KeyError:
			return u'invalid key in template [%s], valid keys: %s]' % (template, str(narr[0].keys()))

		return u'\n'.join(narr)
	#--------------------------------------------------------
	def _get_variant_progress_notes(self, data=None):
		return self._get_variant_soap(data = data)
	#--------------------------------------------------------
	def _get_variant_soap_s(self, data=None):
		return self._get_variant_soap(data = u's')
	#--------------------------------------------------------
	def _get_variant_soap_o(self, data=None):
		return self._get_variant_soap(data = u'o')
	#--------------------------------------------------------
	def _get_variant_soap_a(self, data=None):
		return self._get_variant_soap(data = u'a')
	#--------------------------------------------------------
	def _get_variant_soap_p(self, data=None):
		return self._get_variant_soap(data = u'p')
	#--------------------------------------------------------
	def _get_variant_soap_u(self, data=None):
		return self._get_variant_soap(data = u'u')
	#--------------------------------------------------------
	def _get_variant_soap_admin(self, data=None):
		return self._get_variant_soap(data = u' ')
	#--------------------------------------------------------
	def _get_variant_soap(self, data=None):

		# default: all categories, neutral template
		cats = list(u'soapu')
		cats.append(None)
		template = u'%(narrative)s'

		if data is not None:
			data_parts = data.split('//')

			# part[0]: categories
			cats = []
			# ' ' -> None == admin
			for cat in list(data_parts[0]):
				if cat == u' ':
					cat = None
				cats.append(cat)
			# '' -> SOAP + None
			if cats == u'':
				cats = list(u'soapu')
				cats.append(None)

			# part[1]: template
			if len(data_parts) > 1:
				template = data_parts[1]

		narr = gmNarrativeWidgets.select_narrative_from_episodes(soap_cats = cats)

		if narr is None:
			return u''

		if len(narr) == 0:
			return u''

		# if any "%s" is in the template there cannot be any %(key)s
		# and we also restrict the fields to .narrative (this is the
		# old placeholder behaviour
		if u'%s' in template:
			narr = [ self._escape(n['narrative']) for n in narr ]
		else:
			narr = [ n.fields_as_dict(escape_style = self.__esc_style) for n in narr ]

		try:
			narr = [ template % n for n in narr ]
		except KeyError:
			return u'invalid key in template [%s], valid keys: %s]' % (template, str(narr[0].keys()))
		except TypeError:
			return u'cannot mix "%%s" and "%%(key)s" in template [%s]' % template

		return u'\n'.join(narr)
	#--------------------------------------------------------
	def _get_variant_title(self, data=None):
		return self._get_variant_name(data = u'%(title)s')
	#--------------------------------------------------------
	def _get_variant_firstname(self, data=None):
		return self._get_variant_name(data = u'%(firstnames)s')
	#--------------------------------------------------------
	def _get_variant_lastname(self, data=None):
		return self._get_variant_name(data = u'%(lastnames)s')
	#--------------------------------------------------------
	def _get_variant_name(self, data=None):
		if data is None:
			return [_('template is missing')]

		name = self.pat.get_active_name()

		parts = {
			'title': self._escape(gmTools.coalesce(name['title'], u'')),
			'firstnames': self._escape(name['firstnames']),
			'lastnames': self._escape(name['lastnames']),
			'preferred': self._escape(gmTools.coalesce (
				initial = name['preferred'],
				instead = u' ',
				template_initial = u' "%s" '
			))
		}

		return data % parts
	#--------------------------------------------------------
	def _get_variant_date_of_birth(self, data='%Y %b %d'):
		return self.pat.get_formatted_dob(format = str(data), encoding = gmI18N.get_encoding())
	#--------------------------------------------------------
	# FIXME: extend to all supported genders
	def _get_variant_gender_mapper(self, data='male//female//other'):

		values = data.split('//', 2)

		if len(values) == 2:
			male_value, female_value = values
			other_value = u'<unkown gender>'
		elif len(values) == 3:
			male_value, female_value, other_value = values
		else:
			return _('invalid gender mapping layout: [%s]') % data

		if self.pat['gender'] == u'm':
			return self._escape(male_value)

		if self.pat['gender'] == u'f':
			return self._escape(female_value)

		return self._escape(other_value)
	#--------------------------------------------------------
	# address related placeholders
	#--------------------------------------------------------
	def _get_variant_patient_address(self, data=u''):

		data_parts = data.split(u'//')

		# address type
		adr_type = data_parts[0].strip()
		orig_type = adr_type
		if adr_type != u'':
			adrs = self.pat.get_addresses(address_type = adr_type)
			if len(adrs) == 0:
				_log.warning('no address for type [%s]', adr_type)
				adr_type = u''
		if adr_type == u'':
			_log.debug('asking user for address type')
			adr = gmPersonContactWidgets.select_address(missing = orig_type, person = self.pat)
			if adr is None:
				if self.debug:
					return _('no address type replacement selected')
				return u''
			adr_type = adr['address_type']
		adr = self.pat.get_addresses(address_type = adr_type)[0]

		# formatting template
		template = _('%(street)s %(number)s, %(postcode)s %(urb)s, %(l10n_state)s, %(l10n_country)s')
		if len(data_parts) > 1:
			if data_parts[1].strip() != u'':
				template = data_parts[1]

		try:
			return template % adr.fields_as_dict(escape_style = self.__esc_style)
		except StandardError:
			_log.exception('error formatting address')
			_log.error('template: %s', template)

		return None
	#--------------------------------------------------------
	def __get_variant_adr_part(self, data=u'?', part=None):
		requested_type = data.strip()
		cache_key = 'adr-type-%s' % requested_type
		try:
			type2use = self.__cache[cache_key]
			_log.debug('cache hit (%s): [%s] -> [%s]', cache_key, requested_type, type2use)
		except KeyError:
			type2use = requested_type
			if type2use != u'':
				adrs = self.pat.get_addresses(address_type = type2use)
				if len(adrs) == 0:
					_log.warning('no address of type [%s] for <%s> field extraction', requested_type, part)
					type2use = u''
			if type2use == u'':
				_log.debug('asking user for replacement address type')
				adr = gmPersonContactWidgets.select_address(missing = requested_type, person = self.pat)
				if adr is None:
					_log.debug('no replacement selected')
					if self.debug:
						return self._escape(_('no address type replacement selected'))
					return u''
				type2use = adr['address_type']
				self.__cache[cache_key] = type2use
				_log.debug('caching (%s): [%s] -> [%s]', cache_key, requested_type, type2use)

		return self._escape(self.pat.get_addresses(address_type = type2use)[0][part])
	#--------------------------------------------------------
	def _get_variant_adr_street(self, data=u'?'):
		return self.__get_variant_adr_part(data = data, part = 'street')
	#--------------------------------------------------------
	def _get_variant_adr_number(self, data=u'?'):
		return self.__get_variant_adr_part(data = data, part = 'number')
	#--------------------------------------------------------
	def _get_variant_adr_subunit(self, data=u'?'):
		return self.__get_variant_adr_part(data = data, part = 'subunit')
	#--------------------------------------------------------
	def _get_variant_adr_location(self, data=u'?'):
		return self.__get_variant_adr_part(data = data, part = 'urb')
	#--------------------------------------------------------
	def _get_variant_adr_suburb(self, data=u'?'):
		return self.__get_variant_adr_part(data = data, part = 'suburb')
	#--------------------------------------------------------
	def _get_variant_adr_postcode(self, data=u'?'):
		return self.__get_variant_adr_part(data = data, part = 'postcode')
	#--------------------------------------------------------
	def _get_variant_adr_region(self, data=u'?'):
		return self.__get_variant_adr_part(data = data, part = 'l10n_state')
	#--------------------------------------------------------
	def _get_variant_adr_country(self, data=u'?'):
		return self.__get_variant_adr_part(data = data, part = 'l10n_country')
	#--------------------------------------------------------
	def _get_variant_patient_comm(self, data=None):
		comm_type = None
		template = u'%(url)s'
		if data is not None:
			data_parts = data.split(u'//')
			if len(data_parts) > 0:
				comm_type = data_parts[0]
			if len(data_parts) > 1:
				template = data_parts[1]

		comms = self.pat.get_comm_channels(comm_medium = comm_type)
		if len(comms) == 0:
			if self.debug:
				return template + u': ' + self._escape(_('no URL for comm channel [%s]') % data)
			return u''

		return template % comms[0].fields_as_dict(escape_style = self.__esc_style)
	#--------------------------------------------------------
	def _get_variant_patient_photo(self, data=None):

		template = u'%s'
		target_mime = None
		target_ext = None
		if data is not None:
			parts = data.split(u'//')
			template = parts[0]
			if len(parts) > 1:
				target_mime = parts[1].strip()
			if len(parts) > 2:
				target_ext = parts[2].strip()
			if target_ext is None:
				if target_mime is not None:
					target_ext = gmMimeLib.guess_ext_by_mimetype(mimetype = target_mime)

		mugshot = self.pat.document_folder.latest_mugshot
		if mugshot is None:
			if self.debug:
				return self._escape(_('no mugshot available'))
			return u''

		fname = mugshot.export_to_file (
			target_mime = target_mime,
			target_extension = target_ext,
			ignore_conversion_problems = True
		)
		if fname is None:
			if self.debug:
				return self._escape(_('cannot export or convert latest mugshot'))
			return u''

		return template % fname
	#--------------------------------------------------------
	def _get_variant_patient_tags(self, data=u'%s//\\n'):
		if len(self.pat.tags) == 0:
			if self.debug:
				return self._escape(_('no tags for this patient'))
			return u''

		tags = gmDemographicsWidgets.select_patient_tags(patient = self.pat)

		if tags is None:
			if self.debug:
				return self._escape(_('no patient tags selected for inclusion') % data)
			return u''

		template, separator = data.split('//', 2)

		return separator.join([ template % t.fields_as_dict(escape_style = self.__esc_style) for t in tags ])
#	#--------------------------------------------------------
#	def _get_variant_patient_tags_table(self, data=u'?'):
#		pass
	#--------------------------------------------------------
	# praxis related placeholders
	#--------------------------------------------------------
	def _get_variant_praxis(self, data=None):
		options = data.split(u'//')

		if u'select' in options:
			options.remove(u'select')
			branch = 'select branch'
		else:
			branch = gmPraxis.cPraxisBranch(aPK_obj = gmPraxis.gmCurrentPraxisBranch()['pk_praxis_branch'])

		template = u'%s'
		if len(options) > 0:
			template = options[0]
		if template.strip() == u'':
			template = u'%s'

		return template % branch.fields_as_dict(escape_style = self.__esc_style)

	#--------------------------------------------------------
	def _get_variant_praxis_address(self, data=u''):

		options = data.split(u'//')

		# formatting template
		template = _('%(street)s %(number)s, %(postcode)s %(urb)s, %(l10n_state)s, %(l10n_country)s')
		if len(options) > 0:
			if options[0].strip() != u'':
				template = options[0]

		adr = gmPraxis.gmCurrentPraxisBranch().address
		if adr is None:
			if self.debug:
				return _('no address recorded')
			return u''
		try:
			return template % adr.fields_as_dict(escape_style = self.__esc_style)
		except StandardError:
			_log.exception('error formatting address')
			_log.error('template: %s', template)

		return None
	#--------------------------------------------------------
	def _get_variant_praxis_comm(self, data=None):
		options = data.split(u'//')
		comm_type = options[0]
		template = u'%(url)s'
		if len(options) > 1:
			template = options[1]

		comms = gmPraxis.gmCurrentPraxisBranch().get_comm_channels(comm_medium = comm_type)
		if len(comms) == 0:
			if self.debug:
				return template + u': ' + self._escape(_('no URL for comm channel [%s]') % data)
			return u''

		return template % comms[0].fields_as_dict(escape_style = self.__esc_style)
	#--------------------------------------------------------
	# provider related placeholders
	#--------------------------------------------------------
	def _get_variant_current_provider(self, data=None):
		prov = gmStaff.gmCurrentProvider()

		title = gmTools.coalesce (
			prov['title'],
			gmPerson.map_gender2salutation(prov['gender'])
		)

		tmp = u'%s %s. %s' % (
			title,
			prov['firstnames'][:1],
			prov['lastnames']
		)
		return self._escape(tmp)
	#--------------------------------------------------------
	def _get_variant_current_provider_external_id(self, data=u''):
		data_parts = data.split(u'//')
		if len(data_parts) < 2:
			return self._escape(u'current provider external ID: template is missing')

		id_type = data_parts[0].strip()
		if id_type == u'':
			return self._escape(u'current provider external ID: type is missing')

		issuer = data_parts[1].strip()
		if issuer == u'':
			return self._escape(u'current provider external ID: issuer is missing')

		prov = gmStaff.gmCurrentProvider()
		ids = prov.identity.get_external_ids(id_type = id_type, issuer = issuer)

		if len(ids) == 0:
			if self.debug:
				return self._escape(_('no external ID [%s] by [%s]') % (id_type, issuer))
			return u''

		return self._escape(ids[0]['value'])
	#--------------------------------------------------------
	def _get_variant_primary_praxis_provider(self, data=None):
		prov = self.pat.primary_provider
		if prov is None:
			return self._get_variant_current_provider()

		title = gmTools.coalesce (
			prov['title'],
			gmPerson.map_gender2salutation(prov['gender'])
		)

		tmp = u'%s %s. %s' % (
			title,
			prov['firstnames'][:1],
			prov['lastnames']
		)
		return self._escape(tmp)
	#--------------------------------------------------------
	def _get_variant_primary_praxis_provider_external_id(self, data=u''):
		data_parts = data.split(u'//')
		if len(data_parts) < 2:
			return self._escape(u'primary in-praxis provider external ID: template is missing')

		id_type = data_parts[0].strip()
		if id_type == u'':
			return self._escape(u'primary in-praxis provider external ID: type is missing')

		issuer = data_parts[1].strip()
		if issuer == u'':
			return self._escape(u'primary in-praxis provider external ID: issuer is missing')

		prov = self.pat.primary_provider
		if prov is None:
			if self.debug:
				return self._escape(_('no primary in-praxis provider'))
			return u''

		ids = prov.identity.get_external_ids(id_type = id_type, issuer = issuer)

		if len(ids) == 0:
			if self.debug:
				return self._escape(_('no external ID [%s] by [%s]') % (id_type, issuer))
			return u''

		return self._escape(ids[0]['value'])
	#--------------------------------------------------------
	def _get_variant_external_id(self, data=u''):
		data_parts = data.split(u'//')
		if len(data_parts) < 2:
			return self._escape(u'patient external ID: template is missing')

		id_type = data_parts[0].strip()
		if id_type == u'':
			return self._escape(u'patient external ID: type is missing')

		issuer = data_parts[1].strip()
		if issuer == u'':
			return self._escape(u'patient external ID: issuer is missing')

		ids = self.pat.get_external_ids(id_type = id_type, issuer = issuer)

		if len(ids) == 0:
			if self.debug:
				return self._escape(_('no external ID [%s] by [%s]') % (id_type, issuer))
			return u''

		return self._escape(ids[0]['value'])
	#--------------------------------------------------------
	def _get_variant_allergy_state(self, data=None):
		allg_state = self.pat.get_emr().allergy_state

		if allg_state['last_confirmed'] is None:
			date_confirmed = u''
		else:
			date_confirmed = u' (%s)' % gmDateTime.pydt_strftime (
				allg_state['last_confirmed'],
				format = '%Y %B %d'
			)

		tmp = u'%s%s' % (
			allg_state.state_string,
			date_confirmed
		)
		return self._escape(tmp)
	#--------------------------------------------------------
	def _get_variant_allergy_list(self, data=None):
		if data is None:
			return self._escape(_('template is missing'))

		template, separator = data.split('//', 2)

		return separator.join([ template % a.fields_as_dict(date_format = '%Y %b %d', escape_style = self.__esc_style) for a in self.pat.emr.get_allergies() ])
	#--------------------------------------------------------
	def _get_variant_allergies(self, data=None):

		if data is None:
			return self._escape(_('template is missing'))

		return u'\n'.join([ data % a.fields_as_dict(date_format = '%Y %b %d', escape_style = self.__esc_style) for a in self.pat.emr.get_allergies() ])
	#--------------------------------------------------------
	def _get_variant_current_meds_for_rx(self, data=None):
		if data is None:
			return self._escape(_('current_meds_for_rx: template is missing'))

		emr = self.pat.get_emr()
		from Gnumed.wxpython import gmMedicationWidgets
		current_meds = gmMedicationWidgets.manage_substance_intakes(emr = emr)
		if current_meds is None:
			return u''

		intakes2show = {}
		for intake in current_meds:
			fields_dict = intake.fields_as_dict(date_format = '%Y %b %d', escape_style = self.__esc_style)
			if intake['pk_brand'] is None:
				fields_dict['brand'] = self._escape(_('generic %s') % fields_dict['substance'])
				fields_dict['contains'] = self._escape(u'%s %s%s' % (fields_dict['substance'], fields_dict['amount'], fields_dict['unit']))
				intakes2show[fields_dict['brand']] = fields_dict
			else:
				comps = [ c.split('::') for c in intake.containing_drug['components'] ]
				fields_dict['contains'] = self._escape(u'; '.join([ u'%s %s%s' % (c[0], c[1], c[2]) for c in comps ]))
				intakes2show[intake['brand']] = fields_dict		# this will make multi-component drugs unique

		intakes2dispense = {}
		for brand, intake in intakes2show.items():
			msg = _('Dispense how much/many of "%(brand)s (%(contains)s)" ?') % intake
			amount2dispense = wx.GetTextFromUser(msg, _('Amount to dispense ?'))
			if amount2dispense == u'':
				continue
			intake['amount2dispense'] = amount2dispense
			intakes2dispense[brand] = intake

		return u'\n'.join([ data % intake for intake in intakes2dispense.values() ])
	#--------------------------------------------------------
	def _get_variant_current_meds(self, data=None):

		if data is None:
			return self._escape(_('template is missing'))

		parts = data.split(u'//')
		template = parts[0]
		ask_user = False
		if len(parts) > 1:
			ask_user = (parts[1] == u'select')

		emr = self.pat.get_emr()
		if ask_user:
			from Gnumed.wxpython import gmMedicationWidgets
			current_meds = gmMedicationWidgets.manage_substance_intakes(emr = emr)
			if current_meds is None:
				return u''
		else:
			current_meds = emr.get_current_substance_intakes (
				include_inactive = False,
				include_unapproved = True,
				order_by = u'brand, substance'
			)
			if len(current_meds) == 0:
				return u''

		return u'\n'.join([ template % m.fields_as_dict(date_format = '%Y %b %d', escape_style = self.__esc_style) for m in current_meds ])
	#--------------------------------------------------------
	def _get_variant_current_meds_table(self, data=None):
		options = data.split('//')

		return gmMedication.format_substance_intake (
			emr = self.pat.emr,
			output_format = self.__esc_style,
			table_type = u'by-brand'
		)
	#--------------------------------------------------------
	def _get_variant_current_meds_notes(self, data=None):
		options = data.split('//')

		return gmMedication.format_substance_intake_notes (
			emr = self.pat.get_emr(),
			output_format = self.__esc_style,
			table_type = u'by-brand'
		)
	#--------------------------------------------------------
	def _get_variant_lab_table(self, data=None):
		options = data.split('//')

		return gmPathLab.format_test_results (
			results = self.pat.emr.get_test_results_by_date(),
			output_format = self.__esc_style
		)
	#--------------------------------------------------------
	def _get_variant_test_results(self, data=None):

		template = u''
		date_format = '%Y %b %d %H:%M'
		separator = u'\n'

		options = data.split(u'//')
		try:
			template = options[0].strip()
			date_format = options[1]
			separator = options[2]
		except IndexError:
			pass

		if date_format.strip() == u'':
			date_format = '%Y %b %d %H:%M'
		if separator.strip() == u'':
			separator = u'\n'

		#results = gmMeasurementWidgets.manage_measurements(single_selection = False, emr = self.pat.emr)
		from Gnumed.wxpython.gmMeasurementWidgets import manage_measurements
		results = manage_measurements(single_selection = False, emr = self.pat.emr)
		if results is None:
			if self.debug:
				return self._escape(_('no results for this patient (available or selected)'))
			return u''

		if template == u'':
			return (separator + separator).join([ self._escape(r.format(date_format = date_format)) for r in results ])

		return separator.join([ template % r.fields_as_dict(date_format = date_format, escape_style = self.__esc_style) for r in results ])
	#--------------------------------------------------------
	def _get_variant_latest_vaccs_table(self, data=None):
		options = data.split('//')

		return gmVaccination.format_latest_vaccinations (
			output_format = self.__esc_style,
			emr = self.pat.emr
		)
	#--------------------------------------------------------
	def _get_variant_vaccination_history(self, data=None):
		options = data.split('//')
		template = options[0]
		if len(options) > 1:
			date_format = options[1]
		else:
			date_format = u'%Y %b %d'

		vaccs = self.pat.emr.get_vaccinations(order_by = u'date_given DESC, vaccine')

		return u'\n'.join([ template % v.fields_as_dict(date_format = date_format, escape_style = self.__esc_style) for v in vaccs ])
	#--------------------------------------------------------
	def _get_variant_PHX(self, data=None):

		if data is None:
			if self.debug:
				_log.error('PHX: missing placeholder arguments')
				return self._escape(_('PHX: Invalid placeholder options.'))
			return u''

		_log.debug('arguments: %s', data)

		data_parts = data.split(u'//')
		template = u'%s'
		separator = u'\n'
		date_format = '%Y %b %d'
		esc_style = None
		try:
			template = data_parts[0]
			separator = data_parts[1]
			date_format = data_parts[2]
			esc_style = data_parts[3]
		except IndexError:
			pass

		phxs = gmEMRStructWidgets.select_health_issues(emr = self.pat.emr)
		if phxs is None:
			if self.debug:
				return self._escape(_('no PHX for this patient (available or selected)'))
			return u''

		return separator.join ([
			template % phx.fields_as_dict (
				date_format = date_format,
				#escape_style = esc_style,
				escape_style = self.__esc_style,
				bool_strings = (self._escape(_('yes')), self._escape(_('no')))
			) for phx in phxs
		])
	#--------------------------------------------------------
	def _get_variant_problems(self, data=None):

		if data is None:
			return self._escape(_('template is missing'))

		probs = self.pat.emr.get_problems()

		return u'\n'.join([ data % p.fields_as_dict(date_format = '%Y %b %d', escape_style = self.__esc_style) for p in probs ])
	#--------------------------------------------------------
	def _get_variant_today(self, data='%Y %b %d'):
		return self._escape(gmDateTime.pydt_now_here().strftime(str(data)).decode(gmI18N.get_encoding()))
	#--------------------------------------------------------
	def _get_variant_tex_escape(self, data=None):
		return gmTools.tex_escape_string(text = data)
	#--------------------------------------------------------
	def _get_variant_text_snippet(self, data=None):
		data_parts = data.split(u'//')
		keyword = data_parts[0]
		template = u'%s'
		if len(data_parts) > 1:
			template = data_parts[1]

		expansion = gmKeywordExpansionWidgets.expand_keyword(keyword = keyword, show_list = True)

		if expansion is None:
			if self.debug:
				return self._escape(_('no textual expansion found for keyword <%s>') % keyword)
			return u''

		#return template % self._escape(expansion)
		return template % expansion
	#--------------------------------------------------------
	def _get_variant_data_snippet(self, data=None):
		parts = data.split(u'//')
		keyword = parts[0]
		template = u'%s'
		target_mime = None
		target_ext = None
		if len(parts) > 1:
			template = parts[1]
		if len(parts) > 2:
			target_mime = parts[2].strip()
		if len(parts) > 3:
			target_ext = parts[3].strip()
		if target_ext is None:
			if target_mime is not None:
				target_ext = gmMimeLib.guess_ext_by_mimetype(mimetype = target_mime)

		expansion = gmKeywordExpansion.get_expansion (
			keyword = keyword,
			textual_only = False,
			binary_only = True
		)
		if expansion is None:
			if self.debug:
				return self._escape(_('no binary expansion found for keyword <%s>') % keyword)
			return u''

		filename = expansion.export_to_file()
		if filename is None:
			if self.debug:
				return self._escape(_('cannot export data of binary expansion keyword <%s>') % keyword)
			return u''

		if expansion['is_encrypted']:
			pwd = wx.GetPasswordFromUser (
				message = _('Enter your GnuPG passphrase for decryption of [%s]') % expansion['keyword'],
				caption = _('GnuPG passphrase prompt'),
				default_value = u''
			)
			filename = gmTools.gpg_decrypt_file(filename = filename, passphrase = pwd)
			if filename is None:
				if self.debug:
					return self._escape(_('cannot decrypt data of binary expansion keyword <%s>') % keyword)
				return u''

		target_fname = gmTools.get_unique_filename (
			prefix = '%s-converted-' % os.path.splitext(filename)[0],
			suffix = target_ext
		)
		if not gmMimeLib.convert_file(filename = filename, target_mime = target_mime, target_filename = target_fname):
			if self.debug:
				return self._escape(_('cannot convert data of binary expansion keyword <%s>') % keyword)
			# hoping that the target can cope:
			return template % filename

		return template % target_fname
	#--------------------------------------------------------
	def _get_variant_free_text(self, data=None):

		if data is None:
			msg = _('generic text')
		else:
			msg = data

		dlg = gmGuiHelpers.cMultilineTextEntryDlg (
			None,
			-1,
			title = _('Replacing <free_text> placeholder'),
			msg = _('Below you can enter free text.\n\n [%s]') % msg
		)
		dlg.enable_user_formatting = True
		decision = dlg.ShowModal()

		if decision != wx.ID_SAVE:
			dlg.Destroy()
			if self.debug:
				return self._escape(_('Text input cancelled by user.'))
			return u''

		text = dlg.value.strip()
		if dlg.is_user_formatted:
			dlg.Destroy()
			return text

		dlg.Destroy()

		return self._escape(text)
	#--------------------------------------------------------
	def _get_variant_bill(self, data=None):
		try:
			bill = self.__cache['bill']
		except KeyError:
			from Gnumed.wxpython import gmBillingWidgets
			bill = gmBillingWidgets.manage_bills(patient = self.pat)
			if bill is None:
				if self.debug:
					return self._escape(_('no bill selected'))
				return u''
			self.__cache['bill'] = bill

		return data % bill.fields_as_dict(date_format = '%Y %B %d', escape_style = self.__esc_style)
	#--------------------------------------------------------
	def _get_variant_bill_item(self, data=None):
		try:
			bill = self.__cache['bill']
		except KeyError:
			from Gnumed.wxpython import gmBillingWidgets
			bill = gmBillingWidgets.manage_bills(patient = self.pat)
			if bill is None:
				if self.debug:
					return self._escape(_('no bill selected'))
				return u''
			self.__cache['bill'] = bill

		return u'\n'.join([ data % i.fields_as_dict(date_format = '%Y %B %d', escape_style = self.__esc_style) for i in bill.bill_items ])
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def _escape(self, text=None):
		if self.__esc_func is None:
			return text
		return self.__esc_func(text)
#=====================================================================
class cMacroPrimitives:
	"""Functions a macro can legally use.

	An instance of this class is passed to the GNUmed scripting
	listener. Hence, all actions a macro can legally take must
	be defined in this class. Thus we achieve some screening for
	security and also thread safety handling.
	"""
	#-----------------------------------------------------------------
	def __init__(self, personality = None):
		if personality is None:
			raise gmExceptions.ConstructorError, 'must specify personality'
		self.__personality = personality
		self.__attached = 0
		self._get_source_personality = None
		self.__user_done = False
		self.__user_answer = 'no answer yet'
		self.__pat = gmPerson.gmCurrentPatient()

		self.__auth_cookie = str(random.random())
		self.__pat_lock_cookie = str(random.random())
		self.__lock_after_load_cookie = str(random.random())

		_log.info('slave mode personality is [%s]', personality)
	#-----------------------------------------------------------------
	# public API
	#-----------------------------------------------------------------
	def attach(self, personality = None):
		if self.__attached:
			_log.error('attach with [%s] rejected, already serving a client', personality)
			return (0, _('attach rejected, already serving a client'))
		if personality != self.__personality:
			_log.error('rejecting attach to personality [%s], only servicing [%s]' % (personality, self.__personality))
			return (0, _('attach to personality [%s] rejected') % personality)
		self.__attached = 1
		self.__auth_cookie = str(random.random())
		return (1, self.__auth_cookie)
	#-----------------------------------------------------------------
	def detach(self, auth_cookie=None):
		if not self.__attached:
			return 1
		if auth_cookie != self.__auth_cookie:
			_log.error('rejecting detach() with cookie [%s]' % auth_cookie)
			return 0
		self.__attached = 0
		return 1
	#-----------------------------------------------------------------
	def force_detach(self):
		if not self.__attached:
			return 1
		self.__user_done = False
		# FIXME: use self.__sync_cookie for syncing with user interaction
		wx.CallAfter(self._force_detach)
		return 1
	#-----------------------------------------------------------------
	def version(self):
		ver = _cfg.get(option = u'client_version')
		return "GNUmed %s, %s $Revision: 1.51 $" % (ver, self.__class__.__name__)
	#-----------------------------------------------------------------
	def shutdown_gnumed(self, auth_cookie=None, forced=False):
		"""Shuts down this client instance."""
		if not self.__attached:
			return 0
		if auth_cookie != self.__auth_cookie:
			_log.error('non-authenticated shutdown_gnumed()')
			return 0
		wx.CallAfter(self._shutdown_gnumed, forced)
		return 1
	#-----------------------------------------------------------------
	def raise_gnumed(self, auth_cookie = None):
		"""Raise ourselves to the top of the desktop."""
		if not self.__attached:
			return 0
		if auth_cookie != self.__auth_cookie:
			_log.error('non-authenticated raise_gnumed()')
			return 0
		return "cMacroPrimitives.raise_gnumed() not implemented"
	#-----------------------------------------------------------------
	def get_loaded_plugins(self, auth_cookie = None):
		if not self.__attached:
			return 0
		if auth_cookie != self.__auth_cookie:
			_log.error('non-authenticated get_loaded_plugins()')
			return 0
		gb = gmGuiBroker.GuiBroker()
		return gb['horstspace.notebook.gui'].keys()
	#-----------------------------------------------------------------
	def raise_notebook_plugin(self, auth_cookie = None, a_plugin = None):
		"""Raise a notebook plugin within GNUmed."""
		if not self.__attached:
			return 0
		if auth_cookie != self.__auth_cookie:
			_log.error('non-authenticated raise_notebook_plugin()')
			return 0
		# FIXME: use semaphore
		wx.CallAfter(gmPlugin.raise_notebook_plugin, a_plugin)
		return 1
	#-----------------------------------------------------------------
	def load_patient_from_external_source(self, auth_cookie = None):
		"""Load external patient, perhaps create it.

		Callers must use get_user_answer() to get status information.
		It is unsafe to proceed without knowing the completion state as
		the controlled client may be waiting for user input from a
		patient selection list.
		"""
		if not self.__attached:
			return (0, _('request rejected, you are not attach()ed'))
		if auth_cookie != self.__auth_cookie:
			_log.error('non-authenticated load_patient_from_external_source()')
			return (0, _('rejected load_patient_from_external_source(), not authenticated'))
		if self.__pat.locked:
			_log.error('patient is locked, cannot load from external source')
			return (0, _('current patient is locked'))
		self.__user_done = False
		wx.CallAfter(self._load_patient_from_external_source)
		self.__lock_after_load_cookie = str(random.random())
		return (1, self.__lock_after_load_cookie)
	#-----------------------------------------------------------------
	def lock_loaded_patient(self, auth_cookie = None, lock_after_load_cookie = None):
		if not self.__attached:
			return (0, _('request rejected, you are not attach()ed'))
		if auth_cookie != self.__auth_cookie:
			_log.error('non-authenticated lock_load_patient()')
			return (0, _('rejected lock_load_patient(), not authenticated'))
		# FIXME: ask user what to do about wrong cookie
		if lock_after_load_cookie != self.__lock_after_load_cookie:
			_log.warning('patient lock-after-load request rejected due to wrong cookie [%s]' % lock_after_load_cookie)
			return (0, 'patient lock-after-load request rejected, wrong cookie provided')
		self.__pat.locked = True
		self.__pat_lock_cookie = str(random.random())
		return (1, self.__pat_lock_cookie)
	#-----------------------------------------------------------------
	def lock_into_patient(self, auth_cookie = None, search_params = None):
		if not self.__attached:
			return (0, _('request rejected, you are not attach()ed'))
		if auth_cookie != self.__auth_cookie:
			_log.error('non-authenticated lock_into_patient()')
			return (0, _('rejected lock_into_patient(), not authenticated'))
		if self.__pat.locked:
			_log.error('patient is already locked')
			return (0, _('already locked into a patient'))
		searcher = gmPersonSearch.cPatientSearcher_SQL()
		if type(search_params) == types.DictType:
			idents = searcher.get_identities(search_dict=search_params)
			raise StandardError("must use dto, not search_dict")
		else:
			idents = searcher.get_identities(search_term=search_params)
		if idents is None:
			return (0, _('error searching for patient with [%s]/%s') % (search_term, search_dict))
		if len(idents) == 0:
			return (0, _('no patient found for [%s]/%s') % (search_term, search_dict))
		# FIXME: let user select patient
		if len(idents) > 1:
			return (0, _('several matching patients found for [%s]/%s') % (search_term, search_dict))
		if not gmPatSearchWidgets.set_active_patient(patient = idents[0]):
			return (0, _('cannot activate patient [%s] (%s/%s)') % (str(idents[0]), search_term, search_dict))
		self.__pat.locked = True
		self.__pat_lock_cookie = str(random.random())
		return (1, self.__pat_lock_cookie)
	#-----------------------------------------------------------------
	def unlock_patient(self, auth_cookie = None, unlock_cookie = None):
		if not self.__attached:
			return (0, _('request rejected, you are not attach()ed'))
		if auth_cookie != self.__auth_cookie:
			_log.error('non-authenticated unlock_patient()')
			return (0, _('rejected unlock_patient, not authenticated'))
		# we ain't locked anyways, so succeed
		if not self.__pat.locked:
			return (1, '')
		# FIXME: ask user what to do about wrong cookie
		if unlock_cookie != self.__pat_lock_cookie:
			_log.warning('patient unlock request rejected due to wrong cookie [%s]' % unlock_cookie)
			return (0, 'patient unlock request rejected, wrong cookie provided')
		self.__pat.locked = False
		return (1, '')
	#-----------------------------------------------------------------
	def assume_staff_identity(self, auth_cookie = None, staff_name = "Dr.Jekyll", staff_creds = None):
		if not self.__attached:
			return 0
		if auth_cookie != self.__auth_cookie:
			_log.error('non-authenticated select_identity()')
			return 0
		return "cMacroPrimitives.assume_staff_identity() not implemented"
	#-----------------------------------------------------------------
	def get_user_answer(self):
		if not self.__user_done:
			return (0, 'still waiting')
		self.__user_done = False
		return (1, self.__user_answer)
	#-----------------------------------------------------------------
	# internal API
	#-----------------------------------------------------------------
	def _force_detach(self):
		msg = _(
			'Someone tries to forcibly break the existing\n'
			'controlling connection. This may or may not\n'
			'have legitimate reasons.\n\n'
			'Do you want to allow breaking the connection ?'
		)
		can_break_conn = gmGuiHelpers.gm_show_question (
			aMessage = msg,
			aTitle = _('forced detach attempt')
		)
		if can_break_conn:
			self.__user_answer = 1
		else:
			self.__user_answer = 0
		self.__user_done = True
		if can_break_conn:
			self.__pat.locked = False
			self.__attached = 0
		return 1
	#-----------------------------------------------------------------
	def _shutdown_gnumed(self, forced=False):
		top_win = wx.GetApp().GetTopWindow()
		if forced:
			top_win.Destroy()
		else:
			top_win.Close()
	#-----------------------------------------------------------------
	def _load_patient_from_external_source(self):
		patient = gmPatSearchWidgets.get_person_from_external_sources(search_immediately = True, activate_immediately = True)
		if patient is not None:
			self.__user_answer = 1
		else:
			self.__user_answer = 0
		self.__user_done = True
		return 1
#=====================================================================
# main
#=====================================================================
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	gmI18N.activate_locale()
	gmI18N.install_domain()

	#--------------------------------------------------------
	def test_placeholders():
		handler = gmPlaceholderHandler()
		handler.debug = True

		for placeholder in ['a', 'b']:
			print handler[placeholder]

		pat = gmPersonSearch.ask_for_patient()
		if pat is None:
			return

		gmPatSearchWidgets.set_active_patient(patient = pat)

		print 'DOB (YYYY-MM-DD):', handler['date_of_birth::%Y-%m-%d']

		app = wx.PyWidgetTester(size = (200, 50))

		ph = 'progress_notes::ap'
		print '%s: %s' % (ph, handler[ph])
	#--------------------------------------------------------
	def test_new_variant_placeholders():

		tests = [
			# should work:
			'$<lastname>$',
			'$<lastname::::3>$',
			'$<name::%(title)s %(firstnames)s%(preferred)s%(lastnames)s>$',

			# should fail:
			'lastname',
			'$<lastname',
			'$<lastname::',
			'$<lastname::>$',
			'$<lastname::abc>$',
			'$<lastname::abc::>$',
			'$<lastname::abc::3>$',
			'$<lastname::abc::xyz>$',
			'$<lastname::::>$',
			'$<lastname::::xyz>$',

			'$<date_of_birth::%Y-%m-%d>$',
			'$<date_of_birth::%Y-%m-%d::3>$',
			'$<date_of_birth::%Y-%m-%d::>$',

			# should work:
			'$<adr_location::home::35>$',
			'$<gender_mapper::male//female//other::5>$',
			'$<current_meds::==> %(brand)s %(preparation)s (%(substance)s) <==\n::50>$',
			'$<allergy_list::%(descriptor)s, >$',
			'$<current_meds_table::latex//by-brand>$'

#			'firstname',
#			'title',
#			'date_of_birth',
#			'progress_notes',
#			'soap',
#			'soap_s',
#			'soap_o',
#			'soap_a',
#			'soap_p',

#			'soap',
#			'progress_notes',
#			'date_of_birth'
		]

#		tests = [
#			'$<latest_vaccs_table::latex>$'
#		]

		pat = gmPersonSearch.ask_for_patient()
		if pat is None:
			return

		gmPatSearchWidgets.set_active_patient(patient = pat)

		handler = gmPlaceholderHandler()
		handler.debug = True

		for placeholder in tests:
			print placeholder, "=>", handler[placeholder]
			print "--------------"
			raw_input()

#		print 'DOB (YYYY-MM-DD):', handler['date_of_birth::%Y-%m-%d']

#		app = wx.PyWidgetTester(size = (200, 50))

#		ph = 'progress_notes::ap'
#		print '%s: %s' % (ph, handler[ph])

	#--------------------------------------------------------
	def test_scripting():
		from Gnumed.pycommon import gmScriptingListener
		import xmlrpclib
		listener = gmScriptingListener.cScriptingListener(macro_executor = cMacroPrimitives(personality='unit test'), port=9999)

		s = xmlrpclib.ServerProxy('http://localhost:9999')
		print "should fail:", s.attach()
		print "should fail:", s.attach('wrong cookie')
		print "should work:", s.version()
		print "should fail:", s.raise_gnumed()
		print "should fail:", s.raise_notebook_plugin('test plugin')
		print "should fail:", s.lock_into_patient('kirk, james')
		print "should fail:", s.unlock_patient()
		status, conn_auth = s.attach('unit test')
		print "should work:", status, conn_auth
		print "should work:", s.version()
		print "should work:", s.raise_gnumed(conn_auth)
		status, pat_auth = s.lock_into_patient(conn_auth, 'kirk, james')
		print "should work:", status, pat_auth
		print "should fail:", s.unlock_patient(conn_auth, 'bogus patient unlock cookie')
		print "should work", s.unlock_patient(conn_auth, pat_auth)
		data = {'firstname': 'jame', 'lastnames': 'Kirk', 'gender': 'm'}
		status, pat_auth = s.lock_into_patient(conn_auth, data)
		print "should work:", status, pat_auth
		print "should work", s.unlock_patient(conn_auth, pat_auth)
		print s.detach('bogus detach cookie')
		print s.detach(conn_auth)
		del s

		listener.shutdown()
	#--------------------------------------------------------
	def test_placeholder_regex():

		import re as regex

		tests = [
			' $<lastname>$ ',
			' $<lastname::::3>$ ',

			# should fail:
			'$<date_of_birth::%Y-%m-%d>$',
			'$<date_of_birth::%Y-%m-%d::3>$',
			'$<date_of_birth::%Y-%m-%d::>$',

			'$<adr_location::home::35>$',
			'$<gender_mapper::male//female//other::5>$',
			'$<current_meds::==> %(brand)s %(preparation)s (%(substance)s) <==\\n::50>$',
			'$<allergy_list::%(descriptor)s, >$',

			'\\noindent Patient: $<lastname>$, $<firstname>$',
			'$<allergies::%(descriptor)s & %(l10n_type)s & {\\footnotesize %(reaction)s} \tabularnewline \hline >$',
			'$<current_meds::		\item[%(substance)s] {\\footnotesize (%(brand)s)} %(preparation)s %(amount)s%(unit)s: %(schedule)s >$'
		]

		tests = [

			'junk	$<lastname::::3>$			junk',
			'junk	$<lastname::abc::3>$		junk',
			'junk	$<lastname::abc>$			junk',
			'junk	$<lastname>$				junk',

			'junk	$<lastname>$   junk   $<firstname>$						junk',
			'junk	$<lastname::abc>$   junk   $<fiststname::abc>$			junk',
			'junk	$<lastname::abc::3>$   junk   $<firstname::abc::3>$		junk',
			'junk	$<lastname::::3>$   junk   $<firstname::::3>$			junk'

		]

		tests = [
#			u'junk   $<<<date_of_birth::%Y %B %d $<inner placeholder::%Y %B %d::20>$::20>>>$   junk',
#			u'junk   $<date_of_birth::%Y %B %d::20>$   $<date_of_birth::%Y %B %d::20>$',
#			u'junk   $<date_of_birth::%Y %B %d::>$   $<date_of_birth::%Y %B %d::20>$   $<<date_of_birth::%Y %B %d::20>>$',
#			u'junk   $<date_of_birth::::20>$',
#			u'junk   $<date_of_birth::::>$',
			u'$<<<current_meds::%(brand)s (%(substance)s): Dispense $<free_text::Dispense how many of %(brand)s %(preparation)s (%(substance)s) ?::20>$ (%(preparation)s) \\n::250>>>$',
		]

		print "testing placeholder regex:", first_order_placeholder_regex
		print ""

		for t in tests:
			print 'line: "%s"' % t
			phs = regex.findall(first_order_placeholder_regex, t, regex.IGNORECASE)
			print " %s placeholders:" % len(phs)
			for p in phs:
				print ' => "%s"' % p
			print " "
	#--------------------------------------------------------
	def test_placeholder():

		phs = [
			#u'emr_journal::soapu //%(clin_when)s  %(modified_by)s  %(soap_cat)s  %(narrative)s//1000 days::',
			#u'free_text::tex//placeholder test::9999',
			#u'soap_for_encounters:://::9999',
			#u'soap_p',
			#u'encounter_list::%(started)s: %(assessment_of_encounter)s::30',
			#u'patient_comm::homephone::1234',
			#u'$<patient_address::work::1234>$',
			#u'adr_region::home::1234',
			#u'adr_country::fehlt::1234',
			#u'adr_subunit::fehlt::1234',
			#u'adr_suburb::fehlt-auch::1234',
			#u'external_id::Starfleet Serial Number//Star Fleet Central Staff Office::1234',
			#u'primary_praxis_provider',
			#u'current_provider',
			#u'current_provider_external_id::Starfleet Serial Number//Star Fleet Central Staff Office::1234',
			#u'current_provider_external_id::LANR//LÄK::1234'
			#u'primary_praxis_provider_external_id::LANR//LÄK::1234'
			#u'form_name_long::::1234',
			#u'form_name_long::::5',
			#u'form_name_long::::',
			#u'form_version::::5',
			#u'$<current_meds::\item %(brand)s %(preparation)s (%(substance)s) from %(started)s for %(duration)s as %(schedule)s until %(discontinued)s\\n::250>$',
			#u'$<vaccination_history::%(date_given)s: %(vaccine)s [%(batch_no)s] %(l10n_indications)s::250>$',
			#u'$<date_of_birth::%Y %B %d::20>$',
			#u'$<date_of_birth::%Y %B %d::>$',
			#u'$<date_of_birth::::20>$',
			#u'$<date_of_birth::::>$',
			#u'$<patient_tags::Tag "%(l10n_description)s": %(comment)s//\\n- ::250>$',
			#u'$<PHX::%(description)s\n  side: %(laterality)s, active: %(is_active)s, relevant: %(clinically_relevant)s, caused death: %(is_cause_of_death)s//\n//%Y %B %d//latex::250>$',
			#u'$<patient_photo::\includegraphics[width=60mm]{%s}//image/png//.png::250>$',
			#u'$<data_snippet::binary_test_snippet//path=<%s>//image/png//.png::250>$',
			#u'$<data_snippet::autograph-LMcC//path=<%s>//image/jpg//.jpg::250>$',
			#u'$<current_meds::%s ($<lastname::::50>$)//select::>$',
			#u'$<current_meds::%s//select::>$',
			#u'$<soap_by_issue::soapu //%Y %b %d//%(narrative)s::1000>$',
			#u'$<soap_by_episode::soapu //%Y %b %d//%(narrative)s::1000>$',
			#u'$<documents::select//description//document %(clin_when)s: %(l10n_type)s// file: %(fullpath)s (<some path>/%(name)s)//~/gnumed/export/::>$',
			#u'$<soap::soapu //%s::9999>$',
			#u'$<soap::soapu //%(soap_cat)s: %(date)s | %(provider)s | %(narrative)s::9999>$'
			#u'$<test_results:://%c::>$'
			#u'$<test_results::%(unified_abbrev)s: %(unified_val)s %(val_unit)s//%c::>$'
			#u'$<reminders:://::>$'
			#u'$<current_meds_for_rx::%(brand)s (%(contains)s): dispense %(amount2dispense)s ::>$'
			#u'$<praxis::%(branch)s (%(praxis)s)::>$'
			u'$<praxis_address::::120>$'
		]

		handler = gmPlaceholderHandler()
		handler.debug = True

		gmStaff.set_current_provider_to_logged_on_user()
		gmPraxisWidgets.set_active_praxis_branch(no_parent = True)
		pat = gmPersonSearch.ask_for_patient()
		if pat is None:
			return
		gmPatSearchWidgets.set_active_patient(patient = pat)

		app = wx.PyWidgetTester(size = (200, 50))
		#handler.set_placeholder('form_name_long', 'ein Testformular')
		for ph in phs:
			print ph
			print " result:"
			print '  %s' % handler[ph]
		#handler.unset_placeholder('form_name_long')
	#--------------------------------------------------------
	def test():
		pat = gmPersonSearch.ask_for_patient()
		if pat is None:
			sys.exit()
		gmPerson.set_active_patient(patient = pat)
		from Gnumed.wxpython import gmMedicationWidgets
		gmMedicationWidgets.manage_substance_intakes()
	#--------------------------------------------------------
	def test_show_phs():
		show_placeholders()
	#--------------------------------------------------------

	#test_placeholders()
	#test_new_variant_placeholders()
	#test_scripting()
	#test_placeholder_regex()
	#test()
	test_placeholder()
	#test_show_phs()

#=====================================================================

