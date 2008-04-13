#========================================================
import sys, string, re, types


from Gnumed.pycommon import gmCfg, gmDrugObject, gmExceptions
from Gnumed.business import gmSurgery


_log = gmLog.gmDefLog
_cfg = gmCfg.gmDefCfgFile

darkblue = '#00006C'
darkgreen = '#0106D0A'
darkbrown = '#841310'

#========================================================
class DrugView:
	"""handles a given Interface to a drug database via the Drug object"""

	def __init__(self, aDatabaseName=None):
		"""
		Initialize the DrugView object with information supplied via
		the standard config file. The data should be grouped together
		in the group designated by the database name.
		"""

		if aDatabaseName == None:
			raise gmExceptions.ConstructorError,"No database name specified."

		# open configuration source
		# if we are not inside gnumed we won't get a definite answer on
		# who and where we are. in this case try to get config source 
		# from main config file (see gmCfg on how the name of this file
		# is determined
		currWorkplace = gmSurgery.gmCurrentPractice().active_workplace
		if currWorkplace is None:
			# assume we are outside gnumed
			self.dbConfFile = _cfg.get(aDatabaseName, 'configfile')
		else:
			# 
			self.dbConfFile, match = gmCfg.getDBParam(
				workplace=currWorkplace,
				option="DrugReferenceBrowser.%s.configfile" % aDatabaseName
			)

		_log.Log(gmLog.lInfo, "dbConfFile is [%s]" % str(self.dbConfFile))
			
		if self.dbConfFile is None:
			_log.Log(gmLog.lErr, "No config information on drug database [%s] found." % aDatabaseName)
			raise gmExceptions.ConstructorError,"No DrugDB config file specified."

		try:
			self.mDrugInterface = gmDrugObject.cDrug(queryCfgSource = self.dbConfFile)
		except:
			_log.LogException("Unhandled exception while opening config file", sys.exc_info(), verbose = 0)
			raise gmExceptions.ConstructorError,"Couldn't initialize drug object for DB %s" % aDatabaseName

		self.__mFormatString = {} 	# format strings
		self.__mGroupPos = {}		# query group on position x
		self.__mFormatType = {}		# format type
		self.__mHeading = {}		# the heading used (if any)
		self.__mUsedVars = {}		# parameters used from the query dict
		# get configuration from file
		self.__getFormatInfo()

		# initialize DrugIds
		self.mLastId = {}
		self.mCurrId = -1
        
	def SearchIndex(self, aType=None, aName=None , aMode='exact', format=0):
		"""
		Search a for a certain drug. Possible values for index type include
		0 (brand name index), 1 (generic name index) and 2 (indication index).
		mode can be either exact matching (that is, match all given letters 
		using the LIKE operator), regular expression ('re') matching or
		complete list ('complete').
		"""

		if aName == None:
			return None

		# choose index name
		if aType == 0:
			index = 'brand_index'
		elif aType == 1:
			index = 'generic_index'
		elif aType == 2: 
			index = 'indication_index'
		else:
			return None

		searchExact = 0
		searchAll = 0
		searchRE = 0	

		if aMode == 'exact':
			suffix = '_exact'
			search_exact = 1
		elif aMode == 're':
			suffix = '_re'
			searchRE = 1
		elif aMode == 'complete':
			suffix = '_all'
			searchAll = 1

		if not searchAll:
			self.mDrugInterface.mVars['Key'] = aName

		result = self.mDrugInterface.GetData(index + suffix,refresh=1)
		return result

	def getBrandsForGeneric(self,aId):
		"""
        Returns a list of drugs for a given generic substance.
        The substance is specified by aID.
        """
		if aId is None:
			return None
		# set product Id
		self.mDrugInterface.mVars['ID']=aId        

		result = self.mDrugInterface.GetData('brandsForGeneric',refresh=1)
		return result

	def getProductInfo(self,aId):
		"""
        Returns an HTML-formatted drug information sheet for display
        in the Pharmaceutical Reference Browser. 
        The drug is specified by aID.
        """
		if aId is None:
			return None
		# set product Id
		self.mDrugInterface.mVars['ID']=aId        
		self.mCurrId = aId

		# get product info
		piText=''
		headings=[]
		groupPosList = self.__mGroupPos.keys()

