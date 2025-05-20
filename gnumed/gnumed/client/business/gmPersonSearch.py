# -*- coding: utf-8 -*-
"""GNUmed person searching code.

	How-To search:

		name:     Leonard Spock "Pointy-Ears" NIMOY-ZALDANA
		DOB:      Oct 15 1975
		ID:       12345678
		ext ID:   abcd-13d-4d
		ext ID:   #abcd-13d-4d

	find patient by name (first, last, or nick):

		'leon'
		'spo'
		'nimo'
		'zald'
		'pointy'

	find patient by lastname:

		'NIMO'
		'ZALD'
		'nIm,'
		'Zal,'

	find patient by firstname:

		', spo'
		',Leon'

	find patient by nickname:

		'!point'
		'!ear'

	find patient by firstname and lastname:

		'Leonard NIMO'
		'spock ZALDA'

	find patient by fragment anywhere inside name:

		'...ock'
		'...ldan'
		'...moY'
		'...Nar'
		'...Ear'

	find patient by several name parts:

		'leon nim'
		'spo zal'
		'leon nim zald'
		'kirk, jam'

	find patient by GNUmed ID:

		'12345678' (also searches by DOB)
		'#12345678' (also searches by external ID)

	find patient by DOB:

		'15101975' (also searches for GNUmed ID)
		'*15101975'
		'*15/10/1975'
		'*15-10-1975'
		'*15.10.1975'
		'*15 10 1975'

	find patient by external ID:

		'##abcd-13d-4d'		(finds ID "abcd-13d-4d")
		'## #abcd-13d-4d'	(finds ID "#abcd-13d-4d")
"""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

# std lib
import sys
import logging
import re as regex


# setup translation
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
else:
	try:
		_
	except NameError:
		from Gnumed.pycommon import gmI18N
		gmI18N.activate_locale()
		gmI18N.install_domain()


# GNUmed
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmI18N
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime
from Gnumed.business import gmPerson


_log = logging.getLogger('gm.person')

