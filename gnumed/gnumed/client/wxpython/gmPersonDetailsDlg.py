#!/usr/bin/python
#############################################################################
#
# gmPersonDetailsDlg - dialog & plugin for personal details like name and adddress
#                     (part of the gnumed package)
# ---------------------------------------------------------------------------
#
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: nil
# @change log:
#	10.03.2002 hherb first draft, largely untested
#
# @TODO: Almost everything
############################################################################

from wxPython.wx import *
import gettext
_ = gettext.gettext

import gmPersonDetails, gmPlugin, gmCachedPerson, gmCachedAddress
#from PopupListChoiceWindow import *
import gmPG

ID_BUTTON_SAVE = wxNewId()
ID_BUTTON_ADD = wxNewId()
ID_BUTTON_NEW = wxNewId()
ID_BUTTON_UNDO = wxNewId()
ID_BUTTON_FAMILY = wxNewId()
ID_BUTTON_DELETE = wxNewId()
ID_BUTTON_MERGE = wxNewId()
ID_BUTTON_EXPORT = wxNewId()
ID_BUTTON_IMPORT = wxNewId()

COUNTRY_COLUMN_MAX = 30 

class PersonDetailsDlg(gmPersonDetails.PnlPersonDetails, gmPlugin.wxGuiPlugin):

	def __init__(self, parent, id, guibroker=None, callbackbroker=None, dbbroker=None, name=_("PersonDetails")):
		"""Initializes data structure and command buttons. 
		   Zeroes Id and name/control/operation mappings
		   sets up ui dependency between gender and title.  
		"""

		gmPersonDetails.PnlPersonDetails.__init__(self, parent, id)
		gmPlugin.wxGuiPlugin.__init__(self, name, guibroker, callbackbroker, dbbroker)

		self.__person = gmCachedPerson.CachedPerson()
		self.__address = gmCachedAddress.CachedAddress()
		self.__person.notify_me("PersonDetailsDlg", self.OnDataUpdate)
		#add a button container to the bottom of the dialog
		line = wxStaticLine( self, -1, wxDefaultPosition, wxDefaultSize, wxLI_HORIZONTAL )
		self.szrTop.AddWindow( line, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 0 )
		self.szrCommandButtons = wxBoxSizer(wxHORIZONTAL)
		#add a few command buttons
		self.btnSave = self.AddButton(ID_BUTTON_SAVE, _("&Save"),  self.szrCommandButtons, self.OnSave)
		self.btnUndo = self.AddButton(ID_BUTTON_ADD, _("&Undo"),  self.szrCommandButtons, self.OnUndo)
		self.btnNew = self.AddButton(ID_BUTTON_NEW, _("&New"),  self.szrCommandButtons, self.OnNew)
		self.btnDelete = self.AddButton(ID_BUTTON_DELETE, _("&Delete"),  self.szrCommandButtons, self.OnDelete)
		self.szrTop.AddSizer(self.szrCommandButtons, 1, wxLEFT|wxRIGHT|wxBOTTOM, 5)
		self.szrTop.Fit( parent )
		self.szrTop.SetSizeHints( parent )
		self.personMapping = None
		self.addressMapping = None
		
		self.__LoadCountries()
		self.__setPersonId(None)
		self.__setAddressId(None)

		self.cursor = None
		EVT_COMBOBOX( self.comboTitle, gmPersonDetails.ID_COMBO_TITLE, self.titleChanged)
		self.genderList = [ { 'f' : _('Mrs.'), 'm': _('Mr.') }, 
				    { 'f' : _('Miss'), 'm': _('Mstr.')},
				    {  'f' : _('Ms.'), 'm' : _('Mr.') }
				  ]
		self.otherGender = { 'f' : 'm' , 'm' : 'f' }

		EVT_RADIOBOX( self.chGender, gmPersonDetails.ID_CHOICE_GENDER, self.genderChanged) 

		self.invisibleMap = {} 



	def titleChanged(self, event):
		""" change the gender to match the title
		"""

		if event.GetString() in [ _("Mr."), _("Mstr.")] :
			self.chGender.SetStringSelection('m')
		else:
			if event.GetString() in [_("Miss"), _("Mrs."), _("Ms.")]:
				self.chGender.SetStringSelection('f')
		event.Skip()

	def genderChanged( self, event):
		"""change the title to match the gender
		"""
		
		g = event.GetString()
		print "checking out radiobutton = ", g, event
		other = self.otherGender[g]
		title = self.comboTitle.GetValue()
		for x in self.genderList:
			if x[other] == title:
				print x
				n = self.comboTitle.FindString(x[g])
				self.comboTitle.SetSelection(n)
				#self.comboTitle.SetString(x[g])
				
				event.Skip()
				return
				
		event.Skip()
	
			 
	
	def __setAddressId(self, id):
		self.addressId = id
		print "address id set to ",id	



	def __setPersonId(self, id):
		self.personId = id
		print "person id set to ",id	

	def __LoadCountries(self):
		"""loads the comboBox for countries with a part of the total list.
			Selecting more will load next part of list into comboBox.	
			implemented because Linux ui on gnome doesn't have scrollable
			combo selection box. """
		
		countries = self.__GetCountries()
		list = []
		self.countriesAll = countries
		for x in countries:
			list.append(x[1])
		
		if ( len(countries) > COUNTRY_COLUMN_MAX) :
			n = len(countries) / COUNTRY_COLUMN_MAX
			try:
				self.chCountry.SetColumns(n) 
			except:
				print "not motif, can't set chCountry columns"

			if self.chCountry.GetColumns() != n:
				print "using list box window for extra choices"
				for i in xrange(0, COUNTRY_COLUMN_MAX):
					self.chCountry.Append(list[i])
				self.countryList = list
				self.countryStart = 0
				self.chCountry.Append("MORE")
				EVT_CHOICE ( self.chCountry, -1, self.checkForMore)
			else:
				for x in list:
					self.chCountry.Append(x)

		self.chCountry.SetStringSelection("AUSTRALIA")

