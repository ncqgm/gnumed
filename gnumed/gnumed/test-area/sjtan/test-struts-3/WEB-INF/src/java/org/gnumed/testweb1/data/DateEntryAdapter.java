/*
 * Created on 04-Oct-2004
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
package org.gnumed.testweb1.data;
 
	import java.lang.reflect.InvocationTargetException;

import org.apache.commons.beanutils.BeanUtils;
import org.apache.commons.beanutils.PropertyUtils;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.gnumed.testweb1.global.Util;
	/**
	 *
	 * @author  sjtan
	 */
	public class DateEntryAdapter {
		
	    
	    static  Log log = LogFactory.getLog(ClinWhenEntryAdapter.class);
		private String property;
		private Object target;
	    
	    /** Creates a new instance of ClinWhenEntryAdapter */
	    public DateEntryAdapter(Object target, String property) {
	        this.target = target;
	        this.property = property;
	    }
	    
	     
	    public String getDateString() {
	        try {
				return Util.getShortestDateTimeString((java.util.Date)PropertyUtils.getProperty(target, property));
			} catch (IllegalAccessException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			} catch (InvocationTargetException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			} catch (NoSuchMethodException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			return "";
	    }
	    
	    public void setDateString(String dateString)  {
	        try {
	            log.info("STRING " + dateString + " PARSES TO " +Util.parseDate(dateString.trim() ));
	            BeanUtils.setProperty(target, property, Util.parseDate(dateString));
	        } catch (Exception e) {
	            log.error(e);
	            e.printStackTrace();
	        }
	    }
	    
	

}
