/*
 * ActionUtil.java
 *
 * Created on September 24, 2004, 5:56 PM
 */

package org.gnumed.testweb1.actions;

import javax.servlet.http.HttpServletRequest;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.struts.action.ActionMapping;

/**
 * 
 * @author sjtan
 * common servlet functions.
 */
public class ActionUtil {
	Log log = LogFactory.getLog(ActionUtil.class);

	/** Creates a new instance of ActionUtil */
	public ActionUtil() {
	}
	
	
	/** mapping.attribute is the key to store the form, either on
	 * as a request or a session attribute. mapping.scope has "session"
	 * or "request" to specify which.
	 * 
	 * @param request
	 * @param mapping
	 * @param form
	 */
	public void setAttributeOnScopeFromMappingAttributeAndScope(HttpServletRequest request,
			ActionMapping mapping, Object form) {
		if ("session".equals(mapping.getScope())) {
			request.getSession().setAttribute(mapping.getAttribute(), form);
			log.info("SESSION FORM ATTRIBUTE KEY" + mapping.getAttribute());
		} else {
			request.setAttribute(mapping.getAttribute(), form);
			log.info("REQUEST FORM ATTRIBUTE KEY" + mapping.getAttribute());

		}
	}

}