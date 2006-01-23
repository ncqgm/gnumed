from Gnumed.wxGladeWidgets.wxgAU_StaffMgrPanel import  cAU_StaffMgrPanel 
from Gnumed.wxpython.gmAU_ProviderFind import cAU_ProviderFind
from Gnumed.wxpython.gmAU_ProviderFind import cProviderSelector
from Gnumed.pycommon import gmPG
import wx

class cAU_StaffMgrPanelV01(cAU_StaffMgrPanel):

	def __init__(self, parent , id = -1):
		cAU_StaffMgrPanel.__init__(self,parent, id)
		self.populate_staff_list()

	
	def populate_staff_list(self):
		result = gmPG.run_ro_query("historica", "select pk_staff, title, firstnames, lastnames, role, dob, db_user, short_alias, comment from dem.v_staff")
		
		lc = self.list_ctrl_1
		
		lc.ClearAll()
		titles = ['pk', 'title', 'first names', 'last names', 'role', 'dob' , 'db_user']
		for col, i in zip(titles, range(len(titles)) ):
			lc.InsertColumn(i,col)
		
		if result:
			for vals, i in zip(result, range(len(result))):
				for val, j in zip ( vals, range(len(titles)) ):

					if titles[j] =='dob':
						val = str(val).split(' ')[0]

					if j == 0:	
						lc.InsertStringItem(i,str(val))
					else:
						print val
						lc.SetStringItem(i,j, str(val))

			self.data = {}
			for vals in result:
				pk = vals[0]
				self.data[pk] = {}
				for val, key in zip ( vals, titles+['short_alias', 'comment'] ):
					self.data[pk][key] = val

		for i in range(len(titles)):
			lc.SetColumnWidth(i, wx.LIST_AUTOSIZE)
						  			
		
	def enlist_staff( self, evt):
		dlg = wx.Dialog( self, -1, "Create Provider")

	        c = cAU_ProviderFind(dlg )
		dlg.Fit()
	        if dlg.ShowModal() == wx.ID_OK:
			pass

	       	self.populate_staff_list()
				
	def staff_listitem_selected(self, event):
	 	ix = event.GetIndex()
		#import pdb
		#pdb.set_trace()
		pk = int ( self.list_ctrl_1.GetItem( ix, 0).GetText())
		vals = self.data[pk]
		self.text_ctrl_1.SetValue( str(vals['title']) + '. '+ vals['first names'] + ' ' + vals['last names'])
		self.text_ctrl_2.SetValue( vals['db_user'])
		
		self.text_ctrl_4.SetValue( vals['role'])
		self.text_ctrl_5.SetValue( vals['short_alias'])
		self.text_ctrl_6.SetValue( str(vals['comment']))




if __name__ == "__main__":
	a = wx.App()
	f = wx.Frame(None, -1, "Test StaffMgr")
	p = cAU_StaffMgrPanelV01(f)
	f.Fit()
	f.Show(1)
	a.SetTopWindow(f)
	a.MainLoop()
	
