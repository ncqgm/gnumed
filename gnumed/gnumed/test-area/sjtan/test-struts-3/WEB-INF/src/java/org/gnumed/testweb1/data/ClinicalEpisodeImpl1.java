/*
 * ClinicalEpisodeImpl.java
 *
 * Created on September 19, 2004, 8:30 AM
 */

package org.gnumed.testweb1.data;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;


/**
 *
 * @author  sjtan
 */
public class ClinicalEpisodeImpl1 implements ClinicalEpisode{
	static Log log = LogFactory.getLog(ClinicalEpisodeImpl1.class);
	  
    static long SAME_EPISODE_INTERVAL =  5 * 1000; // 5 seconds
    private boolean closed;
    private String description;
    private HealthIssue hi;
    private Long id;
    private java.util.Date modified_when = new java.util.Date();
    
    private java.util.List rootItems = new java.util.ArrayList();
    
// causes lost episode bug    
//    public boolean equals( Object o ) {
//    	if (! (o instanceof ClinicalEpisode))
//    		return false;
//    	ClinicalEpisode e = (ClinicalEpisode) o;
////version 0.1
////    	return Algorithms.normaliseMatch(e.getDescription(),getDescription())
////		&& isWithinEpisodeLimit(e);
//    	return isWithinEpisodeLimit(e);
//    	}
//  
    
  // another version
    
//   public boolean equals(Object o) {
//   	if (! (o instanceof ClinicalEpisode))
//		return false;
//	ClinicalEpisode e = (ClinicalEpisode) o;
////version 0.1
////	return Algorithms.normaliseMatch(e.getDescription(),getDescription())
////	&& isWithinEpisodeLimit(e);
//	if (e.getHealthIssue() == null || getHealthIssue() == null)
//	    return super.equals(o);
//	return 
//	isWithinEpisodeLimit(e) 
//	&& e.getHealthIssue().getDescription().equals(getHealthIssue().getDescription());
//	}
    
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
        if (!healthIssue.hasClinicalEpisode(this)) {
            healthIssue.addClinicalEpisode(this);
        }
        this.hi = healthIssue; // out here because of nullHealthIssue object
        // the bug causes unlinked episodes not to have
        // a link to nullHealthIssue.
        // it's a problem with hasClinicalEpisode()
        // for some reason, nullHealthIssue may have an
        // an unlinked episode, and won't add it.
        // maybe it's the definition.
        
        
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
        log.info("For "+ this +"  rootItems.size=" + rootItems.size());
        java.util.Iterator i = rootItems.iterator();
        ClinRootItem earliest = null;
        while (i.hasNext()) {
            ClinRootItem item = (ClinRootItem) i.next();
            if   ( earliest == null ||
                item.getClin_when().getTime() < earliest.getClin_when().getTime() ) {
                
                    earliest = (ClinNarrative) item; 
            }
            
        }
        log.info("earliest="+earliest);
        return ((earliest != null) ? earliest : NullRootItem.NullItem);
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEpisode#getRootItemsByType(java.lang.Class)
     */
    public List getRootItemsByType(Class type) {
       
        Iterator i = rootItems.iterator();
        List result = new ArrayList();
        while (i.hasNext()) {
            ClinRootItem item = (ClinRootItem) i.next();
            if(type.isInstance(item)) {
                result.add(item);
            }
        }
        return result;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEpisode#isClosed()
     */
    public boolean isClosed() {
      
        return closed;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.data.ClinicalEpisode#setClosed(boolean)
     */
    public void setClosed(boolean closed) {
         
        this.closed = closed;
        
    }
    
}
