/** Java class "identity.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.gnumed.gmIdentity;

import java.util.*;
import java.util.Date;
import org.gnumed.gmClinical.clin_encouonter;
import org.gnumed.gmClinical.clin_health_issue;

/**
 * <p>
 * 
 * </p>
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
    public Collection clin_health_issue = new java.util.HashSet(); // of type clin_health_issue
/**
 * <p>
 * 
 * </p>
 */
    public Collection clin_encouonter = new java.util.HashSet(); // of type clin_encouonter


   ///////////////////////////////////////
   // access methods for associations

    public Collection getClin_health_issues() {
        return clin_health_issue;
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
    public Collection getClin_encouonters() {
        return clin_encouonter;
    }
    public void addClin_encouonter(clin_encouonter _clin_encouonter) {
        if (! this.clin_encouonter.contains(_clin_encouonter)) {
            this.clin_encouonter.add(_clin_encouonter);
            _clin_encouonter.setProvider(this);
        }
    }
    public void removeClin_encouonter(clin_encouonter _clin_encouonter) {
        boolean removed = this.clin_encouonter.remove(_clin_encouonter);
        if (removed) _clin_encouonter.setProvider((identity)null);
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 */
    public String getPupic() {        
        return pupic;
    } // end getPupic        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setPupic(String _pupic) {        
        pupic = _pupic;
    } // end setPupic        

/**
 * <p>
 * Represents ...
 * </p>
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

} // end identity





