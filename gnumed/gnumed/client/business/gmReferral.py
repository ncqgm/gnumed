"""
Referrals business object

Will contain a VO for referral objects
"""


from Gnumed.business import gmClinicalRecord, gmDemographicRecord, gmForms, gmClinItem
from Gnumed.pycommon import gmExceptions, gmLog, gmWhoAmI, gmCfg


#def gmReferral (cClinItem):
#
#    def __init__ ()

def create_referral (patient, recipient, channel, addr, text, flags = {}):
    """
    If PK_obj is a number, this will instantiate a VO from the backend
    If it is None, the other parameters will be used to create a new referral object
    recipient -- demographic ID of the recipient
    text -- text of the referral
    patient -- the current patient
    addr -- the selected address/fax/email
    flags -- flags for extra info on the letter. Currently supported: meds, pasthx
    """
    if patient is None:
        raise gmExceptions.ConstructorError ('invalid arguments')
    whoami = gmWhoAmI.cWhoAmI ()
    sender = gmDemographicRecord.cDemographicRecord_SQL (whoami.get_staff_identity ())
    machine = whoami.get_workplace ()
    patient_demo = patient.get_demographic_record ()
    patient_clinical = patient.get_clinical_record ()
    params = {}
    sname = sender.get_names()
    params['SENDER'] = '%s %s %s' % (sname['title'], sname['first'], sname['last'])
    pname = patient_demo.get_names()
    params['PATIENTNAME'] = '%s %s %s' % (pname['title'], pname['first'], pname['last'])
    rname = recipient.get_names()
    params['RECIPIENT'] = '%s %s %s' % (rname['title'], rname['first'], rname['last'])
    params['DOB'] = patient_demo.getDOB ().Format ('%x')
    params['PATIENTADDRESS'] = _("%(number)s %(street)s, %(urb)s %(postcode)s") % patient_demo.getAddresses ('home', 1)
    params['TEXT'] = text
    params['INCLUDEMEDS'] = flags['meds']
    # FUTURE
    # params['MEDLIST'] = patient_epr.getMedicationsList ()
    params['INCLUDEPASTHX'] = flags['pasthx']
    #F FUTURE
    # params['PASTHXLIST'] = patient_epr.getPastHistory ()
    
    if channel == 'post':
        params['RECIPIENTADDRESS'] = _('%(number)s %(street)s\n%(urb)s %(postcode)s') % addr
        sndr_addr = sender.getAddresses ('work', 1)
        if sndr_addr:
            params['SENDERADDRESS'] = _('%(number)s %(street)s\n%(urb)s %(postcode)s') % sender.getAddresses('work', 1)
        else:
            params['SENDERADDRESS'] = _('No address')
        form_name, set1 = gmCfg.getFirstMatchingDBSet(machine = machine, option = 'main.comms.paper_referral')
        command, set1 = gmCfg.getFirstMatchingDBSet (machine = machine, option = 'main.comms.print')
    if channel == 'fax':
        params['RECIPIENTADDRESS'] = _('FAX: %s') % addr
        sender_addr = sender.getAddresses('work', 1)
        if sender_addr:
            sender_addr['fax'] = sender.getCommChannel (gmDemographicRecord.FAX)
            params['SENDERADDRESS'] = _('%(number)s %(street)s\n%(urb)s %(postcode)s\nFAX: %(fax)s' % sender_addr)
        else:
            params['SENDERADDRESS'] = _('No address')
        form_name, set1 = gmCfg.getFirstMatchingDBSet(machine = machine, option = 'main.comms.paper_referral')
        command, set1 = gmCfg.getFirstMatchingDBSet (machine = machine, option = 'main.comms.fax')
        command.replace ("%N", addr)   # substitute the %N for the number we need to fax to in the command
    if channel == 'email':
        params['RECIPIENTADDRESS'] = addr
        params['SENDERADDRESS'] = sender.getCommChannel (gmDemographicRecord.EMAIL)
        form_name, set1 = gmCfg.getFirstMatchingDBSet(machine = machine, option = 'main.comms.email_referral')
        command, set1 = gmCfg.getFirstMatchingDBSet (machine = machine, option = 'main.comms.email')
        command.replace ("%R", addr) # substitute recipients email address
        command.replace ("%S", params['SENDERADDRESS']) # substitute senders email address
    form = gmForms.get_form (form_name)
    form.process (params)
    if not form.exe (command):
        return False
    form.cleanup ()
    pool = gmPG.ConnectionPool ()
    conn = pool.GetConnection ('historica', readonly = 0)
    curs = conn.cursor ()
    form_id = form.store (patient_clinical.encounter['id'], patient_clinical.episode['id'], params, curs)
    if form_id:
        if patient_clinical.store_referral (curs, text, form_id):
            curs.close ()
            conn.commit ()
            conn.close ()
            return True
        else:
            conn.rollback ()
            conn.close ()
            return False
    else:
        conn.rollback ()
        conn.close ()
        return False

                
