"""
data objects for organization. Hoping to use the helper class to act as Facade
for aggregated data objects ? with validation rules. 
re-used working code form gmClinItem and followed Script Module layout of gmEMRStructItems.

license: GPL"""
#============================================================
__version__ = "$Revision: 1.20 $"

from Gnumed.pycommon import gmExceptions, gmLog,  gmI18N, gmBorg

from Gnumed.pycommon.gmPyCompat import *
from Gnumed.business import gmDemographicRecord
from Gnumed.business import gmPatient 

_log = gmLog.gmDefLog
_log.Log(gmLog.lInfo, __version__)

from Gnumed.pycommon import gmPG


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
		self.__init__(categoryType)
		result = gmPG.run_ro_query("personalia","select id, description from %s" % categoryType)
		if result is None:
			gmLog.gmDefLog(gmLog.lErr, "failed to load %s" % categoryType)
		
		for (id, description) in result:
			self.categories[categoryType]['toId'][description] = id
			self.categories[categoryType]['toDescription'][id] = description
		return self.categories[categoryType]	
	

		
	def getId(self, categoryType, category):
		return self.categories.get(categoryType, self.reload(categoryType)).get('toId',{}).get(category, None)

	def getCategory(self, categoryType, id):
		return self.categories.get(categoryType, self.reload(categoryType)).get('toDescription',{}).get(id, "")

	def getCategories(self, categoryType):
		return self.categories.get(categoryType, self.reload(categoryType)).get('toId',{}).keys()
	
#cCatFinder('org_category')
#cCatFinder('enum_comm_types')


DEPARTMENT = 1
class cOrg:
	
	def __init__(self):
		pass

	def getId(self):
		return None

	def setId(self, id): # ? change to non-public
		pass	
	
	def set(self, name, office, subtype, memo, category, phone, fax, email,mobile = ""):
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

	def load(self, pk):
		return False

	def save(self):
		return False

	def getSubOrgs(self, orgType = DEPARTMENT):
		return []

	def getParent(self):
		return None

	def addSubOrg(self, org, orgType = DEPARTMENT):
		return False
		


class cOrgHelper:
	#-----------------------------
	# class functions
	#---------------------------------------------------------------

	def findAllOrganizations(self):
		return []

	def findOrgsForIds( self,id_list):
		return []

	def findAllOrganizationPKAndName(self):
		return [ (0,"") ]

	def updateCache(self,cOrgHelperInstance):
		pass
	def cacheContains(self, id):
		return False
	
	def getFromCache(self,id):
		return None

	def removeFromCache(self, id):
		return False

	def create(self):
		return None



class cOrgHelperImpl1(gmBorg.cBorg):

	def __init__(self):
		gmBorg.cBorg.__init__(self)
		self._cache = {}

	def cacheContains(self,id):
		return self._cache.has_key(id)
	
	def getFromCache(self,id):
		return self._cache.get(id, None)
	
	def updateCache(self,org):
		self._cache[org.getId()] = org

	def removeFromCache(self, id):
		if self._cache.has_key(id):
			del self._cache[id]
			return True
		return False

	def findAllOrganizations(self):
		result = gmPG.run_ro_query("personalia", """select id from org""",[])
		if result == None:
			gmLog.gmDefLog.LogException("Unable to select id from org", sys.exc_info())
			return False
		
		ids = [ x for [x] in result]
		return self.findOrgsForIds(ids)


	def findOrgsForIds(self, ids):
		""" finds org objects by id. returns a list of cOrgHelper objects
		"""
		#TODO -	caching of org objects on class level.
		#     - listening for backend data changes using pycommon.gmDispatcher	
		#	and cache update.
	        return self._findOrgsForIdsCacheCheck(ids)



	def _findOrgsForIdsCacheCheck(self, ids):
		orglist = []
		fetch_ids = []	
		for id in ids:
			if self.cacheContains(id):
				org = self.getFromCache(id)
				orglist.append(org)
				continue
			fetch_ids.append(id)
			
		dbOrgList = self._findOrgsForIdsFromDB( fetch_ids)

		for org in dbOrgList:
			self.updateCache(org)

		return orglist	+ dbOrgList
	
	def _findOrgsForIdsFromDB(self, fetch_ids):	
		if fetch_ids == None or fetch_ids == []:
			return []

		om  = get_org_data_for_org_ids(fetch_ids)
		cm = get_comm_channels_data_for_org_ids(fetch_ids )
		am = get_address_data_for_org_ids( fetch_ids)
		m = {}
		orglist = []
		for id in fetch_ids:
			org = self.create()
			if not org._load_org_from_tuple(om.get(id, None), id):
				continue
			org._load_comm_channels_from_tuples( cm.get(id, None) )
			org._load_address_from_tuple( am.get(id, None) )
			orglist.append(org)
		return orglist			
			
	def findOrgsByName( self, name, exact = False):
		"""the org name is a unique key, so should only return one or none org"""
		if exact: query= "select id from org where description = '%s'"%name
		else: query = "select id from org where description like '%s%%'"%name
			
		result = gmPG.run_ro_query("personalia", query )
		if result is None:
			gmLog.gmDefLog.Log(gmLog.lErr, "Unable to find org by name %s" % name) 
			return [None] 

		return self.findOrgsForIds([ x[0] for x in result])	
			

	def findAllOrganizationPKAndName(self):
		return [ (0,"") ]


	def create(self):
		return cOrgImpl1()

		



