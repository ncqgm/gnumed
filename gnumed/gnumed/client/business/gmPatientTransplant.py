"""GNUmed patient transplant.

Export all data belonging to one patient as a self-contained
SQL script. Running that script against another GNUmed database
of the same schema version puts the patient into that database
("transplant").

If the patient seems to already exist in the target database
the script aborts (rolling back everything) and reports the
candidate identities such that the user can decide whether to
create a new patient or to add the data to an existing one.

Properties of the generated script:

- plain SQL, runnable by psql as well as by implant_patient()

- one single transaction, nothing is changed unless everything succeeds

- a block near the top can be edited manually: staff matching mode,
  staff mapping, "same patient as #...", patient mode, force, dry run

- all patient data is first loaded into constraint-free
  temporary staging tables, all subsequent statements do not
  contain patient data literals, such that server side error
  logging cannot leak patient data

- primary keys are never transferred: the target allocates new
  ones, the source->target mapping of rows is persisted into
  dem.identity.aux_info->'gm_transplant' such that repeated
  imports (forced or delta) never duplicate rows

- the original audit metadata (.modified_by/.modified_when)
  and, if available, the audit trail of the source are put into
  the target as documents of the patient
"""
#============================================================
__license__ = "GPL v2 or later"
__author__ = "M.Angermann <marc.angermann@gmx.de>"


import sys
import os
import io
import re
import json
import uuid
import base64
import shutil
import hashlib
import logging
import tempfile
import datetime as pydt


if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmTools

from Gnumed.business import gmPraxis

_log = logging.getLogger('gm.transplant')

#============================================================
# constants
#------------------------------------------------------------
SCRIPT_FORMAT_VERSION = 1
SCHEMA_VERSION = 23

MARKER_STMT = '-- @@gm_tp@@'
MARKER_META = '-- @@gm_tp:meta@@'
MARKER_DATA_BEGIN = '-- @@gm_tp:data-begin@@'
MARKER_SHA256 = '-- @@gm_tp:sha256@@'
MARKER_CFG_BEGIN = '-- ================= CONFIGURATION'
MARKER_CFG_END = '-- ================= END OF CONFIGURATION'

SQLSTATE_DRY_RUN_OK = 'GMTP0_DRY_RUN_OK'
SQLSTATE_CANDIDATES = 'GMTP1_PATIENT_CANDIDATES_EXIST'
SQLSTATE_ALREADY_IMPORTED = 'GMTP2_ALREADY_IMPORTED'
SQLSTATE_SCHEMA_MISMATCH = 'GMTP3_SCHEMA_MISMATCH'
SQLSTATE_INVALID_CONFIG = 'GMTP4_INVALID_CONFIG'
SQLSTATE_STAFF = 'GMTP5_STAFF_ISSUE'
SQLSTATE_MISSING_REFERENCE = 'GMTP6_MISSING_REFERENCE_DATA'
SQLSTATE_VERIFICATION = 'GMTP9_VERIFICATION_ISSUE'

PROVENANCE_EXT_ID_TYPE = 'GNUmed transplant source'
PROVENANCE_EXT_ID_ISSUER = 'GNUmed'
DOC_TYPE_PROTOCOL = 'GNUmed transplant protocol'
DOC_TYPE_PROTOCOL_DE = 'GNUmed-Transplantationsprotokoll'
DOC_TYPE_HISTORY = 'GNUmed audit history'
DOC_TYPE_HISTORY_DE = 'GNUmed-Änderungshistorie'

_BLOB_CHUNK_SIZE = 512 * 1024				# raw bytes per chunk statement
_MAX_STAGING_STMT_SIZE = 1024 * 1024		# characters per staging INSERT
_AUDIT_COLS = ('pk_audit', 'row_version', 'modified_when', 'modified_by')
_NEVER_COPY_COLS = set(_AUDIT_COLS) | {'pk_item', 'pk_lnk_code2item'}
# columns of audit log tables which are not copies of the audited table
_AUDIT_LOG_META_COLS = {
	'pk_audit', 'row_version', 'version_created_when', 'version_created_by',
	'version_logged_when', 'version_logged_by', 'version_logged_why',
	'src_row_pk_audit', 'src_table_oid',
	'orig_version', 'orig_when', 'orig_by', 'orig_tableoid',
	'audit_action', 'audit_when', 'audit_by'
}

#============================================================
# exceptions and results
#------------------------------------------------------------
class cTransplantError(Exception):
	"""Raised when a patient cannot be exported or imported.

	Messages never contain patient data.
	"""
	pass

#------------------------------------------------------------
class cTransplantResult:
	"""Outcome of running a transplant script.

	status:
		'imported': patient data has been committed into the target database
		'dry_run_ok': script ran successfully but was rolled back as requested
		'candidates': the patient seems to exist already, see .candidates
		'already_imported': this very export has been imported before, see .identities
		'error': something went wrong, see .sqlstate/.message
	"""
	def __init__(self, status:str, message:str=None, sqlstate:str=None, summary:dict=None, candidates:list=None, identities:list=None, statement:str=None):
		self.status = status
		self.message = message
		self.sqlstate = sqlstate
		self.summary = summary or {}
		self.candidates = candidates or []
		self.identities = identities or []
		self.statement = statement

	#--------------------------------------------------------
	def _get_pk_identity(self) -> int:
		return self.summary.get('target_identity')

	pk_identity = property(_get_pk_identity)

	#--------------------------------------------------------
	def _get_staff_mapping(self) -> list:
		return self.summary.get('staff', [])

	staff_mapping = property(_get_staff_mapping)

	#--------------------------------------------------------
	def _get_counts(self) -> dict:
		return self.summary.get('counts', {})

	counts = property(_get_counts)

	#--------------------------------------------------------
	def _get_skipped(self) -> list:
		return self.summary.get('skipped', [])

	skipped = property(_get_skipped)

	#--------------------------------------------------------
	def __str__(self) -> str:
		return '<cTransplantResult: status=%s sqlstate=%s target=%s>' % (self.status, self.sqlstate, self.pk_identity)

	#--------------------------------------------------------
	def format(self, eol:str='\n') -> str:
		"""Human readable summary (no patient data beyond primary keys)."""
		lines = []
		summary = self.summary
		if summary.get('patient_mode'):
			lines.append(_('Patient mode: %s') % summary['patient_mode'])
		if summary.get('target_identity'):
			lines.append(_('Target patient: #%s') % summary['target_identity'])
		if summary.get('staff'):
			lines.append(_('Staff mapping:'))
			for staff in summary['staff']:
				lines.append('  %s (%s) -> %s [%s]' % (
					staff.get('src_alias'),
					staff.get('src_db_user'),
					staff.get('target_alias'),
					_STAFF_HOW_LABELS.get(staff.get('how'), staff.get('how'))
				))
		counts = summary.get('counts', {})
		if counts:
			lines.append(_('Rows:'))
			for tbl in sorted(counts):
				if tbl == 'staff' or tbl.startswith('ref:'):
					continue
				by_status = ', '.join([ '%s: %s' % (status, counts[tbl][status]) for status in sorted(counts[tbl]) ])
				lines.append('  %s: %s' % (tbl, by_status))
			refs = [ tbl for tbl in counts if tbl.startswith('ref:') ]
			if refs:
				lines.append(_('Reference data:'))
				for tbl in sorted(refs):
					by_status = ', '.join([ '%s: %s' % (status, counts[tbl][status]) for status in sorted(counts[tbl]) ])
					lines.append('  %s: %s' % (tbl[4:], by_status))
		if summary.get('skipped'):
			lines.append(_('Skipped rows: %s (see transplant protocol)') % len(summary['skipped']))
		return eol.join(lines)

#------------------------------------------------------------
_STAFF_HOW_LABELS = {
	'explicit': 'explicit mapping',
	'alias': 'by alias',
	'db_user': 'by database account',
	'fallback': 'fallback'
}

#============================================================
# what to export, and how to load it
#------------------------------------------------------------
# foreign key column kinds:
#  ('int', 'schema.table')   patient-internal FK, mapped to the new primary key, parent must be available
#  ('soft', 'schema.table')  patient-internal FK, mapped if possible, else NULL
#  ('defer', 'schema.table') patient-internal FK, set during fix-up after all rows are loaded
#  ('staff',)                dem.staff, resolved by staff matching
#  ('ref', 'schema.table')   reference data, looked up by natural key or created
#  ('code',)                 soft FK to ref.coding_system_root.pk_coding_system, looked up or created
#  ('keep', 'schema.table')  natural key value copied verbatim, referenced row ensured to exist
#  ('null',)                 not transferred
#------------------------------------------------------------
class _cTableSpec:
	"""How to export and load one table of patient data."""

	def __init__(self, table:str, where:str, pk:str='pk', fks:dict=None, extra:dict=None, overrides:dict=None,
		match:str=None, dedupe:list=None, skip_if:str=None, skip_reason:str=None, skip_cols:set=None,
		lenient:bool=False, section:int=2, custom_insert:bool=False, pre_insert:list=None, export_filter:str=None,
		post_insert:list=None
	):
		self.table = table
		self.schema, self.name = table.split('.')
		self.where = where
		self.pk = pk
		self.fks = fks or {}
		# extra: {name: (sql type, export expression over alias "t", collect kind or None)}
		self.extra = extra or {}
		self.overrides = overrides or {}
		self.match = match
		self.dedupe = dedupe
		self.skip_if = skip_if
		self.skip_reason = skip_reason
		self.skip_cols = skip_cols or set()
		self.lenient = lenient
		self.section = section
		self.custom_insert = custom_insert
		self.pre_insert = pre_insert or []
		self.post_insert = post_insert or []
		self.export_filter = export_filter
		# filled in from the source database during export
		self.cols = []
		self.col_types = {}
		self.bytea_cols = []
		self.has_audit = False
		self.pk_is_identity = False
		self.sequence = None

	#--------------------------------------------------------
	def _get_staging(self) -> str:
		return 'pg_temp._s_%s__%s' % (self.schema, self.name)

	staging = property(_get_staging)

	#--------------------------------------------------------
	def _get_staged_cols(self) -> list:
		return [ c for c in self.cols if c not in _NEVER_COPY_COLS and c != self.pk and c not in self.skip_cols and self.fks.get(c, ('copy',))[0] != 'null' ]

	staged_cols = property(_get_staged_cols)

	#--------------------------------------------------------
	def _get_insert_cols(self) -> list:
		cols = [ c for c in self.staged_cols if self.fks.get(c, ('copy',))[0] != 'defer' ]
		# columns not transferred as such but computed from other data
		cols.extend([ c for c in self.cols if self.fks.get(c, ('copy',))[0] == 'null' and c in self.overrides ])
		return cols

	insert_cols = property(_get_insert_cols)

#------------------------------------------------------------
_ENC = '{clin.encounter}'
_EPI_FKS = {'fk_encounter': ('int', 'clin.encounter'), 'fk_episode': ('int', 'clin.episode')}

def _mapped(tbl:str, col:str) -> str:
	return "pg_temp._tp_mo('%s', s.%s)" % (tbl, col)

def _staff_review_spec(table:str, reviewed_table:str, one_per_row:bool) -> _cTableSpec:
	if one_per_row:
		match = "(SELECT r.pk FROM %s r WHERE r.fk_reviewed_row = %s ORDER BY r.pk LIMIT 1)" % (table, _mapped(reviewed_table, 'fk_reviewed_row'))
		dedupe = ['s.fk_reviewed_row']
	else:
		match = "(SELECT r.pk FROM %s r WHERE r.fk_reviewed_row = %s AND r.fk_reviewer = pg_temp._tp_s(s.fk_reviewer) ORDER BY r.pk LIMIT 1)" % (table, _mapped(reviewed_table, 'fk_reviewed_row'))
		dedupe = ['s.fk_reviewed_row', 'pg_temp._tp_s(s.fk_reviewer)']
	return _cTableSpec(table,
		where = 'fk_reviewed_row = ANY({%s})' % reviewed_table,
		fks = {'fk_reviewed_row': ('int', reviewed_table), 'fk_reviewer': ('staff',)},
		overrides = {'comment': 'pg_temp._tp_staff_note(s.comment, s.fk_reviewer)'},
		match = match,
		dedupe = dedupe
	)

def _code_link_spec(table:str, item_table:str) -> _cTableSpec:
	return _cTableSpec(table,
		where = 'fk_item = ANY({%s})' % item_table,
		fks = {'fk_item': ('int', item_table), 'fk_generic_code': ('code',)},
		match = "(SELECT l.pk FROM %s l WHERE l.fk_item = %s AND l.fk_generic_code = pg_temp._tp_r('code', s.fk_generic_code) ORDER BY l.pk LIMIT 1)" % (table, _mapped(item_table, 'fk_item')),
		dedupe = ['s.fk_item', "pg_temp._tp_r('code', s.fk_generic_code)"],
		# do not export links to codes which no longer exist (soft FK)
		export_filter = 'EXISTS (SELECT 1 FROM ref.coding_system_root r WHERE r.pk_coding_system = t.fk_generic_code)'
	)

# EMR item tables (children of clin.clin_root_item) which can be typed via clin.lnk_type2item
_ROOT_ITEM_TABLES = [
	'clin.clin_narrative', 'clin.clin_aux_note', 'clin.family_history', 'clin.intake',
	'clin.vaccination', 'clin.hospital_stay', 'clin.lab_request', 'clin.test_result',
	'clin.form_instances', 'clin.allergy', 'clin.procedure'
]

def _type2item_spec() -> _cTableSpec:
	item_pk = 'coalesce(%s)' % ', '.join([ '(SELECT x.pk FROM %s x WHERE x.pk_item = t.fk_item)' % tbl for tbl in _ROOT_ITEM_TABLES ])
	new_item = 'CASE s._x_item_table %s ELSE NULL END' % ' '.join ([
		"WHEN '%s' THEN (SELECT y.pk_item FROM %s y WHERE y.pk = pg_temp._tp_mo('%s', s._x_item_pk))" % (tbl, tbl, tbl)
		for tbl in _ROOT_ITEM_TABLES
	])
	return _cTableSpec('clin.lnk_type2item',
		# soft FK to clin.clin_root_item.pk_item
		where = 'fk_item IN (SELECT r.pk_item FROM clin.clin_root_item r WHERE r.fk_encounter = ANY({clin.encounter}))',
		fks = {'fk_type': ('ref', 'clin.clin_item_type'), 'fk_item': ('null',)},
		extra = {
			'_x_item_table': ('text', '(SELECT n.nspname || \'.\' || c.relname FROM clin.clin_root_item r JOIN pg_class c ON (c.oid = r.tableoid) JOIN pg_namespace n ON (n.oid = c.relnamespace) WHERE r.pk_item = t.fk_item)', None),
			'_x_item_pk': ('integer', item_pk, None)
		},
		overrides = {'fk_item': new_item},
		skip_if = '(%s) IS NULL' % new_item,
		skip_reason = 'typed EMR item not available in target',
		match = "(SELECT l.pk FROM clin.lnk_type2item l WHERE l.fk_type = pg_temp._tp_r('clin.clin_item_type', s.fk_type) AND l.fk_item = (%s) ORDER BY l.pk LIMIT 1)" % new_item,
		dedupe = ["pg_temp._tp_r('clin.clin_item_type', s.fk_type)", new_item]
	)

_SQL_emergency_note = """(
	SELECT concat_ws(', ',
		(SELECT n.lastnames || ', ' || n.firstnames FROM dem.names n WHERE n.id_identity = ec.pk AND n.active LIMIT 1),
		to_char(ec.dob, 'YYYY-MM-DD'),
		(SELECT string_agg(c.url, ', ' ORDER BY c.pk) FROM dem.lnk_identity2comm c WHERE c.fk_identity = ec.pk)
	)
	FROM dem.identity ec WHERE ec.pk = t.fk_emergency_contact
)"""

