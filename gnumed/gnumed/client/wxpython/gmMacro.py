"""GNUmed macro primitives.

This module implements functions a macro can legally use.
"""
#=====================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmMacro.py,v $
__version__ = "$Revision: 1.45 $"
__author__ = "K.Hilbert <karsten.hilbert@gmx.net>"

import sys, time, random, types, logging


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmI18N, gmGuiBroker, gmExceptions, gmBorg, gmTools
from Gnumed.business import gmPerson, gmDemographicRecord
from Gnumed.wxpython import gmGuiHelpers, gmPlugin, gmPatSearchWidgets, gmNarrativeWidgets


_log = logging.getLogger('gm.scripting')


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
	'soap_p'
]


# those must satisfy the default_placeholder_regex when used
known_variant_placeholders = [
	u'soap',
	u'progress_notes',
	u'date_of_birth',
	u'adr_street',
	u'adr_number',
	u'adr_location',
	u'adr_postcode',
	u'gender_mapper'			# "data" holds: value for male // value for female
]


# pattern: "$name::args::optional length$"
default_placeholder_regex = u'\$\<.+(::.+){0,2}\>\$'
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

		self.invalid_placeholder_template = _('invalid placeholder: %s')
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
		original_placeholder = placeholder

		if not placeholder.startswith(default_placeholder_start):
			if self.debug:
				return self.invalid_placeholder_template % original_placeholder
			return None
		placeholder = placeholder[len(default_placeholder_start):]

		if not placeholder.endswith(default_placeholder_end):
			if self.debug:
				return self.invalid_placeholder_template % original_placeholder
			return None
		placeholder = placeholder[:-len(default_placeholder_end)]

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
		parts = placeholder.split('::', 2)
		if len(parts) == 2:
			name, data = parts
			lng = None
		elif len(parts) == 3:
			name, data, lng = parts
			try:
				lng = int(lng)
			except:
				_log.exception('placeholder length definition error: %s, discarding length', original_placeholder)
				lng = None
		else:
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
	#--------------------------------------------------------
	# variant handlers
	#--------------------------------------------------------
	def _get_variant_progress_notes(self, data=None):
		return self._get_variant_soap(data=data)
	#--------------------------------------------------------
	def _get_variant_soap(self, data=None):
		if data is not None:
			data = list(data)
		narr = gmNarrativeWidgets.select_narrative_from_episodes(soap_cats = data)
		if len(narr) == 0:
			return u''
		narr = [ n['narrative'] for n in narr ]
		return u'\n'.join(narr)
	#--------------------------------------------------------
	def _get_variant_date_of_birth(self, data='%x'):
		return self.pat['dob'].strftime(str(data))
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
		return "%s $Revision: 1.45 $" % self.__class__.__name__
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
		searcher = gmPerson.cPatientSearcher_SQL()
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

	gmI18N.activate_locale()
	gmI18N.install_domain()

	#--------------------------------------------------------
	def test_placeholders():
		handler = gmPlaceholderHandler()
		handler.debug = True

		for placeholder in ['a', 'b']:
			print handler[placeholder]

		pat = gmPerson.ask_for_patient()
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

			'$<adr_location::home::35>$',
			'$<gender_mapper::male//female//other::5>$'

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

		pat = gmPerson.ask_for_patient()
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

	if len(sys.argv) > 1 and sys.argv[1] == 'test':
		#test_placeholders()
		test_new_variant_placeholders()
		#test_scripting()

