/*
 * ScriptedSQLHealthRecordAccess.java
 *
 * Created on September 14, 2004, 10:54 PM
 */

package org.gnumed.testweb1.persist.scripted;

import java.lang.reflect.InvocationTargetException;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.Collections;
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
import org.gnumed.testweb1.data.Vitals;
import org.gnumed.testweb1.global.Algorithms;
import org.gnumed.testweb1.global.Constants.Schema;
import org.gnumed.testweb1.persist.ClinicalDataAccess;
import org.gnumed.testweb1.persist.DataObjectFactoryUsing;
import org.gnumed.testweb1.persist.DataSourceException;
import org.gnumed.testweb1.persist.DataSourceUsing;
import org.gnumed.testweb1.persist.HealthRecordAccess01;

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
		DataSourceUsing, DataObjectFactoryUsing {
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
			conn.setReadOnly(true);

			ResultSet healthIssuesRS, episodesRS, encountersRS, vaccinationsRS, medicationsRS, allergyRS, narrativeRS, lab_requestRS, test_resultRS, referralRS, encounterTypeRS;

			ensureXLinkIdentityExists(conn, patientId);
			healthIssuesRS = getHealthIssueRS(conn, patientId);

			episodesRS = getClinEpisodesRS(conn, getIdsFromResultSet(
					healthIssuesRS, "id"));
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
			throw new DataSourceException(e);
		} finally {
			if (conn != null) {
				try {
					conn.close();
				} catch (SQLException se) {
					throw new DataSourceException(se);
				}
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
				+ ((ids.length == 0) ? "( null ) " : "(" + idsToString(ids)
						+ ")"));
		stmt.execute();
		return stmt.getResultSet();
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
			long[] clin_health_issue_ids) throws SQLException {
		return getRowsForIds(conn,
				"select * from clin_episode where fk_health_issue  in",
				clin_health_issue_ids);
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
		String s1 = "insert into clin_encounter (id, description, started, last_affirmed,  fk_patient) values (?, ?, ?,?,  ? )";

		Connection conn = null;
		try {

			conn = getDataSource().getConnection();

			conn.setAutoCommit(false);

			Integer idEncounter = insertEncounter(encounter, summary, s1, conn);
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
			itemsAttached = saveNarrativesCollection(encounter, summary,
					nonFatalExceptions, conn, itemsAttached);

			itemsAttached = saveAllergiesCollection(encounter, summary,
					nonFatalExceptions, conn, itemsAttached);

			itemsAttached = saveVitalsCollection(encounter, summary,
					nonFatalExceptions, conn, itemsAttached);

			itemsAttached = saveVaccinationsCollection(encounter, summary,
					nonFatalExceptions, conn, itemsAttached);
			
			itemsAttached = saveMedicationCollection(encounter, summary,
					nonFatalExceptions, conn, itemsAttached);
			
			if (itemsAttached == 0) {
				conn.rollback();
				Statement stmt = conn.createStatement();
				stmt.execute("delete from clin_encounter where id="
						+ idEncounter.toString());
				conn.commit();
				throw new DataSourceException(
						"No items attached. Encounter deleted");
			}

			conn.commit();
			conn.close();

		} catch (Exception exception) {
			try {
				conn.rollback();
				conn.close();
			} catch (Exception e2) {
				e2.printStackTrace();
			}
			throw new DataSourceException("unexpected ", exception);
		}

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
	private Integer insertEncounter(ClinicalEncounter encounter,
			HealthSummary01 summary, String s1, Connection conn)
			throws DataSourceException, SQLException {
		Integer idEncounter = getNextId(conn, "clin_encounter_id_seq");

		encounter.getDescription();

		java.util.Date started = nullToNow(encounter.getStarted());
		java.util.Date affirmed = nullToNow(encounter.getLastAffirmed());

		PreparedStatement insertEncounter = conn.prepareStatement(s1);
		insertEncounter.setObject(1, idEncounter);
		insertEncounter.setString(2, encounter.getDescription());
		insertEncounter.setTimestamp(3, new Timestamp(started.getTime()));
		insertEncounter.setTimestamp(4, new Timestamp(affirmed.getTime()));
		insertEncounter.setObject(5, summary.getIdentityId());
		insertEncounter.execute();
		encounter.setId(new Long(idEncounter.longValue()));

		return idEncounter;
	}
 
	/**
	 * @param encounter
	 * @param nonFatalExceptions
	 * @param conn
	 * @param itemsAttached
	 * @return
	 */
	private int saveNarrativesCollection(ClinicalEncounter encounter,
			HealthSummary01 summary, List nonFatalExceptions, Connection conn,
			int itemsAttached) {
		for (Iterator i = encounter.getNarratives().iterator(); i.hasNext();) {
			EntryClinNarrative narrative = (EntryClinNarrative) i.next();
			if (!narrative.isEntered())
				continue;
			try {
				linkRootItem(conn, narrative, summary);
				saveNarrative(conn, narrative);
				++itemsAttached;
			} catch (Exception e) {
				log.info("Save Narrative error " + e, e);
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
	 * @param itemsAttached
	 * @return
	 */
	private int saveAllergiesCollection(ClinicalEncounter encounter,
			HealthSummary01 summary, List nonFatalExceptions, Connection conn,
			int itemsAttached) {
		for (Iterator i = encounter.getAllergies().iterator(); i.hasNext();) {
			try {

				AllergyEntry allergy = (AllergyEntry) i.next();
				if (!allergy.isEntered())
					continue;
				linkRootItem(conn, allergy, summary);
				saveAllergy(conn, allergy);
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
	 * @param itemsAttached
	 * @return
	 */
	private int saveVitalsCollection(ClinicalEncounter encounter,
			HealthSummary01 summary, List nonFatalExceptions, Connection conn,
			int itemsAttached) {
		for (Iterator i = encounter.getVitals().iterator(); i.hasNext();) {
			try {
				EntryVitals entryVitals = (EntryVitals) i.next();
				if (entryVitals.isEntered()) {
					linkRootItem(conn, entryVitals, summary);
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
	 * @param itemsAttached
	 * @return
	 */
	private int saveVaccinationsCollection(ClinicalEncounter encounter,
			HealthSummary01 summary, List nonFatalExceptions, Connection conn,
			int itemsAttached) {
		for (Iterator i = encounter.getVaccinations().iterator(); i.hasNext();) {
			try {
				EntryVaccination v = (EntryVaccination) i.next();
				if (v.isEntered()) {
					linkRootItem(conn, v, summary);
					saveVaccination(conn, v, summary);
					itemsAttached++;
				}
			} catch (Exception e) {
				nonFatalExceptions.add(e);
			}
		}
		return itemsAttached;
	}
	
	private int saveMedicationCollection(ClinicalEncounter encounter,
			HealthSummary01 summary, List nonFatalExceptions, Connection conn,
			int itemsAttached) {
		for (Iterator i = encounter.getMedications().iterator(); i.hasNext();) {
			try {
				EntryMedication v = (EntryMedication) i.next();
				if (v.isEntered()) {
					linkRootItem(conn, v, summary);
					saveMedication(conn, v, summary);
					itemsAttached++;
				}
			} catch (Exception e) {
				nonFatalExceptions.add(e);
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
		// TODO Auto-generated method stub
		
		String s9 = "insert into clin_medication(pk_item, " +
				"brandname, atc_code, " +
				"db_origin, db_drug_id," +
				" amount_unit, dose, period," +
				" form, directions, " +
				"prn, sr , " +
				"started, last_prescribed, discontinued," +
				" clin_when, narrative, soap_cat,  fk_encounter, fk_episode) "
			+ "values (?,  ? , ? , ?, ?," +
					" ? , ? , ? , ? , ?" +
					", ? , ? , ? , ? , ?" +
					" , ? , ? , ? , ? , ?)";
		PreparedStatement stmt = conn.prepareStatement(s9);
		setClinRootItemStatement(stmt, med, 16); 
		stmt.setString(2, med.getBrandName());
		stmt.setString(3, med.getATC_code());
		stmt.setString(4, med.getDB_origin());
		stmt.setString(5, med.getDB_drug_id());
		stmt.setString(6, "");
		stmt.setDouble(7, med.getDose());
		stmt.setInt(8, med.getPeriod());
		stmt.setString(9, "form");
		stmt.setString(10, med.getDirections());
		stmt.setBoolean( 11, med.isPRN());
		stmt.setBoolean(12, med.isSR());
		stmt.setDate(13, new java.sql.Date(med.getStart().getTime()));
		stmt.setDate(14, new java.sql.Date(med.getLast().getTime()));
		stmt.setDate(15, new java.sql.Date(med.getDiscontinued().getTime()));
		
		
	}

	/** gets the next id from the sequence named */
	private Integer getNextId(Connection conn, String seqName)
			throws DataSourceException, SQLException {
		Statement stmt = conn.createStatement();
		stmt.execute("select nextval ('" + seqName + "')");
		ResultSet rs = stmt.getResultSet();
		Integer id = null;
		while (rs.next()) {
			id = new Integer(rs.getInt(1));
		}
		if (id == null)
			throw new DataSourceException("id from " + seqName + " was null");
		return id;
	}

	private ClinicalEpisode findOrCreateEpisode(Connection conn,
			HealthIssue issue, ClinicalEpisode candidateEpisode)
			throws DataSourceException, SQLException {
		if ("".equals(candidateEpisode.getDescription())) {
			candidateEpisode.setDescription(factory.getResourceString(Schema.DEFAULT_EPISODE_DESCRIPTION_KEY));
		}
		
		ClinicalEpisode[] episodes = issue.getClinicalEpisodes();
		ClinicalEpisode theEpisode = null;

		for (int i = 0; i < episodes.length; ++i) {
			log.info("episodes[i].description=" + episodes[i].getDescription()
					+ "   candidateEpisodes="
					+ candidateEpisode.getDescription());
			if (episodes[i].equals(candidateEpisode)) {

				theEpisode = episodes[i];
			}
		}
		candidateEpisode = insertEpisode(conn, issue, candidateEpisode, theEpisode);

		return candidateEpisode;

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
			ClinicalEpisode candidateEpisode, ClinicalEpisode theEpisode)
			throws DataSourceException, SQLException {

		if (theEpisode == null || theEpisode.getId() == null) {

			Integer id = getNextId(conn, "clin_episode_pk_seq");

			String s3b = "insert into clin_episode( pk, description, fk_health_issue) values( ? , ?, ?)";
			PreparedStatement stmt = conn.prepareStatement(s3b);

			stmt.setInt(1, id.intValue());
			stmt.setString(2, candidateEpisode.getDescription());
			stmt.setInt(3, issue.getId().intValue());

			stmt.execute();

			candidateEpisode.setId(new Long(id.longValue()));
			candidateEpisode.setHealthIssue(issue);
			issue.addClinicalEpisode(candidateEpisode);
			theEpisode = candidateEpisode;

		}
		return theEpisode;
	}

	private boolean isSameEpisode(ClinicalEpisode e1, ClinicalEpisode e2) {

		return Algorithms
				.isCharMatchedInWords(e1.getDescription(), e2.getDescription(),
						WORD_THRESHOLD, MATCHED_WORDCOUNT_THRESHHOLD)
				&& java.lang.Math.abs(e1.getModified_when().getTime()
						- e2.getModified_when().getTime()) < SAME_EPISODE_INTERVAL;
	}

	private void linkRootItem(Connection conn, ClinRootItem item,
			HealthSummary01 summary) throws DataSourceException, SQLException {
		HealthIssue issue = findOrCreateHealthIssue(conn, item
				.getHealthIssueName(), summary);
		ClinicalEpisode episode = findOrCreateEpisode(conn, issue, item
				.getEpisode());
		episode.setHealthIssue(issue);
		item.setEpisode(episode);

	}

	private HealthIssue findOrCreateHealthIssue(Connection conn,
			String healthIssueName, HealthSummary01 summary)
			throws DataSourceException, SQLException {
		// hacky guard
		if ("".equals(healthIssueName.trim()))
			healthIssueName = "xxxDEFAULTxxx";

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
		if (issue == null || issue.getId() == null) {

			log.info("New health issue is " + healthIssueName
					+ " identity id = " + summary.getIdentityId());
			Integer id = getNextId(conn, "clin_health_issue_id_seq");
			String s2b = "insert into clin_health_issue(id, id_patient, description) values( ?,?,?)";
			PreparedStatement stmt = conn.prepareStatement(s2b);
			stmt.setInt(1, id.intValue());
			stmt.setInt(2, summary.getIdentityId().intValue());
			stmt.setString(3, healthIssueName);
			stmt.execute();
			conn.commit();
			issue = getDataObjectFactory().createHealthIssue();
			issue.setId(new Long(id.longValue()));
			issue.setDescription(healthIssueName);
			summary.addHealthIssue(issue);
		}

		return issue;

	}

	private void saveNarrative(Connection conn, ClinNarrative narrative)
			throws DataSourceException, SQLException {

		String s4 = "insert into clin_narrative(pk_item, is_aoe, is_rfe, clin_when, narrative, soap_cat,  fk_encounter, fk_episode) "
				+ "values (?,  ? , ? , ?, ?, ? , ? , ? )";

		PreparedStatement stmt = conn.prepareStatement(s4);
		stmt.setBoolean(2, narrative.isAoe());
		stmt.setBoolean(3, narrative.isRfe());

		setClinRootItemStatement(stmt, narrative, 4);

		log.info(s4);

		stmt.execute();

	}

	private void setClinRootItemStatement(PreparedStatement stmt,
			ClinRootItem item, int startIndex) throws DataSourceException,
			SQLException {

		Integer id = getNextId(stmt.getConnection(),
				"clin_root_item_pk_item_seq");

		stmt.setInt(1, id.intValue());
		stmt.setTimestamp(startIndex++, new Timestamp(item.getClin_when()
				.getTime()));
		stmt.setString(startIndex++, item.getNarrative() == null ? "" : item
				.getNarrative());

		stmt.setString(startIndex++, item.getSoapCat().substring(0, 1));
		stmt.setInt(startIndex++, item.getEncounter().getId().intValue());
		stmt.setInt(startIndex++, item.getEpisode().getId().intValue());

	}

	private void saveAllergy(Connection conn, Allergy allergy)
			throws DataSourceException, SQLException {
		if (allergy instanceof EntryClinRootItem
				&& !((EntryClinRootItem) allergy).isEntered())
			return;
		try {
			log.info("SAVE ALLERGY" + allergy.getEncounter() + ":"
					+ allergy.getNarrative() + ":" + allergy.getSubstance());

			if (allergy.getEncounter() == null || allergy.getEpisode() == null) {
				log.info("DIDNot save");
				throw new DataSourceException(
						"Allergy had no encounter or episode");
			}
			String s5 = "insert into allergy(pk_item, definite, substance,id_type,   clin_when, narrative, soap_cat,  fk_encounter, fk_episode) "
					+ "values (?,  ? , ? , ?, ?, ? , ? , ?, ?)";

			log.info("SAVE ALLERGY" + allergy.getEncounter() + ":"
					+ allergy.getNarrative() + ":" + allergy.getSubstance());

			PreparedStatement stmt = conn.prepareStatement(s5);

			setClinRootItemStatement(stmt, allergy, 5);

			stmt.setInt(4, 1); // id_type allergy
			//  ** change **

			stmt.setString(3, allergy.getSubstance());

			stmt.setBoolean(2, allergy.isDefinite());

			log.info(s5);
			stmt.execute();
			conn.commit();

		} catch (Exception e) {
			conn.rollback();
			log.info(e, e);
			throw new DataSourceException("allergy save error." + e.getCause(),
					e);
		}

	}

	private void saveVaccination(Connection conn, Vaccination vacc,
			HealthSummary01 summary) throws DataSourceException, SQLException {
		try {
			String s6 = "insert into vaccination (pk_item, fk_patient, fk_provider, fk_vaccine, site, batch_no, "
					+ " clin_when, narrative, soap_cat,  fk_encounter, fk_episode) "
					+ "values (?,  ? , ? , ?, ?, ? , ? , ?, ?, ?, ?)";

			PreparedStatement stmt = conn.prepareStatement(s6);

			setClinRootItemStatement(stmt, vacc, 7);

			stmt.setInt(2, summary.getIdentityId().intValue());

			stmt.setInt(3, 0);
			log.info("TRYING TO SET" + s6 + " WITH vacc.getVaccineGiven()="
					+ vacc.getVaccineGiven());

			stmt.setInt(4, summary.findVaccine(vacc.getVaccineGiven()).getId()
					.intValue());

			stmt.setString(5, vacc.getSite());

			stmt.setString(6, vacc.getBatchNo());

			log.info(s6);

			stmt.execute();
			conn.commit();

		} catch (Exception e) {
			conn.rollback();
			log.info(e, e);
			throw new DataSourceException("vaccine save error." + e.getCause(),
					e);
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

}
