/*
 * MockLoginModuleAdapterPlugIn.java
 *
 * Created on June 22, 2004, 4:19 PM
 */

package org.gnumed.testweb1.adapters;
import org.gnumed.testweb1.business.LoginModule;
import org.apache.struts.action.PlugIn;
import org.apache.struts.config.PlugInConfig;
import java.util.Map;
import java.util.Iterator;
import org.apache.commons.logging.LogFactory;
import org.apache.commons.logging.Log;
import org.gnumed.testweb1.global.Util;
import  org.gnumed.testweb1.global.Constants;


/**
 *
 * @author  sjtan
 */
public class LoginModuleAdapterPlugIn implements PlugIn {
    public final  static String LOGIN_MODULE="loginModule";
    LoginModule module;
    Log log = LogFactory.getFactory().getLog(this.getClass());
    /** Creates a new instance of MockLoginModuleAdapterPlugIn */
    public LoginModuleAdapterPlugIn() {
    
    }
    
    void setLoginModule( LoginModule module) {
        this.module = module;
    }
 
    LoginModule getLoginModule() {
        return this.module;
    }
    
    public void destroy() {
    }
    
    public void init(org.apache.struts.action.ActionServlet actionServlet, org.apache.struts.config.ModuleConfig moduleConfig) throws javax.servlet.ServletException {
        PlugInConfig config = Util.findPluginConfig(moduleConfig, this.getClass());
        Map map = config.getProperties();
        String moduleClassName =(String) map.get(LOGIN_MODULE);
        try {
            LoginModule module = (LoginModule) Class.forName(moduleClassName).newInstance();
            actionServlet.getServletContext().setAttribute(Constants.LOGIN_MODULE, module);
        } catch(Exception e) {
            log.error(e);
        }
    }
    
}
