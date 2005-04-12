"""GnuMed SOAP importer

(specification by Karsten Hilbert <Karsten.Hilbert@gmx.net>)

This script is designed for importing GnuMed SOAP input "bundle".

	- "bundle" is list of dicts. Each "bundle" is processed one by one. The dicts
	  in the list are INDEPENDANT of each other, so every dict is then taken apart

	- each bundle contain information for:
		- a new clin_narrative row 
		- optionally, additionally data, marked by keys "embedded" into the
		  text of the narrative that are looked up, parsed out and appropiately
		  imported	depending on its 'type' using the business classes.
		- additional data that does not have a key is alerted to the
		  user. The same is done for keys in the text that have no entry in the
		  additional data. The most likely reason for this to happen is the user
		  manually editing the [:...:] embedded strings in 'text' while still
		  in the soap input widget.

	- each dict has the keys: 'soap', 'types', 'text', 'struct_data', 'clin_context'
		- 'soap':			 
			- relates to clin_narrative.soap_cat
		- 'types':
			- a list of strings
			- the strings must be found in clin_item_type.type
			- strings not found in clin_item_type.type are ignored during
			  import and the user is warned about that
		- 'text':
			- the narrative for clin_narrative.narrative, imported as is
			- substrings of the form [:...:] are remembered
		- 'clin_context':
			- 'clin_context' is a dictionary containing clinical
			  context information, required to properly create clinical items.
			  Its 'episode_id' must always be supplied.
		- 'struct_data':
			- this is a dictionary with additional structured data
			- the keys to this dictionary are the "..." parts of the [:...:]
			  found in 'text' (see above)
			- the values will be dicts themselves with the keys
			  'type' and 'struct_data':
				- 'type': the type of 'data' such as 'allergy', 'vaccination',
				  set by the popup widgets inside gmSoapInput
			- 'struct_data' is a dict of fields structured according to 'type'
"""
#===============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmSOAPimporter.py,v $
# $Id: gmSOAPimporter.py,v 1.6 2005-04-12 09:59:16 ncq Exp $
__version__ = "$Revision: 1.6 $"
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>"
__license__ = "GPL (details at http://www.gnu.org)"

# stdlib
import sys, re

# 3rd party
import mx.DateTime as mxDT

# GnuMed
from Gnumed.pycommon import gmLog, gmCLI, gmCfg, gmPG, gmLoginInfo, gmExceptions, gmI18N, gmWhoAmI
from Gnumed.pycommon.gmPyCompat import *
from Gnumed.business import gmClinNarrative, gmPerson, gmVaccination

_log = gmLog.gmDefLog
_cfg = gmCfg.gmDefCfgFile

# module level constants
soap_bundle_SOAP_CAT_KEY = "soap"
soap_bundle_TYPES_KEY = "types"
soap_bundle_TEXT_KEY = "text"
soap_bundle_STRUCT_DATA_KEY = 'struct_data'
soap_bundle_CLIN_CTX_KEY = "clin_context"
soap_bundle_TYPE_KEY = "type"
soap_bundle_EPISODE_ID_KEY = "episode_id"
soap_bundle_ENCOUNTER_ID_KEY = "encounter_id"
soap_bundle_STAFF_ID_KEY = "staff_id"
soap_bundle_SOAP_CATS = ['s','o','a','p']		# these are pretty much fixed
# key pattern: any string between [: and :]. Any of chars in '[:]'
# are forbidden in the key string
soap_bundle_KEY_PATTERN = "\[:.[^:\[\]]*:\]"	 
#===============================================================
class cSOAPImporter:
	"""
	Main SOAP importer class
	"""
	
	#-----------------------------------------------------------
	def __init__(self):
		self.__pat = gmPerson.gmCurrentPatient()		
	#-----------------------------------------------------------
	# external API
	#-----------------------------------------------------------
	def set_patient(self, patient=None):
		pass
	#-----------------------------------------------------------
	def import_soap(self, bundle=None):
		"""
		Import supplied GnuMed SOAP input "bundle". For details consult current
		module's description information.
		
		@param bundle: GnuMed SOAP input data (as described in module's information)
		@type bundle: list of dicts
		"""
		# verify bundle
		if bundle is None or len(bundle) == 0:
			_log.Log(gmLog.lWarn, 'no SOAP bundle to import: [%s]' % bundle)
			return False

		# keys in the text that have no entry in the additional data
		unmatched_keys = []
		# additional data that does not have a key
		unkeyed_data = []

		# process each entry in soap bundle independantly
		for soap_entry in bundle:
			if not self.__import_narrative(soap_entry):
				_log.Log(gmLog.lErr, 'skipping soap entry')
				continue
			_log.Log(gmLog.lInfo, "soap narrative imported OK")

			if not self.__import_embedded_data(soap_entry):
				_log.Log(gmLog.lErr, 'skipping soap entry')
				continue
			_log.Log(gmLog.lInfo, "embedded data imported OK")

		return True
	#-----------------------------------------------------------
	# internal helpers
	#-----------------------------------------------------------
	def __import_narrative(self, soap_entry):
		"""Import soap entry into GnuMed backend.

		@param soap_entry: dictionary containing information related to one
						   SOAP input
		@type soap_entry: dictionary with keys 'soap', 'types', 'text', 'struct_data'

		FIXME: Later we may want to allow for explicitely setting a staff ID to be
		FIXME: used for import. This would allow to import data "on behalf of" someone.
		"""
		if not self.__verify_soap_entry(soap_entry=soap_entry):
			_log.Log(gmLog.lErr, 'cannot verify soap entry')
			return False
		# obtain clinical context information
		epi_id = soap_entry[soap_bundle_CLIN_CTX_KEY][soap_bundle_EPISODE_ID_KEY]
		try:
			enc_id = soap_entry[soap_bundle_CLIN_CTX_KEY][soap_bundle_ENCOUNTER_ID_KEY]
		except KeyError:
			emr = self.__pat.get_clinical_record()
			enc = emr.get_active_encounter()
			enc_id = enc['pk_encounter']

		# create narrative row
		status, narr = gmClinNarrative.create_clin_narrative (
			narrative = soap_entry[soap_bundle_TEXT_KEY],
			soap_cat = soap_entry[soap_bundle_SOAP_CAT_KEY],
			episode_id = epi_id,
			encounter_id = enc_id
		)

		print "episode: %s // encounter: %s" % (epi_id, enc_id)
		print "category: %s" % soap_entry[soap_bundle_SOAP_CAT_KEY], "narrative: %s" % soap_entry[soap_bundle_TEXT_KEY]

		# attach types
		if soap_entry.has_key(soap_bundle_TYPES_KEY):
			print "types	: %s" % soap_entry[soap_bundle_TYPES_KEY]
