"""This module encapsulates a document description stored in an XML file.

This is mainly used by GnuMed/Archive.

@copyright: GPL
"""
#============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/business/gmXmlDocDesc.py,v $
# $Id: gmXmlDocDesc.py,v 1.5 2008-01-30 13:34:50 ncq Exp $
__version__ = "$Revision: 1.5 $"
__author__ = "Karsten Hilbert <Karsten.Hilbert@gmx.net>"

import sys, os.path, fileinput, types, string, logging


_log = logging.getLogger('gm.docs')
_log.info(__version__)
#============================================================
class xmlDocDesc:
    # handlers for __getitem__()
    _get_handler = {}
    #--------------------------------------------------------
    def __init__(self, aBaseDir = None, aCfg = None, aGroup = 'metadata'):
        # sanity checks
        if aBaseDir is None:
            raise ConstructorError, "need document path"
        if not os.path.exists(os.path.abspath(aBaseDir)):
            raise ConstructorError, "document path [%s] does not exist" % aBaseDir
        self.__base_dir = aBaseDir
        _log.debug("working from directory [%s]" % self.__base_dir)

        if aCfg is None:
            _log.warning('no config file specified')
            import gmCfg
            self.__cfg = gmCfg.gmDefCfgFile
        else:
            self.__cfg = aCfg

        self.__group = str(aGroup)

        tmp = self.__cfg.get(self.__group, "description")
        self.__xml_file = os.path.join(self.__base_dir, tmp)
        if not os.path.exists(self.__xml_file):
            raise ConstructorError, "skipping [%s]: description file [%s] not found" % (self.__base_dir, tmp)

        self.__data = {}

#       if not self.__load_from_xml():
#           raise ConstructorError, "XML file [%s] cannot be parsed correctly" % anXmlFile

        return None
    #--------------------------------------------------------
    def __load_metadata(self):
        """Load document metadata from XML file.
        """
        # document type
        tmp = self.__get_from_xml(aTag = self.cfg.get(self.__group, "type_tag"), anXMLfile = self.__xml_file)
        if tmp is None:
            _log.error("cannot load document type.")
            return None
        else:
            self.__data['type'] = string.join(tmp)
        # document comment
        tmp = self.__get_from_xml(aTag = self.cfg.get(self.__group, "comment_tag"), anXMLfile = self.__xml_file)
        if tmp is None:
            _log.error("cannot load document comment")
            return None
        else:
            self.__data['comment'] = string.join(tmp)
        # document reference date
        tmp = self.__get_from_xml(aTag = self.cfg.get(self.__group, "date_tag"), anXMLfile = self.__xml_file)
        if tmp is None:
            _log.error("cannot load document reference date.")
            return None
        else:
            self.__data['date'] = string.join(tmp)
        # external reference string
        tmp = self.__get_from_xml(aTag = self.cfg.get(self.__group, "ref_tag"), anXMLfile = self.__xml_file)
        if tmp is None:
            _log.error("cannot load document reference string.")
            return None
        else:
            self.__data['reference'] = string.join(tmp)
        # document description
        tmp = self.__get_from_xml(aTag = self.cfg.get(self.__group, "aux_comment_tag"), anXMLfile = self.__xml_file)
        if tmp is None:
            _log.error("cannot load long document description.")
        else:
            self.__data['description'] = string.join(tmp)
        # list of data files
