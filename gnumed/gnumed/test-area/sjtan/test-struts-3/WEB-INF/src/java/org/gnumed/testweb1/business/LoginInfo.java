/*
 * Created on 06-Feb-2005
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
package org.gnumed.testweb1.business;

import java.sql.Connection;
import java.sql.SQLException;

import javax.sql.DataSource;

/**
 * @author sjtan
 *
 * TODO To change the template for this generated type comment go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
public class LoginInfo {
    private char[] username;
    private char[] password;
    public LoginInfo( String username, String password) {
        this.username = new char[ username.length()];
        this.password = new char[ password.length()];
        
        username.getChars(0, this.username.length, this.username,0);
        password.getChars(0, this.password.length, this.password,0);
    }
    
    public Connection getConnection(DataSource src) throws SQLException {
        
        return src.getConnection(String.copyValueOf(this.username), String.copyValueOf(this.password));
         
    }
}
