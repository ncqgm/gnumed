/*
 * HealthRecordImpl01.java
 *
 * Created on September 13, 2004, 11:16 PM
 */

package org.gnumed.testweb1.data;
import java.util.Set;
import java.util.TreeSet;
import java.util.ArrayList;
import java.util.List;
import java.util.Arrays;
import java.util.Collections;

/**
 *
 * @author  sjtan
 */
public class HealthRecordImpl01 implements HealthRecord01 {
    HealthSummary01 summary;
    Set allergySet = new TreeSet();
    Set healthIssueSet = new TreeSet();
     Set medicationSet = new TreeSet();
      Set oldMedicationSet = new TreeSet();
    
    List vaccinations = new ArrayList();
    Set encounterSet = new TreeSet();
    Long id;
    
    
    /** Creates a new instance of HealthRecordImpl01 */
    public HealthRecordImpl01( HealthSummary01 summary) {
    this.summary = summary;
    }
    
    public void addAllergy(Allergy allergy) {
        allergySet.add(allergy);
    }
    
    public void addHealthIssue(HealthIssue hi) {
        healthIssueSet.add(hi);
    }
    
    public void addVaccination(Vaccination vacc) {
        vaccinations.add(vacc);
    }
    
    public Allergy[] getAllergys() {
        return (Allergy[]) Collections
        .unmodifiableSet(allergySet)
        .toArray(new Allergy[0] );
        
    }
    
    public Medication[] getCurrentMedications() {
        return (Medication[] ) Collections
        .unmodifiableSet(medicationSet)
        .toArray(new Medication[0]);
    }
    
    public int getCurrentMedicationCount() {
        return medicationSet.size();
        
    }
    
    public ClinicalEncounter[] getEncounters() {
         return (ClinicalEncounter[] ) Collections
        .unmodifiableSet(encounterSet)
        .toArray(new ClinicalEncounter[0]);
    }
    
    public HealthIssue getHealthIssue(int index) {
        return (HealthIssue) healthIssueSet.toArray()[index];
    }
    
    public int getHealthIssueCount() {
        return healthIssueSet.size();
    }
    
    public HealthIssue[] getHealthIssues() {
         return (HealthIssue[] ) Collections
        .unmodifiableSet(healthIssueSet)
        .toArray(new HealthIssue[0]);
    }
    
    public Medication getMedication(int index) {
        return (Medication) medicationSet.toArray()[index];
    }
    
    public Medication[] getOldMedications() {
          return (Medication[] ) Collections
        .unmodifiableSet(oldMedicationSet)
        .toArray(new Medication[0]);
    }
    
    public HealthIssue[] getResolvedHealthIssue() {
        return null;
    }
    
    public Vaccination[] getVaccinations() {
        return (Vaccination[] ) Collections
        .unmodifiableList(vaccinations)
        .toArray(new Vaccination[0]);
    }
   
    public Allergy getAllergy(int index) {
         return (Allergy) allergySet.toArray()[index];
    }    
    
    public int getAllergyCount() {
        return allergySet.size();
    }
    
    public int getVaccinationCount() {
        return vaccinations.size();
    }
    
    public Vaccination getVaccination(int index) {
         return (Vaccination) vaccinations.toArray()[index];
    }
    
    public Long getIdentityId() {
        return id;
    }
    
    public HealthSummary01 getHealthSummary() {
        return summary;
    }
    
}
