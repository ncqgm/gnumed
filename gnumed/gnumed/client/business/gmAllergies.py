
import gmDispatcher, gmSignals
from gmClinicalRecord import gmClinicalPart

class gmAllergies( gmClinicalPart):

	def __init__(self, backend, patient):
		gmClinicalPart.__init__(self, backend, patient)

	
	def get_substance_list( self, substr):
		return None

	def get_generic_list( self, substr = None, substance = None):
		return None


	def get_drug_classes( self, substr = None, generic = None, substance = None ):
		return None

	def get_allergy_items(self):
		if not self.__dict__.has_key('allergies'):
			self._load_allergies()
		return self.allergies

		
		
	def _load_allergies(self):
		conn = self._backend.GetConnection('historica', readonly = 1)
		statement = """
			select a.id, a.substance, a.generics,  a.allergene, a.id_type, a.narrative, a.generic_specific, a.definite
			from allergy a, clin_episode ce, clin_health_issue hi
			where
				a.id_episode = ce.id and
				ce.id_health_issue=hi.id and hi.id_patient = % d""" % self.id_patient()

		cu = conn.cursor()
		cu.execute(statement)
		l = cu.fetchall()
		print cu.description, " ******** ALLERGIES LOADED ", l
		self.allergies = self.to_keyed_map(l, ['substance', 'generics', 'allergene', 'id_type', 'narrative', 'generic_specific', 'definite'])
		cu.close()
		
		for k in self.allergies.keys():
			self.__store_to_input(self.allergies[k] )

		gmDispatcher.send( gmSignals.allergy_updated() )


	def update_local_allergies( self, ix, values):
		self.__store_to_input(values)
		a = self.get_allergy_items()
		a[ix] = values
		self._print("UPDATED LOCAL STORE", a)
		
		gmDispatcher.send( gmSignals.allergy_updated() )
	
	def __store_to_input(self, value_map):
		value_map['is allergy'] = value_map['id_type'] == 1
		value_map['sensitivity'] = value_map['id_type'] == 2
		value_map['allergy class'] = value_map['allergene']
		if value_map.has_key('generics'):
			value_map['generic'] = value_map['generics']
		else:
			value_map['generics'] = value_map['generic']

		for k,v in value_map.items():
			if v == None:
				value_map[k] = ''
				





		
	def _validate_has_reaction(self, values):
		try:
			self.validate_not_null( values, ['reaction'] )
		except:
			warn('must have a reaction')
			raise
	

	def  _validate_has_at_least_one_hypothesised_cause(self, values):
		e = 0
		#validate at least one  not null field in substance, generics, allergy_class
		for f in ['substance', 'generics', 'allergy class']:
			try:
				self.validate_not_null( values, f )
			except:
				e  += 1
		
		if e == 3:
			warn("must have one of substance, generics or allergy class filled")
			raise
		
		
	def validate( self, values):
		try:
			self._validate_has_reaction(values)
			self._validate_has_at_least_one_hypothesised_cause(values)
		except:
			return 0
		return 1
	

	def _get_params(self, v):
		"""THIS IS THE MAIN TRANSFORMATION ENTRY FUNCTION to transform user input into the datasource's format """
		
		if not self.validate(v):
			return
		
		v['allergene'] = v['allergy class']
		
		
		if v['sensitivity'] == 1:
			v['id_type'] = 2
		else:
			v['id_type'] = 1
		
		params = [ self.id_encounter(), self.id_episode(), 
				self.escape_str_quote(v['substance']),
				self.escape_str_quote( v['generic']),
				self.escape_str_quote(v['allergene']),
				v['id_type'],
				self.escape_str_quote(v['reaction']),
				v['generic_specific'], v['definite']
			 ]
		self._print( params)
		return params
	
	def create_allergy( self, ( fields, formatting, values) ):
		conn = self._backend.GetConnection('historica', readonly = 0)
		try:
			ix = self._create_allergy( conn, ( fields, formatting, values) )
			conn.commit()
			self.update_local_allergies( ix, values)
		except:
			conn.rollback()
			self._traceback()
			return None
		return ix	
	
	def _create_allergy( self,conn, ( fields, formatting, values) ):
		
#		cmd = "insert into allergy( id_encounter, id_episode, substance, generics, allergene, id_type, narrative, generic_specific, definite) values ( %d, %d, '%s', '%s', '%s', %d, '%s', %d=1, %d=1 )"
#		command =  cmd % tuple(self._get_params(values) )

#		cu = conn.cursor()
#		cu.execute( command )
		
#		cu.execute("select currval('allergy_id_seq')")		
#		[id] = cu.fetchone()

		# FIXME: use business object
		return -1

		return id


	def update_allergy( self, ( fields, formatting, values), ix):
		conn = self._backend.GetConnection('historica', readonly = 0)
		try:
			self._update_allergy( conn, fields, formatting, values, ix)
			conn.commit()
			self.update_local_allergies( ix, values)
		except:
			conn.rollback()
			self._traceback()
	
	def delete_allergy( self, ix):
		conn = self._backend.GetConnection('historica', readonly = 0)
		try:
			cu = conn.cursor()
			cmd = 'delete from allergy where id = %d' % ix
			cu.execute(cmd)
			self._print( cmd)
			conn.commit()
			cu.close()
			
		except:
			conn.rollback()
			self._traceback()
			return 0

		del self.get_allergy_items()[ix]
		gmDispatcher.send( gmSignals.allergy_updated() )

	
	def _update_allergy( self,conn, fields, formatting, values, ix):
		self._print("update_allergy input values = ", values)
		statement = self._get_update_statement( values, ix)

		self._print(statement)
		
		cu = conn.cursor()
		cu.execute(statement)
		cu.close()
		

	def _get_update_statement( self, values, ix):	
		"""convert to fragments in the set [field=value] x n  clause of update allergy statement"""
		cmd = "update allergy set %s where id= %d"
		values = self._get_params(values)[2:]
		fields = "substance, generics, allergene, id_type, narrative, generic_specific, definite".split(', ')
		formatting = "'%s', '%s', '%s', %d, '%s', %d=1, %d=1".split(',')
		frags = []
		for i in xrange( 0, len(fields) ):
			frags.append(" ".join( (fields[i], '=', formatting[i] % values[i] ) ) )

		param_str = ", ".join(frags)

		return cmd % ( param_str, ix)

		
