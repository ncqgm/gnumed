# -*- coding: latin-1 -*-
"""GnuMed patient objects.

This is a patient object intended to let a useful client-side
API crystallize from actual use in true XP fashion.
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmPerson.py,v $
# $Id: gmPerson.py,v 1.24 2005-04-18 19:18:44 ncq Exp $
__version__ = "$Revision: 1.24 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

# std lib
import sys, os.path, time, re, string, types

# 3rd party
import mx.DateTime as mxDT

# GNUmed
from Gnumed.pycommon import gmLog, gmExceptions, gmPG, gmSignals, gmDispatcher, gmBorg, gmPyCompat, gmI18N, gmNull, gmBusinessDBObject
from Gnumed.business import gmClinicalRecord, gmMedDoc, gmDemographicRecord

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

__gender_list = None
__gender_idx = None
#============================================================
class cIdentity (gmBusinessDBObject.cBusinessDBObject):
	_service = "personalia"
	_cmd_fetch_payload = "select * from v_basic_person where pk_identity=%s"
	_cmds_lock_rows_for_update = ["select 1 from identity where pk=%(pk_identity)s and xmin = %(xmin_identity)s"]
	_cmds_store_payload = [
		"""update identity set
			title=%(title)s,
			dob=%(dob)s,
			cob=%(cob)s,
			gender=%(gender)s,
			fk_marital_status = %(pk_marital_status)s,
			karyotype = %(karyotype)s,
			pupic = %(pupic)s
		where pk=%(pk_identity)s""",
		"""select xmin_identity from v_basic_person where pk_identity=%(pk_identity)s"""
	]
	_updatable_fields = ["title", "dob", "cob", "gender", "pk_marital_status", "karyotype", "pupic"]
	_subtables = {
		'addresses': {
			'select': """
				select
					vba.id as pk,
					vba.number,
					vba.addendum, 
					vba.street,
					vba.urb,
					vba.postcode,
					at.name as type,
					lpoa.id_type as id_type
				from
					v_basic_address vba,
					lnk_person_org_address lpoa,
					address_type at
				where
					lpoa.id_address = vba.id
					and lpoa.id_type = at.id
					and lpoa.id_identity = %s""",
			'insert':
				"""insert into lnk_person_org_address (id_identity, id_address)
				values (%(pk_master)s, create_address (%(number)s, %(addendum)s, %(street)s, %(city)s, %(postcode)s))""",
			'delete':
				"""delete from lnk_person_org_address where id_identity = $s and id_address = %s"""
		},
		'ext_ids': {
			'select':"""
				select
					external_id as pk,
					fk_origin as id_type,
					comment,
					external_id,
					eeid.name as type,
					eeid.context as context
				from lnk_identity2ext_id, enum_ext_id_types eeid
				where id_identity = %s and fk_origin = eeid.pk""",
			'delete':
				"""delete from lnk_identity2ext_id where id_identity = %s and external_id = %s""",
			'insert':
				"""insert into lnk_identity2ext_id (external_id, fk_origin, comment, id_identity)
				values(%(external_id)s, %(id_type)s, %(comment)s, %(pk_master)s)"""
		},
		'comms': {
			'select': """
				select
					l2c.id_type,
					l2c.url,
					l2c.url as pk,
					l2c.is_confidential,
					ect.description as type
				from
					lnk_identity2comm l2c,
					enum_comm_types ect
				where
					l2c.id_identity = %s
					and ect.id = id_type""",
			'insert':
				"""insert into lnk_identity2ext_id (id_identity, id_type, url, is_confidential)
				values (%(pk_master)s, %(id_type)s, %(url)s, %(is_confidential)s)""",
			'delete':
				"""delete from lnk_identity2ext_id where id_identity = %s and url = %s"""},
		'occupations': {
			'select':
				"""select o.name as occupation, o.id as pk from occupation o, lnk_job2person lj2p where o.id = lj2p.id_occupation and lj2p.id_identity = %s""",
			'delete':
				"""delete from lnk_job2person lj2p where id_identity = %s and id_occupation = %s""",
			'insert':
				"""insert into lnk_job2person (id_identity, id_occupation) values (%(pk_master)s, create_occupation(%(occupation)s))"""
		}
	}
	#--------------------------------------------------------
	def getId(self):
		return self['pk_identity']
	#--------------------------------------------------------
	def get_all_names(self):
		cmd = """
				select n.firstnames, n.lastnames, i.title, n.preferred
				from names n, identity i
				where n.id_identity=%s and i.pk=%s"""
		rows, idx = gmPG.run_ro_query('personalia', cmd, 1, self['pk_identity'], self['pk_identity'])
		if rows is None:
			return None
		if len(rows) == 0:
			return [{'first': '**?**', 'last': '**?**', 'title': '**?**', 'preferred':'**?**'}]
		else:
			names = []
			for row in rows:
				names.append({'first': row[0], 'last': row[1], 'title': row[2], 'preferred':row[3]})
			return names
	#--------------------------------------------------------
	def get_description (self):
		"""
		Again, allow code reuse where we don't care whether we are talking to a person
		or organisation"""
		title = self._payload[self._idx['title']]
		if title is None:
			title = ''
		else:
			title = title[:4] + '.'
		return "%s%s %s" % (title, self._payload[self._idx['firstnames']], self._payload[self._idx['lastnames']])
	#-------------------------------------------------------- 	
	def add_name(self, firstnames, lastnames, active=True, nickname=None):
		"""
		Add a name.
		@param firstnames The first names.
		@param lastnames The last names.
		@param active When True, the new name will become the active one (hence setting other names to inactive)
		@type active A types.BooleanType instance
		@param nickname The preferred/nick/warrior name to set.
		"""
		queries = []
		active = (active and 't') or 'f'
		queries.append (
			("select add_name(%s, %s, %s, %s)", [self.getId(), firstnames, lastnames, active])
		)
		if nickname is not None:
			queries.append (
				("select set_nickname(%s, %s)", [self.getId(), nickname])
			)
		successful, data = gmPG.run_commit2('personalia', queries)
		if not successful:
			_log.Log(gmLog.lPanic, 'failed to add name: %s' % data)
			return False
		return True
	#--------------------------------------------------------
	def set_nickname(self, nickname=None):
		"""
		Set the nickname. Setting the nickname only makes sense for the currently
		active name.
		@param nickname The preferred/nick/warrior name to set.
		"""
		# dump to backend
		cmd = "select set_nickname(%s, %s)"
		successful, data = gmPG.run_commit2 (
			link_obj = 'personalia',
			queries = [
				(cmd, [self.getId(), nickname])
			]			
		)
		if not successful:
			_log.Log(gmLog.lPanic, 'failed to set nickname: %s' % data)
			return False
		return True
	#--------------------------------------------------------
	def link_occupation(self, occupation):
		"""
		Link an occupation with a patient, creating the occupation if it does not exists.
		@param occupation The name of the occupation to link the patient to.
		"""
		# junk the cache
		if self._ext_cache.has_key('occupations'):
			del self._ext_cache['occupations']
		# dump to backend
		cmd = """
		insert into lnk_job2person (id_identity, id_occupation)
		values (%s, create_occupation(%s))"""
		successful, data =  gmPG.run_commit2 (
			link_obj = 'personalia',
			queries = [
				(cmd, [self._payload[self._idx['pk_identity']], occupation])
			]
		)
		if not successful:
			_log.Log(gmLog.lPanic, 'failed to create occupation: %s' % data)
			return False
		return True
	#----------------------------------------------------------------------
	def get_relatives(self):
		cmd = """
select
        t.description, vbp.pk_identity as id, title, firstnames, lastnames, dob, cob, gender, karyotype, pupic, pk_marital_status,
	marital_status, xmin_identity, preferred
from
	v_basic_person vbp, relation_types t, lnk_person2relative l
where
	(l.id_identity = %s and
	vbp.pk_identity = l.id_relative and
	t.id = l.id_relation_type) or
	(l.id_relative = %s and
	vbp.pk_identity = l.id_identity and
	t.inverse = l.id_relation_type)
