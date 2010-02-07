import os, sys, struct, string, base64
import zipfile
import StringIO

offset = 8
len_offset = 4 

class Extract:
	
	def __init__(self, src_file,  outdir = './outdir', suffix = 'txt', keep_existing = False, one_file = False, _blocksize = 32):
		self._f = file(src_file, 'rb')
		self._blocksize = _blocksize
		self._one_file = one_file
		if not one_file:
			self._outdir = outdir
			if not os.path.exists(outdir):
				os.mkdir(outdir)

		else:
			if not os.path.exists(outdir) or keep_existing is False:
				self._outfile = file( outdir, 'w')
			else:
				self._outfile = file( outdir, 'a+')

		self._keep_existing = keep_existing
		while suffix and len(suffix) and suffix[0] =='.':
			suffix = suffix[1:]
		self._suffix = suffix

	def set_suffix(self, sf):
		self._suffix = sf
    
	def get_base(self, block, process = None, verbose = False ):
		blocks = long(block)

		st0 = blocks * self._blocksize
		f = self._f
		f.seek(st0)
		version, filelen = struct.unpack('>xxxBL', f.read(8))
		if verbose:sys.stderr.write("version is " + str(version) + " length "+ str(filelen)+"\n")		
		bytes = f.read(filelen)

		return bytes
	
	def get_zip_filename(self, bytes):
		fn = None
		try:
			t = StringIO.StringIO(bytes)
			z = zipfile.ZipFile(t)
			for x in z.infolist():
				print x.filename, "time",x.date_time, "sz", x.compress_size, x.file_size
				fn = x.filename
		except:
			sys.stderr.write( "not zip format\n")

		return fn

	def get(self, block, process = None, verbose = False ):
		bytes = self.get_base(block, process, verbose)

		if not self._one_file:
			sys.stdout = sys.__stdout__	
			fn = self.get_zip_filename(bytes)
			if not fn:
                                fn  = str(block)+".bmp"

			sys.stderr.write( "filename is "+ fn +  " filelen is " +  str(filelen)+"\n")

			path = os.path.join(self._outdir,fn)
			if os.path.exists(path):
				if verbose: sys.stderr.write( path + " already exists .")
				if self._keep_existing:
					sys.stderr.write(' keeping\n')
					return
				else:
					sys.stderr.write(' overwriting\n')

                        file(path , 'wb').write( bytes) 
			sys.stderr.write( "from block "+ str(block) + ",  wrote "+ str(filelen) +  " bytes to "+ path+'\n')
		else:
			of = self._outfile		
			of.write('block='+str(block) + '\n')
			of.write('len='+str(filelen) +'\n' )
                        if process :
                           fn, arg = process
                           bytes = fn(bytes, arg)

			of.write( bytes  )
			of.write('\n\n\n')

			
if __name__ == '__main__':
	e = Extract(sys.argv[1])
	e.get( int(sys.argv[2]))
