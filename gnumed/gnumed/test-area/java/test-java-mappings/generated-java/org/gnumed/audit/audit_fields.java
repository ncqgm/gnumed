/** Java class "audit_fields.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.gnumed.audit;

import java.util.*;
import java.util.Date;

/**
 * <p>
 * 
 * </p>
 */
public class audit_fields {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private Long pk_audit; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private Integer row_version; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private Date modified_when; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private String modified_by; 

  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 */
    public Long getPk_audit() {        
        return pk_audit;
    } // end getPk_audit        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setPk_audit(Long _pk_audit) {        
        pk_audit = _pk_audit;
    } // end setPk_audit        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public Integer getRow_version() {        
        return row_version;
    } // end getRow_version        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setRow_version(Integer _row_version) {        
        row_version = _row_version;
    } // end setRow_version        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public Date getModified_when() {        
        return modified_when;
    } // end getModified_when        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setModified_when(Date _modified_when) {        
        modified_when = _modified_when;
    } // end setModified_when        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public String getModified_by() {        
        return modified_by;
    } // end getModified_by        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setModified_by(String _modified_by) {        
        modified_by = _modified_by;
    } // end setModified_by        

} // end audit_fields





