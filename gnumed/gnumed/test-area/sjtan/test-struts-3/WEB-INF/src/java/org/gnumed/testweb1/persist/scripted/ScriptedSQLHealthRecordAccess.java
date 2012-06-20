/*
 * ScriptedSQLHealthRecordAccess.java
 *
 * Created on September 14, 2004, 10:54 PM
 */

package org.gnumed.testweb1.persist.scripted;

import java.lang.reflect.InvocationTargetException;
import java.security.Principal;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import javax.sql.DataSource;

import org.apache.commons.beanutils.PropertyUtils;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.gnumed.testweb1.data.Allergy;
import org.gnumed.testweb1.data.AllergyEntry;
import org.gnumed.testweb1.data.ClinNarrative;
import org.gnumed.testweb1.data.ClinRootItem;
import org.gnumed.testweb1.data.ClinicalEncounter;
import org.gnumed.testweb1.data.ClinicalEpisode;
import org.gnumed.testweb1.data.DataObjectFactory;
import org.gnumed.testweb1.data.EntryClinNarrative;
import org.gnumed.testweb1.data.EntryClinRootItem;
import org.gnumed.testweb1.data.EntryMedication;
import org.gnumed.testweb1.data.EntryVaccination;
import org.gnumed.testweb1.data.EntryVitals;
import org.gnumed.testweb1.data.HealthIssue;
import org.gnumed.testweb1.data.HealthRecord01;
import org.gnumed.testweb1.data.HealthSummary01;
import org.gnumed.testweb1.data.HealthSummaryQuickAndDirty01;
import org.gnumed.testweb1.data.Vaccination;
import org.gnumed.testweb1.data.Vaccine;
import org.gnumed.testweb1.data.Vitals;
import org.gnumed.testweb1.global.Algorithms;
import org.gnumed.testweb1.global.Util;
import org.gnumed.testweb1.persist.ClinicalDataAccess;
import org.gnumed.testweb1.persist.CredentialUsing;
import org.gnumed.testweb1.persist.DataObjectFactoryUsing;
import org.gnumed.testweb1.persist.DataSourceException;
import org.gnumed.testweb1.persist.DataSourceUsing;
import org.gnumed.testweb1.persist.HealthRecordAccess01;
import org.gnumed.testweb1.persist.ThreadLocalCredentialUsing;
import org.gnumed.testweb1.persist.scripted.gnumed.ClinRootInsert;
import org.gnumed.testweb1.persist.scripted.gnumed.MedicationSaveScript;
import org.gnumed.testweb1.persist.scripted.gnumed.clinroot.ClinRootInsertV01;
import org.gnumed.testweb1.persist.scripted.gnumed.medication.MedicationSaveScriptV01;

/**
 * 
 * @author sjtan
 * 
 * Notes: Important Identity l an episode is the same if it has the same name
 * and falls within a same time interval Episodes that have incorrect time
 * intervals may not be regarded as the same episode if the clin_when properties
 * are differently set.
 * 
 * Health Issues are the same if the names are the same or are matched by a
 * matching algorithm in globals.Algorithm .
 * 
 *  
 */
