/*
 * Created on 17-Oct-2004
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
package org.gnumed.testweb1.business;

/**
 * @author sjtan
 *
 * TODO To change the template for this generated type comment go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
public interface ConversionRules {
		public interface ConversionHolder {
			String getUnit();
			double getAmount();
		}
		public String getName();
		public   ConversionHolder convertTo( ConversionHolder fromHolder);
		public   ConversionHolder convertBack( ConversionHolder toHolder);
		
}
