/*
 * HealthSummaryQuickAndDirty01.java
 *
 * Created on September 18, 2004, 1:07 PM
 */

package org.gnumed.testweb1.data;
import java.sql.*;
import java.util.*;
import org.apache.commons.beanutils.ResultSetDynaClass;
import org.apache.commons.beanutils.ResultSetIterator;
import org.apache.commons.beanutils.DynaProperty;
import org.apache.commons.beanutils.DynaBean;
import org.apache.commons.beanutils.DynaClass;
import org.apache.commons.beanutils.BasicDynaClass;
import org.apache.commons.beanutils.BasicDynaBean;
import org.apache.commons.beanutils.MutableDynaClass;
import org.apache.commons.beanutils.PropertyUtils;

/**
 *
 * @author  sjtan
 */
public class HealthSummaryQuickAndDirty01 implements HealthSummary01 {
    Long identityId;
    List healthIssues, episodes, encounters, vaccinations, medications, allergys,
    narratives, lab_requests, test_results, referrals;
    Map mapEpisodes, mapHI, emap;
    DataObjectFactory dof ;
    /** Creates a new instance of HealthSummaryQuickAndDirty01 */
    public HealthSummaryQuickAndDirty01(DataObjectFactory dof,
    Long  patientId,
    Map vaccines,
    ResultSet healthIssuesRS,
    ResultSet episodesRS,
    ResultSet  encountersRS,
    ResultSet  vaccinationsRS,
    ResultSet medicationsRS,
    ResultSet allergyRS,
    ResultSet narrativeRS,
    ResultSet    lab_requestRS,
    ResultSet test_resultRS,
    ResultSet referralRS ) {
        this.dof = dof;
        identityId =  patientId;
        try {
            
            allergys = getListOfDynaBeansFromResultSet(allergyRS);
            
            healthIssues = getListOfDynaBeansFromResultSet(healthIssuesRS);
            constructHealthIssues();
            
            episodes = getListOfDynaBeansFromResultSet(episodesRS);
            
            medications = getListOfDynaBeansFromResultSet(medicationsRS);
            
            narratives= getListOfDynaBeansFromResultSet(narrativeRS);
            
            lab_requests = getListOfDynaBeansFromResultSet(lab_requestRS);
            
            test_results = getListOfDynaBeansFromResultSet(test_resultRS);
            
            referrals = getListOfDynaBeansFromResultSet(referralRS);
            
            vaccinations = getVaccinations(vaccinationsRS, vaccines);
            
            encounters = getListOfDynaBeansFromResultSet(encountersRS);
            
            
            
            constructEpisodes();
            
            constructEncounters();
            
            constructNarratives();
            
            sortEncounterRootItems();
            
        } catch (Exception e) {
            e.printStackTrace();
        }
        
        
    }
    
    void sortEncounterRootItems( ) {
        Iterator i = encounters.iterator();
        while (i.hasNext()) {
            ClinicalEncounter ce = (ClinicalEncounter) i.next();
            ce.sortRootItems(new HealthSummaryQuickAndDirty01.RootItemClinWhenComparator());
            
        }
    }
    
    void constructHealthIssues() {
        Iterator j = healthIssues.iterator();
        List newIssues = new ArrayList();
        mapHI = new HashMap();
        while (j.hasNext()) {
            DynaBean b = (DynaBean) j.next();
            HealthIssue hi = dof.createHealthIssue();
            hi.setDescription((String)b.get("description"));
            hi.setId( new Long( ((Integer)b.get("id")).longValue()));
            newIssues.add(hi);
            mapHI.put( hi.getId(), hi);
        }
        healthIssues = newIssues;
    }
    
