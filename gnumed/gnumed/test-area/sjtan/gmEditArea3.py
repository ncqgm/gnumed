"""This is a module for edit area testing. It lets one configure and construct serving tables or views
for an editarea. The drug screen is currently linked to drugref.org through views, and allows the drug field
to reference both generic drug field and drug classes;  selecting  a parent narrows the child selections;
the selection is activated by pressing enter in the combo box ; this is a limitation of the wxWindows event
macros. Note that drug_class is both a parent of generic and  drug,  but will only narrow generic initially.
There is a multiple parent check bug somewhere which slows down the processing when a selection is made.
Hopefully, fixable. Only started occuring when changed from many-to-one child-parent to many-to-many child-parent

Configuration for testing
.  Please load the drugref schema and drugref data into the target database , gnumed2 ( or change the backup_source default value below.
"""

from wxPython.wx import *
from pyPgSQL import PgSQL
import re
import sys
from traceback import *
import time

from gmBrowse2 import *
TBx = 1
CHBx = 2
RBn = 3
CMBx =4
LAB = 5

#this does make this module dependent on a lot of other modules
if __name__ == "__main__":
	sys.path.append ("../python-common/")
	sys.path.append ("../../client/python-common/")
import gmDateTimeInput
from gmDateTimeInput import *

GMDI = 6
PWh = 7

THRESHOLD_CHANGE = 3
COMBO_MAX_LIST= 60
COMBO_MAX_CACHE=4

sharedConnection = None

backup_dbapi = PgSQL 

backup_source = "localhost::gnumed3" 

re_table = re.compile("^create\s+(?P<type>table|view)\s+(?P<table>\w+)\s*.*", re.I)

def setSharedConnection( conn):
	sharedConnection = conn

def setBackupConnectionSource( dbapi = PgSQL , source = "localhost::gnumed"):
	backup_dbapi = dbapi
	backup_source = source

def getBackupConnection():
	return backup_dbapi.connect(backup_source)

def extractTablename(statement):
	re_obj = re_table.match( statement)
	return re_obj.group("table")

def extractType( statement):
	re_obj = re_table.match( statement)
	return re_obj.group("type")

def makeSet( list):
	set = []
	for x in list:
		if x in set:
			continue
		set.append(x)
	return set	

def getIndexMap( description):
	map = {}
	i = 0
	for x in description:
		x.append(i)
		map[x[0]] = x
		i += 1
	return map	

class SelectedIndexUpdater:
	def __init__(self, widgetName, editArea):
		self.widgetName = widgetName
		self.editArea = editArea
	
	def id_callback(self, id):
		table = self.editArea.getTableFromWidget(self.widgetName)
		self.editArea.selectedIndex[table] = id
		self.editArea.updateParentAndChildSelections(self.widgetName)
		print self, " GOT ID ", id
		
		
		