class cOrgHelperImpl2(cOrgHelperImpl1):
	
	def __init__(self):
		cOrgHelperImpl1.__init__(self)
	
	def create(self):
		return cCompositeOrgImpl1()

	def findOrgsForIds(self, ids):
		"""extends cOrgHelperImpl1's findOrgsforIds and orders them
		parent/ child order"""
		
		l = cOrgHelperImpl1.findOrgsForIds(self, ids)
		childMap = {}
		parents = filter( lambda(o): o.getParent() is None, l)
		childMap = dict( [ (p.getId() , []) for p in parents ] )
		for o in l:
			if o in parents:
				continue
			childMap[o.getParent().getId()].append(o)
		
		l2 = []
		for p in parents:
			l2.append(p)
			for c in childMap[p.getId()]:
				l2.append(c)
		
		return l2
			

	
	
class cOrgImpl1(cOrg):
	
	attrNames = [ 'name', 'office', 'subtype', 'memo','category', 'phone', 'fax', 'email', 'mobile' ]
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

	_cache = {}
	#-----------------------------------------
	# instance methods
	#--------------------------------------------------------------------------

	def __init__(self, helper = cOrgHelperImpl1() ):
		self._map = dict ( [ (n,'') for n in self.__class__.attrNames] )
		
		self._changed= {}
		self.pk = None
		self._addressModified(False)
		self._address = {}

		self._personMap = {}
		self._helper = helper
		pass

	def getHelper(self):
		return self._helper

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
	
	def set(self, name, office, subtype,  memo, category, phone, fax, email,mobile):
		self._set_impl(name, office, subtype,  memo, category, phone, fax, email,mobile)
		
		
	def _set_impl(self, *kwrd, **kargs):
		"""
		
		"""
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
		if urls == []:
			return True
		
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

		# allow for no address
		if a['urb'].strip() == '':
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
		self._load_org_from_tuple(m_org[pk], pk)

	
	def _load_org_from_tuple(self, tuple, pk = None):
		if tuple == None or tuple == []:
			self.setId(None)
			return False

		(description, id_category) = tuple
		m=self._map
		cf = cCatFinder()
		m['category']=cf.getCategory("org_category",id_category)

		m['name']=description
		self.setId(pk)

		return True
	
	
	def _load_comm_channels(self):
		"""uses get_comm_channels_data_for_org_ids with only a singleton id list,
		with the current id to be fetched, then convert to self._map so 
		can be read from self.get() #returning a map of comm channel types vs urls"""
		m = get_comm_channels_data_for_org_ids([ self.getId() ] )
		if m == None:
			return False

		if m.has_key(self.getId()):
			return self._load_comm_channels_from_tuples(m[self.getId()])



	def _load_comm_channels_from_tuples(self, rows):
		if rows == None :
			return False
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
		#precondition: must be a tuple and have right number of fields
		if r == None or len(r) < 6:
			return False

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
		v = self['name']
		if v <> None:
			cmd = "select id from org where description = '%s'" % v
			result = gmPG.run_ro_query('personalia', cmd)
			if result <> None and len(result) <> 0:
				self.setId(result[0][0])
				return True
		
		
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

		#TODO only the name, category attributes are saved; sql places for memo , office, subtype needed.
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
				import sys
				gmLog.gmDefLog.Log(gmLog.lErr, "Cannot create org")
				return False
		if self.getId() is None:
				return False
		# c is any changed, m is what is current
		if c.has_key('name') or c.has_key('category'):	
			
			#print "pk = ", self.getId()
			#org = cOrganization(str(self.getId()))
			cf = cCatFinder()
			#print "cCatFinder", cf.getCategories('org_category')
			#print "m['category']", m['category'], "cf.getId(.. = ", cf.getId('org_category', m['category'])
			cmd = """
				update org set description='%s' , 
						id_category = %s where id = %s
			 	""" % ( m['name'], 
					str( cf.getId('org_category', m['category']) ),
					str(self.getId())  ) 
			result = gmPG.run_commit( "personalia", [ (cmd,[]  ) ] )
			if result is None:
				gmLog.gmDefLog.Log(gmLog.lErr, "Cannot save org")
				return False
			
		self._save_address()
		self._save_comm_channels()
		self._helper.updateCache(self)
		return True

	def linkPerson( self, demographicRecord): # demographicRecord is a cDemographicRecord
		if self.getId() == None:
			return False, _("Org must be saved before adding persons")
		cmd = "insert into lnk_person_org_address(id_identity, id_org) values (%d,%d)" % ( demographicRecord.getID(), self.getId() )
	
		result = gmPG.run_commit("personalia", [ (cmd,[]) ] )

		if result is None:
			gmLog.gmDefLog.Log(gmLog.lErr, "Cannot link person")
			return False, _("SQL failed for link persons")
	
		return True, _("Ok")

	def unlinkPerson(self, demographicRecord):
		if self.getId() == None:
			return False, _("Org must be saved before adding persons")

		cmd = """delete from lnk_person_org_address where id_identity = %d
		and id_org = %d """ % ( demographicRecord.getID() , self.getId() )
		
		result = gmPG.run_commit("personalia", [ (cmd,[]) ] )

		if result is None:
			gmLog.gmDefLog.Log(gmLog.lErr, "Cannot unlink person")
			return False
	
		return True
		
	
	def getPersonMap(self):
		"""gets the persons associated with this org, lazy loading demographic records
		and caching if needed; need to later use a singleton demographic cache,
		so that single copies of a demographic record is shared """
		if self.getId() == None:
			return {}

		query = "select id_identity from lnk_person_org_address where id_org = %d"% self.getId()
		result = gmPG.run_ro_query("personalia", query)
		print "for ", query, " got ", result
		m = {}

		m.update(self._personMap)
		if result is None:
			gmLog.gmDefLog.Log(gmLog.lErr, "Cannot search for org persons")
			return None

		ids = filter( lambda(t): t <> None, [ id	for [id] in result ])
		print "id list is ", ids
		new_ids = filter( lambda(id): id not in m.keys(), ids) 
			
		for id in new_ids:
			rec = gmDemographicRecord.cDemographicRecord_SQL(id)
			m[id] = rec
		
		self._personMap.update(m)
		
		return m
			