    void constructEpisodes() {
        
        Iterator i = episodes.iterator();
        List newEpisodes = new ArrayList();
        mapEpisodes = new HashMap();
        while (i.hasNext()) {
            DynaBean b = (DynaBean) i.next();
            ClinicalEpisode ep = dof.createClinicalEpisode();
            ep.setDescription((String)b.get("description"));
            
            ep.setId( new Long( ((Integer)b.get("id")).longValue()));
            
            ep.setModified_when( new java.util.Date( (long) ( (java.sql.Timestamp)b.get("modified_when")).getTime()));
            Long hiId = new Long(((Number)b.get("fk_health_issue")).longValue());
            
            HealthIssue hi = (HealthIssue) mapHI.get(hiId);
            if (hi != null) {
                ep.setHealthIssue(hi);
                hi.setClinicalEpisode(hi.getClinicalEpisodes().length,ep); //add
            }
            newEpisodes.add(ep);
            mapEpisodes.put(ep.getId(), ep);
        }
        episodes = newEpisodes;
        
    }
    
    void constructEncounters() {
        
        emap = new HashMap();
        List newList = new ArrayList();
        for (int i = 0; i < encounters.size(); ++i) {
            
            DynaBean b = (DynaBean) encounters.get(i);
            ClinicalEncounter encounter = dof.createClinicalEncounter();
            try {
                encounter.setId( new Long(((Number)b.get("id")).longValue()));
                encounter.setDescription((String)b.get("description"));
                encounter.setStarted((java.util.Date) b.get("started"));
                encounter.setLastAffirmed((java.util.Date) b.get("last_affirmed"));
                emap.put(encounter.getId(), encounter);
                newList.add(encounter);
            } catch(Exception e) {
                e.printStackTrace();
            }
        }
        
        Collections.sort(newList, new HealthSummaryQuickAndDirty01.EncounterStartedComparator() );
        encounters = newList;
    }
    
    void constructNarratives() {
        List newNarratives = new ArrayList();
        Iterator j = narratives.iterator();
        int i2 = 0;
        while (j.hasNext()) {
            DynaBean nb = (DynaBean) j.next();
            
            ClinNarrative narrative = dof.createEntryClinNarrative();
            
            
            try {
                narrative.setAoe(((Boolean)nb.get("is_aoe")).booleanValue());
                narrative.setRfe(((Boolean)nb.get("is_rfe")).booleanValue());
                setCommonRootItemAttributes(narrative, nb);
                newNarratives.add(narrative);
                linkRootItem( narrative, nb, i2++, "narrative");
            } catch(Exception e) {
                e.printStackTrace();
            }
            
            
        }
        
        narratives = newNarratives;
        
        
        
    }
    
    void setCommonRootItemAttributes( ClinRootItem rootItem, DynaBean nb) {
        rootItem.setNarrative((String)nb.get("narrative"));
        rootItem.setId( new Long( ((Integer)nb.get("pk")).longValue() ));
        rootItem.setSoapCat( ((String)nb.get("soap_cat")) );
        rootItem.setClin_when( (java.util.Date) nb.get("clin_when"));
    }
    
    void linkRootItem(ClinRootItem rootItem, DynaBean dynaRootItem ,int index, String childName )
    throws NoSuchMethodException,  IllegalAccessException , java.lang.reflect.InvocationTargetException {
        Long id_e =new Long( ((Integer)dynaRootItem.get("fk_encounter")).longValue());
        Long id_episode = new Long( ((Integer)dynaRootItem.get("fk_episode")).longValue());
        
        rootItem.setEncounter((ClinicalEncounter)emap.get( id_e ));
        rootItem.setEpisode((ClinicalEpisode)mapEpisodes.get(id_episode) );
        // set the clinical encounter object to contain the specific type of root item
        PropertyUtils.setIndexedProperty(rootItem.getEncounter(), childName, index, rootItem);
        
    }
    
    
    class RootItemClinWhenComparator implements  Comparator {
        
        public int compare(Object obj, Object obj1) {
            ClinRootItem c1, c2;
            c1 = (ClinRootItem)obj;
            c2 = (ClinRootItem)obj1;
            if (c1 == null) return -1;
            if (c2 == null) return 1;
            return c1.getClin_when().compareTo(c2.getClin_when());
        }
    }
    class EncounterStartedComparator implements Comparator {
        
