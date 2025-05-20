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
	'torso-back-hip-muscles.png',
	'heart-anterior-normal.jpg',
	'Persian_anatomy-17th_century.jpg',
	'shoulder-front-bones.png',
	'head-face-muscles-frontal.jpg',
	'Brain-base.png',
	'head-face-lateral.jpg',
	'thorax-organs.jpg',
	'hip-bone-back.png',
	'back.png',
	'torso-lateral-muscles.png',
	'arm-lower-palm_up.png',
	'hand-muscles-palm_down.png',
	'vertebral_column-prolaps-cross-section.png',
	'ear.png',
	'hip-joint-front.png',
	'hip-joint-back.png',
	'hand-bones-palm_up.png',
	'arm-lower-deep-palm_up.png',
	'head-sagittal-section.jpg',
	'leg-lower-front.png',
	'thorax-organs-frontal.png',
	'torso-front-open.png',
	'hip-bone-front.png',
	'skull-vertebral_column-lateral.png',
	'shoulder-muscles-dorsal.png',
	'skull-base.png',
	'sacrum-lateral.png',
	'skeleton-lateral-frontal.png',
	'foot-plantar.png',
	'leg-upper-front.png',
	'head-lateral.jpg',
	'shoulder-upper-arm-front-muscles.png',
	'knee-joint-front.png',
	'neck-muscles-lateral.png',
	'mouth-hard_palate.png',
	'vertebral_column-lateral.png',
	'leg-lower-back.png',
	'bulbus-in-orbita-sagittal.jpg',
	'skull-lateral.jpg',
	'skeleton-lateral.png',
	'thorax-bones.png',
	'skull-anterior.jpg',
	'foot-ankle-joint-lateral.png',
	'femur.png',
	'skeleton-frontal.png',
	'intestine-large.png',
	'elbow-joint-front.png',
	'foot-ankle-joint-medial.png',
	'hand-bones-palm_down.png',
	'knee-joint-retropatellar.png',
	'Persian_digestive_system-17th_century.jpg',
	'larynx-lateral.png',
	'lungs.png',
	'mouth-frontal.png'
]


template_type = u'visual progress note'

#--------------------------------------------------------------
def run(conn=None):

	for filename in template_files:

		args = {}
		args['sname'] = os.path.splitext(filename)[0].replace('-', ', ').replace('_', ' ')
		args['lname'] = u'%s (GNUmed Default)' % args['sname']
		args['ttype'] = template_type
		args['fname'] = filename

		# delete this template
		cmd = u"""delete from ref.paperwork_templates where name_long = %(lname)s"""
		gmPG2.run_rw_queries(link_obj = conn, queries = [{'sql': cmd, 'args': args}], end_tx = False)

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
				'1.0'::TEXT,
				%(fname)s,
				'I'::TEXT,
				'image data missing'::BYTEA
			)"""
		gmPG2.run_rw_queries(link_obj = conn, queries = [{'sql': cmd, 'args': args}], end_tx = False)

		# - data
		cmd = u"""
			UPDATE ref.paperwork_templates
			SET data = %(data)s::BYTEA
			WHERE name_long = %(lname)s"""
		gmPG2.file2bytea (
			query = cmd,
			filename = os.path.join('..', 'sql', 'v12-v13', 'data', filename),
			conn = conn,
			args = args
		)

	conn.commit()

	return True
#==============================================================
