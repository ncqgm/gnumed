"""
data objects for organization. Hoping to use the helper class to act as Facade
for aggregated data objects ? with validation rules. 
re-used working code form gmClinItem and followed Script Module layout of gmEMRStructItems.

license: GPL"""
#============================================================
__version__ = "$Revision: 1.5 $"

if __name__ == "__main__":
	print
	print "*" * 50 
	print "RUNNING UNIT TEST of gmOrganization "
	print "In the connection query, please enter"
	print "a WRITE-ENABLED user e.g. _test-doc (not test-doc), and the right password"

from Gnumed.pycommon import gmExceptions, gmLog, gmPG, gmI18N, gmBorg
from Gnumed.pycommon.gmPyCompat import *
from Gnumed.business import gmClinItem
from Gnumed.business import gmDemographicRecord

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)


_cmd_template_fetch_payload = "select * from %s where id=%%s"


class cOrgCategory(gmClinItem.cClinItem):
	_cmd_fetch_payload = _cmd_template_fetch_payload % "org_category"
	_cmds_store_payload = [
		"""select 1 from org_category where id = %(id)s for update""",
		"""update org_category set description=%(description)s where id=%(id)s"""
	]
	_updatable_fields= ["description"]


class  cOrganization(gmClinItem.cClinItem):
	SERVICE='personalia'
	def update(self, map):
		for (k,v) in map.items:
			self.__setitem__(k,v)
			
	_cmd_fetch_payload = _cmd_template_fetch_payload % "org"
	_cmds_store_payload = [
		"""select 1 from org where id = %(id)s for update""",
		"""update org set id_category=(%id_category)s , description =(%description)s where id=%(id)s"""
		 
	]
	_updatable_fields= ["id_category", "description"]


class cCommTypes(gmClinItem.cClinItem):
	_cmd_fetch_payload = _cmd_template_fetch_payload % "enum_comm_types"
	_cmds_store_payload=[
		"""select 1 from enum_comm_types where id = %(id)s for update""",
		"""update enum_comm_types set description= %(description)s where id=%(id)s"""
	]
	_updatable_fields=["description"]


# FIXME: I am not sure this needs to be a full-blown clin item class
class cCommChannel(gmClinItem.cClinItem):
	_cmd_fetch_payload = _cmd_template_fetch_payload % "comm_channel"
	_cmds_store_payload = [
		"""select 1 from comm_channel where id = %(id)s for update""",
		"""update comm_channel set id_type= %(id_type)s, set url=%(url)s where id=%(id)s"""
	]
	_updatable_fields = ["id_type", "url"]


class cLnkPersonOrgAddress(gmClinItem.cClinItem):
	_cmd_fetch_payload = _cmd_template_fetch_payload % "lnk_person_org_address"
	_cmds_store_payload=[
		"""select 1 lnk_person_org_address from where id = %(id)s for update""",
		"""update lnk_person_org_address set
			id_identity = %(id_identity)s,
			id_address = %(id_address)s,
			id_type = %(id_type)s,
			id_org =%(id_org)s ,
			id_occupation  =  %(id_occupation)s,
			address_source = %(address_source)s 
			where id=%(id)s"""
	]
	_updatable_fields=["id_identity", "id_address" , "id_type", 
		"id_org" ,"id_occupation", "address_source"]

	# FIXME: this doesn't belong here
	def findByOrgId(id):
		print tmp
#		cmds = """select id from lnk_person_org_address 
#			where id_org = %s and id_identity = NULL
#			"""


class cCatFinder(gmBorg.cBorg):

	def __init__(self, categoryType = None):
		gmBorg.cBorg.__init__(self)
		if not self.__dict__.has_key("categories"):
			self.categories = {}
		
		if categoryType == None:
			return
		
		if not self.categories.has_key(categoryType):
			self.categories[categoryType] = {'toId': {}, 'toDescription': {} }
			self.reload(categoryType)
		
		

	def reload(self, categoryType):
		result = gmPG.run_ro_query("personalia","select id, description from %s" % categoryType)
		if result is None:
			gmLog.gmDefLog(gmLog.lErr, "failed to load %s" % categoryType)
		
		for (id, description) in result:
			self.categories[categoryType]['toId'][description] = id
			self.categories[categoryType]['toDescription'][id] = description

		
	def getId(self, categoryType, category):
		return self.categories.get(categoryType, {}).get('toId',{}).get(category, None)

	def getCategory(self, categoryType, id):
		return self.categories.get(categoryType, {}).get('toDescription',{}).get(id, "")

	def getCategories(self, categoryType):
		return self.categories.get(categoryType,{}).get('toId',{}).keys()
	
