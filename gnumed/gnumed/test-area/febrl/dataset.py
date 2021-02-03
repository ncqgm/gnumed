# =============================================================================
# dataset.py - Access to various data set implementations (CSV, SQL, etc.)
#
# Freely extensible biomedical record linkage (Febrl) Version 0.2.2
# See http://datamining.anu.edu.au/projects/linkage.html
#
# =============================================================================
# AUSTRALIAN NATIONAL UNIVERSITY OPEN SOURCE LICENSE (ANUOS LICENSE)
# VERSION 1.1
#
# The contents of this file are subject to the ANUOS License Version 1.1 (the
# "License"); you may not use this file except in compliance with the License.
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for
# the specific language governing rights and limitations under the License.
# The Original Software is "dataset.py".
# The Initial Developers of the Original Software are Dr Peter Christen
# (Department of Computer Science, Australian National University) and Dr Tim
# Churches (Centre for Epidemiology and Research, New South Wales Department
# of Health). Copyright (C) 2002, 2003 the Australian National University and
# others. All Rights Reserved.
# Contributors:
#
# =============================================================================

"""Module dataset.py - Access to various data set implementations.

   Currently implemented data sets are:

   For sequential and block wise access:
     COL     Column wise fields (with fixed width) text files
     CSV     Comma Separated Values text files
     SQL     SQL database access to MySQL

   For random (direct) access:
     Shelve  Python 'shelve' based (files based dictionary)
     Memory  Python dictionary 'in memory' based.

   The two base classes are 'DataSet' and 'RandomDataSet', with different
   access methods and attributes.

   See the doc strings of individual classes and methods for detailed
   documentation.

   For parallel runs of Febrl the flag 'writemode' in module parallel is used
   to determine if only the host process is writing into data sets or all
   processes are writing into local data sets (in which case the process number
   is added to the file names).
   For SQL data sets only the 'host' writing mode is currently possible.
"""

# =============================================================================
# Imports go here

import string
import sys
import os
import xreadlines
import shelve

import parallel  # Needed to determine parallel write mode ('host' or 'all')
import tcsv      # Tim Churches' CSV parser

try:
  import MySQLdb  # Python database API for MySQL
  # print '1:***** Using "MySQLdb" module for DataSetSQL *****'
except:
  print 'warning:No mySQL module available'

try:
  import pgdb
except:
  print "warning:no pgdb module available"

try:
  import bsddb3  # Import Berkely database module
  shelve_type = 'BSDDB3'
  # print '1:***** using "bsddb3" module for DataSetShelve *****'

except:
  print 'warning:No bsddb3 available, use normal shelve'
  shelve_type = 'SHELVE'

# =============================================================================

class DataSet:
  """class DataSet - The base class for sequential and block wise access.

   The 'DataSet' class and all its derived classes provide methods for
   sequenctial and block wise read and write access to various data set
   implementations (currently CSV and SQL).

   Currently a data set can consists of one underlying file or table only.

   Each record in a data set is made of fields. A dictionary with the field
   names as keys needs to be given when a data set is initialised. The values
   in this dictionary depend on the data set type (e.g. column numbers for CSV
   files, or the names of the attributes in an SQL table).

   Records are returned as dictionaries with the keys being the field names and
   the field values being the data from the data set. Only non-empty field
   values are stored in these dictionaries. All values returned are strings,
   even if they are numbers, e.g. dates.

   For each record two 'hidden' fields are returned, namely '_rec_num_'
   (the record number) and '_dataset_name_' (the name of the data set it is
   loaded from).

   Use the flag 'strip_fields' (set to True) to strip whitespaces off fields
   before they are stored in a record dictionary (or if records are written to
   a data set). As default, fields are stripped.

   All strings are converted to lower case before they are returned.

   BASE METHODS
     __init__()                   The constructor. Initialises a data set in
                                  either 'read', 'write' or 'append' access
                                  mode. With 'write' access all records stored
                                  in a data set are deleted first, before
                                  writing is started, while with 'append'
                                  existing records a kept.
     finalise()                   Finalise access to a data set (close files or
                                  disconnent from database, etc).
     read_record()                For sequential reading of one record after
                                  another. Increases the 'next_record_num' by 1
                                  if a record has been read successfully.
     read_records(first, number)  For block wise reading of records. After a
                                  block of records is read successfully, the
                                  'next_record_num' is set to the number of the
                                  record following the block.
     write_records(record_list)   For block wise writing of records. Increases
                                  the 'next_record_num' by the number of
                                  records in the block.
     write_record(record)         Write (append) one record. Increases the
                                  'next_record_num' by one.

   BASE ATTRIBUTES
     name                The name of the data set.
     description         A longer description of the data set.
     access_mode         The data set's access mode, which can be either
                         'read', 'write', or 'append'.
     fields              Basic fields (columns, attributes) in the data set.
     fields_default      Default string if a field is not found. Used for
                         writing and by the field comparison functions (see
                         'comparison.py').
     strip_fields        A flag (True/False) stating if whitespaces should be
                         stripped off fields before they are returned.
     next_record_num     The number of the next record to read or write.
     num_records         Total number of records in the data set.
     missing_values      A list representation of missing value strings in the
                         data set. These are used by the field comparison
                         functions (see 'comparison.py').

   TODO
   - PC 26/11/2002: Allow multiple files or tables in one data set.
"""

  # ---------------------------------------------------------------------------

  def __init__(self, base_kwargs):
    """Constructor, set general attributes.
    """

    # General attributes for all data sets
    #
    self.name =            None
    self.description =     ''
    self.access_mode =     None
    self.fields =          None
    self.fields_default =  ''
    self.strip_fields =    True
    self.next_record_num = None
    self.num_records =     None
    self.missing_values =  ['']
    self.parallelwrite =   parallel.writemode

    # Process base keyword arguments (all data set specific keywords were
    # processed in the derived class constructor)
    #
    for (keyword, value) in base_kwargs.items():
      if (keyword == 'name'):
        if (not isinstance(value, str)):
          print 'error:Argument "name" must be of type string'
          raise Exception
        self.name = value

      elif (keyword == 'description'):
        self.description = value

      elif (keyword == 'access_mode'):
        if (value not in ['read','write','append']):
          print 'error:Illegal mode for "access_mode": %s' % (str(value))
          raise Exception
        self.access_mode = value

      elif (keyword == 'fields'):
        if (not isinstance(value, dict)):
          print 'error:Argument "fields" must be a dictionary'
          raise Exception
        self.fields = value

      elif (keyword == 'fields_default'):
        if (not isinstance(value, str)):
          print 'error:Argument "fields_default" must be of type string'
          raise Exception
        self.fields_default = value

      elif (keyword == 'strip_fields'):
        if (value not in [True, False]):
          print 'error:Argument "strip_fields" must be "True" or "False"'
          raise Exception
        self.strip_fields = value

      elif (keyword == 'missing_values'):
        if (isinstance(value, str)):
          value = [value]  # Make it a list
        if (not isinstance(value, list)):
          print 'error:Argument "missing_values" must be a string or a '+ \
                'list of strings'
          raise Exception
        self.missing_values = value

      else:
        print 'error:Illegal constructor argument keyword: "%s"' % \
              (str(keyword))
        raise Exception

    # Check if name, access mode and fields are defined - - - - - - - - - - - -
    #
    if (self.name == None):
      print 'error:Data set "name" is not defined'
      raise Exception

    if (self.fields == None):
      print 'error:Data set "fields" are not defined'
      raise Exception

    if (self.access_mode == None):
      print 'error:Data set "access_mode" not defined'
      raise Exception

  # ---------------------------------------------------------------------------

  def finalise(self):
    """Finalise a data set.
       See implementations in derived classes for details.
    """

    print 'error:Override abstract method in derived class'
    raise Exception

  # ---------------------------------------------------------------------------

  def read_records(self, first, number):
    """Read and return a block of records.
       See implementations in derived classes for details.
    """

    print 'error:Override abstract method in derived class'
    raise Exception

  # ---------------------------------------------------------------------------

  def read_record(self):
    """Read the next record, advance by one record.
       See implementations in derived classes for details.
    """

    print 'error:Override abstract method in derived class'
    raise Exception

  # ---------------------------------------------------------------------------

  def write_records(self, record_list):
    """Write a block of records.
       See implementations in derived classes for details.
    """

    print 'error:Override abstract method in derived class'
    raise Exception

  # ---------------------------------------------------------------------------

  def write_record(self, record):
    """Write one record.
       See implementations in derived classes for details.
    """

    print 'error:Override abstract method in derived class'
    raise Exception

# =============================================================================

