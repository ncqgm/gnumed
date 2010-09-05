from pyjamas.ui.PopupPanel import PopupPanel

#======================================================
class cSimplePopup(PopupPanel):
    def __init__(self, app, contents, **kwargs):
        self.app = app
        contents = contents
        contents.addClickListener(getattr(self, "onClick"))

        PopupPanel.__init__(self, autoHide=True, **kwargs)
        self.add(content)
        self.setStyleName("showcase-popup")
        self.show()
        
    def onClick(self, sender=None):
	self.hide()