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
import org.gnumed.testweb1.persist.scripted.gnumed.DrugRefAccess;

/**
 * @author sjtan
 * loads a list of candidate drugs, given drug name prefix from 
 *  request parameter ( parameters are passed as url parameters in 
 * a hyperlink from the clinical encounter form)
 *  .
 */
public class SearchDrugAction extends Action {

	Log log = LogFactory.getLog(this.getClass());

	public ActionForward execute(ActionMapping mapping, ActionForm form,
			HttpServletRequest request, HttpServletResponse response) {

		ActionMessages messages = new ActionMessages();
		DataObjectFactory factory;
		try {
			log
					.info("Got parameters "
							+ request
									.getParameter(Constants.Request.MEDICATION_ENTRY_INDEX)
							+ " , "
							+ request
									.getParameter(Constants.Request.DRUG_NAME_PREFIX));
			if (form instanceof ClinicalUpdateForm) {
				request.getSession().setAttribute(
						Constants.Session.CURRENT_CLINICAL_FORM, form);
			} else {
				log.info("No form found from action method parameter");
				if (request.getSession().getAttribute(mapping.getAttribute()) != null)
					log.info("BUT FOUND A form on session as attribute "
							+ mapping.getAttribute());
				log.info(" : form was "
						+ request.getSession().getAttribute(
								mapping.getAttribute()));
			}
			request
					.getSession()
					.setAttribute(
							Constants.Session.TARGET_MEDICATION_ENTRY_INDEX,
							request
									.getParameter(Constants.Request.MEDICATION_ENTRY_INDEX));

			DrugRefAccess access = (DrugRefAccess) servlet.getServletContext()
					.getAttribute(Constants.Servlet.DRUGREF_ACCESS);

			DrugRef[] candidates = access.findDrugRef((String) request
					.getParameter(Constants.Request.DRUG_NAME_PREFIX));

			request.getSession().setAttribute(
					Constants.Session.DRUG_REF_CANDIDATES, candidates);

			//                if (form == null) {
			//                    form = (ClinicalUpdateForm)
			// request.getSession().getAttribute(Constants.Session.CURRENT_CLINICAL_FORM);
			//                }
			//                ClinicalUpdateForm cform = (ClinicalUpdateForm) form;
			//                int medIndex =
			// Integer.parseInt(request.getParameter(Constants.Request.MEDICATION_ENTRY_INDEX).toString());
			//                cform.getEncounter().getMedication(medIndex).setDB_origin(Constants.Schema.DRUGREF_NAME);
			//
			//
		} catch (Exception e) {

			log.error(e, e);
		}

		log.info("GOING TO FORWARD showCandidateDrugs");
		return mapping.findForward("showCandidateDrugs");
	}
}