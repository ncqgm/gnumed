<?
// LDAP - PHP interface for Wagtail
// v0.2

include("config.php");
include("functions.php");


// Login dn and password set as cookies
$login_dn = (isset( $_COOKIE['login_dn'] ) and $_COOKIE['login_dn']!="" )? $_COOKIE['login_dn'] : "anon";
$login_pass = isset( $_COOKIE['login_pass'] ) ? $_COOKIE['login_pass'] : null;
$Command=$_REQUEST['Command'];
$region=$_REQUEST['region'];


// Need to set new cookies before any text sent
if($_REQUEST['Command']=='Log In'){
	$uid=$_REQUEST['uid'];
	$ldapuser=getUserFromUID($uid);
	$login_pass=$_REQUEST['pw'];
	// See if can bind with those values
	$ldapConn = ldap_connect($ldapServer);
	ldap_set_option( $ldapConn, LDAP_OPT_PROTOCOL_VERSION, 3 );
	$ldapBind = ldap_bind($ldapConn,$ldapuser,$login_pass);
	if ($ldapBind){
		setcookie('login_dn', $ldapuser);
		setcookie('login_pass', $login_pass);
		$login_dn=$ldapuser;
		$login_pass=$_REQUEST['pw'];
	}
	else{
		print "Unable to connect to $ldapServer as $ldapuser with that password<p>";
	}
	$Command="Show";
	$_REQUEST['dn']=$ldapuser;
}
if($_REQUEST['Command']=='LogOut'){
		setcookie('login_dn', '');
		setcookie('login_pass', '');
		$login_dn='anon';
		$Command="";
}
include("header.php");
print "
<TABLE  cellSpacing=0 cellPadding=0 width='100%' border=0 BGCOLOR=#006699>
<TR>
<TD width=100% VALIGN=TOP>
<CENTER><FONT FACE=ARIAL,HELVETICA COLOR=#FFFFFF SIZE=4>
&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;ldap server</FONT></CENTER></td></tr>
<tr><td width=100% align=right><FONT FACE=ARIAL,HELVETICA COLOR=#FFFFFF SIZE=2>
";



if($Command=='LogIn'){
	print "<form action='$PHP_SELF' method=get>\r";
	if ($_REQUEST['uid']!=""){
		print "Log in as ".$_REQUEST['uid']."<br>";
		print"<input type=hidden name=uid value='".$_REQUEST['uid']."'>";
	}
	else{
		print "User <input type=text name=uid size=15><br>\r";
	}
	print"
	Password <input type=password name=pw size=15><br>
	<input type=submit name=Command value='Log In'>
	</form>
	";
	$Command="";
}
else{
	if($login_dn=="anon"){
		print "<a href='$PHP_SELF?Command=LogIn'><FONT FACE=ARIAL,HELVETICA COLOR=#FFFFFF SIZE=2>Log in</font></a> to add or edit entries";
	} 
	else{
		$cn=getCN($login_dn);
		print "Logged in as $cn <a href='$PHP_SELF?Command=LogOut'><FONT FACE=ARIAL,HELVETICA COLOR=#FFFFFF SIZE=2>Log Out</font></a>";
	}
}
print "</font></td></tr></table>";


//
// Connect and bind to ldapserver
//

$ldapConn=wt_ldapConnect();


if($Command=='SimpleSearch'){
	$filter=getSimpleSearchFilter($_REQUEST['searchTerm']);
	showSearchResults($_REQUEST['searchTerm'],$_REQUEST['region'],$filter);
	$Command="";
}

if($Command=='Edit'){
	editEntry($_REQUEST['dn'],$_REQUEST['EditType']);
}
if($Command=='Add'){
	addEntry($_REQUEST['dn'],$_REQUEST['EditType']);
}
if($Command=='SavePerson'){
	savePerson($_REQUEST['dn']);
	$Command="Show";
}
if($Command=='SaveOrg' or $Command=='AddOrg'){
	saveOrg($_REQUEST['dn'],$Command);
	$Command="Show";
}
if($Command=='Show'){
	showEntry($_REQUEST['dn']);
	$Command="";
}
if($Command==""){
	printSimpleSearch($_REQUEST['region']);
}
?>
</body>


</html>