from SimpleCommand import *


class SimpleListCtrlRefreshCommand( Command):

	def __init__(self, query):
		self.query = query
	def execute( self, ui, id):
		qry = self.query % (id)
		ui.SetQueryStr(qry)
		print "trying to run query ", qry 
		ui.RunQuery()			