class DataSetCOL(DataSet):
  """class DataSetCOL

     Implementation of a column wise fields (with fixed width) data set class.

     This data set does not allow the 'readwrite' or 'readappend' access modes,
     i.e. it must be initialised in modes 'read', 'write', or 'append'.

     The 'fields' attribute must contain pairs of field names and tuples with
     start (starting from zero) and length values (start,length).

     DERIVED CLASS ATTRIBUTES
       file_name         A string containing the name of the underlying CSV
                         file.
       header_lines      Number of header lines in the file to be skipped in
                         read access mode. Default is no header line (value 0).
       write_header      A flag, if set to "True" a header line with the field
                         names is written into the output file.
       field_list        A list of the field names sorted according to the
                         column numbers.
       last_col_number   Number of the last column in a line (starting with 0)
  """

  # ---------------------------------------------------------------------------

  def __init__(self, **kwargs):
    """Constructor, set derived attributes, call base class constructor for
       base attributes.
    """

    self.dataset_type =    'COL'
    self.file_name =       None   # The name of the COL file
    self.header_lines =    0      # Default no header lines
    self.write_header =    False  # Flag, set to not write header line
    self.file =            None   # File pointer to current file
    self.field_list =      []     # Field name list sorted according to column
                                  # numbers
    self.last_col_number = 0      # Number of the last column

    # Process all keyword arguments
    #
    base_kwargs = {}  # Dictionary, will contain unprocessed arguments

    for (keyword, value) in kwargs.items():
      if (keyword == 'file_name'):
        if (not isinstance(value, str)):
          print 'error:Argument "file_name" is not a string'
          raise Exception
        self.file_name = value

      elif (keyword == 'header_lines'):
        if (not isinstance(value, int) or (value < 0)):
          print 'error:Argument "header_lines" is not a positive integer '+ \
                'number'
          raise Exception
        self.header_lines = value

      elif (keyword == 'write_header'):
        if (value not in [True, False]):
          print 'error:Value of argument "write_header" must be "True" or '+ \
                '"False"'
          raise Exception
        self.write_header = value

      else:
        base_kwargs[keyword] = value

    if (self.file_name == None):
      print 'error:File name not defined'
      raise Exception

    DataSet.__init__(self, base_kwargs)  # Process base arguments

    # Check if the values in the 'fields' arguments are all tuples with
    # start and length values
    #
    fields_names =   []
    fields_starts =  []
    fields_lengths = []

    for (field_name, field_values) in self.fields.items():

      start_val = field_values[0]
      length_val = field_values[1]

      if (not isinstance(start_val, int) or (start_val < 0)):
        print 'error:Start value of field "%s" must be zero or positive' % \
              (field_name)
        raise Exception

      if (not isinstance(length_val, int) or (length_val <= 0)):
        print 'error:Length value of field "%s" must be positive' % \
              (field_name)
        raise Exception

      fields_names.append(field_name)
      fields_starts.append(start_val)
      fields_lengths.append(length_val)

      if ((start_val+length_val) > self.last_col_number):
        self.last_col_number = start_val+length_val

    # Create sorted list of fields (according to start column)
    #
    self.field_list = map(None, fields_starts, fields_lengths, fields_names)
    self.field_list.sort()

    # Now perform various checks for each access mode - - - - - - - - - - - - -

    if (self.access_mode == 'read'):  # - - - - - - - - - - - - - - - - - - - -

      # Try to open the file in read mode
      #
      try:
        self.file = open(self.file_name,'r')
      except:
        print 'error:Can not open file: "%s" for reading' % (self.file_name)
        raise IOError

      # Count number of records in the file
      #
      if (sys.platform[0:5] in ['linux','sunos']):  # Fast line counting
        wc = os.popen('wc -l ' + self.file_name)
        num_rows = int(string.split(wc.readline())[0])
        wc.close()
      else:  # Slow line counting method
        num_rows = 0
        fp = open(self.file_name,'r')
        for l in fp.xreadlines():
          num_rows += 1
        fp.close()

      self.num_records =     num_rows - self.header_lines
      self.next_record_num = 0

      # Check that there are records in the data set
      #
      if (self.num_records <= 0):
        print 'error:No records in data set'
        raise Exception

      # Skip over header lines if there are
      #
      if (self.header_lines > 0):
        for i in range(self.header_lines):
          self.file.readline()

    elif (self.access_mode == 'write'):   # - - - - - - - - - - - - - - - - - -

      # Modify file name if parallel write mode is set to 'all'
      #
      if (self.parallelwrite == 'all'):
        self.file_name = self.file_name+'-P%i' % (parallel.rank())

      # Make sure fields are not overlapping and are continuous (no gaps)
      #
      col_count = 0

      for (field_start, field_length, field_name) in self.field_list:

        if (col_count != field_start):
          print 'error:Illegal field start value %i for field "%s"' % \
                (field_start, field_name)
          raise Exception

        col_count += field_length  # Increase column counter by field length,
                                   # this should be start column of next field

      # Now only initialize file according to parallel write mode
      #
      if (self.parallelwrite == 'all') or \
         ((self.parallelwrite == 'host') and (parallel.rank() == 0)):

        # Try to open the file in write mode
        #
        try:
          self.file = open(self.file_name,'w')
        except:
          print 'error:Can not open file: "%s" for writing' % (self.file_name)
          raise IOError

        # Write the header line with field names if desired
        #
        if (self.write_header == True):
          header_line = ''

          for (field_start, field_length, field_name) in self.field_list:

            if (self.strip_fields == True):
              field_name = field_name.strip()

            # Make sure field names have length of fields
            #
            header_line += field_name[:field_length].ljust(field_length)

          #print '1:####write: '+str(self.field_list)
          #print '1:####       '+header_line

          self.file.write(header_line+os.linesep)  # Write header line
          self.file.flush()

      else:  # Don't initialise file

        self.file = None

      self.num_records =     0
      self.next_record_num = 0

    elif (self.access_mode == 'append'):  # - - - - - - - - - - - - - - - - - -

      # Modify file name if parallel write mode is set to 'all'
      #
      if (self.parallelwrite == 'all'):
        self.file_name = self.file_name+'-P%i' % (parallel.rank())

      # Make sure fields are not overlapping and are continuous (no gaps)
      #
      col_count = 0

      for (field_start, field_length, field_name) in self.field_list:

        if (col_count != field_start):
          print 'error:Illegal field start value %i for field "%s"' % \
                (field_start, field_name)
          raise Exception

        col_count += field_length  # Increase column counter by field length,
                                   # this should be start column of next field

      # Now only initialize file according to parallel write mode
      #
      if (self.parallelwrite == 'all') or \
         ((self.parallelwrite == 'host') and (parallel.rank() == 0)):

        # Try to open the file in append mode
        #
        try:
          self.file = open(self.file_name,'a')
        except:
          print 'error:Can not open file: "%s" for appending' % \
                (self.file_name)
          raise IOError

        # Count number of records in the file
        #
        if (sys.platform[0:5] in ['linux','sunos']):  # Fast line counting
          wc = os.popen('wc -l ' + self.file_name)
          num_rows = int(string.split(wc.readline())[0])
          wc.close()
        else:  # Slow line counting method
          num_rows = 0
          fp = open(self.file_name,'r')
          for l in fp.xreadlines():
            num_rows += 1
          fp.close()

        # If no records are stored write header if needed
        #
        if (num_rows == 0) and (self.write_header == True):
          header_line = ''

          for (field_start, field_length, field_name) in self.field_list:

            if (self.strip_fields == True):
              field_name = field_name.strip()

            # Make sure field names have length of fields
            #
            header_line += field_name[:field_length].ljust(field_length)

          #print '1:####append: '+str(self.field_list)
          #print '1:####        '+header_line

          self.file.write(header_line+os.linesep)  # Write header line
          self.file.flush()

        self.num_records =     num_rows - self.header_lines
        self.next_record_num = self.num_records

      else:  # Don't initialise file

        self.file = None

        self.num_records =     0
        self.next_record_num = 0

    else:  # Illegal data set access mode - - - - - - - - - - - - - - - - - - -
      print 'error:Illegal data set access mode: "%s"' % \
            (str(self.access_mode))
      raise Exception

    # A log message for low volume log output (level 1) - - - - - - - - - - - -
    #
    print '1:'
    print '1:Initialised COL data set "%s"' % (self.name)
    print '1:  In access mode: %s' % (self.access_mode)
    print '1:  Parallel write: %s' % (self.parallelwrite)
    print '1:  File name:      %s' % (self.file_name)
    print '1:  Fields:         %s' % (str(self.fields))
    print '2:  Fields list:    %s' % (str(self.field_list))
    print '2:  Write header:   %s' % (str(self.write_header))
    print '2:  Header lines:   %i' % (self.header_lines)
    print '2:  Strip fields:   %s' % (str(self.strip_fields))
    print '2:  Missing values: %s' % (str(self.missing_values))
    print '1:  Number of records: %i' % (self.num_records)

  # ---------------------------------------------------------------------------

  def finalise(self):
    """Finalise a data set, i.e. close the file and set various attributes to
       None.
    """

    # Close file if it is open
    #
    if (self.file != None):
      self.file.close()
      self.file = None

    self.access_mode =     None
    self.file_name =       None
    self.write_header =    None
    self.next_record_num = None
    self.num_records =     None
    self.last_col_number = 0

    # A log message for low volume log output (level 1) - - - - - - - - - - - -
    #
    print '1:'
    print '1:Finalised COL data set "%s"' % (self.name)

  # ---------------------------------------------------------------------------

  def read_records(self, first, number):
    """Read and return a block of records.
    """

    if (self.file == None):
      print 'error:Data set not initialised'
      raise Exception

    if (self.access_mode != 'read'):
      print 'error:Data set not initialised for "read" access'
      raise Exception

    if (first < 0) or ((first+number) > self.num_records):
      print 'error:Selected block of records out of range'
      raise Exception

    # Check if the block is at the current position. If not, we have to change
    # to the desired position
    #
    if (first != self.next_record_num):

      self.file.close()  # Close currently open file

      self.file = open(self.file_name,'r')  # Re-open file

      # Skip over header (if there is one) and skip to first record
      #
      for i in range(self.header_lines+first):
        self.file.readline()

    self.next_record_num = first  # Update record counter

    # Now read the desired number of records
    #
    rec_list = []  # Each line becomes an entry in this list

    for i in range(number):

      file_line = self.file.readline()  # Read one line

      # Process the file line (make lower case, split, make a dictionary) - - -
      #
      file_line = file_line.lower()

      rec_dict = {}  # A new dictionary for this record

      for (field_start, field_length, field_name) in self.field_list:

        field_data = file_line[field_start:field_start+field_length]

        if (self.strip_fields == True):  # Strip off white spaces first
          field_data = field_data.strip()
        if (field_data != ''):  # Only add non-empty fields to dictionary
          rec_dict[field_name] = field_data

      # Set hidden fields
      #
      rec_dict['_rec_num_'] = self.next_record_num
      rec_dict['_dataset_name_'] = self.name

      rec_list.append(rec_dict)  # Append to the list of records

      self.next_record_num += 1  # Set counter to next record

      # A log message for high volume log output (level 3)  - - - - - - - - - -
      #
      print '3:    Read record from data set: %s ' % (str(rec_dict))

    # A log message for medium volume log output (level 2)  - - - - - - - - - -
    #
    print '2:  Read record block %i to %i' % (first, first+number-1)

    return rec_list

  # ---------------------------------------------------------------------------

  def read_record(self):
    """Read the next record, advance to next record.
    """

    if (self.file == None):
      print 'error:Data set not initialised'
      raise Exception

    if (self.access_mode != 'read'):
      print 'error:Data set not initialised for "read" access'
      raise Exception

    file_line = self.file.readline()  # Read one line

    if (file_line == ''):  # Empty line, corresponds to end of file (EOF)
      return None

    else:
      self.next_record_num += 1  # Set counter to next record

      file_line = file_line.lower()  # Make it all lowercase

      return_rec = {}  # Return record as a dictionary

      for (field_start, field_length, field_name) in self.field_list:

        field_data = file_line[field_start:field_start+field_length]

        if (self.strip_fields == True):  # Strip off white spaces first
          field_data = field_data.strip()
        if (field_data != ''):  # Only add non-empty fields to dictionary
          return_rec[field_name] = field_data

      # Set hidden fields
      #
      return_rec['_rec_num_'] = self.next_record_num
      return_rec['_dataset_name_'] = self.name

    # A log message for high volume log output (level 3)  - - - - - - - - - - -
    #
    print '3:    Read record %i' % (self.next_record_num-1)

    return return_rec

  # ---------------------------------------------------------------------------

  def write_records(self, record_list):
    """Write a block of records by appending them to the end of a file.
    """

    # Check parallel write mode
    #
    if (self.parallelwrite == 'host') and (parallel.rank() > 0):
      return  # Don't write if not host process

    if (self.file == None):
      print 'error:Data set not initialised'
      raise Exception

    if (self.access_mode not in ['write','append']):
      print 'error:Data set not initialised for  "write" or "append" access'
      raise Exception

    for rec in record_list:

      if (not isinstance(rec, dict)):
        print 'error:Illegal record type: "%s", must be a dictionary' % \
              (str(type(rec)))
        raise Exception

      # Convert record dictionary into a line to be written to file
      #
      rec_line = ''

      for (field_start, field_length, field_name) in self.field_list:

        field_data = rec.get(field_name,self.fields_default)

        rec_line += field_data[:field_length].ljust(field_length)

      #print '1:####write: '+str(rec)
      #print '1:####       '+rec_line

      self.file.write(rec_line+os.linesep)  # Write record to file

      # A log message for high volume log output (level 3)  - - - - - - - - - -
      #
      print '3:    Wrote record to data set: %s' % (str(rec))

    self.next_record_num += len(record_list)
    self.num_records +=     len(record_list)

    self.file.flush()

    # A log message for medium volume log output (level 2)  - - - - - - - - - -
    #
    print '2:  Wrote record block %i to %i' % \
          (self.next_record_num-len(record_list), self.next_record_num-1)

  # ---------------------------------------------------------------------------

  def write_record(self, record):
    """Write one record.
    """

    self.write_records([record])

# =============================================================================

