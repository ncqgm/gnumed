/*
 * TestAccountabilityParty.java
 *
 * Created on 01 July 2003, 14:04
 */
package xgmed.test;
import cirrus.hibernate.*;
import cirrus.hibernate.type.Type;
import cirrus.hibernate.tools.SchemaExport;
// hibernate2
//import cirrus.hibernate.cfg.Configuration;
//import net.sf.hibernate.*;
//import net.sf.hibernate.cfg.Configuration;
//import net.sf.hibernate.type.*;
//import net.sf.hibernate.tool.hbm2ddl.SchemaExport;

import xgmed.domain.accountability.*;
import xgmed.domain.planning.*;
import xgmed.domain.planning.resource.*;
import xgmed.domain.common.*;
import xgmed.domain.observation.*;

import junit.framework.*;
import java.util.*;
/**
 *
 * @author  sjtan
 */
public class TestAccountabilityParty extends AbstractTestCase {
    
    
  
    /** Creates a new instance of TestAccountabilityParty */
    public TestAccountabilityParty() {
        super();
    }
    
   
    int completed = 0;
    synchronized int getCompleted() {
        return completed;
    }
    
    synchronized void incrementCompleted() {
        ++completed;
    }
    
    public void testPerson() throws Exception {
        createOnePerson();
        printAnyPersons();
    }
    
    
  
    
   
    public void testMultipleTelephones() throws Exception {
        Session s = sessions.openSession();
//        xgmed.helper.SessionSaver visitor = new xgmed.helper.SessionSaver(s);
        Person p = createPersonWithMultiTelephones();
        p.addPartyType(getPartyType(PATIENT));
        assertPartyTypesExist(p);
        assertTelephonesExist(p);
//        p.accept(visitor);
        s.save(p);
        s.flush();
        s.connection().commit();
        String first = p.getFirstNames();
        String last = p.getLastNames();
        Person p2 = findPerson(s, last, first);
        assertTrue( p2.getLastNames().equals(p.getLastNames()));
        assertTrue( p2.getBirthdate().getTime() == p.getBirthdate().getTime());
        assertPartyTypesExist(p);
         assertTelephonesExist(p);
       assertPartyTypesExist(p);
         assertTelephonesExist(p2);
       // s.close();
        printAnyPersons();
    }
    
    public void testMultiThreadedPersons() throws Exception {
        String number = System.getProperty("test.persons.number", "200");
        int n = Integer.parseInt(number);
        //        n = 1;
        Date d = new Date();
        for (int i = 0; i < n ; ++i) {
            Runnable r = new Runnable() {
                int backoff = 100;
                public void run() {
                    try {
                        Thread.sleep(backoff);
                        System.out.print( completed + " ");
                        Session s = sessions.openSession();
//                        xgmed.helper.SessionSaver visitor = new xgmed.helper.SessionSaver(s);
                        Person p = createPersonWithMultiTelephones();
//                        p.accept(visitor);
                        s.save(p);
                        s.flush();
                        
                        s.connection().commit();
                        s.close();
                        
                    } catch (Exception e) {
                        // e.printStackTrace();
                        
                        backoff += backoff /2;
                        // run();
                    }
                    incrementCompleted();
                    synchronized(this) {
                        this.notifyAll();
                    }
                }
            };
            new Thread(r).start();
        }
        synchronized(this) {
            while ( getCompleted() < n) {
                try {
                    wait(100);
                } catch (Exception e) {
                    System.out.println(e);
                    System.out.println("Completed = " + getCompleted());
                }
            }
        }
        printAnyPersons();
        Session s = getSessions().openSession();
        System.out.println("Time for "+n+" persons = " + (new Date().getTime() - d.getTime() ) );
        List people = s.find("from p in class xgmed.domain.accountability.Person");
        List telephones = s.find("from t in class xgmed.domain.accountability.Telephone");
        assertTrue( "There seems to be only one telephone per person",  telephones.size() > 4 * people.size() / 3);
    }
    
   
    String get_QueryString_For_AccountabilityType_By_PartyTypes(String commissionerTypeDescription, String responsibleTypeDescription ) {
        //        return "from a in class xgmed.domain.accountability.AccountabilityType";
        StringBuffer qbuf = new StringBuffer();
        qbuf.append("Select a from a in class xgmed.domain.accountability.AccountabilityType ,");
        qbuf.append("   doc in class xgmed.domain.accountability.PartyType,  ");
        qbuf.append("   pat in class xgmed.domain.accountability.PartyType  ");
        qbuf.append("   where doc.description like '");
        qbuf.append(responsibleTypeDescription);
        qbuf.append("%' and pat.description  like '");
        qbuf.append(commissionerTypeDescription);
        qbuf.append("%'");
        qbuf.append("   and doc in a.responsibles.elements");
        qbuf.append(" and pat in a.commissioners.elements");
        System.out.println("*****  Search string  =" +qbuf.toString());
        return qbuf.toString();
        
    }
    
    
    