class EditArea2(wxPanel):
	"""A frills version for prototyping and programming more easily.
	"""

	def _getValidatedConnection(self):
		try:
			cu = self.sharedConnection.cursor()
			cu.execute("select 1")
			self.sharedConnection.commit()
			
		except:
			if self.connectionTry == 2:
				self.connectionTry = 0
				raise
			self.sharedConnection = getBackupConnection()
			
			self.connectionTry += 1
			return self._getValidatedConnection()
		self.connectionTry = 0
		return self.sharedConnection

	def __init__(self, parent, id):
		wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, style = wxNO_BORDER | wxTAB_TRAVERSAL)
		self.topSizer = wxFlexGridSizer(0, 1,0,0)
		self.topSizer. AddGrowableCol(0)
		self.lineSizer = wxBoxSizer(wxHORIZONTAL)
		self.nextId = 1
		self.rowItems = 0
		self.widgets= {}
		self.types = {}
		self.groups = {}
		self.mapping = {}
		self.statements = {}

		self.statementsList = []  # need this for ordered creation
		
		self.refs = {}
		self.comboCache = {}
		self.evictionPolicyFunction = None

		self.selectedIndex = {}
		self.connectionTry = 0
		self.sharedConnection = None

		self.tableToWidgetName = {}
		self.narrowOn= {}
		self.narrowFrom= {}
		self.oldText = ""
		self.disableTextChange = 0

		self.defaultFunctions = {}

		self.ext_refs = {}

		self.writeMapping = {}  # used when an initial value may be mapped as in drug.quantity to the prescription.quantity field, but the write must be for a different table

		self.descriptions = {} # for update and insert to check value types from dbapi cursor.description 

		self.targetId = None 

	def add(self, propName,  type=TBx ,weight=1,  displayName = None,  newline = 0):
		""" sets the default display Name to the property name,
		    capitalizes the display name,
		    creates the widget of the selected type, the default 
		    widget is a textbox,
		    adds the widget at the given weight, adjust if last
		    widget on line ( does this really do anything?),
		    add the line to the sizer if a newline and 
		    start a newline.
		    """

		if displayName == None:
			displayName = propName.capitalize()
			
			
		label = None
		if type == TBx:
			label =  wxStaticText(self, -1, displayName)
			widget = wxTextCtrl(self, -1 )

		if type == RBn:
			widget = wxRadioButton(self, -1, displayName)
		
		if type == CHBx:
			widget = wxCheckBox(self, -1, displayName)
			
		if type == CMBx:
			label= wxStaticText(self, -1, displayName)
			widget = wxComboBox(self, -1)
		
		if type == LAB:
			widget = wxStaticText(self, -1, displayName)

		if type == GMDI:
			label = wxStaticText(self, -1, displayName)
			widget = gmDateTimeInput.gmDateInput(parent = self,id = -1, size= wxDefaultSize, pos = wxDefaultPosition)

		if type == PWh:
			label = wxStaticText(self, -1, displayName)
			selector = SelectedIndexUpdater(propName,  self)
			print "making widget"
			widget = gmPhraseWheel.cPhraseWheel( parent = self, id = -1, size = wxDefaultSize, pos = wxDefaultPosition , id_callback = selector.id_callback)
			

		if label <> None:
			self.lineSizer.Add(label, 1, flag=wxALIGN_RIGHT)
		if newline and self.rowItems == 0:
			aproportion = 4
			aflag = wxEXPAND
		else:
			aproportion = weight 
			aflag =  wxALIGN_LEFT
		self.lineSizer.Add(widget, aproportion, aflag)
		self.rowItems += 1
		
		self.widgets[propName] = widget
		self.types[propName] = type
		widget.SetName(propName)

		if newline:
			self.topSizer.Add(self.lineSizer, flag= wxEXPAND)
			self.lineSizer = wxBoxSizer(wxHORIZONTAL)
			self.rowItems =0
	
	def addSizer(self, sizer):
		self.topSizer.Add( sizer)
			
	def finish(self):
		self._checkMappings()
		self._executeDDL()
		self._executeBrowseDDL()
		self.makeListControl(self)
		self.topSizer.Add(self.lineSizer, wxEXPAND)
		
		saverSizer = SaverSizer(self, -1) 
		saverSizer.setOkCommand( self.saveOrUpdate)
		saverSizer.setCancelCommand( self.clear)
		self.addSizer(saverSizer)
		
		self.topestSizer = wxFlexGridSizer( 2, 1  , 0, 0)
		#self.topestSizer.AddGrowableRow(0)
		self.topestSizer.Add( self.topSizer, wxEXPAND, 0)
		sizer = wxBoxSizer(wxHORIZONTAL)
		sizer.Add(self.listCtrl,1,  wxGROW | wxALL)
		self.listCtrl.SetAutoLayout(true)
		self.listCtrl.SetSizer(sizer)
		sizer.Fit(self.listCtrl)
		sizer.SetSizeHints(self.listCtrl)
			
		
		self.topestSizer.Add( sizer, wxEXPAND, 1)
		#self.listCtrl.SetSizer(self.topestSizer)
		#self.topestSizer.AddGrowableCol(1)
		self.SetAutoLayout(true)
	
		self.SetSizer(self.topestSizer)
		self.topestSizer.Fit(self)
		self.topestSizer.SetSizeHints(self)
		self.topestSizer.AddGrowableCol(0)
		self.topestSizer.AddGrowableRow(1)
		self.Layout()

		
		self._setDefaultText()

	def _setDefaultText(self):
		for w in self.defaultFunctions.keys():
			f = self.defaultFunctions[w]
			if f == None:
				continue
			self.getWidgetByName(w).SetValue(f())	

	def getBrowseSizer(self):
		#sizer = wxFlexGridSizer(1,0, 0, 0)
		#sizer.AddGrowableCol(0)
		#sizer2 = wxFlexGridSizer(1,0 , 0, 0)
		#sizer2.AddGrowableRow(0)
		self.listCtrl = self.getListControl(self)
		#sizer.Add( sizer2, wxEXPAND)
		#self.updateList()
	

	def _checkMappings(self):
		for k in self.mapping.keys():
			widgetType = self.getWidgetType(k)
			if widgetType == CMBx:
				self._linkComboBox(k)
			
	def _linkComboBox(self, key):
		widget = self.getWidgetByName(key)
		EVT_TEXT(widget, widget.GetId(), self._eventComboTextChanged)
		EVT_TEXT_ENTER( widget, widget.GetId(), self._eventComboTextEntered)
		EVT_COMBOBOX( widget, widget.GetId(), self._eventComboListSelected)


	def _executeDDL(self):
		cu = self.getConnection().cursor()
		self._execute_table_ddl(cu)
		self.getConnection().commit()
		self._execute_reference_ddl(cu)			
		self.getConnection().commit()
		self._execute_sequence_ddl(cu)	
		self.getConnection().commit()

	def _executeBrowseDDL(self):
		cu = self.getConnection().cursor()
		try:
			print "executing " , self.listViewStatement
			cu.execute(self.listViewStatement)
			self.getConnection().commit()
		except:
			print sys.exc_info()[0], sys.exc_info()[1]
			print_tb( sys.exc_info()[2])
			
		
	def _execute_table_ddl(self, cu):
		for x in self.statementsList:
			print x
			try:
				cu.execute(x)
				self.getConnection().commit()
			except:
				print sys.exc_info()[0], sys.exc_info()[1]
				print_tb( sys.exc_info()[2])

	def _execute_reference_ddl(self, cu):			
		for x in self.refs.values():
			print x
			try:
				cu.execute(x)
				self.getConnection().commit()
			except:
				print sys.exc_info()[0], sys.exc_info()[1]
				print_tb( sys.exc_info()[2])
				self._try_external_ref_ddl(cu, x)

	def _try_external_ref_ddl(self, cu, oldStatement):			
		list = oldStatement.split(" ")
		statement = " ".join(list[0:-2])
		try:
			print statement
			cu.execute(statement)
			self.getConnection().commit()
		except:
			print sys.exc_info()[0], sys.exc_info()[1]
			print_tb( sys.exc_info()[2])
			
					

	
	def _execute_sequence_ddl(self,cu):
		for x in self.statements.values():
			try:
				tableName = extractTablename(x)
				statement = "select max(id) from %s" % tableName
				#self.ref("drug", "generic")
				print statement
				cu.execute(statement)
				l = cu.fetchone()
				if l[0] == None:
					start = 1
				else:
					start = l[0] + 1
			
				statement = "create sequence %s_id_seq start %d" % ( tableName, start)
				print statement
				cu.execute(statement)
				statement = "alter table %s alter column id set default nextval('%s_id_seq')" % (tableName, tableName)
				print statement
				cu.execute(statement)
				self.getConnection().commit()
			except:
				print sys.exc_info()[0], sys.exc_info()[1]
				print_tb( sys.exc_info()[2])
				cu = self.getConnection().cursor()
			
			

	def getWidgetByName(self, name):
		"""yes, you can get back the widget by name !!"""
		if not self.widgets.has_key(name):
			return None
		return self.widgets[name]

	
	def getTableFromWidget(self, widgetName):
		return self.mapping.get(widgetName, ".").split('.')[0]	

	def getFieldFromWidget(self, widgetName):
		return self.mapping.get(widgetName, ".").split('.')[1]	

	def getWidgetType(self, name):
		if not self.widgets.has_key(name):
			return None
		return self.types[name]

	def getWidgetNameFromTable( self, tableName):
		return  self.tableToWidgetName[tableName][0]	

	def getWidgetNames(self):
		return self.widgets.keys()	

	def clear(self):
		for name, w in self.widgets.items():
			type = self.getWidgetType(name)
			if type == LAB:
				continue

			if type == CHBx or type == RBn:
				w.SetValue(0)
			else:
				w.SetValue('')
				if type == CMBx:
					w.Clear()
		self.targetId = None
		self._setDefaultText()
		self.selectedIndex = {}


	def ddl(self, key, statement):
		"""stores the creation statement for a table or view associated with the key"""
		self.statements[key] = statement
		self.statementsList.append(statement)
	
	def getTableType(self, key):
		statement= self.statements.get(key, "")
		return extractType(statement)

	def ref( self, key1, key2):
		"""adds sql  alteration statement for tables named in creation statements stored at key1 and key2.
		   The alteration adds a foreign key reference from table associated with key1 to table associated
		   with key2.
		   Note  only parent - child relationships where a child table has only one parent is allowed,
		   but parent can have many child relations, however, a parent can be a child of another table.
		"""   
		   
		statement1 = self.statements[key1]
		statement2 = self.statements.get(key2, "create table %s" % key2)
		tablename1 = extractTablename(statement1)
		tablename2 = extractTablename(statement2)
		if tablename1 == tablename2:
			return
		statement3 = "alter table %s add column id_%s integer references %s" % ( tablename1, tablename2, tablename2)

		self.refs["%s_%s_ref" %(tablename1, tablename2)]= statement3

		list = self.narrowOn.get(tablename1, [] )  #narrowOn stores child->parent
		list.append(tablename2)
		self.narrowOn[tablename1] = list

		list = self.narrowFrom.get(tablename2, []) #narrowFrom stores parent->child
		if not tablename1  in list:
			list.append(tablename1)
		self.narrowFrom[tablename2] = list
	
	def map( self, widgetName, sqlNames, order = 0, defaultFunction = None):
		if order == 1:
			self.writeMapping[widgetName] = sqlNames
			return
		self.mapping[widgetName] = sqlNames
		tableName = sqlNames.split('.')[0]
		self._addTableToWidgetMapping(  tableName, widgetName) 
		
		self.defaultFunctions[widgetName] = defaultFunction

		if self.getWidgetType(widgetName) == PWh:
			self._setPhraseWheelMatcher( widgetName, sqlNames)
			
	def _setPhraseWheelMatcher(self, widgetName, sqlNames):
		phraseWheel = self.getWidgetByName(widgetName)
		source_defs = []
		(tableName, fieldName ) = sqlNames.split('.')		
		source_defs.append(  { 'connectionProvider': self.getConnection , 'table': tableName, 'column': fieldName,
			'limit': COMBO_MAX_LIST, 'pk': 'id' , 'extraCondition': self._getNarrowings, 'extraConditionContext' : [tableName] } )
		matcher = gmPhraseWheel.cMatchProvider_SQL( source_defs, poolManager = None) 
		phraseWheel.setMatchProvider(matcher)
		
		


	def isWriteMapping( self, widgetName, field, target):
		"""determines if the target table and field matches the widget named, as a write mapping"""
		(table2, field2) = self.writeMapping.get(widgetName, ".").split(".")	
		return  table2 == target and field2 == field

	def _addTableToWidgetMapping(self, tableName, widgetName):	
		list = self.tableToWidgetName.get(tableName, [] )
		list.append(widgetName)
		self.tableToWidgetName[tableName] = list 
		
		
		
	def getConnection(self):
		return self._getValidatedConnection()

	def ext_ref(self, name1, name2):
		statement1 = self.statements[name1]
		tablename1 = extractTablename(statement1)
		statement  = "alter table %s add column id_%s integer" % (tablename1 , name2)
		self.refs['%s_%s_ref' % ( tablename1, name2)] = statement
		self.ext_refs[name1] = name2
		
		
	def findSelection(self, widgetName, text):
		"""finds a selection for this comboBox , based on a narrowing id from the parent comboBox if any,
		and also on any unnarrowed finds using the phras entered as a starting phrase
		. 
		returns  contents, a list of tuples in the format of dbapi cursor.fetchmaney()
		"""
		text = text.strip()
		
		cache = self._cacheAccess( widgetName, text)
		if cache <> None:
			return cache
		
		contents = self._selectList(widgetName, text)
			
		self._cacheContents(contents, widgetName, text)


		combo = self.getWidgetByName(widgetName)
		#self._doActionsForSingleSelections( combo)
			
		
		return contents

	def _selectList(self, widgetName, text):
		"""retrieve the selection via SQL  based on the text; the selection has a narrowed and unnarrowed part"""
		mapping = self.mapping[widgetName]
		sqlNames = mapping.split('.')
		statement0 = "select id, %s from %s where lower(%s) like '%s%%'"% ( sqlNames[1], sqlNames[0], sqlNames[1],  text.lower() )
		statement = "%s and %s" % ( statement0,  self._getNarrowings(sqlNames[0]) )
		print statement
		cu = self.getConnection().cursor()
		cu.execute(statement)
		
		contents = cu.fetchmany(COMBO_MAX_LIST)
		cu.close()
		self.getConnection().rollback()		
		print contents
		print "____"
		if len(text) > 0:
			self.addUnNarrowedFind( statement0, cu, contents)
		
		return contents

	
	def _cacheAccess(self, widgetName, text):
		cache = self.comboCache.get(widgetName, {}).get(text, None)
		if cache == None:
			return None
		
		return self._doCacheAccess(cache, text)
	
	def _doCacheAccess( self, cache, text):
		cache['access count']= cache.get('access count', 0) + 1
		cache['timestamp'] = int(time.time())
		return cache['contents']

	def _cacheContents( self, contents, widgetName, text):
		""" caches the contents , keyed on which widget, and what text was used to retrieve the contents"""
		# do the eviction before caching, otherwise ,if  using the least frequently used policy, 
		#it will evict the newly  cached contents .
		self._doCacheEvictionPolicy(widgetName)

		cache = {} 
		cache['contents'] = contents
		cache['access count'] = 1
		cache['timestamp'] = int(time.time())
		map =  self.comboCache.get(widgetName, {} ) 
		map[text] = cache
		self.comboCache[widgetName] = map

	def _doCacheEvictionPolicy(self, widgetName):
		if self.evictionPolicyFunction == None:
			self.evictionPolicyFunction = self._oldestCmp
			
		map =  self.comboCache.get(widgetName, {} ) 

		while len(map) > COMBO_MAX_CACHE:
			list = map.items()
			list.sort(self.evictionPolicyFunction)
		
			(text, cache) = list[0]
			print "evicting cache at ", text, " which has been accessed ", cache['access count'], " times"
			del map[text]
		
	
	def _accessCountCmp(self, pair1, pair2):
		"""for the least frequently used (LFU) cache eviction policy"""
		(text1, cache1) = pair1
		(text2, cache2) = pair2
		return cache1['access count'] - cache2['access count']

	def _oldestCmp(self, pair1, pair2):
		"""for the least recently used (LRU) cache eviction policy : who comes up with these catch phrases??"""
		(text1, cache1) = pair1
		(text2, cache2) = pair2
		return cache1['timestamp'] - cache2['timestamp']

	def addUnNarrowedFind(self, statement, cu, contents):
		map = {}
		keyList = []
		for x in contents:
			keyList.append(x[0])

		if len(contents) < COMBO_MAX_LIST:
			print statement
			cu = self.getConnection().cursor()
			cu.execute(statement)
			contents2 = cu.fetchmany(COMBO_MAX_LIST - len(contents) )
			cu.close()
			self.getConnection().rollback()		
			for x in contents2:
				if not  x[0] in keyList:
					contents.append(x)
		
		print contents	
		



	def _getParentTableListFromChild( self, childTableName):
		return  makeSet(self.narrowOn.get( childTableName, []) )

	
	def _getNarrowings(self,  childTableName):
		list = []
		for parentTableName in  self._getParentTableListFromChild(childTableName):
			widgetName = self.tableToWidgetName[parentTableName][0]
			id = self.selectedIndex.get(parentTableName, 0)
			print "for parent table", parentTableName, " , narrowing id = ", id
			if id == 0:
				continue 
			narrowing = "id_%s = %s" % ( parentTableName, id )
			if not narrowing in list:
				list.append(narrowing)
		if (list == []):
			return "true"
		return 	" and ".join(list)

	def _defaultComboPopulate( self, widgetName):
		"""private: handles the widget combo population"""
		if ( self.getWidgetType(widgetName) <> CMBx ):
			return
		combo = self.getWidgetByName(widgetName)
		text = combo.GetValue()
		selection = self.findSelection( widgetName, text)
		if selection == []:
			return
		if combo.GetSelection() <> -1:
			id = combo.GetClientData( combo.GetSelection())
			text = combo.GetString ( combo.GetSelection())
			combo.Clear()
			combo.Append( text, id)
			combo.SetSelection(0)
		else:	
			combo.Clear()
	#	self.disableTextChange = 1
		combo.Clear()
		for (id, name) in selection:
			combo.Append(name, id)
	#	self.disableTextChange = 0	
		
	def _eventComboTextChanged(self, event):
	#	if self.disableTextChange:
	#		return
		widget = event.GetEventObject()
		text = widget.GetValue()
		diff = abs(len(text) - len(self.oldText))
		if diff > THRESHOLD_CHANGE :
			self.oldText = text
		
			
	def _eventComboTextEntered( self, event):
		print "_eventComboTextEntered"
		widget = event.GetEventObject()
		self._actionForTextEntered(widget)	

	def _actionForTextEntered(self, widget):
		self._defaultComboPopulate(widget.GetName())
		if (widget.GetCount() == 1):
			print "firing select event because widget selection count is 1"
			self._doActionsForSingleSelections(widget)

	def _eventComboListSelected(self, event):
		print "_eventComboListSelected"
		combo = event.GetEventObject()
		print "event ", event , " received from ", combo
		self._doActionsForSingleSelections(combo)

	def _doActionsForSingleSelections(self, combo):
		if self.disableTextChange:
			self.disableTextChange = 0
			return
			
		self.setSelectedIndexToCurrentSelection( combo)	
		self.updateParentAndChildSelections(  combo.GetName())

	def updateParentAndChildSelections( self, widgetName):
		self._checkSameTableFields(widgetName)
		self._checkChildCaches(widgetName)
		self._checkParentText(widgetName)
		self._quietenDownPhraseWheelAnimals()

	
	def _checkSameTableFields(self, widgetName):
		table = self.getTableFromWidget(widgetName)
		self.updateWidgetsFromTarget(table ,  self.selectedIndex[table] )



		
	def setSelectedIndexToCurrentSelection(self, combo):	
		if combo.GetSelection() < 0:
			combo.SetSelection(0)
		table = self.getTableFromWidget( combo.GetName())	
		#self.selectedIndex[combo.GetName()] = combo.GetClientData(combo.GetSelection())
		self.selectedIndex[table] = combo.GetClientData(combo.GetSelection())
		print "index set to ", self.selectedIndex[table]

	def _checkChildCaches(self, parentWidgetName):
		"""checks the child caches, and repopulates on narrowing based on a selection  made in a parent widget."""
		parentTable = self.getTableFromWidget(parentWidgetName)
		list = self.narrowFrom.get(parentTable, [])
		#debug
		#print "child list for parent table = ", parentTable, " = ", list
		for childTable in  list:
			widgetName = self.tableToWidgetName.get(childTable,[None]) [0]
			if widgetName == None:
				continue
		#	if widgetName in self.comboCache:
		#		del self.comboCache[widgetName] 
		#	self.comboCache[widgetName] = {}

			# clear the blank cache, otherwise won't repopulate on new selection

			cache = self.comboCache.get(widgetName, {})    
			if cache.has_key(''):
				del cache['']

			#debug	
			#print "widget being checked = ", widgetName
			type =  self.getWidgetType(widgetName)

			if ( type == CMBx):
				widget =self.getWidgetByName(widgetName)
				#debug
				#print "clearing ", widget
				widget.Clear()
				widget.SetValue('')
			
				self.selectedIndex[childTable] = 0
				# re-populate based on parent narrowing
				self._defaultComboPopulate(widgetName)
			
			if (type == PWh):
				widget =self.getWidgetByName(widgetName)
				widget.SetValue('')

				
			
	def getParentWidgetNames( self, childWidgetName):
		list = []
		childTable = self.getTableFromWidget(childWidgetName)
		list2 = self._getParentTableListFromChild( childTable)
		for parentTable in  list2:
			list.append(self.tableToWidgetName.get(parentTable, [None])[0])
		return makeSet(list )

	def _checkParentText( self, childWidgetName):
		"""when a child widget text is selected, the parent widget text is changed to be the
		right parent for the selection ( this allows the unnarrowed selections to get an appropriate
		parent text display ).
		"""
		self.parentVisited = {}
		list =  self.getParentWidgetNames( childWidgetName)
		for parentWidgetName in  list:
			if parentWidgetName == None:
				continue
			self._checkOneParentText( childWidgetName, parentWidgetName)
	
		
	def _checkOneParentText( self, childWidgetName, parentWidgetName):
		parentTable = self.getTableFromWidget(parentWidgetName)
		if parentTable in self.parentVisited:
			return
		self.parentVisited[parentTable] = 1
		
		childTable = self.getTableFromWidget( childWidgetName)
		id = self.selectedIndex.get (childTable, None)

		if id == None:
			return
		print "parent widget=", parentWidgetName, "getFieldFromWidget", self.getFieldFromWidget(parentWidgetName)
		statement = "select parent.id , parent.%s from %s child, %s parent  where child.id = %s and parent.id = child.id_%s " % ( self.getFieldFromWidget(parentWidgetName),  childTable, parentTable ,id, parentTable)
		print statement
		cu = self.getConnection().cursor()
		cu.execute(statement)
		selection= cu.fetchall()
		cu.close()
		(parent_id, value)  = selection[0]
		combo = self.getWidgetByName( parentWidgetName)
		if combo.GetValue() <> value:
			combo.Clear()
			for ( parent_id, value) in selection:
				combo.Append(value, parent_id)
				print "setting parent ", combo, " with ", value
				combo.SetValue(value)
			#cascades check up parent widgets
			#? bug here, checkParentText instead of checkOneParentText
			self._checkParentText(parentWidgetName)
			


	def target(self, target):
		self.target = target
		#self.targets.append(target)
		
	
	def setExtRefId( self,name,  id):
		self.extRef[name] = id

	def setExtRef( self, name):
		self.extRef = name

	def setExtRefId( self, id):
		self.extRefId = id


	def browse(self, list):
		self.listViewStatement = self._createViewFromColumnList(list )
		self.listViewSelect = "select * from %s_list where id_%s = %%s" % ( self.target , self.extRef )

		self.columnList = list	

	
	def makeListControl(self, parent):
		self.listCtrl = BrowseListCtrl(parent)
		self.listCtrl.addListSelectionListener(self.changeTargetRow)
	

	def updateList(self):
		statement = self.listViewSelect % str(self.extRefId)
		print statement
		cu = self.getConnection().cursor()
		cu.execute(statement)
		print "after executing statement ", statement
		print "cursor description = ", cu.description
		self.listCtrl.update( self.listCtrl.convertColList(self.columnList), cu)
		
	
	
	def _parseColumn( self, list):
		columnMap = {}
		for (x, width) in list:
			(table, col) = x.split('.')
			columnMap[table] = { 'name': col, 'width' : width }
		return columnMap	


	def _createViewFromColumnList(self, colList ):

		"""from self.target being the main entity being edited, self.extRef the external container
		for the entity ( i.e. the topmost record type e.g. identity) 
		use the map of table.field:width to create a view for display and editing.
		The view will use the already configured references and entities to 
		create id references for the view."""
		colMap = self._parseColumn(colList)
		tables = colMap.keys()
		pairs = []
		for t in tables:
			list = []
			list.extend(tables)
			list.remove(t)
			refs = self.narrowOn.get(t, [])
			print "table = ", t, "self.narrowOn[t] = ", refs
			for r in refs:
				if r in list:
					pairs.append( (t, r))
	
		statement = [ 'create view %s_list as select distinct ' % self.target]

		attribs = []
		
		for (path, width)  in colList:
			attribs.append(path )
	
		# the external refs column
		for (t,r) in pairs:
			attribs.append('%s.id_%s' % (t, r) )
		
		self.view_refs = pairs

		# the id column
		attribs.append( '%s.id' % self.target)
			
		#for external identity
		l = []
		for (t, r) in pairs:
			if t in self.ext_refs.keys():
				l.append(t)
		
		attribs.append('%s.id_%s' % ( l[0], self.extRef) )
		
		statement.append( ', '.join(attribs) )
		statement.append(' from ')
		statement.append(', '.join(tables) )
		statement.append('where')
		condition = []
		for (t,r) in pairs:
			condition.append('%s.id_%s = %s.id' % (t,r,r) )



