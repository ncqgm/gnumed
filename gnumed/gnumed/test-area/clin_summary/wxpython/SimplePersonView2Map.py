

class SimplePersonView2Map:


	def __init__(self):

		self.list = [  { 'dbname':'firstnames', 'name': 'first name', 'format':"'%s'" },
				{'dbname':'lastnames', 'name': 'last name' , 'format':"'%s'"  },
				{'dbname':'dob', 'name': 'birthdate', 'format': "'%s'" },
				{'dbname':'gender', 'name': 'sex', 'size': 20, 'format': "'%1s'" },
				{'dbname':'street', 'name': 'address 1', 'size' : 200, 'format':"'%s'"  },
				{'dbname': 'addendum', 'name' : 'address 2', 'size': 200, 'format':"'%s'"  },
				{'dbname': 'phone1', 'name': 'phone ah' , 'size' :100, 'format':"'%s'"  }, 
				{'dbname': 'phone2', 'name': 'phone bh' , 'size' :100 , 'format':"'%s'" }, 
				{'dbname':'pupic', 'name': 'medicare no' , 'format':"'%s'"  }
				     ]

	def getBlankData(self, nametype = 'dbname'):
		list = []
		for x in self.list:
			list.append( {  'name': x[nametype], 'value': ' ' * 50} )
		return list

	def getFieldName( self, uiName):
		for x in self.list:
			if x['name'] == uiName :
				return x['dbname']
		return ''

	def getUIName( self, dbName):
		for x in self.list:
			if x['dbname'] == dbName: 
				return x['name']

	def getSize( self, uiName):
		for x in self.list:
			if x['name'] == uiName:		
				return x['size']
	
	def getEntries(self):
		list = self.list[:] 
		return list

	def mapKeysToFieldNames(self, map):
		print "trying to change map ", map
		newMap = {}
		for x in map.keys():
			try:
				newMap[self.getFieldName(x)] = map[x]
			except:
				print "unable to map", x
		return newMap

	
		
	def getFormat(self, dbName):
		for x in self.list:
			if x['dbname'] == dbName:
				return x['format']




