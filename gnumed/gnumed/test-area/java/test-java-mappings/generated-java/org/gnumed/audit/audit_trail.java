/** Java class "audit_trail.java" generated from Poseidon for UML.
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
public class audit_trail {

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
    private Integer orig_version; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private Date orig_when; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private String orig_by; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private String orig_tableoid; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private String audit_action; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private Date audit_when; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private String audit_by; 

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
    public Integer getOrig_version() {        
        return orig_version;
    } // end getOrig_version        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setOrig_version(Integer _orig_version) {        
        orig_version = _orig_version;
    } // end setOrig_version        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public Date getOrig_when() {        
        return orig_when;
    } // end getOrig_when        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setOrig_when(Date _orig_when) {        
        orig_when = _orig_when;
    } // end setOrig_when        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public String getOrig_by() {        
        return orig_by;
    } // end getOrig_by        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setOrig_by(String _orig_by) {        
        orig_by = _orig_by;
    } // end setOrig_by        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public String getOrig_tableoid() {        
        return orig_tableoid;
    } // end getOrig_tableoid        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setOrig_tableoid(String _orig_tableoid) {        
        orig_tableoid = _orig_tableoid;
    } // end setOrig_tableoid        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public String getAudit_action() {        
        return audit_action;
    } // end getAudit_action        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setAudit_action(String _audit_action) {        
        audit_action = _audit_action;
    } // end setAudit_action        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public Date getAudit_when() {        
        return audit_when;
    } // end getAudit_when        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setAudit_when(Date _audit_when) {        
        audit_when = _audit_when;
    } // end setAudit_when        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public String getAudit_by() {        
        return audit_by;
    } // end getAudit_by        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setAudit_by(String _audit_by) {        
        audit_by = _audit_by;
    } // end setAudit_by        

} // end audit_trail





