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
	gmHooks.run_hook_script(hook = u'after_soap_modified')

gmDispatcher.connect(_on_soap_modified, u'clin.clin_narrative_mod_db')

#============================================================
class cNarrative(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one clinical free text entry."""

	_cmd_fetch_payload = u"SELECT * FROM clin.v_narrative WHERE pk_narrative = %s"
	_cmds_store_payload = [
		u"""update clin.clin_narrative set
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
		return self.format(fancy = True, width = 70).split(u'\n')

	#--------------------------------------------------------
	def format(self, left_margin=u'', fancy=False, width=75):

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
				initial_indent = u'',
				subsequent_indent = left_margin + u'   '
			)
		else:
			txt = u'%s [%s]: %s (%.8s)' % (
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

		cmd = u"""
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
		cmd = u"DELETE FROM clin.lnk_code2narrative WHERE fk_item = %(item)s AND fk_generic_code = %(code)s"
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

		cmd = gmCoding._SQL_get_generic_linked_codes % u'pk_generic_code IN %(pks)s'
		args = {'pks': tuple(self._payload[self._idx['pk_generic_codes']])}
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
		return [ gmCoding.cGenericLinkedCode(row = {'data': r, 'idx': idx, 'pk_field': 'pk_lnk_code2item'}) for r in rows ]

	def _set_generic_codes(self, pk_codes):
		queries = []
		# remove all codes
		if len(self._payload[self._idx['pk_generic_codes']]) > 0:
			queries.append ({
				'cmd': u'DELETE FROM clin.lnk_code2narrative WHERE fk_item = %(narr)s AND fk_generic_code IN %(codes)s',
				'args': {
					'narr': self._payload[self._idx['pk_narrative']],
					'codes': tuple(self._payload[self._idx['pk_generic_codes']])
				}
			})
		# add new codes
		for pk_code in pk_codes:
			queries.append ({
				'cmd': u'INSERT INTO clin.lnk_code2narrative (fk_item, fk_generic_code) VALUES (%(narr)s, %(pk_code)s)',
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

	if not gmSoapDefs.are_valid_soap_cats(soap.keys(), allow_upper = True):
		raise ValueError(u'invalid SOAP category in <soap> dictionary: %s', soap)

	if link_obj is None:
		link_obj = gmPG2.get_connection(readonly = False)
		conn_rollback = link_obj.rollback
		conn_commit = link_obj.commit
		conn_close = link_obj.close
	else:
		conn_rollback = lambda x:x
		conn_commit = lambda x:x
		conn_close = lambda x:x

	instances = {}
	for cat in soap:
		val = soap[cat]
		if val is None:
			continue
		if u''.join([ v.strip() for v in val ]) == u'':
			continue
		instance = create_narrative_item (
			narrative = u'\n'.join([ v.strip() for v in val ]),
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
	if narrative == u'':
		return None

	args = {'enc': encounter_id, 'epi': episode_id, 'soap': soap_cat, 'narr': narrative}

	# insert new narrative
	# but, also silently, do not insert true duplicates
	# this should check for .provider = current_user but
	# the view has provider mapped to their staff alias
	cmd = u"""
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
	cmd = u"""
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
	cmd = u"DELETE FROM clin.clin_narrative WHERE pk=%s"
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
	where_parts = [u'TRUE']
	args = {}

	if encounters is not None:
		where_parts.append(u'pk_encounter IN %(encs)s')
		args['encs'] = tuple(encounters)

	if episodes is not None:
		where_parts.append(u'pk_episode IN %(epis)s')
		args['epis'] = tuple(episodes)

	if issues is not None:
		where_parts.append(u'pk_health_issue IN %(issues)s')
		args['issues'] = tuple(issues)

	if patient is not None:
		where_parts.append(u'pk_patient = %(pat)s')
		args['pat'] = patient

	if soap_cats is not None:
		where_parts.append(u'c_vn.soap_cat IN %(soap_cats)s')
		args['soap_cats'] = tuple(soap_cats)

	if order_by is None:
		order_by = u'ORDER BY date, soap_rank'
	else:
		order_by = u'ORDER BY %s' % order_by

	cmd = u"""
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
		u' AND '.join(where_parts),
		order_by
	)

	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)

	filtered_narrative = [ cNarrative(row = {'pk_field': 'pk_narrative', 'idx': idx, 'data': row}) for row in rows ]

	if since is not None:
		filtered_narrative = filter(lambda narr: narr['date'] >= since, filtered_narrative)

	if until is not None:
		filtered_narrative = filter(lambda narr: narr['date'] < until, filtered_narrative)

	if providers is not None:
		filtered_narrative = filter(lambda narr: narr['modified_by'] in providers, filtered_narrative)

	return filtered_narrative

