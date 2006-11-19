# -*- coding: latin-1 -*-
"""GNUmed patient objects.

This is a patient object intended to let a useful client-side
API crystallize from actual use in true XP fashion.
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmPerson.py,v $
# $Id: gmPerson.py,v 1.91 2006-11-19 11:02:33 ncq Exp $
__version__ = "$Revision: 1.91 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

# std lib
import sys, os.path, time, re, string, types, datetime

# 3rd party
import mx.DateTime as mxDT

# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')

from Gnumed.pycommon import gmLog, gmExceptions, gmSignals, gmDispatcher, gmBorg, gmI18N, gmNull, gmBusinessDBObject, gmCfg, gmTools, gmPG2, gmMatchProvider
from Gnumed.business import gmMedDoc, gmDemographicRecord, gmProviderInbox

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

__gender_list = None
__gender_idx = None
__comm_list = None

__gender2salutation_map = None

#============================================================
class cDTO_person(object):

	# FIXME: make this function as a mapping type

	#--------------------------------------------------------
	def __str__(self):
		return '<%s @ %s: %s %s (%s) %s>' % (self.__class__.__name__, id(self), self.firstnames, self.lastnames, self.gender, self.dob)
	#--------------------------------------------------------
	def __setattr__(self, attr, val):
		"""Do some sanity checks on self.* access."""
		if attr in ['firstname', 'lastname']:
			object.__setattr__(self, attr, str(val))
			return

		if attr == 'gender':
			glist, idx = get_gender_list()
			for gender in glist:
				if str(val) in [gender[0], gender[1], gender[2], gender[3]]:
					val = gender[idx['tag']]
					object.__setattr__(self, attr, str(val))
					return
			raise ValueError(_('invalid gender: [%s]') % str(val))

		if attr == 'dob':
			# FIXME: move to datetime
			if isinstance(val, mxDT.DateTimeType):
				object.__setattr__(self, attr, val)
				return
			raise TypeError(_('invalid type for DOB (must be mx.DateTime): %s [%s]') % (type(val), str(val)))

		object.__setattr__(self, attr, str(val))
	#--------------------------------------------------------
	def __getitem__(self, attr):
		return getattr(self, attr)
	#--------------------------------------------------------
	def keys(self):
		return 'firstnames lastnames dob gender'.split()
#============================================================
class cIdentity (gmBusinessDBObject.cBusinessDBObject):
	_cmd_fetch_payload = u"select * from dem.v_basic_person where pk_identity=%s"
	_cmds_store_payload = [
		u"""update dem.identity set
			title=%(title)s,
			dob=%(dob)s,
			cob=%(cob)s,
			gender=%(gender)s,
			fk_marital_status = %(pk_marital_status)s,
			karyotype = %(karyotype)s,
			pupic = %(pupic)s
		where
			pk=%(pk_identity)s and
			xmin = %(xmin_identity)s""",
		u"""select xmin_identity from dem.v_basic_person where pk_identity=%(pk_identity)s"""
	]
	_updatable_fields = ["title", "dob", "cob", "gender", "pk_marital_status", "karyotype", "pupic"]
	_subtable_dml_templates = {
		'ext_ids': {
			'select': u"""
				select
					external_id as pk,
					fk_origin as id_type,
					comment,
					external_id,
					eeid.name as type,
					eeid.context as context
				from dem.lnk_identity2ext_id, dem.enum_ext_id_types eeid
				where id_identity = %s and fk_origin = eeid.pk""",
			'delete': u"delete from dem.lnk_identity2ext_id where id_identity = %s and external_id = %s",
			'insert': u"""
				insert into dem.lnk_identity2ext_id (external_id, fk_origin, comment, id_identity)
				values(%(external_id)s, %(id_type)s, %(comment)s, %(pk_master)s)"""
		},
		'comms': {
			'select': u"""
				select
					l2c.id_type,
					l2c.url,
					l2c.url as pk,
					l2c.is_confidential,
					ect.description as type
				from
					dem.lnk_identity2comm l2c,
					dem.enum_comm_types ect
				where
					l2c.id_identity = %s
					and ect.id = id_type""",
			'insert': u"SELECT dem.link_person_comm(%(pk_master)s, %(comm_medium)s, %(url)s, %(is_confidential)s)",
			'delete': u"delete from dem.lnk_identity2ext_id where id_identity = %s and url = %s"
		}
	}
	#--------------------------------------------------------
	def __setitem__(self, attribute, value):
		if attribute == 'dob':
			if type(value) != datetime.datetime:
				raise TypeError, '[%s]: type [%s] (%s) invalid for attribute [dob], must be datetime.datetime' % (self.__class__.__name__, type(value), value)
			if value.tzinfo is None:
				raise ValueError('datetime.datetime instance is lacking a time zone: [%s]' % dt.isoformat())
		gmBusinessDBObject.cBusinessDBObject.__setitem__(self, attribute, value)
	#--------------------------------------------------------
	def cleanup(self):
		pass
	#--------------------------------------------------------
	def getId(self):
		return self['pk_identity']
	#--------------------------------------------------------
	def get_active_name(self):
		"""
		Retrieve the patient's active name.
		"""
		try:
			self._ext_cache['names']
		except KeyError:
			# ensure the cache of names is created
			self.get_all_names()
		try:
			return self._ext_cache['names']['active']
		except:
			_log.Log(gmLog.lErr, 'cannot retrieve active name for patient [%s]' % self._payload[self._idx['pk_identity']])
			return None
	#--------------------------------------------------------
	def get_all_names(self):
		"""
		Retrieve a list containing all the patient's names, in the
		form of a dictionary of keys: first, last, title, preferred.
		"""
		try:
			return self._ext_cache['names']['all']
		except KeyError:
			pass
		# create cache of names
		self._ext_cache['names'] = {}
		# fetch names from backend
		pk_identity = self._payload[self._idx['pk_identity']]
		cmd = u"""
			select
				n.firstnames,
				n.lastnames,
				i.title,
				n.preferred,
				n.active
			from
				dem.names n, dem.identity i
			where
				n.id_identity=%s and
				i.pk=%s"""
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [pk_identity, pk_identity]}])
		# fill in cache with values
		self._ext_cache['names'] = {}
		self._ext_cache['names']['all'] = []
		self._ext_cache['names']['active'] = None
		if len(rows) == 0:
			# no names registered for patient
			return [{'first': '**?**', 'last': '**?**', 'title': '**?**', 'preferred':'**?**'}]
		for row in rows:
			name = {'first': row[0], 'last': row[1], 'title': row[2], 'preferred':row[3]}
			# fill 'all' names cache
			self._ext_cache['names']['all'].append(name)
			if row[4]:
				# fill 'active' name cache
				self._ext_cache['names']['active'] = name
		return self._ext_cache['names']['all']
	#--------------------------------------------------------
	def get_description(self):
		"""Return descriptive string for patient."""
		title = self._payload[self._idx['title']]
		if title is None:
			title = map_gender2salutation(self._payload[self._idx['gender']]) + u' '
		else:
			title = title[:4] + u'.'
		nick = self._payload[self._idx['preferred']]
		if nick is None:
			nick = u''
		else:
			nick = u' (%s)' % nick
		return u'%s%s %s%s' % (title, self._payload[self._idx['firstnames']], self._payload[self._idx['lastnames']], nick)
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
			{'cmd': u"select dem.add_name(%s, %s, %s, %s)", 'args': [self.getId(), firstnames, lastnames, active]}
		)
		if nickname is not None:
			queries.append({'cmd': u"select dem.set_nickname(%s, %s)", 'args': [self.getId(), nickname]})
		rows, idx = gmPG2.run_rw_queries(queries=queries)
		try:			
			del self._ext_cache['names']
		except: pass
		self.refetch_payload()
		return True
	#--------------------------------------------------------
	def set_nickname(self, nickname=None):
		"""
		Set the nickname. Setting the nickname only makes sense for the currently
		active name.
		@param nickname The preferred/nick/warrior name to set.
		"""
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': u"select dem.set_nickname(%s, %s)", 'args': [self.getId(), nickname]}])
		try:
			del self._ext_cache['names']
		except: pass
		self.refetch_payload()
		return True
	#--------------------------------------------------------
	# occupations API
	#--------------------------------------------------------
	def get_occupations(self):
		cmd = u"select * from dem.v_person_jobs where pk_identity=%s"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_obj]}])
		return rows
	#--------------------------------------------------------
	def link_occupation(self, occupation=None, activities=None):
		"""Link an occupation with a patient, creating the occupation if it does not exists.

			@param occupation The name of the occupation to link the patient to.
		"""
		activities = activities.strip()
		args = {'act': activities, 'pat_id': self.pk_obj, 'job': occupation.strip()}

		cmd = u"select activities from dem.v_person_jobs where pk_identity = %(pat_id)s and l10n_occupation = _(%(job)s)"
		rows, idx = gmPG2.run_ro_queries(queries = {'cmd': cmd, 'args': args})

		queries = []
		if len(rows) == 0:
			queries.append ({
				'cmd': u"INSERT INTO dem.lnk_job2person (fk_identity, fk_occupation, activities) VALUES (%(pat_id)s, dem.create_occupation(%(job)s), %(act)s)",
				'args': args
			})
		else:
			if rows[0]['activities'] != activities:
				queries.append ({
					'cmd': u"update dem.lnk_job2person set activities=%(act)s where fk_identity=%(pat_id)s and fk_occupation=(select id from dem.occupation where _(name) = _(%(job)s))",
					'args': args
				})

		rows, idx = gmPG2.run_rw_queries(queries = queries)

		return True
	#--------------------------------------------------------
	def unlink_occupation(self, occupation=None):
		cmd = u"delete from dem.lnk_job2person where fk_identity=%s and fk_occupation=(select id from dem.occupation where _(name) = _(%(job)s))"
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': [self.pk_obj, occupation.strip()]}])
		return True
	#--------------------------------------------------------
	# comms API
	#--------------------------------------------------------

	#--------------------------------------------------------
	def link_communication(self, comm_medium, url, is_confidential = False):
		"""
		Link a communication medium with a patient.
		@param comm_medium The name of the communication medium.
		@param url The communication resource locator.
		@type url A types.StringType instance.
		@param is_confidential Wether the data must be treated as confidential.
		@type is_confidential A types.BooleanType instance.
		"""
		# locate communication in enum list and sanity check
		comm_list = get_comm_list()
		if comm_medium not in comm_list:
			_log.Log(gmLog.lErr, 'cannot create communication of type: %s' % comm_medium)
			return False
		# FIXME: make link_person_comm() create comm type if necessary
		cmd = u"SELECT dem.link_person_comm(%(pk)s, %(medium)s, %(url)s, %(secret)s)",
		rows, idx = gmPG2.run_rw_queries(queries=[{'cmd': cmd, 'args': {'pk': self.pk_obj, 'medium': comm_medium, 'url': url, 'secret': is_confidential}}])
		return True
	#--------------------------------------------------------
	# contacts API
	#--------------------------------------------------------
	def get_addresses(self, address_type=None):
		cmd = u"select * from dem.v_pat_addresses where pk_identity=%s"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_obj]}], get_col_idx=True)
		addresses = []
		for r in rows:
			addresses.append(gmDemographicRecord.cPatientAddress(row={'idx': idx, 'data': r, 'pk_field': 'pk_address'}))

		filtered = addresses

		if address_type is not None:
			filtered = []
			for adr in addresses:
				if adr['address_type'] == address_type:
					filtered.append(adr)

		return filtered
	#--------------------------------------------------------
	def link_address(self, number=None, street=None, postcode=None, urb=None, state=None, country=None, subunit=None, suburb=None):
		"""Link an address with a patient, creating the address if it does not exists.

		@param number The number of the address.
		@param number A types.StringType instance.
		@param street The name of the street.
		@param street A types.StringType instance.
		@param postcode The postal code of the address.
		@param urb The name of town/city/etc.
		@param urb A types.StringType instance.
		@param state The name of the state.
		@param state A types.StringType instance.
		@param country The name of the country.
		@param country A types.StringType instance.
		"""
		# FIXME: add address type handling

		# create/get address
		adr = gmDemographicRecord.create_address (
			country = country,
			state = state,
			urb = urb,
			suburb = suburb,
			postcode = postcode,
			street = street,
			number = number,
			subunit = subunit
		)

		# purge cache
		try:del self._ext_cache['addresses']
		except: pass

		# already linked ?
		cmd = u"select exists(select 1 from dem.lnk_person_org_address where id_identity=%s and id_address=%s)"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self.pk_obj, adr['pk_address']]}])
		if rows[0][0]:
			return True

		# link to person
		cmd = u"insert into dem.lnk_person_org_address(id_identity, id_address) values (%(id)s, %(adr)s)"
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': {'id': self.pk_obj, 'adr': adr['pk_address']}}])

		return True
	#----------------------------------------------------------------------
	def unlink_address(self, address=None):
		print "[%s].unlink_address(): missing code" % self.__class__.__name__
	#----------------------------------------------------------------------
	# relatives API
	#----------------------------------------------------------------------
	def get_relatives(self):
		cmd = u"""
			select
				t.description,
				vbp.pk_identity as id,
				title,
				firstnames,
				lastnames,
				dob,
				cob,
				gender,
				karyotype,
				pupic,
				pk_marital_status,
				marital_status,+
				xmin_identity,
				preferred
			from
				dem.v_basic_person vbp, dem.relation_types t, dem.lnk_person2relative l
			where
				(
					l.id_identity = %(pk)s and
					vbp.pk_identity = l.id_relative and
					t.id = l.id_relation_type
				) or (
					l.id_relative = %(pk)s and
					vbp.pk_identity = l.id_identity and
					t.inverse = l.id_relation_type
				)"""
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {'pk': self.pk_obj}}])
		if len(rows) == 0:
			return []
		return [(row[0], cIdentity(row = {'data': row[1:], 'idx':idx, 'pk_field': 'pk'})) for row in rows]
	#--------------------------------------------------------
	def link_new_relative(self, rel_type = 'parent'):
		# create new relative
		id_new_relative = create_dummy_identity()
		relative = gmPerson(id_new_relative)
		# pre-fill with data from ourselves
		relative_ident = relative.get_identity()
#		relative_ident.copy_addresses(self)
		relative_ident.add_name( '**?**', self.get_names()['last'])
		# and link the two
		if self._ext_cache.has_key('relatives'):
			del self._ext_cache['relatives']
		cmd = u"""
			insert into dem.lnk_person2relative (
				id_identity, id_relative, id_relation_type
			) values (
				%s, %s, (select id from dem.relation_types where description = %s)
			)"""
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': [self.getId(), id_new_relative, rel_type  ]}])
		return True
	#----------------------------------------------------------------------
	def delete_relative(self, relation):
		# unlink only, don't delete relative itself
		self.set_relative(None, relation)
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

		self._ID = identity['pk_identity']  	# = identity.pk = v_basic_person.pk_identity = primary key
		self.__db_cache = {'identity': identity}

		# register backend notification interests ...
		if not self._register_interests():
			raise gmExceptions.ConstructorError, "Cannot register person modification interests."

		_log.Log(gmLog.lData, 'Instantiated person [%s].' % self._ID)
	#--------------------------------------------------------
	def cleanup(self):
		"""Do cleanups before dying.

		- note that this may be called in a thread
		"""
		_log.Log(gmLog.lData, 'cleaning up after person [%s]' % self._ID)
		if self.__db_cache.has_key('identity'):
			self.__db_cache['identity'].cleanup()
			del self.__db_cache['identity']
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def _register_interests(self):
		return True
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
		return self._ID
	#--------------------------------------------------------
	def get_identity(self):
		# because we are instantiated with it, it always exists
		return self.__db_cache['identity']
	#--------------------------------------------------------
	def export_data(self):
		data = {}
		emr = self.get_emr()
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
	_get_handler['API'] = _get_API
	_get_handler['ID'] = getID
	_get_handler['id'] = getID
	_get_handler['pk'] = getID
	_get_handler['pk_identity'] = getID
#============================================================
class cStaffMember(cPerson):
	"""Represents a staff member which is a person.

	- a specializing subclass of cPerson turning it into a staff member
	"""
	def __init__(self, identity = None):
		cPerson.__init__(self, identity=identity)
		self.__db_cache = {}
	#--------------------------------------------------------
	def cleanup(self):
		"""Do cleanups before dying.

		- note that this may be called in a thread
		"""
		cPerson.cleanup()
#		try:
#			self.__db_cache[''].cleanup()	# if has cleanup()
#			del self.__db_cache['']
#		except KeyError: pass
	#--------------------------------------------------------
	def get_inbox(self):
		return gmProviderInbox.cProviderInbox(provider_id = self._ID)
#============================================================
class cStaff(gmBusinessDBObject.cBusinessDBObject):
	_cmd_fetch_payload = u"select * from dem.v_staff where pk_staff=%s"
	_cmds_store_payload = [
		u"""update dem.staff set
			fk_role = %(pk_role)s,
			short_alias = %(short_alias)s,
			comment = %(comment)s,
			is_active = %(is_active)s,
			db_user = %(db_user)s
		where
			pk=%(pk_staff)s and
			xmin = %(xmin_staff)s""",
		u"""select xmin_staff from dem.v_staff where pk_identity=%(pk_identity)s"""
	]
	_updatable_fields = ['pk_role', 'short_alias', 'comment', 'is_active', 'db_user']
	#--------------------------------------------------------
	def __init__(self, aPK_obj=None, row=None):
		# by default get staff corresponding to CURRENT_USER
		if (aPK_obj is None) and (row is None):
			cmd = u"select * from dem.v_staff where db_user = CURRENT_USER"
			rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx=True)
			if len(rows) == 0:
				raise gmExceptions.ConstructorError, 'no staff record for CURRENT_USER'
			row = {
				'pk_field': 'pk_staff',
				'idx': idx,
				'data': rows[0]
			}
			gmBusinessDBObject.cBusinessDBObject.__init__(self, row=row)
		else:
			gmBusinessDBObject.cBusinessDBObject.__init__(self, aPK_obj=aPK_obj, row=row)

		# are we SELF ?
		self.__is_current_user = (gmPG2.get_current_user() == self._payload[self._idx['db_user']])
	#--------------------------------------------------------
	def __setitem__(self, attribute, value):
		if attribute == 'db_user':
			if self.__is_current_user:
				_log.Log(gmLog.lData, 'will not modify database account association of CURRENT_USER staff member')
				return
		gmBusinessDBObject.cBusinessDBObject.__setitem__(self, attribute, value)
#============================================================
class gmCurrentProvider(gmBorg.cBorg):
	"""Staff member Borg to hold currently logged on provider.

	There may be many instances of this but they all share state.
	"""
	def __init__(self, provider=None):
		"""Change or get currently logged on provider.

		provider:
		* None: get currently logged on provider
		* cStaff instance: change logged on provider (role)
		"""
		gmBorg.cBorg.__init__(self)

		# make sure we do have a provider pointer
		try:
			tmp = self._provider
		except AttributeError:
			self._provider = gmNull.cNull()

		# user wants copy of currently logged on provider
		if provider is None:
			return None

		# must be cStaff instance, then
		if not isinstance(provider, cStaff):
			raise ValueError, 'cannot set logged on provider to [%s], must be either None or cStaff instance' % str(provider)

		# same ID, no change needed
		if self._provider['pk_staff'] == provider['pk_staff']:
			return None

		# first invocation
		if isinstance(self._provider, gmNull.cNull):
			self._provider = provider
			return None

		# user wants different patient
		raise ValueError, 'provider change [%s] -> [%s] not yet supported' % (self._provider['pk_staff'], provider['pk_staff'])
	#--------------------------------------------------------
	def get_staff(self):
		return self._provider
	#--------------------------------------------------------
	def get_workplace(self):
		workplace = 'xxxDEFAULTxxx'
		if gmCfg.gmDefCfgFile is None:
			print _('No config file to read workplace name from !')
		else:
			tmp = gmCfg.gmDefCfgFile.get('workplace', 'name')
			if tmp is None:
				print _('You should name this workplace to better identify the machine !\nTo do this set the option "name" in the group [workplace] in the config file !')
			else:
				# if gmCfg.gmDefCfgFile returned a list type, use only first element
				if type(tmp) == type([]):
					workplace = tmp[0]
				else:
					workplace = tmp
		return workplace
	#--------------------------------------------------------
	# __getitem__ handling
	#--------------------------------------------------------
	def __getitem__(self, aVar = None):
		"""Return any attribute if known how to retrieve it by proxy.
		"""
		return self._provider[aVar]
#============================================================
class cPatient(cPerson):
	"""Represents a patient which is a person.

	- a specializing subclass of cPerson turning it into a patient
	"""
	def __init__(self, identity = None):
		cPerson.__init__(self, identity=identity)
		self.__db_cache = {}
	#--------------------------------------------------------
	def cleanup(self):
		"""Do cleanups before dying.

		- note that this may be called in a thread
		"""
		cPerson.cleanup(self)
		if self.__db_cache.has_key('clinical record'):
			self.__db_cache['clinical record'].cleanup()
			del self.__db_cache['clinical record']
		if self.__db_cache.has_key('document folder'):
			self.__db_cache['document folder'].cleanup()
			del self.__db_cache['document folder']
	#----------------------------------------------------------
	def get_emr(self):
		try:
			return self.__db_cache['clinical record']
		except KeyError:
			pass
		try:
			from Gnumed.business import gmClinicalRecord
			self.__db_cache['clinical record'] = gmClinicalRecord.cClinicalRecord(aPKey = self._ID)
		except StandardError:
			_log.LogException('cannot instantiate clinical record for person [%s]' % self._ID, sys.exc_info())
			return None
		return self.__db_cache['clinical record']
	#--------------------------------------------------------
	def get_last_encounter(self):
		cmd = u'select * from clin.v_most_recent_encounters where pk_patient=%s'
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self._ID]}])
		if len(rows) > 0:
			return rows[0]
		else:
			return None
	#--------------------------------------------------------
	def get_document_folder(self):
		try:
			return self.__db_cache['document folder']
		except KeyError:
			pass
		try:
			# FIXME: we need some way of setting the type of backend such that
			# to instantiate the correct type of document folder class
			self.__db_cache['document folder'] = gmMedDoc.cDocumentFolder(aPKey = self._ID)
		except StandardError:
			_log.LogException('cannot instantiate document folder for person [%s]' % self._ID, sys.exc_info())
			return None
		return self.__db_cache['document folder']
	#--------------------------------------------------------
	def _getMedDocsList(self):
		"""Build a complete list of metadata for all documents of this person.
		"""
		cmd = u"SELECT pk from blobs.doc_med WHERE patient_id=%s"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [self._ID]}])
		docs = []
		for row in rows:
			docs.append(row[0])
		if len(docs) == 0:
			_log.Log(gmLog.lInfo, "No documents found for person (ID [%s])." % self._ID)
			return None
		return docs
#============================================================
class gmCurrentPatient(gmBorg.cBorg):
	"""Patient Borg to hold currently active patient.

	There may be many instances of this but they all share state.
	"""
	def __init__(self, patient=None, forced_reload=False):
		"""Change or get currently active patient.

		patient:
		* None: get currently active patient
		* -1: unset currently active patient
		* cPatient instance: set active patient if possible
		"""
		gmBorg.cBorg.__init__(self)

		# make sure we do have a patient pointer
		try:
			tmp = self.patient
		except AttributeError:
			self.patient = gmNull.cNull()

		# set initial lock state,
		# this lock protects against activating another patient
		# when we are controlled from a remote application
		try:
			tmp = self._locked
		except AttributeError:
			self.unlock()

		# user wants copy of current patient
		if patient is None:
			return None

		# user wants to explicitely unset current patient
		if patient == -1:
			_log.Log(gmLog.lData, 'explicitely unsetting current patient')
			self.__send_pre_selection_notification()
			self.patient.cleanup()
			self.patient = gmNull.cNull()
			self.__send_selection_notification()
			return None

		# must be cPatient instance, then
		if not isinstance(patient, cPatient):
			_log.Log(gmLog.lErr, 'cannot set active patient to [%s], must be either None, -1 or cPatient instance' % str(patient))
			raise TypeError, 'gmPerson.gmCurrentPatient.__init__(): <patient> must be None, -1 or cPatient instance but is: %s' % str(patient)

		# same ID, no change needed
		if (self.patient['pk_identity'] == patient['pk_identity']) and not forced_reload:
			return None

		# user wants different patient
		_log.Log(gmLog.lData, 'patient change [%s] -> [%s] requested' % (self.patient['pk_identity'], patient['pk_identity']))

		# but not if patient is locked
		if self._locked:
			_log.Log(gmLog.lErr, 'patient [%s] is locked, cannot change to [%s]' % (self.patient['pk_identity'], patient['pk_identity']))
			# FIXME: exception ?
			return None

		# everything seems swell
		self.__send_pre_selection_notification()
		self.patient.cleanup()
		self.patient = patient
		self.__send_selection_notification()

		return None
	#--------------------------------------------------------
	def cleanup(self):
		self.patient.cleanup()
	#--------------------------------------------------------
	def get_emr(self):
		return self.patient.get_emr()
	#--------------------------------------------------------
	def get_clinical_record(self):
		print "get_clinical_record() deprecated"
		return self.patient.get_emr()
	#--------------------------------------------------------
	def get_identity(self):
		return self.patient.get_identity()
	#--------------------------------------------------------
	def get_document_folder(self):
		return self.patient.get_document_folder()
	#--------------------------------------------------------
	def getID(self):
		return self.patient.getID()
	#--------------------------------------------------------
	def export_data(self):
		return self.patient.export_data()
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
			'pk_identity': self.patient['pk_identity'],
			'patient': self.patient['pk_identity'],
			'signal': gmSignals.pre_patient_selection(),
			'sender': id(self.__class__)
		}
		gmDispatcher.send(gmSignals.pre_patient_selection(), kwds=kwargs)
	#--------------------------------------------------------
	def __send_selection_notification(self):
		"""Sends signal when another patient has actually been made active."""
		kwargs = {
			'pk_identity': self.patient['pk_identity'],
			'patient': self.patient,
			'signal': gmSignals.post_patient_selection(),
			'sender': id(self.__class__)
		}
		gmDispatcher.send(**kwargs)
	#--------------------------------------------------------
	def is_connected(self):
		if isinstance(self.patient, gmNull.cNull):
			return False
		else:
			return True
	#--------------------------------------------------------
	# __getitem__ handling
	#--------------------------------------------------------
	def __getitem__(self, aVar = None):
		"""Return any attribute if known how to retrieve it by proxy.
		"""
		return self.patient[aVar]
#============================================================
class cPatientSearcher_SQL:
	"""UI independant i18n aware patient searcher."""
	def __init__(self):
		self._generate_queries = self._generate_queries_de
		# make a cursor
		self.conn = gmPG2.get_connection()
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
	def get_persons(self, search_term = None, a_locale = None, dto = None):
		identities = self.get_identities(search_term, a_locale, dto)
		if identities is None:
			return None
		return [cPerson(identity = ident) for ident in identities]
	#--------------------------------------------------------
	def get_patients(self, search_term = None, a_locale = None, dto = None):
		identities = self.get_identities(search_term, a_locale, dto)
		if identities is None:
			return None
		return [cPatient(identity = ident) for ident in identities]
	#--------------------------------------------------------
	def get_identities(self, search_term = None, a_locale = None, dto = None):
		"""Get patient identity objects for given parameters.

		- either search term or search dict
		- dto contains structured data that doesn't need to be parsed (cDTO_person)
		- dto takes precedence over search_term
		"""
		parse_search_term = (dto is None)

		if not parse_search_term:
			queries = self._generate_queries_from_dto(dto)
			if queries is None:
				parse_search_term = True
			if len(queries) == 0:
				parse_search_term = True

		if parse_search_term:
			# temporary change of locale for selecting query generator
			if a_locale is not None:
				print "temporary change of locale on patient search not implemented"
				_log.Log(gmLog.lWarn, "temporary change of locale on patient search not implemented")
			# generate queries
			if search_term is None:
				_log.Log(gmLog.lErr, 'need search term (dto AND search_term are None)')
				return None
			queries = self._generate_queries(search_term)

		# anything to do ?
		if (queries is None) or (len(queries) == 0):
			_log.Log(gmLog.lErr, 'query tree empty')
			_log.Log(gmLog.lErr, '[%s] [%s] [%s]' % (search_term, a_locale, str(dto)))
			return None

		# collect IDs here
		identities = []
		# cycle through query list
		for query in queries:
			_log.Log(gmLog.lData, "running %s" % query)
			try:
				rows, idx = gmPG2.run_ro_queries(queries = [query], get_col_idx=True)
			except:
				_log.LogException('error running query')
				continue
			if len(rows) == 0:
				continue
			identities.extend (
				[ cIdentity(row = {'pk_field': 'pk_identity', 'data': row, 'idx': idx}) for row in rows ]
			)

		return identities
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def _make_sane_caps(self, aName = None):
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
	def _normalize_soundalikes(self, aString = None, aggressive = False):
		"""Transform some characters into a regex."""
		if aString.strip() == '':
			return aString

		# umlauts
		normalized =    aString.replace(u'Ä', u'(Ä|AE|Ae|A|E)')
		normalized = normalized.replace(u'Ö', u'(Ö|OE|Oe|O)')
		normalized = normalized.replace(u'Ü', u'(Ü|UE|Ue|U)')
		normalized = normalized.replace(u'ä', u'(ä|ae|e|a)')
		normalized = normalized.replace(u'ö', u'(ö|oe|o)')
		normalized = normalized.replace(u'ü', u'(ü|ue|u|y)')
		normalized = normalized.replace(u'ß', u'(ß|sz|ss|s)')

		# common soundalikes
		# - René, Desiré, Inés ...
		normalized = normalized.replace(u'é', u'***DUMMY***')
		normalized = normalized.replace(u'è', u'***DUMMY***')
		normalized = normalized.replace(u'***DUMMY***', u'(é|e|è|ä|ae)')

		# FIXME: missing i/a/o - but uncommon in German
		normalized = normalized.replace('v', '***DUMMY***')
		normalized = normalized.replace('f', '***DUMMY***')
		normalized = normalized.replace('ph','***DUMMY***')	# now, this is *really* specific for German
		normalized = normalized.replace('***DUMMY***', '(v|f|ph)')

		# silent characters
		normalized = normalized.replace('Th','***DUMMY***')
		normalized = normalized.replace('T', '***DUMMY***')
		normalized = normalized.replace('***DUMMY***', '(Th|T)')
		normalized = normalized.replace('th', '***DUMMY***')
		normalized = normalized.replace('t', '***DUMMY***')
		normalized = normalized.replace('***DUMMY***', '(th|t)')

		# apostrophes, hyphens et al
		normalized = normalized.replace('"', '***DUMMY***')
		normalized = normalized.replace("'", '***DUMMY***')
		normalized = normalized.replace('`', '***DUMMY***')
		normalized = normalized.replace('***DUMMY***', """("|'|`|***DUMMY***|\s)*""")
		normalized = normalized.replace('-', """(-|\s)*""")
		normalized = normalized.replace('|***DUMMY***|', '|-|')

		if aggressive:
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
	def _make_simple_query(self, raw):
		"""Compose queries if search term seems unambigous."""
		_log.Log(gmLog.lData, '_make_simple_query("%s")' % raw)

		queries = []

		# "<digits>" - GNUmed patient PK or DOB
		if re.match("^(\s|\t)*\d+(\s|\t)*$", raw):
			tmp = raw.strip()
			queries.append ({
				'cmd': u"select *, %s::text as match_type FROM dem.v_basic_person WHERE pk_identity = %s order by lastnames, firstnames, dob",
				'args': [_('internal patient ID'), tmp]
			})
			queries.append ({
				'cmd': u"SELECT *, %s::text as match_type FROM dem.v_basic_person WHERE date_trunc('day', dob::timestamp) = date_trunc('day', %s::timestamp) order by lastnames, firstnames, dob",
				'args': [_('date of birth'), tmp]
			})
			queries.append ({
				'cmd': u"""
					select vba.*, %s::text as match_type from dem.lnk_identity2ext_id li2ext_id, dem.v_basic_person vba
					where vba.pk_identity = li2ext_id.id_identity and li2ext_id.external_id ~* %s
					order by lastnames, firstnames, dob""",
				'args': [_('external patient ID'), tmp]
			})
			return queries

		# "<d igi ts>" - DOB or patient PK
		if re.match("^(\d|\s|\t)+$", raw):
			queries.append ({
				'cmd': u"SELECT *, %s::text as match_type FROM dem.v_basic_person WHERE date_trunc('day', dob::timestamp) = date_trunc('day', %s::timestamp) order by lastnames, firstnames, dob",
				'args': [_('date of birth'), raw]
			})
			tmp = raw.replace(' ', '')
			tmp = tmp.replace('\t', '')
			queries.append ({
				'cmd': u"SELECT *, %s::text as match_type from dem.v_basic_person WHERE pk_identity LIKE %s%%",
				'args': [_('internal patient ID'), tmp]
			})
			return queries

		# "#<di git  s>" - GNUmed patient PK
		if re.match("^(\s|\t)*#(\d|\s|\t)+$", raw):
			tmp = raw.replace('#', '')
			tmp = tmp.strip()
			tmp = tmp.replace(' ', '')
			tmp = tmp.replace('\t', '')
			# this seemingly stupid query ensures the PK actually exists
			queries.append ({
				'cmd': u"SELECT *, %s::text as match_type from dem.v_basic_person WHERE pk_identity = %s order by lastnames, firstnames, dob",
				'args': [_('internal patient ID'), tmp]
			})
			# but might also be an external ID
			tmp = raw.replace('#', '')
			tmp = tmp.strip()
			tmp = tmp.replace(' ',  '***DUMMY***')
			tmp = tmp.replace('\t', '***DUMMY***')
			tmp = tmp.replace('***DUMMY***', '(\s|\t|-|/)*')
			queries.append ({
				'cmd': u"""
					select vba.*, %s::text as match_type from dem.lnk_identity2ext_id li2ext_id, dem.v_basic_person vba
					where vba.pk_identity = li2ext_id.id_identity and li2ext_id.external_id ~* %s
					order by lastnames, firstnames, dob""",
				'args': [_('external patient ID'), tmp]
			})
			return queries

		# "#<di/git s or c-hars>" - external ID (or PUPIC)
		if re.match("^(\s|\t)*#.+$", raw):
			tmp = raw.replace('#', '')
			tmp = tmp.strip()
			tmp = tmp.replace(' ',  '***DUMMY***')
			tmp = tmp.replace('\t', '***DUMMY***')
			tmp = tmp.replace('-',  '***DUMMY***')
			tmp = tmp.replace('/',  '***DUMMY***')
			tmp = tmp.replace('***DUMMY***', '(\s|\t|-|/)*')
			queries.append ({
				'cmd': u"""
					select vba.*, %s::text as match_type from dem.lnk_identity2ext_id li2ext_id, dem.v_basic_person vba
					where vba.pk_identity = li2ext_id.id_identity and li2ext_id.external_id ~* %s
					order by lastnames, firstnames, dob""",
				'args': [_('external patient ID'), tmp]
			})
			return queries

		# digits interspersed with "./-" or blank space - DOB
		if re.match("^(\s|\t)*\d+(\s|\t|\.|\-|/)*\d+(\s|\t|\.|\-|/)*\d+(\s|\t|\.)*$", raw):
			tmp = raw.strip()
			while '\t\t' in tmp: tmp = tmp.replace('\t\t', ' ')
			while '  ' in tmp: tmp = tmp.replace('  ', ' ')
			# apparently not needed due to PostgreSQL smarts...
			#tmp = tmp.replace('-', '.')
			#tmp = tmp.replace('/', '.')
			queries.append ({
				'cmd': u"SELECT *, %s as match_type from dem.v_basic_person WHERE date_trunc('day', dob) = date_trunc('day', %s::timestamp) order by lastnames, firstnames, dob",
				'args': [_('date of birth'), tmp]
			})
			return queries

		# " , <alpha>" - first name
		if re.match("^(\s|\t)*,(\s|\t)*([^0-9])+(\s|\t)*$", raw):
			tmp = raw.split(',')[1].strip()
			tmp = self._normalize_soundalikes(tmp)
			cmd = u"""
SELECT DISTINCT ON (pk_identity) * from (
	select *, %s as match_type from ((
		select vbp.*
		FROM dem.names, dem.v_basic_person vbp
		WHERE dem.names.firstnames ~ %s and vbp.pk_identity = dem.names.id_identity
	) union all (
		select vbp.*
		FROM dem.names, dem.v_basic_person vbp
		WHERE dem.names.firstnames ~ %s and vbp.pk_identity = dem.names.id_identity
	)) as super_list order by lastnames, firstnames, dob
) as sorted_list"""
			queries.append ({
				'cmd': cmd,
				'args': [_('first name'), '^' + self._make_sane_caps(tmp), '^' + tmp]
			})
			return queries

		# "*|$<...>" - DOB
		if re.match("^(\s|\t)*(\*|\$).+$", raw):
			tmp = raw.replace('*', '')
			tmp = tmp.replace('$', '')
			queries.append ({
				'cmd': u"SELECT *, %s as match_type from dem.v_basic_person WHERE date_trunc('day', dob) = date_trunc('day', %s::timestamp) order by lastnames, firstnames, dob",
				'args': [_('date of birth'), tmp]
			})
			return queries

		return None
	#--------------------------------------------------------
	# generic, locale independant queries
	#--------------------------------------------------------
	def _generate_queries_from_dto(self, dto = None):
		"""Generate generic queries.

		- not locale dependant
		- data -> firstnames, lastnames, dob, gender
		"""
		if not isinstance(dto, cDTO_person):
			return None

		vals = [_('name, gender, date of birth')]
		where_snippets = []

		try:
			vals.append(dto.firstnames)
			where_snippets.append(u'firstnames=%s')
		except KeyError:
			pass

		try:
			vals.append(dto.lastnames)
			where_snippets.append(u'lastnames=%s')
		except KeyError:
			pass

		try:
			vals.append(dto.dob)
			where_snippets.append(u"date_trunc('day', dob) = date_trunc('day', %s::timestamp)")
		except KeyError:
			pass

		try:
			vals.append(dto.gender)
			where_snippets.append('gender=%s')
		except KeyError:
			pass

		# sufficient data ?
		if len(where_snippets) == 0:
			_log.Log(gmLog.lErr, 'invalid search dict structure')
			_log.Log(gmLog.lData, data)
			return None

		cmd = u"""
			select *, %%s as match_type from dem.v_basic_person
			where pk_identity in (
				select id_identity from dem.names where %s
			) order by lastnames, firstnames, dob""" % ' and '.join(where_snippets)

		queries = [
			{'cmd': cmd, 'args': vals}
		]

		# shall we mogrify name parts ? probably not

		return queries
	#--------------------------------------------------------
	# queries for DE
	#--------------------------------------------------------
	def _generate_queries_de(self, search_term = None):
		_log.Log(gmLog.lData, '_generate_queries_de("%s")' % search_term)

		if search_term is None:
			return []

		# check to see if we get away with a simple query ...
		queries = self._make_simple_query(search_term)
		if queries is not None:
			return queries

		# no we don't
		queries = []

		# replace Umlauts
		normalized = self._normalize_soundalikes(search_term)

		# "<CHARS>" - single name part
		# yes, I know, this is culture specific (did you read the docs ?)
		if re.match("^(\s|\t)*[a-zäöüßéáúóçøA-ZÄÖÜÇØ]+(\s|\t)*$", search_term):
			# there's no intermediate whitespace due to the regex
			tmp = normalized.strip()
			args = []
			cmd = u"""
SELECT DISTINCT ON (pk_identity) * from (
	select * from ((
		-- last name
		select vbp.*, %s::text as match_type from dem.v_basic_person vbp, dem.names n WHERE vbp.pk_identity = n.id_identity and n.lastnames ~ %s
	) union all (
		select vbp.*, %s::text as match_type from dem.v_basic_person vbp, dem.names n WHERE vbp.pk_identity = n.id_identity and n.lastnames  ~* %s
	) union all (
		-- first name
		select vbp.*, %s::text as match_type from dem.v_basic_person vbp, dem.names n WHERE vbp.pk_identity = n.id_identity and n.firstnames ~ %s
	) union all (
		select vbp.*, %s::text as match_type from dem.v_basic_person vbp, dem.names n WHERE vbp.pk_identity = n.id_identity and n.firstnames ~* %s
	) union all (
		-- anywhere in name
		select vbp.*, %s::text as match_type from dem.v_basic_person vbp, dem.names n WHERE vbp.pk_identity = n.id_identity and n.firstnames || n.lastnames || coalesce(n.preferred, '') ~* %s
	)) as super_list order by lastnames, firstnames, dob
) as sorted_list"""
			args.append(_('last name'))
			args.append('^' + self._make_sane_caps(tmp))
			args.append(_('last name'))
			args.append('^' + tmp)
			args.append(_('first name'))
			args.append('^' + self._make_sane_caps(tmp))
			args.append(_('first name'))
			args.append('^' + tmp)
			args.append(_('any name part'))
			args.append(tmp)

			queries.append ({
				'cmd': cmd,
				'args': args
			})
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
					queries.append ({
						'cmd': u"SELECT DISTINCT ON (id_identity) vbp.*, %s::text as match_type from dem.v_basic_person vbp, dem.names n WHERE vbp.pk_identity = n.id_identity and n.firstnames ~ %s AND n.lastnames ~ %s",
						'args': [_('name: first-last'), '^' + self._make_sane_caps(name_parts[0]), '^' + self._make_sane_caps(name_parts[1])]
					})
					queries.append ({
						'cmd': u"SELECT DISTINCT ON (id_identity) vbp.*, %s::text as match_type from dem.v_basic_person vbp, dem.names n WHERE vbp.pk_identity = n.id_identity and n.firstnames ~* %s AND n.lastnames ~* %s",
						'args': [_('name: first-last'), '^' + name_parts[0], '^' + name_parts[1]]
					})
					# assumption: last first
					queries.append ({
						'cmd': u"SELECT DISTINCT ON (id_identity) vbp.*, %s::text as match_type from dem.v_basic_person vbp, dem.names n WHERE vbp.pk_identity = n.id_identity and n.firstnames ~ %s AND n.lastnames ~ %s",
						'args': [_('name: last-first'), '^' + self._make_sane_caps(name_parts[1]), '^' + self._make_sane_caps(name_parts[0])]
					})
					queries.append ({
						'cmd': u"SELECT DISTINCT ON (id_identity) vbp.*, %s::text as match_type from dem.v_basic_person vbp, dem.names n WHERE vbp.pk_identity = n.id_identity and n.firstnames ~* %s AND n.lastnames ~* %s",
						'args': [_('name: last-first'), '^' + name_parts[1], '^' + name_parts[0]]
					})
					# name parts anywhere in name - third order query ...
					queries.append ({
						'cmd': u"SELECT DISTINCT ON (id_identity) vbp.*, %s::text as match_type from dem.v_basic_person vbp, dem.names n WHERE vbp.pk_identity = n.id_identity and n.firstnames || n.lastnames ~* %s AND firstnames || n.lastnames ~* %s",
						'args': [_('name'), name_parts[0], name_parts[1]]
					})
					return queries
				# FIXME: either "name date" or "date date"
				_log.Log(gmLog.lErr, "don't know how to generate queries for [%s]" % search_term)
				return queries

			# exactly 3 words ?
			if len(sub_parts_list) == 3:
				# special case: 3 words, exactly 1 of them a date, no ",;"
				if date_count == 1:
					# assumption: first, last, dob - first order
					queries.append ({
						'cmd': u"SELECT DISTINCT ON (id_identity) vbp.*, %s::text as match_type from dem.v_basic_person vbp, dem.names n WHERE vbp.pk_identity = n.id_identity and n.firstnames ~ %s AND n.lastnames ~ %s AND date_trunc('day', dob) = date_trunc('day', %s::timestamp)",
						'args': [_('names: first-last, date of birth'), '^' + self._make_sane_caps(name_parts[0]), '^' + self._make_sane_caps(name_parts[1]), date_part]
					})
					queries.append ({
						'cmd': u"SELECT DISTINCT ON (id_identity) vbp.*, %s::text as match_type from dem.v_basic_person vbp, dem.names n WHERE vbp.pk_identity = n.id_identity and firstnames ~* %s AND n.lastnames ~* %s AND date_trunc('day', dob) = date_trunc('day', %s::timestamp)",
						'args': [_('names: first-last, date of birth'), '^' + name_parts[0], '^' + name_parts[1], date_part]
					})
					# assumption: last, first, dob - second order query
					queries.append ({
						'cmd': u"SELECT DISTINCT ON (id_identity) vbp.*, %s::text as match_type from dem.v_basic_person vbp, dem.names n WHERE vbp.pk_identity = n.id_identity and n.firstnames ~ %s AND n.lastnames ~ %s AND date_trunc('day', dob) = date_trunc('day', %s::timestamp)",
						'args': [_('names: last-first, date of birth'), '^' + self._make_sane_caps(name_parts[1]), '^' + self._make_sane_caps(name_parts[0]), date_part]
					})
					queries.append ({
						'cmd': u"SELECT DISTINCT ON (id_identity) vbp.*, %s::text as match_type from dem.v_basic_person vbp, dem.names n WHERE vbp.pk_identity = n.id_identity and n.firstnames ~* %s AND n.lastnames ~* %s AND date_trunc('day', dob) = date_trunc('day', %s::timestamp)",
						'args': [_('names: last-first, dob'), '^' + name_parts[1], '^' + name_parts[0], date_part]
					})
					# name parts anywhere in name - third order query ...
					queries.append ({
						'cmd': u"SELECT DISTINCT ON (id_identity) vbp.*, %s::text as match_type from dem.v_basic_person vbp, dem.names n WHERE vbp.pk_identity = n.id_identity and n.firstnames || n.lastnames ~* %s AND n.firstnames || n.lastnames ~* %s AND date_trunc('day', dob) = date_trunc('day', %s::timestamp)",
						'args': [_('name, date of birth'), name_parts[0], name_parts[1], date_part]
					})
					return queries
				# FIXME: "name name name" or "name date date"
				queries.append([self._generate_dumb_brute_query(search_term)])
				return queries

			# FIXME: no ',;' but neither "name name" nor "name name date"
			queries.append([self._generate_dumb_brute_query(search_term)])
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

			where_parts = []
			# first, handle name parts
			# special case: "<date(s)>, <name> <name>, <date(s)>"
			if (len(name_parts) == 1) and (name_count == 2):
				# usually "first last"
				where_parts.append ({
					'conditions': u"firstnames ~ %s and lastnames ~ %s",
					'args': [_('names: first last'), '^' + self._make_sane_caps(name_parts[0][0]), '^' + self._make_sane_caps(name_parts[0][1])]
				})
				where_parts.append ({
					'conditions': u"firstnames ~* %s and lastnames ~* %s",
					'args': [_('names: first last'), '^' + name_parts[0][0], '^' + name_parts[0][1]]
				})
				# but sometimes "last first""
				where_parts.append ({
					'conditions': u"firstnames ~ %s and lastnames ~ %s",
					'args': [_('names: last, first'), '^' + self._make_sane_caps(name_parts[0][1]), '^' + self._make_sane_caps(name_parts[0][0])]
				})
				where_parts.append ({
					'conditions': u"firstnames ~* %s and lastnames ~* %s",
					'args': [_('names: last, first'), '^' + name_parts[0][1], '^' + name_parts[0][0]]
				})
				# or even substrings anywhere in name
				where_parts.append ({
					'conditions': u"firstnames || lastnames ~* %s OR firstnames || lastnames ~* %s",
					'args': [_('name'), name_parts[0][0], name_parts[0][1]]
				})

			# special case: "<date(s)>, <name(s)>, <name(s)>, <date(s)>"
			elif len(name_parts) == 2:
				# usually "last, first"
				where_parts.append ({
					'conditions': u"firstnames ~ %s AND lastnames ~ %s",
					'args': [_('name: last, first'), '^' + ' '.join(map(self._make_sane_caps, name_parts[1])), '^' + ' '.join(map(self._make_sane_caps, name_parts[0]))]
				})
				where_parts.append ({
					'conditions': u"firstnames ~* %s AND lastnames ~* %s",
					'args': [_('name: last, first'), '^' + ' '.join(name_parts[1]), '^' + ' '.join(name_parts[0])]
				})
				# but sometimes "first, last"
				where_parts.append ({
					'conditions': u"firstnames ~ %s AND lastnames ~ %s",
					'args': [_('name: last, first'), '^' + ' '.join(map(self._make_sane_caps, name_parts[0])), '^' + ' '.join(map(self._make_sane_caps, name_parts[1]))]
				})
				where_parts.append ({
					'conditions': u"firstnames ~* %s AND lastnames ~* %s",
					'args': [_('name: last, first'), '^' + ' '.join(name_parts[0]), '^' + ' '.join(name_parts[1])]
				})
				# or even substrings anywhere in name
				where_parts.append ({
					'conditions': u"firstnames || lastnames ~* %s AND firstnames || lastnames ~* %s",
					'args': [_('name'), ' '.join(name_parts[0]), ' '.join(name_parts[1])]
				})

			# big trouble - arbitrary number of names
			else:
				# FIXME: deep magic, not sure of rationale ...
				if len(name_parts) == 1:
					for part in name_parts[0]:
						where_parts.append ({
							'conditions': u"firstnames || lastnames ~* %s",
							'args': [_('name'), part]
						})
				else:
					tmp = []
					for part in name_parts:
						tmp.append(' '.join(part))
					for part in tmp:
						where_parts.append ({
							'conditions': u"firstnames || lastnames ~* %s",
							'args': [_('name'), part]
						})

			# secondly handle date parts
			# FIXME: this needs a considerable smart-up !
			if len(date_parts) == 1:
				if len(where_parts) == 0:
					where_parts.append ({
						'conditions': u"date_trunc('day', dob) = date_trunc('day', %s::timestamp)",
						'args': [_('date of birth'), date_parts[0]]
					})
				if len(where_parts) > 0:
					where_parts[0]['conditions'] += u" AND date_trunc('day', dob) = date_trunc('day', %s::timestamp)"
					where_parts[0]['args'].append(date_parts[0])
					where_parts[0]['args'][0] += u', ' + _('date of birth')
				if len(where_parts) > 1:
					where_parts[1]['conditions'] += u" AND date_trunc('day', dob) = date_trunc('day', %s::timestamp)"
					where_parts[1]['args'].append(date_parts[0])
					where_parts[1]['args'][0] += u', ' + _('date of birth')
			elif len(date_parts) > 1:
				if len(where_parts) == 0:
					where_parts.append ({
						'conditions': u"date_trunc('day', dob) = date_trunc('day', %s::timestamp) AND date_trunc('day', dem.identity.deceased) = date_trunc('day', %s::timestamp)",
						'args': [_('date of birth/death'), date_parts[0], date_parts[1]]
					})
				if len(where_parts) > 0:
					where_parts[0]['conditions'] += u" AND date_trunc('day', dob) = date_trunc('day', %s::timestamp) AND date_trunc('day', dem.identity.deceased) = date_trunc('day', %s::timestamp)",
					where_parts[0]['args'].append(date_parts[0], date_parts[1])
					where_parts[0]['args'][0] += u', ' + _('date of birth/death')
				if len(where_parts) > 1:
					where_parts[1]['conditions'] += u" AND date_trunc('day', dob) = date_trunc('day', %s::timestamp) AND date_trunc('day', dem.identity.deceased) = date_trunc('day', %s::timestamp)",
					where_parts[1]['args'].append(date_parts[0], date_parts[1])
					where_parts[1]['args'][0] += u', ' + _('date of birth/death')

			# and finally generate the queries ...
			for where_part in where_parts:
				queries.append ({
					'cmd': u"select *, %%s::text as match_type from dem.v_basic_person where %s" % where_part['conditions'],
					'args': where_part['args']
				})
			return queries

		return []
	#--------------------------------------------------------
	def _generate_dumb_brute_query(self, search_term=''):
		where_clause = ''
		args = [_('name')]
		# FIXME: split on more than just ' '
		for arg in search_term.strip().split():
			where_clause += u' and vbp.title || vbp.firstnames || vbp.lastnames ~* %s'
			args.append(arg)

		query = u"""
select distinct on (pk_identity) * from (
	select
		vbp.*, %%s::text as match_type
	from
		dem.v_basic_person vbp,
		dem.names n
	where
		vbp.pk_identity = n.id_identity
		%s
	order by
		lastnames,
		firstnames,
		dob
) as ordered_list""" % where_clause

		return ({'cmd': query, 'args': args})
