/*
 * IntrospectingPrinter.java
 *
 * Created on 4 August 2003, 19:55
 */

package quickmed.usecases.test;
import java.beans.*;
import java.util.*;
import java.lang.reflect.*;
import java.io.*;
import java.util.logging.*;
/**
 *
 * @author  sjtan
 */
public class IntrospectingPrinter {
    static  IntrospectingPrinter ainstance ;
    static {
        ainstance = new IntrospectingPrinter();
    };
    /** Creates a new instance of IntrospectingPrinter */
    public IntrospectingPrinter() {
    }
    
    public static IntrospectingPrinter instance() {
        return ainstance;
    }
    
    Set set = new HashSet();
    
    public   void printObject( PrintStream ps, Object o) throws Exception {
        printObject(ps, o, 0);
    }
    
    boolean visited(Object o) {
        if (set.contains(o))
            return true;
        set.add(o);
        Logger.global.info("remembering " + o + " has been visited");
        return false;
    }
    
    
    public   void printObject( PrintStream ps, Object o, int level) throws Exception {
        Logger.global.info("EXAMINING " + o);
        if (o == null) {
            ps.println("Object is null");
            return;
        }
        BeanInfo info = Introspector.getBeanInfo(o.getClass());
        
        if (visited(o))  {
            for (int  j = 0; j < level; ++j) {
                ps.print("   ");
            }
            ps.print(info.getBeanDescriptor().getName() );
            ps.print(":");
            ps.println(" already visited");
            return;
        }
        PropertyDescriptor[] pds =  info.getPropertyDescriptors();
        for (int i = 0; i < pds.length; ++i) {
            if ( pds[i].getName().equals("class"))
                continue;
            
            Object prop = pds[i].getReadMethod().invoke(o, new Object[0]) ;
            Class type = pds[i].getPropertyType();
             for (int  j = 0; j < level; ++j) {
                ps.print("   ");
            }
            ps.print( pds[i].getName());
            ps.print(":");
            if ( Collection.class.isAssignableFrom(type) ) {
                Iterator it = ( (Collection)prop).iterator();
                while (it.hasNext()) {
                    try {
                        printObject(ps, it.next(), level+1);
                    } catch (Exception e) {
                        ps.println(e);
                    }
                }
            }
            ps.println(prop);
           
            if ( type.isPrimitive() || String.class.isAssignableFrom(type) )
                continue;
            try {
                printObject(ps, prop, level + 1);
            } catch (Exception e) {
                ps.println(e);
            }
        }
    }
}


