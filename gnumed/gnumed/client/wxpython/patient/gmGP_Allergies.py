#============================================================================
# gmGP_Allergies
#
# @dependencies: wxPython (>= version 2.3.1)
#============================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/patient/gmGP_Allergies.py,v $
__version__ = "$Revision: 1.26 $"
__author__  = "R.Terry <rterry@gnumed.net>, H.Herb <hherb@gnumed.net>, K.Hilbert <Karsten.Hilbert@gmx.net>"
__license__ = 'GPL (details at http://www.gnu.org)'


from Gnumed.wxpython import gmPlugin_Patient, gmAllergyWidgets

#============================================================================
class gmGP_Allergies (gmPlugin_Patient.wxPatientPlugin):
	"""Plugin to encapsulate the allergies window"""

	__icons = {
"""icon_letter_A""": 'x\xda\xd3\xc8)0\xe4\nV74S\x00"\x13\x05Cu\xae\xc4`\xf5|\x85d\x05e\x17W\x10\
\x04\xf3\xf5@|77\x03 \x00\xf3\x15\x80|\xbf\xfc\xbcT0\'\x02$i\xee\x06\x82PIT@\
HPO\x0f\xab`\x04\x86\xa0\x9e\x1e\\)\xaa`\x04\x9a P$\x02\xa6\x14Y0\x1f\xa6\
\x14&\xa8\x07\x05h\x82\x11\x11 \xfd\x11H\x82 1\x84[\x11\x82Hn\x85i\x8f\x80\
\xba&"\x82\x08\xbf\x13\x16\xd4\x03\x00\xe4\xa2I\x9c'
}

	def name (self):
		return 'Allergies'

	def MenuInfo (self):
		return ('view', '&Allergies')

	def GetIconData(self, anIconID = None):
		if anIconID == None:
			return self.__icons[_("""icon_letter_A""")]
		else:
			if self.__icons.has_key(anIconID):
				return self.__icons[anIconID]
			else:
				return self.__icons[_("""icon_letter_A""")]

	def GetWidget (self, parent):
		pass
#		return gmAllergyWidgets.cAllergyPanel (parent, -1)

#============================================================================
if __name__ == "__main__":
	print "no unit test available"
#	from wxPython.wx import *
#	app = wxPyWidgetTester(size = (600, 600))
#	app.SetWidget(AllergyPanel, -1)
#	app.MainLoop()
#============================================================================
# $Log: gmGP_Allergies.py,v $
# Revision 1.26  2007-05-21 14:50:05  ncq
# - cleanup
#
# Revision 1.25  2004/07/17 21:16:39  ncq
# - cleanup/refactor allergy widgets:
#   - Horst space plugin added
#   - Richard space plugin separated out
#   - plugin independant GUI code aggregated
#   - allergies edit area factor out from generic edit area file
#
# Revision 1.24  2004/07/15 23:30:16  ncq
# - 'clinical_record' -> get_clinical_record()
#
# Revision 1.23  2004/06/25 13:28:00  ncq
# - logically separate notebook and clinical window plugins completely
#
# Revision 1.22  2004/03/19 21:07:35  shilbert
# - fixed module import
#
# Revision 1.21  2004/02/25 09:46:23  ncq
# - import from pycommon now, not python-common
#
# Revision 1.20  2004/02/05 23:51:01  ncq
# - wxCallAfter() use
#
# Revision 1.19  2003/12/02 02:10:14  ncq
# - comment out stuff so it won't complain, rewrite cleanly eventually !
#
# Revision 1.18  2003/11/23 13:59:10  sjtan
#
# _print removed from base class, so remove debugging calls to it.
#
# Revision 1.17  2003/11/17 10:56:41  sjtan
#
# synced and commiting.
#
# Revision 1.3  2003/10/27 14:01:26  sjtan
#
# syncing with main tree.
#
# Revision 1.2  2003/10/25 08:29:40  sjtan
#
# uses gmDispatcher to send new currentPatient objects to toplevel gmGP_ widgets. Proprosal to use
# yaml serializer to store editarea data in  narrative text field of clin_root_item until
# clin_root_item schema stabilizes.
#
# Revision 1.1  2003/10/23 06:02:40  sjtan
#
# manual edit areas modelled after r.terry's specs.
# Revision 1.16  2003/11/09 14:52:25  ncq
# - use new API in clinical record
#
# Revision 1.15  2003/10/26 01:36:14  ncq
# - gmTmpPatient -> gmPatient
#
# Revision 1.14  2003/06/03 14:28:33  ncq
# - some cleanup, Syans work starts looking good
#
# Revision 1.13  2003/06/01 13:20:32  sjtan
#
# logging to data stream for debugging. Adding DEBUG tags when work out how to use vi
# with regular expression groups (maybe never).
#
# Revision 1.12  2003/06/01 12:55:58  sjtan
#
# sql commit may cause PortalClose, whilst connection.commit() doesnt?
#
# Revision 1.11  2003/06/01 12:46:55  ncq
# - only add pathes if running as main so we don't obscure problems outside this module
#
# Revision 1.10  2003/06/01 01:47:33  sjtan
#
# starting allergy connections.
#
# Revision 1.9  2003/05/21 14:11:26  ncq
# - much needed rewrite/cleanup of gmEditArea
# - allergies/family history edit area adapted to new gmEditArea code
# - old code still there for non-converted edit areas
#
# Revision 1.8  2003/02/02 10:07:58  ihaywood
# bugfix
#
# Revision 1.7  2003/02/02 08:49:49  ihaywood
# demographics being connected to database
#
# Revision 1.6  2003/01/14 20:18:57  ncq
# - fixed setfont() problem
#
# Revision 1.5  2003/01/09 12:01:39  hherb
# connects now to database
#
# @change log:
#	    10.06.2002 rterry initial implementation, untested
#       30.07.2002 rterry images inserted, code cleaned up
