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

if (strlen ($iso_countrycode) != 2)
{
  echo "$iso_countrycode is not a valid ISO country code";
  exit;
}

pg_query ("update manufacturer set name='$name', iso_countrycode = '$iso_countrycode', address = '$address', phone = '$phone', fax = '$fax', comment = '$comment', code = '$code' where id = $id_manu");

echo "manufacturer updated.";

?>