_TABLE_SPECS = [
	_cTableSpec('dem.identity',
		where = 'pk = %(pat)s',
		section = 1,
		fks = {
			'gender': ('keep', 'dem.gender_label'),
			'fk_marital_status': ('ref', 'dem.marital_status'),
			'fk_primary_provider': ('staff',),
			'fk_emergency_contact': ('null',)
		},
		extra = {'_x_emergency_note': ('text', _SQL_emergency_note, None)},
		overrides = {
			'comment': 'pg_temp._tp_identity_comment(s.comment)',
			'emergency_contact': "nullif(concat_ws(' / ', nullif(s.emergency_contact, ''), s._x_emergency_note), '')",
			'aux_info': "(s.aux_info - 'gm_transplant')"
		},
		match = 'pg_temp._tp_add_target()',
		pre_insert = ['SELECT pg_temp._tp_set_dob_tz((SELECT s.dob FROM pg_temp._s_dem__identity s ORDER BY s._src_pk LIMIT 1));'],
		post_insert = ['SELECT pg_temp._tp_reset_tz();']
	),
	_cTableSpec('dem.names',
		pk = 'id',
		where = 'id_identity = %(pat)s',
		section = 1,
		fks = {'id_identity': ('int', 'dem.identity')},
		match = "(SELECT n.id FROM dem.names n WHERE n.id_identity = pg_temp._tp_mo('dem.identity', s.id_identity) AND lower(n.lastnames) = lower(s.lastnames) AND lower(n.firstnames) = lower(s.firstnames) ORDER BY n.id LIMIT 1)",
		custom_insert = True
	),
	_cTableSpec('dem.lnk_identity2ext_id',
		pk = 'id',
		where = 'id_identity = %(pat)s',
		section = 1,
		fks = {'id_identity': ('int', 'dem.identity'), 'fk_origin': ('ref', 'dem.enum_ext_id_types')},
		extra = {
			'_x_type_name': ('text', '(SELECT e.name FROM dem.enum_ext_id_types e WHERE e.pk = t.fk_origin)', None),
			'_x_type_issuer': ('text', '(SELECT e.issuer FROM dem.enum_ext_id_types e WHERE e.pk = t.fk_origin)', None)
		},
		match = "(SELECT x.id FROM dem.lnk_identity2ext_id x WHERE x.id_identity = pg_temp._tp_mo('dem.identity', s.id_identity) AND x.fk_origin = pg_temp._tp_r('dem.enum_ext_id_types', s.fk_origin) AND x.external_id = s.external_id ORDER BY x.id LIMIT 1)"
	),
	_cTableSpec('dem.lnk_identity2comm',
		where = 'fk_identity = %(pat)s',
		fks = {'fk_identity': ('int', 'dem.identity'), 'fk_type': ('ref', 'dem.enum_comm_types'), 'fk_address': ('ref', 'dem.address')},
		match = "(SELECT c.pk FROM dem.lnk_identity2comm c WHERE c.fk_identity = pg_temp._tp_mo('dem.identity', s.fk_identity) AND c.url = s.url ORDER BY c.pk LIMIT 1)",
		dedupe = ['s.url']
	),
	_cTableSpec('dem.lnk_person_org_address',
		pk = 'id',
		where = 'id_identity = %(pat)s',
		fks = {'id_identity': ('int', 'dem.identity'), 'id_address': ('ref', 'dem.address'), 'id_type': ('ref', 'dem.address_type'), 'id_org': ('null',)},
		match = "(SELECT a.id FROM dem.lnk_person_org_address a WHERE a.id_identity = pg_temp._tp_mo('dem.identity', s.id_identity) AND a.id_address = pg_temp._tp_r('dem.address', s.id_address) ORDER BY a.id LIMIT 1)",
		dedupe = ["pg_temp._tp_r('dem.address', s.id_address)"]
	),
	_cTableSpec('dem.identity_tag',
		where = 'fk_identity = %(pat)s',
		fks = {'fk_identity': ('int', 'dem.identity'), 'fk_tag': ('ref', 'ref.tag_image')},
		match = "(SELECT x.pk FROM dem.identity_tag x WHERE x.fk_identity = pg_temp._tp_mo('dem.identity', s.fk_identity) AND x.fk_tag = pg_temp._tp_r('ref.tag_image', s.fk_tag) ORDER BY x.pk LIMIT 1)",
		dedupe = ["pg_temp._tp_r('ref.tag_image', s.fk_tag)"]
	),
	_cTableSpec('dem.lnk_job2person',
		where = 'fk_identity = %(pat)s',
		fks = {'fk_identity': ('int', 'dem.identity'), 'fk_occupation': ('ref', 'dem.occupation')},
		match = "(SELECT x.pk FROM dem.lnk_job2person x WHERE x.fk_identity = pg_temp._tp_mo('dem.identity', s.fk_identity) AND x.fk_occupation = pg_temp._tp_r('dem.occupation', s.fk_occupation) ORDER BY x.pk LIMIT 1)",
		dedupe = ["pg_temp._tp_r('dem.occupation', s.fk_occupation)"]
	),
	_cTableSpec('clin.patient',
		where = 'fk_identity = %(pat)s',
		fks = {'fk_identity': ('int', 'dem.identity')},
		match = "(SELECT p.pk FROM clin.patient p WHERE p.fk_identity = pg_temp._tp_mo('dem.identity', s.fk_identity))"
	),
	_cTableSpec('clin.encounter',
		where = 'fk_patient = %(pat)s',
		fks = {'fk_patient': ('int', 'dem.identity'), 'fk_type': ('ref', 'clin.encounter_type'), 'fk_location': ('ref', 'dem.org_unit')},
		# set by trigger from the session time zone
		skip_cols = {'source_time_zone'}
	),
	_cTableSpec('clin.health_issue',
		where = 'fk_encounter = ANY(%s)' % _ENC,
		fks = {'fk_encounter': ('int', 'clin.encounter')}
	),
	_cTableSpec('clin.episode',
		where = 'fk_encounter = ANY(%s)' % _ENC,
		fks = {'fk_encounter': ('int', 'clin.encounter'), 'fk_health_issue': ('int', 'clin.health_issue')},
		# only one open episode per health issue
		overrides = {'is_open': "CASE WHEN s.is_open AND s.fk_health_issue IS NOT NULL AND EXISTS (SELECT 1 FROM clin.episode e WHERE e.fk_health_issue = pg_temp._tp_mo('clin.health_issue', s.fk_health_issue) AND e.is_open) THEN false ELSE s.is_open END"},
		pre_insert = ["""UPDATE pg_temp._gm_tp_map m SET note = 'inserted as closed episode: health issue already has an open episode'
FROM pg_temp._s_clin__episode s
WHERE m.tbl = 'clin.episode' AND m.src_pk = s._src_pk AND m.status = 'new'
	AND s.is_open AND s.fk_health_issue IS NOT NULL
	AND EXISTS (SELECT 1 FROM clin.episode e WHERE e.fk_health_issue = pg_temp._tp_mo('clin.health_issue', s.fk_health_issue) AND e.is_open)"""]
	),
	_cTableSpec('clin.allergy_state',
		where = 'fk_encounter = ANY(%s)' % _ENC,
		fks = {'fk_encounter': ('int', 'clin.encounter')},
		# one allergy state per patient
		match = '(SELECT a.pk FROM clin.allergy_state a JOIN clin.encounter e ON (e.pk = a.fk_encounter) WHERE e.fk_patient = pg_temp._tp_target() ORDER BY a.pk LIMIT 1)',
		dedupe = ['true']
	),
	_cTableSpec('clin.clin_narrative',
		where = 'fk_encounter = ANY(%s)' % _ENC,
		fks = _EPI_FKS,
		# unique index on (fk_encounter, fk_episode, soap_cat, modified_by, md5(narrative)),
		# .modified_by will be the importing account for all rows
		match = "(SELECT n.pk FROM clin.clin_narrative n WHERE n.fk_encounter = pg_temp._tp_mo('clin.encounter', s.fk_encounter) AND n.fk_episode = pg_temp._tp_mo('clin.episode', s.fk_episode) AND n.soap_cat IS NOT DISTINCT FROM s.soap_cat AND n.modified_by = SESSION_USER AND md5(n.narrative) = md5(s.narrative) ORDER BY n.pk LIMIT 1)",
		dedupe = ['s.fk_encounter', 's.fk_episode', 's.soap_cat', 'md5(s.narrative)']
	),
	_cTableSpec('clin.clin_aux_note',
		where = 'fk_encounter = ANY(%s)' % _ENC,
		fks = _EPI_FKS
	),
	_cTableSpec('clin.family_history',
		where = 'fk_encounter = ANY(%s)' % _ENC,
		fks = dict(_EPI_FKS, fk_relation_type = ('ref', 'clin.fhx_relation_type'))
	),
	_cTableSpec('clin.intake',
		where = 'fk_encounter = ANY(%s)' % _ENC,
		fks = dict(_EPI_FKS, fk_substance = ('ref', 'ref.substance')),
		# unique index on (fk_substance, amount, unit, schedule, discontinued, patient)
		match = "(SELECT i.pk FROM clin.intake i WHERE clin.map_enc_or_epi_to_patient(i.fk_encounter, i.fk_episode) = pg_temp._tp_target() AND i.fk_substance = pg_temp._tp_r('ref.substance', s.fk_substance) AND i.amount IS NOT DISTINCT FROM s.amount AND i.unit IS NOT DISTINCT FROM s.unit AND i.schedule IS NOT DISTINCT FROM s.schedule AND i.discontinued IS NOT DISTINCT FROM s.discontinued ORDER BY i.pk LIMIT 1)",
		# an ongoing non-regimen intake must be the only ongoing intake of a substance
		skip_if = "(s.discontinued IS NULL OR s.discontinued > now()) AND EXISTS (SELECT 1 FROM clin.intake i WHERE clin.map_enc_or_epi_to_patient(i.fk_encounter, i.fk_episode) = pg_temp._tp_target() AND i.fk_substance = pg_temp._tp_r('ref.substance', s.fk_substance) AND (i.discontinued IS NULL OR i.discontinued > now()) AND (i.amount IS NULL OR s.amount IS NULL))",
		skip_reason = 'conflicts with an ongoing intake of the same substance in the target'
	),
	_cTableSpec('clin.vaccination',
		where = 'fk_encounter = ANY(%s)' % _ENC,
		fks = dict(_EPI_FKS, fk_provider = ('staff',), fk_vaccine = ('ref', 'ref.vaccine'))
	),
	_cTableSpec('clin.external_care',
		where = 'fk_encounter = ANY(%s)' % _ENC,
		fks = {'fk_encounter': ('int', 'clin.encounter'), 'fk_health_issue': ('int', 'clin.health_issue'), 'fk_org_unit': ('ref', 'dem.org_unit')},
		# an issue (or health issue) is cared for only once per org unit and patient
		match = """(SELECT x.pk FROM clin.external_care x JOIN clin.encounter e ON (e.pk = x.fk_encounter)
			WHERE e.fk_patient = pg_temp._tp_target()
				AND x.fk_org_unit = pg_temp._tp_r('dem.org_unit', s.fk_org_unit)
				AND (
					(s.fk_health_issue IS NULL AND x.fk_health_issue IS NULL AND x.issue IS NOT DISTINCT FROM s.issue)
						OR
					(s.fk_health_issue IS NOT NULL AND x.fk_health_issue = pg_temp._tp_mo('clin.health_issue', s.fk_health_issue))
				)
			ORDER BY x.pk LIMIT 1)"""
	),
	_cTableSpec('clin.hospital_stay',
		where = 'fk_encounter = ANY(%s)' % _ENC,
		fks = dict(_EPI_FKS, fk_org_unit = ('ref', 'dem.org_unit'))
	),
	_cTableSpec('clin.lab_request',
		where = 'fk_encounter = ANY(%s)' % _ENC,
		fks = dict(_EPI_FKS, fk_test_org = ('ref', 'clin.test_org'), fk_requestor = ('null',)),
		extra = {'_x_requestor_staff': ('integer', '(SELECT st.pk FROM dem.staff st WHERE st.fk_identity = t.fk_requestor ORDER BY st.pk LIMIT 1)', 'staff')},
		overrides = {
			'fk_requestor': '(SELECT st.fk_identity FROM dem.staff st WHERE st.pk = pg_temp._tp_s(s._x_requestor_staff))',
			'request_id': "CASE WHEN s.request_id IS NOT NULL AND EXISTS (SELECT 1 FROM clin.lab_request r WHERE r.fk_test_org = pg_temp._tp_r('clin.test_org', s.fk_test_org) AND r.request_id = s.request_id) THEN s.request_id || ' ' || pg_temp._tp_suffix(m.new_pk) ELSE s.request_id END"
		}
	),
	_cTableSpec('clin.test_result',
		where = 'fk_encounter = ANY(%s)' % _ENC,
		fks = dict(_EPI_FKS, fk_type = ('ref', 'clin.test_type'), fk_request = ('int', 'clin.lab_request'), fk_intended_reviewer = ('staff',))
	),
	_cTableSpec('clin.form_instances',
		where = 'fk_encounter = ANY(%s)' % _ENC,
		fks = dict(_EPI_FKS, fk_form_def = ('ref', 'ref.paperwork_templates'))
	),
	_cTableSpec('clin.allergy',
		where = 'fk_encounter = ANY(%s)' % _ENC,
		fks = dict(_EPI_FKS, fk_type = ('ref', 'clin._enum_allergy_type'))
	),
	_cTableSpec('blobs.doc_med',
		where = 'fk_encounter = ANY(%s)' % _ENC,
		fks = dict(_EPI_FKS, fk_type = ('ref', 'blobs.doc_type'), fk_org_unit = ('ref', 'dem.org_unit'), fk_hospital_stay = ('soft', 'clin.hospital_stay'))
	),
	_cTableSpec('clin.procedure',
		where = 'fk_encounter = ANY(%s)' % _ENC,
		fks = dict(_EPI_FKS, fk_doc = ('int', 'blobs.doc_med'), fk_hospital_stay = ('int', 'clin.hospital_stay'), fk_org_unit = ('ref', 'dem.org_unit'))
	),
	_cTableSpec('blobs.doc_obj',
		where = 'fk_doc = ANY({blobs.doc_med})',
		fks = {'fk_doc': ('int', 'blobs.doc_med'), 'fk_intended_reviewer': ('staff',)}
	),
	_cTableSpec('blobs.doc_desc',
		where = 'fk_doc = ANY({blobs.doc_med})',
		fks = {'fk_doc': ('int', 'blobs.doc_med')}
	),
	_cTableSpec('blobs.lnk_doc_med2episode',
		where = 'fk_doc_med = ANY({blobs.doc_med})',
		fks = {'fk_doc_med': ('int', 'blobs.doc_med'), 'fk_episode': ('int', 'clin.episode')},
		# a trigger silently suppresses links duplicating the primary episode of the document
		lenient = True
	),
	_staff_review_spec('blobs.reviewed_doc_objs', 'blobs.doc_obj', one_per_row = False),
	_staff_review_spec('clin.reviewed_test_results', 'clin.test_result', one_per_row = True),
	_cTableSpec('clin.clin_diag',
		where = 'fk_narrative = ANY({clin.clin_narrative})',
		fks = {'fk_narrative': ('int', 'clin.clin_narrative')},
		match = "(SELECT d.pk FROM clin.clin_diag d WHERE d.fk_narrative = pg_temp._tp_mo('clin.clin_narrative', s.fk_narrative) ORDER BY d.pk LIMIT 1)",
		dedupe = ['s.fk_narrative']
	),
	_type2item_spec(),
	_code_link_spec('clin.lnk_code2rfe', 'clin.encounter'),
	_code_link_spec('clin.lnk_code2aoe', 'clin.encounter'),
	_code_link_spec('clin.lnk_code2h_issue', 'clin.health_issue'),
	_code_link_spec('clin.lnk_code2episode', 'clin.episode'),
	_code_link_spec('clin.lnk_code2narrative', 'clin.clin_narrative'),
	_code_link_spec('clin.lnk_code2procedure', 'clin.procedure'),
	_code_link_spec('clin.lnk_code2fhx', 'clin.family_history'),
	_cTableSpec('clin.export_item',
		where = 'fk_identity = %(pat)s',
		fks = {'fk_identity': ('int', 'dem.identity'), 'fk_doc_obj': ('int', 'blobs.doc_obj')},
		overrides = {
			# unique per patient
			'description': "CASE WHEN EXISTS (SELECT 1 FROM clin.export_item e WHERE e.fk_identity = pg_temp._tp_target() AND e.description = s.description) THEN s.description || ' ' || pg_temp._tp_suffix(m.new_pk) ELSE s.description END",
			# unique per patient, append to existing items
			'list_position': 'coalesce((SELECT max(e.list_position) FROM clin.export_item e WHERE e.fk_identity = pg_temp._tp_target()), 0) + row_number() OVER (ORDER BY s.list_position, s._src_pk)'
		}
	),
	_cTableSpec('bill.bill',
		where = 'pk IN (SELECT bi.fk_bill FROM bill.bill_item bi WHERE bi.fk_encounter = ANY(%s)) OR fk_receiver_identity = %%(pat)s' % _ENC,
		fks = {
			# the database refuses invoices linked to bills without items
			'fk_doc': ('defer', 'blobs.doc_med'),
			'fk_receiver_address': ('soft', 'dem.lnk_person_org_address'),
			'fk_receiver_identity': ('soft', 'dem.identity')
		},
		overrides = {
			'invoice_id': "CASE WHEN EXISTS (SELECT 1 FROM bill.bill b WHERE b.invoice_id = s.invoice_id) THEN s.invoice_id || ' ' || pg_temp._tp_suffix(m.new_pk) ELSE s.invoice_id END"
		}
	),
	_cTableSpec('bill.bill_item',
		where = 'fk_encounter = ANY(%s)' % _ENC,
		fks = {'fk_bill': ('int', 'bill.bill'), 'fk_encounter': ('int', 'clin.encounter'), 'fk_provider': ('staff',), 'fk_billable': ('null',)},
		extra = {'_x_billable_code': ('integer', '(SELECT b.pk_coding_system FROM ref.billable b WHERE b.pk = t.fk_billable)', 'code')},
		overrides = {'fk_billable': "(SELECT b.pk FROM ref.billable b WHERE b.pk_coding_system = pg_temp._tp_r('code', s._x_billable_code))"}
	)
]

_TABLE_SPECS_BY_NAME = { spec.table: spec for spec in _TABLE_SPECS }

# tables referencing patient data which are deliberately not transferred
_EXCLUDED_TABLES = {
	'dem.message_inbox': 'local workflow (inbox)',
	'clin.waiting_list': 'local workflow (waiting list)',
	'clin.incoming_data': 'local workflow (unmatched incoming data)',
	'clin.incoming_data_unmatchable': 'local workflow (unmatched incoming data)',
	'clin.suppressed_hint': 'local workflow (suppressed hints)',
	'dem.staff': 'staff role of the patient',
	'dem.lnk_person2relative': 'other persons, transferred as text only',
	'clin.test_org': 'reference data (contact persons are not transferred)',
	'clin.clin_root_item': 'abstract parent table',
	'clin.review_root': 'abstract parent table',
	'clin.lnk_code2item_root': 'abstract parent table',
	'clin.lnk_code2tst_pnl': 'reference data (test panels)'
}

# unused legacy tables: abort export if the patient has rows in there
_LEGACY_TABLES = {
	'clin.form_data': 'SELECT count(1) FROM clin.form_data WHERE fk_instance = ANY(%(clin__form_instances)s::int[])',
	'clin.lnk_pat2vaccination_course': 'SELECT count(1) FROM clin.lnk_pat2vaccination_course WHERE fk_patient = %(pat)s',
	# locale specific / legacy tables outside the core schemas
	'public.form_job_queue': 'SELECT count(1) FROM public.form_job_queue WHERE fk_form_instance = ANY(%(clin__form_instances)s::int[])',
	'au.referral': 'SELECT count(1) FROM au.referral WHERE fk_encounter = ANY(%(clin__encounter)s::int[])',
	'de_de.kvk': 'SELECT count(1) FROM de_de.kvk WHERE fk_patient = %(pat)s',
	'de_de.zuzahlungsbefreiung': 'SELECT count(1) FROM de_de.zuzahlungsbefreiung WHERE id_patient = %(pat)s'
}

# patient data "roots" for the completeness check
_PATIENT_ROOTS = [('dem.identity', 'pk'), ('clin.patient', 'fk_identity')]
_INHERITANCE_PARENTS = ['clin.clin_root_item', 'clin.review_root', 'clin.lnk_code2item_root']

#------------------------------------------------------------
class _cRefSpec:
	"""How to transfer one table of reference data.

	Reference rows are looked up in the target by natural key
	(alternatives tried in order), and created if not found.
	"""
	def __init__(self, table:str, nks:list=None, pk:str='pk', fks:dict=None, keep:str=None,
		map_name:str=None, map_col:str=None, create_if:str=None, require:dict=None, child_of:tuple=None, extra:dict=None
	):
		self.table = table
		self.schema, self.name = table.split('.')
		self.nks = nks or []
		self.pk = pk
		self.fks = fks or {}
		# natural key column for references which use the natural key value itself
		self.keep = keep
		self.map_name = map_name or ('ref:%s' % table)
		self.map_col = map_col or pk
		self.create_if = create_if
		# {col: (table, col)}: must exist in target, cannot be created
		self.require = require or {}
		# (fk col, parent ref table): rows are transferred along with their parent
		self.child_of = child_of
		self.extra = extra or {}
		self.cols = []
		self.col_types = {}
		self.bytea_cols = []
		self.identity_cols = set()
		self.sequence = None

	#--------------------------------------------------------
	def _get_staging(self) -> str:
		return 'pg_temp._s_ref__%s__%s' % (self.schema, self.name)

	staging = property(_get_staging)

	#--------------------------------------------------------
	def _get_staged_cols(self) -> list:
		if self.keep:
			return [ c for c in self.cols if c not in _NEVER_COPY_COLS and c != self.pk ]
		return [ c for c in self.cols if c not in _NEVER_COPY_COLS and c != self.pk and c != self.map_col and self.fks.get(c, ('copy',))[0] != 'null' ]

	staged_cols = property(_get_staged_cols)

#------------------------------------------------------------
_CODE_NKS = [
	"t.fk_data_source = pg_temp._tp_r('ref.data_source', s.fk_data_source) AND lower(t.code) = lower(s.code) AND t.term IS NOT DISTINCT FROM s.term",
	"t.fk_data_source = pg_temp._tp_r('ref.data_source', s.fk_data_source) AND lower(t.code) = lower(s.code)"
]
_CODE_TABLES = ['ref.atc', 'ref.icd9', 'ref.icd10', 'ref.icpc', 'ref.loinc', 'ref.ops', 'ref.other_code', 'ref.coda', 'ref.billable']

def _code_spec(table:str) -> _cRefSpec:
	require = {}
	if table == 'ref.icpc':
		require = {'fk_chapter': ('ref.icpc_chapter', 'chapter'), 'fk_component': ('ref.icpc_component', 'component')}
	return _cRefSpec(table,
		nks = _CODE_NKS,
		fks = {'fk_data_source': ('ref', 'ref.data_source')},
		map_name = 'ref:code',
		map_col = 'pk_coding_system',
		require = require
	)

_REF_SPECS = [
	_cRefSpec('ref.data_source', nks = ['t.name_short = s.name_short AND t.version IS NOT DISTINCT FROM s.version']),
	_cRefSpec('dem.country', pk = 'id', keep = 'code', nks = ['t.code = s.code']),
	_cRefSpec('dem.region',
		nks = ['t.country = s.country AND lower(t.code) = lower(s.code)'],
		fks = {'country': ('keep', 'dem.country')}
	),
	_cRefSpec('dem.urb', pk = 'id',
		nks = ["t.fk_region = pg_temp._tp_r('dem.region', s.fk_region) AND lower(t.postcode) IS NOT DISTINCT FROM lower(s.postcode) AND lower(t.name) = lower(s.name)"],
		fks = {'fk_region': ('ref', 'dem.region')}
	),
	_cRefSpec('dem.street', pk = 'id',
		nks = ["t.id_urb = pg_temp._tp_r('dem.urb', s.id_urb) AND lower(t.name) = lower(s.name) AND lower(t.postcode) IS NOT DISTINCT FROM lower(s.postcode)"],
		fks = {'id_urb': ('ref', 'dem.urb')}
	),
	_cRefSpec('dem.address', pk = 'id',
		nks = ["t.id_street = pg_temp._tp_r('dem.street', s.id_street) AND t.number IS NOT DISTINCT FROM s.number AND t.subunit IS NOT DISTINCT FROM s.subunit AND t.aux_street IS NOT DISTINCT FROM s.aux_street AND t.addendum IS NOT DISTINCT FROM s.addendum"],
		fks = {'id_street': ('ref', 'dem.street')}
	),
	_cRefSpec('dem.org_category', nks = ['lower(t.description) = lower(s.description)']),
	_cRefSpec('dem.org',
		nks = ['t.description = s.description'],
		fks = {'fk_category': ('ref', 'dem.org_category'), 'fk_data_source': ('ref', 'ref.data_source')}
	),
	_cRefSpec('dem.org_unit',
		nks = ["t.fk_org = pg_temp._tp_r('dem.org', s.fk_org) AND t.description = s.description"],
		fks = {'fk_org': ('ref', 'dem.org'), 'fk_category': ('ref', 'dem.org_category'), 'fk_address': ('ref', 'dem.address')}
	),
	_cRefSpec('dem.gender_label', keep = 'tag', nks = ['t.tag = s.tag']),
	_cRefSpec('dem.marital_status', nks = ['t.name = s.name']),
	_cRefSpec('dem.enum_ext_id_types', nks = ['t.name = s.name AND t.issuer IS NOT DISTINCT FROM s.issuer']),
	_cRefSpec('dem.enum_comm_types', nks = ['t.description = s.description']),
	_cRefSpec('dem.address_type', pk = 'id', nks = ['t.name = s.name']),
	_cRefSpec('dem.occupation', pk = 'id', nks = ['t.name = s.name']),
	_cRefSpec('ref.tag_image', nks = ['t.description = s.description']),
	_cRefSpec('clin.encounter_type', nks = ['t.description = s.description']),
	_cRefSpec('clin.clin_item_type', nks = ['t.code = s.code', 't.type = s.type']),
	_cRefSpec('clin._enum_allergy_type', nks = ['t.value = s.value']),
	_cRefSpec('clin.fhx_relation_type', nks = ['t.description = s.description AND t.is_genetic IS NOT DISTINCT FROM s.is_genetic']),
	_cRefSpec('blobs.doc_type', nks = ['t.name = s.name']),
	_cRefSpec('ref.form_types', nks = ['t.name = s.name']),
	_cRefSpec('ref.paperwork_templates',
		nks = [
			't.name_short = s.name_short AND t.name_long = s.name_long AND t.external_version IS NOT DISTINCT FROM s.external_version',
			't.name_short = s.name_short AND t.name_long = s.name_long'
		],
		fks = {'fk_template_type': ('ref', 'ref.form_types')}
	),
	_cRefSpec('ref.substance', nks = ['lower(t.description) = lower(s.description)']),
	_cRefSpec('ref.vacc_indication', nks = ['t.target = s.target', 't.atc = s.atc']),
	_cRefSpec('ref.vaccine',
		nks = [
			't.brandname = s.brandname',
			't.brandname IS NULL AND s.brandname IS NULL AND (SELECT array_agg(i.target::text ORDER BY i.target::text) FROM ref.lnk_indic2vaccine l JOIN ref.vacc_indication i ON (i.pk = l.fk_indication) WHERE l.fk_vaccine = t.pk) = s._x_targets'
		],
		extra = {'_x_targets': ('text[]', '(SELECT array_agg(i.target::text ORDER BY i.target::text) FROM ref.lnk_indic2vaccine l JOIN ref.vacc_indication i ON (i.pk = l.fk_indication) WHERE l.fk_vaccine = t.pk)')}
	),
	_cRefSpec('ref.lnk_indic2vaccine',
		fks = {'fk_vaccine': ('ref', 'ref.vaccine'), 'fk_indication': ('ref', 'ref.vacc_indication')},
		# only needed when the vaccine itself is created
		create_if = "(SELECT m.status FROM pg_temp._gm_tp_map m WHERE m.tbl = 'ref:ref.vaccine' AND m.src_pk = s.fk_vaccine) = 'ref_created'",
		child_of = ('fk_vaccine', 'ref.vaccine')
	),
	_cRefSpec('clin.meta_test_type', nks = ['t.abbrev = s.abbrev']),
	_cRefSpec('clin.test_org',
		nks = ["t.fk_org_unit = pg_temp._tp_r('dem.org_unit', s.fk_org_unit)"],
		fks = {'fk_org_unit': ('ref', 'dem.org_unit'), 'fk_adm_contact': ('null',), 'fk_med_contact': ('null',)}
	),
	_cRefSpec('clin.test_type',
		nks = [
			"t.fk_test_org = pg_temp._tp_r('clin.test_org', s.fk_test_org) AND t.abbrev = s.abbrev",
			"t.fk_test_org = pg_temp._tp_r('clin.test_org', s.fk_test_org) AND t.name = s.name"
		],
		fks = {'fk_test_org': ('ref', 'clin.test_org'), 'fk_meta_test_type': ('ref', 'clin.meta_test_type')}
	)
] + [ _code_spec(tbl) for tbl in _CODE_TABLES ]