#	if issues is not None:
#		filtered_narrative = filter(lambda narr: narr['pk_health_issue'] in issues, filtered_narrative)
#
#	if episodes is not None:
#		filtered_narrative = filter(lambda narr: narr['pk_episode'] in episodes, filtered_narrative)
#
#	if encounters is not None:
#		filtered_narrative = filter(lambda narr: narr['pk_encounter'] in encounters, filtered_narrative)

#	if soap_cats is not None:
#		soap_cats = map(lambda c: c.lower(), soap_cats)
#		filtered_narrative = filter(lambda narr: narr['soap_cat'] in soap_cats, filtered_narrative)

#------------------------------------------------------------
def get_as_journal(since=None, until=None, encounters=None, episodes=None, issues=None, soap_cats=None, providers=None, order_by=None, time_range=None, patient=None, active_encounter=None):

	if (patient is None) and (episodes is None) and (issues is None) and (encounters is None):
		raise ValueError('at least one of <patient>, <episodes>, <issues>, <encounters> must not be None')

	if order_by is None:
		order_by = u'ORDER BY clin_when, pk_episode, scr, modified_when, src_table'
	else:
		order_by = u'ORDER BY %s' % order_by

	where_parts = []
	args = {}

	if patient is not None:
		where_parts.append(u'c_vej.pk_patient = %(pat)s')
		args['pat'] = patient

	if soap_cats is not None:
		# work around bug in psycopg2 not being able to properly
		# adapt None to NULL inside tuples
		if None in soap_cats:
			where_parts.append(u'((c_vej.soap_cat IN %(soap_cat)s) OR (c_vej.soap_cat IS NULL))')
			soap_cats.remove(None)
		else:
			where_parts.append(u'c_vej.soap_cat IN %(soap_cat)s')
		args['soap_cat'] = tuple(soap_cats)

	if time_range is not None:
		where_parts.append(u"c_vej.clin_when > (now() - '%s days'::interval)" % time_range)

	if episodes is not None:
		where_parts.append(u"c_vej.pk_episode IN %(epis)s")
		args['epis'] = tuple(episodes)

	if issues is not None:
		where_parts.append(u"c_vej.pk_health_issue IN %(issues)s")
		args['issues'] = tuple(issues)

	# FIXME: implement more constraints

	cmd_journal = u"""
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
	""" % u'\n\t\t\t\t\tAND\n\t\t\t\t'.join(where_parts)

	if active_encounter is None:
		cmd = cmd_journal + u'\n ' + order_by
	else:
		args['pk_enc'] = active_encounter['pk_encounter']
		args['enc_start'] = active_encounter['started']
		args['enc_last_affirmed'] = active_encounter['last_affirmed']
		args['enc_type'] = active_encounter['l10n_type']
		args['enc_pat'] = active_encounter['pk_patient']
		cmd_hints = u"""
			SELECT
				to_char(now(), 'YYYY-MM-DD') AS date,
				now() as clin_when,
				'a'::text as soap_cat,
				hints.title || E'\n' || hints.hint
					as narrative,
				'ref.auto_hint'::text as src_table,
				c_scr.rank AS scr,
				now() as modified_when,
				to_char(now(), 'YYYY-MM-DD HH24:MI') AS date_modified,
				current_user as modified_by,
				0::integer as row_version,
				NULL::integer as pk_episode,
				%(pk_enc)s as pk_encounter,
				'a'::text as real_soap_cat,
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
				clin.get_hints_for_patient(%(enc_pat)s) as hints
					join clin.soap_cat_ranks c_scr on (c_scr.soap_cat = 'a')
		"""
		cmd = cmd_journal + u'\nUNION ALL\n' + cmd_hints + u'\n' + order_by

	journal_rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)

	return journal_rows

#============================================================
# convenience functions
#============================================================
def search_text_across_emrs(search_term=None):

	if search_term is None:
		return []

	if search_term.strip() == u'':
		return []

	cmd = u'select * from clin.v_narrative4search where narrative ~* %(term)s order by pk_patient limit 1000'
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': {'term': search_term}}], get_col_idx = False)

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
