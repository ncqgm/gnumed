/*
 * Created on 15-Feb-2005
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
package org.gnumed.testweb1.data2;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Comparator;
import java.util.Date;
import java.util.List;

import org.gnumed.testweb1.data.Allergy;
import org.gnumed.testweb1.data.ClinNarrative;
import org.gnumed.testweb1.data.ClinRootItem;
import org.gnumed.testweb1.data.ClinicalEpisode;
import org.gnumed.testweb1.data.EntryClinRootItem;
import org.gnumed.testweb1.data.EntryEncounterByEpisodes;
import org.gnumed.testweb1.data.EntryVitals;
import org.gnumed.testweb1.data.HealthIssue;
import org.gnumed.testweb1.data.Medication;
import org.gnumed.testweb1.data.Vaccination;

/**
 * @author sjtan
 *
 * TODO To change the template for this generated type comment go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
public class EntryEncounterByEpisodesImpl1 implements EntryEncounterByEpisodes {
    private Long id;
    private Date started, affirmed; 
    private String encounterType, location;
    private List episodes = new ArrayList();
    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.EntryEncounterByEpisodes#setEpisodes(org.gnumed.testweb1.data.ClinicalEpisode[])
     */
    public void setEpisodes(ClinicalEpisode[] episodes) {
        // TODO Auto-generated method stub
        this.episodes = new ArrayList( java.util.Arrays.asList(episodes));
        
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.EntryEncounterByEpisodes#addEpisode(org.gnumed.testweb1.data.ClinicalEpisode)
     */
    public boolean addEpisode(ClinicalEpisode episode) {
        // TODO Auto-generated method stub
        return this.episodes.add(episode);
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.EntryEncounterByEpisodes#getEpisode(int)
     */
    public ClinicalEpisode getEpisode(int index) {
        // TODO Auto-generated method stub
        return (ClinicalEpisode) episodes.get(index);
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.EntryEncounterByEpisodes#setEpisode(int, org.gnumed.testweb1.data.ClinicalEpisode)
     */
    public void setEpisode(int index, ClinicalEpisode episode) {
        // TODO Auto-generated method stub
        if (index < episodes.size()) {
            episodes.set(index, episode);
        } else {
            episodes.add(episode);
        }
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.EntryEncounterByEpisodes#getEpisodes()
     */
    public ClinicalEpisode[] getEpisodes() {
        // TODO Auto-generated method stub
        return (ClinicalEpisode[]) episodes.toArray( new ClinicalEpisode[0]);
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#getId()
     */
    public Long getId() {
        // TODO Auto-generated method stub
        return id;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#setId(java.lang.Long)
     */
    public void setId(Long id) {
        // TODO Auto-generated method stub
        	this.id = id;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#getDescription()
     */
    public String getDescription() {
        // TODO Auto-generated method stub
        return null;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#setDescription(java.lang.String)
     */
    public void setDescription(String description) {
        // TODO Auto-generated method stub

    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#getStarted()
     */
    public Date getStarted() {
        // TODO Auto-generated method stub
        return started;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#setStarted(java.util.Date)
     */
    public void setStarted(Date started) {
        // TODO Auto-generated method stub
        this.started = started;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#getLastAffirmed()
     */
    public Date getLastAffirmed() {
        // TODO Auto-generated method stub
        return affirmed;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#setLastAffirmed(java.util.Date)
     */
    public void setLastAffirmed(Date lastAffirmed) {
        // TODO Auto-generated method stub
        this.affirmed = lastAffirmed;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#getEncounterType()
     */
    public String getEncounterType() {
        // TODO Auto-generated method stub
        return encounterType;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#setEncounterType(java.lang.String)
     */
    public void setEncounterType(String encounterType) {
        // TODO Auto-genertated method stub
        this.encounterType = encounterType;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#getLocation()
     */
    public String getLocation() {
        // TODO Auto-generated method stub
        return location;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#setLocation(java.lang.String)
     */
    public void setLocation(String location) {
        // TODO Auto-generated method stub
        this.location = location;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#getVaccination(int)
     */
    public Vaccination getVaccination(int index) {
        // TODO Auto-generated method stub
        return null;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#setVaccination(int, org.gnumed.testweb1.data.Vaccination)
     */
    public void setVaccination(int index, Vaccination vaccination) {
        // TODO Auto-generated method stub
        
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#getAllergy(int)
     */
    public Allergy getAllergy(int index) {
        // TODO Auto-generated method stub
        return null;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#setAllergy(int, org.gnumed.testweb1.data.Allergy)
     */
    public void setAllergy(int index, Allergy allergy) {
        // TODO Auto-generated method stub
        
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#getMedication(int)
     */
    public Medication getMedication(int index) {
        // TODO Auto-generated method stub
        return null;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#setMedication(int, org.gnumed.testweb1.data.Medication)
     */
    public void setMedication(int index, Medication medication) {
        // TODO Auto-generated method stub
        
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#getNarrative(int)
     */
    public ClinNarrative getNarrative(int index) {
        // TODO Auto-generated method stub
        return null;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#getVaccinations()
     */
    public List getVaccinations() {
        // TODO Auto-generated method stub
        for (int i = 0;  i < episodes.size();++i) {
            ClinicalEpisode episode = getEpisode(i);
            
        }
        return null;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#getMedications()
     */
    public List getMedications() {
        // TODO Auto-generated method stub
        return null;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#getNarratives()
     */
    public List getNarratives() {
        // TODO Auto-generated method stub
        return null;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#setNarrative(int, org.gnumed.testweb1.data.ClinNarrative)
     */
    public void setNarrative(int index, ClinNarrative narrative) {
        // TODO Auto-generated method stub
        
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#removeNarrative(org.gnumed.testweb1.data.ClinNarrative)
     */
    public void removeNarrative(ClinNarrative narrative) {
        // TODO Auto-generated method stub
        
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#sortRootItems(java.util.Comparator)
     */
    public void sortRootItems(Comparator comparator) {
        // TODO Auto-generated method stub
        
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#getAllergies()
     */
    public List getAllergies() {
        // TODO Auto-generated method stub
        return null;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#getRootItems()
     */
    public ClinRootItem[] getRootItems() {
        // TODO Auto-generated method stub
        return null;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#getVital(int)
     */
    public EntryVitals getVital(int index) {
        // TODO Auto-generated method stub
        return null;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#setVital(int, org.gnumed.testweb1.data.EntryVitals)
     */
    public void setVital(int index, EntryVitals vital) {
        // TODO Auto-generated method stub
        
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#getVitals()
     */
    public List getVitals() {
        // TODO Auto-generated method stub
        return null;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#findNarrativeByHealthIssueName(java.lang.String)
     */
    public ClinNarrative[] findNarrativeByHealthIssueName(String issueName) {
        // TODO Auto-generated method stub
        return null;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#findNarrativeBySoapCat(java.lang.String, java.lang.String)
     */
    public ClinNarrative[] findNarrativeBySoapCat(String issueName, String soapCat) {
        // TODO Auto-generated method stub
        return null;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#getEntryRootItems()
     */
    public EntryClinRootItem[] getEntryRootItems() {
        // TODO Auto-generated method stub
        return null;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#contains(org.gnumed.testweb1.data.ClinRootItem)
     */
    public boolean contains(ClinRootItem item) {
        // TODO Auto-generated method stub
        return false;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#addClinRootItem(org.gnumed.testweb1.data.ClinRootItem)
     */
    public boolean addClinRootItem(ClinRootItem item) {
        // TODO Auto-generated method stub
        return false;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#getMappedIssues()
     */
    public Collection getMappedIssues() {
        // TODO Auto-generated method stub
        return null;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#getMappedEpisodes()
     */
    public Collection getMappedEpisodes() {
        // TODO Auto-generated method stub
        return null;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#mergeReferences()
     */
    public void mergeReferences() {
        // TODO Auto-generated method stub
        
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEncounter#replaceMappedIssue(org.gnumed.testweb1.data.HealthIssue)
     */
    public void replaceMappedIssue(HealthIssue hi) {
        // TODO Auto-generated method stub
        
    }

 

}
