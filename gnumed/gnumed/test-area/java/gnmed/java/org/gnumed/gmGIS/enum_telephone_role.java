
/** Java class "enum_telephone_role.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.gnumed.gmGIS;

import java.util.*;

/**
 * <p>
 *
 * </p>
 * @hibernate.class
 */
public class enum_telephone_role {
    
    ///////////////////////////////////////
    // attributes
    
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    private String role;
    
    /** Holds value of property id. */
    private Integer id;
    
    
    ///////////////////////////////////////
    // operations
    
    
    /**
     * <p>
     * Represents ...
     * </p>
     * @hibernate.property
     *
     */
    public String getRole() {
        return role;
    } // end getRole
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    public void setRole(String _role) {
        role = _role;
    }
    
    /** Getter for property id.
     * @return Value of property id.
     * @hibernate.id
     *      generator-class="hilo"
     */
    public Integer getId() {
        return this.id;
    }
    
    /** Setter for property id.
     * @param id New value of property id.
     *
     */
    public void setId(Integer id) {
        this.id = id;
    }
    
    public boolean equals(final Object role) {
        if (role instanceof enum_telephone_role) {
            enum_telephone_role other = (enum_telephone_role)role;
            return getId().equals(other.getId()) || getRole().equals(other.getRole());
        }
        return super.equals(role);
    }
    
    // end setRole
    
} // end enum_telephone_role