#============================================================
# match providers
#============================================================
class cMatchProvider_Provider(gmMatchProvider.cMatchProvider_SQL2):
	def __init__(self):
		gmMatchProvider.cMatchProvider_SQL2.__init__(
			self,
			queries = [u"""select
							pk_staff,
							short_alias || ' (' || title || firstnames || ' ' || lastnames || ')',
							1
						from dem.v_staff
						where
							short_alias || ' ' || firstnames || ' ' || lastnames || ' ' || db_user %(fragment_condition)s"""]
		)
		self.setThresholds(1, 2, 3)
#============================================================
# convenience functions
#============================================================
def dob2medical_age(dob):
	"""Format patient age in a hopefully meaningful way."""
	age = datetime.datetime.now(tz=dob.tzinfo) - dob
	if age.days > 364:
		years, days = divmod(age.days, 365)
		months, day = divmod(days, 30)
		return "%sy%sm" % (int(years), int(months))
	if age.days > 30:
		months, days = divmod(age.days, 30)
		weeks = days // 7
		return "%sm%sw" % (int(months), int(weeks))
	if age.days > 7:
		return "%sd" % age.days
	if age.days > 1:
		hours, seconds = divmod(age.seconds, 3600)
		return "%sd (%sh)" % (age.days, int(hours))
	if age.seconds > (3*3600):
		return "%sh" % int(age.seconds // 3600)
	if age.seconds > 3600:
		hours, seconds = divmod(age.seconds, 3600)
		minutes = seconds // 60
		return "%sh%sm" % (int(hours), int(minutes))
	if age.seconds > (5*60):
		return "%sm" % (int(age.seconds // 60))
	minutes, seconds = divmod(age.seconds, 60)
	return "%sm%ss" % (int(minutes), int(seconds))
#============================================================
def create_identity(gender=None, dob=None, lastnames=None, firstnames=None):

	cmd1 = u"""
insert into dem.identity (
	gender, dob
) values (
	%s, coalesce(%s, CURRENT_TIMESTAMP)
)"""

	cmd2 = u"""
insert into dem.names (
	id_identity, lastnames, firstnames
) values (
	currval('dem.identity_pk_seq'), coalesce(%s, 'xxxDEFAULTxxx'), coalesce(%s, 'xxxDEFAULTxxx')
)"""

	rows, idx = gmPG2.run_rw_queries (
		queries = [
			{'cmd': cmd1, 'args': [gender, dob]},
			{'cmd': cmd2, 'args': [lastnames, firstnames]},
			{'cmd': u"select currval('dem.identity_pk_seq')"}
		],
		return_data = True
	)
	return cIdentity(aPK_obj=rows[0][0])
#============================================================
def create_dummy_identity():	
	cmd1 = u"insert into dem.identity(gender, dob) values('xxxDEFAULTxxx', CURRENT_TIMESTAMP)"
	cmd2 = u"select currval('dem.identity_id_seq')"

	rows, idx = gmPG2.run_rw_queries (
		queries = [
			{'cmd': cmd1},
			{'cmd': cmd2}
		],
		return_data = True
	)
	return gmDemographicRecord.cIdentity(aPK_obj = rows[0][0])
#============================================================
def set_active_patient(patient = None, forced_reload=False):
	"""Set active patient.

	If patient is -1 the active patient will be UNset.
	"""
	if isinstance(patient, cPatient):
		pat = patient
	elif isinstance(patient, cIdentity):
		pat = cPatient(identity = patient)
	elif isinstance(patient, cPerson):
		pat = cPatient(identity = patient.get_identity())
	elif isinstance(patient, cStaff):
		pat = cPatient(identity = cIdentity(patient['pk_identity']))
	elif patient == -1:
		pat = patient
	else:
		raise ValueError('<patient> must be either -1, cPatient, cPerson, cStaff or cIdentity instance, is: %s' % str(patient))

	# attempt to switch
	try:
		pat = gmCurrentPatient(patient=pat, forced_reload=forced_reload)
	except:
		_log.LogException('error changing active patient to [%s]' % str(patient), sys.exc_info())
		return False
	return True
#------------------------------------------------------------
def prompted_input(prompt, default=None):
	"""Obtains entry from standard input.

	prompt - Prompt text to display in standard output
	default - Default value (for user to press enter only)
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
	if search_fragment in ['exit', 'quit', 'bye', None]:
		print "user cancelled patient search"
		return None
	pats = person_searcher.get_patients(search_term = search_fragment)
	if pats is None or len(pats) == 0:
		prompted_input("No patient matches the query term. Press any key to continue.")
		return None
	elif len(pats) > 1:
		for pat in pats:
			print pat
		prompted_input("Several patients match the query term. Press any key to continue.")
		return None
	return pats[0]
#============================================================
# gender related
#------------------------------------------------------------
def get_gender_list():
	global __gender_idx
	global __gender_list
	if __gender_list is None:
		cmd = u"select tag, l10n_tag, label, l10n_label, sort_weight from dem.v_gender_labels order by sort_weight desc"
		__gender_list, __gender_idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	return (__gender_list, __gender_idx)
#------------------------------------------------------------
def map_gender2salutation(gender=None):
	"""Maps GNUmed related i18n-aware gender specifiers to a human-readable salutation."""

	global __gender2salutation_map

	if __gender2salutation_map is None:
		genders, idx = get_gender_list()
		__gender2salutation_map = {
			'm': _('Mr'),
			'f': _('Mrs'),
			'tf': '',
			'tm': '',
			'h': ''
		}
		for g in genders:
			__gender2salutation_map[g[idx['l10n_tag']]] = __gender2salutation_map[g[idx['tag']]]
			__gender2salutation_map[g[idx['label']]] = __gender2salutation_map[g[idx['tag']]]
			__gender2salutation_map[g[idx['l10n_label']]] = __gender2salutation_map[g[idx['tag']]]

	return __gender2salutation_map[gender]
#============================================================
def get_comm_list():	
	global __comm_list
	if __comm_list is None:
		cmd = u"select description from dem.enum_comm_types order by description"
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}])
		__comm_list = []
		for row in rows:
			__comm_list.append(row[0])
	return __comm_list
#============================================================
def get_staff_list(active_only=False):
	if active_only:
		cmd = u"select * from dem.v_staff where is_active order by can_login desc, short_alias asc"
	else:
		cmd = u"select * from dem.v_staff order by can_login desc, is_active desc, short_alias asc"
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx=True)
	staff_list = []
	for row in rows:
		obj_row = {
			'idx': idx,
			'data': row,
			'pk_field': 'pk_staff'
		}
		staff_list.append(cStaff(row=obj_row))
	return staff_list
#============================================================
def get_person_from_xdt(filename=None, encoding=None):
	from Gnumed.business import gmXdtObjects
	return gmXdtObjects.read_person_from_xdt(filename=filename, encoding=encoding)
#============================================================
# main/testing
#============================================================
if __name__ == '__main__':

	_log.SetAllLogLevels(gmLog.lData)
	gmI18N.activate_locale()
	gmI18N.install_domain()

	#--------------------------------------------------------
	def test_set_active_pat():

		ident = cIdentity(1)
		print "setting active patient with", ident
		set_active_patient(patient=ident)


		patient = cPatient(ident)
		print "setting active patient with", patient
		set_active_patient(patient=patient)

		person = cPerson(ident)
		print "setting active patient with", person
		set_active_patient(patient=person)

		staff = cStaff()
		print "setting active patient with", staff
		set_active_patient(patient=staff)

		print "setting active patient with -1"
		set_active_patient(patient=-1)
	#--------------------------------------------------------
	def test_dto_person():
		dto = cDTO_person()
		dto.firstnames = 'Sepp'
		dto.lastnames = 'Herberger'
		dto.gender = 'male'
		dto.dob = mxDT.now()
		print dto

		print dto['firstnames']
		print dto['lastnames']
		print dto['gender']
		print dto['dob']

		for key in dto.keys():
			print key
	#--------------------------------------------------------
	def test_staff():
		me = cStaff()
		print me
	#--------------------------------------------------------
	def test_identity():
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
		print 'Active name: %s' % (new_identity.get_active_name())
		print 'Setting nickname...'
		new_identity.set_nickname(nickname='test nickname')
		print 'Refetching all names...'
		for a_name in new_identity.get_all_names():
			print a_name
		print 'Active name: %s' % (new_identity.get_active_name())		
	 
		print '\nIdentity occupations: %s' % new_identity['occupations']
		print 'Creating identity occupation...'
		new_identity.link_occupation('test occupation')
		print 'Identity occupations: %s' % new_identity['occupations']
	
		print '\nIdentity addresses: %s' % new_identity.get_addresses()
		print 'Creating identity address...'
		# make sure the state exists in the backend
		new_identity.link_address (
			'test 1234',
			'test street',
			'test postcode',
			'test urb',
			'Sachsen',
			'Germany'
		)
		print 'Identity addresses: %s' % new_identity.get_addresses()
		
		print '\nIdentity communications: %s' % new_identity['comms']
		print 'Creating identity communication...'
		new_identity.link_communication('homephone', '1234566')
		print 'Identity communications: %s' % new_identity['comms']
	#--------------------------------------------------------
	def test_patient_search_queries():
		searcher = cPatientSearcher_SQL()

		print "testing _make_sane_caps()"
		print "-------------------------"
		data = ['Lanz', 'McBurney', 'blumberg', 'roVsing']
		for name in data:
			print '%s: %s' % (name, searcher._make_sane_caps(name))

		print "testing _normalize_soundalikes()"
		print "--------------------------------"
		# FIXME: support Ähler -> Äler and Dähler -> Däler
		data = [u'Krüger', u'Krueger', u'Kruger', u'Überle', u'Böger', u'Boger', u'Öder', u'Ähler', u'Däler', u'Großer']
		for name in data:
			print '%s: %s' % (name, searcher._normalize_soundalikes(name))

		print "testing _make_simple_query()"
		print "----------------------------"
		data = ['51234', '1 134 153', '#13 41 34', '#3-AFY322.4', '22-04-1906', '1235/32/3525', ' , johnny']
		for fragment in data:
			print "fragment:", fragment
			qs = searcher._make_simple_query(fragment)
			for q in qs:
				print " match on:", q['args'][0]
				print " query   :", q['cmd']

		print "testing _generate_queries_from_dto()"
		print "------------------------------------"
		dto = cDTO_person()
		dto.gender = 'm'
		dto.lastnames = 'Kirk'
		dto.firstnames = 'James'
		dto.dob = mxDT.now()
		q = searcher._generate_queries_from_dto(dto)[0]
		print "dto:", dto
		print " match on:", q['args']['mt']
		print " query:", q['cmd']

		print "testing _generate_queries_de()"
		print "------------------------------"
		qs = searcher._generate_queries_de('Kirk, James')
		for q in qs:
			print " match on:", q['args'][0]
			print " query   :", q['cmd']
			print " args    :", q['args']

		print "testing _generate_dumb_brute_query()"
		print "------------------------------------"
		q = searcher._generate_dumb_brute_query('Kirk, James Tiberius')
		print " match on:", q['args'][0]
		print " query:", q['cmd']
		print " args:", q['args']
	#--------------------------------------------------------
	def test_ask_for_patient():
		while 1:
			myPatient = ask_for_patient()
			if myPatient is None:
				break
			print "ID       ", myPatient['id']
			identity = myPatient.get_identity()
			print "identity  ", identity
			print "names     ", identity.get_all_names()
			print "addresses:", identity.get_addresses(address_type='home')
#		docs = myPatient.get_document_folder()
#		print "docs     ", docs
#		emr = myPatient.get_emr()
#		print "EMR      ", emr
	#--------------------------------------------------------
	def test_dob2medical_age():
		pass
	#--------------------------------------------------------
#	test_patient_search_queries()
	test_ask_for_patient()
#	test_dto_person()
#	test_staff()
#	test_identity()
#	test_set_active_pat()

#	map_gender2salutation('m')

	# module functions
#	genders, idx = get_gender_list()
#	print "\n\nRetrieving gender enum (tag, label, weight):"	
#	for gender in genders:
#		print "%s, %s, %s" % (gender[idx['tag']], gender[idx['l10n_label']], gender[idx['sort_weight']])
	
#	comms = get_comm_list()
#	print "\n\nRetrieving communication media enum (id, description): %s" % comms
				
#============================================================
# $Log: gmPerson.py,v $
# Revision 1.91  2006-11-19 11:02:33  ncq
# - remove subtable defs, add corresponding APIs
#
# Revision 1.90  2006/11/09 17:46:04  ncq
# - raise exception if dob is about to be set without a timezone
#
# Revision 1.89  2006/11/07 23:43:34  ncq
# - cIdentity now requires datetime.datetime as DOB
# - fix dob2medical_age()
#
# Revision 1.88  2006/11/06 09:58:11  ncq
# - add missing continue in get_identities()
#
# Revision 1.87  2006/11/05 16:01:24  ncq
# - include nick in identity description string, user wants to
#   abuse it for other means
#
# Revision 1.86  2006/11/01 12:54:03  ncq
# - return None from get_last_encounter() if there is none, that's the whole point !
# - fix patient search queries: select distinct on level above order by
#   so pk_identity does not have to be first order by parameter
#
# Revision 1.85  2006/10/31 11:26:56  ncq
# - dob2medical_age(): use datetime.datetime
#
# Revision 1.84  2006/10/28 14:52:07  ncq
# - add get_last_encounter()
#
# Revision 1.83  2006/10/24 13:16:38  ncq
# - add Provider match provider
#
# Revision 1.82  2006/10/21 20:44:06  ncq
# - no longer import gmPG
# - convert to gmPG2
# - add __gender2salutation_map, map_gender2salutation()
# - adjust to changes in gmBusinessDBObject
# - fix patient searcher query generation
# - improved test suite
#
# Revision 1.81  2006/09/13 07:53:26  ncq
# - in get_person_from_xdt() handle encoding
#
# Revision 1.80  2006/07/26 12:22:56  ncq
# - improve set_active_patient
#
# Revision 1.79  2006/07/24 14:16:04  ncq
# - cleanup
#
# Revision 1.78  2006/07/17 21:06:12  ncq
# - cleanup
#
# Revision 1.77  2006/07/17 18:49:07  ncq
# - fix wrong naming
#
# Revision 1.76  2006/07/17 18:08:03  ncq
# - add cDTO_person()
# - add get_patient_from_xdt()
# - fix __generate_queries_generic()
# - cleanup, better testing
#
# Revision 1.75  2006/06/15 07:54:04  ncq
# - allow editing of db_user in cStaff except where cStaff represents CURRENT_USER
#
# Revision 1.74  2006/06/14 10:22:46  ncq
# - create_* stored procs are in schema dem.* now
#
# Revision 1.73  2006/06/12 18:28:32  ncq
# - added missing raise in gmCurrentPatient.__init__()
#
# Revision 1.72  2006/06/09 14:38:42  ncq
# - sort result of get_staff_list()
#
# Revision 1.71  2006/06/06 20:47:39  ncq
# - add is_active to staff class
# - add get_staff_list()
#
# Revision 1.70  2006/05/25 22:12:50  ncq
# - self._patient -> self.patient to be more pythonic
#
# Revision 1.69  2006/05/25 12:07:29  sjtan
#
# base class method needs self object.
#
# Revision 1.68  2006/05/15 13:24:13  ncq
# - signal "activating_patient" -> "pre_patient_selection"
# - signal "patient_selected" -> "post_patient_selection"
#
# Revision 1.67  2006/05/14 21:44:22  ncq
# - add get_workplace() to gmPerson.gmCurrentProvider and make use thereof
# - remove use of gmWhoAmI.py
#
# Revision 1.66  2006/05/12 13:53:08  ncq
# - lazy import gmClinicalRecord
#
# Revision 1.65  2006/05/12 12:03:55  ncq
# - gmLoggedOnStaffMember -> gmCurrentProvider
#
# Revision 1.64  2006/05/10 21:15:58  ncq
# - add current provider Borg
# - add cStaff
#
# Revision 1.63  2006/05/04 09:59:35  ncq
# - add cStaffMember(cPerson)
#
# Revision 1.62  2006/05/04 09:41:05  ncq
# - cPerson
#   - factor out stuff for cPatient
#   - self.__ID -> self._ID for inheritance
# - cPatient
#   - inherit from cPerson
#   - add patient specific methods
#   - deprecate get_clinical_record() over get_emr()
#   - cleanup doc folder instance on cleanup()
# - gmCurrentPatient
#   - keyword change person -> patient
#   - accept cPatient instance
#   - self._person -> self._patient
# - cPatientSearcher_SQL
#   - add get_patients()
# - set_active_patient()
#   - raise ValueError on such
# - ask_for_patient()
#   - improve breakout detection
#   - remove side effect of activating patient
# - make "unit tests" work again
#
# Revision 1.61  2006/01/11 13:14:20  ncq
# - id -> pk
#
# Revision 1.60  2006/01/07 13:13:46  ncq
# - more schema qualifications
#
# Revision 1.59  2006/01/06 10:15:37  ncq
# - lots of small fixes adjusting to "dem" schema
#
# Revision 1.58  2005/11/18 15:16:55  ncq
# - run dumb, brute person search query on really complex search terms
#
# Revision 1.57  2005/11/13 15:28:06  ncq
# - properly fix unicode problem when normalizing name search terms
#
# Revision 1.56  2005/10/09 12:22:54  ihaywood
# new rich text
# widget
# bugfix to gmperson.py
#
# Revision 1.55  2005/09/25 01:00:47  ihaywood
# bugfixes
#
# remember 2.6 uses "import wx" not "from wxPython import wx"
# removed not null constraint on clin_encounter.rfe as has no value on instantiation
# client doesn't try to set clin_encounter.description as it doesn't exist anymore
#
# Revision 1.54  2005/09/19 16:33:31  ncq
# - less incorrect message re EMR loading
#
# Revision 1.53  2005/09/12 15:06:20  ncq
# - add space after title
#
# Revision 1.52  2005/09/11 17:25:31  ncq
# - support force_reload in gmCurrentPatient - needed since Richard wants to
#   reload data when finding the same patient again
#
# Revision 1.51  2005/08/08 08:06:44  ncq
# - cleanup
#
# Revision 1.50  2005/07/24 18:44:33  ncq
# - actually, make it an outright error to stuff strings
#   into DateTime objects - as we can't know the format
#   we couldn't do much about it anyways ... callers better
#   do their part
#
# Revision 1.49  2005/07/24 18:38:42  ncq
# - look out for strings being stuffed into datetime objects
#
# Revision 1.48  2005/06/04 09:30:08  ncq
# - just silly whitespace cleanup
#
# Revision 1.47  2005/06/03 15:24:27  cfmoro
# Fix to make lin_comm work. FIXME added
#
# Revision 1.46  2005/05/28 11:46:28  cfmoro
# Evict cache in identity linking/add methods
#
# Revision 1.45  2005/05/23 12:01:07  cfmoro
# Create/update comms
#
# Revision 1.44  2005/05/19 17:33:07  cfmoro
# Minor fix
#
# Revision 1.43  2005/05/19 16:31:45  ncq
# - handle state_code/country_code in identity.addresses subtable select
#
# Revision 1.42  2005/05/19 15:55:51  ncq
# - de-escalated error level from Panic to Error on failing to add name/nickname
#
# Revision 1.41  2005/05/19 15:19:48  cfmoro
# Minor fixes when object is None
#
# Revision 1.40  2005/05/18 08:27:14  cfmoro
# link_communication failing becouse of situacion of add_to_subtable ( ?
#
# Revision 1.39  2005/05/17 18:01:19  ncq
# - cleanup
#
# Revision 1.38  2005/05/17 14:41:36  cfmoro
# Notebooked patient editor initial code
#
# Revision 1.37  2005/05/17 08:03:05  ncq
# - fix unicode errors in DE query generator normalizer
#
# Revision 1.36  2005/05/14 15:06:18  ncq
# - fix logging error
#
# Revision 1.35  2005/05/12 15:07:25  ncq
# - add get_emr()
#
# Revision 1.34  2005/05/04 08:55:08  ncq
# - streamlining
# - comply with slightly changed subtables API
#
# Revision 1.33  2005/05/01 10:15:59  cfmoro
# Link_XXX methods ported to take advantage of subtables framework. save_payload seems need fixing, as no values are dumped to backed
#
# Revision 1.32  2005/04/28 19:21:18  cfmoro
# zip code streamlining
#
# Revision 1.31  2005/04/28 16:32:19  cfmoro
# Leave town postcode out of linking an address
#
# Revision 1.30  2005/04/26 18:16:13  ncq
# - cIdentity needs a cleanup()
#
# Revision 1.29  2005/04/23 08:48:52  cfmoro
# Improved version of linking communications, controlling duplicates and medium in plpgsql
#
# Revision 1.28  2005/04/23 07:52:38  cfmoro
# Added get_comm_list and cIdentity.link_communication methods
#
# Revision 1.27  2005/04/23 06:14:25  cfmoro
# Added cIdentity.link_address method
#
# Revision 1.26  2005/04/20 21:55:39  ncq
# - just some cleanup
#
# Revision 1.25  2005/04/19 19:51:49  cfmoro
# Names cached in get_all_names. Added get_active_name
#
# Revision 1.24  2005/04/18 19:18:44  ncq
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
