/*
 * Factory.java
 *
 * Created on 5 August 2003, 07:44
 */

package quickmed.usecases.test;
import java.util.List;
/**
 *
 * @author  sjtan
 */
public interface Factory {
    
  Object newInstance();
    
  public List getConvertedList();
  
}