_REF_SPECS_BY_NAME = { spec.table: spec for spec in _REF_SPECS }

#============================================================
# SQL literal rendering
#------------------------------------------------------------
_E_STRING_ESCAPES = {
	ord('\\'): '\\\\',
	ord("'"): "\\'",
	ord('\n'): '\\n',
	ord('\r'): '\\r',
	ord('\t'): '\\t',
	0x2028: '\\u2028',
	0x2029: '\\u2029',
	0x85: '\\u0085'
}
for _code in list(range(0x20)) + [0x7f]:
	_E_STRING_ESCAPES.setdefault(_code, '\\x%02x' % _code)
del _code

def sql_literal(value) -> str:
	"""Render a text value as a single-line SQL E'' literal.

	Line breaks and other control characters are escaped,
	such that a literal never spans lines in the script.
	"""
	if value is None:
		return 'NULL'
	return "E'%s'" % str(value).translate(_E_STRING_ESCAPES)

#------------------------------------------------------------
def _quote_identifier(identifier:str) -> str:
	"""Quote an identifier."""
	return '"%s"' % identifier.replace('"', '""')

#------------------------------------------------------------
def _quote_qual_table(table:str) -> str:
	"""Quote a schema qualified table name."""
	schema, name = table.split('.')
	return '%s.%s' % (_quote_identifier(schema), _quote_identifier(name))

#------------------------------------------------------------
def _array_arg_name(table:str) -> str:
	return table.replace('.', '__')

#------------------------------------------------------------
def _expand_where(where:str) -> str:
	"""Turn {schema.table} placeholders into array parameters."""
	return re.sub(r'\{([a-z_]+\.[a-z_0-9]+)\}', lambda m: '%%(%s)s::int[]' % _array_arg_name(m.group(1)), where)

#============================================================
# script writing
#------------------------------------------------------------
class _cStatementWriter:
	"""Writes marker-separated SQL statements to a text stream."""

	def __init__(self, stream, prefix:str=''):
		self.__stream = stream
		self.__prefix = prefix
		self.__count = 0
		self.__sha = None

	#--------------------------------------------------------
	def start_hashing(self):
		self.__sha = hashlib.sha256()

	#--------------------------------------------------------
	def _get_hexdigest(self) -> str:
		return self.__sha.hexdigest()

	hexdigest = property(_get_hexdigest)

	#--------------------------------------------------------
	def raw(self, text:str):
		if self.__sha:
			self.__sha.update(text.encode('utf8'))
		self.__stream.write(text)

	#--------------------------------------------------------
	def stmt(self, section:str, sql:str):
		self.__count += 1
		sql = sql.strip()
		# psql needs terminated statements
		if not sql.endswith(';') and not sql.split('\n')[-1].lstrip().startswith('--'):
			sql += ';'
		self.raw('%s %s%s %s\n%s\n' % (MARKER_STMT, self.__prefix, self.__count, section, sql))

	#--------------------------------------------------------
	def comment(self, text:str):
		for line in text.split('\n'):
			self.raw(('-- %s' % line).rstrip() + '\n')

#------------------------------------------------------------
class _cRowBatcher:
	"""Batches staging rows into multi-row INSERT statements."""

	def __init__(self, writer:_cStatementWriter, section:str, staging:str, cols:list, key_col:str='_src_pk'):
		self.__writer = writer
		self.__section = section
		self.__head = 'INSERT INTO %s (%s, %s) VALUES' % (staging, key_col, ', '.join([ _quote_identifier(c) for c in cols ]))
		self.__rows = []
		self.__size = 0

	#--------------------------------------------------------
	def add(self, rendered_row:str):
		self.__rows.append(rendered_row)
		self.__size += len(rendered_row)
		if self.__size > _MAX_STAGING_STMT_SIZE:
			self.flush()

	#--------------------------------------------------------
	def flush(self):
		if not self.__rows:
			return
		self.__writer.stmt(self.__section, '%s\n\t  %s;' % (self.__head, '\n\t, '.join(self.__rows)))
		self.__rows = []
		self.__size = 0

#============================================================
# export
#------------------------------------------------------------
_SQL_get_columns = """
SELECT
	a.attname AS name,
	format_type(a.atttypid, a.atttypmod) AS coltype,
	a.attidentity AS identity,
	(a.atttypid = 'bytea'::regtype) AS is_bytea
FROM pg_attribute a
WHERE
	a.attrelid = %(tbl)s::regclass
		AND
	a.attnum > 0
		AND
	NOT a.attisdropped
ORDER BY a.attnum
"""

_SQL_get_column_default = """
SELECT pg_get_expr(d.adbin, d.adrelid)
FROM pg_attrdef d
	JOIN pg_attribute a ON (a.attrelid = d.adrelid AND a.attnum = d.adnum)
WHERE
	d.adrelid = %(tbl)s::regclass
		AND
	a.attname = %(col)s
"""

_SQL_get_all_fks = """
SELECT
	src_ns.nspname || '.' || src.relname AS src_table,
	src_col.attname AS src_col,
	tgt_ns.nspname || '.' || tgt.relname AS tgt_table,
	tgt_col.attname AS tgt_col
FROM pg_constraint con
	JOIN pg_class src ON (src.oid = con.conrelid)
	JOIN pg_namespace src_ns ON (src_ns.oid = src.relnamespace)
	JOIN pg_class tgt ON (tgt.oid = con.confrelid)
	JOIN pg_namespace tgt_ns ON (tgt_ns.oid = tgt.relnamespace)
	JOIN pg_attribute src_col ON (src_col.attrelid = con.conrelid AND src_col.attnum = con.conkey[1])
	JOIN pg_attribute tgt_col ON (tgt_col.attrelid = con.confrelid AND tgt_col.attnum = con.confkey[1])
WHERE con.contype = 'f'
"""

_SQL_get_child_tables = """
SELECT ns.nspname || '.' || c.relname
FROM pg_inherits i
	JOIN pg_class c ON (c.oid = i.inhrelid)
	JOIN pg_namespace ns ON (ns.oid = c.relnamespace)
WHERE i.inhparent = %(tbl)s::regclass
"""

#------------------------------------------------------------
def _run_sql_query(curs, sql:str, args:dict=None) -> list:
	curs.execute(sql, args)
	if curs.description is None:
		return []

	return curs.fetchall()

#------------------------------------------------------------
def verify_export_completeness(conn=None) -> list:
	"""Check that all tables referencing patient data are handled.

	Returns a list of problems (strings, no patient data). An
	empty list means the database layout is fully covered by the
	transplant specifications. This guards against silently
	losing data after future schema changes.
	"""
	conn, close_conn = _get_conn(conn)
	curs = conn.cursor()
	try:
		return _verify_export_completeness(curs)

	finally:
		curs.close()
		close_conn()

#------------------------------------------------------------
def _verify_export_completeness(curs) -> list:
	problems = []
	handled = set(_TABLE_SPECS_BY_NAME)
	known = handled | set(_EXCLUDED_TABLES) | set(_LEGACY_TABLES) | set(_REF_SPECS_BY_NAME)
	fks = _run_sql_query(curs, _SQL_get_all_fks)
	patient_tables = { tbl for tbl, col in _PATIENT_ROOTS } | handled
	for src_table, src_col, tgt_table, tgt_col in fks:
		# anyone referencing patient data must be known
		if tgt_table in patient_tables and src_table not in known:
			problems.append('table [%s.%s] references patient data [%s.%s] but is not handled by the transplant' % (src_table, src_col, tgt_table, tgt_col))
			continue
		# every FK column of handled tables must be classified
		if src_table in handled:
			spec = _TABLE_SPECS_BY_NAME[src_table]
			if src_col not in spec.fks and src_col not in spec.overrides:
				problems.append('FK column [%s.%s] -> [%s] is not classified in the transplant specification' % (src_table, src_col, tgt_table))
		if src_table in _REF_SPECS_BY_NAME:
			spec = _REF_SPECS_BY_NAME[src_table]
			if src_col not in spec.fks and src_col not in spec.require:
				problems.append('FK column [%s.%s] -> [%s] of reference table is not classified in the transplant specification' % (src_table, src_col, tgt_table))
	# EMR items might be added by inheritance only
	for parent in _INHERITANCE_PARENTS:
		for row in _run_sql_query(curs, _SQL_get_child_tables, {'tbl': parent}):
			child = row[0]
			if child not in known:
				problems.append('table [%s] inherits from [%s] but is not handled by the transplant' % (child, parent))
	for row in _run_sql_query(curs, _SQL_get_child_tables, {'tbl': 'ref.coding_system_root'}):
		if row[0] not in _CODE_TABLES:
			problems.append('coding system table [%s] is not handled by the transplant' % row[0])
	for problem in problems:
		_log.error(problem)
	return problems

#------------------------------------------------------------
def _get_conn(conn=None):
	if conn is not None:
		#return conn, False
		return conn, lambda *x: None

	conn = gmPG2.get_connection(readonly = True, pooled = False)
	#return gmPG2.get_connection(readonly = True, pooled = False), True
	return conn, conn.close

#------------------------------------------------------------
def _load_table_layout(curs, spec):
	"""Fill in column details of a table spec from the database."""
	rows = _run_sql_query(curs, _SQL_get_columns, {'tbl': spec.table})
	if not rows:
		raise cTransplantError('table [%s] not found' % spec.table)
	spec.cols = [ r[0] for r in rows ]
	spec.col_types = { r[0]: r[1] for r in rows }
	spec.bytea_cols = [ r[0] for r in rows if r[3] and r[0] in spec.staged_cols ]
	identity_cols = { r[0] for r in rows if r[2] in ('a', 'd') }
	if isinstance(spec, _cTableSpec):
		spec.has_audit = set(_AUDIT_COLS).issubset(set(spec.cols))
		spec.pk_is_identity = spec.pk in identity_cols
		seq_col = spec.pk
	else:
		spec.identity_cols = identity_cols
		seq_col = spec.map_col
		if spec.table in _CODE_TABLES:
			# pk_coding_system comes from the parent's sequence
			seq_col = 'pk_coding_system'
	spec.sequence = _get_sequence(curs, spec.table, seq_col)
	if (spec.sequence is None) and not getattr(spec, 'keep', None) and not getattr(spec, 'child_of', None):
		raise cTransplantError('cannot determine sequence for [%s.%s]' % (spec.table, seq_col))

#------------------------------------------------------------
def _get_sequence(curs, table:str, col:str) -> str:
	rows = _run_sql_query(curs, 'SELECT pg_get_serial_sequence(%(tbl)s, %(col)s)', {'tbl': table, 'col': col})
	if rows and rows[0][0]:
		return rows[0][0]

	rows = _run_sql_query(curs, _SQL_get_column_default, {'tbl': table, 'col': col})
	if rows and rows[0][0]:
		match = re.search(r"nextval\('([^']+)'", rows[0][0])
		if match:
			return match.group(1)

	return None

