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
<title>Change Availability</title>
<body>
<h1>Change Availability</h1>

<form action="recv_change_avail.php" method="post">
<?php
product_select ($id);
?>
<input type="hidden" name="id" value="<?=$id ?>">
Country:<input type="text" name="iso_countrycode" size="2"><p>
From date:<input type="text" name="from_date" size="10"><p>
Banned date:<input type="text" name="banned" size="10"><p>
<input type="submit" value="submit"></form>
</body></html>