#		for t in self.ext_refs.keys():
#			if  t in l and self.ext_refs[t] == self.extRef:
#				condition.append('%s.id_%s = %s.id' % ( t, self.extRef, self.extRef ) )
		

		
		statement.append(' and '.join ( condition) )
		
		s = ' '.join(statement)

		print s

		self.browseColumnList = colList

		return s

	def _getTargetFields(self, target):
		print "mappings for target", self.mapping
		fields = []
		traceField = {}
		for (widgetName, v) in self.mapping.items():
			(table, field) = v.split('.')
			if table == target :
				fields.append( (field, self.getWidgetByName(widgetName)) )
				traceField[widgetName] = len(fields) -1

		print "write mappings are", self.writeMapping
		for (widgetName, v) in self.writeMapping.items():
			(table, field) = v.split('.')
			if self.isWriteMapping( widgetName, field,  target):
				print "appending write mapping", target, field, " for ", widgetName
				if widgetName in traceField:
					del fields[traceField[widgetName]]
				fields.append( (field, self.getWidgetByName(widgetName)) )
		return fields

	def _getReverseMapping(self):
		map = {}
		fieldTrace = {}
		for (widgetName, v) in self.mapping.items():
			(table,field) = v.split('.')
			fmap = map.get(table, {})
			fmap[field] = widgetName
			map[table] = fmap
			
			fieldTrace[field] = table

		#write mappings need to be overlayed
		print "write mappings are", self.writeMapping

		for widgetName in self.getWidgetNames():
			(table, field) = self.writeMapping.get(widgetName, ".").split(".")
			if (table ==""):
				continue
			key = fieldTrace.get(field, "")
			fieldMap = map.get(key, {})
			if field in fieldMap:
				del fieldMap[field]
			map[table][field] = widgetName
			

		
		return map

	def getDescription(self, target):
		description =  self.descriptions.get(target, None)
		if description == None:
			cu = self.getConnection().cursor()
			cu.execute("select * from %s where id = 1" % target)
			description = cu.description
			self.descriptions[target] = description
			cu.close()
		return description	
		
		

	def saveOrUpdate(self):
		print "saveOrUpdate: selectedIndex = ", self.selectedIndex
		if self.targetId == None:
			self.saveNew()
		else:
			self.updateTarget(self.target, self.targetId)	

		self.updateList()
		

	def saveNew(self):
		id = self.saveNewTarget( self.target)
		self.targetId = id


	def parseTargetFields(self,target, recursionCount,  visited):

		
		fields = self._getTargetFields(target)	
		print "_getTargetFields(fields) = ", fields
		
		fieldList = []
		valueList = []
		description = self.getDescription(target)
		indexMap = getIndexMap(description)
		
		for (f, w) in fields:

			fieldList.append(f)
			if not indexMap.has_key(f):
				continue
			print "checking ", indexMap[f][1]
			typestr = str(indexMap[f][1])
			if typestr in ['char', 'varchar','text','bpchar', 'timestamp'] :
				valueList.append("'%s'" % w.GetValue() )
				continue

			if typestr in ["bool", "boolean"]:
				if w.GetValue() == 0:
					v = "'f'"
				else:	
					v = "'t'"
				valueList.append(v)
				continue


			if w.GetValue().strip() == "":
				fieldList.pop()
				continue

			valueList.append("%s" % w.GetValue() )



			

		print "after PARSING \n", fieldList, valueList	

		refList = self.narrowOn.get(target ,[] )
		#print "refList for ", target, " = ", refList

		#set any references, check for unsaved referenced rows.
		for r in refList:
			widgetName = self.getWidgetNameFromTable(r) 

			if not  self.selectedIndex.has_key(r): # cascade saveNewTarget to unsaved row in referenced table
				if (r in visited):
					print "has already been visited=", r
					continue
				visited.append(target)
				#recurse into unsaved referenced row
				id = self.saveNewTarget( r, recursionCount + 1, visited)
				self.selectedIndex[r] = id
			else:
				
			# will need to distinguish readonly references from updateable references
				print "updating ", r, widgetName
				if self.getTableType( self.mapping[widgetName].split(".")[0]).lower() == "table":
					self.updateTarget( r, recursionCount + 1, visited)
				pass
			fieldList.append('id_%s' % r)
			valueList.append( "%d"  % self.selectedIndex[r] )
			
		# set any top container reference	
		#for extRef in self.ext_refs.get(target, []):     # use this later when can do multiple external refs.
		extRef  =  self.ext_refs.get(target, None)
		if extRef <> None:	
			if extRef == self.extRef and not self.extRefId == None:
				fieldList.append('id_%s' % extRef)
				valueList.append('%d' % self.extRefId  )
			
		return (fieldList, valueList)	

	
	def saveNewTarget(self, target, recursionCount = 0, visited = []  ):
		"""will save a row for a table and cascades  save up any referenced tables by recursion, and make
		save for all rows as one transaction."""
		  
		print "save new target", target

		(fieldList, valueList) = self.parseTargetFields( target, recursionCount, visited)			
	
		
		# two stage insert using backend assigned primary key values. Get the next sequence value, and store it on client side first, then
		# insert the row with the id value.  I've tried using the one stage insert and using the default
		# sql assignment of the primary key, but then a select is needed using the other value fields as a 
		# alternate composite candidate key to find the primary key value assigned, and that's pretty clumsy.

		cu = self.getConnection().cursor()

		idStatement = "select nextval('%s_id_seq')" % target

		cu.execute(idStatement)
		
		[id] = cu.fetchone()
		
		print "next id ", id
		
		
		statement  = "insert into %s (id,  %s) values (%d, %s)" % ( target, ", ".join(fieldList), id, ", ".join(valueList)  ) 
		print statement

		cu.execute(statement)
		

		if  recursionCount == 0:
			self.getConnection().commit()
		
	
		return id
		
	def updateTarget(self, target,   recursionCount = 0, visited = [] ):
		(fieldList, valueList) = self.parseTargetFields( target, recursionCount, visited)
		list = []
		for i in xrange(0, len(fieldList)):
			if fieldList[i] == 'id':
				valueList[i] = self.selectedIndex[target]
			list.append( ' %s = %s' % (fieldList[i], valueList[i]) )
			
		statement = "update %s 	set %s where id = %d" % (target, ', '.join(list), self.selectedIndex[target])
		print statement

		cu = self.getConnection().cursor()
		cu.execute(statement)
		
		if recursionCount == 0:
			self.getConnection().commit()
			
	
	def changeTargetRow( self, event):
		self.clear()
		#self._editLoadStrategy1(event)
		self._editLoadStrategy2(event)
		
		self._quietenDownPhraseWheelAnimals()
		
		
	def _quietenDownPhraseWheelAnimals(self):
		names = self.getWidgetNames()
		for name in names:
			if self.getWidgetType(name) == PWh :
				self.getWidgetByName(name).setUserInputChanging(0)

		
		

	def _editLoadStrategy2(self, event):
		"""load using the id and foreign key ids stored with row of the view ; 
			pro: more thorough and up to date, and doesn't rely on all the information being in the view  ; 

			con: view needs at least id information; will access server a few times in order to retrieve 
			each table row as it follows references ; won't update whole editarea if any displayed information
			isn't connected via a reference path to the root target table; absolutely depends on naming
			of references as id_xxxxx where xxxx is the correct spelling of the referenced table"""
		tuple = self.listCtrl.getRow(event.GetIndex())
		d = self.listCtrl.description
		indexMap = getIndexMap(d)
		id = tuple[indexMap['id'][-1]]
		self.updateWidgetsFromTarget(self.target ,  id , [ self._getExtRefCondition() ])
		self.targetId = id
	

	def updateWidgetsFromTarget(self, target, id, extra_conditions = [] ):
	 	"""recursively update widgets, following 'id_'... fields as references"""

		conditions = [ "id = %d" %  id ]
		conditions.extend ( extra_conditions)
		
		cu = self.getConnection().cursor()
		cu.execute("select * from %s where  %s" % (target, " and ".join(conditions) )  )

		row = cu.fetchone()


		rMap = self._getReverseMapping()
		print "reverse mapping = ", rMap
		fieldWidgetMap = rMap.get(target, {})
		self._updateWidgetsFromRow( fieldWidgetMap, cu.description , row)

		indexMap = getIndexMap( cu.description)

		print "target ", target, " ID = ", id
		self.selectedIndex[target] =  id


		for k in indexMap.keys():
			print "checking keys " ,k , " has id in front ? ", k[0:3] == 'id_'
			if k[0:3] == 'id_':
				try:
					target = k[3:]
				#	if target == self.extRef:
				#		external_condition = self._getExtRefCondition()
				#		id = None
					id =  row[indexMap[k][-1]]
					self.updateWidgetsFromTarget( target, id, [])
				except:
					print sys.exc_info()[0], sys.exc_info()[1]
					print_tb( sys.exc_info()[2]) 
					
			
	def _updateWidgetsFromRow(self, fieldWidgetMap, description, row):
		indexMap = getIndexMap( description)
		for (f, widgetName) in fieldWidgetMap.items():
			i  = indexMap.get(f, [None])[-1]
			if i  == None:
				continue
			fieldInfo =  indexMap.get(f, None)
			if (str(fieldInfo[1]) == 'timestamp'):
				try:
					value = time.strftime('%x', time.localtime(row[i]) )
				except:
					value = str(row[i])
				
			elif (str(fieldInfo[1]) in [ 'bool', 'boolean'] ):
				if  str(row[i])[0] in ['1', 't']:
					value = 1
				else:
					value = 0
			else:
				if row[i] == None:
					value = ""
				else:
					value = str(row[i])

			
			w = self.getWidgetByName(widgetName)
			w.SetValue(value)
			#if self.getWidgetType(widgetName) == CMBx:
			#	self._actionForTextEntered(w)
				
				
				
			
			
			

	def _getExtRefCondition(self):
		return " id_%s = %d" % ( self.extRef, self.extRefId)
		
		

		

	def _editLoadStrategy1(self, event):	
		tuple = self.listCtrl.getRow(event.GetIndex())
		targetFields = {}

		i = 0
		for (fieldpath, width) in self.browseColumnList:
			(table, field) = fieldpath.split('.')
			fieldMappings= targetFields.get( table, self._getTargetFields( table) )
			targetFields[table] = fieldMappings
			for (f, w) in fieldMappings:
				if f == field:
					type = self.getWidgetType(w.GetName() )

					if type == CHBx or type == RBn:
						print f, str(tuple[i])
						w.SetValue(str(tuple[i]) == "t" )

					else:	
						w.SetValue(str(tuple[i]))
						print "type of ", w, " = ", type
						if (type == CMBx):
							print "doing actionForTextEntered"
							self._actionForTextEntered(w)
					break
				
			i += 1
		
		for (t, r) in self.view_refs:
			widgetName = self.getWidgetNameFromTable(r)
			#self.selectedIndex[widgetName] = tuple[i]
			self.selectedIndex[r] = tuple[i]
			i += 1
			

		self.targetId = tuple[i]
	
			
				
			
		
		

	def now(self):
		"""used to return default value for date widgets."""
		return time.strftime('%x')
			
		

	

