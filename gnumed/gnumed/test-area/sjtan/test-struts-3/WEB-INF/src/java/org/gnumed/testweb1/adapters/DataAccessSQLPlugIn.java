/*
 * DemographicDataAccessSQLPlugin.java
 *
 * Created on June 21, 2004, 9:54 AM
 */

package org.gnumed.testweb1.adapters;

import org.apache.struts.action.PlugIn;
import org.apache.struts.config.PlugInConfig;
import org.apache.struts.config.MessageResourcesConfig;
import java.util.Map;
import java.util.Iterator;

import org.apache.commons.logging.LogFactory;
import org.apache.commons.logging.Log;

import javax.naming.Context;
import javax.naming.InitialContext;

import javax.sql.DataSource;

import javax.naming.NameClassPair;
import javax.naming.NamingEnumeration;
import javax.naming.Binding;
import javax.naming.Referenceable;
import java.util.Enumeration;
import org.gnumed.testweb1.global.Constants;

import org.gnumed.testweb1.global.Util;

import org.gnumed.testweb1.persist.DemographicDataAccess;
import org.gnumed.testweb1.persist.scripted.ScriptedSQLDemographicDataAccess;
import org.gnumed.testweb1.persist.scripted.DemographicDetailSQL;
import org.gnumed.testweb1.persist.scripted.ClinicalSQL;
import org.gnumed.testweb1.persist.scripted.ScriptedSQLClinicalAccess;
import org.gnumed.testweb1.persist.HealthRecordAccess01;

import org.gnumed.testweb1.persist.DataObjectFactoryUsing;
import org.gnumed.testweb1.persist.ResourceBundleUsing;

import org.gnumed.testweb1.data.DataObjectFactory;
import org.apache.struts.util.MessageResources;

import java.util.ResourceBundle;
import java.util.PropertyResourceBundle;
/**
 *
 * @author  sjtan
 */
public class DataAccessSQLPlugIn implements PlugIn {
    public final static String IMPL="impl";
    /** Creates a new instance of DemographicDataAccessSQLPlugin */
    public DataAccessSQLPlugIn() {
    }
    
    Log log = LogFactory.getFactory().getLog(this.getClass());
    
    public void destroy() {
    }
    
    private void setDataObjectFactory( DataObjectFactoryUsing factoryUsing, DataObjectFactory factory) {
        factoryUsing.setDataObjectFactory(factory);
    }
    
    private void setResourceBundleUsing( ResourceBundleUsing user, ResourceBundle bundle) {
        user.setResourceBundle(bundle);
    }
    
    
    public void init(org.apache.struts.action.ActionServlet actionServlet, org.apache.struts.config.ModuleConfig moduleConfig) throws javax.servlet.ServletException {
        try {
            
            Context ctx = new InitialContext();
            Context ctx2 = (Context) ctx.lookup(Constants.JNDI_ROOT);
            
            DataSource dataSource = (DataSource) ctx2.lookup(Constants.JNDI_REF_POOLED_CONNECTIONS);
            
            
            
            
            
            log.info( this + " got " + dataSource);
            
            PlugInConfig c0 = Util.findPluginConfig(moduleConfig, DataObjectFactoryPlugIn.class);
            Map mapFactory = c0.getProperties();
            
            
            
            PlugInConfig c = Util.findPluginConfig(moduleConfig, this.getClass());
            
            Map map = c.getProperties();
            
            //        Enumeration k = actionServlet.getServletContext().getAttributeNames();
            //        while (k.hasMoreElements() ) {
            //               log.info("attribute="+ k.nextElement());
            //.
            //        }
            
            DataObjectFactory factory = null;
            try {
                String dataObjectFactoryClassName = 
                    (String)mapFactory.get(Constants.Servlet.OBJECT_FACTORY);
                
                factory = (DataObjectFactory) Class.forName(dataObjectFactoryClassName).newInstance();
                
                log.info(this + " found the data object implementation " + dataObjectFactoryClassName);
                
            } catch (Exception e) {
                log.error(e);
            }
            
            ResourceBundle bundle = null;
            try {
                String resourceParameter = moduleConfig.findMessageResourcesConfig("org.apache.struts.action.MESSAGE").getParameter();
                
                bundle = PropertyResourceBundle.getBundle(resourceParameter);
            } catch (Exception e) {
                log.error(e);
            }
            
            try {
                String demoImplClassName =
                (String) map.get(Constants.Plugin.DEMOGRAPHIC_SQL_PROVIDER);
                
                DemographicDetailSQL sqlScriptImpl =
                (DemographicDetailSQL) Class.forName(demoImplClassName).newInstance();
                
                setResourceBundleUsing((ResourceBundleUsing)sqlScriptImpl, bundle);
                setDataObjectFactory((DataObjectFactoryUsing)sqlScriptImpl, factory);
                
                ScriptedSQLDemographicDataAccess dbAccess = new ScriptedSQLDemographicDataAccess();
                
                dbAccess.setDataSource(dataSource);

                dbAccess.setDemographicDetailSQL((DemographicDetailSQL) sqlScriptImpl);
                      
                actionServlet.getServletContext().setAttribute(Constants.Servlet.DEMOGRAPHIC_ACCESS , dbAccess );
                
                     
            } catch (Exception e) {
                log.error( "UNABLE TO SET '" +
                DemographicDataAccess.DEMOGRAPHIC_ACCESS  +
                "' of servlet context", e);
            }
             ScriptedSQLClinicalAccess scriptedClinicalAccess = null;
            try {
                
                String clinImplClassName=
                    
                        (String) map.get(Constants.Plugin.CLINICAL_SQL_PROVIDER);
                
                
                ClinicalSQL clinSqlScriptImpl =
                    
                        (ClinicalSQL) Class.forName(clinImplClassName).newInstance();
               
                setResourceBundleUsing((ResourceBundleUsing) clinSqlScriptImpl, bundle);
                
                setDataObjectFactory((DataObjectFactoryUsing) clinSqlScriptImpl, factory);
           
            
                scriptedClinicalAccess = new ScriptedSQLClinicalAccess();
                scriptedClinicalAccess.setDataSource(dataSource);
               scriptedClinicalAccess.setClinicalSQL(clinSqlScriptImpl);
               actionServlet.getServletContext().
               setAttribute(Constants.Servlet.CLINICAL_ACCESS , scriptedClinicalAccess);
                
            } catch (Exception e) {
                log.error(e);
            }
            
            try {
                String implClassName =
                (String) map.get(Constants.Plugin.HEALTH_RECORD_ACCESS_PROVIDER);
                
                
                HealthRecordAccess01 healthRecordAccess = 
                (HealthRecordAccess01) Class.forName(implClassName).newInstance();
                log.info("implClassName for health record access" + implClassName);
                 
                healthRecordAccess.setDataSource(dataSource);
                healthRecordAccess.setDataObjectFactory(factory);
                healthRecordAccess.setClinicalDataAccess(scriptedClinicalAccess);
                
                actionServlet.getServletContext().setAttribute(Constants.Servlet.HEALTH_RECORD_ACCESS , healthRecordAccess);
                
                     
            } catch (Exception e) {
                log.error( "UNABLE TO SET '" + "HealthRecordAccess"
                   +
                "' of servlet context", e);
            }
            
            
            
            
        } catch(Exception e) {
            throw new javax.servlet.ServletException("Unable to set servlet attribute for pooled datasource", e);
        }
    }
    
}
