/*
 * MedicareBasicScriptPrintable.java
 *
 * Created on 30 August 2003, 09:44
 */

package quickmed.usecases.test;
import java.util.*;
import org.gnumed.gmClinical.*;
import java.awt.print.*;
import java.awt.Point;
import java.awt.Font;
import java.awt.Rectangle;
import java.awt.Graphics;
import java.text.DateFormat;
import org.gnumed.gmIdentity.*;
import org.gnumed.gmGIS.*;
import java.util.logging.*;
/**
 *
 * @author  syan
 */
public class MedicareBasicScriptPrintable implements BasicScriptPrintable, BasicScriptFormLayoutAdjustable {
    public static final int DEFAULT_MAX_CHARS_ACROSS = 60;
    public static final int DEFAULT_SCRIPT_SPLIT_WIDTH = 235;
    public static final int DEFAULT_MAX_HEIGHT = 700;
    private Object prescriber;
    private Object patient;
    private java.util.Date date;
    private java.util.List scriptDrugs;
    //    private java.awt.print.Pageable pageable = new MedicareBasicScriptPrintable.MedicareScriptPageable();
    private MedicareScriptPageable medicarePageable = new MedicareBasicScriptPrintable.MedicareScriptPageable();
    
    /** Creates a new instance of MedicareBasicScriptPrintable */
    public MedicareBasicScriptPrintable() {
        setMaxCharsAcross(DEFAULT_MAX_CHARS_ACROSS);
//        medicarePageable.printable.setSplitWidth(DEFAULT_SCRIPT_SPLIT_WIDTH);
    }
    
    public MedicarePrintable getMedicarePrintable() {
        return  medicarePageable.printable;
    }
    
    class MedicareScriptPageable implements java.awt.print.Pageable {
        MedicareBasicScriptPrintable.MedicarePrintable printable = new MedicarePrintable();
        int drugsPerPage = 3;
        java.util.List authorityDrugs = new java.util.ArrayList();
        java.util.List privateDrugs = new java.util.ArrayList();
        java.util.List publicDrugs  = new java.util.ArrayList();
        PageFormat format = new PageFormat();
        
        Paper paper = new Paper();
        
        /** Holds value of property maxCharsAcross. */
        private int maxCharsAcross;
        
        
        public   MedicareScriptPageable() {
            format.setOrientation(format.PORTRAIT);
            format.setPaper(paper);
        }
        
        int getPublicPageCount() {
            return      getEnoughPages(publicDrugs.size() , drugsPerPage);
        }
        int getPrivatePageCount() {
            
            return   getEnoughPages(privateDrugs.size() , drugsPerPage);
        }
        
        int getAuthorityPageCount() {
            return authorityDrugs.size();
        }
        
        int getEnoughPages(int items, int perPage ) {
            return (  items % perPage != 0 ? 1 : 0 )  +  items/perPage ;
        }
        
        public int getNumberOfPages() {
            return getPublicPageCount() + getPrivatePageCount() + getAuthorityPageCount();
        }
        
        public java.awt.print.PageFormat getPageFormat(int pageIndex) throws IndexOutOfBoundsException {
//            Paper p = new Paper();
//            p.setImageableArea(0, 0, 72 * 4 , 72 * 5);
//            p.setSize(72 * 4, 72 * 5);
//           
//            format.setPaper(p);
            return format;
        }
        
        public MedicareBasicScriptPrintable.MedicarePrintable getMedicarePrintable() {
            return printable;
        }
        
        public java.awt.print.Printable getPrintable(int pageIndex) throws IndexOutOfBoundsException {
            if (pageIndex > getNumberOfPages())
                throw new IndexOutOfBoundsException();
            if (pageIndex < 0)
                throw new IndexOutOfBoundsException();
            
            if (pageIndex <  getPublicPageCount() ) {
                return getPrintableFor( publicDrugs, drugsPerPage, pageIndex, true);
                
            }
            
            if (pageIndex < getPublicPageCount() + getPrivatePageCount() ) {
                return getPrintableFor(privateDrugs, 1, pageIndex - getPublicPageCount(), false);
            }
            
            
            return null;
        }
        
