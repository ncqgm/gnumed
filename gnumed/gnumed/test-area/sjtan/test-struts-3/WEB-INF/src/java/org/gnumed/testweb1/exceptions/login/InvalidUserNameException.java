/*
 * InvalidUserNameException.java
 *
 * Created on June 18, 2004, 4:51 AM
 */

package org.gnumed.testweb1.exceptions.login;

/**
 *
 * @author  sjtan
 */
public class InvalidUserNameException extends java.lang.Exception {
    
    /**
     * Creates a new instance of <code>InvalidUserNameException</code> without detail message.
     */
    public InvalidUserNameException() {
    }
    
    
    /**
     * Constructs an instance of <code>InvalidUserNameException</code> with the specified detail message.
     * @param msg the detail message.
     */
    public InvalidUserNameException(String msg) {
        super(msg);
    }
}
