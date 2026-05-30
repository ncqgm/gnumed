# -*- coding: utf-8 -*-
"""GNUmed clinical business object in generic form.

license: GPL v2 or later
"""
#============================================================
__author__ = "<karsten.hilbert@gmx.net>"

import sys
import logging
import datetime as pydt


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
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmTools

from Gnumed.business import gmSoapDefs
from Gnumed.business.gmHealthIssue import cHealthIssue
from Gnumed.business.gmEpisode import cEpisode
from Gnumed.business.gmEncounter import cEncounter
from Gnumed.business.gmHospitalStay import cHospitalStay
from Gnumed.business.gmPerformedProcedure import cPerformedProcedure
from Gnumed.business.gmExternalCare import cExternalCareItem
from Gnumed.business.gmVaccination import cVaccination
from Gnumed.business.gmClinNarrative import cNarrative
from Gnumed.business.gmMedication import cIntakeRegimen
from Gnumed.business.gmMedication import cSubstanceIntakeEntry
from Gnumed.business.gmAllergy import cAllergy
from Gnumed.business.gmAllergy import cAllergyState
from Gnumed.business.gmFamilyHistory import cFamilyHistory
from Gnumed.business.gmAutoHints import cSuppressedHint
from Gnumed.business.gmAutoHints import cDynamicHint
from Gnumed.business.gmDocuments import cDocument
from Gnumed.business.gmProviderInbox import cInboxMessage
from Gnumed.business.gmPathLab import cTestResult

_log = logging.getLogger('gm.emr')

#============================================================
_MAP_generic_emr_item_table2type_str = {
	'clin.encounter': _('Encounter'),
	'clin.episode': _('Episode'),
	'clin.health_issue': _('Health issue'),
	'clin.external_care': _('External care'),
	'clin.vaccination': _('Vaccination'),
	'clin.clin_narrative': _('Progress note'),
	'clin.test_result': _('Test result'),
	'clin.intake': _('Substance intake'),
	'clin.intake_regimen': _('Substance intake regimen'),
	'clin.hospital_stay': _('Hospital stay'),
	'clin.procedure': _('Performed procedure'),
	'clin.allergy': _('Allergy'),
	'clin.allergy_state': _('Allergy state'),
	'clin.family_history': _('Family history'),
	'blobs.doc_med': _('Document'),
	'dem.message_inbox': _('Inbox message'),
	'ref.auto_hint': _('Dynamic hint')
}

_MAP_generic_emr_item_table2class = {
	'clin.encounter': cEncounter,
	'clin.episode': cEpisode,
	'clin.health_issue': cHealthIssue,
	'clin.external_care': cExternalCareItem,
	'clin.vaccination': cVaccination,
	'clin.clin_narrative': cNarrative,
	'clin.test_result': cTestResult,
	'clin.intake': cSubstanceIntakeEntry,
	'clin.intake_regimen': cIntakeRegimen,
	'clin.hospital_stay': cHospitalStay,
	'clin.procedure': cPerformedProcedure,
	'clin.allergy': cAllergy,
	'clin.allergy_state': cAllergyState,
	'clin.family_history': cFamilyHistory,
	'clin.suppressed_hint': cSuppressedHint,
	'blobs.doc_med': cDocument,
	'dem.message_inbox': cInboxMessage,
	'ref.auto_hint': cDynamicHint
}

