
from wxPython.wx import *
import string

		
class CharValidator:
	def __init__(self):
		self.enabled = 1
		self.lowercase = range(97, 123)
		self.uppercase = range(65, 91)
		self.digits = range(48, 58)
		self.print_other = range(18, 48) + range( 58 , 65) + range(91, 97) + range(123,126)
		self.print_other.remove(32)
		self.print_other.remove(39)
		self.apostrophe = range(39, 40)


	def setSingleSpace(self, control):
		EVT_CHAR( control, self.allow_single_spaces)

	def setUpperAlpha(self, control):
		EVT_CHAR( control, self.allow_upper_only_exclusive)

	def setCapitalize(self, control):
		EVT_CHAR( control, self.capitalize_exclusive)
			
	def setDigits(self, control):
		EVT_CHAR( control, self.allow_digits_only)

	def allow_single_spaces(self, keyEvent):
		"""wrapper for handling single space input"""
		if self._allow_single_spaces(keyEvent) == 0:
			keyEvent.Skip()
	
	def _allow_single_spaces(self, keyEvent):
		"""intercepts space input and vetos extra spaces.
		returns 1 if intercepted and Skip() was called or 0 if no event was handled.
		"""
		textCtrl = keyEvent.GetEventObject()
		if keyEvent.GetKeyCode() == WXK_TAB:
			keyEvent.Skip(0)
			return 1

		if keyEvent.GetKeyCode() == WXK_SPACE and ( 
				textCtrl.GetInsertionPoint() == 0
				or textCtrl.GetValue()[textCtrl.GetInsertionPoint()-1] == ' '
				):
			keyEvent.Skip(0)
			return 1
	
		return 0
	
	def allow_upper_only_exclusive(self, keyEvent):
		"""wrapper for converting to upper case and single spaces
		converts intercepts lowercase input and puts in uppercase.
		"""
		print "keyCode=", keyEvent.GetKeyCode()
		if not self._allow_case_only(keyEvent, self.lowercase, string.ascii_uppercase, exclusiveof = self.print_other + self.digits):
			keyEvent.Skip()	

	def allow_lower_only(self, keyEvent):
		""" wrapper to convert uppercase to lowercase.
		"""	
		if not  self._allow_case_only( self, keyEvent, self.uppercase, string.acii_lowercase):
			keyEvent.Skip()

	def allow_digits_only( self, keyEvent):

		if self._allow_single_spaces(keyEvent):
			return 

		k = keyEvent.GetKeyCode()
		
		if k in self.lowercase or k in  self.uppercase or k in self.print_other or k in  self.apostrophe:
			keyEvent.Skip(0)
			return

		keyEvent.Skip(1)
		

	
	def _allow_case_only( self, keyEvent, case, stringTargetCase, exclusiveof = []):
		if self._allow_single_spaces(keyEvent):
			return 1

		print "not processed by single space"

		c = keyEvent.GetEventObject()
		
		if keyEvent.GetKeyCode() in case:
			print "in range"
			keyEvent.Skip(0)
			
			p = c.GetInsertionPoint()
			
			print "insertion point =", p, " length of text=", len(c.GetValue())	
			t = c.GetValue()	
			u = stringTargetCase[keyEvent.GetKeyCode() - case[0]] 	
			print len(t),len(u)
			#wxwidget's initial value bug.
			t = self._remove_init_whitespace_bug(t)
			c.SetValue(t+u)
			print len(t),len(u)
			print p
			c.SetInsertionPoint(p+1)
			return 1
		
		if exclusiveof <>[] and keyEvent.GetKeyCode()  in exclusiveof:
			keyEvent.Skip(0)
			return 1
		return 0

	def capitalize_exclusive(self, keyEvent):
		if not self._capitalize(keyEvent):
			if  keyEvent.GetKeyCode()  in self.print_other + self.digits :
				keyEvent.Skip(0)
				return
				
			keyEvent.Skip(1)	

	def _remove_init_whitespace_bug(self,t):
			if (t.isspace() and len(t) == 1):
				t = ''
			return t

	def _capitalize(self, keyEvent):
		if self._allow_single_spaces(keyEvent):
			return 1
		k = keyEvent.GetKeyCode()
		if k in self.lowercase:
			keyEvent.Skip(0)
			c = keyEvent.GetEventObject()
			p = c.GetInsertionPoint()
			t = c.GetValue()
			#wxwidget's initial value bug.
			t = self._remove_init_whitespace_bug(t)
			
			words = t.split(' ')
			if len(t) == 0 or filter(lambda(x): x.strip() <>'' ,words) ==[] or t[-1] == ' ' or (len(words)> 0 and words[-1] in ['Mac', 'Mc' , "O'"] ):
				t += string.ascii_uppercase[k-self.lowercase[0]]
			else:
				t += string.ascii_lowercase[k - self.lowercase[0]]
			c.SetValue(t)
			c.SetInsertionPoint(p+1)
			return 1
		
		return 0
			
		
	
