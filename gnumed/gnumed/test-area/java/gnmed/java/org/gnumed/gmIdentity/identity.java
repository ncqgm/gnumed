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

/**
 * <p>
 *
 * </p>
 * @hibernate.class
 */
public class identity {
    
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
    
    ///////////////////////////////////////
    // associations
    
    /**
     * <p>
     *
     * </p>
     */
    public Collection identities_addresses = new java.util.HashSet(); // of type identities_addresses
    /**
     * <p>
     *
     * </p>
     */
    public Collection clin_health_issue = new java.util.HashSet(); // of type clin_health_issue
    /**
     * <p>
     *
     * </p>
     */
    public Collection clin_encounter = new java.util.HashSet(); // of type clin_encounter
    
    public Collection names = new java.util.HashSet(); // of type Names
    ///////////////////////////////////////
    // access methods for associations
    
    /**
     *@hibernate.set
     *  lazy="false"
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
     *      lazy="true"
     *      cascade="all"
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
//    
//    /**
//     *@hibernate.set
//     *  lazy="true"
//     *  cascade="delete"
//     *
//     *@hibernate.collection-key
//     *  column="identity"
//   //  *@hibernate.collection-index
//    // *  column="encounter"
//     *@hibernate.collection-one-to-many
//     *  class="org.gnumed.gmClinical.clin_encounter"
//     */
//    public Collection getClin_encounters() {
//        return clin_encounter;
//    }
//    
//    /** Setter for property clin_encounters.
//     * @param clin_encounters New value of property clin_encounters.
//     *
//     */
//    public void setClin_encounters(Collection clin_encounters) {
//        clin_encounter = clin_encounters;
//    }
//    public void addClin_encounter(clin_encounter _clin_encounter) {
//        if (! this.clin_encounter.contains(_clin_encounter)) {
//            this.clin_encounter.add(_clin_encounter);
//            _clin_encounter.setProvider(this);
//        }
//    }
//    public void removeClin_encounter(clin_encounter _clin_encounter) {
//        boolean removed = this.clin_encounter.remove(_clin_encounter);
//        if (removed) _clin_encounter.setProvider((identity)null);
//    }
//    
    /**
     *
     * @hibernate.set
     *      cascade="save-update"
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
    }
    
   
    // end setId
    
} // end identity