#============================================================
# generic items in clin.v_emr_journal
#------------------------------------------------------------
_SQL_get_generic_emr_items = """SELECT
	to_char(c_vej.clin_when, 'YYYY-MM-DD') AS date,
	c_vej.clin_when,
	coalesce(c_vej.soap_cat, '') as soap_cat,
	c_vej.narrative,
	c_vej.src_table,
	c_scr.rank AS scr,
	c_vej.modified_when,
	to_char(c_vej.modified_when, 'YYYY-MM-DD HH24:MI') AS date_modified,
	c_vej.modified_by,
	c_vej.row_version,
	c_vej.pk_episode,
	c_vej.pk_encounter,
	c_vej.soap_cat as real_soap_cat,
	c_vej.src_pk,
	c_vej.pk_health_issue,
	c_vej.health_issue,
	c_vej.episode,
	c_vej.issue_active,
	c_vej.issue_clinically_relevant,
	c_vej.episode_open,
	c_vej.encounter_started,
	c_vej.encounter_last_affirmed,
	c_vej.encounter_l10n_type,
	c_vej.pk_patient,
	-1 AS xmin_dummy
FROM
	clin.v_emr_journal c_vej
		JOIN clin.soap_cat_ranks c_scr on (c_scr.soap_cat IS NOT DISTINCT FROM c_vej.soap_cat)
"""

_SQL_get_hints_as_generic_emr_items = """SELECT
	to_char(now(), 'YYYY-MM-DD') AS date,
	now() as clin_when,
	'u'::text as soap_cat,
	hints.title || E'\n' || hints.hint
		as narrative,
	-- .src_table does not correspond with the
	-- .src_pk column source because it is generated
	-- from clin.get_hints_for_patient()
	'ref.auto_hint'::text as src_table,
	c_scr.rank AS scr,
	now() as modified_when,
	to_char(now(), 'YYYY-MM-DD HH24:MI') AS date_modified,
	current_user as modified_by,
	1::integer as row_version,
	NULL::integer as pk_episode,
	%(pk_enc)s as pk_encounter,
	'u'::text as real_soap_cat,
	hints.pk_auto_hint as src_pk,
	NULL::integer as pk_health_issue,
	''::text as health_issue,
	''::text as episode,
	False as issue_active,
	False as issue_clinically_relevant,
	False as episode_open,
	%(enc_start)s as encounter_started,
	%(enc_last_affirmed)s  as encounter_last_affirmed,
	%(enc_type)s as encounter_l10n_type,
	%(enc_pat)s as pk_patient,
	-1 AS xmin_dummy
FROM
	clin.get_hints_for_patient(%(enc_pat)s) AS hints
		JOIN clin.soap_cat_ranks c_scr ON (c_scr.soap_cat = 'u')
"""

__SQL_union = """(
	%s
) UNION ALL (
	%s
)"""