class DataSetCSV(DataSet):
  """class DataSetCSV

     Implementation of a CSV (comma separated values) data set class.

     This data set does not allow the 'readwrite' or 'readappend' access modes,
     i.e. it must be initialised in modes 'read', 'write', or 'append'.

     The 'fields' attribute must contain pairs of field names and column
     numbers (starting from zero).

     DERIVED CLASS ATTRIBUTES
       file_name         A string containing the name of the underlying CSV
                         file.
       header_lines      Number of header lines in the file to be skipped in
                         read access mode. Default is no header line (value 0).
       write_header      A flag, if set to "True" a header line with the field
                         names is written into the output file.
       field_list        A list of the field names sorted according to the
                         column numbers.
       tot_field_number  The total number of fields in the data set.
       write_quote_char  A quote character, used when writing to file. Default
                         is no quote character (empty string '').
  """

  # ---------------------------------------------------------------------------

  def __init__(self, **kwargs):
    """Constructor, set derived attributes, call base class constructor for
       base attributes.
    """

    self.dataset_type =     'CSV'
    self.file_name =        None   # The name of the CSV file
    self.header_lines =     0      # Default no header lines
    self.write_header =     False  # Flag, set to not write header line
    self.file =             None   # File pointer to current file
    self.field_list =       []     # Field name list sorted according to column
                                   # numbers
    self.tot_field_number = 0      # The total field (column) number
    self.write_quote_char = ''     # The quote character for writing fields

    # Process all keyword arguments
    #
    base_kwargs = {}  # Dictionary, will contain unprocessed arguments

    for (keyword, value) in kwargs.items():
      if (keyword == 'file_name'):
        if (not isinstance(value, str)):
          print 'error:Argument "file_name" is not a string'
          raise Exception
        self.file_name = value

      elif (keyword == 'header_lines'):
        if (not isinstance(value, int) or (value < 0)):
          print 'error:Argument "header_lines" is not a positive integer '+ \
                'number'
          raise Exception
        self.header_lines = value

      elif (keyword == 'write_header'):
        if (value not in [True, False]):
          print 'error:Value of argument "write_header" must be "True" or '+ \
                '"False"'
          raise Exception
        self.write_header = value

      elif (keyword == 'write_quote_char'):
        if (not isinstance(value, str)):
          print 'error:Argument "write_quote_char" must be a string'
          raise Exception
        self.write_quote_char = value

      else:
        base_kwargs[keyword] = value

    if (self.file_name == None):
      print 'error:File name not defined'
      raise Exception

    DataSet.__init__(self, base_kwargs)  # Process base arguments

    # Check if the values in the 'fields' arguments are all positive integer
    # numbers (column numbers)
    #
    fields_names =     []
    fields_positions = []

    for (field_name, field_col) in self.fields.items():
      fields_names.append(field_name)

      if (not isinstance(field_col, int) or (field_col < 0)):
        print 'error:Value of field column "%s" must be zero or positive' % \
              (field_name)
        raise Exception
      fields_positions.append(field_col)

    self.tot_field_number = max(fields_positions)+1  # Number is last index + 1

    # Create sorted list of fields
    #
    self.field_list = map(None, fields_positions, fields_names)
    self.field_list.sort()

    # Initialise the CSV line parser
    #
    self.csv_parser = tcsv.delimited_parser(delimiter_chars=',', as_strings=1)

    # Now perform various checks for each access mode - - - - - - - - - - - - -

    if (self.access_mode == 'read'):  # - - - - - - - - - - - - - - - - - - - -

      # Try to open the file in read mode
      #
      try:
        self.file = open(self.file_name,'r')
      except:
        print 'error:Can not open file: "%s" for reading' % (self.file_name)
        raise IOError

      # Count number of records in the file
      #
      if (sys.platform[0:5] in ['linux','sunos']):  # Fast line counting
        wc = os.popen('wc -l ' + self.file_name)
        num_rows = int(string.split(wc.readline())[0])
        wc.close()
      else:  # Slow line counting method
        num_rows = 0
        fp = open(self.file_name,'r')
        for l in fp.xreadlines():
          num_rows += 1
        fp.close()

      self.num_records =     num_rows - self.header_lines
      self.next_record_num = 0

      # Check that there are records in the data set
      #
      if (self.num_records <= 0):
        print 'error:No records in data set'
        raise Exception

      # Skip over header lines if there are
      #
      if (self.header_lines > 0):
        for i in range(self.header_lines):
          self.file.readline()

    elif (self.access_mode == 'write'):   # - - - - - - - - - - - - - - - - - -

      # Modify file name if parallel write mode is set to 'all'
      #
      if (self.parallelwrite == 'all'):
        self.file_name = self.file_name+'-P%i' % (parallel.rank())

      # Now only initialize file according to parallel write mode
      #
      if (self.parallelwrite == 'all') or \
         ((self.parallelwrite == 'host') and (parallel.rank() == 0)):

        # Try to open the file in write mode
        #
        try:
          self.file = open(self.file_name,'w')
        except:
          print 'error:Can not open file: "%s" for writing' % (self.file_name)
          raise IOError

        # Write the header line with field names if desired
        #
        if (self.write_header == True):
          header_line = ''
          j = 0  # Index into fields list
          for i in range(self.tot_field_number):
            if (i == self.field_list[j][0]):
              field_name = self.field_list[j][1]
              if (self.strip_fields == True):
                field_name = field_name.strip()
              header_line = header_line + self.write_quote_char + \
                            field_name + self.write_quote_char + ', '
              j += 1
            else:
              header_line = header_line + ', '  # Not specified field
          self.file.write(header_line[:-2]+os.linesep)  # Write header line
          self.file.flush()

      else:  # Don't initialise file

        self.file = None

      self.num_records =     0
      self.next_record_num = 0

    elif (self.access_mode == 'append'):  # - - - - - - - - - - - - - - - - - -

      # Modify file name if parallel write mode is set to 'all'
      #
      if (self.parallelwrite == 'all'):
        self.file_name = self.file_name+'-P%i' % (parallel.rank())

      # Now only initialize file according to parallel write mode
      #
      if (self.parallelwrite == 'all') or \
         ((self.parallelwrite == 'host') and (parallel.rank() == 0)):

        # Try to open the file in append mode
        #
        try:
          self.file = open(self.file_name,'a')
        except:
          print 'error:Can not open file: "%s" for appending' % \
                (self.file_name)
          raise IOError

        # Count number of records in the file
        #
        if (sys.platform[0:5] in ['linux','sunos']):  # Fast line counting
          wc = os.popen('wc -l ' + self.file_name)
          num_rows = int(string.split(wc.readline())[0])
          wc.close()
        else:  # Slow line counting method
          num_rows = 0
          fp = open(self.file_name,'r')
          for l in fp.xreadlines():
            num_rows += 1
          fp.close()

        # If no records are stored write header if needed
        #
        if (num_rows == 0) and (self.write_header == True):
          header_line = ''
          j = 0  # Index into fields list
          for i in range(self.tot_field_number):
            if (i == self.field_list[j][0]):
              field_name = self.field_list[j][1]
              if (self.strip_fields == True):
                field_name = field_name.strip()
              header_line = header_line + field_name + ', '
              j += 1
            else:
              header_line = header_line + ', '  # Not specified field
          self.file.write(header_line[:-2]+os.linesep)  # Write header line
          self.file.flush()

        self.num_records =     num_rows - self.header_lines
        self.next_record_num = self.num_records

      else:  # Don't initialise file

        self.file = None

        self.num_records =     0
        self.next_record_num = 0

    else:  # Illegal data set access mode - - - - - - - - - - - - - - - - - - -
      print 'error:Illegal data set access mode: "%s"' % \
            (str(self.access_mode))
      raise Exception

    # A log message for low volume log output (level 1) - - - - - - - - - - - -
    #
    print '1:'
    print '1:Initialised CSV data set "%s"' % (self.name)
    print '1:  In access mode: %s' % (self.access_mode)
    print '1:  Parallel write: %s' % (self.parallelwrite)
    print '1:  File name:      %s' % (self.file_name)
    print '1:  Fields:         %s' % (str(self.fields))
    print '2:  Fields list:    %s' % (str(self.field_list))
    print '2:  Write header:   %s' % (str(self.write_header))
    print '2:  Header lines:   %i' % (self.header_lines)
    print '2:  Strip fields:   %s' % (str(self.strip_fields))
    print '2:  Missing values: %s' % (str(self.missing_values))
    print '1:  Number of records: %i' % (self.num_records)

  # ---------------------------------------------------------------------------

  def finalise(self):
    """Finalise a data set, i.e. close the file and set various attributes to
       None.
    """

    # Close file if it is open
    #
    if (self.file != None):
      self.file.close()
      self.file = None

    self.access_mode =     None
    self.file_name =       None
    self.write_header =    None
    self.next_record_num = None
    self.num_records =     None

    # A log message for low volume log output (level 1) - - - - - - - - - - - -
    #
    print '1:'
    print '1:Finalised CSV data set "%s"' % (self.name)

  # ---------------------------------------------------------------------------

  def read_records(self, first, number):
    """Read and return a block of records.
    """

    if (self.file == None):
      print 'error:Data set not initialised'
      raise Exception

    if (self.access_mode != 'read'):
      print 'error:Data set not initialised for "read" access'
      raise Exception

    if (first < 0) or ((first+number) > self.num_records):
      print 'error:Selected block of records out of range'
      raise Exception

    # Check if the block is at the current position. If not, we have to change
    # to the desired position
    #
    if (first != self.next_record_num):

      self.file.close()  # Close currently open file

      self.file = open(self.file_name,'r')  # Re-open file

      # Skip over header (if there is one) and skip to first record
      #
      for i in range(self.header_lines+first):
        self.file.readline()

    self.next_record_num = first  # Update record counter

    # Now read the desired number of records
    #
    rec_list = []  # Each line becomes an entry in this list

    for i in range(number):

      file_line = self.file.readline()  # Read one line

      # Process the file line (make lower case, split, make a dictionary) - - -
      #
      file_line = file_line.lower()

      line_list = self.csv_parser.parse(file_line)
      if (len(line_list) < self.tot_field_number):
        # print 'line_list original:', line_list  #########
        line_list += [''] * (self.tot_field_number-len(line_list))
        # print 'line_list expanded:', line_list  ############
        # print self.tot_field_number  ########

      rec_dict = {}  # A new dictionary for this record

      for (key,value) in self.fields.items():
        field_data = line_list[value]  # Extract field
        if (self.strip_fields == True):  # Strip off white spaces first
          field_data = field_data.strip()
        if (field_data != ''):  # Only add non-empty fields to dictionary
          rec_dict[key] = field_data

      # Set hidden fields
      #
      rec_dict['_rec_num_'] = self.next_record_num
      rec_dict['_dataset_name_'] = self.name

      rec_list.append(rec_dict)  # Append to the list of records

      self.next_record_num += 1  # Set counter to next record

      # A log message for high volume log output (level 3)  - - - - - - - - - -
      #
      print '3:    Read record from data set: %s ' % (str(rec_dict))

    # A log message for medium volume log output (level 2)  - - - - - - - - - -
    #
    print '2:  Read record block %i to %i' % (first, first+number-1)

    return rec_list

  # ---------------------------------------------------------------------------

  def read_record(self):
    """Read the next record, advance to next record.
    """

    if (self.file == None):
      print 'error:Data set not initialised'
      raise Exception

    if (self.access_mode != 'read'):
      print 'error:Data set not initialised for "read" access'
      raise Exception

    file_line = self.file.readline()  # Read one line

    if (file_line == ''):  # Empty line, corresponds to end of file (EOF)
      return None

    else:
      self.next_record_num += 1  # Set counter to next record

      file_line = file_line.lower()  # Make it all lowercase
      line_list = self.csv_parser.parse(file_line)

      return_rec = {}  # Return record as a dictionary

      for (key,value) in self.fields.items():
        field_data = line_list[value]  # Extract field
        if (self.strip_fields == True):  # Strip whitespaces of first
          field_data = field_data.strip()
        if (field_data != ''):  # Only add non-empty fields to dictionary
          return_rec[key] = field_data

      # Set hidden fields
      #
      return_rec['_rec_num_'] = self.next_record_num
      return_rec['_dataset_name_'] = self.name

    # A log message for high volume log output (level 3)  - - - - - - - - - - -
    #
    print '3:    Read record %i' % (self.next_record_num-1)

    return return_rec

  # ---------------------------------------------------------------------------

  def write_records(self, record_list):
    """Write a block of records by appending them to the end of a file.
    """

    # Check parallel write mode
    #
    if (self.parallelwrite == 'host') and (parallel.rank() > 0):
      return  # Don't write if not host process

    if (self.file == None):
      print 'error:Data set not initialised'
      raise Exception

    if (self.access_mode not in ['write','append']):
      print 'error:Data set not initialised for  "write" or "append" access'
      raise Exception

    for rec in record_list:

      if (not isinstance(rec, dict)):
        print 'error:Illegal record type: "%s", must be a dictionary' % \
              (str(type(rec)))
        raise Exception

      # Convert record dictionary into a line to be written to file
      #
      rec_line = ''
      j = 0  # Index into fields list
      for i in range(self.tot_field_number):
        if (i == self.field_list[j][0]):
          field_data = rec.get(self.field_list[j][1],self.fields_default)
          if (self.strip_fields == True):
            field_data = field_data.strip()  # Strip off whitespace
          rec_line = rec_line + self.write_quote_char + field_data + \
                     self.write_quote_char
          j += 1
        rec_line = rec_line + ', '

      self.file.write(rec_line[:-2]+os.linesep)  # Write record to file

      # A log message for high volume log output (level 3)  - - - - - - - - - -
      #
      print '3:    Wrote record to data set: %s' % (str(rec))

    self.next_record_num += len(record_list)
    self.num_records +=     len(record_list)

    self.file.flush()

    # A log message for medium volume log output (level 2)  - - - - - - - - - -
    #
    print '2:  Wrote record block %i to %i' % \
          (self.next_record_num-len(record_list), self.next_record_num-1)

  # ---------------------------------------------------------------------------

  def write_record(self, record):
    """Write one record.
    """

    self.write_records([record])

