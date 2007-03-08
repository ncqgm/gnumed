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
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmSOAPimporter.py,v $
# $Id: gmSOAPimporter.py,v 1.18 2007-03-08 11:31:08 ncq Exp $
__version__ = "$Revision: 1.18 $"
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>"
__license__ = "GPL (details at http://www.gnu.org)"

# stdlib
import sys, re

# 3rd party
import mx.DateTime as mxDT

# GnuMed
from Gnumed.pycommon import gmLog, gmCLI, gmCfg, gmExceptions, gmI18N, gmDispatcher, gmSignals
from Gnumed.business import gmClinNarrative, gmPerson

_log = gmLog.gmDefLog
_cfg = gmCfg.gmDefCfgFile

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
		Import supplied GnuMed SOAP input "bundle". For details consult current
		module's description information.
		
		@param bundle: GnuMed SOAP input data (as described in module's information)
		@type bundle: list of dicts
		"""
		# process each entry in soap bundle independently
		for soap_entry in bundle:
			if not self.__import_narrative(soap_entry):
				_log.Log(gmLog.lErr, 'skipping soap entry')
				continue
		gmDispatcher.send(gmSignals.clin_item_updated())
		return True
	#-----------------------------------------------------------
	# internal helpers
	#-----------------------------------------------------------
	def __import_narrative(self, soap_entry):
		"""Import soap entry into GnuMed backend.

		@param soap_entry: dictionary containing information related
						   to one SOAP input line
		@type soap_entry: dictionary with keys 'soap', 'types', 'text'

		FIXME: Later we may want to allow for explicitely setting a staff ID to be
		FIXME: used for import. This would allow to import data "on behalf of" someone.
		"""
		if not self.__verify_soap_entry(soap_entry=soap_entry):
			_log.Log(gmLog.lErr, 'cannot verify soap entry')
			return False
		# obtain clinical context information
		emr = gmPerson.gmCurrentPatient().get_emr()
		epi_id = soap_entry[soap_bundle_CLIN_CTX_KEY][soap_bundle_EPISODE_ID_KEY]
		try:
			enc_id = soap_entry[soap_bundle_CLIN_CTX_KEY][soap_bundle_ENCOUNTER_ID_KEY]
		except KeyError:
			enc = emr.get_active_encounter()
			enc_id = enc['pk_encounter']

		# create narrative row
		status, narr = gmClinNarrative.create_clin_narrative (
			narrative = soap_entry[soap_bundle_TEXT_KEY],
			soap_cat = soap_entry[soap_bundle_SOAP_CAT_KEY],
			episode_id = epi_id,
			encounter_id = enc_id
		)

#		# attach types
#		if soap_entry.has_key(soap_bundle_TYPES_KEY):
#			print "code missing to attach types to imported narrative"

		return status
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
		# obtain patient
		patient = gmPerson.ask_for_patient()
		if patient is None:
			print "No patient. Exiting gracefully..."
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
			except:
				print "error cleaning up patient"
	except StandardError:
		_log.LogException("unhandled exception caught !", sys.exc_info(), 1)
		# but re-raise them
		raise

	_log.Log (gmLog.lInfo, "closing SOAP importer...")
#================================================================
# $Log: gmSOAPimporter.py,v $
# Revision 1.18  2007-03-08 11:31:08  ncq
# - just cleanup
#
# Revision 1.17  2006/10/31 11:27:15  ncq
# - remove use of gmPG
#
# Revision 1.16  2006/10/25 07:17:40  ncq
# - no more gmPG
# - no more cClinItem
#
# Revision 1.15  2006/10/23 13:06:54  ncq
# - vaccs DB object not yet converted
#
# Revision 1.14  2006/07/19 21:37:51  ncq
# - cleanup
#
# Revision 1.13  2006/06/17 13:58:39  ncq
# - cleanup
#
# Revision 1.12  2006/05/12 12:05:04  ncq
# - cleanup
#
# Revision 1.11  2006/05/04 09:49:20  ncq
# - get_clinical_record() -> get_emr()
# - adjust to changes in set_active_patient()
# - need explicit set_active_patient() after ask_for_patient() if wanted
#
# Revision 1.10  2005/10/19 09:14:46  ncq
# - remove half-baked support for embedded data, now handled elsewhere
# - general cleanup/doc fixes
#
# Revision 1.9  2005/10/11 21:50:33  ncq
# - create_clin_narrative() should not be aware of emr object
#
# Revision 1.8  2005/10/08 12:33:08  sjtan
# tree can be updated now without refetching entire cache; done by passing emr object to create_xxxx methods and calling emr.update_cache(key,obj);refresh_historical_tree non-destructively checks for changes and removes removed nodes and adds them if cache mismatch.
#
# Revision 1.7  2005/05/17 08:03:30  ncq
# - cleanup
#
# Revision 1.6  2005/04/12 09:59:16  ncq
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
