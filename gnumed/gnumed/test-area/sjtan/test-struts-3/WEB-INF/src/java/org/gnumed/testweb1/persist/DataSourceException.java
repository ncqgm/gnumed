/*
 * DataSourceException.java
 *
 * Created on June 21, 2004, 1:40 AM
 */

package org.gnumed.testweb1.persist;

import java.util.Iterator;
import java.util.List;

/**
 *
 * @author  sjtan
 */
//public class DataSourceException extends org.apache.commons.lang.exception.NestableException {
public class DataSourceException extends Exception {
    String msg;
    /**
     * Creates a new instance of <code>DataSourceException</code> without detail message.
     */
    public DataSourceException() {
    }
    
    public DataSourceException( List l) {
    	
    	Iterator i= l.iterator();
    	StringBuffer sb = new StringBuffer("\nextra errors:\n");
    	while(i.hasNext()) {
    		Object o = i.next();
    		if (o instanceof Exception) {
    			Exception e = (Exception)o;
    			sb.append(e.getMessage()).append('\n');
    		}
    	}
    	
    	this.msg = sb.toString();
    	
    }
    
    public DataSourceException( Throwable e) {
        super(e);
    }
    
    public DataSourceException(String s, Throwable e) {
        super(s,e);
    }
    
    /**
     * Constructs an instance of <code>DataSourceException</code> with the specified detail message.
     * @param msg the detail message.
     */
    public DataSourceException(String msg) {
        super(msg);
    }
    
    public String getMessage() {
    	return super.getMessage() + ( msg != null ? msg:"");
    }
}