class SaverSizer(wxFlexGridSizer):
	def __init__(self, parent,  id):
		#wxPanel.__init__(self, parent, id, wxDefaultPosition, wxDefaultSize, style = wxNO_BORDER | wxTAB_TRAVERSAL)
		wxFlexGridSizer.__init__(self, 1, 0, 0, 0)

		self.AddGrowableRow(0)
	#	self.topSizer = wxBoxSizer(wxHORIZONTAL)
		self.okButton = wxButton(  parent, -1, "OK")
		self.cancelButton = wxButton( parent, -1 , "CANCEL")
		self.Add(self.okButton, wxEXPAND)
		self.Add(self.cancelButton, wxEXPAND)
		#self.SetAutoLayout(true)
		self.okCommand = self.printOk
		
		EVT_BUTTON( self.okButton, self.okButton.GetId(), self.doOkCommand)
		EVT_BUTTON( self.cancelButton, self.cancelButton.GetId(), self.doCancelCommand)


	def printOk(self):
		print "ok"

	def setOkCommand(self, command):
		self.okCommand = command
		print "self.okCommand = ", command

	def setCancelCommand(self, command):
		self.cancelCommand = command


	def doOkCommand(self, event):
		print event
		self.okCommand()
		

	def doCancelCommand(self, event):
		self.cancelCommand()

		
		
		
