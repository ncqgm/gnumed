# GNUmed vaccination metadata exporter
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/exporters/export_immunization_metadata.py,v $
# $Id: export_immunization_metadata.py,v 1.2 2006-02-26 18:31:28 ncq Exp $
__version__ = "$Revision: 1.2 $"
__author__ = "Karsten Hilbert"
__license__ = 'GPL'

from Gnumed.pycommon import gmPG
#============================================================
# connect to database
pool = gmPG.ConnectionPool()

filename = 'immunization-data.txt'
print "Writing immunization metadata to:", filename
f = file(filename, 'w')

vaccine_template = """
Vaccine "%s" (%s)
  comment  : %s
  given via: %s (%s = %s)
  age range: %s days - %s days
"""

schedule_template = """
Schedule "%s" (%s)
  indication : %s (%s)
  start @ age: %s days
  # of shots : %s
  comment    : %s
"""

#===========================
# export vaccine information
#===========================

# retrieve vaccines
cmd = "select * from clin.v_vaccine"
vaccine_rows, idx = gmPG.run_ro_query (
	link_obj = 'clinical',
	aQuery = cmd,
	get_col_idx = True
)
# error
if vaccine_rows is None:
	print "error retrieving vaccine data"
# display vaccine data
else:
	f.write('Vaccines in the GNUmed database\n')
	f.write('-------------------------------\n')
	for vacc in vaccine_rows:
		f.write(vaccine_template % (
			vacc[idx['trade_name']],
			vacc[idx['short_name']],
			vacc[idx['comment']],
			vacc[idx['l10n_route_description']],
			vacc[idx['route_abbreviation']],
			vacc[idx['route_description']],
			vacc[idx['min_age']].day,
			vacc[idx['max_age']].day
		))
		if vacc[idx['is_live']]:
			f.write("  Cave: live vaccine\n")
		else:
			f.write("  non-live vaccine\n")
		# get indications for this vaccine
		cmd = """select * from clin.v_inds4vaccine where pk_vaccine = %s"""
		indication_rows, ind_idx = gmPG.run_ro_query (
			'clinical',
			cmd,
			True,
			vacc[idx['pk_vaccine']]
		)
		# error
		if indication_rows is None:
			print "error retrieving vaccine indication data"
		# display them
		else:
			f.write('  Indications:\n')
			for ind in indication_rows:
				f.write('  - %s (%s)\n' % (ind[ind_idx['l10n_indication']], ind[ind_idx['indication']]))

#=============================
# export vaccination schedules
#=============================

# retrieve schedules
cmd = "select * from clin.v_vacc_regimes"
schedule_rows, idx = gmPG.run_ro_query (
	'clinical',
	cmd,
	True
)
if schedule_rows is None:
	print "error retrieving vaccination schedules"
else:
	f.write('\n\nVaccination schedules in the GNUmed database\n')
	f.write(    '--------------------------------------------\n')
	for sched in schedule_rows:
		if sched[idx['is_active']]:
			act = 'active'
		else:
			act = 'inactive'
		f.write(schedule_template % (
			sched[idx['regime']],
			act,
			sched[idx['l10n_indication']],
			sched[idx['indication']],
			sched[idx['min_age_due']],
			sched[idx['shots']],
			sched[idx['comment']]
		))
		# get shots for this schedule
		cmd = "select * from clin.v_vacc_defs4reg where pk_regime=%s order by vacc_seq_no"
		shot_rows, shots_idx = gmPG.run_ro_query (
			'clinical',
			cmd,
			True,
			sched[idx['pk_regime']]
		)
		if shot_rows is None:
			print "error retrieving shots for regime"
		else:
			f.write('  Shots defined for this schedule:\n')
			for shot in shot_rows:
				if shot[shots_idx['is_booster']]:
					f.write('  booster) start %s - %s days of age, refresh after %s (%s)\n' % (
						shot[shots_idx['age_due_min']].day,
						shot[shots_idx['age_due_max']].day,
						shot[shots_idx['min_interval']].day,
						shot[shots_idx['vacc_comment']]
					))
				elif shot[shots_idx['vacc_seq_no']] == 1:
					f.write('  shot #%s) due between day %s and %s (%s)\n' % (
						shot[shots_idx['vacc_seq_no']],
						shot[shots_idx['age_due_min']].day,
						shot[shots_idx['age_due_max']].day,
						shot[shots_idx['vacc_comment']]
					))
				else:
					f.write('  shot #%s) due between day %s and %s, minimum %s day after previous (%s)\n' % (
						shot[shots_idx['vacc_seq_no']],
						shot[shots_idx['age_due_min']].day,
						shot[shots_idx['age_due_max']].day,
						shot[shots_idx['min_interval']].day,
						shot[shots_idx['vacc_comment']]
					))
		# get vaccines suitable for this schedule
		cmd = """
select trade_name, short_name
from clin.vaccine
where
	select () = ()
"""

f.close()

#============================================================
# $Log: export_immunization_metadata.py,v $
# Revision 1.2  2006-02-26 18:31:28  ncq
# - improve templates
# - export schedules, too
#
# Revision 1.1  2006/02/23 19:25:47  ncq
# - export immunization metadata from the database into a file
#
