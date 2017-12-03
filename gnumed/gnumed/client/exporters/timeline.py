# -*- coding: utf8 -*-
"""Timeline exporter.

Copyright: authors
"""
#============================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL v2 or later (details at http://www.gnu.org)'

import sys
import logging
import io
import os


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmDateTime


_log = logging.getLogger('gm.tl')

#============================================================
xml_start = u"""<?xml version="1.0" encoding="utf-8"?>
<timeline>
	<version>1.16.0</version>
	<!-- ======================================== Eras ======================================== -->
	<eras>
		<era>
			<name>%s</name>
			<start>%s</start>
			<end>%s</end>
			<color>205,238,241</color>
			<ends_today>%s</ends_today>
		</era>
		<era>
			<name>%s</name>
			<start>%s</start>
			<end>%s</end>
			<color>161,210,226</color>
			<ends_today>%s</ends_today>
		</era>
	</eras>
	<!-- ======================================== Categories ======================================== -->
	<categories>
		<!-- health issues -->
		<category>
			<name>%s</name>
			<color>255,0,0</color>
			<font_color>0,0,0</font_color>
		</category>
		<!-- episodes -->
		<category>
			<name>%s</name>
			<color>0,255,0</color>
			<font_color>0,0,0</font_color>
		</category>
		<!-- encounters -->
		<category>
			<name>%s</name>
			<color>30,144,255</color>
			<font_color>0,0,0</font_color>
		</category>
		<!-- hospital stays -->
		<category>
			<name>%s</name>
			<color>255,255,0</color>
			<font_color>0,0,0</font_color>
		</category>
		<!-- procedures -->
		<category>
			<name>%s</name>
			<color>160,32,140</color>
			<font_color>0,0,0</font_color>
		</category>
		<!-- documents -->
		<category>
			<name>%s</name>
			<color>255,165,0</color>
			<font_color>0,0,0</font_color>
		</category>
		<!-- vaccinations -->
		<category>
			<name>%s</name>
			<color>144,238,144</color>
			<font_color>0,0,0</font_color>
		</category>
		<!-- substance intake -->
		<category>
			<name>%s</name>
			<color>165,42,42</color>
			<font_color>0,0,0</font_color>
		</category>
		<!-- life events -->
		<category>
			<name>%s</name>
			<color>30,144,255</color>
			<font_color>0,0,0</font_color>
		</category>
	</categories>
	<!-- ======================================== Events ======================================== -->
	<events>"""

xml_end = u"""
	</events>
	<view>
		<displayed_period>
			<start>%s</start>
			<end>%s</end>
		</displayed_period>
	<hidden_categories>
	</hidden_categories>
	</view>
</timeline>"""

#============================================================
def format_pydt(pydt, format = '%Y-%m-%d %H:%M:%S'):
	return gmDateTime.pydt_strftime(pydt, format = format, accuracy = gmDateTime.acc_seconds)

#------------------------------------------------------------
# health issues
#------------------------------------------------------------
__xml_issue_template = u"""
		<event>
			<start>%s</start>
			<end>%s</end>
			<text>%s%s</text>
			<fuzzy>False</fuzzy>
			<locked>True</locked>
			<ends_today>%s</ends_today>
			<category>%s</category>
			<description>%s</description>
		</event>"""

def __format_health_issue_as_timeline_xml(issue, patient, emr):
	# container issues do not support <description> (tooltips)
	# container IDs are supposed to be numeric
	# 85bd7a14a1e74aab8db072ff8f417afb@H30.rldata.local
	tooltip = issue.format (
		patient = patient,
		with_summary = True,
		with_codes = True,
		with_episodes = True,
		with_encounters = False,
		with_medications = False,
		with_hospital_stays = False,
		with_procedures = False,
		with_family_history = False,
		with_documents = False,
		with_tests = False,
		with_vaccinations = False
	).strip().strip(u'\n').strip()
	safe_start = issue.safe_start_date
	possible_start = issue.possible_start_date
	txt = u''
	if possible_start < safe_start:
		txt += __xml_issue_template % (
			format_pydt(possible_start),									# start
			format_pydt(safe_start),										# end
			u'',															# empty = no container ID
			gmTools.xml_escape_string(u'?[%s]?' % issue['description']),	# text
			u'False',														# ends_today
			_('Health issues'),												# category
			gmTools.xml_escape_string(tooltip)								# description
		)
	txt += __xml_issue_template % (
		format_pydt(safe_start),											# start
		format_pydt(issue.end_date),										# end
		u'[%s]' % issue['pk_health_issue'],									# container ID
		gmTools.xml_escape_string(issue['description']),					# text
		gmTools.bool2subst(issue['is_active'], u'True', u'False'),			# ends_today
		_('Health issues'),													# category
		gmTools.xml_escape_string(tooltip)									# description
	)
	return txt

