/** Java class "AccountabilityType.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.accountability;

import java.util.*;

/** <p>
 *
 * </p>
 * @hibernate.class 
 *  table="accountability_type"
 */
public class AccountabilityType {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private Long id; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public Collection commissioner = new java.util.HashSet(); // of type PartyType
/**
 * <p>
 * 
 * </p>
 */
    public Collection responsible = new java.util.HashSet();
    
    /** Holds value of property description. */
    private String description;
    
 // of type PartyType


   ///////////////////////////////////////
   // access methods for associations

     
    public Collection getCommissioners() {
        return commissioner;
    }
    public void setCommissioners(Collection c) {
        commissioner = c;
    }
    
    public void addCommissioner(PartyType partyType) {
        if (! this.commissioner.contains(partyType)) {
            this.commissioner.add(partyType);
            partyType.addCommissioning(this);
        }
    }
    public void removeCommissioner(PartyType partyType) {
        boolean removed = this.commissioner.remove(partyType);
        if (removed) partyType.removeCommissioning(this);
    }
    /** the party types which require the accountability type.
     * a many-to-many association with PartyType.
     * a many-to-many association with PartyType. 
     *
     */     
    public Collection getResponsibles() {
        return responsible;
    }
    
    public void setResponsibles(Collection c) {
        responsible = c;
    }
    
    public void addResponsible(PartyType partyType) {
        if (! this.responsible.contains(partyType)) {
            this.responsible.add(partyType);
            partyType.addResponsibility(this);
        }
    }
    public void removeResponsible(PartyType partyType) {
        boolean removed = this.responsible.remove(partyType);
        if (removed) partyType.removeResponsibility(this);
    }


  ///////////////////////////////////////
  // operations


    /** <p>
     * Represents ...
     * </p>
     * @see
     * @return 
     *
     * @hibernate.id     
     *      generator-class="hilo.long"
     *    type="long"
     */
    public Long getId() {        
        return id;
    } // end getId        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setId(Long _id) {        
        id = _id;
    }
    
    /** Getter for property description.
     * @return Value of property description.
     *
     * @hibernate.property
     */
    public String getDescription() {
        return this.description;
    }
    
    /** Setter for property description.
     * @param description New value of property description.
     *
     */
    public void setDescription(String description) {
        this.description = description;
    }
    
 // end setId        

} // end AccountabilityType





