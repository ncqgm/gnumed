"""GNUmed clinical narrative business object."""
#============================================================
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>, Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL v2 or later (for details see http://gnu.org)'

import sys
import logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmBusinessDBObject
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDispatcher
from Gnumed.pycommon import gmHooks
from Gnumed.pycommon import gmDateTime

from Gnumed.business import gmCoding
from Gnumed.business import gmSoapDefs
from Gnumed.business import gmAutoHints


_log = logging.getLogger('gm.emr')

#============================================================
def _on_soap_modified():
	"""Always relates to the active patient."""
	gmHooks.run_hook_script(hook = 'after_soap_modified')

gmDispatcher.connect(_on_soap_modified, 'clin.clin_narrative_mod_db')

#============================================================
class cNarrative(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one clinical free text entry."""

	_cmd_fetch_payload = "SELECT * FROM clin.v_narrative WHERE pk_narrative = %s"
	_cmds_store_payload = [
		"""update clin.clin_narrative set
				narrative = %(narrative)s,
				clin_when = %(date)s,
				soap_cat = lower(%(soap_cat)s),
				fk_encounter = %(pk_encounter)s,
				fk_episode = %(pk_episode)s
			WHERE
				pk = %(pk_narrative)s
					AND
				xmin = %(xmin_clin_narrative)s
			RETURNING
				xmin AS xmin_clin_narrative"""
		]

	_updatable_fields = [
		'narrative',
		'date',
		'soap_cat',
		'pk_episode',
		'pk_encounter'
	]

	#--------------------------------------------------------
	def format_maximum_information(self, patient=None):
		return self.format(fancy = True, width = 70).split('\n')

	#--------------------------------------------------------
	def format(self, left_margin='', fancy=False, width=75):

		if fancy:
			txt = gmTools.wrap (
				text = _('%s: %s by %.8s (v%s)\n%s') % (
					self._payload[self._idx['date']].strftime('%x %H:%M'),
					gmSoapDefs.soap_cat2l10n_str[self._payload[self._idx['soap_cat']]],
					self._payload[self._idx['modified_by']],
					self._payload[self._idx['row_version']],
					self._payload[self._idx['narrative']]
				),
				width = width,
				initial_indent = '',
				subsequent_indent = left_margin + '   '
			)
		else:
			txt = '%s [%s]: %s (%.8s)' % (
				self._payload[self._idx['date']].strftime('%x %H:%M'),
				gmSoapDefs.soap_cat2l10n[self._payload[self._idx['soap_cat']]],
				self._payload[self._idx['narrative']],
				self._payload[self._idx['modified_by']]
			)
			if len(txt) > width:
				txt = txt[:width] + gmTools.u_ellipsis

		return txt

	#--------------------------------------------------------
	def add_code(self, pk_code=None):
		"""<pk_code> must be a value from ref.coding_system_root.pk_coding_system (clin.lnk_code2item_root.fk_generic_code)"""

		if pk_code in self._payload[self._idx['pk_generic_codes']]:
			return

		cmd = """
			INSERT INTO clin.lnk_code2narrative
				(fk_item, fk_generic_code)
			SELECT
				%(item)s,
				%(code)s
			WHERE NOT EXISTS (
				SELECT 1 FROM clin.lnk_code2narrative
				WHERE
					fk_item = %(item)s
						AND
					fk_generic_code = %(code)s
			)"""
		args = {
			'item': self._payload[self._idx['pk_narrative']],
			'code': pk_code
		}
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
		return

	#--------------------------------------------------------
	def remove_code(self, pk_code=None):
		"""<pk_code> must be a value from ref.coding_system_root.pk_coding_system (clin.lnk_code2item_root.fk_generic_code)"""
		cmd = "DELETE FROM clin.lnk_code2narrative WHERE fk_item = %(item)s AND fk_generic_code = %(code)s"
		args = {
			'item': self._payload[self._idx['pk_narrative']],
			'code': pk_code
		}
		rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
		return True

	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_generic_codes(self):
		if len(self._payload[self._idx['pk_generic_codes']]) == 0:
			return []

		cmd = gmCoding._SQL_get_generic_linked_codes % 'pk_generic_code IN %(pks)s'
		args = {'pks': tuple(self._payload[self._idx['pk_generic_codes']])}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ gmCoding.cGenericLinkedCode(row = {'data': r, 'idx': idx, 'pk_field': 'pk_lnk_code2item'}) for r in rows ]

	def _set_generic_codes(self, pk_codes):
		queries = []
		# remove all codes
		if len(self._payload[self._idx['pk_generic_codes']]) > 0:
			queries.append ({
				'cmd': 'DELETE FROM clin.lnk_code2narrative WHERE fk_item = %(narr)s AND fk_generic_code IN %(codes)s',
				'args': {
					'narr': self._payload[self._idx['pk_narrative']],
					'codes': tuple(self._payload[self._idx['pk_generic_codes']])
				}
			})
		# add new codes
		for pk_code in pk_codes:
			queries.append ({
				'cmd': 'INSERT INTO clin.lnk_code2narrative (fk_item, fk_generic_code) VALUES (%(narr)s, %(pk_code)s)',
				'args': {
					'narr': self._payload[self._idx['pk_narrative']],
					'pk_code': pk_code
				}
			})
		if len(queries) == 0:
			return
		# run it all in one transaction
		rows, idx = gmPG2.run_rw_queries(queries = queries)
		return

	generic_codes = property(_get_generic_codes, _set_generic_codes)

#============================================================
def create_progress_note(soap=None, episode_id=None, encounter_id=None, link_obj=None):
	"""Create clinical narrative entries.

	<soap>
		must be a dict, the keys being SOAP categories (including U and
		None=admin) and the values being text (possibly multi-line)

	Existing but empty ('' or None) categories are skipped.
	"""
	if soap is None:
		return True

	if not gmSoapDefs.are_valid_soap_cats(list(soap), allow_upper = True):
		raise ValueError('invalid SOAP category in <soap> dictionary: %s', soap)

	if link_obj is None:
		link_obj = gmPG2.get_connection(readonly = False)
		conn_rollback = link_obj.rollback
		conn_commit = link_obj.commit
		conn_close = link_obj.close
	else:
		conn_rollback = lambda *x:None
		conn_commit = lambda *x:None
		conn_close = lambda *x:None

	instances = {}
	for cat in soap:
		val = soap[cat]
		if val is None:
			continue
		if ''.join([ v.strip() for v in val ]) == '':
			continue
		instance = create_narrative_item (
			narrative = '\n'.join([ v.strip() for v in val ]),
			soap_cat = cat,
			episode_id = episode_id,
			encounter_id = encounter_id,
			link_obj = link_obj
		)
		if instance is None:
			continue
		instances[cat] = instance

	conn_commit()
	conn_close()
	return instances

#============================================================
def create_narrative_item(narrative=None, soap_cat=None, episode_id=None, encounter_id=None, link_obj=None):
	"""Creates a new clinical narrative entry

		narrative - free text clinical narrative
		soap_cat - soap category
		episode_id - episodes's primary key
		encounter_id - encounter's primary key

		any of the args being None (except soap_cat) will fail the SQL code
	"""
	# silently do not insert empty narrative
	narrative = narrative.strip()
	if narrative == '':
		return None

	args = {'enc': encounter_id, 'epi': episode_id, 'soap': soap_cat, 'narr': narrative}

	# insert new narrative
	# but, also silently, do not insert true duplicates
	# this should check for .provider = current_user but
	# the view has provider mapped to their staff alias
	cmd = """
		INSERT INTO clin.clin_narrative
			(fk_encounter, fk_episode, narrative, soap_cat)
		SELECT
			%(enc)s, %(epi)s, %(narr)s, lower(%(soap)s)
		WHERE NOT EXISTS (
			SELECT 1 FROM clin.v_narrative
			WHERE
				pk_encounter = %(enc)s
					AND
				pk_episode = %(epi)s
					AND
				soap_cat = lower(%(soap)s)
					AND
				narrative = %(narr)s
		)
		RETURNING pk"""
	rows, idx = gmPG2.run_rw_queries(link_obj = link_obj, queries = [{'cmd': cmd, 'args': args}], return_data = True, get_col_idx = False)
	if len(rows) == 1:
		# re-use same link_obj if given because when called from create_progress_note we won't yet see rows inside a new tx
		return cNarrative(aPK_obj = rows[0]['pk'], link_obj = link_obj)

	if len(rows) > 1:
		raise Exception('more than one row returned from single-row INSERT')

	# retrieve existing narrative
	cmd = """
		SELECT * FROM clin.v_narrative
		WHERE
			pk_encounter = %(enc)s
				AND
			pk_episode = %(epi)s
				AND
			soap_cat = lower(%(soap)s)
				AND
			narrative = %(narr)s
	"""
	rows, idx = gmPG2.run_ro_queries(link_obj = link_obj, queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
	if len(rows) == 1:
		return cNarrative(row = {'pk_field': 'pk_narrative', 'data': rows[0], 'idx': idx})

	raise Exception('retrieving known-to-exist narrative row returned 0 or >1 result: %s' % len(rows))

#------------------------------------------------------------
def delete_clin_narrative(narrative=None):
	"""Deletes a clin.clin_narrative row by it's PK."""
	cmd = "DELETE FROM clin.clin_narrative WHERE pk=%s"
	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': [narrative]}])
	return True

#------------------------------------------------------------
def get_narrative(since=None, until=None, encounters=None, episodes=None, issues=None, soap_cats=None, providers=None, patient=None, order_by=None):
	"""Get SOAP notes pertinent to this encounter.

		since
			- initial date for narrative items
		until
			- final date for narrative items
		encounters
			- list of encounters whose narrative are to be retrieved
		episodes
			- list of episodes whose narrative are to be retrieved
		issues
			- list of health issues whose narrative are to be retrieved
		soap_cats
			- list of SOAP categories of the narrative to be retrieved
	"""
	where_parts = ['TRUE']
	args = {}

	if encounters is not None:
		where_parts.append('pk_encounter IN %(encs)s')
		args['encs'] = tuple(encounters)

	if episodes is not None:
		where_parts.append('pk_episode IN %(epis)s')
		args['epis'] = tuple(episodes)

	if issues is not None:
		where_parts.append('pk_health_issue IN %(issues)s')
		args['issues'] = tuple(issues)

	if patient is not None:
		where_parts.append('pk_patient = %(pat)s')
		args['pat'] = patient

	if soap_cats is not None:
		where_parts.append('c_vn.soap_cat IN %(soap_cats)s')
		args['soap_cats'] = tuple(soap_cats)

	if order_by is None:
		order_by = 'ORDER BY date, soap_rank'
	else:
		order_by = 'ORDER BY %s' % order_by

	cmd = """
		SELECT
			c_vn.*,
			c_scr.rank AS soap_rank
		FROM
			clin.v_narrative c_vn
				LEFT JOIN clin.soap_cat_ranks c_scr ON c_vn.soap_cat = c_scr.soap_cat
		WHERE
			%s
		%s
	""" % (
		' AND '.join(where_parts),
		order_by
	)

	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)

	filtered_narrative = [ cNarrative(row = {'pk_field': 'pk_narrative', 'idx': idx, 'data': row}) for row in rows ]

	if since is not None:
		filtered_narrative = [ narr for narr in filtered_narrative if narr['date'] >= since ]

	if until is not None:
		filtered_narrative = [ narr for narr in filtered_narrative if narr['date'] < until ]

	if providers is not None:
		filtered_narrative = [ narr for narr in filtered_narrative if narr['modified_by'] in providers ]

	return filtered_narrative

#	if issues is not None:
#		filtered_narrative = (lambda narr: narr['pk_health_issue'] in issues, filtered_narrative)
#
#	if episodes is not None:
#		filtered_narrative = (lambda narr: narr['pk_episode'] in episodes, filtered_narrative)
#
#	if encounters is not None:
#		filtered_narrative = (lambda narr: narr['pk_encounter'] in encounters, filtered_narrative)

#	if soap_cats is not None:
#		soap_cats = map(lambda c: c.lower(), soap_cats)
#		filtered_narrative = (lambda narr: narr['soap_cat'] in soap_cats, filtered_narrative)

#------------------------------------------------------------
def get_as_journal(since=None, until=None, encounters=None, episodes=None, issues=None, soap_cats=None, providers=None, order_by=None, time_range=None, patient=None, active_encounter=None):

	if (patient is None) and (episodes is None) and (issues is None) and (encounters is None):
		raise ValueError('at least one of <patient>, <episodes>, <issues>, <encounters> must not be None')

	if order_by is None:
		order_by = 'ORDER BY clin_when, pk_episode, scr, modified_when, src_table'
	else:
		order_by = 'ORDER BY %s' % order_by

	where_parts = []
	args = {}

	if patient is not None:
		where_parts.append('c_vej.pk_patient = %(pat)s')
		args['pat'] = patient

	if soap_cats is not None:
		# work around bug in psycopg2 not being able to properly
		# adapt None to NULL inside tuples
		if None in soap_cats:
			where_parts.append('((c_vej.soap_cat IN %(soap_cat)s) OR (c_vej.soap_cat IS NULL))')
			soap_cats.remove(None)
		else:
			where_parts.append('c_vej.soap_cat IN %(soap_cat)s')
		args['soap_cat'] = tuple(soap_cats)

	if time_range is not None:
		where_parts.append("c_vej.clin_when > (now() - '%s days'::interval)" % time_range)

	if episodes is not None:
		where_parts.append("c_vej.pk_episode IN %(epis)s")
		args['epis'] = tuple(episodes)

	if issues is not None:
		where_parts.append("c_vej.pk_health_issue IN %(issues)s")
		args['issues'] = tuple(issues)

	# FIXME: implement more constraints

	cmd_journal = """
		SELECT
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
			c_vej.pk_patient
		FROM
			clin.v_emr_journal c_vej
				join clin.soap_cat_ranks c_scr on (c_scr.soap_cat IS NOT DISTINCT FROM c_vej.soap_cat)
		WHERE
			%s
	""" % '\n\t\t\t\t\tAND\n\t\t\t\t'.join(where_parts)

	if active_encounter is None:
		cmd = cmd_journal + '\n ' + order_by
	else:
		args['pk_enc'] = active_encounter['pk_encounter']
		args['enc_start'] = active_encounter['started']
		args['enc_last_affirmed'] = active_encounter['last_affirmed']
		args['enc_type'] = active_encounter['l10n_type']
		args['enc_pat'] = active_encounter['pk_patient']
		cmd_hints = """
			SELECT
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
				0::integer as row_version,
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
				%(enc_pat)s as pk_patient
			FROM
				clin.get_hints_for_patient(%(enc_pat)s) AS hints
					JOIN clin.soap_cat_ranks c_scr ON (c_scr.soap_cat = 'u')
		"""
		cmd = cmd_journal + '\nUNION ALL\n' + cmd_hints + '\n' + order_by

	journal_rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)

	return journal_rows

