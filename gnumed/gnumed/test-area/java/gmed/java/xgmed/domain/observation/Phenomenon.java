/** Java class "Phenomenon.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.observation;
import xgmed.helper.Visitor;
import java.util.*;

/**
 * <p>
 * 
 * </p>
 * @hibernate.subclass
 *  discriminator-value="P"
 */
public class Phenomenon extends ObservationConcept {

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public PhenomenonType phenomenonType; 


   ///////////////////////////////////////
   // access methods for associations
   /**
    *@hibernate.many-to-one
    */
    public PhenomenonType getPhenomenonType() {
        return phenomenonType;
    }
    
    public void setPhenomenonType(PhenomenonType phenomenonType) {
        if (this.phenomenonType != phenomenonType) {
            if (this.phenomenonType != null) this.phenomenonType.removePhenomenon(this);
            this.phenomenonType = phenomenonType;
            if (phenomenonType != null) phenomenonType.addPhenomenon(this);
        }
    }
    
   public void accept(Visitor v) {
       v.visitPhenomenon(this);
    }
} // end Phenomenon





