"""
data objects for organization. Hoping to use the helper class to act as Facade
for aggregated data objects ? with validation rules. 
re-used working code form gmClinItem and followed Script Module layout of gmEMRStructItems.

license: GPL"""
#============================================================
__version__ = "$Revision: 1.8 $"

if __name__ == "__main__":
			
	print
	print "*" * 50 
	print "RUNNING UNIT TEST of gmOrganization "
	print "In the connection query, please enter"
	print "a WRITE-ENABLED user e.g. _test-doc (not test-doc), and the right password"
	print
	print "Run the unit test with cmdline argument '--clean'  if trying to clean out test data"
	print


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

	def getId(self):
		return None

	def setId(self, id): # ? change to non-public
		pass	
	
	def set(self, name, office, department, memo, category, phone, fax, email,mobile):
		pass

	def setAddress(self, number, street, urb, postcode, state, country):
		pass

	def getAddress(self):
		return []

	def __setitem__(self, k, v):
		pass

	def __getitem__(self, k):
		return None


	def get(self): 
		return []

	def findAllOrganizations():
		return []

	def findAllOrganizationPKAndName():
		return [ (0,"") ]

	def load(self, pk):
		return False

	def save(self):
		return False


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

	def getId(self):
		return self.pk

	def setId(self, pk):
		self.pk = pk

	def getAddress(self):
		return self.getAddressDict()

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
			cmds = [  (delete_link_cmd % (id_type, self.getId()) ,[] ), 
				("""insert into lnk_org2comm_channel( id_comm, id_org)
				values ( %d, %d ) """ % ( id_comm, self.getId() ) , [] )
				]
		
		for id_type, url in comm_changes.items():
			if url in existing_urls.keys():
				continue

			if url.strip() == "":
				cmds.append(
					(delete_link_cmd %(id_type, self.getId()) , [] )
						)
			else:
					
				cmds.append( 
					("""insert into comm_channel( url, id_type)
					values( '%s', %d)""" % (url, id_type),[] )
					)
				cmds.append(
					("""insert into lnk_org2comm_channel(id_comm, id_org)
					values( currval('comm_channel_id_seq'), %d)""" %
					 self.getId()  ,[] )  )
		
				
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
		gmPG.run_commit ('personalia', [(cmd, [self.getId()])])

		# yes, address already there, just add the link
		if len(data) > 0:
			addr_id = data[0][0]
			cmd = """
				insert into lnk_person_org_address (id_org, id_address)
				values (%d, %d)
				""" % (self.getId(), addr_id)
			return gmPG.run_commit ("personalia", [ ( cmd,[]) ])

		# no, insert new address and link it, too
		cmd1 = """
			insert into v_basic_address (number, street, city, postcode, state, country)
			values (%s, %s, %s, %s, %s, %s)
			"""
		cmd2 = """
			insert into lnk_person_org_address (id_org, id_address)
			values (%d, currval('address_id_seq'))
			""" % self.getId()
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


	def findAllOrganizations():
		pass
	

	def findAllOrganizationPKAndName():
		return [ (0,"") ]

	def load(self, pk):
		return ( self._load_org(pk) and 
			self._load_comm_channels() 
			and self._load_address() )
		
		

		
	def _load_org(self, pk):	
		m_org = get_org_data_for_org_ids( [pk] )	
		if m_org == None or not m_org.has_key(pk):
			#<DEBUG>
			print "org id = ", pk, " not found"
			#</DEBUG>
			return False
			
		(description, id_category) = m_org[pk]
		m=self._map
		cf = cCatFinder()
		m['category']=cf.getCategory("org_category",id_category)
		m['name']=description
		self.setId(pk)

		return True
	
	
	def _load_comm_channels(self):
		m = get_comm_channels_data_for_org_ids([ self.getId() ] )
		if m == None:
			return False

		if m.has_key(self.getId()):
			return self._load_comm_channels_from_tuples(m[self.getId()])



	def _load_comm_channels_from_tuples(self, rows):
		n = self.__class__.commnames
		for ( id_type, url) in rows:	
			if n.has_key(int(id_type)):
				self._map[n[id_type]] = url
				
		return True
	
	def _load_address(self):
		m = get_address_data_for_org_ids( [self.getId()])
		if m == None:
			return False

		if not m.has_key(self.getId() ):	
			gmLog.gmDefLog.Log(gmLog.lInfo, "No address for org" )
			return True
		
		return self._load_address_from_tuple( m[self.getId()] )

		
	def _load_address_from_tuple(self, r):	
		self._address = { 'number':r[0], 'street':r[1], 'urb':r[2], 'postcode':r[3], 'state':r[4], 'country': r[5]  }
	
		self._addressModified(False)

		return True
	
	
	def shallow_del(self):
		cmds = [
		 ("delete from lnk_person_org_address where id_org = %d"%self.getId() , [] ),
		 ("delete from lnk_org2comm_channel where id_org = %d"%self.getId(),[] ),
		 ("delete from org where id = %d"%self.getId() , [] )
		]

		if (gmPG.run_commit('personalia',cmds) == None):
				gmLog.gmDefLog.Log(gmLog.lErr, "failed to remove org")
				return False

		self.setId(None)

		return True

			
	
	
	def _create(self):
		#<DEBUG>
		#print "in _create"
		#</DEBUG>
		
		cmd = ("""insert into org (description, id_category) values('xxxDefaultxxx', ( select  id from org_category limit 1) )""", [])
		cmd2 = ("""select currval('org_id_seq')""", [])
		result = gmPG.run_commit('personalia', [cmd, cmd2])
		if result is None:
			cmd = ("""select id from org where description ='xxxDefaultxxx'""",[])
			result = gmPG.run_commit('personalia', [cmd] )
			if result <> None and len(result) == 1:
				self.setId(result[0][0])
				#<DEBUG>
				#print "select id from org ->", self.getId()
				#</DEBUG>
				return True
			return False
		self.setId(result[0][0])
		#<DEBUG>
		#print "from select currval -> ", self.getId()
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
		print "self.getId() = ", self.getId() , " is None : ", self.getId() is None
		if self.getId() is None:
			if not self._create():
				gmLog.gmDefLog.Log(gmLog.lErr, "Cannot create org")
				return False
		if self.getId() is None:
				return False
		if c.has_key('name') or c.has_key('category'):	
			
			#print "pk = ", self.getId()
			#org = cOrganization(str(self.getId()))
			cf = cCatFinder()
			cmd = """
				update org set description='%s' , 
						id_category = %s where id = %s
			 	""" % ( c['name'], 
					str( cf.getId('org_category', c['category']) ),
					str(self.getId())  ) 
			result = gmPG.run_commit( "personalia", [ (cmd,[]  ) ] )
			if result is None:
				gmLog.gmDefLog.Log(gmLog.lErr, "Cannot save org")
				return False
			
		self._save_address()
		self._save_comm_channels()
		return True

	def lnkPerson( self, demographicRecord): # demographicRecord is a cDemographicRecord
		pass

		