cCatFinder('org_category')
cCatFinder('enum_comm_types')


class cOrgHelper:
	def __init__(self):
		pass

	def getPk(self):
		pass

	def set(self, name, office, department, address, memo, category, phone, fax, email,mobile):
		pass

	def get_name_office_department_address_memo_category_phone_fax_email_mobile(self): 
		return []

	def findAllOrganizations():
		return []

	def findAllOrganizationPKAndName():
		return [ (0,"") ]

	def load(self, pk):
		return

	def save(self):
		return


class cOrgHelperImpl1(cOrgHelper):
	 
	attrNames = [ 'name', 'office', 'department', 'memo','category', 'phone', 'fax', 'email', 'mobile' ]
	addressNames = [ 'number', 'street', 'urb', 'postcode', 'state', 'country']
		
	commtypes = { 
		"email":gmDemographicRecord.EMAIL, 
		"fax":gmDemographicRecord.FAX, 
		#gmDemographicRecord.HOME_PHONE, 
		"phone":gmDemographicRecord.WORK_PHONE,
		"web":gmDemographicRecord.WEB, 
		"mobile":gmDemographicRecord.MOBILE,
		"jabber":gmDemographicRecord.JABBER 
		}
	
	commnames = dict( [ (v,k) for (k,v) in commtypes.items()] )

	def __init__(self):
		self._map = {}
		self._changed= {}
		self.pk = None
		self._addressModified(False)
		self._address = {}
		pass

	def getPk(self):
		return self.pk

	def setPk(self, pk):
		self.pk = pk

	def getAddressDict(self):
		d = {}
		d.update(self._address)
		return d
	
	def setAddress(self, number, street, urb, postcode, state, country):
		self._setAddressImpl( number, street, urb, postcode, state, country)
	
	def _setAddressImpl( self, *kwrd, **kargs):	
		names = self.__class__.addressNames
		if kargs == {} and kwrd <> []:
			kargs = dict( [ (a, v) for a,v in zip( names, kwrd) ] )


		for k in names:
			a = self._address
			if  a.get(k, None) <> kargs.get(k, None):
				self._addressModified(True)
				a[k] = kargs[k]	
	
	def _addressModified(self, val = None):
		if val <> None:
			self._amodified = val
		return self._amodified
	
	def set(self, name, office, department,  memo, category, phone, fax, email,mobile):
		self._set_impl(name, office, department,  memo, category, phone, fax, email,mobile)
		
		
	def _set_impl(self, *kwrd, **kargs):
		n = self.__class__.attrNames		
		if kargs == {} and kwrd <> []:
			kargs = dict( [ (a, v) for a,v in zip( n, kwrd) ] )
				
		changed = {} 
		for k in n: 
			v = self._map.get(k, None)
			
			if v != kargs[k]:
				changed[k] = kargs[k]
		
		self._changed = changed
	
	def __setitem__(self, k, v):
		if k in self.__class__.attrNames and self._map.get(k, None) <> v:
			self._changed[k] = v
	
	def __getitem__(self, k):
		v = self._changed.get(k, None)
		if v == None:
			v = self._map.get(k, None)
	
		return v
	
	
	def _save_comm_channels(self):
		if self.getId() is None:
			gmLog.gmDefLog.log(gmLog.lInfo, "Unable to save comm channel %s : %s due to no org id" % (k,v) )
			return False
	
		comm_changes = {}
		for k,id_type in self.__class__.commtypes. items():
			if self._changed.has_key(k):
				comm_changes[id_type] = self._changed[k]
		
		urls = comm_changes.values()
		
		places = ['%s'] *len(urls)
		
		format = ', '.join(places)
		
		cmd = [
		("""select id, url, id_type from comm_channel where url in( %s )""" % format, urls) ]
		result = gmPG.run_commit('personalia', cmd)
		if result is None:
			gmLog.gmDefLog.Log(gmLog.lInfo, "find existing org comms failed" )
			return False
		
		
		existing_urls = dict( [ (url,(id, id_type) ) for (id, url, id_type) in result] )
		for id_type , url in comm_changes.items():
			if url in existing_urls.keys() and existing_urls[url][1] <> id_type:
				gmLog.gmDefLog.Log(gmLog.lWarn, "Existing comm url mismatches type for org url %s, inserting same url different type!" % url)
				del existing_urls[url]
		cmds = []

		delete_link_cmd = """delete from lnk_org2comm_channel
				where id_comm in ( 
					select l2.id_comm from 
					lnk_org2comm_channel l2 , comm_channel c 
					where 	     c.id = l2.id_comm 
						and  c.id_type = %d
						and  l2.id_org = %d
					) """
					
		for url in existing_urls.keys():
			(id_comm, id_type) = existing_urls[url]
			cmds = [  (delete_link_cmd % (id_type, self.getPk()) ,[] ), 
				("""insert into lnk_org2comm_channel( id_comm, id_org)
				values ( %d, %d ) """ % ( id_comm, self.getPk() ) , [] )
				]
		
		for id_type, url in comm_changes.items():
			if url in existing_urls.keys():
				continue

			if url.strip() == "":
				cmds.append(
					(delete_link_cmd %(id_type, self.getPk()) , [] )
						)
			else:
					
				cmds.append( 
					("""insert into comm_channel( url, id_type)
					values( '%s', %d)""" % (url, id_type),[] )
					)
				cmds.append(
					("""insert into lnk_org2comm_channel(id_comm, id_org)
					values( currval('comm_channel_id_seq'), %d)""" %
					 self.getPk()  ,[] )  )
		
				
		result = gmPG.run_commit('personalia',cmds)
	
	def _save_address(self):
		a = self._address
		
		if not self._addressModified():
			return True
		
		return self.linkNewAddress(a['number'],a['street'], a['urb'], a['postcode'], a.get('state', None), a.get('country', None)  )
		


	def linkNewAddress (self,  number, street, urb, postcode, state = None, country = None):
		"""Adds a new address into this org list of addresses. Basically cut and
		paste and delete unnecessary fields from gmDemographics function.
		"""
		urb = urb.upper()
		if state == "": state = None
		if country == "": country = None
		
		
		
		if state is None:
			print "urb, postcode", urb, postcode
			state, country = gmDemographicRecord.guess_state_country(urb, postcode)
			print "state, country",  state, country
		# address already in database ?
		cmd = """
			select addr_id from v_basic_address
			where
				number = %s and
				street = %s and
				city = %s and
				postcode = %s and
				state = %s and
				country = %s
			"""
		data = gmPG.run_ro_query ('personalia', cmd, None, number, street, urb, postcode, state, country)
		if data is None:
			s = " ".join( (  number, street, urb, postcode, state, country ) )
			_log.Log(gmLog.lErr, 'cannot check for address existence (%s)' % s)
			return None

		# delete any pre-existing link for this org 
		cmd = """
			delete from lnk_person_org_address
			where
				id_org = %s 
			"""
		gmPG.run_commit ('personalia', [(cmd, [self.getPk()])])

		# yes, address already there, just add the link
		if len(data) > 0:
			addr_id = data[0][0]
			cmd = """
				insert into lnk_person_org_address (id_org, id_address)
				values (%d, %d)
				""" % (self.getPk(), addr_id)
			return gmPG.run_commit ("personalia", [ ( cmd,[]) ])

		# no, insert new address and link it, too
		cmd1 = """
			insert into v_basic_address (number, street, city, postcode, state, country)
			values (%s, %s, %s, %s, %s, %s)
			"""
		cmd2 = """
			insert into lnk_person_org_address (id_org, id_address)
			values (%d, currval('address_id_seq'))
			""" % self.getPk()
		return gmPG.run_commit ("personalia", [
			(cmd1, (number, street, urb, postcode, state, country)),
			(cmd2, [] )
			]
		)

		

	def get(self): 
		m = {}
		m.update(self._map)
		m.update(self._changed)
		return m 

	def get_address(self):
		return self._address

	def findAllOrganizations():
		return []

	def findAllOrganizationPKAndName():
		return [ (0,"") ]

	def load(self, pk):
		return ( self._load_org(pk) and 
			self._load_comm_channels() 
			and self._load_address() )
		
		

		
	def _load_org(self, pk):	
		cmd = "select description, id_category  from org where id = %d" % pk
		#<DEBUG>
		print cmd
		#</DEBUG>
		result = gmPG.run_ro_query("personalia", cmd, )
		if result is None:
			gmLog.gmDefLog.Log(gmLog.lInfo, "Unable to load org %s" %pk )
			return False
		if len(result) == 0:
			#<DEBUG>
			print "org id = ", pk, " not found"
			#</DEBUG>
			return False
		(description, id_category) = result[0]
		m=self._map
		cf = cCatFinder()
		m['category']=cf.getCategory("org_category",id_category)
		m['name']=description
		self.setPk(pk)

		return True
	
	
	def _load_comm_channels(self):
		cmd = """select id_type, url from comm_channel c, lnk_org2comm_channel l where l.id_org = %d and c.id = l.id_comm""" % self.getPk() 
		result = gmPG.run_ro_query("personalia", cmd)
		if result == None:
			gmLog.gmDefLog.Log(gmLog.lInfo, "Unable to load comm channels for org" )
			return False

		n = self.__class__.commnames
		for (id_type, url) in result:	
			if n.has_key(int(id_type)):
				self._map[n[id_type]] = url
				
		return True
	
	def _load_address(self):
		pk = self.getPk()
		cmd = """select number, street, city, postcode, state, country from v_basic_address v , lnk_org2address l where v.addr_id = l.id_address and l.id_org = %d""" % pk
		result = gmPG.run_ro_query( "personalia", cmd)
		if result == None:
			gmLog.gmDefLog.Log(gmLog.lInfo, "failure in org address load" )
			return False
		if len(result ) == 0:
			gmLog.gmDefLog.Log(gmLog.lInfo, "No address for org" )
			return True
		
		r = result[0]
		self._address = { 'number':r[0], 'street':r[1], 'urb':r[2], 'postcode':r[3], 'state':r[4], 'country': r[5]  }
	
		self._addressModified(False)

		return True
	
	
	def shallow_del(self):
		cmds = [
		 ("delete from lnk_person_org_address where id_org = %d"%self.getPk() , [] ),
		 ("delete from lnk_org2comm_channel where id_org = %d"%self.getPk(),[] ),
		 ("delete from org where id = %d"%self.getPk() , [] )
		]

		if (gmPG.run_commit('personalia',cmds) == None):
				gmLog.gmDefLog.Log(gmLog.lErr, "failed to remove org")
				return False

		self.setPk(None)

		return True

			
	
	
	def _create(self):
		#<DEBUG>
		#print "in _create"
		#</DEBUG>
		cmd = ("""insert into org (description, id_category) values('xxxDefaultxxx', 1)""", [])
		cmd2 = ("""select currval('org_id_seq')""", [])
		result = gmPG.run_commit('personalia', [cmd, cmd2])
		if result is None:
			cmd = ("""select id from org where description ='xxxDefaultxxx'""",[])
			result = gmPG.run_commit('personalia', [cmd] )
			if result <> None and len(result) == 1:
				self.setPk(result[0][0])
				#<DEBUG>
				#print "select id from org ->", self.getPk()
				#</DEBUG>
				return True
			return False
		self.setPk(result[0][0])
		#<DEBUG>
		#print "from select currval -> ", self.getPk()
		#</DEBUG>
		return True
	
	def save(self):
		m={}
		c = self._changed
		m.update(self._map)
		m.update(self._map)
		m.update(c)
		if not m.has_key('name') or m['name'].strip() =='':
			print "PLEASE ENTER ORG NAME" #change this
			return False
		print "self.Pk() = ", self.getPk() , " is None : ", self.getPk() is None
		if self.getPk() is None:
			if not self._create():
				gmLog.gmDefLog.Log(gmLog.lErr, "Cannot create org")
				return False
		if self.getPk() is None:
				return False
		if c.has_key('name') or c.has_key('category'):	
			
			#print "pk = ", self.getPk()
			#org = cOrganization(str(self.getPk()))
			cf = cCatFinder()
			cmd = """
				update org set description='%s' , 
						id_category = %s where id = %s
			 	""" % ( c['name'], 
					str( cf.getId('org_category', c['category']) ),
					str(self.getPk())  ) 
			result = gmPG.run_commit( "personalia", [ (cmd,[]  ) ] )
			if result is None:
				gmLog.gmDefLog.Log(gmLog.lErr, "Cannot save org")
				return False
			
		self._save_address()
		self._save_comm_channels()
		return True