#------------------------------------------------------------
class cGenericEMRItem(gmBusinessDBObject.cBusinessDBObject):
	"""Represents an entry in clin.v_emr_journal."""

	_cmd_fetch_payload:str = _SQL_get_generic_emr_items + "WHERE src_table = %(src_table)s AND src_pk = %(src_pk)s"
	_cmds_store_payload:list = []
	_updatable_fields:list = ['']

	#--------------------------------------------------------
	def format(self, eol=None):
		lines = self.formatted_header
		lines.append(gmTools.u_box_horiz_4dashes * 40)
		lines.extend(self._payload['narrative'].strip().split('\n'))
		if eol is None:
			return lines

		return eol.join(lines)

	#--------------------------------------------------------
	def format_tech_info(self) -> list[str]:
		lines = []
		lines.append('%s [%s]' % (self.item_type_str, self._payload['real_soap_cat']))
		lines.append(' ' + _('Table: %s##tx: EMR item source (database table, mostly)') % self._payload['src_table'])
		lines.append(' ' + _('Version: %s%s') % (
			self._payload['row_version'],
			(' (%s)' % _('newly inserted')) if (self._payload['row_version'] == 1) else ''
		))
		lines.append(' ' + _('Last modified:'))
		lines.append('  %s (%s)' % (
			self._payload['modified_when'].timestamp(),
			_('UNIX timestamp')
		))
		format = '%Y-%m-%d (%b, %a) %H:%M:%S:%f %Z'
		lines.append('  %s %s' % (
			gmTools.u_arrow2right,
			self._payload['modified_when'].astimezone(tz = pydt.timezone.utc).strftime(format)
		))
		lines.append('  %s %s (%s)' % (
			gmTools.u_arrow2right,
			self._payload['modified_when'].strftime(format),
			_('local time')
		))
		lines.append(' ' + _('Modified by: %s') % self._payload['modified_by'])
		lines.append(' %s PK: %s' % (
			self._payload['src_table'],
			self._payload['src_pk']
		))
		lines.append(' ' + _('Encounter PK: %s') % self._payload['pk_encounter'])
		lines.append(' ' + _('Episode PK: %s') % self._payload['pk_episode'])
		lines.append(' ' + _('Health Issue PK: %s') % self._payload['pk_health_issue'])
		lines.append(' ' + _('Patient PK: %s') % self._payload['pk_patient'])
		return lines

	formatted_tech_info = property(fget = format_tech_info)

	#--------------------------------------------------------
	def format_header(self, eol=None):
		lines = []
		lines.append('%s (%s)' % (self.item_type_str, self.i18n_soap_cat))
		lines.append('')
		if self._payload['health_issue'] is None:
			issue_info = gmTools.u_diameter
		else:
			issue_info = '%s%s' % (
				self._payload['health_issue'],
				gmTools.bool2subst(self._payload['issue_active'], ' (' + _('active') + ')', ' (' + _('inactive') + ')', '')
			)
		lines.append(_('Health issue: %s') % issue_info)
		if self._payload['episode'] is None:
			episode_info = gmTools.u_diameter
		else:
			episode_info = '%s%s' % (
				self._payload['episode'],
				gmTools.bool2subst(self._payload['episode_open'], ' (' +  _('open') + ')', ' (' +  _('closed') + ')', '')
			)
		lines.append(_('Episode: %s') % episode_info)
		if self._payload['encounter_started'] is None:
			enc_info = gmTools.u_diameter
		else:
			enc_info = '%s - %s (%s)' % (
				self._payload['encounter_started'].strftime('%Y %b %d  %H:%M'),
				self._payload['encounter_last_affirmed'].strftime('%H:%M'),
				self._payload['encounter_l10n_type']
			)
		lines.append(_('Encounter: %s') % enc_info)
		lines.append(_('Event: %s') % self._payload['clin_when'].strftime('%Y %b %d  %H:%M'))
		if eol is None:
			return lines

		return eol.join(lines)

	formatted_header = property(format_header)

	#--------------------------------------------------------
	def __get_item_type_str(self):
		try:
			tmp = _MAP_generic_emr_item_table2type_str[self._payload['src_table']]
		except KeyError:
			tmp = '[%s:%s]' % (
				self._payload['src_table'],
				self._payload['src_pk']
			)
		return tmp

	item_type_str = property(__get_item_type_str)

	#--------------------------------------------------------
	def __get_i18n_soap_cat(self):
		return gmSoapDefs.soap_cat2l10n[self._payload['soap_cat']]

	i18n_soap_cat = property(__get_i18n_soap_cat)

	#--------------------------------------------------------
	def __get_specialized_item(self):
		item_class = _MAP_generic_emr_item_table2class[self._payload['src_table']]
		return item_class(aPK_obj = self._payload['src_pk'])

	specialized_item = property(__get_specialized_item)