#=====================================================================
# $Log: gmMacro.py,v $
# Revision 1.45  2009-09-29 13:18:28  ncq
# - implement address placeholders
# - implement gender mapper placeholder
#
# Revision 1.44  2009/06/04 16:30:30  ncq
# - use set active patient from pat search widgets
#
# Revision 1.43  2009/03/10 14:23:32  ncq
# - support new style placeholders and test
#
# Revision 1.42  2009/01/15 11:40:20  ncq
# - better logging
#
# Revision 1.41  2008/03/20 15:30:37  ncq
# - fix misplaced %
#
# Revision 1.40  2008/03/09 20:16:32  ncq
# *** empty log message ***
#
# Revision 1.39  2008/03/05 22:30:14  ncq
# - new style logging
#
# Revision 1.38  2007/12/03 20:45:16  ncq
# - add variant placeholder handling ! :-)
#
# Revision 1.37  2007/11/05 12:10:21  ncq
# - support admin soap type
#
# Revision 1.36  2007/10/19 12:52:00  ncq
# - immediately search for patient matches
#
# Revision 1.35  2007/09/16 22:40:46  ncq
# - fix soap_* placeholder handling
#
# Revision 1.34  2007/09/09 19:17:44  ncq
# - add a bunch of placeholders regarding SOAP notes
#
# Revision 1.33  2007/08/29 22:09:32  ncq
# - narrative widgets factored out
#
# Revision 1.32  2007/08/13 21:59:54  ncq
# - add placeholder handler
# - add progress_notes placeholder
# - improved test suite
#
# Revision 1.31  2007/07/17 21:44:24  ncq
# - use patient.locked properly
#
# Revision 1.30  2007/07/11 21:09:54  ncq
# - use curr_pat.locked
#
# Revision 1.29  2007/07/03 16:00:56  ncq
# - remove unneeded import
#
# Revision 1.28  2007/01/21 12:21:38  ncq
# - comment on search_dict -> dto
#
# Revision 1.27  2006/12/25 22:54:44  ncq
# - comment fix
#
# Revision 1.26  2006/07/22 12:15:08  ncq
# - add missing import
#
# Revision 1.25  2006/07/22 10:04:51  ncq
# - cleanup
# - pre-init all attributes so connectors won't kill the GNUmed slave
#   with stupid AttributeExceptions
# - add lock_loaded_patient()
#
# Revision 1.24  2006/07/21 14:47:19  ncq
# - cleanup
# - add (_)load_patient_from_external_source()
# - improve testing
#
# Revision 1.23  2006/05/04 09:49:20  ncq
# - get_clinical_record() -> get_emr()
# - adjust to changes in set_active_patient()
# - need explicit set_active_patient() after ask_for_patient() if wanted
#
# Revision 1.22  2005/11/28 23:07:34  ncq
# - add shutdown_gnumed()
#
# Revision 1.21  2005/11/27 22:08:38  ncq
# - patient searcher has somewhat changed so adapt
#
# Revision 1.20  2005/11/27 20:38:10  ncq
# - properly import wx
#
# Revision 1.19  2005/09/28 21:27:30  ncq
# - a lot of wx2.6-ification
#
# Revision 1.18  2005/09/28 15:57:48  ncq
# - a whole bunch of wx.Foo -> wx.Foo
#
# Revision 1.17  2005/09/27 20:44:59  ncq
# - wx.wx* -> wx.*
#
# Revision 1.16  2005/01/31 10:37:26  ncq
# - gmPatient.py -> gmPerson.py
#
# Revision 1.15  2004/09/13 09:38:29  ncq
# - allow to wait for user interaction in controlled GnuMed instance
#   despite having to use wxCallAfter by waiting on a semaphore
#
# Revision 1.14  2004/07/24 17:13:25  ncq
# - main.plugins.gui now horstspace.notebook.gui
#
# Revision 1.13  2004/06/25 13:28:00  ncq
# - logically separate notebook and clinical window plugins completely
#
# Revision 1.12  2004/06/01 07:59:55  ncq
# - comments improved
#
# Revision 1.11  2004/03/20 19:48:07  ncq
# - adapt to flat id list from get_patient_ids
#
# Revision 1.10  2004/03/20 17:54:18  ncq
# - lock_into_patient now supports dicts and strings
# - fix unit test
#
# Revision 1.9  2004/03/12 13:22:38  ncq
# - comment on semaphore for GUI actions
#
# Revision 1.8  2004/03/05 11:22:35  ncq
# - import from Gnumed.<pkg>
#
# Revision 1.7  2004/02/25 09:46:22  ncq
# - import from pycommon now, not python-common
#
# Revision 1.6  2004/02/17 10:45:30  ncq
# - return authentication cookie from attach()
# - use that cookie in all RPCs
# - add assume_staff_identity()
#
# Revision 1.5  2004/02/12 23:57:22  ncq
# - now also use random cookie for attach/detach
# - add force_detach() with user feedback
# - add get_loaded_plugins()
# - implement raise_plugin()
#
# Revision 1.4  2004/02/05 23:52:05  ncq
# - remove spurious return 0
#
# Revision 1.3  2004/02/05 20:46:18  ncq
# - require attach() cookie for detach(), too
#
# Revision 1.2  2004/02/05 20:40:34  ncq
# - added attach()
# - only allow attach()ed clients to call methods
# - introduce patient locking/unlocking cookie
# - enhance unit test
#
# Revision 1.1  2004/02/05 18:10:44  ncq
# - actually minimally functional macro executor with test code
#