#============================================================
class cPatientSearcher_SQL:
	"""UI independent i18n aware patient searcher."""
	def __init__(self):
		self._generate_queries = self._generate_queries_de
		# make a cursor
		self.conn = gmPG2.get_connection()
		self.curs = self.conn.cursor()
	#--------------------------------------------------------
	def __del__(self):
		try:
			self.curs.close()
		except Exception: pass
		try:
			self.conn.close()
		except Exception: pass
	#--------------------------------------------------------
	# public API
	#--------------------------------------------------------
	def get_patients(self, search_term = None, a_locale = None, dto = None):
		identities = self.get_identities(search_term, a_locale, dto)
		if identities is None:
			return None
		return [ gmPerson.cPatient(aPK_obj=ident['pk_identity']) for ident in identities ]

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
				print("temporary change of locale on patient search not implemented")
				_log.warning("temporary change of locale on patient search not implemented")
			# generate queries
			if search_term is None:
				raise ValueError('need search term (dto AND search_term are None)')

			queries = self._generate_queries(search_term)

		# anything to do ?
		if len(queries) == 0:
			_log.error('query tree empty')
			_log.error('[%s] [%s] [%s]' % (search_term, a_locale, str(dto)))
			return None

		# collect IDs here
		identities = []
		# cycle through query list
		for query in queries:
			_log.debug("running %s" % query)
			try:
				rows = gmPG2.run_ro_queries(queries = [query])
			except Exception:
				_log.exception('error running query')
				continue
			if len(rows) == 0:
				continue
			identities.extend (
				[ gmPerson.cPerson(row = {'pk_field': 'pk_identity', 'data': row}) for row in rows ]
			)

		pks = []
		unique_identities = []
		for identity in identities:
			if identity['pk_identity'] in pks:
				continue
			pks.append(identity['pk_identity'])
			unique_identities.append(identity)

		return unique_identities

	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def _normalize_soundalikes(self, aString = None, aggressive = False):
		"""Transform some characters into a regex."""
		if aString.strip() == '':
			return aString

		# umlauts
		normalized = aString.replace('Ö', '(Ö|OE|Oe|O)')
		normalized = normalized.replace('Ü', '(Ü|UE|Ue|U)')
		normalized = normalized.replace('ö', '(ö|oe|o)')
		normalized = normalized.replace('ü', '(ü|ue|u|y)')
		normalized = normalized.replace('ß', '(ß|sz|ss|s)')

		# common soundalikes
		# - René, Desiré, Inés ...
		normalized = normalized.replace('e', '***DUMMY***')
		normalized = normalized.replace('é', '***DUMMY***')
		normalized = normalized.replace('è', '***DUMMY***')
		normalized = normalized.replace('ë', '***DUMMY***')
		normalized = normalized.replace('ê', '***DUMMY***')
		normalized = normalized.replace('ä', '***DUMMY***')
		normalized = normalized.replace('æ', '***DUMMY***')
		normalized = normalized.replace('ae', '***DUMMY***')
		normalized = normalized.replace('***DUMMY***', '(e|é|è|ë|ê|ä|æ|ae)')
		# upper case
		normalized = normalized.replace('E', '***DUMMY***')
		normalized = normalized.replace('É', '***DUMMY***')
		normalized = normalized.replace('È', '***DUMMY***')
		normalized = normalized.replace('Ë', '***DUMMY***')
		normalized = normalized.replace('Ê', '***DUMMY***')
		normalized = normalized.replace('Ä', '***DUMMY***')
		normalized = normalized.replace('Æ', '***DUMMY***')
		normalized = normalized.replace('Ae', '***DUMMY***')
		normalized = normalized.replace('AE', '***DUMMY***')
		normalized = normalized.replace('***DUMMY***', '(E|É|È|Ë|Ê|Ä|Æ|Ae|AE)')

		# FIXME: missing i/a/o - but uncommon in German
		normalized = normalized.replace('v', '***DUMMY***')
		normalized = normalized.replace('f', '***DUMMY***')
		normalized = normalized.replace('ph', '***DUMMY***')	# now, this is *really* specific for German
		normalized = normalized.replace('***DUMMY***', '(v|f|ph)')

		# silent characters (Thomas vs Tomas)
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

		_log.debug('[%s] -> [%s]' % (aString, normalized))

		return normalized

	#--------------------------------------------------------
	# write your own query generator and add it here:
	# use compile() for speedup
	# must escape strings before use !!
	# ORDER BY !
	# FIXME: what about "< 40" ?
	#--------------------------------------------------------
	def __queries_for_firstname_with_comma(self, raw):
		"""Generate search queries for [ , <alpha> ] search terms."""
		if not raw.startswith(','):
			return []

		raw = raw.lstrip(' ,')
		if not raw.isalpha():
			return []

		_log.debug("[%s]: a firstname" % raw)
		normalized = self._normalize_soundalikes(raw)
		cmd = """-- find patients by ",firstname"
			SELECT DISTINCT ON (pk_identity) * FROM (
				SELECT *, %(match)s AS match_type FROM (
					SELECT d_vap.*
					FROM dem.names, dem.v_active_persons d_vap
					WHERE dem.names.firstnames ~* %(first)s and d_vap.pk_identity = dem.names.id_identity
				) AS super_list ORDER BY lastnames, firstnames, dob
			) AS sorted_list"""
		args = {
			'match': _('first name'),
			'first': '\m' + normalized
		}
		return [{'sql': cmd, 'args': args}]

	#--------------------------------------------------------
	def __queries_for_lastname_with_comma(self, raw):
		"""Generate search queries for [ <alpha> , ] search terms."""
		if not raw.endswith(','):
			return []

		raw = raw.rstrip(' ,')
		if not raw.isalpha():
			return []

		_log.debug("[%s]: a lastname" % raw)
		normalized = self._normalize_soundalikes(raw)
		cmd = """-- find patients by "lastname,":
			SELECT DISTINCT ON (pk_identity) * FROM (
				SELECT *, %(match)s AS match_type FROM ((
					SELECT d_vap.*
					FROM dem.names, dem.v_active_persons d_vap
					WHERE dem.names.lastnames ~* %(last)s and d_vap.pk_identity = dem.names.id_identity
				)) AS super_list ORDER BY lastnames, firstnames, dob
			) AS sorted_list"""
		args = {
			'match': _('last name'),
			'last': '\m%s' % normalized
		}
		return [{'sql': cmd, 'args': args}]

	#--------------------------------------------------------
	def __queries_for_LASTNAME(self, raw):
		"""Generate search queries for [ <ALPHA> ] search terms."""
		if not raw.isalpha():
			return []

		if raw != raw.upper():
			return []

		_log.debug("[%s]: a lastname" % raw)
		normalized = self._normalize_soundalikes(raw)
		cmd = """-- find patients by "LASTNAME":
			SELECT DISTINCT ON (pk_identity) * FROM (
				SELECT *, %(match)s AS match_type FROM (
					SELECT d_vap.*
					FROM dem.names, dem.v_active_persons d_vap
					WHERE dem.names.lastnames ~* %(last)s and d_vap.pk_identity = dem.names.id_identity
				) AS super_list ORDER BY lastnames, firstnames, dob
			) AS sorted_list"""
		args = {
			'match': _('last name'),
			'last': '\m' + normalized
		}
		return [{'sql': cmd, 'args': args}]

	#--------------------------------------------------------
	def __queries_for_name_fragment(self, raw):
		if not raw.startswith('...'):
			return []

		raw = raw.lstrip('.')
		if not raw.isalpha():
			return []

		_log.debug("[%s]: a singular name fragment" % raw)
		fragment = self._normalize_soundalikes(raw)
		SQL = """-- find patients by name fragments anywhere in name:
			SELECT DISTINCT ON (pk_identity) * FROM (
				SELECT *, %(match)s AS match_type FROM (
					SELECT d_vap.*
					FROM dem.names JOIN dem.v_active_persons d_vap ON (d_vap.pk_identity = dem.names.id_identity)
					WHERE
						dem.names.lastnames ~* %(fragment)s
						OR dem.names.firstnames ~* %(fragment)s
						OR dem.names.preferred ~* %(fragment)s
				) AS super_list
				ORDER BY lastnames, firstnames, dob
			) AS sorted_list"""
		args = {
			'match': _('name part'),
			'fragment': fragment
		}
		return [{'sql': SQL, 'args': args}]

	#--------------------------------------------------------
	def __queries_for_nickname(self, raw):
		if not raw.startswith('!'):
			return []

		raw = raw[1:]
		_log.debug("[%s]: a nickname" % raw)
		nick = self._normalize_soundalikes(raw)
		SQL = """-- find patients by name fragments anywhere in name:
			SELECT DISTINCT ON (pk_identity) * FROM (
				SELECT *, %(match)s AS match_type FROM (
					SELECT d_vap.*
					FROM dem.names JOIN dem.v_active_persons d_vap ON (d_vap.pk_identity = dem.names.id_identity)
					WHERE dem.names.preferred ~* %(nick)s
				) AS super_list
				ORDER BY lastnames, firstnames, dob
			) AS sorted_list"""
		args = {
			'match': _('nickname'),
			'nick': nick
		}
		return [{'sql': SQL, 'args': args}]

	#--------------------------------------------------------
	def __queries_for_singular_name_part(self, raw):
		if not raw.isalpha():
			return []

		if len(raw) < 3:
			return []

		_log.debug("[%s]: a singular name part" % raw)
		name = self._normalize_soundalikes(raw)
		SQL = """-- find patients by name part even inside multi-part names:
			SELECT DISTINCT ON (pk_identity) * FROM (
				SELECT *, %(match)s AS match_type FROM (
					SELECT d_vap.*
					FROM dem.names JOIN dem.v_active_persons d_vap ON (d_vap.pk_identity = dem.names.id_identity)
					WHERE dem.names.lastnames ~* %(name)s OR dem.names.firstnames ~* %(name)s OR dem.names.preferred ~* %(name)s
				) AS super_list
				ORDER BY lastnames, firstnames, dob
			) AS sorted_list"""
		args = {
			'match': _('name part'),
			'name': '\m%s' % name
		}
		return [{'sql': SQL, 'args': args}]

	#--------------------------------------------------------
	def __queries_for_several_name_parts(self, raw):
		parts = regex.split(r'[,\.\-\s]+', raw)
		print(parts)
		for p in parts:
			if not p.isalpha():
				return []

		parts = [ p for p in parts if len(p) > 1 ]
		if len(parts) < 2:
			return []

		_log.debug("[%s]: several name parts" % parts)
		parts = [ '\m' + self._normalize_soundalikes(p) for p in parts ]
		SQL = """-- find patients by name parts even inside multi-part names:
			SELECT DISTINCT ON (pk_identity) * FROM (
				SELECT *, %(match)s AS match_type FROM (
					SELECT d_vap.*
					FROM dem.names JOIN dem.v_active_persons d_vap ON (d_vap.pk_identity = dem.names.id_identity)
					WHERE dem.names.lastnames ~* ANY(%(parts)s) AND dem.names.firstnames ~* ANY(%(parts)s)
					-- AND dem.names.preferred ~* ANY(%(parts)s)
				) AS super_list
				ORDER BY lastnames, firstnames, dob
			) AS sorted_list"""
		args = {
			'match': _('name parts'),
			'parts': parts
		}
		return [{'sql': SQL, 'args': args}]

	#--------------------------------------------------------
	def __queries_for_LAST_and_first(self, raw):
		"""Generate search queries for [ <ALPHA> <alpha> ] or [ <alpha> <ALPHA> ] search terms."""
