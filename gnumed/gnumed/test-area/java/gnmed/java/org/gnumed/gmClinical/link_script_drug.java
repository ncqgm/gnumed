
/** Java class "link_script_drug.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package  org.gnumed.gmClinical;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 * @hibernate.class
 */
public class link_script_drug {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private Integer id; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private int repeats; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public script_drug script_drug; 
/**
 * <p>
 * 
 * </p>
 */
    public script script; 


   ///////////////////////////////////////
   // access methods for associations
/**
 *
 *@hibernate.many-to-one
 *  cascade="none"
 */
    public script_drug getScript_drug() {
        return script_drug;
    }
    public void setScript_drug(script_drug _script_drug) {
        if (this.script_drug != _script_drug) {
            if (this.script_drug != null) this.script_drug.removeLink_script_drug(this);
            this.script_drug = _script_drug;
            if (_script_drug != null) _script_drug.addLink_script_drug(this);
        }
    }
    
    /**
     *@hibernate.many-to-one
     */
    public script getScript() {
        return script;
    }
    public void setScript(script _script) {
        if (this.script != _script) {
            if (this.script != null) this.script.removeLink_script_drug(this);
            this.script = _script;
            if (_script != null) _script.addLink_script_drug(this);
        }
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 *
 *@hibernate.property
 */
    public int getRepeats() {        
        return repeats;
    } // end getRepeats        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setRepeats(int _repeats) {        
        repeats = _repeats;
    } // end setRepeats        

/**
 * <p>
 * Represents ...
 * </p>
 *
 *@hibernate.id
 *  generator-class="hilo"
 */
    public Integer getId() {        
        return id;
    } // end getId        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setId(Integer _id) {        
        id = _id;
    } // end setId        

} // end link_script_drug