class MedicationEditArea(EditArea2):
	
	def __init__(self, parent, id):
		EditArea2.__init__(self, parent, id)
		self.add("classes", CMBx, newline = 1)
		self.add("generic", PWh, weight = 3)
		self.add("veteran", CHBx,newline=1)
		self.add("drug", PWh,  weight = 3)
		self.add("reg 24", CHBx, newline=1)
		self.add("quantity", CMBx)
		self.add("repeats",  newline=1)
		self.add("direction", weight = 3, newline=1)
		self.add("for", PWh, weight = 5, newline = 1)
		self.add("date", GMDI)
		self.add("usual", CHBx, newline=1)
		self.add("progress notes", weight = 6, newline = 1)
	
		self.ddl("identity", "create table identity( id integer primary key, name text)")
		

		self.ddl("classes", 
		"create VIEW drug_classes AS SELECT dc.id , atc.text as description from drug_class dc, atc,  link_drug_atc la where la.atccode=atc.code and la.id_drug = dc.id")
		self.map("classes", "drug_classes.description")
		self.ddl("generic", "create VIEW generic as SELECT distinct gdn.id_drug as id, gdn.name, ldc.id_class as id_drug_classes  from generic_drug_name gdn, link_drug_class ldc where ldc.id_drug =  gdn.id_drug")
		self.ref("generic","classes")
		self.map("generic", "generic.name")
		

		self.ddl("drug","create VIEW drug as SELECT  distinct on (lpm.id_product) lpm.id_product as id, lpm.brandname || ' ' || p.comment  as name, ldc.id_class as id_drug_classes, ldc.id_drug as id_generic from link_product_manufacturer lpm, product p, link_drug_class ldc where lpm.id_product = p.id and p.id_drug = ldc.id_drug order by lpm.id_product, name")
		
		self.ref("drug", "classes")
		self.ref("drug", "generic")
		self.map("drug", "drug.name")


