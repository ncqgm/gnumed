#!/usr/bin/python

"""This module encapsulates document level operations.

@copyright: GPL
"""
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/blobs_hilbert/modules/Attic/docXML.py,v $
__version__ = "$Revision: 1.1 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"
#=======================================================================================
import os.path, fileinput, string, types
import gmLog

__log__ = gmLog.gmDefLog
#=======================================================================================
def __read_img_list(self, aDescFile = None, aBaseDir = None):
	"""Read list of image files from XML metadata file.

	We assume the order of file names to correspond to the sequence of pages.
	"""
	# sanity check
	if aBaseDir == None:
		aBaseDir = ""

	self.__metadata['objects'] = {}

	i = 1
	# now read the xml file
	for line in fileinput.input(aDescFile):
		# is this a line we want ?
		start_pos = string.find(line,'<image')
		if start_pos == -1:
			continue

		# yes, so check for closing tag
		end_pos = string.find(line,'</image>')
		if end_pos == -1:
			# but we don't do multiline tags
			__log__.Log (gmLog.lErr, "Incomplete <image></image> line. We don't do multiline tags. Sorry.")
			return (1 == 0)

		# extract filename
		# FIXME: this is probably the place to add object level comments ?
		start_pos = string.find(line,'>', start_pos, end_pos) + 1
		file = line[start_pos:end_pos]
		tmp = {}
		tmp['file name'] = os.path.abspath(os.path.join(aBaseDir, file))
		tmp['index'] = i
		# we must use imaginary oid's since we are reading from a file
		self.__metadata['objects'][i] = tmp
		i += 1

	# cleanup
	fileinput.close()

	if len(self.__metadata['objects'].keys()) == 0:
		log.Log (gmLog.lErr, "no files found for import")
		return (1 == 0)

	__log__.Log(gmLog.lData, "document data files to be processed: " + str(self.__metadata['objects']))

	return (1==1)
#-----------------------------------
def __get_from_xml(self, aTag = None, anXMLfile = None):
	# sanity
	if type(aTag) != types.StringType:
		__log__.Log(gmLog.lErr, "Argument aTag (" + str(aTag) + ") is not a string.")
		return None

	TagStart = "<" + aTag + ">"
	TagEnd = "</" + aTag + ">"

	__log__.Log(gmLog.lInfo, "Retrieving " + TagStart + "content" + TagEnd + ".")

	inTag = 0
	content = []

	for line in fileinput.input(anXMLfile):
		tmp = line

		# this line starts a description
		if string.find(tmp, TagStart) != -1:
			inTag = 1
			# strip junk left of <tag>
			(junk, good_stuff) = string.split (tmp, TagStart, 1)
			__log__.Log(gmLog.lData, "Found tag start in line: junk='%s' content='%s'" % (junk, good_stuff))
			tmp = good_stuff

		# this line ends a description
		if string.find(tmp, TagEnd) != -1:
			# only if tag start has been found already
			if inTag == 1:
				# strip junk right of </tag>
				(good_stuff, junk) = string.split (tmp, TagEnd, 1)
				__log__.Log(gmLog.lData, "Found tag end in line: junk='%s' content='%s'" % (junk, good_stuff))
				content.append(good_stuff)
				# shortcut out of for loop
				break

		# might be in-tag data line or line with start tag only
		if inTag == 1:
			content.append(tmp)

	# cleanup
	fileinput.close()

	# looped over all lines
	if len(content) > 0:
		__log__.Log (gmLog.lData, "%s tag content succesfully read: %s" % (TagStart, str(content)))
		return content
	else:
		return None
#----------------------------------------------------------------------------
