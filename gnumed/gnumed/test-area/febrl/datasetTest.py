# =============================================================================
# datasetTest.py - Test module for dataset.py
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
# The Original Software is "datasetTest.py".
# The Initial Developers of the Original Software are Dr Peter Christen
# (Department of Computer Science, Australian National University) and Dr Tim
# Churches (Centre for Epidemiology and Research, New South Wales Department
# of Health). Copyright (C) 2002, 2003 the Australian National University and
# others. All Rights Reserved.
# Contributors:
#
# =============================================================================

"""Module datasetTest.py - Test module for dataset.py.
"""

# -----------------------------------------------------------------------------

import unittest
import dataset

doSQLtest = 'no'  # Set this to 'yes' or 'no' depending if you want to test
                  # your MySQL data set access
		
doPGSQLtest = 'yes'	#Test the for table test(givenname text, surname text, postcode text)
			# in database reclink  with user 'christen' password 'pass'

# -----------------------------------------------------------------------------

class TestCase(unittest.TestCase):

  # Initialise test case  - - - - - - - - - - - - - - - - - - - - - - - - - - -
  #
  def setUp(self):
    self.records = [{'gname':'ole',   'sname':'nielsen', 'pcode':'2600'},
                    {'gname':'peter', 'sname':'christen','pcode':''    },
                    {'gname':'tim',   'sname':'churches','pcode':'2021'},
                    {'gname':'markus','sname':'hegland', 'pcode':''    },
                    {'gname':'s',     'sname':'roberts', 'pcode':'4321'},
                    {'gname':'kim',   'sname':'',        'pcode':'2001'},
                    {'gname':'justin','sname':'xi zhu',  'pcode':''    }]

    self.random_records = \
      [{'gname':'ole',   'sname':'nielsen', 'pcode':'2600', '_rec_num_':0},
       {'gname':'peter', 'sname':'christen','pcode':''    , '_rec_num_':1},
       {'gname':'tim',   'sname':'churches','pcode':'2021', '_rec_num_':2},
       {'gname':'markus','sname':'hegland', 'pcode':''    , '_rec_num_':9},
       {'gname':'s',     'sname':'roberts', 'pcode':'4321', '_rec_num_':42},
       {'gname':'kim',   'sname':'',        'pcode':'2001', '_rec_num_':123},
       {'gname':'justin','sname':'xi zhu',  'pcode':''    , '_rec_num_':0}]

  # Clean up test case  - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  #
  def tearDown(self):
    pass  # Nothing to clean up

  # ---------------------------------------------------------------------------
  #
  # Start test cases

  def testCOL(self):   # - - - - - - - - - - - - - - - - - - - - - - - - - - -
    """Test COL data set"""

    # Initialise data set for writing
    #
    test_ds = dataset.DataSetCOL(name='COLds',
                                 description='no description',
                                 access_mode='write',
                                 header_lines=1,
                                 write_header=True,
                                 file_name='./test.txt',
                                 fields={'gname':(0,10),'sname':(10,10),
                                         'pcode':(20,6)},
                                 fields_default='missing',
                                 strip_fields=True,\
                                 missing_values =['','missing'])

    assert (isinstance(test_ds.fields,dict)), \
           'COL data set fields are not of type dictionary: '+ \
           str(test_ds.fields)

    assert (test_ds.last_col_number == 26), \
           'COL data set last column number is wrong (should be 26): '+ \
           str(test_ds.last_col_number)

    assert (test_ds.name == 'COLds'), \
           'COL data set has wrong name (should be "COLds"): '+ \
           str(test_ds.name)

    assert (test_ds.next_record_num == 0), \
           'COL data set has wrong current record number (should be 0): '+ \
           str(test_ds.next_record_num)

    assert (test_ds.access_mode == 'write'), \
           'COL data set has wrong access mode (should be "write"): '+ \
           str(test_ds.access_mode)

    assert (isinstance(test_ds.file_name, str)), \
           'COL data set file name is not a string: '+ \
           str(test_ds.file_name)

    assert (test_ds.num_records == 0), \
           'COL data set has wrong number of records (should be 0): '+ \
           str(test_ds.num_records)

    # Write a block of records
    #
    test_ds.write_records(self.records)

    assert (test_ds.num_records == len(self.records)), \
           'COL data set has wrong number of records: '+ \
           str(test_ds.num_records)+', should be: '+str(len(self.records))

    assert (test_ds.next_record_num == len(self.records)), \
           'COL data set has wrong current record number (should be '+ \
           str(len(self.records))+'): '+ str(test_ds.next_record_num)

    test_ds.finalise()
    test_ds = None

    # Re-initialise data set for reading

    test_ds = dataset.DataSetCOL(name='COLds',
                                 description='no description',
                                 access_mode='read',
                                 header_lines=1,
                                 write_header=True,
                                 file_name='./test.txt',
                                 fields={'gname':(0,10),'sname':(10,10),
                                         'pcode':(20,6)},
                                 fields_default='missing',
                                 strip_fields=True,\
                                 missing_values =['','missing'])

    assert (isinstance(test_ds.fields,dict)), \
           'COL data set fields are not of type dictionary: '+ \
           str(test_ds.fields)

    assert (test_ds.last_col_number == 26), \
           'COL data set last column number is wrong (should be 26): '+ \
           str(test_ds.last_col_number)

    assert (test_ds.name == 'COLds'), \
           'COL data set has wrong name (should be "COLds"): '+ \
           str(test_ds.name)

    assert (test_ds.access_mode == 'read'), \
           'COL data set has wrong access mode (should be "read"): '+ \
           str(test_ds.access_mode)

    assert (isinstance(test_ds.file_name, str)), \
           'COL data set file name is not a string: '+ \
           str(test_ds.file_name)

    assert (test_ds.num_records == len(self.records)), \
           'COL data set has wrong number of records: '+ \
           str(test_ds.num_records)+', should be: '+str(len(self.records))

    assert (test_ds.next_record_num == 0), \
           'COL data set has wrong current record number (should be 0): '+ \
           str(test_ds.next_record_num)

    # Read first record
    #
    result = test_ds.read_record()

    assert (test_ds.next_record_num == 1), \
           'COL data set has wrong current record number (should be 1): '+ \
           str(test_ds.next_record_num)

    for (key,value) in result.items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (value == self.records[0][key]), \
               'Record 0 read is wrong: '+ str(result)

    # Read second record
    #
    result = test_ds.read_record()

    assert (test_ds.next_record_num == 2), \
           'COL data set has wrong current record number (should be 2): '+ \
           str(test_ds.next_record_num)

    for (key,value) in result.items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[key] == self.records[1][key]), \
               'Record 1 read is wrong: '+ str(result)

    # Read records 2 - 4 in a block
    #
    result = test_ds.read_records(2,3)

    assert (test_ds.next_record_num == 5), \
           'COL data set has wrong current record number (should be 5): '+ \
           str(test_ds.next_record_num)

    for (key,value) in result[0].items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[0][key] == self.records[2][key]), \
               'Record 2 read is wrong: '+ str(result)
    for (key,value) in result[1].items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[1][key] == self.records[3][key]), \
               'Record 3 read is wrong: '+ str(result)
    for (key,value) in result[2].items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[2][key] == self.records[4][key]), \
               'Record 4 read is wrong: '+ str(result)

    # Read sixth record
    #
    result = test_ds.read_record()

    assert (test_ds.next_record_num == 6), \
           'COL data set has wrong current record number (should be 6): '+ \
           str(test_ds.next_record_num)

    for (key,value) in result.items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[key] == self.records[5][key]), \
               'Record 5 read is wrong: '+ str(result)

    # Read last record
    #
    result = test_ds.read_record()

    assert (test_ds.next_record_num == 7), \
           'COL data set has wrong current record number (should be 7): '+ \
           str(test_ds.next_record_num)

    for (key,value) in result.items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[key] == self.records[6][key]), \
               'Record 6 read is wrong: '+ str(result)

    # Try to read another record
    #
    result = test_ds.read_record()

    assert (result == None), 'Result is not "None" as expected: '+ str(result)

    test_ds.finalise()
    test_ds = None

    # Re-initialise data set for appending

    test_ds = dataset.DataSetCOL(name='COLds',
                                 description='no description',
                                 access_mode='append',
                                 header_lines=1,
                                 write_header=True,
                                 file_name='./test.txt',
                                 fields={'gname':(0,10),'sname':(10,10),
                                         'pcode':(20,6)},
                                 fields_default='missing',
                                 strip_fields=True,\
                                 missing_values =['','missing'])

    assert (isinstance(test_ds.fields,dict)), \
           'COL data set fields are not of type dictionary: '+ \
           str(test_ds.fields)

    assert (test_ds.last_col_number == 26), \
           'COL data set last column number is wrong (should be 26): '+ \
           str(test_ds.last_col_number)

    assert (test_ds.name == 'COLds'), \
           'COL data set has wrong name (should be "COLds"): '+ \
           str(test_ds.name)

    assert (test_ds.access_mode == 'append'), \
           'COL data set has wrong access mode (should be "append"): '+ \
           str(test_ds.access_mode)

    assert (isinstance(test_ds.file_name, str)), \
           'COL data set file name is not a string: '+ \
           str(test_ds.file_name)

    assert (test_ds.num_records == len(self.records)), \
           'COL data set has wrong number of records: '+ \
           str(test_ds.num_records)+', should be: '+str(len(self.records))

    assert (test_ds.next_record_num == len(self.records)), \
           'COL data set has wrong current record number (should be '+ \
           str(len(self.records))+'): '+ str(test_ds.next_record_num)

    # Write a block of records
    #
    test_ds.write_records(self.records)

    assert (test_ds.num_records == 2*len(self.records)), \
           'COL data set has wrong number of records: '+ \
           str(test_ds.num_records)+', should be: '+str(2*len(self.records))

    assert (test_ds.next_record_num == 2*len(self.records)), \
           'COL data set has wrong current record number (should be '+ \
           str(2*len(self.records))+'): '+ str(test_ds.next_record_num)

    test_ds.finalise()
    test_ds = None

    # Re-initialise data set for reading

    test_ds = dataset.DataSetCOL(name='COLds',
                                 description='no description',
                                 access_mode='read',
                                 header_lines=1,
                                 write_header=True,
                                 file_name='./test.txt',
                                 fields={'gname':(0,10),'sname':(10,10),
                                         'pcode':(20,6)},
                                 fields_default='missing',
                                 strip_fields=True,\
                                 missing_values =['','missing'])

    assert (isinstance(test_ds.fields,dict)), \
           'COL data set fields are not of type dictionary: '+ \
           str(test_ds.fields)

    assert (test_ds.last_col_number == 26), \
           'COL data set last column number is wrong (should be 26): '+ \
           str(test_ds.last_col_number)

    assert (test_ds.name == 'COLds'), \
           'COL data set has wrong name (should be "COLds"): '+ \
           str(test_ds.name)

    assert (test_ds.access_mode == 'read'), \
           'COL data set has wrong access mode (should be "read"): '+ \
           str(test_ds.access_mode)

    assert (isinstance(test_ds.file_name, str)), \
           'COL data set file name is not a string: '+ \
           str(test_ds.file_name)

    assert (test_ds.num_records == 2*len(self.records)), \
           'COL data set has wrong number of records: '+ \
           str(test_ds.num_records)+', should be: '+str(2*len(self.records))

    assert (test_ds.next_record_num == 0), \
           'COL data set has wrong current record number (should be 0): '+ \
           str(test_ds.next_record_num)

    # Read first record
    #
    result = test_ds.read_record()

    assert (test_ds.next_record_num == 1), \
           'COL data set has wrong current record number (should be 1): '+ \
           str(test_ds.next_record_num)

    for (key,value) in result.items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (value == self.records[0][key]), \
               'Record 0 read is wrong: '+ str(result)

    # Read second record
    #
    result = test_ds.read_record()

    assert (test_ds.next_record_num == 2), \
           'COL data set has wrong current record number (should be 2): '+ \
           str(test_ds.next_record_num)

    for (key,value) in result.items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[key] == self.records[1][key]), \
               'Record 1 read is wrong: '+ str(result)

    # Read records 2 - 13 in a block
    #
    result = test_ds.read_records(2,12)

    assert (test_ds.next_record_num == 14), \
           'COL data set has wrong current record number (should be 14): '+ \
           str(test_ds.next_record_num)

    for (key,value) in result[0].items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[0][key] == self.records[2][key]), \
               'Record 2 read is wrong: '+ str(result)
    for (key,value) in result[1].items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[1][key] == self.records[3][key]), \
               'Record 3 read is wrong: '+ str(result)
    for (key,value) in result[2].items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[2][key] == self.records[4][key]), \
               'Record 4 read is wrong: '+ str(result)
    for (key,value) in result[11].items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[11][key] == self.records[6][key]), \
               'Record 4 read is wrong: '+ str(result)

    # Try to read another record
    #
    result = test_ds.read_record()

    assert (result == None), 'Result is not "None" as expected: '+ str(result)

    test_ds.finalise()
    test_ds = None

  def testCSV(self):   # - - - - - - - - - - - - - - - - - - - - - - - - - - -
    """Test CSV data set"""

    # Initialise data set for writing
    #
    test_ds = dataset.DataSetCSV(name='CSVds',
                                 description='no description',
                                 access_mode='write',
                                 header_lines=1,
                                 write_header=True,
                                 file_name='./test.csv',
                                 fields={'gname':0,'sname':1,'pcode':2},
                                 fields_default='missing',
                                 strip_fields=True,
                                 write_quote_char='"',
                                 missing_values =['','missing'])

    assert (isinstance(test_ds.fields,dict)), \
           'CSV data set fields are not of type dictionary: '+ \
           str(test_ds.fields)

    assert (test_ds.tot_field_number == len(self.records[0])), \
           'CSV data set total field number is wrong (should be '+ \
           str(len(self.records[0]))+'): '+str(test_ds.tot_field_number)

    assert (test_ds.name == 'CSVds'), \
           'CSV data set has wrong name (should be "CSVds"): '+ \
           str(test_ds.name)

    assert (test_ds.next_record_num == 0), \
           'CSV data set has wrong current record number (should be 0): '+ \
           str(test_ds.next_record_num)

    assert (test_ds.access_mode == 'write'), \
           'CSV data set has wrong access mode (should be "write"): '+ \
           str(test_ds.access_mode)

    assert (isinstance(test_ds.file_name, str)), \
           'CSV data set file name is not a string: '+ \
           str(test_ds.file_name)

    assert (test_ds.num_records == 0), \
           'CSV data set has wrong number of records (should be 0): '+ \
           str(test_ds.num_records)

    # Write a block of records
    #
    test_ds.write_records(self.records)

    assert (test_ds.num_records == len(self.records)), \
           'CSV data set has wrong number of records: '+ \
           str(test_ds.num_records)+', should be: '+str(len(self.records))

    assert (test_ds.next_record_num == len(self.records)), \
           'CSV data set has wrong current record number (should be '+ \
           str(len(self.records))+'): '+ str(test_ds.next_record_num)

    test_ds.finalise()
    test_ds = None

    # Re-initialise data set for reading

    test_ds = dataset.DataSetCSV(name='CSVds',
                                 description='no description',
                                 access_mode='read',
                                 header_lines=1,
                                 write_header=True,
                                 file_name='./test.csv',
                                 fields={'gname':0,'sname':1,'pcode':2},
                                 fields_default='missing',
                                 strip_fields=True,\
                                 missing_values =['','missing'])

    assert (isinstance(test_ds.fields,dict)), \
           'CSV data set fields are not of type dictionary: '+ \
           str(test_ds.fields)

    assert (test_ds.tot_field_number == len(self.records[0])), \
           'CSV data set total field number is wrong (should be '+ \
           str(len(self.records[0]))+'): '+str(test_ds.tot_field_number)

    assert (test_ds.name == 'CSVds'), \
           'CSV data set has wrong name (should be "CSVds"): '+ \
           str(test_ds.name)

    assert (test_ds.access_mode == 'read'), \
           'CSV data set has wrong access mode (should be "read"): '+ \
           str(test_ds.access_mode)

    assert (isinstance(test_ds.file_name, str)), \
           'CSV data set file name is not a string: '+ \
           str(test_ds.file_name)

    assert (test_ds.num_records == len(self.records)), \
           'CSV data set has wrong number of records: '+ \
           str(test_ds.num_records)+', should be: '+str(len(self.records))

    assert (test_ds.next_record_num == 0), \
           'CSV data set has wrong current record number (should be 0): '+ \
           str(test_ds.next_record_num)

    # Read first record
    #
    result = test_ds.read_record()

    assert (test_ds.next_record_num == 1), \
           'CSV data set has wrong current record number (should be 1): '+ \
           str(test_ds.next_record_num)

    for (key,value) in result.items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (value == self.records[0][key]), \
               'Record 0 read is wrong: '+ str(result)

    # Read second record
    #
    result = test_ds.read_record()

    assert (test_ds.next_record_num == 2), \
           'CSV data set has wrong current record number (should be 2): '+ \
           str(test_ds.next_record_num)

    for (key,value) in result.items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[key] == self.records[1][key]), \
               'Record 1 read is wrong: '+ str(result)

    # Read records 2 - 4 in a block
    #
    result = test_ds.read_records(2,3)

    assert (test_ds.next_record_num == 5), \
           'CSV data set has wrong current record number (should be 5): '+ \
           str(test_ds.next_record_num)

    for (key,value) in result[0].items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[0][key] == self.records[2][key]), \
               'Record 2 read is wrong: '+ str(result)
    for (key,value) in result[1].items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[1][key] == self.records[3][key]), \
               'Record 3 read is wrong: '+ str(result)
    for (key,value) in result[2].items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[2][key] == self.records[4][key]), \
               'Record 4 read is wrong: '+ str(result)

    # Read sixth record
    #
    result = test_ds.read_record()

    assert (test_ds.next_record_num == 6), \
           'CSV data set has wrong current record number (should be 6): '+ \
           str(test_ds.next_record_num)

    for (key,value) in result.items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[key] == self.records[5][key]), \
               'Record 5 read is wrong: '+ str(result)

    # Read last record
    #
    result = test_ds.read_record()

    assert (test_ds.next_record_num == 7), \
           'CSV data set has wrong current record number (should be 7): '+ \
           str(test_ds.next_record_num)

    for (key,value) in result.items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[key] == self.records[6][key]), \
               'Record 6 read is wrong: '+ str(result)

    # Try to read another record
    #
    result = test_ds.read_record()

    assert (result == None), 'Result is not "None" as expected: '+ str(result)

    test_ds.finalise()
    test_ds = None

    # Re-initialise data set for appending

    test_ds = dataset.DataSetCSV(name='CSVds',
                                 description='no description',
                                 access_mode='append',
                                 header_lines=1,
                                 write_header=True,
                                 file_name='./test.csv',
                                 fields={'gname':0,'sname':1,'pcode':2},
                                 fields_default='missing',
                                 strip_fields=True,\
                                 missing_values =['','missing'])

    assert (isinstance(test_ds.fields,dict)), \
           'CSV data set fields are not of type dictionary: '+ \
           str(test_ds.fields)

    assert (test_ds.tot_field_number == len(self.records[0])), \
           'CSV data set total field number is wrong (should be '+ \
           str(len(self.records[0]))+'): '+str(test_ds.tot_field_number)

    assert (test_ds.name == 'CSVds'), \
           'CSV data set has wrong name (should be "CSVds"): '+ \
           str(test_ds.name)

    assert (test_ds.access_mode == 'append'), \
           'CSV data set has wrong access mode (should be "append"): '+ \
           str(test_ds.access_mode)

    assert (isinstance(test_ds.file_name, str)), \
           'CSV data set file name is not a string: '+ \
           str(test_ds.file_name)

    assert (test_ds.num_records == len(self.records)), \
           'CSV data set has wrong number of records: '+ \
           str(test_ds.num_records)+', should be: '+str(len(self.records))

    assert (test_ds.next_record_num == len(self.records)), \
           'CSV data set has wrong current record number (should be '+ \
           str(len(self.records))+'): '+ str(test_ds.next_record_num)

    # Write a block of records
    #
    test_ds.write_records(self.records)

    assert (test_ds.num_records == 2*len(self.records)), \
           'CSV data set has wrong number of records: '+ \
           str(test_ds.num_records)+', should be: '+str(2*len(self.records))

    assert (test_ds.next_record_num == 2*len(self.records)), \
           'CSV data set has wrong current record number (should be '+ \
           str(2*len(self.records))+'): '+ str(test_ds.next_record_num)

    test_ds.finalise()
    test_ds = None

    # Re-initialise data set for reading

    test_ds = dataset.DataSetCSV(name='CSVds',
                                 description='no description',
                                 access_mode='read',
                                 header_lines=1,
                                 write_header=True,
                                 file_name='./test.csv',
                                 fields={'gname':0,'sname':1,'pcode':2},
                                 fields_default='missing',
                                 strip_fields=True,\
                                 missing_values =['','missing'])

    assert (isinstance(test_ds.fields,dict)), \
           'CSV data set fields are not of type dictionary: '+ \
           str(test_ds.fields)

    assert (test_ds.tot_field_number == len(self.records[0])), \
           'CSV data set total field number is wrong (should be '+ \
           str(len(self.records[0]))+'): '+str(test_ds.tot_field_number)

    assert (test_ds.name == 'CSVds'), \
           'CSV data set has wrong name (should be "CSVds"): '+ \
           str(test_ds.name)

    assert (test_ds.access_mode == 'read'), \
           'CSV data set has wrong access mode (should be "read"): '+ \
           str(test_ds.access_mode)

    assert (isinstance(test_ds.file_name, str)), \
           'CSV data set file name is not a string: '+ \
           str(test_ds.file_name)

    assert (test_ds.num_records == 2*len(self.records)), \
           'CSV data set has wrong number of records: '+ \
           str(test_ds.num_records)+', should be: '+str(2*len(self.records))

    assert (test_ds.next_record_num == 0), \
           'CSV data set has wrong current record number (should be 0): '+ \
           str(test_ds.next_record_num)

    # Read first record
    #
    result = test_ds.read_record()

    assert (test_ds.next_record_num == 1), \
           'CSV data set has wrong current record number (should be 1): '+ \
           str(test_ds.next_record_num)

    for (key,value) in result.items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (value == self.records[0][key]), \
               'Record 0 read is wrong: '+ str(result)

    # Read second record
    #
    result = test_ds.read_record()

    assert (test_ds.next_record_num == 2), \
           'CSV data set has wrong current record number (should be 2): '+ \
           str(test_ds.next_record_num)

    for (key,value) in result.items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[key] == self.records[1][key]), \
               'Record 1 read is wrong: '+ str(result)

    # Read records 2 - 13 in a block
    #
    result = test_ds.read_records(2,12)

    assert (test_ds.next_record_num == 14), \
           'CSV data set has wrong current record number (should be 14): '+ \
           str(test_ds.next_record_num)

    for (key,value) in result[0].items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[0][key] == self.records[2][key]), \
               'Record 2 read is wrong: '+ str(result)
    for (key,value) in result[1].items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[1][key] == self.records[3][key]), \
               'Record 3 read is wrong: '+ str(result)
    for (key,value) in result[2].items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[2][key] == self.records[4][key]), \
               'Record 4 read is wrong: '+ str(result)
    for (key,value) in result[11].items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[11][key] == self.records[6][key]), \
               'Record 4 read is wrong: '+ str(result)

    # Try to read another record
    #
    result = test_ds.read_record()

    assert (result == None), 'Result is not "None" as expected: '+ str(result)

    test_ds.finalise()
    test_ds = None

  def testSQL(self):   # - - - - - - - - - - - - - - - - - - - - - - - - - - -
    """Test SQL data set"""

    if (doSQLtest == 'yes'):
	    dset = dataset.DataSetSQL
    elif doPGSQLtest == 'yes':
	    dset = dataset.DataSetPGSQL
    else:	    
      return  # Don't do SLQ test

    # Initialise data set for writing
    #
    test_ds = dset(name='SQLds',
                                 description='no description',
                                 access_mode='write',
                                 table_name='test',
                                 fields={'gname':'givenname',
                                         'sname':'surname',
                                         'pcode':'postcode'},
                                 fields_default='missing',
                                 strip_fields=True,
                                 missing_values =['','missing'],
                                 database_name='reclink',
                                 database_user='christen')

    assert (isinstance(test_ds.fields,dict)), \
           'SQL data set fields are not of type dictionary: '+ \
           str(test_ds.fields)

    assert (test_ds.tot_field_number == len(self.records[0])), \
           'SQL data set total field number is wrong (should be '+ \
           str(len(self.records[0]))+'): '+str(test_ds.tot_field_number)

    assert (test_ds.name == 'SQLds'), \
           'SQL data set has wrong name (should be "SQLds"): '+ \
           str(test_ds.name)

    assert (test_ds.next_record_num == 0), \
           'SQL data set has wrong current record number (should be 0): '+ \
           str(test_ds.next_record_num)

    assert (test_ds.access_mode == 'write'), \
           'SQL data set has wrong access mode (should be "write"): '+ \
           str(test_ds.access_mode)

    assert (isinstance(test_ds.table_name, str)), \
           'SQL data set table name is not a string: '+ \
           str(test_ds.table_name)

    assert (test_ds.num_records == 0), \
           'SQL data set has wrong number of records (should be 0): '+ \
           str(test_ds.num_records)

    # Write a block of records
    #
    test_ds.write_records(self.records)

    assert (test_ds.num_records == len(self.records)), \
           'SQL data set has wrong number of records: '+ \
           str(test_ds.num_records)+', should be: '+str(len(self.records))

    assert (test_ds.next_record_num == len(self.records)), \
           'SQL data set has wrong current record number (should be '+ \
           str(len(self.records))+'): '+ str(test_ds.next_record_num)

    test_ds.finalise()
    test_ds = None

    # Re-initialise data set for reading

    test_ds = dset(name='SQLds',
                                 description='no description',
                                 access_mode='read',
                                 table_name='test',
                                 fields={'gname':'givenname',
                                         'sname':'surname',
                                         'pcode':'postcode'},
                                 fields_default='missing',
                                 strip_fields=True,
                                 missing_values =['','missing'],
                                 database_name='reclink',
                                 database_user='christen')

    assert (isinstance(test_ds.fields,dict)), \
           'SQL data set fields are not of type dictionary: '+ \
           str(test_ds.fields)

    assert (test_ds.tot_field_number == len(self.records[0])), \
           'SQL data set total field number is wrong (should be '+ \
           str(len(self.records[0]))+'): '+str(test_ds.tot_field_number)

    assert (test_ds.name == 'SQLds'), \
           'SQL data set has wrong name (should be "SQLds"): '+ \
           str(test_ds.name)

    assert (test_ds.access_mode == 'read'), \
           'SQL data set has wrong access mode (should be "read"): '+ \
           str(test_ds.access_mode)

    assert (isinstance(test_ds.table_name, str)), \
           'SQL data set table name is not a string: '+ \
           str(test_ds.table_name)

    assert (test_ds.num_records == len(self.records)), \
           'SQL data set has wrong number of records: '+ \
           str(test_ds.num_records)+', should be: '+str(len(self.records))

    assert (test_ds.next_record_num == 0), \
           'SQL data set has wrong current record number (should be 0): '+ \
           str(test_ds.next_record_num)

    # Read first record
    #
    result = test_ds.read_record()

    assert (test_ds.next_record_num == 1), \
           'SQL data set has wrong current record number (should be 1): '+ \
           str(test_ds.next_record_num)

    for (key,value) in result.items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (value == self.records[0][key]), \
               'Record 0 read is wrong: '+ str(result)

    # Read second record
    #
    result = test_ds.read_record()

    assert (test_ds.next_record_num == 2), \
           'SQL data set has wrong current record number (should be 2): '+ \
           str(test_ds.next_record_num)

    for (key,value) in result.items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[key] == self.records[1][key]), \
               'Record 1 read is wrong: '+ str(result)

    # Read records 2 - 4 in a block
    #
    result = test_ds.read_records(2,3)

    assert (test_ds.next_record_num == 5), \
           'SQL data set has wrong current record number (should be 5): '+ \
           str(test_ds.next_record_num)

    for (key,value) in result[0].items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[0][key] == self.records[2][key]), \
               'Record 2 read is wrong: '+ str(result)
    for (key,value) in result[1].items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[1][key] == self.records[3][key]), \
               'Record 3 read is wrong: '+ str(result)
    for (key,value) in result[2].items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[2][key] == self.records[4][key]), \
               'Record 4 read is wrong: '+ str(result)

    # Read sixth record
    #
    result = test_ds.read_record()

    assert (test_ds.next_record_num == 6), \
           'SQL data set has wrong current record number (should be 6): '+ \
           str(test_ds.next_record_num)

    for (key,value) in result.items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[key] == self.records[5][key]), \
               'Record 5 read is wrong: '+ str(result)

    # Read last record
    #
    result = test_ds.read_record()

    assert (test_ds.next_record_num == 7), \
           'SQL data set has wrong current record number (should be 7): '+ \
           str(test_ds.next_record_num)

    for (key,value) in result.items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[key] == self.records[6][key]), \
               'Record 6 read is wrong: '+ str(result)

    # Try to read another record
    #
    result = test_ds.read_record()

    assert (result == None), 'Result is not "None" as expected: '+ str(result)

    test_ds.finalise()
    test_ds = None

    # Re-initialise data set for appending

    test_ds = dset(name='SQLds',
                                 description='no description',
                                 access_mode='append',
                                 table_name='test',
                                 fields={'gname':'givenname',
                                         'sname':'surname',
                                         'pcode':'postcode'},
                                 fields_default='missing',
                                 strip_fields=True,
                                 missing_values =['','missing'],
                                 database_name='reclink',
                                 database_user='christen')

    assert (isinstance(test_ds.fields,dict)), \
           'SQL data set fields are not of type dictionary: '+ \
           str(test_ds.fields)

    assert (test_ds.tot_field_number == len(self.records[0])), \
           'SQL data set total field number is wrong (should be '+ \
           str(len(self.records[0]))+'): '+str(test_ds.tot_field_number)

    assert (test_ds.name == 'SQLds'), \
           'SQL data set has wrong name (should be "SQLds"): '+ \
           str(test_ds.name)

    assert (test_ds.access_mode == 'append'), \
           'SQL data set has wrong access mode (should be "append"): '+ \
           str(test_ds.access_mode)

    assert (isinstance(test_ds.table_name, str)), \
           'SQL data set table name is not a string: '+ \
           str(test_ds.table_name)

    assert (test_ds.num_records == len(self.records)), \
           'SQL data set has wrong number of records: '+ \
           str(test_ds.num_records)+', should be: '+str(len(self.records))

    assert (test_ds.next_record_num == len(self.records)), \
           'SQL data set has wrong current record number (should be '+ \
           str(len(self.records))+'): '+ str(test_ds.next_record_num)

    # Write a block of records
    #
    test_ds.write_records(self.records)

    assert (test_ds.num_records == 2*len(self.records)), \
           'SQL data set has wrong number of records: '+ \
           str(test_ds.num_records)+', should be: '+str(2*len(self.records))

    assert (test_ds.next_record_num == 2*len(self.records)), \
           'SQL data set has wrong current record number (should be '+ \
           str(2*len(self.records))+'): '+ str(test_ds.next_record_num)

    test_ds.finalise()
    test_ds = None

    # Re-initialise data set for reading

    test_ds = dset(name='SQLds',
                                 description='no description',
                                 access_mode='read',
                                 table_name='test',
                                 fields={'gname':'givenname',
                                         'sname':'surname',
                                         'pcode':'postcode'},
                                 fields_default='missing',
                                 strip_fields=True,
                                 missing_values =['','missing'],
                                 database_name='reclink',
                                 database_user='christen')

    assert (isinstance(test_ds.fields,dict)), \
           'SQL data set fields are not of type dictionary: '+ \
           str(test_ds.fields)

    assert (test_ds.tot_field_number == len(self.records[0])), \
           'SQL data set total field number is wrong (should be '+ \
           str(len(self.records[0]))+'): '+str(test_ds.tot_field_number)

    assert (test_ds.name == 'SQLds'), \
           'SQL data set has wrong name (should be "SQLds"): '+ \
           str(test_ds.name)

    assert (test_ds.access_mode == 'read'), \
           'SQL data set has wrong access mode (should be "read"): '+ \
           str(test_ds.access_mode)

    assert (isinstance(test_ds.table_name, str)), \
           'SQL data set table name is not a string: '+ \
           str(test_ds.table_name)

    assert (test_ds.num_records == 2*len(self.records)), \
           'SQL data set has wrong number of records: '+ \
           str(test_ds.num_records)+', should be: '+str(2*len(self.records))

    assert (test_ds.next_record_num == 0), \
           'SQL data set has wrong current record number (should be 0): '+ \
           str(test_ds.next_record_num)

    # Read first record
    #
    result = test_ds.read_record()

    assert (test_ds.next_record_num == 1), \
           'SQL data set has wrong current record number (should be 1): '+ \
           str(test_ds.next_record_num)

    for (key,value) in result.items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (value == self.records[0][key]), \
               'Record 0 read is wrong: '+ str(result)

    # Read second record
    #
    result = test_ds.read_record()

    assert (test_ds.next_record_num == 2), \
           'SQL data set has wrong current record number (should be 2): '+ \
           str(test_ds.next_record_num)

    for (key,value) in result.items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[key] == self.records[1][key]), \
               'Record 1 read is wrong: '+ str(result)

    # Read records 2 - 14 in a block
    #
    result = test_ds.read_records(2,12)

    assert (test_ds.next_record_num == 14), \
           'SQL data set has wrong current record number (should be 14): '+ \
           str(test_ds.next_record_num)

    for (key,value) in result[0].items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[0][key] == self.records[2][key]), \
               'Record 2 read is wrong: '+ str(result)
    for (key,value) in result[1].items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[1][key] == self.records[3][key]), \
               'Record 3 read is wrong: '+ str(result)
    for (key,value) in result[2].items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[2][key] == self.records[4][key]), \
               'Record 4 read is wrong: '+ str(result)
    for (key,value) in result[11].items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (result[11][key] == self.records[6][key]), \
               'Record 4 read is wrong: '+ str(result)

    # Try to read another record
    #
    result = test_ds.read_record()

    assert (result == None), 'Result is not "None" as expected: '+ str(result)

    test_ds.finalise()
    test_ds = None

  def testShelve(self):   # - - - - - - - - - - - - - - - - - - - - - - - - - -
    """Test Shelve data set"""

    # Initialise data set for writing
    #
    test_ds = dataset.DataSetShelve(name='ShelveDS',
                             description='no description',
                             access_mode='write',
                                  clear = True,
                                 fields = {'gname':0,
                                           'sname':1,
                                           'pcode':2},
                          fields_default='missing',
                               file_name='./testshelve',
                         missing_values =['','missing'])

    assert (test_ds.name == 'ShelveDS'), \
           'Shelve data set has wrong name (should be "ShelveDS"): '+ \
           str(test_ds.name)

    assert (test_ds.access_mode == 'write'), \
           'Shelve data set has wrong access mode (should be "write"): '+ \
           str(test_ds.access_mode)

    assert (isinstance(test_ds.file_name, str)), \
           'Shelve data set file name is not a string: '+ \
           str(test_ds.file_name)

    # Write a list of records
    #
    test_ds.write_records(self.random_records)

    assert (test_ds.num_records == (len(self.random_records)-1)), \
           'Shelve data set has wrong number of records: '+ \
           str(test_ds.num_records)+', should be: '+ \
           str(len(self.random_records)-1)

    test_ds.write_record(self.random_records[1])

    assert (test_ds.num_records == (len(self.random_records)-1)), \
           'Shelve data set has wrong number of records: '+ \
           str(test_ds.num_records)+', should be: '+ \
           str(len(self.random_records)-1)

    test_ds.write_record(self.random_records[4])
    test_ds.write_record(self.random_records[5])

    assert (test_ds.num_records == (len(self.random_records)-1)), \
           'Shelve data set has wrong number of records: '+ \
           str(test_ds.num_records)+', should be: '+ \
           str(len(self.random_records)-1)

    test_ds.finalise()
    test_ds = None

    # Re-initialise data set for reading

    test_ds = dataset.DataSetShelve(name='ShelveDS',
                                    description='no description',
                                    access_mode='read',
                                    clear = True,
                                    fields = {'gname':0,
                                              'sname':1,
                                              'pcode':2},
                                    fields_default='missing',
                                    file_name='./testshelve',
                                    missing_values =['','missing'])

    assert (test_ds.name == 'ShelveDS'), \
           'Shelve data set has wrong name (should be "ShelveDS"): '+ \
           str(test_ds.name)

    assert (test_ds.access_mode == 'read'), \
           'Shelve data set has wrong access mode (should be "read"): '+ \
           str(test_ds.access_mode)

    assert (isinstance(test_ds.file_name, str)), \
           'Shelve data set file name is not a string: '+ \
           str(test_ds.file_name)

    assert (test_ds.num_records == (len(self.random_records)-1)), \
           'Shelve data set has wrong number of records: '+ \
           str(test_ds.num_records)+', should be: '+ \
           str(len(self.records)-1)

    # Read first record
    #
    result = test_ds.read_record(0)

    for (key,value) in result.items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (value == self.random_records[6][key]), \
               'Record 0 read is wrong: '+ str(result)+ '\n'+\
               str(self.random_records[6])

    # Read third record
    #
    result = test_ds.read_record(2)

    for (key,value) in result.items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (value == self.random_records[2][key]), \
               'Record 2 read is wrong: '+ str(result)+ '\n'+\
               str(self.random_records[2])

    # Read second record
    #
    result = test_ds.read_record(1)

    for (key,value) in result.items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (value == self.random_records[1][key]), \
               'Record 1 read is wrong: '+ str(result)+ '\n'+\
               str(self.random_records[1])

    # Read records 123 and 42
    #
    result = test_ds.read_records([123,42])

    for (key,value) in result[0].items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (value == self.random_records[5][key]), \
               'Record 123 read is wrong: '+ str(result)+ '\n'+\
               str(self.random_records[5])
    for (key,value) in result[1].items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (value == self.random_records[4][key]), \
               'Record 42 read is wrong: '+ str(result)+ '\n'+\
               str(self.random_records[4])

    # Try to read another record

    result = test_ds.read_record(99)

    assert (result == None), 'Result is not "None" as expected: '+ str(result)

    test_ds.finalise()
    test_ds = None

    # Re-initialise data set for readwrite, don't clear

    test_ds = dataset.DataSetShelve(name='ShelveDS',
                                    description='no description',
                                    access_mode='readwrite',
                                    fields = {'gname':0,
                                              'sname':1,
                                              'pcode':2},
                                    fields_default='missing',
                                    file_name='./testshelve',
                                    missing_values =['','missing'])

    assert (test_ds.name == 'ShelveDS'), \
           'Shelve data set has wrong name (should be "ShelveDS"): '+ \
           str(test_ds.name)

    assert (test_ds.access_mode == 'readwrite'), \
           'Shelve data set has wrong access mode (should be "readwrite"): '+ \
           str(test_ds.access_mode)

    assert (isinstance(test_ds.file_name, str)), \
           'Shelve data set file name is not a string: '+ \
           str(test_ds.file_name)

    assert (test_ds.num_records == (len(self.random_records)-1)), \
           'Shelve data set has wrong number of records: '+ \
           str(test_ds.num_records)+', should be: '+ \
           str(len(self.records)-1)

    # Write a block of records
    #
    test_ds.write_records(self.random_records)

    assert (test_ds.num_records == (len(self.records)-1)), \
           'Shelve data set has wrong number of records: '+ \
           str(test_ds.num_records)+', should be: '+ \
           str(len(self.records)-1)

    # Read records 1 and 42
    #
    result = test_ds.read_records([1,42])

    for (key,value) in result[0].items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (value == self.random_records[1][key]), \
               'Record 1 read is wrong: '+ str(result)+ '\n'+\
               str(self.random_records[1])

    for (key,value) in result[1].items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (value == self.random_records[4][key]), \
               'Record 42 read is wrong: '+ str(result)+ '\n'+\
               str(self.random_records[4])

    # Read second record
    #
    result = test_ds.read_record(1)

    for (key,value) in result.items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (value == self.random_records[1][key]), \
               'Record 1 read is wrong: '+ str(result)+ '\n'+\
               str(self.random_records[1])

    # Read record 9
    #
    result = test_ds.read_record(9)

    for (key,value) in result.items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (value == self.random_records[3][key]), \
               'Record 9 read is wrong: '+ str(result)+ '\n'+\
               str(self.random_records[3])

    # Read first record
    #
    result = test_ds.read_record(0)

    for (key,value) in result.items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (value == self.random_records[6][key]), \
               'Record 0 read is wrong: '+ str(result)+ '\n'+\
               str(self.random_records[6])

    test_ds.finalise()
    test_ds = None

  def testMemory(self):   # - - - - - - - - - - - - - - - - - - - - - - - - - -
    """Test Memory data set"""

    # Initialise data set for reading and writing
    #
    test_ds = dataset.DataSetMemory(name='MemoryDS',
                                    description='no description',
                                    access_mode='readwrite',
                                    fields = {'gname':0,
                                              'sname':1,
                                              'pcode':2},
                                    fields_default='missing',
                                    missing_values =['','missing'])

    assert (test_ds.name == 'MemoryDS'), \
           'Memory data set has wrong name (should be "MemoryDS"): '+ \
           str(test_ds.name)

    assert (test_ds.access_mode == 'readwrite'), \
           'Memory data set has wrong access mode (should be "readwrite"): '+ \
           str(test_ds.access_mode)

    # Write a list of records
    #
    test_ds.write_records(self.random_records)

    assert (test_ds.num_records == (len(self.random_records)-1)), \
           'Memory data set has wrong number of records: '+ \
           str(test_ds.num_records)+', should be: '+ \
           str(len(self.random_records)-1)

    test_ds.write_record(self.random_records[1])

    assert (test_ds.num_records == (len(self.random_records)-1)), \
           'Memory data set has wrong number of records: '+ \
           str(test_ds.num_records)+', should be: '+ \
           str(len(self.random_records)-1)

    test_ds.write_record(self.random_records[4])
    test_ds.write_record(self.random_records[5])

    assert (test_ds.num_records == (len(self.random_records)-1)), \
           'Memory data set has wrong number of records: '+ \
           str(test_ds.num_records)+', should be: '+ \
           str(len(self.random_records)-1)

    # Read first record
    #
    result = test_ds.read_record(0)

    for (key,value) in result.items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (value == self.random_records[6][key]), \
               'Record 0 read is wrong: '+ str(result)+ '\n'+\
               str(self.random_records[6])

    # Read third record
    #
    result = test_ds.read_record(2)

    for (key,value) in result.items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (value == self.random_records[2][key]), \
               'Record 2 read is wrong: '+ str(result)+ '\n'+\
               str(self.random_records[2])

    # Read second record
    #
    result = test_ds.read_record(1)

    for (key,value) in result.items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (value == self.random_records[1][key]), \
               'Record 1 read is wrong: '+ str(result)+ '\n'+\
               str(self.random_records[1])

    # Read records 123 and 42
    #
    result = test_ds.read_records([123,42])

    for (key,value) in result[0].items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (value == self.random_records[5][key]), \
               'Record 123 read is wrong: '+ str(result)+ '\n'+\
               str(self.random_records[5])
    for (key,value) in result[1].items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (value == self.random_records[4][key]), \
               'Record 42 read is wrong: '+ str(result)+ '\n'+\
               str(self.random_records[4])

    # Try to read another record

    result = test_ds.read_record(99)

    assert (result == None), 'Result is not "None" as expected: '+ str(result)

    test_ds.finalise()
    test_ds = None

    # Re-initialise data set for readwrite

    test_ds = dataset.DataSetMemory(name='MemoryDS',
                                    description='no description',
                                    access_mode='readwrite',
                                    fields = {'gname':0,
                                              'sname':1,
                                              'pcode':2},
                                    fields_default='missing',
                                    missing_values =['','missing'])

    assert (test_ds.name == 'MemoryDS'), \
           'Memory data set has wrong name (should be "MemoryDS"): '+ \
           str(test_ds.name)

    assert (test_ds.access_mode == 'readwrite'), \
           'Memory data set has wrong access mode (should be "readwrite"): '+ \
           str(test_ds.access_mode)

    assert (test_ds.num_records == 0), \
           'Memory data set has wrong number of records: '+ \
           str(test_ds.num_records)+', should be: 0'

    # Write a block of records
    #
    test_ds.write_records(self.random_records)

    assert (test_ds.num_records == (len(self.records)-1)), \
           'Memory data set has wrong number of records: '+ \
           str(test_ds.num_records)+', should be: '+ \
           str(len(self.records)-1)

    # Read records 1 and 42
    #
    result = test_ds.read_records([1,42])

    for (key,value) in result[0].items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (value == self.random_records[1][key]), \
               'Record 1 read is wrong: '+ str(result)+ '\n'+\
               str(self.random_records[1])

    for (key,value) in result[1].items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (value == self.random_records[4][key]), \
               'Record 42 read is wrong: '+ str(result)+ '\n'+\
               str(self.random_records[4])

    # Read second record
    #
    result = test_ds.read_record(1)

    for (key,value) in result.items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (value == self.random_records[1][key]), \
               'Record 1 read is wrong: '+ str(result)+ '\n'+\
               str(self.random_records[1])

    # Read record 9
    #
    result = test_ds.read_record(9)

    for (key,value) in result.items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (value == self.random_records[3][key]), \
               'Record 9 read is wrong: '+ str(result)+ '\n'+\
               str(self.random_records[3])

    # Read first record
    #
    result = test_ds.read_record(0)

    for (key,value) in result.items():
      if (key[0] != '_'):  # Don't test hidden fields
        assert (value == self.random_records[6][key]), \
               'Record 0 read is wrong: '+ str(result)+ '\n'+\
               str(self.random_records[6])

    test_ds.finalise()
    test_ds = None

# -----------------------------------------------------------------------------
# Start tests when called from command line

if (__name__ == "__main__"):
  unittest.main()  # Run all test

  # The following code does the same as 'unittest.main()'
  #
  # mysuite = unittest.makeSuite(TestCase,'test')
  # testrunner = unittest.TextTestRunner(verbosity=1)
  # testrunner.run(mysuite)
