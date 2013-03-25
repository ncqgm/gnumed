# Copyright (C) 2009, 2010, 2011  Rickard Lindberg, Roger Lindberg
#
# This file is part of Timeline.
#
# Timeline is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Timeline is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Timeline.  If not, see <http://www.gnu.org/licenses/>.


"""
A simple, validating, SAX-based XML parser.

Since it is simple, it has some limitations:

    - It can not parse attributes
    - It can not parse arbitrary nested structures
    - It can only parse text in leaf nodes: in other words, this piece of XML
      is not possible to parse: <a>some text <b>here</b> and there</a>

Here's an example how to parse a simple XML document using this module.

First we create a file-like object containing the XML data (any file-like
object is fine, but we create a StringIO for the purpose of making a working
example):

    >>> from StringIO import StringIO

    >>> xml_stream = StringIO('''
    ... <db>
    ...     <person>
    ...         <name>Rickard</name>
    ...     </person>
    ...     <person>
    ...         <name>James</name>
    ...         <age>38</age>
    ...     </person>
    ... </db>
    ... ''')

Then we define two parser functions that we later associate with Tag objects.
Parse functions are called when the end tag has been read. The first argument
to a parse function is the text that the tag contains. It will be empty for all
tags except leaf tags. The second argument is a dictionary that can be used to
store temporary variables. This dictionary is passed to all parse functions,
providing a way to share information between parse functions.

    >>> def parse_name(text, tmp_dict):
    ...     tmp_dict["tmp_name"] = text

    >>> def parse_person(text, tmp_dict):
    ...     # text is empty here since person is not a leaf tag
    ...     name = tmp_dict.pop("tmp_name")
    ...     age = tmp_dict.pop("tmp_age", None)
    ...     print("Found %s in db." % name)
    ...     if age is not None:
    ...         print("%s is %s years old." % (name, age))

Next we define the structure of the XML document that we are going to parse by
creating Tag objects. The first argument is the name of the tag, the second
specifies how many times it can occur inside its parent (should be one of
SINGLE, OPTIONAL, or ANY), the third argument is the parse function to be used
for this tag (can be None if no parsing is needed), and the fourth argument is
a list of child tags.

    >>> root_tag = Tag("db", SINGLE, None, [
    ...     Tag("person", ANY, parse_person, [
    ...         Tag("name", SINGLE, parse_name),
    ...         Tag("age", OPTIONAL, parse_fn_store("tmp_age")),
    ...     ]),
    ... ])

The parse_fn_store function returns a parser function that works exactly like
parse_name: it takes the text of the tag and stores it in the dictionary with
the given key (tmp_age in this case).

The last step is to call the parse function with the stream, the tag
configuration, and a dictionary. The dictionary can be populated with values
before parsing starts if needed.

    >>> parse(xml_stream, root_tag, {})
    Found Rickard in db.
    Found James in db.
    James is 38 years old.

The parse function will raise a ValidationError if the XML is not valid and a
SAXException the if the XML is not well-formed.
"""


from xml.sax import parse as sax_parse
import sys
import xml.sax.handler


# Occurrence rules for tags
SINGLE = 1
OPTIONAL = 2
ANY = 3


class ValidationError(Exception):
    """Raised when parsed xml document does not follow the schema."""
    pass


