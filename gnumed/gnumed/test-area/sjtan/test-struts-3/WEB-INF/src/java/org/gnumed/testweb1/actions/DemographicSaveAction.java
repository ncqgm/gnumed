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

import java.util.Enumeration;
import java.util.Map;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

import org.apache.commons.beanutils.BeanUtils;
import org.apache.commons.beanutils.PropertyUtils;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.struts.action.Action;
import org.apache.struts.action.ActionForm;
import org.apache.struts.action.ActionForward;
import org.apache.struts.action.ActionMapping;
import org.apache.struts.action.ActionMessage;
import org.apache.struts.action.ActionMessages;
import org.gnumed.testweb1.data.DataObjectFactory;
import org.gnumed.testweb1.data.DemographicDetail;
import org.gnumed.testweb1.global.Constants;
import org.gnumed.testweb1.persist.DemographicDataAccess;

/**
 * 
 * @author sjtan
 */
public class DemographicSaveAction extends Action {
	ActionUtil util = new ActionUtil();

	/** Creates a new instance of DemographicEntryAction */
	public DemographicSaveAction() {
	}

	Log log = LogFactory.getLog(this.getClass());

	public ActionForward execute(ActionMapping mapping, ActionForm form,
			HttpServletRequest request, HttpServletResponse response) {

		ActionMessages messages = new ActionMessages();

		try {
			Map map = new java.util.HashMap();
			Enumeration e = request.getAttributeNames();
			while (e.hasMoreElements()) {
				log.info("request has attribute " + e.nextElement());
			}

			//          map.put("givenname","");map.put("surname","");map.put("birthdate","");
			//          BeanUtils.populate(form, map); // THIS WON"T WORK, DynaForm
			// property to accessible with populate
			//
			//          log.info("After populate: the map size=" +
			// Integer.toString(map.size()) );
			//          Map m = Collections.unmodifiableMap(map);
			//          Iterator j = m.keySet().iterator();
			//          while (j.hasNext()) {
			//              String key = (String)j.next();
			//              log.info("form map has key" + key + " with value " + m.get(key));
			//          }

			String username = (String) PropertyUtils.getSimpleProperty(form,
					"givenname");
			log.info("The username found was " + username);

			//   String username = (String) PropertyUtils.getSimpleProperty( form,
			// "username");
			//   password = ( (String)PropertyUtils.getSimpleProperty( form,
			// "password")).getBytes();
			//LoginModule module = (LoginModule)
			// request.getSession().getAttribute(Constants.LOGIN_MODULE);

			//     module.validate(username, password );
			DataObjectFactory objFactory = (DataObjectFactory) servlet
					.getServletContext().getAttribute(
							Constants.Servlet.OBJECT_FACTORY);

			DemographicDetail detail = objFactory.createDemographicDetail();

			log.info("managed to get " + detail);

			//             Map description = BeanUtils.describe(form);
			//            Iterator i2 = description.entrySet().iterator();
			//            while (i2.hasNext()) {
			//                Map.Entry me = (Map.Entry) i2.next();
			//                log.info( detail + " has attribute '" + me.getKey() + "' : " +
			// me.getValue());
			//            }

			// logging
			//    org.gnumed.testweb1.global.Util.logBean(log, form);

			BeanUtils.copyProperties(detail, form);

			//Using the persist module
			DemographicDataAccess dataAccess = (DemographicDataAccess) servlet
					.getServletContext().getAttribute(
							Constants.Servlet.DEMOGRAPHIC_ACCESS);

			detail = dataAccess.save(detail);

			BeanUtils.copyProperties(form, detail);

			//   org.gnumed.testweb1.global.Util.logBean(log, detail);

			updateSessionDemographicList(detail, request.getSession());
			return mapping.findForward("success");

		} catch (Exception e) {
			log.error("error in " + this.toString(), e);
			messages.add("error in form", new ActionMessage(
					"errors.detailSave", e, e.getCause()));

		} finally {

		}

		saveErrors(request, messages);
		//   return mapping.getInputForward();

		util.setAttributeOnScopeFromMappingAttributeAndScope(request, mapping, form);

		return mapping.getInputForward();
	}

	/**
	 * after saving the modified or new demographicDetail, update it if it is
	 * stored in the session attribute DEMOGRAPHIC_DETAILS which is a list of
	 * found demographic details.
	 */
	void updateSessionDemographicList(DemographicDetail detail,
			HttpSession session) {
		if (session.getAttribute(Constants.Session.DEMOGRAPHIC_DETAILS) != null) {
			java.util.List l = java.util.Collections
					.synchronizedList((java.util.List) session
							.getAttribute(Constants.Session.DEMOGRAPHIC_DETAILS));
			java.util.ListIterator i = l.listIterator();
			while (i.hasNext()) {
				DemographicDetail d = (DemographicDetail) i.next();
				if (d.getId().equals(detail.getId())) {
					i.set(detail);
					return;
				}
			}
			l.add(detail);

		}
	}

}