/*
 * FindIdentityAction.java
 *
 * Created on June 25, 2004, 3:46 AM
 */

package org.gnumed.testweb1.actions;

import java.lang.reflect.InvocationTargetException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Enumeration;

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
import org.gnumed.testweb1.data.DataObjectFactory;
import org.gnumed.testweb1.data.DemographicDetail;
import org.gnumed.testweb1.global.Constants;
import org.gnumed.testweb1.persist.DataSourceException;
import org.gnumed.testweb1.persist.DemographicDataAccess;
/**
 *
 * @author  sjtan
 */
public class FindIdentityAction extends Action  {
    
    /** Creates a new instance of FindIdentityAction */
    public FindIdentityAction() {
    }
    
    Log log = LogFactory.getLog(LoginAction.class);
    
    public ActionForward execute(ActionMapping mapping,
    ActionForm form,
    HttpServletRequest request,
    HttpServletResponse response) {
        
        ActionMessages errors = new ActionMessages();
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
           
            errors.add( getClass().toString(), new ActionMessage("errors.writing.response", e) );
            
        } catch (IllegalAccessException e) {
            log.error(e + e.getLocalizedMessage());
            errors.add(getClass().toString(), new ActionMessage("errors.copy.object" , form, detail) );
            
        } catch (InvocationTargetException te) {
            log.error(te + te.getLocalizedMessage());
            errors.add(getClass().toString() , new ActionMessage("errors.copy.object" , form, detail) );
            
        } catch (DataSourceException e) {
            log.error("error during setting DEMOGRAPHIC_DETAILS" , e);
            
            errors.add(getClass().toString(), new ActionMessage("errors.find.demographics", e.getCause()));
            
        }
        
        if (errors.size() > 0) {
            saveErrors(request, errors);
            return mapping.getInputForward();
        }
        
        return mapping.findForward("success");
        
        
        
        
        
    }
}