#		if regex.match('^\w+\s+\w+$', raw) is None:
#			return []
#		if raw == raw.upper():
#			# ALL caps
#			return []
#		if raw == raw.lower():
#			# ALL lowercase
#			return []
#		parts = [ p for p in regex.split('\s+', raw) ]
		parts = raw.split()
		if len(parts) != 2:
			return []

		for p in parts:
			if not p.isalpha():
				return []

		p1_upcase = parts[0] == parts[0].upper()
		p2_upcase = parts[1] == parts[1].upper()
		if p1_upcase and p2_upcase:
			return []

		if True not in [p1_upcase, p2_upcase]:
			return []

		if p1_upcase:
			last = parts[0]
			first = parts[1]
		else:
			last = parts[1]
			first = parts[0]

#		last = None
#		if parts[0] == parts[0].upper():
#			last = parts[0]
#			first = parts[1]
#		if parts[1] == parts[1].upper():
#			last = parts[1]
#			first = parts[0]
		# found no UPPERCASE
#		if last is None:
#			return []

		_log.debug("[%s]: <LASTNAME firstname> or firstname LASTNAME" % raw)
		last = self._normalize_soundalikes(last)
		first = self._normalize_soundalikes(first)
		cmd = """-- get patients by "LASTNAME firstname"
			SELECT DISTINCT ON (pk_identity) *
			FROM (
				SELECT *, %(match)s AS match_type
				FROM (
					SELECT d_vap.*
					FROM dem.names, dem.v_active_persons d_vap
					WHERE
						dem.names.lastnames ~* %(last)s
							AND
						dem.names.firstnames ~* %(first)s
							AND
						d_vap.pk_identity = dem.names.id_identity
				) AS super_list
				ORDER BY lastnames, firstnames, dob
			) AS sorted_list"""
		args = {
			'match': _('LASTNAME and firstname'),
			'last': '\m' + last,
			'first': '\m' + first
		}
		return [{'sql': cmd, 'args': args}]

	#--------------------------------------------------------
	def __queries_for_external_id(self, raw):
		eid = raw.lstrip('#').lstrip()
		if not eid:
			return []

		_log.debug("[%s]: an external ID", raw)
		SQL = """-- find patients by external ID:
			SELECT d_vap.*, %(match_type)s::text AS match_type
			FROM dem.lnk_identity2ext_id d_li2ei, dem.v_active_persons d_vap
			WHERE d_vap.pk_identity = d_li2ei.id_identity AND d_li2ei.external_id ~* %(ext_id)s
			ORDER BY lastnames, firstnames, dob;"""
		args = {
			'match_type': _('external patient ID'),
			'ext_id': eid
		}
		return [{'sql': SQL, 'args': args}]

	#--------------------------------------------------------
	def __queries_for_pk(self, raw):
		raw = raw.lstrip('#')
		if not raw.isdigit():
			return []

		_log.debug("[%s]: a PK" % raw)
		SQL = """-- find patient by PK:
			SELECT *, %(match_type)s::text AS match_type
			FROM dem.v_active_persons
			WHERE pk_identity = %(pk)s
			ORDER BY lastnames, firstnames, dob"""
		args = {
			'match_type': _('internal patient ID'),
			'pk': raw
		}
		return [{'sql': SQL, 'args': args}]

	#--------------------------------------------------------
	def __queries_for_pk_or_external_id(self, raw):
		_log.debug("[%s]: a GNUmed patient PK or an external ID", raw)
		if raw.startswith('##'):
			return self.__queries_for_external_id(raw)

		queries = self.__queries_for_pk(raw)
		if queries:
			return queries

		return self.__queries_for_external_id(raw)

	#--------------------------------------------------------
	def __queries_for_DOB(self, raw):
		if len(raw) < 8:
			return []

		dob = raw.lstrip('*')
		dob = dob.replace('.', '-')
		dob = dob.replace('/', '-')
		dob = dob.replace(' ', '-')
		dob = dob.replace('\t', '-')
		digits = dob.replace('-', '')
		if len(digits) < 6:
			return []

		if not digits.isdigit():
			return []

		_log.debug("[%s]: a DOB (-> %s)" % (raw, dob))
		SQL = """-- find patients by DOB:
			SELECT *, %(match_type)s AS match_type
			FROM dem.v_active_persons
			WHERE dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %(dob)s::timestamp with time zone)
			ORDER BY lastnames, firstnames, dob"""
		args = {
			'match_type': _('date of birth'),
			'dob': dob
		}
		return [{'sql': SQL, 'args': args}]

	#--------------------------------------------------------
	def generate_simple_query(self, raw):
		"""Compose queries if search term seems unambiguous."""
		raw = raw.strip()
		if not raw:
			return []

		# "*..." - DOB
		if raw.startswith('*'):
			queries = self.__queries_for_DOB(raw)
			if queries:
				return queries

		# "##.*" - external ID
		if raw.startswith('##'):
			queries = self.__queries_for_external_id(raw)
			if queries:
				return queries

		# "#.*" - GNUmed patient PK or external ID
		if raw.startswith('#'):
			queries = self.__queries_for_pk_or_external_id(raw)
			if queries:
				return queries

		# "...<alpha>" - *anywhere* inside first or last or nick
		if raw.startswith('...'):
			queries = self.__queries_for_name_fragment(raw)
			if queries:
				return queries

		# "!.*" - nickname
		if raw.startswith('!'):
			queries = self.__queries_for_nickname(raw)
			if queries:
				return queries

		# "<digits>" - GNUmed patient PK or DOB
		if raw.isdigit():
			queries = self.__queries_for_pk(raw)
			queries.extend(self.__queries_for_DOB(raw))
			return queries

		# "<d igi ts>" - DOB
		if regex.match(r"^(\d|\s|\t)+$", raw):
			queries = self.__queries_for_DOB(raw)
			if queries:
				return queries

		# digits interspersed with "./-" or blank space - DOB
		if regex.match(r"^\d+(\s|\t|\.|\-|/)*\d+(\s|\t|\.|\-|/)*\d+\.*$", raw):
			queries = self.__queries_for_DOB(raw)
			if queries:
				return queries

		# ", <alpha>" - first name
		queries = self.__queries_for_firstname_with_comma(raw)
		if queries:
			return queries

		# "<alpha>," - last name
		queries = self.__queries_for_lastname_with_comma(raw)
		if queries:
			return queries

		# "<ALPHA>" - last name
		queries = self.__queries_for_LASTNAME(raw)
		if queries:
			return queries

		# "<alpha alpha>" - first last or last first, depending on UPPERCASE
		queries = self.__queries_for_LAST_and_first(raw)
		if queries:
			return queries

		# "<alpha>" - first OR last name OR nick
		queries = self.__queries_for_singular_name_part(raw)
		if queries:
			return queries

		# "<alpha> <alpha> <alpha> ..." - first OR last name OR nick
		queries = self.__queries_for_several_name_parts(raw)
		if queries:
			return queries

		return []

	#--------------------------------------------------------
	# generic, locale independent queries
	#--------------------------------------------------------
	def _generate_queries_from_dto(self, dto = None):
		"""Generate generic queries.

		- not locale dependant
		- data -> firstnames, lastnames, dob, gender
		"""
		_log.debug('_generate_queries_from_dto("%s")' % dto)

		if not isinstance(dto, gmPerson.cDTO_person):
			return None

		vals = [_('name, gender, date of birth')]
		where_snippets = []

		vals.append(dto.firstnames)
		where_snippets.append('firstnames=%s')
		vals.append(dto.lastnames)
		where_snippets.append('lastnames=%s')

		if dto.dob is not None:
			vals.append(dto.dob)
			#where_snippets.append(u"dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone)")
			where_snippets.append("dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %s)")

		if dto.gender is not None:
			vals.append(dto.gender)
			where_snippets.append('gender=%s')

		# sufficient data ?
		if len(where_snippets) == 0:
			_log.error('invalid search dict structure')
			_log.debug(dto)
			return None

		cmd = """
			SELECT *, %%s AS match_type FROM dem.v_active_persons
			WHERE pk_identity in (
				SELECT id_identity FROM dem.names WHERE %s
			) ORDER BY lastnames, firstnames, dob""" % ' and '.join(where_snippets)

		queries = [
			{'sql': cmd, 'args': vals}
		]

		# shall we mogrify name parts ? probably not

		return queries
	#--------------------------------------------------------
	# queries for DE
	#--------------------------------------------------------
	def __generate_queries_from_single_major_part(self, part=None):

		# split on whitespace
		parts_list = regex.split(r"\s+|\t+", part)
		# ignore empty parts
		parts_list = [ p.strip() for p in parts_list if p.strip() != '' ]

		# parse into name/date parts
		date_count = 0
		name_parts = []
		for part in parts_list:
			# any digit signifies a date,		 FIXME: what about "<40" ?
			if regex.search(r"\d", part):
				date_count = date_count + 1
				date_part = part
			else:
				name_parts.append(part)

		# exactly 1 word ?
		if len(parts_list) == 1:
			return []

		# exactly 2 words ?
		if len(parts_list) == 2:
			if date_count > 0:
				# FIXME: either "name date" or "date date"
				_log.error("don't know how to generate queries for [%s]" % part)
				return []
			# no date = "first last" or "last first"
			queries = []
			# assumption: first last
			queries.append ({
				'sql': "SELECT DISTINCT ON (id_identity) d_vap.*, %s::text AS match_type FROM dem.v_active_persons d_vap, dem.names n WHERE d_vap.pk_identity = n.id_identity and n.firstnames ~ %s AND n.lastnames ~ %s",
				'args': [_('name: first-last'), '^' + gmTools.capitalize(name_parts[0], mode=gmTools.CAPS_NAMES), '^' + gmTools.capitalize(name_parts[1], mode=gmTools.CAPS_NAMES)]
			})
			queries.append ({
				'sql': "SELECT DISTINCT ON (id_identity) d_vap.*, %s::text AS match_type FROM dem.v_active_persons d_vap, dem.names n WHERE d_vap.pk_identity = n.id_identity and lower(n.firstnames) ~* lower(%s) AND lower(n.lastnames) ~* lower(%s)",
				'args': [_('name: first-last'), '^' + name_parts[0], '^' + name_parts[1]]
			})
			# assumption: last first
			queries.append ({
				'sql': "SELECT DISTINCT ON (id_identity) d_vap.*, %s::text AS match_type FROM dem.v_active_persons d_vap, dem.names n WHERE d_vap.pk_identity = n.id_identity and n.firstnames ~ %s AND n.lastnames ~ %s",
				'args': [_('name: last-first'), '^' + gmTools.capitalize(name_parts[1], mode=gmTools.CAPS_NAMES), '^' + gmTools.capitalize(name_parts[0], mode=gmTools.CAPS_NAMES)]
			})
			queries.append ({
				'sql': "SELECT DISTINCT ON (id_identity) d_vap.*, %s::text AS match_type FROM dem.v_active_persons d_vap, dem.names n WHERE d_vap.pk_identity = n.id_identity and lower(n.firstnames) ~* lower(%s) AND lower(n.lastnames) ~* lower(%s)",
				'args': [_('name: last-first'), '^' + name_parts[1], '^' + name_parts[0]]
			})
			# assumption: last nick
			queries.append ({
				'sql': "SELECT DISTINCT ON (id_identity) d_vap.*, %s::text AS match_type FROM dem.v_active_persons d_vap, dem.names n WHERE d_vap.pk_identity = n.id_identity and n.preferred ~ %s AND n.lastnames ~ %s",
				'args': [_('name: last-nick'), '^' + gmTools.capitalize(name_parts[1], mode=gmTools.CAPS_NAMES), '^' + gmTools.capitalize(name_parts[0], mode=gmTools.CAPS_NAMES)]
			})
			queries.append ({
				'sql': "SELECT DISTINCT ON (id_identity) d_vap.*, %s::text AS match_type FROM dem.v_active_persons d_vap, dem.names n WHERE d_vap.pk_identity = n.id_identity and lower(n.preferred) ~* lower(%s) AND lower(n.lastnames) ~* lower(%s)",
				'args': [_('name: last-nick'), '^' + name_parts[1], '^' + name_parts[0]]
			})
			# name parts anywhere inside name - third order query ...
			queries.append ({
				'sql': """SELECT DISTINCT ON (id_identity)
							d_vap.*,
							%s::text AS match_type
						FROM
							dem.v_active_persons d_vap
								left join dem.names n on (n.id_identity = d_vap.pk_identity)
						WHERE
							-- name_parts[0]
							(n.firstnames || ' ' || n.lastnames) ~* %s
								AND
							-- name_parts[1]
							(n.firstnames || ' ' || n.lastnames) ~* lower(%s)""",
				'args': [_('name'), name_parts[0], name_parts[1]]
			})
			return queries

		# exactly 3 words ?
		if len(parts_list) == 3:
			if date_count != 1:
				# FIXME: "name name name" or "name date date"
				return []

			# special case: 3 words, exactly 1 of them a date, no ",;"
			# assumption: first, last, dob - first order
			queries.append ({
				'sql': "SELECT DISTINCT ON (id_identity) d_vap.*, %s::text AS match_type FROM dem.v_active_persons d_vap, dem.names n WHERE d_vap.pk_identity = n.id_identity and n.firstnames ~ %s AND n.lastnames ~ %s AND dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone)",
				'args': [_('names: first-last, date of birth'), '^' + gmTools.capitalize(name_parts[0], mode=gmTools.CAPS_NAMES), '^' + gmTools.capitalize(name_parts[1], mode=gmTools.CAPS_NAMES), date_part.replace(',', '.')]
			})
			queries.append ({
				'sql': "SELECT DISTINCT ON (id_identity) d_vap.*, %s::text AS match_type FROM dem.v_active_persons d_vap, dem.names n WHERE d_vap.pk_identity = n.id_identity and lower(n.firstnames) ~* lower(%s) AND lower(n.lastnames) ~* lower(%s) AND dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone)",
				'args': [_('names: first-last, date of birth'), '^' + name_parts[0], '^' + name_parts[1], date_part.replace(',', '.')]
			})
			# assumption: last, first, dob - second order query
			queries.append ({
				'sql': "SELECT DISTINCT ON (id_identity) d_vap.*, %s::text AS match_type FROM dem.v_active_persons d_vap, dem.names n WHERE d_vap.pk_identity = n.id_identity and n.firstnames ~ %s AND n.lastnames ~ %s AND dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone)",
				'args': [_('names: last-first, date of birth'), '^' + gmTools.capitalize(name_parts[1], mode=gmTools.CAPS_NAMES), '^' + gmTools.capitalize(name_parts[0], mode=gmTools.CAPS_NAMES), date_part.replace(',', '.')]
			})
			queries.append ({
				'sql': "SELECT DISTINCT ON (id_identity) d_vap.*, %s::text AS match_type FROM dem.v_active_persons d_vap, dem.names n WHERE d_vap.pk_identity = n.id_identity and lower(n.firstnames) ~* lower(%s) AND lower(n.lastnames) ~* lower(%s) AND dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone)",
				'args': [_('names: last-first, dob'), '^' + name_parts[1], '^' + name_parts[0], date_part.replace(',', '.')]
			})
			# name parts anywhere in name - third order query ...
			queries.append ({
				'sql': """SELECT DISTINCT ON (id_identity)
							d_vap.*,
							%s::text AS match_type
						FROM
							dem.v_active_persons d_vap,
							dem.names n
						WHERE
							d_vap.pk_identity = n.id_identity
								AND
							lower(n.firstnames || ' ' || n.lastnames) ~* lower(%s)
								AND
							lower(n.firstnames || ' ' || n.lastnames) ~* lower(%s)
								AND
							dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone)
				""",
				'args': [_('name, date of birth'), name_parts[0], name_parts[1], date_part.replace(',', '.')]
			})
			return queries

		return []

	#--------------------------------------------------------
	def _generate_queries_de(self, search_term=None):

		if search_term is None:
			return []

		# check to see if we get away with a simple query ...
		queries = self.generate_simple_query(search_term)
		if len(queries) > 0:
			_log.debug('[%s]: search term with a simple, unambiguous structure' % search_term)
			return queries

		# no we don't
		_log.debug('[%s]: not a search term with a simple, unambiguous structure' % search_term)

		search_term = search_term.strip().strip(',').strip(';').strip()
		normalized = self._normalize_soundalikes(search_term)

		queries = []

		# "<CHARS>" - single name part
		# yes, I know, this is culture specific (did you read the docs ?)
		if regex.match(r"^(\s|\t)*[a-zäöüßéáúóçøA-ZÄÖÜÇØ]+(\s|\t)*$", search_term):
			_log.debug("[%s]: a single name part", search_term)
			# there's no intermediate whitespace due to the regex
			cmd = """
				SELECT DISTINCT ON (pk_identity) * FROM (
					SELECT * FROM ((
						-- lastname
						SELECT d_vap.*, %s::text AS match_type FROM dem.v_active_persons d_vap, dem.names n
						WHERE d_vap.pk_identity = n.id_identity and lower(n.lastnames) ~* lower(%s)
					) union all (
						-- firstname
						SELECT d_vap.*, %s::text AS match_type FROM dem.v_active_persons d_vap, dem.names n
						WHERE d_vap.pk_identity = n.id_identity and lower(n.firstnames) ~* lower(%s)
					) union all (
						-- nickname
						SELECT d_vap.*, %s::text AS match_type FROM dem.v_active_persons d_vap, dem.names n
						WHERE d_vap.pk_identity = n.id_identity and lower(n.preferred) ~* lower(%s)
					) union all (
						-- anywhere in name
						SELECT
							d_vap.*,
							%s::text AS match_type
						FROM
							dem.v_active_persons d_vap,
							dem.names n
						WHERE
							d_vap.pk_identity = n.id_identity
								AND
							lower(n.firstnames || ' ' || n.lastnames || ' ' || coalesce(n.preferred, '')) ~* lower(%s)
					)) AS super_list ORDER BY lastnames, firstnames, dob
				) AS sorted_list
			"""
			tmp = normalized.strip()
			args = []
			args.append(_('lastname'))
			args.append('^' + tmp)
			args.append(_('firstname'))
			args.append('^' + tmp)
			args.append(_('nickname'))
			args.append('^' + tmp)
			args.append(_('any name part'))
			args.append(tmp)

			queries.append ({
				'sql': cmd,
				'args': args
			})
			return queries

		# try to split on (major) part separators
		major_parts = regex.split(r',|;', normalized)

		# ignore empty parts
		major_parts = [ p.strip() for p in major_parts if p.strip() != '' ]

		# only one "major" part ? (i.e. no ",;" ?)
		if len(major_parts) == 1:
			_log.debug('[%s]: only one non-empty part after splitting by , or ; ("major" part)', normalized)
			queries = self.__generate_queries_from_single_major_part(part = normalized)
			if len(queries) > 0:
				return queries
			return self._generate_dumb_brute_query(search_term)

		# more than one major part (separated by ';,')
		# this else is not needed
		else:
			_log.debug('[%s]: more than one non-empty part after splitting by , or ; ("major" parts)', normalized)
			# parse into name and date parts
			date_parts = []
			name_parts = []
			name_count = 0
			for part in major_parts:
				if part.strip() == '':
					continue
				# any digits ?
				if regex.search(r"\d+", part):
					# FIXME: parse out whitespace *not* adjacent to a *word*
					date_parts.append(part)
				else:
					tmp = part.strip()
					tmp = regex.split(r"\s+|\t+", tmp)
					name_count = name_count + len(tmp)
					name_parts.append(tmp)

			_log.debug('found %s character (name) parts and %s number (date ?) parts', len(name_parts), len(date_parts))

			where_parts = []
			# first, handle name parts
			# special case: "<date(s)>, <name> <name>, <date(s)>"
			if (len(name_parts) == 1) and (name_count == 2):
				# usually "first last"
				where_parts.append ({
					'conditions': "firstnames ~ %s and lastnames ~ %s",
					'args': [_('names: first last'), '^' + gmTools.capitalize(name_parts[0][0], mode=gmTools.CAPS_NAMES), '^' + gmTools.capitalize(name_parts[0][1], mode=gmTools.CAPS_NAMES)]
				})
				where_parts.append ({
					'conditions': "lower(firstnames) ~* lower(%s) and lower(lastnames) ~* lower(%s)",
					'args': [_('names: first last'), '^' + name_parts[0][0], '^' + name_parts[0][1]]
				})
				# but sometimes "last first""
				where_parts.append ({
					'conditions': "firstnames ~ %s and lastnames ~ %s",
					'args': [_('names: last, first'), '^' + gmTools.capitalize(name_parts[0][1], mode=gmTools.CAPS_NAMES), '^' + gmTools.capitalize(name_parts[0][0], mode=gmTools.CAPS_NAMES)]
				})
				where_parts.append ({
					'conditions': "lower(firstnames) ~* lower(%s) and lower(lastnames) ~* lower(%s)",
					'args': [_('names: last, first'), '^' + name_parts[0][1], '^' + name_parts[0][0]]
				})
				# or even substrings anywhere in name
				where_parts.append ({
					'conditions': "lower(firstnames || ' ' || lastnames) ~* lower(%s) OR lower(firstnames || ' ' || lastnames) ~* lower(%s)",
					'args': [_('name'), name_parts[0][0], name_parts[0][1]]
				})

			# special case: "<date(s)>, <name(s)>, <name(s)>, <date(s)>"
			elif len(name_parts) == 2:
				# usually "last, first"
				where_parts.append ({
					'conditions': "firstnames ~ %s AND lastnames ~ %s",
					'args': [_('name: last, first'), '^' + ' '.join(map(gmTools.capitalize, name_parts[1])), '^' + ' '.join(map(gmTools.capitalize, name_parts[0]))]
				})
				where_parts.append ({
					'conditions': "lower(firstnames) ~* lower(%s) AND lower(lastnames) ~* lower(%s)",
					'args': [_('name: last, first'), '^' + ' '.join(name_parts[1]), '^' + ' '.join(name_parts[0])]
				})
				# but sometimes "first, last"
				where_parts.append ({
					'conditions': "firstnames ~ %s AND lastnames ~ %s",
					'args': [_('name: last, first'), '^' + ' '.join(map(gmTools.capitalize, name_parts[0])), '^' + ' '.join(map(gmTools.capitalize, name_parts[1]))]
				})
				where_parts.append ({
					'conditions': "lower(firstnames) ~* lower(%s) AND lower(lastnames) ~* lower(%s)",
					'args': [_('name: last, first'), '^' + ' '.join(name_parts[0]), '^' + ' '.join(name_parts[1])]
				})
				# and sometimes "last, nick"
				where_parts.append ({
					'conditions': "preferred ~ %s AND lastnames ~ %s",
					'args': [_('name: last, first'), '^' + ' '.join(map(gmTools.capitalize, name_parts[1])), '^' + ' '.join(map(gmTools.capitalize, name_parts[0]))]
				})
				where_parts.append ({
					'conditions': "lower(preferred) ~* lower(%s) AND lower(lastnames) ~* lower(%s)",
					'args': [_('name: last, first'), '^' + ' '.join(name_parts[1]), '^' + ' '.join(name_parts[0])]
				})

				# or even substrings anywhere in name
				where_parts.append ({
					'conditions': "lower(firstnames || ' ' || lastnames) ~* lower(%s) AND lower(firstnames || ' ' || lastnames) ~* lower(%s)",
					'args': [_('name'), ' '.join(name_parts[0]), ' '.join(name_parts[1])]
				})

			# big trouble - arbitrary number of names
			else:
				# FIXME: deep magic, not sure of rationale ...
				if len(name_parts) == 1:
					for part in name_parts[0]:
						where_parts.append ({
							'conditions': "lower(firstnames || ' ' || lastnames) ~* lower(%s)",
							'args': [_('name'), part]
						})
				else:
					tmp = []
					for part in name_parts:
						tmp.append(' '.join(part))
					for part in tmp:
						where_parts.append ({
							'conditions': "lower(firstnames || ' ' || lastnames) ~* lower(%s)",
							'args': [_('name'), part]
						})

			# secondly handle date parts
			# FIXME: this needs a considerable smart-up !
			if len(date_parts) == 1:
				if len(where_parts) == 0:
					where_parts.append ({
						'conditions': "dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone)",
						'args': [_('date of birth'), date_parts[0].replace(',', '.')]
					})
				if len(where_parts) > 0:
					where_parts[0]['conditions'] += " AND dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone)"
					where_parts[0]['args'].append(date_parts[0].replace(',', '.'))
					where_parts[0]['args'][0] += ', ' + _('date of birth')
				if len(where_parts) > 1:
					where_parts[1]['conditions'] += " AND dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone)"
					where_parts[1]['args'].append(date_parts[0].replace(',', '.'))
					where_parts[1]['args'][0] += ', ' + _('date of birth')
			elif len(date_parts) > 1:
				if len(where_parts) == 0:
					where_parts.append ({
						'conditions': "dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone) AND dem.date_trunc_utc('day'::text, dem.identity.deceased) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone)",
						'args': [_('date of birth/death'), date_parts[0].replace(',', '.'), date_parts[1].replace(',', '.')]
					})
				if len(where_parts) > 0:
					where_parts[0]['conditions'] += " AND dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone) AND dem.date_trunc_utc('day'::text, dem.identity.deceased) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone)"
					where_parts[0]['args'].append(date_parts[0].replace(',', '.'), date_parts[1].replace(',', '.'))
					where_parts[0]['args'][0] += ', ' + _('date of birth/death')
				if len(where_parts) > 1:
					where_parts[1]['conditions'] += " AND dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone) AND dem.date_trunc_utc('day'::text, dem.identity.deceased) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone)"
					where_parts[1]['args'].append(date_parts[0].replace(',', '.'), date_parts[1].replace(',', '.'))
					where_parts[1]['args'][0] += ', ' + _('date of birth/death')

			# and finally generate the queries ...
			for where_part in where_parts:
				queries.append ({
					'sql': "SELECT *, %%s::text AS match_type FROM dem.v_active_persons WHERE %s" % where_part['conditions'],
					'args': where_part['args']
				})
			return queries

		return []
	#--------------------------------------------------------
	def _generate_dumb_brute_query(self, search_term=''):

		_log.debug('_generate_dumb_brute_query("%s")' % search_term)

		where_clause = ''
		args = []
		# FIXME: split on more than just ' '
		for arg in search_term.strip().split():
			where_clause += " AND lower(coalesce(d_vap.title, '') || ' ' || d_vap.firstnames || ' ' || d_vap.lastnames) ~* lower(%s)"
			args.append(arg)

		query = """
SELECT DISTINCT ON (pk_identity) * FROM (
	SELECT
		d_vap.*,
		'%s'::text AS match_type
	FROM
		dem.v_active_persons d_vap,
		dem.names n
	WHERE
		d_vap.pk_identity = n.id_identity
		%s
	ORDER BY
		lastnames,
		firstnames,
		dob
) AS ordered_list""" % (_('full name'), where_clause)

		return ({'sql': query, 'args': args})

