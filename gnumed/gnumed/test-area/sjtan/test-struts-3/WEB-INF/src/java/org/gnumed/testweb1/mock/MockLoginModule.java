/*
 * MockLoginModule.java
 *
 * Created on June 18, 2004, 4:54 AM
 */

package org.gnumed.testweb1.mock;
import org.gnumed.testweb1.business.LoginModule;
import org.gnumed.testweb1.exceptions.login.InvalidPasswordException;
import org.gnumed.testweb1.exceptions.login.InvalidUserNameException;

/**
 *
 * @author  sjtan
 */
public class MockLoginModule implements LoginModule {
    
    /** Creates a new instance of MockLoginModule */
    public MockLoginModule() {
    }
    
    public void validate(String username, byte[] password) throws InvalidUserNameException, InvalidPasswordException {
//                if ( !username.equals("admin") ) {
//                    throw new InvalidUserNameException();
//                }
//                
//                byte[] p = password;
//                if ( p.length ==8 && p[0] =='p' && p[1] =='a' &&  (p[2] | p[3]) =='s'
//                      && p[4] == 'w' && p[5] =='o' && p[6]=='r' && p[7] =='d'
//                      
//                                ) 
                    return;
//               throw new InvalidPasswordException();
    }    
    
}
