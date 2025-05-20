#==============================================================
# GNUmed database schema change script
#
# License: GPL v2 or later
# Author: karsten.hilbert@gmx.net
# 
#==============================================================
import os


from Gnumed.pycommon import gmPG2


template_files = [
	'Human_body_silhouette-male.png',
	'Human_body_silhouette-female.png',
	'Human_body_outline-male-anterior.png',
	'Human_body_outline-female-anterior.png'
]


template_type = u'visual progress note'

#--------------------------------------------------------------
def run(conn=None):

	for filename in template_files:

		args = {}
		args['sname'] = os.path.splitext(filename)[0].replace('-', ', ').replace('_', ', ')
		args['lname'] = u'%s (GNUmed Default)' % args['sname']
		args['ttype'] = template_type
		args['fname'] = filename

		queries = []

		# delete this template
		cmd = u"""delete from ref.paperwork_templates where name_long = %(lname)s"""
		queries.append({'sql': cmd, 'args': args})

		# and (re-)import it
		# - template
		cmd = u"""
			INSERT INTO ref.paperwork_templates (
				fk_template_type,
				instance_type,
				name_short,
				name_long,
				external_version,
				filename,
				engine,
				data
			) VALUES (
				(SELECT pk FROM ref.form_types WHERE name = %(ttype)s),
				%(sname)s,
				%(sname)s,
				%(lname)s,
				'16.0'::TEXT,
				%(fname)s,
				'I'::TEXT,
				'image data missing'::BYTEA
			)"""
		queries.append({'sql': cmd, 'args': args})

		gmPG2.run_rw_queries(link_obj = conn, queries = queries, end_tx = False)

		# - data
		cmd = u"""
			UPDATE ref.paperwork_templates
			SET data = %(data)s::BYTEA
			WHERE name_long = %(lname)s"""
		gmPG2.file2bytea (
			query = cmd,
			filename = os.path.join('..', 'sql', 'v15-v16', 'data', filename),
			conn = conn,
			args = args
		)

	conn.commit()

	return True
#==============================================================
