# -*- coding: iso-8859-1 -*-
"""GnuMed date input widget

All GnuMed date input should happen via classes in
this module. Initially this is just a plain text box
but using this throughout GnuMed will allow us to
transparently add features.

@copyright: author(s)
"""
############################################################################
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/gmDateTimeInput.py,v $
# $Id: gmDateTimeInput.py,v 1.19 2005-06-08 22:01:42 cfmoro Exp $
__version__ = "$Revision: 1.19 $"
__author__  = "K. Hilbert <Karsten.Hilbert@gmx.net>"
__licence__ = "GPL (details at http://www.gnu.org)"

import re, string

import mx.DateTime as mxDT
from wxPython.wx import *

from Gnumed.pycommon import gmLog, gmMatchProvider, gmExceptions, gmI18N
from Gnumed.wxpython import gmPhraseWheel, gmGuiHelpers
from Gnumed.pycommon.gmPyCompat import *

_log = gmLog.gmDefLog
#============================================================
class cMatchProvider_Date(gmMatchProvider.cMatchProvider):
	def __init__(self):
		self.__allow_past = 1 
		self.__shifting_base = None
		self.__expanders = []
		self.__expanders.append(self.__single_number)
		self.__expanders.append(self.__explicit_offset)
		gmMatchProvider.cMatchProvider.__init__(self)
	#--------------------------------------------------------
	# internal matching algorithms
	#
	# if we end up here:
	#	- aFragment will not be "None"
	#   - aFragment will be lower case
	#	- we _do_ deliver matches (whether we find any is a different story)
	#--------------------------------------------------------
	def getMatchesByPhrase(self, aFragment):
		"""Return matches for aFragment at start of phrases."""
		self.__now = mxDT.now()
		matches = []
		for expander in self.__expanders:
			items = expander(aFragment)
			if items is not None:
				matches.extend(items)
		if len(matches) > 0:
			return (True, matches)
		else:
			return (False, [])
	#--------------------------------------------------------
	def getMatchesByWord(self, aFragment):
		"""Return matches for aFragment at start of words inside phrases."""
		return self.getMatchesByPhrase(aFragment)
	#--------------------------------------------------------
	def getMatchesBySubstr(self, aFragment):
		"""Return matches for aFragment as a true substring."""
		return self.getMatchesByPhrase(aFragment)
	#--------------------------------------------------------
	def getAllMatches(self):
		"""Return all items."""
		return None
	#--------------------------------------------------------
	# date fragment expanders
	#--------------------------------------------------------
	def __single_number(self, aFragment):
		if not re.match("^(\s|\t)*\d+(\s|\t)*$", aFragment):
			return None
		val = aFragment.replace(' ', '')
		val = int(val.replace('\t', ''))

		matches = []
		# nth day of this month (if larger than today or past explicitely allowed)
		if (self.__now.day <= val) or (self.__allow_past):
			target_date = self.__now + mxDT.RelativeDateTime(day = val)
			tmp = {
				'data': target_date,
				'label': _('day %d of this month (a %s)') % (val, target_date.strftime('%A'))
			}
			matches.append(tmp)
		# day of next month
		target_date = self.__now + mxDT.RelativeDateTime(months = 1, day = val)
		tmp = {
			'data': target_date,
			'label': _('day %d of next month (a %s)') % (val, target_date.strftime('%A'))
		}
		matches.append(tmp)
		# X days from now (if <32)
		if val < 32:
			target_date = self.__now + mxDT.RelativeDateTime(days = val)
			tmp = {
				'data': target_date,
				'label': _('in %d days (a %s)') % (val, target_date.strftime('%A'))
			}
			matches.append(tmp)
		# X weeks from now (if <5)
		if val < 7:
			target_date = self.__now + mxDT.RelativeDateTime(weeks = val)
			tmp = {
				'data': target_date,
				'label': _('in %d weeks (a %s)') % (val, target_date.strftime('%A'))
			}
			matches.append(tmp)
		# day of this week
		# day of next week
		return matches
	#--------------------------------------------------------
	def __explicit_offset(self, aFragment):
		# "+/-XXd/w/m/t"
		if not re.match("^(\s|\t)*(\+|-)?(\s|\t)*\d{1,2}(\s|\t)*[mdtw](\s|\t)*$", aFragment):
			return None
		# allow past ?
		is_future = 1
		if string.find(aFragment, '-') > -1:
			is_future = 0 
			if not self.__allow_past:
				return None

		val = int(re.search('\d{1,2}', aFragment).group())
		target_date = None
		if re.search('[dt]', aFragment):
			if is_future:
				target_date = self.__now + mxDT.RelativeDateTime(days = val)
				label = _('in %d days (a %s)') % (val, target_date.strftime('%A'))
			else:
				target_date = self.__now - mxDT.RelativeDateTime(days = val)
				label = _('%d days ago (a %s)') % (val, target_date.strftime('%A'))
		elif re.search('[w]', aFragment):
			if is_future:
				target_date = self.__now + mxDT.RelativeDateTime(weeks = val)
				label = _('in %d weeks (a %s)') % (val, target_date.strftime('%A'))
			else:
				target_date = self.__now - mxDT.RelativeDateTime(weeks = val)
				label = _('%d weeks ago (a %s)') % (val, target_date.strftime('%A'))
		elif re.search('[m]', aFragment):
			if is_future:
				target_date = self.__now + mxDT.RelativeDateTime(months = val)
				label = _('in %d months (a %s)') % (val, target_date.strftime('%A'))
			else:
				target_date = self.__now - mxDT.RelativeDateTime(months = val)
				label = _('%d months (a %s)') % (val, target_date.strftime('%A'))
		if target_date is None:
			return None
		tmp = {
			'data': target_date,
			'label': label
		}
		return [tmp]
