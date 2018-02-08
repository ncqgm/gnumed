# Copyright (C) 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018  Rickard Lindberg, Roger Lindberg
#
# This file is part of Timeline.
#
# Timeline is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Timeline is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Timeline.  If not, see <http://www.gnu.org/licenses/>.


CSS = u"""
body {
    background-color: lightblue;
    background: linear-gradient(lightblue, white);
}

#titlebox {
    border-radius: 25px;
    background: #e085c2;
    padding: 5px;
    position: relative;
    top: 40px;
    font-size: 32px;
    font-family: Verdana, Arial, Sans-Serif;
}

#descriptionbox {
    border-radius: 25px;
    background: #b3d1ff;
    padding: 15px;
    position: fixed;
    width: 50%;
    top: 140px;
    left: 40%;
    height: 65%;
    font-size: 24px;
    font-family: Verdana, Arial, Sans-Serif;
    border-style: solid;
    border-color: #4d94ff;
    overflow-y: auto;
}

#only_description {
    border-radius: 12px;
    background: #b3d1ff;
    padding: 15px;
    position: relative;
    width: 80%;
    top: 40px;
    height: 65%;
    font-size: 24px;
    font-family: Verdana, Arial, Sans-Serif;
    border-style: solid;
    border-color: #4d94ff;
    overflow-y: auto;
    margin-left: auto;
    margin-right: auto;
}

#imagebox {
    border-radius: 25px;
    background: lightblue;
    padding: 0;
    position: fixed;
    top: 180px;
    left: 25%;
}

div.timeline_icon {
    position: fixed;
    right: 7px;
    bottom: 7px;
}

.button {
    background-color: #66CDAA;
    border: none;
    color: white;
    padding: 5px 11px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
    margin: 4px 2px;
    cursor: pointer;
    border-radius: 8px;
}

div.left {
    position: fixed;
    top: 50%;
    left: 0;
}

div.right {
    position: fixed;
    top: 50%;
    right: 0;
}

a.button:hover {
    background-color: #6600AA;
}

.enlarge {
    transform: scale(1.5, 1.5);
}

div.history_line {
    position: fixed;
    top: 14px;
    left: 2%;
    width: 90%;
    border-bottom: 1px solid #000;
    line-height: 0.1em;
}

"""

PAGE_TEMPLATE = u"""
<html>
<head>
<link rel="stylesheet" type="text/css" href="slideshow.css">

<style>

/*
Place a filled circle on the history line at the relative position
of the events start date.
The %%s is replaced with one row for each event to display.
The div classname contains the event sequence number like this:
     div.position_in_history_8 { ... }
For each row, there is a corresponding div tag defined in the body
of this page like:
     <div class="position_in_history_8"/>

*/
%s

/*
A filled circle placed at the history line at the relative
position of the event displayed in this page
*/
div.position_in_history {
    border-radius: 50%%;
    width: 16px;
    height: 16px;
    background-color: #e085c2;
    position: fixed;
    top: 7px;
    left: %s%%;
}
</style>
</head>

<body>

<!-- Time and title box
The %%s is replaced with the time period and the text for the event.
-->
<center><p id="titlebox">%s</br>%s</p></center>

<!-- Image and description boxes
The %%s is replaced with the event icon and the event description text.
If the event don't have an image, only the description text is displayed.
-->
%s

<!-- Left navigation button -->
<div class="left">
<a href="page_%s.html" class="button">&lt&lt</a>
</div>

<!-- Right navigation button -->
<div class="right">
<a href="page_%s.html" class="button">&gt&gt</a>
</div>

<!-- Timeline icon -->
<div class="timeline_icon">
<img src="32.png">
</div>

<!-- History Line
Display a line that represents the time span from the start time of the
first event to the start time of the last event.
-->
<div class="history_line"/>

<!-- Position in history
  Display a filled circle on the history line at the relative position
  of the events start date.
  The %%s is replaced with one row for each event to display.
  The div classname contains the event sequence number like this:
     <div class="position_in_history_8"/>
  For each row, there is a corresponding style defined in the head
  of this page like:
     div.position_in_history_8 { ... }
-->
%s

<div class="position_in_history"/>
</body>
</html>
"""

ONLY_DESCRIPTION = """
<div id="only_description">%s</div>
"""

IMAGE_AND_DESCRIPTION = """
<div id="imagebox"><img class="enlarge" src="%s"></div>
<div id="descriptionbox">%s</div>
"""