#============================================================
# convenience functions
#============================================================
_VIEW_clin_v_narrative4search = u"""
create temporary view v_narrative4search as

select * from (

	-- clin.clin_root_items
	select
		vpi.pk_patient as pk_patient,
		vpi.soap_cat as soap_cat,
		vpi.narrative as narrative,
		vpi.pk_encounter as pk_encounter,
		vpi.pk_episode as pk_episode,
		vpi.pk_health_issue as pk_health_issue,
		vpi.pk_item as src_pk,
		vpi.src_table as src_table
	from
		clin.v_pat_items vpi
	where
		src_table not in (
			'clin.allergy',
			'clin.test_result',
			'clin.procedure',
			'clin.substance_intake',
			'clin.family_history'
		)


	union all

		select * from clin.v_subst_intake4narr_search
		where gm.is_null_or_blank_string(narrative) is FALSE


	union all
	select		-- clin.procedure
		(select fk_patient from clin.encounter where pk = cpr.fk_encounter)
			as pk_patient,
		cpr.soap_cat
			as soap_cat,
		cpr.narrative
			as narrative,
		cpr.fk_encounter
			as pk_encounter,
		cpr.fk_episode
			as pk_episode,
		(select fk_health_issue from clin.episode where pk = cpr.fk_episode)
			as pk_health_issue,
		cpr.pk
			as src_pk,
		'clin.procedure'
			as src_table
	from
		clin.procedure cpr
	where
		cpr.narrative is not NULL


	union all
	select		-- test results
		(select fk_patient from clin.encounter where pk = ctr.fk_encounter)
			as pk_patient,
		ctr.soap_cat
			as soap_cat,
		coalesce(ctr.narrative, '')
			|| coalesce(' ' || ctr.val_alpha, '')
			|| coalesce(' ' || ctr.val_unit, '')
			|| coalesce(' ' || ctr.val_normal_range, '')
			|| coalesce(' ' || ctr.val_target_range, '')
			|| coalesce(' ' || ctr.norm_ref_group, '')
			|| coalesce(' ' || ctr.note_test_org, '')
			|| coalesce(' ' || ctr.material, '')
			|| coalesce(' ' || ctr.material_detail, '')
			as narrative,
		ctr.fk_encounter
			as pk_encounter,
		ctr.fk_episode
			as pk_episode,
		(select fk_health_issue from clin.episode where pk = ctr.fk_episode)
			as pk_health_issue,
		ctr.pk
			as src_pk,
		'clin.test_result'
			as src_table
	from
		clin.test_result ctr


	union all	-- test result reviews
	select
		(select fk_patient from clin.encounter where pk =
			(select fk_encounter from clin.test_result where clin.test_result.pk = crtr.fk_reviewed_row)
		)
			as pk_patient,
		'o'::text
			as soap_cat,
		crtr.comment
			as narrative,
		(select fk_encounter from clin.test_result where clin.test_result.pk = crtr.fk_reviewed_row)
			as pk_encounter,
		(select fk_episode from clin.test_result where clin.test_result.pk = crtr.fk_reviewed_row)
			as pk_episode,
		(select fk_health_issue from clin.episode where pk =
			(select fk_episode from clin.test_result where clin.test_result.pk = crtr.fk_reviewed_row)
		)
			as pk_health_issue,
		crtr.pk
			as src_pk,
		'clin.reviewed_test_results'
			as src_table
	from
		clin.reviewed_test_results crtr


	union all
	select -- allergy state
		(select fk_patient from clin.encounter where pk = cas.fk_encounter)
			as pk_patient,
		'o'::text
			as soap_cat,
		cas.comment
			as narrative,
		cas.fk_encounter
			as pk_encounter,
		null
			as pk_episode,
		null
			as pk_health_issue,
		cas.pk
			as src_pk,
		'clin.allergy_state'
			as src_table
	from
		clin.allergy_state cas
	where
		cas.comment is not NULL


	union all
	select -- allergies
		(select fk_patient from clin.encounter where pk = ca.fk_encounter)
			as pk_patient,
		ca.soap_cat
			as soap_cat,
		coalesce(narrative, '')
			|| coalesce(' ' || substance, '')
			|| coalesce(' ' || substance_code, '')
			|| coalesce(' ' || generics, '')
			|| coalesce(' ' || allergene, '')
			|| coalesce(' ' || atc_code, '')
			as narrative,
		ca.fk_encounter
			as pk_encounter,
		ca.fk_episode
			as pk_episode,
		(select fk_health_issue from clin.episode where pk = ca.fk_episode)
			as pk_health_issue,
		ca.pk
			as src_pk,
		'clin.allergy'
			as src_table
	from
		clin.allergy ca


	union all	-- health issues
	select
		(select fk_patient from clin.encounter where pk = chi.fk_encounter)
			as pk_patient,
		'a' as soap_cat,
		chi.description
			|| coalesce(' ' || chi.summary, '')
			as narrative,
		chi.fk_encounter
			as pk_encounter,
		null
			as pk_episode,
		chi.pk
			as pk_health_issue,
		chi.pk
			as src_pk,
		'clin.health_issue'
			as src_table
	from
		clin.health_issue chi


	union all	-- encounters
	select
		cenc.fk_patient as pk_patient,
		's' as soap_cat,
		coalesce(cenc.reason_for_encounter, '')
			|| coalesce(' ' || cenc.assessment_of_encounter, '')
			as narrative,
		cenc.pk as pk_encounter,
		null as pk_episode,
		null as pk_health_issue,
		cenc.pk as src_pk,
		'clin.encounter' as src_table
	from
		clin.encounter cenc


	union all	-- episodes
	select
		(select fk_patient from clin.encounter where pk = cep.fk_encounter)
			as pk_patient,
		's' as soap_cat,
		cep.description
			|| coalesce(' ' || cep.summary, '')
			as narrative,
		cep.fk_encounter
			as pk_encounter,
		cep.pk
			as pk_episode,
		cep.fk_health_issue
			as pk_health_issue,
		cep.pk
			as src_pk,
		'clin.episode'
			as src_table
	from
		clin.episode cep


	union all	-- family history
	select
		c_vfhx.pk_patient,
		c_vfhx.soap_cat,
		(c_vfhx.relation || ' / ' || c_vfhx.l10n_relation || ' '
		 || c_vfhx.name_relative || ': '
		 || c_vfhx.condition
		) as narrative,
		c_vfhx.pk_encounter,
		c_vfhx.pk_episode,
		c_vfhx.pk_health_issue,
		c_vfhx.pk_family_history as src_pk,
		'clin.family_history' as src_table
	from
		clin.v_family_history c_vfhx


	union all	-- documents
	select
		vdm.pk_patient as pk_patient,
		'o' as soap_cat,
		(vdm.l10n_type || ' ' ||
		 coalesce(vdm.ext_ref, '') || ' ' ||
		 coalesce(vdm.comment, '')
		) as narrative,
		vdm.pk_encounter as pk_encounter,
		vdm.pk_episode as pk_episode,
		vdm.pk_health_issue as pk_health_issue,
		vdm.pk_doc as src_pk,
		'blobs.doc_med' as src_table
	from
		blobs.v_doc_med vdm


	union all	-- document objects
	select
		vo4d.pk_patient as pk_patient,
		'o' as soap_cat,
		vo4d.obj_comment as narrative,
		vo4d.pk_encounter as pk_encounter,
		vo4d.pk_episode as pk_episode,
		vo4d.pk_health_issue as pk_health_issue,
		vo4d.pk_obj as src_pk,
		'blobs.doc_obj' as src_table
	from
		blobs.v_obj4doc_no_data vo4d


	union all	-- document descriptions
	select
		vdd.pk_patient as pk_patient,
		'o' as soap_cat,
		vdd.description as narrative,
		vdd.pk_encounter as pk_encounter,
		vdd.pk_episode as pk_episode,
		vdd.pk_health_issue as pk_health_issue,
		vdd.pk_doc_desc as src_pk,
		'blobs.doc_desc' as src_table
	from
		blobs.v_doc_desc vdd


	union all	-- reviewed documents
	select
		vrdo.pk_patient as pk_patient,
		's' as soap_cat,
		vrdo.comment as narrative,
		null as pk_encounter,
		vrdo.pk_episode as pk_episode,
		vrdo.pk_health_issue as pk_health_issue,
		vrdo.pk_review_root as src_pk,
		'blobs.v_reviewed_doc_objects' as src_table
	from
		blobs.v_reviewed_doc_objects vrdo


	union all	-- patient tags
	select
		d_vit.pk_identity
			as pk_patient,
		's' as soap_cat,
		d_vit.l10n_description
			|| coalesce(' ' || d_vit.comment, '')
			as narrative,
		null
			as pk_encounter,
		null
			as pk_episode,
		null
			as pk_health_issue,
		d_vit.pk_identity_tag
			as src_pk,
		'dem.v_identity_tags'
			as src_table
	from
		dem.v_identity_tags d_vit


	union all	-- external care
	select
		c_vec.pk_identity
			as pk_patient,
		's' as soap_cat,
		case
			when c_vec.pk_health_issue is null then
				coalesce(c_vec.issue, '')
				|| coalesce(' / ' || c_vec.provider, '')
				|| coalesce(' / ' || c_vec.comment, '')
			else
				coalesce(c_vec.provider, '')
				|| coalesce(' / ' || c_vec.comment, '')
		end as narrative,
		c_vec.pk_encounter
			as pk_encounter,
		null
			as pk_episode,
		c_vec.pk_health_issue
			as pk_health_issue,
		c_vec.pk_external_care
			as src_pk,
		'clin.v_external_care'
			as src_table
	from
		clin.v_external_care c_vec


	union all	-- export items
	select
		c_vei.pk_identity
			as pk_patient,
		's' as soap_cat,
		case
			when c_vei.pk_doc_obj is null then
				coalesce(c_vei.description, '')
				|| coalesce(' / ' || c_vei.filename, '')
			else
				coalesce(c_vei.description, '')
		end as narrative,
		null
			as pk_encounter,
		null
			as pk_episode,
		null
			as pk_health_issue,
		c_vei.pk_export_item
			as src_pk,
		'clin.v_export_items'
			as src_table
	from
		clin.v_export_items c_vei


	union all	-- hint suppression rationale
	select
		(select fk_patient from clin.encounter where pk = c_sh.fk_encounter)
			as pk_patient,
		'p' as soap_cat,
		c_sh.rationale
			as narrative,
		c_sh.fk_encounter
			as pk_encounter,
		null
			as pk_episode,
		null
			as pk_health_issue,
		c_sh.pk
			as src_pk,
		'clin.suppressed_hint'
			as src_table
	from
		clin.suppressed_hint c_sh


	-- add in demographics ----------------

	union all	-- tags on patients
	SELECT
		d_it.fk_identity
			AS pk_patient,
		'u' AS soap_cat,
		d_it.comment
			AS narrative,
		NULL
			AS pk_encounter,
		NULL
			AS pk_episode,
		NULL
			AS pk_health_issue,
		d_it.pk
			AS src_pk,
		'dem.identity_tag'
			AS src_table
	FROM
		dem.identity_tag d_it


	union all	-- job description
	SELECT
		d_lj2p.fk_identity
			AS pk_patient,
		'u' AS soap_cat,
		d_lj2p.activities
			AS narrative,
		NULL
			AS pk_encounter,
		NULL
			AS pk_episode,
		NULL
			AS pk_health_issue,
		d_lj2p.pk
			AS src_pk,
		'dem.lnk_job2person'
			AS src_table
	FROM
		dem.lnk_job2person d_lj2p


	union all	-- comm channel comment
	SELECT
		d_li2c.fk_identity
			AS pk_patient,
		'u' AS soap_cat,
		d_li2c.comment
			AS narrative,
		NULL
			AS pk_encounter,
		NULL
			AS pk_episode,
		NULL
			AS pk_health_issue,
		d_li2c.pk
			AS src_pk,
		'dem.lnk_identity2comm'
			AS src_table
	FROM
		dem.lnk_identity2comm d_li2c


	union all	-- external ID comment
	SELECT
		d_li2e.id_identity
			AS pk_patient,
		'u' AS soap_cat,
		d_li2e.comment
			AS narrative,
		NULL
			AS pk_encounter,
		NULL
			AS pk_episode,
		NULL
			AS pk_health_issue,
		d_li2e.id
			AS src_pk,
		'dem.lnk_identity2ext_id'
			AS src_table
	FROM
		dem.lnk_identity2ext_id d_li2e

	union all	-- message inbox comment
	SELECT
		d_mi.fk_patient
			AS pk_patient,
		'u' AS soap_cat,
		d_mi.comment
			AS narrative,
		NULL
			AS pk_encounter,
		NULL
			AS pk_episode,
		NULL
			AS pk_health_issue,
		d_mi.pk
			AS src_pk,
		'dem.message_inbox'
			AS src_table
	FROM
		dem.message_inbox d_mi

	-- end demographics data --------------

) AS union_table

where
	trim(coalesce(union_table.narrative, '')) != ''
;
"""


