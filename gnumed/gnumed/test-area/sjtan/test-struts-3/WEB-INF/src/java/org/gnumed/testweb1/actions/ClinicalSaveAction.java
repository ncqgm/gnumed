/*
 * DemographicEntryAction.java
 *
 * Created on June 16, 2004, 9:30 PM
 */

package org.gnumed.testweb1.actions;

/*
 * LoginAction.java
 *
 * Created on June 18, 2004, 4:23 AM
 */

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.struts.action.Action;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;
import org.apache.struts.action.ActionMessage;
import org.apache.struts.action.ActionMessages;
import org.gnumed.testweb1.data.ClinNarrative;
import org.gnumed.testweb1.data.DataObjectFactory;
import org.gnumed.testweb1.data.HealthRecord01;
import org.gnumed.testweb1.data.Vaccination;
import org.gnumed.testweb1.forms.ClinicalUpdateForm;
import org.gnumed.testweb1.global.Constants;
import org.gnumed.testweb1.persist.HealthRecordAccess01;

/**
 * 
 * @author sjtan
 */
public class ClinicalSaveAction extends Action {
	ClinicalActionUtil util = new ClinicalActionUtil();

	/** Creates a new instance of DemographicEntryAction */
	public ClinicalSaveAction() {
	}

	Log log = LogFactory.getLog(this.getClass());

	public ActionForward execute(ActionMapping mapping, ActionForm form,
			HttpServletRequest request, HttpServletResponse response) {

		ActionMessages messages = new ActionMessages();

		try {
			//            Enumeration en1 = request.getSession().getAttributeNames() ;
			//            while(en1.hasMoreElements()) {
			//                log.info("Session has attribute " + en1.nextElement());
			//            }
			//            String[] ss = request.getSession().getValueNames();
			//            for (int i =0; i < ss.length; ++i) {
			//                log.info("And object value names = " + ss[i]);
			//            }

			Map map = new java.util.HashMap();

			DataObjectFactory objFactory = (DataObjectFactory) servlet
					.getServletContext().getAttribute(
							Constants.Servlet.OBJECT_FACTORY);

			ClinicalUpdateForm cform = (ClinicalUpdateForm) form;
			cform.linkObjects();

			//     log.info("TEST ATTRIBUTE FROM "+cform + " = "+cform.getTest());

			List l = cform.getVaccinations();

			Iterator i = l.iterator();
                        // logging exceptional event : no vaccinations
			if (!i.hasNext()) {
				log.info("****");
				log.info("No Vaccinations found.");
				log.info("****");
			}
                        
                        // logging which vaccinations present
			while (i.hasNext()) {
				Vaccination v = (Vaccination) i.next();
				if (v.getVaccineGiven() == null
						|| v.getVaccineGiven().trim().equals("")) {
					log.info("GOT " + v + " which was empty");
				} else {
					log.info("GOT vaccineGiven" + v.getVaccineGiven() + " on "
							+ v.getDateGivenString() + " batch no ="
							+ v.getBatchNo() + " , and site given = "
							+ v.getSite());
				}
			}

			List l2 = cform.getNarratives();
			if (l2.equals(cform.getEncounter().getNarratives())) {
				log.info("The narratives are the same in the form");
			}
			System.err.println("There are " + l2.size() + "NARRATIVES");
			Iterator j = l2.iterator();
			int ix = 0;
			while (j.hasNext()) {
				ClinNarrative n = (ClinNarrative) j.next();
				log.info("narrative #" + ix + "found with text "
						+ n.getNarrative() + ">");
				log.info("Health issue name for " + n + " was "
						+ n.getHealthIssueName());
				log.info("Narrative SOAP CAT " + n.getSoapCat());
				++ix;
			}

			HealthRecordAccess01 access = (HealthRecordAccess01) servlet
					.getServletContext().getAttribute(
							Constants.Servlet.HEALTH_RECORD_ACCESS);

			List nonFatalException = new ArrayList();
			HealthRecord01 record = (HealthRecord01) request.getSession()
					.getAttribute(Constants.Session.HEALTH_RECORD);
			access.save(cform.getEncounter(), record.getHealthSummary(),
					nonFatalException);
			if (nonFatalException.size() > 0) {
				for (int k = 0; k < nonFatalException.size(); ++k) {
					messages.add("save item error",
							new ActionMessage(((Exception) nonFatalException
									.get(k)).getMessage()));
				}
				saveMessages(request, messages);
			}
			// logging
			//    org.gnumed.testweb1.global.Util.logBean(log, form);
			//   org.gnumed.testweb1.global.Util.logBean(log, detail);

			return mapping.findForward("success");

		} catch (Exception e) {

			try {
				util.setRequestAttributes(servlet, request, form, mapping);
			} catch (Exception e2) {
				log.info(e2);
			}
			log.info(e, e);
			messages.add("error in constructing attributes for form",
					new ActionMessage("error is", e));
			saveMessages(request, messages);

			return mapping.getInputForward();
		}

	}

}