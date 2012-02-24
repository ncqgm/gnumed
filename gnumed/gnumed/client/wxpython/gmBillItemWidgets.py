import wx

from Gnumed.wxGladeWidgets import wxgBillItemListPnl
from Gnumed.business import gmPerson
from Gnumed.business import gmBilling
#, gmBillItem
#from Gnumed.wxpython import gmRegetMixin

from Gnumed.pycommon import gmMatchProvider, gmDateTime, gmTools
from Gnumed.wxpython import gmPhraseWheel

from Gnumed.pycommon import gmDispatcher
from Gnumed.wxpython import gmGuiHelpers


class cBillItemListPnl(wxgBillItemListPnl.wxgBillItemListPnl
         #, gmRegetMixin.cRegetOnPaintMixin 
         ):


	def __init__(self, *args, **kwds):
		wxgBillItemListPnl.wxgBillItemListPnl.__init__(self, *args, **kwds)
                #gmRegetMixin.cRegetOnPaintMixin.__init__(self)
		self.__init_ui()

	def __init_ui(self):
		self._LCTRL_billitem.set_columns( [ _('Charge Date'),_('Encounter #'), _('Catalog'),_('#Units'),_('Charge Item'), _('Factor') ,_('Amount'), _('Details'), 
                    #_('Last modified by'),
                    _('Status'), _('Inv #') ])

		#if gmPerson.gmCurrentPatient().connected:
		#	pass

        def onSendPending(self, ev=None):
                from Gnumed.business import gmBill
		pat = gmPerson.gmCurrentPatient().ID
                inv = gmBill.get_latest_open_inv_for(pat)
                if inv is None:
                        inv = gmBill.create_inv( pat )
                        gmDispatcher.send(signal='statustext', msg=_('Invoice #%s created' % inv['pk'] ) )
                cntLines = inv.countPendingLines()
                if cntLines == 0:
                    gmDispatcher.send(signal='statustext',msg=_('No pending lines so nothing was assigned') )
                    return
                inv.assignPendingLines(with_close=1)
                #inv.close()

                self.__populate_idl()

                inv.refetch_payload()

                from Gnumed.business.gmBillFactory import PDFInvoice, pathToInvFile, writeCsvLines
                fn = pathToInvFile( inv['pk'] ) ##fn='/home/nl/lib/Gnumed/silo/%s.pdf' % inv['pk']
                f = open(fn,'w') #wb
                doc = PDFInvoice()
                f.write(doc.generatePDF(inv) )
                f.close()

                writeCsvLines(inv )

                from Gnumed.pycommon.gmMimeLib import call_viewer_on_file
                call_viewer_on_file(fn)


                return True
        def on_toggle_show_noninv(self, ev=None):
                self.__populate_idl()
		return True

	def _populate_with_data(self):
		print "loading bill items"
		self.__populate_idl()
		return True

	def __populate_idl(self):
		self.__idl = []

                showOpenOnly = self.checkbox_show_non_inv_only.GetValue()
                #print "Value of Checkbox is %s"  % showOpenOnly
		if gmPerson.gmCurrentPatient().connected:
		        curr_pat_id = gmPerson.gmCurrentPatient().ID
                        self.__idl = gmBillItem.get_all_bill_records_for( curr_pat_id, showOpenOnly )


		idl = [
			[
				m['date_to_bill'].strftime('%d.%m.%Y'),
				m['pk_encounter_to_bill'],
                                m['catalog_short'],
                                m['unit_count'],
				m['billable_description'],
                                m['amount_multiplier'], #%.2f
				m['net_amount_per_unit'], #@@final_amount
				m['item_detail'] or '',
                                #m['modified_by'],
                                m['status'],
                                m['pk_bill'],
			] for m in self.__idl
		]
		self._LCTRL_billitem.set_string_items(items = idl )
		self._LCTRL_billitem.set_data(data = self.__idl )
		self._LCTRL_billitem.set_column_widths()

        def repopulate_ui(self, *args):
                self.__populate_idl()
                return True




        
	def _validateBeforeInsert(self):
                has_error=False
                if self.charge_item.GetData() is None:
                        gmDispatcher.send(signal='statustext',
                                          msg=_('Cant insert new Billing Record - No Charge Item') )
                        has_error=True
                try:
                        float(self.faktor.GetValue() )
                except ValueError:
                        gmDispatcher.send(signal='statustext',
                                          msg=_('Cant insert new Billing Record - Invalid Qty float' ) )
                        has_error=True
                return not has_error

                #try:
                #        float(self.amount.GetValue() or 0 )
                #except ValueError:
                #        gmDispatcher.send(signal='statustext',
                #                          msg=_('Cant insert new Billing Record - Invalid Amount float' ) )
                #        has_error=True
                return not has_error

        _valid_for_save=_validateBeforeInsert
        _valid_for_save=_validateBeforeInsert
                        
	def _save_as_new(self):
                #from Gnumed.business import gmPerson
                
                pat = gmPerson.gmCurrentPatient()
                emr = pat.get_emr()
                
                new = gmBillItem.create_bill_rec(
                        emr.active_encounter['pk_encounter'],
                        self.charge_item.GetData(),
                        float(self.faktor.GetValue() ),
                        None, #gmTools.none_if(self.amount.GetValue().strip(), u'' ),
                        self.details.GetValue().strip() #gmTools.none_if()
                        
                        )
                
                #new.save()
                
                self.data = new
                
                return True
        def onBillRecInsert(self, event=None):
                #event.Skip()
                if  self._validateBeforeInsert():
                        self._save_as_new()
                        self.__populate_idl()
                        return True


        def _on_edit_billrec(self, *args):
                parent = wx.GetApp().GetTopWindow()
                result = edit_bill_rec( parent, self._ourBillRec )
                
                if result:
                    self.__populate_idl()
                return result
                
        def _on_delete_billrec(self, *args):
                #from Gnumed.business import gmBillItem
                from Gnumed.business import gmBillable
                
                doit = gmGuiHelpers.gm_show_question (
                        aTitle=_('Billing Record: confirm deletion'),
                        aMessage=_('Delete Record %u?\nItem: %s\nStatus: %s\n This can not be reversed.' % (
                                self._ourBillRec['pk'],
                                #self._ourBillRec['billable_description'],
                                gmBillable.cBillable( self._ourBillRec['fk_billable'] )['term'],
                                self._ourBillRec['status'],
                                )),
                        )
                if doit:
                        gmBillItem.remove_bill_rec( self._ourBillRec['pk'] )
                        self.__populate_idl()
                
        def __edit_encounter_details(self, evt):
                from Gnumed.business import gmEMRStructItems
                from Gnumed.wxpython import gmEMRStructWidgets
                enc = gmEMRStructItems.cEncounter(aPK_obj = self._ourBillRec['fk_encounter'])
                gmEMRStructWidgets.edit_encounter(parent = self, encounter = enc)

        def _on_show_inv(self, evt ):
                from Gnumed.business.gmBillFactory import pathToInvFile

                fn = pathToInvFile( self._ourBillRec['fk_bill'] ) #fn='/home/nl/lib/Gnumed/silo/%s.pdf' % self._ourBillRec['fk_bill']
                from Gnumed.pycommon.gmMimeLib import call_viewer_on_file
                call_viewer_on_file(fn)

        def onBillItemRightClick(self, evt):
                
		tmp = self._LCTRL_billitem.get_selected_item_data(only_one = True)
		if tmp is None:
			return
		
		self._ourBillRec= gmBillItem.cBillItem( tmp['pk_bill_item'] ) #can only handle one item  at a time
		
		# build menu
		menu = wx.Menu(title = _('Billrec Actions:'))

		ID = wx.NewId()
		menu.AppendItem(wx.MenuItem(menu, ID, _('Edit corresponding Encounter')))
		wx.EVT_MENU(menu, ID, self.__edit_encounter_details)


                if tmp['status'] == 'sent':
                        ## - show inv message
                        ID = wx.NewId()
                        menu.AppendItem(wx.MenuItem(menu, ID, _('Show Invoice')))
                        wx.EVT_MENU(menu, ID, self._on_show_inv)


		#if not invoiced or sent to clearing house..
		if tmp['status'] <> 'sent':

                        ## - delete message
                        ID = wx.NewId()
                        menu.AppendItem(wx.MenuItem(menu, ID, _('Delete')))
                        wx.EVT_MENU(menu, ID, self._on_delete_billrec)

                        ## - edit 
                        ID = wx.NewId()
                        menu.AppendItem(wx.MenuItem(menu,ID,_('Edit')))
                        wx.EVT_MENU(menu,ID, self._on_edit_billrec )

		# show menu
		self.PopupMenu(menu, wx.DefaultPosition)
		menu.Destroy()

		#self.__populate_idl() #encounter type might have been changed
                self._ourBillRec=None
		
	def onBillItemSelected(self, evt):
                pass



class cStatusPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):

		gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)

		query = u"""
			select min(pk) as pk, status as label
                        from bill.bill_rec
                        group by status

			"""

		mp = gmMatchProvider.cMatchProvider_SQL2(queries = query)
		mp.setThresholds(1, 2, 4)
		self.matcher = mp
		


class cEncounterPhraseWheel(gmPhraseWheel.cPhraseWheel):

	def __init__(self, *args, **kwargs):
                gmPhraseWheel.cPhraseWheel.__init__(self, *args, **kwargs)

		query = u"""
                        select
                                pk, 
                                started || ' '|| l10n_type || ' '|| reason_for_encounter as label,  pk_patient
                        from clin.v_pat_encounters
                                where pk_patient  >0
                        order by started
                        limit 20
                        """  

		mp = gmMatchProvider.cMatchProvider_SQL2(queries = query)
		mp.setThresholds(1, 2, 4)
		self.matcher = mp
		

        

	#----------------------------------------------------------------

from Gnumed.wxGladeWidgets import wxgBillRecordAreaPnl
from Gnumed.wxpython import gmEditArea

def edit_bill_rec(parent=None, rec=None):
        
	ea = cBillRecordAreaPnl(parent = parent, id = -1)
	ea.data = rec
	ea.mode = 'edit' #gmTools.coalesce(rec, 'new', 'edit')
	dlg = gmEditArea.cGenericEditAreaDlg2(parent = parent, id = -1, edit_area = ea)
        dlg._BTN_forward.Disable()
	dlg.SetTitle(
                _('Edit Bill Rec')
                #gmTools.coalesce(encounter_type, _('Adding new encounter type'), _('Editing local encounter type name'))
                )
	if dlg.ShowModal() == wx.ID_OK:
		return True
	return False

