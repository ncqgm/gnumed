from pyjamas.ui.PopupPanel import PopupPanel
from pyjamas.ui.HTML import HTML

#======================================================
class cSimplePopup(PopupPanel):
    def __init__(self, txt, **kwargs):
        txt = HTML(txt)
        txt.addClickListener(self)

        PopupPanel.__init__(self, autoHide=True, StyleName="showcase-popup",
                            **kwargs)
        self.add(txt)
        self.show()
        
    def onClick(self, sender=None):
        self.hide()

