# -*- coding: utf-8 -*-
"""GNUmed allergy related business objects."""
#============================================================
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>"
__license__ = "GPL v2 or later"

import sys
import logging
import datetime as pyDT


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmDateTime
from Gnumed.pycommon import gmTools


_log = logging.getLogger('gm.allergy')

# the allergy state *has* been obtained but remained unknown (this is forensically useful)
ALLERGY_STATE_UNKNOWN = None
# no known allergies
ALLERGY_STATE_NONE = 0
# does have allergies
ALLERGY_STATE_SOME = 1

ALLERGY_STATES = [
	ALLERGY_STATE_UNKNOWN,
	ALLERGY_STATE_NONE,
	ALLERGY_STATE_SOME
]

ALLERGY_STATE_SYMBOLS = {
	ALLERGY_STATE_UNKNOWN: '?',
	ALLERGY_STATE_NONE: gmTools.u_diameter,
	ALLERGY_STATE_SOME: '!'
}

#============================================================
# allergy state related code
#------------------------------------------------------------
class cAllergyState(gmBusinessDBObject.cBusinessDBObject):
	"""Represents the allergy state of one patient.

	See ALLERGY_STATES for the meaning of cAllergyState['has_allergy'].
	"""
	_cmd_fetch_payload = "select * from clin.v_pat_allergy_state where pk_allergy_state = %s"
	_cmds_store_payload = [
		"""update clin.allergy_state set
				last_confirmed = %(last_confirmed)s,
				has_allergy = %(has_allergy)s,
				comment = gm.nullify_empty_string(%(comment)s)
			where
				pk = %(pk_allergy_state)s and
				xmin = %(xmin_allergy_state)s
			RETURNING
				xmin AS xmin_allergy_state"""
		#,"""select xmin_allergy_state from clin.v_pat_allergy_state where pk_allergy_state = %(pk_allergy_state)s"""
	]
	_updatable_fields = [
		'last_confirmed',		# special value 'now' will set to datetime.datetime.now() in the local time zone
		'has_allergy',			# verified against ALLERGY_STATES (see above)
		'comment'				# '' maps to None / NULL
	]

	#--------------------------------------------------------
	def format_maximum_information(self, patient=None):
		lines = []
		lines.append('%s (%s)' % (
			self.state_string,
			gmDateTime.pydt_strftime(self['last_confirmed'], '%Y %b %d', none_str = '?')
		))
		if self._payload['comment']:
			lines.append(' %s' % self._payload['comment'])
		return lines

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_as_string(self):
		if self._payload['has_allergy'] is ALLERGY_STATE_UNKNOWN:
			return _('unknown allergy state')
		if self._payload['has_allergy'] == ALLERGY_STATE_NONE:
			return _('no known allergies')
		if self._payload['has_allergy'] == ALLERGY_STATE_SOME:
			return _('*does* have allergies')
		_log.error('unknown allergy state [%s]', self._payload['has_allergy'])
		return _('ERROR: unknown allergy state [%s]') % self._payload['has_allergy']

	state_string = property(_get_as_string)

	#--------------------------------------------------------
	def _get_as_symbol(self):
		try:
			symbol = ALLERGY_STATE_SYMBOLS[self._payload['has_allergy']]
		except KeyError:
			_log.error('unknown allergy state [%s]', self._payload['has_allergy'])
			symbol = _('ERROR: unknown allergy state [%s]') % self._payload['has_allergy']
		if self._payload['comment']:
			symbol += gmTools.u_superscript_one
		return symbol

	state_symbol = property(_get_as_symbol)

	#--------------------------------------------------------
	def _get_as_amts_latex(self, strict=True):
		table_rows = []
		# Trennzeile als leere Zeile für bessere Lesbarkeit
		table_rows.append('\\multicolumn{11}{l}{}\\tabularnewline')
		# Zwischenüberschrift: 31 Zeichen, $..., 14pt, no frame, \textwidth
		state = '%s (%s)' % (
			self.state_string,
			gmDateTime.pydt_strftime(self['last_confirmed'], '%b %Y', none_str = '?')
		)
		if strict:
			state = state[:31]
		table_rows.append('\\multicolumn{11}{>{\\RaggedRight}p{27.9cm}}{\\rule{0pt}{4.5mm} \\fontsize{14pt}{16pt}\selectfont %s\label{AnchorAllergieDetails}}\\tabularnewline' % gmTools.tex_escape_string(state))
		# Freitextzeile: 200 Zeichen, @..., \textwidth
		if self['comment'] is not None:
			if strict:
				cmt = self['comment'].strip()[:200]
			else:
				cmt = self['comment'].strip()
			table_rows.append('\\multicolumn{11}{>{\\RaggedRight}p{27.9cm}}{%s}\\tabularnewline') % gmTools.tex_escape_string(cmt)
		return table_rows

	as_amts_latex = property(_get_as_amts_latex)

	#--------------------------------------------------------
	def _get_as_amts_data_v_2_0(self, strict=True):
		lines = []
		# Trennzeile für bessere Lesbarkeit als leere Zwischenüberschrift
		lines.append('$ ')
		# Zwischenüberschrift: 31 Zeichen, $..., \textwidth
		txt = '$%s (%s)' % (
			self.state_string,
			gmDateTime.pydt_strftime(self['last_confirmed'], '%b %Y', none_str = '?')
		)
		if strict:
			lines.append(txt[:32])
		else:
			lines.append(txt)
		# Freitextzeile: 200 Zeichen, @..., \textwidth
		if self['comment']:
			if strict:
				lines.append('@%s' % self['comment'][:200])
			else:
				lines.append('@%s' % self['comment'])
		return lines

	#--------------------------------------------------------
	def _get_as_amts_data(self, strict=True):
		# Zwischenüberschrift
		state = '%s (%s)' % (self.state_string, gmDateTime.pydt_strftime(self['last_confirmed'], '%b %Y', none_str = '?'))
		if strict:
			state = state[:32]
		# Freitextzeile
		if self['comment'] is None:
			comment = ''
		else:
			comment = '<X t="%s"/>' % self['comment']
			if strict:
				comment = '<X t="%s"/>' % self['comment'][:200]
		return '<S t="%s">%s%%s</S>' % (state, comment)

	as_amts_data = property(_get_as_amts_data)

	#--------------------------------------------------------
	def __setitem__(self, attribute, value):
		if attribute == 'last_confirmed':
			if value == 'now':
				value = pyDT.datetime.now(tz = gmDateTime.gmCurrentLocalTimezone)
			return

		if attribute == 'has_allergy':
			if value not in ALLERGY_STATES:
				raise ValueError('invalid allergy state [%s]' % value)
		super().__setitem__(attribute, value)

