/*
 * TestClinHealthIssue.java
 *
 * Created on 26 July 2003, 10:39
 */

package gnmed.test;

import org.gnumed.gmIdentity.*;
import org.gnumed.gmGIS.*;
import org.gnumed.gmClinical.*;
import org.drugref.disease_code;


import net.sf.hibernate.*;
import junit.framework.*;
import java.util.*;
import java.util.logging.*;

/**
 *
 * @author  sjtan
 */
public class TestClinHealthIssue  extends TestCase {
    static Random r = new Random();
    static final String[] conditions = { "diabetes", "myocardial infarction", "stroke", "nicotine", "hypertension",
    "asthma", "anxiety", "depression", "obstructive",
    "cancer",  "ulcer", "esophagitis",
    "gout", "arthritis", "failure"
    };
    
    TestIdentityAddress identitySource;
    /** Creates a new instance of TestClinHealthIssue */
    public TestClinHealthIssue() {
    }
    void init() throws Exception {
        identitySource = new TestIdentityAddress();
    }
    
    public static String createSQLSubstr(String substr) {
        StringBuffer sb = new StringBuffer();
        sb.append('%');
        sb.append(substr);
        sb.append('%');
        return sb.toString();
    }
    
    public static disease_code findDiseaseCode(String substr) throws Exception  {
        Session sess = HibernateInit.openSession();
        Logger.global.info("Looking for issue" + substr);
        List l = sess.find("from code in class org.drugref.disease_code where code.description like ?",
        substr, Hibernate.STRING);
        assertTrue(l.size() > 0);
        disease_code code = (disease_code)l.get(r.nextInt((int)l.size()));
        HibernateInit.closeSession(sess);
        return code;
    }
    
    public static clin_health_issue createClinHealthIssue(String substr) throws Exception  {
        clin_health_issue issue = new clin_health_issue();
        disease_code code = findDiseaseCode(createSQLSubstr(substr));
        clin_diagnosis diagnosis = new clin_diagnosis();
        code_ref ref = new code_ref();
        ref.setDisease_code(code);
        diagnosis.setCode_ref(ref);
        issue.addClin_issue_component(diagnosis);
        issue.setDescription(diagnosis.getCode_ref().getDisease_code().getDescription());
        diagnosis.setApprox_start(new Integer( 1980 + r.nextInt(20)).toString() );
        return issue;
        
    }
    
    clin_health_issue createRandomHealthIssue() throws Exception {
        return createClinHealthIssue(conditions[r.nextInt(conditions.length)]);
    }
    
    identity addRandomNumberOfRandomHealthIssues(identity id) throws Exception {
        int n = r.nextInt(6) + 1; // has to be one or More ?
        for (int i = 0; i < n; ++i) {
            id.addClin_health_issue(createRandomHealthIssue());
        }
        return id;
    }
    
    
    public identity createTestIdentityWithHealthIssues() throws Exception {
        if (identitySource == null)
            init();
        identity id = identitySource.createPersonWithAddresses(r.nextInt(3)+1);
        id = addRandomNumberOfRandomHealthIssues(id);
        return id;
    }
    
    public static void printIdentities(List l) throws Exception {
        for (int i = 0; i < l.size(); ++i) {
            identity id = (identity) l.get(i);
            DomainPrinter.getInstance().printIdentity(System.out, id);
        }
    }
    
    public  List createManyPersonsWithIssues() throws Exception {
        int n = r.nextInt(20) + 20;
        List l = new ArrayList();
        for (int i = 0; i <n ; ++i) {
            identity id = createTestIdentityWithHealthIssues();
            l.add(id);
        }
        return l;
    }
    public void testCreateIdentityHealthIssue() throws Exception {
        
        printIdentities(createManyPersonsWithIssues());
    }
    
    public int countIdentitiesWithHealthIssues() throws Exception {
        Session sess = HibernateInit.openSession();
        java.sql.ResultSet rs = sess.
        connection().
        createStatement().
        executeQuery("select count(distinct(identity)) from clin_health_issue");
        int count = 0;
        if (rs.next())
            count = rs.getInt(1);
        HibernateInit.closeSession(sess);
        return count;
    }
    
    public void testStoreIdentityHealthIssue() throws Exception {
        Session sess = HibernateInit.openSession();
        int preCount = countIdentitiesWithHealthIssues();
        List l = createManyPersonsWithIssues();
        
        Session sess2 = HibernateInit.openSession();
        for (int i = 0; i < l.size(); ++i) {
            sess2.save(l.get(i));
        }
        sess2.flush();
        sess2.connection().commit();
        
        
        boolean notFound = false;
        
        int postCount = countIdentitiesWithHealthIssues();
        Logger.global.info(java.text.MessageFormat.format("identity with issue precount= {0}, postcount= {1}",new Object[] { new Integer(preCount), new Integer(postCount) } ) );
        
        assertTrue( "\npersons with issues before="+ new Integer(preCount).toString()+
        "\npersons with issues created" +new Integer((int)l.size()).toString() +
        "\npersons with issues after " +new Integer(postCount).toString() ,
        preCount + l.size() == postCount );
        
        List retrieveList = new ArrayList();
        for (int i = 0; i < l.size(); ++i) {
            retrieveList.add( ((identity)l.get(i)).getId());
        }
        l.clear();
        System.out.println("***********************************\n******************************* Retrieving ***********************\n");
        Session sess3 = HibernateInit.openSession();
        for (int i = 0 ; i < retrieveList.size(); ++i) {
            identity id2 = (identity) sess3.load( identity.class , (java.io.Serializable) retrieveList.get(i) );
            DomainPrinter.getInstance().printIdentity(System.out, id2);
        }
        HibernateInit.closeSession(sess3);
    }
    
    
    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) throws Exception {
        HibernateInit.initAll();
        
        TestSuite suite = new TestSuite();
        suite.addTestSuite(TestClinHealthIssue.class);
        junit.textui.TestRunner.run(suite);
        
    }
    
}
