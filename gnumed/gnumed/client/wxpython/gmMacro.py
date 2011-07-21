"""GNUmed macro primitives.

This module implements functions a macro can legally use.
"""
#=====================================================================
__version__ = "$Revision: 1.51 $"
__author__ = "K.Hilbert <karsten.hilbert@gmx.net>"

import sys, time, random, types, logging


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

from Gnumed.business import gmPerson, gmDemographicRecord, gmMedication, gmPathLab, gmPersonSearch
from Gnumed.business import gmVaccination, gmPersonSearch

from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmNarrativeWidgets
from Gnumed.wxpython import gmPatSearchWidgets
from Gnumed.wxpython import gmPlugin
from Gnumed.wxpython import gmEMRStructWidgets


_log = logging.getLogger('gm.scripting')
_cfg = gmCfg2.gmCfgData()

#=====================================================================
known_placeholders = [
	'lastname',
	'firstname',
	'title',
	'date_of_birth',
	'progress_notes',
	'soap',
	'soap_s',
	'soap_o',
	'soap_a',
	'soap_p',
	u'client_version',
	u'current_provider',
	u'allergy_state'
]


# those must satisfy the pattern "$name::args::optional length$" when used
known_variant_placeholders = [
	u'soap',
	u'progress_notes',			# "data" holds: categories//template
								# 	categories: string with "soap ", " " == None == admin
								#	template:	u'something %s something'		(do not include // in template !)
	u'emr_journal',				# "data" format:   <categories>//<template>//<line length>//<time range>//<target format>
								#	categories:	   string with any of "s", "o", "a", "p", " ";
								#				   (" " == None == admin category)
								#	template:	   something %s something else
								#				   (Do not include // in the template !)
								#	line length:   the length of individual lines, not the total placeholder length
								#	time range:	   the number of weeks going back in time
								#	target format: "tex" or anything else, if "tex", data will be tex-escaped
	u'date_of_birth',
	u'adr_street',				# "data" holds: type of address
	u'adr_number',
	u'adr_location',
	u'adr_postcode',
	u'gender_mapper',			# "data" holds: value for male // value for female
	u'current_meds',			# "data" holds: line template
	u'current_meds_table',		# "data" holds: format, options
	u'current_meds_notes',		# "data" holds: format, options
	u'lab_table',				# "data" holds: format (currently "latex" only)
	u'latest_vaccs_table',		# "data" holds: format, options
	u'today',					# "data" holds: strftime format
	u'tex_escape',				# "data" holds: string to escape
	u'allergies',				# "data" holds: line template, one allergy per line
	u'allergy_list',			# "data" holds: template per allergy, allergies on one line
	u'problems',				# "data" holds: line template, one problem per line
	u'name',					# "data" holds: template for name parts arrangement
	u'free_text',				# show a dialog for entering some free text
	u'soap_for_encounters'		# "data" holds: soap cats // strftime date format
]

default_placeholder_regex = r'\$<.+?>\$'				# this one works (except that OOo cannot be non-greedy |-( )

#_regex_parts = [
#	r'\$<\w+::.*(?::)\d+>\$',
#	r'\$<\w+::.+(?!>\$)>\$',
#	r'\$<\w+?>\$'
#]
#default_placeholder_regex = r'|'.join(_regex_parts)

