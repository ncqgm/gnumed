/** Java class "Timepoint.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.common;

import java.util.*;
import java.util.Date;

import  xgmed.helper.Visitor; 
/**
 * <p>
 * 
 * </p>
 * @hibernate.subclass
 *      discriminator-value="T"
 */
public class Timepoint extends TimeRecord {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private Date timeValue; 



  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.property
 */
    public Date getTimeValue() {
        return timeValue;
    } // end getTime        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setTimeValue(Date _time) {        
        timeValue = _time;
    } // end setTime        

     public void accept(Visitor v) {
        v.visitTimepoint(this);
    }
    
} // end Timepoint





