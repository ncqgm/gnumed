#!/usr/bin/python
#############################################################################
#
# gmPersonDetailsDlg - dialog & plugin for personal details like name and adddress
#                     (part of the gnumed package)
# ---------------------------------------------------------------------------
#
# @author: Dr. Horst Herb
# @copyright: author
# @license: GPL (details at http://www.gnu.org)
# @dependencies: nil
# @change log:
#	10.03.2002 hherb first draft, largely untested
#
# @TODO: Almost everything
############################################################################

from wxPython.wx import *
import gettext
_ = gettext.gettext

import gmPersonDetails, gmPlugin, gmCachedPerson, gmCachedAddress

ID_BUTTON_SAVE = wxNewId()
ID_BUTTON_ADD = wxNewId()
ID_BUTTON_NEW = wxNewId()
ID_BUTTON_UNDO = wxNewId()
ID_BUTTON_FAMILY = wxNewId()
ID_BUTTON_DELETE = wxNewId()
ID_BUTTON_MERGE = wxNewId()
ID_BUTTON_EXPORT = wxNewId()
ID_BUTTON_IMPORT = wxNewId()



class PersonDetailsDlg(gmPersonDetails.PnlPersonDetails, gmPlugin.wxGuiPlugin):

	def __init__(self, parent, id, guibroker=None, callbackbroker=None, dbbroker=None, name=_("PersonDetails")):
		gmPersonDetails.PnlPersonDetails.__init__(self, parent, id)
		gmPlugin.wxGuiPlugin.__init__(self, name, guibroker, callbackbroker, dbbroker)
		self.__person = gmCachedPerson.CachedPerson()
		self.__address = gmCachedAddress.CachedAddress()
		self.__person.notify_me("PersonDetailsDlg", self.OnDataUpdate)
		#add a button container to the bottom of the dialog
		line = wxStaticLine( self, -1, wxDefaultPosition, wxDefaultSize, wxLI_HORIZONTAL )
		self.szrTop.AddWindow( line, 0, wxGROW|wxALIGN_CENTER_VERTICAL|wxALL, 0 )
		self.szrCommandButtons = wxBoxSizer(wxHORIZONTAL)
		#add a few command buttons
		self.btnSave = self.AddButton(ID_BUTTON_SAVE, _("&Save"),  self.szrCommandButtons, self.OnSave)
		self.btnUndo = self.AddButton(ID_BUTTON_ADD, _("&Undo"),  self.szrCommandButtons, self.OnUndo)
		self.btnNew = self.AddButton(ID_BUTTON_NEW, _("&New"),  self.szrCommandButtons, self.OnNew)
		self.btnDelete = self.AddButton(ID_BUTTON_DELETE, _("&Delete"),  self.szrCommandButtons, self.OnDelete)
		self.szrTop.AddSizer(self.szrCommandButtons, 1, wxLEFT|wxRIGHT|wxBOTTOM, 5)
		self.szrTop.Fit( parent )
		self.szrTop.SetSizeHints( parent )


	def AddButton(self, id, caption, szr, callback):
		btn = wxButton( self, id, caption, wxDefaultPosition, wxDefaultSize, 0 )
		szr.AddWindow( btn, 0, wxALIGN_BOTTOM|wxALIGN_CENTER_VERTICAL, 5 )
		EVT_BUTTON(self, id, callback)
		return btn

	def OnNew(self, evt):
		print evt.GetId()

	def OnSave(self, evt):
		print evt.GetId()

	def OnDelete(self, evt):
		print evt.GetId()

	def OnUndo(self, evt):
		print evt.GetId()

	def SetPersonId(self, id):
		pass

	def ClearPersonData(self):
		self.comboTitle.SetSelection(0)
		self.tcGivenNames.Clear()
		self.tcSurnames.Clear()
		self.tcAka.Clear()
		self.chPreferredName.SetSelection(0)
		self.chGender.Clear()
		self.tcDob.Clear()
		self.cbCob.SetSelection(0)


	def ClearAddressData(self):
		self.cbAddressAt.SetSelection(0)
		self.tcAddress1.Clear()
		self.tcStreetNo.Clear()
		self.tcStreet.Clear()
		self.tcCity.Clear()
		self.chCountry.SetSelection(0)
		self.cbPhoneFor.SetSelection(0)
		self.tcAreacode.Clear()
		self.tcPhonenumber.Clear()
		self.tcPhoneComment.Clear()
		self.cbUrlCategory.SetSelection(0)
		self.tcURL.Clear()


	def SetPersonData(self, person=None):
		if person is None:
			self.ClearPersonData()
			return
		p=person	#less typing ...
		self.comboTitle.SetValue(p["title"])
		self.tcGivenNames.SetValue(p["firstnames"])
		self.tcSurnames.SetValue(p["lastnames"])
		#self.chPreferredName.SetStringSelection(p["preferred"])
		#self.tcAka.SetValue(p[])
		self.chGender.SetStringSelection(p["gender"])
		self.tcDob.SetValue(p["dob"])
		self.cbCob.SetSelection(0)


	def SetAddressData(self, address=None):
		if address is None:
			self.ClearAddressData()
			return
		a=address	#less typing ...
		self.cbAddressAt.SetSelection(a["adr_at"])
		self.tcAddress1.SetValue(a["street2"])
		self.tcStreetNo.SetValue(a["number"])
		self.tcStreet.SetValue(a["street"])
		self.tcCity.SetValue(a["city"])
		self.chCountry.SetStringSelection(a["country"])
		#self.cbPhoneFor.SetSelection()
		#self.tcAreacode.SetValue()
		#self.tcPhonenumber.SetValue()
		#self.tcPhoneComment.SetValue()
		#self.cbUrlCategory.SetSelection(0)
		#self.tcURL.SetValue()

	def ClearData(self):
		self.ClearPersonData()
		self.ClearAddressData()


	def OnDataUpdate(self, updater, id):
		#<DEBUG>
		#print "On data update, Person ID =", id
		#</DEBUG>
		self.SetPersonData(self.__person.dictresult(id))
		addresslist = self.__person.addresses(id)
		if len(addresslist) > 0:
			print addresslist
			homeaddress = addresslist[0]
			self.SetAddressData(self.__address.dictresult(homeaddress[0]))

	def OnSaveData(self, updateflag=0):
		if updateflag:
			pass
			#person attribute changed?
			#address attribute changed?
		else:
			pass
			#save person
			#save address








##########################################################################

if __name__ == "__main__":
	app = wxPyWidgetTester(size = (400, 500))
	app.SetWidget(PersonDetailsDlg, -1)
	app.MainLoop()