default_placeholder_start = u'$<'
default_placeholder_end = u'>$'
#=====================================================================
class gmPlaceholderHandler(gmBorg.cBorg):
	"""Replaces placeholders in forms, fields, etc.

	- patient related placeholders operate on the currently active patient
	- is passed to the forms handling code, for example

	Note that this cannot be called from a non-gui thread unless
	wrapped in wx.CallAfter.

	There are currently three types of placeholders:

	simple static placeholders
		- those are listed in known_placeholders
		- they are used as-is

	extended static placeholders
		- those are like the static ones but have "::::<NUMBER>" appended
		  where <NUMBER> is the maximum length

	variant placeholders
		- those are listed in known_variant_placeholders
		- they are parsed into placeholder, data, and maximum length
		- the length is optional
		- data is passed to the handler
	"""
	def __init__(self, *args, **kwargs):

		self.pat = gmPerson.gmCurrentPatient()
		self.debug = False

		self.invalid_placeholder_template = _('invalid placeholder [%s]')
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

		if placeholder.startswith(default_placeholder_start):
			placeholder = placeholder[len(default_placeholder_start):]
			if placeholder.endswith(default_placeholder_end):
				placeholder = placeholder[:-len(default_placeholder_end)]
			else:
				_log.debug('placeholder must either start with [%s] and end with [%s] or neither of both', default_placeholder_start, default_placeholder_end)
				if self.debug:
					return self.invalid_placeholder_template % original_placeholder
				return None

		# simple static placeholder ?
		if placeholder in known_placeholders:
			return getattr(self, placeholder)

		# extended static placeholder ?
		parts = placeholder.split('::::', 1)
		if len(parts) == 2:
			name, lng = parts
			try:
				return getattr(self, name)[:int(lng)]
			except:
				_log.exception('placeholder handling error: %s', original_placeholder)
				if self.debug:
					return self.invalid_placeholder_template % original_placeholder
				return None

		# variable placeholders
		parts = placeholder.split('::')
		if len(parts) == 2:
			name, data = parts
			lng = None
		if len(parts) == 3:
			name, data, lng = parts
			try:
				lng = int(lng)
			except (TypeError, ValueError):
				_log.error('placeholder length definition error: %s, discarding length: >%s<', original_placeholder, lng)
				lng = None
		if len(parts) > 3:
			_log.warning('invalid placeholder layout: %s', original_placeholder)
			if self.debug:
				return self.invalid_placeholder_template % original_placeholder
			return None

		handler = getattr(self, '_get_variant_%s' % name, None)
		if handler is None:
			_log.warning('no handler <_get_variant_%s> for placeholder %s', name, original_placeholder)
			if self.debug:
				return self.invalid_placeholder_template % original_placeholder
			return None

		try:
			if lng is None:
				return handler(data = data)
			return handler(data = data)[:lng]
		except:
			_log.exception('placeholder handling error: %s', original_placeholder)
			if self.debug:
				return self.invalid_placeholder_template % original_placeholder
			return None

		_log.error('something went wrong, should never get here')
		return None
	#--------------------------------------------------------
	# properties actually handling placeholders
	#--------------------------------------------------------
	# property helpers
	#--------------------------------------------------------
	def _setter_noop(self, val):
		"""This does nothing, used as a NOOP properties setter."""
		pass
	#--------------------------------------------------------
	def _get_lastname(self):
		return self.pat.get_active_name()['lastnames']
	#--------------------------------------------------------
	def _get_firstname(self):
		return self.pat.get_active_name()['firstnames']
	#--------------------------------------------------------
	def _get_title(self):
		return gmTools.coalesce(self.pat.get_active_name()['title'], u'')
	#--------------------------------------------------------
	def _get_dob(self):
		return self._get_variant_date_of_birth(data='%x')
	#--------------------------------------------------------
	def _get_progress_notes(self):
		return self._get_variant_soap()
	#--------------------------------------------------------
	def _get_soap_s(self):
		return self._get_variant_soap(data = u's')
	#--------------------------------------------------------
	def _get_soap_o(self):
		return self._get_variant_soap(data = u'o')
	#--------------------------------------------------------
	def _get_soap_a(self):
		return self._get_variant_soap(data = u'a')
	#--------------------------------------------------------
	def _get_soap_p(self):
		return self._get_variant_soap(data = u'p')
	#--------------------------------------------------------
	def _get_soap_admin(self):
		return self._get_variant_soap(soap_cats = None)
	#--------------------------------------------------------
	def _get_client_version(self):
		return gmTools.coalesce (
			_cfg.get(option = u'client_version'),
			u'%s' % self.__class__.__name__
		)
	#--------------------------------------------------------
	def _get_current_provider(self):
		prov = gmPerson.gmCurrentProvider()

		title = gmTools.coalesce (
			prov['title'],
			gmPerson.map_gender2salutation(prov['gender'])
		)

		tmp = u'%s %s. %s' % (
			title,
			prov['firstnames'][:1],
			prov['lastnames']
		)

		return tmp
	#--------------------------------------------------------
	def _get_allergy_state(self):
		allg_state = self.pat.get_emr().allergy_state

		if allg_state['last_confirmed'] is None:
			date_confirmed = u''
		else:
			date_confirmed = u' (%s)' % allg_state['last_confirmed'].strftime('%Y %B %d').decode(gmI18N.get_encoding())

		tmp = u'%s%s' % (
			allg_state.state_string,
			date_confirmed
		)
		return tmp
	#--------------------------------------------------------
	# property definitions for static placeholders
	#--------------------------------------------------------
	placeholder_regex = property(lambda x: default_placeholder_regex, _setter_noop)

	# placeholders
	lastname = property(_get_lastname, _setter_noop)
	firstname = property(_get_firstname, _setter_noop)
	title = property(_get_title, _setter_noop)
	date_of_birth = property(_get_dob, _setter_noop)

	progress_notes = property(_get_progress_notes, _setter_noop)
	soap = property(_get_progress_notes, _setter_noop)
	soap_s = property(_get_soap_s, _setter_noop)
	soap_o = property(_get_soap_o, _setter_noop)
	soap_a = property(_get_soap_a, _setter_noop)
	soap_p = property(_get_soap_p, _setter_noop)
	soap_admin = property(_get_soap_admin, _setter_noop)

	allergy_state = property(_get_allergy_state, _setter_noop)

	client_version = property(_get_client_version, _setter_noop)

	current_provider = property(_get_current_provider, _setter_noop)
	#--------------------------------------------------------
	# variant handlers
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
		cats = list(u'soap')
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
				cats = list(u'soap').append(None)

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
					time_range = None

			# part[4]: output format
			if len(data_parts) > 4:
				target_format = data_parts[4]

		# FIXME: will need to be a generator later on
		narr = self.pat.get_emr().get_as_journal(soap_cats = cats, time_range = time_range)

		if len(narr) == 0:
			return u''

		if target_format == u'tex':
			keys = narr[0].keys()
			lines = []
			line_dict = {}
			for n in narr:
				for key in keys:
					if isinstance(n[key], basestring):
						line_dict[key] = gmTools.tex_escape_string(text = n[key])
						continue
					line_dict[key] = n[key]
				try:
					lines.append((template % line_dict)[:line_length])
				except KeyError:
					return u'invalid key in template [%s], valid keys: %s]' % (template, str(keys))
		else:
			try:
				lines = [ (template % n)[:line_length] for n in narr ]
			except KeyError:
				return u'invalid key in template [%s], valid keys: %s]' % (template, str(narr[0].keys()))

		return u'\n'.join(lines)
	#--------------------------------------------------------
	def _get_variant_progress_notes(self, data=None):
		return self._get_variant_soap(data=data)
	#--------------------------------------------------------
	def _get_variant_soap(self, data=None):

		# default: all categories, neutral template
		cats = list(u'soap')
		cats.append(None)
		template = u'%s'

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
				cats = list(u'soap')
				cats.append(None)

			# part[1]: template
			if len(data_parts) > 1:
				template = data_parts[1]

		#narr = gmNarrativeWidgets.select_narrative_from_episodes_new(soap_cats = cats)
		narr = gmNarrativeWidgets.select_narrative_from_episodes(soap_cats = cats)

		if narr is None:
			return u''

		if len(narr) == 0:
			return u''

		try:
			narr = [ template % n['narrative'] for n in narr ]
		except KeyError:
			return u'invalid key in template [%s], valid keys: %s]' % (template, str(narr[0].keys()))

		return u'\n'.join(narr)
	#--------------------------------------------------------
	def _get_variant_name(self, data=None):
		if data is None:
			return [_('template is missing')]

		name = self.pat.get_active_name()

		parts = {
			'title': gmTools.coalesce(name['title'], u''),
			'firstnames': name['firstnames'],
			'lastnames': name['lastnames'],
			'preferred': gmTools.coalesce (
				initial = name['preferred'],
				instead = u' ',
				template_initial = u' "%s" '
			)
		}

		return data % parts
	#--------------------------------------------------------
	def _get_variant_date_of_birth(self, data='%x'):
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
			return male_value

		if self.pat['gender'] == u'f':
			return female_value

		return other_value
	#--------------------------------------------------------
	def _get_variant_adr_street(self, data=u'?'):
