#!/usr/bin/python
#############################################################################
#
# gmDrugObject - Object hiding all drug related backend communication
# ---------------------------------------------------------------------------
#
# @author: Hilmar Berger
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: nil
#
# @TODO: Almost everything
# - replace ID by 'mapping' using WHERE xxx=ID ?
############################################################################


#==================================================================             
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/gmDrug/gmDrugObject.py,v $      
__version__ = "$Revision: 1.1 $"                                               
__author__ = "Hilmar Berger <Hilmar.Berger@gmx.net>"

import sys, string
import gmLog
_log = gmLog.gmDefLog
import gmCfg
import gmDbObject, gmPG
import gmExceptions

class QueryGroup:
    """Object holding query strings and associated variable lists grouped together.
    Every query has to be identified by a unique identifier (string or number).
    QueryStrings holds the query strings returning one or more parameters.
    VarNames holds a list of variables that are to be filled by the query. 
    Mappings holds the variables that should be mapped to the query.
    These three dictionaries are accessible from other objects.
    You must use addEntry to add entries to the dictionaries, though, 
    else the data will be written to the class as static variables.
    """

    def __init__(self):
    	self.mVarNames = {}
	self.mQueryStrings = {}
	self.mMappings = {}

    def addEntry(self,aEntry=None):
    	if aEntry != None:
	    self.mVarNames[aEntry]=None
	    self.mQueryStrings[aEntry]=None
	    self.mMappings[aEntry]=None
	    
#--------------------------------------------------------------------------

class Drug:
    """High level API to access drug data"""

    _db = None
    
    #--------------------------------------------------------------------------
    def __init__(self, fastInit=0, queryCfgSource=None):
    	"""initialize static variables"""

    	self.mVars = {}    # variables usable for mapping
    	self.__mQueryGroups = {}
    	self.__mQueryGroupHandlers = {}
        self.__fastInit=0
    
    # get static database handle if not already initialized by other instance of Drug object
    	if Drug._db == None:
	    try:
	    	Drug._db = gmPG.ConnectionPool()
    	    except:
		exc = sys.exc_info()
		_log.LogException("Failed to initialize ConnectionPool handle.", exc, fatal=1)

			   
    # get queries from configuration source (currently only files are supported)
    	if queryCfgSource == None:
		_log.Log(gmLog.lWarn,"No query configuration source specified")
    		return
	else:
    	    self.__mQueryCfgSource = queryCfgSource
    	    if not self.__getQueries():
    	    	return None
		    
    # try to fetch all data at once if fastInit is true 
    	self.__fastInit=fastInit
	if fastInit:
    	    self.getAllData()
    

    #--------------------------------------------------------------------------
    def GetData(self, groupName = None):
    	"""Get data of QueryGroupHandlers identified by groupName
	Returns None if the group does not exist or if the query was not
	successful. Else it returns a dictionary containing all the variables
	defined for this query.
	"""
    	# return None if no sub object was named
    	if groupName == None:	
	    return None
    	elif self.__mQueryGroupHandlers.has_key(groupName):
	    # get query group data
	    result = self.__mQueryGroupHandlers[groupName].getData()
    	    return result
    	else:
	    return None
	    
    #--------------------------------------------------------------------------
    def GetAllData(self):
    	"""initialize and fetch data of all standard sub objects"""
    	for s in self.__QueryGroupHandlers.keys():
	    self.GetData(s)

    #--------------------------------------------------------------------------
    def __getQueries(self):
    	"""get query strings and initialize query group objects"""
    	
    	# open configuration source
	try:
	    cfgSource = gmCfg.cCfgFile(aFile = self.__mQueryCfgSource)
    	# handle all exceptions including 'config file not found'
	except:
	    exc = sys.exc_info()
	    _log.LogException("Unhandled exception while opening config file :%s" % self.__mQueryCfgSource, exc, fatal=1)
	    return None
    	
	cfgData = cfgSource.getCfg()

    	# every group holds one query consisting of three items: variables, the
	# query itself and the mappings
	# queries are identified by the item 'type=query' 
	for entry_group in cfgData['groups'].keys():
		gdata = cfgData['groups'][entry_group]

    	    	try:
		    type=gdata['options']['type']['value']
		except KeyError:
    	    	    # groups not containing queries are silently ignored
		    continue
		
		if type != 'query':
		    continue
    	
    	    	try:
		    groupName=gdata['options']['querygroup']['value']
		except KeyError:
		    _log.Log(gmLog.lWarn,"query definition invalid in entry_group %s." % entry_group)
		    continue

    	    	try:
		    variables_str=gdata['options']['variables']['value']
		except KeyError:
		    _log.Log(gmLog.lWarn,"query definition invalid in entry_group %s." % entry_group)
		    continue

    	    	try:
		    query=gdata['options']['query']['value']
		except KeyError:
		    _log.Log(gmLog.lWarn,"query definition invalid in entry_group %s." % entry_group)
		    continue
    	   
    	    	try:
		    mappings_str=gdata['options']['mappings']['value']
		except KeyError:
		    _log.Log(gmLog.lWarn,"query definition invalid in entry_group %s." % entry_group)
		    continue
    	    	

    	    	# add new query group to QueryGroups dictionary
    	    	if not self.__mQueryGroups.has_key(groupName):
    	    	    self.__mQueryGroups[groupName] = QueryGroup()		    
		self.__mQueryGroups[groupName].addEntry(entry_group)

    	    	# set the parameters read from config file				
		self.__mQueryGroups[groupName].mVarNames[entry_group] = string.split(variables_str,',')
		self.__mQueryGroups[groupName].mMappings[entry_group] = string.split(mappings_str,',')
    	    	self.__mQueryGroups[groupName].mQueryStrings[entry_group] = query

    	    	# inititalize variables used for mapping    	    	
	    	for v in string.split(mappings_str,','):
