"""GNUmed Praxis related middleware."""
#============================================================
__license__ = "GPL"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"


import sys


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmBorg
from Gnumed.pycommon import gmCfg2
from Gnumed.pycommon import gmBusinessDBObject


_cfg = gmCfg2.gmCfgData()
#============================================================
def delete_workplace(workplace=None, delete_config=False, conn=None):

	args = {'wp': workplace}

	# delete workplace itself (plugin load list, that is)
	queries = [
		{'cmd': u"""
delete from cfg.cfg_item
where
	fk_template = (
		select pk
		from cfg.cfg_template
		where name = 'horstspace.notebook.plugin_load_order'
	)
		and
	workplace = %(wp)s""",
		'args': args
		}
	]

	# delete other config items associated with this workplace
	if delete_config:
		queries.append ({
			'cmd': u"""
delete from cfg.cfg_item
where
	workplace = %(wp)s""",
			'args': args
		})

	gmPG2.run_rw_queries(link_obj = conn, queries = queries, end_tx = True)

#============================================================
# short description
#------------------------------------------------------------
_SQL_get_praxis_branches = u"SELECT * FROM dem.v_praxis_branches WHERE %s"

class cPraxisBranch(gmBusinessDBObject.cBusinessDBObject):
	"""Represents a praxis branch"""

	_cmd_fetch_payload = _SQL_get_praxis_branches % u"pk_praxis_branch = %s"
	_cmds_store_payload = [
		u"""UPDATE dem.praxis_branch SET
				fk_org_unit = %(pk_org_unit)s
			WHERE
				pk = %(pk_praxis_branch)s
					AND
				xmin = %(xmin_praxis_branch)s
			RETURNING
				xmin as xmin_praxis_branch
		"""
	]
	_updatable_fields = [
		u'pk_org_unit'
	]
	#--------------------------------------------------------
	def format(self):
		return u'%s' % self

#------------------------------------------------------------
def get_praxis_branches(order_by=None):
	if order_by is None:
		order_by = u'true'
	else:
		order_by = u'true ORDER BY %s' % order_by

	cmd = _SQL_get_praxis_branches % order_by
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd}], get_col_idx = True)
	return [ cPraxisBranch(row = {'data': r, 'idx': idx, 'pk_field': 'pk_praxis_branch'}) for r in rows ]
#------------------------------------------------------------
def create_praxis_branch(pk_org_unit=None):

	args = {u'fk_unit': pk_org_unit}
	cmd = u"""
		INSERT INTO dem.praxis_branch (fk_org_unit)
		VALUES (%(fk_unit)s)
		RETURNING pk
	"""
	rows, idx = gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}], return_data = True, get_col_idx = False)

	return cPraxisBranch(aPK_obj = rows[0]['pk'])
#------------------------------------------------------------
def delete_praxis_branch(pk_praxis_branch=None):
	args = {'pk': pk_praxis_branch}
	cmd = u"DELETE FROM dem.praxis_branch WHERE pk = %(pk)s"
	gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	return True

