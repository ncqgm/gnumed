/*
 * Created on 08-Feb-2005
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
package org.gnumed.testweb1.forms;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.List;

import org.apache.struts.validator.ValidatorActionForm;
import org.gnumed.testweb1.data2.EntryClinicalEpisode;

/**
 * @author sjtan
 *
 * TODO To change the template for this generated type comment go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
public class ClinicalUpdateForm2 extends BaseClinicalUpdateForm {
    
    List episodes = new ArrayList();
    
    void setEntryClinicalEpisodes( EntryClinicalEpisode[] episodes) {
        this.episodes.clear();
        this.episodes.addAll( Arrays.asList(episodes));
    }
    
    void setEntryClinicalEpisode( int i, EntryClinicalEpisode e){
            episodes.set(i, e);
    }
    
    EntryClinicalEpisode getEntryClinicalEpisode( int i) {
        return (EntryClinicalEpisode) episodes.get(i);
    }
    
    EntryClinicalEpisode[] getEntryClinicalEpisodes() {	
        return (EntryClinicalEpisode[]) episodes.toArray(new EntryClinicalEpisode[0]);
    }
    
    
}
