<!--
PHP interface to gnumed drug database
Copyright (C) 2002 Ian Haywood 

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
or see online at http://www.gnu.org/licenses/gpl.html
!>


<?php

// very complex form for viewing and changing elements
// depends on $id being set either by newclass.php, newdrug.php or from form

if (! $conn)
{
  include ('connect.php');
}
$result = pg_fetch_array (pg_query ("select *, get_drug_name (id) as name from drug_element where id=$id"));
$category = $result['category'];
$is_drug = ($category == 'c' or $category == 's');
$name = $result['name'];
?>

<html>
<title><?=$name ?> </title>
<body>
<h1> <?=$name ?></h1>

<?php
if ($message)
{
  echo "<h2>$message</h2>";
}
?>

<?php
if ($is_drug)
{
  echo "<h2>Names</h2>";
  echo "<table><tr><th>Name</th><th>Comment</th><th>Countries</th></tr>";
  $result = pg_query ("select * from generic_drug_name where id_drug = $id");
  while ($row = pg_fetch_array ($result))
    {
      echo "<tr><td>{$row['name']}</td><td>{$row['comment']}</td><td>";
      $result2 = pg_query ("select * from link_country_drug_name where id_drug_name = {$row['id']}");
      while ($row2 = pg_fetch_array ($result2))
	{
	  echo $row2['iso_countrycode'] . ",";
	}
      echo "<form action=\"new_link_name_country.php\" method=\"post\"><input type=\"text\" name=\"iso\" size=\"2\">";
      echo "<input type=\"hidden\" name=\"id_drug_name\" value=\"{$row['id']}\">";
      echo "<input type=\"hidden\" name=\"id\" value=\"$id\"></form></td></tr>";
    }

  echo <<<EOD
</table>

<h3>New Name</h3>

<form action="new_drug_name.php" method="post">
Name: <input type="text" name="name" size="10">
<input type="submit" value="submit"><p>
Comment (On the Name):<p>
<textarea name="comment"></textarea>
<input type="hidden" name="id" value="$id">
</form>
EOD;

  echo "<h2>Classes</h2>";
  $result = pg_query ("select drug_class.id, drug_class.description from link_drug_class, drug_class where link_drug_class.id_drug = $id and link_drug_class.id_class = drug_class.id");
  while ($row = pg_fetch_row ($result))
    {
      echo "<a href=\"viewelement.php?id={$row[0]}\">{$row[1]}</a><p>";
    }

echo <<<EOD
<h3>Add This Drug To Class</4>

<form action="new_link_drug_class.php" method="post">
Name:<input type="text" name="class" size="10"><input type="submit" value="submit">
<input type="hidden" name="id" value="$id"></form>
EOD;
}

if ($category == 'c')
{
  $num_components = 0;
  echo "<h2>Compound:</h2>";
  $result = pg_query ("select id_component, get_drug_name (id_component) from link_compound_generics where id_compound = $id");
  while ($row = pg_fetch_row ($result))
  {
    echo "<a href=\"{$row[0]}\">{$row[1]}</a><p>";
    $num_components += 1;
  }

  echo <<<EOD
<h3>New Component</h3>
<form action="new_component.php" method="post">
  Name:<input type="text" name="drug" size="10">
<input type="hidden" name="id" value="$id">
<input type="submit" value="submit">
</form>
EOD;
}
?>


<h2>Interactions</h2>

<table><tr><th>Class/Drug</th><th>Severity</th><th>Description</th><th>Comment</th></tr>

<?php
$result1 = pg_query ("select *, get_drug_name (id_interacts_with) as otherdrug from link_drug_interactions where id_drug = $id");
while ($row = pg_fetch_array ($result1))
{
  $result3 = pg_query ("select severity, description from interactions where id = " . $row['id_interaction']);
  $severity = pg_fetch_result ($result3, 0, 0);
  $description = pg_fetch_result ($result3, 0, 1);
  echo "<tr><td><a href=\"viewelement.php?id={$row['id_interacts_with']}\">{$row['otherdrug']}</a></td><td>$severity</td><td>$description</td><td>{$row['comment']}</td></tr>";
}

$result1 = pg_query ("select *, get_drug_name (id_drug) as otherdrug from link_drug_interactions where id_interacts_with = $id");
while ($row = pg_fetch_array ($result1))
{
  $result3 = pg_query ("select severity, description from interactions where id = " . $row['id_interaction']);
  $severity = pg_fetch_result ($result3, 0, 0);
  $description = pg_fetch_result ($result3, 0, 1);
  echo "<tr><td><a href=\"viewelement.php?id={$row['id_drug']}\">{$row['otherdrug']}</a></td>";
  echo "<td>$severity</td>";
  echo "<td>$description</td>";
  echo "<td>{$row['comment']}</td></tr>";
}
?>
</table>

