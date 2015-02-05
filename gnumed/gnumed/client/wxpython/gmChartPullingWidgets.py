"""GNUmed chart pulling widgets."""
#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"

import sys
import logging


import wx


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmI18N
from Gnumed.pycommon import gmCfg
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmDateTime
from Gnumed.business import gmPraxis
from Gnumed.wxpython import gmGuiHelpers


_log = logging.getLogger('gm.chart_pull')

#================================================================
# encounter
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
	from Gnumed.business import gmEMRStructItems
	return gmEMRStructItems.cEncounter(aPK_obj = rows[0][0])

#----------------------------------------------------------------
def _get_fairly_recent_encounter(pk_identity):
	_here = gmPraxis.gmCurrentPraxisBranch().active_workplace
	cfg_db = gmCfg.cCfgSQL()
	min_ttl = cfg_db.get2 (
		option = u'encounter.minimum_ttl',
		workplace = _here,
		bias = u'user',
		default = u'1 hour 30 minutes'
	)
	max_ttl = cfg_db.get2 (
		option = u'encounter.maximum_ttl',
		workplace = _here,
		bias = u'user',
		default = u'6 hours'
	)
	cmd = u"""
		SELECT pk_encounter
		FROM clin.v_most_recent_encounters
		WHERE
			pk_patient = %(pat)s
				AND
			last_affirmed BETWEEN (now() - %(max)s::interval) AND (now() - %(min)s::interval)
		ORDER BY
			last_affirmed DESC"""
	args = {'pat': pk_identity, 'max': max_ttl, 'min': min_ttl}
	rows, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])

	if len(rows) == 0:
		_log.debug('no <fairly recent> encounter (between [%s] and [%s] old) found' % (min_ttl, max_ttl))
		return None

	_log.debug('"fairly recent" encounter [%s] found', rows[0][0])

	from Gnumed.business import gmEMRStructItems
	encounter = gmEMRStructItems.cEncounter(aPK_obj = rows[0][0])
	cmd = u"""
		SELECT title, firstnames, lastnames, gender, dob
		FROM dem.v_basic_person WHERE pk_identity = %(pat)s"""
	pats, idx = gmPG2.run_ro_queries(queries = [{'cmd': cmd, 'args': args}])
	pat = pats[0]
	pat_str = u'%s %s %s (%s), %s  [#%s]' % (
		gmTools.coalesce(pat[0], u'')[:5],
		pat[1][:15],
		pat[2][:15],
		pat[3],
		gmDateTime.pydt_strftime(pat[4], '%Y %b %d'),
		pk_identity
	)
	msg = _(
		'%s\n'
		'\n'
		"This patient's chart was worked on only recently:\n"
		'\n'
		' %s'
		'\n'
		'Do you want to continue that consultation ?\n'
		' (if not a new one will be started)\n'
	) % (
		pat_str,
		encounter.format (
			episodes = None,
			with_soap = False,
			left_margin = 1,
			patient = None,
			issues = None,
			with_docs = False,
			with_tests = False,
			fancy_header = False,
			with_vaccinations = False,
			with_rfe_aoe = True,
			with_family_history = False,
			with_co_encountlet_hints = False,
			by_episode = False
		)
	)
	attach = gmGuiHelpers.gm_show_question (
		title = _('Pulling electronic chart'),
		question = msg,
		cancel_button = False
	)

	if not attach:
		_log.debug('user decided not to attach to encounter [%s] despite it being fairly recent', encounter['pk_encounter'])
		return None

	encounter['last_affirmed'] = gmDateTime.pydt_now_here()
	encounter.save()

	_log.debug('"fairly recent" encounter reactivated and reaffirmed')
	return encounter

#----------------------------------------------------------------
def _decide_on_active_encounter(pk_identity):

	enc = _get_very_recent_encounter(pk_identity)
	if enc is not None:
		return enc

	enc = _get_fairly_recent_encounter(pk_identity)
	if enc is not None:
		return enc

	from Gnumed.business import gmEMRStructItems
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

#----------------------------------------------------------------
def _do_tasks_after_pulling_chart(emr):
	emr.log_access(action = u'chart pulled for patient [%s]' % emr.pk_patient)
	emr.remove_empty_encounters()

#----------------------------------------------------------------
# main entry point
#----------------------------------------------------------------
def pull_chart(person):
	# provider chart access warning already
	# done during set_active_patient
	_log.debug('pulling chart for identity [%s]', person.ID)

	person.is_patient = True
	enc = _decide_on_active_encounter(person.ID)
	# already done elsewhere
	#person.as_patient.ensure_has_allergy_state(enc['pk_encounter'])

	# set encounter in EMR
	from Gnumed.business import gmClinicalRecord
	emr = gmClinicalRecord.cClinicalRecord(aPKey = person.ID, allow_user_interaction = False, encounter = enc)

	wx.CallAfter(_do_tasks_after_pulling_chart, emr)

	return emr

#================================================================
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	gmI18N.activate_locale()
	gmI18N.install_domain(domain = 'gnumed')

#	def test_message_inbox():
#		app = wx.PyWidgetTester(size = (800, 600))
#		app.SetWidget(cProviderInboxPnl, -1)
#		app.MainLoop()

#	def test_msg_ea():
#		app = wx.PyWidgetTester(size = (800, 600))
#		app.SetWidget(cInboxMessageEAPnl, -1)
#		app.MainLoop()


	#test_message_inbox()
	#test_msg_ea()
