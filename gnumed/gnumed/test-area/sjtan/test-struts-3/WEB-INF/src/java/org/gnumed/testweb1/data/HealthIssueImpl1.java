
package org.gnumed.testweb1.data;

import java.util.Iterator;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

/**
 * 
 * @author sjtan
 */
public class HealthIssueImpl1 implements HealthIssue {

    static Log log = LogFactory.getLog(HealthIssueImpl1.class);

    Long id;

    String description;

    java.util.List episodes = new java.util.ArrayList();

    /** Creates a new instance of HealthIssueImpl */
    public HealthIssueImpl1() {
    }

    public ClinicalEpisode[] getClinicalEpisodes() {
        return (ClinicalEpisode[]) episodes.toArray(new ClinicalEpisode[0]);
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
        if (index >= episodes.size()) {
            episodes.add(clinicalEpisode);
        } else {
            episodes.remove(index);
            episodes.add(index, clinicalEpisode);
        }

    }

    public ClinRootItem getEarliestClinRootItem() {
        log.info(this);
        log.info(this.getDescription() + " has " + episodes.size() + " episodes");
        Iterator ei = episodes.iterator();
        ClinRootItem early = null;
        while (ei.hasNext()) {
            ClinicalEpisode en = (ClinicalEpisode) ei.next();

            ClinRootItem n = en.getEarliestRootItem();
            log.info(n.getNarrative());

            if (early == null
                    || 
              n.getClin_when().getTime() < early.getClin_when().getTime()
                    	
            ) {
                early = n;
            }
        }

        if (early == null) {
            log.info("for " + getDescription()
                    + " there was no earliest clin item found");
            early = NullRootItem.NullItem;

        }
        return early;

    }

    /*
     * (non-Javadoc)
     * 
     * @see org.gnumed.testweb1.data.HealthIssue#addClinicalEpisode(org.gnumed.testweb1.data.ClinicalEpisode)
     */
    public void addClinicalEpisode(ClinicalEpisode candidateEpisode) {
        log.info("before"+ episodes + " has " + episodes.size() );
        episodes.add(candidateEpisode);
        log.info("after"+ episodes + " has " + episodes.size() );
        if (!this.equals(candidateEpisode.getHealthIssue())) {
            candidateEpisode.setHealthIssue(this);
        }

    }

    /*
     * (non-Javadoc)
     * 
     * @see org.gnumed.testweb1.data.HealthIssue#hasClinicalEpisode(org.gnumed.testweb1.data.ClinicalEpisode)
     */
    public boolean hasClinicalEpisode(ClinicalEpisode episode) {

        return episodes.contains(episode);
    }

}