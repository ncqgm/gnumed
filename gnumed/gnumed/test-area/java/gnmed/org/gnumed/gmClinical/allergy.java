/** Java class "allergy.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package  org.gnumed.gmClinical;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 * @hibernate.subclass
 *      discriminator-value="A"
 */
public class allergy extends clin_root_item {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private String reaction; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private String substance; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private String substance_code; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private Boolean definite; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public enum_allergy_type enum_allergy_type; 


   ///////////////////////////////////////
   // access methods for associations

    /**
     *@hibernate.many-to-one
     */
    public enum_allergy_type getEnum_allergy_type() {
        return enum_allergy_type;
    }
    public void setEnum_allergy_type(enum_allergy_type _enum_allergy_type) {
        this.enum_allergy_type = _enum_allergy_type;
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.property
 */
    public String getReaction() {        
        return reaction;
    } // end getReaction        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setReaction(String _reaction) {        
        reaction = _reaction;
    } // end setReaction        

/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.property
 */
    public String getSubstance() {        
        return substance;
    } // end getSubstance        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setSubstance(String _substance) {        
        substance = _substance;
    } // end setSubstance        

/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.property
 */
    public String getSubstance_code() {        
        return substance_code;
    } // end getSubstance_code        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setSubstance_code(String _substance_code) {        
        substance_code = _substance_code;
    } // end setSubstance_code        

/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.property
 */
    public Boolean getDefinite() {        
        return definite;
    } // end getDefinite        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setDefinite(Boolean _definite) {        
        definite = _definite;
    } // end setDefinite        

} // end allergy