# completely changed to just rotating the entries in the choice
	def checkForMore(self, event):
		""" rotates the country list to the next part if MORE selected """
		if (self.chCountry.GetStringSelection() == "MORE"):
			self.countryStart += COUNTRY_COLUMN_MAX
			if self.countryStart >= len(self.countryList):
				self.countryStart = 0
			self.chCountry.Clear()
			for i in xrange( 0, COUNTRY_COLUMN_MAX):
				if self.countryStart + i  < len( self.countryList):
					self.chCountry.Append(self.countryList[self.countryStart + i])
			self.chCountry.Append("MORE")	
			event.Skip()
			
		
	
	def __GetCountries(self):
		query =  "select * from country" 
		db = self.getDB()
		cursor = db.cursor()
		cursor.execute(query)
		countries = cursor.fetchall()
		return countries

	def AddButton(self, id, caption, szr, callback):
		btn = wxButton( self, id, caption, wxDefaultPosition, wxDefaultSize, 0 )
		szr.AddWindow( btn, 0, wxALIGN_BOTTOM|wxALIGN_CENTER_VERTICAL, 5 )
		EVT_BUTTON(self, id, callback)
		return btn

	def OnNew(self, evt):
		print evt.GetId()
		self.ClearData()

	def OnSave(self, evt):
		"""saves the data in the person and the address fields of the dialog, into the
		database. First map the control values into a map, calling GetPersonMAp and GetAddressMap.
		Then using map formatting of sql command strings to get relevant insert or update
		sql statement. If no personId , then an insert statement is needed, otherwise 
		a update statements. 
		Updates and Inserts are done through view triggers for v_basic_person, v_basic_address,
		see gmidentity.sql and gmgis.sql in sql directory for details. 
		"""
	
		print evt.GetId()


		personMap = self.GetPersonMap()
		addressMap = self.GetAddressMap()
		
		queries = []
	
		if self.personId == None or self.personId == -1:


				db = self.getDB()
				try:
					db.commit()
					cursor = db.cursor()
					setup = self.getSqlSettings()
					for x in setup:
						cursor.execute(x)

					map = self.LowerMap( personMap,  self.__GetPersonMapping())
					self.__person.create_person( map, db)

					map = self.LowerMap( addressMap,  self.__GetAddressMapping())
					self.__address.create_address_link( map, db)

					stmt  = """select currval('identity_id_seq'), currval('identities_addresses_id_seq')"""
					print stmt
					cursor.execute(stmt)
					(a,b) = cursor.fetchone()
					print " personId = ", a, "addressId = ",b
					db.commit()
					self.__setPersonId(a)
					self.__setAddressId(b)
					self.__person.reset()
					self.__address.reset()
					self.OnDataUpdate(None, a)
					
				except Exception, errorStr:
					db.rollback()
					print "error in inserting queries, ", errorStr, 'at line=', sys.exc_traceback.tb_lineno
					frame = sys.exc_traceback.tb_frame
					while frame:
						print" from ", frame.f_code," at line no=",   frame.f_lineno
						frame = frame.f_back
					
			
				return	
				
			
				
			
		else:
			queries.append("""update v_basic_person set title='%(Title)s',  lastnames='%(Surnames)s', firstnames='%(Given Names)s',
						gender= '%(Gender)s',  dob='%(Dob)s', cob ='%(Cob)s' where id=%(id)d""" %personMap )

			
			queries.append("""update v_basic_address set number= '%(Street No)s',street= '%(Street)s',
			 street2='%(Address 1)s',  city=upper('%(City)s'),state=upper('%(State)s'), country='%(Country)s', 
			postcode='%(Postcode)s' where  id=%(id)d"""%addressMap) 

			
			
	
			#self.execute2("""select urb.id from urb, state, country c where urb.name=upper('%(City)s')
			#	 and urb.postcode='%(Postcode)s' and urb.statecode = state.id and trim(state.code)=upper('%(State)s') 
			#	and state.country = c.code and c.name = '%(Country)s' """%addressMap)
		
			#urbId = self.cursor.fetchone()[0]
		
			#self.execute2("select find_street( '%s', %d)" % ( addressMap['Street'], urbId )  )
			#streetId = self.cursor.fetchone()[0] 	

			#self.execute2("SELECT address_type.id FROM address_type WHERE (btrim((address_type.name)::text) = btrim(lower(('%s')::text)))"% ( addressMap['address At'] )  )	
			#addrtypeId = self.cursor.fetchone()[0]

			#self.execute2("select id_address from identities_addresses where id_identity = %d"%( self.personId))
			#addrId = self.cursor.fetchone()[0]

			#queries.append("update address set number='%s', street=%d, addrtype=%d ,addendum='%s' where id=%d" %
			#		(addressMap['Street No'], streetId, addrtypeId, addressMap['Address 1'], addrId) ) 
			
			#self.executeUpdate(queries)	
					

			
			try:
                                        db = self.getDB()
                                        db.commit()
                                        setup = self.getSqlSettings()
                                        cursor = db.cursor()
                                        for x in setup:
                                                print x
                                                cursor.execute(x)

                                        for x in queries:
                                                print x
                                                cursor.execute(x)

                                        db.commit()
                                        self.__person.reset()
                                        self.__address.reset()
                                        self.OnDataUpdate(None, self.personId) 

                        except Exception, errorStr:
                                        db.rollback()
                                        print "error in updating queries, ", errorStr






	def execute2(self, query):
		if self.cursor == None:
			cursor = self.getCursor()
		print "executing ",query 
		self.cursor.execute(query)

	def getDB(self):
		backend = gmPG.ConnectionPool()
                db = backend.GetConnection('default')
		return db

	def getSqlSettings(self):
		return ["set datestyle to european", "set transaction isolation level serializable"]

	
	def getName2(self, map):
		if map.has_key('name2'):
			return map['name2']
		return None
		
	
	def LowerMap( self, map, mapping):
			newMap = {}
			for i in mapping:
				print "in LowerMap checking", i
				y = self.getName2(i)
				if y == None:
					y = i['name'].lower()
				try:
					newMap[y] = map[ i['name'] ]
				except Exception , errorStr:
					print errorStr, 'in LowerMap in PersonDlg'
			print "lower case map = ", newMap
			return newMap

				
			 		

	def __GetPersonMapping(self):
		if self.personMapping == None:
			self.personMapping = [ { 'name': 'Given Names' , 'control': self.tcGivenNames, 'name2': 'firstnames'  } ,
					   {'name': 'Surnames', 'control': self.tcSurnames, 'name2': 'lastnames'   },
					   { 'name': 'Title', 'control' : self.comboTitle }, 
					   { 'name': 'Aka', 'control' : self.tcAka },
					   { 'name': 'PreferredName', 'control' : self.chPreferredName, 'op': self.getChoiceSelection },
					   { 'name': 'Gender' , 'control': self.chGender , 'op': self.getChoiceSelection },
					   { 'name': 'Dob' , 'control': self.tcDob },
					   { 'name': 'Cob' , 'control': self.cbCob }
					 ] 		
		return self.personMapping

	def __GetAddressMapping(self):
	        if self.addressMapping == None:
			self.addressMapping = [ 
						{ 'name' : 'address At' , 'control' :self. cbAddressAt , 'name2':'address_at'  }, 				
						{ 'name' : 'Address 1' , 'control' : self.tcAddress1 , 'name2':'street2' }, 				
						{ 'name' : 'Street No' , 'control' : self.tcStreetNo , 'name2':'number' }, 				
						{ 'name' : 'Street' , 'control' : self.tcStreet  }, 				
						{ 'name' : 'State', 'control' : self.tcState },
						{ 'name' : 'City' , 'control' : self.tcCity  }, 				
						{ 'name' : 'Country' , 'control' : self.chCountry , 'op': self.getCountryChoice },
						{ 'name' : 'Postcode', 'control': self.tcPostcode },
						{ 'name' : 'Phone For' , 'control' : self.cbPhoneFor},
						{ 'name' : 'Area Code' , 'control' : self.tcAreacode},
						{ 'name' : 'Phone number' , 'control' : self.tcPhonenumber},
						{ 'name' : 'Phone Comment' , 'control' : self.tcPhoneComment},
						{ 'name' : 'UrlCategory', 'control' : self.cbUrlCategory } ,
						{ 'name' : 'addr_id', 'control': 'addr_id' , 'op': self.getInvisible }
						
					    ]
		return self.addressMapping

	def getChoiceSelection(self, choice, value = None):
		"""sets and gets a wxChoice"""
		if (value != None) :
			choice.SetStringSelection(value)
		return choice.GetStringSelection()

	def getCountryChoice(self, choice, value = None):
		"""sets and gets a country choice."""
		if (value != None):
			for x in self.countriesAll:
				if (x[0] == value):
					choice.SetStringSelection(x[1])
		return choice.GetStringSelection()

	def getInvisible( self, name, value = None):
		"""sets and gets hidden attributes"""
		if (value != None):
			try:
				self.invisibleMap[name] = value
			except: 
				print "error in getInvisible", name, value
		return self.invisibleMap[name]

	def __GetMap(self, list):
		map = {}
		for x in list:
			try:
				map[x['name']] = x['control'].GetValue()
			except:
				try:
					map[x['name']] = x['op']( x['control'] ) 
				except Exception, errorStr:
					print "with ", x , errorStr

		
		return map

	def GetPersonMap(self):
		map =  self.__GetMap(self.__GetPersonMapping())
		map['id'] = self.personId
		return map

	def GetAddressMap(self):
		map =  self.__GetMap(self.__GetAddressMapping())	
		map['id' ] = self.addressId
		return map

		

	def OnDelete(self, evt):
		print evt.GetId()

	def OnUndo(self, evt):
		print evt.GetId()

	def SetPersonId(self, id):
		pass
	

	def ClearPersonData(self):
		self.comboTitle.SetSelection(0)
		self.tcGivenNames.Clear()
		self.tcSurnames.Clear()
		self.tcAka.Clear()
		self.chPreferredName.SetSelection(0)
		self.chGender.Clear()
		self.tcDob.Clear()
		self.cbCob.SetSelection(0)
		self.__setPersonId(None)		


	def ClearAddressData(self):
		#self.cbAddressAt.SetSelection(0)
		self.tcAddress1.Clear()
		self.tcStreetNo.Clear()
		self.tcStreet.Clear()
		self.tcCity.Clear()
		#self.chCountry.SetSelection(0)
		self.cbPhoneFor.SetSelection(0)
		self.tcAreacode.Clear()
		self.tcPhonenumber.Clear()
		self.tcPhoneComment.Clear()
		self.cbUrlCategory.SetSelection(0)
		self.tcURL.Clear()
		self.__setAddressId(None)


	def SetViaMapping( self, data, mapping):
		 """sets a control either through default SetValue, or via a supplied operation in x['op']
		 """

		 print "trying to set with data = ", data, " *** mapping = ", mapping
		 for x in mapping:
                        try:
                                ctrl = x['control']
                                if x.has_key('name2'):
                                        name = x['name2']
                                else:
                                        name = x['name'].lower()

				print "key for data  = ", name
                                  
                                if x.has_key('op'):
                                        x['op']( ctrl, data[name])
                                else:
                                        ctrl.SetValue( data[name].strip())
                        except Exception, errorStr:
                                print "error in setting  ", x ,errorStr
				t =  sys.exc_traceback
				print t.tb_lineno , t.tb_lasti


	def SetPersonData(self, person=None):
		if person is None:
			self.ClearPersonData()
			return
		
		mapping = self.__GetPersonMapping()

		self.SetViaMapping( person, mapping)
		self.__setPersonId(person['id'])

		#p = person
		#self.comboTitle.SetValue(p["title"])
		
		#self.tcGivenNames.SetValue(p["firstnames"])

		#self.tcSurnames.SetValue(p["lastnames"])
		#self.chPreferredName.SetStringSelection(p["preferred"])
		#self.tcAka.SetValue(p[])
		#self.chGender.SetStringSelection(p["gender"])
		#self.tcDob.SetValue(p["dob"])
		#self.cbCob.SetSelection(0)
		
		


	def SetAddressData(self, address=None):
		if address is None:
			self.ClearAddressData()
			return
		self.__setAddressId(address['id'])

		mapping = self.__GetAddressMapping()

		self.SetViaMapping( address, mapping)
		
		return


		a=address	#less typing ...
		self.cbAddressAt.SetSelection(a["adr_at"])
		self.tcAddress1.SetValue(a["street2"])
		self.tcStreetNo.SetValue(a["number"])
		self.tcStreet.SetValue(a["street"])
		self.tcCity.SetValue(a["city"])
		self.chCountry.SetStringSelection(a["country"])
		self.tcState.SetValue(a["state"])
		#self.cbPhoneFor.SetSelection()
		#self.tcAreacode.SetValue()
		#self.tcPhonenumber.SetValue()
		#self.tcPhoneComment.SetValue()
		#self.cbUrlCategory.SetSelection(0)
		#self.tcURL.SetValue()

	def ClearData(self):
		self.ClearPersonData()
		self.ClearAddressData()


	def OnDataUpdate(self, updater, id):
		#<DEBUG>
		print "On data update, Person ID =", id
		#</DEBUG>
		self.SetPersonData(self.__person.dictresult(id))
		addresslist = self.__person.addresses_link(id)
		if len(addresslist) > 0:
			print "address link list = ", addresslist
			homeaddress_link = addresslist[0]
			self.SetAddressData(self.__address.dictresult(homeaddress_link[0]))

	def OnSaveData(self, updateflag=0):
		if updateflag:
			pass
			#person attribute changed?
			#address attribute changed?
		else:
			pass
			#save person
			#save address








##########################################################################

if __name__ == "__main__":
	app = wxPyWidgetTester(size = (400, 500))
	app.SetWidget(PersonDetailsDlg, -1)
	app.MainLoop()
