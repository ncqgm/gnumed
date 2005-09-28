#!/usr/bin/python
#############################################################################
#
# gmCryptoText - implements a "crypto" aware text widget
# ---------------------------------------------------------------------------
# This text widget allows arbitrary text to be entered via keyboard,
# cut'n paste via clipboard, or text files via drag'n drop
# Right clicking pops up a menu that allows to encrypt or decrypt
# the selected text segment.
#
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: wxPython (>= version 2.3.1)
# @change log:
#	30.06.2001 hherb initial implementation, untested
#	25.10.2001 commenting of source, module test enabled, debug log inserts removed
#
# @TODO:
#	- all runtime error checking / exception handling
#	- plug in structure for ciphers, rich popup menu selection of crypto methods
#	- use Python OpenSSL wrappers or GnuPG wrapper!
#	- tagging of the used cipher and the user within the encrypted text
#	- timer that expires pas phrase after arbitrary time intervals
#	- implement a "rich text" widget
############################################################################


"""This module implements a ""crypto"" aware text widget

This text widget allows arbitrary text to be entered via keyboard,
cut'n paste via clipboard, or text files via drag'n drop
Right clicking pops up a menu that allows to encrypt or decrypt
the selected text segment.
"""

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

import string, rotor, binascii

ID_POP_ENCRYPT = wx.NewId()
ID_POP_DECRYPT = wx.NewId()
ID_POP_PASSPHRASE = wx.NewId()

class gmTextctrlFileDropTarget(wx.FileDropTarget):
    """ a generic text control widget that accepts dropped files """

    def __init__(self, textwindow):
        wx.FileDropTarget.__init__(self)
        self.textwindow=textwindow

    def OnDropFiles(self, x, y, filenames):
        """inserts the dropped file(s) content(s) at the cursor position"""
        for file in filenames:
            self.textwindow.WriteText(string.join(open(file, 'r').readlines()))