#------------------------------------------------------------
# episodes
#------------------------------------------------------------
__xml_episode_template = u"""
		<event>
			<start>%s</start>
			<end>%s</end>
			<text>%s%s</text>
			<fuzzy>False</fuzzy>
			<locked>True</locked>
			<ends_today>%s</ends_today>
			<category>%s</category>
			<description>%s</description>
		</event>"""

def __format_episode_as_timeline_xml(episode, patient):
	end = gmTools.bool2subst (
		episode['episode_open'],
		format_pydt(now),
		format_pydt(episode.latest_access_date),
	)
	return __xml_episode_template % (
		format_pydt(episode.best_guess_start_date),							# start
		end,																# end
		gmTools.coalesce(episode['pk_health_issue'], u'', u'(%s)'),			# container ID
		gmTools.xml_escape_string(episode['description']),					# text
		gmTools.bool2subst(episode['episode_open'], u'True', u'False'),		# ends_today
		_('Episodes'),														# category
		gmTools.xml_escape_string(episode.format (							# description
			patient = patient,
			with_summary = True,
			with_codes = True,
			with_encounters = True,
			with_documents = False,
			with_hospital_stays = False,
			with_procedures = False,
			with_family_history = False,
			with_tests = False,
			with_vaccinations = False,
			with_health_issue = True
		).strip().strip(u'\n').strip())
	)

#------------------------------------------------------------
# encounters
#------------------------------------------------------------
__xml_encounter_template = u"""
		<event>
			<start>%s</start>
			<end>%s</end>
			<text>%s</text>
			<progress>0</progress>
			<fuzzy>False</fuzzy>
			<locked>True</locked>
			<ends_today>False</ends_today>
			<category>%s</category>
			<description>%s</description>
			<milestone>%s</milestone>
		</event>"""

def __format_encounter_as_timeline_xml(encounter, patient):
	return __xml_encounter_template % (
		format_pydt(encounter['started']),
		format_pydt(encounter['last_affirmed']),
		#u'(%s)' % encounter['pk_episode'],
		gmTools.xml_escape_string(format_pydt(encounter['started'], format = '%b %d')),
		_('Encounters'),												# category
		gmTools.xml_escape_string(encounter.format (
			patient = patient,
			with_soap = True,
			with_docs = False,
			with_tests = False,
			fancy_header = False,
			with_vaccinations = False,
			with_co_encountlet_hints = False,
			with_rfe_aoe = True,
			with_family_history = False
		).strip().strip(u'\n').strip()),
		u'False'
	)

#------------------------------------------------------------
# hospital stays
#------------------------------------------------------------
__xml_hospital_stay_template = u"""
		<event>
			<start>%s</start>
			<end>%s</end>
			<text>%s</text>
			<fuzzy>False</fuzzy>
			<locked>True</locked>
			<ends_today>False</ends_today>
			<category>%s</category>
			<description>%s</description>
		</event>"""

def __format_hospital_stay_as_timeline_xml(stay):
	end = stay['discharge']
	if end is None:
		end = now
	return __xml_hospital_stay_template % (
		format_pydt(stay['admission']),
		format_pydt(end),
		gmTools.xml_escape_string(stay['hospital']),
		_('Hospital stays'),												# category
		gmTools.xml_escape_string(stay.format().strip().strip(u'\n').strip())
	)