        MedicarePrintable clonePrintable() {
            MedicarePrintable printable = this.printable;
            try {
                printable =(MedicarePrintable ) this.printable.getClass().newInstance();
                printable.setSplitWidth(this.printable.getSplitWidth());
                printable.setOriginMedicareNumber(getOriginHealthNumber());
                printable.setOriginPatientDetail(getOriginPatientDetail());
                printable.setOriginProviderDetail(getOriginProviderDetails());
                printable.setOriginScriptDetail(getOriginDrugDetails());
                printable.setOriginDate(getOriginDate());
                printable.setOriginSubsidized(getOriginSubsidized());
                printable.setFontSize(getFontSize());
                printable.setLeftMargin(getLeftMargin());
            } catch (Exception e) {
                e.printStackTrace();
            }
            return printable;
        }
        
        Printable getPrintableFor( List list, int drugsPerPage, int page, boolean subsidized) {
            int offset = page * drugsPerPage;
             MedicarePrintable printable  = clonePrintable();
           
            printable.setDate( new Date());
            
            social_identity medicareNo = ((identity)getPatient()).findSocialIdentityByEnum(IdentityManager.medicare);
            printable.setMedicareNumber(medicareNo.getNumber());
            
            printable.setProviderDetail(getProviderDetail());
            printable.setPatientDetail(getPatientDetail());
            printable.setScriptDetail(getScriptDetail( list, offset, drugsPerPage)) ;
            printable.setSubsidized(subsidized);
            return printable;
        }
        
        public String[] getScriptDetail(List list, int offset, int count) {
            
            link_script_drug[] lsds = (link_script_drug[])list.toArray(new link_script_drug[0]);
            List lines = new ArrayList();
            int c = 0;
            for (int i = offset; i < offset+count && i < lsds.length ; ++i) {
                Logger.global.info("*** PRINTING DRUG WITH INDEX = " + i);
                addParagraphedLines( lines, lsds[i].getScript_drug().toString());
                lines.add(lsds[i].getRepeats() + " " + Globals.bundle.getString("repeats"));
                lines.add("");
                lines.add("");
                ++c;
            }
            lines.add("");
            lines.add( new Integer(c).toString() + " items");
            return (String[]) lines.toArray(new String[0]);
        }
        
        public void addParagraphedLines(List lines, String text) {
            StringBuffer sb = new StringBuffer(text);
            while (sb.length() > getMaxCharsAcross()) {
                int  i = 0;
                for (i= getMaxCharsAcross(); Character.isLetterOrDigit(sb.charAt(i)) && i > 0; --i);
                lines.add(sb.substring(0, i+1));
                sb.delete(0, i+1);
            }
            lines.add(sb.toString());
        }
        
        public String[] getPatientDetail() {
            List lines = new ArrayList();
            
            if (getPatient() == null || !( getPatient() instanceof identity))
                return new String[0];
            identity p = (identity)getPatient();
            lines.add( p.findNames(0).toString());
            lines.add(p.findIdentityAddressByAddressType(TestGISManager.homeAddress).getAddress().toString());
            return (String[]) lines.toArray(new String[0]);
        }
        
        
        public String[] getProviderDetail() {
            if ( getPrescriber() instanceof identity) {
                identity p = (identity) getPrescriber();
                Names n = p.findNames(0);
                if (n == null)
                    return new String[] { "PLEASE FILL IN PROVIDER DETAILS" };
                    StringBuffer sb = new StringBuffer();
                    List lines = new ArrayList();
                    sb.append(n); lines.add(sb.toString());
                    social_identity id  = p.findSocialIdentityByEnum(IdentityManager.prescriberNo);
                    if (id != null)
                        lines.add( IdentityManager.prescriberNo + " " + id);
                    telephone t = p.findTelephoneByRole(TestGISManager.work);
                    
                    
                    if ( t != null) {
                        sb = new StringBuffer();
                        sb.append(TestGISManager.work.getRole()).append(":").append(t.getNumber());
                        lines.add(sb.toString());
                    }
                    identities_addresses ia = p.findIdentityAddressByAddressType(TestGISManager.workAddress);
                    if (ia != null) {
                        lines.add(ia.getAddress().toString());
                    }
                    return (String[]) lines.toArray(new String[0]);
            }
            return new String[] {  "NO PROVIDER DETAILS" };
        }
        
