import gmDispatcher, gmSignals, gmLog
global _log 
_log = gmLog.gmDefLog 
import time, sys, traceback
import yaml


class gmEditAreaFacade:

	__ddl_executed = 0

	def __init__(self, backend, patient):
		self._backend = backend
		self.patient = patient
		self.ddl()


	def ddl(self):
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
		map = {}
		for f, v in formatting.items():
			map[f] = v % values[f]
		
		list = []
		for f in fields:
			list.append(map[f])
		
		return list

	def traceback(self):
		print sys.exc_info()[0], sys.exc_info()[1]
		traceback.print_tb(sys.exc_info()[2])

	def _error_sql_construct_report(self, f, values, formatting, op = "insert"):
		print sys.exc_info()[0], sys.exc_info()[1], " whilst formatting ", f, " for ", op
		if not values.has_key(f):
			print "no value for for ", f
		if not formatting.has_key(f):
			print "no formatting for ", f

		print "formatting for ", f, " is ", formatting.get(f, "none")

		print "value for ", f, " is ", values.get(f, "none")
		
		

	def escape_str_quote(self, s):
		if type(s) == type(""):
			s = s.replace("'", "\\\'" )
		return s	
	
		
	def editarea_insert_data(self, conn,  fields,  formatting, values):
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
		print sql
		curs.execute(sql)


	def editarea_update_data( self,  conn, fields,  formatting, values ):
		frags = []
		for f in fields:
			try:
				frags.append( "".join( ('"', f,'"', "=", formatting[f]%self.escape_str_quote(values[f]) ) ) )
			except:
				self._error_sql_construct_report( f, values, formatting, op = "update")
		
		cmd = "update %s set %s where %s= %d"
		curs = conn.cursor()
		curs.execute(cmd % (self.table, ", ".join(frags), self.getRefName(),  self.getDataId()) )
			

	def editarea_select_data( self,  conn, pivot):	
		pass


	
			

	#------------------------------------------------------------------



class gmPHxEditAreaDecorator(gmEditAreaFacade):
	__ddl_executed = 0
	def __init__(self, pastHistory):
		self.impl = pastHistory
		gmEditAreaFacade.__init__(self, self.impl._backend, self.impl.patient)

	def ddl(self):

		self.table = "clin_history_editarea"
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
				id_clin_history integer references clin_history,
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
			conn.commit()
		except:
			conn.rollback()
			self.traceback()

	def getRefName(self):
		return "id_clin_history"
	
	def create_history(self, (fields, formatting, values)  ):
   	    conn = self._backend.GetConnection('historica', readonly = 0)
	    try:
		id = self.impl._create_history(conn, (fields, formatting, values) )
		self.setDataId(id)
		self.editarea_insert_data( conn, fields, formatting, values)
		conn.commit()
	    except:
		   conn.rollback()
		   self.traceback()

		
	def update_history( self, (fields, formatting, values), ix ):
   	    conn = self._backend.GetConnection('historica', readonly = 0)
	    try:
		    self.impl._update_history( conn, (fields, formatting, values), ix )	
		    self.setDataId(ix)
		    self.editarea_update_data( conn, fields, formatting, values)
		    conn.commit()
		    self.impl.update_local_history(ix, values)
	    except:
		   conn.rollback()
		   self.traceback()

		
	def update_local_history(self, id, map):
		return self.impl.update_local_history(id, map)

        def _add_to_local_history(self, id, map):
		self.impl._add_to_local_history( id, map)

		
	def short_format(self, map):
		return self.impl.short_format(map)

	def get_significant_past_history( self ):
		return self.impl.get_significant_past_history()
	
        def get_active_history(self, active = 1 ):
		return self.impl.get_active_history( active )


class gmAllergyEditAreaDecorator(gmEditAreaFacade):
	__ddl_executed = 0
	
	def __init__(self, allergy):
		self.impl = allergy
		gmEditAreaFacade.__init__(self, self.impl._backend, self.impl.patient)

	def ddl(self):

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
				id_allergy integer references allergy,
				

				""")
			conn.commit()
		except:
			conn.rollback()
			self.traceback()

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
			self.traceback()
		
		
	def _create_allergy( self,conn, ( fields, formatting, values) ):
		pass

