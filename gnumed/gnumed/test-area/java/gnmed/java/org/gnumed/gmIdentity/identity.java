/** Java class "identity.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.gnumed.gmIdentity;


import java.util.*;
import java.util.Date;
import org.gnumed.gmClinical.clin_encounter;
import org.gnumed.gmClinical.clin_health_issue;
import org.gnumed.gmGIS.identities_addresses;
import org.gnumed.gmClinical.script_drug;
import org.gnumed.gmClinical.clin_attribute;
import org.gnumed.gmClinical.category_attribute;
import org.gnumed.gmClinical.category_type;
import org.drugref.product;
// for the find function.
import org.gnumed.gmGIS.address_type;
import org.gnumed.gmGIS.address;
import org.gnumed.gmGIS.enum_telephone_role;
import org.gnumed.gmGIS.telephone;
/**
 * <p>
 *
 * </p>
 * @hibernate.class
 *  proxy="org.gnumed.gmIdentity.identity"
 */
public class identity {
    
    
    ///////////////////////////////////////
    // attributes
    
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    private Long id;
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    private String pupic;
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    private String gender;
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    private String karyotype;
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    private Date dob;
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    private String cob;
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    private Date deceased;
    
    
    private Collection clin_attribute = new java.util.HashSet(); // of type clin_attribute
    
    
    ///////////////////////////////////////
    // associations
    
    /**
     * <p>
     *
     * </p>
     */
    private Collection identities_addresses = new java.util.HashSet(); // of type identities_addresses
    /**
     * <p>
     *
     * </p>
     */
    private Collection clin_health_issue = new java.util.HashSet(); // of type clin_health_issue
    /**
     * <p>
     *
     * </p>
     */
    private Collection clin_encounter = new java.util.HashSet(); // of type clin_encounter
    
    private Collection names = new java.util.HashSet(); // of type Names
    Collection script_drug = new java.util.HashSet();
    
    /** Holds value of property mobile. */
    private org.gnumed.gmGIS.telephone mobile;
    private Collection social_identity = new java.util.HashSet(); // of type social_identity
    
   
    /** Holds value of property persister. */
    private Object persister;
    
    /** Holds value of property roles. */
    private Collection roles = new java.util.HashSet();
    
    
    
    private StringBuffer sb = new StringBuffer();
    private static java.text.Format dateFormat= java.text.DateFormat.getDateInstance( java.text.DateFormat.SHORT);
    
    
    
    
    
    /**
     *@hibernate.set
     *    inverse="true"
     *    cascade="all"
     *@hibernate.collection-key
     *    column="identity"
     *@hibernate.collection-one-to-many
     *    class="org.gnumed.gmIdentity.social_identity"
     */
    public Collection getSocial_identitys() {
        return social_identity;
    }
    
    /** Setter for property social_identitys.
     * @param social_identitys New value of property social_identitys.
     *
     */
    public void setSocial_identitys(Collection social_identitys) {}
    
    public void addSocial_identity(social_identity _social_identity) {
        if (! this.social_identity.contains(_social_identity)) {
            this.social_identity.add(_social_identity);
            _social_identity.setIdentity(this);
        }
    }
    public void removeSocial_identity(social_identity _social_identity) {
        boolean removed = this.social_identity.remove(_social_identity);
        if (removed) _social_identity.setIdentity((identity)null);
    }
    
    public social_identity findSocialIdentityByEnum(enum_social_id enum) {
        Iterator j = getSocial_identitys().iterator();
        while ( j.hasNext()) {
            social_identity id = (social_identity)j.next();
            if (id.getEnum_social_id().equals(enum))
                return id;
        }
        return null;
    }
    ///////////////////////////////////////
    // access methods for associations
    
    /**
     *@hibernate.set
     *  lazy="false"
     *  inverse="true"
     *  cascade="save-update"
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
    
    public void addIdentities_addresses(identities_addresses _identities_addresses) {
        if (! this.identities_addresses.contains(_identities_addresses)) {
            this.identities_addresses.add(_identities_addresses);
            _identities_addresses.setIdentity(this);
        }
    }
    public void removeIdentities_addresses(identities_addresses _identities_addresses) {
        boolean removed = this.identities_addresses.remove(_identities_addresses);
        if (removed) _identities_addresses.setIdentity((identity)null);
    }
    
    /**
     *@hibernate.set
     *      lazy="false"
     *      cascade="all"
     * //     *      inverse="true"
     *@hibernate.collection-key
     *      column="identity"
     *@hibernate.collection-one-to-many
     *      class="org.gnumed.gmClinical.clin_health_issue"
     */
    public Collection getClin_health_issues() {
        return clin_health_issue;
    }
    
    /** Setter for property clin_health_issues.
     * @param clin_health_issues New value of property clin_health_issues.
     *
     */
    public void setClin_health_issues(Collection clin_health_issues) {
        clin_health_issue = clin_health_issues;
    }
    
