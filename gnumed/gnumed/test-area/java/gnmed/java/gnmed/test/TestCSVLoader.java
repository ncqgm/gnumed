/*
 * TestCSVLoader.java
 *
 * Created on 24 July 2003, 12:24
 */

package gnmed.test;
import junit.framework.*;
import java.util.*;
/**
 *
 * @author  sjtan
 */
public class TestCSVLoader extends TestCase  {
    
    /** Creates a new instance of TestCSVLoader */
    public TestCSVLoader() {
    }
    
    
    
    public void testInit() throws Exception {
        PostcodeCSVToGISLoader loader = new PostcodeCSVToGISLoader();
        
        loader.initFile();
        loader.readHeadings();
        int n = 5;
        assertTrue(loader.headings.length > n);
        assertTrue( loader.headMap.size() > n);
        Set s = new TreeSet();
        for (int i = 0 ; i < n ; ++i) {
            s.add( new Integer(i));
        }
        
        // assert all numbers up to n are entries in map.
        Iterator j = loader.headMap.keySet().iterator();
        while(j.hasNext()) {
            s.remove(loader.headMap.get(j.next()));
        }
        assertTrue(s.size() == 0);
        
        loader.showHeadings();
        assertTrue( loader.hasHeading(loader.CAT));
        assertTrue( loader.hasHeading(loader.URB));
        assertTrue( loader.hasHeading(loader.PCODE));
        assertTrue( loader.hasHeading(loader.STATE));
        
        
        loader.load();
        HibernateInit.setExported(true);
        
    }
    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) throws Exception {
        HibernateInit.initGmIdentityOnly();
        HibernateInit.exportDatabase();
        TestSuite suite = new TestSuite();
        suite.addTestSuite(TestCSVLoader.class);
        junit.textui.TestRunner.run(suite);
    }
    
}
