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

// complex form for viewing and changing drugs

<h3>Drug Dosages</h4>

<table>
<tr><th>Dose</th><th>Warning</th><th>Hints</th></tr>
<?php
$result = pg_query ("select dosage.id, coalesce ((select description from drug_warning_categories where drug_warning_categories.id = id_drug_warning_categories), '') as warning, dosage_type, dosage_start, dosage_max, dosage_hints, unit from dosage, link_drug_dosage, drug_units where id_drug = $id and id_dosage = dosage.id and drug_units.id = dosage.id_drug_units");
while ($row = pg_fetch_array ($result))
{
  if ($row["dosage_type"] == 'w')
    $per = '/kg';
  else 
    if ($row["dosage_type"] == 's')
     $per = '/m2';
     else
       if ($row["dosage_type"] == 'a')
	 $per = '/age (months}';
       else
	 $per = '';
  $per = $row["unit"] . $per; 
  $dose = $row["dosage_start"] . $per . "-" . $row["dosage_max"] . $per;
  echo "<tr><td>$dose</td><td>{$row['warning']}</td><td>{$row['dosage_hints']}</td></tr>";
}
?>
</table>

<h4>New Dosage</h4>

<form action="new_dosage.php" method="post">
<input type="hidden" name="id" value="<?= $id ?>">
Start:<input type="text" name="start" size="3">
Max:<input type="text" name="max" size="3">
<select name="unit">

<?php
$result = pg_query ("select * from drug_units");
while ($row = pg_fetch_array ($result))
{
  echo "<option value=\"{$row['id']}\">{$row['unit']}";
}
?>
</select>
<select name="type">
<option value="*" selected>Normal
<option value="w">By Weight (kg)
<option value="s">By Surface Area (m2)
<option value="a">By Age (months)
</select>
<select name="warning">
<option value="-1" selected>No warning
<?php
$result = pg_query ("select * from drug_warning_categories");
while ($row = pg_fetch_array ($result))
{
  echo "<option value=\"{$row['id']}\">{$row['description']}";
}
?>
</select><p>
Hints:<p>
<textarea name="hints" rows="4" cols="50"></textarea><p>
<input type="submit" value="submit">
</form>

<h3>Products</h3>

<table>
<tr><th>Formulation</th><th>Brandname</th><th>Strength</th><th>Packet</th><th>Comment</th><th>Subsidy</th><th>Availability</th></tr>
<tr><th></th><th></th><th></th><th></th><th></th><th>Scheme Qty Rpt $ Cndn</th><th>Cntry Start End</th></tr>
<?php
$result = pg_query ("select product.*, drug_formulations.description as des, u1.unit as unit, u2.unit as packunit from product , drug_formulations f, drug_units u1, drug_units u2 where id_generic_drug = $id and id_formulation = f.id and id_unit = u1.id and packing_unit = u2.id");
while ($row = pg_fetch_array ($result))
{
  
  echo "<tr><td>{$row['des']}</td><td>{$row['brandname']}({$row['name']})</td><td>{$row['strength']}{$row['unit']}</td><td>{$row['package_size']}{$row['packunit']}</td><td>{$row['comment']}</td><td><a href=\"new_subsidy.php?product={$row['product.id']}\">New Sub</a></td><a href=\"new_availability.php?product={$row['product.id']}\">New Availability</a></td></tr>";
  $r2go = true;
  $r3go = true;
  $result2 = pg_query ("select name, iso_countrycode, max_qty, max_rpt, coalesce (copayment, 0.0) as copay, (condition is not null) as cond from subsidized_products, subsidies where id_product = {$row['product.id']} and id_subsidy = subsidies.id");
  $result3 = pg_query ("select * from availability where id_product = {$row['product.id']}");
  while ($r3go or $r2go)
    {
      if (! $row2 = pg_fetch_array ($result2))
	$r2go = false;
      if (! $row3 = pg_fetch_array ($result3))
	$r3go = false;
      if ($r3go or $r2go)
	{
	  if ($row2['cond'])
	    $condition = '*'; # FIXME turn into a link to enter condition
	  else
	    $condition = '';
	  echo "<tr><th></th><th></th><th></th><th></th><th></th>";
	  if ($r2go)
	    echo "<td>{$row2['name']}({$row2['iso_countrycode']}) {$row2['max_qty']} {$row2['max_rpt']} \${$row2['copay']} {$row2['condition']} ({$condition})</td>";
	  else
	    echo "<td></td>";
	  if ($r3go)
	    echo "<td>{$row3['iso_countrycode']} {$row3['available_from']} {$row3['banned']} ({$row3['comment']})";
	  echo "</tr>";
	}
    }
}
?>
</table>

<h4>New Product</h3>

<form action="new_product.php" method="post">
<select name="formulation">
<?php
$result = pg_query ("select * from drug_formulations");
while ($row = pg_fetch_array ($result))
{
  echo "<option value=\"{$row['id']}\">{$row['description']}";
}
?>
</select>
Brand: <input type="text" name="brandname" value="GENERIC" size="10">
Strength: <input type="float" name="strength" size="4">
<select name="unit">
<?php
$result = pg_query ("select * from drug_units");
while ($row = pg_fetch_array ($result))
{
  echo "<option value=\"{$row['id']}\">{$row['unit']}";
}
?>
</select>
Package:<input type="int" name="package_size">
<select name="packing_unit">
<?php
$result = pg_query ("select * from drug_units");
while ($row = pg_fetch_array ($result))
{
  echo "<option value=\"{$row['id']}\">{$row['unit']}";
}
?>
</select>
<input type="hidden" name="drug_id" value="<?= $id ?>">
<input type="submit" value="submit">
</form>


</body>
</html>
       