import gmDispatcher, gmSignals, gmLog
_log = gmLog.gmDefLog 
import time, sys, traceback

to_stdout = 0 # flag for info logs to go to standard out.

class gmEditAreaFacade:

	__ddl_executed = 0

	def __init__(self, backend, patient):
		""" sets the handle to a backend and patient business object. 
		The backend handle is needed as gmEditAreaFacade is a Decorator pattern object
		around patient business objects : i.e. it has the same interface as the business objects,
		and allows extra processing on business object calls. 
		The extra processing is updating non-core tables which store edit area specific fields. 
		The decorator object always forwards a call to the business object it is decorating.
		"""
		self._backend = backend
		self.patient = patient
		#self.ddl()


	def ddl(self):
		"""DEPRECATED"""
		pass
		self.table = None
		__ddl_executed = 1


	def id_patient(self):
		return self.patient.id_patient

	def id_encounter(self):
		return self.patient.id_encounter

	def id_episode(self):
		return self.patient.id_episode

	def getDataId(self):
		return self.dataId

	def setDataId(self, id):
		self.dataId = id

	def getRefName(self):
		return "id_other"

	def getFormattedValues(self,  fields,  values, formatting):
		"""
			fields - a list of ordered keys for formatting.
			values - a map of values.
			formatting - a map of formatting.
			uses formatting to format values; returns the formatted values as a list
			IN THE ORDER specified in fields list.
		"""
		map = {}
		for f, v in formatting.items():
			map[f] = v % values[f]
		
		list = []
		for f in fields:
			list.append(map[f])
		
		return list

	def _print(self, list):
		"""
			for info/ non-error logging. 
		"""
		try:
			if to_stdout:
				print list
				return
		except:
			_log.LogException(str(self), sys.exc_info(), verbose = 1)

		if type(list) == type(""):
			gmLog.gmDefLog.Log(gmLog.lInfo, list)
			return
		strList = []	
		for x in list:
			strList = str(x)
		gmLog.gmDefLog.Log(gmLog.lInfo, "  ".join(strList))
			


	def _error_sql_construct_report(self, f, values, formatting, op = "insert"):
		""" debugging report for formatting.
		"""
		self._traceback("error whilst formatting")
		if not values.has_key(f):
			_print("no value for for ", f)
		if not formatting.has_key(f):
			_print("no formatting for ", f)

		_print ("formatting for ", f, " is ", formatting.get(f, "none"))

		_print ("value for ", f, " is ", values.get(f, "none"))
		
		

	def escape_str_quote(self, s):
		"""wxPython text controls don't escape the ' character, and Python literally
		will intepret this character as end of string if string inserted in a ' delimited string.
		So escape all text string."""
		if type(s) == type(""):
			s = s.replace("'", "\\\'" )
		return s	
	
		
	def editarea_insert_data(self, conn,  fields,  formatting, values):
		"""generic editarea specific table insert."""
		valList = []
		for f in fields:
			try:
				valList.append( formatting[f]%self.escape_str_quote(values[f]))
			except:
				self._error_sql_construct_report( f, values, formatting)

		fields.append(self.getRefName())
		valList.append(str(self.getDataId()))

		oldFields = fields
		fields = []
		for f in oldFields:
			fields .append( "".join( ('"', f, '"')  ) )
			

		cmd = "insert into %s( %s) values ( %s )" 	
		curs = conn.cursor()			
		sql = cmd % (self.table, ", ".join(fields), ",".join(valList)  ) 
		_print(sql)
		curs.execute(sql)


	def editarea_update_data( self,  conn, fields,  formatting, values ):
		"""generic editarea specific table update."""
		frags = []
		for f in fields:
			try:
				frags.append( "".join( ('"', f,'"', "=", formatting[f]%self.escape_str_quote(values[f]) ) ) )
			except:
				self._error_sql_construct_report( f, values, formatting, op = "update")
		
		cmd = "update %s set %s where %s= %d"
		curs = conn.cursor()
		curs.execute(cmd % (self.table, ", ".join(frags), self.getRefName(),  self.getDataId()) )
			
	def editarea_delete_data( self, conn):
		"""generic editarea specific table delete."""
		cmd = "delete from %s where %s= %d"
		curs = conn.cursor()
		curs.execute(cmd % (self.table,  self.getRefName(),  self.getDataId()) )
		


	def editarea_select_data( self,  conn, pivot):	
		pass


	
			

	#------------------------------------------------------------------



