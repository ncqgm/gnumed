/*
 * PlainLetterBasicGenerator.java
 *
 * Created on 26 August 2003, 17:56
 */

package quickmed.usecases.test;
import org.gnumed.gmIdentity.identity;
import java.text.*;
import java.util.*;
import java.util.logging.*;
import java.io.*;
import gnmed.test.DomainPrinter;
/**
 *
 * @author  syan
 */
public class PlainLetterBasicGenerator implements BasicLetterGenerationCapable {
    
      public static final int DEFAULT_PLAINTEXT_LINELEN= 56;
    public static final int DEFAULT_PLAINTEXT_TABSIZE = 8;
    public static final int HACKY_LEFT_MARGIN = 4;
     
    final static String referralFormatString = "\n\n{0, date}\n\n\n{1},\n{2},\n{3}, {4}.\n\n{5},\n{6}\n\n{7}\n\n\t\t\t{8}";
    
    /** Holds value of property client. */
    private identity client;
    
    /** Holds value of property provider. */
    private identity provider;
    
    
    private String referralFilename;
     /** Holds value of property letter. */
    private String letter;
    
    /** Holds value of property plainTextLineLength. */
    private int plainTextLineLength;
    
    /** Holds value of property plainTextTabSize. */
    private int plainTextTabSize;
    
    /** Holds value of property leftMargin. */
    private int leftMargin;
    /** Creates a new instance of PlainLetterBasicGenerator */
    public PlainLetterBasicGenerator() {
         setPlainTextLineLength(DEFAULT_PLAINTEXT_LINELEN);
        setPlainTextTabSize(DEFAULT_PLAINTEXT_TABSIZE);
        setLeftMargin(HACKY_LEFT_MARGIN);
    }
    public void generateReferralFile()  throws Exception {
        if (getClient().getPersister() instanceof ManagerReference) {
            ManagerReference ref = ( ManagerReference) getClient().getPersister();
            net.sf.hibernate.Session sess = ref.getGISManager().getSession();
            //            if (!sess.isConnected())
            //                sess.reconnect();
            
        }
        
        StringBuffer sb = new StringBuffer();
        org.gnumed.gmGIS.address a = getProvider().findIdentityAddressByAddressType(TestGISManager.homeAddress).getAddress();
        String street = new StringBuffer().append(a.getNumber()).append(", ").append(a.getStreet().getName()).toString();
        String urb = a.getStreet().getUrb().getName();
        String state = a.getStreet().getUrb().getState().getName();
        String postcode = a.getStreet().getUrb().getPostcode();
        MessageFormat mf2 = new MessageFormat(Globals.bundle.getString("neutral_greetings_format"));
        
        String greetings = mf2.format(
        new Object[] {        getProvider().findNames(0).getFirstnames() ,getProvider().findNames(0).getLastnames() });
        
        MessageFormat mf3 = new MessageFormat(Globals.bundle.getString("basic_spiel_format"));
        String spiel = mf3.format(
        new Object[] { getClient().findNames(0).getFirstnames(), getClient().findNames(1).getLastnames(), getClient().getDob() } );
        
        
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        PrintStream ps = new PrintStream( bos);
        
        DomainPrinter.getInstance().printIdentity(ps, getClient());
        String summary = bos.toString();
        String salutations = Globals.bundle.getString("salutations");
        
        MessageFormat mf = new MessageFormat(referralFormatString);
        
        String letter = mf.format( new Object[] { new Date(), street, urb, state, postcode, greetings , spiel, summary, salutations }  );
        
        
        
        // create title
        org.gnumed.gmIdentity.Names cn = getClient().findNames(0);
        
        sb.append(cn.getLastnames()).append('_').append(cn.getFirstnames()).append('_');
        sb.append(DateFormat.getDateTimeInstance(DateFormat.SHORT, DateFormat.SHORT).format(new Date()));
        sb.append(".txt");
        for (int i = 0; i < sb.length(); ++i)
            if (Character.isSpaceChar(sb.charAt(i)) )
                sb.setCharAt(i, '_');
        
        setReferralFilename(sb.toString());
        //        File path = new File(".", getReferralFilename());
        //        path.createNewFile();
        //
        //        OutputStream fos =  new BufferedOutputStream(new FileOutputStream(path));
        //        PrintStream ps2 = new PrintStream(fos);
        //         ps2.println(letter);
        //
        //        fos.close();
        setLetter(addSoftLeftMargin(wordWrap(letter, getPlainTextLineLength(), getPlainTextTabSize())) );
         
    }
     
