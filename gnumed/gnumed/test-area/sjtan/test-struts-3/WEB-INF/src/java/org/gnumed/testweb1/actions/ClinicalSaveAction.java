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
import org.gnumed.testweb1.data.ClinNarrative;
import org.gnumed.testweb1.data.HealthRecord01;
import org.gnumed.testweb1.data.HealthSummary01;

import org.gnumed.testweb1.persist.DemographicDataAccess;
import org.gnumed.testweb1.persist.HealthRecordAccess01;

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
       //     log.info("TEST ATTRIBUTE FROM "+cform + " = "+cform.getTest());
            
            
            
            List l = java.util.Arrays.asList(cform.getVaccinations());
            Iterator i = l.iterator();
            while (i.hasNext()) {
                Vaccination v = (Vaccination)i.next();
                if (v.getVaccineGiven() == null || v.getVaccineGiven().trim().equals("") ) {
                    log.info("GOT " + v + " which was empty");
                } else {
                    log.info("GOT vaccineGiven" + v.getVaccineGiven() + " on " + v.getDateGivenString()
                    + " batch no =" +v.getBatchNo() + " , and site given = " + v.getSite());
                }
                
                
            }
            

            List l2 =java.util. Arrays.asList(cform.getNarratives() );
            if (l2.equals( cform.getEncounter().getNarratives() ) ) {
                log.info("The narratives are the same in the form");
            }
             System.err.println("There are " +l2.size() + "NARRATIVES");
            Iterator j =l2.iterator();
            while(j.hasNext()) {
                ClinNarrative n = (ClinNarrative) j.next();
                 log.info("narrative found with text " + n.getNarrative() + ">");
                 log.info("Health issue name for " + n + " was " + n.getHealthIssueName());
            }
            
            HealthRecordAccess01 access = 
            (HealthRecordAccess01) servlet.getServletContext().
                getAttribute(Constants.Servlet.HEALTH_RECORD_ACCESS);
            
            HealthRecord01 record = (HealthRecord01) request.getSession().getAttribute(Constants.Session.HEALTH_RECORD);
            access.save(cform.getEncounter() , record.getHealthSummary() );
            
            // logging
            //    org.gnumed.testweb1.global.Util.logBean(log, form);
            
            
            
            //Using the persist module
            
            //   org.gnumed.testweb1.global.Util.logBean(log, detail);
            
            return mapping.findForward("success");
            
        } catch (Exception e)  {
              
            
            e.printStackTrace();
            Util.setScopedMappingAttribute(request, mapping, form);
            log.info(e);
            ActionError error = new ActionError(e.toString(), e);
            errors.add("failure in EditClinical", error);
            saveErrors( request, errors);
            return mapping.getInputForward();
        }
        
    }
    
}
