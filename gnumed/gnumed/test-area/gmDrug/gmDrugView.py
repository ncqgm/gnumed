#!/usr/local/bin/python

import sys, string, re, types, os.path

# location of our modules
if __name__ == "__main__":
	sys.path.append(os.path.join('.', 'modules'))

import gmLog
_log = gmLog.gmDefLog

import gmCfg
_cfg = gmCfg.gmDefCfgFile

import gmPG, gmDrugObject

darkblue = '#00006C'
darkgreen = '#0106D0A'
darkbrown = '#841310'


class DrugView:
	"""handles a given Interface to a drug database via the Drug object"""

	def __init__(self, aDatabaseName=None):
		"""
		Initialize the DrugView object with information supplied via
		the standard config file. The data should be grouped together
		in the group designated by the database name.
		"""

		if aDatabaseName == None:
			return None

		# open configuration source
		self.dbConfFile = _cfg.get(aDatabaseName, 'configfile')

		if self.dbConfFile is None:
			_log.Log(gmLog.lErr, "No config information on drug database [%s] found." % aDatabaseName)
			return None

		try:
			self.mDrugInterface = gmDrugObject.Drug(queryCfgSource = self.dbConfFile)
		except:
			_log.LogException("Unhandled exception while opening config file", sys.exc_info(), fatal=1)
			return None

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
        Every entry has a number is used as an pointer in several lists.
        These lists hold the entry type (one of 'heading', 'noheading', 
        'single' or 'list'), the query group containing the parameters in a
        dictionary, the format string and the names of the parameters used 
        (the last is used to test for completely empty parameter sets that 
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

		# query group and format type of current position
		group = self.__mGroupPos[pos]
		type = self.__mFormatType[pos]

        # if the drug ID has not changed for this query group, use cached data
		refresh=0
		if not self.mLastId.has_key(group):
			self.mLastId[group] = -1
		if self.mLastId[group] != self.mCurrId:
			refresh=1
			self.mLastId[group] = self.mCurrId
            
# DEBUG
#		print "TextPart: ",group, " ", type

		# do the query
		queryResult = self.mDrugInterface.GetData(group,refresh)
		
		# check result for empty fields in UsedVarsList
		resultTotalLen = 0
		if type != 'heading':
			usedVars = self.__mUsedVars[pos]
			if not queryResult is None:
				for item in usedVars:
					if not queryResult.has_key(item):
						_log.Log(gmLog.lWarn, "Variable name invalid: %s" % item)
					else:
						resultTotalLen += len(queryResult[item])
# DEBUG
#					print "ITEM",item, "LEN: ", len(queryResult[item])
		else:
			resultTotalLen = -1

		# if all fields are empty, return empty string
		if queryResult is None or resultTotalLen == 0:
			return ''

		# if no heading is desired, just print the format string
		if type == 'noheading':
			formattedInfo = self.__mFormatString[pos] % queryResult
			text = translateASCII2HTML(formattedInfo)        	
			return text
        
		# handle all cases using a heading
		heading = self.__mHeading[pos]
		if type == 'heading':
			if heading != '':
				text = "<A NAME=\"" + heading + "\"></A><BR><FONT  SIZE=5 COLOR='" + darkblue + "'><B>" + heading + "</B></FONT><BR>"
			else:
				text = ''
		elif type == 'single':
			if heading != '':
				text = "<A NAME=\"" + heading + "\"></A><BR><FONT  SIZE=5 COLOR='" + darkblue + "'><B>" + heading + "</B></FONT><BR>"
			else:
				text = ''

			formattedInfo = self.__mFormatString[pos] % queryResult
			text = text + translateASCII2HTML(formattedInfo)
		elif type == 'list':
			if heading != '':
				text = "<A NAME=\"" + heading + "\"></A><BR><FONT  SIZE=5 COLOR='" + darkblue + "'><B>" + heading + "</B></FONT><BR>"
			else:
				text = ''
			resultTotalLen = 0

			# the query result should contain all available indications.
			# we format them as an itemized list
		
			tmpText=''
			# loop through all items
			for ind in queryResult.keys():
				# get item and it's length
				item = queryResult[ind]
				itemLen = len(item)
				# if item is not an empty string, format it as HTML
				if itemLen > 0:
					resultTotalLen += itemLen
					tmpText = tmpText + "<li>" + item + "</li>"

			# if at least one item contained data, return result as HTML list
			if resultTotalLen > 0:
				text = '<ul>' + tmpText + '</ul>'				
			else:
				text = ''
		else:
			text = ''

		return text            	


	#-----------------------------------------------------------------
	def __getFormatInfo(self):
		"""get info on how to format parameters returned by query groups"""

		# open configuration source
		try:
			cfgSource = gmCfg.cCfgFile(aFile = self.dbConfFile)
			# handle all exceptions including 'config file not found'
		except:
			exc = sys.exc_info()
			_log.LogException("Unhandled exception while opening config file [%s]" % self.dbConfFile, exc, fatal=1)
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




def translateASCII2HTML(aString = None):
	subst = aString
	subst=re.sub('<',"&lt;",subst)
	subst=re.sub('>',"&gt;",subst)
	subst=re.sub("\xa7","<br>",subst)
	return subst
 
if __name__ == "__main__":
	pass

# $Log: gmDrugView.py,v $
# Revision 1.5  2002-11-09 15:10:47  hinnef
# detect ID changes for every query group in GetTextPart
#