<h3>New Interaction</h3>
<form action="new_drug_interaction.php" method="post">
With: <input type="text" size="10" name="otherdrug">
<? include ("interactions_option.php"); ?><p>
Comment: <p><textarea rows=5 cols=40 name="comment"></textarea>
<input type="hidden" name="id" value="<?= $id?>">
<input type="submit" value="submit"></form>

<h2>Disease Interactions</h2>

<table><tr>
<th>Disease Code</th><th>Severity</th><th>Description</th><th>Comment</th>
</tr>

<?php
$result1 = pg_query ("select * from link_drug_disease_interactions where id_drug = $id");
while ($row = pg_fetch_array ($result1))
{
  $inter_id = $row['id_interaction'];
  $result2 = pg_query ("select severity, description from interactions where id = $inter_id");
  $result3 = pg_query ("select name, version from code_systems where id = " . $row['id_code_system']);
  $code_system = pg_fetch_result ($result3, 0, 0) . "-" . pg_fetch_result ($result3, 0, 1);
  echo "<tr><td>";
  echo $row['disease_code'] . "($code_system)";
  echo "</td><td>";
  echo pg_fetch_result ($result2, 0, 0);
  echo "</td><td>";
  echo pg_fetch_result ($result2, 0, 1);
  echo "</td><td>";
  echo $row['comment'];
  echo "</td></tr>";
}
?>
</table>

<h3>New Disease-Class Interaction</h3>

<form action="new_disease_interaction.php" method="post">
Disease Code:<input type="text" size="10" name="code"><p>
System: <select name="system">
<?php
  $result = pg_query ("select * from code_systems");
  while ($row = pg_fetch_array ($result))
    {
      echo "<option value=\"{$row['id']}\">";
      echo $row['name'] . "-" . $row['version'];
    }
?>
</select><p>

<?php
 include("interactions_option.php"); 
?><p>

Comment: <p><textarea rows="5" cols="40" name="comment"></textarea>
<input type="hidden" name="id" value="<?=$id ?>">
<input type="submit" value="submit"></form>

<h2>Adverse Effects</h2>
<table>
<tr><th>Severity</th><th>Frequency</th><th>Important</th><th>Description</th></tr>
<?php
$result = pg_query ("select severity, case when frequency='c' then 'common' when frequency='i' then 'infrequent' when frequency='r' then 'rare' end, case when important then 'Yes' else 'No' end, description from link_drug_adverse_effects, adverse_effects where id_drug = $id and id_adverse_effect = adverse_effects.id");
while ($row = pg_fetch_row ($result))
{
  echo "<tr><td>{$row[0]}</td><td>{$row[1]}</td><td>{$row[2]}</td><td>{$row[3]}</td></tr>";
}
?>
</table>

<form action="new_adverse_effect.php" method="post">
Frequency:<select name="frequency">
<option value="c">common
<option value="i">infrequent
<option value="r">rare
</select>
Important:<input type="checkbox" name="important" value="t"><p>
<select name="id_adverse_effect">
<?php
$result = pg_query ("select * from adverse_effects");
while ($row = pg_fetch_array ($result)) {
  echo "<option value=\"{$row['id']}\">{$row['description']}({$row['severity']})</option>";
} ?></select>
<input type="hidden" name="id" value="<?= $id?>">
<input type="submit" value="submit"></form>

<h2>Cautions</h2>
<table>
<tr><th>Type</th><th>Details</th></tr>
<?php
$result = pg_query ("select drug_warning_categories.description, drug_warning.details from link_drug_warning, drug_warning, drug_warning_categories where link_drug_warning.id_drug = $id and link_drug_warning.id_warning = drug_warning.id and drug_warning.id_warning  = drug_warning_categories.id");
while ($row = pg_fetch_row ($result))
{
  echo "<tr><td>{$row[0]}</td><td>{$row[1]}</td></tr>";
}
?>
</table>

<form action="new_warning.php" method="post">
Type:
<select name="id_warning">
<?php
$result = pg_query ("select * from drug_warning_categories");
while ($row = pg_fetch_array ($result)) {
  echo "<option value=\"{$row['id']}\">{$row['description']}</option>";
} ?></select><p>
<textarea name="details" cols="40" rows="3"></textarea>
<input type="hidden" name="id" value="<?= $id?>">
<input type="submit" value="submit"></form>

<h2>Drug Information</h2>

<?php
$result = pg_query ("select title, info_reference.description, info, drug_information.id from link_drug_information, drug_information, information_topic, info_reference where id_drug = $id and id_info = drug_information.id and information_topic.id = id_topic and info_reference.id = id_info_reference");
while ($row = pg_fetch_row ($result))
{
  echo "<h3>{$row[0]}</h3>{$row[2]}<h4>Reference</h4>{$row[1]}<p><a href=\"edit_info?id_info={$row[3]}\">Edit This</a>";
}

