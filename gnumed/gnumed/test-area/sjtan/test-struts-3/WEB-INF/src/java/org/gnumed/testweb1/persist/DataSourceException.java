/*
 * DataSourceException.java
 *
 * Created on June 21, 2004, 1:40 AM
 */

package org.gnumed.testweb1.persist;

/**
 *
 * @author  sjtan
 */
public class DataSourceException extends org.apache.commons.lang.exception.NestableException {
    
    /**
     * Creates a new instance of <code>DataSourceException</code> without detail message.
     */
    public DataSourceException() {
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
}
