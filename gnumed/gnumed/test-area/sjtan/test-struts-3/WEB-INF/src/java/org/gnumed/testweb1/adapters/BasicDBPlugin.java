/*
 * BasicDBPlugin.java
 *
 * Created on June 19, 2004, 9:21 PM
 */

package org.gnumed.testweb1.adapters;
import org.apache.struts.action.PlugIn;
import org.apache.struts.config.PlugInConfig;
import java.util.Map;
import java.util.Iterator;
import org.apache.commons.logging.LogFactory;
import org.apache.commons.logging.Log;
/**
 *
 * @author  sjtan
 */
public class BasicDBPlugin implements PlugIn{
    
    /** Creates a new instance of BasicDBPlugin */
    public BasicDBPlugin() {
    }
    
    public void destroy() {
    }
    
    public void init(org.apache.struts.action.ActionServlet actionServlet, org.apache.struts.config.ModuleConfig moduleConfig) throws javax.servlet.ServletException {
    }
    
}
