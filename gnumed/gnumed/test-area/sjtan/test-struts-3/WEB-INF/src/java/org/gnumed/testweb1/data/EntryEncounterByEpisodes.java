/*
 * Created on 15-Feb-2005
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
package org.gnumed.testweb1.data;

/**
 * @author sjtan
 *
 * TODO To change the template for this generated type comment go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
public interface EntryEncounterByEpisodes extends ClinicalEncounter {
    public void setEpisodes( ClinicalEpisode[] episodes);
    public boolean addEpisode( ClinicalEpisode episode);
    public ClinicalEpisode getEpisode(int index);
    public void setEpisode( int index, ClinicalEpisode episode);
    public ClinicalEpisode[] getEpisodes();
}