#------------------------------------------------------------
class _cExporter:
	"""Extracts one patient into a transplant script."""

	def __init__(self, conn, pk_identity:int, include_history:bool=True, source_description:str=None, progress_callback=None):
		self.conn = conn
		self.pk_identity = pk_identity
		self.include_history = include_history
		self.source_description = source_description
		self.progress_callback = progress_callback
		self.export_uuid = str(uuid.uuid4())
		self.pks = {}							# table -> [src pks]
		self.pk_audits = {}						# table -> [pk_audit]
		self.counts = {}
		self.staff_pks = set()
		self.ref_wanted = {}					# ref table / 'code' -> set of keys
		self.ref_rows = {}						# ref table -> number of staged rows
		self.history_sha256 = None
		self.history_note = None
		self.meta = {}
		self.texts = {}
		self.staff_rows = []
		self.relatives_note = None
		self.src_timezone = None
		self.schema_hash = None
		self.source_id = None

	#--------------------------------------------------------
	def _progress(self, msg:str):
		_log.debug(msg)
		if self.progress_callback:
			self.progress_callback(msg)

	#--------------------------------------------------------
	def _want_ref(self, kind:str, value):
		if value is None:
			return
		self.ref_wanted.setdefault(kind, set()).add(value)

	#--------------------------------------------------------
	def export(self, filename:str) -> dict:
		curs = self.conn.cursor()
		section1 = io.StringIO()
		w1 = _cStatementWriter(section1, prefix = 'a')
		tmp_fd, tmp_name = tempfile.mkstemp(prefix = 'gm-transplant-', suffix = '.part', dir = os.path.dirname(filename))
		try:
			with os.fdopen(tmp_fd, 'wt', encoding = 'utf8', newline = '\n') as section2:
				w2 = _cStatementWriter(section2, prefix = 'b')
				curs.execute('BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY')
				try:
					self._prepare(curs)
					self._extract_patient_tables(curs, w1, w2)
					self._check_legacy_tables(curs)
					self._extract_staff(curs)
					self._extract_refs(curs, w2)
					self._extract_relatives(curs)
					if self.include_history:
						self._export_history(curs, w2)
				finally:
					curs.execute('ROLLBACK')
			self._assemble(filename, section1.getvalue(), tmp_name)
		finally:
			curs.close()
			if os.path.exists(tmp_name):
				os.remove(tmp_name)
		return self.meta

	#--------------------------------------------------------
	def _prepare(self, curs):
		curs.execute("SET LOCAL DateStyle TO 'ISO, YMD'")
		curs.execute("SET LOCAL IntervalStyle TO 'iso_8601'")
		curs.execute('SET LOCAL extra_float_digits TO 3')
		curs.execute("SET LOCAL bytea_output TO 'hex'")
		self.src_timezone = _run_sql_query(curs, 'SHOW TimeZone')[0][0]
		rows = _run_sql_query(curs, 'SELECT 1 FROM dem.identity WHERE pk = %(pat)s', {'pat': self.pk_identity})
		if not rows:
			raise cTransplantError('patient #%s not found' % self.pk_identity)
		rows = _run_sql_query(curs, "SELECT md5(min(imported)::text) FROM gm.schema_revision")
		if rows and rows[0][0]:
			self.source_id = rows[0][0]
		else:
			self.source_id = _run_sql_query(curs, 'SELECT md5(current_database())')[0][0]
		db_name = _run_sql_query(curs, 'SELECT current_database()')[0][0]
		if not self.source_description:
			self.source_description = db_name
		for spec in _TABLE_SPECS + _REF_SPECS:
			_load_table_layout(curs, spec)

	#--------------------------------------------------------
	def _select_sql(self, spec) -> str:
		parts = []
		for col in spec.staged_cols:
			if col in spec.bytea_cols:
				parts.append('octet_length(t.%s)' % _quote_identifier(col))
			else:
				parts.append('t.%s::text' % _quote_identifier(col))
		for name, (sqltype, expr, kind) in spec.extra.items():
			parts.append('(%s)::text' % expr)
		if spec.has_audit:
			parts.append('t.modified_by::text')
			parts.append('t.modified_when::text')
			parts.append('t.pk_audit')
		where = _expand_where(spec.where)
		if spec.export_filter:
			where = '(%s) AND (%s)' % (where, spec.export_filter)
		return 'SELECT t.%s, %s FROM %s t WHERE %s ORDER BY t.%s' % (
			_quote_identifier(spec.pk),
			', '.join(parts),
			_quote_qual_table(spec.table),
			where,
			_quote_identifier(spec.pk)
		)

	#--------------------------------------------------------
	def _query_args(self) -> dict:
		args = {'pat': self.pk_identity}
		for spec in _TABLE_SPECS:
			args[_array_arg_name(spec.table)] = self.pks.get(spec.table, [])
		return args

	#--------------------------------------------------------
	def _extract_patient_tables(self, curs, w1, w2):
		for spec in _TABLE_SPECS:
			self._progress('exporting [%s]' % spec.table)
			writer = w1 if spec.section == 1 else w2
			rows = _run_sql_query(curs, self._select_sql(spec), self._query_args())
			staged_cols = spec.staged_cols
			stage_cols = staged_cols + list(spec.extra) + (['_x_modified_by', '_x_modified_when'] if spec.has_audit else [])
			batcher = _cRowBatcher(writer, 'stage %s' % spec.table, spec.staging, stage_cols)
			pks = []
			pk_audits = []
			blob_lengths = []
			n_vals = len(staged_cols) + len(spec.extra)
			for row in rows:
				src_pk = row[0]
				pks.append(src_pk)
				values = list(row[1:])
				if spec.has_audit:
					pk_audits.append(values[-1])
					values = values[:-1]
				rendered = [str(src_pk)]
				for idx, col in enumerate(staged_cols):
					val = values[idx]
					if col in spec.bytea_cols:
						blob_lengths.append((src_pk, col, val))
						rendered.append('NULL')
						continue
					self._collect(spec.fks.get(col), val)
					rendered.append(sql_literal(val))
				for idx, (name, (sqltype, expr, kind)) in enumerate(spec.extra.items()):
					val = values[len(staged_cols) + idx]
					if kind == 'staff' and val is not None:
						self.staff_pks.add(int(val))
					elif kind == 'code' and val is not None:
						self._want_ref('code', int(val))
					rendered.append(sql_literal(val))
				for val in values[n_vals:]:
					rendered.append(sql_literal(val))
				batcher.add('(%s)' % ', '.join(rendered))
			batcher.flush()
			self.pks[spec.table] = pks
			self.pk_audits[spec.table] = pk_audits
			self.counts[spec.table] = len(pks)
			for src_pk, col, length in blob_lengths:
				self._export_blob(curs, w2, spec.table, spec.table, spec.pk, col, src_pk, length)
		if not self.pks['dem.identity']:
			raise cTransplantError('patient #%s not found' % self.pk_identity)

	#--------------------------------------------------------
	def _collect(self, fk:tuple, val):
		if fk is None or val is None:
			return
		kind = fk[0]
		if kind == 'staff':
			self.staff_pks.add(int(val))
		elif kind == 'ref':
			self._want_ref(fk[1], int(val))
		elif kind == 'code':
			self._want_ref('code', int(val))
		elif kind == 'keep':
			self._want_ref(fk[1], val)

	#--------------------------------------------------------
	def _export_blob(self, curs, writer, map_key:str, table:str, pk_col:str, col:str, src_pk:int, length):
		if length is None:
			return
		offset = 0
		seq = 0
		while True:
			rows = _run_sql_query (
				curs,
				'SELECT substring(%s FROM %%(off)s FOR %%(len)s) FROM %s WHERE %s = %%(pk)s' % (_quote_identifier(col), _quote_qual_table(table), _quote_identifier(pk_col)),
				{'off': offset + 1, 'len': _BLOB_CHUNK_SIZE, 'pk': src_pk}
			)
			data = bytes(rows[0][0]) if rows and rows[0][0] is not None else b''
			writer.stmt('blob %s' % map_key, "INSERT INTO pg_temp._s_blob_chunk (tbl, col, src_pk, seq, data) VALUES (%s, %s, %s, %s, decode('%s', 'base64'));" % (
				sql_literal(map_key),
				sql_literal(col),
				src_pk,
				seq,
				base64.b64encode(data).decode('ascii')
			))
			offset += len(data)
			seq += 1
			if (len(data) < _BLOB_CHUNK_SIZE) or (offset >= length):
				break

	#--------------------------------------------------------
	def _check_legacy_tables(self, curs):
		args = self._query_args()
		for tbl, sql in _LEGACY_TABLES.items():
			exists, readable = _run_sql_query(curs, "SELECT to_regclass(%(tbl)s) IS NOT NULL, coalesce(has_table_privilege(to_regclass(%(tbl)s), 'SELECT'), false)", {'tbl': tbl})[0]
			if not exists:
				continue
			if not readable:
				# fail closed: cannot rule out patient data in there
				raise cTransplantError(_('Cannot check the table [%s] for data of the patient (no permission). Export as the database owner (gm-dbo).') % tbl)
			if _run_sql_query(curs, sql, args)[0][0] > 0:
				raise cTransplantError(_('The patient has data in the legacy table [%s] which cannot be transplanted.') % tbl)
		# bills must not contain items of other patients
		sql = 'SELECT count(1) FROM bill.bill_item bi WHERE bi.fk_bill = ANY(%(bill__bill)s::int[]) AND NOT bi.fk_encounter = ANY(%(clin__encounter)s::int[])'
		if _run_sql_query(curs, sql, args)[0][0] > 0:
			raise cTransplantError(_('A bill of the patient contains items of other patients. Cannot transplant.'))

	#--------------------------------------------------------
	def _extract_staff(self, curs):
		if not self.staff_pks:
			self.staff_rows = []
			return
		self.staff_rows = _run_sql_query(curs, """
			SELECT
				st.pk, st.short_alias, st.db_user::text,
				(SELECT n.lastnames FROM dem.names n WHERE n.id_identity = st.fk_identity ORDER BY n.active DESC, n.id LIMIT 1),
				(SELECT n.firstnames FROM dem.names n WHERE n.id_identity = st.fk_identity ORDER BY n.active DESC, n.id LIMIT 1),
				(SELECT i.dob::text FROM dem.identity i WHERE i.pk = st.fk_identity)
			FROM dem.staff st
			WHERE st.pk = ANY(%(pks)s::int[])
			ORDER BY st.pk""",
			{'pks': sorted(self.staff_pks)}
		)

	#--------------------------------------------------------
	def _extract_refs(self, curs, writer):
		fetched = {}
		code_resolved = set()
		changed = True
		while changed:
			changed = False
			# map wanted codes to their coding system tables
			codes = self.ref_wanted.get('code', set()) - code_resolved
			if codes:
				rows = _run_sql_query(curs, 'SELECT tableoid::regclass::text, pk_coding_system FROM ref.coding_system_root WHERE pk_coding_system = ANY(%(pks)s::int[])', {'pks': sorted(codes)})
				found = set()
				for tbl, pk in rows:
					tbl = tbl if '.' in tbl else 'ref.%s' % tbl
					if tbl not in _CODE_TABLES:
						raise cTransplantError('unsupported coding system table [%s]' % tbl)
					self._want_ref(tbl, pk)
					found.add(pk)
				code_resolved |= codes
				missing = codes - found
				if missing:
					raise cTransplantError('coding system entries referenced but not found: %s' % sorted(missing))
				changed = True
			for spec in reversed(_REF_SPECS):
				done = fetched.setdefault(spec.table, set())
				if spec.child_of:
					fk_col, parent = spec.child_of
					parents = fetched.get(parent, set()) - done
					if not parents:
						continue
					done |= parents
					rows = self._fetch_ref_rows(curs, spec, fk_col, parents)
				else:
					todo = self.ref_wanted.get(spec.table, set()) - done
					if not todo:
						continue
					done |= todo
					rows = self._fetch_ref_rows(curs, spec, spec.keep or spec.map_col, todo)
				changed = True
				self._stage_ref_rows(curs, writer, spec, rows)

	#--------------------------------------------------------
	def _fetch_ref_rows(self, curs, spec, key_col:str, keys:set) -> list:
		parts = []
		for col in spec.staged_cols:
			if col in spec.bytea_cols:
				parts.append('octet_length(t.%s)' % _quote_identifier(col))
			else:
				parts.append('t.%s::text' % _quote_identifier(col))
		for name, (sqltype, expr) in spec.extra.items():
			parts.append('(%s)::text' % expr)
		if spec.keep:
			key_expr = 't.%s::text' % _quote_identifier(spec.keep)
			cond = 't.%s::text = ANY(%%(keys)s::text[])' % _quote_identifier(key_col)
			keys = sorted([ str(k) for k in keys ])
		else:
			key_expr = 't.%s' % _quote_identifier(spec.map_col)
			cond = 't.%s = ANY(%%(keys)s::int[])' % _quote_identifier(key_col)
			keys = sorted(keys)
		sql = 'SELECT %s, %s FROM %s t WHERE %s ORDER BY 1' % (key_expr, ', '.join(parts), _quote_qual_table(spec.table), cond)
		rows = _run_sql_query(curs, sql, {'keys': keys})
		if not spec.child_of and len(rows) != len(keys):
			raise cTransplantError('reference rows missing in [%s]' % spec.table)
		return rows

	#--------------------------------------------------------
	def _stage_ref_rows(self, curs, writer, spec, rows):
		staged_cols = spec.staged_cols
		cols = staged_cols + list(spec.extra)
		key_col = '_src_key' if spec.keep else '_src_pk'
		batcher = _cRowBatcher(writer, 'stage ref %s' % spec.table, spec.staging, cols, key_col = key_col)
		blobs = []
		for row in rows:
			key = row[0]
			rendered = [sql_literal(key) if spec.keep else str(key)]
			for idx, col in enumerate(staged_cols):
				val = row[1 + idx]
				if col in spec.bytea_cols:
					blobs.append((key, col, val))
					rendered.append('NULL')
					continue
				fk = spec.fks.get(col)
				if fk and fk[0] in ('ref', 'keep'):
					self._want_ref(fk[1], val if fk[0] == 'keep' else (int(val) if val is not None else None))
				rendered.append(sql_literal(val))
			for idx in range(len(spec.extra)):
				rendered.append(sql_literal(row[1 + len(staged_cols) + idx]))
			batcher.add('(%s)' % ', '.join(rendered))
		batcher.flush()
		self.ref_rows[spec.table] = self.ref_rows.get(spec.table, 0) + len(rows)
		for key, col, length in blobs:
			self._export_blob(curs, writer, spec.map_name if spec.map_name != 'ref:code' else 'ref:%s' % spec.table, spec.table, spec.map_col, col, key, length)

	#--------------------------------------------------------
	def _extract_relatives(self, curs):
		rows = _run_sql_query(curs, """
			SELECT
				coalesce(rt.description, '?'),
				(SELECT n.lastnames || ', ' || n.firstnames FROM dem.names n WHERE n.id_identity = CASE WHEN r.id_identity = %(pat)s THEN r.id_relative ELSE r.id_identity END AND n.active LIMIT 1),
				(SELECT to_char(i.dob, 'YYYY-MM-DD') FROM dem.identity i WHERE i.pk = CASE WHEN r.id_identity = %(pat)s THEN r.id_relative ELSE r.id_identity END),
				(r.id_identity = %(pat)s)
			FROM dem.lnk_person2relative r
				LEFT JOIN dem.relation_types rt ON (rt.id = r.id_relation_type)
			WHERE r.id_identity = %(pat)s OR r.id_relative = %(pat)s
			ORDER BY r.id""",
			{'pat': self.pk_identity}
		)
		if not rows:
			self.relatives_note = None
			return
		lines = []
		for relation, name, dob, outgoing in rows:
			direction = '' if outgoing else ' (%s)' % _('inverse')
			lines.append('%s%s: %s' % (relation, direction, ', '.join([ x for x in [name, dob] if x ])))
		self.relatives_note = '; '.join(lines)

	#--------------------------------------------------------
	def _export_history(self, curs, writer):
		"""Format the audit trail of all exported rows as text."""
		self._progress('exporting audit trail')
		lines = [
			_('GNUmed audit history (change history) of a transplanted patient'),
			'=' * 72,
			'%s: %s (%s)' % (_('Source'), self.source_description, self.source_id),
			'%s: #%s' % (_('Source patient'), self.pk_identity),
			'%s: %s' % (_('Export'), self.export_uuid),
			'',
			_('Each entry shows a previous version of a row: who created that version, when and why it was replaced, and which values changed.'),
			''
		]
		unreadable = []
		for spec in _TABLE_SPECS:
			log_table = 'audit.log_%s' % spec.name
			rows = _run_sql_query(curs, "SELECT to_regclass(%(tbl)s) IS NOT NULL, coalesce(has_table_privilege(to_regclass(%(tbl)s), 'SELECT'), false)", {'tbl': log_table})
			exists, readable = rows[0]
			if not exists:
				continue
			if not readable:
				unreadable.append(log_table)
				continue
			curs.execute('SAVEPOINT gm_tp_history')
			try:
				lines.extend(self._format_table_history(curs, spec, log_table))
				curs.execute('RELEASE SAVEPOINT gm_tp_history')
			except Exception:
				_log.exception('cannot read audit trail of [%s]', spec.table)
				curs.execute('ROLLBACK TO SAVEPOINT gm_tp_history')
				unreadable.append(log_table)
		if unreadable:
			self.history_note = 'incomplete: no access to %s' % ', '.join(unreadable)
			lines.extend(['', _('Incomplete: no access to audit tables: %s') % ', '.join(unreadable)])
		text = '\n'.join(lines) + '\n'
		data = text.encode('utf8')
		self.history_sha256 = hashlib.sha256(data).hexdigest()
		offset = 0
		seq = 0
		while True:
			chunk = data[offset:offset + _BLOB_CHUNK_SIZE]
			writer.stmt('blob history', "INSERT INTO pg_temp._s_blob_chunk (tbl, col, src_pk, seq, data) VALUES ('history', 'data', 0, %s, decode('%s', 'base64'));" % (seq, base64.b64encode(chunk).decode('ascii')))
			offset += len(chunk)
			seq += 1
			if offset >= len(data):
				break
		writer.stmt('stage history', 'INSERT INTO pg_temp._s_history (_src_pk, data) VALUES (0, NULL);')

	#--------------------------------------------------------
	def _format_table_history(self, curs, spec, log_table:str) -> list:
		cols = _run_sql_query(curs, _SQL_get_columns, {'tbl': log_table})
		data_cols = [ (c[0], c[3]) for c in cols if c[0] not in _AUDIT_LOG_META_COLS and c[0] in spec.cols ]
		if spec.pk not in [ c[0] for c in data_cols ]:
			return []
		select = []
		for name, is_bytea in data_cols:
			if is_bytea:
				select.append("CASE WHEN l.%(c)s IS NULL THEN NULL ELSE '<' || octet_length(l.%(c)s) || ' bytes, md5 ' || md5(l.%(c)s) || '>' END" % {'c': _quote_identifier(name)})
			else:
				select.append('l.%s::text' % _quote_identifier(name))
		# log tables carry the columns of the audited table, so the
		# patient filter also finds versions of since deleted rows
		sql = """SELECT l.row_version, l.version_created_when::text, l.version_created_by::text, l.version_logged_when::text, l.version_logged_by::text, l.version_logged_why, %s
			FROM %s l
			WHERE l.src_table_oid = %%(tbl)s::regclass
				AND (l.src_row_pk_audit = ANY(%%(audits)s::int[]) OR (%s))
			ORDER BY l.%s, l.row_version, l.version_logged_when""" % (
				', '.join(select),
				log_table,
				_expand_where(spec.where),
				_quote_identifier(spec.pk)
			)
		args = self._query_args()
		args['tbl'] = spec.table
		args['audits'] = self.pk_audits.get(spec.table, [])
		log_rows = _run_sql_query(curs, sql, args)
		if not log_rows:
			return []
		names = [ c[0] for c in data_cols ]
		pk_idx = names.index(spec.pk)
		# current values of the rows having history
		row_pks = sorted({ r[6 + pk_idx] for r in log_rows }, key = lambda pk: int(pk) if str(pk).isdigit() else 0)
		cur_select = []
		for name, is_bytea in data_cols:
			if is_bytea:
				cur_select.append("CASE WHEN t.%(c)s IS NULL THEN NULL ELSE '<' || octet_length(t.%(c)s) || ' bytes, md5 ' || md5(t.%(c)s) || '>' END" % {'c': _quote_identifier(name)})
			else:
				cur_select.append('t.%s::text' % _quote_identifier(name))
		current = {}
		for row in _run_sql_query(curs, 'SELECT %s FROM %s t WHERE t.%s::text = ANY(%%(pks)s::text[])' % (', '.join(cur_select), _quote_qual_table(spec.table), _quote_identifier(spec.pk)), {'pks': row_pks}):
			current[row[pk_idx]] = list(row)
		lines = ['', '=== %s ===' % spec.table]
		by_row = {}
		for r in log_rows:
			by_row.setdefault(r[6 + pk_idx], []).append(r)
		for row_pk in row_pks:
			versions = by_row[row_pk]
			state = _('present') if row_pk in current else _('deleted')
			lines.append('--- %s #%s (%s) ---' % (spec.name, row_pk, state))
			for idx, version in enumerate(versions):
				values = list(version[6:])
				if idx + 1 < len(versions):
					next_values = list(versions[idx + 1][6:])
				else:
					next_values = current.get(row_pk)
				lines.append('  v%s %s %s %s, %s %s %s (%s)' % (
					version[0],
					_('created'), version[1], version[2],
					_('replaced'), version[3], version[4],
					version[5]
				))
				if next_values is None:
					# deleted: show last values
					for name, val in zip(names, values):
						if val is not None:
							lines.append('      %s: %s' % (name, val))
					continue
				for name, old, new in zip(names, values, next_values):
					if old != new:
						lines.append('      %s: %s -> %s' % (name, _repr_hist(old), _repr_hist(new)))
		return lines

	#--------------------------------------------------------
	def _assemble(self, filename:str, section1:str, section2_name:str):
		self.meta = {
			'format': SCRIPT_FORMAT_VERSION,
			'schema_version': SCHEMA_VERSION,
			'schema_hash': self.schema_hash,
			'export_uuid': self.export_uuid,
			'exported_when': pydt.datetime.now(tz = pydt.timezone.utc).astimezone().isoformat(),
			'source_id': self.source_id,
			'source': self.source_description,
			'source_pk': self.pk_identity,
			'source_timezone': self.src_timezone,
			'counts': self.counts,
			'reference_rows': self.ref_rows,
			'staff': len(self.staff_rows),
			'history_included': self.history_sha256 is not None,
			'history_note': self.history_note
		}
		tmp_fd, tmp_name = tempfile.mkstemp(prefix = 'gm-transplant-', suffix = '.tmp', dir = os.path.dirname(filename))
		try:
			with os.fdopen(tmp_fd, 'wt', encoding = 'utf8', newline = '\n') as script:
				writer = _cStatementWriter(script)
				self._write_head(writer)
				writer.raw('%s\n' % MARKER_DATA_BEGIN)
				writer.start_hashing()
				self._write_body_start(writer)
				writer.raw(section1)
				self._write_detection(writer)
				with open(section2_name, 'rt', encoding = 'utf8', newline = '\n') as section2:
					for line in section2:
						writer.raw(line)
				self._write_loader(writer)
				digest = writer.hexdigest
				script.write('%s %s\n' % (MARKER_SHA256, digest))
			os.chmod(tmp_name, 0o600)
			os.replace(tmp_name, filename)
		finally:
			if os.path.exists(tmp_name):
				os.remove(tmp_name)

	#--------------------------------------------------------
	def _write_head(self, w):
		w.comment(_SCRIPT_HEADER % {
			'source': self.source_description,
			'source_pk': self.pk_identity,
			'uuid': self.export_uuid,
			'when': self.meta['exported_when'],
			'n_rows': sum(self.counts.values())
		})
		w.raw('%s %s\n' % (MARKER_META, json.dumps(self.meta, sort_keys = True)))
		w.raw('\n')
		w.stmt('settings', "SET client_encoding TO 'UTF8';")
		w.stmt('begin', 'BEGIN READ WRITE;')
		w.stmt('config-table', 'CREATE TEMP TABLE _gm_tp_cfg (key text PRIMARY KEY, value text) ON COMMIT DROP;')
		w.stmt('config-table', 'CREATE TEMP TABLE _gm_tp_staff_map (src_alias text, src_db_user text, src_name text, target_alias text) ON COMMIT DROP;')
		# the editable configuration block is one single "statement" for the client runner
		cfg = io.StringIO()
		cfg.write('%s (darf per Texteditor geaendert werden / may be edited) =================\n' % MARKER_CFG_BEGIN)
		cfg.write(_CONFIG_BLOCK_HELP)
		cfg.write("INSERT INTO pg_temp._gm_tp_cfg VALUES ('staff_match', 'strict');\n")
		cfg.write('%s\n' % _CFG_HELP_SAME_PATIENT)
		cfg.write("INSERT INTO pg_temp._gm_tp_cfg VALUES ('same_patient_as', NULL);\n")
		cfg.write('%s\n' % _CFG_HELP_PATIENT_MODE)
		cfg.write("INSERT INTO pg_temp._gm_tp_cfg VALUES ('patient_mode', 'detect');\n")
		cfg.write('%s\n' % _CFG_HELP_FORCE)
		cfg.write("INSERT INTO pg_temp._gm_tp_cfg VALUES ('force', 'false');\n")
		cfg.write('%s\n' % _CFG_HELP_DRY_RUN)
		cfg.write("INSERT INTO pg_temp._gm_tp_cfg VALUES ('dry_run', 'false');\n")
		cfg.write('%s\n' % _CFG_HELP_FALLBACK)
		cfg.write("INSERT INTO pg_temp._gm_tp_cfg VALUES ('fallback_staff', NULL);\n")
		cfg.write('%s\n' % _CFG_HELP_STAFF_MAP)
		if self.staff_rows:
			cfg.write('INSERT INTO pg_temp._gm_tp_staff_map (src_alias, src_db_user, src_name, target_alias) VALUES\n')
			rendered = []
			for pk, alias, db_user, lastnames, firstnames, dob in self.staff_rows:
				name = ', '.join([ x for x in [lastnames, firstnames] if x ])
				rendered.append('(%s, %s, %s, NULL)' % (sql_literal(alias), sql_literal(db_user), sql_literal(name)))
			cfg.write('\t  %s\n;\n' % '\n\t, '.join(rendered))
		else:
			cfg.write('-- (no staff referenced / kein Personal referenziert)\n')
		cfg.write('%s =================' % MARKER_CFG_END)
		w.stmt('config', cfg.getvalue())

	#--------------------------------------------------------
	def _meta_rows(self) -> dict:
		tag = '[transplant %s]' % self.export_uuid[:8]
		meta = {
			'export_uuid': self.export_uuid,
			'exported_when': self.meta['exported_when'],
			'source_id': self.source_id,
			'source_desc': self.source_description,
			'source_pk': str(self.pk_identity),
			'schema_hash': self.schema_hash,
			'source_timezone': self.src_timezone,
			'provenance': '%s::pk::%s' % (self.source_id, self.pk_identity),
			'tag': tag,
			'relatives': self.relatives_note,
			'history_sha256': self.history_sha256,
			'history_note': self.history_note,
			'txt_err_applied': _('[gm_transplant] This export has already been imported (see DETAIL for the identities). Set force to import again, no rows will be duplicated.'),
			'txt_err_candidates': _('[gm_transplant] The patient may already exist in this database (see DETAIL for candidates). Set patient mode to "new" or set same_patient_as to one of the candidates.'),
			'txt_err_schema': _('[gm_transplant] Database schema does not match the schema of the source database.'),
			'txt_err_config': _('[gm_transplant] Invalid configuration'),
			'txt_err_staff': _('[gm_transplant] Staff problem'),
			'txt_err_no_fallback': _('[gm_transplant] Staff member cannot be mapped and there is no fallback staff member (set fallback_staff).'),
			'txt_err_reference': _('[gm_transplant] Required reference data missing in target database'),
			'txt_err_verify': _('[gm_transplant] Verification failed, nothing was imported'),
			'txt_dry_run_ok': _('[gm_transplant] Dry run successful, nothing was imported (see DETAIL for a summary).'),
			'txt_episode': _('GNUmed transplant'),
			'txt_rfe': _('patient data transplanted from another GNUmed database'),
			'txt_protocol_title': _('GNUmed transplant protocol'),
			'txt_history_title': _('GNUmed audit history (source database)'),
			'txt_orig_staff': _('orig.'),
			'txt_admin_note': _('Patient data transplanted from "{source}" (source patient #{source_pk}, export {export_uuid} of {exported_when}), patient mode: {patient_mode}. Details: documents "GNUmed transplant protocol" and "GNUmed audit history".'),
			'txt_relatives': _('Relatives in the source database'),
			'txt_source': _('Source'),
			'txt_source_patient': _('Source patient'),
			'txt_export': _('Export'),
			'txt_import': _('Import'),
			'txt_mode': _('Mode / target patient'),
			'txt_config': _('Configuration'),
			'txt_staff_mapping': _('Staff mapping (source -> target)'),
			'txt_refs': _('Reference data (looked up / created)'),
			'txt_skipped': _('Rows not imported'),
			'txt_rows': _('Rows (table | source -> target | status | originally modified by @ when)')
		}
		return meta

	#--------------------------------------------------------
	def _write_body_start(self, w):
		w.stmt('settings', "SET LOCAL TimeZone TO '%s';" % self.src_timezone.replace("'", "''"))
		w.stmt('settings', "SET LOCAL DateStyle TO 'ISO, YMD';")
		w.stmt('settings', "SET LOCAL IntervalStyle TO 'iso_8601';")
		w.stmt('settings', 'SET LOCAL statement_timeout TO 0;')
		w.stmt('settings', 'SET LOCAL lock_timeout TO 0;')
		w.stmt('settings', 'SET LOCAL idle_in_transaction_session_timeout TO 0;')
		for sql in _SQL_STATIC_DDL:
			w.stmt('ddl', sql)
		for spec in _TABLE_SPECS:
			w.stmt('ddl', self._staging_ddl(spec))
		for spec in _REF_SPECS:
			w.stmt('ddl', self._ref_staging_ddl(spec))
		rows = []
		for ord_idx, spec in enumerate(_TABLE_SPECS):
			rows.append('(%s, %s, %s)' % (sql_literal(spec.table), sql_literal(spec.pk), ord_idx))
		w.stmt('ddl', 'INSERT INTO pg_temp._gm_tp_tables (tbl, pk_col, ord) VALUES\n\t  %s;' % '\n\t, '.join(rows))
		w.stmt('ddl', gmPG2.SQL__pg_temp_concat_table_structure_v19_and_up)
		for sql in _SQL_FUNCTIONS:
			w.stmt('ddl', sql)
		w.stmt('ddl', self._protocol_function())
		meta_rows = [ '(%s, %s)' % (sql_literal(key), sql_literal(val)) for key, val in self._meta_rows().items() ]
		w.stmt('meta', 'INSERT INTO pg_temp._gm_tp_meta (key, value) VALUES\n\t  %s;' % '\n\t, '.join(meta_rows))
		w.stmt('preflight', _SQL_PREFLIGHT)
		if self.staff_rows:
			rows = []
			for pk, alias, db_user, lastnames, firstnames, dob in self.staff_rows:
				rows.append('(%s, %s, %s, %s, %s, %s)' % (pk, sql_literal(alias), sql_literal(db_user), sql_literal(lastnames), sql_literal(firstnames), sql_literal(dob)))
			w.stmt('stage staff', 'INSERT INTO pg_temp._s_staff (_src_pk, short_alias, db_user, lastnames, firstnames, dob) VALUES\n\t  %s;' % '\n\t, '.join(rows))

	#--------------------------------------------------------
	def _staging_ddl(self, spec) -> str:
		cols = ['_src_pk integer PRIMARY KEY']
		for col in spec.staged_cols:
			cols.append('%s %s' % (_quote_identifier(col), spec.col_types[col]))
		for name, (sqltype, expr, kind) in spec.extra.items():
			cols.append('%s %s' % (_quote_identifier(name), sqltype))
		if spec.has_audit:
			cols.append('_x_modified_by text')
			cols.append('_x_modified_when timestamp with time zone')
		return 'CREATE TEMP TABLE _s_%s__%s (\n\t%s\n) ON COMMIT DROP;' % (spec.schema, spec.name, ',\n\t'.join(cols))

	#--------------------------------------------------------
	def _ref_staging_ddl(self, spec) -> str:
		if spec.keep:
			cols = ['_src_key text PRIMARY KEY']
		else:
			cols = ['_src_pk integer PRIMARY KEY']
		for col in spec.staged_cols:
			cols.append('%s %s' % (_quote_identifier(col), spec.col_types[col]))
		for name, (sqltype, expr) in spec.extra.items():
			cols.append('%s %s' % (_quote_identifier(name), sqltype))
		return 'CREATE TEMP TABLE _s_ref__%s__%s (\n\t%s\n) ON COMMIT DROP;' % (spec.schema, spec.name, ',\n\t'.join(cols))

	#--------------------------------------------------------
	def _write_detection(self, w):
		w.stmt('detect', _SQL_DETECT)
		w.stmt('staff', _SQL_RESOLVE_STAFF)

	#--------------------------------------------------------
	def _write_loader(self, w):
		# assemble blobs
		for spec in _TABLE_SPECS:
			for col in spec.bytea_cols:
				w.stmt('blobs', "SELECT pg_temp._tp_assemble_blobs('%s', '%s', '%s');" % (spec.staging, spec.table, col))
		for spec in _REF_SPECS:
			for col in spec.bytea_cols:
				map_key = spec.map_name if spec.map_name != 'ref:code' else 'ref:%s' % spec.table
				w.stmt('blobs', "SELECT pg_temp._tp_assemble_blobs('%s', '%s', '%s');" % (spec.staging, map_key, col))
		w.stmt('blobs', "SELECT pg_temp._tp_assemble_blobs('pg_temp._s_history', 'history', 'data');")
		w.stmt('map', _SQL_LOAD_PERSISTENT_MAP)
		for spec in _REF_SPECS:
			for sql in _ref_loader_sql(spec):
				w.stmt('ref %s' % spec.table, sql)
		for spec in _TABLE_SPECS:
			for sql in _table_loader_sql(spec):
				w.stmt('load %s' % spec.table, sql)
		for sql in _SQL_FIXUPS:
			w.stmt('fixup', sql)
		w.stmt('admin', _SQL_ADMIN_DOCUMENTS)
		w.stmt('persist', _SQL_PERSIST)
		w.stmt('verify', _verification_sql())
		w.stmt('result', 'SELECT pg_temp._tp_summary()::text AS gm_transplant_result;')
		for func in _TEMP_FUNCTIONS:
			w.stmt('cleanup', 'DROP FUNCTION IF EXISTS pg_temp.%s;' % func)
		w.stmt('commit', 'COMMIT;')

	#--------------------------------------------------------
	def _protocol_function(self) -> str:
		origins = []
		for spec in _TABLE_SPECS:
			if spec.has_audit:
				origins.append("SELECT '%s'::text AS tbl, s._src_pk AS src_pk, s._x_modified_by AS mod_by, s._x_modified_when AS mod_when FROM %s s" % (spec.table, spec.staging))
			else:
				origins.append("SELECT '%s'::text AS tbl, s._src_pk AS src_pk, NULL::text AS mod_by, NULL::timestamptz AS mod_when FROM %s s" % (spec.table, spec.staging))
		return _SQL_PROTOCOL_FUNCTION.replace('@ORIGINS@', '\n\t\t\tUNION ALL\n\t\t\t'.join(origins))

