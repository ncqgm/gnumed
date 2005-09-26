# a simple wrapper for the cryptowidget

try:
	import wxversion
	import wx
except ImportError:
	from wxPython import wx

from Gnumed.wxpython import gmPlugin_Patient, images_gnuMedGP_Toolbar, gmCryptoText 

ID_CRYPTO = wxNewId ()

class gmCrypto (gmPlugin_Patient.wxPatientPlugin):
    """
    Plugin to encapsulate the cryptowidget
    """
    def name (self):
        return 'Test cryptowidget'

    def MenuInfo (self):
        return ('view', '&Crypto')

    def GetIcon (self):
    	return wxBitmapFromXPMData([
	"16 16 2 1",
	"       c None",
	".      c #ED0B47",
	"                ",
	"                ",
	"                ",
	"             .  ",
	"            . . ",
	"           .   .",
	" ...........   .",
	" ...........   .",
	" ..  ..    .   .",
	" ..  ..     . . ",
	" ..  ..      .  ",
	" ..  ..         ",
	"                ",
	"                ",
	"                ",
	"                "])

    def GetWidget (self, parent):
	return gmCryptoText.gmCryptoText (parent, -1)
