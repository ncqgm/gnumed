<?
// functions for Wagtail LDAP/PHP server
// the first four functions should be edited.

function loadRoleName(){   // Major categories, stored as businessCategory in medicalPerson
	$roleName=array("Doctor","Nurse","Allied Health","Administration");
	return $roleName;
}

function loadRole(){    // Specialities, stored as speciality in medicalPerson
	$role[0]=array('Academic','Accident and Emergency Physician','Anaethetist','Cardiologist','Career Medical Officer','Dermatologist','Drug and Alcohol Physician','Endocrinologist','ENT Surgeon','General Physician','General Practitioner','Gynaecologist','Haematologist','Medical Administrator','Medical Registrar','Obstetrician and Gynaecologist','Oncologist','Orthopaedic Surgeon','Paediatrian','Paediatric Surgeon','Pain Management Physician','Palliative Care Physician','Physician','Psychiatrist','Renal Physician','Resident Medical Officer','Registrar','Sports Medicine','Surgeon','Surgical Registrar','Urologist','Vascular Physician','Vascular Surgeon');
	$role[1]=array("Hospital Nurse","Practice Nurse","Clinical Nurse Consultant","Project Manager","Administrator","Early Childhood Nurse","Lactation Consultant","Midwife","Diabetic Educator");
	$role[2]=array('Chiropracter','Counsellor','Diabetic Educator','Dietician','Exercise Physiologist','Occupational Therapist','Physiotherapist','Podiatrist','Psychologist','Social Worker','Speech Pathologist');
	$role[3]=array('Administartive Officer','Chief Executive Officer','Director','Executive Officer','Financial Officer','Practice Manager','Project Manager','Receptionist','Secretary');
	return $role;
}
function loadDefaultRole(){    // Default speciality for each role
	$defaultRole=array();
	$defaultRole[0]="General Practitioner";
	$defaultRole[1]="Practice Nurse";
	$defaultRole[2]="Physiotherapist";
	$defaultRole[3]="Receptionist";
	return $defaultRole;
}
function loadOrgTypes(){    // businessCategory options for medicalOrganization
	$orgTypes=array("General Practice","Specialist Practice","Division of General Practice","Hospital","Hospital Department","Public Health Unit","Community Health");
	return $orgTypes;
}

////////////////////////////////////////////////////////
function printSimpleSearch($region){
	$regions=getRegions($region);
	print"
	<p>
	<p>
	<center>
	<form name='search' action='$PHP_SELF'>
	Search for
	<input type=text name=searchTerm><br>
	<font size=-1>(Use * for wildcard)</font><br>
	in region $regions<br>
	<input type=hidden name=Command value='SimpleSearch'>
	<input type=submit value='Search'>
	</form> 
	</center> 
	";
}
function formatEmail($email){   // to thwart spambots
	$email=str_replace("."," dot ",$email);
	$email=str_replace("@"," at ",$email);
	return $email;
}
function getSelect($selectName,$options,$values,$defoption){  // build html select text
	$theText="<select name='$selectName'>\r";
	for($i=0;$i<count($options);$i++){
		$theText.="<option value='".$values[$i]."'";
		if ($values[$i]==$defoption) 
			$theText.=" selected";
		$theText.=">".$options[$i]."\r";
	}
	$theText.="</select>\r";
	return $theText;
}

function getRegions($default){    // top level 'Division GP' have region as Description field
	global $ldapBase,$ldapConn;
	// $ldapConn=wt_ldapConnect();
	$theText="<select name='region'>\r";
	$theText.="<option value='all'";
	if($default=="" or $default=="All")
		$theText.= " selected";
	$theText.= ">All\r";
	$returnAttributes = array("description");
	$ldapSearch = ldap_list($ldapConn,$ldapBase,"businesscategory=Division GP",$returnAttributes);
	ldap_sort($ldapConn,$ldapSearch,"description");
	$ldapResults = ldap_get_entries($ldapConn, $ldapSearch);
	
	
	if($ldapResults['count']>0){
		for ($item = 0; $item < $ldapResults['count']; $item++){
			$name=$ldapResults[$item]['description'][0];
			if($name=="")
				$name=$region;
			if($name!=""){
				$region=getCN($ldapResults[$item]['dn']);
				$theText.= "<option value='$region'";
				if($default==$region)
					$theText.= "selected";
				$theText.= ">$name\r";
			}
		}
	}
	$theText.="</select>\r";
	return $theText;
}

