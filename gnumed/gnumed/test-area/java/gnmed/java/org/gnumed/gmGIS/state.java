/** Java class "state.java" generated from Poseidon for UML.
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
public class state {
    
    ///////////////////////////////////////
    // attributes
    
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    private Integer id;
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    private String code;
    
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
    
    ///////////////////////////////////////
    // associations
    
    /**
     * <p>
     *
     * </p>
     */
    public country country;
    
    
    ///////////////////////////////////////
    // access methods for associations
    /**
     *@hibernate.many-to-one
     */
    public country getCountry() {
        return country;
    }
    public void setCountry(country _country) {
        this.country = _country;
    }
    
    
    ///////////////////////////////////////
    // operations
    
    
    /**
     * <p>
     * Represents ...
     * </p>
     *  @hibernate.id
     *  generator-class="hilo"
     */
    public Integer getId() {
        return id;
    } // end getId
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    public void setId(Integer _id) {
        id = _id;
    } // end setId
    
    /**
     * <p>
     * Represents ...
     * </p>
     * @hibernate.property
     */
    public String getCode() {
        return code;
    } // end getCode
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    public void setCode(String _code) {
        code = _code;
    } // end setCode
    
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
    } // end setDeprecated
    
} // end state