        /** Getter for property maxCharsAcross.
         * @return Value of property maxCharsAcross.
         *
         */
        public int getMaxCharsAcross() {
            return this.maxCharsAcross;
        }
        
        /** Setter for property maxCharsAcross.
         * @param maxCharsAcross New value of property maxCharsAcross.
         *
         */
        public void setMaxCharsAcross(int maxCharsAcross) {
            this.maxCharsAcross = maxCharsAcross;
        }
        
    }
    
    public static class MedicarePrintable implements Printable  {
        
        /** Holds value of property fontSize. */
        private int fontSize = 8;
        
        /** Holds value of property originProviderDetail. */
        private Point originProviderDetail = new Point(10, 100);
        
        /** Holds value of property originMedicareNumber. */
        private Point originMedicareNumber = new Point( 50, 160);
        
        /** Holds value of property originPatientDetail. */
        private Point originPatientDetail = new Point( 60, 190);
        
        /** Holds value of property providerDetail. */
        private String[] providerDetail;
        
        /** Holds value of property patientDetail. */
        private String[] patientDetail;
        
        /** Holds value of property scriptDetail. */
        private String[] scriptDetail;
        
        /** Holds value of property subsidized. */
        private boolean subsidized;
        
        /** Holds value of property medicareNumber. */
        private String medicareNumber;
        
        /** Holds value of property originDate. */
        private Point originDate = new Point( 10, 190);
        
        /** Holds value of property originSubsidized. */
        private Point originSubsidized = new Point(10, 220);
        
        /** Holds value of property originScriptDetail. */
        private Point originScriptDetail = new Point( 10, 280);
        
        /** Holds value of property date. */
        private Date date;
        
        /** Holds value of property splitWidth. */
        private int splitWidth = DEFAULT_SCRIPT_SPLIT_WIDTH;
        
        /** Holds value of property leftMargin. */
        private int leftMargin = 70;
        
        /** currently ignores format and pageIndex
         */
        public int print(java.awt.Graphics graphics, PageFormat pageFormat, int pageIndex) throws PrinterException {
            Rectangle r = graphics.getClipBounds();
            if (r == null)
                graphics.setClip(getLeftMargin(),0, getLeftMargin() + getSplitWidth() * 2, DEFAULT_MAX_HEIGHT);
            r = graphics.getClipBounds();
            Logger.global.info("rectangle = " + r);
            
            Graphics g1 = graphics.create(getLeftMargin(),0,getLeftMargin()+ getSplitWidth(), (int)graphics.getClipBounds().getHeight());
            printImpl(g1, pageFormat, pageIndex);
            Graphics g2 = graphics.create(getLeftMargin() + getSplitWidth(), 0, (int)graphics.getClipBounds().width, graphics.getClipBounds().height);
            int result = printImpl(g2, pageFormat , pageIndex);
            g1.dispose();
            g2.dispose();
            return result;
            
        }
        
        int printImpl(java.awt.Graphics graphics, PageFormat pageFormat, int pageIndex) throws PrinterException {
            try {
                Font f = graphics.getFont().deriveFont(Font.PLAIN, (float)getFontSize());
                graphics.setFont(f);
                
                
                //                double halfWidth = r.getWidth() /(double)2.0;
                int  height = graphics.getFontMetrics().getHeight();
                printText( graphics, getProviderDetail(), getOriginProviderDetail());
                printText( graphics, new String[] { getMedicareNumber() }, getOriginMedicareNumber());
                printText(graphics, getPatientDetail(), getOriginPatientDetail());
                printText(graphics ,  new String[] { DateFormat.getDateInstance(DateFormat.SHORT).format(getDate()) }, getOriginDate() );
                printText(graphics, new String[] { isSubsidized() ? "y": "N" }, getOriginSubsidized() );
                printText(graphics,  getScriptDetail()  , getOriginScriptDetail() );
                return PAGE_EXISTS;
            } catch (Exception e) {
                e.printStackTrace();
            }
            return NO_SUCH_PAGE;
        }
        