function getUserFromUID($uid){ // used for logging in
	global $ldapBase,$ldapConn;
	
	$returnAttributes = array("dn");
	$filter = "(uid=$uid)";
	$ldapSearch = ldap_search($ldapConn, $ldapBase, $filter,$returnAttributes);
	$ldapResults = ldap_get_entries($ldapConn, $ldapSearch);
	$dn=$ldapResults[0]["dn"];
	return $dn;
}

function wt_ldapConnect(){ // connect and bind to server. 
						   // needs error trapping and warning
	global $login_dn,$login_pass,$ldapServer,$ldapBase,$ldapConn;
	if($ldapConn=="")
		$ldapConn = ldap_connect($ldapServer);
	ldap_set_option( $ldapConn, LDAP_OPT_PROTOCOL_VERSION, 3 );
	if($login_dn=="anon"){   // anonymous bind
	
		$ldapBind = ldap_bind($ldapConn);	
	}
	else{
		$ldapuser="$login_dn";
		$ldapBind = ldap_bind($ldapConn,$ldapuser,$login_pass);	
	}
	
	return $ldapConn; 
}
function getSimpleSearchFilter($searchTerm){  // simple search searches
											  // cn,  ou and mail

	if(strpos($searchTerm,"*")===false){
		// approximate matching unless wildcard used
		$filter = "(&(|(cn~=$searchTerm)(ou~=$searchTerm)(mail~=$searchTerm)(clinicalmail~=$searchTerm))(!(businesscategory=keymaster)))";
			
	} 
	else{
		$filter = "(&(|(cn=$searchTerm)(ou=$searchTerm)(mail=$searchTerm)(clinicalmail~=$searchTerm))(!(businesscategory=keymaster)))";
	}
	
	return $filter;
}

function showSearchResults($searchTerm,$region,$filter){ 
	global $ldapBase,$login_dn,$ldapConn;
	if($region=="" or $region=="all")
		$base=$ldapBase;
	else
		$base="ou=$region,$ldapBase";
	
	//$ldapConn=wt_ldapConnect();
	$returnAttributes = array("ou", "cn","mail","title","clinicalmail","telephonenumber","street","l","fascimiletelephonenumber","postalcode");
	/*
	if ($attribute=='Name'){
		//$filter = "&(|(cn~=$searchTerm)(ou~=$searchTerm))(!(ou=keymasters))";
		$filter = "(&(cn~=$searchTerm)(!(businesscategory=keymaster)))";
		//$filter = "(|(cn~=$searchTerm)(ou~=$searchTerm))";
		
	}
	*/
	
	$ldapSearch = ldap_search($ldapConn, $base, $filter,$returnAttributes);
	$ldapResults = ldap_get_entries($ldapConn, $ldapSearch);
	print "Search Results - $filter - ".$ldapResults['count']." ";
	($ldapResults['count']==1)? print "entry" : print "entries";
	print " found<p>";
	if($ldapResults['count']>0){
		print "<table>";
		for ($item = 0; $item < $ldapResults['count']; $item++){
			$name=formatDN($ldapResults[$item]["dn"]);
			if($ldapResults[0]['title'][0]!="")
				$name[0]=$ldapResults[0]['title'][0]." ".$name[0];
			print "<tr>";
			print "<td valign=top><b><a href='$PHP_SELF?Command=Show&region=$region&dn=".encodeSpecial($ldapResults[$item]['dn'])."'>".$name[0]."</a></b></td>\r";
			print "<td width=50></td>\r";
			print "<td>".$name[1]."<br>";
			print "<font size=-1>";
			if($ldapResults[$item]['mail'][0]!="")
				print "<b>Email :</b> ".formatEmail($ldapResults[$item]['mail'][0])."              ";
			if($ldapResults[$item]['clinicalmail'][0]!="")
				print "<b>Clinical Email :</b> ".formatEmail($ldapResults[$item]['clinicalmail'][0])."   ";
			if(($ldapResults[$item]['mail'][0]!="") or ($ldapResults[$item]['clinicalmail'][0]!=""))
				print "<br>\r";
			if($ldapResults[$item]['telephonenumber'][0]!="")
				print "<b>Phone :</b> ".$ldapResults[$item]['telephonenumber'][0]."   ";
			if($ldapResults[$item]['fascimiletelephonenumber'][0]!="")
				print "<b>Fax :</b> ".$ldapResults[$item]['fascimiletelephonenumber'][0]."   ";			
			print "<br>";
			print "<b>Address  :</b>".$ldapResults[$item]['street'][0].", ".$ldapResults[$item]['l'][0]." ".$ldapResults[$item]['postalcode'][0]."<br>\r";
			print "<a href='$PHP_SELF?Command=Show&region=$region&dn=".encodeSpecial($ldapResults[$item]['dn'])."'>more..</a>";
			print "</font>";
			print "</td></tr>\r"; 
			
		}
		print "</table>\r";
	}
}
function showChildren($dn){  // link to all entries one branch down
	global $ldapConn,$ldapBase,$login_dn,$region ;
	$ldapSearch = ldap_list($ldapConn,$dn,'objectclass=*');
	$ldapResults = ldap_get_entries($ldapConn, $ldapSearch);
	if($ldapResults['count']>0){
		print "<ul>";
		for ($item = 0; $item < $ldapResults['count']; $item++){
			$name=getCN($ldapResults[$item]['dn']);
			print "<li><b><a href='$PHP_SELF?Command=Show&region=$region&dn=".encodeSpecial($ldapResults[$item]['dn'])."'>".$name."</a></b><br>";
		}
		print "</ul>";
	}
}