#		self.ddl("atc", "create view atc_view as select  lda.id_drug as id, atc.code, atc.text as name from atc , link_drug_atc lda where lda.atccode=atc.code")
		self.ddl("package", "create view package as SELECT pz.id_product as id , text(pz.size) as quantity, pz.id_product as id_drug from package_size pz")
		self.ref("package", "drug")

		self.map("quantity", "package.quantity", order=0)
		self.ddl("prescription", "create table prescription(id integer primary key, quantity integer, repeats integer, for_condition text, direction text,  date timestamp default now(), veteran bool, usual bool , reg_24 bool)")
		self.map("date", "prescription.date", defaultFunction = self.now )
		self.map("quantity", "prescription.quantity", order = 1)
		self.map("repeats", "prescription.repeats")
		
		self.ref("prescription", "drug")

		self.ddl("progress_notes","create table progress_notes( id integer primary key, text text)")

		self.ref("prescription", "progress_notes")
		self.map("progress notes", "progress_notes.text")
	
		self.map("veteran", "prescription.veteran")
		self.map("reg 24", "prescription.reg_24")
		self.map("direction", "prescription.direction")
		self.map("for", "disease_code.description", order = 0)
		self.map("for", "prescription.for_condition", order = 1)
		self.map("usual", "prescription.usual")

		self.ext_ref("prescription", "identity")
		self.ext_ref("progress_notes","identity")

		self.setExtRef( "identity")

		self.target("prescription")

		self.browse( [ ("drug.name",180 ),  ( "prescription.direction", 60), ("prescription.quantity", 60) , ( "prescription.repeats",60 ) , ( "prescription.date", 90) , ("prescription.veteran" , 20 )  ])

		
		self.finish()
		# for testing
		self.setExtRefId(1)
		self.updateList()