#------------------------------------------------------------
def _repr_hist(value) -> str:
	if value is None:
		return 'NULL'

	value = str(value)
	if '\n' in value or len(value) > 200:
		return repr(value)

	return value


#============================================================
# loader SQL generation
#------------------------------------------------------------
def _insert_expr(spec, col:str) -> str:
	if col in spec.overrides:
		return spec.overrides[col]
	fk = spec.fks.get(col)
	if fk is None:
		return 's.%s' % _quote_identifier(col)
	kind = fk[0]
	if kind == 'int':
		return "pg_temp._tp_m('%s', s.%s)" % (fk[1], _quote_identifier(col))
	if kind == 'soft':
		return "pg_temp._tp_mo('%s', s.%s)" % (fk[1], _quote_identifier(col))
	if kind == 'staff':
		return 'pg_temp._tp_s(s.%s)' % _quote_identifier(col)
	if kind == 'ref':
		return "pg_temp._tp_r('%s', s.%s)" % (fk[1], _quote_identifier(col))
	if kind == 'code':
		return "pg_temp._tp_r('code', s.%s)" % _quote_identifier(col)
	if kind == 'keep':
		return 's.%s' % _quote_identifier(col)
	raise ValueError('cannot insert column [%s.%s] of kind [%s]' % (spec.table, col, kind))

#------------------------------------------------------------
def _table_loader_sql(spec) -> list:
	"""Generate the statements loading one patient table from staging.

	Steps:
		1) rows whose parent rows are not available are skipped
		2) for the remaining rows not yet mapped (by an earlier
		   transplant), find matching existing target rows,
		   collapse duplicates, apply skip conditions
		3) allocate new primary keys
		4) insert
	"""
	tbl = spec.table
	stg = spec.staging
	not_mapped = "NOT EXISTS (SELECT 1 FROM pg_temp._gm_tp_map m WHERE m.tbl = '%s' AND m.src_pk = s._src_pk)" % tbl
	orphan_parts = [
		"(s.%s IS NOT NULL AND pg_temp._tp_mo('%s', s.%s) IS NULL)" % (_quote_identifier(col), fk[1], _quote_identifier(col))
		for col, fk in spec.fks.items() if fk[0] == 'int'
	]
	stmts = []
	if orphan_parts:
		stmts.append("""INSERT INTO pg_temp._gm_tp_map (tbl, src_pk, new_pk, status, note)
SELECT '%s', s._src_pk, NULL, 'skipped', 'parent row not available in target'
FROM %s s
WHERE %s AND (%s);""" % (tbl, stg, not_mapped, ' OR '.join(orphan_parts)))
	match = spec.match or 'NULL::integer'
	if spec.dedupe:
		leader = 'first_value(s._src_pk) OVER (PARTITION BY %s ORDER BY s._src_pk)' % ', '.join(spec.dedupe)
	else:
		leader = 's._src_pk'
	skip = '(%s)' % spec.skip_if if spec.skip_if else 'false'
	stmts.append("""CREATE TEMP TABLE _gm_tp_alloc ON COMMIT DROP AS
SELECT x._src_pk, x._match, x._leader, (x._match IS NULL AND coalesce(x._skip, false)) AS _skip
FROM (
	SELECT s._src_pk, %s AS _match, %s AS _leader, %s AS _skip
	FROM %s s
	WHERE %s
) x;""" % (match, leader, skip, stg, not_mapped))
	if spec.skip_if:
		stmts.append("""INSERT INTO pg_temp._gm_tp_map (tbl, src_pk, new_pk, status, note)
SELECT '%s', a._src_pk, NULL, 'skipped', %s FROM pg_temp._gm_tp_alloc a WHERE a._skip;""" % (tbl, sql_literal(spec.skip_reason)))
	stmts.append("""INSERT INTO pg_temp._gm_tp_map (tbl, src_pk, new_pk, status, note)
SELECT '%s', a._src_pk, coalesce(a._match, nextval('%s'::regclass)), CASE WHEN a._match IS NULL THEN 'new' ELSE 'merged' END, CASE WHEN a._match IS NULL THEN NULL ELSE 'matched existing row' END
FROM pg_temp._gm_tp_alloc a
WHERE NOT a._skip AND a._leader = a._src_pk
ORDER BY a._src_pk;""" % (tbl, spec.sequence))
	if spec.dedupe:
		stmts.append("""INSERT INTO pg_temp._gm_tp_map (tbl, src_pk, new_pk, status, note)
SELECT '%s', a._src_pk, l.new_pk, 'merged', 'duplicate of source row #' || a._leader
FROM pg_temp._gm_tp_alloc a
	JOIN pg_temp._gm_tp_map l ON (l.tbl = '%s' AND l.src_pk = a._leader AND l.status IN ('new', 'merged'))
WHERE NOT a._skip AND a._leader <> a._src_pk;""" % (tbl, tbl))
		stmts.append("""INSERT INTO pg_temp._gm_tp_map (tbl, src_pk, new_pk, status, note)
SELECT '%s', a._src_pk, NULL, 'skipped', 'duplicate of skipped source row #' || a._leader
FROM pg_temp._gm_tp_alloc a
WHERE NOT EXISTS (SELECT 1 FROM pg_temp._gm_tp_map m WHERE m.tbl = '%s' AND m.src_pk = a._src_pk);""" % (tbl, tbl))
	stmts.append('DROP TABLE pg_temp._gm_tp_alloc;')
	stmts.extend(spec.pre_insert)
	if spec.custom_insert:
		stmts.append(_SQL_INSERT_NAMES)
	else:
		cols = [spec.pk] + spec.insert_cols
		exprs = ['m.new_pk'] + [ _insert_expr(spec, c) for c in spec.insert_cols ]
		stmts.append("""INSERT INTO %s (%s) %s
SELECT %s
FROM %s s
	JOIN pg_temp._gm_tp_map m ON (m.tbl = '%s' AND m.src_pk = s._src_pk AND m.status = 'new')
ORDER BY s._src_pk;""" % (
			_quote_qual_table(tbl),
			', '.join([ _quote_identifier(c) for c in cols ]),
			'OVERRIDING SYSTEM VALUE' if spec.pk_is_identity else '',
			',\n\t'.join(exprs),
			stg,
			tbl
		))
	stmts.extend(spec.post_insert)
	if spec.lenient:
		stmts.append("""UPDATE pg_temp._gm_tp_map m SET status = 'dropped', note = 'suppressed by a trigger of the target database'
WHERE m.tbl = '%s' AND m.status = 'new' AND NOT EXISTS (SELECT 1 FROM %s t WHERE t.%s = m.new_pk);""" % (tbl, _quote_qual_table(tbl), _quote_identifier(spec.pk)))
	return stmts

#------------------------------------------------------------
def _ref_loader_sql(spec) -> list:
	"""Generate the statements resolving one reference table."""
	stg = spec.staging
	stmts = []
	cols = spec.staged_cols
	if spec.keep:
		# the natural key value itself is referenced: just make sure it exists
		nk = ' OR '.join([ '(%s)' % c for c in spec.nks ])
		stmts.append("""INSERT INTO pg_temp._gm_tp_keep_log (tbl, key)
SELECT '%s', s._src_key FROM %s s WHERE NOT EXISTS (SELECT 1 FROM %s t WHERE %s);""" % (spec.table, stg, _quote_qual_table(spec.table), nk))
		stmts.append("""INSERT INTO %s (%s)
SELECT %s FROM %s s WHERE NOT EXISTS (SELECT 1 FROM %s t WHERE %s);""" % (
			_quote_qual_table(spec.table),
			', '.join([ _quote_identifier(c) for c in cols ]),
			', '.join([ _ref_insert_expr(spec, c) for c in cols ]),
			stg,
			_quote_qual_table(spec.table),
			nk
		))
		return stmts

	map_name = spec.map_name
	not_mapped = "NOT EXISTS (SELECT 1 FROM pg_temp._gm_tp_map m WHERE m.tbl = '%s' AND m.src_pk = s._src_pk)" % map_name
	if spec.nks:
		lookups = [
			'(SELECT t.%s FROM %s t WHERE %s ORDER BY t.%s LIMIT 1)' % (_quote_identifier(spec.map_col), _quote_qual_table(spec.table), nk, _quote_identifier(spec.map_col))
			for nk in spec.nks
		]
		lookup = lookups[0] if len(lookups) == 1 else 'coalesce(%s)' % ', '.join(lookups)
		stmts.append("""INSERT INTO pg_temp._gm_tp_map (tbl, src_pk, new_pk, status, note)
SELECT '%s', x._src_pk, x._found, 'ref_found', NULL
FROM (SELECT s._src_pk, %s AS _found FROM %s s WHERE %s) x
WHERE x._found IS NOT NULL;""" % (map_name, lookup, stg, not_mapped))
	for col, (req_table, req_col) in spec.require.items():
		stmts.append("""DO $tp$
BEGIN
	IF EXISTS (SELECT 1 FROM %s s WHERE %s AND s.%s IS NOT NULL AND NOT EXISTS (SELECT 1 FROM %s r WHERE r.%s = s.%s)) THEN
		RAISE EXCEPTION USING ERRCODE = '%s', MESSAGE = pg_temp._tp_meta('txt_err_reference'), DETAIL = '%s.%s';
	END IF;
END;
$tp$;""" % (stg, not_mapped, _quote_identifier(col), _quote_qual_table(req_table), _quote_identifier(req_col), _quote_identifier(col), SQLSTATE_MISSING_REFERENCE, req_table, req_col))
	create_if = '(%s)' % spec.create_if if spec.create_if else 'true'
	stmts.append("""INSERT INTO pg_temp._gm_tp_map (tbl, src_pk, new_pk, status, note)
SELECT '%s', s._src_pk, nextval('%s'::regclass), 'ref_created', '%s'
FROM %s s
WHERE %s AND %s
ORDER BY s._src_pk;""" % (map_name, spec.sequence, spec.table, stg, not_mapped, create_if))
	insert_cols = [spec.map_col] + cols
	overriding = 'OVERRIDING SYSTEM VALUE' if spec.map_col in spec.identity_cols else ''
	stmts.append("""INSERT INTO %s (%s) %s
SELECT m.new_pk, %s
FROM %s s
	JOIN pg_temp._gm_tp_map m ON (m.tbl = '%s' AND m.src_pk = s._src_pk AND m.status = 'ref_created' AND m.note = '%s')
ORDER BY s._src_pk;""" % (
		_quote_qual_table(spec.table),
		', '.join([ _quote_identifier(c) for c in insert_cols ]),
		overriding,
		', '.join([ _ref_insert_expr(spec, c) for c in cols ]),
		stg,
		map_name,
		spec.table
	))
	return stmts

#------------------------------------------------------------
def _ref_insert_expr(spec, col:str) -> str:
	fk = spec.fks.get(col)
	if fk is None or fk[0] == 'keep':
		return 's.%s' % _quote_identifier(col)
	if fk[0] == 'ref':
		return "pg_temp._tp_r('%s', s.%s)" % (fk[1], _quote_identifier(col))
	raise ValueError('cannot insert reference column [%s.%s] of kind [%s]' % (spec.table, col, fk[0]))

#------------------------------------------------------------
def _verification_sql() -> str:
	missing = []
	lost = []
	for spec in _TABLE_SPECS:
		missing.append("SELECT '%s'::text AS tbl, count(1) AS n FROM %s s WHERE NOT EXISTS (SELECT 1 FROM pg_temp._gm_tp_map m WHERE m.tbl = '%s' AND m.src_pk = s._src_pk)" % (spec.table, spec.staging, spec.table))
		lost.append("SELECT '%s'::text AS tbl, count(1) AS n FROM pg_temp._gm_tp_map m WHERE m.tbl = '%s' AND m.status = 'new' AND NOT EXISTS (SELECT 1 FROM %s t WHERE t.%s = m.new_pk)" % (spec.table, spec.table, _quote_qual_table(spec.table), _quote_identifier
		(spec.pk)))
	return _SQL_VERIFY.replace('@MISSING@', '\n\t\tUNION ALL '.join(missing)).replace('@LOST@', '\n\t\tUNION ALL '.join(lost))

#============================================================
# static SQL of the script
#------------------------------------------------------------
_SCRIPT_HEADER = """======================================================================
GNUmed patient transplant script
======================================================================

source        : %(source)s
patient       : #%(source_pk)s
export        : %(uuid)s (%(when)s)
rows          : %(n_rows)s

CONTAINS PATIENT DATA - handle confidentially !!!

usage:

  psql -v ON_ERROR_STOP=1 -U gm-dbo -d <gnumed_v23> -f <this file>

  or GNUmed: Person -> Import -> GNUmed transplant script

The script runs as ONE transaction: everything is imported or
nothing. If the patient seems to exist already the script aborts
with SQLSTATE GMTP1_PATIENT_CANDIDATES_EXIST listing candidates. Then edit the
CONFIGURATION block below: either same_patient_as = <pk> (add
data to that patient) or patient_mode = 'new' (create new patient).

Settings may also be passed in from outside, overriding the block:

  PGOPTIONS='-c gm_transplant.patient_mode=new' psql ...

Do not edit anything below the line "%(data_begin)s":
that part is protected by a SHA-256 checksum.
==========================================================================""".replace('%(data_begin)s', MARKER_DATA_BEGIN)

_CONFIG_BLOCK_HELP = """--
-- Staff matching: 'strict' = alias or database account AND name (and DOB, if known)
-- must match; 'lenient' = alias or database account suffices.
"""
_CFG_HELP_SAME_PATIENT = """--
-- Same patient as target patient #...: NULL = detect, else the pk, say, '4711'.
-- The data will then be added to that patient."""
_CFG_HELP_PATIENT_MODE = """--
-- patient_mode: 'detect' | 'new' | 'add'  (same_patient_as set => 'add')"""
_CFG_HELP_FORCE = """--
-- Allow re-applying this export (NO rows will be duplicated)."""
_CFG_HELP_DRY_RUN = """--
-- Dry run: check all, then roll back."""
_CFG_HELP_FALLBACK = """--
-- Fallback staff member (alias) for unmappable staff; NULL = staff member of the
-- session account. Set this when importing as gm-dbo!"""
_CFG_HELP_STAFF_MAP = """--
-- Staff mapping old -> new: put the target alias into the last column,
-- NULL = automatic (see staff_match).
--   (src_alias, src_db_user, src_name, target_alias)"""

#------------------------------------------------------------
_SQL_STATIC_DDL = [
	'CREATE TEMP TABLE _gm_tp_meta (key text PRIMARY KEY, value text) ON COMMIT DROP;',
	'CREATE TEMP TABLE _gm_tp_state (key text PRIMARY KEY, value text) ON COMMIT DROP;',
	'CREATE TEMP TABLE _gm_tp_map (tbl text NOT NULL, src_pk integer NOT NULL, new_pk integer, status text NOT NULL, note text, PRIMARY KEY (tbl, src_pk)) ON COMMIT DROP;',
	'CREATE TEMP TABLE _gm_tp_tables (tbl text PRIMARY KEY, pk_col text NOT NULL, ord integer NOT NULL) ON COMMIT DROP;',
	'CREATE TEMP TABLE _gm_tp_keep_log (tbl text NOT NULL, key text NOT NULL) ON COMMIT DROP;',
	'CREATE TEMP TABLE _s_blob_chunk (tbl text NOT NULL, col text NOT NULL, src_pk integer NOT NULL, seq integer NOT NULL, data bytea NOT NULL) ON COMMIT DROP;',
	'CREATE TEMP TABLE _s_staff (_src_pk integer PRIMARY KEY, short_alias text, db_user text, lastnames text, firstnames text, dob timestamp with time zone) ON COMMIT DROP;',
	'CREATE TEMP TABLE _s_history (_src_pk integer PRIMARY KEY, data bytea) ON COMMIT DROP;'
]

_TEMP_FUNCTIONS = [
	'concat_table_structure_v19_and_up()',
	'_tp_cfg(text)',
	'_tp_cfg_bool(text)',
	'_tp_meta(text)',
	'_tp_state(text)',
	'_tp_set_state(text, text)',
	'_tp_mo(text, integer)',
	'_tp_m(text, integer)',
	'_tp_r(text, integer)',
	'_tp_s(integer)',
	'_tp_staff_note(text, integer)',
	'_tp_target()',
	'_tp_add_target()',
	'_tp_identity_comment(text)',
	'_tp_suffix(integer)',
	'_tp_set_dob_tz(timestamp with time zone)',
	'_tp_reset_tz()',
	'_tp_assemble_blobs(text, text, text)',
	'_tp_doc_type(text, text)',
	'_tp_admin_note()',
	'_tp_protocol()',
	'_tp_summary()'
]

