/*
 * Created on 13-Oct-2004
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
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
import org.apache.struts.action.ActionMessages;
import org.gnumed.testweb1.data.DataObjectFactory;
import org.gnumed.testweb1.data.DrugRef;
import org.gnumed.testweb1.forms.ClinicalUpdateForm;
import org.gnumed.testweb1.global.Constants;
import org.gnumed.testweb1.persist.scripted.gnumed1.DrugRefAccess;

/**
 * @author sjtan
 *
 * TODO To change the template for this generated type comment go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
public class SearchDrugAction extends Action {

	Log log = LogFactory.getLog(this.getClass());

	public ActionForward execute(ActionMapping mapping, ActionForm form,
			HttpServletRequest request, HttpServletResponse response) {
                
		ActionMessages messages = new ActionMessages();
		DataObjectFactory factory;
                try {
                log.info("Got parameters " + request.getParameter(Constants.Request.MEDICATION_ENTRY_INDEX) + " , "+
                    request.getParameter(Constants.Request.DRUG_NAME_PREFIX));
		if (form instanceof ClinicalUpdateForm) {
                    request.getSession().setAttribute( Constants.Session.CURRENT_CLINICAL_FORM, form);
                } else {
                    log.info("No form found from action method parameter");
                    if (request.getSession().getAttribute( mapping.getAttribute()) != null)
                        log.info("BUT FOUND A form on session as attribute "+ mapping.getAttribute() );
			log.info(" : form was " + request.getSession().getAttribute( mapping.getAttribute()) );
                }
    		request.getSession().setAttribute(Constants.Session.TARGET_MEDICATION_ENTRY_INDEX, 
							request.getParameter(Constants.Request.MEDICATION_ENTRY_INDEX));
    	
		
		DrugRefAccess access  = 
				(DrugRefAccess) servlet.getServletContext().
						getAttribute(Constants.Servlet.DRUGREF_ACCESS);
		
					request.getSession().setAttribute(Constants.Session.DRUG_REF_CANDIDATES, access.findDrugRef((String)request.getParameter(Constants.Request.DRUG_NAME_PREFIX)));
					
		} catch (Exception e) {
			
                        log.error(e,e);
		}
                
                log.info("GOING TO FORWARD showCandidateDrugs");
		return mapping.findForward("showCandidateDrugs");
	}
}