#============================================================
class gmCurrentPractice(gmBorg.cBorg):

	def __init__(self):
		try:
			self.already_inited
			return
		except AttributeError:
			pass

		self.__helpdesk = None
		self.__active_workplace = None

		self.already_inited = True
	#--------------------------------------------------------
	# waiting list handling
	#--------------------------------------------------------
	def remove_from_waiting_list(self, pk=None):
		cmd = u'delete from clin.waiting_list where pk = %(pk)s'
		args = {'pk': pk}
		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	#--------------------------------------------------------
	def update_in_waiting_list(self, pk = None, urgency = 0, comment = None, zone = None):
		cmd = u"""
update clin.waiting_list
set
	urgency = %(urg)s,
	comment = %(cmt)s,
	area = %(zone)s
where
	pk = %(pk)s"""
		args = {
			'pk': pk,
			'urg': urgency,
			'cmt': gmTools.none_if(comment, u''),
			'zone': gmTools.none_if(zone, u'')
		}

		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	#--------------------------------------------------------
	def raise_in_waiting_list(self, current_position=None):
		if current_position == 1:
			return

		cmd = u'select clin.move_waiting_list_entry(%(pos)s, (%(pos)s - 1))'
		args = {'pos': current_position}

		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	#--------------------------------------------------------
	def lower_in_waiting_list(self, current_position=None):
		cmd = u'select clin.move_waiting_list_entry(%(pos)s, (%(pos)s+1))'
		args = {'pos': current_position}

		gmPG2.run_rw_queries(queries = [{'cmd': cmd, 'args': args}])
	#--------------------------------------------------------
	# properties
	#--------------------------------------------------------
	def _get_waiting_list_patients(self):
		cmd = u"""
			SELECT * FROM clin.v_waiting_list
			ORDER BY
				list_position
		"""
		rows, idx = gmPG2.run_ro_queries (
			queries = [{'cmd': cmd}],
			get_col_idx = False
		)
		return rows

	waiting_list_patients = property (_get_waiting_list_patients, lambda x:x)
	#--------------------------------------------------------
	def _set_helpdesk(self, helpdesk):
		return

	def _get_helpdesk(self):

		if self.__helpdesk is not None:
			return self.__helpdesk

		self.__helpdesk = gmTools.coalesce (
			_cfg.get (
				group = u'workplace',
				option = u'help desk',
				source_order = [
					('explicit', 'return'),
					('workbase', 'return'),
					('local', 'return'),
					('user', 'return'),
					('system', 'return')
				]
			),
			u'http://wiki.gnumed.de'
		)

		return self.__helpdesk

	helpdesk = property(_get_helpdesk, _set_helpdesk)
	#--------------------------------------------------------
	def _get_db_logon_banner(self):
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': u'select _(message) from cfg.db_logon_banner'}])
		if len(rows) == 0:
			return u''
		return gmTools.coalesce(rows[0][0], u'').strip()

	def _set_db_logon_banner(self, banner):
		queries = [
			{'cmd': u'delete from cfg.db_logon_banner'}
		]
		if banner.strip() != u'':
			queries.append ({
				'cmd': u'insert into cfg.db_logon_banner (message) values (%(msg)s)',
				'args': {'msg': banner.strip()}
			})
		rows, idx = gmPG2.run_rw_queries(queries = queries, end_tx = True)

	db_logon_banner = property(_get_db_logon_banner, _set_db_logon_banner)
	#--------------------------------------------------------
	def _set_workplace(self, workplace):
		# maybe later allow switching workplaces on the fly
		return True

	def _get_workplace(self):
		"""Return the current workplace (client profile) definition.

		The first occurrence counts.
		"""
		if self.__active_workplace is not None:
			return self.__active_workplace

		self.__active_workplace = gmTools.coalesce (
			_cfg.get (
				group = u'workplace',
				option = u'name',
				source_order = [
					('explicit', 'return'),
					('workbase', 'return'),
					('local', 'return'),
					('user', 'return'),
					('system', 'return'),
				]
			),
			u'Local Default'
		)

		return self.__active_workplace

	active_workplace = property(_get_workplace, _set_workplace)
	#--------------------------------------------------------
	def _set_workplaces(self, val):
		pass

	def _get_workplaces(self):
		rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': u'SELECT DISTINCT workplace FROM cfg.cfg_item ORDER BY workplace'}])
		return [ r[0] for r in rows ]

	workplaces = property(_get_workplaces, _set_workplaces)
	#--------------------------------------------------------
	def _get_user_email(self):
		# FIXME: get this from the current users staff record in the database
		return _cfg.get (
			group = u'preferences',
			option = u'user email',
			source_order = [
				('explicit', 'return'),
				('user', 'return'),
				('local', 'return'),
				('workbase', 'return'),
				('system', 'return')
			]
		)

	def _set_user_email(self, val):
		prefs_file = _cfg.get(option = 'user_preferences_file')
		gmCfg2.set_option_in_INI_file (
			filename = prefs_file,
			group = u'preferences',
			option = u'user email',
			value = val
		)
		_cfg.reload_file_source(file = prefs_file)

	user_email = property(_get_user_email, _set_user_email)
#============================================================
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	def run_tests():
		prac = gmCurrentPractice()
#		print "help desk:", prac.helpdesk
#		print "active workplace:", prac.active_workplace

		old_banner = prac.db_logon_banner
		test_banner = u'a test banner'
		prac.db_logon_banner = test_banner
		if prac.db_logon_banner != test_banner:
			print 'Cannot set logon banner to', test_banner
			return False
		prac.db_logon_banner = u''
		if prac.db_logon_banner != u'':
			print 'Cannot set logon banner to ""'
			return False
		prac.db_logon_banner = old_banner

		return True


	print get_praxis_branches()


#	if not run_tests():
#		print "regression tests failed"
#	print "regression tests succeeded"

#============================================================