#------------------------------------------------------------
# procedures
#------------------------------------------------------------
__xml_procedure_template = u"""
		<event>
			<start>%s</start>
			<end>%s</end>
			<text>%s</text>
			<fuzzy>False</fuzzy>
			<locked>True</locked>
			<ends_today>False</ends_today>
			<category>%s</category>
			<description>%s</description>
		</event>"""

def __format_procedure_as_timeline_xml(proc):
	if proc['is_ongoing']:
		end = now
	else:
		if proc['clin_end'] is None:
			end = proc['clin_when']
		else:
			end = proc['clin_end']
	return __xml_procedure_template % (
		format_pydt(proc['clin_when']),
		format_pydt(end),
		gmTools.xml_escape_string(proc['performed_procedure']),
		_('Procedures'),
		gmTools.xml_escape_string(proc.format (
			include_episode = True,
			include_codes = True
		).strip().strip(u'\n').strip())
	)

#------------------------------------------------------------
# documents
#------------------------------------------------------------
__xml_document_template = u"""
		<event>
			<start>%s</start>
			<end>%s</end>
			<text>%s</text>
			<fuzzy>False</fuzzy>
			<locked>True</locked>
			<ends_today>False</ends_today>
			<category>%s</category>
			<description>%s</description>
		</event>"""

def __format_document_as_timeline_xml(doc):
	return __xml_document_template % (
		format_pydt(doc['clin_when']),
		format_pydt(doc['clin_when']),
		gmTools.xml_escape_string(doc['l10n_type']),
		_('Documents'),
		gmTools.xml_escape_string(doc.format().strip().strip(u'\n').strip())
	)

#------------------------------------------------------------
# vaccinations
#------------------------------------------------------------
__xml_vaccination_template = u"""
		<event>
			<start>%s</start>
			<end>%s</end>
			<text>%s</text>
			<fuzzy>False</fuzzy>
			<locked>True</locked>
			<ends_today>False</ends_today>
			<category>%s</category>
			<description>%s</description>
		</event>"""

def __format_vaccination_as_timeline_xml(vacc):
	return __xml_vaccination_template % (
		format_pydt(vacc['date_given']),
		format_pydt(vacc['date_given']),
		gmTools.xml_escape_string(vacc['vaccine']),
		_('Vaccinations'),
		gmTools.xml_escape_string(u'\n'.join(vacc.format (
			with_indications = True,
			with_comment = True,
			with_reaction = True,
			date_format = '%Y %b %d'
		)).strip().strip(u'\n').strip())
	)

#------------------------------------------------------------
# substance intake
#------------------------------------------------------------
__xml_intake_template = u"""
		<event>
			<start>%s</start>
			<end>%s</end>
			<text>%s</text>
			<fuzzy>False</fuzzy>
			<locked>True</locked>
			<ends_today>False</ends_today>
			<category>%s</category>
			<description>%s</description>
		</event>"""

def __format_intake_as_timeline_xml(intake):
	if intake['discontinued'] is None:
		if intake['duration'] is None:
			if intake['seems_inactive']:
				end = intake['started']
			else:
				end = now
		else:
			end = intake['started'] + intake['duration']
	else:
		end = intake['discontinued']

	return __xml_intake_template % (
		format_pydt(intake['started']),
		format_pydt(end),
		gmTools.xml_escape_string(intake['substance']),
		_('Substances'),
		gmTools.xml_escape_string(intake.format (
			single_line = False,
			show_all_product_components = False
		).strip().strip(u'\n').strip())
	)

