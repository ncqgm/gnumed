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

<h2 id="name">Names</h2>
<table><tr><th>Name</th><th>Comment</th><th>Countries</th><th></th><th></th></tr>
<?php
  $result = pg_query ("select * from generic_drug_name where id_drug = $id");
  while ($row = pg_fetch_array ($result))
    {
      echo "<tr><td>{$row['name']}</td><td>{$row['comment']}</td><td>";
      $result2 = pg_query ("select * from link_country_drug_name where id_drug_name = {$row['id']}");
      while ($row2 = pg_fetch_array ($result2))
	{
	  echo $row2['iso_countrycode'] . ",";
	}
      echo "<form action=\"new_link_name_country.php#name\" method=\"post\"><input type=\"text\" name=\"iso\" size=\"2\">";
      echo "<input type=\"hidden\" name=\"id_drug_name\" value=\"{$row['id']}\">";
      echo "<input type=\"hidden\" name=\"id\" value=\"$id\"></form></td>";
      del_and_comment ('generic_drug_name', $row['id'], "viewnames.php?id=$id");
      echo "</tr>";
    }
?>
</table>

<h3>New Name</h3>

<form action="new_drug_name.php#name" method="post">
Name: <input type="text" name="name" size="10">
<input type="submit" value="submit"><p>
Comment (On the Name):<p>
<textarea name="comment"></textarea>
<input type="hidden" name="id" value="<?=$id ?>">
</form><p>

<a href="viewelement.php?id=<?= $id ?>">Back</a>

</body></html>