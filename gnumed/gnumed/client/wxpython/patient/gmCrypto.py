# a simple wrapper for the cryptowidget
from wxPython.wx import *
import gmPlugin
import gmCryptoText
import images_gnuMedGP_Toolbar

ID_CRYPTO = wxNewId ()

class gmCrypto (gmPlugin.wxPatientPlugin):
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
