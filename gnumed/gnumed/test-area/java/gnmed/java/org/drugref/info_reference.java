/** Java class "info_reference.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.drugref;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 */
public class info_reference {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private char source_category; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private String description; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public Collection comments = new java.util.HashSet(); // of type comments


   ///////////////////////////////////////
   // access methods for associations

    public Collection getCommentss() {
        return comments;
    }
    public void addComments(comments _comments) {
        if (! this.comments.contains(_comments)) {
            this.comments.add(_comments);
            _comments.setInfo_reference(this);
        }
    }
    public void removeComments(comments _comments) {
        boolean removed = this.comments.remove(_comments);
        if (removed) _comments.setInfo_reference((info_reference)null);
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 */
    public char getSource_category() {        
        return source_category;
    } // end getSource_category        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setSource_category(char _source_category) {        
        source_category = _source_category;
    } // end setSource_category        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public String getDescription() {        
        return description;
    } // end getDescription        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setDescription(String _description) {        
        description = _description;
    } // end setDescription        

} // end info_reference