# DEBUG
#		print "LIST",groupPosList
		# get text parts in order of position and combine them 
		groupPosList.sort()
		for pos in groupPosList:
			textPart = self.__getTextPart(pos)
			if textPart != '':
				piText += textPart
				if self.__mHeading.has_key(pos):
					headings.append(self.__mHeading[pos])
                    

		# if no part contained data, no info is available
		piTotalLen = len(piText)         
		if piTotalLen == 0:
			pitext = "<HTML><HEAD></HEAD><BODY BGCOLOR='#FFFFFF8'> <FONT SIZE=3>"
			pitext = pitext + _("No product information available.")            
			pitext = pitext + "</FONT></BODY></HTML>"
			return pitext

		# in all other cases, construct the HTML frame
		#----------------------------------------------------------------------
		# Start construction the html file to display
		# First put up the header of the html file
		# to put in hyperlink
		#----------------------------------------------------------------------
		piTextComplete="<HTML><HEAD></HEAD><BODY BGCOLOR='#FFFFFF8'> <FONT SIZE=-1>"
		#--------------------------------------------------------
		# For each field which is not null put a heading <B> </B>
		#--------------------------------------------------------

		piTextComplete = piTextComplete +  "<A NAME=\"Description\"></A><BR><FONT  SIZE=4 COLOR='" + darkblue + "'><B>Description</B></FONT><BR>"
		piTextComplete = piTextComplete + piText + "</FONT></BODY></HTML>"

		return (piText,headings)

	#--------------------------------------------------------------------
	def __getTextPart(self, pos = 0):
		"""
        get the formatted result of a numbered text entry.
        Every entry has a number that is used as an pointer in several lists.
        These lists hold the entry type (one of 'heading', 'noheading', 
        'single' or 'list'), the query group containing the parameters in a
        dictionary, the format string and the names of the parameters used 
        (the latter is used to test for completely empty parameter sets that 
        wont be displayed).
        Short explanation of types: 
        heading : holds only a heading, takes no parameters from dict
        noheading : the contrary: no heading, only format string is used
        single: has a heading and uses the format string 
        list: has a heading, but does not use the format string. Instead all
         values found for an parameter are put in an itemized list.
         
        All types using parameters from a query must supply a list of parameters
        used via entry 'usedvars' in config file.
        """

		# get query group and format format_type of current position
		group = self.__mGroupPos[pos]
		format_type = self.__mFormatType[pos]

	        # if the drug ID has not changed for this query group, use cached data
		refresh=0
		if not self.mLastId.has_key(group):
			self.mLastId[group] = -1
		if self.mLastId[group] != self.mCurrId:
			refresh=1
			self.mLastId[group] = self.mCurrId
            
# DEBUG
#		print "TextPart: ",group, " ", format_type

		# do the query
		queryResult = self.mDrugInterface.GetData(group,refresh)
		
		# check result for empty fields in UsedVarsList
		# if all fields are empty, we wont show anything
		resultTotalLen = 0
		if format_type != 'heading':
			usedVars = self.__mUsedVars[pos]
			if not queryResult is None:
				for item in usedVars:
					if not queryResult.has_key(item):
						_log.Log(gmLog.lWarn, "Variable name invalid: %s" % item)
					else:
						value = queryResult[item]
						if value == []:
							value = ''
						resultTotalLen += len(str(value))
# DEBUG
#					print "ITEM",item, "LEN: ", len(queryResult[item])
		else:
			resultTotalLen = -1

		# if all fields are empty, return empty string
		if queryResult is None or resultTotalLen == 0:
			return ''

		# if no heading is desired, just print the format string
		if format_type == 'noheading':
			formattedInfo = self.__mFormatString[pos] % queryResult
			text = translateASCII2HTML(formattedInfo)        	
			return text
		else:
			# handle all cases using a heading
			heading = self.__mHeading[pos]
			if heading != '':
				text = "<A NAME=\"" + heading + "\"></A><BR><FONT  SIZE=5 COLOR='" + darkblue + "'><B>" + heading + "</B></FONT><BR>"
			else:
				text = ''
			
			if format_type == "heading":
				return text
		        
		if format_type == 'single':
			formattedInfo = self.__mFormatString[pos] % queryResult
			text = text + translateASCII2HTML(formattedInfo)
		elif format_type == 'list':
			# we didn't check for empty items in list, 
			# so we have to do it here 
			resultTotalLen = 0

			# the variable in question should contain a list of entries.
			# we format them as an itemized list
			# currently we only support one variable per entry
			itemList = queryResult[usedVars[0]]
			# if only one entry, cast to list 
			if not type(itemList) is types.ListType:
				itemList = [itemList]

			tmpText=''
			# loop through all items
			for item_raw in itemList:
				# get item and it's length
				item=str(item_raw)
				itemLen = len(item)
				# if item is not an empty string, format it as HTML
				if itemLen > 0:
					resultTotalLen += itemLen
					tmpText = tmpText + "<li>" + item + "</li>"

			# if at least one item contained data, return result as HTML list
			if resultTotalLen > 0:
				text += '<ul>' + tmpText + '</ul>'				
			else:
				text = ''		
		else:
			# unhandled format type, shouldn't happen
			_log.Log(gmLog.lWarn, "Unknown format type: [%s]" % format_type)
			text = ''

		return text            	


	#-----------------------------------------------------------------
	def __getFormatInfo(self):
		"""get info on how to format parameters returned by query groups"""

		# open configuration source
		try:
			cfgSource = gmCfg.cCfgFile(aFile = self.dbConfFile, \
				flags=gmCfg.cfg_SEARCH_STD_DIRS | gmCfg.cfg_IGNORE_CMD_LINE)
			# handle all exceptions including 'config file not found'
		except:
			exc = sys.exc_info()
			_log.LogException("Unhandled exception while opening config file [%s]" % self.dbConfFile, exc, verbose = 0)
			return None

		cfgData = cfgSource.getCfg()
		groups = cfgSource.getGroups()

		# every info holds 
        # -an format string (presented as an list)
        # -a heading
        # -a format type ('none','single' or 'list')
        # -a position in the product info (int >= 0)
        # -the query group name that supplies the variables that are to be
        #  matched to the format string 
		# format infos are identified by the item 'type=format' 
		for entry_group in groups:
			entry_type = cfgSource.get(entry_group, "type")
			# groups not containing format strings are silently ignored
			if entry_type != 'format':
				continue

			# group name
			qname = cfgSource.get(entry_group, "querygroup")
			if qname is None:
				_log.Log(gmLog.lWarn,"query definition invalid in entry_group %s." % entry_group)
				continue

			# group format type 
			ftype = cfgSource.get(entry_group, "formattype")
			if ftype is None:
				_log.Log(gmLog.lWarn,"query definition invalid in entry_group %s." % entry_group)
				continue

			fposstring = cfgSource.get(entry_group, "position")
			# check that the position is an valid int number
			try:
				fpos = int(fposstring)
			except TypeError:
				fpos = -1

			if fpos is None or fpos < 0:
				_log.Log(gmLog.lWarn,"query definition invalid in entry_group %s." % entry_group)
				continue

			if ftype != 'heading':
				format = cfgSource.get(entry_group, "format")
				if format is None or not type(format) == types.ListType:
					_log.Log(gmLog.lWarn,"query definition invalid in entry_group %s." % entry_group)
					continue

				usedVars = cfgSource.get(entry_group, "usedvars")
				if usedVars is None:
					_log.Log(gmLog.lWarn,"query definition invalid in entry_group %s." % entry_group)
					continue


			if ftype != 'noheading':
				heading = cfgSource.get(entry_group, "heading")
				if format is None or not type(format) == types.ListType:
					_log.Log(gmLog.lWarn,"query definition invalid in entry_group %s." % entry_group)
					continue

			# set the parameters read from config file				
			self.__mGroupPos[fpos] = qname 
			self.__mFormatType[fpos] = ftype
			if ftype != 'heading':
				fstring=string.join(format,'')
				self.__mFormatString[fpos] = fstring
				usedVarsList = string.split(usedVars,',')
				self.__mUsedVars[fpos] = usedVarsList
			if ftype != 'noheading':
				fheading = string.join(heading,'')
				self.__mHeading[fpos] = fheading
		return 1



