/*
 * CommType.java
 *
 * Created on June 21, 2004, 6:59 AM
 */

package org.gnumed.testweb1.global;

/**
 *
 * @author  sjtan
 */
public class CommType {
    public static CommType email, fax, homephone, workphone, mobile , web, jabber;
    static {
        email = new CommType(1);
        fax =new CommType(2);
        homephone = new CommType(3);
        workphone= new CommType(4);
        mobile = new CommType(5);
        web = new CommType(6);
        jabber = new CommType(7);
    }
    
    
    
    
    /**
     * Holds value of property id.
     */
    private int id;
    
    /** Creates a new instance of CommType */
    public CommType(int id) {
        this.id = id;
    }
    
    /**
     * Getter for property id.
     * @return Value of property id.
     */
    public int getId() {
        return this.id;
    }
    
    /**
     * Setter for property id.
     * @param id New value of property id.
     */
    public void setId(int id) {
    }
    
}
