/*
 * ClinicalEncounterImpl1.java
 *
 * Created on September 18, 2004, 3:51 PM
 */

package org.gnumed.testweb1.data;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.Date;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import org.apache.commons.beanutils.BeanUtils;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

/**
 *
 * @author  sjtan
 */
public class ClinicalEncounterImpl1 implements ClinicalEncounter {
    Log log = LogFactory.getLog(ClinicalEncounterImpl1.class);
    java.util.Date started, affirmed;
    String type, description;
    Long id;
    String location;
    List narratives, medications, vaccinations, allergys, vitals;
     
    Map episodeMap, healthIssueMap;
    
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
        vitals = new java.util.ArrayList();
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
        try {
         BeanUtils.setProperty(o, "encounter", this);
        } catch (Exception e) {
            log.error(e);
            e.printStackTrace();
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
         set( narratives, index, narrative);
    }
    
    public List getNarratives() {
        return narratives;
    }
    
    public void sortRootItems(final java.util.Comparator comparator) {
        java.util.Collections.sort( narratives, comparator);
        
    }
    
    public java.util.List getVitals() {
        return vitals;
    }
     
    
    public void removeNarrative(ClinNarrative narrative) {
        narratives.remove(narrative);
    }
    
    public java.util.List getAllergies() {
        return allergys;
    }
     
    public ClinRootItem[] getRootItems() {
        java.util.List l = new ArrayList();
        l.addAll(getNarratives());
        l.addAll(getAllergies());
        l.addAll(getVaccinations());
        l.addAll(getVitals());
        return (ClinRootItem[]) l.toArray( new ClinRootItem[0]);
    }    
     
    public EntryClinRootItem[] getEntryRootItems() {
    	List l = Arrays.asList(getRootItems());
    	Iterator i = l.iterator();
    	List l2 = new ArrayList();
    	while (i.hasNext() ) {
    		ClinRootItem ri = (ClinRootItem) i.next();
    		if (ri instanceof EntryClinRootItem) {
    			l2.add(ri);
    		}
    	}
		return (EntryClinRootItem[])l2.toArray(new EntryClinRootItem[0] );
    }
    
    public EntryVitals getVital(int index) {
        return (EntryVitals) vitals.get(index);
        
    }
    
    public void setVital(int index, EntryVitals vital) {
        if ( index < getVitals().size() ) {
            vitals.set(index, vital);
        } else {
            vitals.add(vital);
        }
    }


	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.ClinicalEncounter#getVaccinations()
	 */
	public List getVaccinations() {
		// TODO Auto-generated method stub
		return vaccinations;
		
	}
    
	public ClinNarrative[] findNarrativeByHealthIssueName(String issueName) {
		Iterator i = getNarratives().iterator();
		List candidates = new ArrayList();
		while (i.hasNext()) {
			ClinNarrative n = (ClinNarrative) i.next();
			if ( issueName.equals( n.getHealthIssueName()) 
			  ) {
				candidates.add(n);
			}
		}
		return (ClinNarrative[])candidates.toArray(new ClinNarrative[0]);
		
	}


	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.ClinicalEncounter#findNarrativeBySoapCat(java.lang.String, java.lang.String)
	 */
	public ClinNarrative[] findNarrativeBySoapCat(String issueName, String soapCat) {
		List candidates = new ArrayList();
		
		ClinNarrative[] ns = findNarrativeByHealthIssueName(issueName);
		for (int i = 0; i < ns.length; ++i) {
			if (ns[i].getSoapCat().equals(soapCat)) {
				candidates.add(ns[i]);
			}
		}
		return (ClinNarrative[])candidates.toArray(new ClinNarrative[0]);
		
	}
	
	public void mergeReferences() {
		EntryClinRootItem[] items = getEntryRootItems();
		episodeMap = new HashMap();
		healthIssueMap = new HashMap();
		for (int i = 0; i < items.length; ++i ) {
			EntryClinRootItem item = items[i];
			item.normalizeHealthIssueName();
			if (healthIssueMap.get( item.getHealthIssueName() ) == null) {
				healthIssueMap.put( item.getHealthIssueName(), item.getEpisode().getHealthIssue());
			}
			item.getEpisode().setHealthIssue((HealthIssue) healthIssueMap.get( item.getHealthIssueName()));
		}
		
		for (int i = 0; i < items.length; ++i ) {
			EntryClinRootItem item = items[i];
			if (episodeMap.get(item.getEpisode().getDescription()) ==null) {
				episodeMap.put(item.getEpisode().getDescription(), item.getEpisode());
			}
			item.setEpisode((ClinicalEpisode)episodeMap.get(item.getEpisode().getDescription()));
		}
	}
	
	public void  updateItemEpisodeReferences() {
		EntryClinRootItem[] items = getEntryRootItems();
		for (int i = 0; i < items.length ; ++i ) {
			items[i].setEpisode((ClinicalEpisode)episodeMap.get(items[i].getEpisode().getDescription()));
			
		}
	}
	
	public Collection getMappedIssues() {
		return healthIssueMap.values();
	}
	
	
	public Collection getMappedEpisodes() {
		return episodeMap.values();
	}


	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.ClinicalEncounter#replaceMappedIssue(org.gnumed.testweb1.data.HealthIssue)
	 */
	public void replaceMappedIssue(HealthIssue hi) {
		// TODO Auto-generated method stub
		healthIssueMap.put(hi.getDescription() , hi);
		updateHealthIssueReferencesInMappedEpisodes();
	}


	/**
	 * 
	 */
	private void updateHealthIssueReferencesInMappedEpisodes() {
		// TODO Auto-generated method stub
		Iterator i = getMappedEpisodes().iterator();
		while (i.hasNext()) {
			ClinicalEpisode ep = (ClinicalEpisode) i.next();
			ep.setHealthIssue( (HealthIssue) healthIssueMap.get(ep.getHealthIssue().getDescription()));
			
		}
	}
	
	
}
