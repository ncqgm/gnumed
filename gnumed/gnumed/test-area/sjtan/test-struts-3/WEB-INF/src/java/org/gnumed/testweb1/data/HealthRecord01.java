/*
 * HealthRecord01.java
 *
 * Created on September 13, 2004, 11:08 PM
 */

package org.gnumed.testweb1.data;

/**
 *
 * @author  sjtan
 */
public interface HealthRecord01 {
    HealthSummary01 getHealthSummary();
    Long getIdentityId();
    HealthIssue[] getHealthIssues();
    HealthIssue[] getResolvedHealthIssue();
    void addHealthIssue( HealthIssue hi);
    int getHealthIssueCount();
    HealthIssue getHealthIssue(int index); 
    
    Vaccination[] getVaccinations();
    void addVaccination(Vaccination vacc);
    int getVaccinationCount();
    Vaccination getVaccination(int index);
    
    Allergy[] getAllergys();
    Allergy getAllergy(int index);
    int getAllergyCount();
    void addAllergy(Allergy allergy);
    
    
    Medication[] getCurrentMedications();
    Medication[] getOldMedications();
    
    Medication getMedication( int index);
    int getCurrentMedicationCount();
    
    ClinicalEncounter[] getEncounters();
    
}
