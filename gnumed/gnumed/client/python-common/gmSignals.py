#############################################################################
#
# gmSignals.py: factory functions returning GnuMed internal signal strings
# ---------------------------------------------------------------------------
#
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: pg, gmLoginInfo
# @change log:
#	08.09.2002 hherb first draft, untested
#
# @TODO: testing
############################################################################
# This source code is protected by the GPL licensing scheme.
# Details regarding the GPL are available at http://www.gnu.org
# You may use and share it as long as you don't deny this right
# to anybody else.

"""gmSignals - factory functions returning GnuMed internal signal strings. 
This helps to avoid that  simple typographic mistakes result in messages
not being dispatched. It would allow to do messenging house keeping as well.
"""

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/python-common/Attic/gmSignals.py,v $
__version__ = "$Revision: 1.7 $"
__author__  = "H. Herb <hherb@gnumed.net>"

#=============================================================
def popup_notice():
	"a notice of general interest has been received"
	return 'popup_notice'

def popup_alert():
	"an important notice of general ineterest has been received"
	return 'popup_alert'
#-------------------------------------------------------------
# clinical signals
#-------------------------------------------------------------
# allergies
def allergy_add_del_db():
	"""Announce insertion/deletion of allergy row into/from backend."""
	return 'allergy_add_del_db'

def allergy_updated():
	"""Announce allergy cache update to interested parties."""
	return 'allergy_updated'
#-------------------------------------------------------------
def patient_selected():
	"the current active patient displayed by the client has been selected"
	return 'patient_selected'

def patient_modified():
	"the current patients demographic data has been modified"
	return 'patient_modified'
	
def medication_modified():
	"the current patient's medication has been modified"
	return 'medication_modified'
#-------------------------------------------------------------
def waitingroom_added():
	"a patient has been added to the waiting room"
	return 'waitingroom_added'
	
def waitingroom_incons():
	"a patient has started his consultation with the doctor"
	return 'waitingroom_incons'
	
def waitingroom_left():
	"a aptient has left the waiting room, finished his consultation"
	return 'waitingroom_left'

def application_clean_closing():
	"an application is intentionally closing"
	return "application_clean_closing"

def application_init():
	"an application is starting"
	return "application_init"
	
#=============================================================	
if __name__ == "__main__":

	import gmDispatcher
	
	def callback(id):
		print "\nSignal received, id = %s" % str(id)
		
	class TestWidget:
		def __init__(self):
			gmDispatcher.connect(self.Update, patient_selected())
		def Update(self, id):
			print "widget updates itself with id=%s" % str(id)
		
	the_id =100
	print "Registering interest in signal %s" % popup_notice()
	gmDispatcher.connect(callback, popup_notice())
	print "Sending signal %s with parameter %d" % (popup_notice(), the_id)
	gmDispatcher.send(popup_notice(), id=the_id)
	print "\nCreating an instance of a widget updating itself on signal %s" % patient_selected()
	tw = TestWidget()
	print "Sending signal %s with parameter %d" % (patient_selected(), the_id+1)
	gmDispatcher.send(patient_selected(), id=the_id+1)

#======================================================================
# $Log: gmSignals.py,v $
# Revision 1.7  2003-05-01 15:01:42  ncq
# - add allergy signals
#
# Revision 1.6  2003/02/12 23:39:12  sjtan
#
# new signals for initialization and teardown of other modules less dependent on gui.
#
# Revision 1.5  2003/01/16 14:45:04  ncq
# - debianized
#
# Revision 1.4  2002/11/30 11:07:50  ncq
# - just a bit of cleanup
#
# Revision 1.3  2002/09/10 07:41:27  ncq
# - added changelog keyword
#
