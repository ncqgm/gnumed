/*
 * TestProperties.java
 *
 * Created on 25 July 2003, 00:43
 */

package gnmed.test;
import java.util.*;
import java.util.logging.*;
import java.io.*;
/**
 *
 * @author  sjtan
 */
public class TestProperties extends Properties {
    public static final String FILENAME = "gnmed-test.properties";
    public static final TestProperties properties;
    static {
        properties = new TestProperties();
    };
    
    
    
    /** Creates a new instance of TestProperties */
    public TestProperties() {
        try {
          File f = new File(".");
        for (int i = 0; i < f.listFiles().length; ++i) {
            System.out.println(f.listFiles()[i]);
        }
        System.out.println(f.listFiles());
        load( new BufferedInputStream(new FileInputStream(FILENAME)));
      
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    public void save() {
        try {
            store( new FileOutputStream(TestProperties.FILENAME), "Test Properties");
            
         } catch (Exception e) {
            e.printStackTrace();
        }
    }
     
    public int getIntProperty( String name) throws Exception {
        String p = getProperty(name);
        if (p== null) {
            Logger.global.info("NO VALUE FOUND FOR PROPERTY" + name);
            return 0;
        }
        return Integer.parseInt(p.trim());
    }
    
}
