#====================================================================
# GnuMed
# GPL
#====================================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/client/wxpython/Attic/gmEditAreaMixin.py,v $
# $Id: gmEditAreaMixin.py,v 1.3 2006-05-15 13:36:00 ncq Exp $
__version__ = "$Revision: 1.3 $"
__author__ = "I. Haywood"

#======================================================================

import sys, traceback, time, types

try:
        import wxversion
        import wx
        import wx.stc
except ImportError:
        from wxPython import wx

from Gnumed.pycommon import gmLog, gmGuiBroker, gmMatchProvider, gmDispatcher, gmSignals, gmExceptions, gmI18N, gmBusinessDBObject
from Gnumed.pycommon.gmPG import unwrap_error as ue
from Gnumed.wxpython import gmDateTimeInput, gmPhraseWheel, gmGuiHelpers
from Gnumed.business import gmForms

_log = gmLog.gmDefLog


class cEditAreaMixin:
    """
    A mixin class for use with wxGlade-generated popups.
    The wxGlade class should be a wxFrame or wxDialog descendant

    methods OnSave, OnCancel, OnClose and OnPrint are provided for
    connection to (presumably) EVT_BUTTON events.

    If you want to print, the __init__ function must set self.template
    to a gmForms.cFormEngine descendant, or there is a wx.ControlWithItems
    descendant with the internal name "form" and __init__ calls
    cEditAreaMixin.ConfigurePrinting

    Example

    class cReferralPopup (gmEditAreaMixin.cEditAreaMixin, gmglReferralPopup): # put the mixin first so it overrides the wxGlade-generated event handlers

        def __init__ (self, *args, **kwargs):
            gmEditAreaMixin.cEditAreaMixin (gmglReferralPopup, *args, *kwargs)
            self.ConfigurePrinting ('referral')

        # then override the methods to talk to the business layer

        def SaveNewBusiness (self, dtd):
            return gmReferral.new_referral (dtd['content'], ....)
    """

    def __init__ (self, sibling, *args, **kwargs):
        """
        sibling is the wxGlade generated sibling class, which we initalise
        """
        if kwargs.has_key ('data'):
            if isinstance (kwargs['data'], gmBusinessDBObject.cBusinessDBObject):
                self.biz = kwargs['data']
                dtd = None
            elif type (kwargs['data']) is types.DictionaryType:
                self.biz = None
                dtd = kwargs['data']
            else:
                raise ConstructorError, "data must be dict or business object"
            del kwargs['data']
        if kwargs.has_key ('episode'):
            self.episode = kwargs['episode']
            del kwargs['episode']
        else:
            if self.dtd and self.dtd.has_key ('episode'):
                self.episode = self.dtd['episode']
            else:
                self.episode = None
        self.form_instance = None
        sibling.__init__ (self, *args, **kwargs)
        if self.biz:
            self.LoadBusiness (self.biz)
        elif dtd:
            self._load_dtd (dtd)
        if isinstance (self, wx.Panel):
            gmDispatcher.connect(signal=gmSignals.post_patient_selection(), receiver=self.OnClear)
            gmDispatcher.connect(signal=gmSignals.pre_patient_selection(), receiver=self.OnSave)
        else:
            wx.Bind (wx.EVT_CLOSE, self.OnClose, self)
            gmDispatcher.connect(signal=gmSignals.pre_patient_selection(), receiver=self.OnPanic)
        self.old_dtd = dtd
        self.template = None
            
    def _load_dtd (self, dtd):
        for w, v in dtd.items ():
            if hasattr(self, w):
                widget = getattr (self, w)
                if isinstance (widget, gmPhraseWheel.cPhraseWheel):
                    widget.SetValue (*v)
                elif isinstance (widget, (wx.RadioBox, wx.ControlWithItems)):
                    widget.SetSelection (v)
                elif isinstance (widget, wx.stc.StyledTextCtrl):
                    widget.SetText (v)
                else:
                    widget.SetValue (v)
            if w == 'form_instance':
                self.form_instance = v

    def _get_dtd (self):
        d = {}
        for n, w in self.__dict__.items ():
            if isinstance (w, gmPhraseWheel.cPhraseWheel):
                d[n] = (w.GetValue (), w.GetData ())
            elif isinstance (w, (wx.RadioBox, wx.ControlWithItems)):
                d[n] = w.GetSelection ()
            elif isinstance (w, wx.stc.StyledTextCtrl):
                d[n] = w.GetText ()
            elif isinstance (w, (wx.TextCtrl, wx.CheckBox, wx.SpinCtrl, wx.Gauge, wx.ToggleButton, wx.Slider)):
                d[n] = w.GetValue ()
        if self.form_instance:
            d['form_instance'] = self.form_instance
        return d
                             

        
    def ValidateDTD (self, dtd):
        """
        accepts a DTD (dictionary of widget values) for validation
        returns (True, summary) or (False, error_msg)
        The summary is a one-line text describing the contents of the edit area
        """
        return (True,self.__class__.__name__)
  
    def LoadBusiness (self, biz):
        """
        Given a business object, loads its values into the widget
        """
        pass
  
    def Save2Business (self, biz, dtd):
        """
        Given a DTD of changed values, loads them into the pre-existing business object
        Returns (True, biz) or (False, error_msg) or the value of save_payload ()
        Can call SaveNewBusiness if that makes sense (i.e. backend rows that never get updated)
        not a class method
        """
        return self.SaveNewBusiness (dtd)

    def SaveNewBusiness (klass, dtd):
        """
        Creates a new business object from a dictionary of widget data
        Must be a class method
        Returns (True, biz_object) or (False, error_message)
        """
        pass
    SaveNewBusiness = classmethod (SaveNewBusiness)


    def OnClear (self, event=None):
        for w in self.__dict__.items ():
            if isinstance (w, (wx.TextCtrl, wx.stc.StyledTextCtrl,gmPhraseWheel.cPhraseWheel)):
                w.Clear ()
            elif isinstance (w, (wx.CheckBox, wx.ToggleButton, wx.SpinCtrl, wx.Gauge)):
                w.SetValue (0)
            elif isinstance (w, (wx.ControlWithItems, wx.RadioBox)):
                w.SetSelection (0)
                
    def OnSave (self, event=None):
        """
        explicitly save content, do not close the dialog
        """
        dtd = self._get_dtd ()
        dtd['episode'] = self.episode
        if self.old_dtd == dtd:
            return
        v = self.ValidateDTD (dtd)
        if not v[0]:
            wx.MessageBox (v[1], _("Input not valid"), wx.OK | wx.ICON_ERROR)
            return
        if self.biz:
            v = self.Save2Business (self.biz, dtd)
        else:
            v = self.SaveNewBusiness (dtd)
        if v[0]:
            if v[1]:
		self.biz = v[1]
            return
        else:
            wx.MessageBox (ue (v[1]), _("Error while saving"), wx.OK | wx.ICON_ERROR)
            # it is assumed the business layer explains itself in the log
            self.biz = None

    def OnClose (self, event=None):
        """
        close the dialog
        if a business object exists, save (no pint delaying)
        if not, send a dictionary to the notes widget, for saving later
        """
        dtd = self._get_dtd ()
        dtd['episode'] = self.episode
        v = self.ValidateDTD (dtd)
        if not v[0]:
            wx.MessageBox (v[1], _("Input not valid"), wx.OK | wx.ICON_ERROR)
            if event and event.CanVeto ():
                event.Veto ()
            else:
                gmDispatcher.disconnect (self.OnPatientChanging)
                self.Destroy ()
            return
        summary = v[1]
        if self.biz:
	    s = self.Save2Business (self.biz, dtd)
            if not s[0]:
	        wx.MessageBox (ue (s[1]), _("Error saving data"), wx.OK | wx.ICON_ERROR)
                if event and event.CanVeto ():
                    event.Veto ()
                else:
                    gmDispatcher.disconnect (self.OnPatientChanging)
                    self.Destroy ()
		return
	    else:
	        if s[1]:
		   self.biz = s[1]
	        data = self.biz
        else:
            data = dtd
            if not dtd.has_key ('episode'):
                dtd['episode'] = self.episode
        gmDispatcher.send (signal=gmSignals.popup_data (), widget=self.__class__, data=data, summary=summary)
        gmDispatcher.disconnect (self.OnPatientChanging)
        self.Destroy ()

    def OnCancel (self, event=None):
        """
        close, explicitly *don't* save
        """
        gmDispatcher.disconnect (self.OnPatientChanging)
        self.Destroy ()
        
    def OnPatientChanging (self, event=None):
        """
        The user is changing the patient while we are still alive
        """
        # for now, just die quietly
        # FIXME: how to we cancel a patient change, should the user wish to do that?
        self.Destroy ()

    def ConfigurePrinting (self, form_type):
        """
        Descendants which wish to print may call this function
        A wx.ControlWithItems called "form" should exist on the widget,
        which is loaded with a list of forms of the given type.

        Alternatively descendants can just set self.template directly
        """
        for n, i in gmForms.get_forms_by_type (form_type):
            self.form.Append (n, i)

        
    def OnPrint (self, event=None):
        self.OnSave ()
        if self.biz:
            if self.template:
                # this widget is hardwired to use a given template
                template = self.template.clone ()
            else:
                # user is selecting a template
                sel = self.form.GetSelection ()
                if sel == wx.NOT_FOUND:
                    wx.MessageBox (_("You need to select a form for printing"), _("Printing"), wx.ICON_ERROR | wx.OK)
                    return
                template = self.form.GetClientData (sel)
            template.accept (self.biz)
            # here's where in the future we would send to the print queue
            try:
                template.process ()
                # I don't like to waste paper while testing
                # template.printout ()
                template.xdvi ()
                template.cleanup ()
                template.store ()
            except gmForms.FormError, e:
                wx.MessageBox (str (e), _("Error with print Form"), wx.ICON_ERROR | wx.OK)
        # else: presumably saving failed, so do nothing
            
# DO NOT ADD DESCENDANT CLASS DEFINTIONS TO THIS FILE
