/*
 * ClinicalAction.java
 *
 * Created on September 24, 2004, 4:26 PM
 */

package org.gnumed.testweb1.actions;

import java.util.List;

import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionMapping;
import org.gnumed.testweb1.data.DataObjectFactory;
import org.gnumed.testweb1.data.DemographicDetail;
import org.gnumed.testweb1.data.HealthRecord01;
import org.gnumed.testweb1.forms.ClinicalUpdateForm;
import org.gnumed.testweb1.global.*;
import org.gnumed.testweb1.persist.*;

/**
 * 
 * @author sjtan
 */
public class ClinicalActionUtil extends ActionUtil {
	Log log = LogFactory.getLog(ClinicalActionUtil.class);

	/** Creates a new instance of ClinicalAction */
	public ClinicalActionUtil() {
	}

	/**
	 * @param request
	 * @param id
	 * @return
	 */
	Long getIdFromRequestParameter(HttpServletRequest request) {
		Long id = null;
		if (request.getParameter(Constants.Request.PATIENT_ID) != null)
			id = new Long(Long.parseLong(request
					.getParameter(Constants.Request.PATIENT_ID)));
		return id;
	}

	/**
	 * @param request
	 * @param id
	 * @throws DataSourceException
	 * sets the session attribute of key = Constants.Session.HEALTH_RECORD,
	 * with the healthRecord object given a demographic identity id.
	 * The healthRecord object is used encounters.
	 */
	void setHealthRecordOnSession(HttpServlet servlet,
			HttpServletRequest request, Long id) throws DataSourceException {
		HealthRecordAccess01 healthRecordAccess = (HealthRecordAccess01) servlet
				.getServletContext().getAttribute(
						Constants.Servlet.HEALTH_RECORD_ACCESS);

		HealthRecord01 healthRecord = healthRecordAccess
				.findHealthRecordByIdentityId(id.longValue());

		request.getSession().setAttribute(Constants.Session.HEALTH_RECORD,
				healthRecord);

	}

	/**
	 * @param request
	 * @param id
	 * @throws DataSourceException
	 */
	void setDemographicDetailOnSession(HttpServlet servlet,
			HttpServletRequest request, Long id) throws DataSourceException {
		DemographicDataAccess demoDataAccess = (DemographicDataAccess) servlet
				.getServletContext().getAttribute(
						Constants.Servlet.DEMOGRAPHIC_ACCESS);

		DemographicDetail detail = demoDataAccess.findDemographicDetailById(id);
		request.getSession().setAttribute(
				Constants.Session.DEMOGRAPHIC_DETAIL_CURRENT, detail);
	}

	/**
	 * @param request
	 * @throws DataSourceException
	 */
	void setVaccinesOnSession(HttpServlet servlet, HttpServletRequest request)
			throws DataSourceException {
		ClinicalDataAccess dataAccess = (ClinicalDataAccess) servlet
				.getServletContext().getAttribute(
						Constants.Servlet.CLINICAL_ACCESS);

		if (request.getSession().getAttribute(Constants.Session.VACCINES) == null) {
			List vaccines = dataAccess.getVaccines();

			request.getSession().setAttribute(Constants.Session.VACCINES,
					vaccines);
		}
	}

	/**
	 * reloads the demographicRecord and healthRecord objects given a patient id
	 * found on the form or as a request attribute.
	 * 
	 * @param servlet
	 * @param request
	 * @param form
	 * @param mapping
	 * @throws DataSourceException
	 */
	void setRequestAttributes(HttpServlet servlet, HttpServletRequest request,
			ActionForm form, ActionMapping mapping) throws DataSourceException {

		setVaccinesOnSession(servlet, request);

		Long id = null;
		if (form != null) {
			id = new Long(((ClinicalUpdateForm) form).getPatientId()
					.longValue());
		} else {
			id = getIdFromRequestParameter(request);
		}
		if (id != null && id.longValue() != (long) 0) {
			setDemographicDetailOnSession(servlet, request, id);
			setHealthRecordOnSession(servlet, request, id);

		}

		if (form == null) {

			DataObjectFactory factory = (DataObjectFactory) servlet
					.getServletContext().getAttribute(
							Constants.Servlet.OBJECT_FACTORY);

			form = new ClinicalUpdateForm(factory, new Integer(id.intValue()));

		}

		log.info("FORM is " + form);

		setAttributeOnScopeFromMappingAttributeAndScope(request, mapping, form);
	}
}