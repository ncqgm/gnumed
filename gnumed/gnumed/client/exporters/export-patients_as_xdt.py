# -*- coding: utf8 -*-
"""Patient xDT exporter.

Copyright: authors
"""
#============================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL v2 or later (details at http://www.gnu.org)'

import sys
import logging
import os


if __name__ == '__main__':
	sys.path.insert(0, '../../')
from Gnumed.pycommon import gmI18N
if __name__ == '__main__':
	gmI18N.activate_locale()
	gmI18N.install_domain('gnumed')
from Gnumed.pycommon import gmPG2
from Gnumed.pycommon import gmTools

from Gnumed.business import gmPerson


_log = logging.getLogger('gm.xdt_exp')
#============================================================
def export_patients_as_xdt(base_path=None):

	path = gmTools.get_unique_filename (
		prefix = 'gm-export-',
		suffix = '',
		tmp_dir = base_path
	)
	path = os.path.splitext(path)[0]
	gmTools.mkdir(path)

	for ID in gmPerson.get_person_IDs():
		_log.info('exporting patient #%s', ID)
		identity = gmPerson.cPerson(aPK_obj = ID)
		_log.info('identity: %s', identity)
		filename = gmTools.get_unique_filename (
			prefix = 'gm_exp-%s-' % identity.subdir_name,
			suffix = '.xdt',
			tmp_dir = path
		)
		_log.info('file: %s', filename)
		identity.export_as_gdt (
			filename = filename,
			encoding = 'utf8'
			#encoding = u'iso-8859-15'
		)

#============================================================
# main
#------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != "test":
		sys.exit()

	path = None
	if len(sys.argv) > 2:
		path = sys.argv[2]

	paths = gmTools.gmPaths(app_name = 'gnumed')
	export_patients_as_xdt(base_path = path)
