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
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
// or see online at http://www.gnu.org/licenses/gpl.html


if (! $conn)
     include ('connect.php');

include ('product_tools.php');
?>
<html>
<title>Add Brand</title>
<body>
<h1>Add Brand</h1>

<form action="recv_add_brand.php" method="post">
<?php
product_select ($id);
?>
<input type="hidden" name="id" value="<?=$id ?>">
<select name="id_manu">
<?php
$result = pg_query ("select * from manufacturer");
while ($row = pg_fetch_array ($result))
{
  echo "<option value=\"{$row['id']}\">{$row['name']}({$row['iso_countrycode']})";
}
?>
</select>
Brand:<input type="text" name="brandname" size="10"><p>
<input type="submit" value="submit"></form><p>

<h2>Edit Manufacturer</h2>
<form action="edit_manu.php" method="get">
<select name="id_manu">
<?php
$result = pg_query ("select * from manufacturer");
while ($row = pg_fetch_array ($result))
{
  echo "<option value=\"{$row['id']}\">{$row['name']}&nbsp;({$row['iso_countrycode']})";
}
?>
</select>
<input type="submit" value="go"></form><p>

<a href="new_manu.php">New Manufacturer</a>

</body></html>