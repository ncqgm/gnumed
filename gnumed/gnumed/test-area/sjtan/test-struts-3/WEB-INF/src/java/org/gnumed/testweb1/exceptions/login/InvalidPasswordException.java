/*
 * InvalidPasswordException.java
 *
 * Created on June 18, 2004, 4:52 AM
 */

package org.gnumed.testweb1.exceptions.login;


/**
 *
 * @author  sjtan
 */
public class InvalidPasswordException extends java.lang.Exception {
    
    /**
     * Creates a new instance of <code>InvalidPasswordException</code> without detail message.
     */
    public InvalidPasswordException() {
    }
    
    
    /**
     * Constructs an instance of <code>InvalidPasswordException</code> with the specified detail message.
     * @param msg the detail message.
     */
    public InvalidPasswordException(String msg) {
        super(msg);
    }
}
