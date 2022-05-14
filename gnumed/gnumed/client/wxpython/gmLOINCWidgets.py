# -*- coding: utf-8 -*-

"""GNUmed LOINC handling widgets."""

#================================================================
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = "GPL v2 or later"

import logging
import sys
import os.path


import wx

if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x
from Gnumed.pycommon import gmNetworkTools
from Gnumed.pycommon import gmDispatcher

from Gnumed.business import gmLOINC

from Gnumed.wxpython import gmAuthWidgets
from Gnumed.wxpython import gmGuiHelpers
from Gnumed.wxpython import gmPhraseWheel


_log = logging.getLogger('gm.ui.loinc')

#================================================================
def update_loinc_reference_data():

	wx.BeginBusyCursor()

	gmDispatcher.send(signal = 'statustext', msg = _('Updating LOINC data can take quite a while...'), beep = True)

	# download
	loinc_zip = gmNetworkTools.download_file(url = 'https://www.gnumed.de/downloads/data/loinc/loinctab.zip', suffix = '.zip')
	if loinc_zip is None:
		wx.EndBusyCursor()
		gmGuiHelpers.gm_show_warning (
			aTitle = _('Downloading LOINC'),
			aMessage = _('Error downloading the latest LOINC data.\n')
		)
		return False

	_log.debug('downloaded zipped LOINC data into [%s]', loinc_zip)

	loinc_dir = gmNetworkTools.unzip_data_pack(filename = loinc_zip)

	# split master data file
	data_fname, license_fname = gmLOINC.split_LOINCDBTXT(input_fname = os.path.join(loinc_dir, 'LOINCDB.TXT'))

	wx.EndBusyCursor()

	conn = gmAuthWidgets.get_dbowner_connection(procedure = _('importing LOINC reference data'))
	if conn is None:
		return False

	wx.BeginBusyCursor()

	# import data
	if gmLOINC.loinc_import(data_fname = data_fname, license_fname = license_fname, conn = conn):
		gmDispatcher.send(signal = 'statustext', msg = _('Successfully imported LOINC reference data.'))
	else:
		gmDispatcher.send(signal = 'statustext', msg = _('Importing LOINC reference data failed.'), beep = True)

	wx.EndBusyCursor()
	return True

#================================================================
class cLOINCPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		mp = gmLOINC.cLOINCMatchProvider()
		mp.setThresholds(1, 2, 4)
		#mp.print_queries = True
		#mp.word_separators = '[ \t:@]+'
		self.matcher = mp
		self.selection_only = False
		self.final_regex = r'\d{1,5}-\d{1}$'
		self.SetToolTip(_('Select a LOINC (Logical Observation Identifiers Names and Codes).'))

#================================================================
# main
#----------------------------------------------------------------
if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmPG2

	#----------------------------------------
	gmPG2.get_connection()
	app = wx.PyWidgetTester(size = (600, 80))
	app.SetWidget(cLOINCPhraseWheel, -1)
	app.MainLoop()
