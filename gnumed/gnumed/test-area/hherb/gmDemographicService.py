class DemographicService(gmDatabaseService.DatabaseService):
	def __init__(self, get_read_cursor, get_write_cursor, translator={}):
		"""get_read_cursor: DB-API2 compliant function returning a database cursor
		for a read-only connection.
		fet_write_cursor: DB-API2 compliant function returning a database cursor
		for a read-only connection.
		translator: optional dictionary that translates attribute names, for example
		'surname' -> 'lastname' to facilitate compatibility between systems. Namespaces
		are prepended to the attribute names, like 'person.surname' -> 'demographics.lastname'"""
		gmDatabaseService.DatabaseService.__init__(self, get_read_cursor, get_write_cursor, translator)
	
	def searchPerson(self, dict, maxreturn=-1):
		"""searches people matching criteria stated in the dictionary 'dict'.
		returns a list of dictionaries matching the critera"""
	
	def getPerson(self, id=-1):
		"""returns a dictionary containing all properties of the person
		identified by 'id'. If id = -1, a blank record with default values
		and a new valid id will be returned"""
		
	def setPerson(self, dict, id=-1):
		"""insert or update the person record with the values specified in 'dict'.
		If id < 0, a new record will be inserted"""
		
	def searchAddress(self, dict):
		"""searches addresses matching criteria stated in the dictionary 'dict'.
		returns a list of dictionaries matching the critera"""
	
	def getAddress(self, id=-1):
		"""returns a dictionary containing all properties of the address
		identified by 'id'. If id = -1, a blank record with default values
		and a new valid id will be returned"""
	
	def setAddress(self, id, dict):
		"""insert or update the address record with the values specified in 'dict'.
		If id is None, a new record will be inserted"""

		
		
			
def startXMLRPC(self, port=20001, allowed_hosts=None, denied_hosts=None, auth=None):
	"""starts a XML-RPC server listening on 'port' 
	allowed_hosts: either None, in which case all hosts are accepted or a list of hosts
	               exclusively allowed to connect
	denied_hosts:  either None, in which case no host is rejected or a list of hosts
	               specifically ecxcluded from being able to connect. 'denied_hosts'
		       overrides any conflicting information arising from 'allowed_hosts'
	auth: authentication method that returns 0 for rejected or <>0 for accepted.
	      If it is None, no authentication required"""
	pass

