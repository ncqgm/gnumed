/*
 * Created on 27-Feb-2005
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
package org.gnumed.testweb1.forms;

import org.apache.struts.validator.ValidatorForm;

/**
 * @author sjtan
 *
 * TODO To change the template for this generated type comment go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
public class BaseClinicalUpdateForm extends ValidatorForm {
    private Integer patientId;

    /**
     * Getter for property patientId.
     * @return Value of property patientId.
     */
    public Integer getPatientId() {
        return this.patientId;
    }
    
    /**
     * Setter for property patientId.
     * @param patientId New value of property patientId.
     */
    public void setPatientId(Integer patientId) {
        this.patientId = patientId;
    }

}