function showEntry($dn){
	global $ldapBase,$login_dn,$ldapConn ;
	// $dn=$dn.",$ldapBase";
	// $ldapConn=wt_ldapConnect();
	$ldapResults =getAttributes($dn,$ldapConn);
	if($ldapResults['count']>0){
		$uid=$ldapResults[0]['uid'][0];
		// is entry an organisation or a person
		$name=formatDN($dn);
		if(getTypeFromDN($dn)=="ou"){
			showOrg($dn,$name,$ldapResults);
		}
		else{
			showPerson($dn,$name,$ldapResults);
		}
		
		if(strpos($dn,$login_dn)===false){
			if($uid != ""){
				print "<a href='$PHP_SELF?Command=LogIn&uid=$uid'>Log In</a> as $uid<br>";
			}
		}else{
			if(getTypeFromDN($dn)=="ou"){
				print "<a href='$PHP_SELF?Command=Edit&EditType=org&dn=".encodeSpecial($dn)."'>Edit this entry</a><br>";
				print "<a href='$PHP_SELF?Command=Add&EditType=person&dn=".encodeSpecial($dn)."'>Add a person</a><br>";
				print "<a href='$PHP_SELF?Command=Add&EditType=org&dn=".encodeSpecial($dn)."'>Add a clinic/dept</a><br>";
			}
			else{
				print "<a href='$PHP_SELF?Command=Edit&EditType=person&dn=".encodeSpecial($dn)."'>Edit this entry</a><br>";
			}
		
		}
		
	}
	else{
		print "No entry found for $dn<p>";
	}	
}
function showPerson($dn,$name,$ldapResults){
		if($ldapResults[0]['title'][0]!="")
			$name[0]=$ldapResults[0]['title'][0]." ".$name[0];
		print "
		<table>
		<tr>
			<td valign=top><b>$name[0]</a></b></td>
			<td width=50></td>
			<td>".$name[1]."<br>
		";
		if($ldapResults[0]['speciality'][0]!="")
			print "<b>".$ldapResults[0]['speciality'][0]."</b><br>";		
		if($ldapResults[0]['mail'][0]!="")
			print "<b>Email :</b> ".formatEmail($ldapResults[0]['mail'][0])."<br>";
		if($ldapResults[0]['clinicalmail'][0]!="")
			print "<b>Clinical Email :</b> ".formatEmail($ldapResults[0]['clinicalmail'][0])."<br>";
		if($ldapResults[0]['telephonenumber'][0]!="")
			print "<b>Phone :</b> ".$ldapResults[0]['telephonenumber'][0]."   ";
		if($ldapResults[0]['mobile'][0]!="")
			print "<b>Mobile :</b> ".$ldapResults[0]['mobile'][0]."   ";
		if($ldapResults[0]['fascimiletelephonenumber'][0]!="")
			print "<b>Fax :</b> ".$ldapResults[0]['fascimiletelephonenumber'][0]."   ";			
		print "<br>";
		print "<b>Address  :</b>".$ldapResults[0]['street'][0].", ".$ldapResults[0]['l'][0]." ".$ldapResults[0]['postalcode'][0];
		print "<br>";
		print "<b>PGP KeyID   :</b><a href='http://www.keyserver.medicine.net.au:11371/pks/lookup?op=get&search=".$ldapResults[0]['pgpkeyid'][0]."'>".$ldapResults[0]['pgpkeyid'][0]."</a>\r";
		$pe="?";
		if($ldapResults[0]['preferredencryption'][0]==1)
			$pe="PGP";
		if($ldapResults[0]['preferredencryption'][0]==2)
			$pe="CA";
				if($ldapResults[0]['preferredencryption'][0]==3)
			$pe="Location";
		print "<br><b>Preferred Encryption  :</b>   $pe<br>";
		print "<b>Jabber ID :</b> ".$ldapResults[0]['jabberid'][0]."<br>";
		print "</td></tr>\r";
		print "</table>\r";
		
}
function showOrg($dn,$name,$ldapResults){
		print "
		<table>
		<tr>
			<td valign=top><b>$name[0]</a></b></td>
			<td width=50></td>
			<td>
		";
		if($name[1]!="")
			print $name[1]."<br>";
		if($ldapResults[0]['businesscategory'][0]!="")
			print "<b>".$ldapResults[0]['businesscategory'][0]."</b><br>";		
		if($ldapResults[0]['mail'][0]!="")
			print "<b>Email :</b> ".formatEmail($ldapResults[0]['mail'][0])."<br>";
		if($ldapResults[0]['clinicalmail'][0]!="")
			print "<b>Clinical Email :</b> ".formatEmail($ldapResults[0]['clinicalmail'][0])."<br>";
		if($ldapResults[0]['telephonenumber'][0]!="")
			print "<b>Phone :</b> ".$ldapResults[0]['telephonenumber'][0]."   ";
		if($ldapResults[0]['fascimiletelephonenumber'][0]!="")
			print "<b>Fax :</b> ".$ldapResults[0]['fascimiletelephonenumber'][0]."   ";			
		print "<br>";
		print "<b>Address  :</b>".$ldapResults[0]['street'][0].", ".$ldapResults[0]['l'][0]." ".$ldapResults[0]['postalcode'][0];
		print "<br>";
		print "<b>PGP KeyID   :</b>".$ldapResults[0]['pgpkeyid'][0];
		$pe="?";
		if($ldapResults[0]['preferredencryption'][0]==1)
			$pe="PGP";
		if($ldapResults[0]['preferredencryption'][0]==2)
			$pe="CA";
		print "<br><b>Preferred Encryption  :</b>   $pe<br>";
		print "</td></tr>\r";
		print "</table>\r";
		showChildren($dn);
		
}
function getCN($dn){   // gets value of cn/ou from dn
					   // so cn=Fred,dc=Quarry,dc=bedrock returns Fred
					   // ou=Slate Industries, dc=bedrock returns Slate Industries
	$parts=split(",",$dn);
	$tmp=split("=",$parts[0]);
	return $tmp[1];
}
function getTypeFromDN($dn){  // is person or org?
					          // so cn=Fred,dc=Quarry,dc=bedrock returns cn
					         // ou=Slate Industries, dc=bedrock returns ou

	$tmp=split("=",$dn);
	return $tmp[0];
}