#============================================================
def ask_for_patient():
	"""Text mode UI function to ask for patient."""

	person_searcher = cPatientSearcher_SQL()

	while True:
		search_fragment = gmTools.prompted_input(prompt = "\nEnter person search term or leave blank to exit")

		if search_fragment in ['exit', 'quit', 'bye', None]:
			print("user cancelled patient search")
			return None

		pats = person_searcher.get_patients(search_term = search_fragment)

		if (pats is None) or (len(pats) == 0):
			print("No patient matches the search term.")
			print("")
			continue

		if len(pats) > 1:
			print("Several patients match the search term:")
			print("")
			for pat in pats:
				print(pat)
				print("")
			print("Please refine the search term so it matches one patient only.")
			continue

		return pats[0]

	return None

#============================================================
# main/testing
#============================================================
if __name__ == '__main__':

	if len(sys.argv) == 1:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	# setup a real translation
	del _
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain('gnumed')

	import datetime
	gmDateTime.init()

	#--------------------------------------------------------
	def test_search_by_dto():
		dto = gmPerson.cDTO_person()
		dto.firstnames = 'Sigrid'
		dto.lastnames = 'Kiesewetter'
		dto.gender = 'female'
#		dto.dob = pyDT.datetime.now(tz=gmDateTime.gmCurrentLocalTimezone)
		dto.dob = datetime.datetime(1939,6,24,23,0,0,0,gmDateTime.gmCurrentLocalTimezone)
		print(dto)

		searcher = cPatientSearcher_SQL()
		pats = searcher.get_patients(dto = dto)
		print(pats)
	#--------------------------------------------------------
	def test_patient_search_queries():
		searcher = cPatientSearcher_SQL()

		print("testing _normalize_soundalikes()")
		print("--------------------------------")
		# FIXME: support Ähler -> Äler and Dähler -> Däler
		data = ['Krüger', 'Krueger', 'Kruger', 'Überle', 'Böger', 'Boger', 'Öder', 'Ähler', 'Däler', 'Großer', 'müller', 'Özdemir', 'özdemir']
		for name in data:
			print('%s: %s' % (name, searcher._normalize_soundalikes(name)))

		input('press [ENTER] to continue')
		print("============")

		print("testing _generate_queries_from_dto()")
		print("------------------------------------")
		dto = gmPerson.cDTO_person()
		dto.gender = 'm'
		dto.lastnames = 'Kirk'
		dto.firstnames = 'James'
		dto.dob = datetime.datetime.now(tz=gmDateTime.gmCurrentLocalTimezone)
		q = searcher._generate_queries_from_dto(dto)[0]
		print("dto:", dto)
		print(" match on:", q['args'][0])
		print(" query:", q['sql'])

		input('press [ENTER] to continue')
		print("============")

		print("testing _generate_queries_de()")
		print("------------------------------")
		qs = searcher._generate_queries_de('Kirk, James')
		for q in qs:
			print(" match on:", q['args'][0])
			print(" query   :", q['sql'])
			print(" args    :", q['args'])
		input('press [ENTER] to continue')
		print("============")

		qs = searcher._generate_queries_de('müller')
		for q in qs:
			print(" match on:", q['args'][0])
			print(" query   :", q['sql'])
			print(" args    :", q['args'])
		input('press [ENTER] to continue')
		print("============")

		qs = searcher._generate_queries_de('özdemir')
		for q in qs:
			print(" match on:", q['args'][0])
			print(" query   :", q['sql'])
			print(" args    :", q['args'])
		input('press [ENTER] to continue')
		print("============")

		qs = searcher._generate_queries_de('Özdemir')
		for q in qs:
			print(" match on:", q['args'][0])
			print(" query   :", q['sql'])
			print(" args    :", q['args'])
		input('press [ENTER] to continue')
		print("============")

		print("testing _generate_dumb_brute_query()")
		print("------------------------------------")
		q = searcher._generate_dumb_brute_query('Kirk, James Tiberius')
		print(" match on:", q['args'][0])
		print(" args:", q['args'])
		print(" query:", q['sql'])


		input('press [ENTER] to continue')
	#--------------------------------------------------------
	def test_ask_for_patient():
		while 1:
			myPatient = ask_for_patient()
			if myPatient is None:
				break
			print("ID       ", myPatient.ID)
			print("names     ", myPatient.get_names())
			print("addresses:", myPatient.get_addresses(address_type='home'))
			print("recent birthday:", myPatient.dob_in_range())
			myPatient.export_as_gdt(filename='apw.gdt', encoding = 'cp850')