"""
		data, idx = gmPG.run_ro_query('personalia', cmd, 1, [self.getId(), self.getId()])
		if data is None:
			return []
		if len(data) == 0:
			return []
		return [(r[0], cIdentity (row = {'data':r[1:], 'idx':idx, 'pk_field': 'pk'})) for r in data ]
	#--------------------------------------------------------
	def link_new_relative(self, rel_type = 'parent'):
		from Gnumed.business.gmPerson import create_dummy_identity
		# create new relative
		id_new_relative = create_dummy_identity()
		relative = gmPerson(id_new_relative)
		# pre-fill with data from ourselves
		relative_ident = relative.get_identity()
		relative_ident.copyAddresses(self)
		relative_ident.addName( '**?**', self.get_names()['last'], activate = 1)
		# and link the two
		if self._ext_cache.has_key('relatives'):
			del self._ext_cache['relatives']
		cmd2 = """
			insert into lnk_person2relative (
				id_identity, id_relative, id_relation_type
			) values (
				%s, %s, (select id from relation_types where description = %s)
			)"""
		if rel_type:
			return gmPG.run_commit2 (
				'personalia',
				[(cmd1, [self.getId(), relation['id'], relation['id'], self.getId()]),
				 (cmd2, [relation['id'], self.getId(), rel_type])]
			)
		else:
			return gmPG.run_commit2 ('personalia', [(cmd1, [self.getId(), relation['id'], relation['id'], self.getId()])])
	#----------------------------------------------------------------------
	def delete_relative(self, relation):
		self.set_relative (None, relation)
	#----------------------------------------------------------------------
	def get_medical_age(self):
		dob = self['dob']
		if dob is None:
			return '??'
		return dob2medical_age(dob)
#============================================================
# may get preloaded by the waiting list
class cPerson:
	"""Represents a person that DOES EXIST in the database.

	Accepting this as a hard-and-fast rule WILL simplify
	internal logic and remove some corner cases, I believe.

	- searching and creation is done OUTSIDE this object
	"""
	# handlers for __getitem__
	_get_handler = {}

	def __init__(self, identity = None):
		if not isinstance (identity, cIdentity):
			# assume to be an identity.pk then
			identity = cIdentity (aPK_obj = int(identity))

		self.__ID = identity['pk_identity']  	# = identity.pk = v_basic_person.pk_identity = primary key
		self.__db_cache = {'identity': identity}

		# register backend notification interests ...
		if not self._register_interests():
			raise gmExceptions.ConstructorError, "Cannot register person modification interests."

		_log.Log(gmLog.lData, 'Instantiated person [%s].' % self.__ID)
	#--------------------------------------------------------
	def cleanup(self):
		"""Do cleanups before dying.

		- note that this may be called in a thread
		"""
		_log.Log(gmLog.lData, 'cleaning up after person [%s]' % self.__ID)
		if self.__db_cache.has_key('clinical record'):
			self.__db_cache['clinical record'].cleanup()
			del self.__db_cache['clinical record']
		if self.__db_cache.has_key('identity'):
			self.__db_cache['identity'].cleanup()
			del self.__db_cache['identity']
		# FIXME: document folder
	#--------------------------------------------------------
	# internal helper
	#--------------------------------------------------------
	def _pkey_exists(self):
		"""Does this primary key exist ?

		- true/false/None
		"""
		cmd = "select exists(select pk from identity where pk = %s)"
		res = gmPG.run_ro_query('personalia', cmd, None, self.__ID)
		if res is None:
			_log.Log(gmLog.lErr, 'check for person PK [%s] existence failed' % self.__ID)
			return None
		return res[0][0]
	#--------------------------------------------------------
	def _register_interests(self):
		return 1
	#--------------------------------------------------------
	# __getitem__ handling
	#--------------------------------------------------------
	def __getitem__(self, aVar = None):
		"""Return any attribute if known how to retrieve it.
		"""
		try:
			return cPerson._get_handler[aVar](self)
		except KeyError:
			_log.LogException('Missing get handler for [%s]' % aVar, sys.exc_info())
			return None
	#--------------------------------------------------------
	def getID(self):
		return self.__ID
	#--------------------------------------------------------
	def _getMedDocsList(self):
		"""Build a complete list of metadata for all documents of this person.
		"""
		cmd = "SELECT id from doc_med WHERE patient_id=%s"
		tmp = gmPG.run_ro_query('blobs', cmd, None, self.__ID)
		_log.Log(gmLog.lData, "document IDs: %s" % tmp)
		if tmp is None:
			return []
		docs = []
		for doc_id in tmp:
			if doc_id is not None:
				docs.extend(doc_id)
		if len(docs) == 0:
			_log.Log(gmLog.lInfo, "No documents found for person (ID [%s])." % self.__ID)
			return None
		return docs
	#----------------------------------------------------------
	def get_clinical_record(self):
		try:
			return self.__db_cache['clinical record']
		except KeyError:
			pass
		tstart = time.time()
		try:
			self.__db_cache['clinical record'] = gmClinicalRecord.cClinicalRecord(aPKey = self.__ID)
		except StandardError:
			_log.LogException('cannot instantiate clinical record for person [%s]' % self.__ID, sys.exc_info())
			return None
		duration = time.time() - tstart
		print "get_clinical_record() took %s seconds" % duration
		return self.__db_cache['clinical record']
	#--------------------------------------------------------
	def get_identity(self):
		# because we are instantiated with it, it always exists
		return self.__db_cache['identity']
	#--------------------------------------------------------
	def get_document_folder(self):
		try:
			return self.__db_cache['document folder']
		except KeyError:
			pass
		try:
			# FIXME: we need some way of setting the type of backend such that
			# to instantiate the correct type of document folder class
			self.__db_cache['document folder'] = gmMedDoc.cDocumentFolder(aPKey = self.__ID)
		except StandardError:
			_log.LogException('cannot instantiate document folder for person [%s]' % self.__ID, sys.exc_info())
			return None
		return self.__db_cache['document folder']
	#--------------------------------------------------------
	def export_data(self):
		data = {}
		emr = self.get_clinical_record()
		if emr is None:
			return None
		data['clinical'] = emr.get_text_dump()
		return data
	#--------------------------------------------------------
	def _get_API(self):
		API = []
		for handler in gmPerson._get_handler.keys():
			data = {}
			# FIXME: how do I get an unbound method object ?
			func = self._get_handler[handler]
			data['API call name'] = handler
			data['internal name'] = func.__name__
#			data['reported by'] = method.im_self
#			data['defined by'] = method.im_class
			data['description'] = func.__doc__
			API.append(data)
		return API
	#--------------------------------------------------------
	# set up handler map
	_get_handler['document folder'] = get_document_folder
	_get_handler['API'] = _get_API
	_get_handler['ID'] = getID
	_get_handler['id'] = getID
	_get_handler['pk'] = getID
	_get_handler['pk_identity'] = getID

#============================================================
class gmCurrentPatient(gmBorg.cBorg):
	"""Patient Borg to hold currently active patient.

	There may be many instances of this but they all share state.
	"""
	def __init__(self, person=None):
		"""Change or get currently active patient.

		person:
		* None: get currently active patient
		* -1: unset currently active patient
		* cPerson instance: set active patient if possible
		"""
		gmBorg.cBorg.__init__(self)

		# make sure we do have a person pointer
		try:
			tmp = self._person
		except AttributeError:
			self._person = gmNull.cNull()

		# set initial lock state,
		# this lock protects against activating another patient
		# when we are controlled from a remote application
		try:
			tmp = self._locked
		except AttributeError:
			self.unlock()

		# user wants copy of current patient
		if person is None:
			return None

		# user wants to explicitely unset current patient
		if person == -1:
			_log.Log(gmLog.lData, 'explicitely unsetting current patient')
			self.__send_pre_selection_notification()
			self._person.cleanup()
			self._person = gmNull.cNull()
			self.__send_selection_notification()
			return None

		# must be cPerson instance, then
		if not isinstance(person, cPerson):
			_log.Log(gmLog.lErr, 'cannot set active patient to [%s], must be either None, -1 or cPerson instance' % str(person))

		# same ID, no change needed
		if self._person['pk_identity'] == person['pk_identity']:
			return None

		# user wants different patient
		_log.Log(gmLog.lData, 'patient change [%s] -> [%s] requested' % (self._person['pk_identity'], person['pk_identity']))

		# but not if patient is locked
		if self._locked:
			_log.Log(gmLog.lErr, 'patient [%s] is locked, cannot change to [%s]' % (self._person['pk_identity'], person['pk_identity']))
			# FIXME: exception ?
			return None

		# everything seems swell
		self.__send_pre_selection_notification()
		self._person.cleanup()
		self._person = person
		self.__send_selection_notification()

		return None
	#--------------------------------------------------------
	def cleanup(self):
		self._person.cleanup()
	#--------------------------------------------------------
	def get_clinical_record(self):
		return self._person.get_clinical_record()
	#--------------------------------------------------------
	def get_identity(self):
		return self._person.get_identity()
	#--------------------------------------------------------
	def get_document_folder(self):
		return self._person.get_document_folder()
	#--------------------------------------------------------
	def getID(self):
		return self._person.getID()
	#--------------------------------------------------------
	def export_data(self):
		return self._person.export_data()
	#--------------------------------------------------------
# this MAY eventually become useful when we start
# using more threads in the frontend
#	def init_lock(self):
#		"""initializes a pthread lock. Doesn't matter if 
#		race of 2 threads in alock assignment, just use the 
#		last lock created ( unless both threads find no alock,
#		then one thread sleeps before self.alock = .. is completed ,
#		the other thread assigns a new RLock object, 
#		and begins immediately using it on a call to self.lock(),
#		and gets past self.alock.acquire()
#		before the first thread wakes up and assigns to self.alock 
#		, obsoleting
#		the already in use alock by the second thread )."""
#		try:
#			if  not self.__dict__.has_key('alock') :
#				self.alock = threading.RLock()
#		except:
#			_log.LogException("Cannot test/create lock", sys.exc_info()) 
	#--------------------------------------------------------
	# patient change handling
	#--------------------------------------------------------
	def lock(self):
		self._locked = True
	#--------------------------------------------------------
	def unlock(self):
		self._locked = False
	#--------------------------------------------------------
	def is_locked(self):
		return self._locked
	#--------------------------------------------------------
	def __send_pre_selection_notification(self):
		"""Sends signal when another patient is about to become active."""
		kwargs = {
			'pk_identity': self._person['pk_identity'],
			'patient': self._person['pk_identity'],
			'signal': gmSignals.activating_patient(),
			'sender': id(self.__class__)
		}
		gmDispatcher.send(gmSignals.activating_patient(), kwds=kwargs)
	#--------------------------------------------------------
	def __send_selection_notification(self):
		"""Sends signal when another patient has actually been made active."""
		kwargs = {
			'pk_identity': self._person['pk_identity'],
			'patient': self._person,
			'signal': gmSignals.patient_selected(),
			'sender': id(self.__class__)
		}
		#gmDispatcher.send(gmSignals.patient_selected(), kwds=kwargs)
		gmDispatcher.send(**kwargs)
	#--------------------------------------------------------
	def is_connected(self):
		if isinstance(self._person, gmNull.cNull):
			return False
		else:
			return True
	#--------------------------------------------------------
	# __getitem__ handling
	#--------------------------------------------------------
	def __getitem__(self, aVar = None):
		"""Return any attribute if known how to retrieve it by proxy.
		"""
		return self._person[aVar]