def get_comm_channels_data_for_org_ids( idList):	
	"""gets comm_channels for a list of org_id. 
	returns a map keyed by org_id with lists of comm_channel data (url, type). 
	this allows a single fetch of comm_channel data for multiple orgs"""

	ids = ", ".join( [ str(x) for x in idList]) 
	cmd = """select l.id_org, id_type, url 
			from comm_channel c, lnk_org2comm_channel l 
			where
				c.id = l.id_comm and
				l.id_org in ( select id from org where id in (%s) )
		""" % ids 
	result = gmPG.run_ro_query("personalia", cmd)
	if result == None:
		gmLog.gmDefLog.Log(gmLog.lInfo, "Unable to load comm channels for org" )
		return None 
	m = {}
	for (id_org, id_type, url) in result:
		if not m.has_key(id_org):
			m[id_org] = []
		m[id_org].append( (id_type, url) )

	return m # is a Map[id_org] = list of comm_channel data 	
		
def get_address_data_for_org_ids( idList):
	"""gets addresses for a list of valid id values for orgs.
	returns a map keyed by org_id with the address data
	"""
	
	ids = ", ".join( [ str(x) for x in idList]) 
	cmd = """select l.id_org, number, street, city, postcode, state, country 
			from v_basic_address v , lnk_org2address l 
				where v.addr_id = l.id_address and 
				l.id_org in ( select id from org where id in (%s) )""" % ids 
	result = gmPG.run_ro_query( "personalia", cmd)
	
	if result == None:
		gmLog.gmDefLog.Log(gmLog.lInfo, "failure in org address load" )
		return None
	m = {}
	for (id_org, n,s,ci,p,st,co) in result:
		m[id_org] =  (n,s,ci,p,st,co) 
	return m  

