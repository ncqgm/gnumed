<?php
// PHP interface to gnumed drug database
// Copyright (C) 2002 Ian Haywood 

// This program is free software; you can redistribute it and/or
// modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA
// or see online at http://www.gnu.org/licenses/gpl.html

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

<h2>Disease Interactions</h2>

<table><tr>
<th>Disease Code</th><th>Severity</th><th>Description</th><th>Comment</th><th></th><th></th>
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
  echo "</td>";
  del_and_comment ('link_drug_disease_interactions', $row['id'], "viewdisease.php?id=$id");
  echo "</tr>";
}
?>
</table>

<h3>New Disease-Class Interaction</h3>

<form action="new_disease_interaction.php#disease" method="post">
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
<p>

<a href="viewelement.php?id=<?= $id ?>">Back</a>
</body></html>