#========================================================
def translateASCII2HTML(aString = None):
	subst = aString
	subst=re.sub('<',"&lt;",subst)
	subst=re.sub('>',"&gt;",subst)
	subst=re.sub("\xa7","<br>",subst)
	subst=re.sub('ä','&aauml;',subst)
	subst=re.sub('ö','&oauml;',subst)	
	subst=re.sub('ü','&uauml;',subst)
	return subst
 
if __name__ == "__main__":
	print "please write unit test code"

#========================================================
# $Log: gmDrugView.py,v $
# Revision 1.12  2008-04-13 14:41:40  ncq
# - old style logging is out
#
# Revision 1.11  2007/10/07 12:29:12  ncq
# - workplace property now on gmSurgery.gmCurrentPractice() borg
#
# Revision 1.10  2007/02/17 14:13:11  ncq
# - gmPerson.gmCurrentProvider().workplace now property
#
# Revision 1.9  2006/10/25 07:19:03  ncq
# - no more gmPG
#
# Revision 1.8  2006/05/14 21:44:22  ncq
# - add get_workplace() to gmPerson.gmCurrentProvider and make use thereof
# - remove use of gmWhoAmI.py
#
# Revision 1.7  2006/05/12 12:06:13  ncq
# - whoami -> whereami
#
# Revision 1.6  2005/03/17 20:32:14  hinnef
# -fixed module dependencies
#
# Revision 1.5  2004/09/18 13:52:41  ncq
# - properly use setDBParam()
#
# Revision 1.4  2004/08/20 13:34:48  ncq
# - getFirstMatchingDBSet() -> getDBParam()
#
# Revision 1.3  2004/07/19 11:50:42  ncq
# - cfg: what used to be called "machine" really is "workplace", so fix
#
# Revision 1.2  2004/03/10 00:14:04  ncq
# - fix imports
#
# Revision 1.1  2004/02/25 09:30:13  ncq
# - moved here from python-common
#
# Revision 1.4  2003/12/29 16:26:14  uid66147
# - use whoami.get_workplace()
#
# Revision 1.3  2003/11/17 10:56:36  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:39  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.2  2003/09/03 17:32:05  hinnef
# make use of gmWhoAmI, try to get config info from backend
#
# Revision 1.1  2003/08/24 13:38:24  hinnef
# moved to main-tree, some bug fixes
#
# Revision 1.6  2002/11/17 16:44:23  hinnef
# fixed some bugs regarding display of non-string items and list entries in PI
#
# Revision 1.5  2002/11/09 15:10:47  hinnef
# detect ID changes for every query group in GetTextPart
#
