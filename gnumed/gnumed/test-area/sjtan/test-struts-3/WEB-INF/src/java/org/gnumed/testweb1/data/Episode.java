/*
 * Episode.java
 *
 * Created on July 7, 2004, 12:35 AM
 */

package org.gnumed.testweb1.data;

/**
 *
 * @author  sjtan
 */
public class Episode {
    
    /**
     * Holds value of property clinHealthIssue.
     */
    private String clinHealthIssue;
    
    /**
     * Holds value of property notes.
     */
    private String notes;
    
    /** Creates a new instance of Episode */
    public Episode() {
        setClinHealthIssue("xxDEFAULTxx");
    }
    
    /**
     * Getter for property clinHealthIssue.
     * @return Value of property clinHealthIssue.
     */
    public String getClinHealthIssue() {
        return this.clinHealthIssue;
    }
    
    /**
     * Setter for property clinHealthIssue.
     * @param clinHealthIssue New value of property clinHealthIssue.
     */
    public void setClinHealthIssue(String clinHealthIssue) {
        this.clinHealthIssue = clinHealthIssue;
    }
    
    /**
     * Getter for property notes.
     * @return Value of property notes.
     */
    public String getNotes() {
        return this.notes;
    }
    
    /**
     * Setter for property notes.
     * @param notes New value of property notes.
     */
    public void setNotes(String notes) {
        this.notes = notes;
    }
    
}
