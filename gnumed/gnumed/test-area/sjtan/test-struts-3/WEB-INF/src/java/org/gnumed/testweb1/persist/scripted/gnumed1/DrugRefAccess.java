/*
 * Created on 12-Oct-2004
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
package org.gnumed.testweb1.persist.scripted.gnumed1;
import java.sql.SQLException;

import javax.sql.DataSource;

import org.gnumed.testweb1.data.DrugRef;
import org.gnumed.testweb1.persist.DataObjectFactoryUsing;
import org.gnumed.testweb1.persist.DataSourceUsing;
/**
 * @author sjtan
 *
 * TODO To change the template for this generated type comment go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
public interface DrugRefAccess extends DataSourceUsing, DataObjectFactoryUsing {
	 public void setDataSource( DataSource ds);
    
    public void load() throws SQLException;
    
    public DrugRef[] findDrugRef(String name) throws SQLException;
    
    final static String ID_PRODUCT="id_product", ID_PRODUCT2="id_product2", BRAND_NAME="brandname", 
	ATC_CODE="atc_code", ATC_NAME="atc_name", PKG_SIZE="pkg_size",
	 ROUTE_LONG="route_description" , ROUTE_SHORT="route_abbrev",
	SUBSIDIZIED_QTY="subsidized_qty", MAX_RPT="max_rpt", COPAYMENT="copayment", 
	SUBSIDY_SCHEME = "sub_scheme", COUNTRY_CODE="country_code",
	DRUG_SHORT_DESCRIPTION="drug_description", DRUG_FORMULATION="drug_formulation",
        AMOUNT_UNIT="amount_unit";
    
    final static String[] TABLES= { "atc", "link_product_manufacturer", "drug_formulations",
    "package_size", "drug_units", "drug_routes",  "drug_element", 
    "subsidized_products", "subsidies", "link_drug_atc", "product" };
    
    final static String SELECT_DRUGS_DRUGREF = "select lpm.brandname, " +
    		"atc.code as atc_code, atc.text as atc_name," +
    		" pkgsz.size as pkg_size , " +
    		"du.unit as drug_units, " + "df.description as formulation, "+
    		"dr.description as route_description, dr.abbreviation as route_abbrev," +
    		" sp.quantity as subsidized_qty, sp.max_rpt as max_rpt, sp.copayment," +
    		" su.name as scheme, su.iso_countrycode as country_code " +
			", p.comment as description" +
			" from  subsidized_products sp, subsidies su , l" +
    		"ink_product_manufacturer lpm, atc, product p, " +
    		"drug_formulations form, package_size pkgsz, " +
    		"drug_units du, drug_routes dr, drug_element d," +
    		" link_drug_atc lda " +
    		"where sp.id_product = p.id and sp.id_subsidy = su.id and" +
    		" lpm.id_product= p.id and p.id_packing_unit = du.id and p.id_route = dr.id and" +
    		" pkgsz.id_product  = p.id and p.id_drug = d.id and d.id = lda.id_drug " +
    		"and lda.atccode = atc.code and p.id_formulation = form.id";
    
    final static String SELECT_PRODUCTS_DRUGREF=	"select distinct(p.id) as "+ID_PRODUCT2+",  lpm.brandname as "+ BRAND_NAME+", "+
    	"atc.code as "+ATC_CODE +", atc.text as "+ATC_NAME + ", " +
		"pkgsz.size as " +PKG_SIZE + " , " + "form.description as "+ DRUG_FORMULATION +", "+
    		"du.unit as "+ AMOUNT_UNIT + " , dr.description as "+ ROUTE_LONG + ", " +
    		"dr.abbreviation as " + ROUTE_SHORT + ", p.comment as " + DRUG_SHORT_DESCRIPTION +
			" from link_product_manufacturer lpm," +
    		" atc, product p, drug_formulations form, package_size pkgsz, " +
    		"drug_units du, drug_routes dr, drug_element d, link_drug_atc lda" +
    		" where lpm.id_product= p.id and p.id_packing_unit = du.id and " +
    		"p.id_route = dr.id and pkgsz.id_product  = p.id and " +
    		"p.id_drug = d.id and d.id = lda.id_drug and lda.atccode = atc.code " +
    		"and p.id_formulation = form.id order by p.id  ";
    final static String SELECT_SUBSIDIES_DRUGREF="select   sp.id_product as "+ID_PRODUCT+" , " +
    		" sp.quantity as "+ SUBSIDIZIED_QTY + ", sp.max_rpt as "+MAX_RPT+", " +
    		"sp.copayment as " + COPAYMENT +", su.name as "+SUBSIDY_SCHEME +", " +
    		" su.iso_countrycode as "+COUNTRY_CODE+"  from  " +
    		"subsidized_products sp, subsidies su  " +
    		"where sp.id_subsidy = su.id order by sp.id_product";
//    
//    final static String VIEW_NAME = "v_drugref1";
//    
//    final static String CREATE_VIEW_DRUGS = "create view "+VIEW_NAME+" as select * from ( "
//    	+SELECT_PRODUCTS_DRUGREF+") as products " +
//    			"left outer join (" + SELECT_SUBSIDIES_DRUGREF +
//				") as subsidy on (subsidy."+ID_PRODUCT+"=products."+ID_PRODUCT2+") ";

   final static String SELECT_DRUGREF = 
   "select * from ("+SELECT_PRODUCTS_DRUGREF+") as products " +
   		"left outer join (" + SELECT_SUBSIDIES_DRUGREF+
                ") as subsidy" +
                " on (subsidy."+ID_PRODUCT+"=products."+ID_PRODUCT2+") ";
   
  
}