function formatDN($dn){   // provide cn as $name[0]
 						  // and comma delimited link to parents as $name[1]

	global $ldapBase;
	
	$baseCount=count(split(",",$ldapBase));
	$parts=split(",",$dn);
	$count=count($parts);
	(getTypeFromDN($dn)=="ou") ? $modifier=2:$modifier=1;
	$theDN=$dn;
	for($i=1;$i<$count-$baseCount-$modifier;$i++){
		$tmp=split("=",$parts[$i]);
		$theDN=getParent($theDN);
		$theText.="<a href='$PHP_SELF?Command=Show&dn=".encodeSpecial($theDN)."'>".$tmp[1]."</a>";
		if ($i<$count-$baseCount-$modifier-1)
			$theText.=", ";
	}
	$tmp=split("=",$parts[0]);
	return array($tmp[1],$theText);
}

function encodeSpecial($term){  // remove = and , from URL
	$term=str_replace(",","%2C",$term);
	return str_replace("=","%3D",$term);
}

function getParent($dn){
	return substr($dn,strpos($dn,",")+1);
}
function addEntry($dnParent,$EditType){   // EditType is person or org
	global $ldapConn;
	if($EditType=='person'){
		global $ldapBase;
		$dnParent=$dnParent;
		$ldapConn=wt_ldapConnect();
		$parentResults=getAttributes($dnParent,$ldapConn);
		$ldapResults="";
		drawPersonForm($dnParent,$ldapResults,$parentResults);
	}else
		drawOrgForm($dnParent,"");
}	

