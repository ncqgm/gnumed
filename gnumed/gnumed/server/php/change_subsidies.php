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
<title>Change Subsidy</title>
<body>
<h1>Change Subsidy</h1>

<form action="recv_change_subsidies.php" method="post">
<?php
product_select ($id);
?>
<input type="hidden" name="id" value="<?=$id ?>">
<input type="hidden" name="subsidy" value="<?=$subsidy ?>">
Max. Quantity:<input type="int" name="max_qty" size="5"><p>
Max. Repeats:<input type="int" name="max_rpt" size="5"><p>
Co-payment:$<input type="float" name="copayment" size="5"><p>
Condition: <select name="condition">
<?php
$result = pg_query ("select id, title from conditions where id_subsidy = $subsidy");
echo "<option value=\"-1\" selected>No condition"; 
while ($row = pg_fetch_row ($result))
{
  echo "<option value=\"{$row[0]}\">{$row[1]}";
}
?></select>
<input type="submit" value="submit"></form><p>


<h2>Edit Condition</h2>
<form action="edit_cond.php" method="get">
<select name="id_cond">
<?php
$result = pg_query ("select * from conditions where id_subsidy = $subsidy");
while ($row = pg_fetch_array ($result))
{
  echo "<option value=\"{$row['id']}\">{$row['title']}";
}
?>
</select>
<input type="submit" value="go"></form><p>

<a href="new_cond.php?subsidy=<?= $subsidy ?>">New Condition</a>

<p><a href="viewproducts.php?id=<?= $id ?>">Back</a>
</body></html>