/*
 * identity_role_info.java
 *
 * Created on 19 August 2003, 00:33
 */

package org.gnumed.gmIdentity;

/**
 *
 * @author  syan
 * @hibernate.class
 */
public class identity_role_info {
    
    /** Holds value of property identity_role. */
    private identity_role identity_role;
    
    /** Holds value of property comments. */
    private String comments;
    
    /** Holds value of property id. */
    private Long id;
    
    /** Creates a new instance of identity_role_info */
    public identity_role_info() {
    }
    
    /** Getter for property identity_role.
     * @return Value of property identity_role.
     *
     * @hibernate.many-to-one
     *      cascade="save-update"
     *     
     */
    public identity_role getIdentity_role() {
        return this.identity_role;
    }
    
    /** Setter for property identity_role.
     * @param identity_role New value of property identity_role.
     *
     */
    public void setIdentity_role(identity_role identity_role) {
        this.identity_role = identity_role;
    }
    
    /** Getter for property comments.
     * @return Value of property comments.
     *
     *
     * @hibernate.property
     */
    public String getComments() {
        return this.comments;
    }
    
    /** Setter for property comments.
     * @param comments New value of property comments.
     *
     */
    public void setComments(String comments) {
        this.comments = comments;
    }
     /** Getter for property id.
     * @return Value of property id.
     *
     * @hibernate.id
     *  generator-class="hilo"
     */
    public Long getId() {
        return this.id;
    }
    
    /** Setter for property id.
     * @param id New value of property id.
     *
     */
    public void setId(Long id) {
        this.id = id;
    }
    
    public String toString() {
       StringBuffer sb = new StringBuffer( getIdentity_role().getName());
        if (getComments() != null )
            sb.append(":  ").append(getComments());
        return sb.toString();
    }
    
}