def search_text_across_emrs(search_term=None):

	if search_term is None:
		return []

	if search_term.strip() == '':
		return []

	#cmd = u'select * from clin.v_narrative4search where narrative ~* %(term)s order by pk_patient limit 1000'
	#rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {'term': search_term}}], get_col_idx = False)
	cmd = u'SELECT * FROM v_narrative4search WHERE narrative ~* %(term)s ORDER BY pk_patient LIMIT 1000'
	queries = [
		{'cmd': _VIEW_clin_v_narrative4search},
		{'cmd': cmd, 'args': {'term': search_term}}
	]
	rows, idx = gmPG2.run_rw_queries(queries = queries, get_col_idx = True, return_data = True)
	return rows

#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain(domain = 'gnumed')

	#-----------------------------------------
	def test_narrative():
		print("\nnarrative test")
		print("--------------")
		narrative = cNarrative(aPK_obj=7)
		fields = narrative.get_fields()
		for field in fields:
			print(field, ':', narrative[field])
		print("updatable:", narrative.get_updatable_fields())
		print("codes:", narrative.generic_codes)
		#print "adding code..."
		#narrative.add_code('Test code', 'Test coding system')
		#print "codes:", diagnose.get_codes()

		#print "creating narrative..."
		#new_narrative = create_narrative_item(narrative = 'Test narrative', soap_cat = 'a', episode_id=1, encounter_id=2)
		#print new_narrative

	#-----------------------------------------
	def test_search_text_across_emrs():
		results = search_text_across_emrs('cut')
		for r in results:
			print(r)
	#-----------------------------------------

	#test_search_text_across_emrs()
	test_narrative()
