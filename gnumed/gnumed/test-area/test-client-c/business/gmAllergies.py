

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

	def get_allergies(self):
		pass

		

	def create_allergy( self, ( fields, formatting, values) ):
		conn = self._backend.GetConnection('historica', readonly = 0)
		try:
			self._create_allergy( conn, ( fields, formatting, values) )
			conn.commit()
			self.update_local_allergies( values)
		except:
			conn.rollback()
			self.traceback()
		
		
	def _create_allergy( self,conn, ( fields, formatting, values) ):
		values['allergene'] = values['allergy class']
		values['id_type'] = 1 + ( values['sensitivity'] == 0 )
		values['definite'] = "%d = 1" % values['definite']
		values['generic_specific'] = "%d = 1" % values['generic_specific']
		
		cmd = "insert into allergy( id_encounter, id_episode, substance, generics, allergene, id_type, reaction, generic_specific, definite) values ( %d, %d, '%s', '%s', '%s', %d, '%s', %s, %s )"
		v = values
		params = [ self.id_encounter(), self.id_episode(), v['substance'], v['generic'], v['allergene'], v['id_type'], v['reaction'], v['generic_specific'], v['definite'] ]
		print params
		
		command =  cmd % tuple(params)

		cu = conn.cursor()
		cu.execute( command )
		
		cu.execute("select currval('allergy_id_seq')")		
		[id] = cu.fetchone()

		return id

  			
