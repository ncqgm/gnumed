import gmDispatcher, gmSignals, gmLog
global _log 
_log = gmLog.gmDefLog 
import time, sys, traceback

from gmClinicalRecord import gmClinicalPart
	
class gmPastHistory(gmClinicalPart):
#	__ddl_executed = 0
	
	def __init__(self, backend, patient):
		gmClinicalPart.__init__(self, backend, patient)
		
	def _getLaterality(self, map):
		if map.get('both', 0) == 1:
			return 'both'
		if map.get('right', 0) == 1:
			return 'right'
		if map.get('left', 0) == 1:
			return 'left'
		if map.get(' ',0) == 1:
			return 'none'
	
	def _putLaterality(self, map):
		laterality = map.get('laterality', None)
		if laterality == None:
			map['laterality'] = self._getLaterality(map)
			return
		map.update( {'both' : laterality == 'both', 
			     'left':  laterality == 'left',
			     'right': laterality == 'right',
			     ' ': laterality == 'none' } )
			
	def _getNotes( self, map):
		s1, s2 = map['notes1'].strip(), map['notes2'].strip()
		
		if s1 == "" or s2 == "":
			return "".join( ('"',s1, s2, '"') )
		return  "|".join( (s1, s2)  )

	def _putNotes( self, map):
		list =  map['notes'].split('|')
		if len(list) == 1:
			map['notes1'] , map['notes2'] = list[0], ''
		else:
			map['notes1'] , map['notes2'] = list[0], list[1]
			
		

	def _putYear( self, map):
		pass
		try:
			map['year'] = int(map['age']) + self._getBirthYear()

		except:
			self._print(  "failed to calc year from age", map['age'] )
		
	def _getBirthDate(self):
		if not self.__dict__.has_key('birthdate') :
			(curs, conn) = self._runQuery(cmd='select dob from v_basic_person where id = %d', params = self.id_patient())
			self.birthdate = curs.fetchone()[0]
			curs.close()
		return self.birthdate	

	def _getBirthYear(self):
		"""need patient info for birth year"""
		return time.localtime(self._getBirthDate())[0]

	def _getCurrentAge(self):
		"""need patient info and current for current age"""
		return time.localtime()[0] - self._getBirthYear()

	def _runQuery(self,schema = 'personalia'  , readonly = 1,  cmd = 'select %d', params = 1):
		conn = self._backend.GetConnection(schema, readonly )
		ro_curs = conn.cursor()

		#<DEBUG>
		self._print(   "executing ", cmd % params ) 
		#</DEBUG>
		_log.Log(gmLog.lData,  "executing ", cmd % params )

		ro_curs.execute(cmd % params)
		return (ro_curs, conn)
		

	def _getYear( self, map):
		y =  int(map.get( 'year','0'))
	
		if  y > 0:
			return y

		age = int(map.get('age', '0'))
		if  age > 0:
			return self._getBirthYear() + map['age']

		return ''

	def _history_input_to_store(self, map):
		map['laterality'] = self._getLaterality( map)
		map['notes'] = self._getNotes(map)
		map['year'] = self._getYear( map)

	def _history_store_to_input(self, map):
		self._putLaterality(map)
		self._putYear(map)
		#self._putNotes(map)

	def get_narrative(self, map):	
		"""gets a narrative description of the data held in the map"""

		str = "in %s, aged %s, %s %s ; condition is %s, %s, %s;%s %s %s" 
		if map['operation'] == 0:
			op = ''
		else:
			op = _('operation performed, ')

		str_table ={ 
			'active' : { 1:_('active'), 0: _('inactive') }, 
			'significant': { 1: _('significant'), 0 : _('insignificant') }, 
			'confidential': { 1: _('confidential') , 0: _('not confidential') }  
			}	

		if map['laterality'] == None:
			map['laterality'] = ""

		narrative = str % ( map['year'], map['age'] ,map['laterality'] ,self.escape_str_quote( map['condition']), 
				str_table['active'].get(map['active'], ''), 
				str_table['significant'].get(map['significant'], ''),
				str_table['confidential'].get(map['confidential'], ''), 
				op, 
				self.escape_str_quote(map['notes1']), 
				self.escape_str_quote(map['notes2'])  
				)

		return narrative

	
	def create_history(self, (fields, formatting, values)  ):
   	    conn = self._backend.GetConnection('historica', readonly = 0)
	    try:
		id = self._create_history(conn, fields, formatting, values )
		conn.commit()
		curs.close()
	    except:
		   conn.rollback()
		   self.traceback()

	    return id   
		

	def _create_history(self, conn,  fields, formatting, values  ):
		self._history_input_to_store( values)
		cmd="insert into clin_history ( narrative, id_type, id_episode, id_encounter) values('%s', 1, %d, %d )" 
		params =( self.get_narrative(values) , self.id_episode(), self.id_encounter() )

		curs = conn.cursor()
		curs.execute( cmd % params)

		curs.execute("select currval('clin_history_id_seq')")
		[id] = curs.fetchone()

		self._add_to_local_history( id, values)

	#	self.setDataId(id)

	#	self.editarea_insert_data( conn, fields, formatting, values)
	

		return id

		
			
	


	def update_history( self, (fields, formatting, values), ix ):
		
   	    conn = self._backend.GetConnection('historica', readonly = 0)
	    try:
		    self._update_history( conn, fields, formatting, values, ix )	
		    conn.commit()
		    self.update_local_history(ix, values)
	    except:
		   conn.rollback()
		   self.traceback()

	def delete_history( self, id):
   	    conn = self._backend.GetConnection('historica', readonly = 0)
	    try:
		    self._delete_history( conn, id )	
		    conn.commit()
		    self.delete_local_history( id)
	    except:
		   conn.rollback()
		   self.traceback()

	def _delete_history(self, conn, id):
		cmd = "delete from clin_history where id = %d" % id
		cu = conn.cursor()
		self._print (cmd)
		cu.execute(cmd)




	def _update_history( self, conn, fields, formatting, values, ix ):
		self._history_input_to_store(values)
		cmd = "update clin_history set  narrative='%s', id_type= 1, id_episode=%d, id_encounter=%d where id = %d"
		params = ( self.get_narrative(values) , self.id_episode(), self.id_encounter() , ix)
		curs = conn.cursor()
		self._print( "using ", cmd , " and params ", params) 
		curs.execute( cmd % params)
	#	self.editarea_update_data( conn, fields, formatting, values)
		curs.close()

		
	def _get_history_storage_keys(self):
		return [ 'significant', 'condition', 'active', 'year' , 'laterality', 'operation', 'confidential', 'notes' ]
	
	
	def get_all_history(self):
		self._print ("""gets the history from the local store , else fetches it with load_past_history""" )
		if not self.__dict__.has_key('past'):
			self.load_all_history()

		return self.past
	

	def _get_history_list(self):


		
		cmd = """select he.id_clin_history, he.condition, he.age, he.active, he.significant, he.confidential,
			he.operation, he."both", he."left", he."right", he."none",  he.notes1, he.notes2, he.progress  
									from clin_history_editarea he,
									clin_history h, 
									clin_episode e , 
									clin_health_issue hi 
									where 
									he.id_clin_history = h.id and	
									h.id_episode = e.id and 
									e.id_health_issue = hi.id and 
									hi.id_patient = %d
									"""
		params = self.id_patient()
		self._print( "self.id_patient=", params )

		try:
			conn = self._backend.GetConnection('historica', readonly = 0)
			curs = conn.cursor()
			curs.execute( cmd % params)
			fetched_items = curs.fetchall()
			curs.close()
		except:
			fetched_items=[]
			self._traceback()
			

		list = []

		map_keys = [ 'condition', 'age', 'active', 'significant', 'confidential', 'operation', 'both','left', 'right', 'none', 'notes1', 'notes2' , 'progress']	
		
		for x in fetched_items:
			map = {}
			for i in xrange(0, len(map_keys) ):
				map[map_keys[i] ] = x[i + 1]
			list.append( [x[0], map] )  # use the first field as index

		for (id, map) in list:
			self._history_store_to_input(map)
			
		return list

	def update_local_history(self, id, map):
		for pair in self.past:
			if pair[0] == id:
				pair[1] = map
				gmDispatcher.send( gmSignals.clin_history_updated())
				break
		
	def delete_local_history( self, id):
		for pair in self.past:
			if pair[0] == id:
				self.past.remove(pair)	
				gmDispatcher.send( gmSignals.clin_history_updated())
				break


			
	def _add_to_local_history(self, id, map):
		self.past.append( [id, map] )
		gmDispatcher.send(gmSignals.clin_history_updated())
		
	
	def load_all_history(self):
		self._print( """loads the past history for the patient""" )
		list = self._get_history_list()
		self.past = list
									

	
	def filter_history(self, key, range, list = [], includeAsDefault = 0):
		self._print ("filtering with ", key, " in ", range )
	
		l = []
		for id, map in list:
			self._print ("checking ", map.get(key, None) )
			if map.get(key , None) in range:
				self._print ("key ", key, " value is in ", range)
				l.append( (id,map) )
			elif includeAsDefault  and not map.has_key(key): 
				self._print( "key ", key, "is not in range ", range, " but included as default.")
				l.append( (id,map) )
			else:
				self._print ("key ", key, "is not in range ", range, " and not included.")
				pass
				
		self._print (" got filtered history ", l)
		
		return l

	def get_accepted_history(self):
		return self.filter_history( 'rejected', range=[0], list = self.get_all_history(), includeAsDefault=1 )
		
	
	def get_active_history(self, active = 1 ):
		list =  self.filter_history( 'active', [active], list = self.get_accepted_history() )
		self._print( "** active =", active, " history =", list)

		return list

		
	def get_significant_history( self, significant = 1, list = []):

		list =  self.filter_history( 'significant', [significant], list, includeAsDefault = 0)

		self._print( "** significant history =  ", list)

		return list

	def get_significant_past_history( self ):
		return self.get_significant_history( list = self.get_active_history( active = 0) )

	def set_rejected_history(self, index, rejected = 1):
		list = self.get_accepted_history()
		if index >= len( list):
			return
		(id, map ) = list[index]
		map['reject'] = rejected
		

	def get_history_fields(self, index):
		"""converts to fields for display"""
		map = self.get_accepted_history()[index]
		self._putLaterality(map)
		self._putAge(map)
		self._putNotes(map)
		return map
	
	def short_format(self, map):
		return  (  str ( map.get('year', ' ') ), self.lateralized_condition(map), str(map.get('notes1','') )  )  

	def lateralized_condition( self, map):
		side = map.get('laterality', '')
		if side == None or type(side) <> type('') or side.lower() == 'none' : 
			side = ''
		condition = " ".join( (side, map['condition'] ))

		return condition	
				
	
#=========================================
