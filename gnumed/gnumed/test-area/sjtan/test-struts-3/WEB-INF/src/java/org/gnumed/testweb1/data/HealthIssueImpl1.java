/*
 * HealthIssueImpl.java
 *
 * Created on September 18, 2004, 9:33 PM
 */

package org.gnumed.testweb1.data;
import java.util.Iterator;
/**
 *
 * @author  sjtan
 */
public class HealthIssueImpl1 implements HealthIssue {
    
    Long id;
    String description;
     java.util.List episodes = new java.util.ArrayList();
    /** Creates a new instance of HealthIssueImpl */
    public HealthIssueImpl1() {
    }
    
    public ClinicalEpisode[] getClinicalEpisodes() {
        return (ClinicalEpisode[]) episodes.toArray(new ClinicalEpisode[0] );
    }    
    
    public String getDescription() {
        return description;
    }    
    
    public Long getId() {
        return id;
    }
    
    public void setClinicalEpisodes(ClinicalEpisode[] clinicalEpisodes) {
    }
    
    public void setDescription(String description) {
        this.description = description;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public ClinicalEpisode getClinicalEpisode(int index) {
        if (index < episodes.size())
            return (ClinicalEpisode) episodes.get(index);
        return null;
    }
    
    public void setClinicalEpisode(int index, ClinicalEpisode clinicalEpisode) {
        if ( index >= episodes.size() ) {
            episodes.add(clinicalEpisode);
        } else {
            episodes.remove(index);
            episodes.add( index, clinicalEpisode);
        }
        
    }
    
    public ClinNarrative getEarliestNarrative() {
        Iterator ei = episodes.iterator();
        ClinNarrative early = null;
        while (ei.hasNext()) {
            ClinicalEpisode en = (ClinicalEpisode) ei.next();
            
            ClinNarrative n = en.getEarliestNarrative();
            
            if ( early == null || n.getClin_when().getTime() < early.getClin_when().getTime()) {
                early = n;
            }
        }
        
        return early;
    }
    
}
