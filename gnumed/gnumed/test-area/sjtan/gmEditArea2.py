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
TBx = 1
CHBx = 2
RBn = 3
CMBx =4
LAB = 5

THRESHOLD_CHANGE = 3
COMBO_MAX_LIST= 40

sharedConnection = None

backup_dbapi = PgSQL 

backup_source = "localhost::gnumed2" 

re_table = re.compile("^create\s+(table|view)\s+(?P<table>\w+)\s*.*", re.I)

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

def makeSet( list):
	set = []
	for x in list:
		if x in set:
			continue
		set.append(x)
	return set	
	

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
		self.refs = {}
		self.comboCache = {}
		self.selectedIndex = {}
		self.connectionTry = 0
		self.sharedConnection = None

		self.tableToWidgetName = {}
		self.narrowOn= {}
		self.narrowFrom= {}
		self.oldText = ""
		self.disableTextChange = 0

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
			
	def finish(self):
		self.topSizer.Add(self.lineSizer, wxEXPAND)
		self.SetSizer(self.topSizer)
		self.topSizer.Fit(self)
		self.SetAutoLayout(true)
		
		self._checkMappings()

		self._executeDDL()

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
		
	def _execute_table_ddl(self, cu):
		for x in self.statements.values():
			print x
			try:
				cu.execute(x)
				self.getConnection().commit()
			except:
				print sys.exc_info()[0], sys.exc_info()[2]
				print_tb( sys.exc_info()[2])

	def _execute_reference_ddl(self, cu):			
		for x in self.refs.values():
			print x
			try:
				cu.execute(x)
			except:
				print sys.exc_info()[0], sys.exc_info()[1]
				print_tb( sys.exc_info()[2])
	
	def _execute_sequence_ddl(self,cu):
		for x in self.statements.values():
			try:
				tableName = extractTablename(x)
				statement = "select max(id) from %s" % tableName
				self.ref("drug", "generic")
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
			except:
				print sys.exc_info()[0], sys.exc_info()[1]
				print_tb( sys.exc_info()[2])
			
			

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


	def getWidgetNames(self):
		return self.widgets.keys()	


	def ddl(self, key, statement):
		"""stores the creation statement for a table or view associated with the key"""
		self.statements[key] = statement

	def ref( self, key1, key2):
		"""adds sql  alteration statement for tables named in creation statements stored at key1 and key2.
		   The alteration adds a foreign key reference from table associated with key1 to table associated
		   with key2.
		   Note  only parent - child relationships where a child table has only one parent is allowed,
		   but parent can have many child relations, however, a parent can be a child of another table.
		"""   
		   
		statement1 = self.statements[key1]
		statement2 = self.statements[key2]
		tablename1 = extractTablename(statement1)
		tablename2 = extractTablename(statement2)
		statement3 = "alter table %s add column id_%s integer references %s" % ( tablename1, tablename2, tablename2)
		self.refs["%s_%s_ref" %(tablename1, tablename2)]= statement3

		list = self.narrowOn.get(tablename1, [] )  
		list.append(tablename2)
		self.narrowOn[tablename1] = list

		list = self.narrowFrom.get(tablename2, [])
		list.append(tablename1)
		self.narrowFrom[tablename2] = list
	
	def map( self, widgetName, sqlNames, order = 0):
		self.mapping[widgetName] = sqlNames
		self.tableToWidgetName[sqlNames.split('.')[0] ] = widgetName
		
		
		
	def getConnection(self):
		return self._getValidatedConnection()

	def ext_ref(self, name1, name2):
		pass
		
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
		
		return self._doCacheAccess(cache)
	
	def _doCacheAccess( self, cache):
		cache['access count']= cache.get('access count', 0) + 1
		return cache['contents']

	def _cacheContents( self, contents, widgetName, text):
		""" caches the contents , keyed on which widget, and what text was used to retrieve the contents"""
		cache = {} 
		cache['contents'] = contents
		map =  self.comboCache.get(widgetName, {} ) 
		map[text] = cache
		self.comboCache[widgetName] = map

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
			widgetName = self.tableToWidgetName[parentTableName]
			id = self.selectedIndex.get(widgetName, 0)
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
			self.setSelectedIndexToCurrentSelection(widget)	
			
	def _eventComboTextEntered( self, event):
		widget = event.GetEventObject()
		name = widget.GetName()
		self._defaultComboPopulate(name)
		if (widget.GetCount() == 1):
			print "firing select event because widget selection count is 1"
			self._clearChildCaches(widget.GetName())
			self._checkParentText(widget.GetName())

	def _eventComboListSelected(self, event):
		if self.disableTextChange:
			self.disableTextChange = 0
			return
		combo = event.GetEventObject()
		print "event ", event , " received from ", combo
		self.setSelectedIndexToCurrentSelection( combo)	
		self._clearChildCaches(combo.GetName())
		self._checkParentText(combo.GetName())
		
	def setSelectedIndexToCurrentSelection(self, combo):	
		if combo.GetSelection() >= 0:
			self.selectedIndex[combo.GetName()] = combo.GetClientData(combo.GetSelection())
		print "index set to ", self.selectedIndex[combo.GetName()]

	def _clearChildCaches(self, parentWidgetName):
		"""clears the child caches, when a selection is made in a parent widget."""
		parentTable = self.getTableFromWidget(parentWidgetName)
		list = self.narrowFrom.get(parentTable, [])
		for childTable in  list:
			widgetName = self.tableToWidgetName.get(childTable,'no table')
		#	if widgetName in self.comboCache:
		#		del self.comboCache[widgetName] 
			self.comboCache[widgetName] = {}

			if ( self.getWidgetType(widgetName) <> CMBx):
				return

			widget =self.getWidgetByName(widgetName)
			widget.Clear()
			widget.SetValue('')
			self.selectedIndex[widgetName] = 0
			# re-populate based on parent narrowing
			self._defaultComboPopulate(widgetName)
			
			
	def getParentWidgetNames( self, childWidgetName):
		list = []
		childTable = self.getTableFromWidget(childWidgetName)
		list2 = self._getParentTableListFromChild( childTable)
		for parentTable in  list2:
			list.append(self.tableToWidgetName.get(parentTable, None))
		return makeSet(list )

	def _checkParentText( self, childWidgetName):
		"""when a child widget text is selected, the parent widget text is changed to be the
		right parent for the selection ( this allows the unnarrowed selections to get an appropriate
		parent text display ).
		"""
		list =  self.getParentWidgetNames( childWidgetName)
		for parentWidgetName in  list:
			if parentWidgetName == None:
				continue
			self._checkOneParentText( childWidgetName, parentWidgetName)
	
		
	def _checkOneParentText( self, childWidgetName, parentWidgetName):
		parentTable = self.getTableFromWidget(parentWidgetName)
		id = self.selectedIndex.get (childWidgetName, None)
		if id == None:
			return
		childTable = self.getTableFromWidget( childWidgetName)
		print "parent widget=", parentWidgetName, "getFieldFromWidget", self.getFieldFromWidget(parentWidgetName)
		statement = "select parent.id , parent.%s from %s child, %s parent  where child.id = %s and parent.id = child.id_%s " % ( self.getFieldFromWidget(parentWidgetName),  childTable, parentTable ,id, parentTable)
		print statement
		cu = self.getConnection().cursor()
		cu.execute(statement)
		(parent_id, value) = cu.fetchone()
		cu.close()
		combo = self.getWidgetByName( parentWidgetName)
		if combo.GetValue() <> value:
			combo.Append(value, parent_id)
			combo.SetValue(value)
			#cascades check up parent widgets
			self._checkParentText(parentWidgetName)
			

		
		
		
		
