"""GNUmed <-> arriba coupling.

The API definition was provided by Thomas Scheithauer
<thomas.scheithauer@gmx.net>.

The GNUmed project is NOT authorized to share the actual
interface specs so you need to get in contact with Thomas in
order to re-implement the interface.

http://www.arriba-hausarzt.de

Note that that official casing is "arriba" rather
than "ARRIBA" or "Arriba".
"""
#============================================================
__license__ = "GPL"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>"


# std lib
import sys
import io
import subprocess
import logging


# GNUmed libraries
if __name__ == '__main__':
	sys.path.insert(0, '../../')
	_ = lambda x:x

from Gnumed.pycommon import gmTools
from Gnumed.pycommon import gmShellAPI
from Gnumed.pycommon import gmDispatcher

from Gnumed.business import gmXdtMappings


_log = logging.getLogger('gm.arriba')
#============================================================
class cArriba(object):

	_date_format = '%d%m%Y'

	def __init__(self):
		self.path_to_binary = None
		self.pdf_result = None
		self.xml_result = None
	#--------------------------------------------------------
	# internal helpers
	#--------------------------------------------------------
	def __detect_binary(self):

		if self.path_to_binary is not None:
			return True

		found, cmd = gmShellAPI.find_first_binary(binaries = [
			r'/usr/local/bin/arriba',
			r'/usr/bin/arriba',
			r'arriba',
			r'arriba.exe'
#			r'c:\programs\freediams\freediams.exe',
#			r'freediams.exe'
		])

		if found:
			self.path_to_binary = cmd
			return True

#		try:
#			self.custom_path_to_binary
#		except AttributeError:
#			_log.error('cannot find FreeDiams binary, no custom path set')
#			return False

#		found, cmd = gmShellAPI.detect_external_binary(binary = self.custom_path_to_binary)
#		if found:
#			self.path_to_binary = cmd
#			return True

		_log.error('cannot find arriba binary')
		return False
	#--------------------------------------------------------
	def __write_config_file(self, patient=None):
		xml = """<?xml version="1.0" encoding="UTF-8"?>

<konsultation version="1.1" xmlns="https://gpzk.de/ns/arriba/start-konfiguration">
	<parameter>
		%s
		<idle-timeout>0</idle-timeout>
	</parameter>
	<speicherorte>
		<status>%s</status>
		<ergebnis-xml>%s</ergebnis-xml>
		<ergebnis-pdf>%s</ergebnis-pdf>
	</speicherorte>
</konsultation>
"""
		if patient is None:
			pat_xml = ''
		else:
			active_name = patient.get_active_name()
			pat_xml = """<vorname>%s%s</vorname>
		<nachname>%s</nachname>
		<geschlecht>%s</geschlecht>
		<geburtsdatum>%s</geburtsdatum>""" % (
			active_name['firstnames'],
			gmTools.coalesce(active_name['preferred'], '', ' (%s)'),
			active_name['lastnames'],
			gmXdtMappings.map_gender_gm2xdt[patient['gender']],
			patient.get_formatted_dob(format = cArriba._date_format, none_string = '00009999')
		)

		fname_cfg = gmTools.get_unique_filename(prefix = 'gm2arriba-', suffix = '.xml')
		fname_status = gmTools.get_unique_filename(prefix = 'arriba2gm_status-', suffix = '.xml')
		self.xml_result = gmTools.get_unique_filename(prefix = 'arriba2gm_result-', suffix = '.xml')
		self.pdf_result = gmTools.get_unique_filename(prefix = 'arriba2gm_result-', suffix = '.pdf')
		xml_file = io.open(fname_cfg, mode = 'wt', encoding = 'utf8', errors = 'replace')
		xml_file.write (xml % (
			pat_xml,
			fname_status,
			self.xml_result,
			self.pdf_result
		))
		xml_file.close()

		return fname_cfg
	#--------------------------------------------------------
	# external API
	#--------------------------------------------------------
	def run(self, patient=None, debug=False):
		self.pdf_result = None

		cfg_file = self.__write_config_file(patient = patient)

		# FIXME: add user-configured path
		if not self.__detect_binary():
			return False

		args = (
			self.path_to_binary,
			'--file=%s' % cfg_file,
			'--show-cli-pane=%s' % gmTools.bool2subst(debug, 'true', 'false')
		)

		try:
			subprocess.check_call(args = args, close_fds = True)
		except (OSError, ValueError, subprocess.CalledProcessError):
			_log.exception('there was a problem executing [%s]', self.path_to_binary)
			gmDispatcher.send(signal = 'statustext', msg = _('Cannot run [arriba] !'), beep = True)
			return False

		try:
			open(self.pdf_result).close()
		except Exception:
			_log.exception('error accessing [%s]', self.pdf_result)
			gmDispatcher.send(signal = 'statustext', msg = _('No [arriba] result found in [%s].') % self.pdf_result, beep = False)
			return False

		return True
#============================================================
# main
#------------------------------------------------------------
if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit()

	if sys.argv[1] != 'test':
		sys.exit()

	from Gnumed.pycommon import gmI18N
	from Gnumed.pycommon import gmDateTime
	gmI18N.activate_locale()
	gmI18N.install_domain()
	gmDateTime.init()

	from Gnumed.business import gmPerson

	gmPerson.set_active_patient(patient = gmPerson.cPerson(aPK_obj = 12))

	arriba = cArriba()
	print(arriba)
	arriba.run(patient = gmPerson.gmCurrentPatient(), debug = True)
