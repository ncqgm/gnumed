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
 * @author  sjtan
 */
public class ActionUtil {
    Log log = LogFactory.getLog( ActionUtil.class);
    /** Creates a new instance of ActionUtil */
    public ActionUtil() {
    }
    
    
    public   void setScopedMappingAttribute(HttpServletRequest request, ActionMapping mapping,   Object form) {
        if ( "session".equals(mapping.getScope() )) {
            request.getSession().setAttribute(mapping.getAttribute(), form);
            log.info("SESSION FORM ATTRIBUTE KEY"+ mapping.getAttribute());
        } else {
            request.setAttribute(mapping.getAttribute(), form);
            log.info("REQUEST FORM ATTRIBUTE KEY"+ mapping.getAttribute());
            
        }
    }
    
   
}
