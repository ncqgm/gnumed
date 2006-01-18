import Gnumed.wxpython.gmPatSearchWidgets as psw

from  Gnumed.pycommon import gmSignals, gmDispatcher, gmPG

from  Gnumed.business.gmPerson  import cPerson

from Gnumed.wxpython.gmDemographicsWidgets import cNewPatientWizard

from Gnumed.wxpython.gmAU_DBUserSetup import cAU_DBUserSetup, populate_pg_user_list

from Gnumed.wxpython.gmAU_StaffV01 import cAU_StaffV01

from Gnumed.wxpython.gmAU_AdminLoginV01 import cAU_AdminLoginDialogV01 as AdminLoginDialog

import wx

class cProviderSelector(psw.cPatientSelector):
	def __init__(self, parent, id = -1):
		psw.cPatientSelector.__init__( self, parent, id)
		self.provider = None
		self.existing_staff = None

	def SetActivePatient( self, pat):
		#import pdb
		#pdb.set_trace()
		if pat and pat <> -1:
			self.provider = cPerson( pat)
			self.SetValue( self.provider.get_identity()['description'] )
			
			result = gmPG.run_ro_query("historica", "select s.pk, db_user, (select name from dem.staff_role r where r.pk = fk_role), sign , comment from dem.staff s where s.fk_identity = %s" % self.provider.getID()  )
			if result and wx.MessageDialog(self, _("Warning. Selected Person already staff member. Continue ? ")).ShowModal() <> wx.ID_OK:
				self.provider = None
				self.SetValue("")
			elif result:
				self.existing_staff = dict(zip(['staff_pk', 'db_user', 'role', 'sign', 'comment'], result[0] ))
			else:
				self.existing_staff = None

			print "self.provider is ", self.provider

		gmDispatcher.send( gmSignals.provider_identity_selected())


class cAU_ProviderFind(wx.Panel):

	def __init__(self, parent, id = -1 ):
		wx.Panel.__init__(self, parent, id)
		
		sz1= wx.BoxSizer(wx.VERTICAL)
		sz2 = wx.BoxSizer(wx.HORIZONTAL)
		sz3 = wx.BoxSizer(wx.HORIZONTAL)
		
		self.label_1 = wx.StaticText(self, -1, _("Search Provider Identity by Name:"))
		
		self.prov_search = cProviderSelector( self, -1 )
		

		self.button_1 = wx.Button( self, -1, _("Create New Provider Identity"))

		self.button_2 = wx.Button( self, -1, _("Link Selected Identity >> "))
	

		sz2.Add( self.label_1, proportion = 1, flag = wx.ALL, border = 10) 
		sz2.Add( self.prov_search, proportion = 2, flag = wx.ALL | wx.EXPAND , border = 10) 
		sz3.Add( self.button_1, proportion = 1, flag = wx.ALL, border = 10) 
		sz3.Add( self.button_2, proportion = 1, flag = wx.ALL, border = 10) 
	
		sz1.Add( sz2 )
		sz1.Add( sz3 )

		self.SetSizer(sz1)

		sz1.Fit(self)

		self.Bind(wx.EVT_BUTTON, self.create_new_provider_identity,  self.button_1)
		self.Bind(wx.EVT_BUTTON, self.associate_pg_user, self.button_2)

		gmDispatcher.connect( signal = gmSignals.provider_identity_selected(), receiver = self.provider_selected)

		self.button_2.Enable(False)	

	def provider_selected(self):
		self.button_2.Enable(  self.prov_search.provider <> None)

	def create_new_provider_identity(self, evt):
	       	c = cNewPatientWizard( self, title = _('Register new provider'), subtitle = _('New Provider details') )
       		ident = c.RunWizard(activate = False)
		self.prov_search.SetActivePatient(ident)
        	print "wizard gave ", ident

	def associate_pg_user(self, evt):
		pass
		dlg = wx.Dialog(self, -1 , "Link identity to a pg user")
		p = cAU_DBUserSetup(dlg)
		if self.prov_search.existing_staff:
			p.set_existing_db_user( self.prov_search.existing_staff['db_user'])
		dlg.Fit()
		if dlg.ShowModal() == wx.ID_OK:
			person = self.prov_search.provider	
			dlg2 = wx.Dialog(self, -1, "Create Staff" )
			p2 = cAU_StaffV01(dlg2)
			dlg2.Fit()
			(w,h) = dlg2.GetSizeTuple()
			dlg2.SetSize( wx.Size(w *2, h) )
			p2.set_data(person , p.pg_user, p.groups )
			if self.prov_search.existing_staff:
				e = self.prov_search.existing_staff
				for k,v in e.items():
					if not v:
						v = ''
					e[k] = str(v)
						
				p2.set_staff_data(e['role'], e['sign'], e['comment'])
			if dlg2.ShowModal() == wx.ID_OK:
			
				
				existing = gmPG.run_ro_query( 'historica', 'select pk from dem.staff  s where s.fk_identity = %s' % str(person.getID()) )
				if existing and len(existing) > 0:
					# need to update staff
					stmt = "update dem.staff set db_user = '%s' , fk_role = ( select pk from dem.staff_role where name='%s') , sign ='%s', comment='%s' where fk_identity = %s " % (p.pg_user, p2.role, p2.sign ,p2.comment,  person.getID() )

				else:
					# need to insert staff
	
					stmt = """insert into dem.staff(  fk_identity, fk_role, db_user, sign, comment) values ( %s, (select pk from dem.staff_role where name = '%s') , '%s', '%s', '%s' )""" % ( person.getID(), p2.role , p.pg_user, p2.sign, p2.comment)

				print "doing ", stmt
				con = su_login(self)
				cu = con.cursor()
				cu.execute(stmt)
				con.commit()

				wx.MessageDialog(self, _("New Staff has been created.")).ShowModal()

				try:
					if self.GetParent().IsModal():
						self.GetParent().EndModal(wx.ID_OK)
				except:
					print "parent was not dialog for ", self, " so EndModal failed"
					
				
def su_login(parent):
	dlg = AdminLoginDialog(parent, -1) 
	con = None
	if dlg.ShowModal() == wx.ID_OK: 
		con = dlg.get_connection() 
	return con
								
		

if __name__== "__main__":
	a = wx.App()	
	f = wx.Frame( None, -1 ,"Test Panel")
	c = cProviderSelectPanel(f)
	f.Fit()
	a.SetTopWindow(f)
	f.Show(1)
	a.MainLoop()
	