#==================================================
class gmDateInput(gmPhraseWheel.cPhraseWheel):
	def __init__(self, *args, **kwargs):
		matcher = cMatchProvider_Date()
		matcher.setWordSeparators('xxx_do_not_separate_words_xxx')
#		matcher.setIgnoredChars("""[?!."'\\(){}\[\]<>~#*$%^_]+""")
		matcher.setThresholds(aWord = 998, aSubstring = 999)

		if not kwargs.has_key('id_callback'):
			kwargs['id_callback'] =  self.__selected
		kwargs['aMatchProvider'] = matcher
		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)
		self.allow_multiple_phrases(None)
		
		self.__display_format = _('%Y-%m-%d')
		self.__default_text = _('enter date here')

		self.SetValue(self.__default_text)
		self.SetSelection (-1,-1)

		EVT_CHAR(self, self.__on_char)
#		EVT_KILL_FOCUS(self, self.__on_lose_focus)
		#EVT_KEY_DOWN (self, self.__on_key_pressed)

		self.__tooltip = _(
"""------------------------------------------------------------------------------
Date input field

 <ALT-v/g/h/m/ü>: vorgestern/gestern/heute/morgen/übermorgen
 <ALT-K>:         Kalender
 +/- X d/w/m:     X days/weeks/months ago/from now
------------------------------------------------------------------------------
""")
		self.SetToolTip(wxToolTip(self.__tooltip))
	#----------------------------------------------
	def on_list_item_selected (self):
		"""Gets called when user selected a list item."""
		self._hide_picklist()

		selection_idx = self._picklist.GetSelection()
		data = self._picklist.GetClientData(selection_idx)

		self.SetValue(data.strftime(self.__display_format))

		if self.notify_caller is not None:
			for f in self.notify_caller:
				f(data)
	#----------------------------------------------
	# event handlers
	#----------------------------------------------
	def __on_char(self, evt):
		keycode = evt.GetKeyCode()

		if evt.AltDown():
			if keycode in [ord('h'), ord('H')]:
				date = mxDT.now()
				self.SetValue(date.strftime(self.__display_format))
				return True
			if keycode in [ord('m'), ord('M')]:
				date = mxDT.now() + mxDT.RelativeDateTime(days = 1)
				self.SetValue(date.strftime(self.__display_format))
				return True
			if keycode in [ord('g'), ord('G')]:
				date = mxDT.now() - mxDT.RelativeDateTime(days = 1)
				self.SetValue(date.strftime(self.__display_format))
				return True
			if keycode in [ord('ü'), ord('Ü')]:
				date = mxDT.now() + mxDT.RelativeDateTime(days = 2)
				self.SetValue(date.strftime(self.__display_format))
				return True
			if keycode in [ord('v'), ord('V')]:
				date = mxDT.now() - mxDT.RelativeDateTime(days = 2)
				self.SetValue(date.strftime(self.__display_format))
				return True
			if keycode in [ord('k'), ord('K')]:
				print "Kalender noch nicht implementiert"
				return True

		evt.Skip()
	#--------------------------------------------------------
	def __validate(self):
		# skip empty value
		if self.GetValue() == '':
			return True
		# don't allow invalid input
		try:
			# FIXME: make this way more generous in accepting data input
			date = mxDT.strptime(self.GetValue(), self.__display_format)
		except:
			# invalid date			
			# FIXME: Gtk-WARNING **: GtkEntry - did not receive focus-out-event
			#        in wxwindows 2.4.x
			#gmGuiHelpers.gm_show_error(msg, _('Invalid date format'), gmLog.lErr)						
			msg = _('Invalid date. Date format: %s ' % self.__display_format)
			gmGuiHelpers.gm_beep_statustext(msg, gmLog.lErr)
			self.SetBackgroundColour('pink')
			self.Refresh()
#			if not event is None:
#				event.Skip()
			return False
			
		# valid date		
		self.SetBackgroundColour(wxSystemSettings_GetColour(wxSYS_COLOUR_WINDOW))
		self.Refresh()