#============================================================

def testOrg():

	print """testing single level orgs"""
	f = [ "name", "office", "department",  "memo", "category", "phone", "fax", "email","mobile"]
	a = ["number", "street", "urb", "postcode", "state", "country"]
	
	f1 = ["Box Hill Hospital", "", "", "eastern", "hospital", "0398953333", "111-1111","bhh@oz", ""]
	a1 = ["33", "Nelson Rd", "Box Hill", "3128", None , None]

	h = cOrgHelperImpl1()

	h.set(*f1)
	h.setAddress(*a1)

	print "testing get, getAddress"
	print h.get()
	print h.getAddressDict()
	
	import sys
	if not	h.save():
		print "failed to save first time. Is an old test org needing manual removal?"
		return False, h
	print "saved pk =", h.getPk()

	
	pk = h.getPk()
	if h.shallow_del():
		print "shallow deleted ", h['name']
	else:
		print "failed shallow delete of ", h['name']

	
	
	h2 = cOrgHelperImpl1()
	
	print "testing load"
	
	print "should fail"
	if not h2.load(pk):
		print "Failed as expected"
	
	if h.save():
		print "saved ", h['name'] , "again"
	else:
		print "failed re-save"
		return False, h
	
	h['fax'] = '222-1111'
	print "using update save"
	
	if h.save():
		print "saved updated passed"
		print "Test reload next"
	else:
		print "failed save of updated data"
		print "continuing to reload"
		
	
	if not h2.load(h.getPk()):
		print "failed load"
		return False, h
	print "reloaded values"
	print h2.get()
	print h2.getAddressDict()

	print "** End of Test org"
	
	if h2.shallow_del():
		print "cleaned up"
	else:
		print "Test org needs to be manually removed"

	return True, h2


