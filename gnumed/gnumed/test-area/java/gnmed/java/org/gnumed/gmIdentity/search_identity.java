/*
 * search_identity.java
 *
 * Created on 8 September 2003, 00:38
 */

package org.gnumed.gmIdentity;
import org.gnumed.gmGIS.*;
import java.util.*;

/**
 *
 * @author  syan
 *
 *  @hibernate.class
 *      table="identity"
 *      mutable="false"
 */
public class search_identity implements identifiable {
    private  Long id;
    private Collection names;
    private String karyotype;
    private Date dob;
    private Collection identities_addresses;
    
    /**
     *@hibernate.set
     *  inverse="true"
     *  cascade="none"
     * @hibernate.collection-key
     *  column="identity"
     *@hibernate.collection-one-to-many
     *  class="org.gnumed.gmGIS.identities_addresses"
     */
    public Collection getIdentities_addressess() {
        return identities_addresses;
    }
    /** Setter for property identities_addressess.
     * @param identities_addressess New value of property identities_addressess.
     *
     */
    
    public void setIdentities_addressess(Collection identities_addressess)
    {identities_addresses= identities_addressess;
    }
    
     /**
     * <p>
     * Represents ...
     * </p>
     * @hibernate.property
     */
    public Date getDob() {
        return dob;
    } // end getDob
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    public void setDob(Date _dob) {
        dob = _dob;
    } // end setDob
    
     /**
     * <p>
     * Represents ...
     * </p>
     * @hibernate.property
     */
    public String getKaryotype() {
        return karyotype;
    } // end getKaryotype
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    public void setKaryotype(String _karyotype) {
        karyotype = _karyotype;
    } // end setKaryotype
    
    
    
    /**
     *
     * @hibernate.set
     *      cascade="none"
     *      inverse="true"
     *      lazy="false"
     * @hibernate.collection-key
     *  column="identity"
     * @hibernate.collection-one-to-many
     *      class="org.gnumed.gmIdentity.Names"
     */
    public Collection getNamess() {
        return names;
    }
    /** Setter for property namess.
     * @param namess New value of property namess.
     *
     */
    public void setNamess(Collection namess) {names = namess;}
    
    
    /**
     * <p>
     * Represents ...
     * </p>
     *  @hibernate.id
     *      generator-class="hilo"
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
    
    /** Creates a new instance of search_identity */
    public search_identity() {
        
    }
    
    public String toString() {
        return identity.toString(this);   
    }
    
}
