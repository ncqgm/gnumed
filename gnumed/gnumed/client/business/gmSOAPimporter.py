"""GNUmed SOAP importer

(specification by Karsten Hilbert <Karsten.Hilbert@gmx.net>)

This script is designed for importing GNUmed SOAP input "bundles".

	- "bundle" is list of dicts
	- each "bundle" is processed dict by dict
	- the dicts in the list are INDEPENDANT of each other
	- each dict contains information for one new clin_narrative row
	- each dict has the keys: 'soap', 'types', 'text', 'clin_context'
		- 'soap':
			- relates to clin_narrative.soap_cat
		- 'types':
			- a list of strings
			- the strings must be found in clin_item_type.type
			- strings not found in clin_item_type.type are ignored during
			  import and the user is warned about that
		- 'text':
			- the narrative for clin_narrative.narrative, imported as is
		- 'clin_context':
			- 'clin_context' is a dictionary containing clinical
			  context information, required to properly create clinical items.
			  Its 'episode_id' must always be supplied.
"""
#===============================================================
__version__ = "$Revision: 1.24 $"
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>"
__license__ = "GPL v2 or later (details at http://www.gnu.org)"

# stdlib
import sys, re, logging


# GNUmed
from Gnumed.pycommon import gmExceptions, gmI18N, gmDispatcher
from Gnumed.business import gmClinNarrative, gmPerson, gmPersonSearch


_log = logging.getLogger('gm.soap')


# module level constants
soap_bundle_SOAP_CAT_KEY = "soap"
soap_bundle_TYPES_KEY = "types"
soap_bundle_TEXT_KEY = "text"
soap_bundle_CLIN_CTX_KEY = "clin_context"
soap_bundle_TYPE_KEY = "type"
soap_bundle_EPISODE_ID_KEY = "episode_id"
soap_bundle_ENCOUNTER_ID_KEY = "encounter_id"
soap_bundle_STAFF_ID_KEY = "staff_id"
soap_bundle_SOAP_CATS = ['s','o','a','p']		# these are pretty much fixed
#===============================================================
class cSOAPImporter:
	"""
	Main SOAP importer class
	"""
	#-----------------------------------------------------------
	def __init__(self):
		pass
	#-----------------------------------------------------------
	# external API
	#-----------------------------------------------------------
	def import_soap(self, bundle=None):
		"""
		Import supplied GNUmed SOAP input "bundle". For details consult current
		module's description information.

		@param bundle: GNUmed SOAP input data (as described in module's information)
		@type bundle: list of dicts
		"""
		# process each entry in soap bundle independently
		for soap_entry in bundle:
			if not self.__import_narrative(soap_entry):
				_log.error('skipping soap entry')
				continue
		gmDispatcher.send(signal = 'clin_item_updated')
		return True
	#-----------------------------------------------------------
	# internal helpers
	#-----------------------------------------------------------
	def __import_narrative(self, soap_entry):
		"""Import soap entry into GNUmed backend.

		@param soap_entry: dictionary containing information related
						   to one SOAP input line
		@type soap_entry: dictionary with keys 'soap', 'types', 'text'

		FIXME: Later we may want to allow for explicitly setting a staff ID to be
		FIXME: used for import. This would allow to import data "on behalf of" someone.
		"""
		if not self.__verify_soap_entry(soap_entry=soap_entry):
			_log.error('cannot verify soap entry')
			return False
		# obtain clinical context information
		emr = gmPerson.gmCurrentPatient().emr
		epi_id = soap_entry[soap_bundle_CLIN_CTX_KEY][soap_bundle_EPISODE_ID_KEY]
		try:
			enc_id = soap_entry[soap_bundle_CLIN_CTX_KEY][soap_bundle_ENCOUNTER_ID_KEY]
		except KeyError:
			enc = emr.active_encounter
			enc_id = enc['pk_encounter']

		# create narrative row
		narr = gmClinNarrative.create_narrative_item (
			narrative = soap_entry[soap_bundle_TEXT_KEY],
			soap_cat = soap_entry[soap_bundle_SOAP_CAT_KEY],
			episode_id = epi_id,
			encounter_id = enc_id
		)

