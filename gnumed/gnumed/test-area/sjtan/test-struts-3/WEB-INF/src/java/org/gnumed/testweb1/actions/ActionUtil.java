/*
 * ActionUtil.java
 *
 * Created on September 24, 2004, 5:56 PM
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
import org.apache.struts.action.DynaActionForm;

import org.gnumed.testweb1.forms.ClinicalUpdateForm;

import java.util.List;
/**
 *
 * @author  sjtan
 */
public class ActionUtil {
    Log log = LogFactory.getFactory().getLog( ActionUtil.class);
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
