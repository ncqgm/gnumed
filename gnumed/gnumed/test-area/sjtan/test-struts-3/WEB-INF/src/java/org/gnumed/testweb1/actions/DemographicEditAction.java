/*
 * DemographicEditAction.java
 *
 * Created on June 28, 2004, 3:23 AM
 */

package org.gnumed.testweb1.actions;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.commons.beanutils.BeanUtils;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.struts.action.Action;

import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;
import org.apache.struts.action.ActionMessage;
import org.apache.struts.action.ActionMessages;
import org.apache.struts.config.FormBeanConfig;
import org.gnumed.testweb1.data.DemographicDetail;
import org.gnumed.testweb1.global.Constants;
import org.gnumed.testweb1.persist.DemographicDataAccess;

/**
 * 
 * @author sjtan
 */
public class DemographicEditAction extends Action {
	ActionUtil util = new ActionUtil();

	/** Creates a new instance of DemographicEditAction */
	public DemographicEditAction() {
	}

	Log log = LogFactory.getLog(this.getClass());

	public ActionForward execute(ActionMapping mapping, ActionForm form,
			HttpServletRequest request, HttpServletResponse response) {

		try {
			if (form == null) {

				//        deprecated in Struts 1.2
				//            ActionFormBeans beans = (ActionFormBeans)
				// servlet.getServletContext()
				//          .getAttribute("org.apache.struts.action.FORM_BEANS") ;
				//        ActionFormBean bean = beans.findFormBean("demographicForm");
				//          DynaActionFormClass dynaClass =
				//          DynaActionFormClass.createDynaActionFormClass(bean);

				FormBeanConfig config = mapping.getModuleConfig()
						.findFormBeanConfig("demographicForm");

				form = (ActionForm) config.getDynaActionFormClass()
						.newInstance();

			}
			log.info("FORM is " + form);

			DemographicDataAccess dataAccess = (DemographicDataAccess) servlet
					.getServletContext().getAttribute(
							Constants.Servlet.DEMOGRAPHIC_ACCESS);

			Long id = null;

			if (request.getParameter(Constants.Request.PATIENT_ID) != null)

				id = new Long(Long.parseLong(request
						.getParameter(Constants.Request.PATIENT_ID)));

			if (id != null && id.longValue() != (long) 0) {

				DemographicDetail detail = dataAccess
						.findDemographicDetailById(id);

				BeanUtils.copyProperties(form, detail);

				log.info("FORM ID IS "
						+ BeanUtils.getSimpleProperty(form, "id"));

			}

			util.setAttributeOnScopeFromMappingAttributeAndScope(request, mapping, form);

			//            if ("session".equals(mapping.getScope())) {
			//                request.getSession().setAttribute(mapping.getAttribute(), form);
			//
			//            } else {
			//                request.setAttribute(mapping.getAttribute(), form);
			//            }
			//
		} catch (Exception e) {
			util.setAttributeOnScopeFromMappingAttributeAndScope(request, mapping, form);
			log.info(e);
			ActionMessages messages = new ActionMessages();
			messages.add("error in constructing attributes for form",
					new ActionMessage("error is", e));
			saveMessages(request, messages);
			return mapping.getInputForward();
		}

		return mapping.findForward("successLoadForEdit");
	}
}