class PastHistoryEditArea(EditArea2):
	def __init__(self, parent, id):
		EditArea2.__init__(self, parent, id)
		#self.add("coding system", CMBx, newline = 1)
		self.add("condition", PWh, weight = 3,  newline  = 1 )
		self.add("laterality", LAB)
		self.add("left",  RBn)
		self.add("right", RBn)
		self.add("both",  RBn, newline = 1)
		self.add("notes",  newline = 1)
		self.add("age onset" )
		self.add("year onset",  newline = 1)
		self.add("active", CHBx)
		self.add("operation", CHBx)
		self.add("confidential", CHBx)
		self.add("significant", CHBx, newline = 1)

		self.ddl("condition", "create view condition as select distinct id, description , code from disease_code")
		self.map("condition", "condition.description")
		self.ddl("past_history", "create table past_history( id integer primary key, aleft boolean, aright boolean, aboth boolean, notes text, age_onset integer, year_onset integer, active boolean, operation boolean, confidential boolean, significant boolean )")
		self.map("left", "past_history.aleft")
		self.map("right", "past_history.aright")
		self.map("both", "past_history.aboth")
		self.map("notes", "past_history.notes")
		self.map("age onset", "past_history.age_onset")
		self.map("year onset", "past_history.year_onset")
		self.map("active", "past_history.active")
		self.map("operation", "past_history.operation")
		self.map("confidential", "past_history.confidential")
		self.map("significant", "past_history.significant")
		self.ref("past_history", "condition")
		self.ext_ref("past_history", "identity")
		self.setExtRef( "identity")
		self.target("past_history")
		self.browse([ ( "past_history.year_onset" , 60), ("past_history.age_onset", 60), ("condition.description", 200) , ("past_history.aleft", 20), ( "past_history.aright", 20) , ("past_history.aboth", 20) , ("past_history.active", 20), ("past_history.notes", 200 ) ] )
		
		self.finish()
		# for testing
		self.setExtRefId(1)
		self.updateList()

					    


class RecallEditArea(EditArea2):
	def __init__(self, parent, id):
		EditArea2.__init__(self, parent, id)
		self.add("to see", newline = 1)
		self.add("recall for", newline =1 )
		self.add("date", newline = 1)
		self.add("contact by", CMBx, weight=1)
		self.add("appointment type", newline = 1, weight = 2)
		self.add("include", CMBx , weight = 1)
		self.add("for", newline=1, weight = 2)
		self.add("instructions", newline = 1)
		self.add("progress notes", newline = 1)
	#	self.group("recall servicer", ["to see"] )
	#	self.group("recall", ["recall for", "date", "contact by", "appointment type", "for", "instructions"] )
	#	self.group("recall investigation", ["include"] )
	#	self.group("progress notes", ["progress notes"] )
		
		self.finish()
		
class ReferralEditArea(EditArea2):
	def __init__(self, parent, id):
		"""initializes the ui.
		   The behaviour 
		   1)is select ref_person where ref_person.name =  pers category OR
		   	select category where category.name = pers category
		   1.1) on select person, fill person.name in name; fill person.use_firstname in name
		   2) on name focue exit, set restriction on organization as select organization.name  (display), organization.id( hidden key)  where person_org_link.person_id = person.id and person_org_link.org_id= organization.id 
		   3) on  organization focus exit, validate organization.id exists, 
		   4) on orgsnization select 
		   """
		EditArea2.__init__(self, parent, id)
		self.add("pers category", newline = 1)
		self.add("name", weight = 3)
		self.add("use firstname", CHBx, newline=1)
		self.add("organization", weight = 3)
		self.add("head office", CHBx, newline = 1)
		self.add("street1", weight=2)
		self.add("w phone", newline = 1)
		self.add("street2", weight=2)
		self.add("w fax", newline=1)
		self.add("street3", weight=2)
		self.add("w email", newline=1)
		self.add("suburb", weight=2)
		self.add("postcode", newline=1)
		self.add("for", newline=1)
		self.add("include", LAB)
		self.add("medications", CHBx)
		self.add("social history", CHBx)
		self.add("family history", CHBx, newline = 1)
		self.add("", LAB)
		self.add("past problems", CHBx)
		self.add("active problems", CHBx)
		self.add("habits", CHBx, newline = 1)
		self.finish()

	#	self.group("selector", ["pers category"])
	#	self.group("consultant", ["name", "use firstname"])

	#	self.group("organization", ["organization"])
	#	self.group("head office", ["head office"])
	#	self.group("address", ["street1", "street2", "street3", "suburb", "postcode"] )
	#	self.group("comm", ["w phone", "w fax", "w email"] )
	#	self.group("referral", ["for", "medications", "social history", "family history", "past problems", "active problems", "habits" ] )
			

