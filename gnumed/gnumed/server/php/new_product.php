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
// or see online at http://www.gnu.org/licenses/gpl.html\\
// recieves form for new product

include ('connect.php');

pg_query ("insert into product (id_generic_drug, id_formulation, packing_unit, id_route, package_size) values ($id, $formulation, $packing_unit, $route, $package_size)"); 

if ($is_compound)
{
  $result = pg_query ("select id_component from link_compound_generics where id_compound = $id");
  while ($row = pg_fetch_row ($result))
    {
      $str = "strength" . $row[0];
      $uni = "unit" . $row[0];
      pg_query ("insert into link_product_component (id_product, id_component, strength, id_unit) values (currval ('product_id_seq'), {$row[0]}, ${$str}, ${$uni})");
    }
}
else
{
  pg_query ("insert into link_product_component (id_product, strength, id_unit) values (currval ('product_id_seq'), $strength, $unit)");
}

$result = pg_query ("select id from drug_flags");
while ($row = pg_fetch_array ($result))
{
  $flagname = 'flag' . $row['id'];
  if (isset ($$flagname))
    pg_query ("insert into link_flag_product (id_product, id_flag) values (currval ('product_id_seq'), {$row['id']})");
}

include ('viewproducts.php');

?>