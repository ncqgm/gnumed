/*
 * DemographicEditAction.java
 *
 * Created on June 28, 2004, 3:23 AM
 */

package org.gnumed.testweb1.actions;

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

import org.gnumed.testweb1.adapters.DataObjectFactoryPlugIn;
import org.gnumed.testweb1.data.DataObjectFactory;
import org.gnumed.testweb1.data.DemographicDetail;
import org.gnumed.testweb1.persist.DemographicDataAccess;

import org.gnumed.testweb1.global.Util;
import org.gnumed.testweb1.global.Constants;
import org.apache.struts.validator.DynaValidatorForm;
import org.apache.struts.config.FormPropertyConfig;

import org.apache.struts.action.ActionFormBeans;
import org.apache.struts.action.ActionFormBean;
import org.apache.struts.action.DynaActionFormClass;
/**
 *
 * @author  sjtan
 */
public class DemographicEditAction extends Action {
    
    /** Creates a new instance of DemographicEditAction */
    public DemographicEditAction() {
    }
    Log log = LogFactory.getFactory().getLog(this.getClass());
    
    public ActionForward execute(ActionMapping mapping,
    ActionForm form,
    HttpServletRequest request,
    HttpServletResponse response) {
        
        ActionErrors errors = new ActionErrors();
        
        try {
            if (form == null) {
                
                ActionFormBeans beans  = (ActionFormBeans) servlet.getServletContext()
                .getAttribute("org.apache.struts.action.FORM_BEANS") ;
                ActionFormBean bean = beans.findFormBean("demographicForm");
                DynaActionFormClass dynaClass =
                DynaActionFormClass.createDynaActionFormClass(bean);
                
                form = (ActionForm) dynaClass.newInstance();
                
                
            }
            log.info("FORM is " + form);
            
            DemographicDataAccess dataAccess = (DemographicDataAccess)
            servlet.getServletContext().getAttribute(Constants.Servlet.DEMOGRAPHIC_ACCESS);
            
            Long id = null;
            
            if (request.getParameter(Constants.Request.PATIENT_ID) != null)
                
                id = new Long(Long.parseLong(
                request.getParameter(Constants.Request.PATIENT_ID) ));
            
            if (id != null && id.longValue() != (long) 0) {
                
                DemographicDetail detail = dataAccess.findDemographicDetailById(id);
                
                BeanUtils.copyProperties(form, detail);
                
                log.info("FORM ID IS " + BeanUtils.getSimpleProperty(form, "id"));
                
            }
            
            Util.setScopedMappingAttribute(request, mapping, form);
            
            //            if ("session".equals(mapping.getScope())) {
            //                request.getSession().setAttribute(mapping.getAttribute(), form);
            //
            //            } else {
            //                request.setAttribute(mapping.getAttribute(), form);
            //            }
            //
        } catch (Exception e) {
            Util.setScopedMappingAttribute(request, mapping, form);
            log.info(e);
            ActionError error = new ActionError(e.toString(), e);
            errors.add("failure in EditDemographics", error);
            saveErrors( request, errors);
            return mapping.getInputForward();
        }
        
        return mapping.findForward("successLoadForEdit");
    }
}

