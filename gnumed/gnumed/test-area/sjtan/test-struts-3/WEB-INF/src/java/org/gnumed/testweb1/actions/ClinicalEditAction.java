/*
 * ClinicalEditAction.java
 *
 * Created on July 5, 2004, 11:58 PM
 */

package org.gnumed.testweb1.actions;

import java.util.List;

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
import org.gnumed.testweb1.data.HealthRecord01;

/**
 * 
 * @author sjtan
 * this action sets the form , demographic, and health record objects
 */
public class ClinicalEditAction extends Action {
	ClinicalActionUtil clinicalActionUtil = ClinicalActionUtil.instance();

	/** Creates a new instance of ClinicalEditAction */
	public ClinicalEditAction() {
	}

	Log log = LogFactory.getLog(this.getClass());

/**
 *  
 *  action to set attributes for form, and medical record prior to clinical encounter
 * entry use case. The form is for new encounter information, and the medical record
 * is for displaying the current medical record for viewing whilst entering the
 * encounter. Other attribute includes demographic details and vaccination choices.
 * Medication choices are handled in a separate window , and selections are 
 * transferred as strings onto form fields, rather than medication objects.
 */
	public ActionForward execute(ActionMapping mapping, ActionForm form,
			HttpServletRequest request, HttpServletResponse response) {

		try {
			clinicalActionUtil.setRequestAttributes(servlet, request, form,
					mapping);
		} catch (Exception e) {
			e.printStackTrace();
			clinicalActionUtil
					.setAttributeOnScopeFromMappingAttributeAndScope(request, mapping, form);
			log.info(e);
			ActionMessages messages = new ActionMessages();
			messages.add("error in constructing attributes for form",
					new ActionMessage("error is", e));
			saveMessages(request, messages);
			return mapping.getInputForward();
		}

		return mapping.findForward("successLoadClinical");
	}

	private void logHealthIssues(HealthRecord01 healthRecord) {
		List l = healthRecord.getHealthSummary().getHealthIssues();
		log.info("got health issues " + l + " size = "
				+ ((l == null) ? "null" : Integer.toString(l.size())));

	}
}