def get_org_data_for_org_ids(idList):
	""" for a given list of org id values , 
		returns a map of id_org vs. org attributes: description, id_category"""
	
	ids = ", ".join( [ str(x) for x in idList]) 
	cmd = """select id, description, id_category  from org 
			where id in ( select id from org where id in( %s) )""" % ids 
	#<DEBUG>
	print cmd
	#</DEBUG>
	result = gmPG.run_ro_query("personalia", cmd, )
	if result is None:
		gmLog.gmDefLog.Log(gmLog.lInfo, "Unable to load orgs with ids (%s)" %ids)
		return None
	m = {}
	for (id_org, d, id_cat) in result:
		m[id_org] = (d, id_cat)
	return m 

#============================================================

def get_test_data():
	"""test org data for unit testing in testOrg()"""
	return [ 
			( ["Box Hill Hospital", "", "", "Eastern", "hospital", "0398953333", "111-1111","bhh@oz", ""],  ["33", "Nelson Rd", "Box Hill", "3128", None , None] ), 
			( ["Frankston Hospital", "", "", "Peninsula", "hospital", "0397847777", "03784-3111","fh@oz", ""],  ["21", "Hastings Rd", "Frankston", "3334", None , None] )
		]
		
def testOrg():
	"""runs a test of load, save , shallow_del  on items in from get_test_data"""
	l = get_test_data()
	for (f, a) in l:
		result, obj =	_testOrgRun(f, a)
		results.append( (result, obj) )
	return results	



def _testOrgRun( f1, a1):

	print """testing single level orgs"""
	f = [ "name", "office", "department",  "memo", "category", "phone", "fax", "email","mobile"]
	a = ["number", "street", "urb", "postcode", "state", "country"]
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
	print "saved pk =", h.getId()

	
	pk = h.getId()
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
		
	
	if not h2.load(h.getId()):
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

def clean_test_org():
	l = get_test_data()
	names = [ "".join( ["'" ,str(org[0]), "'"] )  for ( org, address) in l]
	nameList = ",".join(names)
	cmds = [ ("""delete from lnk_person_org_address 
		where id_org in ( select id from org where description in ( %s ))""" % nameList,[]),
		("""delete from lnk_org2comm_channel 
		where id_org in (select id from org where description in ( %s )) """ % nameList,[]),
		("""delete from org where description in ( %s) """ % nameList, [] )
		]
	return gmPG.run_commit("personalia", cmds) <> None
	
		

