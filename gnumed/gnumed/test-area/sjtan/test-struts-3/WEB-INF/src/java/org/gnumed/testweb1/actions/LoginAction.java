/*
 * LoginAction.java
 *
 * Created on June 18, 2004, 4:23 AM
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
import org.gnumed.testweb1.global.Constants;
import org.gnumed.testweb1.business.LoginModule;
import org.gnumed.testweb1.exceptions.login.*;
import java.lang.reflect.InvocationTargetException;
/**
 *
 * @author  sjtan
 */
public class LoginAction extends Action {
    
    /** Creates a new instance of LoginAction */
    public LoginAction() {
    }
    
    Log log = LogFactory.getFactory().getLog(LoginAction.class);
    
    public ActionForward execute(ActionMapping mapping,
    ActionForm form,
    HttpServletRequest request,
    HttpServletResponse response) {
        byte[] password = null;
        ActionErrors errors = new ActionErrors();
        
        try {
            String username = (String) PropertyUtils.getSimpleProperty( form, "username");
            password =  ( (String)PropertyUtils.getSimpleProperty( form, "password")).getBytes();
            LoginModule module = (LoginModule) servlet.getServletContext().getAttribute(Constants.LOGIN_MODULE);
            //  LoginModule module = new org.gnumed.testweb1.mock.MockLoginModule();
            
            log.info("Module is " + module );
            module.validate(username, password );   
            
            // Remove the obsolete form bean
            if (mapping.getAttribute() != null) {
                if ("request".equals(mapping.getScope()))
                    request.removeAttribute(mapping.getAttribute());
                else
                    request.getSession().removeAttribute(mapping.getAttribute());
            }
            
            
            return mapping.findForward("success");
        
        }  catch (InvalidUserNameException iue) {
            log.error(iue);
            errors.add(errors.GLOBAL_MESSAGE, new /*Should be ActionMessage for Struts 1.2*/ActionError("errors.invalid.user"));
        } catch (InvalidPasswordException ipe) {
            log.error(ipe);
            errors.add( errors.GLOBAL_MESSAGE, new ActionError("errors.invalid.password"));
        } catch (IllegalAccessException iae) {
            log.error(iae);
            errors.add(errors.GLOBAL_MESSAGE, new ActionError("errors.app", iae));
        } catch(InvocationTargetException ite ) {
            log.error(ite);
            errors.add(errors.GLOBAL_MESSAGE, new ActionMessage("errors.app", ite));
        } catch ( NoSuchMethodException nsme) {
            log.error(nsme);
            errors.add(errors.GLOBAL_MESSAGE, new ActionError("errors.app", nsme));
        } catch (NullPointerException npe) {
            npe.printStackTrace();
            log.error(npe);
        }
        
        
        finally {
            java.util.Arrays.fill(password, (byte) 0);
            
            
            
        }
        
        saveErrors(request, errors);
        return  mapping.getInputForward();
    }
    
}
