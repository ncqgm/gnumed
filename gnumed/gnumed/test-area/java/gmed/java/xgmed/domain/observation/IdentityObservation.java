/** Java class "IdentityObservation.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.observation;

import java.util.*;

import xgmed.helper.Visitable;
import  xgmed.helper.Visitor;
/**
 * <p>
 * 
 * </p>
 * @hibernate.subclass
 *      discriminator-value="I"
 */
public class IdentityObservation extends CategoryObservation {

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public Coding coding; 


   ///////////////////////////////////////
   // access methods for associations

    /**
     *@hibernate.one-to-one
     *  cascade="all"
     */
     public Coding getCoding() {
        return coding;
    }
    public void setCoding(Coding coding) {
        if (this.coding != coding) {
            this.coding = coding;
            if (coding != null) coding.setIdentityObservation(this);
        }
    }
  public void accept(Visitor v) {
      
        v.visitIdentityObservation(this);
         
    }
} // end IdentityObservation