#		    print "var %s" % v
		    if v != '':
		    	self.mVars[v]=None
    	        		    
	# initialize new QueryGroupHandler objects using configuration data
	for so in self.__mQueryGroups.keys():
	    self.__mQueryGroupHandlers[so]=QueryGroupHandler(self,so,self.__mQueryGroups[so])
	
	return 1	
    
#--------------------------------------------------------------------------

class QueryGroupHandler:
    """Object covering groups of related items; used to access the backend
       to fetch all those items at once. 
    """
    
    #--------------------------------------------------------------------------
    def __init__(self, aParent=None, aName=None, aQueryGroup=None):
    	
	self.__mParent	    = None   # points to the parent Drug object, used to access mVars
	self.__mDBObject     = None  # reference to DBObject
	self.__mObjectName   = None  # this DrugQueryGroupHandler's name
	self.__mQueries      = QueryGroup()    # a QueryGroup holding queries to get the data for this QueryGroupHandlers.
	self.__mData 	    = {}    # a dictionary holding all items belonging to this QueryGroupHandlers

	if aParent != None:
	    self.__mParent = aParent
	    	    
	if aQueryGroup != None:
	    self.__mQueries = aQueryGroup
	
	if aName != None:
	    self.__mObjectName = aName

    #--------------------------------------------------------------------------
    def getData(self):
    	"""returns a dictionary of entry names and its values"""
    	# if data has not been fetched until now, get the data from backend
	if len(self.__mData) == 0 :
	    if self.__fetchBackendData():
	    	return self.__mData
	    else:
	    	return None
	# else return the data already available
	return self.__mData

    #--------------------------------------------------------------------------
    def __fetchBackendData(self):
    	"""try to fetch data from backend"""	
	# if no DBObject has been initialized so far, do it now
	if self.__mDBObject == None:
	    self.__mDBObject = gmDbObject.DBObject(Drug._db,'pharmaceutica') 
    	
	# cycle through query strings and get data
	for queryName in self.__mQueries.mQueryStrings.keys():

	    # get variable mappings
	    mappings = self.__mQueries.mMappings[queryName]
	    allVars = []    
	    for var in mappings:
	    	# get variables from parent
	    	if var != '':
		    allVars = allVars + [self.__mParent.mVars[var]]

	    # set query string
	    if len(allVars)>0:
	    	self.__mDBObject.SetSelectQuery(self.__mQueries.mQueryStrings[queryName] % allVars)
	    else:
	    	self.__mDBObject.SetSelectQuery(self.__mQueries.mQueryStrings[queryName])

    	    # do the query
	    result = self.__mDBObject.Select(listonly=0)
	    
	    # get results
    	    VarNames = self.__mQueries.mVarNames[queryName]
    	    VarNumMax = len(VarNames)
	    for vn in VarNames:
	    	if not self.__mData.has_key(vn):
		    self.__mData[vn] = []

	    # if we got more than one row
    	    if len(result) > 1:
	    	row_num=0
	    	for row in result[:]:
		    row_num = row_num+1
		    DataNumMax = len(row)
    		    VarNum = 0
		    for res in row:
			if VarNum > VarNumMax or VarNum > DataNumMax:
			# raise aException
		    	    break
			VarName = VarNames[VarNum]
    	    	    	
    			self.__mData[VarName].append(res)
			VarNum = VarNum + 1

	    else:
	    	VarNum = 0
    	    	DataNumMax = len(result[0])
		for res in result[0]:
		    if VarNum > VarNumMax  or VarNum > DataNumMax:
		    # raise anException
		    	break
		    VarName = VarNames[VarNum]
    		    self.__mData[VarName] = res
		    VarNum = VarNum + 1
    	# return TRUE if everything went right
	return 1    	


#====================================================================================
# MAIN
#====================================================================================

if __name__ == "__main__":

    a=Drug(0,"/home/hinnef/.gnumed/amis.conf")
    x=a.GetData('brand')
    if x:
    	print x
    else:
    	print "Query wasn't successful."

    print "-----------------------------------------------------"
    y=a.GetData('brand_all')
    print y
    print len(x['brandname'])