public class ScriptedSQLHealthRecordAccess implements HealthRecordAccess01,
		DataSourceUsing, DataObjectFactoryUsing , CredentialUsing {
	
	private ClinRootInsert clinRootInsert = new ClinRootInsertV01();
	private MedicationSaveScript medicationSaveScript = new MedicationSaveScriptV01();
	
	DataSource dataSource;

	DataObjectFactory factory;

	// THIS MIGHT NEED TO BE A SEPARATE SERVICE, in order for multi-thread to
	// work.
	//
	private Map accessedRecords = new HashMap();

	/**
	 * change the fields for aliasing , if field names change
	 */

	private ClinicalDataAccess clinicalDataAccess;

	private static final String HEALTH_ISSUE_ATTRIBUTES = "hi.id as id, hi.description as description ";

	private static final String CLIN_EPISODE_ATTRIBUTES = "id as id, modified_when as modified_when, description as description";

	private static final String CLIN_ROOT_ITEM_ATTRIBUTES = "pk_item as id, clin_when as clin_when , soap_cat as soap_cat, narrative as narrative";

	private static final String CLIN_NARRATIVE_ATTRIBUTES = CLIN_ROOT_ITEM_ATTRIBUTES
			+ ", is_rfe as is_rfe, is_aoe as is_aoe";

	static double WORD_THRESHOLD = 0.7;

	static double MATCHED_WORDCOUNT_THRESHHOLD = 0.7;

	static long SAME_EPISODE_INTERVAL = 5 * 1000; // 5 seconds

	static Log log = LogFactory.getLog(ScriptedSQLHealthRecordAccess.class);

	static ThreadLocalCredentialUsing threadCredential;
	static {
	    threadCredential = new ThreadLocalCredentialUsing();
	}
	
	/** Creates a new instance of ScriptedSQLHealthRecordAccess */
	public ScriptedSQLHealthRecordAccess() {
	}

	public Map getAccessedRecords() {
		return Collections.synchronizedMap(accessedRecords);
	}

	public HealthRecord01 findHealthRecordByIdentityId(long patientId)
			throws DataSourceException {
		/*
		 * Map accessedRecords = getAccessedRecords(); if
		 * (accessedRecords.containsKey(new Long(patientId)) ) { return
		 * (HealthRecord01) accessedRecords.get(new Long(patientId)); }
		 *  
		 */
		Connection conn = null;
		try {
			conn = dataSource.getConnection();
			conn.rollback();
			Util.setSessionAuthentication(conn,(Principal)threadCredential.getCredential());
			conn.setReadOnly(true);

			ResultSet healthIssuesRS, episodesRS, encountersRS, vaccinationsRS, medicationsRS, allergyRS, narrativeRS, lab_requestRS, test_resultRS, referralRS, encounterTypeRS;

			ensureXLinkIdentityExists(conn, patientId);
			healthIssuesRS = getHealthIssueRS(conn, patientId);

			episodesRS = getClinEpisodesRS(conn, getIdsFromResultSet(
					healthIssuesRS, "id"), patientId);
			encountersRS = getClinEncountersRS(conn, patientId);
			long[] encounter_ids = getIdsFromResultSet(encountersRS, "id");

			vaccinationsRS = getVaccinationRS(conn, encounter_ids);
			medicationsRS = getMedicationRS(conn, encounter_ids);
			allergyRS = getAllergyRS(conn, encounter_ids);
			narrativeRS = getClinNarrativeRS(conn, encounter_ids);

			lab_requestRS = getLabRequestRS(conn, encounter_ids);
			test_resultRS = getTestResultRS(conn, encounter_ids);
			referralRS = getReferralRS(conn, encounter_ids);
			encounterTypeRS = getEncounterTypeRS(conn);
			Map vaccineMap = getVaccineMap();

			HealthSummary01 hs = new HealthSummaryQuickAndDirty01(
					getDataObjectFactory(), new Long(patientId), vaccineMap,

					healthIssuesRS, episodesRS, encountersRS, vaccinationsRS,
					medicationsRS, allergyRS, narrativeRS, lab_requestRS,
					test_resultRS, referralRS, encounterTypeRS);

			accessedRecords.put(new Long(patientId), getDataObjectFactory()
					.createHealthRecord(hs));
			return (HealthRecord01) accessedRecords.get(new Long(patientId));

		} catch (Exception e) {
		    e.printStackTrace();
			throw new DataSourceException(e);
		} finally {
		
				try {
					conn.close();
				} catch (Exception se) {
					throw new DataSourceException(se);
				}


		}

	}

	private Map getVaccineMap() throws DataSourceException {

		Map vaccMap = getClinicalDataAccess().getVaccineMap();
		return vaccMap;

	}

	private long[] getIdsFromResultSet(ResultSet rs, String idName)
			throws SQLException {
		List l = new ArrayList();
		rs.beforeFirst();
		while (rs.next()) {
			l.add(new Long(rs.getLong(idName)));
		}

		long[] l2 = new long[l.size()];
		for (int i = 0; i < l.size(); ++i) {
			Long lobj = (Long) l.get(i);
			l2[i] = lobj.longValue();
		}
		rs.beforeFirst();
		return l2;
	}

	private String idsToString(long[] ids) {
		StringBuffer sb = new StringBuffer();
		for (int i = 0; i < ids.length; ++i) {
			if (i > 0)
				sb.append(',');
			sb.append(Long.toString(ids[i]));
		}
		return sb.toString();
	}

	private ResultSet getRowsForIds(Connection conn, String selectString,
			long[] ids) throws SQLException {

		PreparedStatement stmt = conn.prepareStatement(selectString
				+ getIdSelectionWhereClause(ids));
		stmt.execute();
		return stmt.getResultSet();
	}

	/**
     * @param ids
     * @return
     */
    private String getIdSelectionWhereClause(long[] ids) {
        return ((ids.length == 0) ? "( null ) " : "(" + idsToString(ids)
        		+ ")");
    }

    private ResultSet getHealthIssueRS(Connection conn, long patientId)
			throws SQLException {
		String s = "select " + HEALTH_ISSUE_ATTRIBUTES
				+ " from clin_health_issue hi  where hi.id_patient =  ?";
		System.err.println("finding HI :" + s + " for id " + patientId);
		PreparedStatement stmt = conn.prepareStatement(s);
		stmt.setLong(1, patientId);
		stmt.execute();
		ResultSet rs = stmt.getResultSet();
		System.err.println("result set = " + rs);
		return rs;

	}

	private ResultSet getClinEpisodesRS(Connection conn,
			long[] clin_health_issue_ids, long patientId) throws SQLException {
		    String stmt = 
				"select * from clin_episode where fk_health_issue  in  " + getIdSelectionWhereClause(
				clin_health_issue_ids) + " union select * from clin_episode where fk_patient = " + Long.toString(patientId);
		    Statement s=  conn.createStatement();
		    return s.executeQuery(stmt);
		    
	}

	private ResultSet getClinEncountersRS(Connection conn, long patientId)
			throws SQLException {
		PreparedStatement stmt = conn
				.prepareStatement("select * from clin_encounter where fk_patient =  ?   ");
		stmt.setLong(1, patientId);
		stmt.execute();
		return stmt.getResultSet();

	}

	private ResultSet getEncounterTypeRS(Connection conn) throws SQLException {
		PreparedStatement stmt = conn
				.prepareStatement("select * from encounter_type");
		stmt.execute();
		return stmt.getResultSet();

	}

	private ResultSet getClinRootItemRS(Connection conn,/* String attributeList, */
	String subtype, long[] encounter_ids) throws SQLException {
		return getRowsForIds(conn, "select * from " + subtype
				+ " where fk_encounter in ", encounter_ids);

	}

	private ResultSet getAllergyRS(Connection conn, long[] encounter_ids)
			throws SQLException {
		return getClinRootItemRS(conn, /* ALLERGY_ATTRIBUTES, */"allergy",
				encounter_ids);
	}

	private ResultSet getVaccinationRS(Connection conn, long[] encounter_ids)
			throws SQLException {
		return getClinRootItemRS(conn,/* VACCINATION_ATTRIBUTES, */
		"vaccination", encounter_ids);
	}

	private ResultSet getClinNarrativeRS(Connection conn, long[] encounter_ids)
			throws SQLException {
		return getClinRootItemRS(conn, "clin_narrative", encounter_ids);
	}

	private ResultSet getLabRequestRS(Connection conn, long[] encounter_ids)
			throws SQLException {
		return getClinRootItemRS(conn, "lab_request", encounter_ids);
	}

	private ResultSet getTestResultRS(Connection conn, long[] encounter_ids)
			throws SQLException {
		return getClinRootItemRS(conn, "test_result", encounter_ids);
	}

	private ResultSet getReferralRS(Connection conn, long[] encounter_ids)
			throws SQLException {
		return getClinRootItemRS(conn, "referral", encounter_ids);
	}

	private ResultSet getMedicationRS(Connection conn, long[] encounter_ids)
			throws SQLException {
		return getClinRootItemRS(conn, "clin_medication", encounter_ids);
	}

	private ResultSet getClinDiagRS(Connection conn, long[] clin_narrative_ids)
			throws SQLException {
		return getRowsForIds(conn,
				"select * from clin_diag where fk_narrative in ",
				clin_narrative_ids);
	}

	private ClinicalEncounter fromRow(ResultSet rs) throws SQLException {
		return null;
	}

	public void save(HealthRecord01 healthRecord) throws DataSourceException {
	}

	public DataSource getDataSource() {
		return dataSource;
	}

	public void setDataSource(DataSource ds) {
		this.dataSource = ds;
	}

	public DataObjectFactory getDataObjectFactory() {
		return factory;
	}

	public void setDataObjectFactory(DataObjectFactory dataObjectFactory) {
		this.factory = dataObjectFactory;
	}

	public ClinicalDataAccess getClinicalDataAccess() {
		return clinicalDataAccess;
	}

	public void setClinicalDataAccess(ClinicalDataAccess cda) {
		clinicalDataAccess = cda;
	}

	/**
	 * saves a clinical encounter and it's elements. ClinNarrative elements
	 * which have empty narrative fields are not saved.
	 */
	public void save(ClinicalEncounter encounter, HealthSummary01 summary,
			List nonFatalExceptions) throws DataSourceException {
		
		Connection conn = null;
		try {

			conn = getDataSource().getConnection();
			conn.rollback();
			Statement stmt0 = conn.createStatement();
			stmt0.execute("rollback;begin");
			Util.setSessionAuthentication(conn,(Principal)threadCredential.getCredential());
			

		//	conn.setAutoCommit(false);

			insertEncounter(encounter, summary, conn);
			conn.commit();

			List healthIssues = new ArrayList();
			
			

			/*
			 * EntryClinRootItem[] items = (EntryClinRootItem[]) encounter
			 * .getEntryRootItems(); resolveHealthIssueAndEpisode(summary, conn,
			 * healthIssues, items);
			 */
			// resolveHealthIssueAndEpisode(encounter,summary, conn);
			//       List[] itemLists = new List[] {
			//           encounter.getNarratives(), encounter.getAllergies()
			//       };
			//       removeEmptyNarratives(itemLists);
			int itemsAttached = 0;
			Map newIssues = new HashMap();
			itemsAttached = saveNewHealthIssues(encounter, summary,
			        nonFatalExceptions, conn, newIssues);
			
			linkNarratives(encounter,summary, nonFatalExceptions, conn, newIssues);
			
			itemsAttached += saveNamedEpisodes(encounter, summary,
			        	nonFatalExceptions, conn ,newIssues);

			
			itemsAttached += saveNarrativesCollection(encounter, summary,
					nonFatalExceptions, conn, newIssues);
			
			itemsAttached += saveAllergiesCollection(encounter, summary,
					nonFatalExceptions, conn);

			itemsAttached += saveVitalsCollection(encounter, summary,
					nonFatalExceptions, conn);

			itemsAttached += saveVaccinationsCollection(encounter, summary,
					nonFatalExceptions, conn);
			
			itemsAttached += saveMedicationCollection(encounter, summary,
					nonFatalExceptions, conn);
			
			if (nonFatalExceptions.size() > 0 ) {
			    Iterator i = nonFatalExceptions.iterator();
			    while (i.hasNext()) {
			        Exception exc = (Exception) i.next();
			        log.info("non fatal exception", exc);
			        
			    }
			}
			
			if (itemsAttached == 0) {
				removeEmptyEncounter(encounter, conn);
			}
			Statement stmt = conn.createStatement();
			stmt.execute("commit");
			conn.commit();
			

		} catch (Exception exception) {
			try {
			    Statement stmt = conn.createStatement();
			    stmt.execute("rollback;commit");
				conn.rollback();
				conn.commit(); 
			} catch (Exception e2) {
				e2.printStackTrace();
			}
			log.info(exception, exception);
			throw new DataSourceException("unexpected ", exception);
		} finally {
		    try {
                        conn.close();
		    } catch (Exception e) {
                log.error(e,e);
            }
		}

	}

	/**
     * @param encounter
	 * @param summary
     * @param nonFatalExceptions
     * @param conn
	 * @param newIssues
     * @return
     */
    private int saveNamedEpisodes(ClinicalEncounter encounter, HealthSummary01 summary, List nonFatalExceptions, Connection conn, Map newIssues) throws DataSourceException, SQLException{
        // TODO Auto-generated method stub
        List savedNamedEpisodes = new ArrayList();
        List narratives = encounter.getNarratives();
        Iterator i = narratives.iterator();
        while (i.hasNext()) {
            EntryClinNarrative n = (EntryClinNarrative) i.next();
            
            
            if (savedNamedEpisodes.contains(n.getEpisode()) ) {
                continue;
            }
            
            HealthIssue issue =  n.getEpisode().getHealthIssue();
          
            n.setEpisode(findOrCreateEpisode(conn,summary, n.getEpisode(), newIssues.get(issue.getDescription())!= null));
            newIssues.remove(issue.getDescription());
            savedNamedEpisodes.add(n.getEpisode());
            
        }
        return savedNamedEpisodes.size();
    }

    /**
     * @param encounter
     * @param summary
     * @param nonFatalExceptions
     * @param conn
     * @return
     */
    private int saveNewHealthIssues(ClinicalEncounter encounter, HealthSummary01 summary, List nonFatalExceptions, Connection conn, Map newHealthIssues) {
        
        int itemsAttached = 0;
		for (Iterator i = encounter.getNarratives().iterator(); i.hasNext();) {
			EntryClinNarrative narrative = (EntryClinNarrative) i.next();
			
			try {
			    log.info("Checking for NEW HEALTH ISSUE " + narrative.getHealthIssueName());
			    if (!"".equals(narrative.getHealthIssueName()) && 
			            narrative.getHealthIssueName() != null ) {
			        
			        HealthIssue issue = 
			            findExistingHealthIssue(narrative.getHealthIssueName(), summary);
					
					if (issue == null || issue.getId() == null) {
						issue = createNewHealthIssue(conn, narrative, summary);
						summary.addHealthIssue(issue);
						newHealthIssues.put(issue.getDescription(), issue);
						issue.addClinicalEpisode(narrative.getEpisode());
						//narrative.getEpisode().setHealthIssue(issue);
						setNarrativeTimeToNewHealthIssueOnset(narrative);
						
						itemsAttached++;
					}
					
			    }
				

			} catch (Exception e) {
				log.info("Save new health issue error " + e, e);
				nonFatalExceptions.add(e);
			}
		}
		return itemsAttached;
    }

    /**
     * @param encounter
     * @param conn
     * @throws SQLException
     * @throws DataSourceException
     */
    private void removeEmptyEncounter(ClinicalEncounter encounter, Connection conn) throws SQLException, DataSourceException {
        conn.rollback();
        Statement stmt = conn.createStatement();
        stmt.execute("delete from clin_encounter where id="
        		+ encounter.getId());
        conn.commit();
        throw new DataSourceException(
        		"No items attached. Encounter deleted" );
    }

    /**
	 * @param encounter
	 * @param summary
	 * @param s1
	 * @param conn
	 * @return @throws
	 *         DataSourceException
	 * @throws SQLException
	 */
	private Long insertEncounter(ClinicalEncounter encounter,
			HealthSummary01 summary,  Connection conn)
			throws DataSourceException, SQLException {
//		this can cause deadlocking   
//		Integer idEncounter = getNextId(conn, "clin_encounter_id_seq");
	    String s1 = "insert into clin_encounter ( description, started, last_affirmed,  fk_patient) values ( ?, ?,?,  ? )";

		encounter.getDescription();

		java.util.Date started = nullToNow(encounter.getStarted());
		java.util.Date affirmed = nullToNow(encounter.getLastAffirmed());

		PreparedStatement insertEncounter = conn.prepareStatement(s1);
		insertEncounter.setString(1, encounter.getDescription());
		insertEncounter.setTimestamp(2, new Timestamp(started.getTime()));
		insertEncounter.setTimestamp(3, new Timestamp(affirmed.getTime()));
		insertEncounter.setObject(4, summary.getIdentityId());
		insertEncounter.execute();
		log.info("EXECUTED " + s1 + " with " + encounter.getDescription());
		encounter.setId(new Long( getLastId(conn, "clin_encounter_id_seq").intValue()));
		return encounter.getId();
		
		
	}
 
	/**
     * @param conn
     * @return
     * @throws SQLException
     */
    private Integer getLastId(Connection conn, String sequence) throws SQLException {
        Statement stmt = conn.createStatement();
		ResultSet rs = stmt.executeQuery("select currval('" + sequence + "')");
		if (!rs.next())
		    throw new SQLException("no currval found for "+sequence );
		Integer id =  new Integer (rs.getInt(1));
		log.info( "got from seq=" + sequence + " currval = " + id);
		return id;
    }

    /**
	 * @param encounter
	 * @param nonFatalExceptions
	 * @param conn
	 * @return
	 */
	private int saveNarrativesCollection(ClinicalEncounter encounter,
			HealthSummary01 summary, List nonFatalExceptions, Connection conn , Map newIssues) {
	    int itemsAttached = 0;
		for (Iterator i = encounter.getNarratives().iterator(); i.hasNext();) {
			EntryClinNarrative narrative = (EntryClinNarrative) i.next();
			
			if(!narrative.isEntered() )
			    continue;
			
			try {
			    
				 
				saveNarrative(conn, narrative);
				++itemsAttached;
			} catch (Exception e) {
				log.info("Save Narrative error " + e, e);
				nonFatalExceptions.add(e);
			}
		}
		return itemsAttached;
	}
	
	private void linkNarratives(ClinicalEncounter encounter,
			HealthSummary01 summary, List nonFatalExceptions, Connection conn , Map newIssues) {
	    int itemsAttached = 0;
		for (Iterator i = encounter.getNarratives().iterator(); i.hasNext();) {
			EntryClinNarrative narrative = (EntryClinNarrative) i.next();
			
			if(!narrative.isEntered() &&
			        "".equals(Util.nullIsBlank(narrative.getEpisode().getDescription())))
			    continue;
			
			try {
			    	linkRootItem(conn, narrative, summary, newIssues.containsValue(narrative.getEpisode().getHealthIssue()));
			} catch (Exception e) {
				log.info("Save Narrative error " + e, e);
				nonFatalExceptions.add(e);
			}
		}
		
	}

	/**
     * @param newIssues
     * @param narrative
     */
    private boolean ensureEpisodeWithOnsetOfNewHealthIssue(Map newIssues, EntryClinNarrative narrative) {
        boolean firstNarrativeOnNewHealthIssue =false;
        if ( isNarrativeOfANewHealthIssue(newIssues, narrative)) {
            
            setNarrativeTimeToNewHealthIssueOnset(narrative);
            
            // don't need this with named episode check.
           // ensureNewHealthIssueHasNarrativeWithText(narrative);
            
            newIssues.remove(narrative.getHealthIssueName());
            
            firstNarrativeOnNewHealthIssue = true;
        }
        return firstNarrativeOnNewHealthIssue;
    }

    /**
     * @param narrative
     */
    private void ensureNewHealthIssueHasNarrativeWithText(EntryClinNarrative narrative) {
        if (!narrative.isEntered()) {
            narrative.setNarrative("initial narrative(auto) for health issue");
        }
    }

    /**
     * @param narrative
     */
    private void setNarrativeTimeToNewHealthIssueOnset(EntryClinNarrative narrative) {
        narrative.setClin_when( narrative.getHealthIssueStart());
    }

    /**
     * @param newIssues
     * @param narrative
     * @return
     */
    private boolean isNarrativeOfANewHealthIssue(Map newIssues, EntryClinNarrative narrative) {
        return newIssues.get(narrative.getHealthIssueName()) != null;
    }

    /**
	 * @param encounter
	 * @param summary
	 * @param nonFatalExceptions
	 * @param conn
	 * @return
	 */
	private int saveAllergiesCollection(ClinicalEncounter encounter,
			HealthSummary01 summary, List nonFatalExceptions, Connection conn) {
	    int itemsAttached =0;
	    boolean defaultAllergyEpisode = false;
		for (Iterator i = encounter.getAllergies().iterator(); i.hasNext();) {
			try {

				AllergyEntry allergy = (AllergyEntry) i.next();
				if (!allergy.isEntered())
					continue;
				if (!defaultAllergyEpisode) {
				    meetSchemaRequirementEpisode(encounter, summary, conn, "allergy entered: " + allergy.getSubstance() + " (autotext)");
				    defaultAllergyEpisode =true;
				}
				linkRootItem(conn, allergy, summary,false);
				saveAllergy(conn, allergy, summary);
				itemsAttached++;
			} catch (Exception e) {
				nonFatalExceptions.add(e);
			}
		}
		return itemsAttached;
	}

	/**
	 * @param encounter
	 * @param summary
	 * @param nonFatalExceptions
	 * @param conn
	 * @return
	 */
	private int saveVitalsCollection(ClinicalEncounter encounter,
			HealthSummary01 summary, List nonFatalExceptions, Connection conn) {
	    int itemsAttached =0;
		for (Iterator i = encounter.getVitals().iterator(); i.hasNext();) {
			try {
				EntryVitals entryVitals = (EntryVitals) i.next();
				if (entryVitals.isEntered()) {
					linkRootItem(conn, entryVitals, summary, false);
					saveVitals(conn, entryVitals, nonFatalExceptions);
					itemsAttached++;
				}
			} catch (Exception e) {
				nonFatalExceptions.add(e);
			}
		}
		return itemsAttached;
	}

	/**
	 * @param encounter
	 * @param summary
	 * @param nonFatalExceptions
	 * @return
	 * @throws SQLException
	 */
	private int saveVaccinationsCollection(ClinicalEncounter encounter,
			HealthSummary01 summary, List nonFatalExceptions, Connection conn) throws SQLException {
	    int itemsAttached =0;
	   try{
	    boolean defaultVaccEpisode = false;
	   
		for (Iterator i = encounter.getVaccinations().iterator(); i.hasNext();) {
			try {
				EntryVaccination v = (EntryVaccination) i.next();
				log.info("inspecting VACCINATION OBJECT" + v + " :" + v.getVaccineGiven() + " ");
				
				Util.logBean(log, v);
				if (v.isEntered()) {
				    String vaccName = getVaccineName(v);
				    log.info("VACCINATION APPEARS ENTERED FOR ABOVE ");
				    if (! defaultVaccEpisode) {
				        meetSchemaRequirementEpisode(encounter, summary  , conn, "vaccination given: " + vaccName + " (auto-text)");
				        defaultVaccEpisode = true;
				    } else {
				        addVaccNameToDefaultEpisode(conn, vaccName);
				    }
					linkRootItem(conn, v, summary, false);
					saveVaccination(conn, v, summary, encounter.getId().intValue());
					itemsAttached++;
				}
			} catch (Exception e) {
				nonFatalExceptions.add(e);
				
				conn.rollback();
			}
		}
		conn.commit();
	    } 
	   		catch ( Exception e2) {
	        log.error(e2,e2);
	        conn.rollback();
	    }
	    
		return itemsAttached;
	}
	
	/**
     * @param conn
     * @param vaccName
     */
    private void addVaccNameToDefaultEpisode(Connection conn, String vaccName) {
        // TODO Auto-generated method stub
        try {
        Statement stmt = conn.createStatement();
        stmt.execute("update clin_narrative set narrative= narrative || '\n" + "vaccination given: "+
                vaccName+" (auto-text)' where pk=(select max(pk) from clin_narrative)");
    
        } catch (Exception e) {
            
            log.error(e,e);
        }
    }

    /**
     * @param v
     * @return
     */
    private String getVaccineName(EntryVaccination v) {
        String vaccName = "not determined";
        try {
            Vaccine vacc = (Vaccine)getVaccineMap().get(new Integer(Integer.parseInt(v.getVaccineGiven())));
            vaccName = vacc.getTradeName();
        } catch (Exception e) {
            log.error(e,e);
        }
        return vaccName;
    }

    /**
     * @param i
	 * @param conn
	 * @param narrativeText TODO
	 * @throws SQLException
     */
    private void meetSchemaRequirementEpisode(ClinicalEncounter encounter, HealthSummary01 summary, Connection conn, String narrativeText) throws SQLException {
        // TODO Auto-generated method stub
        
        conn.commit();
  /*
        Statement defer = conn.createStatement();
        log.info("AUTOCOMMIT IS " + conn.getAutoCommit());
  
        defer.execute("set constraints all deferred");
  
        PreparedStatement stmt0 = conn.prepareStatement(
                "insert into clin_episode(" +
                "fk_patient, fk_clin_narrative)" +
                " values(  " +
                " ? , " +
                " (select max(pk) from clin_narrative where fk_patient = ?)  )");
        stmt0.setInt(1, idPatient);
        stmt0.setInt(2, idPatient);
        stmt0.execute();
        PreparedStatement stmt = 
            conn.prepareStatement(
                "insert into clin_narrative( pk, fk_encounter, fk_clin_episode, narrative)" +
                " values( currval('clin_narrative_pk_seq'), (select max(id) from clin_encounter where fk_patient = ?),  select currval('clin_episode_pk_seq') " +
                ", 'vaccination given (auto-recorded)')  ");
        	stmt.setInt(1, idPatient);
        	stmt.execute();
        	PreparedStatement relink = conn.prepareStatement("update clin_episode set fk_clin_narrative=" +
        			"(select max(pk) from clin_narrative where fk_patient = ?) " +
        			" where fk_patient = ?");
        	relink.setInt(1, idPatient);
        	relink.execute();
        	defer.execute("set constraints all immediate");
*/		
        
        
        insertNamingNarrativeWithIdentityId(conn, narrativeText, summary.getIdentityId());

//        PreparedStatement  defer = conn.prepareStatement("set constraints rfi_fk_clin_narrative deferred");
//            defer.execute();
//            
//            PreparedStatement initNarrative = conn.prepareStatement(
//                            "insert into clin_episode( fk_patient, fk_clin_narrative) values ( ?, nextval('clin_narrative_pk_seq')) ");
//          initNarrative.setInt(1, idPatient);
//            initNarrative.execute();
//            PreparedStatement stmt0 = conn.prepareStatement(
//                            "insert into clin_narrative(pk,  fk_episode, fk_encounter, narrative) values(currval('clin_narrative_pk_seq'), (select max(pk) from clin_episode where fk_patient = ?), (select max(id) from clin_encounter where fk_patient = ?) ,  'vaccination (auto record)' )");
//          stmt0.setInt(1, idPatient);
//          stmt0.setInt(2, idPatient);
//          stmt0.execute();
//            PreparedStatement  immed= conn.prepareStatement("set constraints all immediate");
//            immed.execute();

    }

    /**
     * @param conn
     * @param narrativeText
     * @param identityId
     * @throws SQLException
     */
    private void insertNamingNarrativeWithIdentityId(Connection conn, String narrativeText, Long identityId) throws SQLException {
        String identityIdString = Integer.toString(identityId.intValue());
        insertNamingNarrativeWithIdStr(getDeferredConstraintStatement(conn), null, narrativeText, identityIdString , "null", null);
    }
    
    public void insertNamingNarrativeWithEpisodeDescriptionAndHealthIssueId( Connection conn, HealthSummary01 summary, ClinicalEpisode e, boolean isNewHealthIssue) throws DataSourceException,SQLException  {
//        String identityIdString = "( select id_patient from clin_health_issue issue, clin_episode episode" +
//        		"  where " +
//        		" issue.id = episode.fk_health_issue  and episode.pk = " +
//        		e.getId().toString() + " )";
        Statement deferredStatement = getDeferredConstraintStatement(conn);
        
        if (e.getId() == null ) {
            linkEpisodeHealthIssue(conn, summary, e);
            e = insertEpisode(conn,e.getHealthIssue(), e);
        }
        String identityIdString = summary.getIdentityId().toString();
        insertNamingNarrativeWithIdStr(deferredStatement, e.getId(), e.getDescription(),"null", e.getHealthIssue().getId().toString(), ( isNewHealthIssue? e.getEarliestRootItem().getClin_when(): null) );
    }
    /**
     * @param conn
     * @param summary
     * @param e
     * @throws SQLException
     */
    private void linkEpisodeHealthIssue(Connection conn, HealthSummary01 summary, ClinicalEpisode e) throws SQLException {
        if (e.getHealthIssue().getId() == null) {
            HealthIssue issue = findExistingHealthIssue(e.getHealthIssue().getDescription(), summary);
            
            e.getHealthIssue().setId(issue != null ? issue.getId() : new Long(insertNewHealthIssue(conn,e.getHealthIssue().getDescription(), summary).longValue()));
        }
    }

    /**
     * @param conn
     * @param narrativeText
     * @param identityIdString
     * @param healthIssueIdString
     * @param date
     * @throws SQLException
     */
    private void insertNamingNarrativeWithIdStr(Statement c, Long episodeId, String narrativeText, String identityIdString, String healthIssueIdString, Date date) throws SQLException {
       if (episodeId == null) {
        c.executeUpdate("insert into clin_episode " +
                        "(fk_health_issue,  fk_patient, fk_clin_narrative) " +
                        "values ("+ healthIssueIdString +", " + identityIdString + " , nextval('clin_narrative_pk_seq')) ");
    	} else {
    	    c.executeUpdate("update clin_episode set fk_health_issue = "+healthIssueIdString+"" +
    	    		", fk_patient = "+ identityIdString + "" +
    	    				", fk_clin_narrative  =  nextval('clin_narrative_pk_seq')" +
    	    				" where pk= " + episodeId.toString());
    	}
       c.executeUpdate("insert into clin_narrative " +
                        "(pk,  fk_episode, fk_encounter, narrative, soap_cat) " +
                        "values(" +
                        "currval('clin_narrative_pk_seq')," +
                        " (select currval('clin_episode_pk_seq'))," +
                        " (select max(id) from clin_encounter where " +
                        "fk_patient = " +
                        "coalesce(" +
                        		"(select id_patient from clin_health_issue where id = "+healthIssueIdString + ")" +
                        	",	"+identityIdString+
                        	") " +
                        				") ," +
                        "  '"+narrativeText+"', 'a' )");
         if (date != null) {
             PreparedStatement stmt = c.getConnection().prepareStatement("update clin_narrative set clin_when = ? where pk=currval('clin_narrative_pk_seq')");
         		stmt.setTimestamp(1,new Timestamp( date.getTime() ) );
         		stmt.execute();
         }
        c.getConnection().commit();
    }

    /**
     * @param conn
     * @return
     * @throws SQLException
     */
    private Statement getDeferredConstraintStatement(Connection conn) throws SQLException {
        Statement c = conn.createStatement();
        
        c.execute("commit;begin"); // required on publicdb for some reason.
        
        c.executeUpdate("set constraints rfi_fk_clin_narrative deferred");
        return c;
    }

    private int saveMedicationCollection(ClinicalEncounter encounter,
			HealthSummary01 summary, List nonFatalExceptions, Connection conn) {
	    int itemsAttached =0;
		for (Iterator i = encounter.getMedications().iterator(); i.hasNext();) {
                    EntryMedication med=null;
			try {
				med = (EntryMedication) i.next();
				if (med.isEntered()) {
					
					
					med.updateDirections(); // parsed data added to directions
					// one way of storing qty and repeats on clin_medication
					med.setNarrative(med.getNarrative() + "\n\nscript:"+med.getGenericName()+"("
							+med.getBrandName()+") " 
							+med.getDirections() );
					linkRootItem(conn, med, summary, false);
					saveMedication(conn, med, summary);
					itemsAttached++ ;
				} else {
                                    log.info("Medication "+ med.toString() +" name:"+ med.getBrandName() + " WAS NOT SAVED DUE TO ENTERED=FALSE");
                                }
			} catch (Exception e) {
				nonFatalExceptions.add(e);
                                log.info("Error in saving?" + med.getBrandName() , e);
			}
		}
		return itemsAttached;
	}


	/**
	 * @param conn
	 * @param v
	 * @param summary
	 */
	private void saveMedication(Connection conn, EntryMedication med, HealthSummary01 summary)
throws SQLException, DataSourceException {
		log.info("SAVING WITH " + getMedicationSaveScript());
		getMedicationSaveScript().save(conn, med, summary, getClinRootInsert() );
                
	}

//	/** gets the next id from the sequence named */
//	private Integer getNextId(Connection conn, String seqName)
//			throws DataSourceException, SQLException {
//		
//			return clinRootInsert.getNextId(conn, seqName);
//	}

	private ClinicalEpisode findOrCreateEpisode(Connection conn,
			HealthSummary01 summary, ClinicalEpisode candidateEpisode , boolean isNewHealthIssue)
			throws DataSourceException, SQLException {
	    
		if (candidateEpisode.getId() == null ) {
		  //  candidateEpisode = insertEpisode(conn, issue, candidateEpisode);
			insertEpisodeDescriptionNarrative( conn, summary, candidateEpisode, isNewHealthIssue);
		}
		return candidateEpisode;

	}

	/**
 * @param candidateEpisode
	 * @param conn TODO
	 * @param summary
 */
private void insertEpisodeDescriptionNarrative( Connection conn ,HealthSummary01 summary, ClinicalEpisode candidateEpisode, boolean isFirstForHealthIssue) {
    // TODO Auto-generated method stub
    try {
        if (!isNamedEpisode(candidateEpisode)) {
            setDefaultEpisodeName(candidateEpisode);
        }
        
        insertNamingNarrativeWithEpisodeDescriptionAndHealthIssueId(conn , summary, candidateEpisode,isFirstForHealthIssue);
        
        
    } catch (Exception e) {
        // TODO: handle exception
        log.error(e,e);
    }
}

    /**
     * @param candidateEpisode
     */
    private void setDefaultEpisodeName(ClinicalEpisode candidateEpisode) {
        candidateEpisode.setDescription("episode of " + candidateEpisode.getHealthIssue().getDescription() + " on "
                + new Date() );
    }

    /**
     * @param candidateEpisode
     * @return
     */
    private boolean isNamedEpisode(ClinicalEpisode candidateEpisode) {
        return !Util.nullIsBlank(candidateEpisode.getDescription()).equals("");
    }

    /**
	 * @param conn
	 * @param issue
	 * @param candidateEpisode -
	 *            the episode to consider saving
	 * @param theEpisode -
	 *            a possibly matching , possibly already saved episode
	 * @throws DataSourceException
	 * @throws SQLException
	 * 
	 * precondition: candidateEpisode <>Null postcondition: theEpisode.id !=
	 * null
	 *  
	 */
	private ClinicalEpisode insertEpisode(Connection conn, HealthIssue issue,
			ClinicalEpisode candidateEpisode )
			throws DataSourceException, SQLException {
	    	
// this might cause deadlock?
//			Integer id = getNextId(conn, "clin_episode_pk_seq");

		    //version 0.1
//			String s3b = "insert into clin_episode( pk, description, fk_health_issue) values( ? , ?, ?)";
//			PreparedStatement stmt = conn.prepareStatement(s3b);
//
//			stmt.setInt(1, id.intValue());
//			stmt.setString(2, candidateEpisode.getDescription());
//			stmt.setInt(3, issue.getId().intValue());

//version 0.2			
			String s3b = "insert into clin_episode(  fk_health_issue) values(   ?)";
			
			PreparedStatement stmt = conn.prepareStatement(s3b);
			
			stmt.setInt(1 , issue.getId().intValue());

			stmt.execute();
			
			
			
			candidateEpisode.setId(new Long( getLastId(conn, "clin_episode_pk_seq").longValue()));
			candidateEpisode.setHealthIssue(issue);
			issue.addClinicalEpisode(candidateEpisode);
			 
		return candidateEpisode;
	}

	private boolean isSameEpisode(ClinicalEpisode e1, ClinicalEpisode e2) {

		return Algorithms
				.isCharMatchedInWords(e1.getDescription(), e2.getDescription(),
						WORD_THRESHOLD, MATCHED_WORDCOUNT_THRESHHOLD)
				&& java.lang.Math.abs(e1.getModified_when().getTime()
						- e2.getModified_when().getTime()) < SAME_EPISODE_INTERVAL;
	}

	private void linkRootItem(Connection conn, ClinRootItem item,
			HealthSummary01 summary, boolean isNewIssue) throws DataSourceException, SQLException {
		
	    HealthIssue issue = findOrCreateHealthIssue(conn, item
				, summary);
		ClinicalEpisode episode = findOrCreateEpisode(conn, summary, item
				.getEpisode(), isNewIssue);
		episode.setHealthIssue(issue);
		item.setEpisode(episode);
		log.info(issue+" "+episode+" "+item);
	}

	private HealthIssue findOrCreateHealthIssue(Connection conn,
			ClinRootItem issueHolder, HealthSummary01 summary)
			throws DataSourceException, SQLException {
		// hacky guard
		if ("".equals(issueHolder.getHealthIssueName().trim()))
			issueHolder .setHealthIssueName( "xxxDEFAULTxxx");

		HealthIssue issue = findExistingHealthIssue(issueHolder.getHealthIssueName(), summary);
		
		if (issue == null || issue.getId() == null) {
			issue = createNewHealthIssue(conn, issueHolder, summary);
			summary.addHealthIssue(issue);
		}

		return issue;

	}

	/**
     * @param healthIssueName
     * @param summary
     * @return
     */
    private HealthIssue findExistingHealthIssue(String healthIssueName, HealthSummary01 summary) {
        HealthIssue issue = null;
		Iterator i = summary.getHealthIssues().iterator();
		while (i.hasNext()) {
			HealthIssue hi = (HealthIssue) i.next();
			if (Algorithms.normaliseMatch(hi.getDescription(), healthIssueName))

			{
				log.info("Matched " + hi.getDescription().toLowerCase()
						+ " with " + healthIssueName.toLowerCase());
				issue = hi;
				break;
			}
		}
        return issue;
    }

    /**
     * @param conn
     * @param healthIssueNameHolder
     * @param summary
     * @return
     * @throws SQLException
     */
    private HealthIssue createNewHealthIssue(Connection conn, ClinRootItem healthIssueNameHolder, HealthSummary01 summary) throws SQLException {
        HealthIssue issue;
        Integer id = insertNewHealthIssue(conn, healthIssueNameHolder.getHealthIssueName(), summary);
        if (healthIssueNameHolder.getEpisode().getHealthIssue() == null ) {
            issue = getDataObjectFactory().createHealthIssue();
        } else {
            issue = healthIssueNameHolder.getEpisode().getHealthIssue();
        }
        issue.setId(new Long(id.longValue()));
        issue.setDescription(healthIssueNameHolder.getHealthIssueName());
        conn.commit();
        return issue;
    }

    /**
     * @param conn
     * @param healthIssueName
     * @param summary
     * @return
     * @throws SQLException
     */
    private Integer insertNewHealthIssue(Connection conn, String healthIssueName, HealthSummary01 summary) throws SQLException {
        log.info("New health issue is " + healthIssueName
        		+ " identity id = " + summary.getIdentityId());
        String s2b = "insert into clin_health_issue" +
        		"(  id_patient, description)" +
        		" values( ?,?)";
        PreparedStatement stmt = conn.prepareStatement(s2b);
         stmt.setInt(1, summary.getIdentityId().intValue());
        stmt.setString(2, healthIssueName);
        stmt.execute();
 
        Integer id = getLastId(conn, "clin_health_issue_id_seq" );
        return id;
    }

    private void saveNarrative(Connection conn, ClinNarrative narrative)
			throws DataSourceException, SQLException {

		String s4 = "insert into clin_narrative(" +
				" is_aoe, is_rfe, clin_when, narrative, soap_cat,  fk_encounter, fk_episode) "
				+ "values (" +
				"  ?,     ? ,       ? ,       ?,          ?,        ? ,           ? " +
				" )";

		PreparedStatement stmt = conn.prepareStatement(s4);
		stmt.setBoolean(1, narrative.isAoe());
		stmt.setBoolean(2, narrative.isRfe());

		setClinRootItemStatement(stmt, narrative, 3);
		
		// for the first narrative with a healthIssueStart set,
		log.info("HealthIssueStart "+narrative.getHealthIssueStart() +" is " + (narrative.getHealthIssueStart().getTime() + 1000 * 3600 * 24) + " vs narrative.clin_when = "+  narrative.getClin_when() +" is " + narrative.getClin_when().getTime());
		if ( narrative.getHealthIssueStart().getTime()  < narrative.getClin_when().getTime()  ) {
		    stmt.setTimestamp(3, new Timestamp(narrative.getHealthIssueStart().getTime()));
		}
		
		log.info(s4);

		stmt.execute();

	}

	public void setClinRootItemStatement(PreparedStatement stmt,
			ClinRootItem item, int startIndex) throws DataSourceException,
			SQLException {	
		
			clinRootInsert.setClinRootItemStatement(stmt, item, startIndex);
	}

	private void saveAllergy(Connection conn, Allergy allergy, HealthSummary01 summary)
			throws DataSourceException, SQLException {
		if (allergy instanceof EntryClinRootItem
				&& !((EntryClinRootItem) allergy).isEntered())
			return;
		try {
			log.info("SAVE ALLERGY" + allergy.getEncounter() + ":"
					+ allergy.getNarrative() + ":" + allergy.getSubstance());

			if (allergy.getEncounter() == null || allergy.getEpisode() == null) {
				throw new DataSourceException(
						"Allergy had no encounter or episode, allergy not saved.");
			}
			String s5 = "insert into allergy" +
            "( definite, substance,id_type,   clin_when, narrative, soap_cat,  fk_encounter, fk_episode) "
+ "values        (?,        ? ,         ? ,         ?,      ?,          ? , "+ getMaxEncounterMaxEpisodeString(summary)+ " )";

			log.info("SAVE ALLERGY" + allergy.getEncounter() + ":"
					+ allergy.getNarrative() + ":" + allergy.getSubstance());
                                        
                        conn.commit();
                        
			PreparedStatement stmt = conn.prepareStatement(s5);

                        stmt.setBoolean(1, allergy.isDefinite());
                        
			stmt.setString(2, allergy.getSubstance());

			stmt.setInt(3, 1); // id_type allergy
			//  ** change **
			setClinRootItemStatement(stmt, allergy, 4,7);


			log.info(s5);
			stmt.execute();
			conn.commit();

		} catch (Exception e) {
			conn.rollback();
                        Statement recovery = conn.createStatement();
                        recovery.execute("abort");
                        conn.commit();
                        recovery.close();
                        
			log.info(e, e);
			throw new DataSourceException("allergy save error." + e.getCause(),
					e);
		}

	}

	private void saveVaccination(Connection conn, Vaccination vacc,
			HealthSummary01 summary, int idEncounter) throws DataSourceException, SQLException {
		try {
		    int idVaccine = Integer.parseInt(vacc.getVaccineGiven());
		    if (idVaccine == 0) {
		        return;
		    }
			String encounterEpisodeString = getMaxEncounterMaxEpisodeString(summary);
            String s6 = "insert into vaccination (" +
					" fk_patient, fk_provider, fk_vaccine, site, batch_no, "
					+ " clin_when, narrative, soap_cat,  " +
							"fk_encounter, 	fk_episode) "
					+ "values (?,  ? , 			? ,			 ?, 	?		," +
							" ? , 	? , 	   ?," +
							encounterEpisodeString +
							 
							" )";

			PreparedStatement stmt = conn.prepareStatement(s6);
			int i = 0;
			stmt.setInt(++i, summary.getIdentityId().intValue());

			stmt.setInt(++i, 0);
			log.info("TRYING TO SET" + s6 + " WITH vacc.getVaccineGiven()="
					+ vacc.getVaccineGiven());

			
            stmt.setInt(++i, idVaccine);

			stmt.setString(++i, vacc.getSite());

			stmt.setString(++i, vacc.getBatchNo());

			setClinRootItemStatement(stmt, vacc, 6, 9);
			
			
			
			log.info(s6);

			stmt.execute();
			

		} catch (Exception e) {
			conn.rollback();
			log.info(e, e);
			throw new DataSourceException("vaccine save error." + e.getCause(),
					e);
		}

	}

	/**
     * @param summary
     * @return
     */
    private String getMaxEncounterMaxEpisodeString(HealthSummary01 summary) {
        String getEncounterEpisodeParameterString = " (select max(id) from clin_encounter " +
        					"where fk_patient=" +summary.getIdentityId().toString() +
        				" ), " +
        				"(select max(pk) from clin_episode "+
        				"where fk_patient=" +summary.getIdentityId().toString() +")";
        return getEncounterEpisodeParameterString;
    }

    /**
     * @param stmt
     * @param vacc
     * @param i
     * @param j
	 * @throws SQLException
	 * @throws DataSourceException
     */
    private void setClinRootItemStatement(PreparedStatement stmt, ClinRootItem item, int i, int j) throws DataSourceException, SQLException {
        // TODO Auto-generated method stub
        clinRootInsert.setClinRootItemStatement(stmt, item, i, j);
    }

    /**
     * @param idEncounter
	 * @throws SQLException
     */
    private void meetSchemaRequirementVaccinations2(Connection conn, PreparedStatement stmt, int idEncounter) throws SQLException {
        // TODO Auto-generated method stub
        Statement stmt1 = conn.createStatement();
        
        stmt.setInt(10, idEncounter);
      
        ResultSet rs = stmt1.executeQuery("select currval('clin_episode_pk_seq')");
        if ( rs.next() ) {
            stmt.setInt(11, rs.getInt(1));
        }
        
    }

    private java.util.Date nullToNow(java.util.Date d) {
		if (d == null)
			return new java.util.Date();
		return d;

	}

	private void ensureXLinkIdentityExists(Connection conn, long patientId)
			throws SQLException {
		String s8 = "select xfk_identity from xlnk_identity where xfk_identity=  ?";
		PreparedStatement stmt = conn.prepareStatement(s8);
		stmt.setLong(1, patientId);
		stmt.execute();
		ResultSet rs = stmt.getResultSet();
		if (rs.next()) {
			stmt.close();
			return;
		}
		String s9 = "insert into xlnk_identity( xfk_identity, pupic) values( ? , ?)";
		PreparedStatement stmt2 = conn.prepareStatement(s9);
		stmt2.setLong(1, patientId);
		stmt2.setLong(2, patientId);
		stmt2.execute();

		stmt2.close();
	}

	private static Map codeMap = new HashMap();

	static {
		final String[] propertyToCodeName = { "diastolic", "dBP", "height",
				"hght", "pr", "PR", "systolic", "sBP", "temp", "T", "weight",
				"wght", "rr", "rr" };

		for (int i = propertyToCodeName.length - 1; i >= 0; i -= 2) {
			codeMap.put(propertyToCodeName[i - 1], propertyToCodeName[i]);
		}
	}

	static Map getCodeMap() {
		return Collections.unmodifiableMap(codeMap);
	}

	private void saveVitals(Connection conn, EntryVitals v, List exceptions)
			throws DataSourceException, SQLException {

		if (!v.isEntered()) {
			log.info("** " + v + " HAS NOT BEEN ENTERED");
			return;
		}

		log.info("LOOKING TO SAVE" + v);
		PreparedStatement stmt = null;

		try {

			String s6 = "insert into test_result(pk_item, fk_type,  val_num, val_alpha,  clin_when, narrative, soap_cat,  fk_encounter, fk_episode) "
					+ "values (?, (select id from test_type where code=?) , ? , ?, ?, ? , ? , ?, ?)";

			stmt = conn.prepareStatement(s6);

			for (Iterator i = getCodeMap().keySet().iterator(); i.hasNext();) {
				String property = (String) i.next();
				String code = (String) getCodeMap().get(property);

				if (!v.isSet(property)) {
					log.info("property= " + property + " is not set. SKIPPING");
					continue;
				}
				log.info(s6);
				setInsertStatementForVitalProperty(v, stmt, property, code);
				try {
					stmt.execute();
					conn.commit();
				} catch (Exception e) {
					log.info("saving " + v + " " + property + "  got " + e, e);
					conn.rollback();
					exceptions.add(e);
				}

			}

		} catch (Exception e) {
			throw new DataSourceException(
					"exception before vitals items processed", e);

		} finally {
			stmt.close();
		}

	}

	/**
	 * @param v
	 * @param stmt
	 * @param property
	 * @param code
	 * @throws DataSourceException
	 * @throws SQLException
	 */
	private void setInsertStatementForVitalProperty(Vitals v,
			PreparedStatement stmt, String property, String code)
			throws DataSourceException, SQLException {

		setClinRootItemStatement(stmt, v, 5);
		stmt.setString(2, code);

		stmt.setString(4, "");

		try {
			log.info("Trying to get double from " + property);
			double val = ((Number) PropertyUtils.getProperty(v, property))
					.doubleValue();
			log.info("GOT this double" + val + " for " + v);
			stmt.setDouble(3, val);
		} catch (SQLException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IllegalAccessException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (InvocationTargetException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (NoSuchMethodException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	public void setClinRootInsert( ClinRootInsert inserter) {
		clinRootInsert = inserter;
	}
	public ClinRootInsert getClinRootInsert() {
		return clinRootInsert;
	}
	
	public void setMedicationSave( MedicationSaveScript medSaveScript) {
		medicationSaveScript = medSaveScript;
	}
	
	public MedicationSaveScript getMedicationSaveScript( ) {
		return medicationSaveScript;
	}

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.persist.CredentialUsing#setCredential(java.lang.Object)
     */
    public void setCredential(Object o) {
        // TODO Auto-generated method stub
        threadCredential.setCredential(o);
        
    }
	
}
