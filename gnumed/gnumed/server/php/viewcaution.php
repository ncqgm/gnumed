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


<h2>Cautions</h2>
<table>
<tr><th>Type</th><th>Details</th><th></th><th></th></tr>
<?php
$result = pg_query ("select drug_warning_categories.description, drug_warning.details, link_drug_warning.id from link_drug_warning, drug_warning, drug_warning_categories where link_drug_warning.id_drug = $id and link_drug_warning.id_warning = drug_warning.id and drug_warning.id_warning  = drug_warning_categories.id");
while ($row = pg_fetch_row ($result))
{
  echo "<tr><td>{$row[0]}</td><td>{$row[1]}</td>";
  del_and_comment ('link_drug_warning', $row[2], "viewcaution.php?id=$id");
  echo "</tr>";
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
<p>

<a href="viewelement.php?id=<?= $id ?>">Back</a>
</body></html>