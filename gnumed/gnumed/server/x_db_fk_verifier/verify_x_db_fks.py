#!/usr/bin/env python

"""GnuMed cross-database foreign key referential integrity checker.

This script checks cross-database referential integrity
constraints and logs violations. It is intended to be
run from cron.
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/x_db_fk_verifier/Attic/verify_x_db_fks.py,v $
# $Id: verify_x_db_fks.py,v 1.2 2003-09-16 22:41:34 ncq Exp $
__version__ = "$Revision: 1.2 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

import sys, os.path
# go find our modules
sys.path.append ("./modules/")

import gmLog
_log = gmLog.gmDefLog
_log.SetAllLogLevels(gmLog.lData)

import gmPG
gmPG.set_default_client_encoding('latin1')

import gmI18N

#============================================================
def log_violation(aCurs = None, id_fk_def = None, viol_pk = None, viol_val = 'programmer forgot to pass in offending value', viol_comment = None):
	_log.Log(gmLog.lErr, viol_comment)

	if aCurs is None:
		_log.Log(gmLog.lErr, 'need cursor to log violation')
		return None
	if id_fk_def is None:
		_log.Log(gmLog.lErr, 'need foreign key definition id to log violation')
		return None
	if viol_pk is None:
		_log.Log(gmLog.lErr, 'need offending primary key to log violation')
		return None
	if viol_comment is None:
		viol_comment = 'referential integrity violation: unspecified error, please check log'

	cmd = "select log_x_db_fk_violation(%s, %s, %s, %s)"
	if not gmPG.run_query (aCurs, cmd, id_fk_def, viol_pk, viol_val, viol_comment):
		_log.Log(gmLog.lErr, 'cannot log referential integrity violation')
		return None

	return 1
#------------------------------------------------------------
def verify_fk(aSrcConn = None, anFK = None, aColIdx = None):
	if aSrcConn is None:
		_log.Log(gmLog.lErr, 'need source connection to check key')
		return None
	if anFK is None:
		_log.Log(gmLog.lErr, 'need foreign key definition to check it')
		return None
	if aColIdx is None:
		_log.Log(gmLog.lErr, 'need column index to check key')
		return None
	_log.Log(gmLog.lInfo, 'checking cross-db FK: %s' % anFK)

	# use schema qualifier ?
	# - source
	if anFK[aColIdx['fk_src_schema']] is None:
		src_table = anFK[aColIdx['fk_src_table']]
	else:
		src_table = "%s.%s" % (anFK[aColIdx['fk_src_schema']], anFK[aColIdx['fk_src_table']])
	# - target
	if anFK[aColIdx['ext_schema']] is None:
		ext_table = anFK[aColIdx['ext_table']]
	else:
		ext_table = "%s.%s" % (anFK[aColIdx['ext_schema']], anFK[aColIdx['ext_table']])

	src_curs = aSrcConn.cursor()
	log_curs = aSrcConn.cursor()

	# get name of pk attribute for this table
	pk_name = gmPG.get_pkey_name(src_curs, anFK[aColIdx['fk_src_table']])
	pk = ''
	if pk_name not in [None, -1]:
		pk = "%s, " % pk_name
	else:
		pk = "oid, "

	# get fk values
	cmd = "select %s%s from %s" % (pk, anFK[aColIdx['fk_src_col']], src_table)
	if not gmPG.run_query(src_curs, cmd):
		log_violation(
			aCurs = log_curs,
			id_fk_def = anFK[aColIdx['id']],
			viol_pk = '__n/a__',
			viol_val = '__n/a__',
			viol_comment = 'cannot retrieve cross-db FK values, skipping referential integrity check'
		)
		aSrcConn.commit()
		src_curs.close()
		return None
	# and cycle over them as long as there still is one available
	row = src_curs.fetchone()
	while row is not None:
		# connect to external service
		ext_service = anFK[aColIdx['ext_service']]
		ext_conn = dbpool.GetConnection(ext_service)
		if ext_conn is None:
			log_violation(
				aCurs = log_curs,
				id_fk_def = anFK[aColIdx['id']],
				viol_pk = '__n/a__',
				viol_val = '__n/a__',
				viol_comment = 'cannot connect to referenced service [%s]' % ext_service
			)
			aSrcConn.commit()
			src_curs.close()
			return None
		ext_curs = ext_conn.cursor()
		# get occurrence count of referenced key value
		cmd = "select count(%s) from %s where %s=%%s" % (anFK[aColIdx['ext_col']], ext_table, anFK[aColIdx['ext_col']])
		if not gmPG.run_query(ext_curs, cmd, row[1]):
			log_violation(
				aCurs = log_curs,
				id_fk_def = anFK[aColIdx['id']],
				viol_pk = '__n/a__',
				viol_val = '__n/a__',
				viol_comment = 'cannot verify referential integrity'
			)
			aSrcConn.commit()
			src_curs.close()
			ext_curs.close()
			dbpool.ReleaseConnection(ext_service)
			return None
		remote_count = ext_curs.fetchone()[0]
		# disconnect from external service
		ext_curs.close()
		dbpool.ReleaseConnection(ext_service)
		# is referenced key value unique ?
		if remote_count == 0:
			log_violation(
				aCurs = log_curs,
				id_fk_def = anFK[aColIdx['id']],
				viol_pk = str(row[0]),
				viol_val = str(row[1]),
				viol_comment = 'referential integrity violation: fk value not found in referenced table'
			)
		elif remote_count > 1:
			log_violation(
				aCurs = log_curs,
				id_fk_def = anFK[aColIdx['id']],
				viol_pk = str(row[0]),
				viol_val = str(row[1]),
				viol_comment = 'referential integrity violation: fk value not unique in referenced table (count = %s)' % remote_count
			)
		# and do next one
		row = src_curs.fetchone()

	log_curs.close()
	aSrcConn.commit()
	src_curs.close()		
	return 1
#------------------------------------------------------------
def verify_service(aService = None):
	_log.Log(gmLog.lInfo, 'verifying cross-db FKs in service [%s]' % aService)
	src_conn = dbpool.GetConnection(aService)
	if src_conn is None:
		_log.Log(gmLog.lErr, 'cannot connect to source service [%s] to check cross-db FKs, skipping' % aService)
		return None
	src_curs = src_conn.cursor()
	# FIXME: add "where last_checked > ..." logic
	cmd = "select * from x_db_fk"
	if not gmPG.run_query(src_curs, cmd):
		_log.Log(gmLog.lErr, 'cannot retrieve cross-db FK defs from service [%s], skipping' % aService)
		src_curs.close()
		src_conn.close()
		return None
	rows = src_curs.fetchall()
	col_idx = gmPG.get_col_indices(src_curs)
	src_curs.close()
	for x_db_fk in rows:
		verify_fk(src_conn, x_db_fk, col_idx)
	src_conn.close()
	return 1
#------------------------------------------------------------
def verify_services():
	for srvc in dbpool.GetAvailableServices():
		verify_service(srvc)
	return 1
#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':
	# get parameter from config file
	import gmCfg, gmLoginInfo
	_cfg = gmCfg.gmDefCfgFile
	login_info = gmLoginInfo.LoginInfo(
		user = _cfg.get('backend', 'user'),
		passwd = _cfg.get('backend', 'password'),
		host = _cfg.get('backend', 'host'),
		port = _cfg.get('backend', 'port'),
		database = _cfg.get('backend', 'database')
	)

	# connect to core database
	dbpool = gmPG.ConnectionPool(login_info)

	# and verify all the services
	if not verify_services():
		_log.Log(gmLog.lErr, 'cannot verify cross-db referential integrity')

#============================================================
# $Log: verify_x_db_fks.py,v $
# Revision 1.2  2003-09-16 22:41:34  ncq
# - get_pkey_name renaming
#
# Revision 1.1  2003/08/17 17:53:45  ncq
# - first check in
# - run from cron
#
