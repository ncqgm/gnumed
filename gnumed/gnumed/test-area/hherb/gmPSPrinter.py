import tempfile, os

psprolog = """%!PS
%0 36 translate .9727 dup scale %convert Legal To A4
%scale points to millimetres for whole document:
matrix currentmatrix /originmat exch def
/umatrix {originmat matrix concatmatrix setmatrix} def
[28.3465 0 0 28.3465 10.5 100.0] umatrix"""
	
psepilog = """
showpage
"""
	
def setfont(fontfamily='Times-Roman', size='0.4'):
	return """
/%(fontfamily)s findfont
%(size)s scalefont
setfont
newpath
""" % {'fontfamily':fontfamily, 'size':size}


def escape(string):
	s = string.replace("(", "\C")

class PSPrinter:
	def __init__(self, printer=None, leftmargin=0, bottommargin=0, printcmd='lpr', listprinterscmd='lpstat -v', printoptions=None):
		self.printer = printer
		self.leftmargin=leftmargin
		self.bottommargin=bottommargin
		self.printcmd=printcmd
		self.listprinterscmd=listprinterscmd
		self.printoptions=printoptions
		
	def prolog(self):
		global psprolog
		return psprolog
		
	def epilog(self):
		global psepilog
		return psepilog
		 
	def compose(self):
		return setfont() + """10 10 moveto (Hello, World!) show"""
	
	def printout(self, ps=None):
		page =  self.prolog() + (ps or self.compose()) + self.epilog()
		
		cmd = self.printcmd 
		if self.printer:
			cmd = '%s -P%s' %(cmd, self.printer)
		fname = tempfile.mktemp()
		file= open(fname, 'wb')
		file.write(page)
		file.close()
		cmd = "%s %s" % (cmd, fname)
		if not os.system(cmd):
			return fname
		else:
			return 0

	
if __name__ == "__main__":
	class MyCustomPrinter(PSPrinter):
		def compose(self):
			return  setfont(size=1.5) + """5 10 moveto (This is a Test) show""" 
			 
	p = MyCustomPrinter()
	temp = p.printout()
	if temp:
		print "Printing succeeded, now delete temp file", temp
	else:
		print "Something went wrong with the printing"