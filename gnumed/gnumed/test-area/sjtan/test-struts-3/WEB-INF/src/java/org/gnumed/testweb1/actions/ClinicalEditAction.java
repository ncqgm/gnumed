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
import org.gnumed.testweb1.persist.DataSourceException;
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
     Log log = LogFactory.getLog(this.getClass());
    
    public ActionForward execute(ActionMapping mapping,
    ActionForm form,
    HttpServletRequest request,
    HttpServletResponse response) {
        
        ActionErrors errors = new ActionErrors();
        
        try {
            
            setVaccinesOnSession(request);
             
            Long id = getIdFromRequest(request);
            
            if (id != null && id.longValue() != (long) 0) {
                setDemographicDetailOnSession(request, id);
                 setHealthRecordOnSession(request, id);
                  
            }
        	
            if (form == null) {
            	DataObjectFactory factory =  
            		(DataObjectFactory) servlet.getServletContext()
					.getAttribute(Constants.Servlet.OBJECT_FACTORY);
            	
                form = new ClinicalUpdateForm(factory, new Integer( id.intValue()) );
                
                
            }
            
            log.info("FORM is " + form);

            
            Util.setScopedMappingAttribute(request, mapping, form);
           
            
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
    
    /**
	 * @param request
	 * @param id
	 * @return
	 */
	private Long getIdFromRequest(HttpServletRequest request ) {
		Long id = null;
		if (request.getParameter(Constants.Request.PATIENT_ID) != null)
		    id = new Long(Long.parseLong( request.getParameter(Constants.Request.PATIENT_ID) ));
		return id;
	}

	/**
	 * @param request
	 * @param id
	 * @throws DataSourceException
	 */
	private void setHealthRecordOnSession(HttpServletRequest request, Long id) throws DataSourceException {
		HealthRecordAccess01 healthRecordAccess = (HealthRecordAccess01)
		servlet.getServletContext().getAttribute( 
		    Constants.Servlet.HEALTH_RECORD_ACCESS);
		
		HealthRecord01 healthRecord = healthRecordAccess.findHealthRecordByIdentityId(id.longValue());
		
		request.getSession().setAttribute(Constants.Session.HEALTH_RECORD, healthRecord);
		
		logHealthIssues(healthRecord);
		
	}

	/**
	 * @param request
	 * @param id
	 * @throws DataSourceException
	 */
	private void setDemographicDetailOnSession(HttpServletRequest request, Long id) throws DataSourceException {
		DemographicDataAccess demoDataAccess = (DemographicDataAccess)
		 servlet.getServletContext().getAttribute( 
		    Constants.Servlet.DEMOGRAPHIC_ACCESS);
         
		DemographicDetail detail = demoDataAccess.findDemographicDetailById(id);
		request.setAttribute(Constants.Request.DEMOGRAPHIC_DETAIL_DISPLAY, detail);
	}

	/**
	 * @param request
	 * @throws DataSourceException
	 */
	private void setVaccinesOnSession(HttpServletRequest request) throws DataSourceException {
		ClinicalDataAccess dataAccess = (ClinicalDataAccess )
		servlet.getServletContext().getAttribute( Constants.Servlet.CLINICAL_ACCESS);
		
		if (request.getSession().getAttribute(Constants.Session.VACCINES) == null) {
		    List vaccines = dataAccess.getVaccines();
		    
		    request.getSession().setAttribute(Constants.Session.VACCINES, vaccines);
		}
	}

	private void logHealthIssues(   HealthRecord01 healthRecord) {
        List l = healthRecord.getHealthSummary().getHealthIssues();
        log.info("got health issues " + l + " size = " + ( (l == null)? "null" : Integer.toString(l.size())));
        
    
    }
}