function editEntry($dn,$EditType){   // EditType is person or org
	global $ldapBase,$ldapConn;
	//$dn=$dn.",$ldapBase";
	// read all the attributes of that $dn;
	// $ldapConn=wt_ldapConnect();
	$ldapResults=getAttributes($dn,$ldapConn);
	if($EditType=='person'){
		// read all the attributes of parent; 
		$dnParent=getParent($dn);
		$parentResults=getAttributes($dnParent,$ldapConn);
		drawPersonForm($dn,$ldapResults,$parentResults);
	}else
		drawOrgForm($dn,$ldapResults);
}
function getAttributes($dn,$ldapConn){
	$ldapSearch = ldap_read($ldapConn,$dn,'objectclass=*');
	$ldapResults = ldap_get_entries($ldapConn, $ldapSearch);
	return $ldapResults;
}

function drawPersonForm($dn,$ldapResults,$parentResults){
	$first=$ldapResults[0]['givenname'][0];
	if ($first=="")
		$first='first';
	$surname=$ldapResults[0]['sn'][0];
	if($surname=="")
		$surname='last';
	$phone=$ldapResults[0]['telephonenumber'][0];
	if($phone=='')
		$phone=$parentResults[0]['telephonenumber'][0];
	$clinicalMail=$ldapResults[0]['clinicalmail'][0];
	if($clinicalMail=='')
		$clinicalMail=$parentResults[0]['clinicalmail'][0];	
	
print "
	<script language='javascript'>
	<!--
	
	/*
	 * Populates the uid field based 
	 */
	function autoFillUID( form )
	{
		var first_name;
		var last_name;
		// var common_name;
	
	        first_name = form.givenname.value;
	        last_name = form.sn.value;
	
		if( last_name == '' ) {
			return false;
		}
		uid_value=first_name+last_name;
		uid_value=uid_value.toLowerCase();
		uid_value=uid_value.replace(' ','');
		// common_name = first_name + ' ' + last_name;
		// form.cn.value = common_name;
		form.uid.value=uid_value;
	}
	";
	writeSelectScript();
	print"
	-->
	</script>
	<form action='$PHP_SELF' name='editentry' method=get>
	<table>
	<tr>
		<td><img src='images/uid.png' /></td>
		<td class='heading'>Name:</td>
		<td>
			<select name='title'>
			<option>Mr
			<option>Ms
			<option>Dr
			<option>Prof
			<option>Assoc Prof
			</select>
			<input type='text' name='givenname' 
				id='givenname' value='$first' onChange='autoFillUID(this.form)' />
			<input type='text' name='sn' 
				id='sn' value='$surname' onChange='autoFillUID(this.form)' />
		</td>
	</tr>
	";
	// <tr>
	// 	<td></td>
	//	<td class='heading'>Common name:</td>
	//	<td><input type='text' name='cn' id='cn' value='".$ldapResults[0]['cn'][0]."' /></td>
	//</tr>
	print "
	<tr>
	<td></td>
	<td class='heading'>Log in as :</td>
	<td><input type='text' name='uid' id='uid' value='".$ldapResults[0]['uid'][0]."' /></td>
	</tr>
	<tr>
	<td></td>
	<td class='heading'>Role and Speciality :</td>
	<td>
		<select name='businesscategory' onChange=\"changeCat(this.selectedIndex,'')\">
		<option>-
		</select>
		<select name='speciality'>
		<option>-
		</select>

		<script>
			loadSelect('".$ldapResults[0]['businesscategory'][0]."','".$ldapResults[0]['speciality'][0]."');
		</script>
		</td>
	</tr>
	<tr class='spacer'><td colspan='3'></td></tr>
	<tr>
		<td><img src='images/phone.png' /></td>
		<td class='heading'>Work phone:</td>
		<td><input type='text' name='telephonenumber'  value='$phone' /></td>
	</tr>
	<tr>
		<td></td>
		<td class='heading'>Mobile:</td>
		<td><input type='text' name='mobile' value='' /></td>
	</tr>
	<tr>
		<td></td>
		<td class='heading'>Email:</td>
		<td><input type='text' name='mail' value='".$ldapResults[0]['mail'][0]."' /></td>
	</tr>
	<tr>
		<td></td>
		<td class='heading'>Clinical Email:</td>
		<td><input type='text' name='clinicalmail' value='$clinicalMail' /></td>
	</tr>
	<tr>
		<td></td>
		<td>Clinic / Dept:</td>
		<td><b>".$parentResults[0]['ou'][0]."</b></td>
	</tr>
	<tr>
		<td></td>
		<td>Address:</td>
		<td><b>".$parentResults[0]['street'][0]."</b></td>
	</tr>
	<tr>
		<td></td>
		<td>Postal Address:</td>
		<td><b>".$parentResults[0]['postalAddress'][0]."</b></td>
	</tr>
	<tr>
		<td></td>
		<td>Suburb / Town:</td>
		<td><b>".$parentResults[0]['l'][0]."</b></td>
	</tr>
	<tr>
		<td></td>
		<td>Fax:</td>
		<td><b>".$parentResults[0]['facsimiletelephonenumber'][0]."</b></td>
	</tr>
	<tr>
		<td></td>
		<td colspan=2>
		<input type=hidden name=Command value='SavePerson'>
		<input type=hidden name='dn' value='$dn'>
		<center><input type=submit value='Save'></center></td>
	</tr>
	</table>
	</form>
	";
}