#       if not self.__read_img_list(self.__xml_file, aBaseDir, self.__group):
#           _log.error("Cannot retrieve list of document data files.")
#           return None

        _log.debug("long document description: " + str(self.__data['description']))
        _log.debug("document reference string: " + str(self.__data['reference']))
        _log.debug("document reference date: " + str(self.__data['date']))
        _log.debug("Document comment: " + str(self.__data['comment']))
        _log.debug("Document type: " + str(self.__data['type']))

        return 1
    #--------------------------------------------------------
    # attribute access
    #--------------------------------------------------------
    def __getitem__(self, item):
        try:
            return self.__data[item]
        except KeyError:
            try:
                return xmlDocDesc._get_handler[item](self)
            except KeyError:
                _log.LogException('[%s] neither cached in self.__data nor get handler available' % item, sys.exc_info())
                return None
    #--------------------------------------------------------
    def _get_obj_list(self):
        try:
            return self.__data['objects']
        except KeyError:
            self.__load_obj_list()
            return self.__data['objects']
        return None
    #--------------------------------------------------------
    _get_handler['objects'] = _get_obj_list
    #--------------------------------------------------------
    def __load_obj_list(self):
        """Read list of image files from XML metadata file.

        We assume the order of file names to correspond to the sequence of pages.
        - don't use self.__get_from_xml, because we want to
          scan lines sequentially here
        """
        self.__data['objects'] = {}
        tag_name = self.__cfg.get(self.__group, "obj_tag")
        # now scan the xml file
        idx = 0
        for line in fileinput.input(self.__xml_file):
            content = self.__extract_xml_content(line, tag_name)
            if content is None:
                continue
            idx += 1
            tmp = {}
            tmp['file name'] = os.path.abspath(os.path.join(self.__base_dir, content))
            # this 'index' defines the order of objects in the document
            tmp['index'] = idx
            # we must use imaginary oid's since we are reading from a file,
            # this OID defines the object ID in the data store, this
            # has nothing to do with the semantic order of objects
            self.__data['objects'][idx] = tmp

        # cleanup
        fileinput.close()

        if idx == 0:
            _log.warning("no files found for import")
            return None

        _log.debug("document data files to be processed: %s" % self.__data['objects'])

        return 1        
    #--------------------------------------------------------
    # public methods
    #--------------------------------------------------------
    def remove_object(self, anObjID = None):
        print "remove_object: FIXME !!"
        print anObjID
        return 1
    #--------------------------------------------------------
    def __get_from_xml(self, aTag = None):
        # sanity
        if not type(aTag) is types.StringType:
            _log.error("Argument aTag (" + str(aTag) + ") is not a string.")
            return None

        TagStart = "<" + aTag + ">"
        TagEnd = "</" + aTag + ">"

        _log.info("Retrieving " + TagStart + "content" + TagEnd + ".")

        inTag = 0
        content = []

        for line in fileinput.input(self.__xml_file):
            tmp = line

            # this line starts a description
            if string.find(tmp, TagStart) != -1:
                inTag = 1
                # strip junk left of <tag>
                (junk, good_stuff) = string.split (tmp, TagStart, 1)
                _log.debug("Found tag start in line: junk='%s' content='%s'" % (junk, good_stuff))
                tmp = good_stuff

            # this line ends a description
            if string.find(tmp, TagEnd) != -1:
                # only if tag start has been found already
                if inTag == 1:
                    # strip junk right of </tag>
                    (good_stuff, junk) = string.split (tmp, TagEnd, 1)
                    _log.debug("Found tag end in line: junk='%s' content='%s'" % (junk, good_stuff))
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
            _log.debug("%s tag content successfully read: %s" % (TagStart, str(content)))
            return content
        else:
            return None

    #--------------------------------------------------------
    def __extract_xml_content(self, aLine, aTag):
        # is this a line we care about ?
        start_tag_pos = string.find(aLine,'<%s' % aTag)
        if start_tag_pos == -1:
            return None
        # yes, so check for closing tag
        end_tag_pos = string.find(aLine, '</%s>' % aTag)
        if end_tag_pos == -1:
            # but we don't do multiline tags
            _log.error("Line [%s] is incomplete for tag [%s]. We don't do multiline tags here."  % (aLine, aTag))
            return None
        # actually extract content
        content_start = string.find(aLine,'>', start_tag_pos, end_tag_pos) + 1
        return aLine[content_start:end_tag_pos]
#============================================================
# main
#------------------------------------------------------------

#============================================================
# $Log: gmXmlDocDesc.py,v $
# Revision 1.5  2008-01-30 13:34:50  ncq
# - switch to std lib logging
#
# Revision 1.4  2004/03/19 17:07:20  shilbert
# - import statement fixed
#
# Revision 1.3  2004/02/25 09:46:20  ncq
# - import from pycommon now, not python-common
#
# Revision 1.2  2003/11/17 10:56:35  sjtan
#
# synced and commiting.
#
# Revision 1.1  2003/10/23 06:02:38  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.1  2003/04/20 15:42:27  ncq
# - first version
#
