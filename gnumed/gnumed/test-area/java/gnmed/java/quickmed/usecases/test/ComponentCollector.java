/*
 * ComponentCollector.java
 *
 * Created on 05 April 2003, 22:30
 */

package quickmed.usecases.test;
import java.awt.Container;
import java.awt.Component;
import java.util.Collection;
import java.util.ArrayList;
/**
 *
 * @author  sjtan
 */
public class ComponentCollector {
    
   public static Collection collectType( Class aClass, Container parent) {
     ArrayList list = new ArrayList();
     Component[] comps = parent.getComponents();
     for ( int i = 0 ; i < comps.length; ++i) {
         Component c = comps[i];
         if ( aClass.isAssignableFrom(c.getClass()) ) 
             list.add(c);
         
         if (Container.class.isAssignableFrom(c.getClass())) {
                list.addAll(collectType(aClass, (Container) c));
         }
     }
     return list;
   }
    
}
