/** Java class "comments.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.drugref;

import java.util.*;
import java.util.Date;

/**
 * <p>
 * 
 * </p>
 */
public class comments {

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
    private Date stamp; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private String who; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private Integer source; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private String signature; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private String table_name; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private Integer table_row; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public info_reference info_reference; 


   ///////////////////////////////////////
   // access methods for associations

    public info_reference getInfo_reference() {
        return info_reference;
    }
    public void setInfo_reference(info_reference _info_reference) {
        if (this.info_reference != _info_reference) {
            if (this.info_reference != null) this.info_reference.removeComments(this);
            this.info_reference = _info_reference;
            if (_info_reference != null) _info_reference.addComments(this);
        }
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
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

/**
 * <p>
 * Represents ...
 * </p>
 */
    public Date getStamp() {        
        return stamp;
    } // end getStamp        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setStamp(Date _stamp) {        
        stamp = _stamp;
    } // end setStamp        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public String getWho() {        
        return who;
    } // end getWho        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setWho(String _who) {        
        who = _who;
    } // end setWho        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public Integer getSource() {        
        return source;
    } // end getSource        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setSource(Integer _source) {        
        source = _source;
    } // end setSource        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public String getSignature() {        
        return signature;
    } // end getSignature        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setSignature(String _signature) {        
        signature = _signature;
    } // end setSignature        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public String getTable_name() {        
        return table_name;
    } // end getTable_name        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setTable_name(String _table_name) {        
        table_name = _table_name;
    } // end setTable_name        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public Integer getTable_row() {        
        return table_row;
    } // end getTable_row        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setTable_row(Integer _table_row) {        
        table_row = _table_row;
    } // end setTable_row        

} // end comments