#============================================================
class cPatientSearcher_SQL:
	"""UI independant i18n aware patient searcher."""
	def __init__(self):
		# list more generators here once they are written
		self.__query_generators = {
			'default': self.__generate_queries_de,
			'de': self.__generate_queries_de
		}
		# set locale dependant query handlers
		# - generator
		try:
			self.__generate_queries = self.__query_generators[gmI18N.system_locale_level['full']]
		except KeyError:
			try:
				self.__generate_queries = self.__query_generators[gmI18N.system_locale_level['country']]
			except KeyError:
				try:
					self.__generate_queries = self.__query_generators[gmI18N.system_locale_level['language']]
				except KeyError:
					self.__generate_queries = self.__query_generators['default']
		# make a cursor
		self.conn = gmPG.ConnectionPool().GetConnection('personalia')
		self.curs = self.conn.cursor()
	#--------------------------------------------------------
	def __del__(self):
		try:
			self.curs.close()
		except: pass
		try:
			self.conn.close()
		except: pass
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------
	def get_persons(self, search_term = None, a_locale = None, search_dict = None):
		identities = self.get_identities(search_term, a_locale, search_dict)
		if identities is None:
			return None
		else:
			return [cPerson(identity = ident) for ident in identities]
	#--------------------------------------------------------
	def get_identities(self, search_term = None, a_locale = None, search_dict = None):
		"""Get patient identity objects for given parameters.

		- either search term or search dict
		- search dict contains structured data that doesn't need to be parsed
		- search_dict takes precedence over search_term
		"""
		parse_search_term = (search_dict is None)
		if not parse_search_term:
			query_lists = self.__generate_queries_generic(search_dict)
			if query_lists is None:
				parse_search_term = True
			if len(query_lists) == 0:
				parse_search_term = True
		if parse_search_term:
			# temporary change of locale for selecting query generator
			if a_locale is not None:
				print "temporary change of locale on patient search not implemented"
				_log.Log(gmLog.lWarn, "temporary change of locale on patient search not implemented")
			# generate queries
			if search_term is None:
				_log.Log(gmLog.lErr, 'need search term (search_dict AND search_term are None')
				return None
			query_lists = self.__generate_queries(search_term)

		# anything to do ?
		if (query_lists is None) or (len(query_lists) == 0):
			_log.Log(gmLog.lErr, 'query tree empty')
			_log.Log(gmLog.lErr, '[%s] [%s] [%s]' % (search_term, a_locale, str(search_dict)))
			return None

		# collect IDs here
		pat_ids = []
		# cycle through query list
		for query_list in query_lists:
			_log.Log(gmLog.lData, "running %s" % query_list)
			# try all queries at this query level
			for cmd in query_list:
				# FIXME: actually, we should pass in the parsed search_term
				if search_dict is None:
					rows, idx = gmPG.run_ro_query(self.curs, cmd, True)
				else:
					rows, idx = gmPG.run_ro_query(self.curs, cmd, True, search_dict)
				if rows is None:
					_log.Log(gmLog.lErr, 'error fetching patient IDs')
					continue
				if len(rows) != 0:
					pat_ids.append((rows, idx))
			# if we got patients don't try more query levels
			if len(pat_ids) > 0:
				break
		pat_identities = []
		try:
			for rows, idx in pat_ids:
				pat_identities.extend (
					[ cIdentity(row={'pk_field': 'pk_identity', 'data': row, 'idx': idx})
						for row in rows ]
				)
		except:
			_log.LogException ("cannot create patient identity objects", sys.exc_info (), verbose=0)
		return pat_identities
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __make_sane_caps(self, aName = None):
		"""Make user input suitable for case-sensitive matching.

		- this mostly applies to names
		- it will be correct in "most" cases

		- "burney"  -> "Burney"
		- "mcburney" -> "Mcburney" (probably wrong but hard to be smart about it)
		- "mcBurney" -> "McBurney" (try to preserve effort put in by the user)
		- "McBurney" -> "McBurney"
		"""
		if aName is None:
			_log.Log(gmLog.lErr, 'argument error: aName is None')
			return None
		return aName[:1].upper() + aName[1:]
	#--------------------------------------------------------
	def __normalize(self, aString = None, aggressive = 0):
		"""Transform some characters into a regex."""
		if aString is None:
			return None
		if len(aString) == 0:
			return aString

		# umlauts
		normalized =    aString.replace(u'Ä', u'(Ä|AE|Ae|A|E)')
		normalized = normalized.replace(u'Ö', u'(Ö|OE|Oe|O)')
		normalized = normalized.replace(u'Ü', u'(Ü|UE|Ue|U)')
		normalized = normalized.replace(u'ä', u'(ä|ae|e|a)')
		normalized = normalized.replace(u'ö', u'(ö|oe|o)')
		normalized = normalized.replace(u'ü', u'(ü|ue|u|y|i)')
		normalized = normalized.replace(u'ß', u'(ß|sz|ss|s)')

		# common soundalikes
		# - René, Desiré, Inés ...
		normalized = normalized.replace(u'é', u'*#DUMMY#*')
		normalized = normalized.replace(u'è', u'*#DUMMY#*')
		normalized = normalized.replace(u'*#DUMMY#*', u'(é|e|è|ä|ae)')
		# FIXME: missing i/a/o - but uncommon in German
		normalized = normalized.replace('v', '*#DUMMY#*')
		normalized = normalized.replace('f', '*#DUMMY#*')
		normalized = normalized.replace('ph','*#DUMMY#*')	# now, this is *really* specific for German
		normalized = normalized.replace('*#DUMMY#*', '(v|f|ph)')

		# silent characters
		normalized = normalized.replace('Th','*#DUMMY#*')
		normalized = normalized.replace('T', '*#DUMMY#*')
		normalized = normalized.replace('*#DUMMY#*', '(Th|T)')
		normalized = normalized.replace('th', '*#DUMMY#*')
		normalized = normalized.replace('t', '*#DUMMY#*')
		normalized = normalized.replace('*#DUMMY#*', '(th|t)')

		# apostrophes, hyphens et al
		normalized = normalized.replace('"', '*#DUMMY#*')
		normalized = normalized.replace("'", '*#DUMMY#*')
		normalized = normalized.replace('`', '*#DUMMY#*')
		normalized = normalized.replace('*#DUMMY#*', """("|'|`|*#DUMMY#*|\s)*""")
		normalized = normalized.replace('-', """(-|\s)*""")
		normalized = normalized.replace('|*#DUMMY#*|', '|-|')

		if aggressive == 1:
			pass
			# some more here
		return normalized
	#--------------------------------------------------------
	# write your own query generator and add it here:
	# use compile() for speedup
	# must escape strings before use !!
	# ORDER BY !
	# FIXME: what about "< 40" ?
	#--------------------------------------------------------
	def __make_simple_query(self, raw):
		"""Compose queries if search term seems unambigous."""
		_log.Log(gmLog.lData, '__make_simple_query("%s")' % raw)

		queries = []

		# "<digits>" - GnuMed patient PK or DOB
		if re.match("^(\s|\t)*\d+(\s|\t)*$", raw):
			tmp = raw.strip()
			queries.append(["SELECT * FROM v_basic_person WHERE pk_identity = '%s'" % tmp])
			queries.append(["SELECT * FROM v_basic_person WHERE dob='%s'::timestamp" % raw])
			return queries

		# "#<di git  s>" - GnuMed patient PK
		if re.match("^(\s|\t)*#(\d|\s|\t)+$", raw):
			tmp = raw.replace('#', '')
			tmp = tmp.strip()
			tmp = tmp.replace(' ', '')
			tmp = tmp.replace('\t', '')
			# this seemingly stupid query ensures the PK actually exists
			queries.append(["SELECT * FROM v_basic_person WHERE pk_identity = '%s'" % tmp])
			# but might also be an external ID
			tmp = raw.replace('#', '')
			tmp = tmp.strip()
			tmp = tmp.replace(' ', '*#DUMMY#*')
			tmp = tmp.replace('\t', '*#DUMMY#*')
			tmp = tmp.replace('*#DUMMY#*', '(\s|\t|-|/)*')
			queries.append(["select vba.* from lnk_identity2ext_id li2ei, v_basic_person vba where vba.pk_identity = li2ei.id_identity and li2ei.external_id ~* '^%s'" % tmp])
			queries.append(["select vba.* from lnk_identity2ext_id li2ei, v_basic_person vba where vba.pk_identity = li2ei.id_identity and li2ei.external_id ~* '%s'" % tmp])
			return queries

		# "#<di/git s/orc-hars>" - external ID (or PUPIC)
		if re.match("^(\s|\t)*#.+$", raw):
			tmp = raw.replace('#', '')
			tmp = tmp.strip()
			tmp = tmp.replace(' ', '*#DUMMY#*')
			tmp = tmp.replace('\t', '*#DUMMY#*')
			tmp = tmp.replace('-', '*#DUMMY#*')
			tmp = tmp.replace('/', '*#DUMMY#*')
			tmp = tmp.replace('*#DUMMY#*', '(\s|\t|-|/)*')
			queries.append(["select vba.* from lnk_identity2ext_id li2ei, v_basic_person vba where vba.pk_identity = li2ei.id_identity and li2ei.external_id ~* '%s'" % tmp])
			queries.append(["select vba.* from lnk_identity2ext_id li2ei, v_basic_person vba where vba.pk_identity = li2ei.id_identity and li2ei.external_id ~* '%s'" % tmp])
			return queries

		# "<d igi ts>" - DOB or patient PK
		if re.match("^(\d|\s|\t)+$", raw):
			queries.append(["SELECT * FROM v_basic_person WHERE dob='%s'::timestamp" % raw])
			tmp = raw.replace(' ', '')
			tmp = tmp.replace('\t', '')
			queries.append(["SELECT * FROM v_basic_person WHERE pk_identity LIKE '%s%%'" % tmp])
			return queries

		# "<Z(.|/|-/ )I  FF ERN>" - DOB
		if re.match("^(\s|\t)*\d+(\s|\t|\.|\-|/)*\d+(\s|\t|\.|\-|/)*\d+(\s|\t|\.)*$", raw):
			tmp = raw.replace(' ', '')
			tmp = tmp.replace('\t', '')
			# apparently not needed due to PostgreSQL smarts...
			#tmp = tmp.replace('-', '.')
			#tmp = tmp.replace('/', '.')
			queries.append(["SELECT * FROM v_basic_person WHERE dob='%s'::timestamp" % tmp])
			return queries

		# " , <alpha>" - first name
		if re.match("^(\s|\t)*,(\s|\t)*([^0-9])+(\s|\t)*$", raw):
			tmp = raw.split(',')[1].strip()
			tmp = self.__normalize(tmp)
			queries.append(["SELECT DISTINCT ON (id_identity) vbp.* FROM names, v_basic_person vbp WHERE names.firstnames ~ '^%s' and vbp.pk_identity = names.id_identity" % self.__make_sane_caps(tmp)])
			queries.append(["SELECT DISTINCT ON (id_identity) vbp.* FROM names, v_basic_person vbp WHERE names.firstnames ~ '^%s' and vbp.pk_identity = names.id_identity" % tmp])
			return queries

		# "*|$<...>" - DOB
		if re.match("^(\s|\t)*(\*|\$).+$", raw):
			tmp = raw.replace('*', '')
			tmp = tmp.replace('$', '')
			queries.append(["SELECT * FROM v_basic_person WHERE dob='%s'::timestamp" % tmp])
			return queries

		return None
	#--------------------------------------------------------
	# generic, locale independant queries
	#--------------------------------------------------------
	def __generate_queries_generic(self, data = None):
		"""Generate generic queries.

		- not locale dependant
		- data -> firstnames, lastnames, dob, gender
		"""
		_log.Log(gmLog.lData, '__generate_queries_generic("%s")' % data)

		if data is None:
			return []

		vals = {}
		where_snippets = []
		try:
			data['firstnames']
			where_snippets.append('firstnames=%(firstnames)s')
		except KeyError:
			pass
		try:
			data['lastnames']
			where_snippets.append('lastnames=%(lastnames)s')
		except KeyError:
			pass
		queries = []
		if where_snippets:
			queries.append(['select id_identity from names where %s' % ' and '.join(where_snippets)])
		where_snippets = []
		try:
			data['dob']
			where_snippets.append("dob=%(dob)s::timestamp")
		except KeyError:
			pass
		try:
			data['gender']
			where_snippets.append('gender=%(gender)s')
		except KeyError:
			pass

		queries.append(['select * from v_basic_person where %s' % ' and '.join(where_snippets)])
		# sufficient data ?
		if len(queries) == 0:
			_log.Log(gmLog.lErr, 'invalid search dict structure')
			_log.Log(gmLog.lData, data)
			return []
		# shall we mogrify name parts ? probably not
		
		return queries
	#--------------------------------------------------------
	# queries for DE
	#--------------------------------------------------------
	def __generate_queries_de(self, a_search_term = None):
		_log.Log(gmLog.lData, '__generate_queries_de("%s")' % a_search_term)

		if a_search_term is None:
			return []

		# check to see if we get away with a simple query ...
		queries = self.__make_simple_query(a_search_term)
		if queries is not None:
			return queries

		_log.Log(gmLog.lData, '__generate_queries_de() again')

		# no we don't
		queries = []

		# replace Umlauts
		normalized = self.__normalize(a_search_term)

		# "<CHARS>" - single name part
		# yes, I know, this is culture specific (did you read the docs ?)
		if re.match("^(\s|\t)*[a-zäöüßéáúóçøA-ZÄÖÜÇØ]+(\s|\t)*$", a_search_term):
			# there's no intermediate whitespace due to the regex
			tmp = normalized.strip()
			# assumption: this is a last name
			queries.append(["SELECT DISTINCT ON (id_identity) vbp.* FROM v_basic_person vbp, names n WHERE vbp.pk_identity = n.id_identity and n.lastnames  ~ '^%s'" % self.__make_sane_caps(tmp)])
			queries.append(["SELECT DISTINCT ON (id_identity) vbp.* FROM v_basic_person vbp, names n WHERE vbp.pk_identity = n.id_identity and n.lastnames  ~* '^%s'" % tmp])
			# assumption: this is a first name
			queries.append(["SELECT DISTINCT ON (id_identity) vbp.* FROM v_basic_person vbp, names n WHERE vbp.pk_identity = n.id_identity and n.firstnames ~ '^%s'" % self.__make_sane_caps(tmp)])
			queries.append(["SELECT DISTINCT ON (id_identity) vbp.* FROM v_basic_person vbp, names n WHERE vbp.pk_identity = n.id_identity and n.firstnames ~* '^%s'" % tmp])
			# name parts anywhere in name
			queries.append(["SELECT DISTINCT ON (id_identity) vbp.* FROM v_basic_person vbp, names n WHERE vbp.pk_identity = n.id_identity and n.firstnames || n.lastnames ~* '%s'" % tmp])
			return queries

		# try to split on (major) part separators
		parts_list = re.split(",|;", normalized)

		# only one "major" part ? (i.e. no ",;" ?)
		if len(parts_list) == 1:
			# re-split on whitespace
			sub_parts_list = re.split("\s*|\t*", normalized)

			# parse into name/date parts
			date_count = 0
			name_parts = []
			for part in sub_parts_list:
				# any digit signifies a date
				# FIXME: what about "<40" ?
				if re.search("\d", part):
					date_count = date_count + 1
					date_part = part
				else:
					name_parts.append(part)

			# exactly 2 words ?
			if len(sub_parts_list) == 2:
				# no date = "first last" or "last first"
				if date_count == 0:
					# assumption: first last
					queries.append([
						"SELECT DISTINCT ON (id_identity) vbp.* FROM v_basic_person vbp, names n WHERE vbp.pk_identity = n.id_identity and n.firstnames ~ '^%s' AND n.lastnames ~ '^%s'" % (self.__make_sane_caps(name_parts[0]), self.__make_sane_caps(name_parts[1]))
					])
					queries.append([
						 "SELECT DISTINCT ON (id_identity) vbp.* FROM v_basic_person vbp, names n WHERE vbp.pk_identity = n.id_identity and n.firstnames ~* '^%s' AND n.lastnames ~* '^%s'" % (name_parts[0], name_parts[1])
					])
					# assumption: last first
					queries.append([
						"SELECT DISTINCT ON (id_identity) vbp.* FROM v_basic_person vbp, names n WHERE vbp.pk_identity = n.id_identity and n.firstnames ~ '^%s' AND n.lastnames ~ '^%s'" % (self.__make_sane_caps(name_parts[1]), self.__make_sane_caps(name_parts[0]))
					])
					queries.append([
						"SELECT DISTINCT ON (id_identity) vbp.* FROM v_basic_person vbp, names n WHERE vbp.pk_identity = n.id_identity and n.firstnames ~* '^%s' AND n.lastnames ~* '^%s'" % (name_parts[1], name_parts[0])
					])
					# name parts anywhere in name - third order query ...
					queries.append([
						"SELECT DISTINCT ON (id_identity) vbp.* FROM v_basic_person vbp, names n WHERE vbp.pk_identity = n.id_identity and n.firstnames || n.lastnames ~* '%s' AND firstnames || n.lastnames ~* '%s'" % (name_parts[0], name_parts[1])
					])
					return queries
				# FIXME: either "name date" or "date date"
				_log.Log(gmLog.lErr, "don't know how to generate queries for [%s]" % a_search_term)
				return queries

			# exactly 3 words ?
			if len(sub_parts_list) == 3:
				# special case: 3 words, exactly 1 of them a date, no ",;"
				if date_count == 1:
					# assumption: first, last, dob - first order
					queries.append([
						"SELECT DISTINCT ON (id_identity) vbp.* FROM v_basic_person vbp, names n WHERE vbp.pk_identity = n.id_identity and n.firstnames ~ '^%s' AND n.lastnames ~ '^%s' AND dob='%s'::timestamp" % (self.__make_sane_caps(name_parts[0]), self.__make_sane_caps(name_parts[1]), date_part)
					])
					queries.append([
						"SELECT DISTINCT ON (id_identity) vbp.* FROM v_basic_person vbp, names n WHERE vbp.pk_identity = n.id_identity and firstnames ~* '^%s' AND n.lastnames ~* '^%s' AND dob='%s'::timestamp" % (name_parts[0], name_parts[1], date_part)
					])
					# assumption: last, first, dob - second order query
					queries.append([
						"SELECT DISTINCT ON (id_identity) vbp.* FROM v_basic_person vbp, names n WHERE vbp.pk_identity = n.id_identity and n.firstnames ~ '^%s' AND n.lastnames ~ '^%s' AND dob='%s'::timestamp" % (self.__make_sane_caps(name_parts[1]), self.__make_sane_caps(name_parts[0]), date_part)
					])
					queries.append([
						"SELECT DISTINCT ON (id_identity) vbp.* FROM v_basic_person vbp, names n WHERE vbp.pk_identity = n.id_identity and n.firstnames ~* '^%s' AND n.lastnames ~* '^%s' AND dob='%s'::timestamp" % (name_parts[1], name_parts[0], date_part)
					])
					# name parts anywhere in name - third order query ...
					queries.append([
						"SELECT DISTINCT ON (id_identity) vbp.* FROM v_basic_person vbp, names n WHERE vbp.pk_identity = n.id_identity and n.firstnames || n.lastnames ~* '%s' AND n.firstnames || n.lastnames ~* '%s' AND dob='%s'::timestamp" % (name_parts[0], name_parts[1], date_part)
					])
					return queries
				# FIXME: "name name name" or "name date date"
				_log.Log(gmLog.lErr, "don't know how to generate queries for [%s]" % a_search_term)
				return queries

			# FIXME: no ',;' but neither "name name" nor "name name date"
			_log.Log(gmLog.lErr, "don't know how to generate queries for [%s]" % a_search_term)
			return queries

		# more than one major part (separated by ';,')
		else:
			# parse into name and date parts
			date_parts = []
			name_parts = []
			name_count = 0
			for part in parts_list:
				# any digits ?
				if re.search("\d+", part):
					# FIXME: parse out whitespace *not* adjacent to a *word*
					date_parts.append(part)
				else:
					tmp = part.strip()
					tmp = re.split("\s*|\t*", tmp)
					name_count = name_count + len(tmp)
					name_parts.append(tmp)

			wheres = []
			# first, handle name parts
			# special case: "<date(s)>, <name> <name>, <date(s)>"
			if (len(name_parts) == 1) and (name_count == 2):
				# usually "first last"
				wheres.append([
					"firstnames ~ '^%s'" % self.__make_sane_caps(name_parts[0][0]),
					"lastnames ~ '^%s'"  % self.__make_sane_caps(name_parts[0][1])
				])
				wheres.append([
					"firstnames ~* '^%s'" % name_parts[0][0],
					"lastnames ~* '^%s'" % name_parts[0][1]
				])
				# but sometimes "last first""
				wheres.append([
					"firstnames ~ '^%s'" % self.__make_sane_caps(name_parts[0][1]),
					"lastnames ~ '^%s'"  % self.__make_sane_caps(name_parts[0][0])
				])
				wheres.append([
					"firstnames ~* '^%s'" % name_parts[0][1],
					"lastnames ~* '^%s'" % name_parts[0][0]
				])
				# or even substrings anywhere in name
				wheres.append([
					"firstnames || lastnames ~* '%s'" % name_parts[0][0],
					"firstnames || lastnames ~* '%s'" % name_parts[0][1]
				])

			# special case: "<date(s)>, <name(s)>, <name(s)>, <date(s)>"
			elif len(name_parts) == 2:
				# usually "last, first"
				wheres.append([
					"firstnames ~ '^%s'" % string.join(map(self.__make_sane_caps, name_parts[1]), ' '),
					"lastnames ~ '^%s'"  % string.join(map(self.__make_sane_caps, name_parts[0]), ' ')
				])
				wheres.append([
					"firstnames ~* '^%s'" % string.join(name_parts[1], ' '),
					"lastnames ~* '^%s'" % string.join(name_parts[0], ' ')
				])
				# but sometimes "first, last"
				wheres.append([
					"firstnames ~ '^%s'" % string.join(map(self.__make_sane_caps, name_parts[0]), ' '),
					"lastnames ~ '^%s'"  % string.join(map(self.__make_sane_caps, name_parts[1]), ' ')
				])
				wheres.append([
					"firstnames ~* '^%s'" % string.join(name_parts[0], ' '),
					"lastnames ~* '^%s'" % string.join(name_parts[1], ' ')
				])
				# or even substrings anywhere in name
				wheres.append([
					"firstnames || lastnames ~* '%s'" % string.join(name_parts[0], ' '),
					"firstnames || lastnames ~* '%s'" % string.join(name_parts[1], ' ')
				])

			# big trouble - arbitrary number of names
			else:
				# FIXME: deep magic, not sure of rationale ...
				if len(name_parts) == 1:
					for part in name_parts[0]:
						wheres.append([
							"firstnames || lastnames ~* '%s'" % part
						])
						wheres.append([
							"firstnames || lastnames ~* '%s'" % part
						])
				else:
					tmp = []
					for part in name_parts:
						tmp.append(string.join(part, ' '))
					for part in tmp:
						wheres.append([
							"firstnames || lastnames ~* '%s'" % part
						])
						wheres.append([
							"firstnames || lastnames ~* '%s'" % part
						])

			# secondly handle date parts
			# FIXME: this needs a considerable smart-up !
			if len(date_parts) == 1:
				if len(wheres) > 0:
					wheres[0].append("dob='%s'::timestamp" % date_parts[0])
				else:
					wheres.append([
						"dob='%s'::timestamp" % date_parts[0]
					])
				if len(wheres) > 1:
					wheres[1].append("dob='%s'::timestamp" % date_parts[0])
				else:
					wheres.append([
						"dob='%s'::timestamp" % date_parts[0]
					])
			elif len(date_parts) > 1:
				if len(wheres) > 0:
					wheres[0].append("dob='%s'::timestamp" % date_parts[0])
					wheres[0].append("date_trunc('day', identity.deceased) LIKE (select timestamp '%s'" % date_parts[1])
				else:
					wheres.append([
						"dob='%s'::timestamp" % date_parts[0],
						"date_trunc('day', identity.deceased) LIKE (select timestamp '%s'" % date_parts[1]
					])
				if len(wheres) > 1:
					wheres[1].append("dob='%s'::timestamp" % date_parts[0])
					wheres[1].append("date_trunc('day', identity.deceased) LIKE (select timestamp '%s')" % date_parts[1])
				else:
					wheres.append([
						"dob='%s'::timestamp" % date_parts[0],
						"identity.deceased='%s'::timestamp" % date_parts[1]
					])

			# and finally generate the queries ...
			for where_clause in wheres:
				if len(where_clause) > 0:
					queries.append([
						"SELECT * FROM v_basic_person WHERE %s" % ' AND '.join(where_clause)
					])
				else:
					queries.append([])
			return queries

		return []