# =============================================================================

class DataSetSQL(DataSet):
  """class DataSetSQL

     Implementation of a SQL (structured query language) data base access
     class.

     This data set does not allow the 'readwrite' or 'readappend' access modes,
     i.e. it must be initialised in modes 'read', 'write', or 'append'.

     The 'fields' attribute must contain pairs of field names and the
     corresponding SQL column names.

     In write or append mode the SQL data set assumes that the given table is
     already created, i.e. it does not have the functionality to create tables.

     DERIVED CLASS ATTRIBUTES
       table_name           The name of the database tabe.
       database_name        The name of the database to connect to.
       database_user        The user name for the database.
       database_password    The corresponding password, if not set at
                            initialisation, it is queried interactively.
       database_block_size  The maximum number of records read in a block.
                            Default value is 10,000.
  """

  # ---------------------------------------------------------------------------

  def __init__(self, **kwargs):

    if (not sys.modules.has_key('MySQLdb')):
      print 'error:MySQLdb module not available, so SQL data set can not be'+ \
            ' used'
      raise Exception

    self.dataset_type =       'SQL'
    self.database_name =       None  # Database name
    self.database_user =       None  # User name
    self.database_password =   None  # User password
    self.database =            None  # Database object
    self.database_block_size = 10000 # Number of transactions for blocking
    self.field_list =          []    # Field name list sorted according to
                                     # database column numbers
    self.table_name =          ''
    self.tot_field_number = 0     # The total field (column) number

    base_kwargs = {}  # Dictionary, will contain unprocessed arguments

    # Process all keyword arguments
    #
    for (keyword, value) in kwargs.items():
      if (keyword == 'database_name'):
        if (not isinstance(value, str)):
          print 'error:Argument "database_name" is not a string'
          raise Exception
        self.database_name = value

      elif (keyword == 'database_user'):
        if (not isinstance(value, str)):
          print 'error:Argument "database_user" is not a string'
          raise Exception
        self.database_user = value

      elif (keyword == 'database_password'):
        if (not isinstance(value, str)):
          print 'error:Argument "database_password" is not a string'
          raise Exception
        self.database_password = value

      elif (keyword == 'table_name'):
        if (not isinstance(value, str)):
          print 'error:Argument "table_name" is not a string'
          raise Exception
        self.table_name = value

      elif (keyword == 'database_block_size'):
        if (not isinstance(value, int) or (value <= 0)):
          print 'error:Argument "database_block_size" must be a positive '+ \
                'integer'
          raise Exception
        self.database_block_size = value

      else:
        base_kwargs[keyword] = value

    # Check if database attributes are set  - - - - - - - - - - - - - - - - - -
    #
    if (self.database_name == ''):
      print 'error:No database name given'
      raise Exception

    if (self.database_user == ''):
      print 'error:No database user given'
      raise Exception

    if (self.table_name == ''):
      print 'error:Table name is not defined'
      raise Exception

    DataSet.__init__(self, base_kwargs)

    # Check if parallel write is set to 'host'  - - - - - - - - - - - - - - - -
    #
    if (self.parallelwrite != 'host'):
      print 'warning:Parallel write mode for  SQL data set is not "host": %s' \
            % (self.parallelwrite)

    # Only host process will access SQL data base
    #
    if (parallel.rank() > 0):
      return  # All other processes don't do anything

    # Check if the values in the 'fields' arguments are all strings (database
    # column names)
    #
    for (field_name, field_col) in self.fields.items():
      if (not isinstance(field_col, str)):
        print 'error:Field column "%s" is not a string' % (str(field_col))
        raise Exception

    # if no database password is given, query it interactively  - - - - - - - -
    #
    if (self.database_password == None):
      print '*****************************************'
      pwd = raw_input('Please enter database password:')
      print '*****************************************'

    else:
      pwd = self.database_password

    # Connect to the database - - - - - - - - - - - - - - - - - - - - - - - - -
    #
    self.database = MySQLdb.Connect(db=self.database_name, \
                                    user=self.database_user, passwd=pwd)
    pwd = ''  # Delete password

    dbcu = self.database.cursor()  # Get a database cursor

    # Check if the table is available - - - - - - - - - - - - - - - - - - - - -
    #
    query = 'show tables'
    lines = dbcu.execute(query)
    if lines > 0:
      table_name_list = dbcu.fetchall()
    else:
      table_name_list = []  # 'fetchall' returned an empty tuple

    if ((self.table_name,) not in table_name_list):
      print 'error:Table "%s" is not in database "%s"' % \
            (t, self.database_name)
      raise Exception

    # Check if columns are available in the table - - - - - - - - - - - - - - -
    #
    query = 'describe '+self.table_name
    lines = dbcu.execute(query)
    if lines > 0:
      column_name_list = dbcu.fetchall()
    else:
      column_name_list = []  # 'fetchall' returned an empty tuple

    db_field_dict = {}
    col_num = 0  # Column number counter
    column_names = []
    for c in column_name_list:
      column_names.append(c[0])  # Make a list of column names only
      db_field_dict[c[0]] = col_num
      col_num += 1

    self.tot_field_number = col_num

    # Create a sorted list of field names and correspondinmg column numbers - -
    #
    fields_names =     []
    fields_positions = []

    for (field_name, field_sql) in self.fields.items():
      if (field_sql not in column_names):
        print 'error:Column "%s" not in table "%s"' % (field_sql, t)
        raise Exception

      fields_names.append(field_name)
      fields_positions.append(db_field_dict[field_sql])

    self.field_list = map(None, fields_positions, fields_names)
    self.field_list.sort()

    # Now perform various checks for each access mode - - - - - - - - - - - - -
    #
    self.num_records = 0     # Total number of records

    # For 'read' mode, count records  - - - - - - - - - - - - - - - - - - - - -
    #
    if (self.access_mode == 'read'):

      # Count number of records in the table
      #
      query = 'select count(*) from '+self.table_name
      lines = dbcu.execute(query)
      if lines > 0:
        num_records = dbcu.fetchall()
      else:
        num_records = []  # 'fetchall' returned an empty tuple

      if (num_records == []):
        print 'error:Query "%s" returns empty result' % (query)
        raise Exception

      self.num_records =     int(num_records[0][0])
      self.next_record_num = 0

    # For 'write' mode check if all records in table can be deleted - - - - - -
    #
    elif (self.access_mode == 'write'):

      query = 'delete from '+self.table_name
      lines = dbcu.execute(query)
      if lines > 0:
        num_records = dbcu.fetchall()
      else:
        num_records = []  # 'fetchall' returned an empty tuple

      self.num_records =     0
      self.next_record_num = 0

    # For 'append' mode, check how many records are stored  - - - - - - - - - -
    #
    elif (self.access_mode == 'append'):

      query = 'select count(*) from '+self.table_name
      lines = dbcu.execute(query)
      if lines > 0:
        num_records = dbcu.fetchall()
      else:
        num_records = []  # 'fetchall' returned an empty tuple

      if (num_records == []):
        print 'error:Query "%s" returns empty result' % (query)
        raise Exception

      self.num_records =     int(num_records[0][0])
      self.next_record_num = self.num_records

    else:  # Illegal data set access mode - - - - - - - - - - - - - - - - - - -
      print 'error:Illegal data set access mode: "%s"' % \
            (str(self.access_mode))
      raise Exception

    dbcu.close()

    # A log message for low volume log output (level 1) - - - - - - - - - - - -
    #
    print '1:'
    print '1:Initialised SQL data set "%s"' % (self.name)
    print '1:  In access mode: %s' % (self.access_mode)
    print '1:  Parallel write: %s' % (self.parallelwrite)
    print '1:  Database name:  %s' % (self.database_name)
    print '1:  Database user:  %s' % (self.database_user)
    print '1:  Table name:     %s' % (self.table_name)
    print '1:  Fields:         %s' % (str(self.fields))
    print '2:  Fields list:    %s' % (str(self.field_list))
    print '2:  Block size:     %i' % (self.database_block_size)
    print '2:  Strip fields:   %s' % (str(self.strip_fields))
    print '2:  Missing values: %s' % (str(self.missing_values))
    print '1:  Number of records: %i' % (self.num_records)

  # ---------------------------------------------------------------------------

  def finalise(self):
    """Finalise a data set. Disconnect from a database.
    """

    self.database.close()
    self.database = None

    self.access_mode =     None
    self.table_names =     []
    self.table_records =   []
    self.current_table =   None
    self.next_record_num = None

    # A log message for low volume log output (level 1) - - - - - - - - - - - -
    #
    print '1:'
    print '1:Finalised SQL data set "%s"' % (self.name)

  # ---------------------------------------------------------------------------

  def read_records(self, first, number):
    """Read and return a block of records.
    """

    if (self.database == None):
      print 'error:Data set not initialised'
      raise Exception

    if (self.access_mode != 'read'):
      print 'error:Data set not initialised for "read" access'
      raise Exception

    if (first < 0) or ((first+number) > self.num_records):
      print 'error:Selected block of records out of range'
      raise Exception

    dbcu = self.database.cursor()  # Get a database cursor

    # Now read the desired number of records blockwise
    #
    rec_list = []  # Each line becomes an entry in this list

    if (number <= self.database_block_size):

      query = 'select * from '+self.table_name+' limit '+str(first)+', '+ \
              str(number)
      lines = dbcu.execute(query)
      if lines > 0:
        result_list = dbcu.fetchall()
      else:
        result_list = []  # 'fetchall' returned an empty tuple

      if (result_list == []):
        print 'error:Query "%s" returns empty result' % (query)
        raise Exception

    else:
      result_list = []

      start = first
      size  = self.database_block_size
      left  = number

      while (left > 0):
        query = 'select * from '+self.table_name+' limit '+str(start)+', '+ \
              str(size)
        lines = dbcu.execute(query)
        if lines > 0:
          tmp_list = dbcu.fetchall()
        else:
          tmp_list = []  # 'fetchall' returned an empty tuple

        if (tmp_list == []):
          print 'error:Query "%s" returns empty result' % (query)
          raise Exception

        result_list += tmp_list

        # Calculate next block start and size
        #
        start += size
        left -= size

        if (left > self.database_block_size):
          size = self.database_block_size
        else:
          size = left

    # Append all records to record list
    #
    for r in result_list:
      rec_dict = {}  # A new dictionary for this record

      for (value, key) in self.field_list:
        field_data = r[value]  # Extract field
        if (self.strip_fields == True):  # Strip off white spaces first
          field_data = field_data.strip()
        if (field_data != ''):  # Only add non-empty fields to dictionary
          rec_dict[key] = field_data

      # Set hidden fields
      #
      rec_dict['_rec_num_'] = self.next_record_num
      rec_dict['_dataset_name_'] = self.name

      rec_list.append(rec_dict)  # Append to the list of records

      # A log message for high volume log output (level 3)  - - - - - - - - - -
      #
      print '3:    Read record from data set: %s' % (str(rec_dict))

      self.next_record_num += 1 

    dbcu.close()

    # A log message for medium volume log output (level 2)  - - - - - - - - - -
    #
    print '2:  Read record block %i to %i' % (first, first+number-1)

    return rec_list

  # ---------------------------------------------------------------------------

  def read_record(self):
    """Read the next record, advance by one record.
    """

    if (self.next_record_num >= self.num_records):  # All records are read
      return None

    else:
      rec_list =  self.read_records(self.next_record_num, 1)
      return rec_list[0]

  # ---------------------------------------------------------------------------

  def write_records(self, record_list):
    """Write a block of records.
    """

    # Check parallel write mode
    #
    if (self.parallelwrite == 'host') and (parallel.rank() > 0):
      return  # Don't write if not host process

    if (self.database == None):
      print 'error:Data set not initialised'
      raise Exception

    if (self.access_mode not in ['write','append']):
      print 'error:Data set not initialised for "write" or "append" access'
      raise Exception

    dbcu = self.database.cursor()  # Get a database cursor

    for rec in record_list:

      if (not isinstance(rec, dict)):
        print 'error:Illegal record type: "%s", must be a dictionary' % \
              (str(type(rec)))
        raise Exception

      # Convert record dictionary into a 'insert' query
      #
      query = 'insert into '+self.table_name+' values ('
      j = 0  # Index into fields list
      for i in range(self.tot_field_number):
        if (i == self.field_list[j][0]):
          field_data = rec.get(self.field_list[j][1],self.fields_default)
          if (self.strip_fields == True):
            field_data = field_data.strip()  # Strip off whitespace
          query = query +"'"+ field_data +"',"
          j += 1
        else:
          query = query +"'',"

      query = query[:-1]+')'
      lines = dbcu.execute(query)
      if lines > 0:
        result_list = dbcu.fetchall()
      else:
        result_list = []  # 'fetchall' returned an empty tuple

      if (result_list == []):
        print 'error:Query "%s" returns empty result' % (query)
        raise Exception

      # A log message for high volume log output (level 3)  - - - - - - - - - -
      #
      print '3:    Wrote record to data set: '+str(rec)

    self.next_record_num += len(record_list)
    self.num_records +=     len(record_list)

    dbcu.close()

    # A log message for medium volume log output (level 2)  - - - - - - - - - -
    #
    print '2:  Wrote record block %i to %i' % \
          (self.next_record_num-len(record_list), self.next_record_num-1)

  # ---------------------------------------------------------------------------

  def write_record(self, record):
    """Write one record.
    """

    self.write_records([record])