#------------------------------------------------------------
def get_allergy_state(pk_encounter:int=None, pk_patient:int=None) -> cAllergyState:
	"""Get allergy state for patient by patient XOR encounter.

	Args:
		pk_encounter: any encounter (primary key) of the patient
		pk_patient: the patient primary key

	Returns:
		cAllergyState or None. If None is returned, the allergy state
		has yet to be obtained.

	Return of None means the state has not yet been
	(documented to have been) determined.

	This is forensically vastly different from

		cAllergyState['has_allergy'] == None

	meaning that the allergy state has been asked
	for but no data was available.
	"""
	assert not((pk_encounter is None) and (pk_patient is None)), 'one of <pk_encounter> or <pk_patient> must be given'

	args = {'pk_enc': pk_encounter, 'pk_pat': pk_patient}
	if pk_encounter:
		SQL = """
			SELECT pk_allergy_state FROM clin.v_pat_allergy_state
			WHERE pk_patient = (
				SELECT fk_patient FROM clin.encounter WHERE pk = %(pk_enc)s
			)
		"""
	else:
		SQL = 'SELECT pk_allergy_state FROM clin.v_pat_allergy_state WHERE pk_patient = %(pk_pat)s'
	rows = gmPG2.run_rw_queries(queries = [{'sql': SQL, 'args': args}], return_data = True)
	if not rows:
		return None

	return cAllergyState(aPK_obj = rows[0][0])

#------------------------------------------------------------
def ensure_has_allergy_state(encounter=None) -> cAllergyState:
	_log.debug('checking allergy state for identity of encounter [%s]', encounter)
	args = {'enc': encounter}
	SQL_create = """
		INSERT INTO clin.allergy_state (
			fk_encounter,
			has_allergy
		)	SELECT
				%(enc)s,
				NULL
			WHERE NOT EXISTS (
				SELECT 1 FROM clin.v_pat_allergy_state
				WHERE pk_patient = (
					SELECT fk_patient FROM clin.encounter WHERE pk = %(enc)s
				)
			)
	"""
	SQL_search = """
		SELECT pk_allergy_state FROM clin.v_pat_allergy_state
		WHERE pk_patient = (
			SELECT fk_patient FROM clin.encounter WHERE pk = %(enc)s
		)
	"""
	rows = gmPG2.run_rw_queries (
		queries = [
			{'sql': SQL_create, 'args': args},
			{'sql': SQL_search, 'args': args}
		],
		return_data = True
	)
	return cAllergyState(aPK_obj = rows[0][0])