    public void addClin_health_issue(clin_health_issue _clin_health_issue) {
        if (! this.clin_health_issue.contains(_clin_health_issue)) {
            this.clin_health_issue.add(_clin_health_issue);
            _clin_health_issue.setIdentity(this);
        }
    }
    public void removeClin_health_issue(clin_health_issue _clin_health_issue) {
        boolean removed = this.clin_health_issue.remove(_clin_health_issue);
        if (removed) _clin_health_issue.setIdentity((identity)null);
    }
    
    /**
     *@hibernate.set
     *  lazy="false"
     *  cascade="all"
     *  inverse="true"
     *@hibernate.collection-key
     *  column="identity"
     *@hibernate.collection-one-to-many
     *  class="org.gnumed.gmClinical.clin_encounter"
     */
    public Collection getClin_encounters() {
        return clin_encounter;
    }
    
    /** Setter for property clin_encounters.
     * @param clin_encounters New value of property clin_encounters.
     *
     */
    public void setClin_encounters(Collection clin_encounters) {
        clin_encounter = clin_encounters;
    }
    public void addClin_encounter(clin_encounter _clin_encounter) {
        if (! this.clin_encounter.contains(_clin_encounter)) {
            this.clin_encounter.add(_clin_encounter);
            _clin_encounter.setIdentity(this);
        }
    }
    public void removeClin_encounter(clin_encounter _clin_encounter) {
        boolean removed = this.clin_encounter.remove(_clin_encounter);
        if (removed) _clin_encounter.setIdentity((identity)null);
    }
    
    /**
     *
     * @hibernate.set
     *      cascade="all"
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
    
    
    
    public void addNames(Names names) {
        if (! this.names.contains(names)) {
            this.names.add(names);
            names.setIdentity(this);
        }
    }
    public void removeNames(Names names) {
        boolean removed = this.names.remove(names);
        if (removed) names.setIdentity((identity)null);
    }
    
    /**
     *@hibernate.set
     *  cascade="all"
     *  lazy="false"
     * @hibernate.collection-key
     *  column="identity"
     * @hibernate.collection-one-to-many
     *  class="org.gnumed.gmClinical.script_drug"
     */
    public Collection getScript_drugs() {
        return script_drug;
    }
    public void addScript_drug(script_drug _script_drug) {
        if (! this.script_drug.contains(_script_drug)) {
            this.script_drug.add(_script_drug);
            _script_drug.setIdentity(this);
        }
    }
    public void removeScript_drug(script_drug _script_drug) {
        boolean removed = this.script_drug.remove(_script_drug);
        if (removed) _script_drug.setIdentity((identity)null);
    }
    /** Setter for property script_drugs.
     * @param script_drugs New value of property script_drugs.
     *
     */
    public void setScript_drugs(Collection script_drugs) {
        script_drug = script_drugs;
    }
    
    
    ///////////////////////////////////////
    // operations
    
    
    /**
     * <p>
     * Represents ...
     * </p>
     * @hibernate.property
     */
    public String getPupic() {
        return pupic;
    } // end getPupic
    
    /**
     * <p>
     * Represents ...
     * </p>
     *
     */
    public void setPupic(String _pupic) {
        pupic = _pupic;
    } // end setPupic
    
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
    public String getCob() {
        return cob;
    } // end getCob
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    public void setCob(String _cob) {
        cob = _cob;
    } // end setCob
    
    /**
     * <p>
     * Represents ...
     * </p>
     *  @hibernate.property
     */
    public Date getDeceased() {
        return deceased;
    } // end getDeceased
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    public void setDeceased(Date _deceased) {
        deceased = _deceased;
    } // end setDeceased
    
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
    
    /** Getter for property mobile.
     * @return Value of property mobile.
     *
     *@hibernate.many-to-one
     *  cascade="all"
     */
    public org.gnumed.gmGIS.telephone getMobile() {
        return this.mobile;
    }
    
    /** Setter for property mobile.
     * @param mobile New value of property mobile.
     *
     */
    public void setMobile(org.gnumed.gmGIS.telephone mobile) {
        this.mobile = mobile;
    }
    
    /**
     *@hibernate.set
     *  cascade="all"
     *@hibernate.collection-key
     *  column="identity"
     *@hibernate.collection-one-to-many
     *  class="org.gnumed.gmClinical.clin_attribute"
     */
    public Collection getClin_attributes() {
        return clin_attribute;
    }
    public void addClin_attribute(clin_attribute _clin_attribute) {
        if (! this.clin_attribute.contains(_clin_attribute)) {
            this.clin_attribute.add(_clin_attribute);
            _clin_attribute.setIdentity(this);
        }
    }
    public void removeClin_attribute(clin_attribute _clin_attribute) {
        
        boolean removed = this.clin_attribute.remove(_clin_attribute);
        if (removed) _clin_attribute.setIdentity((identity)null);
    }
    
    /** Setter for property clin_attributes.
     * @param clin_attributes New value of property clin_attributes.
     *
     */
    public void setClin_attributes(Collection clin_attributes) {
        clin_attribute = clin_attributes;
    }
    
