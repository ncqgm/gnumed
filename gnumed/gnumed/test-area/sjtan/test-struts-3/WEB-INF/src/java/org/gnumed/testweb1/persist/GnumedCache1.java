/*
 * GnumedCache.java
 *
 * Created on September 18, 2004, 9:58 AM
 */

package org.gnumed.testweb1.persist;
import org.gnumed.testweb1.data.*;
/**
 *
 * @author  sjtan
 */
public interface GnumedCache1 {
    public HealthIssue getHealthIssue(Long id);
    public ClinicalEpisode getClinicalEpisode(Long id);
    
}
