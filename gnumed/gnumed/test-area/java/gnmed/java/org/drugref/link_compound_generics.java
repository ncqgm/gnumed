/** Java class "link_compound_generics.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.drugref;

import java.util.*;

/**
 * <p>
 *
 * </p>
 * @hibernate.class
 *  mutable="false"
 */
public class link_compound_generics {
    
    ///////////////////////////////////////
    // associations
    
    /**
     * <p>
     *
     * </p>
     */
    public drug_element component;
    /**
     * <p>
     *
     * </p>
     */
    public drug_element compound;
    
    /** Holds value of property audit_id. */
    private Integer audit_id;
    
    ///////////////////////////////////////
    // access methods for associations
    /**
     *@hibernate.many-to-one
     *     column="id_component"
     */
    public drug_element getComponent() {
        return component;
    }
    public void setComponent(drug_element _drug_element) {
        if (this.component != _drug_element) {
            if (this.component != null) this.component.removeToCompound(this);
            this.component = _drug_element;
            if (_drug_element != null) _drug_element.addToCompound(this);
        }
    }
    /**
     *@hibernate.many-to-one
     *   column="id_compound"
     */
    
    public drug_element getCompound() {
        return compound;
    }
    public void setCompound(drug_element _drug_element) {
        if (this.compound != _drug_element) {
            if (this.compound != null) this.compound.removeToComponent(this);
            this.compound = _drug_element;
            if (_drug_element != null) _drug_element.addToComponent(this);
        }
    }
    
    /** Getter for property audit_id.
     * @return Value of property audit_id.
     *
     * @hibernate.id
     *  generator-class="assigned"
     */
    public Integer getAudit_id() {
        return this.audit_id;
    }
    
    /** Setter for property audit_id.
     * @param audit_id New value of property audit_id.
     *
     */
    public void setAudit_id(Integer audit_id) {
        this.audit_id = audit_id;
    }
    
} // end link_compound_generics