# =============================================================================

class DataSetPGSQL(DataSet):
  """class DataSetPGSQL

     Implementation of a SQL (structured query language) data base access
     class for pgdb module.

     This data set does not allow the 'readwrite' or 'readappend' access modes,
     i.e. it must be initialised in modes 'read', 'write', or 'append'.

     The 'fields' attribute must contain pairs of field names and the
     corresponding SQL column names.

     In write or append mode the SQL data set assumes that the given table is
     already created, i.e. it does not have the functionality to create tables.

     DERIVED CLASS ATTRIBUTES
       table_name           The name of the database tabe.
       database_name        The name of the database to connect to.
       database_user        The user name for the database.
       database_password    The corresponding password, if not set at
                            initialisation, it is queried interactively.
       database_block_size  The maximum number of records read in a block.
                            Default value is 10,000.
  """

  # ---------------------------------------------------------------------------

  def __init__(self, **kwargs):
    try:
	    import pgdb
    except:
      print 'error:pgdb module not available, so SQL data set can not be'+ \
            ' used'
      raise Exception

    self.dataset_type =       'PGSQL'
    self.database_host = 'localhost'
    self.database_name =       None  # Database name
    self.database_user =       None  # User name
    self.database_password =   None  # User password
    self.database =            None  # Database object
    self.database_block_size = 10000 # Number of transactions for blocking
    self.field_list =          []    # Field name list sorted according to
                                     # database column numbers
    self.table_name =          ''
    self.tot_field_number = 0     # The total field (column) number

    base_kwargs = {}  # Dictionary, will contain unprocessed arguments

    # Process all keyword arguments
    #
    for (keyword, value) in kwargs.items():
      if (keyword == 'database_host'):
        if (not isinstance(value, str)):
	  print 'error:Argument "database_host" is not a string'
	  self.database_host = value
      elif (keyword == 'database_name'):
        if (not isinstance(value, str)):
          print 'error:Argument "database_name" is not a string'
          raise Exception
        self.database_name = value

      elif (keyword == 'database_user'):
        if (not isinstance(value, str)):
          print 'error:Argument "database_user" is not a string'
          raise Exception
        self.database_user = value

      elif (keyword == 'database_password'):
        if (not isinstance(value, str)):
          print 'error:Argument "database_password" is not a string'
          raise Exception
        self.database_password = value

      elif (keyword == 'table_name'):
        if (not isinstance(value, str)):
          print 'error:Argument "table_name" is not a string'
          raise Exception
        self.table_name = value

      elif (keyword == 'database_block_size'):
        if (not isinstance(value, int) or (value <= 0)):
          print 'error:Argument "database_block_size" must be a positive '+ \
                'integer'
          raise Exception
        self.database_block_size = value

      else:
        base_kwargs[keyword] = value

    # Check if database attributes are set  - - - - - - - - - - - - - - - - - -
    #
    if (self.database_name == ''):
      print 'error:No database name given'
      raise Exception

    if (self.database_user == ''):
      print 'error:No database user given'
      raise Exception

    if (self.table_name == ''):
      print 'error:Table name is not defined'
      raise Exception

    DataSet.__init__(self, base_kwargs)

    # Check if parallel write is set to 'host'  - - - - - - - - - - - - - - - -
    #
    if (self.parallelwrite != 'host'):
      print 'warning:Parallel write mode for  SQL data set is not "host": %s' \
            % (self.parallelwrite)

    # Only host process will access SQL data base
    #
    if (parallel.rank() > 0):
      return  # All other processes don't do anything

    # Check if the values in the 'fields' arguments are all strings (database
    # column names)
    #
    for (field_name, field_col) in self.fields.items():
      if (not isinstance(field_col, str)):
        print 'error:Field column "%s" is not a string' % (str(field_col))
        raise Exception

    # if no database password is given, query it interactively  - - - - - - - -
    #
    if (self.database_password == None):
      print '*****************************************'
      pwd = raw_input('Please enter database password:')
      print '*****************************************'

    else:
      pwd = self.database_password

    # Connect to the database - - - - - - - - - - - - - - - - - - - - - - - - -
    #
    #self.database = MySQLdb.Connect(db=self.database_name, \
    #                                user=self.database_user, passwd=pwd)
    self.database=pgdb.connect(":".join([self.database_host, self.database_name, self.database_user, pwd]))

    pwd = ''  # Delete password

    dbcu = self.database.cursor()  # Get a database cursor

    # Check if the table is available - - - - - - - - - - - - - - - - - - - - -
    #
    query = 'select relname from pg_class'
    lines = dbcu.execute(query)
    #if lines > 0:
    table_name_list = [x[0] for x in dbcu.fetchall()]

    # Give ability to read views as well ------------------------------
    #
    query = 'select viewname from pg_views'
    dbcu.execute(query)
    table_name_list.extend([x[0] for x in dbcu.fetchall()])

    #print "table_name_list ", table_name_list
    #else:
    #  table_name_list = []  # 'fetchall' returned an empty tuple

    if (self.table_name not in table_name_list):
      print 'error:Table "%s" is not in database "%s"' % \
            (self.table_name, self.database_name)
      raise Exception

    # Check if columns are available in the table - - - - - - - - - - - - - - -
    #
    query = 'select * from '+self.table_name + " limit 1"
    #lines = dbcu.execute(query)
    #if lines > 0:
    dbcu.execute(query)
    result = dbcu.fetchall()
    column_name_list =  dbcu.description
    
    #else:
    #column_name_list = []  # 'fetchall' returned an empty tuple

    db_field_dict = {}
    #col_num = 0  # Column number counter
    column_names = []
    for c in column_name_list:
      column_names.append(c[0])  # Make a list of column names only
      #db_field_dict[c[0]] = col_num
      #col_num += 1

    print "column_names = ", column_names
    self.tot_field_number = len(column_names) #col_num

    # Create a sorted list of field names and correspondinmg column numbers - -
    #
    fields_names =     []
    fields_positions = []

    for (field_name, field_sql) in self.fields.items():
      if (field_sql not in column_names):
        print 'error:Column "%s" not in table "%s"' % (field_sql, self.table_name)
        raise Exception

      fields_names.append(field_name)
      fields_positions.append(column_names.index(field_sql))  #db_field_dict[field_sql])

    self.field_list = map(None, fields_positions, fields_names)
    self.field_list.sort()

    # Now perform various checks for each access mode - - - - - - - - - - - - -
    #
    self.num_records = 0     # Total number of records

    # For 'read' mode, count records  - - - - - - - - - - - - - - - - - - - - -
    #
    if (self.access_mode == 'read'):

      # Count number of records in the table
      #
      query = 'select count(*) from '+self.table_name
      dbcu.execute(query)
      #print query, " returned lines = ", lines
      #if lines > 0:
      num_records = dbcu.fetchall()
      #else:
      #  num_records = []  # 'fetchall' returned an empty tuple

      if (num_records == []):
        print 'error:Query "%s" returns empty result' % (query)
        raise Exception

      self.num_records =     int(num_records[0][0])
      self.next_record_num = 0

    # For 'write' mode check if all records in table can be deleted - - - - - -
    #
    elif (self.access_mode == 'write'):

      query = 'delete from '+self.table_name
      lines = dbcu.execute(query)
      if lines > 0:
        num_records = dbcu.fetchall()
      else:
        num_records = []  # 'fetchall' returned an empty tuple

      self.num_records =     0
      self.next_record_num = 0

    # For 'append' mode, check how many records are stored  - - - - - - - - - -
    #
    elif (self.access_mode == 'append'):

      query = 'select count(*) from '+self.table_name
      lines = dbcu.execute(query)
      #if lines > 0:
      num_records = dbcu.fetchall()
      #else:
      #  num_records = []  # 'fetchall' returned an empty tuple

      if (num_records == []):
        print 'error:Query "%s" returns empty result' % (query)
        raise Exception

      self.num_records =     int(num_records[0][0])
      self.next_record_num = self.num_records

    else:  # Illegal data set access mode - - - - - - - - - - - - - - - - - - -
      print 'error:Illegal data set access mode: "%s"' % \
            (str(self.access_mode))
      raise Exception

    dbcu.close()

    # A log message for low volume log output (level 1) - - - - - - - - - - - -
    #
    print '1:'
    print '1:Initialised SQL data set "%s"' % (self.name)
    print '1:  In access mode: %s' % (self.access_mode)
    print '1:  Parallel write: %s' % (self.parallelwrite)
    print '1:  Database name:  %s' % (self.database_name)
    print '1:  Database user:  %s' % (self.database_user)
    print '1:  Table name:     %s' % (self.table_name)
    print '1:  Fields:         %s' % (str(self.fields))
    print '2:  Fields list:    %s' % (str(self.field_list))
    print '2:  Block size:     %i' % (self.database_block_size)
    print '2:  Strip fields:   %s' % (str(self.strip_fields))
    print '2:  Missing values: %s' % (str(self.missing_values))
    print '1:  Number of records: %i' % (self.num_records)

  # ---------------------------------------------------------------------------

  def finalise(self):
    """Finalise a data set. Disconnect from a database.
    """

    self.database.close()
    self.database = None

    self.access_mode =     None
    self.table_names =     []
    self.table_records =   []
    self.current_table =   None
    self.next_record_num = None

    # A log message for low volume log output (level 1) - - - - - - - - - - - -
    #
    print '1:'
    print '1:Finalised SQL data set "%s"' % (self.name)

  # ---------------------------------------------------------------------------

  def read_records(self, first, number):
    """Read and return a block of records.
    """
    print'1: read_records called with first='+ str(first)+ ' number = ' + str( number)
    if (self.database == None):
      print 'error:Data set not initialised'
      raise Exception

    if (self.access_mode != 'read'):
      print 'error:Data set not initialised for "read" access'
      raise Exception

    if (first < 0) or ((first+number) > self.num_records):
      print 'error:Selected block of records out of range'
      raise Exception

    dbcu = self.database.cursor()  # Get a database cursor

    # Now read the desired number of records blockwise
    #
    rec_list = []  # Each line becomes an entry in this list

    if (number <= self.database_block_size):

      query = 'select * from '+self.table_name + ' limit '+  str(number) + ' offset '+str(first)

      lines = dbcu.execute(query)
      #if lines > 0:
      result_list = dbcu.fetchall()
      print '1: length of result_list = ' + str(len(result_list))
      #else:
      #  result_list = []  # 'fetchall' returned an empty tuple

      if (result_list == []):
        print 'error:Query "%s" returns empty result' % (query)
        raise Exception

    else:
      result_list = []

      start = first
      size  = self.database_block_size
      left  = number

      while (left > 0):
        query = 'select * from '+self.table_name+ ' limit '+  str(size)+ ' offset '+str(start)
        lines = dbcu.execute(query)
        #if lines > 0:
        tmp_list = dbcu.fetchall()
        #else:
        #  tmp_list = []  # 'fetchall' returned an empty tuple

        if (tmp_list == []):
          print 'error:Query "%s" returns empty result' % (query)
          raise Exception

        result_list += tmp_list

        # Calculate next block start and size
        #
        start += size
        left -= size

        if (left > self.database_block_size):
          size = self.database_block_size
        else:
          size = left

    # Append all records to record list
    #
    for r in result_list:
      rec_dict = {}  # A new dictionary for this record

      for (value, key) in self.field_list:
        field_data = r[value]  # Extract field
        if (self.strip_fields == True):  # Strip off white spaces first
          field_data = field_data.strip()
        if (field_data != ''):  # Only add non-empty fields to dictionary
          rec_dict[key] = field_data

      # Set hidden fields
      #
      rec_dict['_rec_num_'] = self.next_record_num
      rec_dict['_dataset_name_'] = self.name

      rec_list.append(rec_dict)  # Append to the list of records

      # A log message for high volume log output (level 3)  - - - - - - - - - -
      #
      print '3:    Read record from data set: %s' % (str(rec_dict))

      self.next_record_num += 1 

    dbcu.close()

    # A log message for medium volume log output (level 2)  - - - - - - - - - -
    #
    print '2:  Read record block %i to %i' % (first, first+number-1)

    return rec_list

  # ---------------------------------------------------------------------------

  def read_record(self):
    """Read the next record, advance by one record.
    """

    if (self.next_record_num >= self.num_records):  # All records are read
      return None

    else:
      rec_list =  self.read_records(self.next_record_num, 1)
      
      return rec_list[0]

  # ---------------------------------------------------------------------------

  def write_records(self, record_list):
    """Write a block of records.
    """

    # Check parallel write mode
    #
    if (self.parallelwrite == 'host') and (parallel.rank() > 0):
      return  # Don't write if not host process

    if (self.database == None):
      print 'error:Data set not initialised'
      raise Exception

    if (self.access_mode not in ['write','append']):
      print 'error:Data set not initialised for "write" or "append" access'
      raise Exception

    dbcu = self.database.cursor()  # Get a database cursor

    for rec in record_list:

      if (not isinstance(rec, dict)):
        print 'error:Illegal record type: "%s", must be a dictionary' % \
              (str(type(rec)))
        raise Exception

      # Convert record dictionary into a 'insert' query
      #
      query = 'insert into '+self.table_name+' values ('
      j = 0  # Index into fields list
      for i in range(self.tot_field_number):
        if (i == self.field_list[j][0]):
          field_data = rec.get(self.field_list[j][1],self.fields_default)
          if (self.strip_fields == True):
            field_data = field_data.strip()  # Strip off whitespace
          query = query +"'"+ field_data +"',"
          j += 1
        else:
          query = query +"'',"

      query = query[:-1]+')'
      lines = dbcu.execute(query)
      if lines == 0:
      #  result_list = dbcu.fetchall()
      #else:
      #  result_list = []  # 'fetchall' returned an empty tuple

      #if (result_list == []):
        print 'error:Query "%s" returns empty result' % (query)
        raise Exception

      # A log message for high volume log output (level 3)  - - - - - - - - - -
      #
      self.database.commit()
      print '3:    Wrote record to data set: '+str(rec)

    self.next_record_num += len(record_list)
    self.num_records +=     len(record_list)

    dbcu.close()

    # A log message for medium volume log output (level 2)  - - - - - - - - - -
    #
    print '2:  Wrote record block %i to %i' % \
          (self.next_record_num-len(record_list), self.next_record_num-1)

  # ---------------------------------------------------------------------------

  def write_record(self, record):
    """Write one record.
    """

    self.write_records([record])

