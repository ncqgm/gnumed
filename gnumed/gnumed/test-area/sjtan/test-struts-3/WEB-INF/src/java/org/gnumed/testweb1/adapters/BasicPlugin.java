/*
 * Created on 04-Oct-2004
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
package org.gnumed.testweb1.adapters;

import java.util.PropertyResourceBundle;
import java.util.ResourceBundle;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
/**
 * @author sjtan
 *
 * TODO To change the template for this generated type comment go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
public class BasicPlugin {
	/**
	 * @param moduleConfig
	 * @return 
	 */
	Log log = LogFactory.getLog(this.getClass());
	protected ResourceBundle getResourceBundle(org.apache.struts.config.ModuleConfig moduleConfig) {
		ResourceBundle bundle = null;
		try {
		    String resourceParameter = moduleConfig.findMessageResourcesConfig("org.apache.struts.action.MESSAGE").getParameter();
		    
		    bundle = PropertyResourceBundle.getBundle(resourceParameter);
		} catch (Exception e) {
		    log.error(e);
		}
		return bundle;
	}
}
