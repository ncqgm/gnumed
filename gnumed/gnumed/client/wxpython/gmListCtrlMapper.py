from wxPython.wx import *
try:
	import gmLog
except:
	sys.path.append('../python-common')
	import gmLog
	
class gmListCtrlMapper:

    def __init__(self, listCtrl):
	    self.list = listCtrl

    def SetData( self, map):
	gmLog.gmDefLog.Log (gmLog.lData, "SETTING DATA FOR %s with %s" % ( str(list) ,  map ))
	items = map.items()
	self.list.DeleteAllItems()
	for x in range(len(items)):
            key, data = items[x]
            #<DEBUG>
	    gmLog.gmDefLog.Log (gmLog.lData, items[x])
            #</DEBUG>
	    #print x, data[0],data[1]
	    self.list.InsertStringItem(x, data[0])
            self.list.SetItemData(x, key)
	    for row in range( 1, len(data)):
		    self.list.SetStringItem(x, row, str(data[row]))

    def GetData(self):
	map = {}
	l = self.list
	c = l.GetColumnCount()
	r = l.GetItemCount()
	for x in xrange(0, r):
		list = []
		for col in xrange(0, c):
			list.append( l.GetItem(x, col).GetText() )
		k = l.GetItemData(x)
		map[k] = list
	return map	
	
