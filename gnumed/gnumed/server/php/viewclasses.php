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

<table><th>Class</th><th></th><th></th>

<h2 id="classes">Classes</h2>
<?php

  $result = pg_query ("select drug_class.id, drug_class.description, link_drug_class.id from link_drug_class, drug_class where link_drug_class.id_drug = $id and link_drug_class.id_class = drug_class.id");
  while ($row = pg_fetch_row ($result))
    {
      echo "<tr><td><a href=\"viewelement.php?id={$row[0]}\">{$row[1]}</a></td>";
      del_and_comment ('link_drug_class', $row[2], "viewclasses.php?id=$id");
      echo "</tr>";
    }
?>


<h3>Add This Drug To Class</4>

<form action="new_link_drug_class.php" method="post">
Name:<input type="text" name="class" size="10"><input type="submit" value="submit">
<input type="hidden" name="id" value="<?=$id?>"></form>
<p>

<a href="viewelement.php?id=<?= $id ?>">Back</a>

</body></html>