if __name__== "__main__":
	_log.SetAllLogLevels(gmLog.lData)



	for n in xrange(1,8):
		print "Test Fetch of CommType , id=",n
		commType = cCommTypes(aPK_obj=n)
		print commType
		fields = commType.get_fields()
		for f in fields:
			print f,":", commType[f]
		print "updateable : ", commType.get_updatable_fields()
		print "-"*50

	print "TESTING cCatFinder"

	print """c = cCatFinder("org_category")"""
	c = cCatFinder("org_category")

	print c.getCategories("org_category")

	print """c = cCatFinder("enum_comm_types")"""
	c = cCatFinder("enum_comm_types")

	l = c.getCategories("enum_comm_types")
	print "testing getId()"
	l2 = []
	for x in l:
		l2.append((x, c.getId("enum_comm_types", x)))
	print l2

	
				
	

	print """testing borg behaviour of cCatFinder"""

	print c.getCategories("org_category")
	
	result, org = testOrg()

	if not result:
		print "trying cleanup"
		if org.shallow_del(): print " 	may have succeeded"
	
	
			
	
	
#============================================================
# $Log: gmOrganization.py,v $
# Revision 1.5  2004-05-22 10:31:29  ncq
# - == None -> is None
#
# Revision 1.4  2004/05/21 15:39:22  sjtan
#
# passed unit test for save, load, shallow_del, save again, update and save.
#
# Revision 1.3  2004/05/20 15:37:12  sjtan
#
# pre-test version of gmOrganization connecting to current org tables. Needs
# unit testing, and then handling of subOrgs and organizational people
# linking. Some cut and paste of linkAddress from gmDemographicRecord. Not
# for use .
#
# Revision 1.2  2004/05/16 13:05:14  ncq
# - remove methods that violate the basic rules for
#   clinical items (eg no creation via clin item objects)
# - cleanup
#
