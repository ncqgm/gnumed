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
{
  include ('connect.php');
}

foreach ($products as $key => $value)
{
  pg_query ("insert into link_product_manufacturer values ($key, $id_manu, '$brandname')");
}


// show country data from country of this manufacturer
$result = pg_query ("select iso_countrycode from manufacturer where id = $id_manu");
$available = pg_fetch_result ($result, 0, 0);
include ('viewproducts.php');
?>