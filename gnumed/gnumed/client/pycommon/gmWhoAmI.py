#===================================================
__version__ = "$Revision: 1.6 $"
__author__ = "Hilmar.Berger@gmx.de"
__license__ = "GPL"

from Gnumed.pycommon import gmLog, gmGuiBroker, gmPG, gmBorg, gmExceptions, gmCfg

_log = gmLog.gmDefLog
_cfg = gmCfg.gmDefCfgFile

_log.Log(gmLog.lInfo, __version__)
#===================================================
class cWhoAmI(gmBorg.cBorg):
	"""Who we are and which workplace we are on.

	- db_account is derived from CURRENT_USER in the database, 
	  thus it is determined by the name used to login
	- workplace is determined by what is set in the config file
	- staff_* is determined by CURRENT_USER via a mapping table
	"""
	def __init__(self):
		gmBorg.cBorg.__init__(self)
	#-----------------------------------------------
	def __get_db_account(self):
		cmd = 'select CURRENT_USER'
		result = gmPG.run_ro_query('default', cmd)
		if result is None:
			_log.Log(gmLog.lPanic, 'cannot retrieve database account name')
			return None
		if len(result) == 0:
			_log.Log(gmLog.lPanic, 'cannot retrieve database account name')
			return None
		self._db_account = result[0][0]
		return 1
	#-----------------------------------------------
	def get_db_account(self):
		"""return db account"""
		try:
			return self._db_account
		except AttributeError:
			pass

		if not self.__get_db_account():
			_log.Log(gmLog.lPanic, 'cannot retrieve database account name')
			raise ValueError, 'cannot retrieve database account name'

		return self._db_account
	#-----------------------------------------------
	def get_workplace(self):
		try:
			return self._workplace
		except AttributeError:
			pass

		self._workplace = 'xxxDEFAULTxxx'
		if _cfg is None:
			print _('No config file to read workplace name from !')
		else:
			tmp = _cfg.get('workplace', 'name')
			if tmp is None:
				print _('You should name this workplace to better identify the machine !\nTo do this set the option "name" in the group [workplace] in the config file !')
			else:
				# if cfg returned a list type, use only first element
				if type(tmp) == type([]):
					self._workplace = tmp[0]
				else:
					self._workplace = tmp
		return self._workplace
	#-----------------------------------------------
	def get_staff_ID(self):
		try:
			return self._staff_ID
		except AttributeError:
			pass

		cmd = "select pk_staff from v_staff where db_user=CURRENT_USER"
		result = gmPG.run_ro_query('personalia', cmd, None)
		if result is None:
			raise ValueError, _('cannot resolve db account name to primary key of staff member')
		if len(result) == 0:
			raise ValueError, _('no correspondig staff member for current database login')
		self._staff_ID = result[0][0]
		return self._staff_ID
	#-----------------------------------------------
	def get_staff_identity (self):
		try:
			return self._staff_identity
		except AttributeError:
			pass

		cmd = "select pk_identity from v_staff where db_user=CURRENT_USER"
		result = gmPG.run_ro_query('personalia', cmd, None)
		if result is None:
			raise ValueError, _('cannot resolve db account name to identity of staff member')
		if len(result) == 0:
			raise ValueError, _('no correspondig staff member for current database login')
		self._staff_identity = result[0][0]
		return self._staff_identity	
	#-----------------------------------------------
	def get_staff_name(self):
		try:
			return self._staff_name
		except AttributeError:
			pass

		cmd = "select title, firstnames, lastnames from v_staff where db_user=CURRENT_USER"
		result = gmPG.run_ro_query('personalia', cmd, None)
		if result is None:
			raise ValueError, _('cannot get staff name')
		if len(result) == 0:
			raise ValueError, _('no staff name on file for current database login')
		self._staff_name = '%s%s.%s' % (result[0][0], result[0][1][:1], result[0][2])
		return self._staff_name
	#-----------------------------------------------
	def get_staff_sign(self):
		try:
			return self._staff_sign
		except AttributeError:
			pass

		cmd = "select sign from v_staff where db_user=CURRENT_USER"
		result = gmPG.run_ro_query('personalia', cmd, None)
		if result is None:
			raise ValueError, _('cannot get staff sign')
		if len(result) == 0:
			raise ValueError, _('no staff sign on file for current database login')
		self._staff_sign = result[0][0]
		return self._staff_sign
#===================================================
if __name__ == '__main__':
	_ = lambda x:x
	_log.SetAllLogLevels(gmLog.lData)
	whoami = cWhoAmI()
	print "workplace :", whoami.get_workplace()
	print "db account:", whoami.get_db_account()
	print "staff ID  :", whoami.get_staff_ID()
	print "staff name:", whoami.get_staff_name()
#===================================================
# $Log: gmWhoAmI.py,v $
# Revision 1.6  2005-04-03 20:09:47  ncq
# - get_staff_sign()
#
# Revision 1.5  2004/08/13 08:54:24  ncq
# - overdue import cleanup
#
# Revision 1.4  2004/08/11 16:56:04  hinnef
# - fixed workplace bug when specifying a list in gnumed.conf
#
# Revision 1.3  2004/07/19 11:50:42  ncq
# - cfg: what used to be called "machine" really is "workplace", so fix
#
# Revision 1.2  2004/04/10 01:48:31  ihaywood
# can generate referral letters, output to xdvi at present
#
# Revision 1.1  2004/02/25 09:30:13  ncq
# - moved here from python-common
#
# Revision 1.4  2004/01/06 23:44:40  ncq
# - __default__ -> xxxDEFAULTxxx
#
# Revision 1.3  2003/12/29 16:37:03  uid66147
# - whoami class is now a borg which automatically handles shared state
# - more precise naming of API
# - remove setUser/Machine
# - handle staff tables
# - add test code
#
# Revision 1.2  2003/11/17 10:56:37  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:39  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.1  2003/09/03 17:29:41  hinnef
# added gmWhoAmI to facilitate user/machine determination
#
