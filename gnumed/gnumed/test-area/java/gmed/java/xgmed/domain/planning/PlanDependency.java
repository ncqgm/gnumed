/** Java class "PlanDependency.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.planning;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 */
public class PlanDependency {

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
    public ActionRef dependantActionRef; 
/**
 * <p>
 * 
 * </p>
 */
    public ActionRef consequentActionRef; 


   ///////////////////////////////////////
   // access methods for associations

    public ActionRef getDependantActionRef() {
        return dependantActionRef;
    }
    public void setDependantActionRef(ActionRef actionRef) {
        if (this.dependantActionRef != actionRef) {
            if (this.dependantActionRef != null) this.dependantActionRef.removeDependent(this);
            this.dependantActionRef = actionRef;
            if (actionRef != null) actionRef.addDependent(this);
        }
    }
    public ActionRef getConsequentActionRef() {
        return consequentActionRef;
    }
    public void setConsequentActionRef(ActionRef actionRef) {
        if (this.consequentActionRef != actionRef) {
            if (this.consequentActionRef != null) this.consequentActionRef.removeConsequent(this);
            this.consequentActionRef = actionRef;
            if (actionRef != null) actionRef.addConsequent(this);
        }
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
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

} // end PlanDependency





