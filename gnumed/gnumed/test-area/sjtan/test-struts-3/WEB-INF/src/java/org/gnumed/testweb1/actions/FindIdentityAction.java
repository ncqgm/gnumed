/*
 * FindIdentityAction.java
 *
 * Created on June 25, 2004, 3:46 AM
 */

package org.gnumed.testweb1.actions;

import org.apache.struts.action.Action;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;
import javax.servlet.http.HttpServletResponse;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.struts.action.Action;
import org.apache.struts.action.ActionError;
import org.apache.struts.action.ActionErrors;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;
import org.apache.struts.util.ModuleException;
import org.apache.struts.util.MessageResources;
import org.apache.commons.beanutils.PropertyUtils;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;
import javax.servlet.http.HttpServletResponse;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.struts.action.Action;
import org.apache.struts.action.ActionError;
import org.apache.struts.action.ActionErrors;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;
import org.apache.struts.action.ActionMessages;
import org.apache.struts.action.ActionMessage;
import org.apache.struts.util.ModuleException;
import org.apache.struts.util.MessageResources;
import org.apache.commons.beanutils.PropertyUtils;
import org.apache.commons.beanutils.BeanUtils;

import org.gnumed.testweb1.global.Constants;
import org.gnumed.testweb1.business.LoginModule;
import org.gnumed.testweb1.exceptions.demographic.*;
import java.lang.reflect.InvocationTargetException;
import java.util.Map;
import java.util.Iterator;
import java.util.Enumeration;
import java.util.Collections;
import java.util.Arrays; import java.util.Collection; import java.util.ArrayList;

import org.gnumed.testweb1.data.DataObjectFactory;
import org.gnumed.testweb1.data.DemographicDetail;

import org.gnumed.testweb1.persist.DemographicDataAccess;
import org.gnumed.testweb1.persist.DataSourceException;
/**
 *
 * @author  sjtan
 */
public class FindIdentityAction extends Action  {
    
    /** Creates a new instance of FindIdentityAction */
    public FindIdentityAction() {
    }
    
    Log log = LogFactory.getFactory().getLog(LoginAction.class);
    
    public ActionForward execute(ActionMapping mapping,
    ActionForm form,
    HttpServletRequest request,
    HttpServletResponse response) {
        
        ActionErrors errors = new ActionErrors();
        Enumeration en = servlet.getServletContext().getAttributeNames();
        while(en.hasMoreElements()) {
            log.info("Servlet context has attribute named " + en.nextElement());
        }
        DataObjectFactory factory = (DataObjectFactory) 
        servlet.getServletContext().
        getAttribute(Constants.Servlet.OBJECT_FACTORY);
        
        DemographicDetail detail = factory.createDemographicDetail();
        
        try {
            BeanUtils.copyProperties(detail, form);
            
            
            DemographicDataAccess access =
            (DemographicDataAccess) servlet.getServletContext().
            getAttribute(Constants.Servlet.DEMOGRAPHIC_ACCESS);
            
            DemographicDetail[] details = access.findDemographicDetail(detail);
            
            java.util.List  list = new ArrayList( Arrays.asList(details));
            
            request.getSession().setAttribute(
                Constants.Session.DEMOGRAPHIC_DETAILS,
                list );
            
            log.info("GOT TO END OF " + this);
            java.io.PrintWriter w = response.getWriter();
            w.println("<body>Got to end of FindIdentity</body>");
            
        } catch( java.io.IOException e) {
            log.error(e);
            errors.add(errors.GLOBAL_MESSAGE, new ActionMessage("errors.writing.response", e) );
            
        } catch (IllegalAccessException e) {
            log.error(e + e.getLocalizedMessage());
            errors.add(errors.GLOBAL_MESSAGE, new ActionError("errors.copy.object" , form, detail) );
            
        } catch (InvocationTargetException te) {
            log.error(te + te.getLocalizedMessage());
            errors.add(errors.GLOBAL_MESSAGE, new ActionError("errors.copy.object" , form, detail) );
            
        } catch (DataSourceException e) {
            log.error("error during setting DEMOGRAPHIC_DETAILS" , e);
            
            errors.add(errors.GLOBAL_MESSAGE, new ActionError("errors.find.demographics", e.getCause()));
            
        }
        
        if (errors.size() > 0) {
            saveErrors(request, errors);
            return mapping.getInputForward();
        }
        
        return mapping.findForward("success");
        
        
        
        
        
    }
}
