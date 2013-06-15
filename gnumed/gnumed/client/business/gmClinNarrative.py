"""GNUmed clinical narrative business object."""
#============================================================
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>, Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL v2 or later (for details see http://gnu.org)'

import sys, logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2, gmExceptions, gmBusinessDBObject, gmTools, gmDispatcher, gmHooks
from Gnumed.business import gmCoding


try:
	_('dummy-no-need-to-translate-but-make-epydoc-happy')
except NameError:
	_ = lambda x:x


_log = logging.getLogger('gm.emr')


soap_cat2l10n = {
	u's': _('soap_S').replace(u'soap_', u''),
	u'o': _('soap_O').replace(u'soap_', u''),
	u'a': _('soap_A').replace(u'soap_', u''),
	u'p': _('soap_P').replace(u'soap_', u''),
	u'u': _('soap_U').replace(u'soap_', u''),
#	u'u': u'?',
	None: gmTools.u_ellipsis,
	u'': gmTools.u_ellipsis
}

soap_cat2l10n_str = {
	u's': _('soap_Subjective').replace(u'soap_', u''),
	u'o': _('soap_Objective').replace(u'soap_', u''),
	u'a': _('soap_Assessment').replace(u'soap_', u''),
	u'p': _('soap_Plan').replace(u'soap_', u''),
	u'u': _('soap_Unspecified').replace(u'soap_', u''),
	None: _('soap_Administrative').replace(u'soap_', u'')
}

l10n2soap_cat = {
	_('soap_S').replace(u'soap_', u''): u's',
	_('soap_O').replace(u'soap_', u''): u'o',
	_('soap_A').replace(u'soap_', u''): u'a',
	_('soap_P').replace(u'soap_', u''): u'p',
	_('soap_U').replace(u'soap_', u''): u'u',
#	u'?': u'u',
	gmTools.u_ellipsis: None
}

#============================================================
def _on_soap_modified():
	"""Always relates to the active patient."""
	gmHooks.run_hook_script(hook = u'after_soap_modified')

gmDispatcher.connect(_on_soap_modified, u'clin_narrative_mod_db')

#============================================================
class cNarrative(gmBusinessDBObject.cBusinessDBObject):
	"""Represents one clinical free text entry.
	"""
	_cmd_fetch_payload = u"select *, xmin_clin_narrative from clin.v_pat_narrative where pk_narrative = %s"
	_cmds_store_payload = [
		u"""update clin.clin_narrative set
				narrative = %(narrative)s,
				clin_when = %(date)s,
				soap_cat = lower(%(soap_cat)s),
				fk_encounter = %(pk_encounter)s
			where
				pk=%(pk_narrative)s and
				xmin=%(xmin_clin_narrative)s""",
		u"""select xmin_clin_narrative from clin.v_pat_narrative where pk_narrative=%(pk_narrative)s"""
		]

	_updatable_fields = [
		'narrative',
		'date',
		'soap_cat',
		'pk_episode',
		'pk_encounter'
	]

	#--------------------------------------------------------
	def format(self, left_margin=u'', fancy=False, width=75):

		if fancy:
			# FIXME: add revision
			txt = gmTools.wrap (
				text = _('%s: %s by %.8s (v%s)\n%s') % (
					self._payload[self._idx['date']].strftime('%x %H:%M'),
					soap_cat2l10n_str[self._payload[self._idx['soap_cat']]],
					self._payload[self._idx['provider']],
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
				soap_cat2l10n[self._payload[self._idx['soap_cat']]],
				self._payload[self._idx['narrative']],
				self._payload[self._idx['provider']]
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
def create_clin_narrative(narrative=None, soap_cat=None, episode_id=None, encounter_id=None):
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
		return (True, None)

	# 2) also, silently do not insert true duplicates
	# FIXME: this should check for .provider = current_user but
	# FIXME: the view has provider mapped to their staff alias
	cmd = u"""
		SELECT
			*, xmin_clin_narrative
		FROM clin.v_pat_narrative
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
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
	if len(rows) == 1:
		narrative = cNarrative(row = {'pk_field': 'pk_narrative', 'data': rows[0], 'idx': idx})
		return (True, narrative)

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
			SELECT *, xmin_clin_narrative
			FROM clin.v_pat_narrative
			WHERE
				pk_narrative = currval(pg_get_serial_sequence('clin.clin_narrative', 'pk'))"""
		}
	]
	rows, idx = gmPG2.run_rw_queries(queries = queries, return_data = True, get_col_idx = True)

	narrative = cNarrative(row = {'pk_field': 'pk_narrative', 'idx': idx, 'data': rows[0]})
	return (True, narrative)
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
		where_parts.append(u'soap_cat IN %(soap_cats)s')
		args['soap_cats'] = tuple(soap_cats)

	if order_by is None:
		order_by = u'ORDER BY date, soap_rank'
	else:
		order_by = u'ORDER BY %s' % order_by

	cmd = u"""
		SELECT
			cvpn.*,
			(SELECT rank FROM clin.soap_cat_ranks WHERE soap_cat = cvpn.soap_cat)
				AS soap_rank
		FROM
			clin.v_pat_narrative cvpn
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
		filtered_narrative = filter(lambda narr: narr['provider'] in providers, filtered_narrative)

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
def get_as_journal(since=None, until=None, encounters=None, episodes=None, issues=None, soap_cats=None, providers=None, order_by=None, time_range=None, patient=None):

	if (patient is None) and (episodes is None) and (issues is None) and (encounters is None):
		raise ValueError('at least one of <patient>, <episodes>, <issues>, <encounters> must not be None')

	if order_by is None:
		order_by = u'ORDER BY vemrj.clin_when, vemrj.pk_episode, scr, vemrj.src_table'
	else:
		order_by = u'ORDER BY %s' % order_by

	where_parts = []
	args = {}

	if patient is not None:
		where_parts.append(u'pk_patient = %(pat)s')
		args['pat'] = patient

	if soap_cats is not None:
		# work around bug in psycopg2 not being able to properly
		# adapt None to NULL inside tuples
		if None in soap_cats:
			where_parts.append(u'((vemrj.soap_cat IN %(soap_cat)s) OR (vemrj.soap_cat IS NULL))')
			soap_cats.remove(None)
		else:
			where_parts.append(u'vemrj.soap_cat IN %(soap_cat)s')
		args['soap_cat'] = tuple(soap_cats)

	if time_range is not None:
		where_parts.append(u"vemrj.clin_when > (now() - '%s days'::interval)" % time_range)

	if episodes is not None:
		where_parts.append(u"vemrj.pk_episode IN %(epis)s")
		args['epis'] = tuple(episodes)

	if issues is not None:
		where_parts.append(u"vemrj.pk_health_issue IN %(issues)s")
		args['issues'] = tuple(issues)

	# FIXME: implement more constraints

	cmd = u"""
		SELECT
			to_char(vemrj.clin_when, 'YYYY-MM-DD') AS date,
			vemrj.clin_when,
			coalesce(vemrj.soap_cat, '') as soap_cat,
			vemrj.narrative,
			vemrj.src_table,

			(SELECT rank FROM clin.soap_cat_ranks WHERE soap_cat = vemrj.soap_cat) AS scr,

			vemrj.modified_when,
			to_char(vemrj.modified_when, 'YYYY-MM-DD HH24:MI') AS date_modified,
			vemrj.modified_by,
			vemrj.row_version,
			vemrj.pk_episode,
			vemrj.pk_encounter,
			vemrj.soap_cat as real_soap_cat
		FROM clin.v_emr_journal vemrj
		WHERE
			%s
		%s""" % (
			u'\n\t\t\t\t\tAND\n\t\t\t\t'.join(where_parts),
			order_by
		)

	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}], get_col_idx = True)
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
		#status, new_narrative = create_clin_narrative(narrative = 'Test narrative', soap_cat = 'a', episode_id=1, encounter_id=2)
		#print new_narrative

	#-----------------------------------------
	def test_search_text_across_emrs():
		results = search_text_across_emrs('cut')
		for r in results:
			print r
	#-----------------------------------------

	#test_search_text_across_emrs()
	test_narrative()

#============================================================