function drawOrgForm($dn,$ldapResults){
	$ou=$ldapResults[0]['ou'][0];

	
print "
	<script language='javascript'>
	<!--
	
	/*
	 * Populates uid field based on the Organisation Name
	 */
	function autoFillCommonName( form )
	{
		var org_name;

	
	    org_name = form.ou.value;

	
		if( org_name == '' ) {
			return false;
		}

		org_name=org_name.toLowerCase();
		org_name=org_name.replace(' ','');
		org_name=org_name.replace('\'','');
		org_name=org_name.replace(',','');
		form.uid.value=org_name; 
	}
	
	";
	
	print "
	
	-->
	</script>
	<form action='$PHP_SELF' method=get>
	<table>
	<tr>
		<td></td>
		<td class='heading'>Organisation:</td>
		<td>
			<input type='text' name='ou' 
				id='ou' value='$ou' onChange='autoFillCommonName(this.form)' />
		</td>
	</tr>
	<tr>
	<td></td>
	<td class='heading'>Log in as :</td>
	<td><input type='text' name='uid' id='uid' value='".$ldapResults[0]['uid'][0]."' /></td>
	</tr>


	<tr>
		<td></td>
		<td class='heading'>Business Type</td>
	";
	$options=loadOrgTypes();
	$values=$options;
	print "<td>".getSelect("businesscategory",$options,$values,$ldapResults[0]['businesscategory'][0])."</td>\r";
	print "
	</tr>
	<tr class='spacer'><td colspan='3'></td></tr>
	<tr>
		<td><img src='images/phone.png' /></td>
		<td class='heading'>Work phone:</td>
		<td><input type='text' name='telephonenumber'  value='".$ldapResults[0]['telephonenumber'][0]."' /></td>
	</tr>
	<tr>
		<td></td>
		<td>Fax:</td>
		<td><input type='text' name='fascimiletelephonenumber' value='".$ldapResults[0]['fascimiletelephonenumber'][0]."' /></td>

	</tr>	
	<tr>
		<td></td>
		<td class='heading'>Email:</td>
		<td><input type='text' name='mail' value='".$ldapResults[0]['mail'][0]."' /></td>
	</tr>
	<tr>
		<td></td>
		<td class='heading'>Clinical Email:</td>
		<td><input type='text' name='clinicalmail' value='".$ldapResults[0]['clinicalmail'][0]."' /></td>
	</tr>
	<tr>
		<td></td>
		<td>Address:</td>
		<td><input type='text' name='street' value='".$ldapResults[0]['street'][0]."' /></td>

	</tr>
	<tr>
		<td></td>
		<td>Postal Address:</td>
		<td><input type='text' name='postaladdress' value='".$ldapResults[0]['postaladdress'][0]."' /></td>

	</tr>
	<tr>
		<td></td>
		<td>Suburb / Town:</td>
		<td><input type='text' name='l' value='".$ldapResults[0]['l'][0]."' /></td>

	</tr>
	<tr>
		<td></td>
		<td>Postcode:</td>
		<td><input type='text' name='postalcode' value='".$ldapResults[0]['postalcode'][0]."' /></td>

	</tr>

	<tr>
		<td></td>
		<td colspan=2>
		";
	if($ldapResults=="")
		print "<input type=hidden name=Command value='AddOrg'>";
	else
		print "<input type=hidden name=Command value='SaveOrg'>";
	print "
		<input type=hidden name='dn' value='$dn'>
		<center><input type=submit value='Save'></center></td>
	</tr>
	</table>
	</form>
	";
} 