#------------------------------------------------------------
# library entry point
#------------------------------------------------------------
def create_timeline_file(patient=None, filename=None):

	emr = patient.emr
	global now
	now = gmDateTime.pydt_now_here()

	if filename is None:
		timeline_fname = gmTools.get_unique_filename(prefix = u'gm-', suffix = u'.timeline')
	else:
		timeline_fname = filename
	_log.debug('exporting EMR as timeline into [%s]', timeline_fname)
	timeline = io.open(timeline_fname, mode = 'wt', encoding = 'utf8', errors = 'xmlcharrefreplace')

	if patient['dob'] is None:
		lifespan_start = format_pydt(now.replace(year = now.year - 100))
	else:
		lifespan_start = format_pydt(patient['dob'])

	if patient['deceased'] is None:
		life_ends2day = u'True'
		lifespan_end = format_pydt(now)
	else:
		life_ends2day = u'False'
		lifespan_end = format_pydt(patient['deceased'])

	earliest_care_date = emr.earliest_care_date
	most_recent_care_date = emr.most_recent_care_date
	if most_recent_care_date is None:
		most_recent_care_date = lifespan_end
		care_ends2day = life_ends2day
	else:
		most_recent_care_date = format_pydt(most_recent_care_date)
		care_ends2day = u'False'

	timeline.write(xml_start % (
		# era: life span of patient
		_(u'Lifespan'),
		lifespan_start,
		lifespan_end,
		life_ends2day,
		_(u'Care Period'),
		format_pydt(earliest_care_date),
		most_recent_care_date,
		care_ends2day,
		# categories
		_('Health issues'),
		_('Episodes'),
		_('Encounters'),
		_('Hospital stays'),
		_('Procedures'),
		_('Documents'),
		_('Vaccinations'),
		_('Substances'),
		_('Life events')
	))
	# birth
	if patient['dob'] is None:
		start = now.replace(year = now.year - 100)
		timeline.write(__xml_encounter_template % (
			format_pydt(start),
			format_pydt(start),
			u'?',
			_('Life events'),
			_('Date of birth unknown'),
			u'True'
		))
	else:
		start = patient['dob']
		timeline.write(__xml_encounter_template % (
			format_pydt(patient['dob']),
			format_pydt(patient['dob']),
			u'*',
			_('Life events'),
			u'%s: %s%s' % (
				_(u'Birth'),
				format_pydt(patient['dob']),
				gmTools.bool2subst(patient['dob_is_estimated'], u' (%s)' % gmTools.u_almost_equal_to, u'')
			),
			u'True'
		))

	# start of care
	timeline.write(__xml_encounter_template % (
		format_pydt(earliest_care_date),
		format_pydt(earliest_care_date),
		gmTools.u_heavy_greek_cross,
		_('Life events'),
		_('Start of Care: %s (the earliest recorded event of care in this praxis)') % format_pydt(earliest_care_date, format = '%Y-%m-%d'),
		u'True'
	))

	# containers must be defined before their
	# subevents, so put health issues first
	timeline.write(u'\n<!--\n========================================\n Health issues\n======================================== -->')
	for issue in emr.health_issues:
		timeline.write(__format_health_issue_as_timeline_xml(issue, patient, emr))

	timeline.write(u'\n<!--\n========================================\n Episodes\n======================================== -->')
	for epi in emr.get_episodes(order_by = u'pk_health_issue'):
		timeline.write(__format_episode_as_timeline_xml(epi, patient))

	timeline.write(u'\n<!--\n========================================\n Encounters\n======================================== -->')
	for enc in emr.get_encounters(skip_empty = True):
		timeline.write(__format_encounter_as_timeline_xml(enc, patient))

	timeline.write(u'\n<!--\n========================================\n Hospital stays\n======================================== -->')
	for stay in emr.hospital_stays:
		timeline.write(__format_hospital_stay_as_timeline_xml(stay))

	timeline.write(u'\n<!--\n========================================\n Procedures\n======================================== -->')
	for proc in emr.performed_procedures:
		timeline.write(__format_procedure_as_timeline_xml(proc))

	timeline.write(u'\n<!--\n========================================\n Vaccinations\n======================================== -->')
	for vacc in emr.vaccinations:
		timeline.write(__format_vaccination_as_timeline_xml(vacc))

	timeline.write(u'\n<!--\n========================================\n Substance intakes\n======================================== -->')
	for intake in emr.get_current_medications(include_inactive = True, include_unapproved = False):
		timeline.write(__format_intake_as_timeline_xml(intake))

	timeline.write(u'\n<!--\n========================================\n Documents\n======================================== -->')
	for doc in patient.document_folder.documents:
		timeline.write(__format_document_as_timeline_xml(doc))

	# allergies ?
	# test results ?

	# death
	if patient['deceased'] is None:
		end = now
	else:
		end = patient['deceased']
		timeline.write(__xml_encounter_template % (
			format_pydt(end),
			format_pydt(end),
			gmTools.u_dagger,
			_('Life events'),
			_(u'Death: %s') % format_pydt(end)
		))

	# display range
	if end.month == 2:
		if end.day == 29:
			# leap years aren't consecutive
			end = end.replace(day = 28)
	target_year = end.year + 1
	end = end.replace(year = target_year)
	timeline.write(xml_end % (
		format_pydt(start),
		format_pydt(end)
	))
	timeline.close()
	return timeline_fname

