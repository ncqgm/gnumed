"""converts the output of twiki2moin.py for an earlier file format of moinmoin.
must run in the directory beneath the 'moin' directory where the data is stored."""
import os

l = os.listdir("moin")
for d in l:
	src = file( os.path.join("./moin/"+d, "revisions/00000001") )
	targ = file( os.path.join("./text", d), "w+" )
	for l in src:
		targ.write(l)
	