#		docs = myPatient.get_document_folder()
#		print "docs     ", docs
#		emr = myPatient.emr
#		print "EMR      ", emr

	#--------------------------------------------------------
	def test_generate_simple_query():
		searcher = cPatientSearcher_SQL()
		print("testing generate_simple_query()")
		print("----------------------------")
		data = [
			'jam tib, kir',
			'...tiber',
			'...iber',
			'kirk',
			'#123',
			'#1 23',
			'##123',
			'##1 23',
			'#abc',
			'##abc',
			'## #abc',
			'123',
			'1 23',
			'1 23 1974'
			'!Pointy'
#			'51234', '1 134 153', '#13 41 34', '#3-AFY322.4', '22-04-1906', '1235/32/3525',
#			', tiberiu',# firstname
#			'KIRK',		# lastname
#			'kirk,',	# lastname + comma
#			'Kirk,',	# lastname + comma
#			'KIR tib',	# LAST first
#			'Tib KI'	# first LAST
		]
		for fragment in data:
			print("fragment:", fragment)
			qs = searcher.generate_simple_query(fragment)
			for q in qs:
				print('')
				print(" query   :", q['sql'])
				print(" match on:", q['args'])
				print(gmPG2.run_ro_queries(queries = [q]))
			input('press [ENTER] to continue')
			print("============")

	#--------------------------------------------------------
	gmPG2.request_login_params(setup_pool = True)

	#test_generate_simple_query()
	#test_patient_search_queries()
	test_ask_for_patient()
	#test_search_by_dto()

#============================================================
