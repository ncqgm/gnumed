/*
 * DataObjectFactoryPlugin.java
 *
 * Created on June 19, 2004, 6:43 PM
 */

package org.gnumed.testweb1.adapters;
import java.util.Iterator;
import java.util.Map;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.struts.action.PlugIn;
import org.apache.struts.config.PlugInConfig;
import org.apache.struts.upload.FormFile;
import org.gnumed.testweb1.data.DataObjectFactory;
import org.gnumed.testweb1.global.Constants;
import org.gnumed.testweb1.global.Util;
import org.gnumed.testweb1.forms.ClinicalFormFactory1;
import org.gnumed.testweb1.forms.IClinicalFormFactory;
/**
 *
 * @author  sjtan
 */
public class DataObjectFactoryPlugIn extends BasicPlugin implements PlugIn {
   
    
    Log log = LogFactory.getLog(this.getClass());
    
    /** Creates a new instance of DataObjectFactoryPlugin */
    public DataObjectFactoryPlugIn() {
    }
    
    public void destroy() {
    }
    
    private void logProperties(Map map) {
        Iterator it = map.entrySet().iterator();
        
        while (it.hasNext()) {
            Map.Entry entry = (Map.Entry) it.next();
            log.info( this + " has property " + entry.getKey() + ":" + entry.getValue());
        }
    }
    
    /** the PlugInConfig is the object constructed from 
     * the xml configuration in struts-config.xml for this plugin.
     * The map of properties of this config, has the name of the 
     * class used as the implementation of dataObjectFactory.
     */
    public void init(org.apache.struts.action.ActionServlet actionServlet, org.apache.struts.config.ModuleConfig moduleConfig) throws javax.servlet.ServletException {
        
        DataObjectFactory factory = null;
        IClinicalFormFactory formFactory = null;
        try {
            factory = (DataObjectFactory)
            Class.forName( getPluginConfigValue(moduleConfig, Constants.Servlet.OBJECT_FACTORY) ).newInstance();
            
            factory.setBundle(getResourceBundle(moduleConfig));
            
            actionServlet.getServletContext().setAttribute(Constants.Servlet.OBJECT_FACTORY, factory);
            
            log.info ("Set Servlet context attribute "+ Constants.Servlet.OBJECT_FACTORY);
            
           
        } catch (Exception e) {
            log.error( "UNABLE TO SET '" + Constants.Servlet.OBJECT_FACTORY + "' of servlet context", e);
        }
        
       
        
        try {
            formFactory = (IClinicalFormFactory) Class.forName(getPluginConfigValue(moduleConfig, Constants.Servlet.FORM_FACTORY) ).newInstance();
            formFactory.setDataObjectFactory(factory);
           formFactory.setEntryEpisodeCount(Integer.parseInt(getPluginConfigValue(moduleConfig, Constants.Servlet.FORM_FACTORY_EPISODE_COUNT)));
            actionServlet.getServletContext().setAttribute(Constants.Servlet.FORM_FACTORY, formFactory);
        } catch (Exception e) {
            // TODO: handle exception
        }
    }

    /**
     * @param moduleConfig
     * @param stringFactoryName TODO
     * @return
     */
    private String getPluginConfigValue(org.apache.struts.config.ModuleConfig moduleConfig, String stringFactoryName) {
        PlugInConfig c = Util.findPluginConfig(moduleConfig, this.getClass());
        Map map = c.getProperties();
        
        logProperties(map);
        
        String implClassName =(String) map.get(stringFactoryName);
        return implClassName;
    }
    
}