class cBillRecordAreaPnl(wxgBillRecordAreaPnl.wxgBillRecordAreaPnl, gmEditArea.cGenericEditAreaMixin):
	def __init__(self, *args, **kwargs):
                #try:
                #    data = kwargs['record']
                #    del kwargs['record']
                #except KeyError:
                #    data=None

		wxgBillRecordAreaPnl.wxgBillRecordAreaPnl.__init__(self, *args, **kwargs)
		gmEditArea.cGenericEditAreaMixin.__init__(self)

                #self.mode='new'
                #self.data=data
                #if self.data is not None:
                #    self.mode='edit'

                self.__init_ui()
                #self.__register_interests()
	#-------------------------------------------------------
	# generic edit area API
	#-------------------------------------------------------
	def __init_ui(self ):
                pat = gmPerson.gmCurrentPatient()
                self._enc = gmBillItem.get_enc_combo_for(pat.ID )

                self.encounter.Clear()
                for x in self._enc:
                    self.encounter.Append( x['display_text'])

        

	def _valid_for_save(self):
                no_errors=True

                try:
                        int(self.count.GetValue() )
                except ValueError:
                        no_errors=False

                try:
                        #int( self.encounter.GetValue() )
                        #int( self.encounter.GetValue().split()[0] )
                        int(1)
                        #@@dont allow move to another patient
                except ValueError:
                        no_errors=False
                try:
                        gmDateTime.wxDate2py_dt( self.charge_date.GetValue() )
                except:
                        no_errors=False
                
                try:
                        float( self.factor.GetValue() )
                        
                except ValueError:
                        no_errors=False

                try:
                        float(self.amount.GetValue() )
                except ValueError:
                        no_errors=False

                
                if self.status.GetValue() == 'sent':
                        gmDispatcher.send(signal='statustext', msg='Only Invoice Close can assign status sent'  )
                        no_errors = False
                
		return no_errors
	def _save_as_update(self):
                rec = self.data

                #rec['fk_encounter']=int( self.encounter.GetValue() )
                rec['fk_encounter'] = int( self.encounter.GetValue().split()[0] )
                rec['date_to_bill'] = gmDateTime.wxDate2py_dt( self.charge_date.GetValue() )
                rec['unit_count'] = int( self.count.GetValue() )
                rec['amount_multiplier'] = float( self.factor.GetValue() )
                rec['net_amount_per_unit'] = float(self.amount.GetValue() )
                rec['description'] = self.details.GetValue().strip()
                rec['status'] = self.status.GetValue().strip()
                
                success,data= rec.save_payload()
                if not success:
                    gmGuiHelpers.gm_show_error (
                    aMessage = _('Did *NOT* save your changes. Mostly due to someone has changed this Record meanwhile. Please close this Dialog and try it again.'),
                    aTitle = _('Problem wigh updating')
                    )
                    return False

                
                #self.data.save() #is this necessary?
                
		
		return True
	def _refresh_from_existing(self):
                enc = self.data['fk_encounter']
                idx = [x['pk_encounter'] for x in self._enc].index(enc)
                self.encounter.SetValue( self._enc[idx]['display_text'] ) #u'%u' % self.data['fk_encounter'] )

                dt = self.data['date_to_bill']
                wxdt = gmDateTime.py_dt2wxDate(dt,wx)
                self.charge_date.SetValue( wxdt )

                from Gnumed.business import gmBillable
                xdesc = gmBillable.cBillable( self.data['fk_billable'] )['term']
                self.ci_descrip.SetLabel( u'%s' % xdesc )

                self.count.SetValue( str( self.data['unit_count'])  )
                self.factor.SetValue( u'%.2f' %  self.data['amount_multiplier'] )
                self.amount.SetValue( u'%.2f' %  self.data['net_amount_per_unit'] )
                self.details.SetValue( self.data['description'] or u'' )

                
                #those = self.status.GetItems()
                #val = self.data['status']
                #idx_status=0
                #try:
                #        idx_status = those.index( val )
                #except ValueError: #item not in list
                #        #self.status.Append( u'%s' % val )
                #        gmDispatcher.send(signal='statustext', msg='Status %s not supported ' % val )
                #
                # 
                #self.status.SetSelection( idx_status )

                #st = self.data['status']
                #if st not in u'sent unknown cancelled pending stalled'.split():
                #        gmDispatcher.send(signal='statustext', msg='Please check Status %s ' % st )
                self.status.SetValue( self.data['status'] )
                if self.data['status'] == 'sent':
                    self.status.Disable()
                else:
                    self.status.Enable()

                return True
        def _refresh_as_new(self ):
            return True

                
		
                
        #def __register_interests(self):
        #       return




        
if __name__ == '__main__':
    pass

