/** Java class "Accountability.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package  xgmed.domain.accountability;

import java.util.*;
import xgmed.domain.common.TimePeriod;
import xgmed.domain.planning.Action;

/**
 * <p>
 * 
 * </p>
 * @hibernate.class
 *  table="accountability"
 */
public class Accountability {

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
    public Party commissioner; 
/**
 * <p>
 * 
 * </p>
 */
    public Collection action = new java.util.HashSet(); // of type Action
/**
 * <p>
 * 
 * </p>
 */
    public AccountabilityType accountabilityType; 
/**
 * <p>
 * 
 * </p>
 */
    public Party responsible; 
/**
 * <p>
 * 
 * </p>
 */
    public TimePeriod timePeriod; 


   ///////////////////////////////////////
   // access methods for associations
   
    /**
     * the party commissioning the accountability.
     *@hibernate.many-to-one
     */
    public Party getCommissioner() {
        return commissioner;
    }
    public void setCommissioner(Party party) {
        if (this.commissioner != party) {
            if (this.commissioner != null) this.commissioner.removeRequirement(this);
            this.commissioner = party;
            if (party != null) party.addRequirement(this);
        }
    }
    /**
     *the actions that are under this accountability.
     */
    public Collection getActions() {
        return action;
    }
    public void addAction(Action action) {
        if (! this.action.contains(action)) {
            this.action.add(action);
            action.addAccountability(this);
        }
    }
    public void removeAction(Action action) {
        boolean removed = this.action.remove(action);
        if (removed) action.removeAccountability(this);
    }
    
    /**
     *the accountability's type.
     */
    public AccountabilityType getAccountabilityType() {
        return accountabilityType;
    }
    public void setAccountabilityType(AccountabilityType accountabilityType) {
        this.accountabilityType = accountabilityType;
    }
    
    /**
     *the party accountable.
     * @hibernate.many-to-one
     */
    public Party getResponsible() {
        return responsible;
    }
    public void setResponsible(Party party) {
        if (this.responsible != party) {
            if (this.responsible != null) this.responsible.removeResponsibility(this);
            this.responsible = party;
            if (party != null) party.addResponsibility(this);
        }
    }
    
    /**
     *the time of accountability.
     */
    public TimePeriod getTimePeriod() {
        return timePeriod;
    }
    public void setTimePeriod(TimePeriod timePeriod) {
        if (this.timePeriod != timePeriod) {
            if (this.timePeriod != null) this.timePeriod.removeAccountability(this);
            this.timePeriod = timePeriod;
            if (timePeriod != null) timePeriod.addAccountability(this);
        }
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 *  @hibernate.id
 *      generator-class="hilo.long"
 *      type="long"
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
    
    /** Setter for property actions.
     * @param actions New value of property actions.
     *
     */
    public void setActions(Collection actions) {
        action = actions;
    }
    
 // end setId        

} // end Accountability