#		if data == u'?':
#			types = xxxxxxxxxxx
		adrs = self.pat.get_addresses(address_type=data)
		if len(adrs) == 0:
			return _('no street for address type [%s]') % data
		return adrs[0]['street']
	#--------------------------------------------------------
	def _get_variant_adr_number(self, data=u'?'):
		adrs = self.pat.get_addresses(address_type=data)
		if len(adrs) == 0:
			return _('no number for address type [%s]') % data
		return adrs[0]['number']
	#--------------------------------------------------------
	def _get_variant_adr_location(self, data=u'?'):
		adrs = self.pat.get_addresses(address_type=data)
		if len(adrs) == 0:
			return _('no location for address type [%s]') % data
		return adrs[0]['urb']
	#--------------------------------------------------------
	def _get_variant_adr_postcode(self, data=u'?'):
		adrs = self.pat.get_addresses(address_type=data)
		if len(adrs) == 0:
			return _('no postcode for address type [%s]') % data
		return adrs[0]['postcode']
	#--------------------------------------------------------
	def _get_variant_allergy_list(self, data=None):
		if data is None:
			return [_('template is missing')]

		template, separator = data.split('//', 2)

		emr = self.pat.get_emr()
		return separator.join([ template % a for a in emr.get_allergies() ])
	#--------------------------------------------------------
	def _get_variant_allergies(self, data=None):

		if data is None:
			return [_('template is missing')]

		emr = self.pat.get_emr()
		return u'\n'.join([ data % a for a in emr.get_allergies() ])
	#--------------------------------------------------------
	def _get_variant_current_meds(self, data=None):

		if data is None:
			return [_('template is missing')]

		emr = self.pat.get_emr()
		current_meds = emr.get_current_substance_intake (
			include_inactive = False,
			include_unapproved = False,
			order_by = u'brand, substance'
		)

		# FIXME: we should be dealing with translating None to u'' here

		return u'\n'.join([ data % m for m in current_meds ])
	#--------------------------------------------------------
	def _get_variant_current_meds_table(self, data=None):

		options = data.split('//')

		if u'latex' in options:
			return gmMedication.format_substance_intake (
				emr = self.pat.get_emr(),
				output_format = u'latex',
				table_type = u'by-brand'
			)

		_log.error('no known current medications table formatting style in [%]', data)
		return _('unknown current medication table formatting style')
	#--------------------------------------------------------
	def _get_variant_current_meds_notes(self, data=None):

		options = data.split('//')

		if u'latex' in options:
			return gmMedication.format_substance_intake_notes (
				emr = self.pat.get_emr(),
				output_format = u'latex',
				table_type = u'by-brand'
			)

		_log.error('no known current medications notes formatting style in [%]', data)
		return _('unknown current medication notes formatting style')
	#--------------------------------------------------------
	def _get_variant_lab_table(self, data=None):

		options = data.split('//')

		emr = self.pat.get_emr()

		if u'latex' in options:
			return gmPathLab.format_test_results (
				results = emr.get_test_results_by_date(),
				output_format = u'latex'
			)

		_log.error('no known test results table formatting style in [%s]', data)
		return _('unknown test results table formatting style [%s]') % data
	#--------------------------------------------------------
	def _get_variant_latest_vaccs_table(self, data=None):

		options = data.split('//')

		emr = self.pat.get_emr()

		if u'latex' in options:
			return gmVaccination.format_latest_vaccinations(output_format = u'latex', emr = emr)

		_log.error('no known vaccinations table formatting style in [%s]', data)
		return _('unknown vaccinations table formatting style [%s]') % data
	#--------------------------------------------------------
	def _get_variant_problems(self, data=None):

		if data is None:
			return [_('template is missing')]

		probs = self.pat.get_emr().get_problems()

		return u'\n'.join([ data % p for p in probs ])
	#--------------------------------------------------------
	def _get_variant_today(self, data='%x'):
		return gmDateTime.pydt_now_here().strftime(str(data)).decode(gmI18N.get_encoding())
	#--------------------------------------------------------
	def _get_variant_tex_escape(self, data=None):
		return gmTools.tex_escape_string(text = data)
	#--------------------------------------------------------
	def _get_variant_free_text(self, data=u'tex//'):
		# <data>:
		#	format:	tex (only, currently)
		#	message: shown in input dialog, must not contain "//" or "::"

		format, msg = data.split('//')

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
			return _('Text input cancelled by user.')

		text = dlg.value.strip()
		if dlg.is_user_formatted:
			dlg.Destroy()
			return text

		dlg.Destroy()

		if format == u'tex':
			return gmTools.tex_escape_string(text = text)

		return text
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------

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
			print "must use dto, not search_dict"
			print xxxxxxxxxxxxxxxxx
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
		for placeholder in known_placeholders:
			print placeholder, "=", handler[placeholder]

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

		tests = [
			'$<latest_vaccs_table::latex>$'
		]

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
#		for placeholder in known_placeholders:
#			print placeholder, "=", handler[placeholder]

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

		print "testing placeholder regex:", default_placeholder_regex
		print ""

		for t in tests:
			print 'line: "%s"' % t
			print "placeholders:"
			for p in regex.findall(default_placeholder_regex, t, regex.IGNORECASE):
				print ' => "%s"' % p
			print " "
	#--------------------------------------------------------
	def test_placeholder():

		#ph = u'emr_journal::soap //%(date)s  %(modified_by)s  %(soap_cat)s  %(narrative)s//30::'
		#ph = u'free_text::latex//placeholder test::9999'
		#ph = u'soap_for_encounters:://::9999'
		ph = u'soap_a'

		handler = gmPlaceholderHandler()
		handler.debug = True

		pat = gmPersonSearch.ask_for_patient()
		if pat is None:
			return

		gmPatSearchWidgets.set_active_patient(patient = pat)

		app = wx.PyWidgetTester(size = (200, 50))
		print u'%s => %s' % (ph, handler[ph])
	#--------------------------------------------------------

	#test_placeholders()
	#test_new_variant_placeholders()
	#test_scripting()
	#test_placeholder_regex()
	test_placeholder()

#=====================================================================

