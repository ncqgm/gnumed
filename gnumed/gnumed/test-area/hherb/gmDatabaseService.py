class gmDatabaseService:
	def __init__(self, get_read_cursor, get_write_cursor, translator=None):
		"""get_read_cursor: DB-API2 compliant function returning a database cursor
		for a read-only connection.
		get_write_cursor: DB-API2 compliant function returning a database cursor
		for a writeable connection.
		translator: optional dictionary that translates attribute names, for example
		'surname' -> 'lastname' to facilitate compatibility between systems. Namespaces
		are prepended to the attribute names, like 'person.surname' -> 'demographics.lastname'"""
		self._translator = translator
		self._ro_cursor = get_read_cursor
		self._rw_cursor = get_write_cursor
		
	
	def cursor(self, readonly=1):
		if readonly:
			return self._ro_cursor
		else:
			return self._rw_cursor
			
			
	def translate(self, dict):
		if translator is None:
			return dict
		td = {}
		for key in dict.keys():
			try:
				td[translator[key]] = dict[value]
			except KeyError:
				td[key] = dict[value]
		return td
			
			
		
	
