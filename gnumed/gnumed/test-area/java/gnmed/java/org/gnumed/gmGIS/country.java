/** Java class "country.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.gnumed.gmGIS;

import java.util.*;
import java.util.Date;

/**
 * <p>
 *
 * </p>
 * @hibernate.class
 */
public class country {
    
    ///////////////////////////////////////
    // attributes
    
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    private char[] code;
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    private String name;
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    private Date deprecated;
    
    /** Holds value of property id. */
    private Integer id;
    
    
    ///////////////////////////////////////
    // operations
    
    
    /**
     * <p>
     * Represents ...
     * </p>
     * @hibernate.property
     */
    public String getName() {
        return name;
    } // end getName
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    public void setName(String _name) {
        name = _name;
    } // end setName
    
    /**
     * <p>
     * Represents ...
     * </p>
     * @hibernate.property
     */
    public Date getDeprecated() {
        return deprecated;
    } // end getDeprecated
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    public void setDeprecated(Date _deprecated) {
        deprecated = _deprecated;
    }
    
    /** Getter for property id.
     * @return Value of property id.
     *
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
    
    // end setDeprecated
    
} // end country





