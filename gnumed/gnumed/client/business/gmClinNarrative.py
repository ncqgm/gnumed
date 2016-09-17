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
		if cat not in gmSoapDefs.KNOWN_SOAP_CATS:
			conn_rollback()
			conn_close()
			raise ValueError(u'invalid SOAP category [%s] in <soap> dictionary: %s', cat, soap)
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
	"""
	# any of the args being None (except soap_cat) should fail the SQL code

	# sanity checks:

	# 1) silently do not insert empty narrative
	narrative = narrative.strip()
	if narrative == u'':
		return None

	# 2) also, silently do not insert true duplicates
	# FIXME: this should check for .provider = current_user but
	# FIXME: the view has provider mapped to their staff alias
	cmd = u"""
		SELECT * FROM clin.v_narrative
		WHERE
			pk_encounter = %(enc)s
				AND
			pk_episode = %(epi)s
				AND
			soap_cat = %(soap)s
				AND
			narrative = %(narr)s
	"""
	args = {
		'enc': encounter_id,
		'epi': episode_id,
		'soap': soap_cat,
		'narr': narrative
	}
	rows, idx = gmPG2.run_ro_queries(link_obj = link_obj, queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
	if len(rows) == 1:
		narrative = cNarrative(row = {'pk_field': 'pk_narrative', 'data': rows[0], 'idx': idx})
		return narrative

	# insert new narrative
	queries = [
		{'cmd': u"""
			INSERT INTO clin.clin_narrative
				(fk_encounter, fk_episode, narrative, soap_cat)
			VALUES
				(%s, %s, %s, lower(%s))""",
		 'args': [encounter_id, episode_id, narrative, soap_cat]
		},
		{'cmd': u"""
			SELECT * FROM clin.v_narrative
			WHERE
				pk_narrative = currval(pg_get_serial_sequence('clin.clin_narrative', 'pk'))"""
		}
	]
	rows, idx = gmPG2.run_rw_queries(link_obj = link_obj, queries = queries, return_data = True, get_col_idx = True)

	narrative = cNarrative(row = {'pk_field': 'pk_narrative', 'idx': idx, 'data': rows[0]})
	return narrative

#------------------------------------------------------------
def delete_clin_narrative(narrative=None):
	"""Deletes a clin.clin_narrative row by it's PK."""
	cmd = u"delete from clin.clin_narrative where pk=%s"
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
		order_by = u'ORDER BY c_vej.clin_when, c_vej.pk_episode, scr, c_vej.modified_when, c_vej.src_table'
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

	# get rows from clin.v_emr_journal
	cmd = u"""
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
		%s""" % (
			u'\n\t\t\t\t\tAND\n\t\t\t\t'.join(where_parts),
			order_by
		)
	journal_rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)

	if active_encounter is not None:
		# get rows from clin.get_hints_for_patient()
		pk_identity = journal_rows[0]['pk_patient']
		hints = gmAutoHints.get_hints_for_patient(pk_identity = pk_identity)
		for hint in hints:
			d = {}
			d['date'] = gmDateTime.pydt_strftime(active_encounter['started'], '%Y-%m-%d')
			d['clin_when'] = active_encounter['started']
			d['soap_cat'] = u'a'
			d['narrative'] = hint.format()
			d['src_table'] = u'ref.auto_hint'
			d['rank'] = 3									# FIXME: should be rank_of['a']
			d['modified_when'] = active_encounter['started']		# FIXME: should be hint['modified_when']
			d['date_modified'] = gmDateTime.pydt_strftime(active_encounter['started'], '%Y-%m-%d %H:%M')	# FIXME: should use hint['modified_when']
			d['modified_by'] = active_encounter['modified_by']		# FIXME: should be hint['modified_by']
			d['row_version'] = 0							# FIXME: should be hint['row_version']
			d['pk_episode'] = None
			d['pk_encounter'] = active_encounter['pk_encounter']
			d['real_soap_cat'] = u'a'
			d['src_pk'] = hint['pk_auto_hint']
			d['pk_health_issue'] = None
			d['health_issue'] = u''
			d['episode'] = u''
			d['issue_active'] = False
			d['issue_clinically_relevant'] = False
			d['episode_open'] = False
			d['encounter_started'] = active_encounter['started']
			d['encounter_last_affirmed'] = active_encounter['last_affirmed']
			d['encounter_l10n_type'] = active_encounter['l10n_type']
			d['pk_patient'] = pk_identity
			journal_rows.append(d)

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
		print "\nnarrative test"
		print	"--------------"
		narrative = cNarrative(aPK_obj=7)
		fields = narrative.get_fields()
		for field in fields:
			print field, ':', narrative[field]
		print "updatable:", narrative.get_updatable_fields()
		print "codes:", narrative.generic_codes
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
			print r
	#-----------------------------------------

	#test_search_text_across_emrs()
	test_narrative()