?><p>

<h3>New Information</h3>

<form action="new_info.php" method="post">
<select name="id_topic">
<?php

$result = pg_query ("select * from information_topic");
while ($row = pg_fetch_array ($result))
{
  echo "<option value=\"{$row['id']}\">{$row['title']}";
}
?></select>
<select name="id_info_reference">
<?php

$result = pg_query ("select * from info_reference");
while ($row = pg_fetch_array ($result))
{
  echo "<option value=\"{$row['id']}\">{$row['description']}";
}
?></select><p>
<input type="hidden" name="id" value="<?= $id ?>">
<input type="submit" value="create &amp; edit">
</form>



<?php
if (! $is_drug) {
  echo "<h2>Drugs in This Class</h2>";
  $result = pg_query ("select id_drug, get_drug_name (id_drug) from link_drug_class where id_class = $id");
  while ($row = pg_fetch_row ($result))
  {
    echo "<a href=\"viewelement.php?id={$row[0]}\">{$row[1]}</a><p>";
  }

  echo <<<EOD
<h3>New Drug</h3>

<form action="newdrug.php" method="post">
<input type="radio" name="category" value="s">Single drug
<input type="radio" name="category" value="c">Compound<p>
<input type="hidden" name="id_class" value="$id">
<input type="submit">
</form>
EOD;
} ?>

<?php
if ($category == 's' or $category == 'c')
{
  // dosages for substances
  echo "<h2>Dosage Recommendations</h2><table><tr><th>Route</th><th>Category</th><th>Dose</th><th>Hints</th></tr>";
  $result = pg_query (<<<EOD
select coalesce ((select description from drug_warning_categories dwc where dwc.id = id_drug_warning_categories), '')as dwc, 
       drug_routes.description as dr, 
       dosage_hints,
	drug_dosage.id as id	      
from drug_dosage, drug_routes 
where 
       id_drug = $id and  
       drug_routes.id = id_drug_route 
EOD
); 
  while ($row = pg_fetch_array ($result))
    {
      echo "<tr><td>{$row['dr']}</td><td>{$row['dwc']}</td><td>";

      $result2 = pg_query ("select * from substance_dosage, drug_units where id_drug_dosage = {$row['id']} and drug_units.id = id_drug_units");
      while ($row2 = pg_fetch_array ($result2))
	{
	  if ($row2["dosage_type"] == 'w')
	    $per = '/kg';
	  else 
	    if ($row2["dosage_type"] == 's')
	      $per = '/m2';
	    else
	      if ($row2["dosage_type"] == 'a')
		$per = '/age (months}';
	      else
		$per = '';
	  $per = $row2["description"] . $per;
	  if ($category == 'c')
	    {
	      $result3 = pg_query ("select get_drug_name ({$row2['id_component']})");
	      $drugname = "$nbsp;" . pg_fetch_result ($result3, 0, 0) . ':';
	    }
	  else
	    $drugname = '';
	  echo "$drugname{$row2['dosage_start']}{$per}-{$row2['dosage_max']}{$per}";
	}

      echo "</td><td>{$row['dosage_hints']}</td></tr>";
    }
  echo "</table><h3>New Dosage</h3>";
  
  if ($category == 's')
    {
      echo <<<EOD
<form action="new_dosage.php" method="post">
<input type="hidden" name="id" value="<?= $id ?>">
Start:<input type="text" name="start" size="3">
Max:<input type="text" name="max" size="3">
<select name="unit">
EOD;
  $result = pg_query ("select * from drug_units");
  while ($row = pg_fetch_array ($result))
    {
      echo "<option value=\"{$row['id']}\">{$row['unit']}";
    }
  echo <<<EOD
</select>
<select name="type">
<option value="*" selected>Normal
<option value="w">By Weight (kg)
<option value="s">By Surface Area (m2)
<option value="a">By Age (months)
</select>
<select name="warning">
<option value="-1" selected>No warning
EOD;
  $result = pg_query ("select * from drug_warning_categories");
  while ($row = pg_fetch_array ($result))
    {
      echo "<option value=\"{$row['id']}\">{$row['description']}";
    }
  echo <<<EOD
</select><p>
Hints:<p>
<textarea name="hints" rows="4" cols="50"></textarea><p>
<input type="submit" value="submit">
</form>
EOD;
    }
  else
    {
      // compound dose recommendation, quite different, and IMHO, of limited usefulness,
      // as compound drug dose are generally fixed by the formulation
      // TODO
      echo "<b>Dosage not yet supported for compounds</b>";
    }
} 
?>

<?php
if ($category == 'c' or $category == 's')
     echo "<p><big><a href=\"viewproducts.php?id=$id\">View Products</a></big>";
?>

</body>
</html>