#		if not event is None:
#			event.Skip()
		return True
	#--------------------------------------------------------
	def _on_lose_focus(self, event):
		self.__validate()
		gmPhraseWheel.cPhraseWheel._on_lose_focus(self, event)
	#----------------------------------------------
	def __on_key_pressed (self, key):
		"""Is called when a key is pressed."""
		print "on key pressed"
		if key.GetKeyCode in (ord('h'), ord('H')):
			date = mxDT.now()
			self.SetValue(date.strftime(self.__display_format))
			return
		if key.GetKeyCode in (ord('m'), ord('M')):
			date = mxDT.now() + mxDT.RelativeDateTime(days = 1)
			self.SetValue(date.strftime(self.__display_format))
			return
		if key.GetKeyCode in (ord('g'), ord('G')):
			date = mxDT.now() - mxDT.RelativeDateTime(days = 1)
			self.SetValue(date.strftime(self.__display_format))
			return
		if key.GetKeyCode in (ord('ü'), ord('Ü')):
			date = mxDT.now() + mxDT.RelativeDateTime(days = 2)
			self.SetValue(date.strftime(self.__display_format))
			return
		if key.GetKeyCode in (ord('v'), ord('V')):
			date = mxDT.now() - mxDT.RelativeDateTime(days = 2)
			self.SetValue(date.strftime(self.__display_format))
			return

		key.Skip()
	#--------------------------------------------------------		
	def SetValue(self, val):
		gmPhraseWheel.cPhraseWheel.SetValue(self, val)
		if len(val.strip()) and val != self.__default_text > 0:
			self.__validate()		
	#----------------------------------------------
	def __selected(self, data):
		pass
	#----------------------------------------------
	def set_value(self, aValue = None):
		"""Only set value if it's a valid one."""
		pass
	#----------------------------------------------	
	def set_range(self, list_of_ranges):
	#----------------------------------------------
		pass
#==================================================
class gmTimeInput(wxTextCtrl):
	def __init__(self, parent, *args, **kwargs):
		if len(args) < 2:
			if not kwargs.has_key('value'):
				kwargs['value'] = _('enter time here')
		wxTextCtrl.__init__(
			self,
			parent,
			*args,
			**kwargs
		)
	#----------------------------------------------
#==================================================
# main
#--------------------------------------------------
if __name__ == '__main__':
	#----------------------------------------------------
	def clicked (data):
		print "Selected :%s" % data
	#----------------------------------------------------
	class TestApp (wxApp):
		def OnInit (self):

			frame = wxFrame (
				None,
				-4,
				"date input wheel test for GNUmed",
				size=wxSize(300, 350),
				style=wxDEFAULT_FRAME_STYLE|wxNO_FULL_REPAINT_ON_RESIZE
			)

			date_wheel = gmDateInput(
				parent = frame,
				id = -1,
				pos = (50, 50),
				size = (180, 30)
			)
			date_wheel.on_resize (None)

			frame.Show (1)
			return 1
	#--------------------------------------------------------
	app = TestApp ()
	app.MainLoop ()

#	app = wxPyWidgetTester(size = (200, 80))
#	app.SetWidget(gmTimeInput, -1)
#	app.MainLoop()
#==================================================
# - free text input: start string with "
#==================================================
# $Log: gmDateTimeInput.py,v $
# Revision 1.19  2005-06-08 22:01:42  cfmoro
# Avoid validating when empty date
#
# Revision 1.18  2005/06/08 21:19:50  cfmoro
# Crash fix
#
# Revision 1.17  2005/06/04 09:55:32  ncq
# - also call parent class _on_lose_focus so we don't loose
#   callbacks set by other people
#
# Revision 1.16  2005/06/03 00:54:33  cfmoro
# Validte date in SetValue
#
# Revision 1.15  2005/06/03 00:36:54  cfmoro
# Validate date on setValue
#
# Revision 1.14  2005/06/02 23:28:54  cfmoro
# Date validation
#
# Revision 1.13  2005/04/25 17:11:33  ncq
# - set encoding for file
#
# Revision 1.12  2005/04/24 15:05:22  ncq
# - use gmI18N properly
#
# Revision 1.11  2004/12/23 16:20:15  ncq
# - add licence
#
# Revision 1.10  2004/07/18 20:30:53  ncq
# - wxPython.true/false -> Python.True/False as Python tells us to do
#
# Revision 1.9  2004/03/05 11:22:35  ncq
# - import from Gnumed.<pkg>
#
# Revision 1.8  2004/02/25 09:46:21  ncq
# - import from pycommon now, not python-common
#
# Revision 1.7  2003/11/05 22:21:06  sjtan
#
# let's gmDateInput specify id_callback in constructor list.
#
# Revision 1.6  2003/11/04 10:35:23  ihaywood
# match providers in gmDemographicRecord
#
# Revision 1.5  2003/10/06 17:49:40  ncq
# - remove dependancy on gmI18N on standalone test run
#
# Revision 1.4  2003/10/02 20:51:12  ncq
# - add alt-XX shortcuts, move __* to _*
#
# Revision 1.3  2003/09/30 18:47:47  ncq
# - converted date time input field into phrase wheel descendant
#
# Revision 1.2  2003/08/10 00:57:15  ncq
# - add TODO item
#
# Revision 1.1  2003/05/23 14:05:01  ncq
# - first implementation
#
