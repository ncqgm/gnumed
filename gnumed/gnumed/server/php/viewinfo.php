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

<h2>Drug Information</h2>

<?php
$result = pg_query ("select title, info_reference.description, info, drug_information.id from link_drug_information, drug_information, information_topic, info_reference where id_drug = $id and id_info = drug_information.id and information_topic.id = id_topic and info_reference.id = id_info_reference");
while ($row = pg_fetch_row ($result))
{
  echo "<h3>{$row[0]}</h3>{$row[2]}<h4>Reference</h4>{$row[1]}<p><a href=\"edit_info?id_info={$row[3]}\">Edit This</a><p>";
  // echo "<table><tr>";
  // we need deland comment here, need to rationalise drug information tables first
  // del_and_comment ("drug_information", $row[3], "viewinfo.php?id=$id");
  // echo "</tr></table>";
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
<p>

<a href="viewelement.php?id=<?= $id ?>">Back</a>
</body></html>