class RequestEditArea(EditArea2):
	def __init__(self, parent, id):
		EditArea2.__init__(self, parent, id)
		self.add("type", newline =1 )
		self.add("company", newline = 1)
		self.add("street", newline = 1)
		self.add("suburb", weight = 2)
		self.add("phone", weight = 2,newline = 1)
		self.add("request", newline = 1)
		self.add("notes on form", newline = 1)
		self.add("medications", weight=3)
		self.add("include all meds", CHBx, newline = 1)
		self.add("copy to", newline = 1)
		self.add("progress notes", newline = 1)
		self.add("billing", LAB)
		self.add("bulk bill", RBn)
		self.add("private", RBn)
		self.add("rebate", RBn)
		self.add("wcover", RBn, newline = 1)
		self.add("", LAB)
		self.finish()

class VaccinationEditArea(EditArea2):
	def __init__(self, parent, id):
		EditArea2.__init__(self, parent, id)
		self.add("target disease", CMBx, weight = 2)
		self.add("schedule age", CMBx,  newline = 1)
		self.add("vaccine", CMBx, newline = 1)
		self.add("date given", newline = 1)
		self.add("serial no", newline = 1)
		self.add("route", CMBx)
		self.add("site injected", CMBx)
		self.finish()

class AllergyEditArea(EditArea2):
	def __init__(self, parent, id):
		EditArea2.__init__(self, parent, id)
		self.add("date", newline = 1)
		self.add("drug", CMBx, newline = 1)
		self.add("class", newline = 1)
		self.add("reaction", CMBx, newline = 1)
		self.add("specificity", CMBx)
		self.add("definite", CHBx)
		self.add("reaction", RBn)
		self.add("sensitivity", RBn, newline = 1)
		self.finish()


class DemographicEditArea(EditArea2):
	def __init__(self, parent, id):
		EditArea2.__init__(self, parent, id)

		#need to have the ability for one-to-many relationships , in order to use current gnumed names table.


		self.add("first names",  newline = 1)
		self.add("last names" )
		self.add("title", newline = 1)
		self.add("birthdate")
		self.add("sex", newline =1 )
	#	self.add("family", CMBx, newline = 1)
	#	self.add("place", CMBx, newline = 1)
		
		self.add("street 1")
		self.add("street 2", newline=1)
		self.add("suburb", CMBx, newline = 1)
		self.add("state", CMBx)
		self.add("postcode", CMBx, newline = 1)

		self.add("home tel.")
		self.add("work tel.", newline = 1)

		self.add("medicare no")
		self.add("DVA no", newline = 1)
		self.add("health insurance no" )
		self.add("ins.company", newline = 1)

		self.ddl("alt_names", "create table alt_names (id integer primary key,  firstnames varchar(250), lastnames varchar(250), title varchar(10) )")
		self.map("first names", "alt_names.firstnames")
		self.map("last names", "alt_names.lastnames")
		self.map("title", "alt_names.title")
	
		self.ddl("demographic", "create table demographic( id integer primary key, birthdate timestamp, sex varchar(10) )")
		self.map("birthdate", "demographic.birthdate")
		self.map("sex", "demographic.sex")
	
		self.ddl("social_id", "create table social_id( id integer primary key, medicare_no varchar(30), dva_no varchar(30), health_ins varchar(30), company varchar(40)) ")
		self.ddl("alt_address", "create table alt_address( id integer primary key,street1 varchar(100), street2 varchar(100))")
		
		self.ddl("alt_tel", "create table alt_tel( id integer primary key, home varchar(20), work varchar(20) )")	
		self.map("street 1", "alt_address.street1")
		self.map("street 2", "alt_address.street2")
		
		self.ddl("alt_urb", "create view alt_urb as select id, name as urb_name, postcode,  id_state from urb")
		
		self.ref("alt_address", "alt_urb")
		self.map("suburb", "alt_urb.urb_name")
		self.map("state", "state.name")
		self.ref("alt_urb", "state")
		self.map("postcode", "alt_urb.postcode")

		self.map("home tel.", "alt_tel.home")
		self.map("work tel.", "alt_tel.work")
		
		self.map("medicare no", "social_id.medicare_no")
		self.map("DVA no", "social_id.dva_no")
		self.map("health insurance no", "social_id.health_ins")
		self.map("ins.company", "social_id.company")

		self.ref("demographic", "alt_address")
		self.ref("demographic", "alt_names")
		self.ref("demographic", "social_id")
		self.ref("demographic", "alt_tel")

		self.ext_ref("demographic", "practice")
		self.setExtRef("practice")
		self.target("demographic")

		self.browse( [ ("alt_names.lastnames", 150) , ("alt_names.firstnames", 150) , ("demographic.birthdate", 90), ("demographic.sex", 50), ("alt_address.street1", 200) , ("alt_urb.urb_name", 120), ("state.name", 100) , ("alt_urb.postcode",90 ) ] )
		self.setExtRef("practice")

		self.setExtRefId(1)
		self.finish()
		self.updateList()
		
		


if __name__=="__main__":
	setBackupConnectionSource()

	print "sys.argv[1] == ", sys.argv[len(sys.argv) -1]


	if sys.argv[len(sys.argv) -1] == 'past':
		app = wxPyWidgetTester(size=(500,300) )
		app.SetWidget( PastHistoryEditArea, -1)
		app.MainLoop()

	if sys.argv[len(sys.argv) -1] == 'iden':
		app = wxPyWidgetTester( size=(500, 200) )
		app.SetWidget( DemographicEditArea, -1)
		app.MainLoop()

	app = wxPyWidgetTester(size=(500,300) )
	app.SetWidget( MedicationEditArea, -1)
	app.MainLoop()
	
	
	app = wxPyWidgetTester( size=(500, 300) )
	app.SetWidget( RecallEditArea, -1)
	app.MainLoop()

	
	app = wxPyWidgetTester( size=(500, 300) )
	app.SetWidget( ReferralEditArea, -1)
	app.MainLoop()
	
	app = wxPyWidgetTester( size=(500, 300) )
	app.SetWidget( RequestEditArea, -1)
	app.MainLoop()
	
		
	app = wxPyWidgetTester( size=(500, 200) )
	app.SetWidget( VaccinationEditArea, -1)
	app.MainLoop()

	app = wxPyWidgetTester( size=(500, 200) )
	app.SetWidget( AllergyEditArea, -1)
	app.MainLoop()
			

	
		

	

		

