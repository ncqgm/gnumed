/** Java class "Suspension.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.planning;

import java.util.*;
import xgmed.domain.common.TimePeriod;

/**
 * <p>
 * 
 * </p>
 *@hibernate.class
 *  table="suspension"
 */
public class Suspension {

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
    public Action action; 
/**
 * <p>
 * 
 * </p>
 */
    public TimePeriod timePeriod; 


   ///////////////////////////////////////
   // access methods for associations
   /**
    *@hibernate.many-to-one
    */
    public Action getAction() {
        return action;
    }
    public void setAction(Action action) {
        if (this.action != action) {
            if (this.action != null) this.action.removeSuspension(this);
            this.action = action;
            if (action != null) action.addSuspension(this);
        }
    }
    
    /**
     *@hibernate.many-to-one
     */
    public TimePeriod getTimePeriod() {
        return timePeriod;
    }
    public void setTimePeriod(TimePeriod timePeriod) {
        this.timePeriod = timePeriod;
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.id
 *  generator-class="hilo.long"
 *  type="long"
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
    } // end setId        

} // end Suspension





