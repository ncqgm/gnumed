/*
 * ClinicalSaveAndExit.java
 *
 * Created on 11 February 2005, 09:12
 */

package org.gnumed.testweb1.actions;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.struts.action.Action;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;
import org.apache.struts.action.ActionMessage;
import org.apache.struts.action.ActionMessages;
import org.gnumed.testweb1.data.ClinNarrative;
/**
 *
 * @author sjtan
 */
public class ClinicalSaveAndExit extends ClinicalSaveAction {
    
    /** Creates a new instance of ClinicalSaveAndExit */
    public ClinicalSaveAndExit() {
    }
    
    public ActionForward execute(ActionMapping mapping, ActionForm form,
			HttpServletRequest request, HttpServletResponse response) {
        ActionForward fwd = super.execute(mapping,form, request, response);
        if ( fwd.getName().equals("successClinicalEditAgain")) 
            return mapping.findForward("success");
        
        return fwd;
    }

}