#============================================================
# convenience functions
#============================================================
def dob2medical_age(dob):
	"""format patient age in a hopefully meaningful way"""

	age = mxDT.Age(mxDT.now(), dob)

	if age.years > 0:
		return "%sy%sm" % (age.years, age.months)
	weeks = age.days / 7
	if weeks > 4:
		return "%sm%sw" % (age.months, age.weeks)
	if weeks > 1:
		return "%sd" % age.days
	if age.days > 1:
		return "%sd (%sh)" % (age.days, age.hours)
	if age.hours > 3:
		return "%sh" % age.hours
	if age.hours > 0:
		return "%sh%sm" % (age.hours, age.minutes)
	if age.minutes > 5:
		return "%sm" % (age.minutes)
	return "%sm%ss" % (age.minutes, age.seconds)
#============================================================
def create_identity(gender=None, dob=None, lastnames=None, firstnames=None):
	cmd1 = """insert into identity (gender, dob)
values (%s, coalesce(%s, CURRENT_TIMESTAMP))"""
	cmd2 = """insert into names (id_identity, lastnames, firstnames)
values (currval('identity_pk_seq'), coalesce(%s, 'xxxDEFAULTxxx'), coalesce(%s, 'xxxDEFAULTxxx'))"""
	cmd3 = """select currval('identity_pk_seq')"""

	successful, data = gmPG.run_commit2 (
		link_obj = 'personalia',
		queries = [
			(cmd1, [gender, dob]),
			(cmd2, [lastnames, firstnames]),
			(cmd3, [])
		],
		max_tries = 2
	)
	if not successful:
		_log.Log(gmLog.lPanic, 'failed to create identity: %s' % data)
		return None
	rows, idx = data
	return cIdentity(aPK_obj=rows[0][0])