_SQL_FUNCTIONS = [
"""CREATE FUNCTION pg_temp._tp_cfg(_p_key text) RETURNS text LANGUAGE sql STABLE AS $tp$
	SELECT coalesce (
		nullif(current_setting('gm_transplant.' || _p_key, true), ''),
		(SELECT c.value FROM pg_temp._gm_tp_cfg c WHERE c.key = _p_key)
	)
$tp$;""",

"""CREATE FUNCTION pg_temp._tp_cfg_bool(_p_key text) RETURNS boolean LANGUAGE sql STABLE AS $tp$
	SELECT coalesce(lower(trim(pg_temp._tp_cfg(_p_key))) IN ('true', 't', 'yes', 'y', 'on', '1'), false)
$tp$;""",

"""CREATE FUNCTION pg_temp._tp_meta(_p_key text) RETURNS text LANGUAGE sql STABLE AS $tp$
	SELECT m.value FROM pg_temp._gm_tp_meta m WHERE m.key = _p_key
$tp$;""",

"""CREATE FUNCTION pg_temp._tp_state(_p_key text) RETURNS text LANGUAGE sql STABLE AS $tp$
	SELECT s.value FROM pg_temp._gm_tp_state s WHERE s.key = _p_key
$tp$;""",

"""CREATE FUNCTION pg_temp._tp_set_state(_p_key text, _p_value text) RETURNS void LANGUAGE sql AS $tp$
	INSERT INTO pg_temp._gm_tp_state (key, value) VALUES (_p_key, _p_value)
	ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
$tp$;""",

"""CREATE FUNCTION pg_temp._tp_mo(_p_tbl text, _p_src integer) RETURNS integer LANGUAGE sql STABLE AS $tp$
	SELECT m.new_pk FROM pg_temp._gm_tp_map m
	WHERE
		m.tbl = _p_tbl
			AND
		m.src_pk = _p_src
			AND
		m.status IN ('new', 'merged', 'existing', 'ref_found', 'ref_created')
$tp$;""",

"""CREATE FUNCTION pg_temp._tp_m(_p_tbl text, _p_src integer) RETURNS integer LANGUAGE plpgsql STABLE AS $tp$
DECLARE
	_v_new integer;
BEGIN
	IF _p_src IS NULL THEN
		RETURN NULL;
	END IF;
	_v_new := pg_temp._tp_mo(_p_tbl, _p_src);
	IF _v_new IS NULL THEN
		RAISE EXCEPTION USING
			ERRCODE = '%(GMTP9)s',
			MESSAGE = pg_temp._tp_meta('txt_err_verify'),
			DETAIL = format('no target row for %%s #%%s', _p_tbl, _p_src);
	END IF;
	RETURN _v_new;
END;
$tp$;""" % {'GMTP9': SQLSTATE_VERIFICATION},

"""CREATE FUNCTION pg_temp._tp_r(_p_tbl text, _p_src integer) RETURNS integer LANGUAGE sql STABLE AS $tp$
	SELECT pg_temp._tp_m('ref:' || _p_tbl, _p_src)
$tp$;""",

"""CREATE FUNCTION pg_temp._tp_s(_p_src integer) RETURNS integer LANGUAGE sql STABLE AS $tp$
	SELECT pg_temp._tp_m('staff', _p_src)
$tp$;""",

"""CREATE FUNCTION pg_temp._tp_staff_note(_p_comment text, _p_src integer) RETURNS text LANGUAGE sql STABLE AS $tp$
	SELECT CASE
		WHEN _p_src IS NULL THEN _p_comment
		WHEN (SELECT m.note FROM pg_temp._gm_tp_map m WHERE m.tbl = 'staff' AND m.src_pk = _p_src) = 'fallback' THEN
			concat_ws (
				' ',
				nullif(_p_comment, ''),
				'[' || pg_temp._tp_meta('txt_orig_staff') || ': ' || (SELECT coalesce(st.short_alias, st.db_user, '#' || st._src_pk) FROM pg_temp._s_staff st WHERE st._src_pk = _p_src) || ']'
			)
		ELSE _p_comment
	END
$tp$;""",

"""CREATE FUNCTION pg_temp._tp_target() RETURNS integer LANGUAGE sql STABLE AS $tp$
	SELECT m.new_pk FROM pg_temp._gm_tp_map m
	WHERE m.tbl = 'dem.identity' AND m.status IN ('new', 'merged', 'existing')
	ORDER BY m.src_pk
	LIMIT 1
$tp$;""",

"""CREATE FUNCTION pg_temp._tp_add_target() RETURNS integer LANGUAGE sql STABLE AS $tp$
	SELECT CASE WHEN pg_temp._tp_state('patient_mode') = 'add' THEN pg_temp._tp_state('target')::integer ELSE NULL END
$tp$;""",

"""CREATE FUNCTION pg_temp._tp_identity_comment(_p_comment text) RETURNS text LANGUAGE sql STABLE AS $tp$
	SELECT CASE
		WHEN pg_temp._tp_state('tag_identity_comment') = 'true' THEN concat_ws(' ', nullif(_p_comment, ''), pg_temp._tp_meta('tag'))
		ELSE _p_comment
	END
$tp$;""",

"""CREATE FUNCTION pg_temp._tp_set_dob_tz(_p_dob timestamp with time zone) RETURNS void LANGUAGE plpgsql AS $tp$
DECLARE
	_v_offset integer;
BEGIN
	-- dem.identity.dob is re-normalized to 11:11:11.111 in the session time zone on
	-- every INSERT/UPDATE, so use the UTC offset under which <_p_dob> is normalized
	IF _p_dob IS NULL THEN
		RETURN;
	END IF;
	_v_offset := round(extract(epoch FROM '11:11:11.111'::time) - extract(epoch FROM (_p_dob AT TIME ZONE 'UTC')::time));
	IF _v_offset > 50400 THEN
		_v_offset := _v_offset - 86400;
	ELSIF _v_offset < -50400 THEN
		_v_offset := _v_offset + 86400;
	END IF;
	IF abs(_v_offset) > 50400 OR (_v_offset % 60) <> 0 THEN
		-- not normalized (legacy data), leave as is
		RETURN;
	END IF;
	-- POSIX notation: offsets west of Greenwich are positive
	PERFORM set_config (
		'TimeZone',
		format('<GMTP>%s%s', CASE WHEN _v_offset >= 0 THEN '-' ELSE '+' END, to_char(make_interval(secs => abs(_v_offset)), 'HH24:MI')),
		true
	);
END;
$tp$;""",

"""CREATE FUNCTION pg_temp._tp_reset_tz() RETURNS void LANGUAGE sql AS $tp$
	SELECT set_config('TimeZone', pg_temp._tp_meta('source_timezone'), true);
$tp$;""",

"""CREATE FUNCTION pg_temp._tp_suffix(_p_new_pk integer) RETURNS text LANGUAGE sql STABLE AS $tp$
	SELECT '[transplant ' || left(pg_temp._tp_meta('export_uuid'), 8) || '/' || _p_new_pk || ']'
$tp$;""",

"""CREATE FUNCTION pg_temp._tp_assemble_blobs(_p_staging text, _p_tbl text, _p_col text) RETURNS void LANGUAGE plpgsql AS $tp$
DECLARE
	_v_src integer;
BEGIN
	FOR _v_src IN
		SELECT DISTINCT c.src_pk FROM pg_temp._s_blob_chunk c WHERE c.tbl = _p_tbl AND c.col = _p_col
	LOOP
		EXECUTE format (
			'UPDATE %s s SET %I = (SELECT string_agg(c.data, ''''::bytea ORDER BY c.seq) FROM pg_temp._s_blob_chunk c WHERE c.tbl = $1 AND c.col = $2 AND c.src_pk = $3) WHERE s._src_pk = $3',
			_p_staging,
			_p_col
		) USING _p_tbl, _p_col, _v_src;
		DELETE FROM pg_temp._s_blob_chunk c WHERE c.tbl = _p_tbl AND c.col = _p_col AND c.src_pk = _v_src;
	END LOOP;
END;
$tp$;""",

"""CREATE FUNCTION pg_temp._tp_doc_type(_p_name text, _p_name_de text) RETURNS integer LANGUAGE plpgsql AS $tp$
DECLARE
	_v_pk integer;
BEGIN
	SELECT dt.pk INTO _v_pk FROM blobs.doc_type dt WHERE dt.name = _p_name ORDER BY dt.pk LIMIT 1;
	IF _v_pk IS NOT NULL THEN
		RETURN _v_pk;
	END IF;
	INSERT INTO blobs.doc_type (name) VALUES (_p_name) RETURNING pk INTO _v_pk;
	BEGIN
		PERFORM i18n.upd_tx('de', _p_name, _p_name_de);
		PERFORM i18n.upd_tx('de_DE', _p_name, _p_name_de);
	EXCEPTION
		WHEN undefined_function OR insufficient_privilege THEN
			NULL;
	END;
	RETURN _v_pk;
END;
$tp$;""",

"""CREATE FUNCTION pg_temp._tp_admin_note() RETURNS text LANGUAGE sql STABLE AS $tp$
	SELECT
		replace(replace(replace(replace(replace(
			pg_temp._tp_meta('txt_admin_note'),
			'{source}', coalesce(pg_temp._tp_meta('source_desc'), '?')),
			'{source_pk}', coalesce(pg_temp._tp_meta('source_pk'), '?')),
			'{export_uuid}', coalesce(pg_temp._tp_meta('export_uuid'), '?')),
			'{exported_when}', coalesce(pg_temp._tp_meta('exported_when'), '?')),
			'{patient_mode}', coalesce(pg_temp._tp_state('patient_mode'), '?'))
		|| coalesce(E'\\n' || pg_temp._tp_meta('txt_relatives') || ': ' || pg_temp._tp_meta('relatives'), '')
$tp$;""",

"""CREATE FUNCTION pg_temp._tp_summary() RETURNS jsonb LANGUAGE sql STABLE AS $tp$
	SELECT jsonb_build_object (
		'format', 1,
		'export_uuid', pg_temp._tp_meta('export_uuid'),
		'source_id', pg_temp._tp_meta('source_id'),
		'source_pk', pg_temp._tp_meta('source_pk'),
		'patient_mode', pg_temp._tp_state('patient_mode'),
		'target_identity', pg_temp._tp_target(),
		'dry_run', pg_temp._tp_cfg_bool('dry_run'),
		'forced', pg_temp._tp_cfg_bool('force'),
		'staff_match', lower(coalesce(pg_temp._tp_cfg('staff_match'), 'strict')),
		'counts', (
			SELECT coalesce(jsonb_object_agg(x.tbl, x.by_status), '{}'::jsonb) FROM (
				SELECT c.tbl, jsonb_object_agg(c.status, c.n) AS by_status FROM (
					SELECT mm.tbl, mm.status, count(1) AS n FROM pg_temp._gm_tp_map mm GROUP BY mm.tbl, mm.status
				) c GROUP BY c.tbl
			) x
		),
		'staff', (
			SELECT coalesce(jsonb_agg(jsonb_build_object (
				'src_alias', st.short_alias,
				'src_db_user', st.db_user,
				'target_alias', tst.short_alias,
				'target_pk', m.new_pk,
				'how', m.note
			) ORDER BY st._src_pk), '[]'::jsonb)
			FROM pg_temp._s_staff st
				JOIN pg_temp._gm_tp_map m ON (m.tbl = 'staff' AND m.src_pk = st._src_pk)
				LEFT JOIN dem.staff tst ON (tst.pk = m.new_pk)
		),
		'skipped', (
			SELECT coalesce(jsonb_agg(jsonb_build_object('table', m.tbl, 'src_pk', m.src_pk, 'status', m.status, 'why', m.note) ORDER BY m.tbl, m.src_pk), '[]'::jsonb)
			FROM pg_temp._gm_tp_map m
			WHERE m.status IN ('skipped', 'dropped', 'gone')
		),
		'keep_refs_created', (SELECT coalesce(jsonb_agg(jsonb_build_object('table', k.tbl, 'key', k.key)), '[]'::jsonb) FROM pg_temp._gm_tp_keep_log k),
		'admin_encounter', pg_temp._tp_state('admin_encounter'),
		'protocol_doc', pg_temp._tp_state('protocol_doc'),
		'history_doc', pg_temp._tp_state('history_doc')
	)
$tp$;"""
]

#------------------------------------------------------------
_SQL_PROTOCOL_FUNCTION = """CREATE FUNCTION pg_temp._tp_protocol() RETURNS text LANGUAGE plpgsql STABLE AS $tp$
DECLARE
	_v_lines text[] := ARRAY[]::text[];
	_v_txt text;
BEGIN
	_v_lines := _v_lines || ARRAY[
		pg_temp._tp_meta('txt_protocol_title'),
		repeat('=', 72),
		format('%s: %s (%s)', pg_temp._tp_meta('txt_source'), pg_temp._tp_meta('source_desc'), pg_temp._tp_meta('source_id')),
		format('%s: #%s', pg_temp._tp_meta('txt_source_patient'), pg_temp._tp_meta('source_pk')),
		format('%s: %s (%s)', pg_temp._tp_meta('txt_export'), pg_temp._tp_meta('export_uuid'), pg_temp._tp_meta('exported_when')),
		format('%s: %s (%s)', pg_temp._tp_meta('txt_import'), now(), SESSION_USER),
		format('%s: %s / #%s', pg_temp._tp_meta('txt_mode'), pg_temp._tp_state('patient_mode'), pg_temp._tp_target()),
		format('%s: staff_match=%s, same_patient_as=%s, force=%s, fallback_staff=%s',
			pg_temp._tp_meta('txt_config'),
			lower(coalesce(pg_temp._tp_cfg('staff_match'), 'strict')),
			coalesce(pg_temp._tp_cfg('same_patient_as'), '-'),
			pg_temp._tp_cfg_bool('force'),
			coalesce(pg_temp._tp_cfg('fallback_staff'), '-')
		)
	];
	IF pg_temp._tp_meta('history_note') IS NOT NULL THEN
		_v_lines := _v_lines || ('history: ' || pg_temp._tp_meta('history_note'));
	END IF;
	IF pg_temp._tp_meta('relatives') IS NOT NULL THEN
		_v_lines := _v_lines || (pg_temp._tp_meta('txt_relatives') || ': ' || pg_temp._tp_meta('relatives'));
	END IF;
	-- staff
	_v_lines := _v_lines || ARRAY['', pg_temp._tp_meta('txt_staff_mapping'), repeat('-', 72)];
	SELECT string_agg (
		format('  %s (%s, db: %s) -> %s [%s]',
			coalesce(st.short_alias, '?'),
			concat_ws(', ', st.lastnames, st.firstnames),
			coalesce(st.db_user, '?'),
			coalesce(tst.short_alias, '#' || m.new_pk),
			m.note
		),
		E'\\n' ORDER BY st._src_pk
	) INTO _v_txt
	FROM pg_temp._s_staff st
		JOIN pg_temp._gm_tp_map m ON (m.tbl = 'staff' AND m.src_pk = st._src_pk)
		LEFT JOIN dem.staff tst ON (tst.pk = m.new_pk);
	_v_lines := _v_lines || coalesce(_v_txt, '  -');
	-- reference data
	_v_lines := _v_lines || ARRAY['', pg_temp._tp_meta('txt_refs'), repeat('-', 72)];
	SELECT string_agg (
		format('  %s: %s #%s -> #%s', substr(m.tbl, 5), m.status, m.src_pk, m.new_pk),
		E'\\n' ORDER BY m.tbl, m.src_pk
	) INTO _v_txt
	FROM pg_temp._gm_tp_map m
	WHERE m.tbl LIKE 'ref:%';
	_v_lines := _v_lines || coalesce(_v_txt, '  -');
	SELECT string_agg(format('  %s: %s (created)', k.tbl, k.key), E'\\n' ORDER BY k.tbl, k.key) INTO _v_txt FROM pg_temp._gm_tp_keep_log k;
	IF _v_txt IS NOT NULL THEN
		_v_lines := _v_lines || _v_txt;
	END IF;
	-- skipped
	_v_lines := _v_lines || ARRAY['', pg_temp._tp_meta('txt_skipped'), repeat('-', 72)];
	SELECT string_agg (
		format('  %s #%s: %s (%s)', m.tbl, m.src_pk, m.status, coalesce(m.note, '-')),
		E'\\n' ORDER BY t.ord, m.src_pk
	) INTO _v_txt
	FROM pg_temp._gm_tp_map m
		JOIN pg_temp._gm_tp_tables t ON (t.tbl = m.tbl)
	WHERE m.status IN ('skipped', 'dropped', 'gone');
	_v_lines := _v_lines || coalesce(_v_txt, '  -');
	-- rows
	_v_lines := _v_lines || ARRAY['', pg_temp._tp_meta('txt_rows'), repeat('-', 72)];
	SELECT string_agg (
		format('  %s | #%s -> #%s | %s%s | %s @ %s',
			m.tbl,
			m.src_pk,
			coalesce(m.new_pk::text, '-'),
			m.status,
			coalesce(' (' || m.note || ')', ''),
			coalesce(o.mod_by, '?'),
			coalesce(o.mod_when::text, '?')
		),
		E'\\n' ORDER BY t.ord, m.src_pk
	) INTO _v_txt
	FROM pg_temp._gm_tp_map m
		JOIN pg_temp._gm_tp_tables t ON (t.tbl = m.tbl)
		JOIN (
			@ORIGINS@
		) o ON (o.tbl = m.tbl AND o.src_pk = m.src_pk);
	_v_lines := _v_lines || coalesce(_v_txt, '  -');
	RETURN array_to_string(_v_lines, E'\\n') || E'\\n';
END;
$tp$;"""

#------------------------------------------------------------
_SQL_PREFLIGHT = """DO $tp$
DECLARE
	_v_hash text;
	_v_value text;
	_v_fallback integer;
BEGIN
	-- serialize transplants
	PERFORM pg_advisory_xact_lock(hashtext('gm_transplant'));
	-- schema
	_v_hash := md5(pg_temp.concat_table_structure_v19_and_up());
	IF _v_hash IS DISTINCT FROM pg_temp._tp_meta('schema_hash') THEN
		RAISE EXCEPTION USING
			ERRCODE = '%(GMTP3)s',
			MESSAGE = pg_temp._tp_meta('txt_err_schema'),
			DETAIL = jsonb_build_object('expected', pg_temp._tp_meta('schema_hash'), 'found', _v_hash)::text;
	END IF;
	-- configuration
	_v_value := lower(trim(coalesce(pg_temp._tp_cfg('staff_match'), 'strict')));
	IF _v_value NOT IN ('strict', 'lenient') THEN
		RAISE EXCEPTION USING ERRCODE = '%(GMTP4)s', MESSAGE = pg_temp._tp_meta('txt_err_config'), DETAIL = 'staff_match: strict | lenient';
	END IF;
	_v_value := lower(trim(coalesce(pg_temp._tp_cfg('patient_mode'), 'detect')));
	IF _v_value NOT IN ('detect', 'new', 'add') THEN
		RAISE EXCEPTION USING ERRCODE = '%(GMTP4)s', MESSAGE = pg_temp._tp_meta('txt_err_config'), DETAIL = 'patient_mode: detect | new | add';
	END IF;
	FOREACH _v_value IN ARRAY ARRAY['force', 'dry_run'] LOOP
		IF lower(trim(coalesce(pg_temp._tp_cfg(_v_value), 'false'))) NOT IN ('true', 't', 'yes', 'y', 'on', '1', 'false', 'f', 'no', 'n', 'off', '0') THEN
			RAISE EXCEPTION USING ERRCODE = '%(GMTP4)s', MESSAGE = pg_temp._tp_meta('txt_err_config'), DETAIL = _v_value || ': true | false';
		END IF;
	END LOOP;
	_v_value := nullif(trim(coalesce(pg_temp._tp_cfg('same_patient_as'), '')), '');
	IF _v_value IS NOT NULL THEN
		IF _v_value !~ '^[0-9]+$' THEN
			RAISE EXCEPTION USING ERRCODE = '%(GMTP4)s', MESSAGE = pg_temp._tp_meta('txt_err_config'), DETAIL = 'same_patient_as: primary key of a patient';
		END IF;
		IF NOT EXISTS (SELECT 1 FROM dem.identity i WHERE i.pk = _v_value::integer AND i.deleted IS FALSE) THEN
			RAISE EXCEPTION USING ERRCODE = '%(GMTP4)s', MESSAGE = pg_temp._tp_meta('txt_err_config'), DETAIL = 'same_patient_as: no (active) patient #' || _v_value;
		END IF;
	ELSIF lower(trim(coalesce(pg_temp._tp_cfg('patient_mode'), 'detect'))) = 'add' THEN
		RAISE EXCEPTION USING ERRCODE = '%(GMTP4)s', MESSAGE = pg_temp._tp_meta('txt_err_config'), DETAIL = 'patient_mode add requires same_patient_as';
	END IF;
	-- staff
	SELECT string_agg(DISTINCT trim(sm.target_alias), ', ') INTO _v_value
	FROM pg_temp._gm_tp_staff_map sm
	WHERE
		nullif(trim(sm.target_alias), '') IS NOT NULL
			AND
		NOT EXISTS (SELECT 1 FROM dem.staff st WHERE st.short_alias = trim(sm.target_alias));
	IF _v_value IS NOT NULL THEN
		RAISE EXCEPTION USING ERRCODE = '%(GMTP5)s', MESSAGE = pg_temp._tp_meta('txt_err_staff'), DETAIL = 'unknown target staff alias(es): ' || _v_value;
	END IF;
	_v_value := nullif(trim(coalesce(pg_temp._tp_cfg('fallback_staff'), '')), '');
	IF _v_value IS NOT NULL THEN
		SELECT st.pk INTO _v_fallback FROM dem.staff st WHERE st.short_alias = _v_value;
		IF _v_fallback IS NULL THEN
			RAISE EXCEPTION USING ERRCODE = '%(GMTP5)s', MESSAGE = pg_temp._tp_meta('txt_err_staff'), DETAIL = 'unknown fallback staff alias: ' || _v_value;
		END IF;
	ELSE
		SELECT st.pk INTO _v_fallback FROM dem.staff st WHERE st.db_user = SESSION_USER;
		IF _v_fallback IS NULL THEN
			SELECT st.pk INTO _v_fallback FROM dem.staff st WHERE st.db_user = CURRENT_USER;
		END IF;
	END IF;
	PERFORM pg_temp._tp_set_state('fallback_staff', _v_fallback::text);
END;
$tp$;""" % {
	'GMTP3': SQLSTATE_SCHEMA_MISMATCH,
	'GMTP4': SQLSTATE_INVALID_CONFIG,
	'GMTP5': SQLSTATE_STAFF
}

