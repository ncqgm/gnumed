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

if (strlen ($from_date) < 5)
{
  $from_date = 'NULL';
}
else
$from_date = "'$from_date'";
if (strlen ($banned) < 5)
{
  $banned = 'NULL';
}
else
$banned = "'$banned'";

foreach ($products as $key => $value)
{
  pg_query ("insert into available (id_product, iso_countrycode, available_from, banned) values ($key, '$iso_countrycode', $from_date, $banned)");
}

$available = $iso_countrycode;
include ('viewproducts.php');
?>