"""GnuMed SOAP importer (specification by Karsten Hilbert <Karsten.Hilbert@gmx.net>)

This script is designed for importing GnuMed SOAP input "bundle". 

    - "bundle" is list of dicts. Each "bundle" is processed one by one. The dicts
      in the list are INDEPENDANT of each other, so every dict is then taken apart
      
    - each bundle contain information for:
        - a new clin_narrative row 
        - optionally, additionally data, marked by keys "embedded" into the
          text of the narrative that are looked up, parsed out and appropiately
          imported  depending on its 'type' using the business classes.
        - additional data that does not have a key is alerted to the
          user. The same is done for keys in the text that have no entry in the
          additional data. The most likely reason for this to happen is the user
          manually editing the [:...:] embedded strings in 'text' while still
          in the soap input widget.
      
    - each dict has the keys: 'soap', 'types', 'text', 'data'
        - 'soap':            
            - relates to clin_narrative.soap_cat
        - 'types':
            - a list of strings
            - the strings must be found in clin_item_type.type
            - strings not found in clin_item_type.type are ignored during
              import and the user is warned about that
        -'text':
            - the narrative for clin_narrative.narrative, imported as is
            - substrings of the form [:...:] are remembered

        -'data':
            - this is a dictionary with additional data
            - the keys to this dictionary are the "..." parts of the [:...:]
              found in 'text' (see above)
            - the values will be dicts themselves with the keys
              'type' and 'data':
                - 'type': the type of 'data' such as 'allergy', 'vaccination',
                  set by the popup widgets inside gmSoapInput
            - 'data' is a dict of fields depending on 'type'
"""
#===============================================================
__version__ = "$Revision: 1.1 $"
__author__ = "Carlos Moro <cfmoro1976@yahoo.es>"
__license__ = "GPL, details at http://www.gnu.org"

# stdlib
import sys

from Gnumed.pycommon import gmLog, gmCLI
if __name__ == '__main__':
    if gmCLI.has_arg('--debug'):
        gmLog.gmDefLog.SetAllLogLevels(gmLog.lData)
    else:
        gmLog.gmDefLog.SetAllLogLevels(gmLog.lInfo)

from Gnumed.pycommon import gmCfg, gmPG, gmLoginInfo, gmExceptions, gmI18N
from Gnumed.pycommon.gmPyCompat import *
from Gnumed.business import gmClinNarrative, gmPatient

import mx.DateTime as mxDT

_log = gmLog.gmDefLog
_cfg = gmCfg.gmDefCfgFile
#===============================================================
class cSOAPImporter:
    """
    Main SOAP importer class
    """
    
    #-----------------------------------------------------------
    def __init__(self):
                        
        self._pat = gmPatient.gmCurrentPatient()
            
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
            _log.Log(gmLog.lErr, 'cannot import supplied SOAP bundle: [%s]' % bundle)
            return False        
            
        # process each entry in soap bundle indepently
        for soap_entry in bundle:
            if not self._verify_soap_entry(soap_entry):
                _log.Log(gmLog.lErr, 'cannot import soap entry [%s]' % soap_entry)
                continue
            _log.Log(gmLog.lInfo, "soap entry verified OK: [%s]" % soap_entry)
            self._soap_to_db(soap_entry)
                            
    #-----------------------------------------------------------
    # internal helpers
    #-----------------------------------------------------------
    def _soap_to_db(self, soap_entry):
        """
        Dump soap entry to GnuMed backend
        
        @param soap_entry: dictionary containing information related to one
                           SOAP input
        @type soap_entry: dictionary with keys 'soap', 'types', 'text', 'data'        
        """

        # obtain active encounter and episode
        emr = self._pat.get_clinical_record()
        active_encounter = emr.get_active_encounter()
        active_episode = emr.get_active_episode()
        
        # create narrative row
        stat, narr = gmClinNarrative.create_clin_narrative(narrative = soap_entry['text'],
        soap_cat = soap_entry['soap'], episode_id= active_episode['pk_episode'], encounter_id=active_encounter['pk_encounter'])
        
        return stat
        	
    #-----------------------------------------------------------        
    def _verify_soap_entry(self, soap_entry):
        """
        Perform basic integrity check of a supplied SOAP entry
        
        @param soap_entry: dictionary containing information related to one
                           SOAP input
        @type soap_entry: dictionary with keys 'soap', 'types', 'text', 'data'
        """
        
        must_keys = ['soap', 'types', 'text', 'data']
        
        # verify soap entry contains all must have keys
        for a_must_key in must_keys:
            if not soap_entry.has_key(a_must_key):
                _log.Log(gmLog.lErr, 'soap entry [%s] has not key [%s]' %
                (soap_entry, a_must_key))
                return False
        
        # verify basic key's values indepently
        result = True
        tmp = self._verify_soap(soap_entry)
        if not tmp:
            result = False
        tmp = self._verify_types(soap_entry)
        if not tmp:
            result = False
        tmp = self._verify_text(soap_entry)
        if not tmp:
            result = False
             
        return result

    #-----------------------------------------------------------
    def _verify_soap(self, soap_entry):
        """
        Perform soap key check of a supplied SOAP entry
        
        @param soap_entry: dictionary containing information related to one
                           SOAP input
        @type soap_entry: dictionary with keys 'soap', 'types', 'text', 'data'
        """
        
        # FIXME fetch from backend
        soap_cats = ['s','o','a','p']
        if not soap_entry['soap'] in soap_cats:
            _log.Log(gmLog.lErr, 'bad clin_narrative.soap_cat in supplied soap entry [%s]' % 
            soap_entry)
            return False
        return True

    #-----------------------------------------------------------
    def _verify_types(self, soap_entry):
        """
        Perform types key check of a supplied SOAP entry
        
        @param soap_entry: dictionary containing information related to one
                           SOAP input
        @type soap_entry: dictionary with keys 'soap', 'types', 'text', 'data'
        """
        
        # FIXME fetch from backend
        allowed_types = ['Hx']
        for input_type in soap_entry['types']:
            if not input_type in allowed_types:
                _log.Log(gmLog.lErr, 'bad clin_item_type.type in supplied soap entry [%s]' % 
                soap_entry)
                return False
        return True
        
    #-----------------------------------------------------------
    def _verify_text(self, soap_entry):
        """
        Perform text check of a supplied SOAP entry
        
        @param soap_entry: dictionary containing information related to one
                           SOAP input
        @type soap_entry: dictionary with keys 'soap', 'types', 'text', 'data'
        """
                
        text = soap_entry['text']
        if text is None or len(text) == 0:
            _log.Log(gmLog.lErr, 'empty clin_narrative.narrative in supplied soap entry [%s]' % 
                soap_entry)
            return False
        return True
                
    #-----------------------------------------------------------
    def _verify_data(self, soap_entry):
        """
        Perform additional data check of a supplied SOAP entry
        
        @param soap_entry: dictionary containing information related to one
                           SOAP input
        @type soap_entry: dictionary with keys 'soap', 'types', 'text', 'data'
        """
                
        # FIXME pending
        pass
    
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
        bundle = [{'soap':'s', 'types':['Hx'], 'text':'Test narrarive', 'data':''}]
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
    