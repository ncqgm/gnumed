/*
 * UpdateDemographicException.java
 *
 * Created on June 16, 2004, 9:34 PM
 */

package org.gnumed.testweb1.exceptions.demographic;

/**
 *
 * @author  sjtan
 */
public class UpdateDemographicException extends java.lang.Exception {
    
    /**
     * Creates a new instance of <code>UpdateDemographicException</code> without detail message.
     */
    public UpdateDemographicException() {
    }
    
    
    /**
     * Constructs an instance of <code>UpdateDemographicException</code> with the specified detail message.
     * @param msg the detail message.
     */
    public UpdateDemographicException(String msg) {
        super(msg);
    }
}
