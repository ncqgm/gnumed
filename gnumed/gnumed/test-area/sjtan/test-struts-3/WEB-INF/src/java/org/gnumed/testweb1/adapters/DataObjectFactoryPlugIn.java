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
import org.gnumed.testweb1.data.DataObjectFactory;
import org.gnumed.testweb1.global.Constants;
import org.gnumed.testweb1.global.Util;
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
    
    public void init(org.apache.struts.action.ActionServlet actionServlet, org.apache.struts.config.ModuleConfig moduleConfig) throws javax.servlet.ServletException {
        
        PlugInConfig c = Util.findPluginConfig(moduleConfig, this.getClass());
        Map map = c.getProperties();
        
        logProperties(map);
        
        String implClassName =(String) map.get(Constants.Servlet.OBJECT_FACTORY);
        DataObjectFactory factory = null;
        try {
            factory = (DataObjectFactory) Class.forName(implClassName).newInstance();
            
            factory.setBundle(getResourceBundle(moduleConfig));
            actionServlet.getServletContext().setAttribute(Constants.Servlet.OBJECT_FACTORY, factory);
            log.info ("Set Servlet context attribute "+ Constants.Servlet.OBJECT_FACTORY);
            
           
        } catch (Exception e) {
            log.error( "UNABLE TO SET '" + Constants.Servlet.OBJECT_FACTORY + "' of servlet context", e);
        }
        
        
        //TODO
        // move this somewhere better
        
        try {
            
             org.gnumed.testweb1.forms.ClinicalUpdateForm.setDataObjectFactory((org.gnumed.testweb1.data.DataObjectFactory) factory);
                
            log.info ("Set clinical update form "+ Constants.Servlet.OBJECT_FACTORY);
            
           
        } catch (Exception e) {
            log.error( "UNABLE TO SET '" + Constants.Servlet.OBJECT_FACTORY + "' of clinical update form class", e);
        }
    }
    
}
