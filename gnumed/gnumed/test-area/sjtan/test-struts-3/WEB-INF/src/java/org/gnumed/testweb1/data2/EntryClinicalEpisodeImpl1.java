/*
 * Created on 17-Feb-2005
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
package org.gnumed.testweb1.data2;

import java.util.Date;
import java.util.List;

import org.gnumed.testweb1.data.Allergy;
import org.gnumed.testweb1.data.ClinNarrative;
import org.gnumed.testweb1.data.ClinRootItem;
import org.gnumed.testweb1.data.ClinicalEpisode;
import org.gnumed.testweb1.data.HealthIssue;
import org.gnumed.testweb1.data.Medication;
import org.gnumed.testweb1.data.Vaccination;
import org.gnumed.testweb1.data.Vitals;

/**
 * @author sjtan
 *
 * TODO To change the template for this generated type comment go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
public class EntryClinicalEpisodeImpl1 implements EntryClinicalEpisode {
    HealthIssue healthIssue;
    ClinNarrative describingNarrative;
    ClinicalEpisode lastEpisode;
    List narratives, vitals, medications, allergies, vaccinations;
    private Long id;
    private Date modified_when;
    private List allergys;
    private boolean closingLastEpisode;
    private boolean openLastEpisode;
    private boolean lastEpisodeOpenable;
    private boolean lastEpisodeCloseable;
    private boolean closed;
    
    
    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEpisode#setHealthIssue(org.gnumed.testweb1.data.HealthIssue)
     */
    public void setHealthIssue(HealthIssue issue) {
        healthIssue = issue;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEpisode#getHealthIssue()
     */
    public HealthIssue getHealthIssue() {
        // TODO Auto-generated method stub
        return healthIssue;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#setNarratedDescription(boolean)
     */
    public void setNarratedDescription(boolean narrated) {
        // TODO Auto-generated method stub
        
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#isNarratedDescription()
     */
    public boolean isNarratedDescription() {
        // TODO Auto-generated method stub
        return false;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#getDefiningNarrative()
     */
    public ClinNarrative getDefiningNarrative() {
        return describingNarrative;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#setDefiningNarrative(org.gnumed.testweb1.data.ClinNarrative)
     */
    public void setDefiningNarrative(ClinNarrative narrative) {
   
        describingNarrative = narrative;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#setClinNarrative(int, org.gnumed.testweb1.data.ClinNarrative)
     */
    public void setClinNarrative(int i, ClinNarrative n) {
       
        if (i < narratives.size()) {
            narratives.set(i, n);
        } else {
           narratives.add(n);
        }
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#getClinNarrative(int)
     */
    public ClinNarrative getClinNarrative(int i) {
        return (ClinNarrative) narratives.get(i);
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#getClinNarratives()
     */
    public List getClinNarratives() {
        return narratives;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#setClinNarratives(java.util.List)
     */
    public void setClinNarratives(List l) {
       narratives = l;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#setVitals(java.util.List)
     */
    public void setVitals(List l) {
        vitals = l;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#setVital(int, org.gnumed.testweb1.data.Vitals)
     */
    public void setVital(int i, Vitals v) {
        if (i < vitals.size() ) {
            vitals.set(i, v);
        } else {
            vitals.add(v);
        }

    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#getVital(int)
     */
    public Vitals getVital(int i) {
        return (Vitals)vitals.get(i);
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#getVitals()
     */
    public List getVitals() {
      
        return vitals;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#setMedications(java.util.List)
     */
    public void setMedications(List l) {
        medications = l;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#setMedication(int, org.gnumed.testweb1.data.Medication)
     */
    public void setMedication(int i, Medication med) {
        if (i < medications.size() ) {
            medications.set(i, med);
        } else {
            medications.add(med);
        }
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#getMedication(int)
     */
    public Medication getMedication(int i) {
        return (Medication) medications.get(i);
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#getMedications()
     */
    public List getMedications() {
        return medications;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#setVaccinations(java.util.List)
     */
    public void setVaccinations(List l) {
        vaccinations =l;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#setVaccination(int, org.gnumed.testweb1.data.Vaccination)
     */
    public void setVaccination(int i, Vaccination vacc) {
        if (i < vaccinations.size() ) {
            vaccinations.set(i, vacc);
        } else {
            vaccinations.add(vacc);
        }
       
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#getVaccination(int)
     */
    public Vaccination getVaccination(int i) {
        return (Vaccination) vaccinations.get(i);
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#getVaccinations()
     */
    public List getVaccinations() {
        return vaccinations;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEpisode#getDescription()
     */
    public String getDescription() {
        // TODO Auto-generated method stub
        return null;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEpisode#setDescription(java.lang.String)
     */
    public void setDescription(String description) {
        // TODO Auto-generated method stub

    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEpisode#getId()
     */
    public Long getId() {
         
        return id;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEpisode#setId(java.lang.Long)
     */
    public void setId(Long id) {  
        this.id = id;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEpisode#getModified_when()
     */
    public Date getModified_when() {
         
        return modified_when;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEpisode#setModified_when(java.util.Date)
     */
    public void setModified_when(Date modified_when) {
         
        this.modified_when = modified_when;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEpisode#getRootItem(int)
     */
    public ClinRootItem getRootItem(int index) {
        // TODO Auto-generated method stub
        return null;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEpisode#setRootItem(int, org.gnumed.testweb1.data.ClinRootItem)
     */
    public void setRootItem(int index, ClinRootItem rootItem) {
        // TODO Auto-generated method stub

    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEpisode#getRootItemCount()
     */
    public int getRootItemCount() {
        // TODO Auto-generated method stub
        return 0;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEpisode#getRootItems()
     */
    public List getRootItems() {
        // TODO Auto-generated method stub
        return null;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEpisode#getRootItemsByType(java.lang.Class)
     */
    public List getRootItemsByType(Class type) {
        // TODO Auto-generated method stub
        return null;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEpisode#getEarliestRootItem()
     */
    public ClinRootItem getEarliestRootItem() {
        // TODO Auto-generated method stub
        return null;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#setAllergys(java.util.List)
     */
    public void setAllergys(List l) {
        allergys = l;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#setAllergy(int, org.gnumed.testweb1.data.Allergy)
     */
    public void setAllergy(int i, Allergy a) {
        if (i < allergys.size() ) {
            allergys.set(i, a);
        } else {
            allergys.add(a);
        }
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#getAllergy(int)
     */
    public Allergy getAllergy(int i) {
        return (Allergy) allergys.get(i);
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#getAllergys()
     */
    public List getAllergys() {
        return allergys;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#isClosingLastEpisode()
     */
    public boolean isClosingLastEpisode() {
        
        return closingLastEpisode;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#setClosingLastEpisode(boolean)
     */
    public void setClosingLastEpisode(boolean close) {
        this.closingLastEpisode = close;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#setLastEpisode(org.gnumed.testweb1.data.ClinicalEpisode)
     */
    public void setLastEpisode(ClinicalEpisode episode) {
        this.lastEpisode=episode;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#getLastEpisode()
     */
    public ClinicalEpisode getLastEpisode() {
        return lastEpisode;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#isLastEpisodeCloseable()
     */
    public boolean isLastEpisodeCloseable() {
        return  getLastEpisode() == null ? false : ( !getLastEpisode().isClosed());
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#isLastEpisodeOpenable()
     */
    public boolean isLastEpisodeOpenable() {
        return getLastEpisode() == null ? false : ( getLastEpisode().isClosed());
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#isOpeningLastEpisode()
     */
    public boolean isOpeningLastEpisode() {
        return openLastEpisode;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data2.EntryClinicalEpisode#setOpeningLastEpisode(boolean)
     */
    public void setOpeningLastEpisode(boolean open) {
        this.openLastEpisode = open;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEpisode#isClosed()
     */
    public boolean isClosed() {
        // TODO Auto-generated method stub
        return closed;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEpisode#setClosed(boolean)
     */
    public void setClosed(boolean closed) {
        // TODO Auto-generated method stub
        this.closed = closed;
    }

}
