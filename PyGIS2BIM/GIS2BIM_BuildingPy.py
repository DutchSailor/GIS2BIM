# -*- coding: utf8 -*-
#***************************************************************************
#*   Copyright (c) 2021 Maarten Vroegindeweij <maarten@3bm.co.nl>          *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Library General Public License for more details.                  *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with this program; if not, write to the Free Software   *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************

"""This module provides tools to edit Geometry with BuildingPy
"""

__title__= "GIS2BIM_BuildingPy"
__author__ = "Maarten Vroegindeweij"
__url__ = "https://github.com/DutchSailor/GIS2BIM"


def gmlcoordTo2DPoints(gmlstr: str):
    coord = []
    for x in gmlstr.split(" "):
        coords = x.split(",")
        coord.append(Point2D(x=float(coords[0]), y=float(coords[1])))
    return coord

def gmlNearestPointLine(gmlstr, pntsstr):
    pnts = gmlcoordTo2DPoints(gmlstr)
    pointhouse = gmlcoordTo2DPoints(pntsstr)
    plycurve = PolyCurve2D.byPoints(pnts)
    lst1 = []
    lst2 = []

    for x in plycurve.points():
        dist = Point2D.distance(x, pointhouse[0])
        lst1.append(dist)
        lst2.append(x)

    lst3 = [x for _, x in sorted(zip(lst1, lst2), key=lambda pair: pair[0])]
    lst4 = sorted(lst1)
    ln = Line2D(lst3[0], lst3[3])

    return ln