    public category_attribute findCategoryAttribute(final category_type type) {
        Iterator i = getClin_attributes().iterator();
        while (i.hasNext()) {
            Object o = i.next();
            if ( ! ( o instanceof category_attribute))
                continue;
            category_attribute attr = (category_attribute) o;
            if (attr.getCategory().getCategory_type().equals(type))
                return attr;
        }
        return null;
    }
    
    
    /** this method will create a identities_addresses association
     *  if there is not one found existing for the address type for this identity.
     *  Otherwise, it will replace the address referenced and returns the
     *  old address.
     *
     * @returns the old address, if there was one for the address_type and identity.
     *
     */
    public  address setIdentityAddress( address_type  type, address a) {
        identities_addresses ia = findIdentityAddressByAddressType(type);
        if (ia == null) {
            ia = new identities_addresses();
            ia.setAddress_type(type);
            
            ia.setAddress(a);
            addIdentities_addresses(ia);
            
            return null;
        }
        
        address old = ia.getAddress();
        ia.setAddress(a);
        return old;
        
    }
    
    public identities_addresses findIdentityAddressByAddressType(final address_type a) {
        Iterator i = getIdentities_addressess().iterator();
        while (i.hasNext()) {
            identities_addresses ia = (identities_addresses) i.next();
            if (a.equals(ia.getAddress_type())  )
                return ia;
        }
        return null;
    }
    
    public Names findNames(int n) {
        if (getNamess().size() < n)
            return new Names();
        
        Names names = null;
        Iterator j = getNamess().iterator();
        for (int i = 0;j.hasNext() && i < n + 1; ++i)
            names = (Names) j.next();
        return names;
    }
    
    /** find the first telephone by role
     */
    public telephone findTelephoneByRole( enum_telephone_role role) {
        // temporary hack
        if ( role.getRole().equals( ResourceBundle.getBundle("SummaryTerms").getString("mobile")))
            return getMobile();
        Iterator i = getIdentities_addressess().iterator();
        while (i.hasNext()) {
            identities_addresses ia = (identities_addresses)i.next();
            if (ia.getAddress() == null)
                continue;
            if (ia.getAddress().findTelephone(role) != null )
                return ia.getAddress().findTelephone(role);
        }
        return telephone.NULL;
    }
    
    
    
    
    
    
    
    public script_drug findDrugScriptWithProduct(final product product, Double qty) throws Exception {
        Iterator i = getScript_drugs().iterator();
        long smallest = Long.MAX_VALUE;
        script_drug chosen = null;
        while (i.hasNext()) {
            script_drug sd = (script_drug) i.next();
            
            // if points to same product
            if (sd.getPackage_size().getProduct() == product)
                return sd;
            // if pretty close
            try {
                long diff = Math.abs(Double.doubleToLongBits(qty.doubleValue()) - Double.doubleToLongBits(sd.getQty().doubleValue()));
                if (sd.getPackage_size().getProduct().equals(product) &&  diff < smallest) {
                    smallest = diff;
                    chosen = sd;
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        return chosen;
    }
    
    
    
    
    
    public String toString() {
        sb.delete(0, sb.length());
        Names n =(Names) getNamess().iterator().next();
        Iterator i =  getIdentities_addressess().iterator();
        
        identities_addresses ia = null;
        if (i.hasNext())
            ia =(identities_addresses )i.next();
        
        if (n != null) {
            sb.append(n.toString());
            sb.append(", ").
            append("XY".equals(getKaryotype()) ? "male ": "female ");
            sb.
            append( getDob() != null ?  dateFormat.format(getDob()) : "");
            if (ia != null && ia.getAddress() != null)
                sb.append(" : ").append(ia.getAddress().getNumber()).
                append(",").append(ia.getAddress().getStreet().getName()).
                append(",").append(ia.getAddress().getStreet().getUrb().getName()).
                append(",").append(ia.getAddress().getStreet().getUrb().getState().getName()).
                append(",").
                append(ia.getAddress().getStreet().getUrb().getPostcode()).
                append(".");
            
            return sb.toString();
        }
        
        return super.toString();
    }
    
    /** Getter for property persister.
     * @return Value of property persister.
     *
     */
    public Object getPersister() {
        return this.persister;
    }
    
    /** Setter for property persister.
     * @param persister New value of property persister.
     *
     */
    public void setPersister(Object persister) {
        this.persister = persister;
    }
    
    /** Getter for property role.
     * @return Value of property role.
     * @hibernate.set
     *      cascade="all"
     *      inverse="false"
     * @hibernate.collection-key
     *      column="identity"
     * @hibernate.collection-one-to-many
     *      class="org.gnumed.gmIdentity.identity_role_info"
     */
    public Collection getRoles() {
        return this.roles;
    }
    
    /** Setter for property role.
     * @param role New value of property role.
     *
     */
    public void setRoles(Collection roles) {
        this.roles = roles;
    }
    
    public void addRole(identity_role_info role) {
        if (getRoles().contains(role))
            return;
        getRoles().add(role);
    }
    
    public void removeRole(identity_role_info role) {
        if (getRoles().contains(role))
            return;
        getRoles().remove(role);
    }
    
    // end setId
    
} // end identity





