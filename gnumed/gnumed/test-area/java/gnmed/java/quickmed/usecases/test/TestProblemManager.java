/*
 * TestProblemManager.java
 *
 * Created on 11 August 2003, 10:11
 */

package quickmed.usecases.test;
import org.drugref.*;
import net.sf.hibernate.*;
import net.sf.hibernate.type.*;

import java.util.logging.*;
import java.util.*;
import java.text.DateFormat;

import gnmed.test.HibernateInit;


import org.drugref.disease_code;
import org.gnumed.gmIdentity.*;
import org.gnumed.gmClinical.*;
/**
 *
 * @author  sjtan
 */
public class TestProblemManager {
     static Logger logger = Logger.global;
    private static TestProblemManager manager = new TestProblemManager();
    
    public static TestProblemManager instance() {
        return manager;
    }
    
    /** Creates a new instance of TestProblemManager */
    private TestProblemManager() {
        try{
         HibernateInit.initAll();
        } catch(Exception e) {
            e.printStackTrace();
        }
    }
    
    public List findDiseaseCodeByDescription( String description) throws Exception {
        List list = null;
        Session sess = null;
        if ( description.trim().length() < 3)
            return list;
        try {
            sess =  HibernateInit.openSession();
            list  =
            sess.find("select dc from disease_code dc where dc.description like ?",
               "%"+description+"%", Hibernate.STRING);
        } catch (Exception e) {
             e.printStackTrace();
        } finally {
            sess.close();
        }
        logger.info("found disease_codes = "  + list.size());
        return list;
  
    }
    
    static DateFormat formatter = DateFormat.getDateInstance(DateFormat.SHORT);
    
    public clin_diagnosis createProblem( identity id, Date date, disease_code code) {
         clin_health_issue issue = new clin_health_issue();
          clin_diagnosis diagnosis = createDiagnosis(date, code);
          issue.addClin_issue_component(diagnosis);
          id.addClin_health_issue(issue);
          return diagnosis;
    }
    
    public clin_diagnosis createDiagnosis(  Date date, disease_code code) {
        clin_diagnosis diagnosis = new clin_diagnosis();
         diagnosis.setApprox_start(formatter.format(date));
           diagnosis.setText(code.getDescription());
          code_ref ref = new code_ref();
          ref.setDisease_code(code);
          diagnosis.setCode_ref(ref);
          return diagnosis;
    }
    
    public clin_diagnosis updateProblem( identity id, Date date, disease_code code , clin_diagnosis oldDiagnosis) {
        Collection c = id.getClin_health_issues();
        Iterator i = c.iterator();
        while(i.hasNext()) {
            clin_health_issue issue = (clin_health_issue) i.next();
            if (issue.getClin_issue_components().contains(oldDiagnosis) ) {
                issue.removeClin_issue_component(oldDiagnosis);
                clin_diagnosis d = createDiagnosis(date, code);
                issue.addClin_issue_component(d);
                return d;
            }
        }
        return createProblem(id, date, code);
    }
}
