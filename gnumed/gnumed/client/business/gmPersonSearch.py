# -*- coding: utf-8 -*-
"""GNUmed person searching code."""
#============================================================
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL"

# std lib
import sys, logging, re as regex


# GNUmed
if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2, gmI18N, gmTools, gmDateTime
from Gnumed.business import gmPerson


_log = logging.getLogger('gm.person')
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
				print "temporary change of locale on patient search not implemented"
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
				rows, idx = gmPG2.run_ro_queries(queries = [query], get_col_idx=True)
			except:
				_log.exception('error running query')
				continue
			if len(rows) == 0:
				continue
			identities.extend (
				[ gmPerson.cPerson(row = {'pk_field': 'pk_identity', 'data': row, 'idx': idx}) for row in rows ]
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
		if aString.strip() == u'':
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
		normalized = normalized.replace(u'v', u'***DUMMY***')
		normalized = normalized.replace(u'f', u'***DUMMY***')
		normalized = normalized.replace(u'ph', u'***DUMMY***')	# now, this is *really* specific for German
		normalized = normalized.replace(u'***DUMMY***', u'(v|f|ph)')

		# silent characters (Thomas vs Tomas)
		normalized = normalized.replace(u'Th',u'***DUMMY***')
		normalized = normalized.replace(u'T', u'***DUMMY***')
		normalized = normalized.replace(u'***DUMMY***', u'(Th|T)')
		normalized = normalized.replace(u'th', u'***DUMMY***')
		normalized = normalized.replace(u't', u'***DUMMY***')
		normalized = normalized.replace(u'***DUMMY***', u'(th|t)')

		# apostrophes, hyphens et al
		normalized = normalized.replace(u'"', u'***DUMMY***')
		normalized = normalized.replace(u"'", u'***DUMMY***')
		normalized = normalized.replace(u'`', u'***DUMMY***')
		normalized = normalized.replace(u'***DUMMY***', u"""("|'|`|***DUMMY***|\s)*""")
		normalized = normalized.replace(u'-', u"""(-|\s)*""")
		normalized = normalized.replace(u'|***DUMMY***|', u'|-|')

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
	def _generate_simple_query(self, raw):
		"""Compose queries if search term seems unambigous."""
		queries = []

		raw = raw.strip().rstrip(u',').rstrip(u';').strip()

		# "<digits>" - GNUmed patient PK or DOB
		if regex.match(u"^(\s|\t)*\d+(\s|\t)*$", raw, flags = regex.LOCALE | regex.UNICODE):
			_log.debug("[%s]: a PK or DOB" % raw)
			tmp = raw.strip()
			queries.append ({
				'cmd': u"SELECT *, %s::text AS match_type FROM dem.v_active_persons WHERE pk_identity = %s ORDER BY lastnames, firstnames, dob",
				'args': [_('internal patient ID'), tmp]
			})
			if len(tmp) > 7:	# DOB needs at least 8 digits
				queries.append ({
					'cmd': u"SELECT *, %s::text AS match_type FROM dem.v_active_persons WHERE dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone) ORDER BY lastnames, firstnames, dob",
					'args': [_('date of birth'), tmp.replace(',', '.')]
				})
			queries.append ({
				'cmd': u"""
					SELECT vba.*, %s::text AS match_type
					FROM
						dem.lnk_identity2ext_id li2ext_id,
						dem.v_active_persons vba
					WHERE
						vba.pk_identity = li2ext_id.id_identity and lower(li2ext_id.external_id) ~* lower(%s)
					ORDER BY
						lastnames, firstnames, dob
				""",
				'args': [_('external patient ID'), tmp]
			})
			return queries

		# "<d igi ts>" - DOB or patient PK
		if regex.match(u"^(\d|\s|\t)+$", raw, flags = regex.LOCALE | regex.UNICODE):
			_log.debug("[%s]: a DOB or PK" % raw)
			queries.append ({
				'cmd': u"SELECT *, %s::text AS match_type FROM dem.v_active_persons WHERE dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone) ORDER BY lastnames, firstnames, dob",
				'args': [_('date of birth'), raw.replace(',', '.')]
			})
			tmp = raw.replace(u' ', u'')
			tmp = tmp.replace(u'\t', u'')
			queries.append ({
				'cmd': u"SELECT *, %s::text AS match_type FROM dem.v_active_persons WHERE pk_identity LIKE %s%%",
				'args': [_('internal patient ID'), tmp]
			})
			return queries

		# "#<di git  s>" - GNUmed patient PK
		if regex.match(u"^(\s|\t)*#(\d|\s|\t)+$", raw, flags = regex.LOCALE | regex.UNICODE):
			_log.debug("[%s]: a PK or external ID" % raw)
			tmp = raw.replace(u'#', u'')
			tmp = tmp.strip()
			tmp = tmp.replace(u' ', u'')
			tmp = tmp.replace(u'\t', u'')
			# this seemingly stupid query ensures the PK actually exists
			queries.append ({
				'cmd': u"SELECT *, %s::text AS match_type FROM dem.v_active_persons WHERE pk_identity = %s ORDER BY lastnames, firstnames, dob",
				'args': [_('internal patient ID'), tmp]
			})
			# but might also be an external ID
			tmp = raw.replace(u'#', u'')
			tmp = tmp.strip()
			tmp = tmp.replace(u' ',  u'***DUMMY***')
			tmp = tmp.replace(u'\t', u'***DUMMY***')
			tmp = tmp.replace(u'***DUMMY***', u'(\s|\t|-|/)*')
			queries.append ({
				'cmd': u"""
					SELECT vba.*, %s::text AS match_type FROM dem.lnk_identity2ext_id li2ext_id, dem.v_active_persons vba
					WHERE vba.pk_identity = li2ext_id.id_identity and lower(li2ext_id.external_id) ~* lower(%s)
					ORDER BY lastnames, firstnames, dob""",
				'args': [_('external patient ID'), tmp]
			})
			return queries

		# "#<di/git s or c-hars>" - external ID
		if regex.match(u"^(\s|\t)*#.+$", raw, flags = regex.LOCALE | regex.UNICODE):
			_log.debug("[%s]: an external ID" % raw)
			tmp = raw.replace(u'#', u'')
			tmp = tmp.strip()
			tmp = tmp.replace(u' ',  u'***DUMMY***')
			tmp = tmp.replace(u'\t', u'***DUMMY***')
			tmp = tmp.replace(u'-',  u'***DUMMY***')
			tmp = tmp.replace(u'/',  u'***DUMMY***')
			tmp = tmp.replace(u'***DUMMY***', u'(\s|\t|-|/)*')
			queries.append ({
				'cmd': u"""
					SELECT
						vba.*,
						%s::text AS match_type
					FROM
						dem.lnk_identity2ext_id li2ext_id,
						dem.v_active_persons vba
					WHERE
						vba.pk_identity = li2ext_id.id_identity
							AND
						lower(li2ext_id.external_id) ~* lower(%s)
					ORDER BY
						lastnames, firstnames, dob""",
				'args': [_('external patient ID'), tmp]
			})
			return queries

		# digits interspersed with "./-" or blank space - DOB
		if regex.match(u"^(\s|\t)*\d+(\s|\t|\.|\-|/)*\d+(\s|\t|\.|\-|/)*\d+(\s|\t|\.)*$", raw, flags = regex.LOCALE | regex.UNICODE):
			_log.debug("[%s]: a DOB" % raw)
			tmp = raw.strip()
			while u'\t\t' in tmp: tmp = tmp.replace(u'\t\t', u' ')
			while u'  ' in tmp: tmp = tmp.replace(u'  ', u' ')
			# apparently not needed due to PostgreSQL smarts...
			#tmp = tmp.replace('-', '.')
			#tmp = tmp.replace('/', '.')
			queries.append ({
				'cmd': u"SELECT *, %s AS match_type FROM dem.v_active_persons WHERE dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone) ORDER BY lastnames, firstnames, dob",
				'args': [_('date of birth'), tmp.replace(',', '.')]
			})
			return queries

		# " , <alpha>" - first name
		if regex.match(u"^(\s|\t)*,(\s|\t)*([^0-9])+(\s|\t)*$", raw, flags = regex.LOCALE | regex.UNICODE):
			_log.debug("[%s]: a firstname" % raw)
			tmp = self._normalize_soundalikes(raw[1:].strip())
			cmd = u"""
SELECT DISTINCT ON (pk_identity) * FROM (
	SELECT *, %s AS match_type FROM ((
		SELECT d_vap.*
		FROM dem.names, dem.v_active_persons d_vap
		WHERE dem.names.firstnames ~ %s and d_vap.pk_identity = dem.names.id_identity
	) union all (
		SELECT d_vap.*
		FROM dem.names, dem.v_active_persons d_vap
		WHERE dem.names.firstnames ~ %s and d_vap.pk_identity = dem.names.id_identity
	)) AS super_list ORDER BY lastnames, firstnames, dob
) AS sorted_list"""
			queries.append ({
				'cmd': cmd,
				'args': [_('first name'), '^' + gmTools.capitalize(tmp, mode=gmTools.CAPS_NAMES), '^' + tmp]
			})
			return queries

		# "*|$<...>" - DOB
		if regex.match(u"^(\s|\t)*(\*|\$).+$", raw, flags = regex.LOCALE | regex.UNICODE):
			_log.debug("[%s]: a DOB" % raw)
			tmp = raw.replace(u'*', u'')
			tmp = tmp.replace(u'$', u'')
			queries.append ({
				'cmd': u"SELECT *, %s AS match_type FROM dem.v_active_persons WHERE dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone) ORDER BY lastnames, firstnames, dob",
				'args': [_('date of birth'), tmp.replace(u',', u'.')]
			})
			return queries

		return queries	# = []
	#--------------------------------------------------------
	# generic, locale independant queries
	#--------------------------------------------------------
	def _generate_queries_from_dto(self, dto = None):
		"""Generate generic queries.

		- not locale dependant
		- data -> firstnames, lastnames, dob, gender
		"""
		_log.debug(u'_generate_queries_from_dto("%s")' % dto)

		if not isinstance(dto, gmPerson.cDTO_person):
			return None

		vals = [_('name, gender, date of birth')]
		where_snippets = []

		vals.append(dto.firstnames)
		where_snippets.append(u'firstnames=%s')
		vals.append(dto.lastnames)
		where_snippets.append(u'lastnames=%s')

		if dto.dob is not None:
			vals.append(dto.dob)
			#where_snippets.append(u"dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone)")
			where_snippets.append(u"dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %s)")

		if dto.gender is not None:
			vals.append(dto.gender)
			where_snippets.append('gender=%s')

		# sufficient data ?
		if len(where_snippets) == 0:
			_log.error('invalid search dict structure')
			_log.debug(data)
			return None

		cmd = u"""
			SELECT *, %%s AS match_type FROM dem.v_active_persons
			WHERE pk_identity in (
				SELECT id_identity FROM dem.names WHERE %s
			) ORDER BY lastnames, firstnames, dob""" % ' and '.join(where_snippets)

		queries = [
			{'cmd': cmd, 'args': vals}
		]

		# shall we mogrify name parts ? probably not

		return queries
	#--------------------------------------------------------
	# queries for DE
	#--------------------------------------------------------
	def _generate_queries_de(self, search_term=None):

		if search_term is None:
			return []

		# check to see if we get away with a simple query ...
		queries = self._generate_simple_query(search_term)
		if len(queries) > 0:
			_log.debug('[%s]: search term with a simple, unambigous structure' % search_term)
			return queries

		# no we don't
		_log.debug('[%s]: not a search term with a simple, unambigous structure' % search_term)

		search_term = search_term.strip().strip(u',').strip(u';').strip()
		normalized = self._normalize_soundalikes(search_term)

		queries = []

		# "<CHARS>" - single name part
		# yes, I know, this is culture specific (did you read the docs ?)
		if regex.match(u"^(\s|\t)*[a-zäöüßéáúóçøA-ZÄÖÜÇØ]+(\s|\t)*$", search_term, flags = regex.LOCALE | regex.UNICODE):	
			_log.debug("[%s]: a single name part", search_term)
			# there's no intermediate whitespace due to the regex
			cmd = u"""
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
				'cmd': cmd,
				'args': args
			})
			return queries

		# try to split on (major) part separators
		parts_list = regex.split(u",|;", normalized)

		# ignore empty parts
		parts_list = [ p.strip() for p in parts_list if p.strip() != u'' ]

		# only one "major" part ? (i.e. no ",;" ?)
		if len(parts_list) == 1:
			# re-split on whitespace
			sub_parts_list = regex.split(u"\s*|\t*", normalized)
			# ignore empty parts
			sub_parts_list = [ p.strip() for p in sub_parts_list if p.strip() != u'' ]

			# parse into name/date parts
			date_count = 0
			name_parts = []
			for part in sub_parts_list:
				# skip empty parts
				if part.strip() == u'':
					continue
				# any digit signifies a date
				# FIXME: what about "<40" ?
				if regex.search(u"\d", part, flags = regex.LOCALE | regex.UNICODE):
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
						'cmd': u"SELECT DISTINCT ON (id_identity) d_vap.*, %s::text AS match_type FROM dem.v_active_persons d_vap, dem.names n WHERE d_vap.pk_identity = n.id_identity and n.firstnames ~ %s AND n.lastnames ~ %s",
						'args': [_('name: first-last'), '^' + gmTools.capitalize(name_parts[0], mode=gmTools.CAPS_NAMES), '^' + gmTools.capitalize(name_parts[1], mode=gmTools.CAPS_NAMES)]
					})
					queries.append ({
						'cmd': u"SELECT DISTINCT ON (id_identity) d_vap.*, %s::text AS match_type FROM dem.v_active_persons d_vap, dem.names n WHERE d_vap.pk_identity = n.id_identity and lower(n.firstnames) ~* lower(%s) AND lower(n.lastnames) ~* lower(%s)",
						'args': [_('name: first-last'), '^' + name_parts[0], '^' + name_parts[1]]
					})
					# assumption: last first
					queries.append ({
						'cmd': u"SELECT DISTINCT ON (id_identity) d_vap.*, %s::text AS match_type FROM dem.v_active_persons d_vap, dem.names n WHERE d_vap.pk_identity = n.id_identity and n.firstnames ~ %s AND n.lastnames ~ %s",
						'args': [_('name: last-first'), '^' + gmTools.capitalize(name_parts[1], mode=gmTools.CAPS_NAMES), '^' + gmTools.capitalize(name_parts[0], mode=gmTools.CAPS_NAMES)]
					})
					queries.append ({
						'cmd': u"SELECT DISTINCT ON (id_identity) d_vap.*, %s::text AS match_type FROM dem.v_active_persons d_vap, dem.names n WHERE d_vap.pk_identity = n.id_identity and lower(n.firstnames) ~* lower(%s) AND lower(n.lastnames) ~* lower(%s)",
						'args': [_('name: last-first'), '^' + name_parts[1], '^' + name_parts[0]]
					})
					print "before nick"
					print queries
					# assumption: last nick
					queries.append ({
						'cmd': u"SELECT DISTINCT ON (id_identity) d_vap.*, %s::text AS match_type FROM dem.v_active_persons d_vap, dem.names n WHERE d_vap.pk_identity = n.id_identity and n.preferred ~ %s AND n.lastnames ~ %s",
						'args': [_('name: last-nick'), '^' + gmTools.capitalize(name_parts[1], mode=gmTools.CAPS_NAMES), '^' + gmTools.capitalize(name_parts[0], mode=gmTools.CAPS_NAMES)]
					})
					queries.append ({
						'cmd': u"SELECT DISTINCT ON (id_identity) d_vap.*, %s::text AS match_type FROM dem.v_active_persons d_vap, dem.names n WHERE d_vap.pk_identity = n.id_identity and lower(n.preferred) ~* lower(%s) AND lower(n.lastnames) ~* lower(%s)",
						'args': [_('name: last-nick'), '^' + name_parts[1], '^' + name_parts[0]]
					})
					print "after nick"
					print queries
					# name parts anywhere inside name - third order query ...
					queries.append ({
						'cmd': u"""SELECT DISTINCT ON (id_identity)
									d_vap.*,
									%s::text AS match_type
								FROM
									dem.v_active_persons d_vap,
									dem.names n
								WHERE
									d_vap.pk_identity = n.id_identity
										AND
									-- name_parts[0]
									lower(n.firstnames || ' ' || n.lastnames) ~* lower(%s)
										AND
									-- name_parts[1]
									lower(n.firstnames || ' ' || n.lastnames) ~* lower(%s)""",
						'args': [_('name'), name_parts[0], name_parts[1]]
					})
					return queries
				# FIXME: either "name date" or "date date"
				_log.error("don't know how to generate queries for [%s]" % search_term)
				return queries

			# exactly 3 words ?
			if len(sub_parts_list) == 3:
				# special case: 3 words, exactly 1 of them a date, no ",;"
				if date_count == 1:
					# assumption: first, last, dob - first order
					queries.append ({
						'cmd': u"SELECT DISTINCT ON (id_identity) d_vap.*, %s::text AS match_type FROM dem.v_active_persons d_vap, dem.names n WHERE d_vap.pk_identity = n.id_identity and n.firstnames ~ %s AND n.lastnames ~ %s AND dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone)",
						'args': [_('names: first-last, date of birth'), '^' + gmTools.capitalize(name_parts[0], mode=gmTools.CAPS_NAMES), '^' + gmTools.capitalize(name_parts[1], mode=gmTools.CAPS_NAMES), date_part.replace(u',', u'.')]
					})
					queries.append ({
						'cmd': u"SELECT DISTINCT ON (id_identity) d_vap.*, %s::text AS match_type FROM dem.v_active_persons d_vap, dem.names n WHERE d_vap.pk_identity = n.id_identity and lower(n.firstnames) ~* lower(%s) AND lower(n.lastnames) ~* lower(%s) AND dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone)",
						'args': [_('names: first-last, date of birth'), '^' + name_parts[0], '^' + name_parts[1], date_part.replace(u',', u'.')]
					})
					# assumption: last, first, dob - second order query
					queries.append ({
						'cmd': u"SELECT DISTINCT ON (id_identity) d_vap.*, %s::text AS match_type FROM dem.v_active_persons d_vap, dem.names n WHERE d_vap.pk_identity = n.id_identity and n.firstnames ~ %s AND n.lastnames ~ %s AND dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone)",
						'args': [_('names: last-first, date of birth'), '^' + gmTools.capitalize(name_parts[1], mode=gmTools.CAPS_NAMES), '^' + gmTools.capitalize(name_parts[0], mode=gmTools.CAPS_NAMES), date_part.replace(u',', u'.')]
					})
					queries.append ({
						'cmd': u"SELECT DISTINCT ON (id_identity) d_vap.*, %s::text AS match_type FROM dem.v_active_persons d_vap, dem.names n WHERE d_vap.pk_identity = n.id_identity and lower(n.firstnames) ~* lower(%s) AND lower(n.lastnames) ~* lower(%s) AND dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone)",
						'args': [_('names: last-first, dob'), '^' + name_parts[1], '^' + name_parts[0], date_part.replace(u',', u'.')]
					})
					# name parts anywhere in name - third order query ...
					queries.append ({
						'cmd': u"""SELECT DISTINCT ON (id_identity)
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
						'args': [_('name, date of birth'), name_parts[0], name_parts[1], date_part.replace(u',', u'.')]
					})
					return queries
				# FIXME: "name name name" or "name date date"
				queries.append(self._generate_dumb_brute_query(search_term))
				return queries

			# FIXME: no ',;' but neither "name name" nor "name name date"
			queries.append(self._generate_dumb_brute_query(search_term))
			return queries

		# more than one major part (separated by ';,')
		else:
			# parse into name and date parts
			date_parts = []
			name_parts = []
			name_count = 0
			for part in parts_list:
				if part.strip() == u'':
					continue
				# any digits ?
				if regex.search(u"\d+", part, flags = regex.LOCALE | regex.UNICODE):
					# FIXME: parse out whitespace *not* adjacent to a *word*
					date_parts.append(part)
				else:
					tmp = part.strip()
					tmp = regex.split(u"\s*|\t*", tmp)
					name_count = name_count + len(tmp)
					name_parts.append(tmp)

			where_parts = []
			# first, handle name parts
			# special case: "<date(s)>, <name> <name>, <date(s)>"
			if (len(name_parts) == 1) and (name_count == 2):
				# usually "first last"
				where_parts.append ({
					'conditions': u"firstnames ~ %s and lastnames ~ %s",
					'args': [_('names: first last'), '^' + gmTools.capitalize(name_parts[0][0], mode=gmTools.CAPS_NAMES), '^' + gmTools.capitalize(name_parts[0][1], mode=gmTools.CAPS_NAMES)]
				})
				where_parts.append ({
					'conditions': u"lower(firstnames) ~* lower(%s) and lower(lastnames) ~* lower(%s)",
					'args': [_('names: first last'), '^' + name_parts[0][0], '^' + name_parts[0][1]]
				})
				# but sometimes "last first""
				where_parts.append ({
					'conditions': u"firstnames ~ %s and lastnames ~ %s",
					'args': [_('names: last, first'), '^' + gmTools.capitalize(name_parts[0][1], mode=gmTools.CAPS_NAMES), '^' + gmTools.capitalize(name_parts[0][0], mode=gmTools.CAPS_NAMES)]
				})
				where_parts.append ({
					'conditions': u"lower(firstnames) ~* lower(%s) and lower(lastnames) ~* lower(%s)",
					'args': [_('names: last, first'), '^' + name_parts[0][1], '^' + name_parts[0][0]]
				})
				# or even substrings anywhere in name
				where_parts.append ({
					'conditions': u"lower(firstnames || ' ' || lastnames) ~* lower(%s) OR lower(firstnames || ' ' || lastnames) ~* lower(%s)",
					'args': [_('name'), name_parts[0][0], name_parts[0][1]]
				})

			# special case: "<date(s)>, <name(s)>, <name(s)>, <date(s)>"
			elif len(name_parts) == 2:
				# usually "last, first"
				where_parts.append ({
					'conditions': u"firstnames ~ %s AND lastnames ~ %s",
					'args': [_('name: last, first'), '^' + ' '.join(map(gmTools.capitalize, name_parts[1])), '^' + ' '.join(map(gmTools.capitalize, name_parts[0]))]
				})
				where_parts.append ({
					'conditions': u"lower(firstnames) ~* lower(%s) AND lower(lastnames) ~* lower(%s)",
					'args': [_('name: last, first'), '^' + ' '.join(name_parts[1]), '^' + ' '.join(name_parts[0])]
				})
				# but sometimes "first, last"
				where_parts.append ({
					'conditions': u"firstnames ~ %s AND lastnames ~ %s",
					'args': [_('name: last, first'), '^' + ' '.join(map(gmTools.capitalize, name_parts[0])), '^' + ' '.join(map(gmTools.capitalize, name_parts[1]))]
				})
				where_parts.append ({
					'conditions': u"lower(firstnames) ~* lower(%s) AND lower(lastnames) ~* lower(%s)",
					'args': [_('name: last, first'), '^' + ' '.join(name_parts[0]), '^' + ' '.join(name_parts[1])]
				})
				# and sometimes "last, nick"
				where_parts.append ({
					'conditions': u"preferred ~ %s AND lastnames ~ %s",
					'args': [_('name: last, first'), '^' + ' '.join(map(gmTools.capitalize, name_parts[1])), '^' + ' '.join(map(gmTools.capitalize, name_parts[0]))]
				})
				where_parts.append ({
					'conditions': u"lower(preferred) ~* lower(%s) AND lower(lastnames) ~* lower(%s)",
					'args': [_('name: last, first'), '^' + ' '.join(name_parts[1]), '^' + ' '.join(name_parts[0])]
				})

				# or even substrings anywhere in name
				where_parts.append ({
					'conditions': u"lower(firstnames || ' ' || lastnames) ~* lower(%s) AND lower(firstnames || ' ' || lastnames) ~* lower(%s)",
					'args': [_('name'), ' '.join(name_parts[0]), ' '.join(name_parts[1])]
				})

			# big trouble - arbitrary number of names
			else:
				# FIXME: deep magic, not sure of rationale ...
				if len(name_parts) == 1:
					for part in name_parts[0]:
						where_parts.append ({
							'conditions': u"lower(firstnames || ' ' || lastnames) ~* lower(%s)",
							'args': [_('name'), part]
						})
				else:
					tmp = []
					for part in name_parts:
						tmp.append(' '.join(part))
					for part in tmp:
						where_parts.append ({
							'conditions': u"lower(firstnames || ' ' || lastnames) ~* lower(%s)",
							'args': [_('name'), part]
						})

			# secondly handle date parts
			# FIXME: this needs a considerable smart-up !
			if len(date_parts) == 1:
				if len(where_parts) == 0:
					where_parts.append ({
						'conditions': u"dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone)",
						'args': [_('date of birth'), date_parts[0].replace(u',', u'.')]
					})
				if len(where_parts) > 0:
					where_parts[0]['conditions'] += u" AND dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone)"
					where_parts[0]['args'].append(date_parts[0].replace(u',', u'.'))
					where_parts[0]['args'][0] += u', ' + _('date of birth')
				if len(where_parts) > 1:
					where_parts[1]['conditions'] += u" AND dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone)"
					where_parts[1]['args'].append(date_parts[0].replace(u',', u'.'))
					where_parts[1]['args'][0] += u', ' + _('date of birth')
			elif len(date_parts) > 1:
				if len(where_parts) == 0:
					where_parts.append ({
						'conditions': u"dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone) AND dem.date_trunc_utc('day'::text, dem.identity.deceased) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone)",
						'args': [_('date of birth/death'), date_parts[0].replace(u',', u'.'), date_parts[1].replace(u',', u'.')]
					})
				if len(where_parts) > 0:
					where_parts[0]['conditions'] += u" AND dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone) AND dem.date_trunc_utc('day'::text, dem.identity.deceased) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone)",
					where_parts[0]['args'].append(date_parts[0].replace(u',', u'.'), date_parts[1].replace(u',', u'.'))
					where_parts[0]['args'][0] += u', ' + _('date of birth/death')
				if len(where_parts) > 1:
					where_parts[1]['conditions'] += u" AND dem.date_trunc_utc('day'::text, dob) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone) AND dem.date_trunc_utc('day'::text, dem.identity.deceased) = dem.date_trunc_utc('day'::text, %s::timestamp with time zone)",
					where_parts[1]['args'].append(date_parts[0].replace(u',', u'.'), date_parts[1].replace(u',', u'.'))
					where_parts[1]['args'][0] += u', ' + _('date of birth/death')

			# and finally generate the queries ...
			for where_part in where_parts:
				queries.append ({
					'cmd': u"SELECT *, %%s::text AS match_type FROM dem.v_active_persons WHERE %s" % where_part['conditions'],
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
			where_clause += u" AND lower(coalesce(d_vap.title, '') || ' ' || d_vap.firstnames || ' ' || d_vap.lastnames) ~* lower(%s)"
			args.append(arg)

		query = u"""
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

		return ({'cmd': query, 'args': args})
#============================================================
def ask_for_patient():
	"""Text mode UI function to ask for patient."""

	person_searcher = cPatientSearcher_SQL()

	while True:
		search_fragment = gmTools.prompted_input(prompt = "\nEnter person search term or leave blank to exit")

		if search_fragment in ['exit', 'quit', 'bye', None]:
			print "user cancelled patient search"
			return None

		pats = person_searcher.get_patients(search_term = search_fragment)

		if (pats is None) or (len(pats) == 0):
			print "No patient matches the query term."
			print ""
			continue

		if len(pats) > 1:
			print "Several patients match the query term:"
			print ""
			for pat in pats:
				print pat
				print ""
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

	import datetime

	gmI18N.activate_locale()
	gmI18N.install_domain()
	gmDateTime.init()

	#--------------------------------------------------------
	def test_search_by_dto():
		dto = gmPerson.cDTO_person()
		dto.firstnames = 'Sigrid'
		dto.lastnames = 'Kiesewetter'
		dto.gender = 'female'
#		dto.dob = pyDT.datetime.now(tz=gmDateTime.gmCurrentLocalTimezone)
		dto.dob = datetime.datetime(1939,6,24,23,0,0,0,gmDateTime.gmCurrentLocalTimezone)
		print dto

		searcher = cPatientSearcher_SQL()
		pats = searcher.get_patients(dto = dto)
		print pats
	#--------------------------------------------------------
	def test_patient_search_queries():
		searcher = cPatientSearcher_SQL()

		print "testing _normalize_soundalikes()"
		print "--------------------------------"
		# FIXME: support Ähler -> Äler and Dähler -> Däler
		data = [u'Krüger', u'Krueger', u'Kruger', u'Überle', u'Böger', u'Boger', u'Öder', u'Ähler', u'Däler', u'Großer', u'müller', u'Özdemir', u'özdemir']
		for name in data:
			print '%s: %s' % (name, searcher._normalize_soundalikes(name))

		raw_input('press [ENTER] to continue')
		print "============"

		print "testing _generate_simple_query()"
		print "----------------------------"
		data = ['51234', '1 134 153', '#13 41 34', '#3-AFY322.4', '22-04-1906', '1235/32/3525', ' , johnny']
		for fragment in data:
			print "fragment:", fragment
			qs = searcher._generate_simple_query(fragment)
			for q in qs:
				print " match on:", q['args'][0]
				print " query   :", q['cmd']
			raw_input('press [ENTER] to continue')
			print "============"

		print "testing _generate_queries_from_dto()"
		print "------------------------------------"
		dto = cDTO_person()
		dto.gender = 'm'
		dto.lastnames = 'Kirk'
		dto.firstnames = 'James'
		dto.dob = pyDT.datetime.now(tz=gmDateTime.gmCurrentLocalTimezone)
		q = searcher._generate_queries_from_dto(dto)[0]
		print "dto:", dto
		print " match on:", q['args'][0]
		print " query:", q['cmd']

		raw_input('press [ENTER] to continue')
		print "============"

		print "testing _generate_queries_de()"
		print "------------------------------"
		qs = searcher._generate_queries_de('Kirk, James')
		for q in qs:
			print " match on:", q['args'][0]
			print " query   :", q['cmd']
			print " args    :", q['args']
		raw_input('press [ENTER] to continue')
		print "============"

		qs = searcher._generate_queries_de(u'müller')
		for q in qs:
			print " match on:", q['args'][0]
			print " query   :", q['cmd']
			print " args    :", q['args']
		raw_input('press [ENTER] to continue')
		print "============"

		qs = searcher._generate_queries_de(u'özdemir')
		for q in qs:
			print " match on:", q['args'][0]
			print " query   :", q['cmd']
			print " args    :", q['args']
		raw_input('press [ENTER] to continue')
		print "============"

		qs = searcher._generate_queries_de(u'Özdemir')
		for q in qs:
			print " match on:", q['args'][0]
			print " query   :", q['cmd']
			print " args    :", q['args']
		raw_input('press [ENTER] to continue')
		print "============"

		print "testing _generate_dumb_brute_query()"
		print "------------------------------------"
		q = searcher._generate_dumb_brute_query('Kirk, James Tiberius')
		print " match on:", q['args'][0]
		print " query:", q['cmd']
		print " args:", q['args']

		raw_input('press [ENTER] to continue')
	#--------------------------------------------------------
	def test_ask_for_patient():
		while 1:
			myPatient = ask_for_patient()
			if myPatient is None:
				break
			print "ID       ", myPatient.ID
			print "names     ", myPatient.get_names()
			print "addresses:", myPatient.get_addresses(address_type='home')
			print "recent birthday:", myPatient.dob_in_range()
			myPatient.export_as_gdt(filename='apw.gdt', encoding = 'cp850')
#		docs = myPatient.get_document_folder()
#		print "docs     ", docs
#		emr = myPatient.get_emr()
#		print "EMR      ", emr
	#--------------------------------------------------------
	#test_patient_search_queries()
	#test_ask_for_patient()
	test_search_by_dto()

#============================================================
