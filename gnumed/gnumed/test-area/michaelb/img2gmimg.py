#!/usr/env/python
# img2gmimg.py
#
# Author: Michael Bonert
#
# This little program creates a cPickled, compressed and formated picture from the a specified input file
# usage: $ python img2gmimg.py name_of_picture
#
# The output file is called: 'name_of_picture.gmimg'
#
# REQUIRES the wxPython tools


import zlib, cStringIO, cPickle, os, sys
from wxPython import wx
from wxPython.tools import img2img

def main():
	# BORROWED FUNCTION
	def crunch_data(data, compressed):
	    # this function is borrowed from 'img2py.py'
	    # compress it?
	    if compressed:
	        data = zlib.compress(data, 9)

	    # convert to a printable format, so it can be in a Python source file
	    data = repr(data)

	    #print 'compressed data'
	    #print data

	    # This next bit is borrowed from PIL.  It is used to wrap the text intelligently.
	    fp = cStringIO.StringIO()
	    data = data + " "  # buffer for the +1 test
	    c = i = 0
	    word = ""
	    octdigits = "01234567"
	    hexdigits = "0123456789abcdef"
	    while i < len(data):
	        if data[i] != "\\":
	            word = data[i]
	            i = i + 1
	        else:
	            if data[i+1] in octdigits:
	                for n in range(2, 5):
	                    if data[i+n] not in octdigits:
	                        break
	                word = data[i:i+n]
	                i = i + n
	            elif data[i+1] == 'x':
	                for n in range(2, 5):
	                    if data[i+n] not in hexdigits:
	                        break
	                word = data[i:i+n]
        	        i = i + n
        	    else:
        	        word = data[i:i+2]
        	        i = i + 2

	        l = len(word)
	        if c + l >= 78-1:
	            fp.write("\\\n")
	            c = 0
	        fp.write(word)
	        c = c + l

	    # return the formatted compressed data
	    return fp.getvalue()

	# --------------------------------------------------------------------------------
	
	# convert image to 'xpm'
	img2img.main( ['-n']+['xpm_img.xpm']+sys.argv[1:2], wx.wxBITMAP_TYPE_XPM, ".xpm", __doc__)


	# --------------------------------------------------------------------------------
	# open xpm-file
	filename='xpm_img.xpm'
	fp=open(filename,'r')

	alist=[]
	line=fp.readline()
	# this section strips header & comments from xpm file
	while line:
		line=fp.readline()
		if (line[:11]=='static char' or line=='/* columns rows colors chars-per-pixel */\n' \
		or line=='/* pixels */\n' or line=='\n'):
			pass	# eliminate first three lines & the line that denotes '/* pixels */'
				# eliminate trailing empty line with just a '\n' character
		else:
			# print line	# test
			if( len(line)>5):
				if (line[-2]==','):
					alist=alist+[ line[1:-3] ]	# eliminate '[', ']' ,',' ,'\n'
				else:
					alist=alist+[ line[1:-2] ]	# last element not followed by ','
	fp.close()

	fppic=open("xpm2gm_img.tmp",'w')
	cPickle.dump(alist,fppic)
	fppic.close()

	# ----- re-open -- read as text file
	fp2=open('xpm2gm_img.tmp','r')
	data=fp2.read()
	fp2.close()

	#print 'from xpm2gm_img.tmp'	# test
	#print data			# test
	#type(data) 			# test

	# compress and reorder
	compressed=1
	data_c = crunch_data(data, compressed)

	print '\ncompressed data...'
	print data_c

	outfilen=sys.argv[1]+'.gmimg'
	fpout=open(outfilen,'w')
	fpout.write(data_c)

	# clean-up
	os.remove('xpm2gm_img.tmp')
	os.remove('xpm_img.xpm')

if __name__ == '__main__':
	main()
