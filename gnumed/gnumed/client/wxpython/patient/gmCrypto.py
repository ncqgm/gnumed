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
        return images_gnuMedGP_Toolbar.getToolbar_CryptoBitmap()

    def GetWidget (self, parent):
        return gmCryptoText.gmCryptoText (parent, -1)
