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

<h2>Compound</h2>

<?php
  $num_components = 0;
  $result = pg_query ("select id_component, get_drug_name (id_component) from link_compound_generics where id_compound = $id");
  while ($row = pg_fetch_row ($result))
  {
    echo "<a href=\"viewelement.php?id={$row[0]}\">{$row[1]}</a><p>";
    $num_components += 1;
  }
?>
<h3>New Component</h3>
<form action="new_component.php" method="post">
  Name:<input type="text" name="drug" size="10">
<input type="hidden" name="id" value="<?= $id ?>">
<input type="submit" value="submit">
</form>
<p>

<a href="viewelement.php?id=<?= $id ?>">Back</a>
</body></html>