class Tag(object):
    """
    Represents a tag in an xml document.

    Used to define structure of an xml document and define parser functions for
    individual parts of an xml document.

    Parser functions are called when the end tag has been read.

    See SaxHandler class defined below to see how this class is used.
    """

    def __init__(self, name, occurrence_rule, parse_fn, child_tags=[]):
        self.name = name
        self.occurrence_rule = occurrence_rule
        self.parse_fn = parse_fn
        self.child_tags = []
        self.add_child_tags(child_tags)
        self.parent = None
        # Variables defining state
        self.occurrences = 0
        self.next_possible_child_pos = 0
        self.start_read = False

    def add_child_tags(self, tags):
        for tag in tags:
            self.add_child_tag(tag)

    def add_child_tag(self, tag):
        tag.parent = self
        self.child_tags.append(tag)

    def read_enough_times(self):
        return self.occurrences > 0 or self.occurrence_rule in (OPTIONAL, ANY)

    def can_read_more(self):
        return self.occurrences == 0 or self.occurrence_rule == ANY

    def handle_start_tag(self, name, tmp_dict):
        if name == self.name:
            if self.start_read == True:
                # Nested tag
                raise ValidationError("Did not expect <%s>." % name)
            else:
                self.start_read = True
                return self
        elif self.start_read == True:
            next_child = self._find_next_child(name)
            return next_child.handle_start_tag(name, tmp_dict)
        else:
            raise ValidationError("Expected <%s> but got <%s>."
                                  % (self.name, name))

    def handle_end_tag(self, name, text, tmp_dict):
        self._ensure_end_tag_valid(name, text)
        if self.parse_fn is not None:
            self.parse_fn(text, tmp_dict)
        self._ensure_all_children_read()
        self._reset_parse_data()
        self.occurrences += 1
        return self.parent

    def _ensure_end_tag_valid(self, name, text):
        if name != self.name:
            raise ValidationError("Expected </%s> but got </%s>."
                                  % (self.name, name))
        if self.child_tags:
            if text.strip():
                raise ValidationError("Did not expect text but got '%s'."
                                      % text)

    def _ensure_all_children_read(self):
        num_child_tags = len(self.child_tags)
        while self.next_possible_child_pos < num_child_tags:
            child = self.child_tags[self.next_possible_child_pos]
            if not child.read_enough_times():
                raise ValidationError("<%s> not read enough times."
                                      % child.name)
            self.next_possible_child_pos += 1

    def _reset_parse_data(self):
        for child_tag in self.child_tags:
            child_tag.occurrences = 0
        self.next_possible_child_pos = 0
        self.start_read = False

    def _find_next_child(self, name):
        num_child_tags = len(self.child_tags)
        while self.next_possible_child_pos < num_child_tags:
            child = self.child_tags[self.next_possible_child_pos]
            if child.name == name:
                if child.can_read_more():
                    return child
                else:
                    break
            else:
                if child.read_enough_times():
                    self.next_possible_child_pos += 1
                else:
                    break
        raise ValidationError("Did not expect <%s>." % name)


class SaxHandler(xml.sax.handler.ContentHandler):

    def __init__(self, root_tag, tmp_dict):
        self.tag_to_parse = root_tag
        self.tmp_dict = tmp_dict
        self.text = ""

    def startElement(self, name, attrs):
        """
        Called when a start tag has been read.
        """
        if attrs.getLength() > 0:
            raise ValidationError("Did not expect attributes on <%s>." % name)
        if self.text.strip():
            raise ValidationError("Did not expect text but got '%s'."
                                  % self.text)
        self.tag_to_parse = self.tag_to_parse.handle_start_tag(name,
                                                               self.tmp_dict)
        self.text = ""

    def endElement(self, name):
        """
        Called when an end tag (and everything between the start and end tag)
        has been read.
        """
        self.tag_to_parse = self.tag_to_parse.handle_end_tag(name, self.text,
                                                             self.tmp_dict)
        self.text = ""

    def characters(self, content):
        self.text += content


def parse(xml, schema, tmp_dict):
    """
    xml should be a filename or a file-like object containing xml data.

    schema should be a Tag object defining the structure of the xml document.

    tmp_dict is used by parser functions in Tag objects to share data. It can
    be pre-populated with values.
    """
    if isinstance(xml, unicode):
        # Workaround for "Sax parser crashes if given unicode file name" bug:
        # http://bugs.python.org/issue11159
        xml = xml.encode(sys.getfilesystemencoding())
    sax_parse(xml, SaxHandler(schema, tmp_dict))


def parse_fn_store(store_key):
    def fn(text, tmp_dict):
        tmp_dict[store_key] = text
    return fn
