#
# dbf.py version 0.2
# 1999/11/12
#
# A module for reading dbf files. Tested ONLY on Linux.
#
# Author        : Michal Spalinski (mspal@curie.harvard.edu)
#                 minor changes (dictresult) by H.Herb
# Copying policy: unlimited (do what you want with it)
# Warranty      : none whatsoever
#
# URL: http://schwinger.harvard.edu/~mspal/pystuff.html


"""
This is a module for reading dbf files.

It has been modified thanks to suggestions and patches from Jeff Bauer
and Kevin Dahlhausen. Unfortunately I lost patches which fix
endianness problems, which were sent to me by someone, so that will
have to wait. I do not use this module much these days, but since it
seems to be in use "out there" I thought I would finally make an
update available. This version should be more portable. Also, rather
than printing an error message an exception is now raised when the dbf
file appears to be corrupt.

Usage: the following

import dbf
db = dbf.dbf('mydata.dbf')

creates a dbf object db associated with an existing dbf file
'mydata.dbf'.  The dbf file is opened by the constructor. If the file
is not there IOError is raised. If the file appears not to be a dbf
format file, TypeError is raised.

If you prefer to create a dbf object, but open the actual file later,
you can use the following:

import dbf
db = dbf.dbf('mydata.dbf', openit=0)

and then you can call

db.open()

to actually open the file. Note that the constructor, if called this
way, does not verify that the file is there, so the IOError exception
is raised by the call to open.

Once the dbf object is created and opened (implicitly or not), the
following are available:

-- db.fields  : returns a a list of tuples describing the fields
-- db.nrecs   : returns the number of records
-- db[n]      : returns a tuple containing record number n (0 <= n < nrecs)
-- db.status(): prints some essential data about the dbf file

So to list the first two fields of mydata.dbf, assuming they are string
fields, one might write:

import dbf
from string import strip
db=dbf.dbf('mydata.dbf')
for k in db:
    print "%s, %s" % (strip(k[1]), strip(k[2]))


Good luck!

"""


from struct import unpack

class dbf:
	def __init__(self, fname, openit=1):
		self.fname = fname
		if openit:
			self.open()

	def open(self):
		self.f = open(self.fname,'rb')
		head = self.f.read(32)
		if (head[0] != '\003') and (head[0] != '\203') and (head[0] != '\365'):
			raise TypeError, 'Not a Dbase III+ file!'
		(self.nrecs, self.hlen, self.rlen) = unpack('4xihh20x', head)
		fdalen = (self.hlen - 33)/32
		# read field descriptor array
		fda = []
		for k in range(fdalen):
			fda.append(self.f.read(32))
		# interpret the field descriptors
		self.fields = []
		#field index dictionary
		self.fieldindex = {}
		idx = 0
		for fd in fda:
			bytes = unpack('12c4xBb14x', fd)
			field = ""
			for i in range(11):
				if bytes[i] == '\000':
					break
				field = field+bytes[i]
			type = bytes[11]
			length = bytes[12]
			dec = bytes[13]
			self.fields.append((field,type,length,dec))
			self.fieldindex[idx]=field
			idx=idx+1

	# record numbers go from 0 to self.nrecs-1
	def _get(self, recno):
		offs = self.hlen + recno*self.rlen
		self.f.seek(offs,0)
		return self.f.read(self.rlen)

	def __getitem__(self, recno):
		if recno < 0 or recno >= self.nrecs:
			raise IndexError
		else:
			raw = self._get(recno)
		res = []
		pos = 0
		for field in self.fields:
			end = pos+field[2]
			item = raw[pos+1:end+1]
			pos=end
			res.append(item)
		return tuple(res)

	def dictresult(self, recno):
		res = self.__getitem__(recno)
		d = {}
		i = 0
		for field in res:
			d[self.fieldindex[i]]=field
			i = i+1
		return d




	def status(self):
		print ''
		print 'Header length     :', self.hlen
		print 'Record length     :', self.rlen
		print 'Number of records :',  self.nrecs
		print ''
		print '%-12s %-12s %-12s %-12s' % ('Field','Type','Length','Decimal')
		print '%-12s %-12s %-12s %-12s' % ('-----','----','------','-------')
		for k in self.fields:
			print '%-12s %-12s %-12s %-12s' % k
		print ''

	def close(self):
		self.f.close()