#------------------------------------------------------------
__fake_timeline_start = u"""<?xml version="1.0" encoding="utf-8"?>
<timeline>
	<version>0.20.0</version>
	<categories>
		<!-- life events -->
		<category>
			<name>%s</name>
			<color>30,144,255</color>
			<font_color>0,0,0</font_color>
		</category>
	</categories>
	<events>""" % _('Life events')

__fake_timeline_body_template = u"""
		<event>
			<start>%s</start>
			<end>%s</end>
			<text>%s</text>
			<fuzzy>False</fuzzy>
			<locked>True</locked>
			<ends_today>False</ends_today>
			<!-- category></category -->
			<description>%s
			</description>
		</event>"""

def create_fake_timeline_file(patient=None, filename=None):
	"""Used to create an 'empty' timeline file for display.

	- needed because .clear_timeline() doesn't really work
	"""
	emr = patient.emr
	global now
	now = gmDateTime.pydt_now_here()

	if filename is None:
		timeline_fname = gmTools.get_unique_filename(prefix = u'gm-', suffix = u'.timeline')
	else:
		timeline_fname = filename

	_log.debug('creating dummy timeline in [%s]', timeline_fname)
	timeline = io.open(timeline_fname, mode = 'wt', encoding = 'utf8', errors = 'xmlcharrefreplace')

	timeline.write(__fake_timeline_start)

	# birth
	if patient['dob'] is None:
		start = now.replace(year = now.year - 100)
		timeline.write(__xml_encounter_template % (
			format_pydt(start),
			format_pydt(start),
			_('Birth') + u': ?',
			_('Life events'),
			_('Date of birth unknown'),
			u'False'
		))
	else:
		start = patient['dob']
		timeline.write(__xml_encounter_template % (
			format_pydt(patient['dob']),
			format_pydt(patient['dob']),
			_('Birth') + gmTools.bool2subst(patient['dob_is_estimated'], u' (%s)' % gmTools.u_almost_equal_to, u''),
			_('Life events'),
			u'',
			u'False'
		))

	# death
	if patient['deceased'] is None:
		end = now
	else:
		end = patient['deceased']
		timeline.write(__xml_encounter_template % (
			format_pydt(end),
			format_pydt(end),
			#u'',
			_('Death'),
			_('Life events'),
			u'',
			u'False'
		))

	# fake issue
	timeline.write(__fake_timeline_body_template % (
		format_pydt(start),
		format_pydt(end),
		_('Cannot display timeline.'),
		_('Cannot display timeline.')
	))

	# display range
	if end.month == 2:
		if end.day == 29:
			# leap years aren't consecutive
			end = end.replace(day = 28)
	target_year = end.year + 1
	end = end.replace(year = target_year)
	timeline.write(xml_end % (
		format_pydt(start),
		format_pydt(end)
	))

	timeline.close()
	return timeline_fname

#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != "test":
		sys.exit()

	from Gnumed.pycommon import gmI18N
	gmI18N.activate_locale()
	gmI18N.install_domain('gnumed')
	from Gnumed.business import gmPerson
	# 14 / 20 / 138 / 58 / 20 / 5
	pat = gmPerson.gmCurrentPatient(gmPerson.cPatient(aPK_obj = 12))
	fname = u'~/tmp/gm2tl-%s.timeline' % pat.get_dirname()

	print create_timeline_file(patient = pat, filename = os.path.expanduser(fname))