#============================================================
class cAllergy(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one allergy item.

	Actually, those things are really things to "avoid".
	Allergy is just one of several reasons for that.
	See Adrian's post on gm-dev.

	Another word might be Therapeutic Precautions.
	"""
	_cmd_fetch_payload = "SELECT * FROM clin.v_pat_allergies WHERE pk_allergy = %s"
	_cmds_store_payload = [
		"""UPDATE clin.allergy SET
				clin_when = %(date)s,
				substance = %(substance)s,
				substance_code = %(substance_code)s,
				generics = %(generics)s,
				allergene = %(allergene)s,
				atc_code = %(atc_code)s,
				fk_type = %(pk_type)s,
				generic_specific = %(generic_specific)s::boolean,
				definite = %(definite)s::boolean,
				narrative = %(reaction)s
			WHERE
				pk = %(pk_allergy)s AND
				xmin = %(xmin_allergy)s""",
		"""SELECT xmin_allergy FROM clin.v_pat_allergies WHERE pk_allergy=%(pk_allergy)s"""
	]
	_updatable_fields = [
		'date',
		'substance',
		'substance_code',
		'generics',
		'allergene',
		'atc_code',
		'pk_type',
		'generic_specific',
		'definite',
		'reaction'
	]
	#--------------------------------------------------------
	def format_maximum_information(self, patient=None):
		lines = []
		lines.append('%s%s: %s     [#%s]' % (
			self._payload['l10n_type'],
			gmTools.bool2subst (
				self._payload['definite'],
				' (%s)' % _('definite'),
				' (%s)' % _('indefinite'),
				''
			),
			self._payload['descriptor'],
			self._payload['pk_allergy']
		))
		if self._payload['reaction'] is not None:
			lines.append(' ' + _('Reaction:') + ' ' + self._payload['reaction'])
		if self._payload['date']:
			lines.append(' ' + _('Noted:') + ' ' + self._payload['date'].strftime('%Y %b %d'))
		if self._payload['allergene'] is not None:
			lines.append(' ' + _('Allergene:') + ' ' + self._payload['allergene'])
		if self._payload['substance'] is not None:
			lines.append(' ' + _('Substance:') + ' ' + self._payload['substance'])
		if self._payload['substance_code'] is not None:
			lines.append(' ' + _('Code:') + ' ' + self._payload['substance_code'])
		if self._payload['atc_code'] is not None:
			lines.append(' ' + _('ATC:') + ' ' + self._payload['atc_code'])
		lines.append(' ' + _('Specific to:') + ' ' + gmTools.bool2subst (
			self._payload['generic_specific'],
			_('this substance only'),
			_('drug class'),
			_('unknown')
		))
		if self._payload['generics']:
			lines.append(' ' + _('Generics:') + ' ' + self._payload['generics'])
		return lines

	#--------------------------------------------------------
	def format_for_failsafe_output(self, max_width:int=80) -> list[str]:
		lines = [
			'%s%s: %s' % (
				self._payload['l10n_type'],
				gmTools.bool2subst (
					self._payload['definite'],
					' (%s)' % _('definite'),
					' (%s)' % _('indefinite'),
					''
				),
				self._payload['descriptor']
			)
		]
		if self._payload['reaction']:
			lines.append(gmTools.shorten_text('  ' + self._payload['reaction'], max_width))
		return lines

	#--------------------------------------------------------
	def __setitem__(self, attribute, value):
		if attribute == 'pk_type':
			if value in ['allergy', 'sensitivity']:
				cmd = 'select pk from clin._enum_allergy_type where value = %(allg_type)s'
				rows = gmPG2.run_ro_queries(queries = [{'sql': cmd, 'args': {'allg_type': value}}])
				value = rows[0][0]
		gmBusinessDBObject.cBusinessDBObject.__setitem__(self, attribute, value)

	#--------------------------------------------------------
	def _get_as_amts_latex(self, strict=True):
		# Freitextzeile: 200 Zeichen, @...
		cells = ['\\multicolumn{1}{>{\\RaggedRight}p{4cm}}{%s}' % gmTools.tex_escape_string(self['descriptor'])]
		txt = '%s%s' % (
			self['l10n_type'],
			gmTools.coalesce(self['reaction'], '', ': %s')
		)
		if strict:
			txt = txt[:(200-len(self['descriptor']))]
		cells.append('\\multicolumn{10}{>{\\RaggedRight}p{23.9cm}}{%s}' % gmTools.tex_escape_string(txt))
		table_row = ' & '.join(cells)
		table_row += '\\tabularnewline'
		return table_row

	as_amts_latex = property(_get_as_amts_latex)

	#--------------------------------------------------------
	def _get_as_amts_data_v_2_0(self, strict=True):
		# Freitextzeile: 200 Zeichen, @..., \textwidth
		txt = '@%s %s%s' % (
			self['descriptor'],
			self['l10n_type'],
			gmTools.coalesce(self['reaction'], '', ': %s')
		)
		if strict:
			return txt[:200]
		return txt

	#--------------------------------------------------------
	def _get_as_amts_data(self, strict=True):
		txt = '%s %s%s' % (
			self['descriptor'],
			self['l10n_type'],
			gmTools.coalesce(self['reaction'], '', ': %s')
		)
		if strict:
			txt = txt[:200]
		# Freitextzeile: 200 Zeichen
		return '<X t="%s"/>' % txt

	as_amts_data = property(_get_as_amts_data)

#============================================================
# convenience functions
#------------------------------------------------------------
def create_allergy(allergene:str=None, allg_type=None, episode_id:int=None, encounter_id:int=None) -> cAllergy:
	"""Creates a new allergy clinical item.

	Args:
		allergene: allergic substance
		allg_type: allergy or sensitivity, pk or string
		encounter_id - encounter
		episode_id - episode

	Returns:
		The newly created allergy.
	"""
	SQL = """
		SELECT pk_allergy
		FROM clin.v_pat_allergies
		WHERE
			pk_patient = (SELECT fk_patient FROM clin.encounter WHERE pk = %(enc)s)
				AND
			allergene = %(allergene)s
	"""
	args = {'enc': encounter_id, 'allergene': allergene}
	rows = gmPG2.run_ro_queries(queries = [{'sql': SQL, 'args': args}])
	if rows:
		# don't implicitely change existing data, return existing allergy
		return cAllergy(aPK_obj = rows[0][0])

	# insert new allergy
	queries = []
	if isinstance(allg_type, int):
		SQL = """
			INSERT INTO clin.allergy (fk_type, fk_encounter, fk_episode, allergene, substance)
			VALUES (%(allg_type)s, %(enc)s, %(epi)s, %(allergene)s, %(subst)s)"""
	else:
		SQL = """
			insert into clin.allergy (fk_type, fk_encounter, fk_episode,  allergene, substance)
			VALUES (
				(select pk from clin._enum_allergy_type where value = %(allg_type)s),
				%(enc)s,
				%(epi)s,
				%(allergene)s,
				%(subst)s
			)"""
	args = {
		'allg_type': allg_type,
		'enc': encounter_id,
		'epi': episode_id,
		'allergene': allergene,
		'subst': allergene
	}
	queries.append({'sql': SQL, 'args': args})
	SQL = "select currval('clin.allergy_id_seq')"
	queries.append({'sql': SQL})
	rows = gmPG2.run_rw_queries(queries = queries, return_data = True)
	allergy = cAllergy(aPK_obj = rows[0][0])
	return allergy

#============================================================
# main - unit testing
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	#--------------------------------------------------------
	def test_state():
		for idx in range(15):
			print('pat:', idx, '->', get_allergy_state(pk_patient = idx))

		for idx in range(15):
			print('enc:', idx, '->', get_allergy_state(pk_encounter = idx))

	#--------------------------------------------------------
	def test():
		allg = cAllergy(aPK_obj=1)
		print(allg)
		print('\n'.join(allg.format_for_failsafe_output()))
		return

		fields = allg.get_fields()
		for field in fields:
			print(field, ':', allg[field])
		print("updatable:", allg.get_updatable_fields())
		enc_id = allg['pk_encounter']
		epi_id = allg['pk_episode']
		allg = create_allergy (
			allergene = 'test substance',
			allg_type = 1,
			episode_id = epi_id,
			encounter_id = enc_id
		)
		print(allg)
		allg['reaction'] = 'hehehe'
		status, data = allg.save_payload()
		print('status:', status)
		print('data:', data)
		print(allg)

	#--------------------------------------------------------
	gmPG2.request_login_params(setup_pool = True)

	#test_state()
	test()
