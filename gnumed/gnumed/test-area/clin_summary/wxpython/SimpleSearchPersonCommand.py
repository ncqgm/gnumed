from SimpleChainedCommand import *
from string import * 

class SimpleSearchPersonCommand( SimpleChainedCommand):
	
	def execute( self, text, selectUI):
		if (len(text) < 2) :
			print "need more characters"
			return
		
		#sqlcmd = SimpleChainedCommand.execute(self, text, None)
		#print "Simple Search Command got" , sqlcmd

		names = split(text, ',')

                last = strip(names[0])
                try:
                        first = strip(names[1])
                except:
                        first =''

                cmds = ("select * from person_view2 where lastnames like '%s"% last, '%', "'", "  and firstnames like '%s"% first, '%',"'")
                cmdstr = join(cmds, '')
                print cmdstr

		selectUI.updateList(sqlcmd = cmdstr)
	
		
						
