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

<h2>Interactions</h2>

<table><tr><th>Class/Drug</th><th>Severity</th><th>Description</th><th>Comment</th><th></th><th></th></tr>

<?php
$result1 = pg_query ("select *, get_drug_name (id_interacts_with) as otherdrug from link_drug_interactions where id_drug = $id");
while ($row = pg_fetch_array ($result1))
{
  $result3 = pg_query ("select severity, description from interactions where id = " . $row['id_interaction']);
  $severity = pg_fetch_result ($result3, 0, 0);
  $description = pg_fetch_result ($result3, 0, 1);
  echo "<tr><td><a href=\"viewelement.php?id={$row['id_interacts_with']}\">{$row['otherdrug']}</a></td><td>$severity</td><td>$description</td><td>{$row['comment']}</td>";
  del_and_comment ('link_drug_interactions', $row['id'], "viewinter.php?id=$id");
  echo "</tr>";
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
  echo "<td>{$row['comment']}</td>";
  del_and_comment ('link_drug_interactions', $row['id'], "viewinter.php?id=$id");
  echo "</tr>";
}
?>
</table>

<h3>New Interaction</h3>
<form action="new_drug_interaction.php" method="post">
With: <input type="text" size="10" name="otherdrug">
<? include ("interactions_option.php"); ?><p>
Comment: <p><textarea rows=5 cols=50 name="comment"></textarea>
<input type="hidden" name="id" value="<?= $id?>">
<input type="submit" value="submit"></form>
<P>

<a href="viewelement.php?id=<?= $id ?>">Back</a>

</body></html>