#============================================================
def create_dummy_identity():	
	cmd1 = "insert into identity(gender, dob) values('xxxDEFAULTxxx', CURRENT_TIMESTAMP)"
	cmd2 = "select currval('identity_id_seq')"

	data = gmPG.run_commit('personalia', [(cmd1, []), (cmd2, [])])
	if data is None:
		_log.Log(gmLog.lPanic, 'failed to create dummy identity')
		return None
	return gmDemographicRecord.cIdentity (aPK_obj = int(data[0][0]))
#============================================================
def set_active_patient(person = None):
	"""Set active patient.

	If person is -1 the active patient will be unset.
	"""
	if person is None:
		_log.Log(gmLog.lErr, 'programming error: anID is None, must be -1, cPerson instance or cIdentity instance')
		return False
	if isinstance(person, cIdentity):
		person = cPerson(identity=person)
	# attempt to switch
	tstart = time.time()
	try:
		pat = gmCurrentPatient(person)
	except:
		_log.LogException('error changing active patient', sys.exc_info())
		return False
	duration = time.time() - tstart
	_log.Log(gmLog.lData, "set_active_patient took %3.3f seconds" % duration)
	return True
#------------------------------------------------------------
def prompted_input(prompt, default=None):
	"""Obtains entry from standard input.

	promp - Promt text to display in standard output
	default - Default value (for user to press only intro)
	"""
	msg = '%s (CTRL-C aborts) [%s]: ' % (prompt, default)
	try:
		usr_input = raw_input(msg)
	except KeyboardInterrupt:
		return None
	if usr_input == '':
		return default
	return usr_input
