/*
 * identity_role.java
 *
 * Created on 18 August 2003, 01:48
 */

package org.gnumed.gmIdentity;
import java.util.*;
/**
 *
 * @author  syan
 * @hibernate.class
 */
public class identity_role {
    
    /** Holds value of property name. */
    private String name;
    
    /** Holds value of property superTypes. */
    private Collection superTypes = new HashSet();
    
    /** Holds value of property subTypes. */
    private Collection subTypes = new HashSet();
    
    /** Holds value of property id. */
    private Integer id;
    
    /** Creates a new instance of identity_role */
    public identity_role() {
    }
    
    /** Getter for property name.
     * @return Value of property name.
     *
     * @hibernate.property
     */
    public String getName() {
        return this.name;
    }
    
    /** Setter for property name.
     * @param name New value of property name.
     *
     */
    public void setName(String name) {
        this.name = name;
    }
    
    /** Getter for property superTypes.
     * @return Value of property superTypes.
     * @hibernate.set
     *      table="link_role_identity"
     *      inverse="true"
     *      lazy="true"
     *      cascade="save-update"
     * @hibernate.collection-key
     *  column="subtype"
     * @hibernate.collection-many-to-many
     *      column="supertype"
     *      class="org.gnumed.gmIdentity.identity_role"
     */
    public Collection getSuperTypes() {
        return this.superTypes;
    }
    
    /** Setter for property superTypes.
     * @param superTypes New value of property superTypes.
     *
     */
    public void setSuperTypes(Collection superTypes) {
        this.superTypes = superTypes;
    }
    
    
    public void addSuperType( identity_role role) {
        try {
            if (role == null || isSubType(role) || role.isSubType(this) ||  getSuperTypes().contains(role) )
                return ;
             this.getSuperTypes().add(role);
             role.addSubType(this);
            
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    public void removeSuperType( identity_role role) {
        if (role != null) {
            role.removeSubType( this);
            getSubTypes().remove(role);
        }
    }
    /** Getter for property subTypes.
     * @return Value of property subTypes.
     *
     *
     * @hibernate.set
     *      table="link_role_role"
     *      inverse="false"
     *      lazy="true"
     *      cascade="save-update"
     * @hibernate.collection-key
     *  column="supertype"
     * @hibernate.collection-many-to-many
     *      column="subtype"
     *      class="org.gnumed.gmIdentity.identity_role"
     *
     */
    public Collection getSubTypes() {
        return this.subTypes;
    }
    
    /** Setter for property subTypes.
     * @param subTypes New value of property subTypes.
     *
     */
    public void setSubTypes(Collection subTypes) {
        this.subTypes = subTypes;
    }
    
    public void addSubType( identity_role role) {
         if (role == null || isSubType(role) || role.isSubType(this) ||  getSubTypes().contains(role) )
                return ;
             this.getSubTypes().add(role);
             role.addSuperType(this);
    }
    
    public void removeSubType( identity_role role) {
        if (role != null) {
            role.removeSuperType(this);
            this.getSubTypes().remove(role);
        }
    }
    
    public boolean isSubType( identity_role role) {
        Iterator j = getSubTypes().iterator();
        while (j.hasNext()) {
            identity_role role2 = (identity_role) j.next();
            if (role2.equals(role) )
                return true;
            if ( role2.isSubType(role) )
                return true;
        }
        return false;
    }
    
    /** Getter for property id.
     * @return Value of property id.
     *
     * @hibernate.id
     *  generator-class="hilo"
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
    
    public String toString() {
        return getName();
    }
    
}
