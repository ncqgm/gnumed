import  string

def isBlank(value):
	return len(string.strip(str(value)) ) == 0
def isNotBlank(value):
	return not isBlank(value)

global revocation, phx_eventInsert , phx_durableInsert
	
phx_eventInsert = """insert into phx_event (author, rec_time, started, description, place, extra , patient)
                                        values ( CURRENT_USER, now(), '%(date)s', '%(description)s', '%(place)s', '%(extra)s', %(patient)d );"""

revocation = """insert into revocation( revoked, rec_time,  author, replacing_id )
					 values ( %(clin_id)d, now(), CURRENT_USER, currval('clin_id_seq'));"""

phx_durableInsert =  """insert into phx_durable(author, rec_time, started, fin , description, place, extra, patient)
	       values ( CURRENT_USER, now(), '%(date)s', '%(fin)s',  '%(description)s', '%(place)s' , '%(extra)s', %(patient)d );"""

allergy_insert = """ insert into allergy (author, rec_time, started, drug, description, patient) 
		values (  CURRENT_USER, now(), '%(date)s', '%(drug)s', '%(description)s', %(patient)d ); """


class SimpleSummaryMap:


	def __init__(self):
		
		phxList = [	
				{'dbname': 'date', 'name' : 'date' },
				{'dbname': 'fin', 'name': 'end_date' },
				{'dbname': 'description', 'name' : 'condition'},
				{'dbname' : 'place', 'name': 'place' },
				{'dbname' : 'extra', 'name': 'comments', 'size':200, 'multiline':5 }
			   ]

		
		medsList = [ 
				{'dbname': 'started', 'name' : 'started' },
				{'dbname': 'drug', 'name' : 'drug'},
				{'dname' : 'dose', 'name': 'dose' },
				{'dname' : 'unit', 'name': 'unit' },
				{ 'dname' : 'route', 'name': 'route' },
				{ 'dname' : 'freq', 'name': 'freq' },
				{ 'dname' : 'qty' , 'name' : 'qty' },
				{ 'dname' : 'repeats', 'name' : 'repeats' }
			 ]
		allergyList = [

				{'dbname': 'date', 'name' : 'date'},
				{'dbname' : 'drug', 'name': 'drug' },
				{ 'dbname' : 'description', 'name': 'reaction' },
			      ]

		self.allMap = { 'phx': phxList, 'meds' : medsList , 'allergies': allergyList }

	def getMap(self):
		return self.allMap

	def getScriptMap(self):
		return {  'phx' : "select * from phx_view where patient_id=%d and clin_id not in ( select revoked from revocation) order by to_date(date, 'DD-MON-YYYY') " ,
			  'meds' : "select * from meds_view where patient_id =%d and clin_id not in ( select revoked from revocation) order by to_date(started, 'DD-MON-YYYY') ", 
		 'allergies' : "select * from allergy_view where patient_id = %d and clin_id not in (select revoked from revocation) order by to_date(date , 'DD-MON-YYYY') " }



	def getSQLMap(self):
##""" map syntax is   part : list of alternative actions : 
##			alternative action = precondition : function and parameter ;
##					"insert":	list of insert statement,
##					"update": 	list of update statement
## 	late change: in order to implement traceability later, there is no update. Old versions are added to a revoked list.
##"""					

	
		return {  'phx' : [ { "precondition" : [isBlank, 'fin'] , 
					"insert" : [phx_eventInsert], 
					"edit" : [phx_eventInsert, revocation ],
					"delete" : [ revocation ] 
				    },
				 
				    { "precondition" : [isNotBlank, 'fin'],
					 "insert" :	[ phx_durableInsert ],
			 		 "edit" :  [phx_durableInsert, revocation],
					 "delete" : [ revocation ] 
				    } 
				 ]
				,
			   'allergies': [ { "insert" : [allergy_insert],
					  "edit" : [allergy_insert, revocation] ,
					  "delete" : [ revocation] 
					}
				    ]	  
			
			}	

	def getStatements( self, part, sqlop, data):
		sqlMap = self.getSQLMap()
		stmts = []
		list = sqlMap[part]
		for x in list:
			map = x
			try:
				precondPair = map["precondition"]
				print "evaluating ",precondPair[0], "data[",precondPair[1],"]" 
				yes = precondPair[0](data[precondPair[1]])
				if yes:
					return map[sqlop]
			except Exception, errorStr:
				print self,"getStatements() error: for ",x," in ", list, " when checking for precondition" 
		try:
			return sqlMap[part][0][sqlop]
		except:
			try:
				return sqlMap[part][sqlop]
			except errorStr:
				print "failed to find map for part=", part, "op=",sqlop , ":",errorStr
				
				
			
		
								 
			


		
