from SimpleCommand import *
from SimpleSummaryMap import *
import gmPG
from SimpleDefaultNameMapper import *
import dateCheck
import string
	
def showDateFields( when, map):
	for x in ( 'started', 'date', 'fin' ) :
		try:	
			print when, "checking map[",x,"] = ", map[x]
		except:
			print "no key ", x	

def checkDates(map):
	showDateFields('before', map)
	if map.has_key('started'):	
		map['started'] = dateCheck.checkStrDate(map['started'] )
	if map.has_key('date'):
		map['date'] = dateCheck.checkStrDate(map['date'] )
	if map.has_key('fin'):	
		map['fin'] = dateCheck.checkStrDate(map['fin'])
	showDateFields('after', map)


class SimpleGenericMultiCommand(Command):

	def __init__( self, list,  part, sqlOp = 'insert',  map = SimpleSummaryMap() , afilter = checkDates):
		self.nameList = list
		self.cmdMap = map
		self.part = part
		self.sqlOp = sqlOp
		self.afilter = afilter



        def execute( self, event, data):

                backend = gmPG.ConnectionPool()
                db = backend.GetConnection('default')

                cursor = db.cursor()
                cmdstr = "set datestyle to european"
                print cmdstr
                cursor.execute(cmdstr)

		cursor.execute("commit")
 # transaction starts after last commit
                try:
			
                        fMap = SimpleDefaultNameMapper().mapKeysToFieldNames( data, self.nameList)
                        self.afilter(fMap)
			try:
				fMap['patient'] = data['id']
			except:
				pass
			try:				
				fMap['id'] = data['patient']
			except:
				pass

			try:
				fMap['clin_id'] = data['clin_id']
			except:
				pass


			stmts = self.cmdMap.getStatements(self.part, self.sqlOp , fMap)
			print "got statements = ", stmts
			for x in stmts :
				print "creating statement with template ", x , " with ",  fMap
				
				qry = x % fMap
				print "doing " , qry 
				cursor.execute(qry)

                        cursor.execute("commit")
			ui = event.GetEventObject()
			ui.update()
                except Exception , errorStr:
                        print "error in Insert ", errorStr
                        cursor.execute("rollback")
                        raise Exception


		
