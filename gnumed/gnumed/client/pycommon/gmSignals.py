"""gmSignals - factory functions returning GnuMed internal signal strings. 

This helps to avoid that  simple typographic mistakes result in messages
not being dispatched. It would allow to do messenging house keeping as well.

@copyright: author
@license: GPL (details at http://www.gnu.org)
"""
# This source code is protected by the GPL licensing scheme.
# Details regarding the GPL are available at http://www.gnu.org
# You may use and share it as long as you don't deny this right
# to anybody else.
#=============================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/pycommon/Attic/gmSignals.py,v $
__version__ = "$Revision: 1.12 $"
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
def allg_mod_db():
	"""Announce modification of allergy row into/from backend."""
	return 'allg_mod_db'

def allergy_updated():
	"""Announce allergy cache update to interested parties."""
	return 'allergy_updated'

#------------------------------------------
# vaccinations
def vacc_mod_db():
	"""table vaccination"""
	return 'vacc_mod_db'

def vaccinations_updated():
	"""Announce vaccination cache update to interested parties."""
	return 'vaccinations_updated'

#------------------------------------------
def health_issue_change_db():
	"""Announce health issue row insert/update/delete in backend.

	- there's only very few health issue rows per patient and they
	  are rarely accessed so efficiency does not make it necessary to
	  have separate signals for insert/delete and update
	"""
	return 'health_issue_change_db'

def health_issue_updated():
	"""Announce health issue cache update within frontend."""
	return 'health_issue_updated'

#------------------------------------------
def episode_change_db():
	"""Announce episode row insert/update/delete in backend.

	- there's only a few episode rows per patient and they
	  are rarely accessed so efficiency does not make it necessary to
	  have separate signals for insert/delete and update
	"""
	return 'episode_change_db'

def episodes_modified():
	"""Announce episode cache update within frontend."""
	return 'episodes_modified'

#------------------------------------------
def item_change_db():
	"""Backend modification to clin_root_item.

	- directly or indirectly
	- the actual signal name is appended with the relevant patient ID
	"""
	return 'item_change_db'

def clin_history_updated():
	"""Frontend signal for clin_history  update."""
	return "clin_history_updated"

def clin_item_updated():
	"""Frontend signal for clin_root_item cache update."""
	return 'clin_item_updated'
#-------------------------------------------------------------
def pre_patient_selection():
	"""the currently active patient is about to be changed"""
	return 'activating_patient'

def activating_patient():
	return pre_patient_selection()

def post_patient_selection():
	"""another patient has been selected to be the currently active patient"""
	return 'patient_selected'

def patient_selected():
	return post_patient_selection()

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

#-------------------------------------------------------------
def application_closing():
	"""The main application is intentionally closing down."""
	return "application_closing"

def application_init():
	"an application is starting"
	return "application_init"

#-------------------------------------------------------------
def user_error ():
	"an error of interest to the user"
	return "user_error"

def new_notebook ():
	"""a new notebook page creation event
It should carry a dictionary:
- name: the unique name (for unloading)
- widget: the wxWindow to display
- label: the notebook label
- icon: the notebook icon (which may or may not be used, can be None)
	"""
	return "new_notebook"

def unload_plugin ():
	"""
	Requested that the named plugin be unloaded
	- name: the plugin name
	"""
	return "unload_notebook"

def display_plugin ():
	"""
	Requested that the named plugin be displayed
	- name: the unique name of the plugin

	If the plugin doesn't want to be displayed, it should listen for this event and
	return the string 'veto'
	"""
	return "display_plugin"


def wish_display_plugin ():
	"""
	This event expressed the desire that a plugin be displayed
	I.e the plugin manger *receives* this event, it generates the above
	- name: plugin unique name
	"""
	return "wish_display_plugin"

def search_result ():
	"""
	The results of a patient search
	- ids: a list of gmPerson.cIdentity objects
	- display_fields: a list of fields to display
	"""
	return "search_result"


def pg_users_changed():
	"""
		when the pg_user list is modified , or a user perms changed
	
	"""
	return "pg_users_changed" 

def provider_identity_selected():
	"""
		when a provider selection widget selects a existing potential identity provider 
	"""
	return "provider_identity_selected"
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
# Revision 1.12  2006-01-18 14:16:01  sjtan
#
# extra signals for provider mgmt
#
# Revision 1.11  2005/09/11 17:29:16  ncq
# - pre/post_patient_selection() make much more sense than activating_patient()
#   and patient_selected()
#
# Revision 1.10  2005/05/06 15:29:47  ncq
# - cleanup
#
# Revision 1.9  2005/04/14 08:51:51  ncq
# - cIdentity has moved
#
# Revision 1.8  2005/02/23 19:39:37  ncq
# - episodes_updated -> episodes_modified
#
# Revision 1.7  2005/02/01 10:16:07  ihaywood
# refactoring of gmDemographicRecord and follow-on changes as discussed.
#
# gmTopPanel moves to gmHorstSpace
# gmRichardSpace added -- example code at present, haven't even run it myself
# (waiting on some icon .pngs from Richard)
#
# Revision 1.6  2005/01/31 20:25:37  ncq
# - add episode change signals
#
# Revision 1.5  2004/07/15 07:57:20  ihaywood
# This adds function-key bindings to select notebook tabs
# (Okay, it's a bit more than that, I've changed the interaction
# between gmGuiMain and gmPlugin to be event-based.)
#
# Oh, and SOAPTextCtrl allows Ctrl-Enter
#
# Revision 1.4  2004/05/22 11:48:16  ncq
# - allergy signal handling cleanup
#
# Revision 1.3  2004/03/28 11:50:16  ncq
# - cleanup
#
# Revision 1.2  2004/03/03 23:53:22  ihaywood
# GUI now supports external IDs,
# Demographics GUI now ALPHA (feature-complete w.r.t. version 1.0)
# but happy to consider cosmetic changes
#
# Revision 1.1  2004/02/25 09:30:13  ncq
# - moved here from python-common
#
# Revision 1.14  2003/12/29 16:33:59  uid66147
# - vaccinations related signals
#
# Revision 1.13  2003/12/02 01:59:19  ncq
# - cleanup, add vaccination_updated()
#
# Revision 1.12  2003/11/17 10:56:37  sjtan
#
# synced and commiting.
#
# Revision 1.4  2003/10/26 00:58:52  sjtan
#
# use pre-existing signalling
#
# Revision 1.3  2003/10/25 16:13:26  sjtan
#
# past history , can add  after selecting patient.
#
# Revision 1.2  2003/10/25 08:29:40  sjtan
#
# uses gmDispatcher to send new currentPatient objects to toplevel gmGP_ widgets. Proprosal to use
# yaml serializer to store editarea data in  narrative text field of clin_root_item until
# clin_root_item schema stabilizes.
#
# Revision 1.1  2003/10/23 06:02:39  sjtan
#
# manual edit areas modelled after r.terry's specs.
#
# Revision 1.11  2003/07/19 20:19:19  ncq
# - add clin_root_item signals
#
# Revision 1.10  2003/07/09 16:22:04  ncq
# - add health issue signals
#
# Revision 1.9  2003/06/25 22:47:23  ncq
# - added application_closing() (I seem to keep adding stuff Sian proposed earlier)
#
# Revision 1.8  2003/06/22 16:19:09  ncq
# - add pre-selection signal
#
# Revision 1.7  2003/05/01 15:01:42  ncq
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
# @change log:
#	08.09.2002 hherb first draft, untested
