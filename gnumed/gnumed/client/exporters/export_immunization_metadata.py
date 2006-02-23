# GNUmed vaccination metadata exporter
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/exporters/export_immunization_metadata.py,v $
# $Id: export_immunization_metadata.py,v 1.1 2006-02-23 19:25:47 ncq Exp $
__version__ = "$Revision: 1.1 $"
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
Vaccine "%s" (%s):
  comment  : %s
  given via: %s (%s = %s)
  age range: %s days - %s days
"""

# export vaccine information

# retrieve vaccines
cmd = """select * from clin.v_vaccine"""
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


# export known schedules

f.close()

#============================================================
# $Log: export_immunization_metadata.py,v $
# Revision 1.1  2006-02-23 19:25:47  ncq
# - export immunization metadata from the database into a file
#
#
