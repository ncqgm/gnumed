"""GNUmed chart pulling related middleware."""
#============================================================
__license__ = "GPL v2 or later"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"


import sys
import logging


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmCfg
from Gnumed.pycommon import gmPG2

from Gnumed.business import gmStaff
from Gnumed.business import gmProviderInbox
from Gnumed.business import gmEMRStructItems
from Gnumed.business import gmPraxis


_log = logging.getLogger('gm.praxis')
#============================================================
def _check_for_provider_chart_access(person):

	curr_prov = gmStaff.gmCurrentProvider()

	# can view my own chart
	if person.ID == curr_prov['pk_identity']:
		return True

	# primary provider can view patient
	if person['pk_primary_provider'] == curr_prov['pk_staff']:
		return True

	# is the patient a provider ?
	if person.ID not in [ s['pk_identity'] for s in gmStaff.get_staff_list() ]:
		return True

	prov = u'%s (%s%s %s)' % (
		curr_prov['short_alias'],
		gmTools.coalesce(curr_prov['title'], u'', u'%s '),
		curr_prov['firstnames'],
		curr_prov['lastnames']
	)
	pat = u'%s%s %s' % (
		gmTools.coalesce(person['title'], u'', u'%s '),
		person['firstnames'],
		person['lastnames']
	)
	# notify the staff member
	gmProviderInbox.create_inbox_message (
		staff = person.staff_id,
		message_type = _('Privacy notice'),
		message_category = u'administrative',
		subject = _('%s: Your chart has been accessed by %s (without user interaction, probably by a script).') % (pat, prov),
		patient = person.ID
	)
	# notify /me about the staff member notification
	gmProviderInbox.create_inbox_message (
		staff = curr_prov['pk_staff'],
		message_type = _('Privacy notice'),
		message_category = u'administrative',
		subject = _('%s: Staff member %s has been notified of your chart access.') % (prov, pat)
	)

	return True

#----------------------------------------------------------------
def _ensure_person_is_patient(person):
	if person.is_patient:
		return True
	person.is_patient = True
	return True

#----------------------------------------------------------------
def _get_very_recent_encounter(pk_identity):
	cfg_db = gmCfg.cCfgSQL()
	min_ttl = cfg_db.get2 (
		option = u'encounter.minimum_ttl',
		workplace = gmPraxis.gmCurrentPraxisBranch().active_workplace,
		bias = u'user',
		default = u'1 hour 30 minutes'
	)
	cmd = u"""
		SELECT pk_encounter
		FROM clin.v_most_recent_encounters
		WHERE
			pk_patient = %s
				and
			last_affirmed > (now() - %s::interval)
		ORDER BY
			last_affirmed DESC"""
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': [pk_identity, min_ttl]}])
	if len(rows) == 0:
		_log.debug('no <very recent> encounter (younger than [%s]) found' % min_ttl)
		return None
	_log.debug('"very recent" encounter [%s] found and re-activated', rows[0][0])
	return gmEMRStructItems.cEncounter(aPK_obj = rows[0][0])

#----------------------------------------------------------------
def _decide_on_active_encounter(pk_identity):

	enc = _get_very_recent_encounter(pk_identity)
	if enc is not None:
		return enc

	_here = gmPraxis.gmCurrentPraxisBranch()
	cfg_db = gmCfg.cCfgSQL()
	enc_type = cfg_db.get2 (
		option = u'encounter.default_type',
		workplace = _here.active_workplace,
		bias = u'user'
	)
	if enc_type is None:
		enc_type = gmEMRStructItems.get_most_commonly_used_encounter_type()
	if enc_type is None:
		enc_type = u'in surgery'
	enc = gmEMRStructItems.create_encounter(fk_patient = pk_identity, enc_type = enc_type)
	enc['pk_org_unit'] = _here['pk_org_unit']
	enc.save()
	_log.debug('new encounter [%s] initiated' % enc['pk_encounter'])

	return enc

#------------------------------------------------------------
def tui_chart_puller(pk_identity):
	from Gnumed.business import gmPerson

	_log.debug('pulling chart for identity [%s]', pk_identity)

	success, pk_identity = gmTools.input2int(initial = pk_identity, minval = 1)
	if not success:
		raise TypeError('<%s> is not an integer' % pk_identity)

	person = gmPerson.cIdentity(pk_identity)

	# be careful about pulling charts of our own staff
	if not _check_for_provider_chart_access(person):
		return None

	# create chart if necessary
	if not _ensure_person_is_patient(person):
		return None

	del person

	# detect which encounter to use
	enc = _decide_on_active_encounter(pk_identity)

	# ensure has allergy state
	patient = gmPerson.cPatient(pk_identity)
	patient.ensure_has_allergy_state(enc['pk_encounter'])

	# set encounter in EMR
	from Gnumed.business import gmClinicalRecord
	emr = gmClinicalRecord.cClinicalRecord(aPKey = pk_identity, allow_user_interaction = False, encounter = enc)
	emr.log_access(action = u'chart pulled for patient [%s] (no user interaction)' % pk_identity)

	return emr

#============================================================
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

#	from Gnumed.pycommon import gmI18N
#	gmI18N.install_domain()