#------------------------------------------------------------
def ask_for_patient():
	"""Text mode UI function to ask for patient."""
	person_searcher = cPatientSearcher_SQL()
	search_fragment = prompted_input("\nEnter person search term (eg. 'Kirk') or leave blank to exit")
	if search_fragment in ['bye', None]:
		print "user cancelled patient search"
		return None
	persons = person_searcher.get_persons(search_term = search_fragment)
	if persons is None or len(persons) == 0:
		prompted_input("No patient matches the query term. Press any key to continue.")
		return None
	elif len(persons) > 1:
		prompted_input("Several patients match the query term. Press any key to continue.")
		return None
	person = persons[0]
	try:
		patient = gmCurrentPatient(person)
	except:
		_log.LogException('Unable to set up patient [%s]' % str(person), sys.exc_info())
		print "Cannot set up active patient."
		print "Person:", person
		prompted_input("Press any key to continue.")
		return None
	return patient
#============================================================
def get_gender_list():
	global __gender_idx
	global __gender_list
	if __gender_list is None:
		cmd = "select tag, l10n_tag, label, l10n_label, sort_weight from v_gender_labels order by sort_weight desc"
		__gender_list, __gender_idx = gmPG.run_ro_query('personalia', cmd, True)
		if __gender_list is None:
			_log.Log(gmLog.lPanic, 'cannot retrieve gender values from database')
	return (__gender_list, __gender_idx)
#============================================================
# main/testing
#============================================================
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)
	
	 # create patient
	print '\n\nCreating identity...'
	new_identity = create_identity(gender='m', dob='2005-01-01', lastnames='test lastnames', firstnames='test firstnames')
	print 'Identity created: %s' % new_identity
	
	print '\nSetting title and gender...'
	new_identity['title'] = 'test title';
	new_identity['gender'] = 'f';
	new_identity.save_payload()
	print 'Refetching identity from db: %s' % cIdentity(aPK_obj=new_identity['pk_identity'])
	
	print '\nGetting all names...'
	for a_name in new_identity.get_all_names():
		print a_name
	print 'Setting nickname...'
	new_identity.set_nickname(nickname='test nickname')
	print 'Refetching all names...'
	for a_name in new_identity.get_all_names():
		print a_name	
	 
	print '\nIdentity occupations: %s' % new_identity['occupations']
	print 'Creating identity occupation...'
	new_identity.link_occupation('test occupation')
	print 'Identity occupations: %s' % new_identity['occupations']
		
	searcher = cPatientSearcher_SQL()
	p_data = None
	while 1:
		myPatient = ask_for_patient()
		if myPatient is None:
			break
		print "ID       ", myPatient['id']
		identity = myPatient.get_identity()
		print "identity  ", identity
		print "get_names() apparently missing ?"
#		print "name     ", identity.get_names(1)
		print "doc ids  ", myPatient['document id list']
		emr = myPatient.get_clinical_record()
		print "EMR      ", emr
		print "--------------------------------------"
	gmPG.ConnectionPool().StopListeners()