# ---------------------------------------------------------------------------

class RandomDataSet:
  """class RandomDataSet - The base class for random access.

   The 'RandomDataSet' class and all its derived classes provide methods for
   direct random access to records.

   Random access data sets can be used for temporary storage of records for
   example between the standardisation and linkage processes.

   Each record in a data set is made of fields. A dictionary with the field
   names as keys needs to be given when a data set is initialised. The values
   in this dictionary are not used in random access data sets.

   Each record given to (for write access) or returned from (in read access)
   random access data sets must be a dictionary containing the 'hidden' field
   '_rec_num_' (the record number), a positive (or zero) integer number. This
   record number is created and returned by one of the sequential data sets.

   For records that are read from a random access data set, their hidden field
   '_dataset_name_' is set to the name of the random data set.

   BASE METHODS
     __init__()                     The constructor. Initialises a data set in
                                    either 'read', 'write' or 'readwrite'
                                    access mode.
     finalise()                     Finalise access to a data set.
     re_initialise(access_mode)     To close and re-initialise a data set. It
                                    is possible to change the access mode when
                                    a data set is re-initialised.
     read_record(rec_number)        Read the record with the given number.
                                    Return 'None' if the record is not in the
                                    data set.
                                    The record is returned in a dictionary.
     read_records(rec_number_list)  Read the records with the numbers given in
                                    the list. Returns a list of records (in
                                    dictionaries). If a record is not available
                                    in the data set, a warning will be
                                    generated (and nothing will be be appended
                                    to the list of record, i.e. no 'None').
     write_records(record_list)     Writes a list of records given as
                                    dictionaries into the data set. Uses the
                                    hidden fields '_rec_num_' as keys for
                                    direct record access.
     write_record(record)           Writes a record given as a dictionary into
                                    the data set. Uses the hidden field
                                    '_rec_num_' as a key for direct record
                                    access.

   BASE ATTRIBUTES
     name                The name of the data set.
     description         A longer description of the data set.
     access_mode         The data set's access mode, which can be either
                         'read', 'write', or 'readwrite'.
     fields              Basic fields (columns, attributes) in the data set.
     fields_default      Default string if a field is not found. Used by the
                         field comparison functions (see 'comparison.py').
     num_records         Total number of records in the data set.
     missing_values      A list representation of missing value strings in the
                         data set. These are used by the field comparison
                         functions (see 'comparison.py').
"""

# =============================================================================

  def __init__(self, base_kwargs):
    """Constructor, set general attributes.
    """

    # General attributes for all data sets
    #
    self.name =            None
    self.description =     ''
    self.access_mode =     None
    self.fields =          None
    self.fields_default =  ''
    self.num_records =     None
    self.missing_values =  ['']
    self.parallelwrite =   parallel.writemode

    # Process base keyword arguments (all data set specific keywords were
    # processed in the derived class constructor)
    #
    for (keyword, value) in base_kwargs.items():
      if (keyword == 'name'):
        if (not isinstance(value, str)):
          print 'error:Argument "name" must be of type string'
          raise Exception
        self.name = value

      elif (keyword == 'description'):
        self.description = value

      elif (keyword == 'access_mode'):
        if (value not in ['read','write','readwrite']):
          print 'error:Illegal value for "access_mode": %s' % (str(value))
          raise Exception
        self.access_mode = value

      elif (keyword == 'fields'):
        if (not isinstance(value, dict)):
          print 'error:Argument "fields" must be a dictionary'
          raise Exception
        self.fields = value

      elif (keyword == 'fields_default'):
        if (not isinstance(value, str)):
          print 'error:Argument "fields_default" must be of type string'
          raise Exception
        self.fields_default = value

      elif (keyword == 'missing_values'):
        if (isinstance(value, str)):
          value = [value]  # Make it a list
        if (not isinstance(value, list)):
          print 'error:Argument "missing_values" must be a string or a '+ \
                'list of strings'
          raise Exception
        self.missing_values = value

      else:
        print 'error:Illegal constructor argument keyword: "%s"' % \
              (str(keyword))
        raise Exception

    # Check if name and access mode are defined - - - - - - - - - - - - - - - -
    #
    if (self.name == None):
      print 'error:Data set "name" is not defined'
      raise Exception

    if (self.access_mode == None):
      print 'error:Data set "access_mode" not defined'
      raise Exception

    if (self.fields == None):
      print 'error:Data set "fields" are not defined'
      raise Exception

  # ---------------------------------------------------------------------------

  def finalise(self):
    """Finalise a data set.
       See implementations in derived classes for details.
    """

    print 'error:Override abstract method in derived class'
    raise Exception

  # ---------------------------------------------------------------------------

  def re_initialise(self, access_mode):
    """Re-initalise the data set (close and open it) so that all data
       structures are up to date.

       A new access mode can be set with the given argument 'access_mode'. If
       set to None, the current access mode is kept.
    """

    print 'error:Override abstract method in derived class'
    raise Exception

  # ---------------------------------------------------------------------------

  def read_records(self, rec_number_list):
    """Read and return the records with the given record numbers.
       See implementations in derived classes for details.
    """

    print 'error:Override abstract method in derived class'
    raise Exception

  # ---------------------------------------------------------------------------

  def read_record(self, rec_number):
    """Read the record with the given record number.
       See implementations in derived classes for details.
    """

    print 'error:Override abstract method in derived class'
    raise Exception

  # ---------------------------------------------------------------------------

  def write_records(self, record_list):
    """Write the given records.
       See implementations in derived classes for details.
    """

    print 'error:Override abstract method in derived class'
    raise Exception

  # ---------------------------------------------------------------------------

  def write_record(self, record):
    """Write one record.
       See implementations in derived classes for details.
    """

    print 'error:Override abstract method in derived class'
    raise Exception


