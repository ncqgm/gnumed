"""GnuMed clinical narrative business object.

license: GPL
"""
#============================================================
__version__ = "$Revision: 1.1 $"
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>"

import types, sys

from Gnumed.pycommon import gmLog, gmPG, gmExceptions
from Gnumed.business import gmClinItem
from Gnumed.pycommon.gmPyCompat import *

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)
#============================================================
# FIXME: write cNarrative object based on clin_narrative
# FIXME: write cDiag based on v_pat_diag (with a method get_codes())
#============================================================
class cRFE(gmClinItem.cClinItem):
	"""Represents one Reason For Encounter

	FIXME: rewrite based on v_rfe
	"""
	_cmd_fetch_payload = """
		select * from clin_narrative
		where pk=%s
		"""
	_cmds_store_payload = [
		"""select 1 from clin_narrative where pk=%(pk)s for update""",
		"""update clin_narrative set
				narrative=%(narrative)s,
				clin_when=%(clin_when)s
			where pk=%(pk)s"""
		]

	_updatable_fields = [
		'narrative',
		'clin_when'
	]
#============================================================
class cAOE(gmClinItem.cClinItem):
	"""
        Represents one Assessment Of Encounter

	FIXME: rewrite based on v_rfe
	"""
	_cmd_fetch_payload = """
		select * from clin_narrative
		where pk=%s
		"""
	_cmds_store_payload = [
		"""select 1 from clin_narrative where pk=%(pk)s for update""",
		"""update clin_narrative set
				narrative=%(narrative)s,
				clin_when=%(clin_when)s
			where pk=%(pk)s"""
		]

	_updatable_fields = [
		'narrative',
		'clin_when'
	]
	#--------------------------------------------------------
	def is_diagnosis(self):
	    """
            Checks if the AOE is a real diagosis
	    """
	    try:
	        self.__diagnosis
	    except:
	        self.load_diagnosis()
	    if  self.__diagnosis is None or len(self.__diagnosis) == 0:
	        return False
	    else:
	        return True
	#--------------------------------------------------------
	def get_diagnosis(self):
	    """
            Returns diagnosis for this AOE
	    """
	    try:
	        self.__diagnosis
	    except:
	        self.load_diagnosis()
	    return self.__diagnosis
	#--------------------------------------------------------
	def load_diagnosis(self):
	    """
            Fetches from backend diagnosis associated with this AOE
	    """
	    self.__diagnosis = []
	    queries = []
	    vals = {'enc': self['fk_encounter'], 'epi': self['fk_episode'], 'dat': self['clin_when']}
		# FIXME: v_pat_diag.fk_narrative
	    cmd = "select * from v_pat_diag where pk_encounter =%(enc)s and pk_episode=%(epi)s and diagnosed_when=%(dat)s"
	    rows = gmPG.run_ro_query('historica', cmd, None, vals)
	    if rows is None:
	        _log.Log(gmLog.lErr, 'cannot query diagnosis for aoe [%s]' % (self.pk_obj))
	        del self.__diagnosis
	        return
	    if len(rows) > 0:
	        self.__diagnosis = rows[0]
#============================================================
def create_clin_narrative():
	print "fixme"

#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':
	print "unit test missing"

#============================================================
# $Log: gmClinNarrative.py,v $
# Revision 1.1  2004-07-04 13:24:31  ncq
# - add cRFE/cAOE
# - use in get_rfes(), get_aoes()
#