        void printText( java.awt.Graphics graphics, String[] lines, Point origin ) {
            for (int i = 0; i < lines.length; ++i) {
                graphics.drawString(lines[i], origin.x, origin.y + graphics.getFontMetrics().getHeight() * i );
            }
        }
        
        /** Getter for property fontSize.
         * @return Value of property fontSize.
         *
         */
        public int getFontSize() {
            return this.fontSize;
        }
        
        /** Setter for property fontSize.
         * @param fontSize New value of property fontSize.
         *
         */
        public void setFontSize(int fontSize) {
            this.fontSize = fontSize;
        }
        
        /** Getter for property originProviderDetail.
         * @return Value of property originProviderDetail.
         *
         */
        public Point getOriginProviderDetail() {
            return this.originProviderDetail;
        }
        
        /** Setter for property originProviderDetail.
         * @param originProviderDetail New value of property originProviderDetail.
         *
         */
        public void setOriginProviderDetail(Point originProviderDetail) {
            this.originProviderDetail = originProviderDetail;
        }
        
        /** Getter for property originMedicareNumber.
         * @return Value of property originMedicareNumber.
         *
         */
        public Point getOriginMedicareNumber() {
            return this.originMedicareNumber;
        }
        
        /** Setter for property originMedicareNumber.
         * @param originMedicareNumber New value of property originMedicareNumber.
         *
         */
        public void setOriginMedicareNumber(Point originMedicareNumber) {
            this.originMedicareNumber = originMedicareNumber;
        }
        
        /** Getter for property originPatientDetail.
         * @return Value of property originPatientDetail.
         *
         */
        public Point getOriginPatientDetail() {
            return this.originPatientDetail;
        }
        
        /** Setter for property originPatientDetail.
         * @param originPatientDetail New value of property originPatientDetail.
         *
         */
        public void setOriginPatientDetail(Point originPatientDetail) {
            this.originPatientDetail = originPatientDetail;
        }
        
        /** Getter for property providerDetail.
         * @return Value of property providerDetail.
         *
         */
        public String[] getProviderDetail() {
            return this.providerDetail;
        }
        
        /** Setter for property providerDetail.
         * @param providerDetail New value of property providerDetail.
         *
         */
        public void setProviderDetail(String[] providerDetail) {
            this.providerDetail = providerDetail;
        }
        
        /** Getter for property patientDetail.
         * @return Value of property patientDetail.
         *
         */
        public String[] getPatientDetail() {
            return this.patientDetail;
        }
        
        /** Setter for property patientDetail.
         * @param patientDetail New value of property patientDetail.
         *
         */
        public void setPatientDetail(String[] patientDetail) {
            this.patientDetail = patientDetail;
        }
        
        /** Getter for property scriptDetail.
         * @return Value of property scriptDetail.
         *
         */
        public String[] getScriptDetail() {
            return this.scriptDetail;
        }
        
        /** Setter for property scriptDetail.
         * @param scriptDetail New value of property scriptDetail.
         *
         */
        public void setScriptDetail(String[] scriptDetail) {
            this.scriptDetail = scriptDetail;
        }
        
        /** Getter for property subsidized.
         * @return Value of property subsidized.
         *
         */
        public boolean isSubsidized() {
            return this.subsidized;
        }
        
        /** Setter for property subsidized.
         * @param subsidized New value of property subsidized.
         *
         */
        public void setSubsidized(boolean subsidized) {
            this.subsidized = subsidized;
        }
        
        /** Getter for property medicareNumber.
         * @return Value of property medicareNumber.
         *
         */
        public String getMedicareNumber() {
            return this.medicareNumber;
        }
        
