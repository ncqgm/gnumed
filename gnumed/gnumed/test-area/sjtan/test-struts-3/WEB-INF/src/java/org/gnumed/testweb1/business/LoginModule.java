/*
 * LoginModule.java
 *
 * Created on June 18, 2004, 4:49 AM
 */

package org.gnumed.testweb1.business;
import org.gnumed.testweb1.exceptions.login.*;
/**
 *
 * @author  sjtan
 */
public interface LoginModule {
    
    void validate ( String username, byte[] password ) throws InvalidUserNameException, InvalidPasswordException;
}