#		# attach types
#		if soap_bundle_TYPES_KEY in soap_entry:
#			print "code missing to attach types to imported narrative"

		return (narr is not None)
	#-----------------------------------------------------------
	def __verify_soap_entry(self, soap_entry):
		"""Perform basic integrity check of a supplied SOAP entry.

		@param soap_entry: dictionary containing information related to one
						   SOAP input
		@type soap_entry: dictionary with keys 'soap', 'types', 'text'
		"""
		required_keys = [
			soap_bundle_SOAP_CAT_KEY,
			soap_bundle_CLIN_CTX_KEY,
			soap_bundle_TEXT_KEY
		]
		# verify key existence
		for a_key in required_keys:
			try:
				soap_entry[a_key]
			except KeyError:
				_log.error('key [%s] is missing from soap entry' % a_key)
				_log.error('%s' % soap_entry)
				return False
		# verify key *values*
		if not soap_entry[soap_bundle_SOAP_CAT_KEY] in soap_bundle_SOAP_CATS:
			_log.error('invalid soap category [%s]' % soap_entry[soap_bundle_SOAP_CAT_KEY])
			_log.error('%s' % soap_entry)
			return False
		try:
			soap_entry[soap_bundle_CLIN_CTX_KEY][soap_bundle_EPISODE_ID_KEY]
		except KeyError:
			_log.error('SOAP entry does not provide mandatory episode ID')
			_log.error('%s' % soap_entry)
			return False
		return True
	#-----------------------------------------------------------
#	def _verify_types(self, soap_entry):
#		"""
#		Perform types key check of a supplied SOAP entry
#
#		@param soap_entry: dictionary containing information related to one
#						   SOAP input
#		@type soap_entry: dictionary with keys 'soap', 'types', 'text'
#		"""
#
#		# FIXME fetch from backend
#		allowed_types = ['Hx']
#		for input_type in soap_entry[soap_bundle_TYPES_KEY]:
#			if not input_type in allowed_types:
#				_log.error('bad clin_item_type.type in supplied soap entry [%s]' % 
#				soap_entry)
#				return False
#		return True
	
#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':
	_log.info("starting SOAP importer...")

	# obtain patient
	patient = gmPersonSearch.ask_for_patient()
	if patient is None:
		print("No patient. Exiting gracefully...")
		sys.exit(0)
	gmPerson.set_active_patient(patient=patient)

	# now import
	importer = cSOAPImporter()
	bundle = [
		{soap_bundle_SOAP_CAT_KEY: 's',
		 soap_bundle_TYPES_KEY: ['Hx'],
		 soap_bundle_TEXT_KEY: 'Test subjective narrative',
		 soap_bundle_CLIN_CTX_KEY: {soap_bundle_EPISODE_ID_KEY: '1'}
		},
		{soap_bundle_SOAP_CAT_KEY: 'o',
		 soap_bundle_TYPES_KEY: ['Hx'],
		 soap_bundle_TEXT_KEY: 'Test objective narrative',
		 soap_bundle_CLIN_CTX_KEY: {soap_bundle_EPISODE_ID_KEY: '1'}
		},
		{soap_bundle_SOAP_CAT_KEY: 'a',
		 soap_bundle_TYPES_KEY: ['Hx'],
		 soap_bundle_TEXT_KEY: 'Test assesment narrative',
		 soap_bundle_CLIN_CTX_KEY: {soap_bundle_EPISODE_ID_KEY: '1'}
		},
		{soap_bundle_SOAP_CAT_KEY: 'p',
		 soap_bundle_TYPES_KEY: ['Hx'],
		 soap_bundle_TEXT_KEY: 'Test plan narrative. [:tetanus:]. [:pneumoniae:].',
		 soap_bundle_CLIN_CTX_KEY: {
		 	soap_bundle_EPISODE_ID_KEY: '1',
			soap_bundle_ENCOUNTER_ID_KEY: '1',
			soap_bundle_STAFF_ID_KEY: '1'
			},
		}
	]
	importer.import_soap(bundle)

	# clean up
	if patient is not None:
		try:
			patient.cleanup()
		except Exception:
			print("error cleaning up patient")

	_log.info("closing SOAP importer...")
#================================================================