class gmCryptoText(wx.TextCtrl):
    """A special text widget that supports cryptography

    A right mouse click pops up a manu that allows to encrypt
    or decrypt selected text segments.
    You can drag and drop any number of text files into the text
    widget, and that text will be inserted at the current cursor
    position
    """

    def __init__(self, parent, id, size=wxDefaultSize, style=wx.TE_MULTILINE|wx.TE_RICH, defaulttext=None):
        #initialize parent class
        wx.TextCtrl.__init__(self, parent, id, size=size, style=style)
 	self.SetDefaultStyle(wx.TextAttr(wx.RED))

        #will search for text tags within fuzzymargin characters
        self.fuzzymargin = 25
        self.passphrase = None
        #time in seconds until passphrase expires
        self. passphrase_expiry = 120
        #the text selected for encryption/decryption
        self.textselection = None
        self. selectionStart = 0
        self.selectionEnd = 0

	if defaulttext is not None:
		self.WriteText(defaulttext)

        #a reserved ID for events related to this widget
        self.aID = wx.NewId()

        #make this text widget a drop target for drag&dropped text files
        dt = gmTextctrlFileDropTarget(self)
        self.SetDropTarget(dt)

        #bugger... this one for wxGTK
        EVT_RIGHT_UP(self,self.OnRightClick)
        EVT_RIGHT_DOWN(self, self.OnRightDown)

        #...and this one for wxMSW (hope this inconsistency is fixed soon
        #EVT_COMMAND_RIGHT_CLICK(self, self.aID, self.OnRightClick)

    def OnRightClick(self, event):
        "A right mouse click triggers a popup menu for cryptographic functionality"

        self.selectionStart, self.selectionEnd = self.GetSelection()

        #create a popup menu
        menu = wx.Menu()
        menu.Append(ID_POP_ENCRYPT, _("Encrypt"))
        menu.Append(ID_POP_DECRYPT, _("Decrypt"))
        menu.Append(ID_POP_PASSPHRASE, _("Set pass phrase"))

        #connect the events to event handler functions
        EVT_MENU(self, ID_POP_ENCRYPT, self.OnEncrypt)
        EVT_MENU(self, ID_POP_DECRYPT, self.OnDecrypt)
        EVT_MENU(self, ID_POP_PASSPHRASE, self.OnSetPassphrase)

        #show the menu
        self.PopupMenu(menu, wxPoint(event.GetX(), event.GetY()))

        #free resources
        menu.Destroy()

        #anybody else needs to intercept right click events?
        event.Skip()


	def OnContextMenu(self, event):
		pass


    def OnEncrypt(self, event):
        """triggered by popup contect menu event"""

        #get the selected text if any
        self.textselection = self.GetValue()[self.selectionStart:self.selectionEnd]
        #anything to do?
        if len(self.textselection)<1:
            return

        #we can't crypt without passphrase, so ask for it if needed!
        if self.passphrase is None:
            self.passphrase = self.AskForPassphrase()
            if self.passphrase == None:
                return
        #In order to be displayed, binary crypt output has to be 'hexlified'
        #encrypted text is tagged with <! ... !>
        #future versions will embed a algorithm tag here
        self.Replace(self.selectionStart, self.selectionEnd, \
                     '<!' + self.GetIdentTag() + binascii.hexlify(self.Encrypt(self.textselection, self.passphrase)) + '!>')


    def OnDecrypt(self, event):

        if self.passphrase is None:
            self.passphrase = self.AskForPassphrase()
            if self.passphrase == None:
                return

        textselection, self.selectionStart, self.selectionEnd = \
            self.FuzzyScanSelection(self.selectionStart, self.selectionEnd, self.fuzzymargin)
        #is the selection tagged as encrypted ?
        if textselection[:2] != '<!' or textselection[-2:] != '!>':
            wx.MessageBox(_("This is not correctly encrypted text!"))
            return
        #get rid of the tags
        textselection = textselection[2:-2]
        identtag, textselection = self.StripIdentTag(textselection)
        #self.textselection = self.textselection[len(identtag):]
        #and don't forget to unhexlify the ciphertext before you feed it to the crypt
        decoded = self.Decrypt(binascii.unhexlify(textselection), self.passphrase, identtag)
        self.Replace(self.selectionStart, self.selectionEnd, decoded)


    def OnSetPassphrase(self, event):
        self.passphrase = self.AskForPassphrase()


    def OnRightDown(self, event):
        """dummy function; if this event was not intercepted, GTK would
        clear the text selection the very moment the mouse button is clicked"""
        pass

    def AskForPassphrase(self):
        """asks for a pass phrase and returns it"""
        dlg = wxTextEntryDialog(self, _("Please enter your pass phrase:"), _("Pass phrase expired"), style=wxOK|wxCANCEL|wx.CENTRE|wx.TE_PASSWORD)
        if dlg.ShowModal() == wx.ID_OK:
            retval = dlg.GetValue()
        else:
            retval = None
        dlg.Destroy()
        return retval


    def Encrypt(self, cleartext, key):
        """override this function for your own crypto funcs"""
        rt = rotor.newrotor(key, 12)
        return rt.encrypt(cleartext)


    def Decrypt(self, ciphertext, key, identtag):
        """override this function for your own crypto funcs"""
        rt = rotor.newrotor(key, 12)
        return rt.decrypt(ciphertext)


    def StripIdentTag(self, text):
        """Remove the 'ident tag' from text and return both tag and test"""
        if text[0] != '[':
            "No ident tag ?"
            return '', text
        try:
            endtag = string.index(text, ']')+1
        except ValueError:
            return '', text
        return text[:endtag], text[endtag:]


    def GetIdentTag(self):
        """This is a 'virtual' function which should be overridden to provide your own meaningful tag"""
        return '[rotor]'


    def SetFuzzyMargin(self, margin):
        """The fuzzy margin is the number of characters on each side of the text selection
        the decryption algorithm will search for correct delimiters. It should be at least as long as
        the IdentTag is plus an extra 3 characters to allow for the crypto tag"""
        self.fuzzymargin = margin


    def FuzzyScanSelection(self, frompos, topos, margin):
        fulltext = self.GetValue()
        #search left margin
        start = frompos - margin
        if start < 0: start = 0
        if frompos == 0: frompos = 1
        #search right margin
        finish = topos + margin
        if finish > len(fulltext): finish = len(fulltext)
        if topos > len(fulltext)-2: topos = len (fulltext)-2
        try:
            left = string.rindex(fulltext, '<', start, frompos)
            right = string.index(fulltext, '>', topos, finish)+1
        except ValueError:
            wx.LogMessage("FuzzyScan went wrong")
            return ''
        return fulltext[left:right], left,right
 
#############################################################################
# test function for this module: simply run the module as "main"
# a text entry window will pop up. Write something, select arbitray
# segmnts of text with the mouse, and then right click the selection
# for options like encryption, decryption, and setting of passphrase
#############################################################################
if __name__ == '__main__':
	_ = lambda x:x
	app = wxPyWidgetTester(size = (400, 400))
	#show the login panel in a main window
	app.SetWidget(gmCryptoText, -1)
	app.MainLoop()
