/*
 * ClinicalRecord.java
 *
 * Created on July 6, 2004, 5:23 AM
 */

package org.gnumed.testweb1.data;

/**
 *
 * @author  sjtan
 */
public interface ClinicalRecord {
    
    /**
     * Getter for property patientId.
     * @return Value of property patientId.
     */
    public Long getPatientId();
    
    /**
     * Setter for property patientId.
     * @param patientId New value of property patientId.
     */
    public void setPatientId(Long patientId);
    
    /**
     * Getter for property healthIssues.
     * @return Value of property healthIssues.
     */
    public HealthIssue[] getHealthIssues();
    
    /**
     * Setter for property healthIssues.
     * @param healthIssues New value of property healthIssues.
     */
    public void setHealthIssues(HealthIssue[] healthIssues);
    
}
