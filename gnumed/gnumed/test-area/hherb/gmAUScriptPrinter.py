import copy, gmPSPrinter

_psvars ="""
/drname {(%(drname)s)} def
/drstreet {(%(drstreet)s)} def
/draddress {(%(draddress)s)} def
/drprescriber {(%(drprescriber)s)} def
/ptmedicare {(%(ptmedicare)s)} def
/ptentitlement {(%(ptentitlement)s)} def
/ptsafetynet {(%(ptsafetynet)s)} def
/ptconcessional {(%(ptconcessional)s)} def
/ptname {(%(ptname)s)} def
/ptstreet {(%(ptstreet)s)} def
/ptaddress {(%(ptaddress)s)} def
/scriptdate {(%(scriptdate)s)} def
/scriptno {(%(scriptno)s)} def
/pbstick {(%(pbstick)s)} def
/rpbstick {(%(rpbstick)s)} def
/brandsubst {(%(brandsubst)s)} def
/rx1name {(%(rx1name)s)} def
/rx1amount {(%(rx1amount)s)} def 
/rx1instr {(%(rx1instr)s)} def
/rx2name {(%(rx2name)s)} def
/rx2amount {(%(rx2amount)s)} def
/rx2instr {(%(rx2instr)s)} def
/rx3name {(%(rx3name)s)} def
/rx3amount {(%(rx3amount)s)} def
/rx3instr {(%(rx3instr)s)} def
/rxitems {(%(rxitems)s)} def
"""

_ps = """
/fontDrug {/Times-Bold findfont 0.4 scalefont setfont} def
/fontDrugDetails {/Times-Roman findfont 0.3 scalefont setfont} def

/resetRX {
/rxLineheight {0.4} def
/rxNewDrugDY {0.6} def
/rxX {2.1} def
/rxY {17.3} def
} def

/CR {rxY rxLineheight sub 
/rxY exch def 
rxX rxY moveto
} def 

/nextdrug {rxY rxNewDrugDY sub 
/rxY exch def 
rxX rxY moveto
} def 


%the doctor's details on the script
/drheader {
/Times-Bold findfont 0.5 scalefont setfont 
0.5 25.0 moveto  drname show 
/Times-Roman findfont 0.4 scalefont setfont
0.5 24.6 moveto drstreet  show
0.5 24.2 moveto draddress show
2.2 23.5 moveto drprescriber show
5.0 23.5 moveto scriptno show
} def

/ptdetails {
/Times-Roman findfont 0.4 scalefont setfont
3.3 22.7 moveto ptmedicare show
/Times-Roman findfont 0.4 scalefont setfont
2.0 21.9 moveto ptentitlement show
2.0 21.0 moveto ptsafetynet show
6.1 21.0 moveto ptconcessional show
/Times-Bold findfont 0.5 scalefont setfont
2.1 20.3 moveto ptname show
/Times-Roman findfont 0.4 scalefont setfont
2.1 19.8 moveto ptstreet show
2.1 19.4 moveto ptaddress show
0.8 18.8 moveto scriptdate show
0.8 18.4 moveto pbstick show
2.4 18.4 moveto rpbstick show
4.2 18.4 moveto brandsubst show
} def

/scriptitems {
resetRX
%first script item
fontDrug rxX rxY moveto rx1name show
fontDrugDetails
CR rx1amount show
CR rx1instr show
%second script item
rx2name stringwidth pop % does item 2 exist?
0 gt	%only print details if item exists
{ fontDrug nextdrug rx2name show
fontDrugDetails
CR rx2amount show
CR rx2instr show } if
%third script item
rx3name stringwidth pop % does item 3 exist?
0 gt	%only print details if item exists
{
fontDrug nextdrug rx3name show
fontDrugDetails
CR rx3amount show
CR rx3instr show } if
%script summary
nextdrug rxitems show
nextdrug (Signed:_________________________) show
CR drname show 

} def

/script {
newpath
drheader
ptdetails
scriptitems
} def

script
10.5 0.0 translate
script

"""

class AUScriptPrinter(gmPSPrinter.PSPrinter):
	
	def escapeDict(self, dict):
		"""TODO: escape all the postscript sensitive characters like "/", "\" and "(", ")"""
		return dict
		
	def setData(self, params):
		global _psvars, _ps
		self._psdata = copy.deepcopy(_psvars)
		self._psdata = "%s %s" % (self._psdata % params, _ps)
	
	def compose(self):
		assert(self._psdata is not None)
		return self._psdata

if __name__ == "__main__":
	s = {}
	s['drname']="Dr Horst Herb, M.D."
	s['drstreet']="8 Hickory St"
	s['draddress']="Dorrigon, NSW 2453"
	s['drprescriber']="2078899"
	s['ptmedicare']="3456 78901 2 / 3"
	s['ptentitlement']="Z12345XY"
	s['ptsafetynet']="X"
	s['ptconcessional']="X"
	s['ptname']="Mr Joe Blogg"
	s['ptstreet']="1 Acacia Drive"
	s['ptaddress']="Megan, NSW 2453"
	s['scriptdate']="01/02/2003"
	s['scriptno']="123456"
	s['pbstick']="X"
	s['rpbstick']="X"
	s['brandsubst']="X"
	s['rx1name']="Amoxycillin 500mg tablets"
	s['rx1amount']="20 tablets, no repeats"
	s['rx1instr']="take one tablet three times daily until finished"
	s['rx2name']="Hydrochlorothiazide 25mg tablets"
	s['rx2amount']="100 tablets, 1 repeat"
	s['rx2instr']="take 1/2 tablet every morning"
	s['rx3name']="Paracetamol 500mg tablets"
	s['rx3amount']="300 tablets, 4 repeats"
	s['rx3instr']="take 1-2 tablets up to every 6 hours if needed"
	s['rxitems']="3"
	printer = AUScriptPrinter()
	printer.setData(s)
	temp = printer.printout()
	if temp:
		print "Printing succeeded, now delete temp file", temp
	else:
		print "Something went wrong with the printing"