/*
 * ClinicalEpisodeImpl.java
 *
 * Created on September 19, 2004, 8:30 AM
 */

package org.gnumed.testweb1.data;

import org.gnumed.testweb1.global.Algorithms;

/**
 *
 * @author  sjtan
 */
public class ClinicalEpisodeImpl1 implements ClinicalEpisode{
	
	  
    static long SAME_EPISODE_INTERVAL =  5 * 1000; // 5 seconds
    
    private String description;
    private HealthIssue hi;
    private Long id;
    private java.util.Date modified_when = new java.util.Date();
    
    private java.util.List rootItems = new java.util.ArrayList();
    
    public boolean equals( Object o ) {
    	if (! (o instanceof ClinicalEpisode))
    		return false;
    	ClinicalEpisode e = (ClinicalEpisode) o;
    	
    	return Algorithms.normaliseMatch(e.getDescription(),getDescription())
		&& isWithinEpisodeLimit(e);
    	}
    
    protected boolean isWithinEpisodeLimit(ClinicalEpisode e ) {
    	return Math.abs( e.getModified_when().getTime() 
    			- getModified_when().getTime() )
												< SAME_EPISODE_INTERVAL ;
     }
    /** Creates a new instance of ClinicalEpisodeImpl */
    public ClinicalEpisodeImpl1()  {
    }
    
    public String getDescription() {
        return description;
    }
    
    public HealthIssue getHealthIssue() {
        return hi;
    }
    
    public Long getId() {
        return id;
    }
    
    public void setDescription(String description) {
        this.description = description;
    }
    
    public void setHealthIssue(HealthIssue healthIssue) {
        this.hi = healthIssue;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public java.util.Date getModified_when() {
        return modified_when;
    }
    
    public void setModified_when(java.util.Date modified_when) {
        this.modified_when = modified_when;
    }
    
    
    
    public ClinRootItem getRootItem(int index) {
        return (ClinRootItem) rootItems.get(index);
    }    
    
    public void setRootItem(int index, ClinRootItem rootItem) {
        if  ( rootItems.size() > index) {
            rootItems.set(index, rootItem);
        } else {
            rootItems.add(rootItem);
        }
    }
    
    public int getRootItemCount() {
        return rootItems.size();
    }
    
    public java.util.List getRootItems() {
        return rootItems;
    }
    
    public ClinRootItem getEarliestRootItem() {
        java.util.Iterator i = rootItems.iterator();
        ClinRootItem earliest = null;
        while (i.hasNext()) {
            ClinRootItem item = (ClinRootItem) i.next();
            if   ( earliest == null ||
                item.getClin_when().getTime() < earliest.getClin_when().getTime() ) {
                
                    earliest = (ClinNarrative) item; 
            }
            
        }
        
        return ((earliest != null) ? earliest : NullRootItem.NullItem);
    }
    
}