#			for narr_type in soap_entry[soap_bundle_TYPES_KEY]:
#				narr.attach_type(item_type = narr_type)

		return status
	#-----------------------------------------------------------
	def __verify_soap_entry(self, soap_entry):
		"""
		Perform basic integrity check of a supplied SOAP entry
		
		@param soap_entry: dictionary containing information related to one
						   SOAP input
		@type soap_entry: dictionary with keys 'soap', 'types', 'text', 'struct_data'
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
				_log.Log(gmLog.lErr, 'key [%s] is missing from soap entry' % a_key)
				_log.Log(gmLog.lErr, '%s' % soap_entry)
				return False
		# verify key *values*
		if not soap_entry[soap_bundle_SOAP_CAT_KEY] in soap_bundle_SOAP_CATS:
			_log.Log(gmLog.lErr, 'invalid soap category [%s]' % soap_entry[soap_bundle_SOAP_CAT_KEY])
			_log.Log(gmLog.lErr, '%s' % soap_entry)
			return False
		try:
			soap_entry[soap_bundle_CLIN_CTX_KEY][soap_bundle_EPISODE_ID_KEY]
		except KeyError:
			_log.Log(gmLog.lErr, 'SOAP entry does not provide mandatory episode ID')
			_log.Log(gmLog.lErr, '%s' % soap_entry)
			return False
		return True
	#-----------------------------------------------------------
	def __print_item(self, soap_entry=None, data=None):
		epi_id = soap_entry[soap_bundle_CLIN_CTX_KEY][soap_bundle_EPISODE_ID_KEY]
		try:
			enc_id = soap_entry[soap_bundle_CLIN_CTX_KEY][soap_bundle_ENCOUNTER_ID_KEY]
		except KeyError:
			emr = self.__pat.get_clinical_record()
			enc_id = emr.get_active_encounter()['pk_encounter']

		print "additional data"
		print "type	 : %s" % data[soap_bundle_TYPE_KEY]
		print "episode  : %s" % epi_id
		print "encounter: %s" % enc_id
		for key in data[soap_bundle_STRUCT_DATA_KEY].keys():
			print "%s: %s" % (key, data[soap_bundle_STRUCT_DATA_KEY][key])
	#-----------------------------------------------------------
	# FIXME: to be replaced as written
	_struct_data_handlers = {
		'vaccination': __print_item,
		'allergy': __print_item
	}
	#-----------------------------------------------------------
	def __import_embedded_data(self, soap_entry):
		# find embedded keys
		narr = soap_entry[soap_bundle_TEXT_KEY]
		embedded_keys = re.findall(soap_bundle_KEY_PATTERN, narr)
		embedded_keys = map(lambda key: key.replace("[:","").replace(":]",""), embedded_keys)
		# cross-check
		try:
			struct_data_list = soap_entry[soap_bundle_STRUCT_DATA_KEY]
		except KeyError:
			if len(embedded_keys) == 0:
				return True
			# FIXME: we want to alert the user here and allow her to
			# FIXME: match dangling data with dangling keys ...
			_log.Log(gmLog.lErr, 'dangling data keys: %s' % embedded_keys)
			return False
		# try importing
		for key in struct_data_list.keys():
			embedded_keys.remove(key)
			struct_data = struct_data_list[key]
			try:
				struct_data_handler = cSOAPImporter._struct_data_handlers[struct_data[soap_bundle_TYPE_KEY]]
			except KeyError:
				_log.Log(gmLog.lErr, 'unknown type [%s] of additional data' % struct_data[soap_bundle_TYPE_KEY])
				_log.Log(gmLog.lErr, '%s' % struct_data)
				continue
			if not struct_data_handler(self, soap_entry=soap_entry, data=struct_data):
				_log.Log(gmLog.lErr, 'cannot import structured data')
				continue
		# all done ?
		if len(embedded_keys) != 0:
			# FIXME: we want to alert the user here and allow her to
			# FIXME: match dangling data with dangling keys ...
			_log.Log(gmLog.lErr, 'dangling data keys: %s' % embedded_keys)

		return True
	#-----------------------------------------------------------
	#-----------------------------------------------------------
	#-----------------------------------------------------------
#	def _verify_types(self, soap_entry):
#		"""
#		Perform types key check of a supplied SOAP entry
#		
#		@param soap_entry: dictionary containing information related to one
#						   SOAP input
#		@type soap_entry: dictionary with keys 'soap', 'types', 'text', 'struct_data'
#		"""
#		
#		# FIXME fetch from backend
#		allowed_types = ['Hx']
#		for input_type in soap_entry[soap_bundle_TYPES_KEY]:
#			if not input_type in allowed_types:
#				_log.Log(gmLog.lErr, 'bad clin_item_type.type in supplied soap entry [%s]' % 
#				soap_entry)
#				return False
#		return True
	
