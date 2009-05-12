# -*- coding: utf8 -*-
"""Medication handling code.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmMedication.py,v $
# $Id: gmMedication.py,v 1.1 2009-05-12 12:02:01 ncq Exp $
__version__ = "$Revision: 1.1 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"

import sys, logging
#, codecs


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmBusinessDBObject
# gmPG2, gmTools


_log = logging.getLogger('gm.meds')
_log.info(__version__)
#============================================================
class cConsumedSubstance(gmBusinessDBObject.cBusinessDBObject):
	"""Represents a substance currently taken by the patient."""

	_cmd_fetch_payload = u"select * from clin.v_pat_substance_intake where pk_substance_intake = %s"
	_cmds_store_payload = [
#		u"""update clin.allergy_state set
#				last_confirmed = %(last_confirmed)s,
#				has_allergy = %(has_allergy)s,
#				comment = %(comment)s
#			where
#				pk = %(pk_allergy_state)s and
#				xmin = %(xmin_allergy_state)s""",
#		u"""select xmin_allergy_state from clin.v_pat_allergy_state where pk_allergy_state = %(pk_allergy_state)s"""
	]
	_updatable_fields = [
#		'last_confirmed',		# special value u'now' will set to datetime.datetime.now() in the local time zone
#		'has_allergy',			# verified against allergy_states (see above)
#		'comment'				# u'' maps to None / NULL
	]
#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	from Gnumed.pycommon import gmLog2
	from Gnumed.pycommon import gmI18N

	gmI18N.activate_locale()
#	gmDateTime.init()
	#--------------------------------------------------------
	#--------------------------------------------------------
	#--------------------------------------------------------
	if (len(sys.argv)) > 1 and (sys.argv[1] == 'test'):
		pass

#============================================================
# $Log: gmMedication.py,v $
# Revision 1.1  2009-05-12 12:02:01  ncq
# - start supporting current medications
#
#