# =============================================================================

class DataSetShelve(RandomDataSet):
  """class DataSetShelve

     Implementation of a shelve data set based on the Python shelve module.
     Basically, this is a file based dictionary.

     If a shelve data set is opened in 'write' or 'readwrite' access mode its
     previous content will be cleared (truncated) when it is opened.

     DERIVED CLASS ATTRIBUTES
       file_name  A string containing the name of the underlying shelve
                  file(s).
       clear      A flag (True or False), when True the content of the database
                  will be cleared when opened in 'write' or 'readwrite' access
                  modes.
  """

  # ---------------------------------------------------------------------------

  def __init__(self, **kwargs):
    """Constructor, set derived attributes, call base class constructor for
       base attributes.
    """

    self.dataset_type = 'SHELVE'
    self.file_name =    None   # The name of the shelve files (without
                               # extensions)
    self.shelve =       None   # The 'shelve' File pointer to current file.
    self.db =           None   # A reference to the underlting database
    self.clear =        False  # Flag True/False for clearing the database
                               # when opening or not
 
    # Process all keyword arguments
    #
    base_kwargs = {}  # Dictionary, will contain unprocessed arguments

    for (keyword, value) in kwargs.items():
      if (keyword == 'file_name'):
        if (not isinstance(value, str)):
          print 'error:Argument "file_name" is not a string'
          raise Exception
        self.file_name = value

      elif (keyword == 'clear'):
        if (value not in [True, False]):
          print 'error:Illegal value for argument "clear" ' + \
                '(must be True or False)'
          raise Exception
        self.clear = value

      else:
        base_kwargs[keyword] = value

    if (self.file_name == None):
      print 'error:File name not defined'
      raise Exception

    RandomDataSet.__init__(self, base_kwargs)  # Process base arguments

    # Open the shelve - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    # Modify file name if parallel write mode is set to 'all'
    #
    if (self.access_mode in ['readwrite', 'write']) and \
       (self.parallelwrite == 'all'):
      self.file_name = self.file_name+'-P%i' % (parallel.rank())

    if (self.access_mode == 'read'):
      shelve_access = 'r'  # Read access mode for shelve implementation

      if (self.clear == True):
        print 'warning:Open Shelve dataset in read access mode, clearing' + \
              ' not possible'
    else:
      shelve_access = 'c'  # Read/write access, but also create if not there

#      # Clear the old database by deleting its file
#      #
#      if (self.clear == True) and (parallel.rank() == 0):
#
#        print '1:  Delete old database files for Shelve data set'
#
#        if (self.shelve_db == 'BSDDB3'):
#          try:
#            os.remove(self.file_name)
#          except:
#            print 'error:Can not delete database file "%s"' % (self.file_name)
#            raise Exception
#
#        elif (self.shelve_db == 'Shelve'):
#          try:
#            os.remove(self.file_name+'.dir')
#          except:
#            print 'error:Can not delete database file "%s"' % \
#                  (self.file_name+'.dir')
#            raise Exception
#
#          try:
#            os.remove(self.file_name+'.pag')
#          except:
#            print 'error:Can not delete database file "%s"' % \
#                  (self.file_name+'.pag')
#            raise Exception

    # Only open Shelve data set if in read mode or appropriate  - - - - - - - -
    # parallel write mode
    #
    if (self.access_mode == 'read') or (self.parallelwrite == 'all') or \
       ((self.parallelwrite == 'host') and (parallel.rank() == 0)):

      if (shelve_type == 'BSDDB3'):  # Berkeley database module available

        # Open the BSDDB data base first
        #
        try:
          self.db = bsddb3.rnopen(self.file_name, shelve_access)

        except:
          print 'error:Can not open BSDDB3 shelve: "%s" in mode "%s"' % \
                (str(self.file_name), str(shelve_access))
          raise Exception

        self.shelve = shelve.BsdDbShelf(self.db)  # Open the shelve

      else:  # Use standard shelve module
        try:
          self.shelve = shelve.open(self.file_name, shelve_access)
        except:
          print 'error:Can not open shelve: "%s" in mode "%s"' % \
                (str(self.file_name), str(shelve_access))
          raise Exception

      # Now clear the shelve if the 'clear' flag is set to True - - - - - - - -
      # (and we're not in read only access mode)
      #
      if (self.clear == True) and (self.access_mode != 'read'):
        if ((self.parallelwrite == 'host') and (parallel.rank() == 0)) or \
            (self.parallelwrite == 'all'):
          all_keys = self.shelve.keys()  # Get all keys

          for k in all_keys:
            del self.shelve[k]

          self.shelve.sync()  # And make sure the database is updated

      # Get the number of records in the shelve - - - - - - - - - - - - - - - -
      #
      self.num_records = len(self.shelve)

    else:  # Don't initialise shelve
      self.shelve =      None
      self.db =          None
      self.num_records = 0

    # Check that there are records in the data set
    #
    if (self.access_mode == 'read') and (self.num_records <= 0):
      print 'error:No records in data set initialised in "read" mode'
      raise Exception

    # A log message for low volume log output (level 1) - - - - - - - - - - - -
    #
    print '1:'
    print '1:Initialised Shelve data set "%s"' % (str(self.name))
    print '1:  In access mode: %s' % (self.access_mode)
    print '1:  Parallel write: %s' % (self.parallelwrite)
    print '1:  File name:      %s' % (self.file_name)
    print '2:  Missing values: %s' % (str(self.missing_values))
    print '1:  Number of records: %i' % (self.num_records)
    if (self.clear == True):
      print '1:  All elements in data set deleted (cleared)'

  # ---------------------------------------------------------------------------

  def finalise(self):
    """Finalise a data set, i.e. close the file and set various attributes to
       None.
    """

    # Close shelve if it is open
    #
    if (self.shelve != None):

      self.shelve.close()

      if (shelve_type == 'BSDDB3'):  # Berkeley database module available
        self.db.close()  # Also close the BSDDB data base
        self.db = None

      self.shelve = None

    self.access_mode =        None
    self.file_name =          None
    self.num_records =        None

    # A log message for low volume log output (level 1) - - - - - - - - - - - -
    #
    print '1:'
    print '1:Finalised Shelve data set "%s"' % (str(self.name))

  # ---------------------------------------------------------------------------

  def re_initialise(self, access_mode):
    """Re-initalise the data set (close and open it) so that all data
       structures are up to date.

       A new access mode can be set with the given argument 'access_mode'. If
       set to None, the current access mode is kept.
    """

    if (access_mode != None):
      if (access_mode not in ['read','write','readwrite']):
        print 'error:Illegal value for "access_mode": %s' % (str(access_mode))
        raise Exception
      self.access_mode = access_mode

    # First close shelve if it is open  - - - - - - - - - - - - - - - - - - - -
    #
    if (self.shelve != None):
      self.shelve.sync()  # Make sure all data is written to disk

      self.shelve.close()
      self.shelve = None

      if (shelve_type == 'BSDDB3'):  # Berkeley database module available
        self.db.close()  # Also close the BSDDB data base
        self.db = None

    parallel.Barrier()

    # Re-open the shelve  - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #
    if (self.access_mode == 'read'):
      shelve_access = 'r'  # Read access mode for shelve implementation

    else:
      shelve_access = 'c'  # Read/write access, but also create if not there

    # Only open Shelve data set if in read mode or appropriate  - - - - - - - -
    # parallel write mode
    #
    if (self.access_mode == 'read') or (self.parallelwrite == 'all') or \
       ((self.parallelwrite == 'host') and (parallel.rank() == 0)):

      if (shelve_type == 'BSDDB3'):  # Berkeley database module available

        # Open the BSDDB data base
        #
        try:
          self.db = bsddb3.rnopen(self.file_name, shelve_access)
        except:
          print 'error:Can not open BSDDB3 shelve: "%s" in mode "%s"' % \
                (str(self.file_name), str(shelve_access))
          raise Exception
        self.shelve = shelve.BsdDbShelf(self.db)  # Open the shelve

      else:  # Use standard shelve module
        try:
          self.shelve = shelve.open(self.file_name, shelve_access)
        except:
          print 'error:Can not open shelve: "%s" in mode "%s"' % \
                (str(self.file_name), str(shelve_access))
          raise Exception

      # Get the number of records in the shelve - - - - - - - - - - - - - - - -
      #
      self.num_records = len(self.shelve)

    else:  # Don't initialise shelve
      self.shelve = None
      self.num_records = 0

    # Check that there are records in the data set
    #
    if (self.access_mode == 'read') and (self.num_records <= 0):
      print 'error:No records in data set initialised in "read" mode'
      raise Exception

    # A log message for low volume log output (level 1) - - - - - - - - - - - -
    #
    print '1:'
    print '1:Re-initialised Shelve data set "%s"' % (str(self.name))

  # ---------------------------------------------------------------------------

  def read_records(self, rec_number_list):
    """Read and return the records with the given record numbers.
    """

    if (self.shelve == None):
      print 'error:Data set not initialised'
      raise Exception

    if (self.access_mode not in ['read','readwrite']):
      print 'error:Data set not initialised for "read" or "readwrite" access'
      raise Exception

    # Now read the desired number of records
    #
    record_list = []  # Each record becomes an entry in this list

    for rec_num in rec_number_list:

      if (shelve_type == 'BSDDB3'):  # Berkeley database module available
        shelve_key = int(rec_num)+1  # Positive integer needed for BSDDB3
      else:
        shelve_key = str(rec_num+1)  # String for shelve

      try:
        rec_dict = self.shelve[shelve_key]

        # Set hidden fields
        #
        rec_dict['_rec_num_'] =      rec_num
        rec_dict['_dataset_name_'] = self.name

        record_list.append(rec_dict)

      except KeyError:  # No record under this number in shelve
        print 'warning:Record with number %s is not stored in shelve' % \
              (rec_num)

      except:
        print 'error:Something is wrong when reading from shelve "%s"' % \
              (self.file_name)
        raise Exception

      # A log message for high volume log output (level 3)  - - - - - - - - - -
      #
      print '3:    Read record from data set: %s' % (str(rec_dict))

    # A log message for medium volume log output (level 2)  - - - - - - - - - -
    #
    print '2:  Read %i records from data set' % (len(rec_number_list))

    return record_list

  # ---------------------------------------------------------------------------

  def read_record(self, rec_num):
    """Read the record with the given record number.
    """

    if (self.shelve == None):
      print 'error:Data set not initialised'
      raise Exception

    if (self.access_mode not in ['read','readwrite']):
      print 'error:Data set not initialised for "read" or "readwrite" access'
      raise Exception

    if (shelve_type == 'BSDDB3'):  # Berkeley database module available
      shelve_key = int(rec_num)+1  # Positive integer needed for BSDDB3
    else:
      shelve_key = str(rec_num+1)  # String for shelve

    try:
      rec_dict = self.shelve[shelve_key]

      # Set hidden fields
      #
      rec_dict['_rec_num_'] =      rec_num
      rec_dict['_dataset_name_'] = self.name

    except KeyError:  # No record under this number in shelve
      print 'warning:Record with number %s is not stored in shelve' % \
            (rec_num)

      rec_dict = None

    except:
      print 'error:Something is wrong when reading from shelve "%s"' % \
            (self.file_name)
      raise Exception

    # A log message for high volume log output (level 3)  - - - - - - - - - - -
    #
    if (rec_dict != None):
      print '3:    Read record %s from data set: %s' % \
            (shelve_key, str(rec_dict))

    return rec_dict

  # ---------------------------------------------------------------------------

  def write_records(self, record_list):
    """Write the records in the given list into the data set.
    """

    # Check parallel write mode
    #
    if (self.parallelwrite == 'host') and (parallel.rank() > 0):
      return  # Don't write if not host process

    if (self.shelve == None):
      print 'error:Data set not initialised'
      raise Exception

    if (self.access_mode not in ['write','readwrite']):
      print 'error:Data set not initialised for "write" or "readwrite" access'
      raise Exception

    # Now write the given records
    #
    for record in record_list:

      rec_num = record.get('_rec_num_', None)  # Get the record number

      if (rec_num == None):
        print 'error:Record without record number given: %s' % (str(record))
        raise Exception

      if (shelve_type == 'BSDDB3'):  # Berkeley database module available
        shelve_key = int(rec_num)+1  # Positive integer needed for BSDDB3
      else:
        shelve_key = str(rec_num+1)  # String for shelve

      if (not self.shelve.has_key(shelve_key)):  # A new record
        self.num_records += 1

      # Insert record into data set
      #
      self.shelve[shelve_key] = record

      # A log message for high volume log output (level 3)  - - - - - - - - - -
      #
      print '3:    Wrote record to data set: %s' % (str(record))

    # self.shelve.sync()  # Flush to disk

    # A log message for medium volume log output (level 2)  - - - - - - - - - -
    #
    print '2:  Wrote %i records to data set' % (len(record_list))

  # ---------------------------------------------------------------------------

  def write_record(self, record):
    """Write the given record into the data set.
    """

    # Check parallel write mode
    #
    if (self.parallelwrite == 'host') and (parallel.rank() > 0):
      return  # Don't write if not host process

    if (self.shelve == None):
      print 'error:Data set not initialised'
      raise Exception

    if (self.access_mode not in ['write','readwrite']):
      print 'error:Data set not initialised for "write" or "readwrite" access'
      raise Exception

    # Now write the given record
    #
    rec_num = record.get('_rec_num_', None)  # Get the record number

    if (rec_num == None):
      print 'error:Record without record number given: %s' % (str(record))
      raise Exception

    if (shelve_type == 'BSDDB3'):  # Berkeley database module available
      shelve_key = int(rec_num)+1  # Positive integer needed for BSDDB3
    else:
      shelve_key = str(rec_num+1)  # String for shelve

    if (not self.shelve.has_key(shelve_key)):  # A new record
      self.num_records += 1

    # Insert record into data set
    #
    try:
      self.shelve[shelve_key] = record

    except:
      print 'error:Something is wrong when writing into shelve "%s"' % \
            (self.file_name)
      raise Exception

    self.shelve.sync()  # Flush to disk

    # A log message for high volume log output (level 3)  - - - - - - - - - - -
    #
    print '3:    Wrote record %s to data set: %s' % (shelve_key, str(record))