if __name__== "__main__":
	_log.SetAllLogLevels(gmLog.lData)

	import sys
	if len(sys.argv) > 1:
		if sys.argv[1] == '--clean':
			result = clean_test_org()
			if result:
				print "probably succeeded in cleaning orgs"
			else: 	print "failed to clean orgs"
			sys.exit(1)


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

	print """
	Pre-requisite data in database is :
	gnumed=# select * from org_category ;
	 id | description
	 ----+-------------
	   1 | hospital
	   (1 row)

	gnumed=# select * from enum_comm_types ;
	 id | description
	----+-------------
	  1 | email
	  2 | fax
	  3 | homephone
	  4 | workphone
	  5 | mobile
	  6 | web
	  7 | jabber
	  (7 rows)
	  """
	tmp_category = False  
	if not "hospital" in c.getCategories("org_category") :
		print "FAILED in prerequisite for org_category : test categories are not present."

		tmp_category = True
	
	if tmp_category:
		print """You will need to switch login identity to database administrator in order
			to have permission to write to the org_category table, 
			and then switch back to the ordinary write-enabled user in order
			to run the test cases.
			Finally you will need to switch back to administrator login to 
			remove the temporary org_categories.
			"""
		
		print "NEED TO CREATE TEMPORARY ORG_CATEGORY.\n\n ** PLEASE ENTER administrator login  : e.g  user 'gm-dbowner' and  his password"
		tmplogin = gmPG.request_login_params()
		p = gmPG.ConnectionPool( tmplogin) 
		conn = p.GetConnection("personalia")
		
		cursor = conn.cursor()
		cursor.execute( "insert into org_category(description) values('hospital')")
		cursor.execute("select id from org_category where description in ('hospital')")
		result =  cursor.fetchone()
		if result == None or len(result) == 0:
			print "Unable to create temporary org_category. Test aborted"
			import sys
			sys.exit(-1)
	
		conn.commit()
		
	try:
		if tmp_category:		
			print "succeeded in creating temporary org_category"	
			print 
			print "** Now ** RESUME LOGIN **  of write-enabled user (e.g. _test-doc) "
			conn = None
			p.ReleaseConnection("personalia")
			login2 = gmPG.request_login_params()
			gmPG.ConnectionPool( login2)
			
			c.reload("org_category")

		
		results = [] 
		results = testOrg()
	except:
		import  sys
		print sys.exc_info()[0], sys.exc_info()[1]
		gmLog.gmDefLog.LogException( "Fatal exception", sys.exc_info(),1)

	for (result , org) in results:
		if not result:
			print "trying cleanup"
			if org.shallow_del(): print " 	may have succeeded"
			else:
				print "May need manual removal of org id =", org.getId()
				
				
	if tmp_category:
		while(1):
			try:
				print """Test completed. The temporary category(s) will now
				need to be removed under an administrator login
				e.g. gm-dbowner
				Please enter login for administrator:
				"""
				
		
				tmplogin = gmPG.request_login_params()
				p = gmPG.ConnectionPool(tmplogin)

				conn = p.GetConnection("personalia")

				
				cursor = conn.cursor()
				cursor.execute( "delete from  org_category where description in ('hospital')")
				conn.commit()
				cursor.execute("select id from org_category where description in ('hospital')")
			except:
				import sys
				print sys.exc_info()[0], sys.exc_info()[1]
				continue

			if cursor.fetchone() == None:
				
				print "Succeeded in removing temporary org_category"
			else:
				print "*** Unable to remove temporary org_category"

			conn = None
			p.ReleaseConnection('personalia')
			break
			
		
	
			
	
	
#============================================================
# $Log: gmOrganization.py,v $
# Revision 1.8  2004-05-23 15:22:41  sjtan
#
# allow Unit testcase to run in naive database, by allowing temporary org_category creation/deletion.
#
# Revision 1.7  2004/05/23 13:27:51  sjtan
#
# refactored so getting n orgs using a finder operation will make 3 sql calls
# instead of n x 3 calls (reduce network traffic). Test case expanded, and
# cleanup option for running unit test case added.
#
# Revision 1.6  2004/05/23 11:26:19  sjtan
#
# getPk() now getId() , more consistent with other modules.
#
# Revision 1.5  2004/05/22 10:31:29  ncq
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