#------------------------------------------------------------
_SQL_DETECT = """DO $tp$
DECLARE
	_v_mode text;
	_v_same text;
	_v_target integer;
	_v_applied jsonb;
	_v_candidates jsonb;
BEGIN
	_v_mode := lower(trim(coalesce(pg_temp._tp_cfg('patient_mode'), 'detect')));
	_v_same := nullif(trim(coalesce(pg_temp._tp_cfg('same_patient_as'), '')), '');
	-- this very export imported before ?
	SELECT jsonb_agg(i.pk ORDER BY i.pk) INTO _v_applied
	FROM dem.identity i
	WHERE (i.aux_info -> 'gm_transplant' -> 'imports') @> jsonb_build_array(jsonb_build_object('export_uuid', pg_temp._tp_meta('export_uuid')));
	IF _v_applied IS NOT NULL AND NOT pg_temp._tp_cfg_bool('force') THEN
		RAISE EXCEPTION USING
			ERRCODE = '%(GMTP2)s',
			MESSAGE = pg_temp._tp_meta('txt_err_applied'),
			DETAIL = jsonb_build_object('identities', _v_applied)::text;
	END IF;
	IF _v_same IS NOT NULL THEN
		_v_mode := 'add';
		_v_target := _v_same::integer;
	ELSIF _v_mode = 'detect' THEN
		WITH cands AS (
			-- same name and date of birth
			SELECT i.pk, 'name+dob'::text AS why
			FROM dem.identity i
				JOIN dem.names n ON (n.id_identity = i.pk)
				JOIN pg_temp._s_dem__names sn ON (lower(sn.lastnames) = lower(n.lastnames) AND lower(sn.firstnames) = lower(n.firstnames))
				CROSS JOIN pg_temp._s_dem__identity si
			WHERE date_trunc('day', i.dob) = date_trunc('day', si.dob)
			UNION
			-- same external ID (except database local GNUmed IDs)
			SELECT x.id_identity, 'external_id'
			FROM dem.lnk_identity2ext_id x
				JOIN dem.enum_ext_id_types e ON (e.pk = x.fk_origin)
				JOIN pg_temp._s_dem__lnk_identity2ext_id sx ON (
					sx._x_type_name = e.name
						AND
					sx._x_type_issuer IS NOT DISTINCT FROM e.issuer
						AND
					sx.external_id = x.external_id
				)
			WHERE e.issuer IS DISTINCT FROM 'GNUmed'
			UNION
			-- transplanted from this source before (or from the same origin)
			SELECT x.id_identity, 'transplant_provenance'
			FROM dem.lnk_identity2ext_id x
				JOIN dem.enum_ext_id_types e ON (e.pk = x.fk_origin)
			WHERE
				e.name = 'GNUmed transplant source'
					AND
				e.issuer = 'GNUmed'
					AND
				x.external_id IN (
					SELECT pg_temp._tp_meta('provenance')
					UNION
					SELECT sx.external_id FROM pg_temp._s_dem__lnk_identity2ext_id sx WHERE sx._x_type_name = 'GNUmed transplant source' AND sx._x_type_issuer = 'GNUmed'
				)
		)
		SELECT jsonb_agg(jsonb_build_object('pk', g.pk, 'reasons', g.reasons, 'deleted', g.deleted) ORDER BY g.pk) INTO _v_candidates
		FROM (
			SELECT c.pk, jsonb_agg(DISTINCT c.why) AS reasons, i.deleted
			FROM cands c JOIN dem.identity i ON (i.pk = c.pk)
			GROUP BY c.pk, i.deleted
		) g;
		IF _v_candidates IS NOT NULL THEN
			RAISE EXCEPTION USING
				ERRCODE = '%(GMTP1)s',
				MESSAGE = pg_temp._tp_meta('txt_err_candidates'),
				DETAIL = jsonb_build_object('candidates', _v_candidates)::text;
		END IF;
		_v_mode := 'new';
	END IF;
	PERFORM pg_temp._tp_set_state('patient_mode', _v_mode);
	PERFORM pg_temp._tp_set_state('target', _v_target::text);
	-- a new identity must not clash with existing (name, dob, gender, comment)
	IF _v_mode = 'new' THEN
		IF EXISTS (
			SELECT 1
			FROM pg_temp._s_dem__identity si
				CROSS JOIN pg_temp._s_dem__names sn
			WHERE coalesce(array_length(dem.get_person_duplicates(si.dob, sn.lastnames, sn.firstnames, si.gender, si.comment), 1), 0) > 0
		) THEN
			PERFORM pg_temp._tp_set_state('tag_identity_comment', 'true');
		END IF;
	END IF;
END;
$tp$;""" % {
	'GMTP1': SQLSTATE_CANDIDATES,
	'GMTP2': SQLSTATE_ALREADY_IMPORTED
}

#------------------------------------------------------------
_SQL_RESOLVE_STAFF = """DO $tp$
DECLARE
	_v_strict boolean;
	_v_fallback integer;
	_v_alias text;
	_v_target integer;
	_v_how text;
	_v_staff record;
	_v_cand record;
BEGIN
	_v_strict := lower(trim(coalesce(pg_temp._tp_cfg('staff_match'), 'strict'))) <> 'lenient';
	_v_fallback := pg_temp._tp_state('fallback_staff')::integer;
	FOR _v_staff IN
		SELECT st._src_pk, st.short_alias, st.db_user, st.lastnames, st.firstnames, st.dob
		FROM pg_temp._s_staff st
		ORDER BY st._src_pk
	LOOP
		_v_target := NULL;
		_v_how := NULL;
		-- explicit mapping
		SELECT trim(sm.target_alias) INTO _v_alias
		FROM pg_temp._gm_tp_staff_map sm
		WHERE
			sm.src_alias IS NOT DISTINCT FROM _v_staff.short_alias
				AND
			sm.src_db_user IS NOT DISTINCT FROM _v_staff.db_user
				AND
			nullif(trim(sm.target_alias), '') IS NOT NULL
		LIMIT 1;
		IF _v_alias IS NOT NULL THEN
			SELECT st.pk INTO _v_target FROM dem.staff st WHERE st.short_alias = _v_alias;
			_v_how := 'explicit';
		END IF;
		-- matching
		IF _v_target IS NULL THEN
			FOR _v_cand IN
				SELECT x.staff_pk, x.identity_pk, x.how FROM (
					SELECT st.pk AS staff_pk, st.fk_identity AS identity_pk, 'alias'::text AS how, 1 AS prio
					FROM dem.staff st WHERE st.short_alias = _v_staff.short_alias
					UNION ALL
					SELECT st.pk, st.fk_identity, 'db_user', 2
					FROM dem.staff st WHERE st.db_user::text = _v_staff.db_user
				) x
				ORDER BY x.prio, x.staff_pk
			LOOP
				IF (NOT _v_strict) OR EXISTS (
					SELECT 1
					FROM dem.names n
						JOIN dem.identity i ON (i.pk = n.id_identity)
					WHERE
						n.id_identity = _v_cand.identity_pk
							AND
						lower(n.lastnames) = lower(_v_staff.lastnames)
							AND
						lower(n.firstnames) = lower(_v_staff.firstnames)
							AND
						((i.dob IS NULL) OR (_v_staff.dob IS NULL) OR (date_trunc('day', i.dob) = date_trunc('day', _v_staff.dob)))
				) THEN
					_v_target := _v_cand.staff_pk;
					_v_how := _v_cand.how;
					EXIT;
				END IF;
			END LOOP;
		END IF;
		-- fallback
		IF _v_target IS NULL THEN
			IF _v_fallback IS NULL THEN
				RAISE EXCEPTION USING
					ERRCODE = '%(GMTP5)s',
					MESSAGE = pg_temp._tp_meta('txt_err_no_fallback'),
					DETAIL = 'source staff: ' || coalesce(_v_staff.short_alias, _v_staff.db_user, '#' || _v_staff._src_pk);
			END IF;
			_v_target := _v_fallback;
			_v_how := 'fallback';
		END IF;
		INSERT INTO pg_temp._gm_tp_map (tbl, src_pk, new_pk, status, note)
		VALUES ('staff', _v_staff._src_pk, _v_target, 'existing', _v_how);
	END LOOP;
END;
$tp$;""" % {'GMTP5': SQLSTATE_STAFF}

#------------------------------------------------------------
_SQL_LOAD_PERSISTENT_MAP = """DO $tp$
DECLARE
	_v_rows jsonb;
	_v_tbl record;
BEGIN
	IF pg_temp._tp_state('patient_mode') IS DISTINCT FROM 'add' THEN
		RETURN;
	END IF;
	SELECT i.aux_info -> 'gm_transplant' -> 'sources' -> pg_temp._tp_meta('source_id') -> 'rows' INTO _v_rows
	FROM dem.identity i
	WHERE i.pk = pg_temp._tp_state('target')::integer;
	IF _v_rows IS NULL THEN
		RETURN;
	END IF;
	INSERT INTO pg_temp._gm_tp_map (tbl, src_pk, new_pk, status, note)
	SELECT t.key, r.key::integer, (r.value #>> '{}')::integer, 'existing', 'transplanted before'
	FROM jsonb_each(_v_rows) t
		CROSS JOIN LATERAL jsonb_each(t.value) r
	WHERE t.key IN (SELECT tt.tbl FROM pg_temp._gm_tp_tables tt)
	ON CONFLICT DO NOTHING;
	-- rows deleted in the target since are not restored
	FOR _v_tbl IN SELECT tt.tbl, tt.pk_col FROM pg_temp._gm_tp_tables tt LOOP
		EXECUTE format (
			'UPDATE pg_temp._gm_tp_map m SET status = %L, note = %L WHERE m.tbl = %L AND m.status = %L AND NOT EXISTS (SELECT 1 FROM %s t WHERE t.%I = m.new_pk)',
			'gone',
			'deleted in target after earlier transplant, not restored',
			_v_tbl.tbl,
			'existing',
			_v_tbl.tbl,
			_v_tbl.pk_col
		);
	END LOOP;
END;
$tp$;"""

#------------------------------------------------------------
_SQL_INSERT_NAMES = """DO $tp$
DECLARE
	_v_name record;
BEGIN
	FOR _v_name IN
		SELECT s.*, m.new_pk AS _new_pk
		FROM pg_temp._s_dem__names s
			JOIN pg_temp._gm_tp_map m ON (m.tbl = 'dem.names' AND m.src_pk = s._src_pk AND m.status = 'new')
		ORDER BY s.active, s._src_pk
	LOOP
		BEGIN
			INSERT INTO dem.names (id, id_identity, active, lastnames, firstnames, preferred, comment)
			VALUES (
				_v_name._new_pk,
				pg_temp._tp_m('dem.identity', _v_name.id_identity),
				-- names added to an existing patient do not replace the active name
				CASE WHEN pg_temp._tp_state('patient_mode') = 'add' THEN false ELSE _v_name.active END,
				_v_name.lastnames,
				_v_name.firstnames,
				_v_name.preferred,
				_v_name.comment
			);
		EXCEPTION
			WHEN unique_violation THEN
				IF pg_temp._tp_state('patient_mode') IS DISTINCT FROM 'add' THEN
					-- do not re-raise the original error, it contains patient data
					RAISE EXCEPTION USING ERRCODE = '%s', MESSAGE = pg_temp._tp_meta('txt_err_verify'), DETAIL = 'name of new patient clashes with existing person';
				END IF;
				UPDATE pg_temp._gm_tp_map m SET status = 'skipped', note = 'name clashes with another person in the target'
				WHERE m.tbl = 'dem.names' AND m.src_pk = _v_name._src_pk;
		END;
	END LOOP;
END;
$tp$;""" % SQLSTATE_VERIFICATION

#------------------------------------------------------------
_SQL_FIXUPS = [
# invoices can only be linked to bills which have items
"""UPDATE bill.bill b SET fk_doc = pg_temp._tp_mo('blobs.doc_med', s.fk_doc)
FROM pg_temp._s_bill__bill s
	JOIN pg_temp._gm_tp_map m ON (m.tbl = 'bill.bill' AND m.src_pk = s._src_pk AND m.status = 'new')
WHERE
	b.pk = m.new_pk
		AND
	s.fk_doc IS NOT NULL
		AND
	pg_temp._tp_mo('blobs.doc_med', s.fk_doc) IS NOT NULL
		AND
	EXISTS (SELECT 1 FROM bill.bill_item bi WHERE bi.fk_bill = b.pk);""",

"""UPDATE pg_temp._gm_tp_map m SET note = 'invoice document not linked (bill has no items)'
FROM pg_temp._s_bill__bill s
WHERE
	m.tbl = 'bill.bill' AND m.src_pk = s._src_pk AND m.status = 'new'
		AND
	s.fk_doc IS NOT NULL
		AND
	NOT EXISTS (SELECT 1 FROM bill.bill_item bi WHERE bi.fk_bill = m.new_pk);""",

# inserting allergies modifies the allergy state, restore it
"""UPDATE clin.allergy_state a SET
	has_allergy = s.has_allergy,
	last_confirmed = s.last_confirmed
FROM pg_temp._s_clin__allergy_state s
	JOIN pg_temp._gm_tp_map m ON (m.tbl = 'clin.allergy_state' AND m.src_pk = s._src_pk AND m.status = 'new')
WHERE
	a.pk = m.new_pk
		AND
	((a.has_allergy IS DISTINCT FROM s.has_allergy) OR (a.last_confirmed IS DISTINCT FROM s.last_confirmed));""",

# merge into an existing allergy state
"""UPDATE clin.allergy_state a SET
	has_allergy = greatest(a.has_allergy, s.has_allergy),
	last_confirmed = greatest(a.last_confirmed, s.last_confirmed)
FROM pg_temp._s_clin__allergy_state s
	JOIN pg_temp._gm_tp_map m ON (m.tbl = 'clin.allergy_state' AND m.src_pk = s._src_pk AND m.status = 'merged')
WHERE
	a.pk = m.new_pk
		AND
	((a.has_allergy IS DISTINCT FROM greatest(a.has_allergy, s.has_allergy)) OR (a.last_confirmed IS DISTINCT FROM greatest(a.last_confirmed, s.last_confirmed)));""",

# opening episodes activates health issues, restore
"""UPDATE clin.health_issue h SET is_active = s.is_active
FROM pg_temp._s_clin__health_issue s
	JOIN pg_temp._gm_tp_map m ON (m.tbl = 'clin.health_issue' AND m.src_pk = s._src_pk AND m.status = 'new')
WHERE
	h.pk = m.new_pk
		AND
	h.is_active IS DISTINCT FROM s.is_active;""",

# keep the expected date of confinement of an existing patient
"""UPDATE clin.patient p SET edc = s.edc
FROM pg_temp._s_clin__patient s
	JOIN pg_temp._gm_tp_map m ON (m.tbl = 'clin.patient' AND m.src_pk = s._src_pk AND m.status = 'merged')
WHERE
	p.pk = m.new_pk
		AND
	p.edc IS NULL
		AND
	s.edc IS NOT NULL;"""
]

#------------------------------------------------------------
_SQL_ADMIN_DOCUMENTS = """DO $tp$
DECLARE
	_v_tgt integer;
	_v_enc integer;
	_v_epi integer;
	_v_type integer;
	_v_doc integer;
	_v_reviewer integer;
	_v_prev_sha text;
	_v_loc integer;
BEGIN
	_v_tgt := pg_temp._tp_target();
	INSERT INTO clin.patient (fk_identity)
	SELECT _v_tgt WHERE NOT EXISTS (SELECT 1 FROM clin.patient p WHERE p.fk_identity = _v_tgt);
	-- encounter
	SELECT et.pk INTO _v_type FROM clin.encounter_type et WHERE et.description = 'chart review' ORDER BY et.pk LIMIT 1;
	IF _v_type IS NULL THEN
		INSERT INTO clin.encounter_type (description) VALUES ('chart review') RETURNING pk INTO _v_type;
	END IF;
	-- location: the importing praxis, else where the patient was seen last
	SELECT coalesce (
		(SELECT pb.fk_org_unit FROM dem.praxis_branch pb ORDER BY pb.pk LIMIT 1),
		(SELECT e.fk_location FROM clin.encounter e WHERE e.fk_patient = _v_tgt ORDER BY e.started DESC LIMIT 1)
	) INTO _v_loc;
	INSERT INTO clin.encounter (fk_patient, fk_type, fk_location, started, last_affirmed, reason_for_encounter)
	VALUES (_v_tgt, _v_type, _v_loc, now(), now(), pg_temp._tp_meta('txt_rfe'))
	RETURNING pk INTO _v_enc;
	-- episode
	SELECT e.pk INTO _v_epi
	FROM clin.episode e
		JOIN clin.encounter c ON (c.pk = e.fk_encounter)
	WHERE
		c.fk_patient = _v_tgt
			AND
		e.fk_health_issue IS NULL
			AND
		e.description = pg_temp._tp_meta('txt_episode')
	ORDER BY e.pk
	LIMIT 1;
	IF _v_epi IS NULL THEN
		INSERT INTO clin.episode (fk_encounter, description, is_open)
		VALUES (_v_enc, pg_temp._tp_meta('txt_episode'), false)
		RETURNING pk INTO _v_epi;
	END IF;
	-- administrative progress note
	INSERT INTO clin.clin_narrative (fk_encounter, fk_episode, soap_cat, narrative, clin_when)
	VALUES (_v_enc, _v_epi, NULL, pg_temp._tp_admin_note(), now());
	_v_reviewer := coalesce (
		pg_temp._tp_state('fallback_staff')::integer,
		(SELECT i.fk_primary_provider FROM dem.identity i WHERE i.pk = _v_tgt),
		(SELECT m.new_pk FROM pg_temp._gm_tp_map m WHERE m.tbl = 'staff' ORDER BY m.src_pk LIMIT 1),
		(SELECT st.pk FROM dem.staff st WHERE st.is_active ORDER BY st.pk LIMIT 1)
	);
	-- protocol
	_v_type := pg_temp._tp_doc_type('GNUmed transplant protocol', 'GNUmed-Transplantationsprotokoll');
	INSERT INTO blobs.doc_med (fk_encounter, fk_episode, fk_type, comment, clin_when)
	VALUES (_v_enc, _v_epi, _v_type, pg_temp._tp_meta('txt_protocol_title'), now())
	RETURNING pk INTO _v_doc;
	INSERT INTO blobs.doc_obj (fk_doc, seq_idx, filename, data, fk_intended_reviewer)
	VALUES (_v_doc, 1, 'gm-transplant-protocol.txt', convert_to(pg_temp._tp_protocol(), 'UTF8'), _v_reviewer);
	PERFORM pg_temp._tp_set_state('admin_encounter', _v_enc::text);
	PERFORM pg_temp._tp_set_state('protocol_doc', _v_doc::text);
	-- audit history of source, unless unchanged since the last transplant from that source
	IF EXISTS (SELECT 1 FROM pg_temp._s_history h WHERE h.data IS NOT NULL) THEN
		SELECT i.aux_info -> 'gm_transplant' -> 'sources' -> pg_temp._tp_meta('source_id') ->> 'history_sha256' INTO _v_prev_sha
		FROM dem.identity i
		WHERE i.pk = _v_tgt;
		IF _v_prev_sha IS DISTINCT FROM pg_temp._tp_meta('history_sha256') THEN
			_v_type := pg_temp._tp_doc_type('GNUmed audit history', 'GNUmed-Änderungshistorie');
			INSERT INTO blobs.doc_med (fk_encounter, fk_episode, fk_type, comment, clin_when)
			VALUES (_v_enc, _v_epi, _v_type, pg_temp._tp_meta('txt_history_title'), now())
			RETURNING pk INTO _v_doc;
			INSERT INTO blobs.doc_obj (fk_doc, seq_idx, filename, data, fk_intended_reviewer)
			SELECT _v_doc, 1, 'gm-transplant-audit_history.txt', h.data, _v_reviewer
			FROM pg_temp._s_history h
			WHERE h.data IS NOT NULL;
			PERFORM pg_temp._tp_set_state('history_doc', _v_doc::text);
		END IF;
	END IF;
END;
$tp$;"""

