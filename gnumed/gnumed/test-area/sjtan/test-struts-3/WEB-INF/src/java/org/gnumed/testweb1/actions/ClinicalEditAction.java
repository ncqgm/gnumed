/*
 * ClinicalEditAction.java
 *
 * Created on July 5, 2004, 11:58 PM
 */

package org.gnumed.testweb1.actions;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpServlet;
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
    ClinicalActionUtil clinicalActionUtil = new ClinicalActionUtil();
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
            clinicalActionUtil.setRequestAttributes( servlet,  request,   form,  mapping ) ;
        } catch (Exception e) {
            e.printStackTrace();
            clinicalActionUtil.setScopedMappingAttribute(request, mapping, form);
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