        /** Setter for property medicareNumber.
         * @param medicareNumber New value of property medicareNumber.
         *
         */
        public void setMedicareNumber(String medicareNumber) {
            this.medicareNumber = medicareNumber;
        }
        
        /** Getter for property originDate.
         * @return Value of property originDate.
         *
         */
        public Point getOriginDate() {
            return this.originDate;
        }
        
        /** Setter for property originDate.
         * @param originDate New value of property originDate.
         *
         */
        public void setOriginDate(Point originDate) {
            this.originDate = originDate;
        }
        
        /** Getter for property originSubsidized.
         * @return Value of property originSubsidized.
         *
         */
        public Point getOriginSubsidized() {
            return this.originSubsidized;
        }
        
        /** Setter for property originSubsidized.
         * @param originSubsidized New value of property originSubsidized.
         *
         */
        public void setOriginSubsidized(Point originSubsidized) {
            this.originSubsidized = originSubsidized;
        }
        
        /** Getter for property originScriptDetail.
         * @return Value of property originScriptDetail.
         *
         */
        public Point getOriginScriptDetail() {
            return this.originScriptDetail;
        }
        
        /** Setter for property originScriptDetail.
         * @param originScriptDetail New value of property originScriptDetail.
         *
         */
        public void setOriginScriptDetail(Point originScriptDetail) {
            this.originScriptDetail = originScriptDetail;
        }
        
        /** Getter for property date.
         * @return Value of property date.
         *
         */
        public Date getDate() {
            return this.date;
        }
        
        /** Setter for property date.
         * @param date New value of property date.
         *
         */
        public void setDate(Date date) {
            this.date = date;
        }
        
        /** Getter for property splitWidth.
         * @return Value of property splitWidth.
         *
         */
        public int getSplitWidth() {
            return this.splitWidth;
        }
        
        /** Setter for property splitWidth.
         * @param splitWidth New value of property splitWidth.
         *
         */
        public void setSplitWidth(int splitWidth) {
            this.splitWidth = splitWidth;
        }
        
        /** Getter for property leftMargin.
         * @return Value of property leftMargin.
         *
         */
        public int getLeftMargin() {
            return this.leftMargin;
        }        
        
        /** Setter for property leftMargin.
         * @param leftMargin New value of property leftMargin.
         *
         */
        public void setLeftMargin(int leftMargin) {
            this.leftMargin = leftMargin;
        }
        
    }
    
    public java.awt.print.Pageable getPageable() {
        return medicarePageable;
    }
    
    public Object getPatient() {
        return patient;
    }
    
    public Object getPrescriber() {
        return prescriber;
    }
    
    public java.util.Date getScriptDate() {
        return date;
    }
    
    public java.util.List getScriptItems() {
        return     scriptDrugs ;
    }
    
    public void setPatient(Object patient) {
        this.patient = patient;
    }
    
    public void setPrescriber(Object prescriber) {
        this.prescriber = prescriber;
    }
    
    public void setScriptDate(java.util.Date scriptDate) {
        this.date = scriptDate;
    }
    
    public void setScriptItems(java.util.List scriptItems) {
        scriptDrugs = scriptItems;
        categorizeDrugs();
    }
    