        public int compare(Object obj, Object obj1) {
            ClinicalEncounter ce1,ce2;
            ce1 = (ClinicalEncounter) obj;
            ce2 = (ClinicalEncounter) obj1;
            if (ce1 == null) return -1;
            if (ce2 == null) return 1;
            return ce1.getStarted().compareTo(ce2.getStarted());
        }
        
    }
    
    public List getHealthIssues() {
        return healthIssues;
    }
    
    private List getHealthIssues(ResultSet rs )  throws java.sql.SQLException{
        List l = new ArrayList();
        while (rs.next()) {
            HealthIssue issue = dof.createHealthIssue();
            issue.setId( new Long( (long) rs.getInt("id")));
            issue.setDescription(rs.getString("description"));
            l.add(issue);
        }
        return l;
    }
    
    private List getVaccinations( ResultSet rs, Map vaccines)  throws java.sql.SQLException{
        List l = new ArrayList();
        while (rs.next()) {
            Vaccination vaccination = dof.createVaccination(
            new Long(rs.getInt("pk_item")),
            new Integer( rs.getInt("fk_vaccine")),
            rs.getString("site"),
            rs.getString("batch_no"),
            rs.getTimestamp("clin_when") , vaccines);
            l.add(vaccination);
            
        }
        return l;
        
    }
    
    /** gets a List of Dynabeans from a result set.
     *  this is from the example in the Apache documentation
     */
    private List getListOfDynaBeansFromResultSet(ResultSet rs) throws IllegalAccessException, java.sql.SQLException, InstantiationException, java.lang.reflect.InvocationTargetException, java.lang.NoSuchMethodException{
        ArrayList results = new ArrayList(); // To hold copied list
        ResultSetDynaClass rsdc = new ResultSetDynaClass(rs);
        DynaProperty properties[] = rsdc.getDynaProperties();
        BasicDynaClass bdc =
        new BasicDynaClass("foo", BasicDynaBean.class,
        rsdc.getDynaProperties());
        rs.beforeFirst();
        Iterator rows = rsdc.iterator();
        while (rows.hasNext()) {
            DynaBean oldRow = (DynaBean) rows.next();
            System.out.println( "got oldRow" + oldRow);
            PropertyUtils.setDebug(4);
            DynaBean newRow = bdc.newInstance();
            PropertyUtils.copyProperties(newRow, oldRow);
            results.add(newRow);
        }
        return results;
    }
    
    /*
    private void loadAllergies() {
        allergyRS.beforeFirst();
        allergys = getListOfDynaBeansFromResultSet(allergyRS);
    }
     
    private Allergy loadAllergy() {
        Allergy a = dof.createAllergy();
        a.setDefinite(allergyRS.getBoolean("definite"));
        a.setGenerics(allergyRS.getString("generics"));
        a.setSubstance(allergyRS.getString("substance"));
        a.setSoapCat(allergyRS.getString("soap_cat").charAt(0));
        return a;
    }
     
     
     */
    public List getAllergys() {
        
        return allergys;
    }
    
    
    public Long getIdentityId() {
        return identityId;
    }
    
    public List getMedications() {
        
        return medications;
    }
    
    public List getVaccinations() {
        
        return vaccinations;
    }
    
    public List getClinEpisodes() {
        return episodes;
    }
    
    public List getEncounters() {
        System.err.println(" Encounters = " + encounters + "size=" + encounters.size());
        return encounters;
    }
    
    public void setEncounters(List encounters) {
    }
    
    public boolean hasHealthIssue(HealthIssue issue) {
        Iterator j = healthIssues.iterator();
        while (j.hasNext()) {
            HealthIssue issue2 = (HealthIssue) j.next();
            if (issue2.getId().equals(issue.getId() ) ) {
                return true;
            }
        }
        return false;
    }
    
    public boolean addHealthIssue(HealthIssue issue) {
        
        addEpisodes( issue.getClinicalEpisodes() );
        return healthIssues.add(issue);
        
    }
    
    public void addEpisodes( ClinicalEpisode[] es) {
        for ( int i = 0; i < es.length; ++i ) {
            getClinEpisodes().add(es[i]);
        
        }
    }
    
}
