/*
 * ClinicalEditAction.java
 *
 * Created on July 5, 2004, 11:58 PM
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


import org.gnumed.testweb1.persist.ClinicalDataAccess;
import org.gnumed.testweb1.persist.DemographicDataAccess;

import org.gnumed.testweb1.persist.HealthRecordAccess01;

import org.gnumed.testweb1.data.HealthRecord01;

import org.gnumed.testweb1.data.DemographicDetail;
import org.gnumed.testweb1.data.Vaccine;

import org.gnumed.testweb1.global.Constants;
import org.gnumed.testweb1.global.Util;
import org.gnumed.testweb1.global.Constants;
import org.apache.struts.validator.DynaValidatorForm;
import org.apache.struts.config.FormPropertyConfig;

import org.apache.struts.action.ActionFormBeans;
import org.apache.struts.action.ActionFormBean;
import org.apache.struts.action.DynaActionFormClass;

import org.gnumed.testweb1.forms.ClinicalUpdateForm;

import java.util.List;
/**
 *
 * @author  sjtan
 */
public class ClinicalEditAction extends Action {
    
    /** Creates a new instance of ClinicalEditAction */
    public ClinicalEditAction() {
    }
     Log log = LogFactory.getFactory().getLog(this.getClass());
    
    public ActionForward execute(ActionMapping mapping,
    ActionForm form,
    HttpServletRequest request,
    HttpServletResponse response) {
        
        ActionErrors errors = new ActionErrors();
        
        try {
            if (form == null) {
                form = new ClinicalUpdateForm();
            }
            
            log.info("FORM is " + form);
            
            ClinicalDataAccess dataAccess = (ClinicalDataAccess )
            servlet.getServletContext().getAttribute( Constants.Servlet.CLINICAL_ACCESS);
            
            
            
            Long id = null;
            
            if (request.getSession().getAttribute(Constants.Session.VACCINES) == null) {
                List vaccines = dataAccess.getVaccines();
                
                request.getSession().setAttribute(Constants.Session.VACCINES, vaccines);
            }
            
            if (request.getParameter(Constants.Request.PATIENT_ID) != null)
                id = new Long(Long.parseLong( request.getParameter(Constants.Request.PATIENT_ID) ));
            
            if (id != null && id.longValue() != (long) 0) {
                DemographicDataAccess demoDataAccess = (DemographicDataAccess)
                 servlet.getServletContext().getAttribute( 
                    Constants.Servlet.DEMOGRAPHIC_ACCESS);
            
                DemographicDetail detail = demoDataAccess.findDemographicDetailById(id);
                request.setAttribute(Constants.Request.DEMOGRAPHIC_DETAIL_DISPLAY, detail);
                
             
                HealthRecordAccess01 healthRecordAccess = (HealthRecordAccess01)
                servlet.getServletContext().getAttribute( 
                    Constants.Servlet.HEALTH_RECORD_ACCESS);
                
                HealthRecord01 healthRecord = healthRecordAccess.findHealthRecordByIdentityId(id.longValue());
                logHealthIssues(healthRecord);
                request.setAttribute(Constants.Request.HEALTH_RECORD_DISPLAY, healthRecord);
                
              //  log.info("CLIN FORM ID IS " + BeanUtils.getSimpleProperty(form, "id"));
                
            }
            
            Util.setScopedMappingAttribute(request, mapping, form);
            //request.setAttribute(Constants.Request.CLINICAL_UPDATE_FORM, form);
            request.getSession().setAttribute("vaccinations", 
                ((ClinicalUpdateForm)form).getVaccinations());
            
            
        } catch (Exception e) {
            e.printStackTrace();
            Util.setScopedMappingAttribute(request, mapping, form);
            log.info(e);
            ActionError error = new ActionError(e.toString(), e);
            errors.add("failure in EditClinical", error);
            saveErrors( request, errors);
            return mapping.getInputForward();
        }
        
        return mapping.findForward("successLoadClinical");
    }
    
    private void logHealthIssues(   HealthRecord01 healthRecord) {
        List l = healthRecord.getHealthSummary().getHealthIssues();
        log.info("got health issues " + l + " size = " + ( (l == null)? "null" : Integer.toString(l.size())));
        
    
    }
}