class cCompositeOrgImpl1( cOrgImpl1):
	"""this class behaves differently from cOrgImpl1 iff there is a parent org"""

	def __init__(self, parent = None, helper = cOrgHelperImpl2() ):
		cOrgImpl1.__init__(self, helper)
		self._parent = parent

	def _create(self):
		
		if not cOrgImpl1._create(self):

			return False
		
		return self._saveCompositeName()

	def save(self):
		"""if getParent() is None, then the behaviour is 
		unchanged from cOrgImpl1, but if there is a parent org,
		then there will also sub-org information saved in the description"""

		if not cOrgImpl1.save(self):
			return False
		return self._saveCompositeName()

	
	
	def _saveCompositeName(self):
		parent = self.getParent()
		if parent == None:
			return True

		new_description = '\n'.join([parent['name'] , self['name'], self['subtype']])
		result = gmPG.run_commit("personalia", [ ("""update org set description='%s' where id=%d
			""" % (new_description, self.getId() ), [] ) ])
		if result == None:
			gmLog.gmDefLog.LogException("unable to update sub-org name", sys.exc_info() )
			return False
		return True

	
	def _load_org_from_tuple(self, tuple, pk = None):
		"""this loads the org like cOrgImpl1, but then checks for
		additional sub-org information in the 'name' aka org.description,
		and if it exists, the parent is retrieved or constructed using
		the findOrgByName function.
		"""

		if not cOrgImpl1._load_org_from_tuple(self, tuple, pk):
			return False

		# first extended behaviour, recognise subtype attribute.
		self['subtype'] = ''

		l = self['name'].split('\n')
		print "split org name into ", l
		if len(l) < 3:
			return True

		(parentName, self['name'], self['subtype'] ) = l
		orgList = self._helper.findOrgsByName(parentName, exact = True)
		if orgList == []:
			return True
		org = orgList[0]
		self.setParent(org)	
		
		return True	

			
			
	def setParent(self, parent):
		self._parent = parent
		
		

	def getParent(self):
		return self._parent

	def getSubOrgs(self, orgtype=DEPARTMENT):
		return []

	
		
		

		
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
				l.id_org in ( select id from org where id in (%s) ) """ % ids 
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
#
#  IGNORE THE FOLLOWING, IF NOT INTERESTED IN TEST CODE
#
#

if __name__ == '__main__':
	print "Please enter a write-enabled user e.g. _test-doc "

def testListOrgs():
	print "running test listOrg"
	for (f,a) in get_test_data():
		h = cOrgImpl1()
		h.set(*f)
		h.setAddress(*a)
		if not h.save():
			print "did not save ", f

	orgs = cOrgHelperImpl1().findAllOrganizations()

	for org in orgs:
		print "Found org ", org.get(), org.getAddress()
		if not org.shallow_del():
			print "Unable to delete above org"






def get_test_data():
	"""test org data for unit testing in testOrg()"""
	return [
			( ["Box Hill Hospital", "", "", "Eastern", "hospital", "0398953333", "111-1111","bhh@oz", ""],  ["33", "Nelson Rd", "Box Hill", "3128", None , None] ),
			( ["Frankston Hospital", "", "", "Peninsula", "hospital", "0397847777", "03784-3111","fh@oz", ""],  ["21", "Hastings Rd", "Frankston", "3199", None , None] )
		]

def get_test_persons():
	return { "Box Hill Hospital":
			[
			['Dr', 'Bill' , 'Smith', '123-4567', '0417 111 222'],
			['Ms', 'Anita', 'Jones', '124-5544', '0413 222 444'],
			['Dr', 'Will', 'Stryker', '999-4444', '0402 333 111']  ],
		"Frankston Hospital":
			 [ [ "Dr", "Jason", "Boathead", "444-5555", "0403 444 2222" ],
			   [ "Mr", "Barnie", "Commuter", "222-1111", "0444 999 3333"],
			   [ "Ms", "Morita", "Traveller", "999-1111", "0222 333 1111"]] }

def testOrgPersons():
	m = get_test_persons()
	d  = dict(  [  (f[0] , (f, a)) for (f, a) in get_test_data() ] )
	for orgName , personList in m.items():
		_testOrgPersonRun( d[orgName][0], d[orgName][1], personList )




def _testOrgPersonRun(f1, a1, personList):
	print "Using test data :f1 = ", f1, "and a1 = ", a1 , " and lp = ", personList
	print "-" * 50
	h = cOrgImpl1()
	h.set(*f1)
	h.setAddress(*a1)
	if not h.save():
		print "Unable to save org for person test"
		h.shallow_del()
		return False
	# use gmDemographicRecord to convert person list
	for lp in personList:
		id = gmPatient.create_dummy_identity()

		identity = gmDemographicRecord.cDemographicRecord_SQL(id)

		identity.addName(lp[1], lp[2], True)
		identity.setTitle(lp[0])
		identity.linkCommChannel( gmDemographicRecord.WORK_PHONE, lp[3])
		identity.linkCommChannel( gmDemographicRecord.MOBILE, lp[4])

		result , msg = h.linkPerson(identity)
		print msg

	m = h.getPersonMap()

	if m== []:
		print "NO persons were found unfortunately"

	print """ TestOrgPersonRun got back for """
	a = h.getAddress()
	print h["name"], a["number"], a["street"], a["urb"], a["postcode"] , " phone=", h['phone']

	for id, r in m.items():
		print "\t",", ".join( [ " ".join(r.get_names().values()),
					"work no=", r.getCommChannel(gmDemographicRecord.WORK_PHONE),
					"mobile no=", r.getCommChannel(gmDemographicRecord.MOBILE)
					] )
		h.unlinkPerson(r)

		result = deletePerson(r.getID())
		if result == None:
			gmLog.gmDefLog.Log(gmLog.lErr, "FAILED TO CLEANUP PERSON %d" %r.getID() )



	if h.shallow_del():
		print "Managed to dispose of org"
	else:
		print "unable to dispose of org"

	return True

def deletePerson(id):
	cmds = [ ( "delete from lnk_identity2comm_chan where id_identity=%d"%id,[]),
		("delete from names where id_identity=%d"%id,[]),
		("delete from identity where id = %d"%id,[]) ]
	result = gmPG.run_commit("personalia", cmds)
	return result


def testOrg():
	"""runs a test of load, save , shallow_del  on items in from get_test_data"""
	l = get_test_data()
	results = []
	for (f, a) in l:
		result, obj =	_testOrgRun(f, a)
		results.append( (result, obj) )
	return results



def _testOrgRun( f1, a1):

	print """testing single level orgs"""
	f = [ "name", "office", "subtype",  "memo", "category", "phone", "fax", "email","mobile"]
	a = ["number", "street", "urb", "postcode", "state", "country"]
	h = cOrgImpl1()

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



	h2 = cOrgImpl1()

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
	names += [ "'John Hunter Hospital'", "'Belmont District Hospital'"]
	nameList = ",".join(names)
	categoryList = "'hospital'"

	cmds = [ ( """create temp table del_org as 
			select id  from org 
			where description in(%s) or 
			id_category in ( select id from org_category c 
						where c.description in (%s))
		""" % (nameList, categoryList), [] ),
		("""create temp table del_identity as  
		select id  from identity 
		where id in 
			( 
				select id_identity from lnk_person_org_address 
				where id_org in ( select id from del_org)
			)""",[] ),
		("""create temp table del_comm as 
		(select id_comm from lnk_org2comm_channel where 
			id_org in ( select id from del_org) 
		) UNION
		(select id_comm from lnk_identity2comm_chan where
			id_identity in ( select id from del_identity)
		)""", [] ), 
		("""delete from names where id_identity in 
				(select id from del_identity)""",[]), 
		("""delete from lnk_person_org_address where 
				id_org in (select id from del_org )""",[]), 
		("""delete from lnk_person_org_address where 
				id_identity in (select id from del_identity)""", []),
		("""delete from lnk_org2comm_channel 
		where id_org in (select id from del_org) """,[]),
		("""delete from lnk_identity2comm_chan 
				where id_identity in (select id from del_identity)""",[] ), 
		("""delete from comm_channel where id in ( select id_comm from del_comm)""",[]),
		("""delete from identity where id in (select id from del_identity)""",[] ),
		("""delete from org where id in ( select id from del_org) """ , [] ),
		("""drop table del_comm""",[]),
		("""drop table del_identity""",[]),
		("""drop table del_org""", [])
				
		]
	result =  gmPG.run_commit("personalia", cmds) <> None

	return result	


def login_user_and_test(logintest, service = 'personalia', msg = "failed test" , use_prefix_rw= False):
	""" tries to get and verify a read-write connection
	 which has permission to write to org tables, so the test case
	 can run.
	 """
	login2 = gmPG.request_login_params()

	#login as the RW user
	p = gmPG.ConnectionPool( login2)
	if use_prefix_rw:
		conn = p.GetConnection( service, readonly = 0)
	else:
		conn = p.GetConnection(service)
	result = logintest(conn)

	if result is False:
		print msg

	p.ReleaseConnection(service)	
	return result, login2

def test_rw_user(conn):
	# test it is a RW user, by making a entry and deleting it
	try:
		c.reload("org_category")
		cursor = conn.cursor()

		cursor.execute("select last_value from org_id_seq")
		[org_id_seq] = cursor.fetchone()

		cursor.execute("""
	insert into org ( description, id_category, id)
	values ( 'xxxDEFAULTxxx', %d,
	%d)
		""" % ( c.getId('org_category', 'hospital') , org_id_seq + 1 ) )
		cursor.execute("""
	delete from org where id = %d""" % ( org_id_seq + 1) )
	# make sure this exercise is committed, else a deadlock will occur
		conn.commit()
	except:
		gmLog.gmDefLog.LogException("Test of Update Permission failed", sys.exc_info() )
		return False
	return True

def test_admin_user(conn):
	try:
		cursor = conn.cursor()

		cursor.execute("select last_value from org_category_id_seq")
		[org_cat_id_seq] = cursor.fetchone()

		cursor.execute("""
	insert into org_category ( description, id)
	values ( 'xxxDEFAULTxxx',%d)
		""" %   (org_cat_id_seq + 1 ) )
		cursor.execute("""
	delete from org_category where description like 'xxxDEFAULTxxx' """ )
	# make sure this exercise is committed, else a deadlock will occur
		conn.commit()
	except:
		gmLog.gmDefLog.LogException("Test of Update Permission failed", sys.exc_info() )
		return False
	return True

def login_rw_user():
	return  login_user_and_test( test_rw_user, "login cannot update org", use_prefix_rw = True)


def login_admin_user():
	return  login_user_and_test( test_admin_user, "login cannot update org_category" )


def create_temp_categories( categories = ['hospital']):
	print "NEED TO CREATE TEMPORARY ORG_CATEGORY.\n\n ** PLEASE ENTER administrator login  : e.g  user 'gm-dbowner' and  his password"
	#get a admin login
	for i in xrange(0, 4):
		result ,tmplogin = login_admin_user()
		if result:
			break
	if i == 4:
		print "Failed to login"
		return categories

	# and save it , for later removal of test categories.
	from Gnumed.pycommon import gmLoginInfo
	adminlogin = gmLoginInfo.LoginInfo(*tmplogin.GetInfo())

	#login as admin
	p = gmPG.ConnectionPool( tmplogin)
	conn = p.GetConnection("personalia")

	# use the last value + 1 of the relevant sequence, but don't increment it
	cursor = conn.cursor()

	failed_categories = []
	n =1
	for cat in categories:
		cursor.execute("select last_value from org_category_id_seq")
		[org_cat_id_seq] = cursor.fetchone()

		cursor.execute( "insert into org_category(description, id) values('%s', %d)" % (cat, org_cat_id_seq + n) )
		cursor.execute("select id from org_category where description in ('%s')" % cat)

		result =  cursor.fetchone()
		if result == None or len(result) == 0:
			failed_categories.append(cat)
			print "Failed insert of category", cat
			conn.rollback()
		else:
			conn.commit()
		n += 1	

	conn.commit()
	p.ReleaseConnection('personalia')
	return failed_categories, adminlogin

def clean_org_categories(adminlogin = None, categories = ['hospital'], service='personalia'):

	print"""

	The temporary category(s) will now
	need to be removed under an administrator login
	e.g. gm-dbowner
	Please enter login for administrator:
	"""
	if adminlogin is None:
		for i in xrange(0, 4):
			result, adminlogin = login_admin_user()
			if  result:
				break
		if i == 4:
			print "FAILED TO LOGIN"
			return categories

	p = gmPG.ConnectionPool(adminlogin)
	conn = p.GetConnection(service)
	failed_remove = []
	for cat in categories:
		try:
			cursor = conn.cursor()
			cursor.execute( "delete from  org_category where description in ('%s')"%cat)
			conn.commit()
			cursor.execute("select id from org_category where description in ('%s')"%cat)
			if cursor.fetchone() == None:
				print "Succeeded in removing temporary org_category"
			else:
				print "*** Unable to remove temporary org_category"
				failed_remove .append(cat)
		except:
			import sys
			print sys.exc_info()[0], sys.exc_info()[1]
			import traceback
			traceback.print_tb(sys.exc_info()[2])

			failed_remove.append(cat)

	conn = None
	p.ReleaseConnection(service)
	if failed_remove <> []:
		print "FAILED TO REMOVE ", failed_remove
	return failed_remove

def test_CatFinder():
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


def help():
	print """\nNB If imports not found , try:

	change to gnumed/client directory , then

	export PYTHONPATH=$PYTHONPATH:../;python business/gmOrganization.py
	"""
	print
	print "In the connection query, please enter"
	print "a WRITE-ENABLED user e.g. _test-doc (not test-doc), and the right password"
	print
	print "Run the unit test with cmdline argument '--clean'  if trying to clean out test data"
	print

	print """You can get a sermon by running
	export PYTHONPATH=$PYTHONPATH:../;python business/gmOrganization.py --sermon
	"""
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

def sermon():
			print"""
	This test case shows how many things can go wrong , even with just a test case.
	Problem areas include:
	- postgres administration :  pg_ctl state, pg_hba.conf, postgres.conf  config files .
	- schema integrity constraints : deletion of table entries which are subject to foreign keys, no input for no default value and no null value columns, input with duplicated values where unique key constraint applies to non-primary key columns, dealing with access control by connection identity management.


	- efficiency trade-offs -e.g. using db objects for localising code with data and easier function call interface ( then hopefully, easier to program with) , vs. need to access many objects at once
	without calling the backend for each object.

	- error and exception handling - at what point in the call stack to handle an error.
	Better to use error return values and log exceptions near where they occur, vs. wrapping inside try: except: blocks and catching typed exceptions.


	- test-case construction:  test data is needed often, and the issue
	is whether it is better to keep the test data volatile in the test-case,
	which handles both its creation and deletion, or to add it to test data
	server configuration files, which may involve running backend scripts
	for loading and removing test data.



	- Database connection problems:
	-Is the problem in :
		- pg_ctl start -D  /...mydata-directory is wrong, and gnumed isn't existing there.

		- ..mydata-directory/pg_hba.conf
			- can psql connect locally and remotely with the username and password.
			- Am I using md5 authenentication and I've forgotten the password.
				- I need to su postgres, alter pg_hba.conf to use trust for
				the gnumed database, pg_ctl restart -D .., su normal_user,  psql gnumed, alter user my_username password 'doh'
				- might be helpful: the default password for _test-doc is test-doc

		- ../mydata-directory/postgres.conf
			- tcp connect  flag isn't set to true

		- remote/local mixup :
		a different set of user passwords on different hosts. e.g the password
		for _test-doc is 'pass' on localhost and 'test-doc' for the serverhost.
		- In the prompts for admin and user login, local host was used for one, and
		remote host for the other



	- test data won't go away :
	- 'hospital' category in org_category : the test case failed in a previous run
	and the test data was left there; now the test case won't try to delete it
	because it exists as a pre-existing category, so manually delete with psql.

	- test-case failed unexpectedly, or break key was hit in the middle of a test-case run.
		Soln: run with --clean option,
			then delete temporary org_category  entries with psql.

	- remote/local mixup: as above

	"""


#============================================================
if __name__ == "__main__":
	_log.SetAllLogLevels(gmLog.lData)
	import sys
	testgui = False
	if len(sys.argv) > 1:
		if sys.argv[1] == '--clean':
			result = clean_test_org()
			p = gmPG.ConnectionPool()
			p.ReleaseConnection('personalia')
			if result:
				print "probably succeeded in cleaning orgs"
			else: 	print "failed to clean orgs"

			clean_org_categories()
			sys.exit(1)

		if sys.argv[1] == "--sermon":
			sermon()

		if sys.argv[1] == "--help":
			help()
		
		if sys.argv[1] =="--gui":
			testgui = True
			
	print "*" * 50
	print "RUNNING UNIT TEST of gmOrganization "


	test_CatFinder()
	tmp_category = False  # tmp_category means test data will need to be added and removed
			# for  org_category .
	
	c = cCatFinder()
	if not "hospital" in c.getCategories("org_category") :
		print "FAILED in prerequisite for org_category : test categories are not present."

		tmp_category = True

	if tmp_category:
		# test data in a categorical table (restricted access) is needed

		print """You will need to switch login identity to database administrator in order
			to have permission to write to the org_category table,
			and then switch back to the ordinary write-enabled user in order
			to run the test cases.
			Finally you will need to switch back to administrator login to
			remove the temporary org_categories.
			"""
		categories = ['hospital']
		result, adminlogin = create_temp_categories(categories)
		if result == categories:
			print "Unable to create temporary org_category. Test aborted"
			sys.exit(-1)
		if result <> []:
			print "UNABLE TO CREATE THESE CATEGORIES"
			if not raw_input("Continue ?") in ['y', 'Y'] :
				sys.exit(-1)

	try:
		results = []
		if tmp_category:
				print "succeeded in creating temporary org_category"
				print
				print "** Now ** RESUME LOGIN **  of write-enabled user (e.g. _test-doc) "
				while (1):
					# get the RW user for org tables (again)
					if login_rw_user():
						break

		if testgui:
			if cCatFinder().getId('org_category','hospital') == None:
				print "Needed to set up temporary org_category 'hospital"
				sys.exit(-1)
			import os
			print os.environ['PWD']
		 	os.spawnl(os.P_WAIT, "/usr/bin/python", "/usr/bin/python","wxpython/gnumed.py", "--debug") 
			
			#os.popen2('python client/wxpython/gnumed.py --debug')

			# run the test case
		results = testOrg()

			# cleanup after the test case
		for (result , org) in results:
			if not result and org.getId() <> None:
				print "trying cleanup"
				if  org.shallow_del(): print " 	may have succeeded"
				else:
					print "May need manual removal of org id =", org.getId()

		testOrgPersons()

		testListOrgs()

	except:
		import  sys
		print sys.exc_info()[0], sys.exc_info()[1]
		gmLog.gmDefLog.LogException( "Fatal exception", sys.exc_info(),1)

		# clean-up any temporary categories.
	if tmp_category:
		try:
			clean_org_categories(adminlogin)
		except:
			while(not login_rw_user()[0]):
				pass
			clean_test_org()
			clean_org_categories(adminlogin)
#===========================================================
# $Log: gmOrganization.py,v $
# Revision 1.20  2004-05-28 15:13:53  sjtan
#
# one level of sub orgs done ; can enter departments; category stays as hospital.
#
# Revision 1.19  2004/05/28 13:19:23  ncq
# - Syan, can't we move all test related code
#   into if __name__ == '__main__' ?
#
# Revision 1.18  2004/05/28 04:29:53  sjtan
#
# gui test case option; should setup/teardown ok if correct logins.
#
# Revision 1.17  2004/05/28 01:20:14  sjtan
#
# cleanup script would probably work for comm_channel if left out org.del_shallow()
# in test runs.
#
# Revision 1.16  2004/05/26 18:21:38  sjtan
#
# add org , save  toolbar buttons linked,  list select linked, needs testing,
# must have 'hospital' if table org_category.
#
# Revision 1.15  2004/05/25 14:10:45  sjtan
#
# cleanup temp persons as well.
#
# Revision 1.14  2004/05/25 13:32:45  sjtan
#
# cleanup, obsolete removed.
#
# Revision 1.13  2004/05/24 21:09:01  ncq
# - cleanup
#
# Revision 1.12  2004/05/24 05:49:59  sjtan
#
# test case working for gmDemographicRecord_SQL linking/unlinking; local and remote tested.
#
# Revision 1.11  2004/05/24 03:34:56  sjtan
#
# tested local and remote test case; setup/pulldown for test case is within test case.
#
# Revision 1.10  2004/05/24 00:32:24  sjtan
#
# don't want to increment the sequence number for a temporary org_category, as there is no way
# of restoring it.
#
# Revision 1.9  2004/05/23 15:27:56  sjtan
#
# allow test case to run without sql test data script for org tables.
#
# Revision 1.8  2004/05/23 15:22:41  sjtan
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
