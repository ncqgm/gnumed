"""GnuMed SOAP importer (specification by Karsten Hilbert <Karsten.Hilbert@gmx.net>)

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
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/cfmoro/soap_input/Attic/gmSOAPimporter.py,v $
# $Id: gmSOAPimporter.py,v 1.6 2004-12-16 17:59:38 cfmoro Exp $
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
from Gnumed.business import gmClinNarrative, gmPatient, gmVaccination

_log = gmLog.gmDefLog
_cfg = gmCfg.gmDefCfgFile
#===============================================================
class cSOAPImporter:
	"""
	Main SOAP importer class
	"""
	_soap_cats = ['s','o','a','p']		# these are pretty much fixed
	_soap_cat_key = "soap"
	_types_key = "types"
	_text_key = "text"
	_struct_data_key = 'struct_data'
	_clin_ctx_key = "clin_context"
	_type_key = "type"
	_episode_id_key = "episode_id"
	_encounter_id_key = "encounter_id"
	_staff_id_key = "staff_id"
	# key pattern: any string between [: and :]. Any of chars in '[:]'
	# are forbidden in the key string
	_key_pattern = "\[:.[^:\[\]]*:\]"	 
	#-----------------------------------------------------------
	def __init__(self):
		self.__pat = gmPatient.gmCurrentPatient()		
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
		epi_id = soap_entry[cSOAPImporter._clin_ctx_key][cSOAPImporter._episode_id_key]
		try:
			enc_id = soap_entry[cSOAPImporter._clin_ctx_key][cSOAPImporter._encounter_id_key]
		except KeyError:
			emr = self.__pat.get_clinical_record()
			print emr
			enc = emr.get_active_encounter()
			print enc
			enc_id = emr.get_active_encounter()['pk_encounter']

		# create narrative row
		status = True

#		status, narr = gmClinNarrative.create_clin_narrative (
#			narrative = soap_entry[cSOAPImporter._text_key],
#			soap_cat = soap_entry[cSOAPImporter._soap_cat_key],
#			episode_id = epi_id,
#			encounter_id = enc_id
#		)

		print "SOAP row created"
		print "episode  : %s" % epi_id
		print "encounter: %s" % enc_id
		print "category : %s" % soap_entry[cSOAPImporter._soap_cat_key]
		print "narrative: %s" % soap_entry[cSOAPImporter._text_key]

		# attach types
		if soap_entry.has_key(cSOAPImporter._types_key):
			print "types	: %s" % soap_entry[cSOAPImporter._types_key]
#			for narr_type in soap_entry[cSOAPImporter._types_key]:
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
			cSOAPImporter._soap_cat_key,
			cSOAPImporter._clin_ctx_key,
			cSOAPImporter._text_key
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
		if not soap_entry[cSOAPImporter._soap_cat_key] in cSOAPImporter._soap_cats:
			_log.Log(gmLog.lErr, 'invalid soap category [%s]' % soap_entry[cSOAPImporter._soap_cat_key])
			_log.Log(gmLog.lErr, '%s' % soap_entry)
			return False
		try:
			soap_entry[cSOAPImporter._clin_ctx_key][cSOAPImporter._episode_id_key]
		except KeyError:
			_log.Log(gmLog.lErr, 'SOAP entry does not provide mandatory episode ID')
			_log.Log(gmLog.lErr, '%s' % soap_entry)
			return False
		return True
	#-----------------------------------------------------------
	def __print_item(self, soap_entry=None, data=None):
		epi_id = soap_entry[cSOAPImporter._clin_ctx_key][cSOAPImporter._episode_id_key]
		try:
			enc_id = soap_entry[cSOAPImporter._clin_ctx_key][cSOAPImporter._encounter_id_key]
		except KeyError:
			emr = self.__pat.get_clinical_record()
			enc_id = emr.get_active_encounter()['pk_encounter']

		print "additional data"
		print "type	 : %s" % data[cSOAPImporter._type_key]
		print "episode  : %s" % epi_id
		print "encounter: %s" % enc_id
		for key in data[cSOAPImporter._struct_data_key].keys():
			print "%s: %s" % (key, data[cSOAPImporter._struct_data_key][key])
	#-----------------------------------------------------------
	# FIXME: to be replaced as written
	_struct_data_handlers = {
		'vaccination': __print_item,
		'allergy': __print_item
	}
	#-----------------------------------------------------------
	def __import_embedded_data(self, soap_entry):
		# find embedded keys
		narr = soap_entry[cSOAPImporter._text_key]
		embedded_keys = re.findall(cSOAPImporter._key_pattern, narr)
		embedded_keys = map(lambda key: key.replace("[:","").replace(":]",""), embedded_keys)
		# cross-check
		try:
			struct_data_list = soap_entry[cSOAPImporter._struct_data_key]
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
				struct_data_handler = cSOAPImporter._struct_data_handlers[struct_data[cSOAPImporter._type_key]]
			except KeyError:
				_log.Log(gmLog.lErr, 'unknown type [%s] of additional data' % struct_data[cSOAPImporter._type_key])
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
#		for input_type in soap_entry[cSOAPImporter._types_key]:
#			if not input_type in allowed_types:
#				_log.Log(gmLog.lErr, 'bad clin_item_type.type in supplied soap entry [%s]' % 
#				soap_entry)
#				return False
#		return True


#== Module convenience functions (for standalone use) =======================
def prompted_input(prompt, default=None):
	"""
	Obtains entry from standard input
	
	promp - Promt text to display in standard output
	default - Default value (for user to press only intro)
	"""
	usr_input = raw_input(prompt)
	if usr_input == '':
		return default
	return usr_input
	
#------------------------------------------------------------				  
def askForPatient():
	"""
		Main module application patient selection function.
	"""
	
	# Variable initializations
	pat_searcher = gmPatient.cPatientSearcher_SQL()

	# Ask patient
	patient_term = prompted_input("\nPatient search term (or 'bye' to exit) (eg. Kirk): ")
	
	if patient_term == 'bye':
		return None
	search_ids = pat_searcher.get_patient_ids(search_term = patient_term)
	if search_ids is None or len(search_ids) == 0:
		prompted_input("No patient matches the query term. Press any key to continue.")
		return None
	elif len(search_ids) > 1:
		prompted_input("Various patients match the query term. Press any key to continue.")
		return None
	patient_id = search_ids[0]
	patient = gmPatient.gmCurrentPatient(patient_id)
	
	return patient
	
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
		patient = askForPatient()
		if patient is None:
			print "No patient. Exiting gracefully..."
			sys.exit(0)

		# now import
		importer = cSOAPImporter()
		bundle = [
			{cSOAPImporter._soap_cat_key: 's',
			 cSOAPImporter._types_key: ['Hx'],
			 cSOAPImporter._text_key: 'Test subjective narrative',
			 cSOAPImporter._clin_ctx_key: {cSOAPImporter._episode_id_key: '1'}
			},
			{cSOAPImporter._soap_cat_key: 'o',
			 cSOAPImporter._types_key: ['Hx'],
			 cSOAPImporter._text_key: 'Test objective narrative',
			 cSOAPImporter._clin_ctx_key: {cSOAPImporter._episode_id_key: '1'}
			},
			{cSOAPImporter._soap_cat_key: 'a',
			 cSOAPImporter._types_key: ['Hx'],
			 cSOAPImporter._text_key: 'Test assesment narrative',
			 cSOAPImporter._clin_ctx_key: {cSOAPImporter._episode_id_key: '1'}
			},
			{cSOAPImporter._soap_cat_key: 'p',
			 cSOAPImporter._types_key: ['Hx'],
			 cSOAPImporter._text_key: 'Test plan narrative. [:tetanus:]. [:pneumoniae:].',
			 cSOAPImporter._clin_ctx_key: {
			 	cSOAPImporter._episode_id_key: '1',
				cSOAPImporter._encounter_id_key: '1',
				cSOAPImporter._staff_id_key: '1'
				},
			 cSOAPImporter._struct_data_key: {
				'tetanus': {
					cSOAPImporter._type_key: 'vaccination',
					cSOAPImporter._struct_data_key: {
						'vaccine':'tetanus'
					}
				},
				'pneumoniae': {
					cSOAPImporter._type_key: 'vaccination',
					cSOAPImporter._struct_data_key: {
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
# Revision 1.6  2004-12-16 17:59:38  cfmoro
# Encapsulation syntax fixed (_ replaced by __). Using tab indentation, in consistency with the rest of gnumed files
#
# Revision 1.5  2004/12/13 19:37:08  ncq
# - cleanup after review by Carlos
# - will be moved to main trunk RSN
#
#