class gmPHxEditAreaDecorator(gmEditAreaFacade):
	__ddl_executed = 0
	def __init__(self, pastHistory):
		self.impl = pastHistory
		gmEditAreaFacade.__init__(self, self.impl._backend, self.impl.patient)
		self.table = "clin_history_editarea"

	def ddl(self):
		"""THIS METHOD IS DEPRECATED AND NO LONGER USED. KEPT to show the link to extra table"""
		if gmPHxEditAreaDecorator.__ddl_executed:
			return
		
		gmPHxEditAreaDecorator.__ddl_executed = 1
		print "execute past history ddl"
		conn = self._backend.GetConnection( "historica", readonly = 0 )
		curs = conn.cursor()
		try:
			curs.execute("""create sequence id_clin_history_editarea_seq""");
			curs.execute("""create table clin_history_editarea( 
				id integer primary key default nextval('id_clin_history_editarea_seq'),
				id_clin_history integer references clin_history on delete cascade,
				condition text, 
				age varchar(20), 
				"year" varchar(20),
				"left" integer, 
				"right" integer, "both" integer, "none" integer,
				active integer, 
				significant integer,
				confidential integer, 
				operation integer, 
				notes1 text, notes2 text , progress text) """)
			#-----------------
			#	NOTE: on delete cascade is needed in id_clin_history, otherwise no grant permissions 
			#	will allow an entry here to be deleted, and then the entry in clin_history.
			#----------------
			conn.commit()
			curs = conn.cursor()
			
			#---------------------
			# the following grant
			# this won't work, unless one can open a connect as gm-dbowner or postgres
			# so do it manually ?
			#--------------------
			curs.execute("""grant  insert, update, delete, select on clin_history_editarea, clin_history_id_seq to group "_gm-doctors"; """)
			conn.commit()
					
		except:
			conn.rollback()
			_log.LogException(str(self), sys.exc_info(), verbose = 1)

	def getRefName(self):
		return "id_clin_history"
	
	def create_history(self, (fields, formatting, values)  ):
	    """update via impl, the real business object, then save the editarea specific fields"""
   	    conn = self._backend.GetConnection('historica', readonly = 0)
	    try:
		id = self.impl._create_history(conn, fields, formatting, values )
		self.setDataId(id)
		self.editarea_insert_data( conn, fields, formatting, values)
		conn.commit()
	    except:
		   conn.rollback()
		   _log.LogException(str(self), sys.exc_info(), verbose = 1)
	    return id	   

		
	def update_history( self, (fields, formatting, values), ix ):
	    """update via impl, the real business object, then save the editarea specific fields"""
   	    conn = self._backend.GetConnection('historica', readonly = 0)
	    try:
		    self.impl._update_history( conn, fields, formatting, values, ix )	
		    self.setDataId(ix)
		    self.editarea_update_data( conn, fields, formatting, values)
		    conn.commit()
		    self.impl.update_local_history(ix, values)
	    except:
		   conn.rollback()
		   _log.LogException(str(self), sys.exc_info(), verbose = 1)

	def delete_history( self, ix):
   	    conn = self._backend.GetConnection('historica', readonly = 0)
	    try:
		    self.impl._delete_history( conn,  ix )	
		    self.setDataId(ix)
		    self.editarea_delete_data( conn)
		    conn.commit()
		    self.impl.delete_local_history( ix)
	    except:
		   conn.rollback()
		   _log.LogException(str(self), sys.exc_info(), verbose = 1)


		
	def update_local_history(self, id, map):
		"""cache update"""
		return self.impl.update_local_history(id, map)

        def _add_to_local_history(self, id, map):
		self.impl._add_to_local_history( id, map)

		
	def short_format(self, map):
		"""get a short format string from the field values found in map"""
		return self.impl.short_format(map)

	def get_significant_past_history( self ):
		return self.impl.get_significant_past_history()
	
        def get_active_history(self, active = 1 ):
		return self.impl.get_active_history( active )

#----------------------
# started doing this decorator, but left as an example; decorator not plugged in
# because historica.allergy has all necessary fields.
#--------------------
class gmAllergyEditAreaDecorator(gmEditAreaFacade):
	__ddl_executed = 0
	
	def __init__(self, allergy):
		self.impl = allergy
		gmEditAreaFacade.__init__(self, self.impl._backend, self.impl.patient)

	def ddl(self):
		# THIS IS NOT NEEDED FOR ALLERGY, as historica.allergy has all fields
		# needed.
		return
	
		self.table = "allergy_editarea"
		if gmAllergyEditAreaDecorator.__ddl_executed:
			return
		
		gmAllergyAreaDecorator.__ddl_executed = 1
		print "execute allergy editarea ddl"
		conn = self._backend.GetConnection( "historica", readonly = 0 )
		curs = conn.cursor()
		try:
			curs.execute("""create sequence id_allergy_editarea_seq""");
			curs.execute("""create table allergy_editarea( 
				id integer primary key default nextval('id_allergy_editarea_seq'),
				id_allergy integer references allergy
				""")
			conn.commit()
		except:
			conn.rollback()
			_log.LogException(str(self), sys.exc_info(), verbose = 1)

	def getRefName(self):
		return "id_allergy"
	

	def get_substance_list( self, substr):
		return None

	def get_generic_list( self, substr = None, substance = None):
		return None


	def get_drug_classes( self, substr = None, generic = None, substance = None ):
		return None

	def create_allergy( self, ( fields, formatting, values) ):
		conn = self._backend.GetConnection('historica', readonly = 0)
		try:
			self._create_allergy( conn, ( fields, formatting, values) )
		except:
			conn.rollback()
			_log.LogException(str(self), sys.exc_info(), verbose = 1)
		
		
	def _create_allergy( self,conn, ( fields, formatting, values) ):
		pass

