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
        setDiagnosisValues( diagnosis, date, code);
        return diagnosis;
    }
    
    
    /**
     *may need to tidy and remove old links as well
     */
    void setDiagnosisValues( clin_diagnosis diagnosis, Date date, disease_code code) {
           diagnosis.setApprox_start(formatter.format(date));
           diagnosis.setText(code.getDescription());
           code_ref oldref = diagnosis.getCode_ref();
          code_ref ref = new code_ref();
          ref.setDisease_code(code);
          diagnosis.setCode_ref(ref);
          
    }
    
    
    /** 
     * simplistic removal of diagnosis;     Should probably be implemented with a non-active flag
     */
    public void removeDiagnosis( identity id, clin_diagnosis diagnosis) throws Exception {
        Iterator i = id.getClin_health_issues().iterator();
        while (i.hasNext()) {
             clin_health_issue issue = (clin_health_issue) i.next();
             if (issue.getClin_issue_components().contains(diagnosis) ) {
                    id.removeClin_health_issue(issue);
//                    IdentityManager.instance().save(id);
                    return;
             }
        }
    }
    
    
    
    public clin_diagnosis updateProblem( identity id, Date date, disease_code code , clin_diagnosis oldDiagnosis) {
        Collection c = id.getClin_health_issues();
        Iterator i = c.iterator();
        while(i.hasNext()) {
            clin_health_issue issue = (clin_health_issue) i.next();
            if (issue.getClin_issue_components().contains(oldDiagnosis) ) {
                 setDiagnosisValues(oldDiagnosis, date, code);
                 return oldDiagnosis;
            }
        }
        return createProblem(id, date, code);
    }
}
