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

if (! $conn)
     include ('connect.php');
include ('product_tools.php');

$result = pg_query ("select get_drug_name ($id)");
$drugname = pg_fetch_result ($result, 0, 0);
$result = pg_query ("select category from drug_element where id = $id");
$category = pg_fetch_result ($result, 0, 0);
if ($category == 'c')
{
  $compound = '&nbsp;(';
  $flag = 0;
  $result = pg_query ("select get_drug_name (id_component) from link_compound_generics where id_compound = $id order by id_component");
  while ($row = pg_fetch_row ($result))
    {
      if ($flag)
       $compound = $compound . "/";
      $compound = $compound . $row[0];
      $flag = 1;
    }
  $compound = $compound . ')';
}
else
{
  $compound = '';
}

if (isset ($available))
{
  if (strlen ($available) != 2)
    {
      echo "$available is not a valid ISO country code. Go back!";
      exit;
    }
}
?>
<html>
<title>Products of <?= $drugname?><?=$compound ?></title>
<body>
<h1>Products of <?=$drugname?><?=$compound ?></h1>

<table>
<tr><th>Route</th><th>Form</th><th>Dose</th><th>Package</th><th>Comment</th>

<?php
if (isset ($available)) {
  echo "<th>Avail ($available)</th><th>Brands</th>";
}
if (isset ($subsidy)) {
  echo "<th>$subsidy (Qty Rpt \$ Cndn)</th>";
}
?>
<td></td></tr>

<?php
$result = pg_query ("select df.description as df, du.unit as du, p.comment, p.id, dr.description as dr, package_size from product p, drug_formulations df, drug_units du, drug_routes dr where p.id_generic_drug = $id and df.id = id_formulation and du.id = packing_unit and dr.id = id_route");
while ($row = pg_fetch_array ($result))
{
  echo "<tr>";
  print_product_row ($row);
  if (isset ($available)) 
    {
      echo "<td>";
      $result2 = pg_query ("select * from available where id_product = {$row['id']} and iso_countrycode = '$available'");
      if ($row2 = pg_fetch_array ($result2))
	{
	  if ($row2['available_from'])
	    echo "From:" . $row2['available_from'];
	  else
	    if ($row2['banned'])
	      echo "<b>Banned: " . $row2['banned'] . "</b>";
	    else
	      echo "Yes";
	  if ($row2['comment'])
	    echo "({$row2['comment']})";
	}
      else
	echo "No";
      echo "</td><td>";
      $result2 = pg_query ("select lpm.brandname, m.code, m.id from link_product_manufacturer lpm, manufacturer m where lpm.id_product = {$row['id']} and m.id = lpm.id_manufacturer aand m.iso_countrycode = '$available'");
      while ($row2 = pg_fetch_row ($result2))
	{
	  echo "{$row2[0]}(<a href=\"mnfctr.php?id_man={$row2[2]}\">{$row2[1]}</a>)&nbsp;";
	}
    echo "</td>";
    }
  if (isset ($subsidy)) 
    {
      $result2 = pg_query ("select * from subsidized_products where id_product = {$row['id']} and id_subsidy = $subsidy");
      while ($row2 = pg_fetch_array ($result2))
	{
	  echo "<td>{$row2['max_qty']}$nbsp;{$row2['max_rpt']}$nbsp;\${$row2['copayment']}";
	  if ($row2['condition'])
	    echo "&nbsp;<a href=\"show_condition.php?id_cond={$row2['condition']}\">*</a>";
	  echo "</td>";
	}
    }
  echo "<td><a onClick=\"return confirm(\"are you sure?\");\" href=\"del_product.php?id_prod={$row['id']}\">DELETE</a></td></tr>";
}
?>
</table>

<h2>New Product</h2>

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
<select name="route">
<?php
$result = pg_query ("select * from drug_routes");
while ($row = pg_fetch_array ($result))
{
  echo "<option value=\"{$row['id']}\">{$row['description']}";
}
?>
</select>
<?php
if ($category == 'c')
{
  $result = pg_query ("select id_component, get_drug_name (id_component) from link_compound_generics where id_compound = $id");
  while ($row = pg_fetch_row ($result))
    {
      $comp = $row[1];
      $id_comp = $row[0];
      echo "<b>$comp</b>: <input type=\"float\" name=\"strength$id_comp\" size=\"4\"><select name=\"unit$id_comp\">";
      $result2 = pg_query ("select * from drug_units");
      while ($row2 = pg_fetch_array ($result2))
	{
	  echo "<option value=\"{$row2['id']}\">{$row2['unit']}";
	}
      echo "</select>";
    }
  echo "<input type=\"hidden\" name=\"is_compound\" value=\"1\">";
}
else
{
  echo "Strength: <input type=\"float\" name=\"strength\" size=\"4\"><select name=\"unit\">";
  $result2 = pg_query ("select * from drug_units");
  while ($row2 = pg_fetch_array ($result2))
  {
    echo "<option value=\"{$row2['id']}\">{$row2['unit']}";
  }
 echo "</select>";
}
?><p>

Package:<input type="int" name="package_size" size="3">
<select name="packing_unit">
<?php
$result = pg_query ("select * from drug_units");
while ($row = pg_fetch_array ($result))
{
  echo "<option value=\"{$row['id']}\">{$row['unit']}";
}
?>
</select><p>
Flags:<?php
$result = pg_query ("select * from drug_flags");
while ($row = pg_fetch_array ($result))
     echo "<input type=\"checkbox\" name=\"flag{$row['id']}\" value=\"1\">{$row['description']}"; 
?><p><input type="hidden" name="id" value="<?= $id ?>">
<input type="submit" value="submit"></form>


<h2>Change View</h2>

<form method="post" action="viewproducts.php">
<input type="hidden" name="id" value="<?= $id?>">
Add Country Details:<input type="text" name="available" size="2">
<input type="submit" value="go"></form><p>

<a href="change_avail.php?id=<?= $id?>">Change Availability</a><p>
<a href="add_brand.php?id=<?= $id ?>">Add Brand</a>

<form method="post" action="viewproducts.php">
Show Subsidies:
<select name="subsidy">
<?php
$result = pg_query ("select * from subsidies");
while ($row = pg_fetch_array ($result))
{
  echo "<option value=\"{$row['id']}\">{$row['name']}";
}
?>

<input type="hidden" name="id" value="<?= $id ?>">
<input type="submit" value="go"></form><p>

<a href="change_subsidies.php?id=<?=$id?>">Change Subsidies</a>

</body></html>