class MedicationEditArea(EditArea2):
	
	def __init__(self, parent, id):
		EditArea2.__init__(self, parent, id)
		self.add("classes", CMBx, newline = 1)
		self.add("generic", CMBx, weight = 3)
		self.add("veteran", CHBx,newline=1)
		self.add("drug", CMBx,  weight = 3)
		self.add("reg 24", CHBx, newline=1)
		self.add("strength", weight = 2)
		self.add("quantity",  newline=1)
		self.add("direction", weight = 2)
		self.add("repeats",  newline=1)
		self.add("for", weight = 3)
		self.add("usual", CHBx, newline=1)
		self.add("progress notes", weight = 6)

		#self.ddl("classes", "create table drug_classes( id integer primary key, description varchar(255))")
		self.ddl("classes", 
		"create VIEW drug_classes AS SELECT dc.id , atc.text as description from drug_class dc, atc,  link_drug_atc la where la.atccode=atc.code and la.id_drug = dc.id")
		self.map("classes", "drug_classes.description")
		self.ddl("generic", "create VIEW generic as SELECT gdn.id_drug as id, gdn.name, ldc.id_class as id_drug_classes  from generic_drug_name gdn, link_drug_class ldc where ldc.id_drug =  gdn.id_drug")
		self.ref("generic","classes")
		self.map("generic", "generic.name")
		
	#	self.ddl("drug", "create table drug ( id integer primary key, name varchar(255), atc varchar(255) )")

		self.ddl("drug","create VIEW drug as SELECT lpm.audit_id as id, lpm.brandname as name, ldc.id_class as id_drug_classes, ldc.id_drug as id_generic from link_product_manufacturer lpm, product p, link_drug_class ldc where lpm.id_product = p.id and p.id_drug = ldc.id_drug")
		
		self.ref("drug", "classes")
		self.ref("drug", "generic")
		self.map("drug", "drug.name")


		self.ddl("atc", "create view atc_view as select  lda.id_drug as id, atc.code, atc.text as name from atc , link_drug_atc lda where lda.atccode=atc.code")
		self.ddl("package", "create table package( id  integer primary key, strength float, unit varchar(10), quantity integer ) ")
		self.ref("package", "drug")
		self.map("strength", "package.strength package.unit")
		self.map("quantity", "package.quantity", order=0)
		self.ddl("prescription", "create table prescription(id integer primary key, quantity integer, repeats integer, for_condition text, veteran bool, usual bool , reg_24 bool)")
		self.map("quantity", "prescription.quantity", order = 1)
		self.ref("prescription", "package")
		self.ddl("progress_notes","create table progress_notes( id integer primary key, text text)")
		self.ref("prescription", "progress_notes")
		self.map("progress notes", "progress_notes.text")
	
		self.map("veteran", "prescription.veteran")
		self.map("reg 24", "prescription.reg_24")
		self.map("direction", "prescription.direction")
		self.map("for", "prescription.for_condition")
		self.map("usual", "prescription.usual")

		self.ext_ref("prescription", "identity")
		self.ext_ref("progress_notes","identity")

		#self.browse( { "drug.name":30, "package.strength":10, "prescription.direction":20, "prescription.quantity":10,"prescription.repeats":10, "prescription.date":12, "prescription.veteran":5 })
		
		
		self.finish()


