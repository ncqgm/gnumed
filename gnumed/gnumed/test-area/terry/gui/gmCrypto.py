# a simple wrapper for the cryptowidget
from wxPython.wx import *
import gmPlugin
import gmCryptoText
import images_gnuMedGP_Toolbar

ID_CRYPTO = wxNewId ()

class gmCrypto (gmPlugin.wxBasePlugin):
    """
    Plugin to encapsulate the cryptowidget
    """
    def name (self):
        return 'CryptoPlugin'

    def register (self):
         self.mwm = self.gb['main.manager']
         self.mwm.RegisterLeftSide ('cryptowidget', gmCryptoText.gmCryptoText
                                    (self.mwm, -1))
         tb2 = self.gb['main.bottom_toolbar']
         tb2.AddSeparator()
         tool1 = tb2.AddTool(ID_CRYPTO,
                             images_gnuMedGP_Toolbar.getToolbar_CryptoBitmap(),
                             shortHelpString="Test Cryptowidget")
         EVT_TOOL (tb2, ID_CRYPTO, self.OnCryptoTool)
        
    def OnCryptoTool (self, event):
        self.mwm.Display ('cryptowidget')