    public void  testPartyType() throws Exception {
        s = sessions.openSession();
        // create a patient party type.
        Transaction t = s.beginTransaction();
        PartyType patientType =  createPartyType( PATIENT) ;
        PartyType doctorType = createPartyType(DOCTOR); 
        AccountabilityType accountType = createAccountabilityType( "primary care consultation",patientType,  doctorType);
        s.save(patientType);
        s.save(doctorType);
        s.save(accountType);
        t.commit();
        
        Person patient = createPersonWithMultiTelephones();
        patient.addPartyType(patientType);
        Person doctor = createPersonWithMultiTelephones();
        doctor.addPartyType(doctorType);
//        xgmed.helper.SessionSaver saveVisitor = new xgmed.helper.SessionSaver(s);
//        patient.accept(saveVisitor);
//        doctor.accept(saveVisitor);
        s.save(doctor);
        s.save(patient);
        t.commit();
        List accountabilityTypes =  s.find(get_QueryString_For_AccountabilityType_By_PartyTypes("patient", "doctor"));
        assertTrue( "No accountability types were saved", accountabilityTypes.size() > 0);
       // assertTrue( "More than one accountability type found", accountabilityTypes.size() == 1);
        AccountabilityType  accType = (AccountabilityType) accountabilityTypes.get(0);
        Accountability acc = createAccountability( accType,  patient, doctor);
        s.save(acc);
        s.update(patient);
        s.update(doctor);
        t.commit();
         printPerson(patient);
         printPerson(doctor);
        
    }
    
    public void testObservation() throws Exception {
        s = getSessions().openSession();
        PhenomenonType ageType = new PhenomenonType();
        ageType.setDescription("age");
        
        PhenomenonType sexType = new PhenomenonType();
        sexType.setDescription("sex");
        Phenomenon male = new Phenomenon();
        male.setDescription("male");
        Phenomenon female = new Phenomenon();
        female.setDescription("female");
        sexType.addPhenomenon(male);
        sexType.addPhenomenon(female);
        
        s.save(ageType);
        s.save(sexType);
        
        Measurement age = new Measurement();
        Quantity qAge = new Quantity();
        Unit yearUnit = new Unit();
        yearUnit.setLabel("years");
        qAge.setUnit(yearUnit);
        
                
        Person p1 = new Person();
        p1.setFirstNames("Bill");
        p1.setLastNames("Smith");
        Calendar cal = Calendar.getInstance();
        cal.set(1967, 12,15);
        p1.setBirthdate(cal.getTime());
        
        
    }
    
    public static TestSuite suite() {
        TestSuite suite= new TestSuite();
        suite.addTestSuite(TestAccountabilityParty.class);
        return suite;
    }
      /** run test suite */
    public static void main(String args[]) {
        
        junit.textui.TestRunner.run(suite());
    }
   
    
}
