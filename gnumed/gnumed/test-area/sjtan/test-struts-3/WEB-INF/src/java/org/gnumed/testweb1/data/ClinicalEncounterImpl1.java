/*
 * ClinicalEncounterImpl1.java
 *
 * Created on September 18, 2004, 3:51 PM
 */

package org.gnumed.testweb1.data;
import java.util.Date;
import java.util.List;

/**
 *
 * @author  sjtan
 */
public class ClinicalEncounterImpl1 implements ClinicalEncounter {
    
    java.util.Date started, affirmed;
    String type, description;
    Long id;
    String location;
    List narratives, medications, vaccinations, allergys;
    Vitals vitals;
    
    /** Creates a new instance of ClinicalEncounterImpl1 */
    public ClinicalEncounterImpl1() {
        started = new Date();
        affirmed = new Date();
        
        createCollections();
        
        
    }
    
    
    public ClinicalEncounterImpl1( int nn, int nm, int nv, int na, DataObjectFactory f) {
        this();
        load( narratives, nn, f.createClinNarrative() );
        load( medications, nm, f.createMedication() );
        load( vaccinations, nv, f.createVaccination() );
        //load( allergys, na, f.createAllergy() );
    }
    
    private void load(List l, int n, Object o) {
        System.err.println("l , n, o" + l + n + o);
        try {
            for (int i = 0; i < n; ++i ) {
                l.add( o.getClass().newInstance());
            }
            
        } catch (Exception e) {
            e.printStackTrace();
        }
        
    }
    
    private void createCollections() {
        narratives = new java.util.ArrayList();
        medications = new java.util.ArrayList();
        vaccinations = new java.util.ArrayList();
        allergys = new java.util.ArrayList();
    }
    
    
    public Allergy getAllergy(int index) {
        return (Allergy) allergys.get(index);
    }
    
    public String getDescription() {
        return description;
    }
    
    public String getEncounterType() {
        return type;
    }
    
    public Long getId() {
        return id;
    }
    public java.util.Date getLastAffirmed() {
        return affirmed;
    }
    
    public Medication getMedication(int index) {
        return (Medication) medications.get(index);
    }
    
    public java.util.Date getStarted() {
        return started;
    }
    
    public Vaccination getVaccination(int index) {
        return (Vaccination) vaccinations.get(index);
        
    }
    
    public void setAllergy(int index, Allergy allergy) {
        set(allergys, index, allergy);
    }
    
    public void setDescription(String description) {
        this.description = description;
    }
    
    public void setEncounterType(String encounterType) {
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public void setLastAffirmed(java.util.Date lastAffirmed) {
        this.affirmed = lastAffirmed;
    }
    
    public void setMedication(int index, Medication medication) {
        set(medications, index, medication);
    }
    
    /** set operation means if index is larger than current collection,
     *  an append instead of a replace will be done
     */
    public void set( List l, int index, Object o) {
        if (index >= l.size()) {
            l.add(o);
        }
        else {
            Object old = l.remove(index);
            l.add(index, o);
        }
        
    }
    
    public void setStarted(java.util.Date started) {
        this.started = started;
    }
    
    public void setVaccination(int index, Vaccination vaccination) {
        set(vaccinations, index, vaccination);
    }
    
    public String getLocation() {
        return location;
    }
    
    public void setLocation(String location) {
        this.location = location;
    }
    
    public ClinNarrative getNarrative(int index) {
        return (ClinNarrative) narratives.get(index);
    }
    
    public void setNarrative(int index, ClinNarrative narrative) {
        narrative.setEncounter(this);
        set( narratives, index, narrative);
    }
    
    public List getNarratives() {
        return narratives;
    }
    
    public void sortRootItems(final java.util.Comparator comparator) {
        java.util.Collections.sort( narratives, comparator);
        
    }
    
    public Vitals getVitals() {
        return vitals;
    }
    
    public void setVitals(Vitals vitals) {
        this.vitals = vitals;
    }
    
}
