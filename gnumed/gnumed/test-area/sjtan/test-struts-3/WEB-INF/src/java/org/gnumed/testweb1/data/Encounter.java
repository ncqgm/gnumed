/*
 * Encounter.java
 *
 * Created on July 6, 2004, 11:03 PM
 */

package org.gnumed.testweb1.data;
import org.gnumed.testweb1.global.Util;

/**
 *
 * @author  sjtan
 */
public class Encounter {
    private static int MAX_EPISODES = 5;
    /**
     * Holds value of property dateString.
     */
    private String dateString;
    
    /**
     * Holds value of property location.
     */
    private String location;
    
    /**
     * Holds value of property description.
     */
    private String description;
    
    /**
     * Holds value of property episode.
     */
    private Episode[] episode;
    
    /** Creates a new instance of Encounter */
    public Encounter() {
        setDateString(Util.getShortNowString(true));
        initEpisodes();
    }
    
    private void initEpisodes() {
        episode = new Episode[MAX_EPISODES];
        for (int i = 0; i < episode.length; ++i ) {
            episode[i] = new Episode();
        }
    }
    /**
     * Getter for property dateString.
     * @return Value of property dateString.
     */
    public String getDateString() {
        return this.dateString;
    }
    
    /**
     * Setter for property dateString.
     * @param dateString New value of property dateString.
     */
    public void setDateString(String dateString) {
        this.dateString = dateString;
    }
    
    /**
     * Getter for property location.
     * @return Value of property location.
     */
    public String getLocation() {
        return this.location;
    }
    
    /**
     * Setter for property location.
     * @param location New value of property location.
     */
    public void setLocation(String location) {
        this.location = location;
    }
    
    /**
     * Getter for property notes.
     * @return Value of property notes.
     */
    public String getDescription() {
        return this.description;
    }
    
    /**
     * Setter for property notes.
     * @param notes New value of property notes.
     */
    public void setDescription(String description) {
        this.description = description;
    }
    
    /**
     * Indexed getter for property episode.
     * @param index Index of the property.
     * @return Value of the property at <CODE>index</CODE>.
     */
    public Episode getEpisode(int index) {
        return this.episode[index];
    }
    
    /**
     * Indexed setter for property episode.
     * @param index Index of the property.
     * @param episode New value of the property at <CODE>index</CODE>.
     */
    public void setEpisode(int index, Episode episode) {
        this.episode[index] = episode;
    }
    
    public Episode[] getEpisodes() {
        return episode;
    }
    
}
