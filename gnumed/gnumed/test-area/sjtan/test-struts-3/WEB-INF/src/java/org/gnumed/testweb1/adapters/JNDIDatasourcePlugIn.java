/*
 * JNDIDatasourcePlugin.java
 *
 * Created on June 20, 2004, 11:13 PM
 */

package org.gnumed.testweb1.adapters;
import javax.naming.Context;
import javax.naming.InitialContext;
import javax.sql.DataSource;

import org.apache.struts.action.PlugIn;
import org.gnumed.testweb1.global.Constants;
/**
 *
 * @author  sjtan
 */
public class JNDIDatasourcePlugIn implements PlugIn {
    
    /** Creates a new instance of JNDIDatasourcePlugin */
    public JNDIDatasourcePlugIn() {
    }
    
    public void destroy() {
    }    
    /** looks up the jndi context at application startup and gets
     * a reference to a apache common's dbcp  pooled datasource,
     * and sets an attribute on the servlet context by the name
     * Constants.POOLED_DATASOURCE to the reference. 
     * This addresses a bug where looking up the ctx in another
     * servlet call returns a null BasicDataSource.
     */
    public void init(org.apache.struts.action.ActionServlet actionServlet,
        
        org.apache.struts.config.ModuleConfig moduleConfig) throws javax.servlet.ServletException {
        try {
        Context ctx = new InitialContext();
        Context ctx2 = (Context) ctx.lookup(Constants.JNDI_ROOT);
        DataSource src = (DataSource) ctx2.lookup(Constants.JNDI_REF_POOLED_CONNECTIONS);
        actionServlet.getServletContext().setAttribute(Constants.POOLED_DATASOURCE,  src);
        } catch(Exception e) {
            throw new javax.servlet.ServletException("Unable to set servlet attribute for pooled datasource", e);
        }
        
    }
    
}