#------------------------------------------------------------
_SQL_PERSIST = """DO $tp$
DECLARE
	_v_tgt integer;
	_v_sid text;
	_v_aux jsonb;
	_v_tp jsonb;
	_v_src jsonb;
	_v_rows jsonb;
	_v_type integer;
BEGIN
	_v_tgt := pg_temp._tp_target();
	_v_sid := pg_temp._tp_meta('source_id');
	-- source row -> target row mapping, used to never duplicate rows on later transplants
	SELECT coalesce(jsonb_object_agg(g.tbl, g.rows), '{}'::jsonb) INTO _v_rows
	FROM (
		SELECT m.tbl, jsonb_object_agg(m.src_pk::text, m.new_pk) AS rows
		FROM pg_temp._gm_tp_map m
			JOIN pg_temp._gm_tp_tables t ON (t.tbl = m.tbl)
		WHERE m.status IN ('new', 'merged', 'existing', 'gone')
		GROUP BY m.tbl
	) g;
	SELECT coalesce(i.aux_info, '{}'::jsonb) INTO _v_aux FROM dem.identity i WHERE i.pk = _v_tgt;
	_v_tp := coalesce(_v_aux -> 'gm_transplant', '{}'::jsonb);
	_v_src := coalesce(_v_tp -> 'sources' -> _v_sid, '{}'::jsonb) || jsonb_build_object (
		'source', pg_temp._tp_meta('source_desc'),
		'source_pk', pg_temp._tp_meta('source_pk'),
		'rows', _v_rows
	);
	IF pg_temp._tp_state('history_doc') IS NOT NULL THEN
		_v_src := _v_src || jsonb_build_object('history_sha256', pg_temp._tp_meta('history_sha256'));
	END IF;
	_v_tp := _v_tp || jsonb_build_object (
		'imports', coalesce(_v_tp -> 'imports', '[]'::jsonb) || jsonb_build_array(jsonb_build_object (
			'export_uuid', pg_temp._tp_meta('export_uuid'),
			'exported_when', pg_temp._tp_meta('exported_when'),
			'source_id', _v_sid,
			'source_pk', pg_temp._tp_meta('source_pk'),
			'imported_when', now(),
			'imported_by', SESSION_USER,
			'patient_mode', pg_temp._tp_state('patient_mode'),
			'forced', pg_temp._tp_cfg_bool('force')
		)),
		'sources', coalesce(_v_tp -> 'sources', '{}'::jsonb) || jsonb_build_object(_v_sid, _v_src)
	);
	PERFORM pg_temp._tp_set_dob_tz((SELECT i.dob FROM dem.identity i WHERE i.pk = _v_tgt));
	UPDATE dem.identity SET aux_info = _v_aux || jsonb_build_object('gm_transplant', _v_tp) WHERE pk = _v_tgt;
	PERFORM pg_temp._tp_reset_tz();
	-- provenance external ID
	SELECT e.pk INTO _v_type FROM dem.enum_ext_id_types e WHERE e.name = 'GNUmed transplant source' AND e.issuer = 'GNUmed' ORDER BY e.pk LIMIT 1;
	IF _v_type IS NULL THEN
		INSERT INTO dem.enum_ext_id_types (name, issuer) VALUES ('GNUmed transplant source', 'GNUmed') RETURNING pk INTO _v_type;
	END IF;
	INSERT INTO dem.lnk_identity2ext_id (id_identity, external_id, fk_origin, comment)
	SELECT _v_tgt, pg_temp._tp_meta('provenance'), _v_type, pg_temp._tp_meta('source_desc')
	WHERE NOT EXISTS (
		SELECT 1 FROM dem.lnk_identity2ext_id x
		WHERE x.id_identity = _v_tgt AND x.fk_origin = _v_type AND x.external_id = pg_temp._tp_meta('provenance')
	);
END;
$tp$;"""

#------------------------------------------------------------
_SQL_VERIFY = """DO $tp$
DECLARE
	_v_bad jsonb;
BEGIN
	-- every staged row must have been accounted for
	SELECT jsonb_object_agg(x.tbl, x.n) INTO _v_bad FROM (
		@MISSING@
	) x WHERE x.n > 0;
	IF _v_bad IS NOT NULL THEN
		RAISE EXCEPTION USING ERRCODE = '%(GMTP9)s', MESSAGE = pg_temp._tp_meta('txt_err_verify'), DETAIL = jsonb_build_object('unaccounted', _v_bad)::text;
	END IF;
	-- every new row must exist
	SELECT jsonb_object_agg(x.tbl, x.n) INTO _v_bad FROM (
		@LOST@
	) x WHERE x.n > 0;
	IF _v_bad IS NOT NULL THEN
		RAISE EXCEPTION USING ERRCODE = '%(GMTP9)s', MESSAGE = pg_temp._tp_meta('txt_err_verify'), DETAIL = jsonb_build_object('lost', _v_bad)::text;
	END IF;
	IF pg_temp._tp_cfg_bool('dry_run') THEN
		RAISE EXCEPTION USING ERRCODE = '%(GMTP0)s', MESSAGE = pg_temp._tp_meta('txt_dry_run_ok'), DETAIL = pg_temp._tp_summary()::text;
	END IF;
END;
$tp$;""" % {
	'GMTP9': SQLSTATE_VERIFICATION,
	'GMTP0': SQLSTATE_DRY_RUN_OK
}

#============================================================
# public API: export
#------------------------------------------------------------
def explant_patient(pk_identity:int, filename:str=None, conn=None, include_history:bool=True, passphrase:str=None, source_description:str=None, progress_callback=None) -> str:
	"""Export a patient as a transplant script.

	Contrary to what EXplant might suggest, source data is
	NOT removed from the source.

	Args:
		pk_identity: the patient (dem.identity.pk)
		filename: where to put the script, default: work directory
		conn: a connection to read from, should be gm-dbo
			such that the audit trail can be read; if None a
			connection of the current user is used
		include_history: whether to include the audit trail
		passphrase: if given, the script is encrypted symmetrically
		source_description: shown to the user importing the script

	Returns:
		The name of the (possibly encrypted) script file.

	Raises:
		cTransplantError: messages contain no patient data
	"""
	if filename is None:
		filename = gmTools.get_unique_filename (
			prefix = 'gm-transplant-pk%s-%s-' % (pk_identity, pydt.datetime.now().strftime('%Y%m%d-%H%M%S')),
			suffix = '.sql',
			tmp_dir = gmTools.gmPaths().user_work_dir
		)
	filename = os.path.abspath(os.path.expanduser(filename))
	conn, close_conn = _get_conn(conn)
	_log.info('exporting patient #%s for transplant into [%s]', pk_identity, filename)
	curs = conn.cursor()
	try:
		problems = _verify_export_completeness(curs)
	finally:
		curs.close()
	if problems:
		close_conn()
		raise cTransplantError(_('This GNUmed version cannot fully transplant patients from this database:\n\n%s') % '\n'.join(problems))

	schema_hash = gmPG2.get_schema_hash(link_obj = conn)
	expected_hash = gmPG2.known_schema_hashes.get(SCHEMA_VERSION)
	if schema_hash != expected_hash:
		close_conn()
		raise cTransplantError(_('Database schema hash [%s] does not match the expected v%s schema hash [%s].') % (schema_hash, SCHEMA_VERSION, expected_hash))

	if source_description is None:
		source_description = _get_source_description()
	prev_autocommit = conn.autocommit
	try:
		conn.rollback()
		conn.autocommit = True
		exporter = _cExporter (
			conn = conn,
			pk_identity = pk_identity,
			include_history = include_history,
			source_description = source_description,
			progress_callback = progress_callback
		)
		exporter.schema_hash = schema_hash
		exporter.export(filename)
	except cTransplantError:
		_log.exception('patient #%s cannot be exported for transplant', pk_identity)
		raise

	except Exception as exc:
		_log.exception('error exporting patient #%s for transplant', pk_identity)
		raise cTransplantError(_('Error exporting the patient (%s). Check the log.') % exc.__class__.__name__) from exc
	finally:
		try:
			conn.autocommit = prev_autocommit
		except Exception:
			pass
		close_conn()
	_log.info('patient #%s exported: %s rows', pk_identity, sum(exporter.counts.values()))
	if passphrase:
		from Gnumed.pycommon import gmCrypto
		# GPG such that import_patient_from_transplant_script() can decrypt it
		encrypted = gmCrypto.encrypt_file_symmetric_gpg (
			filename = filename,
			passphrase = passphrase,
			comment = 'GNUmed transplant script',
			remove_unencrypted = True
		)
		if not encrypted:
			raise cTransplantError(_('Cannot encrypt transplant script (is GnuPG installed ?).'))

		os.chmod(encrypted, 0o600)
		return encrypted

	return filename

#------------------------------------------------------------
def _get_source_description() -> str:
	try:
		branch = gmPraxis.gmCurrentPraxisBranch()
		return '%s / %s' % (branch['praxis'], branch['branch'])
	except Exception:
		_log.debug('cannot determine praxis branch')
	return None

#------------------------------------------------------------
def run_patient_explant_tool():
	from Gnumed.business import gmPersonSearch
	print('praxis branch:', gmPraxis.gmCurrentPraxisBranch.from_first_branch())
	print('Note: the change history (audit trail) of the patient can only')
	print('      be exported when logged in as the database owner (gm-dbo).')
	exit_code = 0
	pat = gmPersonSearch.ask_for_patient()
	while pat:
		print('patient: #%s' % pat.ID)
		def_fname = os.path.join (
			gmTools.gmPaths().user_work_dir,
			'patients',
			'gm-transplant-pk%s.sql'
		) % pat.ID
		fname = gmTools.prompted_input(prompt = 'Script file name', default = def_fname)
		if fname is None:
			break
		try:
			fname = explant_patient (
				pk_identity = pat.ID,
				filename = fname,
				progress_callback = lambda msg: print('  %s' % msg)
			)
			print('Transplant script:', fname)
			print('The script contains patient data, treat it as confidential.')
		except cTransplantError as exc:
			print('ERROR: %s' % exc)
			exit_code = -2
		pat = gmPersonSearch.ask_for_patient()
	return exit_code

#============================================================
# public API: reading scripts
#------------------------------------------------------------
def read_script_metadata(filename:str) -> dict:
	"""Read the metadata of a transplant script (without running it)."""
	with open(filename, 'rb') as script:
		for line in script:
			if line.startswith(MARKER_DATA_BEGIN.encode('utf8')):
				break
			if line.startswith(MARKER_META.encode('utf8')):
				return json.loads(line[len(MARKER_META):].decode('utf8'))
	raise cTransplantError(_('[%s] is not a GNUmed transplant script.') % filename)

#------------------------------------------------------------
_REGEX_CFG_LINE = re.compile(r"^\s*INSERT INTO pg_temp\._gm_tp_cfg VALUES \('([a-z_]+)',\s*(NULL|E?'(?:[^']|'')*')\s*\);", re.IGNORECASE)

def read_script_config(filename:str) -> dict:
	"""Read the (possibly manually edited) configuration block.

	Best effort, for display purposes only.
	"""
	config = {'staff_map': []}
	in_cfg = False
	in_staff = False
	with open(filename, 'rb') as script:
		for raw_line in script:
			line = raw_line.decode('utf8', errors = 'replace').rstrip('\n')
			if line.startswith(MARKER_DATA_BEGIN):
				break
			if line.startswith(MARKER_CFG_BEGIN):
				in_cfg = True
				continue
			if line.startswith(MARKER_CFG_END):
				break
			if not in_cfg or line.lstrip().startswith('--'):
				continue
			match = _REGEX_CFG_LINE.match(line)
			if match:
				val = match.group(2)
				config[match.group(1)] = None if val.upper() == 'NULL' else _unquote_sql(val)
				continue
			if 'pg_temp._gm_tp_staff_map' in line:
				in_staff = True
				continue
			if in_staff:
				values = re.findall(r"NULL|E?'(?:[^'\\]|\\.|'')*'", line)
				if len(values) == 4:
					config['staff_map'].append(tuple([ None if v.upper() == 'NULL' else _unquote_sql(v) for v in values ]))
				if line.strip().endswith(';'):
					in_staff = False
	return config

#------------------------------------------------------------
def _unquote_sql(literal:str) -> str:
	if literal.startswith(('E', 'e')):
		body = literal[2:-1]
		return body.encode('latin1', errors = 'backslashreplace').decode('unicode_escape', errors = 'replace').replace("''", "'")
	return literal[1:-1].replace("''", "'")

#------------------------------------------------------------
def verify_script_checksum(filename:str) -> bool:
	"""Check the SHA-256 checksum of the protected part of a script."""
	sha = hashlib.sha256()
	hashing = False
	expected = None
	with open(filename, 'rb') as script:
		for line in script:
			if line.startswith(MARKER_SHA256.encode('utf8')):
				expected = line[len(MARKER_SHA256):].strip().decode('ascii')
				break
			if hashing:
				sha.update(line)
				continue
			if line.startswith(MARKER_DATA_BEGIN.encode('utf8')):
				hashing = True
	if expected is None:
		_log.error('no checksum in [%s]', filename)
		return False

	if sha.hexdigest() != expected:
		_log.error('checksum mismatch in [%s]', filename)
		return False

	return True

#------------------------------------------------------------
def _iter_script_statements(filename:str):
	"""Yield (statement id, section, SQL) of a script.

	Statements are separated by marker lines. Literals never
	span lines, so marker lines cannot occur inside data.
	"""
	marker = MARKER_STMT.encode('utf8')
	current_id = None
	section = None
	lines = []
	with open(filename, 'rb') as script:
		for line in script:
			if line.startswith(marker) or line.startswith(MARKER_SHA256.encode('utf8')):
				if current_id is not None:
					yield current_id, section, b''.join(lines).decode('utf8')
				if line.startswith(MARKER_SHA256.encode('utf8')):
					return
				parts = line[len(marker):].decode('utf8').strip().split(' ', 1)
				current_id = parts[0]
				section = parts[1] if len(parts) > 1 else ''
				lines = []
				continue
			if current_id is not None:
				lines.append(line)
	if current_id is not None:
		yield current_id, section, b''.join(lines).decode('utf8')

#============================================================
# public API: import
#------------------------------------------------------------
def implant_patient(filename:str, conn, patient_mode:str=None, same_patient_as:int=None, staff_match:str=None, fallback_staff:str=None, dry_run:bool=False, force:bool=False, progress_callback=None) -> cTransplantResult:
	"""Run a transplant script against the database of <conn>.

	Settings passed in override the configuration block of the script.

	Args:
		conn: connection to the target database, should be gm-dbo
		patient_mode: 'detect' / 'new' / 'add'
		same_patient_as: target patient pk to add the data to (implies patient_mode 'add')
		staff_match: 'strict' / 'lenient'
		fallback_staff: alias of the staff member to use for unmappable staff
		dry_run: run everything, then roll back
		force: allow importing this export again (never duplicates rows)
	"""
	if not verify_script_checksum(filename):
		return cTransplantResult('error', message = _('The transplant script is damaged or has been modified below the configuration block (checksum mismatch).'))

	settings = {}
	if patient_mode is not None:
		settings['patient_mode'] = patient_mode
	if same_patient_as is not None:
		settings['same_patient_as'] = str(same_patient_as)
		settings['patient_mode'] = 'add'
	if staff_match is not None:
		settings['staff_match'] = staff_match
	if fallback_staff is not None:
		settings['fallback_staff'] = fallback_staff
	if dry_run:
		settings['dry_run'] = 'true'
	if force:
		settings['force'] = 'true'
	_log.info('running transplant script [%s], settings: %s', filename, settings)
	prev_autocommit = conn.autocommit
	conn.rollback()
	conn.autocommit = True
	curs = conn.cursor()
	stmt_id = None
	section = None
	result_row = None
	in_tx = False
	try:
		for stmt_id, section, sql in _iter_script_statements(filename):
			if progress_callback and section.split(' ')[0] in ('load', 'ref', 'detect', 'staff', 'admin', 'verify', 'preflight'):
				progress_callback(section)
			curs.execute(sql)
			if section == 'begin':
				in_tx = True
				for key, val in settings.items():
					curs.execute('SELECT set_config(%(key)s, %(val)s, true)', {'key': 'gm_transplant.%s' % key, 'val': val})
			elif section == 'result':
				result_row = curs.fetchone()
			elif section == 'commit':
				in_tx = False
	except Exception as exc:
		if in_tx:
			try:
				curs.execute('ROLLBACK')
			except Exception:
				_log.exception('cannot roll back')
		return _result_from_exception(exc, stmt_id, section)
	finally:
		curs.close()
		try:
			conn.autocommit = prev_autocommit
		except Exception:
			pass
	if result_row is None:
		_log.error('transplant script did not report a result')
		return cTransplantResult('error', message = _('The transplant script did not report a result.'))
	summary = json.loads(result_row[0])
	_log.info('transplant done: target #%s, patient_mode [%s]', summary.get('target_identity'), summary.get('patient_mode'))
	return cTransplantResult('imported', summary = summary)

#------------------------------------------------------------
def _result_from_exception(exc, stmt_id:str, section:str) -> cTransplantResult:
	pgcode = getattr(exc, 'pgcode', None)
	diag = getattr(exc, 'diag', None)
	primary = getattr(diag, 'message_primary', None) if diag else None
	detail = getattr(diag, 'message_detail', None) if diag else None
	if pgcode is None or not pgcode.startswith('GMTP'):
		# might contain patient data, do not log the message itself
		_log.error('transplant script failed at statement [%s] (%s): %s, SQLSTATE %s', stmt_id, section, exc.__class__.__name__, pgcode)
		return cTransplantResult (
			'error',
			sqlstate = pgcode,
			statement = '%s (%s)' % (stmt_id, section),
			message = primary or str(exc)
		)
	_log.info('transplant script stopped at statement [%s] (%s): SQLSTATE %s, detail: %s', stmt_id, section, pgcode, detail)
	try:
		detail_data = json.loads(detail) if detail else {}
	except ValueError:
		detail_data = {'detail': detail}
	if not isinstance(detail_data, dict):
		detail_data = {'detail': detail_data}
	if pgcode == SQLSTATE_DRY_RUN_OK:
		return cTransplantResult('dry_run_ok', message = primary, sqlstate = pgcode, summary = detail_data)
	if pgcode == SQLSTATE_CANDIDATES:
		return cTransplantResult('candidates', message = primary, sqlstate = pgcode, candidates = detail_data.get('candidates', []))
	if pgcode == SQLSTATE_ALREADY_IMPORTED:
		return cTransplantResult('already_imported', message = primary, sqlstate = pgcode, identities = detail_data.get('identities', []))
	return cTransplantResult (
		'error',
		sqlstate = pgcode,
		statement = '%s (%s)' % (stmt_id, section),
		message = '%s\n%s' % (primary, detail or '')
	)

#------------------------------------------------------------
def run_patient_implant_tool(transplant_filename:str=None):
	if transplant_filename:
		if os.access(transplant_filename, os.F_OK):
			print('transplant file: %s' % transplant_filename)
		else:
			print('ERROR: [%s] does not seem to be an accessible file' % transplant_filename)
			transplant_filename = None

	if not transplant_filename:
		transplant_filename = gmTools.prompted_input(prompt = 'Transplant script file name')
		if not transplant_filename:
			return 0

	transplant_filename = os.path.abspath(os.path.expanduser(transplant_filename))
	try:
		meta = read_script_metadata(transplant_filename)
	except (cTransplantError, OSError, ValueError) as exc:
		print('ERROR: %s' % exc)
		return -2

	print('source        : %s' % meta.get('source'))
	print('source patient: #%s' % meta.get('source_pk'))
	print('exported      : %s' % meta.get('exported_when'))
	print('rows          : %s' % sum(meta.get('counts', {}).values()))
	settings = {}
	fallback = gmTools.prompted_input(prompt = 'Alias of the staff member to use for unmappable staff (empty: as configured in the script)')
	if fallback:
		settings['fallback_staff'] = fallback.strip()
	conn = gmPG2.get_connection(readonly = False, pooled = False)
	try:
		while True:
			print('dry run ...')
			result = implant_patient(transplant_filename, conn, dry_run = True, **settings)
			if result.status == 'already_imported':
				print('This export has already been imported into: %s' % ', '.join([ '#%s' % pk for pk in result.identities ]))
				if gmTools.prompted_input(prompt = 'Import again (no rows will be duplicated) ? [y/N]', default = 'n').strip().lower() != 'y':
					return 0
				settings['force'] = True
				continue
			if result.status == 'candidates':
				print('The patient may already exist in this database:')
				for cand in result.candidates:
					print('  #%s (%s)%s' % (cand['pk'], ', '.join(cand.get('reasons', [])), ' [deactivated]' if cand.get('deleted') else ''))
				answer = gmTools.prompted_input(prompt = '[n]ew patient / [a]dd <pk> / [c]ancel', default = 'c')
				answer = (answer or 'c').strip().lower()
				if answer == 'n':
					settings['patient_mode'] = 'new'
					continue
				if answer.startswith('a'):
					pk = answer[1:].strip()
					if not pk.isdigit():
						print('ERROR: add requires the pk of the patient, say: a 4711')
						continue
					settings['same_patient_as'] = int(pk)
					continue
				return 0
			if result.status != 'dry_run_ok':
				print('ERROR (SQLSTATE %s, statement %s):' % (result.sqlstate, result.statement))
				print(result.message)
				print('Nothing has been changed in the database.')
				return -2
			print('')
			print(result.format())
			print('')
			if gmTools.prompted_input(prompt = 'Import now ? [y/N]', default = 'n').strip().lower() != 'y':
				return 0
			result = implant_patient(transplant_filename, conn, dry_run = False, **settings)
			if result.status != 'imported':
				print('ERROR (SQLSTATE %s, statement %s):' % (result.sqlstate, result.statement))
				print(result.message)
				print('Nothing has been changed in the database.')
				return -2
			print('Patient imported as #%s.' % result.pk_identity)
			return 0
	finally:
		conn.close()

#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmLog
	gmLog.print_logfile_name()

	#--------------------------------------------------------
	def test_literals():
		for val in [None, '', 'abc', "O'Neil", 'a\\b', 'line1\nline2\r\n\ttab', '\x01\x7f', 'umlaut äöü ß', ' ']:
			print(repr(val), '->', sql_literal(val))
			assert '\n' not in sql_literal(val)

	#--------------------------------------------------------
	def test_specs():
		for spec in _TABLE_SPECS:
			print(spec.table, _expand_where(spec.where))

	#--------------------------------------------------------
	def test_completeness():
		gmPG2.request_login_params(setup_pool = True)
		for problem in verify_export_completeness():
			print(problem)

	#--------------------------------------------------------
	def test_explant():
		gmPG2.request_login_params(setup_pool = True)
		print(explant_patient(int(sys.argv[2]), filename = sys.argv[3] if len(sys.argv) > 3 else None))

	#--------------------------------------------------------
	def test_implant():
		gmPG2.request_login_params(setup_pool = True)
		conn = gmPG2.get_connection(readonly = False, pooled = False)
		result = implant_patient(sys.argv[2], conn, dry_run = True)
		print(result)
		print(result.message)
		print(result.format())

	#--------------------------------------------------------
	test_literals()
	test_specs()
	#test_completeness()
	#test_explant()
	#test_implant()
