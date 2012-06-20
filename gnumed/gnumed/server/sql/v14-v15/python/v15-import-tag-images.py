#==============================================================
# GNUmed database schema change script
#
# License: GPL v2 or later
# Author: karsten.hilbert@gmx.net
# 
#==============================================================
import os

from Gnumed.pycommon import gmPG2

#--------------------------------------------------------------
def run(conn=None):

	gmPG2.file2bytea (
		query = u"""
UPDATE ref.tag_image
SET image = %(data)s::bytea
WHERE description = 'Occupation: astronaut'
""",
		filename = os.path.join('..', 'sql', 'v14-v15', 'data', 'johnny_automatic_astronaut_s_helmet.png'),
		conn = conn
	)

	gmPG2.file2bytea (
		query = u"""
UPDATE ref.tag_image
SET image = %(data)s::bytea
WHERE description = 'smokes'
""",
		filename = os.path.join('..', 'sql', 'v14-v15', 'data', 'Anonymous_aiga_smoking.png'),
		conn = conn
	)

	gmPG2.file2bytea (
		query = u"""
UPDATE ref.tag_image
SET image = %(data)s::bytea
WHERE description = 'often late'
""",
		filename = os.path.join('..', 'sql', 'v14-v15', 'data', 'CoD_fsfe_Pocket_watch_icon.png'),
		conn = conn
	)

	gmPG2.file2bytea (
		query = u"""
UPDATE ref.tag_image
SET image = %(data)s::bytea
WHERE description = 'Extra care !'
""",
		filename = os.path.join('..', 'sql', 'v14-v15', 'data', 'eastshores_Warning_Notification.png'),
		conn = conn
	)

	gmPG2.file2bytea (
		query = u"""
UPDATE ref.tag_image
SET image = %(data)s::bytea
WHERE description = 'mobility impairment'
""",
		filename = os.path.join('..', 'sql', 'v14-v15', 'data', 'schoolfreeware_WheelChair_Sign.png'),
		conn = conn
	)

	gmPG2.file2bytea (
		query = u"""
UPDATE ref.tag_image
SET image = %(data)s::bytea
WHERE description = 'minor depression'
""",
		filename = os.path.join('..', 'sql', 'v14-v15', 'data', 'weather-few-clouds.png'),
		conn = conn
	)

	gmPG2.file2bytea (
		query = u"""
UPDATE ref.tag_image
SET image = %(data)s::bytea
WHERE description = 'major depression'
""",
		filename = os.path.join('..', 'sql', 'v14-v15', 'data', 'weather-showers-scattered.png'),
		conn = conn
	)

	gmPG2.file2bytea (
		query = u"""
UPDATE ref.tag_image
SET image = %(data)s::bytea
WHERE description = 'choleric'
""",
		filename = os.path.join('..', 'sql', 'v14-v15', 'data', 'weather-storm.png'),
		conn = conn
	)

	return True
#==============================================================