    public String addSoftLeftMargin(String letter) {
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        PrintStream ps = new PrintStream( bos);
        char[] margin = new char[ getLeftMargin()];
        Arrays.fill(margin, ' ');
        ps.print(margin);
        for ( int j = 0; j < letter.length(); ++j) {
            if (letter.charAt(j) == '\n' ) {
                ps.print('\n');
                ps.print(margin);
                continue;
            }
            
            ps.print(letter.charAt(j) );
        }
        return bos.toString();
    }
    
    public String transformToPlatformNewlines(String letter) {
        
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        PrintStream ps = new PrintStream( bos);
        
        // transform /n to platform specific newline
        for (int j = 0;j < letter.length(); ++j) {
            if (letter.charAt(j) == '\n') {
                ps.println();
            }
            ps.print(letter.charAt(j));
        }
        return  bos.toString();
    }
    
    public String wordWrap( String letter , int triggerLineLength, int tabSize) {
        int len = 0;
        StringBuffer buf = new StringBuffer();
        for (int j = 0;j < letter.length(); ++j) {
            //            Logger.global.info("Char at " + j + " = "
            //            + Character.toString(letter.charAt(j) ) + " ; type = " +
            //            (String) ( Character.isWhitespace(letter.charAt(j) ) ? "whitespace ":
            //                 (Character.isSpaceChar(letter.charAt(j)) ? "unicode space ":
            //                     (
            //                    Character.isSpaceChar(letter.charAt(j)) ? "normal space" :
            //                      (  Character.isLetterOrDigit(letter.charAt(j)) ? "letter or digit" :
            //                            "some other character other than whitespace or alnum" ) ) )) );
            if (letter.charAt(j) == '\t')
                len += tabSize;
            else
                if (letter.charAt(j) == '\n')
                    len = 0;
            if (len >= triggerLineLength
            &&(
            //             Character.isISOControl(letter.charAt(j)) ||
            Character.isWhitespace(letter.charAt(j) ) )  ) {
                Logger.global.info("APPENDING CR");
                buf.append('\n');
                len = 0;
                continue;
            }
            
            buf.append(letter.charAt(j));
            ++len;
        }
        return buf.toString();
    }
    /** Getter for property referralFilename.
     * @return Value of property referralFilename.
     *
     */
    public String getReferralFilename() {
        return this.referralFilename;
    }
    
    /** Setter for property referralFilename.
     * @param referralFilename New value of property referralFilename.
     *
     */
    public void setReferralFilename(String referralFilename) {
        this.referralFilename = referralFilename;
    }
    
    /** Getter for property letter.
     * @return Value of property letter.
     *
     */
    public String getLetter() {
        if (letter == null)
            return "";
        return this.letter;
    }
    
    /** Setter for property letter.
     * @param letter New value of property letter.
     *
     */
    public void setLetter(String letter) {
        this.letter = letter;
    }
    
    /** Getter for property plainTextLineLength.
     * @return Value of property plainTextLineLength.
     *
     */
    public int getPlainTextLineLength() {
        return this.plainTextLineLength;
    }
    
    /** Setter for property plainTextLineLength.
     * @param plainTextLineLength New value of property plainTextLineLength.
     *
     */
    public void setPlainTextLineLength(int plainTextLineLength) {
        this.plainTextLineLength = plainTextLineLength;
    }
    
    /** Getter for property plainTextTabSize.
     * @return Value of property plainTextTabSize.
     *
     */
    public int getPlainTextTabSize() {
        return this.plainTextTabSize;
    }
    
    /** Setter for property plainTextTabSize.
     * @param plainTextTabSize New value of property plainTextTabSize.
     *
     */
    public void setPlainTextTabSize(int plainTextTabSize) {
        this.plainTextTabSize = plainTextTabSize;
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
    /** Getter for property client.
     * @return Value of property client.
     *
     */
    public identity getClient() {
        return this.client;
    }
    
    /** Setter for property client.
     * @param client New value of property client.
     *
     */
    public void setClient(identity client) {
        this.client = client;
    }
    
    /** Getter for property provider.
     * @return Value of property provider.
     *
     */
    public identity getProvider() {
        return this.provider;
    }
    
    /** Setter for property provider.
     * @param provider New value of property provider.
     *
     */
    public void setProvider(identity provider) {
        this.provider = provider;
    }
    
    public void printTo( PrintStream ps) {
        ps.print( transformToPlatformNewlines(getLetter()) );
    }
    
    public void printTo(PrintWriter pw) {
        pw.print( transformToPlatformNewlines(getLetter()) );
    }
    
    public void execute() throws Exception  {
        generateReferralFile();
    }
    
}