#------------------------------------------------------------
def get_generic_emr_items (
	encounters:list=None,
	episodes:list=None,
	issues:list=None,
	patient=None,
	soap_cats:str | list[str|None] | tuple[str|None]=None,
	time_range=None,			# in days
	order_by:str=None,
	active_encounter:bool=None,
	return_pks:bool=False,
	exclude_soap_cats:bool=False,
	item_types2exclude:list[str]=None
) -> list[cGenericEMRItem] | list[int]:
	"""Return generic EMR items.

	Args:
		timerange: number of days for going back in EMR
	"""
	faulty_args = (
		(patient is None) and
		(encounters is None) and
		(episodes is None) and
		(issues is None) and
		(active_encounter is None)
	)
	assert not faulty_args, 'one of <patient>, <episodes>, <issues>, <active_encounter> must not be None'

	if (patient is not None) and (active_encounter is not None):
		if patient != active_encounter['pk_patient']:
			raise AssertionError('<patient> (%s) and <active_encounter>["pk_patient"] (%s) must match, if both given', patient, active_encounter['pk_patient'])

	if order_by is None:
		order_by = 'ORDER BY clin_when, pk_episode, scr, modified_when, src_table'
	else:
		order_by = 'ORDER BY %s' % order_by
	if (patient is None) and (active_encounter is not None):
		patient = active_encounter['pk_patient']
	where_parts = []
	args = {}
	if patient is not None:
		where_parts.append('pk_patient = %(pat)s')
		args['pat'] = patient
	if soap_cats:
		cats = list(soap_cats)
		# work around bug in psycopg2 not being able to properly
		# adapt None to NULL inside tuples
		if None in cats:
			where_arg = '((c_vej.soap_cat = ANY(%(soap_cat)s)) OR (c_vej.soap_cat IS NULL))'
			cats.remove(None)
		else:
			where_arg = 'c_vej.soap_cat = ANY(%(soap_cat)s)'
		if exclude_soap_cats:
			where_arg = 'NOT (%s)' % where_arg
		where_parts.append(where_arg)
		args['soap_cat'] = cats
	if item_types2exclude:
		where_parts.append('NOT (src_table = ANY(%(item_types)s))')
		args['item_types'] = item_types2exclude
	if time_range is not None:
		where_parts.append("clin_when > (now() - '%s days'::interval)" % time_range)
	if encounters is not None:
		where_parts.append("pk_encounter = ANY(%(encs)s)")
		args['encs'] = encounters
	if episodes is not None:
		where_parts.append("pk_episode = ANY(%(epis)s)")
		args['epis'] = episodes
	if issues is not None:
		where_parts.append("pk_health_issue = ANY(%(issues)s)")
		args['issues'] = issues
	SQL_journal = _SQL_get_generic_emr_items
	if len(where_parts) > 0:
		SQL_journal += '\nWHERE\n\t'
		SQL_journal += '\n\t\tAND '.join(where_parts)
	SQL = SQL_journal + '\n' + order_by
#	if active_encounter is None:
#		cmd = SQL_journal + '\n' + order_by
#	else:
#		args['pk_enc'] = active_encounter['pk_encounter']
#		args['enc_start'] = active_encounter['started']
#		args['enc_last_affirmed'] = active_encounter['last_affirmed']
#		args['enc_type'] = active_encounter['l10n_type']
#		args['enc_pat'] = active_encounter['pk_patient']
#		cmd = __SQL_union % (
#			SQL_journal,
#			_SQL_get_hints_as_generic_emr_items
#		) + '\n' + order_by
	rows = gmPG2.run_ro_query(sql = SQL, args = args)
	if return_pks:
		return [ {
			'src_table': r['src_table'],
			'src_pk': r['src_pk']
		} for r in rows ]

	return [ cGenericEMRItem(row = {
		'data': r,
		'pk_obj': {'src_table': r['src_table'], 'src_pk': r['src_pk']}
	} ) for r in rows ]

#------------------------------------------------------------
def generic_item_type_str(table):
	try:
		return _MAP_generic_emr_item_table2type_str[table]

	except KeyError:
		return _('unmapped entry type from table [%s]') % table

#============================================================
# main - unit testing
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	del _
	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain('gnumed')

	gmPG2.request_login_params(setup_pool = True)

	#--------------------------------------------------------
	def test_gen_item():
		for item in get_generic_emr_items (
			order_by = None,
			patient = 12,
			return_pks = False
		):
			print('------------------------------')
			print('\n'.join(item.formatted_tech_info))
#			print(item.format(eol = '\n'))
#			print(item.staff_id)
			input('<next>')
			#print(item.specialized_item)
			#input('<next>')

	#--------------------------------------------------------
	test_gen_item()