function savePerson($dn){
	global $_REQUEST,$ldapConn;
	//$ldapConn=wt_ldapConnect();
	// Get attributes that are inherited from Parent Org
	$addAttr['objectclass']='medicalPerson';

	// Now check attributes posted from form

	$attrToUse=array('sn','givenname','mail','uid','mobile','clinicalmail','telephonenumber','businesscategory','speciality','title');
	
	if(getTypeFromDN($dn)=="cn"){ // modify existing entry
		// need to know old attributes to delete
		$ldapResults=getAttributes($dn,$ldapConn);
		$delFlag=0;
		foreach($attrToUse as $attr){
			if($_REQUEST[$attr]=="" and $ldapResults[0][$attr][0]!=""){
				$delAttr[$attr]=$ldapResults[0][$attr][0];
				$delFlag=1;
			}
			elseif($_REQUEST[$attr]!=""){
				$addAttr[$attr]=$_REQUEST[$attr];
				
			}
		}
		print "Saving $dn<p>";
		$r=ldap_modify($ldapConn,$dn,$addAttr);
		if($delFlag)
			$r=ldap_mod_del($ldapConn,$dn,$delAttr);
	}
	else{ // adding new entry
		$addAttr['cn']=$_REQUEST['givenname']." ".$_REQUEST['sn'];
		foreach($attrToUse as $attr){
			if($_REQUEST[$attr]!="")	
				$addAttr[$attr]=$_REQUEST[$attr];
		}
		$dnParent=$dn;
		$parentResults=getAttributes($dnParent,$ldapConn);
		$attrToUse=array('street','l','postalcode','facsimiletelephonenumber',);
		foreach($attrToUse as $attr){
			if($parentResults[0][$attr][0]!="")	{
				$addAttr[$attr]=$parentResults[0][$attr][0];
			}
		}

		$dn="cn=".$addAttr['cn'].",$dn";
		print "Saving $dn<p>";
		foreach($addAttr as $attr){
			print "$attr<br>";
		}
		$r=ldap_add($ldapConn,$dn,$addAttr);
	}
	print "Saved";

	
	
}
function saveOrg($dn,$EditType){
	global $_REQUEST;
	$ldapConn=wt_ldapConnect();
	

	$attrToUse=array('uid','mail','clinicalmail','telephonenumber','facsimiletelephonenumber','street','l','postaladdress','postalcode','description','businesscategory');
	if($EditType=="SaveOrg"){ // modify existing entry
		// need to know old attributes to delete
		$ldapResults=getAttributes($dn,$ldapConn);
		$delFlag=0;
		foreach($attrToUse as $attr){
			if($_REQUEST[$attr]=="" and $ldapResults[0][$attr][0]!=""){
				$delAttr[$attr]=$ldapResults[0][$attr][0];
				$delFlag=1;
			}
			elseif($_REQUEST[$attr]!=""){
				$addAttr[$attr]=$_REQUEST[$attr];
			}
		}

		print "Saving $dn<p>";
		$r=ldap_modify($ldapConn,$dn,$addAttr);
		if($delFlag)
			$r=ldap_mod_del($ldapConn,$dn,$delAttr);
	}
	else{ // adding new entry
		foreach($attrToUse as $attr){
			if($_REQUEST[$attr]!="")
				$addAttr[$attr]=$_REQUEST[$attr];
				
		}
		$dn="ou=".$_REQUEST['ou'].",$dn";
		print "Saving $dn<p>";
		
		$r=ldap_add($ldapConn,$dn,$addAttr);
	}
	print "Saved";

	
}