#================================================================
# MAIN
#----------------------------------------------------------------
if __name__ == '__main__':
	from Gnumed.pycommon import gmCfg

	_log.SetAllLogLevels(gmLog.lData)
	_log.Log (gmLog.lInfo, "starting SOAP importer...")

	_cfg = gmCfg.gmDefCfgFile	  
	if _cfg is None:
		_log.Log(gmLog.lErr, "Cannot run without config file.")
		sys.exit("Cannot run without config file.")

	try:
		# make sure we have a db connection
		gmPG.set_default_client_encoding('latin1')
		pool = gmPG.ConnectionPool()
		
		# obtain patient
		patient = gmPerson.ask_for_patient()
		if patient is None:
			print "No patient. Exiting gracefully..."
			sys.exit(0)

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
			 soap_bundle_STRUCT_DATA_KEY: {
				'tetanus': {
					soap_bundle_TYPE_KEY: 'vaccination',
					soap_bundle_STRUCT_DATA_KEY: {
						'vaccine':'tetanus'
					}
				},
				'pneumoniae': {
					soap_bundle_TYPE_KEY: 'vaccination',
					soap_bundle_STRUCT_DATA_KEY: {
						'vaccine':'pneumoniae'
					}
				}
			}
			}									 
		]
		importer.import_soap(bundle)

		# clean up
		if patient is not None:
			try:
				patient.cleanup()
			except:
				print "error cleaning up patient"
	except StandardError:
		_log.LogException("unhandled exception caught !", sys.exc_info(), 1)
		# but re-raise them
		raise
	try:
		pool.StopListeners()
	except:
		_log.LogException('unhandled exception caught', sys.exc_info(), verbose=1)
		raise

	_log.Log (gmLog.lInfo, "closing SOAP importer...")
#================================================================
# $Log: gmSOAPimporter.py,v $
# Revision 1.6  2005-04-12 09:59:16  ncq
# - cleanup
# - enable actual backend storage
#
# Revision 1.5  2005/01/31 13:00:40  ncq
# - use ask_for_patient() in gmPerson
#
# Revision 1.4  2005/01/31 10:37:26  ncq
# - gmPatient.py -> gmPerson.py
#
# Revision 1.3  2004/12/20 09:51:28  ncq
# - tie constants to bundle not importer re naming
#
# Revision 1.2  2004/12/19 18:41:55  cfmoro
# Struct keys made module level constants
#
# Revision 1.1  2004/12/18 16:14:13  ncq
# - moved here from test area
#
# Revision 1.7  2004/12/18 16:00:37  ncq
# - final touch up before moving over
#
# Revision 1.6  2004/12/16 17:59:38  cfmoro
# Encapsulation syntax fixed (_ replaced by __). Using tab indentation, in consistency with the rest of gnumed files
#
# Revision 1.5  2004/12/13 19:37:08  ncq
# - cleanup after review by Carlos
# - will be moved to main trunk RSN
#
#