class PastHistoryEditArea(EditArea2):
	def __init__(self, parent, id):
		EditArea2.__init__(self, parent, id)
		self.add("coding system", CMBx, newline = 1)
		self.add("condition", CMBx,  newline  = 1 )
		self.add("left",  RBn)
		self.add("right", RBn)
		self.add("both",  RBn, newline = 1)
		self.add("notes",  newline = 1)
		self.add("age onset" )
		self.add("year onset",  newline = 1)
		self.add("active", CHBx)
		self.add("operation", CHBx)
		self.add("confidential", CHBx)
		self.add("significant", CHBx)
	#	self.group("coding system", ["coding system"] )
	#	self.group("past history", ["condition", "left", "right", "both", "notes", "age onset", "year onset", "active", "operation", "confidential", "significant" ] )
					    
	#	self.group_ref("past history","coding system")
	#	self.group_mapping("disease_code.description[coding system]", "condition")
		
					    
		self.finish()


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
		self.add("first names", weight = 2)
		self.add("last names", weight = 2)
		self.add("title", CMBx, newline = 1)
		self.add("birthdate")
		self.add("sex", CMBx, newline =1 )
		self.add("family", CMBx, newline = 1)
		self.add("place", CMBx, newline = 1)
		self.add("street 1", newline=1)
		self.add("street 2", newline=1)
		self.add("suburb", CMBx, newline = 1)
		self.add("state", CMBx)
		self.add("postcode", newline = 1)
		self.add("medicare no", newline = 1)
		self.add("DVA no", newline = 1)
		self.add("health insurance no", weight = 2)
		self.add("ins.company", newline = 1)
		self.finish()
		
		


if __name__=="__main__":
	setBackupConnectionSource()
	app = wxPyWidgetTester(size=(500,300) )
	app.SetWidget( PastHistoryEditArea, -1)
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
			

	app = wxPyWidgetTester( size=(500, 200) )
	app.SetWidget( DemographicEditArea, -1)
	app.MainLoop()
	
		

	

		

