

""" helper class for translating names in a table as a list of  maps with keys  dbname, name, size, format """

class SimpleDefaultNameMapper:
	mapper = None
	def getMapper():
		if SimpleDefaultNameMapper.mapper == None:
			SimpleDefaultNameMapper.mapper = SimpleDefaultNameMapper()
		return SimpleDefaultNameMapper.mapper

	def getFieldName( self, uiName, list):
		for x in list:
			if x['name'] == uiName :
				return x['dbname']
		return ''

	def getUIName( self, dbName, list):
		for x in list:
			if x['dbname'] == dbName: 
				return x['name']

	def getSize( self, uiName, list):
		for x in list:
			if x['name'] == uiName:		
				return x['size']
	
	def copyId(self, newMap, map):
                try:
                        newMap['id'] = map['id']
                except:
			try:
				newMap['id'] = map['patient_id']
			except:
				print "no id(id of patient) found "

	def copyClinId(self, newMap, map):
		try:
                        newMap['clin_id'] = map['clin_id']
                except:
                        print "no clin_id(id of record)  found "


## """get map of uiNames to values, and returns a map of dbNames to values """

	def mapKeysToFieldNames(self, map , list):
		print "trying to change map ", map, " with list ", list
		newMap = {}
		
		for x in map.keys():
			try:
				newMap[self.getFieldName(x, list)] = map[x]
			except Exception , errorStr:
				print "unable to map", x , " b/c ", errorStr

		self.copyId(newMap, map)
		self.copyClinId(newMap, map)	
		print "new map is now ", newMap
		return newMap

	def mapKeysToDialogNames(self, map, list):
		newMap = {}
		for x in map.keys():
			try:
				dialogName = self.getUIName(x, list)
				newMap[dialogName] = map[x]	
			except:
				print "unable to map", x
		self.copyId(newMap, map)
                self.copyClinId(newMap, map)
                print "new dialog map is now ", newMap
                return newMap

			

	def createMap( self, labels, list):
		i = 0
		map = {}
		for x in labels:
			map[x] = list[i]
			i = i + 1
		return map

		
		
	def getFormat(self, dbName, list):
		for x in list:
			if x['dbname'] == dbName:
				return x['format']


	def createSimpleDialogData(self, entries, dbNameMap):
		uiList = []

                for x  in entries :
			entry = {}
			for y in x.keys():
				try:
					entry[y] = x[y]
				except:
					print "unable to map ", y, " into entry"

                        try:
                                entry['value'] = dbNameMap[x['dbname']]
                        except:
                                print 'no value for ', name, 'has dbname ', x['dbname']
                                pass

                        uiList.append(entry)

                print "before", uiList
		return uiList