    void categorizeDrugs() {
        medicarePageable.publicDrugs.clear();
        medicarePageable.authorityDrugs.clear();
        medicarePageable.privateDrugs.clear();
        List l = getScriptItems();
        for (int i = 0; i < l.size(); ++i) {
            if (l.get(i) instanceof link_script_drug) {
                link_script_drug lsd = (link_script_drug) l.get(i);
                Logger.global.info( "lsd = " + lsd   );
                try {
                    
                    Logger.global.info("lsd.script_drug=" + lsd.getScript_drug());
                    Logger.global.info("lsd.script_drug.package_size=" + lsd.getScript_drug().getPackage_size() );
                } catch (Exception e) {
                    for (int j = 0;j < e.getStackTrace().length; ++j)
                        System.err.println(e.getStackTrace()[j]);
                    
                }
                try {
                    if (lsd.getScript_drug().getPackage_size().getProduct().getSubsidized_productss().isEmpty() ) {
                        medicarePageable.privateDrugs.add(lsd);
                        continue;
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                }
                
                medicarePageable.publicDrugs.add(lsd);
            }
            Logger.global.info("Medicare drugs = " + medicarePageable.publicDrugs.size() + " Private drugs = " + medicarePageable.privateDrugs.size() );
        }
        
    }
    
    /** Getter for property maxCharsAcross.
     * @return Value of property maxCharsAcross.
     *
     */
    public int getMaxCharsAcross() {
        return medicarePageable.getMaxCharsAcross();
    }
    
    /** Setter for property maxCharsAcross.
     * @param maxCharsAcross New value of property maxCharsAcross.
     *
     */
    public void setMaxCharsAcross(int maxCharsAcross) {
        medicarePageable.setMaxCharsAcross(maxCharsAcross);
    }
    
    /** Getter for property splitWidth.
     * @return Value of property splitWidth.
     *
     */
    public int getSplitWidth() {
        return medicarePageable.printable.getSplitWidth();
    }
    
    /** Setter for property splitWidth.
     * @param splitWidth New value of property splitWidth.
     *
     */
    public void setSplitWidth(int splitWidth) {
        medicarePageable.printable.setSplitWidth(splitWidth);
    }
    
    /** Getter for property fontSize.
     * @return Value of property fontSize.
     *
     */
    public int getFontSize() {
        return  medicarePageable.printable.getFontSize();
    }
    
    /** Setter for property fontSize.
     * @param fontSize New value of property fontSize.
     *
     */
    public void setFontSize(int fontSize) {
        medicarePageable.printable.setFontSize(fontSize);
    }
    
    public BasicScriptFormLayoutAdjustable getAdjustableLayout() {
        return this;
    }
    
    public Point getOriginDate() {
        return medicarePageable.getMedicarePrintable().getOriginDate();
    }
    
    public Point getOriginDrugDetails() {
        return medicarePageable.getMedicarePrintable().getOriginScriptDetail();
    }
    
    public Point getOriginHealthNumber() {
        return medicarePageable.getMedicarePrintable().getOriginMedicareNumber();
    }
    
    public Point getOriginPatientDetail() {
        return medicarePageable.getMedicarePrintable().getOriginPatientDetail();
    }
    
    public Point getOriginProviderDetails() {
        return medicarePageable.getMedicarePrintable().getOriginProviderDetail();
    }
    
    public Point getOriginSignoff() {
        return null;
        //     return medicarePageable.getMedicarePrintable().get
    }
    
    public Point getOriginSubsidized() {
        return medicarePageable.getMedicarePrintable().getOriginSubsidized();
    }
    
    public void setOriginDate(Point originDate) {
        medicarePageable.getMedicarePrintable().setOriginDate(originDate);
    }
    
    public void setOriginDrugDetails(Point originDrugDetails) {
        medicarePageable.getMedicarePrintable().setOriginScriptDetail(originDrugDetails);
    }
    
    
    public void setOriginHealthNumber(Point originHealthNumber) {
        medicarePageable.getMedicarePrintable().setOriginMedicareNumber(originHealthNumber);
    }
    
    public void setOriginPatientDetail(Point originPatientDetail) {
        medicarePageable.getMedicarePrintable().setOriginPatientDetail(originPatientDetail);
    }
    
    public void setOriginProviderDetails(Point originProviderDetails) {
        medicarePageable.getMedicarePrintable().setOriginProviderDetail(originProviderDetails);
    }
    
    public void setOriginSignoff(Point originSignoff) {
    }
    
    public void setOriginSubsidized(Point originSubsidized) {
        medicarePageable.getMedicarePrintable().setOriginSubsidized(originSubsidized);
    }
    
    public int getLeftMargin() {
        return medicarePageable.getMedicarePrintable().getLeftMargin();
    }
    
    public void setLeftMargin(int leftMargin) {
        medicarePageable.getMedicarePrintable().setLeftMargin(leftMargin);
    }
    
}
