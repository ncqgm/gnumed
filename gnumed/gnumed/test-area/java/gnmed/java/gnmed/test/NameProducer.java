/*
 * NameProducer.java
 *
 * Created on 12 June 2003, 21:10
 */

package gnmed.test;
import java.util.Random;

import java.util.*;
/**
 *
 * @author  sjtan
 */
public class NameProducer {
    
    public static final String [] countries = { "Australia", "Germany", "Canada" , "Singapore" };
    public static  final String [] streets = { "st", "st", "st", "st", "rd", "Ave", "Gve", "Pde" };
    
    final static String[] surnames = {
        "Adams" , "Au", "Ang", "Alexandros", "Armani", "Aitken", "Atkinson", "Ali",
        "Burden", "Bowden", "Burke", "Bevan", "Bill", "Bronowski", "Blatski", "Bui",
        "Caroll", "Czarnecki", "Comer", "Callan", "Cameron", "Chong", "Chan", "Czilla",
        "David", "Dobrowski", "Dong", "D'Souza", "Dakis", "Dell", "Darwin", "Dodd", "De Beer",
        "Estefan", "Ellis", "Evans", "Eade", "El Salvadori", "El Cid",
        "Farnsby", "Fui", "Foo", "Fotakis", "Fairlane", "Fellini",
        "Greer", "Grotan", "Gordon", "Gage", "Gagliato", "Gideon",
        "Harry", "Hermes", "Halloway", "Hillebrand", "Hui",
        "Iliossi", "Ireland", "Innes", "Imbruglio", "Inventes",
        "Joon", "Jorgen", "Jarman", "Jules", "Juliosi",
        "Khan", "Kraag", "Khol",
        "Lim", "Lucia", "Le Man", "Lefevre", "Lavoisoir",
        "Morgan", "Milton", "Mohammed", "Marks", "McMann", "MacDonald",
        "Nguyen", "Norgen",
        "Osborne", "Ooi", "Olowasi", "Oban",
        "Peters", "Pak", "Parker", "Perugia",
        "Quinn", "Quan",
        "Sarak", "Soo", "Sorbonne", "Sardin", "Son",
        "Thomas", "Thui", "Tali", "Tak", "Terry", "Tamada",
        "Ubako", "Una", "Unsborough",
        "Vermont", "Vasgama", "Velas", "Victorio",
        "Whelan", "Woo", "Wal",
        "Xi",
        "Yu", "Yamada",
        "Zolk", "Zelleg" };
        
        final static String[] femaleFirst = {
            "Alice", "Anna", "Amy", "Aileen",
            "Betty", "Beatrice",
            "Chawtha", "Chai",
            "Diane", "Dana", "Delilah", "Deborah", "Denise", "Darlene",
            "Elizabeth", "Elle", "Emma",
            "Fay", "Flavia",
            "Heidi", "Heather", "Hillary",
            "Ivy","Ima",
            "Julia", "Jenny", "Judy", "Jane", "Judith",
            "Karen", "Katherine", "Kay",
            "Lisa", "Linda",
            "Maria", "Marie", "Madeline", "Margeret", "Mani",
            "Nina", "Nena",
            "Priscilla", "Penny", "Pauline",
            "Raelene", "Roberta", "Rene",
            "Sally", "Selina","Silvia","Simone",
            "Theresa", "Thelma", "Tamara", "Tess",
            "Uma", "Una", "Uki",
            "Veronica", "Violet",
            "Wilma",
        };
        
        final static String[] maleFirst = {
            "Adam", "Aaron", "Amon", "Amir", "Amos", "Ali",
            "Ben",
            "Cameron", "Con", "Charles",
            "David", "Duncan", "Davros",
            "Elise", "Eric",
            "Fred", "Florio",
            "Grogan", "Gavin", "Gianne", "Gregori",
            "Herbert", "Hanne",  "Hani", "Hobi",
            "Ignatius", "Ian", "Ike",
            "John", "Johannes", "Jorges", "Julio", "Jules",
            
            "Len", "Louis", "Larry",
            "Mark", "Matthew", "Martin", "Michael",
            "Nick", "Nestor",  "Nigel", "Noel",
            "Ogi",
            "Pedro", "Pierre", "Paul",
            "Robert", "Ramon",
            "Simon", "Selwyn",
            "Tom",
            
            "Valentino",
            "Wai Yin", "Wilson",
            "Xavier",
            "Yuri",
            "Zoltan"  };
            static Random r = new Random();
            
            public static boolean getMale() {
                return r.nextInt(100) < 50;
            }
            
            public static String[] getFirstLastName(boolean male) throws Exception {
                String first = male ? NameProducer.getMaleFirst() : NameProducer.getFemaleFirst();
                String last =NameProducer.getLastNames();
                return new String[] { first, last };
                
            }
            
            public static String getId() {
               Integer i = new Integer( r.nextInt( 99999999) );
                return i.toString();
            }
            
            public static  Date getBirth() {
                Calendar cal = Calendar.getInstance();
                cal.set( 1910 + r.nextInt(93) , r.nextInt(12) + 1, 1);
                cal.set( cal.DAY_OF_MONTH, cal.getMaximum(cal.DAY_OF_MONTH));
                return cal.getTime();
                
            }
            
            public static String getStreet() {
                StringBuffer sb = new StringBuffer();
                sb.append( Integer.toString(r.nextInt(100)) );
                sb.append(',');
                sb.append( NameProducer.getLastName() );
                sb.append(' ');
                sb.append(NameProducer.streets[r.nextInt(NameProducer.streets.length)]);
                return sb.toString();
            }
            public static String getFemaleFirst() {
                return getRandomNames(femaleFirst);
            }
            public static String getMaleFirst() {
                return getRandomNames(maleFirst);
            }
            
            static String getRandomNames(String[] source) {
                int n = source.length;
                StringBuffer sb = new StringBuffer();
                sb.append( source[ r.nextInt(n)]);
                sb.append(' ');
                sb.append( source[ r.nextInt(n)]);
                return sb.toString();
            }
            
            public static String getLastName() {
                int n = r.nextInt( surnames.length);
                return surnames[n];
            }
            
            public static String getLastNames() {
                return getRandomNames(surnames);
            }
            /** Creates a new instance of NameProducer */
            public NameProducer() {
            }
            
}
