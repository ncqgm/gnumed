/*
 * DemographicEntryAction.java
 *
 * Created on June 16, 2004, 9:30 PM
 */

package org.gnumed.testweb1.actions;
/*
 * LoginAction.java
 *
 * Created on June 18, 2004, 4:23 AM
 */

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
import org.gnumed.testweb1.data.Vaccination;

import org.gnumed.testweb1.persist.DemographicDataAccess;

import org.gnumed.testweb1.forms.ClinicalUpdateForm;

import org.gnumed.testweb1.global.Constants;
import org.gnumed.testweb1.global.Util;
import java.util.List;
/**
 *
 * @author  sjtan
 */
public class ClinicalSaveAction extends Action {
    
    /** Creates a new instance of DemographicEntryAction */
    public ClinicalSaveAction() {
    }
    Log log = LogFactory.getFactory().getLog(this.getClass());
    
    
    
    public ActionForward execute(ActionMapping mapping,
    ActionForm form,
    HttpServletRequest request,
    HttpServletResponse response) {
        
        ActionErrors errors = new ActionErrors();
        
        try {
//            Enumeration en1 = request.getSession().getAttributeNames() ;
//            while(en1.hasMoreElements()) {
//                log.info("Session has attribute " + en1.nextElement());
//            }
//            String[] ss = request.getSession().getValueNames();
//            for (int i =0; i < ss.length; ++i) {
//                log.info("And object value names = " + ss[i]);
//            }
            
           
            Map map = new java.util.HashMap();
            
            DataObjectFactory objFactory = (DataObjectFactory)
            servlet.getServletContext().
            getAttribute(Constants.Servlet.OBJECT_FACTORY);
            
            ClinicalUpdateForm cform = (ClinicalUpdateForm) form;
            log.info("TEST ATTRIBUTE FROM "+cform + " = "+cform.getTest());
            
            
            
            List l = java.util.Arrays.asList(cform.getVaccinations());
            Iterator i = l.iterator();
            while (i.hasNext()) {
                Vaccination v = (Vaccination)i.next();
                if (v.getVaccineGiven() == null || v.getVaccineGiven().trim().equals("") ) {
                    log.info("GOT " + v + " which was empty");
                } else {
                    log.info("GOT vaccineGiven" + v.getVaccineGiven() + " on " + v.getDateGivenString()
                    + " batch no =" +v.getBatchNo() + " , and site given = " + v.getSiteGiven());
                }
                
                
            }
            
            
            // logging
            //    org.gnumed.testweb1.global.Util.logBean(log, form);
            
            
            
            //Using the persist module
            
            //   org.gnumed.testweb1.global.Util.logBean(log, detail);
            
            return mapping.findForward("success");
            
        } catch (Exception e)  {
            log.error("error in " + this.toString() , e);
            
            errors.add(errors.GLOBAL_MESSAGE, new ActionError("errors.detailSave" , e , e.getCause() ) );
        }
        finally {
            
            
        }
        
        saveErrors(request, errors);
        //   return  mapping.getInputForward();
        
        Util.setScopedMappingAttribute(request, mapping, form);
        
        return mapping.getInputForward();
    }
    
}