function writeSelectScript(){
	$defaultRole=loadDefaultRole();
	$role=loadRole();
	$roleName=loadRoleName();
	$max=0;
	foreach($role as $job){
		if(count($job)>$max)
			$max=count($job);
	}
	
	print"

	function makeArray(size){
		this.length=size;
		for(i=1;i<=size;i++){
			this[i]='';
		}
		return this;
	}

	spec=new makeArray($max);
	busCat=new makeArray(".count($role).");
	function loadSelect(defaultBusCat,defaultSpec){
		if(defaultBusCat=='' || defaultBusCat=='-'){
			defaultBusCat='".$roleName[0]."';
		}
	";
	for($i=0;$i<count($role);$i++){ 
		print "\r\t\tbusCat[$i]='".$roleName[$i]."';";
	}
	print"
		document.editentry.businesscategory.length =busCat.length;
		for(i=0;i<busCat.length;i++){
			document.editentry.businesscategory.options[i] = new Option(busCat[i],busCat[i]);
			if(busCat[i]==defaultBusCat){
				document.editentry.businesscategory.selectedIndex=i;
			}
		}
		changeCat(document.editentry.businesscategory.selectedIndex,defaultSpec);
	}
	
	function loadSpec(cat){";
	
	for($i=0;$i<count($role);$i++){
		print "\r\t\tif (cat==$i){\r\t\t\tspec.length=".count($role[$i]).";\r";
		for($j=0;$j<count($role[$i]);$j++){
			print "\t\t\tspec[$j]='".$role[$i][$j]."';\r";
		}
		print "\t\t}\r";
	}
	print "\t\treturn spec;\r";
	print "\t}\r";
	
	print "
	function loadDefaultSpec(cat){";
	for($i=0;$i<count($role);$i++){
		print "\r\t\t\tif(cat==$i) defaultSpec='".$defaultRole[$i]."';";
	}
	print "\r\t\treturn defaultSpec;\r";
	print "\t}\r";

	print"
	function changeCat(cat,defaultSpec){
		
		spec=loadSpec(cat);
		if(defaultSpec=='' || defaultSpec=='-'){
			defaultSpec=loadDefaultSpec(cat);
		}

		document.editentry.speciality.length =spec.length;
		for(i=0;i<spec.length;i++){
			document.editentry.speciality.options[i] = new Option(spec[i],spec[i]);
			if(spec[i]==defaultSpec){
					document.editentry.speciality.selectedIndex=i;
			}
		}	
	}	
	";

}
?>