# =============================================================================

class DataSetMemory(RandomDataSet):
  """class DataSetMemory

     Implementation of a memory based data set using Python dictionaries.

     The only possible access mode is 'readwrite'.
  """

  # ---------------------------------------------------------------------------

  def __init__(self, **kwargs):
    """Constructor, set derived attributes, call base class constructor for
       base attributes.
    """

    self.dataset_type = 'MEMORY'
    self.dict =         {}        # The dictionary containing the records.

    # Process all keyword arguments (no keywords for derived class)
    #
    RandomDataSet.__init__(self, kwargs)  # Process base arguments

    if (self.access_mode != 'readwrite'):
      print 'error:Memory data set must be initialised in "readwrite" ' + \
            ' access mode'
      raise Exception

    self.num_records = 0

    # A log message for low volume log output (level 1) - - - - - - - - - - - -
    #
    print '1:'
    print '1:Initialised Memory data set "%s"' % (self.name)
    print '1:  In access mode: %s' % (self.access_mode)
    print '1:  Parallel write: %s' % (self.parallelwrite)
    print '2:  Missing values: %s' % (str(self.missing_values))
    print '1:  Number of records: %i' % (self.num_records)

  # ---------------------------------------------------------------------------

  def finalise(self):
    """Finalise a data set. All data will be lost.
    """

    self.dict = None

    self.access_mode =        None
    self.num_records =        None

    # A log message for low volume log output (level 1) - - - - - - - - - - - -
    #
    print '1:'
    print '1:Finalised Memory data set "%s"' % (self.name)

  # ---------------------------------------------------------------------------

  def re_initialise(self, access_mode):
    """Re-initalise the data set (close and open it) so that all data
       structures are up to date.

       A new access mode can be set with the given argument 'access_mode'. If
       set to None, the current access mode is kept.

       Only access modes "read" and "readwrite" can be used.
    """

    if (access_mode != None):
      if (self.access_mode not in ['readwrite','read']):
        print 'error:Memory data set must be initialised in "readwrite" ' + \
              ' access mode'
        raise Exception

    # We have to communicate the temporary memory data set to all processes
    #
    if (parallel.size() > 1):

      if (parallel.rank() == 0):
        for p in range(1, parallel.size()):
          parallel.send(self.dict, p)
          print '1:    Sent Memory data set to process %i' % (p)
      else:
        del self.dict  # Delete old data set

        self.dict = parallel.receive(0)
        print '1:    Received Memory data set from process 0'

    self.num_records = len(self.dict)  # Get the current number of records

    # A log message for low volume log output (level 1) - - - - - - - - - - - -
    #
    print '1:'
    print '1:Re-initialised Memory data set "%s"' % (str(self.name))

  # ---------------------------------------------------------------------------

  def read_records(self, rec_number_list):
    """Read and return the records with the given record numbers.
    """

    if (self.dict == None):
      print 'error:Data set not initialised'
      raise Exception

    if (self.access_mode not in ['read','readwrite']):
      print 'error:Data set not initialised for "read" or "readwrite" access'
      raise Exception

    # Now read the desired number of records
    #
    record_list = []  # Each record becomes an entry in this list

    for rec_num in rec_number_list:

      dict_key = str(rec_num)

      try:
        rec_dict = self.dict[dict_key]

        # Set hidden fields
        #
        rec_dict['_rec_num_'] =      rec_num
        rec_dict['_dataset_name_'] = self.name

        record_list.append(rec_dict)

      except KeyError:  # No record under this number in shelve
        print 'warning:Record with number %s is not stored in data set' % \
              (dict_key)

      except:
        print 'error:Something is wrong when reading from memory data ' + \
              'set "%s"' % (self.name)
        raise Exception

      # A log message for high volume log output (level 3)  - - - - - - - - - -
      #
      print '3:    Read record from data set: %s ' % (str(rec_dict))

    # A log message for medium volume log output (level 2)  - - - - - - - - - -
    #
    print '2:  Read %i records from data set' % (len(rec_number_list))

    return record_list

  # ---------------------------------------------------------------------------

  def read_record(self, rec_number):
    """Read the record with the given record number.
    """

    if (self.dict == None):
      print 'error:Data set not initialised'
      raise Exception

    if (self.access_mode not in ['read','readwrite']):
      print 'error:Data set not initialised for "read" or "readwrite" access'
      raise Exception

    dict_key = str(rec_number)

    try:
      rec_dict = self.dict[dict_key]

      # Set hidden fields
      #
      rec_dict['_rec_num_'] =      rec_number
      rec_dict['_dataset_name_'] = self.name

    except KeyError:  # No record under this number in shelve
      print 'warning:Record with number %s is not stored in data set' % \
            (dict_key)

      rec_dict = None

    except:
      print 'error:Something is wrong when reading from memory data ' + \
            'set "%s"' % (self.name)
      raise Exception

    # A log message for high volume log output (level 3)  - - - - - - - - - - -
    #
    if (rec_dict != None):
      print '3:    Read record %s from data set: %s' % \
            (dict_key, str(rec_dict))

    return rec_dict

  # ---------------------------------------------------------------------------

  def write_records(self, record_list):
    """Write the records in the given list into the data set.
    """

    # Check parallel write mode
    #
    if (self.parallelwrite == 'host') and (parallel.rank() > 0):
      return  # Don't write if not host process

    if (self.dict == None):
      print 'error:Data set not initialised'
      raise Exception

    if (self.access_mode not in ['write','readwrite']):
      print 'error:Data set not initialised for "write" or "readwrite" access'
      raise Exception

    # Now write the given records
    #
    for record in record_list:

      rec_num = record.get('_rec_num_', None)  # Get the record number

      if (rec_num == None):
        print 'error:Record without record number given: %s' % (str(record))
        raise Exception

      dict_key = str(rec_num)

      if (not self.dict.has_key(dict_key)):  # A new record
        self.num_records += 1

      # Insert record into data set
      #
      try:
        self.dict[dict_key] = record

      except:
        print 'error:Something is wrong when writing into memory data ' + \
            'set "%s"' % (self.name)
        raise Exception

      # A log message for high volume log output (level 3)  - - - - - - - - - -
      #
      print '3:    Wrote record to data set: %s' % (str(record))

    # A log message for medium volume log output (level 2)  - - - - - - - - - -
    #
    print '2:  Wrote %i records to data set' % (len(record_list))

  # ---------------------------------------------------------------------------

  def write_record(self, record):
    """Write the given record into the data set.
    """

    # Check parallel write mode
    #
    if (self.parallelwrite == 'host') and (parallel.rank() > 0):
      return  # Don't write if not host process

    if (self.dict == None):
      print 'error:Data set not initialised'
      raise Exception

    if (self.access_mode not in ['write','readwrite']):
      print 'error:Data set not initialised for "write" or "readwrite" access'
      raise Exception

    # Now write the given record
    #
    rec_num = record.get('_rec_num_', None)  # Get the record number

    if (rec_num == None):
      print 'error:Record without record number given: %s' % (str(record))
      raise Exception

    dict_key = str(rec_num)

    if (not self.dict.has_key(dict_key)):  # A new record
      self.num_records += 1

    # Insert record into data set
    #
    try:
      self.dict[dict_key] = record

    except:
      print 'error:Something is wrong when writing into memory data ' + \
          'set "%s"' % (self.name)
      raise Exception

    # A log message for high volume log output (level 3)  - - - - - - - - - - -
    #
    print '3:    Wrote record %s to data set: %s' % (dict_key, str(record))

# =============================================================================
