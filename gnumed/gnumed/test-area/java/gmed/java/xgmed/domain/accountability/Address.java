/** Java class "Address.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.accountability;

import java.util.*;

import xgmed.helper.Visitable;
import xgmed.helper.Visitor;

/**
 * <p>
 *
 * </p>
 * @hibernate.class
 *  table="address"
 */
public class Address implements Visitable {
    
    ///////////////////////////////////////
    // attributes
    
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    private String street;
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    private String suburb;
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    private String state;
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    private int postcode;
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    private Long id;
    
    ///////////////////////////////////////
    // associations
    
    /**
     * <p>
     *
     * </p>
     */
    public Collection party = new java.util.HashSet(); // of type Party
    
    
    ///////////////////////////////////////
    // access methods for associations
    
    public Collection getPartys() {
        return party;
    }
    public void addParty(Party party) {
        if (! this.party.contains(party)) {
            this.party.add(party);
            party.setAddress(this);
        }
    }
    public void removeParty(Party party) {
        boolean removed = this.party.remove(party);
        if (removed) party.setAddress((Address)null);
    }
    
    
    ///////////////////////////////////////
    // operations
    
    
    /**
     * <p>
     * Represents ...
     * </p>
     * @hibernate.property
     */
    public String getStreet() {
        return street;
    } // end getStreet
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    public void setStreet(String _street) {
        street = _street;
    } // end setStreet
    
    /**
     * <p>
     * Represents ...
     * </p>
    * @hibernate.property
     */
    public String getSuburb() {
        return suburb;
    } // end getSuburb
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    public void setSuburb(String _suburb) {
        suburb = _suburb;
    } // end setSuburb
    
    /**
     * <p>
     * Represents ...
     * @hibernate.property
     */
    public String getState() {
        return state;
    } // end getState
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    public void setState(String _state) {
        state = _state;
    } // end setState
    
    /**
     * <p>
     * Represents ...
     * </p>
     * @hibernate.property
     */
    public int getPostcode() {
        return postcode;
    } // end getPostcode
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    public void setPostcode(int _postcode) {
        postcode = _postcode;
    } // end setPostcode
    
    /**
     * <p>
     * Represents ...
     * @hibernate.id
     *  generator-class="hilo.long"
     *  type="long"
     */
    public Long getId() {
        return id;
    } // end getId
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    public void setId(Long _id) {
        id = _id;
    }
    
    /** Setter for property partys.
     * @param partys New value of property partys.
     *
     */
    public void setPartys(Collection partys) {
    party = partys;
    }
    
    public void accept(Visitor v) {
        v.visitAddress(this);
    }
    
 // end setId
    
} // end Address





