"""GnuMed demographics object.

This is a patient object intended to let a useful client-side
API crystallize from actual use in true XP fashion.

license: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmDemographicRecord.py,v $
# $Id: gmDemographicRecord.py,v 1.76 2005-10-09 08:11:48 ihaywood Exp $
__version__ = "$Revision: 1.76 $"
__author__ = "K.Hilbert <Karsten.Hilbert@gmx.net>, I.Haywood <ihaywood@gnu.org>"

# access our modules
import sys, os.path, time, string

from Gnumed.pycommon import gmLog, gmExceptions, gmPG, gmSignals, gmDispatcher, gmMatchProvider, gmI18N, gmBusinessDBObject
from Gnumed.business import gmMedDoc
from Gnumed.pycommon.gmPyCompat import *

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

# 3rd party
import mx.DateTime as mxDT


#============================================================
# map gender abbreviations in a GnuMed demographic service
# to a meaningful localised string
#demographics_GENDER_DICT = {
#			'm' : _('Male'),
#			'f' : _('Female'),
#			'?' : _('Unknown'),
#			'tm' : _('Transexual to Male'),
#			'tf' : _('Transexual to Female'),
#			'h' : _('Hermaphrodite')
#		}
#===================================================================
#class cComm (gmBusinessDBObject.cBusinessDBObject):
	
#===================================================================

#class cAddress (gmBusinessDBObject.cBusinessObject):
	# to be honest, I'm not really convinced it means much sense to be able to
	# change addresses and comms. When someone 'changes' their address, really they are unbinding
	# from the old address and binding to a new one,
	# so I'm going back to having addresses and comms as plain dictionaries
	
#===================================================================
class cOrg (gmBusinessDBObject.cBusinessDBObject):
	"""
	Organisations

	This is also the common ancestor of cIdentity, self._table is used to
	hide the difference.
	The aim is to be able to sanely write code which doesn't care whether
	its talking to an organisation or an individual"""
	_table = "org"

	_cmd_fetch_payload = "select *, xmin from org where id=%s"
	_cmds_lock_rows_for_update = ["select 1 from org where id=%(id)s and xmin=%(xmin)s"]
	_cmds_store_payload = ["update org set description=%(description)s, id_category=(select id from org_category where description=%(occupation)s) where id=%(id)s", "select xmin from org whereid=%(id)s"]
	_updatable_fields = ["description", "occupation"]
	_service = 'personalia'
		      
		
	#------------------------------------------------------------------
	def cleanup (self):
		pass
	#------------------------------------------------------------------
	def export_demographics (self):
		if not self.__cache.has_key ('addresses'):
			self['addresses']
		if not self.__cache.has_key ('comms'):
			self['comms']
		return self.__cache
	#--------------------------------------------------------------------
	def get_members (self):
		"""
		Returns a list of (address dict, cIdentity) tuples 
		"""
		cmd = """select
				vba.id,
				vba.number,
				vba.addendum, 
				vba.street,
				vba.urb,
				vba.postcode,
				at.name,
				lpoa.id_type,
				vbp.pk_identity,
				title,
				firstnames,
				lastnames,
				dob,
				cob,
				gender,
				pupic,
				pk_marital_status,
				marital_status,
				karyotype,
				xmin_identity,
				preferred
			from
				v_basic_address vba,
				lnk_person_org_address lpoa,
				address_type at,
				v_basic_person vbp
			where
				lpoa.id_address = vba.id
				and lpoa.id_type = at.id
				and lpoa.id_identity = vbp.pk_identity
				and lpoa.id_org = %%s
				"""

		rows, idx = gmPG.run_ro_query('personalia', cmd, 1, self.getId ())
		if rows is None:
			return []
		elif len(rows) == 0:
			return []
		else:
			return [({'pk':i[0], 'number':i[1], 'addendum':i[2], 'street':i[3], 'city':i[4], 'postcode':i[5], 'type':i[6], 'id_type':i[7]}, cIdentity (row = {'data':i[8:], 'id':idx[8:], 'pk_field':'id'})) for i in rows]	
	#------------------------------------------------------------
	def set_member (self, person, address):
		"""
		Binds a person to this organisation at this address.
		person is a cIdentity object
		address is a dict of {'number', 'street', 'addendum', 'city', 'postcode', 'type'}
		type is one of the IDs returned by getAddressTypes
		"""
		cmd = "insert into lnk_person_org_address (id_type, id_address, id_org, id_identity) values (%(type)s, create_address (%(number)s, %(addendum)s, %(street)s, %(city)s, %(postcode)s), %(org_id)s, %(pk_identity)s)"
		address['pk_identity'] = person['pk_identity']
		address['org_id'] = self.getId()
		if not id_addr:
			return (False, None)
		return gmPG.run_commit2 ('personalia', [(cmd, [address])])
	#------------------------------------------------------------
	def unlink_person (self, person):
		cmd = "delete from lnk_person_org_address where id_org = %s and id_identity = %s"
		return gmPG.run_commit2 ('personalia', [(cmd, [self.getId(), person['id']])])
	#----------------------------------------------------------------------
	def getId (self):
		"""
		Hide the difference between org.id and v_basic_person.pk_identity
		"""
		return self['id']
#==============================================================================
def get_time_tuple (mx):
	"""
	wrap mx.DateTime brokenness
	Returns 9-tuple for use with pyhon time functions
	"""
	return [ int(x) for x in  str(mx).split(' ')[0].split('-') ] + [0,0,0, 0,0,0]
#----------------------------------------------------------------
def getAddressTypes():
	"""Gets a dict matching address types to thier ID"""
	row_list = gmPG.run_ro_query('personalia', "select name, id from address_type")
	if row_list is None:
		return {}
	if len(row_list) == 0:
		return {}
	return dict (row_list)
#----------------------------------------------------------------
def getMaritalStatusTypes():
	"""Gets a dictionary matching marital status types to their internal ID"""
	row_list = gmPG.run_ro_query('personalia', "select name, pk from marital_status")
	if row_list is None:
		return {}
	if len(row_list) == 0:
		return {}
	return dict(row_list)
#------------------------------------------------------------------
def getExtIDTypes (context = 'p'):
	"""Gets dictionary mapping ext ID names to internal code from the backend for the given context
	"""
	# FIXME: error handling
	rl = gmPG.run_ro_query('personalia', "select name, pk from enum_ext_id_types where context = %s", None, context)
	if rl is None:
		return {}
	return dict (rl)
#----------------------------------------------------------------
def getCommChannelTypes():
	"""Gets the dictionary of comm channel types to internal ID"""
	row_list = gmPG.run_ro_query('personalia', "select description, id from enum_comm_types")
	if row_list is None:
		return None
	if len (row_list) == 0:
		return None
	return dict(row_list)
#----------------------------------------------------------------
def getRelationshipTypes():
	"""Gets a dictionary of relationship types to internal id"""
	row_list = gmPG.run_ro_query('personalia', "select description, id from relation_types")
	if row_list is None:
		return None
	if len (row_list) == 0:
		return None
	return dict(row_list)

#----------------------------------------------------------------
def getUrb (id_urb):
	row_list = gmPG.run_ro_query('personalia', "select state.name, urb.postcode from urb,state where urb.id = %s and urb.id_state = state.id", None, id_urb)
	if not row_list:
		return None
	else:
		return (row_list[0][0], row_list[0][1])

def getStreet (id_street):
	row_list = gmPG.run_ro_query('personalia', "select state.name, coalesce (street.postcode, urb.postcode), urb.name from urb,state,street where street.id = %s and street.id_urb = urb.id and urb.id_state = state.id", None, id_street)
	if not row_list:
		return None
	else:
		return (row_list[0][0], row_list[0][1], row_list[0][2])

def getCountry (country_code):
	row_list = gmPG.run_ro_query('personalia', "select name from country where code = %s", None, country_code)
	if not row_list:
		return None
	else:
		return row_list[0][0]
#-------------------------------------------------------------------------------
def get_town_data (town):
	row_list = gmPG.run_ro_query ('personalia', "select urb.postcode, state.code, state.name, country.code, country.name from urb, state, country where urb.name = %s and urb.id_state = state.id and state.country = country.code", None, town)
	if not row_list:
		return (None, None, None, None, None)
	else:
		return tuple (row_list[0])
#-------------------------------------------------------------------------------
class PostcodeMP (gmMatchProvider.cMatchProvider_SQL):
	"""Returns a list of valid postcodes,
	Accepts two contexts : "urb" and "street" being the **IDs** of urb and street
	"""
	def __init__ (self):
		# we search two tables here, as in some jurisdictions (UK, Germany, US)
		# postcodes are tied to streets or small groups of streets,
		# and in others (Australia) postcodes refer to an entire town

		# reviewers' comments:
		# - pk this will be the data return to the id_callback() function passed 
		#   as  gmPhrasewheel.__init__ last parameter , so the event data  will be 
		#   the postcode for urb or street , not the id of those tables.
		#   This is in the cMatchProvider.__findMatches code.

		source = [{
			'column':'postcode',
			'pk':'postcode',
			'limit':10,
			'table':'urb',
			'extra conditions':{'urb':'id = %s', 'default':'postcode is not null'}
			, 'service': 'personalia'
			},{
			'column':'postcode',
			'table':'street',
			'limit':10,
			'pk':'postcode',
			'extra conditions':{'urb':'id_urb = %s', 'street': 'id = %s', 'default':'postcode is not null'}
			, 'service': 'personalia'
			}]
		gmMatchProvider.cMatchProvider_SQL.__init__(self, source)
			
#----------------------------------------------------------------
class StreetMP (gmMatchProvider.cMatchProvider_SQL):
	"""Returns a list of streets

	accepts "urb" and "postcode" contexts  
		e.g.
			using cMatchProvider_SQL's  self.set_context("urb",...) 
					
	"""
	def __init__ (self):
		source = [{
			'service': 'personlia',
			'table': 'street',
			'pk':'id',
			'column': 'name',
			'limit': 10,
			'extra conditions': {
				'urb': 'id_urb = %s',
				'postcode': 'postcode = %s or postcode is null'
				}
			}]
		gmMatchProvider.cMatchProvider_SQL.__init__(self, source)
#------------------------------------------------------------

class StateMP (gmMatchProvider.cMatchProvider_SQL):
					
	"""
	"""
	def __init__ (self):
		source = [{
			'service': 'personlia',
			'table': 'state',
			'pk':'id',
			'column': 'name',
			'limit': 10,
			'extra conditions': {}
			}]
		gmMatchProvider.cMatchProvider_SQL.__init__(self, source)
#-----------------------------------------------------------
class MP_urb_by_zip (gmMatchProvider.cMatchProvider_SQL):
	"""Returns a list of urbs

	accepts "postcode" and "state" contexts
	"""
	def __init__ (self):
		source = [{
			'service': 'personalia',
			'table': 'urb',
			'pk':'id',
			'column': 'name',
			'limit': 15,
			'extra conditions': {'postcode': '(postcode = %s or postcode is null)',
					     'state':'(id_state = %s)'}
			}]
		gmMatchProvider.cMatchProvider_SQL.__init__(self, source)

class CountryMP (gmMatchProvider.cMatchProvider_SQL):
	"""
	Returns a list of countries
	"""
	def __init__ (self):
		source = [{
			'service':'personalia',
			'table':'country',
			'pk':'code',
			'column':'name',
			'limit':5
			}]
		gmMatchProvider.cMatchProvider_SQL.__init__ (self, source)

class OccupationMP (gmMatchProvider.cMatchProvider_SQL):
	"""
	Returns a list of occupations
	"""
	def __init__ (self):
		source = [{
			'service':'personalia',
			'table':'occupation',
			'pk':'id',
			'column':'name',
			'limit':7
			}]
		gmMatchProvider.cMatchProvider_SQL.__init__ (self, source)

class NameMP (gmMatchProvider.cMatchProvider):
	"""
	List of names
	"""
	def getMatches (self, fragment):
		cmd = "select search_identity (%s)"
		data, idx = gmPG.run_ro_query ('personalia', cmd, 1, fragment)
		if data is None:
			_log.Log(gmLog.lErr, "cannot search for identity")
			return None
		return [{'data':cIdentity (idx, i), 'label':"%s %s %s" % (i[idx['title']], i[idx['firstnames']], i[idx['lastnames']])} for i in data]

#------------------------------------------------------------
class OrgCategoryMP (gmMatchProvider.cMatchProvider_SQL):
	"""
	List of org categories.
	"""
	def __init__(self):
		source = [ {
			'service': 'personalia',
			'table'	: 'org_category',
			'pk'	: 'id',
			'column': 'description',
			'result': 'description' ,
			'limit' : 5,
			}]
		gmMatchProvider.cMatchProvider_SQL.__init__(self, source)
#------------------------------------------------------------

#============================================================
# callbacks
#------------------------------------------------------------
def _patient_selected(**kwargs):
	print "received patient_selected notification"
	print kwargs['kwds']
#============================================================
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)
	gmDispatcher.connect(_patient_selected, gmSignals.patient_selected())
	while 1:
		pID = raw_input('a patient: ')
		if pID == '':
			break
		try:
			print pID
			myPatient = gmPerson.cIdentity (aPK_obj = pID)
		except:
			_log.LogException('Unable to set up patient with ID [%s]' % pID, sys.exc_info())
			print "patient", pID, "can not be set up"
			continue
		print "ID       ", myPatient['id']
		print "name     ", myPatient['description']
		print "title    ", myPatient['title']
		print "dob      ", myPatient['dob']
		print "med age  ", myPatient['medical_age']
		for adr in myPatient['addresses']:
			print "address  ", adr	
		print "--------------------------------------"
#============================================================
# $Log: gmDemographicRecord.py,v $
# Revision 1.76  2005-10-09 08:11:48  ihaywood
# introducing get_town_data (), a convience method to get info that can be inferred from a town's name (in AU)
#
# Revision 1.75  2005/10/09 02:19:40  ihaywood
# the address widget now has the appropriate widget order and behaviour for australia
# when os.environ["LANG"] == 'en_AU' (is their a more graceful way of doing this?)
#
# Remember our postcodes work very differently.
#
# Revision 1.74  2005/06/07 10:15:47  ncq
# - setContext -> set_context
#
# Revision 1.73  2005/04/25 08:26:48  ncq
# - cleanup
#
# Revision 1.72  2005/04/14 19:14:51  cfmoro
# Gender dict was replaced by get_genders method
#
# Revision 1.71  2005/04/14 18:58:14  cfmoro
# Added create occupation method and minor gender map clean up, to replace later by get_gender_list
#
# Revision 1.70  2005/04/14 08:49:29  ncq
# - move cIdentity and dob2medical_age() to gmPerson.py
#
# Revision 1.69  2005/03/30 21:04:01  cfmoro
# id -> pk_identity
#
# Revision 1.68  2005/03/29 18:55:39  cfmoro
# Var name fix
#
# Revision 1.67  2005/03/20 16:47:26  ncq
# - cleanup
#
# Revision 1.66  2005/03/08 16:41:37  ncq
# - properly handle title
#
# Revision 1.65  2005/03/06 08:17:02  ihaywood
# forms: back to the old way, with support for LaTeX tables
#
# business objects now support generic linked tables, demographics
# uses them to the same functionality as before (loading, no saving)
# They may have no use outside of demographics, but saves much code already.
#
# Revision 1.64  2005/02/20 21:00:20  ihaywood
# getId () is back
#
# Revision 1.63  2005/02/20 09:46:08  ihaywood
# demographics module with load a patient with no exceptions
#
# Revision 1.61  2005/02/19 15:04:55  sjtan
#
# identity.id is now identity.pk_identity, so adapt
#
# Revision 1.60  2005/02/18 11:16:41  ihaywood
# new demographics UI code won't crash the whole client now ;-)
# still needs much work
# RichardSpace working
#
# Revision 1.59  2005/02/13 15:46:46  ncq
# - trying to keep up to date with schema changes but may conflict with Ian
#
# Revision 1.58  2005/02/12 14:00:21  ncq
# - identity.id -> pk
# - v_basic_person.i_id -> i_pk
# - likely missed some places here, though
#
# Revision 1.57  2005/02/03 20:17:18  ncq
# - get_demographic_record() -> get_identity()
#
# Revision 1.56  2005/02/01 10:16:07  ihaywood
# refactoring of gmDemographicRecord and follow-on changes as discussed.
#
# gmTopPanel moves to gmHorstSpace
# gmRichardSpace added -- example code at present, haven't even run it myself
# (waiting on some icon .pngs from Richard)
#
# Revision 1.55  2005/01/31 10:37:26  ncq
# - gmPatient.py -> gmPerson.py
#
# Revision 1.54  2004/08/18 09:05:07  ncq
# - just some cleanup, double-check _ is defined for epydoc
#
# Revision 1.53  2004/07/26 14:34:49  sjtan
#
# numbering correction from labels in gmDemograpics.
#
# Revision 1.52  2004/06/25 12:37:19  ncq
# - eventually fix the import gmI18N issue
#
# Revision 1.51  2004/06/21 16:02:08  ncq
# - cleanup, trying to make epydoc fix do the right thing
#
# Revision 1.50  2004/06/21 14:48:25  sjtan
#
# restored some methods that gmContacts depends on, after they were booted
# out from gmDemographicRecord with no home to go , works again ;
# removed cCatFinder('occupation') instantiating in main module scope
# which was a source of complaint , as it still will lazy load anyway.
#
# Revision 1.49  2004/06/20 15:38:00  ncq
# - remove import gettext/_ = gettext.gettext
# - import gmI18N handles that if __main__
# - else the importer of gmDemographicRecord has
#   to handle setting _
# - this is the Right Way as per the docs !
#
# Revision 1.48  2004/06/20 06:49:21  ihaywood
# changes required due to Epydoc's OCD
#
# Revision 1.47  2004/06/17 11:36:12  ihaywood
# Changes to the forms layer.
# Now forms can have arbitrary Python expressions embedded in @..@ markup.
# A proper forms HOWTO will appear in the wiki soon
#
# Revision 1.46  2004/05/30 03:50:41  sjtan
#
# gmContacts can create/update org, one level of sub-org, org persons, sub-org persons.
# pre-alpha or alpha ? Needs cache tune-up .
#
# Revision 1.45  2004/05/29 12:03:47  sjtan
#
# OrgCategoryMP for gmContact's category field
#
# Revision 1.44  2004/05/28 15:05:10  sjtan
#
# utility functions only called with exactly 2 args in order to fulfill function intent, but do some checking for invalid args.
#
# Revision 1.43  2004/05/26 12:58:14  ncq
# - cleanup, error handling
#
# Revision 1.42  2004/05/25 16:18:13  sjtan
#
# move methods for postcode -> urb interaction to gmDemographics so gmContacts can use it.
#
# Revision 1.41  2004/05/25 16:00:34  sjtan
#
# move common urb/postcode collaboration  to business class.
#
# Revision 1.40  2004/05/19 11:16:08  sjtan
#
# allow selecting the postcode for restricting the urb's picklist, and resetting
# the postcode for unrestricting the urb picklist.
#
# Revision 1.39  2004/04/15 09:46:56  ncq
# - cleanup, get_lab_data -> get_lab_results
#
# Revision 1.38  2004/04/11 10:15:56  ncq
# - load title in get_names() and use it superceding getFullName
#
# Revision 1.37  2004/04/10 01:48:31  ihaywood
# can generate referral letters, output to xdvi at present
#
# Revision 1.36  2004/04/07 18:43:47  ncq
# - more gender mappings
# - *comm_channel -> comm_chan
#
# Revision 1.35  2004/03/27 04:37:01  ihaywood
# lnk_person2address now lnk_person_org_address
# sundry bugfixes
#
# Revision 1.34  2004/03/25 11:01:45  ncq
# - getActiveName -> get_names(all=false)
# - export_demographics()
#
# Revision 1.33  2004/03/20 19:43:16  ncq
# - do import gmI18N, we need it
# - gm2long_gender_map -> map_gender_gm2long
# - gmDemo* -> cDemo*
#
# Revision 1.32  2004/03/20 17:53:15  ncq
# - cleanup
#
# Revision 1.31  2004/03/15 15:35:45  ncq
# - optimize getCommChannel() a bit
#
# Revision 1.30  2004/03/10 12:56:01  ihaywood
# fixed sudden loss of main.shadow
# more work on referrals,
#
# Revision 1.29  2004/03/10 00:09:51  ncq
# - cleanup imports
#
# Revision 1.28  2004/03/09 07:34:51  ihaywood
# reactivating plugins
#
# Revision 1.27  2004/03/04 10:41:21  ncq
# - comments, cleanup, adapt to minor schema changes
#
# Revision 1.26  2004/03/03 23:53:22  ihaywood
# GUI now supports external IDs,
# Demographics GUI now ALPHA (feature-complete w.r.t. version 1.0)
# but happy to consider cosmetic changes
#
# Revision 1.25  2004/03/03 05:24:01  ihaywood
# patient photograph support
#
# Revision 1.24  2004/03/02 10:21:09  ihaywood
# gmDemographics now supports comm channels, occupation,
# country of birth and martial status
#
# Revision 1.23  2004/02/26 17:19:59  ncq
# - setCommChannel: arg channel -> channel_type
# - setCommChannel: we need to read currval() within
#   the same transaction as the insert to get consistent
#   results
#
# Revision 1.22  2004/02/26 02:12:00  ihaywood
# comm channel methods
#
# Revision 1.21  2004/02/25 09:46:20  ncq
# - import from pycommon now, not python-common
#
# Revision 1.20  2004/02/18 15:26:39  ncq
# - fix dob2medical_age()
#
# Revision 1.19  2004/02/18 06:36:04  ihaywood
# bugfixes
#
# Revision 1.18  2004/02/17 10:30:14  ncq
# - enhance GetAddresses() to return all types if addr_type is None
#
# Revision 1.17  2004/02/17 04:04:34  ihaywood
# fixed patient creation refeential integrity error
#
# Revision 1.16  2004/02/14 00:37:10  ihaywood
# Bugfixes
# 	- weeks = days / 7
# 	- create_new_patient to maintain xlnk_identity in historica
#
# Revision 1.15  2003/12/01 01:01:41  ncq
# - get_medical_age -> dob2medical_age
#
# Revision 1.14  2003/11/30 01:06:21  ncq
# - add/remove_external_id()
#
# Revision 1.13  2003/11/23 23:32:01  ncq
# - some cleanup
# - setTitle now works on identity instead of names
#
# Revision 1.12  2003/11/23 14:02:40  sjtan
#
# by setting active=false first, then updating values, side effects from triggers can be avoided; see also
# F_active_name trigger function in server sql script,which fires only if new.active = true .
#
# Revision 1.11  2003/11/22 14:44:17  ncq
# - setTitle now only operates on active names and also doesn't set the name
#   to active which would trigger the trigger
#
# Revision 1.10  2003/11/22 14:40:59  ncq
# - setActiveName -> addName
#
# Revision 1.9  2003/11/22 12:53:48  sjtan
#
# modified the setActiveName and setTitle so it works as intended in the face of insurmountable triggers ;)
#
# Revision 1.8  2003/11/20 07:45:45  ncq
# - update names/identity, not v_basic_person in setTitle et al
#
# Revision 1.7  2003/11/20 02:10:50  sjtan
#
# remove 'self' parameter from functions moved into global module namespace.
#
# Revision 1.6  2003/11/20 01:52:03  ncq
# - actually, make that **?** for good measure
#
# Revision 1.5  2003/11/20 01:50:52  ncq
# - return '?' for missing names in getActiveName()
#
# Revision 1.4  2003/11/18 16:44:24  ncq
# - getAddress -> getAddresses
# - can't verify mxDateTime bug with missing time tuple
# - remove getBirthYear, do getDOB() -> mxDateTime -> format
# - get_relative_list -> get_relatives
# - create_dummy_relative -> link_new_relative
# - cleanup
#
# Revision 1.3  2003/11/17 10:56:34  sjtan
#
# synced and commiting.
#
# Revision 1.2  2003/11/04 10:35:22  ihaywood
# match providers in gmDemographicRecord
#
# Revision 1.1  2003/11/03 23:59:55  ncq
# - renamed to avoid namespace pollution with plugin widget
#
# Revision 1.6  2003/10/31 23:21:20  ncq
# - remove old history
#
# Revision 1.5  2003/10/27 15:52:41  ncq
# - if aFormat is None in getDOB() return datetime object, else return formatted string
#
# Revision 1.4  2003/10/26 17:35:04  ncq
# - conceptual cleanup
# - IMHO, patient searching and database stub creation is OUTSIDE
#   THE SCOPE OF gmPerson and gmDemographicRecord
#
# Revision 1.3  2003/10/26 16:35:03  ncq
# - clean up as discussed with Ian, merge conflict resolution
#
# Revision 1.2  2003/10/26 11:27:10  ihaywood
# gmPatient is now the "patient stub", all demographics stuff in gmDemographics.
#
# Ergregious breakages are fixed, but needs more work
#
# Revision 1.1  2003/10/25 08:48:06  ihaywood
# Split from gmTmpPatient
#



# old gmTmpPatient log
# Revision 1.41  2003/10/19 10:42:57  ihaywood
# extra functions
#
# Revision 1.40  2003/09/24 08:45:40  ihaywood
# NewAddress now functional
#
# Revision 1.39  2003/09/23 19:38:03  ncq
# - cleanup
# - moved GetAddressesType out of patient class - it's a generic function
#
