/** Java class "Location.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.common;

import java.util.*;

/**
 * <p>
 *
 * </p>
 *@hibernate.class
 *  table="location"
 */
public class Location {
    
    ///////////////////////////////////////
    // attributes
    
    private Long id;
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
    private String code;
    
    ///////////////////////////////////////
    // associations
    
    /**
     * <p>
     *
     * </p>
     */
    public Collection sub = new java.util.HashSet(); // of type Location
    /**
     * <p>
     *
     * </p>
     */
    public Location parent;
    
    
    ///////////////////////////////////////
    // access methods for associations
    
    public Collection getSubs() {
        return sub;
    }
    public void addSub(Location location) {
        if (! this.sub.contains(location)) {
            this.sub.add(location);
            location.setParent(this);
        }
    }
    public void removeSub(Location location) {
        boolean removed = this.sub.remove(location);
        if (removed) location.setParent((Location)null);
    }
    
    /**
     *@hibernate.many-to-one
     */
    public Location getParent() {
        return parent;
    }
    public void setParent(Location location) {
        if (this.parent != location) {
            if (this.parent != null) this.parent.removeSub(this);
            this.parent = location;
            if (location != null) location.addSub(this);
        }
    }
    
    
    ///////////////////////////////////////
    // operations
    
    
    /**
     * <p>
     * Does ...
     * </p><p>
     *
     * @return a String with ...
     * </p>
     *@hibernate.property
     */
    public String getName() {
        return name;
    } // end getName
    
    /**
     * <p>
     * Does ...
     * </p><p>
     *
     * </p><p>
     *
     * @param _name ...
     * </p>
     */
    public void setName(String _name) {
        name = _name;
    } // end setName
    
    /**
     * <p>
     * Does ...
     * </p><p>
     *
     * @return a String with ...
     * </p>
     *@hibernate.property
     */
    public String getCode() {
        return code;
    } // end getCode
    
    /**
     * <p>
     * Does ...
     * </p><p>
     *
     * </p><p>
     *
     * @param _code ...
     * </p>
     */
    public void setCode(String _code) {
        code = _code;
    }
    
    /** Setter for property subs.
     * @param subs New value of property subs.
     *
     */
    public void setSubs(Collection subs) {
        sub=subs;
    }
    
    // end setCode
     /** Getter for property id.
     * @return Value of property id.
     * @hibernate.id
     *  generator-class="hilo.long"
     *  type="long"
     */
    public Long getId() {
        return this.id;
    }
    
    /** Setter for property id.
     * @param id New value of property id.
     *
     */
    public void setId(Long id) {
        this.id = id;
    }
} // end Location





