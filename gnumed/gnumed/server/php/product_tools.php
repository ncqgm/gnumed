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
// some useful functions for the product-related pages

function print_product_row ($row)
{
  // prints a row from the products table
  echo "<td>{$row['dr']}</td><td>{$row['df']}</td><td>";
  $result = pg_query ("select lpc.strength, du.unit from link_product_component lpc, drug_units du where du.id = lpc.id_unit and lpc.id_product = {$row['id']} order by lpc.id_component");
  $flag = 0;
  while ($row2 = pg_fetch_row ($result))
    {
      if ($flag)
	echo "/";
      $flag = 1;
      echo $row2[0] . $row2[1];
    }
  echo "</td><td>";
  echo "{$row['package_size']}{$row['du']}";
  echo "</td><td>";
  $result = pg_query ("select drug_flags.description from drug_flags, link_flag_product where id_product = {$row['id']} and id_flag = id");
  $flag = 0;
  while ($row2 = pg_fetch_row ($result))
    {
      if ($flag)
	echo "&nbsp;";
      $flag = 1;
      echo $row2[0];
    }
  if ($row['comment'])
    echo "({$row['comment']})</td>";
}


function product_select ($id)
{
  echo "<table><tr><th>Select</th><th>Route</th><th>Form</th><th>Dose</th><th>Package</th><th>Comment</th></tr>";
  // shows a table of selectable products for a drug
  $result = pg_query ("select df.description as df, du.unit as du, p.comment, p.id, dr.description as dr, package_size from product p, drug_formulations df, drug_units du, drug_routes dr where p.id_drug = $id and df.id = id_formulation and du.id = id_packing_unit and dr.id = id_route");
  while ($row = pg_fetch_array ($result))
    {
      echo "<tr><td><input type=\"checkbox\" name=\"products[{$row['id']}]\" value=\"1\" checked></td>";
      print_product_row ($row);
      echo "</tr>";
    }
  echo "</table>";
}
?>
  