/*
 * CreateDemographicException.java
 *
 * Created on June 16, 2004, 9:34 PM
 */

package org.gnumed.testweb1.exceptions.demographic;

/**
 *
 * @author  sjtan
 */
public class CreateDemographicException extends java.lang.Exception {
    
    /**
     * Creates a new instance of <code>CreateDemographicException</code> without detail message.
     */
    public CreateDemographicException() {
    }
    
    
    /**
     * Constructs an instance of <code>CreateDemographicException</code> with the specified detail message.
     * @param msg the detail message.
     */
    public CreateDemographicException(String msg) {
        super(msg);
    }
}