#============================================================
# $Log: gmPerson.py,v $
# Revision 1.24  2005-04-18 19:18:44  ncq
# - cleanup, link_occuption doesn't work right yet
#
# Revision 1.23  2005/04/18 16:07:11  cfmoro
# Improved sanity check in add_name
#
# Revision 1.22  2005/04/18 15:55:37  cfmoro
# added set_nickname method, test code and minor update string fixes
#
# Revision 1.21  2005/04/14 22:34:50  ncq
# - some streamlining of create_identity
#
# Revision 1.20  2005/04/14 19:27:20  cfmoro
# Added title param to create_identity, to cover al fields in basic patient details
#
# Revision 1.19  2005/04/14 19:04:01  cfmoro
# create_occupation -> add_occupation
#
# Revision 1.18  2005/04/14 18:58:14  cfmoro
# Added create occupation method and minor gender map clean up, to replace later by get_gender_list
#
# Revision 1.17  2005/04/14 18:23:59  ncq
# - get_gender_list()
#
# Revision 1.16  2005/04/14 08:51:13  ncq
# - add cIdentity/dob2medical_age() from gmDemographicRecord.py
# - make cIdentity inherit from cBusinessDBObject
# - add create_identity()
#
# Revision 1.15  2005/03/20 16:49:07  ncq
# - fix SQL syntax and do run all queries until identities found
# - we now find Richard
# - cleanup
#
# Revision 1.14  2005/03/18 07:44:10  ncq
# - queries fixed but logic needs more work !
#
# Revision 1.13  2005/03/16 12:57:26  sjtan
#
# fix import error.
#
# Revision 1.12  2005/03/08 16:43:58  ncq
# - allow a cIdentity instance to be passed to gmCurrentPatient
#
# Revision 1.11  2005/02/19 15:06:33  sjtan
#
# **kwargs should be passed for signal parameters.
#
# Revision 1.10  2005/02/15 18:29:03  ncq
# - test_result.id -> pk
#
# Revision 1.9  2005/02/13 15:23:31  ncq
# - v_basic_person.i_pk -> pk_identity
#
# Revision 1.8  2005/02/12 13:50:25  ncq
# - identity.id -> identity.pk and followup changes in v_basic_person
#
# Revision 1.7  2005/02/02 23:03:17  ncq
# - change "demographic record" to "identity"
# - dependant files still need being changed
#
# Revision 1.6  2005/02/01 19:27:56  ncq
# - more renaming, I think we are getting there, if you think about it it
#   seems "demographic record" really is "identity"
#
# Revision 1.5  2005/02/01 19:14:10  ncq
# - cleanup, internal renaming for consistency
# - reallow cPerson to be instantiated with PK but retain main instantiation mode with cIdentity
# - smarten up gmCurrentPatient() and re-add previous speedups
# - do use ask_for_patient() in unit test
#
# Revision 1.4  2005/02/01 10:16:07  ihaywood
# refactoring of gmDemographicRecord and follow-on changes as discussed.
#
# gmTopPanel moves to gmHorstSpace
# gmRichardSpace added -- example code at present, haven't even run it myself
# (waiting on some icon .pngs from Richard)
#
# Revision 1.3  2005/01/31 18:48:45  ncq
# - self._patient -> self._person
# - speedup
#
# Revision 1.2  2005/01/31 12:59:56  ncq
# - cleanup, improved comments
# - rename class gmPerson to cPerson
# - add helpers prompted_input() and ask_for_patient()
#
# Revision 1.1  2005/01/31 10:24:17  ncq
# - renamed from gmPatient.py
#
# Revision 1.56  2004/09/02 00:52:10  ncq
# - wait, #digits may still be an external ID search so allow for that
#
# Revision 1.55  2004/09/02 00:37:49  ncq
# - it's ~*, not *~
#
# Revision 1.54  2004/09/01 21:57:55  ncq
# - make search GnuMed primary key work
# - add search for arbitrary external ID via "#..."
# - fix regexing in __normalize() to avoid nested replacements
#
# Revision 1.53  2004/08/24 19:15:42  ncq
# - __normalize_soundalikes() -> __normalize() + improve (apostrophy/hyphen)
#
# Revision 1.52  2004/08/24 14:27:06  ncq
# - improve __normalize_soundalikes()
# - fix nasty bug: missing ] resulting in endless logging
# - prepare search on external id
#
# Revision 1.51  2004/08/20 13:28:16  ncq
# - cleanup/improve inline docs
# - allow gmCurrentPatient._patient to be reset to gmNull.cNull on aPKey = -1
# - teach patient searcher about ", something" to be first name
#
# Revision 1.50  2004/08/18 08:13:51  ncq
# - fixed encoding special comment
#
# Revision 1.49  2004/07/21 07:53:12  ncq
# - some cleanup in set_active_patient
#
# Revision 1.48  2004/07/20 10:09:44  ncq
# - a bit of cleanup here and there
# - use Null design pattern instead of None when no real
#   patient connected to gmCurrentPatient Borg
#
#   this allows us to forego all the tests for None as
#   Null() reliably does nothing no matter what you try,
#   eventually, this will allow us to remove all the
#   is_patient_avail checks in the frontend,
#   it also acts sanely for code forgetting to check
#   for a connected patient
#
# Revision 1.47  2004/07/20 01:01:44  ihaywood
# changing a patients name works again.
# Name searching has been changed to query on names rather than v_basic_person.
# This is so the old (inactive) names are still visible to the search.
# This is so when Mary Smith gets married, we can still find her under Smith.
# [In Australia this odd tradition is still the norm, even female doctors
# have their medical registration documents updated]
#
# SOAPTextCtrl now has popups, but the cursor vanishes (?)
#
# Revision 1.46  2004/07/15 23:30:11  ncq
# - 'clinical_record' -> get_clinical_record()
#
# Revision 1.45  2004/07/05 22:26:24  ncq
# - do some timings to find patient change time sinks
#
# Revision 1.44  2004/06/15 19:14:30  ncq
# - add cleanup() to current patient calling gmPerson.cleanup()
#
# Revision 1.43  2004/06/01 23:58:01  ncq
# - debugged dob handling in _make_queries_generic
#
# Revision 1.42  2004/06/01 07:50:56  ncq
# - typo fix
#
# Revision 1.41  2004/05/18 22:38:19  ncq
# - __patient -> _patient
#
# Revision 1.40  2004/05/18 20:40:11  ncq
# - streamline __init__ significantly
# - check return status of get_clinical_record()
# - self.patient -> self.__patient
#
# Revision 1.39  2004/04/11 10:14:36  ncq
# - fix b0rked dob/dod handling in query generation
# - searching by dob should now work
#
# Revision 1.38  2004/03/25 11:14:48  ncq
# - fix get_document_folder()
#
# Revision 1.37  2004/03/25 11:03:23  ncq
# - getActiveName -> get_names
#
# Revision 1.36  2004/03/25 09:47:56  ncq
# - fix whitespace breakage
#
# Revision 1.35  2004/03/23 15:04:59  ncq
# - merge Carlos' constraints into get_text_dump
# - add gmPatient.export_data()
#
# Revision 1.34  2004/03/20 19:44:50  ncq
# - do import gmI18N
# - only fetch i_id in queries
# - revert to returning flat list of ids from get_patient_ids, must have been Syan fallout, I assume
#
# Revision 1.33  2004/03/20 13:31:18  ncq
# - PostgreSQL has date_trunc, not datetrunc
#
# Revision 1.32  2004/03/20 13:14:36  ncq
# - sync data dict and named substs in __generate_queries_generic
#
# Revision 1.31  2004/03/20 13:05:20  ncq
# - we of course need to return results from __generate_queries_generic
#
# Revision 1.30  2004/03/20 12:49:55  ncq
# - support gender, too, in search_dict in get_patient_ids
#
# Revision 1.29  2004/03/20 12:32:51  ncq
# - check for query_lists is None in get_pat_ids
#
# Revision 1.28  2004/03/20 11:45:41  ncq
# - don't pass search_dict[id] to get_patient_ids()
#
# Revision 1.27  2004/03/20 11:10:46  ncq
# - where_snippets needs to be []
#
# Revision 1.26  2004/03/20 10:48:31  ncq
# - if search_dict given we need to pass it to run_ro_query
#
# Revision 1.25  2004/03/19 11:46:24  ncq
# - add search_term to get_pat_ids()
#
# Revision 1.24  2004/03/10 13:44:33  ncq
# - shouldn't just import gmI18N, needs fix, I guess
#
# Revision 1.23  2004/03/10 12:56:01  ihaywood
# fixed sudden loss of main.shadow
# more work on referrals,
#
# Revision 1.22  2004/03/10 00:09:51  ncq
# - cleanup imports
#
# Revision 1.21  2004/03/09 07:34:51  ihaywood
# reactivating plugins
#
# Revision 1.20  2004/03/07 23:52:32  ncq
# - get_document_folder()
#
# Revision 1.19  2004/03/04 19:46:53  ncq
# - switch to package based import: from Gnumed.foo import bar
#
# Revision 1.18  2004/02/25 09:46:20  ncq
# - import from pycommon now, not python-common
#
# Revision 1.17  2004/02/18 06:36:04  ihaywood
# bugfixes
#
# Revision 1.16  2004/02/17 10:38:27  ncq
# - create_new_patient() -> xlnk_patient_in_clinical()
#
# Revision 1.15  2004/02/14 00:37:10  ihaywood
# Bugfixes
# 	- weeks = days / 7
# 	- create_new_patient to maintain xlnk_identity in historica
#
# Revision 1.14  2004/02/05 18:38:56  ncq
# - add .get_ID(), .is_locked()
# - set_active_patient() convenience function
#
# Revision 1.13  2004/02/04 00:57:24  ncq
# - added UI-independant patient search logic taken from gmPatientSelector
# - we can now have a console patient search field just as powerful as
#   the GUI version due to it running the same business logic code
# - also fixed _make_simple_query() results
#
# Revision 1.12  2004/01/18 21:43:00  ncq
# - speed up get_clinical_record()
#
# Revision 1.11  2004/01/12 16:21:03  ncq
# - _get_clini* -> get_clini*
#
# Revision 1.10  2003/11/20 01:17:14  ncq
# - consensus was that N/A is no good for identity.gender hence
#   don't use it in create_dummy_identity anymore
#
# Revision 1.9  2003/11/18 16:35:17  ncq
# - correct create_dummy_identity()
# - move create_dummy_relative to gmDemographicRecord and rename it to link_new_relative
# - remove reload keyword from gmCurrentPatient.__init__() - if you need it your logic
#   is screwed
#
# Revision 1.8  2003/11/17 10:56:34  sjtan
#
# synced and commiting.
#
# Revision 1.7  2003/11/16 10:58:36  shilbert
# - corrected typo
#
# Revision 1.6  2003/11/09 16:39:34  ncq
# - get handler now 'demographic record', not 'demographics'
#
# Revision 1.5  2003/11/04 00:07:40  ncq
# - renamed gmDemographics
#
# Revision 1.4  2003/10/26 17:35:04  ncq
# - conceptual cleanup
# - IMHO, patient searching and database stub creation is OUTSIDE
#   THE SCOPE OF gmPerson and gmDemographicRecord
#
# Revision 1.3  2003/10/26 11:27:10  ihaywood
# gmPatient is now the "patient stub", all demographics stuff in gmDemographics.
#
# Ergregious breakages are fixed, but needs more work
#
# Revision 1.2  2003/10/26 01:38:06  ncq
# - gmTmpPatient -> gmPatient, cleanup
#
# Revision 1.1  2003/10/26 01:26:45  ncq
# - now go live, this is for real
#
# Revision 1.41  2003/10/19 10:42:57  ihaywood
# extra functions
#
# Revision 1.40  2003/09/24 08:45:40  ihaywood
# NewAddress now functional
#
# Revision 1.39  2003/09/23 19:38:03  ncq
# - cleanup
# - moved GetAddressesType out of patient class - it's a generic function
#
# Revision 1.38  2003/09/23 12:49:56  ncq
# - reformat, %d -> %s
#
# Revision 1.37  2003/09/23 12:09:26  ihaywood
# Karsten, we've been tripping over each other again
#
# Revision 1.36  2003/09/23 11:31:12  ncq
# - properly use ro_run_query()s returns
#
# Revision 1.35  2003/09/22 23:29:30  ncq
# - new style run_ro_query()
#
# Revision 1.34  2003/09/21 12:46:30  ncq
# - switched most ro queries to run_ro_query()
#
# Revision 1.33  2003/09/21 10:37:20  ncq
# - bugfix, cleanup
#
# Revision 1.32  2003/09/21 06:53:40  ihaywood
# bugfixes
#
# Revision 1.31  2003/09/17 11:08:30  ncq
# - cleanup, fix type "personaliaa"
#
# Revision 1.30  2003/09/17 03:00:59  ihaywood
# support for local inet connections
#
# Revision 1.29  2003/07/19 20:18:28  ncq
# - code cleanup
# - explicitely cleanup EMR when cleaning up patient
#
# Revision 1.28  2003/07/09 16:21:22  ncq
# - better comments
#
# Revision 1.27  2003/06/27 16:04:40  ncq
# - no ; in DB-API
#
# Revision 1.26  2003/06/26 21:28:02  ncq
# - fatal->verbose, %s; quoting bug
#
# Revision 1.25  2003/06/22 16:18:34  ncq
# - cleanup, send signal prior to changing the active patient, too
#
# Revision 1.24  2003/06/19 15:24:23  ncq
# - add is_connected check to gmCurrentPatient to find
#   out whether there's a live patient record attached
# - typo fix
#
# Revision 1.23  2003/06/01 14:34:47  sjtan
#
# hopefully complies with temporary model; not using setData now ( but that did work).
# Please leave a working and tested substitute (i.e. select a patient , allergy list
# will change; check allergy panel allows update of allergy list), if still
# not satisfied. I need a working model-view connection ; trying to get at least
# a basically database updating version going .
#
# Revision 1.22  2003/06/01 13:34:38  ncq
# - reinstate remote app locking
# - comment out thread lock for now but keep code
# - setting gmCurrentPatient is not how it is supposed to work (I think)
#
# Revision 1.21  2003/06/01 13:20:32  sjtan
#
# logging to data stream for debugging. Adding DEBUG tags when work out how to use vi
# with regular expression groups (maybe never).
#
# Revision 1.20  2003/06/01 01:47:32  sjtan
#
# starting allergy connections.
#
# Revision 1.19  2003/04/29 15:24:05  ncq
# - add _get_clinical_record handler
# - add _get_API API discovery handler
#
# Revision 1.18  2003/04/28 21:36:33  ncq
# - compactify medical age
#
# Revision 1.17  2003/04/25 12:58:58  ncq
# - dynamically handle supplied data in create_patient but added some sanity checks
#
# Revision 1.16  2003/04/19 22:54:46  ncq
# - cleanup
#
# Revision 1.15  2003/04/19 14:59:04  ncq
# - attribute handler for "medical age"
#
# Revision 1.14  2003/04/09 16:15:44  ncq
# - get handler for age
#
# Revision 1.13  2003/04/04 20:40:51  ncq
# - handle connection errors gracefully
# - let gmCurrentPatient be a borg but let the person object be an attribute thereof
#   instead of an ancestor, this way we can safely do __init__(aPKey) where aPKey may or
#   may not be None
#
# Revision 1.12  2003/03/31 23:36:51  ncq
# - adapt to changed view v_basic_person
#
# Revision 1.11  2003/03/27 21:08:25  ncq
# - catch connection errors
# - create_patient rewritten
# - cleanup on __del__
#
# Revision 1.10  2003/03/25 12:32:31  ncq
# - create_patient helper
# - __getTitle
#
# Revision 1.9  2003/02/21 16:42:02  ncq
# - better error handling on query generation
#
# Revision 1.8  2003/02/18 02:41:54  ncq
# - helper function get_patient_ids, only structured search term search implemented so far
#
# Revision 1.7  2003/02/17 16:16:13  ncq
# - document list -> document id list
#
# Revision 1.6  2003/02/11 18:21:36  ncq
# - move over to __getitem__ invoking handlers
# - self.format to be used as an arbitrary format string
#
# Revision 1.5  2003/02/11 13:03:44  ncq
# - don't change patient on patient not found ...
#
# Revision 1.4  2003/02/09 23:38:21  ncq
# - now actually listens patient selectors, commits old patient and
#   inits the new one if possible
#
# Revision 1.3  2003/02/08 00:09:46  ncq
# - finally starts being useful
#
# Revision 1.2  2003/02/06 15:40:58  ncq
# - hit hard the merge wall
#
# Revision 1.1  2003/02/01 17:53:12  ncq
# - doesn't do anything, just to show people where I am going
#
